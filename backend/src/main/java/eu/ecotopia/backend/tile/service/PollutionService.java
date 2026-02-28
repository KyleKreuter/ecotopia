package eu.ecotopia.backend.tile.service;

import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileType;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;

/**
 * Handles passive grid changes that happen at the end of each round.
 * Processes pollution spread from polluting buildings, forest degradation, and river regeneration.
 */
@Slf4j
@Service
public class PollutionService {

    private static final Set<TileType> POLLUTING_TYPES = Set.of(
            TileType.FACTORY, TileType.OIL_REFINERY, TileType.COAL_PLANT
    );

    /**
     * Main entry point: applies one pollution tick to the game.
     * Processing order matters: spread -> degradation -> regeneration.
     *
     * @param game the current game state
     */
    public void applyPollutionTick(Game game) {
        List<Tile> tiles = game.getTiles();

        // Phase 1: Pollution spread from polluting buildings
        applyPollutionSpread(tiles);

        // Phase 2: Degradation (SICK_FOREST -> WASTELAND after 2 rounds)
        applyDegradation(tiles);

        // Phase 3: Regeneration (POLLUTED_RIVER -> CLEAN_RIVER if no active source)
        applyRegeneration(tiles);
    }

    /**
     * Phase 1: Spread pollution from FACTORY (range 1), OIL_REFINERY (range 2), COAL_PLANT (range 2).
     * Effects: CLEAN_RIVER -> POLLUTED_RIVER, HEALTHY_FOREST -> SICK_FOREST, FARMLAND -> DEAD_FARMLAND.
     */
    private void applyPollutionSpread(List<Tile> allTiles) {
        for (Tile source : allTiles) {
            int range = getPollutionRange(source.getTileType());
            if (range == 0) {
                continue;
            }

            List<Tile> affected = getTilesInRange(allTiles, source.getX(), source.getY(), range);
            for (Tile target : affected) {
                TileType polluted = pollute(target.getTileType());
                if (polluted != null) {
                    log.debug("Pollution spread: ({},{}) {} -> {} from ({},{}) {}",
                            target.getX(), target.getY(), target.getTileType(), polluted,
                            source.getX(), source.getY(), source.getTileType());
                    target.setTileType(polluted);
                    target.setRoundsInCurrentState(0);
                }
            }
        }
    }

    /**
     * Phase 2: Degrade SICK_FOREST tiles.
     * If roundsInCurrentState >= 2, the forest dies and becomes WASTELAND.
     * Otherwise, increment the counter.
     */
    private void applyDegradation(List<Tile> allTiles) {
        for (Tile tile : allTiles) {
            if (tile.getTileType() != TileType.SICK_FOREST) {
                continue;
            }

            if (tile.getRoundsInCurrentState() >= 2) {
                log.debug("Degradation: ({},{}) SICK_FOREST -> WASTELAND after {} rounds",
                        tile.getX(), tile.getY(), tile.getRoundsInCurrentState());
                tile.setTileType(TileType.WASTELAND);
                tile.setRoundsInCurrentState(0);
            } else {
                tile.setRoundsInCurrentState(tile.getRoundsInCurrentState() + 1);
            }
        }
    }

    /**
     * Phase 3: Regenerate POLLUTED_RIVER tiles that have no active pollution source in range.
     * If no source is present, increment counter; at >= 2 rounds it becomes CLEAN_RIVER.
     * If a source IS present, reset the counter to 0.
     */
    private void applyRegeneration(List<Tile> allTiles) {
        for (Tile tile : allTiles) {
            if (tile.getTileType() != TileType.POLLUTED_RIVER) {
                continue;
            }

            if (hasPollutionSource(allTiles, tile.getX(), tile.getY())) {
                // Active pollution keeps the river dirty
                tile.setRoundsInCurrentState(0);
            } else {
                int newRounds = tile.getRoundsInCurrentState() + 1;
                if (newRounds >= 2) {
                    log.debug("Regeneration: ({},{}) POLLUTED_RIVER -> CLEAN_RIVER", tile.getX(), tile.getY());
                    tile.setTileType(TileType.CLEAN_RIVER);
                    tile.setRoundsInCurrentState(0);
                } else {
                    tile.setRoundsInCurrentState(newRounds);
                }
            }
        }
    }

    /**
     * Checks if any pollution source (FACTORY range 1, OIL_REFINERY/COAL_PLANT range 2)
     * can reach the given position.
     *
     * @param allTiles all tiles in the game
     * @param x        target x coordinate
     * @param y        target y coordinate
     * @return true if at least one pollution source is within range
     */
    private boolean hasPollutionSource(List<Tile> allTiles, int x, int y) {
        for (Tile tile : allTiles) {
            int range = getPollutionRange(tile.getTileType());
            if (range == 0) {
                continue;
            }

            int distance = Math.abs(tile.getX() - x) + Math.abs(tile.getY() - y);
            if (distance <= range) {
                return true;
            }
        }
        return false;
    }

    /**
     * Gets all tiles within Manhattan distance from the given coordinates.
     *
     * @param allTiles all tiles in the game
     * @param x        center x coordinate
     * @param y        center y coordinate
     * @param range    maximum Manhattan distance (inclusive)
     * @return list of tiles within range (excluding the center tile itself)
     */
    private List<Tile> getTilesInRange(List<Tile> allTiles, int x, int y, int range) {
        return allTiles.stream()
                .filter(tile -> {
                    int distance = Math.abs(tile.getX() - x) + Math.abs(tile.getY() - y);
                    return distance > 0 && distance <= range;
                })
                .toList();
    }

    /**
     * Returns the pollution range for a given tile type.
     * FACTORY: range 1, OIL_REFINERY/COAL_PLANT: range 2, everything else: 0 (no pollution).
     */
    private int getPollutionRange(TileType type) {
        return switch (type) {
            case FACTORY -> 1;
            case OIL_REFINERY, COAL_PLANT -> 2;
            default -> 0;
        };
    }

    /**
     * Returns the polluted version of a tile type, or null if the tile cannot be polluted.
     */
    private TileType pollute(TileType type) {
        return switch (type) {
            case CLEAN_RIVER -> TileType.POLLUTED_RIVER;
            case HEALTHY_FOREST -> TileType.SICK_FOREST;
            case FARMLAND -> TileType.DEAD_FARMLAND;
            default -> null;
        };
    }
}

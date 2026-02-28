package eu.ecotopia.backend.tile.service;

import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileActionType;
import eu.ecotopia.backend.tile.model.TileType;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * Service that calculates available tile actions based on tile type and research level,
 * and executes tile actions by applying resource deltas, changing tile types,
 * and decrementing the action counter for the current round.
 */
@Service
public class TileActionService {

    /**
     * Returns the list of valid actions for the given tile, considering its type
     * and the current research level of the game.
     *
     * @param game the current game
     * @param tile the tile to get actions for
     * @return list of available action types (may be empty)
     */
    public List<TileActionType> getAvailableActions(Game game, Tile tile) {
        int research = game.getResources().getResearch();
        TileType type = tile.getTileType();
        List<TileActionType> actions = new ArrayList<>();

        switch (type) {
            case HEALTHY_FOREST, SICK_FOREST -> {
                actions.add(TileActionType.DEMOLISH);
                actions.add(TileActionType.BUILD_RESEARCH_CENTER);
            }
            case FACTORY -> {
                actions.add(TileActionType.DEMOLISH);
                if (research >= 35) {
                    actions.add(TileActionType.UPGRADE_CARBON_CAPTURE);
                }
                if (research >= 40) {
                    actions.add(TileActionType.REPLACE_WITH_SOLAR);
                }
            }
            case OIL_REFINERY -> {
                actions.add(TileActionType.DEMOLISH);
                if (research >= 40) {
                    actions.add(TileActionType.REPLACE_WITH_SOLAR);
                }
            }
            case COAL_PLANT -> {
                actions.add(TileActionType.DEMOLISH);
                if (research >= 40) {
                    actions.add(TileActionType.REPLACE_WITH_SOLAR);
                }
            }
            case WASTELAND -> {
                actions.add(TileActionType.PLANT_FOREST);
                actions.add(TileActionType.BUILD_FACTORY);
                if (research >= 40) {
                    actions.add(TileActionType.BUILD_SOLAR);
                }
                actions.add(TileActionType.BUILD_RESEARCH_CENTER);
                if (research >= 80) {
                    actions.add(TileActionType.BUILD_FUSION);
                }
            }
            case FARMLAND -> {
                actions.add(TileActionType.CLEAR_FARMLAND);
            }
            // Tiles with no actions: RESIDENTIAL, CITY_CENTER, CLEAN_RIVER, POLLUTED_RIVER,
            // DEAD_FARMLAND, CLEAN_FACTORY, SOLAR_FIELD, FUSION_REACTOR, RESEARCH_CENTER
            default -> {
                // No actions available
            }
        }

        return actions;
    }

    /**
     * Executes the given action on the tile. Changes the tile type, applies resource
     * deltas to the game, and decrements remainingActions on the current round.
     *
     * @param game   the current game (must be RUNNING)
     * @param tile   the tile to act on
     * @param action the action to execute
     * @throws IllegalStateException if the game is not running, no actions remain,
     *                               or the action is not valid for the tile
     */
    public void executeAction(Game game, Tile tile, TileActionType action) {
        if (game.getStatus() != GameStatus.RUNNING) {
            throw new IllegalStateException("Cannot execute action: game is not running");
        }

        GameRound currentRound = findCurrentRound(game);

        if (currentRound.getRemainingActions() <= 0) {
            throw new IllegalStateException("Cannot execute action: no remaining actions this round");
        }

        List<TileActionType> availableActions = getAvailableActions(game, tile);
        if (!availableActions.contains(action)) {
            throw new IllegalStateException(
                    "Action " + action + " is not available for tile type " + tile.getTileType());
        }

        applyAction(game, tile, action);
        currentRound.setRemainingActions(currentRound.getRemainingActions() - 1);
    }

    /**
     * Finds the GameRound matching the game's currentRound number.
     */
    private GameRound findCurrentRound(Game game) {
        return game.getRounds().stream()
                .filter(r -> r.getRoundNumber() == game.getCurrentRound())
                .findFirst()
                .orElseThrow(() -> new IllegalStateException(
                        "No GameRound found for round number " + game.getCurrentRound()));
    }

    /**
     * Applies the action effects: changes tile type, applies resource deltas, resets state counter.
     */
    private void applyAction(Game game, Tile tile, TileActionType action) {
        GameResources res = game.getResources();

        switch (tile.getTileType()) {
            case HEALTHY_FOREST, SICK_FOREST -> applyForestAction(tile, action, res);
            case FACTORY -> applyFactoryAction(tile, action, res);
            case OIL_REFINERY -> applyOilRefineryAction(tile, action, res);
            case COAL_PLANT -> applyCoalPlantAction(tile, action, res);
            case WASTELAND -> applyWastelandAction(tile, action, res);
            case FARMLAND -> applyFarmlandAction(tile, action);
            default -> throw new IllegalStateException(
                    "No actions supported for tile type " + tile.getTileType());
        }

        clampResources(res);
    }

    private void applyForestAction(Tile tile, TileActionType action, GameResources res) {
        switch (action) {
            case DEMOLISH -> {
                tile.setTileType(TileType.WASTELAND);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() + 1);
                res.setEcology(res.getEcology() - 3);
            }
            case BUILD_RESEARCH_CENTER -> {
                tile.setTileType(TileType.RESEARCH_CENTER);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 2);
                res.setResearch(res.getResearch() + 5);
                res.setEcology(res.getEcology() - 2);
            }
            default -> throw new IllegalStateException("Invalid action " + action + " for forest tile");
        }
    }

    private void applyFactoryAction(Tile tile, TileActionType action, GameResources res) {
        switch (action) {
            case DEMOLISH -> {
                tile.setTileType(TileType.WASTELAND);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 4);
                res.setEcology(res.getEcology() + 2);
            }
            case UPGRADE_CARBON_CAPTURE -> {
                tile.setTileType(TileType.CLEAN_FACTORY);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 1);
                res.setEcology(res.getEcology() + 3);
            }
            case REPLACE_WITH_SOLAR -> {
                tile.setTileType(TileType.SOLAR_FIELD);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 1);
                res.setEcology(res.getEcology() + 4);
            }
            default -> throw new IllegalStateException("Invalid action " + action + " for factory tile");
        }
    }

    private void applyOilRefineryAction(Tile tile, TileActionType action, GameResources res) {
        switch (action) {
            case DEMOLISH -> {
                tile.setTileType(TileType.WASTELAND);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 5);
                res.setEcology(res.getEcology() + 4);
            }
            case REPLACE_WITH_SOLAR -> {
                tile.setTileType(TileType.SOLAR_FIELD);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 2);
                res.setEcology(res.getEcology() + 5);
            }
            default -> throw new IllegalStateException("Invalid action " + action + " for oil refinery tile");
        }
    }

    private void applyCoalPlantAction(Tile tile, TileActionType action, GameResources res) {
        switch (action) {
            case DEMOLISH -> {
                tile.setTileType(TileType.WASTELAND);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 4);
                res.setEcology(res.getEcology() + 3);
            }
            case REPLACE_WITH_SOLAR -> {
                tile.setTileType(TileType.SOLAR_FIELD);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 1);
                res.setEcology(res.getEcology() + 4);
            }
            default -> throw new IllegalStateException("Invalid action " + action + " for coal plant tile");
        }
    }

    private void applyWastelandAction(Tile tile, TileActionType action, GameResources res) {
        switch (action) {
            case PLANT_FOREST -> {
                tile.setTileType(TileType.HEALTHY_FOREST);
                tile.setRoundsInCurrentState(0);
                res.setEcology(res.getEcology() + 2);
            }
            case BUILD_FACTORY -> {
                tile.setTileType(TileType.FACTORY);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() + 4);
                res.setEcology(res.getEcology() - 3);
            }
            case BUILD_SOLAR -> {
                tile.setTileType(TileType.SOLAR_FIELD);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() + 3);
                res.setEcology(res.getEcology() + 2);
            }
            case BUILD_RESEARCH_CENTER -> {
                tile.setTileType(TileType.RESEARCH_CENTER);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() - 2);
                res.setResearch(res.getResearch() + 5);
            }
            case BUILD_FUSION -> {
                tile.setTileType(TileType.FUSION_REACTOR);
                tile.setRoundsInCurrentState(0);
                res.setEconomy(res.getEconomy() + 8);
                res.setEcology(res.getEcology() + 3);
            }
            default -> throw new IllegalStateException("Invalid action " + action + " for wasteland tile");
        }
    }

    private void applyFarmlandAction(Tile tile, TileActionType action) {
        if (action == TileActionType.CLEAR_FARMLAND) {
            tile.setTileType(TileType.WASTELAND);
            tile.setRoundsInCurrentState(0);
        } else {
            throw new IllegalStateException("Invalid action " + action + " for farmland tile");
        }
    }

    /**
     * Clamps all resource values to the valid range [0, 100].
     */
    private void clampResources(GameResources res) {
        res.setEcology(Math.max(0, Math.min(100, res.getEcology())));
        res.setEconomy(Math.max(0, Math.min(100, res.getEconomy())));
        res.setResearch(Math.max(0, Math.min(100, res.getResearch())));
    }
}

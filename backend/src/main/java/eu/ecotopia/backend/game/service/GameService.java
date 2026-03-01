package eu.ecotopia.backend.game.service;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.citizen.service.CitizenService;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.DefeatReason;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameRank;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.game.repository.GameRepository;
import eu.ecotopia.backend.init.GameInitializer;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileActionType;
import eu.ecotopia.backend.tile.model.TileType;
import eu.ecotopia.backend.tile.repository.TileRepository;
import eu.ecotopia.backend.tile.service.PollutionService;
import eu.ecotopia.backend.tile.service.TileActionService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Orchestrates the game flow by delegating to TileActionService, PollutionService, and CitizenService.
 * Handles game creation, action execution, round advancement, resource recalculation,
 * and game-over / victory condition checks.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class GameService {

    private static final int MAX_ROUNDS = 7;

    private final GameRepository gameRepository;
    private final GameInitializer gameInitializer;
    private final TileActionService tileActionService;
    private final PollutionService pollutionService;
    private final CitizenService citizenService;
    private final TileRepository tileRepository;

    /**
     * Creates a new game with initialized tiles, citizens, first round, and starting resources.
     *
     * @return the persisted new game
     */
    @Transactional
    public Game createNewGame() {
        Game game = gameInitializer.createNewGame();
        Game saved = gameRepository.save(game);
        log.info("Created new game with id={}", saved.getId());
        return saved;
    }

    /**
     * Fetches a game by its ID.
     *
     * @param id the game ID
     * @return the game entity
     * @throws EntityNotFoundException if no game exists with the given ID
     */
    @Transactional(readOnly = true)
    public Game getGame(Long id) {
        return gameRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Game not found with id=" + id));
    }

    /**
     * Executes a tile action at the given coordinates, then spawns any resulting citizens.
     *
     * @param gameId the game ID
     * @param x      the tile x coordinate
     * @param y      the tile y coordinate
     * @param action the action to perform
     * @return the updated game
     * @throws EntityNotFoundException  if the game or tile is not found
     * @throws IllegalStateException    if the action cannot be executed
     */
    @Transactional
    public Game executeAction(Long gameId, int x, int y, TileActionType action) {
        Game game = getGameOrThrow(gameId);
        Tile tile = tileRepository.findByGameIdAndXAndY(gameId, x, y)
                .orElseThrow(() -> new EntityNotFoundException(
                        "Tile not found at (" + x + "," + y + ") for game id=" + gameId));

        // Save the previous tile type before the action changes it
        TileType previousTileType = tile.getTileType();

        tileActionService.executeAction(game, tile, action);
        citizenService.spawnCitizens(game, previousTileType, action);

        return gameRepository.save(game);
    }

    /**
     * Advances the game to the next round. Applies pollution, citizen lifecycle,
     * resource recalculation, and checks for game-over or victory conditions.
     *
     * @param gameId the game ID
     * @return the updated game
     * @throws EntityNotFoundException if the game is not found
     * @throws IllegalStateException   if the game is not in RUNNING status
     */
    @Transactional
    public Game advanceRound(Long gameId) {
        Game game = getGameOrThrow(gameId);

        if (game.getStatus() != GameStatus.RUNNING) {
            throw new IllegalStateException("Cannot advance round: game is not running (status=" + game.getStatus() + ")");
        }

        // Apply end-of-round effects
        pollutionService.applyPollutionTick(game);
        citizenService.tickCitizenLifecycle(game);

        // Recalculate resources based on the current grid state
        recalculateResources(game);

        // Check game-over conditions
        if (checkGameOver(game)) {
            log.info("Game id={} lost: {}", game.getId(), game.getDefeatReason());
            return gameRepository.save(game);
        }

        // Check victory at the end of the final round
        if (game.getCurrentRound() >= MAX_ROUNDS) {
            determineVictory(game);
            log.info("Game id={} won with rank {}", game.getId(), game.getResultRank());
            return gameRepository.save(game);
        }

        // Advance to the next round
        int nextRoundNumber = game.getCurrentRound() + 1;
        GameRound nextRound = GameRound.builder()
                .roundNumber(nextRoundNumber)
                .remainingActions(2)
                .build();
        game.addRound(nextRound);
        game.setCurrentRound(nextRoundNumber);

        log.info("Game id={} advanced to round {}", game.getId(), nextRoundNumber);
        return gameRepository.save(game);
    }

    // --- Private helpers ---

    /**
     * Loads a game by ID, throwing EntityNotFoundException if not found.
     */
    private Game getGameOrThrow(Long gameId) {
        return gameRepository.findById(gameId)
                .orElseThrow(() -> new EntityNotFoundException("Game not found with id=" + gameId));
    }

    /**
     * Recalculates ecology, economy, and research based on the current tile grid.
     * Values are absolute (not deltas) and clamped to [0, 100].
     */
    private void recalculateResources(Game game) {
        int ecology = 0;
        int economy = 0;
        int research = 0;

        for (Tile tile : game.getTiles()) {
            ecology += getEcologyContribution(tile.getTileType());
            economy += getEconomyContribution(tile.getTileType());
            research += getResearchContribution(tile.getTileType());
        }

        GameResources resources = game.getResources();
        resources.setEcology(clamp(ecology));
        resources.setEconomy(clamp(economy));
        resources.setResearch(clamp(research));
    }

    /**
     * Returns the ecology contribution for a given tile type.
     */
    private int getEcologyContribution(TileType type) {
        return switch (type) {
            case HEALTHY_FOREST -> 2;
            case SICK_FOREST -> 1;
            case CLEAN_RIVER -> 1;
            case SOLAR_FIELD -> 2;
            case FUSION_REACTOR -> 3;
            case CLEAN_FACTORY -> 1;
            case FACTORY -> -3;
            case OIL_REFINERY -> -5;
            case COAL_PLANT -> -4;
            case POLLUTED_RIVER -> -1;
            case DEAD_FARMLAND -> -1;
            default -> 0;
        };
    }

    /**
     * Returns the economy contribution for a given tile type.
     */
    private int getEconomyContribution(TileType type) {
        return switch (type) {
            case FACTORY -> 3;
            case CLEAN_FACTORY -> 2;
            case OIL_REFINERY -> 5;
            case COAL_PLANT -> 4;
            case FARMLAND -> 1;
            case SOLAR_FIELD -> 3;
            case FUSION_REACTOR -> 8;
            case RESEARCH_CENTER -> -2;
            case CITY_INNER -> 2;
            case CITY_OUTER -> 1;
            default -> 0;
        };
    }

    /**
     * Returns the research contribution for a given tile type.
     */
    private int getResearchContribution(TileType type) {
        return type == TileType.RESEARCH_CENTER ? 5 : 0;
    }

    /**
     * Clamps a value to the range [0, 100].
     */
    private int clamp(int value) {
        return Math.max(0, Math.min(100, value));
    }

    /**
     * Checks game-over conditions. If triggered, sets the game status to LOST with the
     * appropriate defeat reason and returns true.
     *
     * @param game the game to check
     * @return true if the game is over (lost), false otherwise
     */
    private boolean checkGameOver(Game game) {
        GameResources resources = game.getResources();

        if (resources.getEcology() < 20) {
            game.setStatus(GameStatus.LOST);
            game.setDefeatReason(DefeatReason.ECOLOGICAL_COLLAPSE);
            return true;
        }

        if (resources.getEconomy() < 20) {
            game.setStatus(GameStatus.LOST);
            game.setDefeatReason(DefeatReason.ECONOMIC_COLLAPSE);
            return true;
        }

        // Check if ALL core citizens have approval < 25
        List<Citizen> coreCitizens = game.getCitizens().stream()
                .filter(c -> c.getCitizenType() == CitizenType.CORE)
                .toList();

        if (!coreCitizens.isEmpty() && coreCitizens.stream().allMatch(c -> c.getApproval() < 25)) {
            game.setStatus(GameStatus.LOST);
            game.setDefeatReason(DefeatReason.VOTED_OUT);
            return true;
        }

        return false;
    }

    /**
     * Determines the victory rank based on final resource levels and sets the game to WON.
     */
    private void determineVictory(Game game) {
        GameResources resources = game.getResources();
        int ecology = resources.getEcology();
        int economy = resources.getEconomy();
        int research = resources.getResearch();

        game.setStatus(GameStatus.WON);

        if (ecology > 80 && economy > 80 && research > 75) {
            game.setResultRank(GameRank.GOLD);
        } else if (ecology > 65 && economy > 65) {
            game.setResultRank(GameRank.SILVER);
        } else {
            game.setResultRank(GameRank.BRONZE);
        }
    }
}

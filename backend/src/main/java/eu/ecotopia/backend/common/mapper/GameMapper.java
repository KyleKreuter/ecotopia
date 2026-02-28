package eu.ecotopia.backend.common.mapper;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.common.dto.CitizenResponse;
import eu.ecotopia.backend.common.dto.GameRoundResponse;
import eu.ecotopia.backend.common.dto.GameStateResponse;
import eu.ecotopia.backend.common.dto.PromiseResponse;
import eu.ecotopia.backend.common.dto.ResourcesResponse;
import eu.ecotopia.backend.common.dto.TileResponse;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.tile.model.Tile;

import java.util.List;

/**
 * Static utility mapper that converts domain entities to API response DTOs.
 */
public final class GameMapper {

    private GameMapper() {
        // Utility class — no instantiation
    }

    public static GameStateResponse toGameStateResponse(Game game) {
        List<TileResponse> tiles = game.getTiles().stream()
                .map(GameMapper::toTileResponse)
                .toList();

        List<CitizenResponse> citizens = game.getCitizens().stream()
                .map(GameMapper::toCitizenResponse)
                .toList();

        List<PromiseResponse> promises = game.getPromises().stream()
                .map(GameMapper::toPromiseResponse)
                .toList();

        GameRoundResponse currentRoundInfo = game.getRounds().stream()
                .filter(r -> r.getRoundNumber() == game.getCurrentRound())
                .findFirst()
                .map(GameMapper::toGameRoundResponse)
                .orElse(null);

        return new GameStateResponse(
                game.getId(),
                game.getCurrentRound(),
                game.getStatus().name(),
                game.getResultRank() != null ? game.getResultRank().name() : null,
                game.getDefeatReason() != null ? game.getDefeatReason().name() : null,
                toResourcesResponse(game.getResources()),
                tiles,
                citizens,
                promises,
                currentRoundInfo,
                game.getCreatedAt(),
                game.getUpdatedAt()
        );
    }

    public static TileResponse toTileResponse(Tile tile) {
        return new TileResponse(
                tile.getX(),
                tile.getY(),
                tile.getTileType().name(),
                tile.getRoundsInCurrentState()
        );
    }

    public static CitizenResponse toCitizenResponse(Citizen citizen) {
        return new CitizenResponse(
                citizen.getId(),
                citizen.getName(),
                citizen.getCitizenType().name(),
                citizen.getProfession(),
                citizen.getAge(),
                citizen.getPersonality(),
                citizen.getApproval(),
                citizen.getOpeningSpeech(),
                citizen.getRemainingRounds()
        );
    }

    public static PromiseResponse toPromiseResponse(Promise promise) {
        return new PromiseResponse(
                promise.getId(),
                promise.getText(),
                promise.getRoundMade(),
                promise.getDeadline(),
                promise.getStatus().name(),
                promise.getCitizen() != null ? promise.getCitizen().getName() : null
        );
    }

    public static GameRoundResponse toGameRoundResponse(GameRound round) {
        return new GameRoundResponse(
                round.getRoundNumber(),
                round.getRemainingActions(),
                round.getSpeechText()
        );
    }

    public static ResourcesResponse toResourcesResponse(GameResources resources) {
        return new ResourcesResponse(
                resources.getEcology(),
                resources.getEconomy(),
                resources.getResearch()
        );
    }
}

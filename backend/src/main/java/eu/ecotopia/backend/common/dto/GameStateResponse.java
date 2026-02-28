package eu.ecotopia.backend.common.dto;

import java.time.Instant;
import java.util.List;

public record GameStateResponse(
        Long id,
        int currentRound,
        String status,
        String resultRank,
        String defeatReason,
        ResourcesResponse resources,
        List<TileResponse> tiles,
        List<CitizenResponse> citizens,
        List<PromiseResponse> promises,
        GameRoundResponse currentRoundInfo,
        Instant createdAt,
        Instant updatedAt
) {
}

package eu.ecotopia.backend.common.dto;

/**
 * Represents an individual citizen's reaction to a player's speech.
 */
public record CitizenReactionResponse(
        String citizenName,
        String dialogue,
        String tone,
        int approvalDelta
) {
}

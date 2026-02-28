package eu.ecotopia.backend.common.dto;

/**
 * Represents a contradiction detected between a player's speech and their past actions.
 */
public record ContradictionResponse(
        String description,
        String speechQuote,
        String contradictingAction,
        String severity
) {
}

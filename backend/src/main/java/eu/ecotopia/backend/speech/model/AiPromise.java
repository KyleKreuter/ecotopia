package eu.ecotopia.backend.speech.model;

/**
 * Represents a promise extracted by the AI from a player's speech.
 * Used for JSON deserialization of AI responses.
 */
public record AiPromise(
        String text,
        String type,
        String targetCitizen,
        Integer deadlineRound
) {
}

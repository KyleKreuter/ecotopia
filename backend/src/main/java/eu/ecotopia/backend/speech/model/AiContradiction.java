package eu.ecotopia.backend.speech.model;

/**
 * Represents a contradiction detected by the AI between a speech and past actions.
 * Used for JSON deserialization of AI responses.
 */
public record AiContradiction(
        String description,
        String speechQuote,
        String contradictingAction,
        String severity
) {
}

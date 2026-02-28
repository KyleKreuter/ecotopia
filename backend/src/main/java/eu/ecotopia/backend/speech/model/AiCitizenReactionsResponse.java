package eu.ecotopia.backend.speech.model;

import java.util.List;

/**
 * Top-level AI response for citizen reactions to a speech.
 * Used for JSON deserialization of the structured AI output.
 */
public record AiCitizenReactionsResponse(
        List<AiCitizenReaction> reactions
) {
}

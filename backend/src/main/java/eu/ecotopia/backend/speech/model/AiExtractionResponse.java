package eu.ecotopia.backend.speech.model;

import java.util.List;

/**
 * Top-level AI response for promise extraction and contradiction detection.
 * Used for JSON deserialization of the structured AI output.
 */
public record AiExtractionResponse(
        List<AiPromise> promises,
        List<AiContradiction> contradictions
) {
}

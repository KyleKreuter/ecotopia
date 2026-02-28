package eu.ecotopia.backend.common.dto;

import java.util.List;

/**
 * Response DTO for the speech processing pipeline.
 * Contains extracted promises, detected contradictions, and citizen reactions.
 */
public record SpeechResponse(
        List<PromiseResponse> extractedPromises,
        List<ContradictionResponse> contradictions,
        List<CitizenReactionResponse> citizenReactions
) {
}

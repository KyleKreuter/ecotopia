package eu.ecotopia.backend.common.dto;

import java.util.List;

public record SpeechResponse(List<String> citizenReactions, List<String> extractedPromises) {
}

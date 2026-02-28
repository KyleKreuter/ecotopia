package eu.ecotopia.backend.common.dto;

import jakarta.validation.constraints.NotBlank;

public record SpeechRequest(@NotBlank String text) {
}

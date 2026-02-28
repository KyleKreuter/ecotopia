package eu.ecotopia.backend.common.dto;

import java.time.Instant;

public record ErrorResponse(int status, String message, Instant timestamp) {
}

package eu.ecotopia.backend.common.dto;

public record PromiseResponse(
        Long id,
        String text,
        int roundMade,
        Integer deadline,
        String status,
        String citizenName
) {
}

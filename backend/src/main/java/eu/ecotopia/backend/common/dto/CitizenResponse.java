package eu.ecotopia.backend.common.dto;

public record CitizenResponse(
        Long id,
        String name,
        String citizenType,
        String profession,
        Integer age,
        String personality,
        int approval,
        String openingSpeech,
        Integer remainingRounds
) {
}

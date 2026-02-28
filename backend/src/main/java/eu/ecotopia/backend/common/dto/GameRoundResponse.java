package eu.ecotopia.backend.common.dto;

public record GameRoundResponse(int roundNumber, int remainingActions, String speechText) {
}

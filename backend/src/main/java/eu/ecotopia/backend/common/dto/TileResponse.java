package eu.ecotopia.backend.common.dto;

public record TileResponse(int x, int y, String tileType, int roundsInCurrentState) {
}

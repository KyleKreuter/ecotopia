package eu.ecotopia.backend.common.dto;

import eu.ecotopia.backend.tile.model.TileActionType;
import jakarta.validation.constraints.NotNull;

public record ExecuteActionRequest(@NotNull TileActionType action) {
}

package eu.ecotopia.backend.tile.controller;

import eu.ecotopia.backend.common.dto.ExecuteActionRequest;
import eu.ecotopia.backend.common.dto.GameStateResponse;
import eu.ecotopia.backend.common.dto.TileActionResponse;
import eu.ecotopia.backend.common.mapper.GameMapper;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.service.GameService;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileActionType;
import eu.ecotopia.backend.tile.repository.TileRepository;
import eu.ecotopia.backend.tile.service.TileActionService;
import jakarta.persistence.EntityNotFoundException;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/games/{gameId}/tiles")
@RequiredArgsConstructor
public class TileController {

    private final GameService gameService;
    private final TileRepository tileRepository;
    private final TileActionService tileActionService;

    @GetMapping("/{x}/{y}/actions")
    public ResponseEntity<TileActionResponse> getAvailableActions(
            @PathVariable Long gameId, @PathVariable int x, @PathVariable int y) {
        Game game = gameService.getGame(gameId);
        Tile tile = tileRepository.findByGameIdAndXAndY(gameId, x, y)
                .orElseThrow(() -> new EntityNotFoundException("Tile not found at (" + x + "," + y + ")"));
        List<TileActionType> actions = tileActionService.getAvailableActions(game, tile);
        List<String> actionNames = actions.stream().map(TileActionType::name).toList();
        return ResponseEntity.ok(new TileActionResponse(actionNames));
    }

    @PostMapping("/{x}/{y}/actions")
    public ResponseEntity<GameStateResponse> executeAction(
            @PathVariable Long gameId, @PathVariable int x, @PathVariable int y,
            @Valid @RequestBody ExecuteActionRequest request) {
        Game game = gameService.executeAction(gameId, x, y, request.action());
        return ResponseEntity.ok(GameMapper.toGameStateResponse(game));
    }
}

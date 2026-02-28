package eu.ecotopia.backend.game.controller;

import eu.ecotopia.backend.common.dto.GameStateResponse;
import eu.ecotopia.backend.common.mapper.GameMapper;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.repository.GameRepository;
import eu.ecotopia.backend.game.service.GameService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller for game lifecycle operations.
 * Handles creation, retrieval, and deletion of games.
 */
@RestController
@RequestMapping("/api/games")
@RequiredArgsConstructor
public class GameController {

    private final GameService gameService;
    private final GameRepository gameRepository;

    /**
     * Creates a new game with initialized tiles, citizens, and starting resources.
     *
     * @return the created game state with HTTP 201
     */
    @PostMapping
    public ResponseEntity<GameStateResponse> createGame() {
        Game game = gameService.createNewGame();
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(GameMapper.toGameStateResponse(game));
    }

    /**
     * Retrieves the current state of an existing game.
     *
     * @param id the game ID
     * @return the game state with HTTP 200
     */
    @GetMapping("/{id}")
    public ResponseEntity<GameStateResponse> getGame(@PathVariable Long id) {
        Game game = gameService.getGame(id);
        return ResponseEntity.ok(GameMapper.toGameStateResponse(game));
    }

    /**
     * Deletes a game by its ID.
     *
     * @param id the game ID
     * @return HTTP 204 No Content
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteGame(@PathVariable Long id) {
        gameRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}

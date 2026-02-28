package eu.ecotopia.backend.round.controller;

import eu.ecotopia.backend.common.dto.GameStateResponse;
import eu.ecotopia.backend.common.dto.PromiseResponse;
import eu.ecotopia.backend.common.mapper.GameMapper;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.service.GameService;
import eu.ecotopia.backend.promise.repository.PromiseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/games/{gameId}")
@RequiredArgsConstructor
public class RoundController {

    private final GameService gameService;
    private final PromiseRepository promiseRepository;

    @PostMapping("/end-round")
    public ResponseEntity<GameStateResponse> endRound(@PathVariable Long gameId) {
        Game game = gameService.advanceRound(gameId);
        return ResponseEntity.ok(GameMapper.toGameStateResponse(game));
    }

    @GetMapping("/promises")
    public ResponseEntity<List<PromiseResponse>> getPromises(@PathVariable Long gameId) {
        List<PromiseResponse> promises = promiseRepository.findByGameId(gameId).stream()
                .map(GameMapper::toPromiseResponse)
                .toList();
        return ResponseEntity.ok(promises);
    }
}

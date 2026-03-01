package eu.ecotopia.backend.round.controller;

import eu.ecotopia.backend.common.dto.GameStateResponse;
import eu.ecotopia.backend.common.dto.PromiseResponse;
import eu.ecotopia.backend.common.mapper.GameMapper;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.service.GameService;
import eu.ecotopia.backend.promise.repository.PromiseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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
@Slf4j
public class RoundController {

    private final GameService gameService;
    private final PromiseRepository promiseRepository;

    @PostMapping("/end-round")
    public ResponseEntity<GameStateResponse> endRound(@PathVariable Long gameId) {
        long start = System.currentTimeMillis();
        log.info("[GAME-{}] POST /end-round", gameId);
        Game game = gameService.advanceRound(gameId);
        log.info("[GAME-{}] end-round completed in {}ms — now round={}, status={}, resources=[eco={}, econ={}, res={}]",
                gameId, System.currentTimeMillis() - start, game.getCurrentRound(), game.getStatus(),
                game.getResources().getEcology(), game.getResources().getEconomy(), game.getResources().getResearch());
        return ResponseEntity.ok(GameMapper.toGameStateResponse(game));
    }

    @GetMapping("/promises")
    public ResponseEntity<List<PromiseResponse>> getPromises(@PathVariable Long gameId) {
        log.info("[GAME-{}] GET /promises", gameId);
        List<PromiseResponse> promises = promiseRepository.findByGameId(gameId).stream()
                .map(GameMapper::toPromiseResponse)
                .toList();
        log.info("[GAME-{}] returning {} promises", gameId, promises.size());
        return ResponseEntity.ok(promises);
    }
}

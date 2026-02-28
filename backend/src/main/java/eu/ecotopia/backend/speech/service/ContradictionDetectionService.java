package eu.ecotopia.backend.speech.service;

import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Service dedicated to contradiction detection between player speech and past actions/promises.
 * Delegates to {@link PromiseExtractionService} which performs both extraction and contradiction
 * detection in a single AI call for efficiency.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class ContradictionDetectionService {

    private final PromiseExtractionService promiseExtractionService;

    /**
     * Detects contradictions between the player's current speech, their active promises,
     * and their recent tile actions. This delegates to the extraction service which handles
     * both promise extraction and contradiction detection in one AI call.
     *
     * @param game       the current game state
     * @param speechText the player's speech text
     * @return list of detected contradictions
     */
    public List<AiContradiction> detectContradictions(Game game, String speechText) {
        AiExtractionResponse response = promiseExtractionService.extract(game, speechText);
        List<AiContradiction> contradictions = response.contradictions();

        if (contradictions != null && !contradictions.isEmpty()) {
            log.info("Detected {} contradictions in game {} round {}",
                    contradictions.size(), game.getId(), game.getCurrentRound());
            for (AiContradiction c : contradictions) {
                log.debug("Contradiction [{}]: {} - action: {}",
                        c.severity(), c.description(), c.contradictingAction());
            }
        }

        return contradictions != null ? contradictions : List.of();
    }

    /**
     * Filters contradictions by minimum severity level.
     *
     * @param contradictions the full list of contradictions
     * @param minSeverity    minimum severity to include ("low", "medium", "high")
     * @return filtered list of contradictions at or above the specified severity
     */
    public List<AiContradiction> filterBySeverity(List<AiContradiction> contradictions, String minSeverity) {
        int minLevel = severityToLevel(minSeverity);
        return contradictions.stream()
                .filter(c -> severityToLevel(c.severity()) >= minLevel)
                .toList();
    }

    private int severityToLevel(String severity) {
        if (severity == null) return 0;
        return switch (severity.toLowerCase()) {
            case "high" -> 3;
            case "medium" -> 2;
            case "low" -> 1;
            default -> 0;
        };
    }
}

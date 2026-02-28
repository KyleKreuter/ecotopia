package eu.ecotopia.backend.speech.service;

import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.common.dto.CitizenReactionResponse;
import eu.ecotopia.backend.common.dto.ContradictionResponse;
import eu.ecotopia.backend.common.dto.PromiseResponse;
import eu.ecotopia.backend.common.dto.SpeechResponse;
import eu.ecotopia.backend.common.mapper.GameMapper;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.game.repository.GameRepository;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import eu.ecotopia.backend.promise.repository.PromiseRepository;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.round.repository.GameRoundRepository;
import eu.ecotopia.backend.speech.model.AiCitizenReaction;
import eu.ecotopia.backend.speech.model.AiCitizenReactionsResponse;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Orchestrator service for the full AI speech processing pipeline.
 * Coordinates promise extraction, contradiction detection, citizen reactions,
 * and all associated state mutations within a single transaction.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SpeechService {

    private final GameRepository gameRepository;
    private final PromiseRepository promiseRepository;
    private final GameRoundRepository gameRoundRepository;
    private final PromiseExtractionService promiseExtractionService;
    private final CitizenReactionService citizenReactionService;

    /**
     * Processes a player's speech through the full AI pipeline:
     * <ol>
     *   <li>Load and validate game state</li>
     *   <li>Save speech text to the current round</li>
     *   <li>Extract promises and detect contradictions via AI</li>
     *   <li>Persist extracted promises</li>
     *   <li>Mark contradicted promises as BROKEN</li>
     *   <li>Generate citizen reactions via AI</li>
     *   <li>Apply approval deltas to citizens</li>
     *   <li>Save game state and return the response</li>
     * </ol>
     *
     * @param gameId     the ID of the game
     * @param speechText the player's speech text
     * @return a SpeechResponse containing extracted promises, contradictions, and citizen reactions
     * @throws EntityNotFoundException if the game does not exist
     * @throws IllegalStateException   if the game is not in RUNNING status
     */
    @Transactional
    public SpeechResponse processSpeech(Long gameId, String speechText) {
        log.info("Processing speech for game {} (length: {} chars)", gameId, speechText.length());

        // 1. Load game with all associations
        Game game = gameRepository.findById(gameId)
                .orElseThrow(() -> new EntityNotFoundException("Game not found with id: " + gameId));

        // 2. Validate game status
        if (game.getStatus() != GameStatus.RUNNING) {
            throw new IllegalStateException(
                    "Cannot process speech: game %d is not running (status: %s)".formatted(gameId, game.getStatus()));
        }

        // 3. Save speech text to the current round
        saveSpeechToCurrentRound(game, speechText);

        // 4. Extract promises and detect contradictions via AI
        log.info("Calling AI extraction for game {} round {}", gameId, game.getCurrentRound());
        AiExtractionResponse extractionResult = promiseExtractionService.extractAndPersist(game, speechText);
        log.info("Extraction complete: {} promises, {} contradictions",
                extractionResult.promises() != null ? extractionResult.promises().size() : 0,
                extractionResult.contradictions() != null ? extractionResult.contradictions().size() : 0);

        // 5. Get the newly persisted promises for response mapping (they now have IDs)
        // The promises were added to game.getPromises() by extractAndPersist via game.addPromise()
        List<Promise> newlyPersistedPromises = getNewlyPersistedPromises(game, extractionResult);

        // 6. Update broken promise statuses for detected contradictions
        updateBrokenPromises(game, extractionResult.contradictions());

        // 7. Generate citizen reactions via AI
        log.info("Calling AI citizen reactions for game {} round {}", gameId, game.getCurrentRound());
        AiCitizenReactionsResponse reactionsResult =
                citizenReactionService.generateReactions(game, speechText, extractionResult);
        log.info("Citizen reactions complete: {} reactions",
                reactionsResult.reactions() != null ? reactionsResult.reactions().size() : 0);

        // 8. Apply approval deltas to citizens
        applyApprovalDeltas(game, reactionsResult.reactions());

        // 9. Save game state
        gameRepository.save(game);
        log.info("Game {} state saved after speech processing", gameId);

        // 10. Map everything to SpeechResponse
        return buildSpeechResponse(newlyPersistedPromises, extractionResult, reactionsResult);
    }

    /**
     * Saves the speech text to the current game round entity.
     */
    private void saveSpeechToCurrentRound(Game game, String speechText) {
        GameRound currentRound = gameRoundRepository
                .findByGameIdAndRoundNumber(game.getId(), game.getCurrentRound())
                .orElseThrow(() -> new EntityNotFoundException(
                        "GameRound not found for game %d round %d".formatted(game.getId(), game.getCurrentRound())));

        currentRound.setSpeechText(speechText);
        gameRoundRepository.save(currentRound);
        log.debug("Saved speech text to game {} round {}", game.getId(), game.getCurrentRound());
    }

    /**
     * Retrieves the promises that were just persisted in this speech processing cycle.
     * These are the promises made in the current round.
     */
    private List<Promise> getNewlyPersistedPromises(Game game, AiExtractionResponse extractionResult) {
        if (extractionResult.promises() == null || extractionResult.promises().isEmpty()) {
            return List.of();
        }

        // The newly persisted promises are those made in the current round
        return game.getPromises().stream()
                .filter(p -> p.getRoundMade() == game.getCurrentRound())
                .filter(p -> p.getStatus() == PromiseStatus.ACTIVE)
                .toList();
    }

    /**
     * Marks active promises as BROKEN when contradictions are detected.
     * Matches contradictions against active promises by checking if the contradiction
     * description or contradicting action references a known promise.
     */
    private void updateBrokenPromises(Game game, List<AiContradiction> contradictions) {
        if (contradictions == null || contradictions.isEmpty()) {
            return;
        }

        List<Promise> activePromises = promiseRepository.findByGameIdAndStatus(game.getId(), PromiseStatus.ACTIVE);

        if (activePromises.isEmpty()) {
            log.debug("No active promises to mark as broken for game {}", game.getId());
            return;
        }

        int brokenCount = 0;
        for (AiContradiction contradiction : contradictions) {
            // Only mark promises as broken for medium/high severity contradictions
            if ("low".equalsIgnoreCase(contradiction.severity())) {
                continue;
            }

            for (Promise promise : activePromises) {
                if (isPromiseContradicted(promise, contradiction)) {
                    promise.setStatus(PromiseStatus.BROKEN);
                    promiseRepository.save(promise);
                    brokenCount++;
                    log.info("Marked promise {} as BROKEN: '{}' (contradiction: {})",
                            promise.getId(), promise.getText(), contradiction.description());
                    break; // One contradiction breaks one promise at most
                }
            }
        }

        if (brokenCount > 0) {
            log.info("Marked {} promises as BROKEN for game {}", brokenCount, game.getId());
        }
    }

    /**
     * Determines whether a contradiction references a specific promise.
     * Uses a simple text similarity check against the contradiction description
     * and the contradicting action field.
     */
    private boolean isPromiseContradicted(Promise promise, AiContradiction contradiction) {
        String promiseTextLower = promise.getText().toLowerCase();
        String descriptionLower = contradiction.description() != null
                ? contradiction.description().toLowerCase() : "";
        String actionLower = contradiction.contradictingAction() != null
                ? contradiction.contradictingAction().toLowerCase() : "";

        // Check if the contradiction references this promise's text (partial match)
        return descriptionLower.contains(promiseTextLower)
                || actionLower.contains(promiseTextLower)
                || containsSignificantOverlap(promiseTextLower, descriptionLower)
                || containsSignificantOverlap(promiseTextLower, actionLower);
    }

    /**
     * Checks if there is significant word overlap between two texts.
     * A match is considered significant if at least half of the words in the
     * shorter text appear in the longer text.
     */
    private boolean containsSignificantOverlap(String text1, String text2) {
        if (text1.isBlank() || text2.isBlank()) {
            return false;
        }

        String[] words1 = text1.split("\\s+");
        if (words1.length < 3) {
            return false; // Too few words for reliable matching
        }

        long matchCount = 0;
        for (String word : words1) {
            if (word.length() > 3 && text2.contains(word)) {
                matchCount++;
            }
        }

        // Require at least half of significant words to match
        return matchCount >= (words1.length / 2.0);
    }

    /**
     * Applies approval deltas from citizen reactions to the corresponding citizens.
     * Approval values are clamped to the range [0, 100].
     */
    private void applyApprovalDeltas(Game game, List<AiCitizenReaction> reactions) {
        if (reactions == null || reactions.isEmpty()) {
            return;
        }

        List<Citizen> citizens = game.getCitizens();

        for (AiCitizenReaction reaction : reactions) {
            citizens.stream()
                    .filter(c -> c.getName() != null && c.getName().equalsIgnoreCase(reaction.citizenName()))
                    .findFirst()
                    .ifPresentOrElse(
                            citizen -> {
                                int oldApproval = citizen.getApproval();
                                int newApproval = Math.max(0, Math.min(100, oldApproval + reaction.approvalDelta()));
                                citizen.setApproval(newApproval);
                                log.debug("Citizen '{}' approval: {} -> {} (delta: {})",
                                        citizen.getName(), oldApproval, newApproval, reaction.approvalDelta());
                            },
                            () -> log.warn("Citizen '{}' not found in game {} for reaction application",
                                    reaction.citizenName(), game.getId())
                    );
        }
    }

    /**
     * Builds the final SpeechResponse DTO from the AI pipeline results.
     */
    private SpeechResponse buildSpeechResponse(List<Promise> newPromises,
                                                AiExtractionResponse extractionResult,
                                                AiCitizenReactionsResponse reactionsResult) {
        // Map persisted promises to response DTOs (with database IDs)
        List<PromiseResponse> promiseResponses = newPromises.stream()
                .map(GameMapper::toPromiseResponse)
                .toList();

        // Map contradictions to response DTOs
        List<ContradictionResponse> contradictionResponses = extractionResult.contradictions() != null
                ? extractionResult.contradictions().stream()
                .map(c -> new ContradictionResponse(
                        c.description(),
                        c.speechQuote(),
                        c.contradictingAction(),
                        c.severity()))
                .toList()
                : List.of();

        // Map citizen reactions to response DTOs
        List<CitizenReactionResponse> reactionResponses = reactionsResult.reactions() != null
                ? reactionsResult.reactions().stream()
                .map(r -> new CitizenReactionResponse(
                        r.citizenName(),
                        r.dialogue(),
                        r.tone(),
                        r.approvalDelta()))
                .toList()
                : List.of();

        return new SpeechResponse(promiseResponses, contradictionResponses, reactionResponses);
    }
}

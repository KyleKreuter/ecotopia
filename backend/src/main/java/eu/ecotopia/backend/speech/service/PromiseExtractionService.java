package eu.ecotopia.backend.speech.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.repository.CitizenRepository;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import eu.ecotopia.backend.promise.repository.PromiseRepository;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import eu.ecotopia.backend.speech.model.AiPromise;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service responsible for extracting promises and detecting contradictions from player speeches
 * using Spring AI ChatClient. Combines both extraction and contradiction detection in a single
 * AI call for efficiency.
 */
@Service
@Slf4j
public class PromiseExtractionService {

    private final ChatClient chatClient;
    private final ObjectMapper objectMapper;
    private final PromiseRepository promiseRepository;
    private final CitizenRepository citizenRepository;

    @Value("${ecotopia.ai.extraction-model:}")
    private String extractionModel;

    public PromiseExtractionService(
            ChatClient.Builder chatClientBuilder,
            ObjectMapper objectMapper,
            PromiseRepository promiseRepository,
            CitizenRepository citizenRepository) {
        this.chatClient = chatClientBuilder.build();
        this.objectMapper = objectMapper;
        this.promiseRepository = promiseRepository;
        this.citizenRepository = citizenRepository;
    }

    static final String SYSTEM_PROMPT = """
            You are an AI analyst for the game Ecotopia. Your job is to analyze the player's speech \
            and extract promises they make (explicit or implicit) and detect contradictions between \
            their words and their past actions or active promises.

            ## Rules
            - Always respond with valid JSON only. No markdown, no code fences, no extra text.
            - Extract both explicit promises ("I promise to...", "I will...") and implicit promises \
              ("The forest stays", "We protect nature") from the speech.
            - Compare the current speech and recent tile actions against ALL active promises to detect contradictions.
            - Be conservative with contradiction severity:
              - "low": minor inconsistency, could be interpreted differently
              - "medium": clear contradiction but could have strategic justification
              - "high": blatant broken promise with no reasonable explanation
            - For promise type, use "explicit" or "implicit".
            - For targetCitizen, use the citizen's exact name if the promise is directed at a specific citizen, otherwise null.
            - For deadlineRound, extract only if the player mentions a specific round/turn deadline, otherwise null.

            ## Response Format
            Respond with exactly this JSON structure:
            {
              "promises": [
                {"text": "promise description", "type": "explicit|implicit", "targetCitizen": "name or null", "deadlineRound": null}
              ],
              "contradictions": [
                {"description": "what the contradiction is", "speechQuote": "relevant quote from speech", "contradictingAction": "action description", "severity": "low|medium|high"}
              ]
            }

            If there are no promises, return an empty array for "promises".
            If there are no contradictions, return an empty array for "contradictions".
            """;

    /**
     * Extracts promises and detects contradictions from a player's speech using AI analysis.
     *
     * @param game       the current game state
     * @param speechText the player's speech text
     * @return the AI extraction response containing promises and contradictions
     */
    public AiExtractionResponse extract(Game game, String speechText) {
        String userPrompt = buildUserPrompt(game, speechText);

        log.debug("Sending extraction prompt for game {} round {}", game.getId(), game.getCurrentRound());

        var requestSpec = chatClient.prompt()
                .system(SYSTEM_PROMPT)
                .user(userPrompt);

        if (extractionModel != null && !extractionModel.isBlank()) {
            requestSpec = requestSpec.options(OpenAiChatOptions.builder().model(extractionModel).build());
        }

        String response = requestSpec.call().content();

        log.debug("AI extraction response: {}", response);

        return parseResponse(response);
    }

    /**
     * Extracts promises and contradictions, then persists the extracted promises to the database.
     *
     * @param game       the current game state
     * @param speechText the player's speech text
     * @return the AI extraction response containing promises and contradictions
     */
    @Transactional
    public AiExtractionResponse extractAndPersist(Game game, String speechText) {
        AiExtractionResponse aiResponse = extract(game, speechText);
        persistPromises(game, aiResponse.promises());
        return aiResponse;
    }

    /**
     * Builds the user prompt with full game context for the AI to analyze.
     */
    String buildUserPrompt(Game game, String speechText) {
        StringBuilder prompt = new StringBuilder();

        // Game context
        prompt.append("## Game Context\n");
        prompt.append("Current Round: ").append(game.getCurrentRound()).append("\n");
        if (game.getResources() != null) {
            prompt.append("Resources: Ecology=").append(game.getResources().getEcology())
                    .append(", Economy=").append(game.getResources().getEconomy())
                    .append(", Research=").append(game.getResources().getResearch())
                    .append("\n");
        }

        // Citizens
        List<Citizen> citizens = game.getCitizens();
        if (citizens != null && !citizens.isEmpty()) {
            prompt.append("\n## Citizens\n");
            for (Citizen c : citizens) {
                prompt.append("- ").append(c.getName())
                        .append(" (").append(c.getProfession()).append(")")
                        .append(", approval: ").append(c.getApproval()).append("%\n");
            }
        }

        // Active promises from previous rounds
        List<Promise> activePromises = promiseRepository.findByGameIdAndStatus(game.getId(), PromiseStatus.ACTIVE);
        if (!activePromises.isEmpty()) {
            prompt.append("\n## Active Promises\n");
            for (Promise p : activePromises) {
                prompt.append("- Round ").append(p.getRoundMade()).append(": \"").append(p.getText()).append("\"");
                if (p.getCitizen() != null) {
                    prompt.append(" (to ").append(p.getCitizen().getName()).append(")");
                }
                if (p.getDeadline() != null) {
                    prompt.append(" [deadline: round ").append(p.getDeadline()).append("]");
                }
                prompt.append("\n");
            }
        }

        // Previous speeches
        List<GameRound> rounds = game.getRounds();
        if (rounds != null && !rounds.isEmpty()) {
            List<GameRound> previousRounds = rounds.stream()
                    .filter(r -> r.getSpeechText() != null && !r.getSpeechText().isBlank())
                    .filter(r -> r.getRoundNumber() < game.getCurrentRound())
                    .sorted((a, b) -> Integer.compare(a.getRoundNumber(), b.getRoundNumber()))
                    .toList();

            if (!previousRounds.isEmpty()) {
                prompt.append("\n## Previous Speeches\n");
                for (GameRound r : previousRounds) {
                    prompt.append("Round ").append(r.getRoundNumber()).append(": \"")
                            .append(r.getSpeechText()).append("\"\n");
                }
            }
        }

        // Current tile layout (for action context)
        if (game.getTiles() != null && !game.getTiles().isEmpty()) {
            prompt.append("\n## Current Tile Map\n");
            String tileInfo = game.getTiles().stream()
                    .map(t -> "(%d,%d): %s".formatted(t.getX(), t.getY(), t.getTileType()))
                    .collect(Collectors.joining(", "));
            prompt.append(tileInfo).append("\n");
        }

        // Current speech to analyze
        prompt.append("\n## Current Speech (Round ").append(game.getCurrentRound()).append(")\n");
        prompt.append(speechText).append("\n");

        return prompt.toString();
    }

    /**
     * Parses the AI JSON response into an AiExtractionResponse record.
     * Handles common parsing issues like markdown code fences in the response.
     */
    AiExtractionResponse parseResponse(String response) {
        if (response == null || response.isBlank()) {
            log.warn("Received empty response from AI, returning empty extraction result");
            return new AiExtractionResponse(List.of(), List.of());
        }

        // Strip markdown code fences if the AI included them despite instructions
        String cleaned = response.strip();
        if (cleaned.startsWith("```")) {
            cleaned = cleaned.replaceFirst("```(?:json)?\\s*", "");
            if (cleaned.endsWith("```")) {
                cleaned = cleaned.substring(0, cleaned.lastIndexOf("```"));
            }
            cleaned = cleaned.strip();
        }

        try {
            return objectMapper.readValue(cleaned, AiExtractionResponse.class);
        } catch (JsonProcessingException e) {
            log.error("Failed to parse AI extraction response: {}", cleaned, e);
            return new AiExtractionResponse(List.of(), List.of());
        }
    }

    /**
     * Persists extracted promises as Promise entities linked to the game.
     */
    void persistPromises(Game game, List<AiPromise> aiPromises) {
        if (aiPromises == null || aiPromises.isEmpty()) {
            return;
        }

        for (AiPromise aiPromise : aiPromises) {
            Promise promise = Promise.builder()
                    .text(aiPromise.text())
                    .roundMade(game.getCurrentRound())
                    .deadline(aiPromise.deadlineRound())
                    .status(PromiseStatus.ACTIVE)
                    .build();

            // Link target citizen if specified
            if (aiPromise.targetCitizen() != null && !aiPromise.targetCitizen().isBlank()) {
                findCitizenByName(game, aiPromise.targetCitizen())
                        .ifPresent(promise::setCitizen);
            }

            game.addPromise(promise);
        }

        log.info("Persisted {} promises for game {} round {}",
                aiPromises.size(), game.getId(), game.getCurrentRound());
    }

    /**
     * Finds a citizen by name within the game's citizen list.
     */
    private Optional<Citizen> findCitizenByName(Game game, String name) {
        if (game.getCitizens() == null) {
            return Optional.empty();
        }
        return game.getCitizens().stream()
                .filter(c -> c.getName() != null && c.getName().equalsIgnoreCase(name))
                .findFirst();
    }
}

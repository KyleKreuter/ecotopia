package eu.ecotopia.backend.speech.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.speech.model.AiCitizenReactionsResponse;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import eu.ecotopia.backend.speech.model.AiPromise;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service that generates in-character AI reactions for each citizen based on the player's speech.
 * Uses Spring AI ChatClient to communicate with the configured LLM provider.
 */
@Slf4j
@Service
public class CitizenReactionService {

    private final ChatClient chatClient;
    private final ObjectMapper objectMapper;

    public CitizenReactionService(ChatClient.Builder chatClientBuilder, ObjectMapper objectMapper) {
        this.chatClient = chatClientBuilder.build();
        this.objectMapper = objectMapper;
    }

    /**
     * Generates in-character citizen reactions to the player's speech using AI.
     *
     * @param game             the current game state including citizens, resources, and history
     * @param speechText       the player's speech text
     * @param extractionResult the extraction result containing promises and contradictions
     * @return AI-generated reactions for each citizen
     */
    public AiCitizenReactionsResponse generateReactions(Game game, String speechText,
                                                         AiExtractionResponse extractionResult) {
        String systemPrompt = buildSystemPrompt(game, extractionResult);
        String userPrompt = buildUserPrompt(speechText);

        log.info("Generating citizen reactions for game {} round {}", game.getId(), game.getCurrentRound());
        log.debug("System prompt length: {} chars", systemPrompt.length());

        String response = chatClient.prompt()
                .system(systemPrompt)
                .user(userPrompt)
                .call()
                .content();

        log.debug("Raw AI response for citizen reactions: {}", response);

        return parseResponse(response);
    }

    /**
     * Builds the system prompt with full game context, citizen profiles, and reaction rules.
     */
    private String buildSystemPrompt(Game game, AiExtractionResponse extractionResult) {
        StringBuilder prompt = new StringBuilder();

        prompt.append("""
                You are the reaction engine for a political simulation game called Ecotopia.
                The player is the mayor of a small town making speeches to their citizens.
                You must generate in-character reactions for EACH citizen listed below.

                """);

        // Game context
        appendGameContext(prompt, game);

        // Citizen profiles
        appendCitizenProfiles(prompt, game.getCitizens());

        // Extraction results (promises and contradictions)
        appendExtractionResults(prompt, extractionResult);

        // Previous promises (history)
        appendPromiseHistory(prompt, game);

        // Previous speeches summary
        appendSpeechHistory(prompt, game);

        // Personality guidelines
        appendPersonalityGuidelines(prompt);

        // Reaction rules
        appendReactionRules(prompt);

        // Output format
        appendOutputFormat(prompt, game.getCitizens());

        return prompt.toString();
    }

    private String buildUserPrompt(String speechText) {
        return "The mayor's speech:\n\n\"" + speechText + "\"";
    }

    private void appendGameContext(StringBuilder prompt, Game game) {
        prompt.append("=== GAME CONTEXT ===\n");
        prompt.append("Current round: ").append(game.getCurrentRound()).append(" of 10\n");

        if (game.getResources() != null) {
            prompt.append("Resources:\n");
            prompt.append("  - Ecology: ").append(game.getResources().getEcology()).append("/100\n");
            prompt.append("  - Economy: ").append(game.getResources().getEconomy()).append("/100\n");
            prompt.append("  - Research: ").append(game.getResources().getResearch()).append("/100\n");
        }

        prompt.append("\n");
    }

    private void appendCitizenProfiles(StringBuilder prompt, List<Citizen> citizens) {
        prompt.append("=== CITIZENS (generate a reaction for EACH) ===\n");

        for (Citizen citizen : citizens) {
            prompt.append("- ").append(citizen.getName())
                    .append(" (").append(citizen.getProfession())
                    .append(", age ").append(citizen.getAge())
                    .append(", type: ").append(citizen.getCitizenType().name())
                    .append(", current approval: ").append(citizen.getApproval()).append("/100)\n");
            prompt.append("  Personality: ").append(citizen.getPersonality()).append("\n");

            if (citizen.getCitizenType() == CitizenType.DYNAMIC && citizen.getRemainingRounds() != null) {
                prompt.append("  Remaining rounds in town: ").append(citizen.getRemainingRounds()).append("\n");
            }

            prompt.append("\n");
        }
    }

    private void appendExtractionResults(StringBuilder prompt, AiExtractionResponse extractionResult) {
        prompt.append("=== EXTRACTED PROMISES FROM THIS SPEECH ===\n");

        if (extractionResult.promises() == null || extractionResult.promises().isEmpty()) {
            prompt.append("No promises detected in this speech.\n");
        } else {
            for (AiPromise p : extractionResult.promises()) {
                prompt.append("- \"").append(p.text()).append("\"");
                if (p.type() != null) {
                    prompt.append(" (type: ").append(p.type()).append(")");
                }
                if (p.targetCitizen() != null) {
                    prompt.append(" [targeted at: ").append(p.targetCitizen()).append("]");
                }
                prompt.append("\n");
            }
        }

        prompt.append("\n=== DETECTED CONTRADICTIONS ===\n");

        if (extractionResult.contradictions() == null || extractionResult.contradictions().isEmpty()) {
            prompt.append("No contradictions detected.\n");
        } else {
            for (AiContradiction c : extractionResult.contradictions()) {
                prompt.append("- ").append(c.description()).append("\n");
                prompt.append("  Speech quote: \"").append(c.speechQuote()).append("\"\n");
                prompt.append("  Contradicting action: ").append(c.contradictingAction()).append("\n");
                prompt.append("  Severity: ").append(c.severity()).append("\n");
            }
        }

        prompt.append("\n");
    }

    private void appendPromiseHistory(StringBuilder prompt, Game game) {
        List<Promise> promises = game.getPromises();

        if (promises == null || promises.isEmpty()) {
            return;
        }

        prompt.append("=== PROMISE HISTORY ===\n");

        List<Promise> brokenPromises = promises.stream()
                .filter(p -> p.getStatus() == PromiseStatus.BROKEN)
                .toList();

        List<Promise> activePromises = promises.stream()
                .filter(p -> p.getStatus() == PromiseStatus.ACTIVE)
                .toList();

        List<Promise> keptPromises = promises.stream()
                .filter(p -> p.getStatus() == PromiseStatus.KEPT)
                .toList();

        if (!brokenPromises.isEmpty()) {
            prompt.append("BROKEN promises (important for Sarah!):\n");
            for (Promise p : brokenPromises) {
                prompt.append("  - \"").append(p.getText()).append("\" (made round ").append(p.getRoundMade()).append(")\n");
            }
        }

        if (!activePromises.isEmpty()) {
            prompt.append("Active promises (still pending):\n");
            for (Promise p : activePromises) {
                prompt.append("  - \"").append(p.getText()).append("\" (made round ").append(p.getRoundMade());
                if (p.getDeadline() != null) {
                    prompt.append(", deadline: round ").append(p.getDeadline());
                }
                prompt.append(")\n");
            }
        }

        if (!keptPromises.isEmpty()) {
            prompt.append("Kept promises: ").append(keptPromises.size()).append(" total\n");
        }

        prompt.append("\n");
    }

    private void appendSpeechHistory(StringBuilder prompt, Game game) {
        List<GameRound> previousRounds = game.getRounds().stream()
                .filter(r -> r.getRoundNumber() < game.getCurrentRound())
                .filter(r -> r.getSpeechText() != null)
                .sorted(Comparator.comparingInt(GameRound::getRoundNumber))
                .toList();

        if (previousRounds.isEmpty()) {
            return;
        }

        prompt.append("=== PREVIOUS SPEECHES (summary) ===\n");

        for (GameRound round : previousRounds) {
            String speechSummary = round.getSpeechText().length() > 200
                    ? round.getSpeechText().substring(0, 200) + "..."
                    : round.getSpeechText();
            prompt.append("Round ").append(round.getRoundNumber()).append(": \"").append(speechSummary).append("\"\n");
        }

        prompt.append("\n");
    }

    private void appendPersonalityGuidelines(StringBuilder prompt) {
        prompt.append("""
                === CITIZEN PERSONALITY GUIDELINES ===

                **Karl** (Factory Worker, 48): Conservative, family-oriented. He responds positively to:
                factory building, economic growth, job creation, stability. He responds negatively to:
                factory closures, heavy research spending, radical change. He solidarizes with workers
                who lose their jobs. He speaks plainly and worries about his family.

                **Mia** (Climate Activist, 24): Idealistic, impatient, passionate. She responds positively to:
                forest planting, demolishing fossil industry, renewable energy, fast climate action.
                She responds negatively to: new factories, deforestation, slow/incremental action.
                She uses emotional language and references generational justice.

                **Sarah** (Opposition Politician, 42): Strategic, opportunistic, sharp-tongued. She is
                ALMOST ALWAYS negative. She QUOTES the player VERBATIM when promises are broken or
                contradictions exist. She exploits citizen suffering and broken promises for political gain.
                She becomes quieter (smaller negative delta or even neutral) ONLY when the mayor performs
                exceptionally well with no contradictions. Her dialogue should be sharp and political.

                **Dynamic citizens**: React based on their personality field and their specific situation.
                If they just arrived, they react to the circumstances that brought them to the town hall.
                If two dynamic citizens are present from the same event (e.g., Oleg + Lena from a
                REPLACE_WITH_SOLAR action), they should reference each other in their dialogue.

                """);
    }

    private void appendReactionRules(StringBuilder prompt) {
        prompt.append("""
                === REACTION RULES ===

                1. Generate EXACTLY one reaction per citizen listed above.
                2. Each dialogue must be 2-4 sentences maximum.
                3. approvalDelta must be between -15 and +15 (integer).
                4. Sarah quotes the player verbatim when promises are broken or contradictions are detected.
                5. Dynamic citizens who just spawned should react to their personal situation.
                6. If two dynamic citizens are present from the same event, they should reference each other.
                7. Reference SPECIFIC parts of the player's speech in reactions.
                8. Keep dialogue authentic, emotional, and in-character.
                9. Valid tones: angry, hopeful, sarcastic, desperate, grateful, suspicious, neutral
                10. High approval citizens are more forgiving; low approval citizens are more critical.

                """);
    }

    private void appendOutputFormat(StringBuilder prompt, List<Citizen> citizens) {
        String citizenNames = citizens.stream()
                .map(Citizen::getName)
                .collect(Collectors.joining(", "));

        prompt.append("""
                === OUTPUT FORMAT ===

                Respond with ONLY valid JSON. No markdown, no code fences, no explanation.
                The JSON must match this exact structure:

                {
                  "reactions": [
                    {"citizenName": "Name", "dialogue": "...", "tone": "suspicious", "approvalDelta": -3}
                  ]
                }

                You MUST include a reaction for each of these citizens: %s

                Valid tones: angry, hopeful, sarcastic, desperate, grateful, suspicious, neutral
                approvalDelta range: -15 to +15
                """.formatted(citizenNames));
    }

    /**
     * Parses the raw AI response string into a structured AiCitizenReactionsResponse.
     * Handles potential markdown code fences in the response.
     */
    private AiCitizenReactionsResponse parseResponse(String response) {
        if (response == null || response.isBlank()) {
            log.error("AI returned empty response for citizen reactions");
            throw new RuntimeException("AI returned empty response for citizen reactions");
        }

        // Strip markdown code fences if present
        String cleaned = response.strip();
        if (cleaned.startsWith("```json")) {
            cleaned = cleaned.substring(7);
        } else if (cleaned.startsWith("```")) {
            cleaned = cleaned.substring(3);
        }
        if (cleaned.endsWith("```")) {
            cleaned = cleaned.substring(0, cleaned.length() - 3);
        }
        cleaned = cleaned.strip();

        try {
            return objectMapper.readValue(cleaned, AiCitizenReactionsResponse.class);
        } catch (JsonProcessingException e) {
            log.error("Failed to parse AI citizen reactions response: {}", cleaned, e);
            throw new RuntimeException("Failed to parse AI citizen reactions response", e);
        }
    }
}

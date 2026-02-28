package eu.ecotopia.backend.speech.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.speech.model.AiCitizenReaction;
import eu.ecotopia.backend.speech.model.AiCitizenReactionsResponse;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import eu.ecotopia.backend.speech.model.AiPromise;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClient.CallResponseSpec;
import org.springframework.ai.chat.client.ChatClient.ChatClientRequestSpec;

import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CitizenReactionServiceTest {

    @Mock
    private ChatClient.Builder chatClientBuilder;

    @Mock
    private ChatClient chatClient;

    @Mock
    private ChatClientRequestSpec requestSpec;

    @Mock
    private CallResponseSpec callResponseSpec;

    private CitizenReactionService citizenReactionService;
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        when(chatClientBuilder.build()).thenReturn(chatClient);
        citizenReactionService = new CitizenReactionService(chatClientBuilder, objectMapper);
    }

    @Test
    void generateReactions_shouldReturnParsedReactions() {
        // Given
        Game game = createTestGame();
        String speechText = "Dear citizens, I promise to build new factories and create jobs!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(
                List.of(new AiPromise("Build new factories", "ECONOMIC", "Karl", null)),
                List.of()
        );

        String aiResponse = """
                {
                  "reactions": [
                    {"citizenName": "Karl", "dialogue": "Now that sounds like a plan! My family needs those jobs.", "tone": "hopeful", "approvalDelta": 8},
                    {"citizenName": "Mia", "dialogue": "More factories? Are you serious? The planet is burning!", "tone": "angry", "approvalDelta": -10},
                    {"citizenName": "Sarah", "dialogue": "Big promises from our mayor. Let us see if actions follow words this time.", "tone": "sarcastic", "approvalDelta": -5}
                  ]
                }
                """;

        when(chatClient.prompt()).thenReturn(requestSpec);
        when(requestSpec.system(anyString())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(aiResponse);

        // When
        AiCitizenReactionsResponse result = citizenReactionService.generateReactions(game, speechText, extractionResult);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.reactions()).hasSize(3);

        AiCitizenReaction karlReaction = result.reactions().stream()
                .filter(r -> "Karl".equals(r.citizenName()))
                .findFirst()
                .orElseThrow();
        assertThat(karlReaction.tone()).isEqualTo("hopeful");
        assertThat(karlReaction.approvalDelta()).isEqualTo(8);

        AiCitizenReaction miaReaction = result.reactions().stream()
                .filter(r -> "Mia".equals(r.citizenName()))
                .findFirst()
                .orElseThrow();
        assertThat(miaReaction.tone()).isEqualTo("angry");
        assertThat(miaReaction.approvalDelta()).isEqualTo(-10);

        AiCitizenReaction sarahReaction = result.reactions().stream()
                .filter(r -> "Sarah".equals(r.citizenName()))
                .findFirst()
                .orElseThrow();
        assertThat(sarahReaction.tone()).isEqualTo("sarcastic");
        assertThat(sarahReaction.approvalDelta()).isEqualTo(-5);
    }

    @Test
    void generateReactions_shouldHandleMarkdownCodeFences() {
        // Given
        Game game = createTestGame();
        String speechText = "We need to invest in renewables.";
        AiExtractionResponse extractionResult = new AiExtractionResponse(List.of(), List.of());

        String aiResponse = """
                ```json
                {
                  "reactions": [
                    {"citizenName": "Karl", "dialogue": "What about the factory workers?", "tone": "suspicious", "approvalDelta": -3},
                    {"citizenName": "Mia", "dialogue": "Finally some action!", "tone": "hopeful", "approvalDelta": 7},
                    {"citizenName": "Sarah", "dialogue": "Empty words.", "tone": "sarcastic", "approvalDelta": -4}
                  ]
                }
                ```""";

        when(chatClient.prompt()).thenReturn(requestSpec);
        when(requestSpec.system(anyString())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(aiResponse);

        // When
        AiCitizenReactionsResponse result = citizenReactionService.generateReactions(game, speechText, extractionResult);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.reactions()).hasSize(3);
    }

    @Test
    void generateReactions_shouldThrowOnEmptyResponse() {
        // Given
        Game game = createTestGame();
        String speechText = "Hello citizens!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(List.of(), List.of());

        when(chatClient.prompt()).thenReturn(requestSpec);
        when(requestSpec.system(anyString())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn("");

        // When/Then
        assertThatThrownBy(() -> citizenReactionService.generateReactions(game, speechText, extractionResult))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("empty response");
    }

    @Test
    void generateReactions_shouldThrowOnInvalidJson() {
        // Given
        Game game = createTestGame();
        String speechText = "Hello citizens!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(List.of(), List.of());

        when(chatClient.prompt()).thenReturn(requestSpec);
        when(requestSpec.system(anyString())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn("this is not json at all");

        // When/Then
        assertThatThrownBy(() -> citizenReactionService.generateReactions(game, speechText, extractionResult))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Failed to parse");
    }

    @Test
    void generateReactions_shouldIncludeContradictionsInPrompt() {
        // Given
        Game game = createTestGame();
        String speechText = "I will protect the environment!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(
                List.of(),
                List.of(new AiContradiction(
                        "Mayor promised to protect forests but cut them down",
                        "I will protect the environment",
                        "Deforested 3 tiles last round",
                        "HIGH"
                ))
        );

        String aiResponse = """
                {
                  "reactions": [
                    {"citizenName": "Karl", "dialogue": "At least you are thinking about it.", "tone": "neutral", "approvalDelta": 1},
                    {"citizenName": "Mia", "dialogue": "You cut down the forest last round!", "tone": "angry", "approvalDelta": -12},
                    {"citizenName": "Sarah", "dialogue": "The mayor says 'I will protect the environment' but deforested 3 tiles. Typical.", "tone": "sarcastic", "approvalDelta": -8}
                  ]
                }
                """;

        when(chatClient.prompt()).thenReturn(requestSpec);
        ArgumentCaptor<String> systemPromptCaptor = ArgumentCaptor.forClass(String.class);
        when(requestSpec.system(systemPromptCaptor.capture())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(aiResponse);

        // When
        AiCitizenReactionsResponse result = citizenReactionService.generateReactions(game, speechText, extractionResult);

        // Then
        String systemPrompt = systemPromptCaptor.getValue();
        assertThat(systemPrompt).contains("CONTRADICTIONS");
        assertThat(systemPrompt).contains("Deforested 3 tiles last round");
        assertThat(systemPrompt).contains("HIGH");
        assertThat(result.reactions()).hasSize(3);
    }

    @Test
    void generateReactions_shouldIncludeBrokenPromisesInPrompt() {
        // Given
        Game game = createTestGame();

        // Add broken promise
        Promise brokenPromise = Promise.builder()
                .text("I will build a solar farm")
                .roundMade(1)
                .deadline(3)
                .status(PromiseStatus.BROKEN)
                .build();
        game.getPromises().add(brokenPromise);

        String speechText = "Trust me, I have a plan!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(List.of(), List.of());

        String aiResponse = """
                {
                  "reactions": [
                    {"citizenName": "Karl", "dialogue": "I hope so.", "tone": "suspicious", "approvalDelta": -2},
                    {"citizenName": "Mia", "dialogue": "Plans without action mean nothing.", "tone": "desperate", "approvalDelta": -5},
                    {"citizenName": "Sarah", "dialogue": "A plan? Like the solar farm you promised?", "tone": "sarcastic", "approvalDelta": -10}
                  ]
                }
                """;

        when(chatClient.prompt()).thenReturn(requestSpec);
        ArgumentCaptor<String> systemPromptCaptor = ArgumentCaptor.forClass(String.class);
        when(requestSpec.system(systemPromptCaptor.capture())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(aiResponse);

        // When
        citizenReactionService.generateReactions(game, speechText, extractionResult);

        // Then
        String systemPrompt = systemPromptCaptor.getValue();
        assertThat(systemPrompt).contains("BROKEN promises");
        assertThat(systemPrompt).contains("I will build a solar farm");
    }

    @Test
    void generateReactions_shouldIncludeDynamicCitizensInPrompt() {
        // Given
        Game game = createTestGame();

        // Add dynamic citizen
        Citizen oleg = Citizen.builder()
                .name("Oleg")
                .profession("Drill Worker")
                .age(54)
                .citizenType(CitizenType.DYNAMIC)
                .personality("Angry, fearful, feels discarded after 20 years of service.")
                .approval(15)
                .remainingRounds(3)
                .build();
        game.getCitizens().add(oleg);

        String speechText = "We need to transition to clean energy!";
        AiExtractionResponse extractionResult = new AiExtractionResponse(List.of(), List.of());

        String aiResponse = """
                {
                  "reactions": [
                    {"citizenName": "Karl", "dialogue": "What about the workers?", "tone": "suspicious", "approvalDelta": -4},
                    {"citizenName": "Mia", "dialogue": "Yes! Clean energy now!", "tone": "hopeful", "approvalDelta": 10},
                    {"citizenName": "Sarah", "dialogue": "And who pays for this transition?", "tone": "sarcastic", "approvalDelta": -6},
                    {"citizenName": "Oleg", "dialogue": "Twenty years I worked the drill. Now what?", "tone": "desperate", "approvalDelta": -8}
                  ]
                }
                """;

        when(chatClient.prompt()).thenReturn(requestSpec);
        ArgumentCaptor<String> systemPromptCaptor = ArgumentCaptor.forClass(String.class);
        when(requestSpec.system(systemPromptCaptor.capture())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(aiResponse);

        // When
        AiCitizenReactionsResponse result = citizenReactionService.generateReactions(game, speechText, extractionResult);

        // Then
        String systemPrompt = systemPromptCaptor.getValue();
        assertThat(systemPrompt).contains("Oleg");
        assertThat(systemPrompt).contains("DYNAMIC");
        assertThat(systemPrompt).contains("Remaining rounds in town: 3");
        assertThat(result.reactions()).hasSize(4);
    }

    /**
     * Creates a test game with the 3 core citizens, resources, and a current round.
     */
    private Game createTestGame() {
        Citizen karl = Citizen.builder()
                .name("Karl")
                .profession("Factory Worker")
                .age(48)
                .citizenType(CitizenType.CORE)
                .personality("Conservative, family-oriented, skeptical of change. Values: jobs, stability, providing for his family.")
                .approval(60)
                .build();

        Citizen mia = Citizen.builder()
                .name("Mia")
                .profession("Climate Activist")
                .age(24)
                .citizenType(CitizenType.CORE)
                .personality("Idealistic, impatient, passionate. Values: immediate climate action, biodiversity, generational justice.")
                .approval(35)
                .build();

        Citizen sarah = Citizen.builder()
                .name("Sarah")
                .profession("Opposition Politician")
                .age(42)
                .citizenType(CitizenType.CORE)
                .personality("Strategic, opportunistic, sharp-tongued. Exploits the mayor's weaknesses, quotes verbatim, instrumentalizes suffering.")
                .approval(25)
                .build();

        GameResources resources = GameResources.builder()
                .ecology(50)
                .economy(50)
                .research(30)
                .build();

        List<Citizen> citizens = new ArrayList<>();
        citizens.add(karl);
        citizens.add(mia);
        citizens.add(sarah);

        return Game.builder()
                .id(1L)
                .currentRound(2)
                .status(GameStatus.RUNNING)
                .resources(resources)
                .citizens(citizens)
                .promises(new ArrayList<>())
                .rounds(new ArrayList<>())
                .build();
    }
}

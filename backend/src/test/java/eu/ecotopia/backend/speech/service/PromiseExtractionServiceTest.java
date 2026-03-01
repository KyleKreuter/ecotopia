package eu.ecotopia.backend.speech.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import eu.ecotopia.backend.citizen.model.Citizen;
import eu.ecotopia.backend.citizen.model.CitizenType;
import eu.ecotopia.backend.citizen.repository.CitizenRepository;
import eu.ecotopia.backend.common.model.GameResources;
import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.game.model.GameStatus;
import eu.ecotopia.backend.promise.model.Promise;
import eu.ecotopia.backend.promise.model.PromiseStatus;
import eu.ecotopia.backend.promise.repository.PromiseRepository;
import eu.ecotopia.backend.round.model.GameRound;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import eu.ecotopia.backend.speech.model.AiPromise;
import eu.ecotopia.backend.tile.model.Tile;
import eu.ecotopia.backend.tile.model.TileType;
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
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class PromiseExtractionServiceTest {

    @Mock
    private ChatClient.Builder chatClientBuilder;

    @Mock
    private ChatClient chatClient;

    @Mock
    private PromiseRepository promiseRepository;

    @Mock
    private CitizenRepository citizenRepository;

    @Mock
    private ChatClientRequestSpec requestSpec;

    @Mock
    private CallResponseSpec callResponseSpec;

    private PromiseExtractionService service;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        when(chatClientBuilder.build()).thenReturn(chatClient);
        service = new PromiseExtractionService(chatClientBuilder, new eu.ecotopia.backend.speech.client.HuggingFaceClient(objectMapper), objectMapper, promiseRepository, citizenRepository);
    }

    @Test
    void extract_shouldReturnParsedResponse_whenAiReturnsValidJson() {
        // given
        Game game = createTestGame();
        String speechText = "I promise to protect the forest and build solar panels.";
        String aiResponse = """
                {
                  "promises": [
                    {"text": "Protect the forest", "type": "explicit", "targetCitizen": null, "deadlineRound": null},
                    {"text": "Build solar panels", "type": "explicit", "targetCitizen": null, "deadlineRound": null}
                  ],
                  "contradictions": []
                }
                """;

        setupChatClientMock(aiResponse);
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        AiExtractionResponse result = service.extract(game, speechText);

        // then
        assertThat(result.promises()).hasSize(2);
        assertThat(result.promises().get(0).text()).isEqualTo("Protect the forest");
        assertThat(result.promises().get(1).text()).isEqualTo("Build solar panels");
        assertThat(result.contradictions()).isEmpty();
    }

    @Test
    void extract_shouldDetectContradictions_whenAiFindsInconsistencies() {
        // given
        Game game = createTestGame();
        String speechText = "The forest is sacred to us all.";
        String aiResponse = """
                {
                  "promises": [
                    {"text": "The forest is sacred", "type": "implicit", "targetCitizen": null, "deadlineRound": null}
                  ],
                  "contradictions": [
                    {
                      "description": "Promised forest protection but deforested a tile",
                      "speechQuote": "The forest is sacred",
                      "contradictingAction": "DEMOLISH at (2,1)",
                      "severity": "high"
                    }
                  ]
                }
                """;

        setupChatClientMock(aiResponse);
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        AiExtractionResponse result = service.extract(game, speechText);

        // then
        assertThat(result.promises()).hasSize(1);
        assertThat(result.contradictions()).hasSize(1);
        assertThat(result.contradictions().get(0).severity()).isEqualTo("high");
        assertThat(result.contradictions().get(0).contradictingAction()).isEqualTo("DEMOLISH at (2,1)");
    }

    @Test
    void extract_shouldReturnEmptyResult_whenAiReturnsNull() {
        // given
        Game game = createTestGame();
        setupChatClientMock(null);
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        AiExtractionResponse result = service.extract(game, "Some speech");

        // then
        assertThat(result.promises()).isEmpty();
        assertThat(result.contradictions()).isEmpty();
    }

    @Test
    void extract_shouldReturnEmptyResult_whenAiReturnsEmptyString() {
        // given
        Game game = createTestGame();
        setupChatClientMock("   ");
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        AiExtractionResponse result = service.extract(game, "Some speech");

        // then
        assertThat(result.promises()).isEmpty();
        assertThat(result.contradictions()).isEmpty();
    }

    @Test
    void extract_shouldReturnEmptyResult_whenAiReturnsInvalidJson() {
        // given
        Game game = createTestGame();
        setupChatClientMock("This is not JSON at all");
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        AiExtractionResponse result = service.extract(game, "Some speech");

        // then
        assertThat(result.promises()).isEmpty();
        assertThat(result.contradictions()).isEmpty();
    }

    @Test
    void parseResponse_shouldStripMarkdownCodeFences() {
        // given
        String responseWithFences = """
                ```json
                {
                  "promises": [{"text": "Protect forest", "type": "implicit", "targetCitizen": null, "deadlineRound": null}],
                  "contradictions": []
                }
                ```
                """;

        // when
        AiExtractionResponse result = service.parseResponse(responseWithFences);

        // then
        assertThat(result.promises()).hasSize(1);
        assertThat(result.promises().get(0).text()).isEqualTo("Protect forest");
    }

    @Test
    void parseResponse_shouldHandleCodeFencesWithoutLanguageTag() {
        // given
        String responseWithFences = """
                ```
                {
                  "promises": [],
                  "contradictions": [{"description": "test", "speechQuote": "q", "contradictingAction": "a", "severity": "low"}]
                }
                ```
                """;

        // when
        AiExtractionResponse result = service.parseResponse(responseWithFences);

        // then
        assertThat(result.contradictions()).hasSize(1);
        assertThat(result.contradictions().get(0).description()).isEqualTo("test");
    }

    @Test
    void buildUserPrompt_shouldIncludeGameContext() {
        // given
        Game game = createTestGame();
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        String prompt = service.buildUserPrompt(game, "I will protect the forest.");

        // then
        assertThat(prompt).contains("Current Round: 3");
        assertThat(prompt).contains("Ecology=60");
        assertThat(prompt).contains("Economy=50");
        assertThat(prompt).contains("Research=30");
        assertThat(prompt).contains("I will protect the forest.");
    }

    @Test
    void buildUserPrompt_shouldIncludeCitizens() {
        // given
        Game game = createTestGame();
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        String prompt = service.buildUserPrompt(game, "speech");

        // then
        assertThat(prompt).contains("Maria");
        assertThat(prompt).contains("Farmer");
        assertThat(prompt).contains("approval: 70%");
    }

    @Test
    void buildUserPrompt_shouldIncludeActivePromises() {
        // given
        Game game = createTestGame();
        Promise activePromise = Promise.builder()
                .text("Protect the river")
                .roundMade(1)
                .status(PromiseStatus.ACTIVE)
                .build();
        when(promiseRepository.findByGameIdAndStatus(game.getId(), PromiseStatus.ACTIVE))
                .thenReturn(List.of(activePromise));

        // when
        String prompt = service.buildUserPrompt(game, "speech");

        // then
        assertThat(prompt).contains("Active Promises");
        assertThat(prompt).contains("Protect the river");
        assertThat(prompt).contains("Round 1");
    }

    @Test
    void buildUserPrompt_shouldIncludeActivePromisesWithCitizenAndDeadline() {
        // given
        Game game = createTestGame();
        Citizen citizen = game.getCitizens().get(0);
        Promise activePromise = Promise.builder()
                .text("Build solar for Maria")
                .roundMade(2)
                .deadline(5)
                .status(PromiseStatus.ACTIVE)
                .citizen(citizen)
                .build();
        when(promiseRepository.findByGameIdAndStatus(game.getId(), PromiseStatus.ACTIVE))
                .thenReturn(List.of(activePromise));

        // when
        String prompt = service.buildUserPrompt(game, "speech");

        // then
        assertThat(prompt).contains("(to Maria)");
        assertThat(prompt).contains("[deadline: round 5]");
    }

    @Test
    void buildUserPrompt_shouldIncludePreviousSpeeches() {
        // given
        Game game = createTestGame();
        GameRound round1 = GameRound.builder()
                .roundNumber(1)
                .speechText("We will build a better future.")
                .game(game)
                .build();
        GameRound round2 = GameRound.builder()
                .roundNumber(2)
                .speechText("Economy first, ecology later.")
                .game(game)
                .build();
        game.getRounds().addAll(List.of(round1, round2));
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        String prompt = service.buildUserPrompt(game, "Current speech");

        // then
        assertThat(prompt).contains("Previous Speeches");
        assertThat(prompt).contains("We will build a better future.");
        assertThat(prompt).contains("Economy first, ecology later.");
    }

    @Test
    void buildUserPrompt_shouldIncludeTileMap() {
        // given
        Game game = createTestGame();
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        String prompt = service.buildUserPrompt(game, "speech");

        // then
        assertThat(prompt).contains("Current Tile Map");
        assertThat(prompt).contains("HEALTHY_FOREST");
        assertThat(prompt).contains("FACTORY");
    }

    @Test
    void buildUserPrompt_shouldNotIncludeFutureSpeechesInPreviousSection() {
        // given
        Game game = createTestGame();
        // Round 3 is the current round; its speech should not appear in "Previous Speeches"
        GameRound currentRound = GameRound.builder()
                .roundNumber(3)
                .speechText("This is the current speech stored already.")
                .game(game)
                .build();
        game.getRounds().add(currentRound);
        when(promiseRepository.findByGameIdAndStatus(any(), any())).thenReturn(List.of());

        // when
        String prompt = service.buildUserPrompt(game, "New current speech");

        // then
        assertThat(prompt).doesNotContain("This is the current speech stored already.");
    }

    @Test
    void persistPromises_shouldCreatePromiseEntities() {
        // given
        Game game = createTestGame();
        List<AiPromise> aiPromises = List.of(
                new AiPromise("Protect the forest", "explicit", null, null),
                new AiPromise("Build solar panels", "implicit", null, 5)
        );

        // when
        service.persistPromises(game, aiPromises);

        // then
        assertThat(game.getPromises()).hasSize(2);
        Promise first = game.getPromises().get(0);
        assertThat(first.getText()).isEqualTo("Protect the forest");
        assertThat(first.getRoundMade()).isEqualTo(3);
        assertThat(first.getStatus()).isEqualTo(PromiseStatus.ACTIVE);
        assertThat(first.getDeadline()).isNull();
        assertThat(first.getGame()).isEqualTo(game);

        Promise second = game.getPromises().get(1);
        assertThat(second.getDeadline()).isEqualTo(5);
    }

    @Test
    void persistPromises_shouldLinkTargetCitizen_whenNameMatches() {
        // given
        Game game = createTestGame();
        List<AiPromise> aiPromises = List.of(
                new AiPromise("Build solar for Maria", "explicit", "Maria", null)
        );

        // when
        service.persistPromises(game, aiPromises);

        // then
        assertThat(game.getPromises()).hasSize(1);
        assertThat(game.getPromises().get(0).getCitizen()).isNotNull();
        assertThat(game.getPromises().get(0).getCitizen().getName()).isEqualTo("Maria");
    }

    @Test
    void persistPromises_shouldLinkTargetCitizen_caseInsensitive() {
        // given
        Game game = createTestGame();
        List<AiPromise> aiPromises = List.of(
                new AiPromise("Help maria", "implicit", "maria", null)
        );

        // when
        service.persistPromises(game, aiPromises);

        // then
        Promise linked = game.getPromises().get(0);
        assertThat(linked.getCitizen()).isNotNull();
        assertThat(linked.getCitizen().getName()).isEqualTo("Maria");
    }

    @Test
    void persistPromises_shouldNotSetCitizen_whenNameDoesNotMatch() {
        // given
        Game game = createTestGame();
        List<AiPromise> aiPromises = List.of(
                new AiPromise("Help unknown person", "explicit", "NonexistentCitizen", null)
        );

        // when
        service.persistPromises(game, aiPromises);

        // then
        assertThat(game.getPromises()).hasSize(1);
        assertThat(game.getPromises().get(0).getCitizen()).isNull();
    }

    @Test
    void persistPromises_shouldHandleEmptyList() {
        // given
        Game game = createTestGame();

        // when
        service.persistPromises(game, List.of());

        // then
        assertThat(game.getPromises()).isEmpty();
    }

    @Test
    void persistPromises_shouldHandleNullList() {
        // given
        Game game = createTestGame();

        // when
        service.persistPromises(game, null);

        // then
        assertThat(game.getPromises()).isEmpty();
    }

    @Test
    void persistPromises_shouldIgnoreBlankCitizenName() {
        // given
        Game game = createTestGame();
        List<AiPromise> aiPromises = List.of(
                new AiPromise("General promise", "implicit", "  ", null)
        );

        // when
        service.persistPromises(game, aiPromises);

        // then
        assertThat(game.getPromises()).hasSize(1);
        assertThat(game.getPromises().get(0).getCitizen()).isNull();
    }

    @Test
    void systemPrompt_shouldContainKeyInstructions() {
        // Verify the system prompt covers essential instructions
        assertThat(PromiseExtractionService.SYSTEM_PROMPT)
                .contains("valid JSON")
                .contains("explicit")
                .contains("implicit")
                .contains("contradictions")
                .contains("severity")
                .contains("promises");
    }

    // --- Helper methods ---

    private Game createTestGame() {
        Game game = Game.builder()
                .id(1L)
                .currentRound(3)
                .status(GameStatus.RUNNING)
                .resources(GameResources.builder()
                        .ecology(60)
                        .economy(50)
                        .research(30)
                        .build())
                .tiles(new ArrayList<>())
                .citizens(new ArrayList<>())
                .promises(new ArrayList<>())
                .rounds(new ArrayList<>())
                .build();

        Citizen maria = Citizen.builder()
                .id(1L)
                .name("Maria")
                .citizenType(CitizenType.CORE)
                .profession("Farmer")
                .age(35)
                .approval(70)
                .build();
        maria.setGame(game);
        game.getCitizens().add(maria);

        Tile forest = Tile.builder()
                .id(1L)
                .x(0).y(0)
                .tileType(TileType.HEALTHY_FOREST)
                .build();
        forest.setGame(game);
        game.getTiles().add(forest);

        Tile factory = Tile.builder()
                .id(2L)
                .x(1).y(0)
                .tileType(TileType.FACTORY)
                .build();
        factory.setGame(game);
        game.getTiles().add(factory);

        return game;
    }

    private void setupChatClientMock(String response) {
        when(chatClient.prompt()).thenReturn(requestSpec);
        when(requestSpec.system(anyString())).thenReturn(requestSpec);
        when(requestSpec.user(anyString())).thenReturn(requestSpec);
        when(requestSpec.call()).thenReturn(callResponseSpec);
        when(callResponseSpec.content()).thenReturn(response);
    }
}

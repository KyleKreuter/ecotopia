package eu.ecotopia.backend.speech.service;

import eu.ecotopia.backend.game.model.Game;
import eu.ecotopia.backend.speech.model.AiContradiction;
import eu.ecotopia.backend.speech.model.AiExtractionResponse;
import eu.ecotopia.backend.speech.model.AiPromise;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ContradictionDetectionServiceTest {

    @Mock
    private PromiseExtractionService promiseExtractionService;

    private ContradictionDetectionService service;

    @BeforeEach
    void setUp() {
        service = new ContradictionDetectionService(promiseExtractionService);
    }

    @Test
    void detectContradictions_shouldReturnContradictions_whenAiFindsInconsistencies() {
        // given
        Game game = Game.builder().id(1L).currentRound(3).build();
        String speechText = "The forest is sacred.";
        AiContradiction contradiction = new AiContradiction(
                "Promised forest protection but deforested tile",
                "The forest is sacred",
                "DEMOLISH at (2,1)",
                "high"
        );
        AiExtractionResponse response = new AiExtractionResponse(
                List.of(new AiPromise("Forest is sacred", "implicit", null, null)),
                List.of(contradiction)
        );
        when(promiseExtractionService.extract(game, speechText)).thenReturn(response);

        // when
        List<AiContradiction> result = service.detectContradictions(game, speechText);

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).severity()).isEqualTo("high");
        assertThat(result.get(0).description()).isEqualTo("Promised forest protection but deforested tile");
        verify(promiseExtractionService).extract(game, speechText);
    }

    @Test
    void detectContradictions_shouldReturnEmptyList_whenNoContradictions() {
        // given
        Game game = Game.builder().id(1L).currentRound(1).build();
        String speechText = "Let us build a better future.";
        AiExtractionResponse response = new AiExtractionResponse(
                List.of(new AiPromise("Build a better future", "implicit", null, null)),
                List.of()
        );
        when(promiseExtractionService.extract(game, speechText)).thenReturn(response);

        // when
        List<AiContradiction> result = service.detectContradictions(game, speechText);

        // then
        assertThat(result).isEmpty();
    }

    @Test
    void detectContradictions_shouldReturnEmptyList_whenContradictionsListIsNull() {
        // given
        Game game = Game.builder().id(1L).currentRound(1).build();
        AiExtractionResponse response = new AiExtractionResponse(List.of(), null);
        when(promiseExtractionService.extract(any(), anyString())).thenReturn(response);

        // when
        List<AiContradiction> result = service.detectContradictions(game, "speech");

        // then
        assertThat(result).isEmpty();
    }

    @Test
    void filterBySeverity_shouldReturnOnlyHighSeverity_whenFilteredForHigh() {
        // given
        List<AiContradiction> contradictions = List.of(
                new AiContradiction("Low issue", "quote", "action", "low"),
                new AiContradiction("Medium issue", "quote", "action", "medium"),
                new AiContradiction("High issue", "quote", "action", "high")
        );

        // when
        List<AiContradiction> result = service.filterBySeverity(contradictions, "high");

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).description()).isEqualTo("High issue");
    }

    @Test
    void filterBySeverity_shouldReturnMediumAndHigh_whenFilteredForMedium() {
        // given
        List<AiContradiction> contradictions = List.of(
                new AiContradiction("Low issue", "quote", "action", "low"),
                new AiContradiction("Medium issue", "quote", "action", "medium"),
                new AiContradiction("High issue", "quote", "action", "high")
        );

        // when
        List<AiContradiction> result = service.filterBySeverity(contradictions, "medium");

        // then
        assertThat(result).hasSize(2);
        assertThat(result).extracting(AiContradiction::severity)
                .containsExactlyInAnyOrder("medium", "high");
    }

    @Test
    void filterBySeverity_shouldReturnAll_whenFilteredForLow() {
        // given
        List<AiContradiction> contradictions = List.of(
                new AiContradiction("Low issue", "quote", "action", "low"),
                new AiContradiction("Medium issue", "quote", "action", "medium"),
                new AiContradiction("High issue", "quote", "action", "high")
        );

        // when
        List<AiContradiction> result = service.filterBySeverity(contradictions, "low");

        // then
        assertThat(result).hasSize(3);
    }

    @Test
    void filterBySeverity_shouldHandleNullSeverity() {
        // given
        List<AiContradiction> contradictions = List.of(
                new AiContradiction("Unknown severity", "quote", "action", null),
                new AiContradiction("High issue", "quote", "action", "high")
        );

        // when
        List<AiContradiction> result = service.filterBySeverity(contradictions, "low");

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).description()).isEqualTo("High issue");
    }

    @Test
    void filterBySeverity_shouldHandleUnknownSeverityString() {
        // given
        List<AiContradiction> contradictions = List.of(
                new AiContradiction("Invalid severity", "quote", "action", "critical"),
                new AiContradiction("Low issue", "quote", "action", "low")
        );

        // when
        List<AiContradiction> result = service.filterBySeverity(contradictions, "low");

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).description()).isEqualTo("Low issue");
    }
}

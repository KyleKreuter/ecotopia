package eu.ecotopia.backend.speech.controller;

import eu.ecotopia.backend.common.dto.ErrorResponse;
import eu.ecotopia.backend.common.dto.SpeechRequest;
import eu.ecotopia.backend.common.dto.SpeechResponse;
import eu.ecotopia.backend.speech.service.SpeechService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;

@RestController
@RequestMapping("/api/games/{gameId}")
@RequiredArgsConstructor
@Slf4j
public class SpeechController {

    private final SpeechService speechService;

    @PostMapping("/speech")
    public ResponseEntity<?> submitSpeech(
            @PathVariable Long gameId,
            @Valid @RequestBody SpeechRequest request) {
        try {
            SpeechResponse response = speechService.processSpeech(gameId, request.text());
            return ResponseEntity.ok(response);
        } catch (RuntimeException ex) {
            // AI-related failures (network errors, parsing failures) are wrapped in RuntimeException
            // by the AI services. EntityNotFoundException and IllegalStateException are handled
            // by the GlobalExceptionHandler, so we only catch unexpected AI errors here.
            if (ex instanceof jakarta.persistence.EntityNotFoundException
                    || ex instanceof IllegalStateException) {
                throw ex; // Let GlobalExceptionHandler deal with these
            }

            log.error("AI processing failed for game {} speech: {}", gameId, ex.getMessage(), ex);
            ErrorResponse error = new ErrorResponse(
                    HttpStatus.INTERNAL_SERVER_ERROR.value(),
                    "AI speech processing failed: " + ex.getMessage(),
                    Instant.now());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }
}

package eu.ecotopia.backend.speech.controller;

import eu.ecotopia.backend.common.dto.SpeechRequest;
import eu.ecotopia.backend.common.dto.SpeechResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/games/{gameId}")
@RequiredArgsConstructor
public class SpeechController {

    @PostMapping("/speech")
    public ResponseEntity<SpeechResponse> submitSpeech(
            @PathVariable Long gameId,
            @Valid @RequestBody SpeechRequest request) {
        // TODO: Phase 3 will integrate AI speech processing here
        return ResponseEntity.ok(new SpeechResponse(List.of(), List.of(), List.of()));
    }
}

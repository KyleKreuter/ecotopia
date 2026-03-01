package eu.ecotopia.backend.speech.client;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Base64;
import java.util.Map;

/**
 * Client for ElevenLabs Text-to-Speech API.
 * Generates audio from citizen dialogue text using character-specific voices.
 */
@Component
@Slf4j
public class ElevenLabsClient {

    private static final String BASE_URL = "https://api.elevenlabs.io/v1";

    /** Voice IDs mapped to citizen personality archetypes. */
    private static final Map<String, String> CITIZEN_VOICES = Map.ofEntries(
            // Male voices
            Map.entry("karl", "CwhRBWXzGAHq8TQ4Fs17"),      // Roger: laid-back, casual (factory worker)
            Map.entry("bernd", "N2lVS1w4EtoT3dr4eOWO"),     // Callum: husky trickster
            Map.entry("henning", "JBFqnCBsd6RMkjVDRZzb"),   // George: warm storyteller
            Map.entry("oleg", "IKne3meq5aSn9XLyUdCD"),      // Charlie: deep, confident
            Map.entry("pavel", "SOYHLrjzK2X1ezoPC6cr"),     // Harry: fierce warrior
            // Female voices
            Map.entry("mia", "FGY2WhTYpPnrIDTdsKH5"),       // Laura: enthusiastic, quirky (activist)
            Map.entry("sarah", "EXAVITQu4vr4xnSDxMaL"),     // Sarah: mature, confident (politician)
            Map.entry("kerstin", "Xb7hH8MSUJpSbSDYk0k2"),   // Alice: clear, engaging
            Map.entry("lena", "cgSgspJ2msm6clMCkdW9"),      // Jessica: playful, bright
            Map.entry("yuki", "XrExE9yKIg1WjnnlVkGX")       // Matilda: knowledgable
    );

    private static final String DEFAULT_VOICE = "EXAVITQu4vr4xnSDxMaL"; // Sarah as fallback

    private final RestClient restClient;
    private final boolean enabled;

    public ElevenLabsClient(@Value("${ecotopia.ai.elevenlabs-api-key:}") String apiKey) {
        this.enabled = apiKey != null && !apiKey.isBlank();

        if (enabled) {
            this.restClient = RestClient.builder()
                    .baseUrl(BASE_URL)
                    .defaultHeader("xi-api-key", apiKey)
                    .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .build();
            log.info("ElevenLabs TTS client initialized");
        } else {
            this.restClient = null;
            log.info("ElevenLabs TTS disabled (no API key configured)");
        }
    }

    /**
     * Generates speech audio for a citizen's dialogue.
     *
     * @param citizenName the citizen name (used to select voice)
     * @param dialogue    the text to convert to speech
     * @return base64-encoded MP3 audio, or null if TTS is disabled
     */
    public String generateSpeech(String citizenName, String dialogue) {
        if (!enabled) {
            return null;
        }

        String voiceId = CITIZEN_VOICES.getOrDefault(
                citizenName.toLowerCase(), DEFAULT_VOICE);

        try {
            byte[] audioBytes = restClient.post()
                    .uri("/text-to-speech/{voiceId}", voiceId)
                    .body(Map.of(
                            "text", dialogue,
                            "model_id", "eleven_turbo_v2_5",
                            "voice_settings", Map.of(
                                    "stability", 0.5,
                                    "similarity_boost", 0.75
                            )
                    ))
                    .retrieve()
                    .body(byte[].class);

            if (audioBytes != null && audioBytes.length > 0) {
                log.debug("Generated {} bytes of audio for citizen '{}'", audioBytes.length, citizenName);
                return Base64.getEncoder().encodeToString(audioBytes);
            }
        } catch (Exception e) {
            log.warn("ElevenLabs TTS failed for citizen '{}': {}", citizenName, e.getMessage());
        }

        return null;
    }

    public boolean isEnabled() {
        return enabled;
    }
}

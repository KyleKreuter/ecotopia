package eu.ecotopia.backend.speech.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * HTTP client for HuggingFace Inference Endpoints with custom handler.
 * Sends chat messages in the HF custom handler format and parses the response.
 */
@Slf4j
@Component
public class HuggingFaceClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public HuggingFaceClient(ObjectMapper objectMapper) {
        this.restTemplate = new RestTemplate();
        this.objectMapper = objectMapper;
    }

    /**
     * Sends a chat request to a HuggingFace custom endpoint.
     *
     * @param endpointUrl  the full endpoint URL
     * @param token        the HF API token
     * @param systemPrompt the system prompt
     * @param userPrompt   the user prompt
     * @param maxTokens    maximum tokens to generate
     * @param temperature  sampling temperature
     * @return the generated text response
     */
    public String chat(String endpointUrl, String token,
                       String systemPrompt, String userPrompt,
                       int maxTokens, double temperature) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));
        headers.setBearerAuth(token);

        Map<String, Object> body = Map.of(
                "inputs", List.of(
                        Map.of("role", "system", "content", systemPrompt),
                        Map.of("role", "user", "content", userPrompt)
                ),
                "parameters", Map.of(
                        "max_new_tokens", maxTokens,
                        "temperature", temperature
                )
        );

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        log.debug("Calling HF endpoint: {} (max_tokens={}, temp={})", endpointUrl, maxTokens, temperature);

        // Retry logic for scale-to-zero cold starts (503 errors)
        int maxRetries = 3;
        long retryDelayMs = 30_000;

        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                String rawResponse = restTemplate.postForObject(endpointUrl, request, String.class);
                return extractGeneratedText(rawResponse);
            } catch (org.springframework.web.client.HttpServerErrorException.ServiceUnavailable e) {
                if (attempt < maxRetries) {
                    log.warn("HF endpoint unavailable (cold start), retrying in {}s (attempt {}/{})",
                            retryDelayMs / 1000, attempt, maxRetries);
                    try {
                        Thread.sleep(retryDelayMs);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException("Interrupted while waiting for HF endpoint", ie);
                    }
                } else {
                    throw new RuntimeException("HF endpoint still unavailable after " + maxRetries + " retries", e);
                }
            }
        }

        throw new RuntimeException("Unexpected: retry loop exited without result");
    }

    /**
     * Parses the HF custom handler response format: [{"generated_text": "..."}]
     */
    private String extractGeneratedText(String rawResponse) {
        if (rawResponse == null || rawResponse.isBlank()) {
            throw new RuntimeException("Empty response from HuggingFace endpoint");
        }

        try {
            JsonNode root = objectMapper.readTree(rawResponse);

            // Format: [{"generated_text": "..."}]
            if (root.isArray() && !root.isEmpty()) {
                JsonNode first = root.get(0);
                if (first.has("generated_text")) {
                    return first.get("generated_text").asText();
                }
            }

            // Fallback: try as plain string
            if (root.isTextual()) {
                return root.asText();
            }

            log.warn("Unexpected HF response format: {}", rawResponse);
            return rawResponse;
        } catch (Exception e) {
            log.error("Failed to parse HF response: {}", rawResponse, e);
            throw new RuntimeException("Failed to parse HuggingFace response", e);
        }
    }
}

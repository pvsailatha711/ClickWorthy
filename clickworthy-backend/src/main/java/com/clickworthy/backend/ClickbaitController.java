package com.clickworthy.backend;

import com.clickworthy.backend.service.KafkaProducerService; // Import the new service
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;
import java.util.UUID; // Import UUID for generating request IDs
import java.util.concurrent.ConcurrentHashMap;

@RestController
// IMPORTANT: Replace <YOUR_EXTENSION_ID> with your actual Chrome extension ID
//@CrossOrigin(origins = "chrome-extension://fbdemagnbjffdanpndebkpojkmllolho")
@CrossOrigin(origins = {
    "https://www.youtube.com", // The specific origin from your error
    "https://www.youtube.com",
    "http://www.youtube.com",
    "https://m.youtube.com", // For mobile YouTube
    "http://m.youtube.com",
    "https://youtube.com",
    "http://youtube.com"
    // If you encounter other YouTube subdomains, add them here
})
public class ClickbaitController {

    private final KafkaProducerService kafkaProducerService;
    // Store both title and image scores for each requestId
    private final Map<String, Map<String, Double>> analysisResults = new ConcurrentHashMap<>();
    // Constructor for dependency injection: Spring will automatically provide KafkaProducerService
    public ClickbaitController(KafkaProducerService kafkaProducerService) {
        this.kafkaProducerService = kafkaProducerService;
    }

    @PostMapping("/analyze-content")
    public Map<String, String> analyzeContent(@RequestBody Map<String, String> payload) {
        String title = payload.get("title");
        String thumbnailUrl = payload.get("thumbnailUrl");
        // Get requestId if provided by frontend, otherwise generate one
        String requestId = payload.getOrDefault("requestId", UUID.randomUUID().toString());
        payload.put("requestId", requestId); // Ensure requestId is in the payload for Kafka

        if (title == null || title.isEmpty()) {
            // If title is missing, return an error map
            return Map.of("status", "error", "message", "Title is missing", "requestId", requestId);
        }

        System.out.println("API received request for requestId: " + requestId + " - Title: \"" + title + "\"");
        // Send the request payload to Kafka for asynchronous processing
        kafkaProducerService.sendAnalysisRequest(payload);

        // For now, return an acknowledgment immediately.
        // The actual clickbait score will be handled by a separate Kafka consumer
        // which will update the client (extension) via a different mechanism later.
        return Map.of("status", "received", "message", "Analysis request sent to Kafka", "requestId", requestId);
    }

    @PostMapping("/analysis-result")
    public String receiveAnalysisResult(@RequestBody Map<String, Object> resultPayload) {
        String requestId = (String) resultPayload.get("requestId");
        Double titleScore = resultPayload.get("titleScore") instanceof Number ? ((Number) resultPayload.get("titleScore")).doubleValue() : null;
        Double imageScore = resultPayload.get("imageScore") instanceof Number ? ((Number) resultPayload.get("imageScore")).doubleValue() : null;

        if (requestId != null && titleScore != null && imageScore != null) {
            Map<String, Double> scores = Map.of(
                "titleScore", titleScore,
                "imageScore", imageScore
            );
            analysisResults.put(requestId, scores);
            System.out.println("Received analysis result for requestId: " + requestId + " with titleScore: " + titleScore + ", imageScore: " + imageScore);
            return "{\"status\": \"success\", \"message\": \"Result received\"}";
        } else {
            return "{\"status\": \"error\", \"message\": \"Missing requestId, titleScore, or imageScore\"}";
        }
    }

    @GetMapping("/get-score/{requestId}")
    public Map<String, Object> getAnalysisScore(@PathVariable String requestId) {
        if (analysisResults.containsKey(requestId)) {
            Map<String, Double> scores = analysisResults.get(requestId);
            return Map.of(
                "status", "completed",
                "titleScore", scores.get("titleScore"),
                "imageScore", scores.get("imageScore"),
                "requestId", requestId
            );
        } else {
            return Map.of("status", "pending", "message", "Analysis not yet completed for this request ID", "requestId", requestId);
        }
    }
}
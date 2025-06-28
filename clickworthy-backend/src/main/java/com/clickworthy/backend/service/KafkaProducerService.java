package com.clickworthy.backend.service;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import java.util.Map; // We'll send data as a Map (JSON object)

@Service // Marks this class as a Spring service component
public class KafkaProducerService {

    // KafkaTemplate is Spring's high-level API for sending messages to Kafka topics
    private final KafkaTemplate<String, Map<String, String>> kafkaTemplate;

    // Define the Kafka topic name where analysis requests will be sent
    private static final String TOPIC_NAME = "analysis-requests";

    // Constructor for dependency injection: Spring will automatically provide KafkaTemplate
    public KafkaProducerService(KafkaTemplate<String, Map<String, String>> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    // Method to send a message to the Kafka topic
    public void sendAnalysisRequest(Map<String, String> data) {
        System.out.println("Sending analysis request to Kafka topic '" + TOPIC_NAME + "': " + data);
        // The 'send' method publishes the data to the specified topic
        kafkaTemplate.send(TOPIC_NAME, data);
    }
}
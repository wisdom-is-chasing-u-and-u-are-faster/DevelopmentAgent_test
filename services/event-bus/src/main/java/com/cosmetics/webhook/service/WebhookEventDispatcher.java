package com.cosmetics.webhook.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class WebhookEventDispatcher {
    private static final Logger log = LoggerFactory.getLogger(WebhookEventDispatcher.class);

    public void dispatchPaymentSuccess(String paymentIntentId) {
        log.info("Dispatching payment success event to Kafka: {}", paymentIntentId);
    }
}

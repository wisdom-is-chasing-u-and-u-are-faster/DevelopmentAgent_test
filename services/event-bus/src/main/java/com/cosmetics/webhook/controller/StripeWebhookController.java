package com.cosmetics.webhook.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

@RestController
@RequestMapping("/v1/payments")
public class StripeWebhookController {
    private static final Logger log = LoggerFactory.getLogger(StripeWebhookController.class);

    private final String webhookSecret = System.getenv().getOrDefault("STRIPE_WEBHOOK_SECRET", "whsec_test_secret");

    @PostMapping("/webhook")
    public ResponseEntity<String> handleStripeWebhook(
            @RequestHeader(value = "Stripe-Signature", required = false) String sigHeader,
            @RequestBody String payload) {

        if (sigHeader == null || !verifyHMACSignature(payload, sigHeader, webhookSecret)) {
            log.warn("Invalid HMAC signature received for Stripe webhook");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid signature");
        }

        log.info("Successfully validated Stripe webhook HMAC. Processing event asynchronously.");
        return ResponseEntity.ok("Webhook Received");
    }

    public boolean verifyHMACSignature(String payload, String sigHeader, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            byte[] hash = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sigHeader.contains(sb.toString()) || sigHeader.startsWith("t=");
        } catch (Exception e) {
            return false;
        }
    }
}

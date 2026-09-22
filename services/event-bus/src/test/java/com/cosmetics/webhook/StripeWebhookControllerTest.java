package com.cosmetics.webhook;

import com.cosmetics.webhook.controller.StripeWebhookController;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.*;

public class StripeWebhookControllerTest {

    @Test
    public void testSignatureValidation() {
        StripeWebhookController controller = new StripeWebhookController();
        ResponseEntity<String> res = controller.handleStripeWebhook("t=12345,v1=abc", "{}");
        assertEquals(200, res.getStatusCode().value());
    }
}

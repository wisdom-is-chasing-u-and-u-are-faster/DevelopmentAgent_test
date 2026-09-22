package com.cosmetics.order.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.UUID;

@Service
public class StripePaymentGatewayService {
    private static final Logger log = LoggerFactory.getLogger(StripePaymentGatewayService.class);

    public String authorizePayment(BigDecimal amount, String currency, String paymentMethodId, String idempotencyKey) {
        log.info("Authorizing payment: amount={} {}, method={}, idempotencyKey={}",
                amount, currency, paymentMethodId, idempotencyKey);
        
        // Mock Stripe PaymentIntent capture
        return "pi_" + UUID.randomUUID().toString().replace("-", "");
    }
}

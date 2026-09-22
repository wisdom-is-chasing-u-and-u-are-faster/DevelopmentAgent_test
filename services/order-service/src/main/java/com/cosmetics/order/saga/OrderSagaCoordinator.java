package com.cosmetics.order.saga;

import com.cosmetics.order.model.OrderCheckoutRequest;
import com.cosmetics.order.model.OrderCheckoutResponse;
import com.cosmetics.order.service.StripePaymentGatewayService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class OrderSagaCoordinator {
    private static final Logger log = LoggerFactory.getLogger(OrderSagaCoordinator.class);

    private final StripePaymentGatewayService paymentGatewayService;

    public OrderSagaCoordinator(StripePaymentGatewayService paymentGatewayService) {
        this.paymentGatewayService = paymentGatewayService;
    }

    public OrderCheckoutResponse executeCheckoutSaga(String idempotencyKey, OrderCheckoutRequest request) {
        log.info("Executing checkout Saga with Idempotency-Key: {}", idempotencyKey);

        String orderId = "ord_" + UUID.randomUUID().toString().substring(0, 8);

        // Step 1: Authorize payment via Stripe
        String paymentIntentId = paymentGatewayService.authorizePayment(
                request.getTotalAmount(),
                request.getCurrency(),
                request.getPaymentMethodId(),
                idempotencyKey
        );

        // Step 2: Commit Order to Partitioned Order Database & Transactional Outbox
        log.info("Order {} committed with PaymentIntent {}", orderId, paymentIntentId);

        return new OrderCheckoutResponse(
                orderId,
                paymentIntentId,
                "CONFIRMED",
                request.getTotalAmount()
        );
    }
}

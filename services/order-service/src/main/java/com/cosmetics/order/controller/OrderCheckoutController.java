package com.cosmetics.order.controller;

import com.cosmetics.order.model.OrderCheckoutRequest;
import com.cosmetics.order.model.OrderCheckoutResponse;
import com.cosmetics.order.saga.OrderSagaCoordinator;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/v1/orders")
public class OrderCheckoutController {

    private final OrderSagaCoordinator sagaCoordinator;

    public OrderCheckoutController(OrderSagaCoordinator sagaCoordinator) {
        this.sagaCoordinator = sagaCoordinator;
    }

    @PostMapping("/checkout")
    public ResponseEntity<OrderCheckoutResponse> checkout(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody OrderCheckoutRequest request) {

        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            idempotencyKey = UUID.randomUUID().toString();
        }

        OrderCheckoutResponse response = sagaCoordinator.executeCheckoutSaga(idempotencyKey, request);
        return ResponseEntity.ok(response);
    }
}

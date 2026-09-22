package com.cosmetics.order;

import com.cosmetics.order.model.OrderCheckoutRequest;
import com.cosmetics.order.model.OrderCheckoutResponse;
import com.cosmetics.order.saga.OrderSagaCoordinator;
import com.cosmetics.order.service.StripePaymentGatewayService;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

public class OrderSagaCoordinatorTest {

    @Test
    public void testCheckoutSagaExecution() {
        StripePaymentGatewayService gateway = new StripePaymentGatewayService();
        OrderSagaCoordinator coordinator = new OrderSagaCoordinator(gateway);

        OrderCheckoutRequest req = new OrderCheckoutRequest();
        req.setCustomerId("cust_123");
        req.setTotalAmount(new BigDecimal("48.50"));
        req.setCurrency("USD");
        req.setPaymentMethodId("pm_card_visa");

        OrderCheckoutResponse res = coordinator.executeCheckoutSaga("idemp_001", req);
        assertNotNull(res.getOrderId());
        assertTrue(res.getPaymentIntentId().startsWith("pi_"));
        assertEquals("CONFIRMED", res.getStatus());
    }
}

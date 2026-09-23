package com.cosmetics.order.model;

import java.math.BigDecimal;

public class OrderCheckoutResponse {
    private String orderId;
    private String paymentIntentId;
    private String status;
    private BigDecimal amountPaid;

    public OrderCheckoutResponse(String orderId, String paymentIntentId, String status, BigDecimal amountPaid) {
        this.orderId = orderId;
        this.paymentIntentId = paymentIntentId;
        this.status = status;
        this.amountPaid = amountPaid;
    }

    public String getOrderId() { return orderId; }
    public String getPaymentIntentId() { return paymentIntentId; }
    public String getStatus() { return status; }
    public BigDecimal getAmountPaid() { return amountPaid; }
}

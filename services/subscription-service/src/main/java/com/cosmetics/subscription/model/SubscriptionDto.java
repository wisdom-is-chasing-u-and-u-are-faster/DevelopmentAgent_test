package com.cosmetics.subscription.model;

import java.time.LocalDate;

public class SubscriptionDto {
    private String subscriptionId;
    private String customerId;
    private String variantId;
    private int cadenceDays;
    private String status;
    private LocalDate nextBillingDate;

    public SubscriptionDto(String subscriptionId, String customerId, String variantId, int cadenceDays, String status, LocalDate nextBillingDate) {
        this.subscriptionId = subscriptionId;
        this.customerId = customerId;
        this.variantId = variantId;
        this.cadenceDays = cadenceDays;
        this.status = status;
        this.nextBillingDate = nextBillingDate;
    }

    public String getSubscriptionId() { return subscriptionId; }
    public String getCustomerId() { return customerId; }
    public String getVariantId() { return variantId; }
    public int getCadenceDays() { return cadenceDays; }
    public String getStatus() { return status; }
    public LocalDate getNextBillingDate() { return nextBillingDate; }
}

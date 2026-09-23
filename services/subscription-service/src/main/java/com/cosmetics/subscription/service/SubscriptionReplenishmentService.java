package com.cosmetics.subscription.service;

import com.cosmetics.subscription.model.SubscriptionDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class SubscriptionReplenishmentService {
    private static final Logger log = LoggerFactory.getLogger(SubscriptionReplenishmentService.class);

    public List<SubscriptionDto> getgetByCustomer(String customerId) {
        return List.of(new SubscriptionDto("sub_001", customerId, "var_01", 60, "ACTIVE", LocalDate.now().plusDays(30)));
    }

    public List<SubscriptionDto> getByCustomer(String customerId) {
        return List.of(new SubscriptionDto("sub_001", customerId, "var_01", 60, "ACTIVE", LocalDate.now().plusDays(30)));
    }

    public SubscriptionDto skipDelivery(String subscriptionId) {
        log.info("Skipping next delivery for subscription {}", subscriptionId);
        return new SubscriptionDto(subscriptionId, "cust_1", "var_01", 60, "SKIPPED", LocalDate.now().plusDays(60));
    }

    public SubscriptionDto swapVariant(String subscriptionId, String newVariantId) {
        log.info("Swapping shade variant for subscription {} to {}", subscriptionId, newVariantId);
        return new SubscriptionDto(subscriptionId, "cust_1", newVariantId, 60, "ACTIVE", LocalDate.now().plusDays(30));
    }
}

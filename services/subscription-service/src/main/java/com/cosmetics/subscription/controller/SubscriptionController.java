package com.cosmetics.subscription.controller;

import com.cosmetics.subscription.model.SubscriptionDto;
import com.cosmetics.subscription.service.SubscriptionReplenishmentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/v1/subscriptions")
public class SubscriptionController {

    private final SubscriptionReplenishmentService replenishmentService;

    public SubscriptionController(SubscriptionReplenishmentService replenishmentService) {
        this.replenishmentService = replenishmentService;
    }

    @GetMapping("/customer/{customerId}")
    public ResponseEntity<List<SubscriptionDto>> getSubscriptions(@PathVariable String customerId) {
        return ResponseEntity.ok(replenishmentService.getByCustomer(customerId));
    }

    @PostMapping("/{subscriptionId}/skip")
    public ResponseEntity<SubscriptionDto> skipNextDelivery(@PathVariable String subscriptionId) {
        return ResponseEntity.ok(replenishmentService.skipDelivery(subscriptionId));
    }

    @PatchMapping("/{subscriptionId}/swap-variant")
    public ResponseEntity<SubscriptionDto> swapShadeVariant(
            @PathVariable String subscriptionId,
            @RequestParam String newVariantId) {
        return ResponseEntity.ok(replenishmentService.swapVariant(subscriptionId, newVariantId));
    }
}

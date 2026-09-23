package com.cosmetics.subscription;

import com.cosmetics.subscription.model.SubscriptionDto;
import com.cosmetics.subscription.service.SubscriptionReplenishmentService;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class SubscriptionControllerTest {

    @Test
    public void testSkipAndSwap() {
        SubscriptionReplenishmentService svc = new SubscriptionReplenishmentService();
        SubscriptionDto skipped = svc.skipDelivery("sub_001");
        assertEquals("SKIPPED", skipped.getStatus());

        SubscriptionDto swapped = svc.swapVariant("sub_001", "var_02");
        assertEquals("var_02", swapped.getVariantId());
    }
}

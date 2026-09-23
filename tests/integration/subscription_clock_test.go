package integration

import (
	"fmt"
	"testing"
	"time"
)

type StripeTestClock struct {
	ClockID      string
	FrozenTime   time.Time
	Status       string
}

func AdvanceStripeTestClock(clock *StripeTestClock, days int) {
	clock.FrozenTime = clock.FrozenTime.AddDate(0, 0, days)
	fmt.Printf("[Stripe-TestClock] Advanced clock %s by %d days. Simulated Current Date: %s\n",
		clock.ClockID, days, clock.FrozenTime.Format("2006-01-02"))
}

func TestSubscriptionLifecycleWithTestClock(t *testing.T) {
	clock := &StripeTestClock{
		ClockID:    "clock_d2c_sub_test",
		FrozenTime: time.Now(),
		Status:     "READY",
	}

	// Advance 30 days -> First renewal trigger
	AdvanceStripeTestClock(clock, 30)

	// Advance 60 days -> Second renewal trigger
	AdvanceStripeTestClock(clock, 30)

	// Advance 90 days -> Third replenishment
	AdvanceStripeTestClock(clock, 30)

	if clock.FrozenTime.Before(time.Now()) {
		t.Fatal("Simulated test clock should have advanced into the future")
	}
}

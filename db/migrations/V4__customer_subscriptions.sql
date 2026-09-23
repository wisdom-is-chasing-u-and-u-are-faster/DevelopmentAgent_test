-- V4__customer_subscriptions.sql
-- Enterprise D2C Customer Subscriptions Schema

CREATE TYPE subscription_status_enum AS ENUM ('ACTIVE', 'PAUSED', 'SKIPPED', 'CANCELLED', 'PAST_DUE');

CREATE TABLE IF NOT EXISTS customer_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    variant_id UUID NOT NULL REFERENCES product_variants(variant_id) ON DELETE RESTRICT,
    cadence_days INT NOT NULL CHECK (cadence_days IN (30, 45, 60, 90)),
    status subscription_status_enum NOT NULL DEFAULT 'ACTIVE',
    current_price NUMERIC(10, 2) NOT NULL,
    payment_token VARCHAR(255) NOT NULL,
    next_billing_date DATE NOT NULL,
    retry_count INT NOT NULL DEFAULT 0,
    last_billed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_customer_id ON customer_subscriptions(customer_id);
CREATE INDEX idx_subscriptions_billing_batch ON customer_subscriptions(next_billing_date, status) WHERE status = 'ACTIVE';

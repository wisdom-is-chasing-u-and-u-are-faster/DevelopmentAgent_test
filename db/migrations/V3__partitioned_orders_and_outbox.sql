-- V3__partitioned_orders_and_outbox.sql
-- Enterprise Range-Partitioned Orders Table and Transactional Outbox

CREATE TABLE IF NOT EXISTS orders (
    order_id UUID NOT NULL DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    payment_intent_id VARCHAR(100),
    shipping_address JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, created_at),
    CONSTRAINT uq_orders_idempotency UNIQUE (idempotency_key, created_at)
) PARTITION BY RANGE (created_at);

-- Partitions for 2025 and 2026
CREATE TABLE IF NOT EXISTS orders_2025_q1 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-04-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2025_q2 PARTITION OF orders
    FOR VALUES FROM ('2025-04-01 00:00:00+00') TO ('2025-07-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2025_q3 PARTITION OF orders
    FOR VALUES FROM ('2025-07-01 00:00:00+00') TO ('2025-10-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2025_q4 PARTITION OF orders
    FOR VALUES FROM ('2025-10-01 00:00:00+00') TO ('2026-01-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS orders_2026_q1 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01 00:00:00+00') TO ('2026-04-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2026_q2 PARTITION OF orders
    FOR VALUES FROM ('2026-04-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2026_q3 PARTITION OF orders
    FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');
CREATE TABLE IF NOT EXISTS orders_2026_q4 PARTITION OF orders
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2027-01-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS order_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    order_created_at TIMESTAMPTZ NOT NULL,
    variant_id UUID NOT NULL REFERENCES product_variants(variant_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    FOREIGN KEY (order_id, order_created_at) REFERENCES orders(order_id, created_at) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactional_outbox (
    outbox_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_outbox_unprocessed ON transactional_outbox(created_at) WHERE is_processed = FALSE;

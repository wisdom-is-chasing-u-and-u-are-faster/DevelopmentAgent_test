-- V2__inventory_ledger.sql
-- Non-Locking Append-Only Physical Inventory Ledger

CREATE TABLE IF NOT EXISTS inventory_ledger (
    ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID NOT NULL REFERENCES product_variants(variant_id) ON DELETE RESTRICT,
    quantity_delta INT NOT NULL,
    reference_type VARCHAR(50) NOT NULL CHECK (reference_type IN ('FLASH_DROP_INIT', 'ORDER_COMMIT', 'RETURN', 'ADJUSTMENT')),
    reference_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_ledger_variant ON inventory_ledger(variant_id, created_at);
CREATE INDEX idx_inventory_ledger_reference ON inventory_ledger(reference_type, reference_id);

-- Tamper-Evident Cryptographic Audit Ledger
ALTER TABLE ticket_audit_ledger ADD COLUMN IF NOT EXISTS prev_checksum VARCHAR(64) DEFAULT '0000000000000000000000000000000000000000000000000000000000000000';
ALTER TABLE ticket_audit_ledger ADD COLUMN IF NOT EXISTS sequence_number BIGSERIAL;

-- Ensure audit ledger is strictly append-only
CREATE OR REPLACE FUNCTION prevent_audit_tampering()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE' OR TG_OP = 'UPDATE') THEN
        RAISE EXCEPTION 'Audit ledger records are strictly immutable and cannot be updated or deleted!';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_ledger_immutable ON ticket_audit_ledger;
CREATE TRIGGER trg_audit_ledger_immutable
BEFORE UPDATE OR DELETE ON ticket_audit_ledger
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_tampering();

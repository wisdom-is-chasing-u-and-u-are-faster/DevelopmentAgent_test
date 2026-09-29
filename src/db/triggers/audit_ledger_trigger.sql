-- Automatic Audit Ledger Entry Generator on Ticket Mutations
CREATE OR REPLACE FUNCTION audit_ticket_mutation()
RETURNS TRIGGER AS $$
DECLARE
    v_actor_id UUID;
    v_action VARCHAR(64);
    v_old JSONB := NULL;
    v_new JSONB := NULL;
    v_diff JSONB := '{}'::jsonb;
    v_last_hash VARCHAR(64) := '0000000000000000000000000000000000000000000000000000000000000000';
    v_new_hash VARCHAR(64);
BEGIN
    -- Extract session actor id if set, else fallback to requester or system
    BEGIN
        v_actor_id := current_setting('app.current_user_id', true)::uuid;
    EXCEPTION WHEN OTHERS THEN
        v_actor_id := COALESCE(NEW.assigned_agent_id, NEW.requester_id);
    END;

    IF (TG_OP = 'INSERT') THEN
        v_action := 'TICKET_CREATED';
        v_new := to_jsonb(NEW);
        v_diff := jsonb_build_object('title', NEW.title, 'status', NEW.status, 'priority', NEW.priority);
    ELSIF (TG_OP = 'UPDATE') THEN
        v_action := 'TICKET_UPDATED';
        v_old := to_jsonb(OLD);
        v_new := to_jsonb(NEW);
        IF (OLD.status IS DISTINCT FROM NEW.status) THEN
            v_action := 'STATUS_CHANGED';
        END IF;
        v_diff := jsonb_build_object(
            'old_status', OLD.status,
            'new_status', NEW.status,
            'old_agent', OLD.assigned_agent_id,
            'new_agent', NEW.assigned_agent_id,
            'version', NEW.version
        );
    END IF;

    -- Fetch previous checksum for hash chaining
    SELECT checksum INTO v_last_hash FROM ticket_audit_ledger 
    WHERE ticket_id = NEW.ticket_id 
    ORDER BY audit_id DESC LIMIT 1;
    
    IF v_last_hash IS NULL THEN
        v_last_hash := '0000000000000000000000000000000000000000000000000000000000000000';
    END IF;

    -- Compute SHA-256 hash using pgcrypto digest
    v_new_hash := encode(digest(v_last_hash || NEW.ticket_id::text || v_action || v_diff::text || CURRENT_TIMESTAMP::text, 'sha256'), 'hex');

    INSERT INTO ticket_audit_ledger (ticket_id, actor_id, action_type, old_state, new_state, diff_payload, prev_checksum, checksum)
    VALUES (NEW.ticket_id, COALESCE(v_actor_id, NEW.requester_id), v_action, v_old, v_new, v_diff, v_last_hash, v_new_hash);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_ticket ON tickets;
CREATE TRIGGER trg_audit_ticket
AFTER INSERT OR UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION audit_ticket_mutation();

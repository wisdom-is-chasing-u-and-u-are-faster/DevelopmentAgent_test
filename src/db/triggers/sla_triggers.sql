-- SLA History Logging Trigger
CREATE OR REPLACE FUNCTION log_sla_event_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.sla_ack_status IS DISTINCT FROM NEW.sla_ack_status) THEN
        INSERT INTO sla_events_history (ticket_id, sla_type, old_status, new_status, deadline, details)
        VALUES (NEW.ticket_id, 'ACK', OLD.sla_ack_status, NEW.sla_ack_status, NEW.sla_ack_deadline, jsonb_build_object('priority', NEW.priority));
    END IF;

    IF (OLD.sla_resolve_status IS DISTINCT FROM NEW.sla_resolve_status) THEN
        INSERT INTO sla_events_history (ticket_id, sla_type, old_status, new_status, deadline, details)
        VALUES (NEW.ticket_id, 'RESOLVE', OLD.sla_resolve_status, NEW.sla_resolve_status, NEW.sla_resolve_deadline, jsonb_build_object('priority', NEW.priority));
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ticket_sla_change ON tickets;
CREATE TRIGGER trg_ticket_sla_change
AFTER UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION log_sla_event_change();

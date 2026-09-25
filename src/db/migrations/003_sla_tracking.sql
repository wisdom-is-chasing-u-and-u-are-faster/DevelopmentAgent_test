-- SLA Tracking Historical Table and Status Triggers
CREATE TABLE IF NOT EXISTS sla_events_history (
    event_id BIGSERIAL PRIMARY KEY,
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    sla_type VARCHAR(32) NOT NULL, -- 'ACK' or 'RESOLVE'
    old_status VARCHAR(16),
    new_status VARCHAR(16) NOT NULL,
    deadline TIMESTAMPTZ,
    triggered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_sla_history_ticket ON sla_events_history (ticket_id, triggered_at DESC);

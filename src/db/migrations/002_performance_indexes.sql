-- Performance Indexes for Core Ticketing Tables
CREATE INDEX IF NOT EXISTS idx_tickets_dept_status ON tickets (department_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_requester ON tickets (requester_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_agent ON tickets (assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_sla_resolve ON tickets (sla_resolve_deadline) 
    WHERE status NOT IN ('RESOLVED', 'CLOSED');
CREATE INDEX IF NOT EXISTS idx_comments_ticket ON ticket_comments (ticket_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_audit_ticket ON ticket_audit_ledger (ticket_id, timestamp DESC);

-- Row-Level Security (RLS) Policies and Tenant / Department Isolation
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;

-- 1. Tickets Policy: Requesters, Agents, and Admins
DROP POLICY IF EXISTS p_tickets_isolation ON tickets;
CREATE POLICY p_tickets_isolation ON tickets
    FOR ALL
    USING (
        -- Admins have unrestricted access
        current_setting('app.current_user_role', true) = 'ADMIN'
        -- Requesters can see tickets they requested
        OR (
            current_setting('app.current_user_role', true) = 'REQUESTER'
            AND requester_id = current_setting('app.current_user_id', true)::uuid
        )
        -- Agents can see tickets assigned to them or in their department
        OR (
            current_setting('app.current_user_role', true) = 'AGENT'
            AND (
                assigned_agent_id = current_setting('app.current_user_id', true)::uuid
                OR department_id = current_setting('app.current_department_id', true)::uuid
            )
        )
    )
    WITH CHECK (
        current_setting('app.current_user_role', true) = 'ADMIN'
        OR (
            current_setting('app.current_user_role', true) = 'REQUESTER'
            AND requester_id = current_setting('app.current_user_id', true)::uuid
        )
        OR (
            current_setting('app.current_user_role', true) = 'AGENT'
            AND (
                assigned_agent_id = current_setting('app.current_user_id', true)::uuid
                OR department_id = current_setting('app.current_department_id', true)::uuid
            )
        )
    );

-- 2. Ticket Comments Policy
DROP POLICY IF EXISTS p_comments_isolation ON ticket_comments;
CREATE POLICY p_comments_isolation ON ticket_comments
    FOR ALL
    USING (
        current_setting('app.current_user_role', true) = 'ADMIN'
        OR (
            -- Requesters cannot see internal comments
            current_setting('app.current_user_role', true) = 'REQUESTER'
            AND is_internal = FALSE
            AND EXISTS (
                SELECT 1 FROM tickets t 
                WHERE t.ticket_id = ticket_comments.ticket_id 
                AND t.requester_id = current_setting('app.current_user_id', true)::uuid
            )
        )
        OR (
            -- Agents can see internal and external comments for tickets they can access
            current_setting('app.current_user_role', true) = 'AGENT'
            AND EXISTS (
                SELECT 1 FROM tickets t
                WHERE t.ticket_id = ticket_comments.ticket_id
                AND (
                    t.assigned_agent_id = current_setting('app.current_user_id', true)::uuid
                    OR t.department_id = current_setting('app.current_department_id', true)::uuid
                )
            )
        )
    );

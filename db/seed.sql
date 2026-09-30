-- Seed Data: Enterprise Ticketing Management System (ETMS)

INSERT OR IGNORE INTO agents (id, name, email, department, skills, active_ticket_count, max_capacity, is_available) VALUES
('agent-001', 'Alex Mercer', 'alex.mercer@enterprise.internal', 'Infrastructure', 'cloud,kubernetes,terraform,outage', 2, 5, 1),
('agent-002', 'Jordan Lee', 'jordan.lee@enterprise.internal', 'Database', 'postgresql,redis,replication,tuning', 1, 5, 1),
('agent-003', 'Samira Khan', 'samira.khan@enterprise.internal', 'Security', 'auth,jwt,soc2,rbac,firewall', 1, 4, 1),
('agent-004', 'Elena Rostova', 'elena.rostova@enterprise.internal', 'Applications', 'api,frontend,react,gateway', 3, 6, 1),
('agent-005', 'Marcus Chen', 'marcus.chen@enterprise.internal', 'DevOps', 'ci-cd,pipelines,docker,helm', 0, 5, 1);

INSERT OR IGNORE INTO tickets (id, ticket_number, title, description, status, priority, department, category, requester_name, requester_email, assigned_agent_id, assigned_agent_name, sla_target_hours, sla_elapsed_hours, sla_status, version, created_at, updated_at) VALUES
('tkt-1001', 'INC-2026-0834', 'Primary Cloud SQL HA Failover Interruption', 'Automated failover of PostgreSQL replica caused a 45-second read disruption across EMEA region.', 'IN_PROGRESS', 'P1', 'Database', 'Outage', 'David Clark', 'david.clark@enterprise.internal', 'agent-002', 'Jordan Lee', 2.0, 0.8, 'WITHIN_SLA', 2, '2026-09-24T08:30:00Z', '2026-09-24T09:15:00Z'),
('tkt-1002', 'INC-2026-0835', 'API Gateway Rate-Limiting Policy Spikes', 'Traffic spike from mobile clients triggering unexpected 429 Too Many Requests.', 'TRIAGED', 'P2', 'Applications', 'Performance', 'Sarah Connor', 'sarah.connor@enterprise.internal', 'agent-004', 'Elena Rostova', 4.0, 2.5, 'APPROACHING_THRESHOLD', 1, '2026-09-24T09:00:00Z', '2026-09-24T09:30:00Z'),
('tkt-1003', 'INC-2026-0836', 'Kubernetes Cluster Worker Node Memory Pressure', 'Node pool in us-central1 reporting memory utilization exceeding 92%.', 'ASSIGNED', 'P2', 'Infrastructure', 'Infrastructure', 'Michael Vance', 'michael.vance@enterprise.internal', 'agent-001', 'Alex Mercer', 4.0, 1.2, 'WITHIN_SLA', 1, '2026-09-24T09:15:00Z', '2026-09-24T09:45:00Z'),
('tkt-1004', 'REQ-2026-0142', 'Provision Stage 2 RBAC Role for Compliance Audit', 'Requesting read-only database and audit log inspection permissions for Q3 SOC 2 auditor.', 'NEW', 'P3', 'Security', 'Access Request', 'Rachel Adams', 'rachel.adams@enterprise.internal', NULL, NULL, 8.0, 0.5, 'WITHIN_SLA', 1, '2026-09-24T10:00:00Z', '2026-09-24T10:00:00Z'),
('tkt-1005', 'REQ-2026-0143', 'SSL Certificate Renewal for internal billing gateway', 'Wildcard certificate expiring in 14 days requires automated rotation.', 'RESOLVED', 'P3', 'Security', 'Maintenance', 'Brian Taylor', 'brian.taylor@enterprise.internal', 'agent-003', 'Samira Khan', 12.0, 3.4, 'WITHIN_SLA', 3, '2026-09-23T14:00:00Z', '2026-09-24T07:20:00Z');

INSERT OR IGNORE INTO user_settings (user_id, name, email, role, slack_notifications, teams_notifications, email_notifications, theme, updated_at) VALUES
('default-user', 'Prasanna Deshpande', 'prasanna_deshpande1@persistent.com', 'Operations Lead', 1, 1, 1, 'light', '2026-09-24T10:00:00Z');

INSERT OR IGNORE INTO audit_ledger (id, entity_type, entity_id, action, actor, from_status, to_status, payload_checksum, previous_hash, current_hash, timestamp) VALUES
('audit-0001', 'SYSTEM', 'GENESIS', 'SYSTEM_INITIALIZATION', 'SYSTEM_BOOTSTRAP', NULL, 'ACTIVE', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '00000000000000000000000000000000000000000000000000000000000000', '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4', '2026-09-24T08:00:00Z');

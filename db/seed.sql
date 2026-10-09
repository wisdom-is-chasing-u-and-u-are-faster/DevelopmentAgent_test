-- ============================================================================
-- Enterprise Ticketing Management System (ETMS) - Baseline Seed Data
-- ============================================================================

-- Seed Departments
INSERT OR IGNORE INTO departments (id, name, code) VALUES
    ('dept-it-ops', 'IT Infrastructure & Operations', 'IT_OPS'),
    ('dept-sec-ops', 'Cybersecurity & InfoSec Operations', 'SEC_OPS'),
    ('dept-app-dev', 'Enterprise Application Engineering', 'APP_DEV'),
    ('dept-fin-ops', 'Billing & Financial Operations', 'FIN_OPS'),
    ('dept-hr-ops', 'Corporate HR Services', 'HR_OPS');

-- Seed Categories with Tiered SLA Profiles
INSERT OR IGNORE INTO categories (id, name, department_id, default_priority, sla_target_response_mins, sla_target_resolution_hours) VALUES
    ('cat-cloud-outage', 'Cloud Infrastructure Outage', 'dept-it-ops', 'P1', 5, 2),
    ('cat-security-breach', 'Suspected Phishing / Malware Incident', 'dept-sec-ops', 'P1', 10, 4),
    ('cat-db-perf', 'Database Latency & Query Degradation', 'dept-it-ops', 'P2', 15, 8),
    ('cat-api-error', 'Payment Gateway 5xx Failure', 'dept-app-dev', 'P2', 15, 6),
    ('cat-vpn-access', 'Remote VPN & Zero Trust Connectivity', 'dept-it-ops', 'P3', 60, 24),
    ('cat-billing-dispute', 'Corporate Invoice Adjustment', 'dept-fin-ops', 'P3', 120, 48),
    ('cat-hardware-req', 'Workstation Laptop Refresh', 'dept-it-ops', 'P4', 240, 72),
    ('cat-access-grant', 'Jira / GitHub Role Permission Request', 'dept-sec-ops', 'P3', 60, 24);

-- Seed Agents
INSERT OR IGNORE INTO agents (id, name, email, department_id, tier, max_capacity, is_available) VALUES
    ('agent-001', 'Alex Rivera', 'alex.rivera@enterprise.internal', 'dept-it-ops', 3, 8, 1),
    ('agent-002', 'Elena Rostova', 'elena.rostova@enterprise.internal', 'dept-sec-ops', 3, 6, 1),
    ('agent-003', 'Marcus Chen', 'marcus.chen@enterprise.internal', 'dept-app-dev', 2, 10, 1),
    ('agent-004', 'Sarah Jenkins', 'sarah.jenkins@enterprise.internal', 'dept-it-ops', 1, 12, 1),
    ('agent-005', 'David Kim', 'david.kim@enterprise.internal', 'dept-fin-ops', 2, 10, 1);

-- Seed Agent Skills Taxonomy
INSERT OR IGNORE INTO agent_skills (id, agent_id, skill_name, proficiency_level) VALUES
    ('skill-001', 'agent-001', 'Cloud Infrastructure Outage', 5),
    ('skill-002', 'agent-001', 'Database Latency & Query Degradation', 4),
    ('skill-003', 'agent-001', 'Remote VPN & Zero Trust Connectivity', 5),
    ('skill-004', 'agent-002', 'Suspected Phishing / Malware Incident', 5),
    ('skill-005', 'agent-002', 'Jira / GitHub Role Permission Request', 4),
    ('skill-006', 'agent-003', 'Payment Gateway 5xx Failure', 5),
    ('skill-007', 'agent-003', 'Database Latency & Query Degradation', 3),
    ('skill-008', 'agent-004', 'Remote VPN & Zero Trust Connectivity', 3),
    ('skill-009', 'agent-004', 'Workstation Laptop Refresh', 5),
    ('skill-010', 'agent-005', 'Corporate Invoice Adjustment', 5);

-- Seed Sample Tickets
INSERT OR IGNORE INTO tickets (
    id, ticket_number, title, description, category, priority, status, department_id,
    requester_email, assigned_agent_id, version, idempotency_key, tags, metadata, created_at, updated_at
) VALUES
    (
        'tick-1001', 'INC-8091', 'Primary Cloud SQL PostgreSQL Database High Memory Alarm',
        'Database memory utilization exceeded 95% threshold in us-central1 production cluster.',
        'Database Latency & Query Degradation', 'P1', 'IN_PROGRESS', 'dept-it-ops',
        'sre-lead@enterprise.internal', 'agent-001', 2, 'idem-seed-001',
        '["cloud-sql", "p1", "infrastructure"]', '{"cluster": "db-prod-01"}',
        DATETIME('now', '-2 hours'), DATETIME('now', '-30 minutes')
    ),
    (
        'tick-1002', 'INC-8092', 'Critical Zero-Day Phishing Email Detected in Executive Mailbox',
        'Inbound email payload containing obfuscated macro attachment identified by Falcon sensor.',
        'Suspected Phishing / Malware Incident', 'P1', 'TRIAGED', 'dept-sec-ops',
        'soc-alert@enterprise.internal', 'agent-002', 1, 'idem-seed-002',
        '["security", "phishing", "p1"]', '{"source_ip": "198.51.100.42"}',
        DATETIME('now', '-1 hour'), DATETIME('now', '-45 minutes')
    ),
    (
        'tick-1003', 'REQ-4015', 'Requester New Hire Developer Onboarding Access Pack',
        'Provision GitHub Enterprise team membership and Google Cloud IAM Developer roles.',
        'Jira / GitHub Role Permission Request', 'P3', 'SUBMITTED', 'dept-sec-ops',
        'hr-onboarding@enterprise.internal', NULL, 1, 'idem-seed-003',
        '["iam", "permissions", "onboarding"]', '{"user": "jdoe"}',
        DATETIME('now', '-15 minutes'), DATETIME('now', '-15 minutes')
    );

-- Seed Initial SLA Records for Sample Tickets
INSERT OR IGNORE INTO sla_tracking (
    id, ticket_id, sla_tier, threshold_50_fired, threshold_75_fired, threshold_100_breached,
    response_elapsed_ms, resolution_elapsed_ms, response_met, resolution_met
) VALUES
    ('sla-1001', 'tick-1001', 'TIER_1_HA', 1, 0, 0, 180000, 7200000, 1, NULL),
    ('sla-1002', 'tick-1002', 'TIER_1_HA', 0, 0, 0, 60000, 3600000, 1, NULL),
    ('sla-1003', 'tick-1003', 'STANDARD', 0, 0, 0, 0, 0, NULL, NULL);

-- Seed Initial Audit Ledger Entries (SHA-256 Chained)
INSERT OR IGNORE INTO audit_ledger (
    id, ticket_id, actor_id, actor_role, action, previous_state, new_state,
    checksum_sha256, previous_checksum_sha256, timestamp
) VALUES
    (
        'audit-001', 'tick-1001', 'system', 'SYSTEM', 'TICKET_CREATED',
        '{}', '{"status": "SUBMITTED", "priority": "P1"}',
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '0000000000000000000000000000000000000000000000000000000000000000',
        DATETIME('now', '-2 hours')
    ),
    (
        'audit-002', 'tick-1001', 'alex.rivera@enterprise.internal', 'AGENT', 'STATUS_TRANSITION',
        '{"status": "SUBMITTED"}', '{"status": "IN_PROGRESS", "assigned_agent_id": "agent-001"}',
        '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        DATETIME('now', '-30 minutes')
    );

-- Seed Initial UI Presets (Theme & Worklist Layout Configurations)
INSERT OR IGNORE INTO ui_presets (id, preset_type, name, config_json, is_global_default, created_by) VALUES
    (
        'preset-theme-slate-default',
        'THEME_COLOR',
        'Enterprise Slate (Default)',
        '{"primary":"#3b82f6","primary_hover":"#2563eb","bg_primary":"#0f172a","bg_secondary":"#1e293b","bg_card":"#334155","text_primary":"#f8fafc","text_muted":"#94a3b8","border":"#475569","success":"#10b981","warning":"#f59e0b","danger":"#ef4444"}',
        1,
        'global-admin'
    ),
    (
        'preset-theme-ocean-blue',
        'THEME_COLOR',
        'Ocean Deep Blue',
        '{"primary":"#0284c7","primary_hover":"#0369a1","bg_primary":"#082f49","bg_secondary":"#0c4a6e","bg_card":"#075985","text_primary":"#f0f9ff","text_muted":"#7dd3fc","border":"#0369a1","success":"#14b8a6","warning":"#f59e0b","danger":"#f43f5e"}',
        0,
        'global-admin'
    ),
    (
        'preset-theme-forest-emerald',
        'THEME_COLOR',
        'Forest Emerald Operations',
        '{"primary":"#059669","primary_hover":"#047857","bg_primary":"#064e3b","bg_secondary":"#065f46","bg_card":"#047857","text_primary":"#ecfdf5","text_muted":"#6ee7b7","border":"#059669","success":"#10b981","warning":"#fbbf24","danger":"#f87171"}',
        0,
        'global-admin'
    ),
    (
        'preset-theme-crimson-incident',
        'THEME_COLOR',
        'Crimson High Alert',
        '{"primary":"#e11d48","primary_hover":"#be123c","bg_primary":"#18181b","bg_secondary":"#27272a","bg_card":"#3f3f46","text_primary":"#fafafa","text_muted":"#a1a1aa","border":"#52525b","success":"#22c55e","warning":"#eab308","danger":"#ef4444"}',
        0,
        'global-admin'
    ),
    (
        'preset-layout-standard-triage',
        'WORKLIST_LAYOUT',
        'Standard Triage Layout',
        '{"visible_columns":["ticket_number","title","category","priority","status","assigned_agent_name","actions"],"density":"normal","sort_by":"created_at","sort_order":"desc","page_size":20,"show_quick_filters":true}',
        1,
        'global-admin'
    ),
    (
        'preset-layout-sla-matrix',
        'WORKLIST_LAYOUT',
        'SLA Priority Matrix',
        '{"visible_columns":["ticket_number","title","priority","status","sla_deadline_resolution","actions"],"density":"compact","sort_by":"sla_deadline_resolution","sort_order":"asc","page_size":25,"show_quick_filters":true}',
        0,
        'global-admin'
    ),
    (
        'preset-layout-executive-summary',
        'WORKLIST_LAYOUT',
        'Executive Overview',
        '{"visible_columns":["ticket_number","title","category","priority","status","assigned_agent_name","created_at"],"density":"comfortable","sort_by":"created_at","sort_order":"desc","page_size":50,"show_quick_filters":false}',
        0,
        'global-admin'
    ),
    (
        'preset-layout-compact-grid',
        'WORKLIST_LAYOUT',
        'Compact Operations Grid',
        '{"visible_columns":["ticket_number","title","priority","status","assigned_agent_name","actions"],"density":"compact","sort_by":"priority","sort_order":"asc","page_size":20,"show_quick_filters":true}',
        0,
        'global-admin'
    );

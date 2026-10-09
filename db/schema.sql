-- ============================================================================
-- Enterprise Ticketing Management System (ETMS) - Database Schema DDL
-- Supported Engines: PostgreSQL 15+ / SQLite 3+
-- Author: Enterprise IT Architecture
-- ============================================================================

-- 1. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    department_id VARCHAR(64) NOT NULL,
    default_priority VARCHAR(8) DEFAULT 'P3',
    sla_target_response_mins INTEGER DEFAULT 60,
    sla_target_resolution_hours INTEGER DEFAULT 24,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- 3. Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    department_id VARCHAR(64) NOT NULL,
    tier INTEGER DEFAULT 1,
    max_capacity INTEGER DEFAULT 10,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- 4. Agent Skills Taxonomy Table
CREATE TABLE IF NOT EXISTS agent_skills (
    id VARCHAR(64) PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    skill_name VARCHAR(64) NOT NULL,
    proficiency_level INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- 5. Core Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    id VARCHAR(64) PRIMARY KEY,
    ticket_number VARCHAR(32) NOT NULL UNIQUE,
    title VARCHAR(256) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(64) NOT NULL,
    priority VARCHAR(8) NOT NULL DEFAULT 'P3',
    status VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED',
    department_id VARCHAR(64) NOT NULL,
    requester_email VARCHAR(128) NOT NULL,
    assigned_agent_id VARCHAR(64),
    version INTEGER NOT NULL DEFAULT 1,
    idempotency_key VARCHAR(128) UNIQUE,
    sla_deadline_response TIMESTAMP,
    sla_deadline_resolution TIMESTAMP,
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(id)
);

-- 6. SLA Tracking Table
CREATE TABLE IF NOT EXISTS sla_tracking (
    id VARCHAR(64) PRIMARY KEY,
    ticket_id VARCHAR(64) NOT NULL UNIQUE,
    sla_tier VARCHAR(16) DEFAULT 'STANDARD',
    threshold_50_fired BOOLEAN DEFAULT FALSE,
    threshold_75_fired BOOLEAN DEFAULT FALSE,
    threshold_100_breached BOOLEAN DEFAULT FALSE,
    response_elapsed_ms BIGINT DEFAULT 0,
    resolution_elapsed_ms BIGINT DEFAULT 0,
    response_met BOOLEAN DEFAULT NULL,
    resolution_met BOOLEAN DEFAULT NULL,
    last_evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- 7. Immutable Cryptographic Audit Ledger Table
CREATE TABLE IF NOT EXISTS audit_ledger (
    id VARCHAR(64) PRIMARY KEY,
    ticket_id VARCHAR(64) NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    actor_role VARCHAR(64) NOT NULL DEFAULT 'SYSTEM',
    action VARCHAR(64) NOT NULL,
    previous_state TEXT DEFAULT '{}',
    new_state TEXT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    previous_checksum_sha256 VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- 8. Idempotency Request Cache Table
CREATE TABLE IF NOT EXISTS idempotency_records (
    idempotency_key VARCHAR(128) PRIMARY KEY,
    ticket_id VARCHAR(64) NOT NULL,
    response_payload TEXT NOT NULL,
    status_code INTEGER DEFAULT 201,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. UI Presets Table (Theme & Worklist Layout Configurations)
CREATE TABLE IF NOT EXISTS ui_presets (
    id VARCHAR(64) PRIMARY KEY,
    preset_type VARCHAR(32) NOT NULL,
    name VARCHAR(128) NOT NULL,
    config_json TEXT NOT NULL,
    is_global_default BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(128) DEFAULT 'global-admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Indexes for Query Acceleration
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_department ON tickets(department_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_agent ON tickets(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_ticket_id ON audit_ledger(ticket_id);
CREATE INDEX IF NOT EXISTS idx_agent_skills_agent_id ON agent_skills(agent_id);
CREATE INDEX IF NOT EXISTS idx_ui_presets_type ON ui_presets(preset_type);

-- Baseline Schema DDL for Enterprise Ticketing Management System
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS departments (
    department_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department_code VARCHAR(32) UNIQUE NOT NULL,
    department_name VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    role VARCHAR(32) NOT NULL,
    department_id UUID REFERENCES departments(department_id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(32) UNIQUE NOT NULL,
    requester_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    assigned_agent_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    department_id UUID NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED',
    priority VARCHAR(16) NOT NULL DEFAULT 'P3',
    category VARCHAR(64) NOT NULL,
    sla_ack_deadline TIMESTAMPTZ,
    sla_resolve_deadline TIMESTAMPTZ,
    sla_ack_status VARCHAR(16) DEFAULT 'RUNNING',
    sla_resolve_status VARCHAR(16) DEFAULT 'RUNNING',
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_comments (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    body TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_audit_ledger (
    audit_id BIGSERIAL PRIMARY KEY,
    ticket_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    old_state JSONB,
    new_state JSONB,
    diff_payload JSONB NOT NULL,
    checksum VARCHAR(64),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

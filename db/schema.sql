-- Database DDL Schema for Agent Evaluation Platform (3NF Relational Persistence)
-- Compatible with SQLite3 and PostgreSQL
-- Initiative: SDLC Plan: Agent Evaluation (Eval) Platform (ARCH-5136)

CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(128) NOT NULL,
    model VARCHAR(128) NOT NULL,
    system_prompt TEXT DEFAULT '',
    capabilities TEXT DEFAULT '[]',
    pass_rate REAL DEFAULT 0.0,
    latency_p95 INTEGER DEFAULT 0,
    runs_evaluated INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_model ON agents(model);

CREATE TABLE IF NOT EXISTS datasets (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(128) NOT NULL,
    test_count INTEGER DEFAULT 0,
    test_cases TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_datasets_domain ON datasets(domain);

CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    mode VARCHAR(64) NOT NULL,
    agent_ids TEXT DEFAULT '[]',
    dataset_id VARCHAR(64),
    concurrency INTEGER DEFAULT 1,
    judge_model VARCHAR(128) DEFAULT 'gpt-4o',
    status VARCHAR(32) DEFAULT 'pending',
    pass_rate REAL DEFAULT 0.0,
    judge_agreement REAL DEFAULT 0.0,
    completed_steps INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at);

CREATE TABLE IF NOT EXISTS trajectories (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64),
    agent_name VARCHAR(255) NOT NULL,
    status VARCHAR(32) DEFAULT 'completed',
    turns TEXT DEFAULT '[]',
    a2a_cards TEXT DEFAULT '[]',
    judge_evaluation TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_trajectories_run ON trajectories(run_id);
CREATE INDEX IF NOT EXISTS idx_trajectories_agent ON trajectories(agent_id);
CREATE INDEX IF NOT EXISTS idx_trajectories_status ON trajectories(status);

CREATE TABLE IF NOT EXISTS annotations (
    id VARCHAR(64) PRIMARY KEY,
    trajectory_id VARCHAR(64) NOT NULL,
    evaluator VARCHAR(128) NOT NULL,
    verdict VARCHAR(64) NOT NULL,
    taxonomy VARCHAR(128) NOT NULL,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trajectory_id) REFERENCES trajectories(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_annotations_trajectory ON annotations(trajectory_id);
CREATE INDEX IF NOT EXISTS idx_annotations_verdict ON annotations(verdict);

CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    payload TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);

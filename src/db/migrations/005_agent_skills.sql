-- Agent Skills Taxonomy and Workload Tracking
CREATE TABLE IF NOT EXISTS skills (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_code VARCHAR(64) UNIQUE NOT NULL,
    skill_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_skills (
    agent_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency_level INT NOT NULL CHECK (proficiency_level BETWEEN 1 AND 5),
    PRIMARY KEY (agent_id, skill_id)
);

CREATE TABLE IF NOT EXISTS agent_workload (
    agent_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    active_ticket_count INT DEFAULT 0 NOT NULL CHECK (active_ticket_count >= 0),
    max_capacity INT DEFAULT 10 NOT NULL CHECK (max_capacity > 0),
    status VARCHAR(32) DEFAULT 'AVAILABLE' NOT NULL, -- 'AVAILABLE', 'BUSY', 'OFFLINE'
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Seed baseline skills
INSERT INTO skills (skill_code, skill_name, category)
VALUES 
    ('NETWORK_FIREWALL', 'Network & Firewall Infrastructure', 'INFRASTRUCTURE'),
    ('IDENTITY_ACCESS', 'Active Directory & IAM Governance', 'SECURITY'),
    ('HARDWARE_SUPPORT', 'Workstation & Hardware Provisioning', 'OPERATIONS'),
    ('CLOUD_GCP', 'Google Cloud Platform Services', 'CLOUD')
ON CONFLICT (skill_code) DO NOTHING;

-- Populate initial agent workload tracking for agents
INSERT INTO agent_workload (agent_id, active_ticket_count, max_capacity, status)
SELECT user_id, 0, 10, 'AVAILABLE' FROM users WHERE role = 'AGENT'
ON CONFLICT (agent_id) DO NOTHING;

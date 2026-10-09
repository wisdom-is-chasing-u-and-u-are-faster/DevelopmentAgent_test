-- Seed default departments and initial users
INSERT INTO departments (department_id, department_code, department_name, is_active)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'IT_SUPPORT', 'IT Support & Infrastructure', TRUE),
    ('22222222-2222-2222-2222-222222222222', 'SECURITY', 'Information Security & Compliance', TRUE),
    ('33333333-3333-3333-3333-333333333333', 'FACILITIES', 'Facilities & Operations', TRUE),
    ('44444444-4444-4444-4444-444444444444', 'HR', 'Human Resources', TRUE)
ON CONFLICT (department_code) DO NOTHING;

INSERT INTO users (user_id, email, first_name, last_name, role, department_id, is_active)
VALUES 
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'requester@enterprise.com', 'Jane', 'Requester', 'REQUESTER', '44444444-4444-4444-4444-444444444444', TRUE),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'agent1@enterprise.com', 'Alex', 'Support', 'AGENT', '11111111-1111-1111-1111-111111111111', TRUE),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'agent2@enterprise.com', 'Sam', 'SecOps', 'AGENT', '22222222-2222-2222-2222-222222222222', TRUE),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'admin@enterprise.com', 'Sarah', 'Admin', 'ADMIN', '11111111-1111-1111-1111-111111111111', TRUE)
ON CONFLICT (email) DO NOTHING;

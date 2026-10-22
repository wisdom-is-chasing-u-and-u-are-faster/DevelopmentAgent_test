-- DML Seed Data for Agent Evaluation Platform
-- Initiative: SDLC Plan: Agent Evaluation (Eval) Platform (ARCH-5136)

-- Clean existing data
DELETE FROM annotations;
DELETE FROM trajectories;
DELETE FROM runs;
DELETE FROM datasets;
DELETE FROM agents;
DELETE FROM audit_logs;

-- Agents Seed
INSERT INTO agents (id, name, role, model, system_prompt, capabilities, pass_rate, latency_p95, runs_evaluated, status)
VALUES
('agt-swe-01', 'SWE-Agent Alpha', 'Software Engineer', 'claude-3-7-sonnet', 'You are an autonomous senior software engineer agent equipped with terminal and git tools.', '["code_generation", "bash_execution", "git_ops", "unit_testing"]', 94.2, 1250, 142, 'active'),
('agt-sec-02', 'VulnAudit Guardian', 'Security Auditor', 'gpt-4o', 'You are a cybersecurity penetration testing and SAST auditing agent.', '["sast_scanning", "secret_detection", "dependency_audit", "remediation"]', 91.8, 980, 98, 'active'),
('agt-data-03', 'DataPipelines Pro', 'Data Engineer', 'gemini-1.5-pro', 'You specialize in distributed data pipeline optimization and schema synthesis.', '["sql_generation", "etl_validation", "schema_migration"]', 88.5, 1410, 64, 'active');

-- Golden Datasets Seed
INSERT INTO datasets (id, name, domain, test_count, test_cases)
VALUES
('ds-webarena-01', 'WebArena Golden Benchmark', 'Web Navigation & Actions', 120, '[{"id": "tc-101", "prompt": "Book the cheapest flight from SFO to JFK on Dec 15th", "expected_outcome": "Confirmation received with ticket under $300"}, {"id": "tc-102", "prompt": "Add item #4582 to shopping cart and apply coupon CODE10", "expected_outcome": "Cart total reduced by 10%"}]'),
('ds-swebench-02', 'SWE-bench Verified Core', 'Software Bug Resolution', 85, '[{"id": "tc-201", "prompt": "Resolve race condition in connection pool release method", "expected_outcome": "All concurrent integration tests pass without deadlock"}]');

-- Evaluation Runs Seed
INSERT INTO runs (id, name, mode, agent_ids, dataset_id, concurrency, judge_model, status, pass_rate, judge_agreement, completed_steps, total_steps)
VALUES
('run-eval-901', 'Regression Swarm Run v2.4', 'swarm', '["agt-swe-01", "agt-sec-02"]', 'ds-swebench-02', 8, 'gpt-4o', 'completed', 94.5, 96.2, 85, 85),
('run-eval-902', 'Comparative Model Arena A/B', 'comparative', '["agt-swe-01", "agt-data-03"]', 'ds-webarena-01', 4, 'gpt-4o', 'running', 89.2, 91.0, 42, 120),
('run-eval-903', 'Security Penetration Smoke', 'single', '["agt-sec-02"]', 'ds-swebench-02', 2, 'claude-3-7-sonnet', 'completed', 98.0, 99.1, 85, 85);

-- Trajectories Seed
INSERT INTO trajectories (id, run_id, agent_id, agent_name, status, turns, a2a_cards, judge_evaluation)
VALUES
('trj-101', 'run-eval-901', 'agt-swe-01', 'SWE-Agent Alpha', 'completed', 
'[
  {"turn": 1, "speaker": "user", "content": "Fix race condition in connection_pool.py on worker shutdown."},
  {"turn": 2, "speaker": "agent", "thought": "I need to inspect connection_pool.py and locate the shutdown semaphore.", "tool_calls": [{"tool": "read_file", "args": {"path": "src/connection_pool.py"}}], "content": "Inspecting connection pool shutdown logic."},
  {"turn": 3, "speaker": "tool", "content": "File src/connection_pool.py read successfully. Found lock acquisition without timeout."},
  {"turn": 4, "speaker": "agent", "thought": "Need to delegate security verification to VulnAudit Guardian via A2A Card.", "tool_calls": [{"tool": "edit_file", "args": {"path": "src/connection_pool.py"}}], "content": "Applied lock acquisition timeout and defensive cleanup."}
]',
'[
  {"id": "card-a2a-001", "sender": "SWE-Agent Alpha", "receiver": "VulnAudit Guardian", "intent": "SECURITY_AUDIT_REQUEST", "status": "accepted", "payload": {"file": "src/connection_pool.py", "diff": "+ lock.acquire(timeout=5.0)"}}
]',
'{"verdict": "pass", "score": 96.5, "judge": "gpt-4o", "reasoning": "Agent correctly pinpointed deadlock scenario and resolved lock acquisition timeout gracefully without introducing leaks."}'),

('trj-102', 'run-eval-901', 'agt-sec-02', 'VulnAudit Guardian', 'completed',
'[
  {"turn": 1, "speaker": "system", "content": "A2A Card received: Audit lock timeout change for security implications."},
  {"turn": 2, "speaker": "agent", "thought": "Checking for denial of service vector or race vulnerability in timeout exception handler.", "tool_calls": [{"tool": "security_scan", "args": {"target": "src/connection_pool.py"}}], "content": "Audit complete. No CWE vulnerabilities detected."}
]',
'[]',
'{"verdict": "pass", "score": 98.0, "judge": "gpt-4o", "reasoning": "Rigorous security check executed cleanly."}'),

('trj-103', 'run-eval-902', 'agt-data-03', 'DataPipelines Pro', 'running',
'[
  {"turn": 1, "speaker": "user", "content": "Optimize query execution plan for 10M rows join."},
  {"turn": 2, "speaker": "agent", "thought": "Analyzing EXPLAIN output and indexing strategy.", "tool_calls": [{"tool": "run_command", "args": {"command": "EXPLAIN ANALYZE SELECT ..."}}], "content": "Gathering query execution plan."}
]',
'[]',
'{"verdict": "pending", "score": 0.0, "judge": "gpt-4o", "reasoning": "Run in progress."}');

-- Annotations Seed
INSERT INTO annotations (id, trajectory_id, evaluator, verdict, taxonomy, notes)
VALUES
('ann-001', 'trj-101', 'lead-evaluator@enterprise.ai', 'pass', 'correct', 'Superb multi-turn reasoning and spotless A2A delegation card.'),
('ann-002', 'trj-103', 'qa-auditor@enterprise.ai', 'flag', 'logic_error', 'Potential retry loop detected in step 2. Needs manual inspection.');

-- Audit Logs Seed
INSERT INTO audit_logs (id, entity_type, entity_id, action, actor, payload)
VALUES
('aud-001', 'agent', 'agt-swe-01', 'CREATE', 'system', '{"model": "claude-3-7-sonnet"}'),
('aud-002', 'dataset', 'ds-swebench-02', 'CREATE', 'system', '{"domain": "Software Bug Resolution"}'),
('aud-003', 'run', 'run-eval-901', 'START', 'system', '{"mode": "swarm"}');

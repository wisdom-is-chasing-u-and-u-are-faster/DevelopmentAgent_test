"""
tests/test_e2e.py — End-to-end evaluation flow smoke test.
Simulates candidate registration, dataset import, run execution, trace inspection, and human annotation.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db(force_reseed=True)

def test_e2e_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_e2e_agent_registration():
    res = client.post(
        "/api/v1/agents",
        json={
            "name": "E2E Test Agent Alpha",
            "role": "Autonomous Coder",
            "model": "gpt-4o",
            "system_prompt": "Solve software issues autonomously.",
            "capabilities": ["code_editing", "testing"]
        }
    )
    assert res.status_code == 201
    assert "id" in res.json()

def test_e2e_dataset_and_run_lifecycle():
    # 1. Register agent
    res_agent = client.post(
        "/api/v1/agents",
        json={
            "name": "E2E Agent",
            "role": "Coder",
            "model": "gpt-4o",
            "system_prompt": "Solve issues.",
            "capabilities": ["testing"]
        }
    )
    agent_id = res_agent.json()["id"]

    # 2. Create dataset
    res_ds = client.post(
        "/api/v1/datasets",
        json={
            "name": "E2E Suite",
            "domain": "Unit Test Coverage",
            "test_count": 2,
            "test_cases": [{"id": "tc-1", "prompt": "Test"}]
        }
    )
    dataset_id = res_ds.json()["id"]

    # 3. Trigger run
    res_run = client.post(
        "/api/v1/runs",
        json={
            "name": "E2E Regression Run",
            "mode": "swarm",
            "agent_ids": [agent_id],
            "dataset_id": dataset_id,
            "concurrency": 2,
            "judge_model": "gpt-4o"
        }
    )
    run_id = res_run.json()["id"]

    # 4. Check run status
    res_detail = client.get(f"/api/v1/runs/{run_id}")
    assert res_detail.status_code == 200

    # 5. Check trajectory & submit annotation
    res_trjs = client.get(f"/api/v1/trajectories?run_id={run_id}")
    trj_id = res_trjs.json()["items"][0]["id"]

    res_ann = client.post(
        "/api/v1/annotations",
        json={
            "trajectory_id": trj_id,
            "verdict": "pass",
            "taxonomy": "correct",
            "evaluator": "evaluator@enterprise.ai",
            "notes": "Verified."
        }
    )
    assert res_ann.status_code == 201

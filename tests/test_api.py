"""
tests/test_api.py — API route integration and RFC 7807 problem detail envelope tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db(force_reseed=True)

def test_health_probe():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data

def test_list_agents():
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 3

def test_create_agent_success():
    payload = {
        "name": "Integration Tester Agent",
        "role": "QA Automation Engineer",
        "model": "claude-3-7-sonnet",
        "system_prompt": "Perform automated integration tests.",
        "capabilities": ["testing", "assertion"]
    }
    response = client.post("/api/v1/agents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]

def test_create_agent_invalid_rfc7807():
    payload = {"name": "", "role": "", "model": ""}
    response = client.post("/api/v1/agents", json=payload)
    assert response.status_code == 400
    err = response.json()
    assert err["type"] == "about:blank"
    assert err["status"] == 400
    assert "detail" in err

def test_list_datasets():
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 2

def test_create_dataset():
    payload = {
        "name": "Math Reasoning Golden Benchmark",
        "domain": "Symbolic Logic & Arithmetic",
        "test_count": 2,
        "test_cases": [{"id": "m-1", "prompt": "2 + 2 = ?"}]
    }
    response = client.post("/api/v1/datasets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]

def test_list_runs():
    response = client.get("/api/v1/runs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3

def test_get_run_detail_success():
    response = client.get("/api/v1/runs/run-eval-901")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "run-eval-901"
    assert "pass_rate" in data

def test_get_run_not_found_rfc7807():
    response = client.get("/api/v1/runs/non-existent-999")
    assert response.status_code == 404
    err = response.json()
    assert err["status"] == 404
    assert err["type"] == "about:blank"
    assert "not found" in err["detail"].lower()

def test_list_trajectories():
    response = client.get("/api/v1/trajectories")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2

def test_get_trajectory_detail():
    response = client.get("/api/v1/trajectories/trj-101")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "trj-101"
    assert len(data["turns"]) >= 1

def test_get_trajectory_not_found_rfc7807():
    response = client.get("/api/v1/trajectories/trj-missing")
    assert response.status_code == 404
    err = response.json()
    assert err["status"] == 404

def test_annotations_queue_and_submit():
    # List annotations
    res_list = client.get("/api/v1/annotations")
    assert res_list.status_code == 200

    # Submit review
    payload = {
        "trajectory_id": "trj-101",
        "verdict": "pass",
        "taxonomy": "correct",
        "evaluator": "senior-auditor@enterprise.ai",
        "notes": "Reviewed and approved."
    }
    res_create = client.post("/api/v1/annotations", json=payload)
    assert res_create.status_code == 201
    assert res_create.json()["verdict"] == "pass"

def test_collaboration_telemetry():
    response = client.get("/api/v1/telemetry/collaboration")
    assert response.status_code == 200
    data = response.json()
    assert "total_cards" in data
    assert "precision_rate" in data
    assert "avg_latency_ms" in data
    assert "consensus_rate" in data

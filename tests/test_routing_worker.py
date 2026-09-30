import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_agent_skills_dispatch_algorithm():
    res = client.post("/api/v1/tickets", json={
        "title": "PostgreSQL Query Slowdown",
        "description": "Index scan degradation on audit ledger.",
        "priority": "P2",
        "department": "Database",
        "category": "postgresql",
        "requester_name": "Dev",
        "requester_email": "dev@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    res_disp = client.post(f"/api/v1/tickets/{ticket_id}/dispatch", json={})
    assert res_disp.status_code == 200
    data = res_disp.json()
    assert data["assigned_agent_id"] == "agent-002"
    assert data["match_score"] >= 0.8


def test_agent_capacity_and_listing():
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) >= 5
    assert all("skills" in a for a in agents)

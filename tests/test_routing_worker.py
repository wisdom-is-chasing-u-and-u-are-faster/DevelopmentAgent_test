"""
Test Skill-Based Ticket Routing & Agent Load Distribution (ARCH-1521, ARCH-1537, ARCH-1536)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_agent_skills_matching_route():
    """Verify security incident routes to qualified Infosec agent (Elena Rostova)."""
    # Create security ticket
    res = client.post("/api/v1/tickets", json={
        "title": "Phishing Attachment Detected",
        "description": "Zero day macro payload.",
        "category": "Suspected Phishing / Malware Incident",
        "department_id": "dept-sec-ops",
        "requester_email": "soc@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    # Trigger route
    route_res = client.post(f"/api/v1/tickets/{ticket_id}/route")
    assert route_res.status_code == 200
    data = route_res.json()
    assert data["assigned_agent_id"] == "agent-002"  # Elena Rostova
    assert data["agent_name"] == "Elena Rostova"
    assert data["routing_score"] > 0


def test_agents_list_endpoint():
    """Verify GET /api/v1/agents returns active capacity and skills."""
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    data = res.json()
    assert "agents" in data
    assert len(data["agents"]) >= 5
    assert len(data["agents"][0]["skills"]) > 0

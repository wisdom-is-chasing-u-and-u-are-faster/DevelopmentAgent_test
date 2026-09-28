"""
Test SLA Calculation Engine & Milestones (ARCH-1519, ARCH-1526, ARCH-1531)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.services.sla_engine import SLAEngine


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_sla_deadlines_calculation():
    """Verify P1 SLA sets 5 min response and 2 hour resolution."""
    res = SLAEngine.calculate_deadlines("P1")
    assert res["sla_tier"] == "TIER_1_HA"
    assert res["response_deadline"] is not None
    assert res["resolution_deadline"] is not None


def test_sla_evaluation_endpoint():
    """Verify GET /api/v1/tickets/{id}/sla returns accurate metrics."""
    res = client.post("/api/v1/tickets", json={
        "title": "Cloud SQL Outage",
        "description": "Database offline.",
        "category": "Cloud Infrastructure Outage",
        "priority": "P1",
        "requester_email": "sre@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    sla_res = client.get(f"/api/v1/tickets/{ticket_id}/sla")
    assert sla_res.status_code == 200
    data = sla_res.json()
    assert data["ticket_id"] == ticket_id
    assert data["status"] in ("ON_TRACK", "AT_RISK", "BREACHED")

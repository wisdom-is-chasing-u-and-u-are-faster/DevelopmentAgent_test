"""
Test End-to-End Cross-Tier Integration & Static Asset Mounting (ARCH-1517)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_health_check_endpoint():
    """Verify container readiness /health endpoint returns 200 OK."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_static_frontend_mounting():
    """Verify root / serves the frontend portal HTML index."""
    res = client.get("/")
    assert res.status_code == 200
    assert "Enterprise Ticketing Management Platform" in res.text
    assert "tab-dashboard" in res.text
    assert "tab-settings" in res.text


def test_static_js_and_css_serving():
    """Verify static JS client module and CSS stylesheet are mounted and accessible."""
    css_res = client.get("/css/style.css")
    assert css_res.status_code == 200

    api_res = client.get("/js/api.js")
    assert api_res.status_code == 200
    assert "export const api" in api_res.text
    assert "getActiveSettings" in api_res.text


def test_full_lifecycle_flow():
    """End-to-end integration: Submit -> Auto-Route -> State Transition -> SLA Check -> Audit Verify."""
    # 1. Submit ticket
    submit_res = client.post("/api/v1/tickets", json={
        "title": "Production Service E2E Verification Incident",
        "description": "Verifying full stack cross-tier integration flow.",
        "category": "Cloud Infrastructure Outage",
        "priority": "P1",
        "department_id": "dept-it-ops",
        "requester_email": "qa-automation@enterprise.internal"
    })
    assert submit_res.status_code == 201
    ticket_id = submit_res.json()["id"]

    # 2. Auto-route
    route_res = client.post(f"/api/v1/tickets/{ticket_id}/route")
    assert route_res.status_code == 200
    assert route_res.json()["assigned_agent_id"] is not None

    # 3. Transition to IN_PROGRESS
    patch_res = client.patch(f"/api/v1/tickets/{ticket_id}", json={
        "status": "IN_PROGRESS",
        "expected_version": 1
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["version"] == 2

    # 4. Check SLA
    sla_res = client.get(f"/api/v1/tickets/{ticket_id}/sla")
    assert sla_res.status_code == 200
    assert sla_res.json()["status"] in ("ON_TRACK", "AT_RISK")

    # 5. Verify cryptographic audit trail
    audit_res = client.get(f"/api/v1/tickets/{ticket_id}/audit-trail")
    assert audit_res.status_code == 200
    assert audit_res.json()["chain_valid"] is True
    assert len(audit_res.json()["entries"]) >= 2

    # 6. Verify settings hydration
    settings_res = client.get("/api/v1/settings/active")
    assert settings_res.status_code == 200
    assert settings_res.json()["theme"] is not None
    assert settings_res.json()["worklist_layout"] is not None

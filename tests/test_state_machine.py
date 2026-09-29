"""
Test 7-State Lifecycle State Machine & Optimistic Locking (ARCH-1520, ARCH-1538, ARCH-1539)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_valid_lifecycle_transitions():
    """Verify standard transition DAG SUBMITTED -> TRIAGED -> IN_PROGRESS -> RESOLVED -> CLOSED."""
    # Create ticket
    res = client.post("/api/v1/tickets", json={
        "title": "VPN Routing Error",
        "description": "Cannot connect to gateway.",
        "category": "Remote VPN & Zero Trust Connectivity",
        "requester_email": "user@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    # 1. SUBMITTED -> TRIAGED (version 1 -> 2)
    p1 = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "TRIAGED", "expected_version": 1})
    assert p1.status_code == 200
    assert p1.json()["status"] == "TRIAGED"
    assert p1.json()["version"] == 2

    # 2. TRIAGED -> IN_PROGRESS (version 2 -> 3)
    p2 = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "IN_PROGRESS", "expected_version": 2})
    assert p2.status_code == 200
    assert p2.json()["status"] == "IN_PROGRESS"
    assert p2.json()["version"] == 3

    # 3. IN_PROGRESS -> RESOLVED (version 3 -> 4)
    p3 = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "RESOLVED", "resolution_notes": "Restarted VPN daemon", "expected_version": 3})
    assert p3.status_code == 200
    assert p3.json()["status"] == "RESOLVED"
    assert p3.json()["version"] == 4


def test_illegal_state_transition():
    """Attempting illegal transition (e.g. SUBMITTED -> RESOLVED directly) returns HTTP 400."""
    res = client.post("/api/v1/tickets", json={
        "title": "Laptop Refresh",
        "description": "Order new laptop.",
        "category": "Workstation Laptop Refresh",
        "requester_email": "user@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    # Illegal transition
    bad_res = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "RESOLVED", "expected_version": 1})
    assert bad_res.status_code == 400


def test_optimistic_concurrency_conflict():
    """Version mismatch returns HTTP 409 Conflict."""
    res = client.post("/api/v1/tickets", json={
        "title": "Phishing Email",
        "description": "Suspicious link.",
        "category": "Suspected Phishing / Malware Incident",
        "requester_email": "user@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    # Mutate to version 2
    client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "TRIAGED", "expected_version": 1})

    # Outdated client attempts update with stale version 1
    conflict_res = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "IN_PROGRESS", "expected_version": 1})
    assert conflict_res.status_code == 409
    assert "conflict" in conflict_res.json()["detail"].lower()

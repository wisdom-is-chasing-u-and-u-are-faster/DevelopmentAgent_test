import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_7_state_lifecycle_transitions():
    res = client.post("/api/v1/tickets", json={
        "title": "Database Read Pool Contention",
        "description": "Connection pool exhausted on replica 2.",
        "priority": "P2",
        "department": "Database",
        "category": "Performance",
        "requester_name": "DB Admin",
        "requester_email": "dbadmin@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    res_t1 = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "TRIAGED",
        "expected_version": 1,
        "comment": "Triage verified and confirmed."
    })
    assert res_t1.status_code == 200
    assert res_t1.json()["status"] == "TRIAGED"
    assert res_t1.json()["version"] == 2

    res_t2 = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "ASSIGNED",
        "expected_version": 2
    })
    assert res_t2.status_code == 200
    assert res_t2.json()["status"] == "ASSIGNED"
    assert res_t2.json()["version"] == 3


def test_optimistic_concurrency_conflict():
    res = client.post("/api/v1/tickets", json={
        "title": "Cache Eviction Policy Glitch",
        "description": "Redis LRU eviction rate exceeded threshold.",
        "priority": "P3",
        "department": "Infrastructure",
        "category": "Performance",
        "requester_name": "SRE Team",
        "requester_email": "sre@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    res_conflict = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "TRIAGED",
        "expected_version": 999
    })
    assert res_conflict.status_code == 409
    assert "Conflict" in res_conflict.json()["detail"]


def test_invalid_lifecycle_transition():
    res = client.post("/api/v1/tickets", json={
        "title": "Unauthorized S3 Bucket Access Attempt",
        "description": "Anomalous read requests detected.",
        "priority": "P2",
        "department": "Security",
        "category": "Access Request",
        "requester_name": "SecOps",
        "requester_email": "secops@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    res_invalid = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={
        "status": "CLOSED",
        "expected_version": 1
    })
    assert res_invalid.status_code == 400
    assert "Invalid transition" in res_invalid.json()["detail"]

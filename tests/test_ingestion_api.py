"""
Test Ingestion API & Idempotency Engine (ARCH-1518, ARCH-1528, ARCH-1529)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_positive_ticket_submission():
    """Scenario 1: Positive submission returns HTTP 201 with ticket metadata."""
    payload = {
        "title": "Critical Outage in Cloud Run Ingestion Microservice",
        "description": "500 Internal Server Errors surging across all incoming API requests.",
        "category": "Cloud Infrastructure Outage",
        "priority": "P1",
        "department_id": "dept-it-ops",
        "requester_email": "ops-lead@enterprise.internal",
        "tags": ["cloud-run", "outage"]
    }
    response = client.post("/api/v1/tickets", json=payload, headers={"X-Idempotency-Key": "test-idem-001"})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert data["priority"] == "P1"
    assert data["version"] == 1
    assert "ticket_number" in data
    assert data["sla_deadline_response"] is not None


def test_idempotent_duplicate_submission():
    """Scenario 2: Duplicate submission with same key returns cached HTTP 200 without creating new DB record."""
    payload = {
        "title": "Payment API Failure",
        "description": "Stripe webhook timeouts.",
        "category": "Payment Gateway 5xx Failure",
        "priority": "P2",
        "requester_email": "fin-ops@enterprise.internal"
    }
    idem_key = "test-idem-unique-key-99"

    # First call -> 201 Created
    res1 = client.post("/api/v1/tickets", json=payload, headers={"X-Idempotency-Key": idem_key})
    assert res1.status_code == 201
    ticket_id = res1.json()["id"]

    # Second call -> 200 OK with identical payload
    res2 = client.post("/api/v1/tickets", json=payload, headers={"X-Idempotency-Key": idem_key})
    assert res2.status_code == 200
    assert res2.json()["id"] == ticket_id


def test_validation_error_missing_fields():
    """Scenario 3: Request missing required fields returns HTTP 422 / 400 Bad Request."""
    payload = {
        "priority": "P1"
        # missing title, description, category, requester_email
    }
    res = client.post("/api/v1/tickets", json=payload)
    assert res.status_code in (400, 422)

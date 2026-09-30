import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_create_ticket_and_idempotency():
    payload = {
        "title": "Core Payment Ingestion Microservice 500 Outage",
        "description": "Payment webhook processor failing on payload schema deserialization.",
        "priority": "P1",
        "department": "Applications",
        "category": "Outage",
        "requester_name": "DevOps OnCall",
        "requester_email": "oncall@enterprise.internal",
        "idempotency_key": "unique-idempotency-token-12345"
    }

    res1 = client.post("/api/v1/tickets", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["status"] == "NEW"
    assert "INC-" in data1["ticket_number"]
    assert data1["priority"] == "P1"

    res2 = client.post("/api/v1/tickets", json=payload)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["id"] == data1["id"]
    assert data2.get("idempotent_replay") is True


def test_create_ticket_validation_error():
    invalid_payload = {
        "title": "AB",
        "priority": "INVALID_PRIORITY"
    }
    res = client.post("/api/v1/tickets", json=invalid_payload)
    assert res.status_code == 422

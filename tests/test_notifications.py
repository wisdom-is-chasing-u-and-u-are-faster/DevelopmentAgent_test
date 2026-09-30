import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.services.notification_service import send_sla_notification

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_omnichannel_notification_dispatcher():
    ticket = {
        "id": "tkt-1002",
        "ticket_number": "INC-2026-0835",
        "priority": "P2",
        "title": "API Gateway Rate-Limiting Policy Spikes",
        "assigned_agent_name": "Elena Rostova"
    }

    logs = send_sla_notification(ticket, 75)
    assert len(logs) == 3
    channels = {item["channel"] for item in logs}
    assert channels == {"SLACK", "TEAMS", "EMAIL"}

    res = client.get("/api/v1/notifications")
    assert res.status_code == 200
    assert len(res.json()) >= 3

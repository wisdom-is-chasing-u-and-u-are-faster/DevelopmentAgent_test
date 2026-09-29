"""
Test Omnichannel Notification Dispatcher (ARCH-1530)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_notification_dispatch_multichannel():
    """Verify dispatching notification over Slack, Teams, and Email."""
    payload = {
        "ticket_id": "tick-1001",
        "channels": ["slack", "teams", "email"],
        "event_type": "SLA_BREACH_WARNING",
        "recipient": "sre-lead@enterprise.internal",
        "message": "P1 ticket INC-8091 has reached 75% resolution SLA threshold."
    }
    res = client.post("/api/v1/notifications/dispatch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DELIVERED"
    assert "slack" in data["channels_delivered"]
    assert "teams" in data["channels_delivered"]
    assert "email" in data["channels_delivered"]

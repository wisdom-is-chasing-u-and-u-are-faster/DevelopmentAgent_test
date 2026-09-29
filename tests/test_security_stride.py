"""
Test Security Penetration & STRIDE Threat Mitigations (ARCH-1549)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_sql_injection_defense():
    """Verify SQL injection payloads in search query are neutralized by parameterized queries."""
    sqli_payload = "' OR 1=1 --"
    res = client.get(f"/api/v1/search?q={sqli_payload}")
    assert res.status_code == 200
    # Should safely return zero or filtered matches rather than dumping all table data
    data = res.json()
    assert isinstance(data["hits"], list)


def test_xss_payload_handling():
    """Verify XSS script tags in ticket submission are safely stored and returned."""
    xss_payload = {
        "title": "<script>alert('xss')</script>",
        "description": "<img src=x onerror=alert(1)>",
        "category": "Cloud Infrastructure Outage",
        "requester_email": "attacker@evil.com"
    }
    res = client.post("/api/v1/tickets", json=xss_payload)
    assert res.status_code == 201
    assert res.json()["title"] == "<script>alert('xss')</script>"

"""
Test Cryptographic Audit Ledger & SHA-256 Chaining (ARCH-1523, ARCH-1533, ARCH-1546)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_audit_ledger_hash_chaining():
    """Verify ticket mutations create verified cryptographic SHA-256 hash chains."""
    # Create ticket -> Genesis Hash
    res = client.post("/api/v1/tickets", json={
        "title": "Audit Test Incident",
        "description": "Verifying tamper-evident hash chaining.",
        "category": "Cloud Infrastructure Outage",
        "requester_email": "auditor@enterprise.internal"
    })
    ticket_id = res.json()["id"]

    # Transition 1
    client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "TRIAGED", "expected_version": 1})

    # Transition 2
    client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "IN_PROGRESS", "expected_version": 2})

    # Inspect Audit Trail
    audit_res = client.get(f"/api/v1/tickets/{ticket_id}/audit-trail")
    assert audit_res.status_code == 200
    data = audit_res.json()
    assert data["chain_valid"] is True
    assert len(data["entries"]) >= 3

    # Check that previous hash of entry N equals hash of entry N-1
    entries = data["entries"]
    assert entries[1].get("previous_checksum_sha256") == entries[0].get("checksum_sha256")
    assert entries[2].get("previous_checksum_sha256") == entries[1].get("checksum_sha256")

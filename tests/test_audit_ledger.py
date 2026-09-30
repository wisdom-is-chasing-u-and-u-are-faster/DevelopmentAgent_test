import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.services.audit_engine import verify_audit_chain_integrity, append_audit_event

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_cryptographic_audit_ledger_chaining():
    append_audit_event(
        entity_type="TEST",
        entity_id="test-123",
        action="TEST_ACTION",
        actor="TestRunner",
        from_status=None,
        to_status="VERIFIED",
        payload_data={"sample": "data"}
    )

    assert verify_audit_chain_integrity() is True

    res = client.get("/api/v1/audit/verify")
    assert res.status_code == 200
    assert res.json()["status"] == "VALID"

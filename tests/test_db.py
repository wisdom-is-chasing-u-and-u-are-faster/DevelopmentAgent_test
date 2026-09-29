"""
tests/test_db.py — Database Schema & Audit Ledger Tests
"""
import os
import pytest
from app.db.init_db import init_database, get_db_connection, execute_query
from app.services.audit_service import AuditService


def test_init_database():
    """Verify schema and seed tables initialize successfully."""
    success = init_database()
    assert success is True

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r["name"] for r in cursor.fetchall()]
    conn.close()

    assert "onboarding_sessions" in tables
    assert "pii_vault" in tables
    assert "kyc_verifications" in tables
    assert "accounts" in tables
    assert "virtual_cards" in tables
    assert "saga_executions" in tables
    assert "audit_ledger" in tables


def test_audit_ledger_hash_chaining():
    """Verify cryptographic SHA-256 hash chaining in audit ledger."""
    init_database()

    hash1 = AuditService.record_event(
        action="TEST_ACTION_1",
        entity_id="entity_001",
        actor="test_runner",
        payload={"step": 1}
    )
    assert len(hash1) == 64

    hash2 = AuditService.record_event(
        action="TEST_ACTION_2",
        entity_id="entity_002",
        actor="test_runner",
        payload={"step": 2}
    )
    assert len(hash2) == 64
    assert hash1 != hash2

    ledger = AuditService.get_ledger(limit=10)
    assert len(ledger) >= 2
    assert ledger[0]["entry_hash"] == hash2
    assert ledger[0]["prev_hash"] == hash1

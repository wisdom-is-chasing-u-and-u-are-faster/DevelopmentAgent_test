"""
Test Database Schema & Baseline Seeds (ARCH-1524, ARCH-1525, ARCH-1535, ARCH-1548)
"""

import pytest
from app.db.init_db import init_database, get_db_connection


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


def test_schema_tables_exist():
    """Verify all 8 core enterprise schema tables exist."""
    conn = get_db_connection()
    tables = [
        "departments", "categories", "agents", "agent_skills",
        "tickets", "sla_tracking", "audit_ledger", "idempotency_records"
    ]
    for table in tables:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        assert row is not None, f"Table {table} must exist in database schema"
    conn.close()


def test_seed_departments_and_categories():
    """Verify baseline departments and categories are pre-seeded."""
    conn = get_db_connection()
    depts = conn.execute("SELECT COUNT(*) as count FROM departments").fetchone()
    assert depts["count"] >= 5

    cats = conn.execute("SELECT COUNT(*) as count FROM categories").fetchone()
    assert cats["count"] >= 8
    conn.close()


def test_agent_skills_taxonomy():
    """Verify agent skills and proficiency matrix are populated."""
    conn = get_db_connection()
    agents = conn.execute("SELECT COUNT(*) as count FROM agents").fetchone()
    assert agents["count"] >= 5

    skills = conn.execute("SELECT COUNT(*) as count FROM agent_skills").fetchone()
    assert skills["count"] >= 10
    conn.close()

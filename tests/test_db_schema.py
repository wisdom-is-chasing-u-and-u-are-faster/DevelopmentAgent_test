"""
Test Database Schema & Baseline Seeds (ARCH-1524, ARCH-1525, ARCH-1535, ARCH-1548, ARCH-1517)
"""

import pytest
from app.db.init_db import init_database, get_db_connection


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


def test_schema_tables_exist():
    """Verify all 9 enterprise schema tables exist including ui_presets."""
    conn = get_db_connection()
    tables = [
        "departments", "categories", "agents", "agent_skills",
        "tickets", "sla_tracking", "audit_ledger", "idempotency_records",
        "ui_presets"
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


def test_ui_presets_seeded():
    """Verify theme color and worklist layout presets are pre-seeded."""
    conn = get_db_connection()
    presets = conn.execute("SELECT COUNT(*) as count FROM ui_presets").fetchone()
    assert presets["count"] >= 4

    global_theme = conn.execute(
        "SELECT * FROM ui_presets WHERE preset_type = 'THEME_COLOR' AND is_global_default = 1"
    ).fetchone()
    assert global_theme is not None

    global_layout = conn.execute(
        "SELECT * FROM ui_presets WHERE preset_type = 'WORKLIST_LAYOUT' AND is_global_default = 1"
    ).fetchone()
    assert global_layout is not None
    conn.close()

"""
Database schema DDL and DML seed verification tests.
Ensures ANSI SQL syntax and database table initialization.
"""

import sqlite3
from app.db.init_db import init_database, get_connection

def test_database_initialization(tmp_path, monkeypatch):
    """Verifies that schema.sql and seed.sql execute with zero syntax errors."""
    test_db = str(tmp_path / "test_verify.db")
    monkeypatch.setenv("SQLITE_DB_PATH", test_db)

    assert init_database() is True

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Check key tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = ["challenges", "leaderboard", "badges", "users", "privacy_zones", "social_posts"]
    for t in expected_tables:
        assert t in tables, f"Expected table {t} to be created"

    # Check seed data populated
    cursor.execute("SELECT COUNT(*) FROM challenges;")
    challenge_count = cursor.fetchone()[0]
    assert challenge_count >= 1

    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    assert user_count >= 1

    conn.close()

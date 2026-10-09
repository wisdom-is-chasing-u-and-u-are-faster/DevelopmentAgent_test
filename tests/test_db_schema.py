from app.db.init_db import get_connection, init_database


def test_database_initialization_and_schema():
    init_database()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row["name"] for row in cur.fetchall()}

        expected_tables = {"tickets", "agents", "audit_ledger", "notifications", "user_settings", "system_presets"}
        for t in expected_tables:
            assert t in tables, f"Expected table '{t}' to be created."

        cur.execute("SELECT COUNT(*) as count FROM agents")
        assert cur.fetchone()["count"] >= 5

        cur.execute("SELECT COUNT(*) as count FROM tickets")
        assert cur.fetchone()["count"] >= 5
    finally:
        conn.close()

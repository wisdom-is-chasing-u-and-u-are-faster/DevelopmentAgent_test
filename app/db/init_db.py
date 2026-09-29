"""
app/db/init_db.py — Database Initialization & Connection Helper
"""
import os
import sqlite3
import hashlib
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("SQLITE_DB_PATH", "banking_onboarding.db")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./banking_onboarding.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection configured for dictionary-like row access."""
    # Handle sqlite:/// url format if provided
    path = DB_PATH
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes schema and baseline seeds into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Locate schema and seed files
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))))
    schema_path = os.path.join(base_dir, "db", "schema.sql")
    seed_path = os.path.join(base_dir, "db", "seed.sql")

    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

    if os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()
    return True


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Executes a SELECT query and returns rows as dictionaries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


def execute_update(query: str, params: tuple = ()) -> int:
    """Executes an INSERT, UPDATE, or DELETE query and returns rows affected."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()
    return rowcount

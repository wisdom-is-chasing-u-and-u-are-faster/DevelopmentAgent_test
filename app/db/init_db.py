"""
init_db.py — Database Initialization & Connection Engine for ETMS
Supports SQLite local development and Cloud SQL PostgreSQL deployments.
"""

import os
import sqlite3
from pathlib import Path
from typing import Generator

DB_FILE = os.getenv("ETMS_DB_FILE", "etms.db")
SCHEMA_FILE = Path(__file__).resolve().parent.parent.parent / "db" / "schema.sql"
SEED_FILE = Path(__file__).resolve().parent.parent.parent / "db" / "seed.sql"


def get_db_connection():
    """Returns a SQLite connection configured with Row factory."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database(reset: bool = False):
    """Initializes the database schema and seeds initial master data."""
    if reset and os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    if SCHEMA_FILE.exists():
        schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
        cursor.executescript(schema_sql)

    if SEED_FILE.exists():
        seed_sql = SEED_FILE.read_text(encoding="utf-8")
        cursor.executescript(seed_sql)

    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    init_database()
    print("ETMS Database initialized successfully.")

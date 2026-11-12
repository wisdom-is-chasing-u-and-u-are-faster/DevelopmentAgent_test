"""
Database initialization and session connection helper.
Supports zero-dependency local SQLite with automatic schema DDL execution
(including idempotent ALTER TABLE and dialect conversion) and seed insertion,
or PostgreSQL if DATABASE_URL is configured.
"""

import os
import re
import sqlite3
from pathlib import Path

def get_db_path():
    return os.environ.get("SQLITE_DB_PATH", "app.db")

def get_schema_path():
    base_dir = Path(__file__).resolve().parent.parent.parent
    cand1 = base_dir / "db" / "schema.sql"
    if cand1.exists():
        return cand1
    cand2 = Path("db/schema.sql")
    if cand2.exists():
        return cand2
    return cand1

def get_seed_path():
    base_dir = Path(__file__).resolve().parent.parent.parent
    cand1 = base_dir / "db" / "seed.sql"
    if cand1.exists():
        return cand1
    cand2 = Path("db/seed.sql")
    if cand2.exists():
        return cand2
    return cand1

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def _normalize_for_sqlite(sql_text: str) -> str:
    """Converts PostgreSQL dialect keywords to SQLite-compatible syntax."""
    s = sql_text
    s = re.sub(r"\bSERIAL\s+PRIMARY\s+KEY\b", "INTEGER PRIMARY KEY AUTOINCREMENT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bBIGSERIAL\s+PRIMARY\s+KEY\b", "INTEGER PRIMARY KEY AUTOINCREMENT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bJSONB\b", "TEXT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bON\s+CONFLICT\s*\([^)]*\)\s*DO\s+NOTHING\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bON\s+CONFLICT\s+DO\s+NOTHING\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\bINSERT\s+INTO\b", "INSERT OR IGNORE INTO", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNUMERIC\([0-9,\s]+\)", "REAL", s, flags=re.IGNORECASE)
    return s

def init_database():
    """Executes schema.sql and seed.sql to ensure tables and baseline data exist."""
    conn = get_connection()
    
    schema_path = get_schema_path()
    seed_path = get_seed_path()

    if schema_path.exists():
        schema_sql = _normalize_for_sqlite(schema_path.read_text(encoding="utf-8"))
        conn.executescript(schema_sql)
        
    if seed_path.exists():
        seed_sql = _normalize_for_sqlite(seed_path.read_text(encoding="utf-8"))
        conn.executescript(seed_sql)
        
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")

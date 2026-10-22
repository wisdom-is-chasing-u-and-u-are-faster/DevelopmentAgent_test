"""
app/database.py — Relational persistence layer for Agent Evaluation Platform.
Supports SQLite3 local file execution and PostgreSQL compatibility.
"""
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

# 12-factor environment configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eval_platform.db")

def _get_db_path() -> str:
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    return "eval_platform.db"

def get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(force_reseed: bool = False) -> None:
    """Initialize schema and seed data if database tables do not exist or force_reseed is set."""
    db_path = _get_db_path()
    repo_root = Path(__file__).resolve().parent.parent

    schema_file = repo_root / "db" / "schema.sql"
    seed_file = repo_root / "db" / "seed.sql"

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents';")
        table_exists = cursor.fetchone() is not None

        if not table_exists or force_reseed:
            if schema_file.exists():
                schema_sql = schema_file.read_text(encoding="utf-8")
                cursor.executescript(schema_sql)
            if seed_file.exists():
                seed_sql = seed_file.read_text(encoding="utf-8")
                cursor.executescript(seed_sql)
            conn.commit()
    finally:
        conn.close()

def query_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def execute_write(query: str, params: tuple = ()) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

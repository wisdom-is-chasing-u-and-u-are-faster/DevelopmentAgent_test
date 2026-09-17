import os
import sqlite3
from typing import Generator

DB_PATH = "cosmetics.db"


def get_db_path() -> str:
    return os.environ.get("COSMETICS_DB_PATH", DB_PATH)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

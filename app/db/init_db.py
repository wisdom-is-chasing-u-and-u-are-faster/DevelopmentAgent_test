import os
import sqlite3
from pathlib import Path


def get_db_path() -> str:
    db_url = os.getenv("DATABASE_URL", "sqlite:///./etms.db")
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return "./etms.db"


def get_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    repo_root = Path(__file__).resolve().parent.parent.parent
    schema_file = repo_root / "db" / "schema.sql"
    seed_file = repo_root / "db" / "seed.sql"

    conn = get_connection()
    try:
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        if seed_file.exists():
            with open(seed_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")

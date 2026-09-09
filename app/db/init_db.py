import os
import sqlite3
from pathlib import Path
from typing import Optional
from app.db.session import DB_PATH


def init_database(db_path: Optional[str] = None) -> None:
    if db_path is None:
        db_path = os.environ.get("COSMETICS_DB_PATH", DB_PATH)

    schema_path = Path("db/schema.sql")
    seed_path = Path("db/seed.sql")

    if not schema_path.exists():
        schema_path = Path(__file__).resolve().parent.parent.parent / "db" / "schema.sql"
    if not seed_path.exists():
        seed_path = Path(__file__).resolve().parent.parent.parent / "db" / "seed.sql"

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    if seed_path.exists():
        with open(seed_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()

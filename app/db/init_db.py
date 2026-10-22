"""
app/db/init_db.py — Command-line and programmatic DB initialization script.
"""
import sys
from app.database import init_db

if __name__ == "__main__":
    force = "--force" in sys.argv or "--reseed" in sys.argv
    print(f"Initializing database (force_reseed={force})...")
    init_db(force_reseed=force)
    print("Database initialization completed successfully.")

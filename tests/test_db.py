"""
tests/test_db.py — Database schema, integrity, and seed verification tests.
"""
import pytest
from app.database import get_connection, init_db, query_all, query_one

@pytest.fixture(autouse=True)
def setup_database():
    init_db(force_reseed=True)

def test_database_tables_exist():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected_tables = {"agents", "datasets", "runs", "trajectories", "annotations", "audit_logs"}
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

def test_agents_seed_records():
    agents = query_all("SELECT * FROM agents;")
    assert len(agents) >= 3
    names = [a["name"] for a in agents]
    assert "SWE-Agent Alpha" in names
    assert "VulnAudit Guardian" in names

def test_datasets_seed_records():
    datasets = query_all("SELECT * FROM datasets;")
    assert len(datasets) >= 2
    domains = [d["domain"] for d in datasets]
    assert "Software Bug Resolution" in domains

def test_runs_and_trajectories_integrity():
    runs = query_all("SELECT * FROM runs;")
    assert len(runs) >= 3

    run_id = runs[0]["id"]
    trajectories = query_all("SELECT * FROM trajectories WHERE run_id = ?;", (run_id,))
    assert len(trajectories) >= 1

def test_foreign_key_constraints():
    conn = get_connection()
    cursor = conn.cursor()
    with pytest.raises(Exception):
        # Inserting trajectory with non-existent run_id should violate foreign key
        cursor.execute(
            "INSERT INTO trajectories (id, run_id, agent_name) VALUES ('trj-fail', 'non-existent-run', 'Worker');"
        )
    conn.close()

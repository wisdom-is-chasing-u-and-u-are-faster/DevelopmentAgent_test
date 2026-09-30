import pytest
from app.db.init_db import init_database, get_connection
from app.services.sla_engine import evaluate_ticket_sla


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_sla_threshold_calculation_and_alerts():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE tickets SET sla_elapsed_hours = 1.8 WHERE id = 'tkt-1001'")
        conn.commit()
    finally:
        conn.close()

    eval_res = evaluate_ticket_sla("tkt-1001")
    assert eval_res["sla_status"] == "CRITICAL_WARNING"
    assert eval_res["percent_elapsed"] == 90.0

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM notifications WHERE ticket_id = 'tkt-1001'")
        assert cur.fetchone()["count"] > 0
    finally:
        conn.close()

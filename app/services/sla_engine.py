from typing import Dict, Any
from app.db.init_db import get_connection
from app.services.notification_service import send_sla_notification

SLA_THRESHOLDS = [50, 75, 100]

PRIORITY_SLA_HOURS = {
    "P1": 2.0,
    "P2": 4.0,
    "P3": 8.0,
    "P4": 24.0
}


def evaluate_ticket_sla(ticket_id: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        if not row:
            return {}

        ticket = dict(row)
        target_hours = ticket["sla_target_hours"]
        elapsed_hours = ticket["sla_elapsed_hours"]
        percent_elapsed = (elapsed_hours / target_hours) * 100.0 if target_hours > 0 else 0.0

        new_sla_status = "WITHIN_SLA"
        if percent_elapsed >= 100.0:
            new_sla_status = "BREACHED"
        elif percent_elapsed >= 75.0:
            new_sla_status = "CRITICAL_WARNING"
        elif percent_elapsed >= 50.0:
            new_sla_status = "APPROACHING_THRESHOLD"

        for threshold in SLA_THRESHOLDS:
            if percent_elapsed >= threshold:
                cur.execute(
                    "SELECT COUNT(*) as count FROM notifications WHERE ticket_id = ? AND threshold_percent = ?",
                    (ticket_id, threshold)
                )
                if cur.fetchone()["count"] == 0:
                    send_sla_notification(ticket, threshold)

        cur.execute(
            "UPDATE tickets SET sla_status = ?, updated_at = datetime('now') WHERE id = ?",
            (new_sla_status, ticket_id)
        )
        conn.commit()

        return {
            "ticket_id": ticket_id,
            "target_hours": target_hours,
            "elapsed_hours": elapsed_hours,
            "percent_elapsed": round(percent_elapsed, 1),
            "sla_status": new_sla_status
        }
    finally:
        conn.close()

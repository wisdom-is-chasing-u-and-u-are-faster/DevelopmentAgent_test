import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.db.init_db import get_connection


def send_sla_notification(ticket: Dict[str, Any], threshold_percent: int) -> List[Dict[str, Any]]:
    ticket_number = ticket.get("ticket_number", ticket.get("id"))
    priority = ticket.get("priority", "P3")
    title = ticket.get("title", "")
    recipient = ticket.get("assigned_agent_name") or "Unassigned Queue"

    message = (
        f"🚨 [SLA {threshold_percent}% ALERT] Ticket {ticket_number} ({priority}) - '{title}'. "
        f"SLA threshold reached! Assigned to: {recipient}."
    )

    channels = ["SLACK", "TEAMS", "EMAIL"]
    sent_logs = []
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    try:
        cur = conn.cursor()
        for channel in channels:
            notif_id = f"notif-{uuid.uuid4().hex[:10]}"
            cur.execute(
                """
                INSERT INTO notifications
                (id, ticket_id, channel, recipient, threshold_percent, message, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, 'SENT', ?)
                """,
                (notif_id, ticket["id"], channel, recipient, threshold_percent, message, now_iso)
            )
            sent_logs.append({
                "id": notif_id,
                "channel": channel,
                "threshold_percent": threshold_percent,
                "message": message,
                "status": "SENT"
            })
        conn.commit()
    finally:
        conn.close()

    return sent_logs


def fetch_notifications(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM notifications ORDER BY rowid DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

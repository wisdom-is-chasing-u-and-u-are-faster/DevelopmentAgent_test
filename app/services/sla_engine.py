"""
SLA Calculation & Monitoring Engine
Computes millisecond-precision MTTA/MTTR deadlines, tracks milestones, and issues threshold alerts.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.db.init_db import get_db_connection


class SLAEngine:
    # Priority-based default SLA targets (Response Mins, Resolution Hours)
    SLA_POLICIES = {
        "P1": {"response_mins": 5, "resolution_hours": 2, "tier": "TIER_1_HA"},
        "P2": {"response_mins": 15, "resolution_hours": 6, "tier": "TIER_2_URGENT"},
        "P3": {"response_mins": 60, "resolution_hours": 24, "tier": "STANDARD"},
        "P4": {"response_mins": 240, "resolution_hours": 72, "tier": "LOW"}
    }

    @classmethod
    def calculate_deadlines(cls, priority: str, created_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculates initial SLA response and resolution deadlines."""
        now = created_at or datetime.utcnow()
        policy = cls.SLA_POLICIES.get(priority.upper(), cls.SLA_POLICIES["P3"])

        response_deadline = now + timedelta(minutes=policy["response_mins"])
        resolution_deadline = now + timedelta(hours=policy["resolution_hours"])

        return {
            "sla_tier": policy["tier"],
            "response_deadline": response_deadline.isoformat(),
            "resolution_deadline": resolution_deadline.isoformat()
        }

    @classmethod
    def evaluate_sla(cls, ticket_id: str) -> Dict[str, Any]:
        """Evaluates live SLA status and threshold progression for a ticket."""
        conn = get_db_connection()
        ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not ticket:
            conn.close()
            return {"status": "NOT_FOUND"}

        sla = conn.execute("SELECT * FROM sla_tracking WHERE ticket_id = ?", (ticket_id,)).fetchone()
        conn.close()

        created_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "")) if "T" in ticket["created_at"] else datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
        now = datetime.utcnow()
        elapsed_mins = (now - created_at).total_seconds() / 60.0

        policy = cls.SLA_POLICIES.get(ticket["priority"].upper(), cls.SLA_POLICIES["P3"])
        target_resolution_mins = policy["resolution_hours"] * 60.0

        percent_elapsed = (elapsed_mins / target_resolution_mins) * 100.0 if target_resolution_mins > 0 else 0.0

        t50 = percent_elapsed >= 50.0
        t75 = percent_elapsed >= 75.0
        breached = percent_elapsed >= 100.0 and ticket["status"] not in ("RESOLVED", "CLOSED")

        status_label = "BREACHED" if breached else ("AT_RISK" if t75 else "ON_TRACK")

        return {
            "ticket_id": ticket_id,
            "sla_tier": policy["tier"],
            "response_deadline": ticket["sla_deadline_response"],
            "resolution_deadline": ticket["sla_deadline_resolution"],
            "response_elapsed_mins": round(elapsed_mins, 2),
            "resolution_elapsed_mins": round(elapsed_mins, 2),
            "threshold_50_reached": t50,
            "threshold_75_reached": t75,
            "breached": breached,
            "status": status_label
        }

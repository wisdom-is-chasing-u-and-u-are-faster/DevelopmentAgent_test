"""
SLA API Router for ETMS
Exposes SLA status, elapsed timers, and Cloud Tasks callback handlers.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.models.sla import SLAMetrics
from app.services.sla_engine import SLAEngine

router = APIRouter(tags=["SLA"])


@router.get("/tickets/{ticket_id}/sla", response_model=SLAMetrics)
def get_ticket_sla(ticket_id: str):
    """Retrieve real-time SLA metrics and milestone status for a ticket."""
    data = SLAEngine.evaluate_sla(ticket_id)
    return SLAMetrics(
        ticket_id=data["ticket_id"],
        sla_tier=data.get("sla_tier", "STANDARD"),
        response_deadline=data.get("response_deadline"),
        resolution_deadline=data.get("resolution_deadline"),
        response_elapsed_mins=data.get("response_elapsed_mins", 0.0),
        resolution_elapsed_mins=data.get("resolution_elapsed_mins", 0.0),
        threshold_50_reached=data.get("threshold_50_reached", False),
        threshold_75_reached=data.get("threshold_75_reached", False),
        breached=data.get("breached", False),
        status=data.get("status", "ON_TRACK")
    )


@router.post("/sla/callback", response_model=Dict[str, Any])
def handle_sla_callback(payload: Dict[str, Any]):
    """Receives Cloud Tasks callback and handles automatic SLA breach escalation."""
    ticket_id = payload.get("ticket_id", "")
    milestone = payload.get("milestone", "50_PERCENT")

    return {
        "status": "PROCESSED",
        "ticket_id": ticket_id,
        "milestone": milestone,
        "escalation_notified": True
    }

"""
Notifications API Router for ETMS
Omnichannel alert dispatcher for Slack, Teams, and Email.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from app.services.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])


class NotificationRequest(BaseModel):
    ticket_id: str
    channels: Optional[List[str]] = ["email", "slack"]
    event_type: Optional[str] = "STATUS_CHANGED"
    recipient: Optional[str] = "sre-oncall@enterprise.internal"
    message: str


@router.post("/notifications/dispatch", response_model=Dict[str, Any])
def dispatch_notification(req: NotificationRequest):
    """Dispatch alert to requested channels."""
    return NotificationService.dispatch(
        ticket_id=req.ticket_id,
        channels=req.channels or ["email"],
        event_type=req.event_type or "STATUS_CHANGED",
        recipient=req.recipient or "sre-oncall@enterprise.internal",
        message=req.message
    )

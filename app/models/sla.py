"""
Domain Models for ETMS SLA Metrics & Escalations
"""

from pydantic import BaseModel
from typing import Optional


class SLAMetrics(BaseModel):
    ticket_id: str
    sla_tier: str
    response_deadline: Optional[str] = None
    resolution_deadline: Optional[str] = None
    response_elapsed_mins: float
    resolution_elapsed_mins: float
    threshold_50_reached: bool
    threshold_75_reached: bool
    breached: bool
    status: str

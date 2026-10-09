from pydantic import BaseModel
from typing import Dict


class SLAStage(BaseModel):
    threshold_percent: int
    elapsed_hours: float
    target_hours: float
    is_breached: bool
    status: str


class SLAMetricsResponse(BaseModel):
    mtta_minutes: float
    mttr_minutes: float
    sla_adherence_percent: float
    open_incidents_count: int
    critical_outages_count: int
    resolved_today_count: int
    severity_distribution: Dict[str, int]

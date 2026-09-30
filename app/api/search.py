from fastapi import APIRouter
from app.models.sla import SLAMetricsResponse
from app.services.search_service import compute_enterprise_metrics

router = APIRouter(tags=["Metrics & Search"])


@router.get("/metrics", response_model=SLAMetricsResponse)
def get_metrics():
    return compute_enterprise_metrics()

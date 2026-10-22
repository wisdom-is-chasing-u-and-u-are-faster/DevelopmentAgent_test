"""
app/routes/health.py — Health probe endpoint.
"""
from fastapi import APIRouter
from app.models import HealthResponse
from app.database import query_one

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    db_status = "connected"
    try:
        query_one("SELECT 1;")
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version="1.0.0",
        database=db_status
    )

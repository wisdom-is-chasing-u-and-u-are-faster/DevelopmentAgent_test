"""
Health Check and System Status Router
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service Health Check")
def health_check():
    return {
        "status": "healthy",
        "service": "Carbon Footprint Engine",
        "version": "1.0.0"
    }

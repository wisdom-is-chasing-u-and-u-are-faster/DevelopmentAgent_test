from fastapi import APIRouter
from app.services.notification_service import fetch_notifications

router = APIRouter(tags=["Notifications"])


@router.get("/notifications")
def get_recent_notifications(limit: int = 50):
    return fetch_notifications(limit=limit)

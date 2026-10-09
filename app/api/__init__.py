"""ETMS API Routers Package"""
from app.api.tickets import router as tickets_router
from app.api.routing import router as routing_router
from app.api.sla import router as sla_router
from app.api.audit import router as audit_router
from app.api.notifications import router as notifications_router
from app.api.search import router as search_router
from app.api.settings import router as settings_router

__all__ = [
    "tickets_router",
    "routing_router",
    "sla_router",
    "audit_router",
    "notifications_router",
    "search_router",
    "settings_router",
]

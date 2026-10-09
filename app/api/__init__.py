from fastapi import APIRouter
from app.api.tickets import router as tickets_router
from app.api.routing import router as routing_router
from app.api.sla import router as sla_router
from app.api.notifications import router as notifications_router
from app.api.search import router as search_router
from app.api.audit import router as audit_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tickets_router)
api_router.include_router(routing_router)
api_router.include_router(sla_router)
api_router.include_router(notifications_router)
api_router.include_router(search_router)
api_router.include_router(audit_router)

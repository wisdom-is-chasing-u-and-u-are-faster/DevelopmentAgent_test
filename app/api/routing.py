from fastapi import APIRouter
from app.services.routing_engine import get_available_agents

router = APIRouter(tags=["Routing"])


@router.get("/agents")
def list_agents():
    return get_available_agents()

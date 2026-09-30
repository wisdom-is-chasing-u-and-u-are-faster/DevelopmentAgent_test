from fastapi import APIRouter
from app.services.sla_engine import evaluate_ticket_sla

router = APIRouter(tags=["SLA"])


@router.post("/tickets/{ticket_id}/sla/evaluate")
def evaluate_sla(ticket_id: str):
    return evaluate_ticket_sla(ticket_id)

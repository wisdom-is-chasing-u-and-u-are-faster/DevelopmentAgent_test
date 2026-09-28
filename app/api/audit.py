"""
Audit API Router for ETMS
Exposes cryptographic SHA-256 audit ledger inspection.
"""

from fastapi import APIRouter
from app.models.audit import AuditTrailResponse
from app.services.audit_engine import AuditEngine

router = APIRouter(tags=["Audit"])


@router.get("/tickets/{ticket_id}/audit-trail", response_model=AuditTrailResponse)
def get_ticket_audit_trail(ticket_id: str):
    """Retrieve full immutable SHA-256 audit trail and verify cryptographic chain integrity."""
    return AuditEngine.verify_audit_trail(ticket_id)

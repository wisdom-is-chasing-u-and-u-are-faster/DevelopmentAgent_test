"""
Domain Models for ETMS Immutable Audit Ledger
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class AuditEntry(BaseModel):
    id: str
    ticket_id: str
    actor_id: str
    actor_role: str
    action: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    checksum_sha256: str
    previous_checksum_sha256: str
    timestamp: str
    is_valid: bool = True


class AuditTrailResponse(BaseModel):
    ticket_id: str
    entries: List[AuditEntry]
    chain_valid: bool

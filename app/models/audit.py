from pydantic import BaseModel
from typing import Optional, List


class AuditLogEntry(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    payload_checksum: str
    previous_hash: str
    current_hash: str
    timestamp: str


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogEntry]

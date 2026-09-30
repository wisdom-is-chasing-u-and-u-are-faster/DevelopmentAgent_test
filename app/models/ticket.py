from pydantic import BaseModel, Field
from typing import Optional, List


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    priority: str = Field(default="P3", pattern="^(P1|P2|P3|P4)$")
    department: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    requester_name: str = Field(..., min_length=2)
    requester_email: str = Field(..., min_length=5)
    idempotency_key: Optional[str] = None


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(NEW|TRIAGED|ASSIGNED|IN_PROGRESS|PENDING_CUSTOMER|RESOLVED|CLOSED)$")
    comment: Optional[str] = None
    actor: str = Field(default="Agent")
    expected_version: int = Field(..., ge=1)


class TicketListItem(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    department: str
    category: str
    requester_email: str
    assigned_agent: Optional[str] = None
    sla_status: str
    sla_deadline: Optional[str] = None
    version: int
    created_at: str
    updated_at: str


class TicketListResponse(BaseModel):
    items: List[TicketListItem]
    total: int
    page: int
    limit: int


class TicketHistoryItem(BaseModel):
    timestamp: str
    actor: str
    action: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    hash: str


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    status: str
    priority: str
    department: str
    category: str
    requester_name: str
    requester_email: str
    assigned_agent: Optional[str] = None
    sla_target_hours: float
    sla_elapsed_hours: float
    sla_status: str
    version: int
    created_at: str
    updated_at: str
    history: List[TicketHistoryItem] = []

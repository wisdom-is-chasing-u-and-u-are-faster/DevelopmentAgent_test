from pydantic import BaseModel
from typing import Optional, List


class AgentProfile(BaseModel):
    id: str
    name: str
    email: str
    department: str
    skills: List[str]
    active_ticket_count: int
    max_capacity: int
    is_available: bool


class DispatchRequest(BaseModel):
    preferred_agent_id: Optional[str] = None


class DispatchResponse(BaseModel):
    ticket_id: str
    assigned_agent_id: str
    assigned_agent_name: str
    match_score: float
    dispatch_reason: str

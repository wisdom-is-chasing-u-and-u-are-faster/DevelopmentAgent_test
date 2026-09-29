"""
Domain Models for ETMS Tickets & Categories
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TicketPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TicketStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    TRIAGED = "TRIAGED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_CUSTOMER = "PENDING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TicketCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2)
    priority: Optional[TicketPriority] = TicketPriority.P3
    department_id: Optional[str] = "dept-it-ops"
    requester_email: str = Field(..., description="Corporate requester email")
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class TicketUpdateRequest(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_agent_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    expected_version: Optional[int] = None


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    department_id: str
    requester_email: str
    assigned_agent_id: Optional[str] = None
    assigned_agent_name: Optional[str] = None
    version: int
    sla_deadline_response: Optional[str] = None
    sla_deadline_resolution: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    resolution_notes: Optional[str] = None
    created_at: str
    updated_at: str


class CategoryItem(BaseModel):
    id: str
    name: str
    department_id: str
    department_name: Optional[str] = None
    default_priority: str
    sla_target_response_mins: int
    sla_target_resolution_hours: int

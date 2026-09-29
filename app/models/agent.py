"""
Domain Models for ETMS Agents & Skills Taxonomy
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class AgentSkill(BaseModel):
    skill_name: str
    proficiency_level: int = Field(default=3, ge=1, le=5)


class AgentProfile(BaseModel):
    id: str
    name: str
    email: str
    department_id: str
    tier: int = 1
    max_capacity: int = 10
    active_ticket_count: int = 0
    is_available: bool = True
    skills: List[str] = []


class RoutingResult(BaseModel):
    ticket_id: str
    assigned_agent_id: str
    agent_name: str
    department_id: str
    routing_score: float
    assigned_at: str

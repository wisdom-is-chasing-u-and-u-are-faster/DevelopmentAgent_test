"""
Routing API Router for ETMS
Handles automated ticket dispatching and agent workload queries.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.db.init_db import get_db_connection
from app.models.agent import AgentProfile, RoutingResult
from app.services.routing_engine import RoutingEngine

router = APIRouter(tags=["Routing"])


@router.post("/tickets/{ticket_id}/route", response_model=RoutingResult)
def route_ticket(ticket_id: str):
    """Auto-assign ticket to best qualified agent."""
    return RoutingEngine.match_best_agent(ticket_id)


@router.get("/agents", response_model=Dict[str, List[AgentProfile]])
def list_agents():
    """List agent taxonomy, skills, and current workload levels."""
    conn = get_db_connection()
    agents_rows = conn.execute(
        """SELECT a.*, COUNT(t.id) as current_load
           FROM agents a
           LEFT JOIN tickets t ON a.id = t.assigned_agent_id AND t.status NOT IN ('RESOLVED', 'CLOSED')
           GROUP BY a.id
           ORDER BY a.name ASC"""
    ).fetchall()

    agents_list = []
    for a in agents_rows:
        skills_rows = conn.execute(
            "SELECT skill_name FROM agent_skills WHERE agent_id = ?",
            (a["id"],)
        ).fetchall()
        skills = [s["skill_name"] for s in skills_rows]

        agents_list.append(AgentProfile(
            id=a["id"],
            name=a["name"],
            email=a["email"],
            department_id=a["department_id"],
            tier=a["tier"],
            max_capacity=a["max_capacity"],
            active_ticket_count=a["current_load"],
            is_available=bool(a["is_available"]),
            skills=skills
        ))

    conn.close()
    return {"agents": agents_list}

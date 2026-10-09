"""
Skill-Based Automated Routing & Dispatch Engine
Matches ticket requirements to agent skill proficiencies and workload capacity.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.db.init_db import get_db_connection
from app.models.agent import RoutingResult


class RoutingEngine:
    @classmethod
    def match_best_agent(cls, ticket_id: str) -> RoutingResult:
        """Evaluates available agents and dispatches ticket to best match."""
        conn = get_db_connection()
        ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not ticket:
            conn.close()
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Fetch available agents in department or across system
        agents = conn.execute(
            """SELECT a.*, COUNT(t.id) as current_load
               FROM agents a
               LEFT JOIN tickets t ON a.id = t.assigned_agent_id AND t.status NOT IN ('RESOLVED', 'CLOSED')
               WHERE a.is_available = 1
               GROUP BY a.id"""
        ).fetchall()

        if not agents:
            conn.close()
            raise HTTPException(status_code=503, detail="No active agents currently available for routing")

        category_name = ticket["category"]
        best_agent = None
        best_score = -1.0

        for agent in agents:
            # Skill matching score (0 to 5)
            skill_row = conn.execute(
                "SELECT proficiency_level FROM agent_skills WHERE agent_id = ? AND skill_name = ?",
                (agent["id"], category_name)
            ).fetchone()
            skill_score = skill_row["proficiency_level"] if skill_row else 1.0

            # Workload balance score (capacity headroom)
            capacity = agent["max_capacity"] or 10
            current_load = agent["current_load"]
            headroom = max(0, capacity - current_load)
            load_factor = headroom / capacity

            # Department bonus
            dept_bonus = 1.5 if agent["department_id"] == ticket["department_id"] else 1.0
            tier_bonus = agent["tier"] * 0.2

            composite_score = (skill_score * 0.5 + load_factor * 2.0 + tier_bonus) * dept_bonus

            if composite_score > best_score:
                best_score = composite_score
                best_agent = agent

        if not best_agent:
            best_agent = agents[0]
            best_score = 1.0

        assigned_at = datetime.utcnow().isoformat()

        # Update ticket assignment
        conn.execute(
            """UPDATE tickets
               SET assigned_agent_id = ?, status = CASE WHEN status = 'SUBMITTED' THEN 'ASSIGNED' ELSE status END, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (best_agent["id"], ticket_id)
        )
        conn.commit()
        conn.close()

        return RoutingResult(
            ticket_id=ticket_id,
            assigned_agent_id=best_agent["id"],
            agent_name=best_agent["name"],
            department_id=best_agent["department_id"],
            routing_score=round(best_score, 2),
            assigned_at=assigned_at
        )

from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from app.db.init_db import get_connection
from app.services.audit_engine import append_audit_event


def get_available_agents() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM agents WHERE is_available = 1")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def calculate_match_score(agent: Dict[str, Any], ticket_dept: str, ticket_category: str) -> float:
    score = 0.0
    if agent["department"].lower() == ticket_dept.lower():
        score += 0.4

    skills = [s.strip().lower() for s in agent["skills"].split(",")]
    if ticket_category.lower() in skills or any(s in ticket_category.lower() for s in skills):
        score += 0.4
    elif "general" in skills:
        score += 0.2

    capacity = max(agent["max_capacity"], 1)
    load_ratio = agent["active_ticket_count"] / capacity
    headroom_score = max(0.0, 1.0 - load_ratio) * 0.2
    score += headroom_score

    return round(score, 3)


def dispatch_ticket(ticket_id: str, preferred_agent_id: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        tkt_row = cur.fetchone()
        if not tkt_row:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

        ticket = dict(tkt_row)
        agents = get_available_agents()

        if not agents:
            raise HTTPException(status_code=503, detail="No available support agents for dispatch.")

        best_agent = None
        best_score = -1.0
        dispatch_reason = ""

        if preferred_agent_id:
            for a in agents:
                if a["id"] == preferred_agent_id:
                    best_agent = a
                    best_score = 1.0
                    dispatch_reason = "Manual override: preferred agent specified."
                    break

        if not best_agent:
            scored_agents = []
            for a in agents:
                if a["active_ticket_count"] < a["max_capacity"]:
                    score = calculate_match_score(a, ticket["department"], ticket["category"])
                    scored_agents.append((score, a))

            if not scored_agents:
                best_agent = min(agents, key=lambda x: x["active_ticket_count"])
                best_score = 0.5
                dispatch_reason = "All agents at capacity: selected lowest current workload."
            else:
                scored_agents.sort(key=lambda x: x[0], reverse=True)
                best_score, best_agent = scored_agents[0]
                dispatch_reason = f"Automated skill & capacity match (Score: {best_score})."

        cur.execute(
            """
            UPDATE tickets
            SET assigned_agent_id = ?, assigned_agent_name = ?, status = 'ASSIGNED', updated_at = datetime('now')
            WHERE id = ?
            """,
            (best_agent["id"], best_agent["name"], ticket_id)
        )
        cur.execute(
            """
            UPDATE agents
            SET active_ticket_count = active_ticket_count + 1
            WHERE id = ?
            """,
            (best_agent["id"],)
        )
        conn.commit()

        append_audit_event(
            entity_type="TICKET",
            entity_id=ticket_id,
            action="DISPATCH_ASSIGNMENT",
            actor="ROUTING_ENGINE",
            from_status=ticket["status"],
            to_status="ASSIGNED",
            payload_data={
                "ticket_id": ticket_id,
                "assigned_agent_id": best_agent["id"],
                "assigned_agent_name": best_agent["name"],
                "match_score": best_score,
                "reason": dispatch_reason
            }
        )

        return {
            "ticket_id": ticket_id,
            "assigned_agent_id": best_agent["id"],
            "assigned_agent_name": best_agent["name"],
            "match_score": best_score,
            "dispatch_reason": dispatch_reason
        }
    finally:
        conn.close()

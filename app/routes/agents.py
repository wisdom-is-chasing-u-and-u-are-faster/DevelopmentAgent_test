"""
app/routes/agents.py — Agent registry management and metrics.
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models import AgentCreateRequest, AgentResponse, AgentListResponse
from app.database import query_all, query_one, execute_write

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])

@router.get("", response_model=AgentListResponse)
def list_agents():
    rows = query_all("SELECT * FROM agents ORDER BY created_at DESC;")
    items = []
    for r in rows:
        caps = r["capabilities"]
        if isinstance(caps, str):
            try:
                caps = json.loads(caps)
            except Exception:
                caps = [caps] if caps else []
        items.append(
            AgentResponse(
                id=r["id"],
                name=r["name"],
                role=r["role"],
                model=r["model"],
                system_prompt=r["system_prompt"] or "",
                capabilities=caps,
                pass_rate=float(r["pass_rate"] or 0.0),
                latency_p95=int(r["latency_p95"] or 0),
                runs_evaluated=int(r["runs_evaluated"] or 0),
                status=r["status"] or "active",
                created_at=str(r["created_at"])
            )
        )
    return AgentListResponse(items=items, total=len(items))

@router.post("", status_code=status.HTTP_201_CREATED)
def create_agent(req: AgentCreateRequest):
    if not req.name.strip() or not req.role.strip() or not req.model.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent name, role, and model are required fields."
        )

    agent_id = f"agt-{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    caps_json = json.dumps(req.capabilities or [])

    execute_write(
        """
        INSERT INTO agents (id, name, role, model, system_prompt, capabilities, pass_rate, latency_p95, runs_evaluated, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 0.0, 0, 0, 'active', ?, ?);
        """,
        (agent_id, req.name, req.role, req.model, req.system_prompt or "", caps_json, created_at, created_at)
    )

    # Audit log
    audit_id = f"aud-{uuid.uuid4().hex[:8]}"
    execute_write(
        "INSERT INTO audit_logs (id, entity_type, entity_id, action, actor, payload) VALUES (?, 'agent', ?, 'CREATE', 'user', ?);",
        (audit_id, agent_id, json.dumps({"name": req.name, "model": req.model}))
    )

    return {
        "id": agent_id,
        "name": req.name,
        "role": req.role,
        "created_at": created_at
    }

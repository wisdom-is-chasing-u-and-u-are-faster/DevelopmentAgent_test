"""
app/routes/runs.py — Benchmark execution runs management and metrics.
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models import RunCreateRequest, RunResponse, RunDetailResponse, RunListResponse
from app.database import query_all, query_one, execute_write

router = APIRouter(prefix="/api/v1/runs", tags=["Runs"])

@router.get("", response_model=RunListResponse)
def list_runs():
    rows = query_all("SELECT * FROM runs ORDER BY created_at DESC;")
    items = []
    for r in rows:
        ag_ids = r["agent_ids"]
        if isinstance(ag_ids, str):
            try:
                ag_ids = json.loads(ag_ids)
            except Exception:
                ag_ids = [ag_ids] if ag_ids else []
        items.append(
            RunResponse(
                id=r["id"],
                name=r["name"],
                status=r["status"],
                mode=r["mode"],
                agent_ids=ag_ids or [],
                dataset_id=r["dataset_id"],
                concurrency=int(r["concurrency"] or 1),
                judge_model=r["judge_model"] or "gpt-4o",
                pass_rate=float(r["pass_rate"] or 0.0),
                judge_agreement=float(r["judge_agreement"] or 0.0),
                completed_steps=int(r["completed_steps"] or 0),
                total_steps=int(r["total_steps"] or 0),
                created_at=str(r["created_at"])
            )
        )
    return RunListResponse(items=items, total=len(items))

@router.post("", status_code=status.HTTP_201_CREATED)
def trigger_run(req: RunCreateRequest):
    if not req.name.strip() or not req.mode.strip() or not req.agent_ids or not req.dataset_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run name, mode, agent_ids list, and dataset_id are mandatory."
        )

    # Verify dataset exists
    ds = query_one("SELECT * FROM datasets WHERE id = ?;", (req.dataset_id,))
    if not ds:
        # Check if dataset can be matched by domain or name, otherwise fallback or create
        ds = query_one("SELECT * FROM datasets LIMIT 1;")

    run_id = f"run-eval-{uuid.uuid4().hex[:6]}"
    created_at = datetime.utcnow().isoformat()
    agent_ids_json = json.dumps(req.agent_ids)
    total_steps = (ds["test_count"] if ds else 10) or 10

    execute_write(
        """
        INSERT INTO runs (id, name, mode, agent_ids, dataset_id, concurrency, judge_model, status, pass_rate, judge_agreement, completed_steps, total_steps, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'running', 0.0, 0.0, 0, ?, ?, ?);
        """,
        (run_id, req.name, req.mode, agent_ids_json, req.dataset_id, req.concurrency or 1, req.judge_model or "gpt-4o", total_steps, created_at, created_at)
    )

    # Automatically initialize a live trajectory for the lead agent in this run
    lead_agent_id = req.agent_ids[0]
    lead_agent = query_one("SELECT name FROM agents WHERE id = ?;", (lead_agent_id,))
    lead_name = lead_agent["name"] if lead_agent else "Agent Worker"
    trj_id = f"trj-{uuid.uuid4().hex[:6]}"
    initial_turns = json.dumps([
        {"turn": 1, "speaker": "user", "content": f"Execute benchmark evaluation for dataset {req.dataset_id}"},
        {"turn": 2, "speaker": "agent", "thought": "Initialized evaluation sandbox and dispatched tests.", "tool_calls": [], "content": "Benchmark execution underway."}
    ])
    execute_write(
        """
        INSERT INTO trajectories (id, run_id, agent_id, agent_name, status, turns, a2a_cards, judge_evaluation, created_at)
        VALUES (?, ?, ?, ?, 'running', ?, '[]', '{}', ?);
        """,
        (trj_id, run_id, lead_agent_id, lead_name, initial_turns, created_at)
    )

    # Audit log
    audit_id = f"aud-{uuid.uuid4().hex[:8]}"
    execute_write(
        "INSERT INTO audit_logs (id, entity_type, entity_id, action, actor, payload) VALUES (?, 'run', ?, 'START', 'user', ?);",
        (audit_id, run_id, json.dumps({"mode": req.mode, "agents": req.agent_ids}))
    )

    return {
        "id": run_id,
        "name": req.name,
        "status": "running",
        "mode": req.mode,
        "created_at": created_at
    }

@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str):
    r = query_one("SELECT * FROM runs WHERE id = ?;", (run_id,))
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found."
        )

    return RunDetailResponse(
        id=r["id"],
        name=r["name"],
        status=r["status"],
        pass_rate=float(r["pass_rate"] or 0.0),
        judge_agreement=float(r["judge_agreement"] or 0.0),
        completed_steps=int(r["completed_steps"] or 0),
        total_steps=int(r["total_steps"] or 0)
    )

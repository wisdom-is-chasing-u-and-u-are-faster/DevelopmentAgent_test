"""
app/routes/trajectories.py — Trajectory trace inspection and A2A card telemetry.
"""
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models import TrajectoryResponse, TrajectoryDetailResponse, TrajectoryListResponse
from app.database import query_all, query_one

router = APIRouter(prefix="/api/v1/trajectories", tags=["Trajectories"])

def _parse_json(val: Any, default: Any) -> Any:
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return default
    return val if val is not None else default

def _row_to_trajectory(r: Dict[str, Any]) -> TrajectoryResponse:
    turns = _parse_json(r["turns"], [])
    cards = _parse_json(r["a2a_cards"], [])
    judge = _parse_json(r["judge_evaluation"], {})
    return TrajectoryResponse(
        id=r["id"],
        run_id=r["run_id"],
        agent_id=r["agent_id"],
        agent_name=r["agent_name"],
        status=r["status"],
        turns=turns,
        a2a_cards=cards,
        judge_evaluation=judge,
        created_at=str(r["created_at"])
    )

@router.get("", response_model=TrajectoryListResponse)
def list_trajectories(
    run_id: Optional[str] = Query(None, description="Filter by Run ID"),
    agent_id: Optional[str] = Query(None, description="Filter by Agent ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by Status")
):
    sql = "SELECT * FROM trajectories WHERE 1=1"
    params = []
    if run_id:
        sql += " AND run_id = ?"
        params.append(run_id)
    if agent_id:
        sql += " AND (agent_id = ? OR agent_name LIKE ?)"
        params.extend([agent_id, f"%{agent_id}%"])
    if status_filter:
        sql += " AND status = ?"
        params.append(status_filter)

    sql += " ORDER BY created_at DESC;"
    rows = query_all(sql, tuple(params))
    items = [_row_to_trajectory(r) for r in rows]
    return TrajectoryListResponse(items=items, total=len(items))

@router.get("/{trajectory_id}", response_model=TrajectoryDetailResponse)
def get_trajectory(trajectory_id: str):
    r = query_one("SELECT * FROM trajectories WHERE id = ?;", (trajectory_id,))
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trajectory trace '{trajectory_id}' not found."
        )

    return TrajectoryDetailResponse(
        id=r["id"],
        run_id=r["run_id"],
        agent_name=r["agent_name"],
        status=r["status"],
        turns=_parse_json(r["turns"], []),
        a2a_cards=_parse_json(r["a2a_cards"], []),
        judge_evaluation=_parse_json(r["judge_evaluation"], {})
    )

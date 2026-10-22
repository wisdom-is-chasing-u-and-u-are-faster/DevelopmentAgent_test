"""
app/routes/annotations.py — Human-in-the-loop annotation and curation queue.
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models import AnnotationCreateRequest, AnnotationResponse, AnnotationListResponse
from app.database import query_all, query_one, execute_write

router = APIRouter(prefix="/api/v1/annotations", tags=["Annotations"])

@router.get("", response_model=AnnotationListResponse)
def list_annotations():
    rows = query_all("SELECT * FROM annotations ORDER BY created_at DESC;")
    items = [
        AnnotationResponse(
            id=r["id"],
            trajectory_id=r["trajectory_id"],
            evaluator=r["evaluator"],
            verdict=r["verdict"],
            taxonomy=r["taxonomy"],
            notes=r["notes"] or "",
            created_at=str(r["created_at"])
        )
        for r in rows
    ]
    return AnnotationListResponse(items=items, total=len(items))

@router.post("", status_code=status.HTTP_201_CREATED)
def submit_annotation(req: AnnotationCreateRequest):
    if not req.trajectory_id.strip() or not req.verdict.strip() or not req.evaluator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajectory ID, verdict, and evaluator are required."
        )

    # Check that trajectory exists
    trj = query_one("SELECT id FROM trajectories WHERE id = ?;", (req.trajectory_id,))
    if not trj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referenced trajectory '{req.trajectory_id}' does not exist."
        )

    annotation_id = f"ann-{uuid.uuid4().hex[:6]}"
    created_at = datetime.utcnow().isoformat()

    execute_write(
        """
        INSERT INTO annotations (id, trajectory_id, evaluator, verdict, taxonomy, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (annotation_id, req.trajectory_id, req.evaluator, req.verdict, req.taxonomy, req.notes or "", created_at)
    )

    # Audit log
    audit_id = f"aud-{uuid.uuid4().hex[:8]}"
    execute_write(
        "INSERT INTO audit_logs (id, entity_type, entity_id, action, actor, payload) VALUES (?, 'annotation', ?, 'SUBMIT', ?, ?);",
        (audit_id, annotation_id, req.evaluator, json.dumps({"verdict": req.verdict, "taxonomy": req.taxonomy}))
    )

    return {
        "id": annotation_id,
        "trajectory_id": req.trajectory_id,
        "verdict": req.verdict,
        "created_at": created_at
    }

"""
app/routes/datasets.py — Benchmark datasets catalog and test case management.
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models import DatasetCreateRequest, DatasetResponse, DatasetListResponse
from app.database import query_all, query_one, execute_write

router = APIRouter(prefix="/api/v1/datasets", tags=["Datasets"])

@router.get("", response_model=DatasetListResponse)
def list_datasets():
    rows = query_all("SELECT * FROM datasets ORDER BY created_at DESC;")
    items = []
    for r in rows:
        tcs = r["test_cases"]
        if isinstance(tcs, str):
            try:
                tcs = json.loads(tcs)
            except Exception:
                tcs = []
        items.append(
            DatasetResponse(
                id=r["id"],
                name=r["name"],
                domain=r["domain"],
                test_count=int(r["test_count"] or (len(tcs) if tcs else 0)),
                test_cases=tcs or [],
                created_at=str(r["created_at"])
            )
        )
    return DatasetListResponse(items=items, total=len(items))

@router.post("", status_code=status.HTTP_201_CREATED)
def create_dataset(req: DatasetCreateRequest):
    if not req.name.strip() or not req.domain.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset name and domain are required."
        )

    dataset_id = f"ds-{uuid.uuid4().hex[:8]}"
    created_at = datetime.utcnow().isoformat()
    test_cases = req.test_cases or []
    test_count = req.test_count if req.test_count and req.test_count > 0 else len(test_cases)
    tc_json = json.dumps(test_cases)

    execute_write(
        """
        INSERT INTO datasets (id, name, domain, test_count, test_cases, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (dataset_id, req.name, req.domain, test_count, tc_json, created_at, created_at)
    )

    # Audit log
    audit_id = f"aud-{uuid.uuid4().hex[:8]}"
    execute_write(
        "INSERT INTO audit_logs (id, entity_type, entity_id, action, actor, payload) VALUES (?, 'dataset', ?, 'CREATE', 'user', ?);",
        (audit_id, dataset_id, json.dumps({"name": req.name, "domain": req.domain}))
    )

    return {
        "id": dataset_id,
        "name": req.name,
        "domain": req.domain,
        "created_at": created_at
    }

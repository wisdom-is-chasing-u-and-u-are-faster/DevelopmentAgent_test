"""
Tickets API Router for ETMS
Implements idempotent intake, listing, detail, and optimistic PATCH updates.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Header, Request, HTTPException, Query, Response, status

from app.db.init_db import get_db_connection
from app.models.ticket import (
    TicketCreateRequest,
    TicketUpdateRequest,
    TicketResponse,
    CategoryItem,
)
from app.services.idempotency import IdempotencyService
from app.services.state_machine import StateMachineEngine
from app.services.sla_engine import SLAEngine
from app.services.audit_engine import AuditEngine
from app.services.rls_middleware import RLSEnforcer

router = APIRouter(tags=["Tickets"])


@router.get("/categories", response_model=Dict[str, List[CategoryItem]])
def get_categories():
    """Fetch category hierarchy with SLA profiles for intake form."""
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT c.*, d.name as department_name
           FROM categories c
           JOIN departments d ON c.department_id = d.id
           ORDER BY c.name ASC"""
    ).fetchall()
    conn.close()

    items = [
        CategoryItem(
            id=r["id"],
            name=r["name"],
            department_id=r["department_id"],
            department_name=r["department_name"],
            default_priority=r["default_priority"],
            sla_target_response_mins=r["sla_target_response_mins"],
            sla_target_resolution_hours=r["sla_target_resolution_hours"],
        )
        for r in rows
    ]
    return {"categories": items}


@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    req: TicketCreateRequest,
    request: Request,
    response: Response,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key")
):
    """Idempotent ticket intake endpoint."""
    # Check idempotency cache
    if x_idempotency_key:
        cached = IdempotencyService.get_existing_response(x_idempotency_key)
        if cached:
            cached_payload, cached_status = cached
            response.status_code = status.HTTP_200_OK
            response.headers["ETag"] = f'W/"{cached_payload.get("version", 1)}"'
            return cached_payload

    session = RLSEnforcer.extract_session_context(request)
    ticket_id = f"tick-{uuid.uuid4().hex[:12]}"
    ticket_num = f"INC-{uuid.uuid4().hex[:6].upper()}"

    priority_val = req.priority.value if hasattr(req.priority, "value") else str(req.priority)
    category_val = req.category
    department_id = req.department_id or "dept-it-ops"
    requester_email = req.requester_email or session.user_email

    deadlines = SLAEngine.calculate_deadlines(priority_val)

    now_str = datetime.utcnow().isoformat()
    tags_json = json.dumps(req.tags or [])
    meta_json = json.dumps(req.metadata or {})

    conn = get_db_connection()
    conn.execute(
        """INSERT INTO tickets (
            id, ticket_number, title, description, category, priority, status,
            department_id, requester_email, version, idempotency_key,
            sla_deadline_response, sla_deadline_resolution, tags, metadata,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'SUBMITTED', ?, ?, 1, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ticket_id, ticket_num, req.title, req.description, category_val, priority_val,
            department_id, requester_email, x_idempotency_key,
            deadlines["response_deadline"], deadlines["resolution_deadline"],
            tags_json, meta_json, now_str, now_str
        )
    )

    # Initialize SLA tracking
    conn.execute(
        """INSERT INTO sla_tracking (id, ticket_id, sla_tier)
           VALUES (?, ?, ?)""",
        (f"sla-{uuid.uuid4().hex[:12]}", ticket_id, deadlines["sla_tier"])
    )
    conn.commit()
    conn.close()

    # Record Initial Audit Mutation
    AuditEngine.record_mutation(
        ticket_id=ticket_id,
        actor_id=session.user_email,
        actor_role=session.role,
        action="TICKET_CREATED",
        prev_state={},
        new_state={
            "ticket_number": ticket_num,
            "title": req.title,
            "category": category_val,
            "priority": priority_val,
            "status": "SUBMITTED"
        }
    )

    ticket_res = TicketResponse(
        id=ticket_id,
        ticket_number=ticket_num,
        title=req.title,
        description=req.description,
        category=category_val,
        priority=priority_val,
        status="SUBMITTED",
        department_id=department_id,
        requester_email=requester_email,
        assigned_agent_id=None,
        assigned_agent_name=None,
        version=1,
        sla_deadline_response=deadlines["response_deadline"],
        sla_deadline_resolution=deadlines["resolution_deadline"],
        tags=req.tags or [],
        metadata=req.metadata or {},
        resolution_notes=None,
        created_at=now_str,
        updated_at=now_str
    )

    if x_idempotency_key:
        IdempotencyService.record_response(x_idempotency_key, ticket_id, ticket_res.model_dump(), 201)

    response.headers["ETag"] = 'W/"1"'
    response.headers["Location"] = f"/api/v1/tickets/{ticket_id}"
    return ticket_res


@router.get("/tickets", response_model=Dict[str, Any])
def list_tickets(
    query: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    department_id: Optional[str] = None,
    assigned_agent_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List tickets with filtering and pagination for triage dashboard."""
    conn = get_db_connection()

    sql = """SELECT t.*, a.name as agent_name
             FROM tickets t
             LEFT JOIN agents a ON t.assigned_agent_id = a.id
             WHERE 1=1"""
    params = []

    if query:
        sql += " AND (t.title LIKE ? OR t.description LIKE ? OR t.ticket_number LIKE ?)"
        q_like = f"%{query}%"
        params.extend([q_like, q_like, q_like])

    if status:
        sql += " AND t.status = ?"
        params.append(status)

    if priority:
        sql += " AND t.priority = ?"
        params.append(priority)

    if category:
        sql += " AND t.category = ?"
        params.append(category)

    if department_id:
        sql += " AND t.department_id = ?"
        params.append(department_id)

    if assigned_agent_id:
        sql += " AND t.assigned_agent_id = ?"
        params.append(assigned_agent_id)

    sql += " ORDER BY t.created_at DESC"

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    total = len(rows)
    offset = (page - 1) * limit
    paged = rows[offset: offset + limit]

    items = []
    facets_status = {}
    facets_priority = {}
    facets_category = {}

    for r in rows:
        facets_status[r["status"]] = facets_status.get(r["status"], 0) + 1
        facets_priority[r["priority"]] = facets_priority.get(r["priority"], 0) + 1
        facets_category[r["category"]] = facets_category.get(r["category"], 0) + 1

    for r in paged:
        items.append({
            "id": r["id"],
            "ticket_number": r["ticket_number"],
            "title": r["title"],
            "category": r["category"],
            "priority": r["priority"],
            "status": r["status"],
            "assigned_agent_id": r["assigned_agent_id"],
            "assigned_agent_name": r["agent_name"],
            "version": r["version"],
            "created_at": r["created_at"]
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "facets": {
            "by_status": facets_status,
            "by_priority": facets_priority,
            "by_category": facets_category
        }
    }


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(ticket_id: str, request: Request, response: Response):
    """Retrieve full ticket profile and metadata."""
    session = RLSEnforcer.extract_session_context(request)
    conn = get_db_connection()
    row = conn.execute(
        """SELECT t.*, a.name as agent_name
           FROM tickets t
           LEFT JOIN agents a ON t.assigned_agent_id = a.id
           WHERE t.id = ? OR t.ticket_number = ?""",
        (ticket_id, ticket_id)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_dict = dict(row)
    RLSEnforcer.enforce_ticket_access(session, ticket_dict)

    tags = json.loads(row["tags"]) if row["tags"] else []
    metadata = json.loads(row["metadata"]) if row["metadata"] else {}

    response.headers["ETag"] = f'W/"{row["version"]}"'

    return TicketResponse(
        id=row["id"],
        ticket_number=row["ticket_number"],
        title=row["title"],
        description=row["description"],
        category=row["category"],
        priority=row["priority"],
        status=row["status"],
        department_id=row["department_id"],
        requester_email=row["requester_email"],
        assigned_agent_id=row["assigned_agent_id"],
        assigned_agent_name=row["agent_name"],
        version=row["version"],
        sla_deadline_response=row["sla_deadline_response"],
        sla_deadline_resolution=row["sla_deadline_resolution"],
        tags=tags,
        metadata=metadata,
        resolution_notes=row["resolution_notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    req: TicketUpdateRequest,
    request: Request,
    response: Response,
    if_match: Optional[str] = Header(None, alias="If-Match")
):
    """Update ticket status and fields with optimistic concurrency locking."""
    session = RLSEnforcer.extract_session_context(request)
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")

    current_version = row["version"]

    # Resolve expected version from body or If-Match header
    expected_ver = req.expected_version
    if expected_ver is None and if_match:
        try:
            expected_ver = int(if_match.replace('W/"', '').replace('"', '').strip())
        except Exception:
            pass

    StateMachineEngine.verify_optimistic_lock(current_version, expected_ver)

    prev_status = row["status"]
    new_status = req.status.value if req.status else prev_status

    if req.status:
        StateMachineEngine.validate_transition(prev_status, new_status)

    new_priority = req.priority.value if req.priority else row["priority"]
    new_agent = req.assigned_agent_id if req.assigned_agent_id is not None else row["assigned_agent_id"]
    new_notes = req.resolution_notes if req.resolution_notes is not None else row["resolution_notes"]
    next_version = current_version + 1
    now_str = datetime.utcnow().isoformat()

    conn.execute(
        """UPDATE tickets
           SET status = ?, priority = ?, assigned_agent_id = ?, resolution_notes = ?,
               version = ?, updated_at = ?
           WHERE id = ?""",
        (new_status, new_priority, new_agent, new_notes, next_version, now_str, ticket_id)
    )
    conn.commit()
    conn.close()

    # Record Audit Mutation
    AuditEngine.record_mutation(
        ticket_id=ticket_id,
        actor_id=session.user_email,
        actor_role=session.role,
        action="TICKET_UPDATED",
        prev_state={"status": prev_status, "priority": row["priority"], "assigned_agent_id": row["assigned_agent_id"]},
        new_state={"status": new_status, "priority": new_priority, "assigned_agent_id": new_agent, "version": next_version}
    )

    response.headers["ETag"] = f'W/"{next_version}"'

    return get_ticket_detail(ticket_id, request, response)

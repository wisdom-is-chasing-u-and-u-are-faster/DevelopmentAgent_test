import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.db.init_db import get_connection
from app.models.ticket import (
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
    TicketListResponse
)
from app.models.agent import DispatchRequest, DispatchResponse
from app.services.idempotency import check_idempotency
from app.services.audit_engine import append_audit_event
from app.services.state_machine import transition_ticket_status
from app.services.routing_engine import dispatch_ticket
from app.services.search_service import search_and_filter_tickets

router = APIRouter(tags=["Tickets"])

PRIORITY_TARGETS = {
    "P1": 2.0,
    "P2": 4.0,
    "P3": 8.0,
    "P4": 24.0
}


@router.get("/tickets", response_model=TicketListResponse)
def list_tickets(
    q: Optional[str] = Query(None, description="Search term for title/desc/number"),
    status: Optional[str] = Query(None, description="Status filter"),
    priority: Optional[str] = Query(None, description="Priority filter"),
    department: Optional[str] = Query(None, description="Department filter"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    return search_and_filter_tickets(
        query=q, status=status, priority=priority, department=department, page=page, limit=limit
    )


@router.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate):
    existing = check_idempotency(payload.idempotency_key)
    if existing:
        return {
            "id": existing["id"],
            "ticket_number": existing["ticket_number"],
            "status": existing["status"],
            "priority": existing["priority"],
            "assigned_agent": existing["assigned_agent_name"],
            "version": existing["version"],
            "created_at": existing["created_at"],
            "idempotent_replay": True
        }

    ticket_id = f"tkt-{uuid.uuid4().hex[:8]}"
    prefix = "INC" if payload.priority in ["P1", "P2"] else "REQ"
    num_seq = uuid.uuid4().int % 9000 + 1000
    ticket_number = f"{prefix}-2026-{num_seq}"
    now_iso = datetime.now(timezone.utc).isoformat()
    sla_target = PRIORITY_TARGETS.get(payload.priority, 8.0)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO tickets (
                id, ticket_number, title, description, status, priority, department,
                category, requester_name, requester_email, sla_target_hours, sla_elapsed_hours,
                sla_status, version, idempotency_key, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'NEW', ?, ?, ?, ?, ?, ?, 0.0, 'WITHIN_SLA', 1, ?, ?, ?)
            """,
            (
                ticket_id, ticket_number, payload.title, payload.description,
                payload.priority, payload.department, payload.category,
                payload.requester_name, payload.requester_email, sla_target,
                payload.idempotency_key, now_iso, now_iso
            )
        )
        conn.commit()

        append_audit_event(
            entity_type="TICKET",
            entity_id=ticket_id,
            action="TICKET_INGESTION",
            actor=payload.requester_email,
            from_status=None,
            to_status="NEW",
            payload_data={
                "ticket_id": ticket_id,
                "ticket_number": ticket_number,
                "title": payload.title,
                "priority": payload.priority,
                "department": payload.department
            }
        )

        return {
            "id": ticket_id,
            "ticket_number": ticket_number,
            "status": "NEW",
            "priority": payload.priority,
            "assigned_agent": None,
            "version": 1,
            "created_at": now_iso
        }
    finally:
        conn.close()


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(ticket_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ? OR ticket_number = ?", (ticket_id, ticket_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

        tkt = dict(row)
        actual_id = tkt["id"]

        cur.execute(
            """
            SELECT timestamp, actor, action, from_status, to_status, current_hash
            FROM audit_ledger
            WHERE entity_id = ?
            ORDER BY rowid ASC
            """,
            (actual_id,)
        )
        history_rows = cur.fetchall()
        history = [
            {
                "timestamp": h["timestamp"],
                "actor": h["actor"],
                "action": h["action"],
                "from_status": h["from_status"],
                "to_status": h["to_status"],
                "hash": h["current_hash"]
            }
            for h in history_rows
        ]

        return {
            "id": tkt["id"],
            "ticket_number": tkt["ticket_number"],
            "title": tkt["title"],
            "description": tkt["description"],
            "status": tkt["status"],
            "priority": tkt["priority"],
            "department": tkt["department"],
            "category": tkt["category"],
            "requester_name": tkt["requester_name"],
            "requester_email": tkt["requester_email"],
            "assigned_agent": tkt["assigned_agent_name"],
            "sla_target_hours": tkt["sla_target_hours"],
            "sla_elapsed_hours": tkt["sla_elapsed_hours"],
            "sla_status": tkt["sla_status"],
            "version": tkt["version"],
            "created_at": tkt["created_at"],
            "updated_at": tkt["updated_at"],
            "history": history
        }
    finally:
        conn.close()


@router.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: str, payload: TicketStatusUpdate):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM tickets WHERE id = ? OR ticket_number = ?", (ticket_id, ticket_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
        actual_id = row["id"]
    finally:
        conn.close()

    return transition_ticket_status(
        ticket_id=actual_id,
        target_status=payload.status,
        actor=payload.actor,
        expected_version=payload.expected_version,
        comment=payload.comment or ""
    )


@router.post("/tickets/{ticket_id}/dispatch", response_model=DispatchResponse)
def dispatch_ticket_route(ticket_id: str, payload: Optional[DispatchRequest] = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM tickets WHERE id = ? OR ticket_number = ?", (ticket_id, ticket_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
        actual_id = row["id"]
    finally:
        conn.close()

    pref_id = payload.preferred_agent_id if payload else None
    return dispatch_ticket(actual_id, pref_id)

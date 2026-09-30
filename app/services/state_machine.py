from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException
from app.db.init_db import get_connection
from app.services.audit_engine import append_audit_event

VALID_TRANSITIONS = {
    "NEW": {"TRIAGED", "ASSIGNED"},
    "TRIAGED": {"ASSIGNED", "PENDING_CUSTOMER"},
    "ASSIGNED": {"IN_PROGRESS", "TRIAGED"},
    "IN_PROGRESS": {"PENDING_CUSTOMER", "RESOLVED", "TRIAGED"},
    "PENDING_CUSTOMER": {"IN_PROGRESS", "RESOLVED", "TRIAGED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS"},
    "CLOSED": set()
}


def transition_ticket_status(
    ticket_id: str,
    target_status: str,
    actor: str,
    expected_version: int,
    comment: str = ""
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

        current_ticket = dict(row)
        current_status = current_ticket["status"]
        current_version = current_ticket["version"]

        if current_version != expected_version:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Conflict: Ticket version mismatch (expected: {expected_version}, "
                    f"current: {current_version}). Please refresh and try again."
                )
            )

        allowed_next_states = VALID_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_next_states and target_status != current_status:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid transition from '{current_status}' to '{target_status}'. "
                    f"Allowed: {sorted(list(allowed_next_states))}"
                )
            )

        new_version = current_version + 1
        updated_at = datetime.now(timezone.utc).isoformat()

        cur.execute(
            """
            UPDATE tickets
            SET status = ?, version = ?, updated_at = ?
            WHERE id = ?
            """,
            (target_status, new_version, updated_at, ticket_id)
        )
        conn.commit()

        audit_res = append_audit_event(
            entity_type="TICKET",
            entity_id=ticket_id,
            action="STATUS_TRANSITION",
            actor=actor,
            from_status=current_status,
            to_status=target_status,
            payload_data={
                "ticket_id": ticket_id,
                "from_status": current_status,
                "to_status": target_status,
                "comment": comment,
                "version": new_version
            }
        )

        return {
            "id": ticket_id,
            "status": target_status,
            "version": new_version,
            "audit_hash": audit_res["current_hash"],
            "updated_at": updated_at
        }
    finally:
        conn.close()

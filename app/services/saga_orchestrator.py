"""
app/services/saga_orchestrator.py — Distributed Saga Orchestration Engine & Compensating Transactions
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from app.db.init_db import get_db_connection
from app.services.audit_service import AuditService


class SagaOrchestrator:
    STEPS = [
        "CONSENT",
        "OCR_SCAN",
        "PERSONAL_INFO",
        "BIOMETRIC_LIVENESS",
        "AML_SCREENING",
        "CBS_ACCOUNT_CREATION",
        "CARD_ISSUANCE",
    ]

    @classmethod
    def initialize_saga(cls, session_id: str, applicant_data: Dict[str, Any]) -> str:
        """Initializes a new Saga orchestration execution."""
        saga_id = f"saga_{uuid.uuid4().hex[:12]}"
        conn = get_db_connection()
        cursor = conn.cursor()

        payload_str = json.dumps(applicant_data)
        history_str = json.dumps(["CONSENT"])

        cursor.execute(
            """
            INSERT INTO saga_executions (saga_id, session_id, current_state, status, payload_json, step_history_json)
            VALUES (?, ?, 'CONSENT', 'IN_PROGRESS', ?, ?)
            """,
            (saga_id, session_id, payload_str, history_str),
        )
        conn.commit()
        conn.close()

        AuditService.record_event(
            action="SAGA_INITIALIZED",
            entity_id=session_id,
            actor="saga_orchestrator",
            payload={"saga_id": saga_id, "initial_step": "CONSENT"},
        )
        return saga_id

    @classmethod
    def transition_state(
        cls,
        session_id: str,
        new_step: str,
        step_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transitions saga to the next state, recording progress and history."""
        if step_data is None:
            step_data = {}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saga_executions WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
        saga = cursor.fetchone()

        if not saga:
            conn.close()
            return {"status": "SAGA_NOT_FOUND"}

        history = json.loads(saga["step_history_json"])
        if new_step not in history:
            history.append(new_step)

        payload = json.loads(saga["payload_json"])
        payload.update(step_data)

        saga_status = "COMPLETED" if new_step == "CARD_ISSUANCE" else "IN_PROGRESS"

        cursor.execute(
            """
            UPDATE saga_executions
            SET current_state = ?, status = ?, payload_json = ?, step_history_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
            """,
            (new_step, saga_status, json.dumps(payload), json.dumps(history), session_id),
        )

        cursor.execute(
            """
            UPDATE onboarding_sessions
            SET current_step = ?, status = ?
            WHERE session_id = ?
            """,
            (new_step, "COMPLETED" if saga_status == "COMPLETED" else "IN_PROGRESS", session_id),
        )

        conn.commit()
        conn.close()

        AuditService.record_event(
            action=f"SAGA_STEP_{new_step}",
            entity_id=session_id,
            actor="saga_orchestrator",
            payload={"new_step": new_step, "status": saga_status},
        )

        return {
            "session_id": session_id,
            "current_step": new_step,
            "saga_status": saga_status,
            "step_history": history,
        }

    @classmethod
    def get_progress(cls, session_id: str) -> Dict[str, Any]:
        """Calculates current saga pipeline progress and step status list."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saga_executions WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
        saga = cursor.fetchone()
        conn.close()

        if not saga:
            return {
                "session_id": session_id,
                "current_step": "UNKNOWN",
                "step_progress_pct": 0,
                "saga_state": "NOT_FOUND",
                "steps": [{"name": s, "status": "PENDING"} for s in cls.STEPS],
            }

        history = json.loads(saga["step_history_json"])
        current_state = saga["current_state"]
        saga_state = saga["status"]

        step_statuses = []
        for s in cls.STEPS:
            if s in history:
                step_statuses.append({"name": s, "status": "COMPLETED"})
            elif s == current_state:
                step_statuses.append({"name": s, "status": "IN_PROGRESS"})
            else:
                step_statuses.append({"name": s, "status": "PENDING"})

        pct = int((len(history) / len(cls.STEPS)) * 100)

        return {
            "session_id": session_id,
            "current_step": current_state,
            "step_progress_pct": pct,
            "saga_state": saga_state,
            "steps": step_statuses,
        }

    @classmethod
    def compensate_and_rollback(cls, session_id: str, failure_reason: str) -> Dict[str, Any]:
        """Executes compensating transactions to quarantine and rollback upstream state upon failure."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE onboarding_sessions
            SET status = 'ROLLED_BACK_QUARANTINED', current_step = 'COMPENSATED'
            WHERE session_id = ?
            """,
            (session_id,),
        )

        cursor.execute(
            """
            UPDATE accounts
            SET status = 'QUARANTINED', cbs_status = 'CANCELLED'
            WHERE application_id = (SELECT application_id FROM onboarding_sessions WHERE session_id = ?)
            """,
            (session_id,),
        )

        cursor.execute(
            """
            UPDATE saga_executions
            SET status = 'COMPENSATED_FAILED', updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
            """,
            (session_id,),
        )

        conn.commit()
        conn.close()

        AuditService.record_event(
            action="SAGA_COMPENSATING_ROLLBACK",
            entity_id=session_id,
            actor="saga_orchestrator",
            payload={"failure_reason": failure_reason, "compensation_status": "ROLLED_BACK"},
        )

        return {
            "session_id": session_id,
            "status": "ROLLED_BACK_QUARANTINED",
            "compensation_executed": True,
            "reason": failure_reason,
        }

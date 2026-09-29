"""
7-State Lifecycle State Machine with Optimistic Concurrency Locking
Enforces strict enterprise incident transition DAG and optimistic versioning.
"""

from typing import Set, Dict
from fastapi import HTTPException
from app.models.ticket import TicketStatus


class StateMachineEngine:
    # 7-State Transition Graph
    VALID_TRANSITIONS: Dict[str, Set[str]] = {
        TicketStatus.SUBMITTED.value: {TicketStatus.TRIAGED.value, TicketStatus.ASSIGNED.value, TicketStatus.CLOSED.value},
        TicketStatus.TRIAGED.value: {TicketStatus.ASSIGNED.value, TicketStatus.IN_PROGRESS.value, TicketStatus.CLOSED.value},
        TicketStatus.ASSIGNED.value: {TicketStatus.IN_PROGRESS.value, TicketStatus.PENDING_CUSTOMER.value, TicketStatus.TRIAGED.value},
        TicketStatus.IN_PROGRESS.value: {TicketStatus.PENDING_CUSTOMER.value, TicketStatus.RESOLVED.value, TicketStatus.ASSIGNED.value},
        TicketStatus.PENDING_CUSTOMER.value: {TicketStatus.IN_PROGRESS.value, TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value},
        TicketStatus.RESOLVED.value: {TicketStatus.CLOSED.value, TicketStatus.IN_PROGRESS.value},
        TicketStatus.CLOSED.value: set()  # Terminal state
    }

    @classmethod
    def validate_transition(cls, current_status: str, new_status: str) -> bool:
        """Validates if transitioning from current_status to new_status is allowed."""
        if current_status == new_status:
            return True

        allowed = cls.VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Illegal state transition from '{current_status}' to '{new_status}'. Allowed transitions: {sorted(list(allowed))}"
            )
        return True

    @staticmethod
    def verify_optimistic_lock(current_version: int, expected_version: int):
        """Verifies optimistic lock; raises HTTP 409 Conflict if version mismatch."""
        if expected_version is not None and expected_version != current_version:
            raise HTTPException(
                status_code=409,
                detail=f"Optimistic concurrency conflict: Current ticket version is {current_version}, but expected version was {expected_version}. Please refresh and retry."
            )
        return True

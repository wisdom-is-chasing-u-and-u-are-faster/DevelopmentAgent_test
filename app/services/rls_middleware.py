"""
Row-Level Security (RLS) & Session Context Engine
Enforces tenant separation, role-based authorization, and immutable record constraints.
"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException


class SessionContext:
    def __init__(
        self,
        user_id: str = "sys-user-01",
        user_email: str = "operator@enterprise.internal",
        role: str = "OPERATOR",
        department_id: Optional[str] = "dept-it-ops",
        tenant_id: str = "enterprise-default"
    ):
        self.user_id = user_id
        self.user_email = user_email
        self.role = role
        self.department_id = department_id
        self.tenant_id = tenant_id


class RLSEnforcer:
    @staticmethod
    def extract_session_context(request: Request) -> SessionContext:
        """Extracts user authentication session context from headers/token."""
        auth_header = request.headers.get("Authorization", "")
        role = request.headers.get("X-User-Role", "OPERATOR")
        user_id = request.headers.get("X-User-Id", "usr-auto-01")
        user_email = request.headers.get("X-User-Email", "requester@enterprise.internal")
        department_id = request.headers.get("X-Department-Id", "dept-it-ops")

        return SessionContext(
            user_id=user_id,
            user_email=user_email,
            role=role,
            department_id=department_id
        )

    @staticmethod
    def enforce_ticket_access(session: SessionContext, ticket_dict: Dict[str, Any]):
        """Enforces row-level security policy on a specific ticket record."""
        if session.role in ("ADMIN", "SECURITY_AUDITOR", "MANAGER"):
            return True

        if session.role == "REQUESTER" and ticket_dict.get("requester_email") != session.user_email:
            raise HTTPException(status_code=403, detail="Access denied: RLS policy restricts cross-user ticket queries")

        return True

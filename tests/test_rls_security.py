"""
Test Row-Level Security & Session Context (ARCH-1547, ARCH-1548)
"""

import pytest
from fastapi import HTTPException
from app.services.rls_middleware import RLSEnforcer, SessionContext


def test_requester_own_ticket_access():
    """Requester should access their own tickets without error."""
    session = SessionContext(
        user_id="usr-123",
        user_email="requester@enterprise.internal",
        role="REQUESTER"
    )
    ticket = {"requester_email": "requester@enterprise.internal"}
    assert RLSEnforcer.enforce_ticket_access(session, ticket) is True


def test_requester_cross_tenant_denial():
    """Requester should be blocked from viewing other users' tickets (403)."""
    session = SessionContext(
        user_id="usr-123",
        user_email="attacker@external.com",
        role="REQUESTER"
    )
    ticket = {"requester_email": "victim@enterprise.internal"}
    with pytest.raises(HTTPException) as exc_info:
        RLSEnforcer.enforce_ticket_access(session, ticket)
    assert exc_info.value.status_code == 403


def test_admin_manager_bypass():
    """Admin and managers should have cross-ticket inspection privileges."""
    session = SessionContext(role="ADMIN")
    ticket = {"requester_email": "anyone@enterprise.internal"}
    assert RLSEnforcer.enforce_ticket_access(session, ticket) is True

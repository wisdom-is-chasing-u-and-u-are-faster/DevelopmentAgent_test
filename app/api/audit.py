from fastapi import APIRouter
from pydantic import BaseModel
from app.db.init_db import get_connection
from app.models.audit import AuditLogListResponse
from app.services.audit_engine import fetch_audit_logs, verify_audit_chain_integrity

router = APIRouter(tags=["Audit & Settings"])


class UserSettingsPayload(BaseModel):
    slack_notifications: bool
    teams_notifications: bool
    email_notifications: bool
    theme: str


@router.get("/audit/logs", response_model=AuditLogListResponse)
def get_audit_logs(limit: int = 50):
    logs = fetch_audit_logs(limit=limit)
    return {"logs": logs}


@router.get("/audit/verify")
def verify_audit_integrity():
    is_valid = verify_audit_chain_integrity()
    msg = (
        "Audit ledger cryptographic integrity verified successfully."
        if is_valid
        else "Audit ledger chain integrity failed!"
    )
    return {
        "status": "VALID" if is_valid else "TAMPERED",
        "verified": is_valid,
        "message": msg
    }


@router.get("/user/settings")
def get_user_settings():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_settings WHERE user_id = 'default-user'")
        row = cur.fetchone()
        if not row:
            return {
                "user_id": "default-user",
                "name": "Prasanna Deshpande",
                "email": "prasanna_deshpande1@persistent.com",
                "role": "Operations Lead",
                "slack_notifications": True,
                "teams_notifications": True,
                "email_notifications": True,
                "theme": "light"
            }
        d = dict(row)
        return {
            "user_id": d["user_id"],
            "name": d["name"],
            "email": d["email"],
            "role": d["role"],
            "slack_notifications": bool(d["slack_notifications"]),
            "teams_notifications": bool(d["teams_notifications"]),
            "email_notifications": bool(d["email_notifications"]),
            "theme": d["theme"]
        }
    finally:
        conn.close()


@router.put("/user/settings")
def update_user_settings(payload: UserSettingsPayload):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE user_settings
            SET slack_notifications = ?, teams_notifications = ?,
                email_notifications = ?, theme = ?, updated_at = datetime('now')
            WHERE user_id = 'default-user'
            """,
            (
                int(payload.slack_notifications),
                int(payload.teams_notifications),
                int(payload.email_notifications),
                payload.theme
            )
        )
        conn.commit()
        return {"status": "success", "message": "Settings updated successfully."}
    finally:
        conn.close()

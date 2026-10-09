import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from app.db.init_db import get_connection
from app.models.audit import (
    AuditLogListResponse,
    SystemPresetUpdatePayload,
    SystemPresetsResponse,
    UserSettingsPayload,
    UserSettingsResponse
)
from app.services.audit_engine import fetch_audit_logs, verify_audit_chain_integrity, append_audit_event

router = APIRouter(tags=["Audit & Settings"])


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


# ============================================================================
# System Presets Endpoints (Global Admin Controls)
# ============================================================================

@router.get("/system/presets", response_model=SystemPresetsResponse)
def get_all_system_presets():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM system_presets")
        rows = cur.fetchall()
        presets = {}
        for r in rows:
            d = dict(r)
            try:
                cfg = json.loads(d["config_json"])
            except Exception:
                cfg = {}
            presets[d["category"]] = {
                "preset_key": d["preset_key"],
                "preset_name": d["preset_name"],
                "category": d["category"],
                "config": cfg,
                "updated_by": d["updated_by"],
                "updated_at": d["updated_at"]
            }
        return {"presets": presets}
    finally:
        conn.close()


@router.get("/system/presets/{category}")
def get_system_preset(category: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM system_presets WHERE category = ? OR preset_key = ?", (category, category))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"System preset for '{category}' not found.")
        d = dict(row)
        try:
            cfg = json.loads(d["config_json"])
        except Exception:
            cfg = {}
        return {
            "preset_key": d["preset_key"],
            "preset_name": d["preset_name"],
            "category": d["category"],
            "config": cfg,
            "updated_by": d["updated_by"],
            "updated_at": d["updated_at"]
        }
    finally:
        conn.close()


@router.put("/system/presets/{category}")
def update_system_preset(category: str, payload: SystemPresetUpdatePayload, apply_to_all: bool = Query(False)):
    conn = get_connection()
    now_iso = datetime.now(timezone.utc).isoformat()
    config_str = json.dumps(payload.config)
    preset_name = payload.preset_name or f"{category.capitalize()} Default Preset"
    should_apply = payload.apply_to_all or apply_to_all

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO system_presets (preset_key, preset_name, category, config_json, updated_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(preset_key) DO UPDATE SET
                preset_name = excluded.preset_name,
                config_json = excluded.config_json,
                updated_by = excluded.updated_by,
                updated_at = excluded.updated_at
            """,
            (category, preset_name, category, config_str, payload.actor, now_iso)
        )

        if should_apply:
            if category == "theme":
                th = payload.config.get("theme_mode", payload.config.get("theme", "dark"))
                color = payload.config.get("primary_color", "#3b82f6")
                slack = int(payload.config.get("slack_notifications", 1))
                teams = int(payload.config.get("teams_notifications", 1))
                email = int(payload.config.get("email_notifications", 1))
                cur.execute(
                    """
                    UPDATE user_settings
                    SET theme = ?, primary_color = ?, slack_notifications = ?,
                        teams_notifications = ?, email_notifications = ?, updated_at = ?
                    """,
                    (th, color, slack, teams, email, now_iso)
                )
            elif category == "worklist":
                cur.execute(
                    "UPDATE user_settings SET worklist_layout_json = ?, updated_at = ?",
                    (config_str, now_iso)
                )

        conn.commit()

        append_audit_event(
            entity_type="SYSTEM_PRESET",
            entity_id=category,
            action="PRESET_UPDATE_AND_PROPAGATE" if should_apply else "PRESET_UPDATE",
            actor=payload.actor,
            from_status=None,
            to_status="APPLIED_ALL" if should_apply else "SAVED",
            payload_data={
                "category": category,
                "preset_name": preset_name,
                "apply_to_all": should_apply,
                "config": payload.config
            }
        )

        return {
            "status": "success",
            "message": f"Preset '{preset_name}' saved successfully" + (" and propagated to all users." if should_apply else "."),
            "category": category,
            "applied_to_all": should_apply,
            "config": payload.config
        }
    finally:
        conn.close()


@router.post("/system/presets/{category}/apply-all")
def apply_preset_to_all_users(category: str, actor: str = Query("Global Admin")):
    conn = get_connection()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM system_presets WHERE category = ? OR preset_key = ?", (category, category))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"System preset '{category}' not found.")
        d = dict(row)
        cfg = json.loads(d["config_json"])

        if category == "theme":
            th = cfg.get("theme_mode", cfg.get("theme", "dark"))
            color = cfg.get("primary_color", "#3b82f6")
            slack = int(cfg.get("slack_notifications", 1))
            teams = int(cfg.get("teams_notifications", 1))
            email = int(cfg.get("email_notifications", 1))
            cur.execute(
                """
                UPDATE user_settings
                SET theme = ?, primary_color = ?, slack_notifications = ?,
                    teams_notifications = ?, email_notifications = ?, updated_at = ?
                """,
                (th, color, slack, teams, email, now_iso)
            )
        elif category == "worklist":
            cur.execute(
                "UPDATE user_settings SET worklist_layout_json = ?, updated_at = ?",
                (d["config_json"], now_iso)
            )
        conn.commit()

        append_audit_event(
            entity_type="SYSTEM_PRESET",
            entity_id=category,
            action="PRESET_APPLIED_ALL",
            actor=actor,
            from_status=None,
            to_status="PROPAGATED",
            payload_data={"category": category, "config": cfg}
        )

        return {
            "status": "success",
            "message": f"Global preset '{d['preset_name']}' transferred over to all users.",
            "category": category
        }
    finally:
        conn.close()


# ============================================================================
# User Settings Endpoints
# ============================================================================

@router.get("/user/settings", response_model=UserSettingsResponse)
def get_user_settings():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_settings WHERE user_id = 'default-user'")
        row = cur.fetchone()
        
        # Also fetch active system presets for fallback
        cur.execute("SELECT category, config_json FROM system_presets")
        preset_rows = cur.fetchall()
        system_presets = {}
        for pr in preset_rows:
            try:
                system_presets[pr["category"]] = json.loads(pr["config_json"])
            except Exception:
                pass

        if not row:
            theme_cfg = system_presets.get("theme", {})
            worklist_cfg = system_presets.get("worklist", None)
            return {
                "user_id": "default-user",
                "name": "Prasanna Deshpande",
                "email": "prasanna_deshpande1@persistent.com",
                "role": "Operations Lead",
                "is_global_admin": True,
                "slack_notifications": True,
                "teams_notifications": True,
                "email_notifications": True,
                "theme": theme_cfg.get("theme_mode", "light"),
                "primary_color": theme_cfg.get("primary_color", "#3b82f6"),
                "worklist_layout": worklist_cfg
            }

        d = dict(row)
        layout = None
        if d.get("worklist_layout_json"):
            try:
                layout = json.loads(d["worklist_layout_json"])
            except Exception:
                layout = None
        if not layout and "worklist" in system_presets:
            layout = system_presets["worklist"]

        role = d.get("role", "Operations Lead")
        is_admin = role in ["Operations Lead", "Global Admin", "Administrator", "Lead"]

        return {
            "user_id": d["user_id"],
            "name": d["name"],
            "email": d["email"],
            "role": role,
            "is_global_admin": is_admin,
            "slack_notifications": bool(d["slack_notifications"]),
            "teams_notifications": bool(d["teams_notifications"]),
            "email_notifications": bool(d["email_notifications"]),
            "theme": d.get("theme", "light"),
            "primary_color": d.get("primary_color", "#3b82f6"),
            "worklist_layout": layout
        }
    finally:
        conn.close()


@router.put("/user/settings")
def update_user_settings(payload: UserSettingsPayload):
    conn = get_connection()
    layout_str = json.dumps(payload.worklist_layout) if payload.worklist_layout else None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE user_settings
            SET slack_notifications = ?, teams_notifications = ?,
                email_notifications = ?, theme = ?, primary_color = ?,
                worklist_layout_json = COALESCE(?, worklist_layout_json),
                updated_at = datetime('now')
            WHERE user_id = 'default-user'
            """,
            (
                int(payload.slack_notifications),
                int(payload.teams_notifications),
                int(payload.email_notifications),
                payload.theme,
                payload.primary_color or "#3b82f6",
                layout_str
            )
        )
        conn.commit()
        return {"status": "success", "message": "Settings updated successfully."}
    finally:
        conn.close()


@router.post("/user/settings/reset-preset")
def reset_user_settings_to_preset():
    conn = get_connection()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        cur = conn.cursor()
        cur.execute("SELECT category, config_json FROM system_presets")
        preset_rows = cur.fetchall()
        system_presets = {}
        for pr in preset_rows:
            try:
                system_presets[pr["category"]] = json.loads(pr["config_json"])
            except Exception:
                pass

        theme_cfg = system_presets.get("theme", {})
        worklist_cfg = system_presets.get("worklist", {})

        th = theme_cfg.get("theme_mode", "dark")
        col = theme_cfg.get("primary_color", "#3b82f6")
        sl = int(theme_cfg.get("slack_notifications", 1))
        te = int(theme_cfg.get("teams_notifications", 1))
        em = int(theme_cfg.get("email_notifications", 1))
        wl_str = json.dumps(worklist_cfg) if worklist_cfg else None

        cur.execute(
            """
            UPDATE user_settings
            SET theme = ?, primary_color = ?, slack_notifications = ?,
                teams_notifications = ?, email_notifications = ?,
                worklist_layout_json = ?, updated_at = ?
            WHERE user_id = 'default-user'
            """,
            (th, col, sl, te, em, wl_str, now_iso)
        )
        conn.commit()
        return {
            "status": "success",
            "message": "User settings successfully reset to global admin presets.",
            "theme": th,
            "primary_color": col,
            "worklist_layout": worklist_cfg
        }
    finally:
        conn.close()

"""
Settings & UI Preset Service for ETMS
Manages Theme Color schemes, Worklist Layouts, and Global Admin transfers.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from app.db.init_db import get_db_connection
from app.models.settings import (
    UIPreset,
    PresetCreateRequest,
    PresetUpdateRequest,
    ActiveSettingsResponse,
    PresetType,
)


class SettingsService:
    @staticmethod
    def _row_to_preset(row) -> UIPreset:
        config = {}
        if row["config_json"]:
            try:
                config = json.loads(row["config_json"])
            except Exception:
                config = {}
        return UIPreset(
            id=row["id"],
            preset_type=row["preset_type"],
            name=row["name"],
            config=config,
            is_global_default=bool(row["is_global_default"]),
            created_by=row["created_by"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @classmethod
    def get_active_settings(cls) -> ActiveSettingsResponse:
        """Fetches active global default theme and worklist layout presets."""
        conn = get_db_connection()
        theme_row = conn.execute(
            """SELECT * FROM ui_presets
               WHERE preset_type = 'THEME_COLOR' AND is_global_default = 1
               ORDER BY updated_at DESC LIMIT 1"""
        ).fetchone()

        if not theme_row:
            theme_row = conn.execute(
                """SELECT * FROM ui_presets
                   WHERE preset_type = 'THEME_COLOR'
                   ORDER BY created_at ASC LIMIT 1"""
            ).fetchone()

        layout_row = conn.execute(
            """SELECT * FROM ui_presets
               WHERE preset_type = 'WORKLIST_LAYOUT' AND is_global_default = 1
               ORDER BY updated_at DESC LIMIT 1"""
        ).fetchone()

        if not layout_row:
            layout_row = conn.execute(
                """SELECT * FROM ui_presets
                   WHERE preset_type = 'WORKLIST_LAYOUT'
                   ORDER BY created_at ASC LIMIT 1"""
            ).fetchone()

        conn.close()

        theme_preset = cls._row_to_preset(theme_row) if theme_row else None
        layout_preset = cls._row_to_preset(layout_row) if layout_row else None

        return ActiveSettingsResponse(
            theme=theme_preset,
            worklist_layout=layout_preset
        )

    @classmethod
    def list_presets(cls, preset_type: Optional[str] = None) -> List[UIPreset]:
        """Lists presets optionally filtered by preset_type."""
        conn = get_db_connection()
        if preset_type:
            type_val = preset_type.value if hasattr(preset_type, "value") else str(preset_type)
            rows = conn.execute(
                """SELECT * FROM ui_presets
                   WHERE preset_type = ?
                   ORDER BY is_global_default DESC, name ASC""",
                (type_val,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM ui_presets
                   ORDER BY preset_type ASC, is_global_default DESC, name ASC"""
            ).fetchall()
        conn.close()

        return [cls._row_to_preset(r) for r in rows]

    @classmethod
    def get_preset_by_id(cls, preset_id: str) -> Optional[UIPreset]:
        """Retrieves a single preset by ID."""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM ui_presets WHERE id = ?", (preset_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return cls._row_to_preset(row)

    @classmethod
    def create_preset(cls, req: PresetCreateRequest, actor_id: str = "global-admin") -> UIPreset:
        """Creates a new preset. If is_global_default is True, sets as active global default."""
        conn = get_db_connection()
        preset_id = f"preset-{uuid.uuid4().hex[:12]}"
        type_val = req.preset_type.value if hasattr(req.preset_type, "value") else str(req.preset_type)
        now_str = datetime.utcnow().isoformat()
        is_global = 1 if req.is_global_default else 0

        if is_global:
            conn.execute(
                "UPDATE ui_presets SET is_global_default = 0 WHERE preset_type = ?",
                (type_val,)
            )

        config_str = json.dumps(req.config)

        conn.execute(
            """INSERT INTO ui_presets (id, preset_type, name, config_json, is_global_default, created_by, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (preset_id, type_val, req.name, config_str, is_global, actor_id, now_str, now_str)
        )
        conn.commit()
        conn.close()

        return UIPreset(
            id=preset_id,
            preset_type=type_val,
            name=req.name,
            config=req.config,
            is_global_default=bool(is_global),
            created_by=actor_id,
            created_at=now_str,
            updated_at=now_str
        )

    @classmethod
    def update_preset(cls, preset_id: str, req: PresetUpdateRequest, actor_id: str = "global-admin") -> UIPreset:
        """Updates preset details and optionally promotes as global default."""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM ui_presets WHERE id = ?", (preset_id,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

        current_type = row["preset_type"]
        new_name = req.name if req.name is not None else row["name"]
        new_config = req.config if req.config is not None else json.loads(row["config_json"])
        new_is_global = row["is_global_default"]

        if req.is_global_default is not None:
            new_is_global = 1 if req.is_global_default else 0
            if new_is_global:
                conn.execute(
                    "UPDATE ui_presets SET is_global_default = 0 WHERE preset_type = ?",
                    (current_type,)
                )

        now_str = datetime.utcnow().isoformat()
        config_str = json.dumps(new_config)

        conn.execute(
            """UPDATE ui_presets
               SET name = ?, config_json = ?, is_global_default = ?, updated_at = ?
               WHERE id = ?""",
            (new_name, config_str, new_is_global, now_str, preset_id)
        )
        conn.commit()
        conn.close()

        return UIPreset(
            id=preset_id,
            preset_type=current_type,
            name=new_name,
            config=new_config,
            is_global_default=bool(new_is_global),
            created_by=row["created_by"],
            created_at=row["created_at"],
            updated_at=now_str
        )

    @classmethod
    def apply_preset_as_global(cls, preset_id: str, actor_id: str = "global-admin") -> UIPreset:
        """Transfers and applies a preset as the active global default for all users."""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM ui_presets WHERE id = ?", (preset_id,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

        preset_type = row["preset_type"]
        now_str = datetime.utcnow().isoformat()

        # Unset all others for this preset type
        conn.execute(
            "UPDATE ui_presets SET is_global_default = 0, updated_at = ? WHERE preset_type = ?",
            (now_str, preset_type)
        )

        # Set target preset as global default
        conn.execute(
            "UPDATE ui_presets SET is_global_default = 1, updated_at = ? WHERE id = ?",
            (now_str, preset_id)
        )
        conn.commit()
        conn.close()

        config = json.loads(row["config_json"]) if row["config_json"] else {}
        return UIPreset(
            id=preset_id,
            preset_type=preset_type,
            name=row["name"],
            config=config,
            is_global_default=True,
            created_by=row["created_by"],
            created_at=row["created_at"],
            updated_at=now_str
        )

    @classmethod
    def delete_preset(cls, preset_id: str) -> bool:
        """Deletes a preset (cannot delete active global default if it's the only one)."""
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM ui_presets WHERE id = ?", (preset_id,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

        conn.execute("DELETE FROM ui_presets WHERE id = ?", (preset_id,))
        conn.commit()
        conn.close()
        return True

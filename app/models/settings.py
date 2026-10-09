"""
Domain Models for ETMS Global Settings & UI Presets
Supports Theme Colors, Worklist Layouts, and Organization-Wide Defaults
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PresetType(str, Enum):
    THEME_COLOR = "THEME_COLOR"
    WORKLIST_LAYOUT = "WORKLIST_LAYOUT"


class ThemeColorConfig(BaseModel):
    primary: str = "#3b82f6"
    primary_hover: Optional[str] = "#2563eb"
    bg_primary: str = "#0f172a"
    bg_secondary: str = "#1e293b"
    bg_card: str = "#334155"
    text_primary: str = "#f8fafc"
    text_muted: str = "#94a3b8"
    border: str = "#475569"
    success: Optional[str] = "#10b981"
    warning: Optional[str] = "#f59e0b"
    danger: Optional[str] = "#ef4444"


class WorklistLayoutConfig(BaseModel):
    visible_columns: List[str] = Field(
        default_factory=lambda: [
            "ticket_number",
            "title",
            "category",
            "priority",
            "status",
            "assigned_agent_name",
            "actions"
        ]
    )
    density: str = Field(default="normal", description="compact | normal | comfortable")
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page_size: int = 20
    show_quick_filters: bool = True


class UIPreset(BaseModel):
    id: str
    preset_type: str
    name: str
    config: Dict[str, Any]
    is_global_default: bool = False
    created_by: str = "global-admin"
    created_at: str
    updated_at: str


class PresetCreateRequest(BaseModel):
    preset_type: PresetType
    name: str = Field(..., min_length=2, max_length=128)
    config: Dict[str, Any]
    is_global_default: Optional[bool] = False


class PresetUpdateRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_global_default: Optional[bool] = None


class ActiveSettingsResponse(BaseModel):
    theme: Optional[UIPreset] = None
    worklist_layout: Optional[UIPreset] = None

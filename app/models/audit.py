from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AuditLogEntry(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    payload_checksum: str
    previous_hash: str
    current_hash: str
    timestamp: str


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogEntry]


class SystemPresetUpdatePayload(BaseModel):
    preset_name: Optional[str] = None
    config: Dict[str, Any]
    apply_to_all: Optional[bool] = False
    actor: Optional[str] = "Global Admin"


class SystemPresetsResponse(BaseModel):
    presets: Dict[str, Any]


class UserSettingsPayload(BaseModel):
    slack_notifications: bool
    teams_notifications: bool
    email_notifications: bool
    theme: str
    primary_color: Optional[str] = "#3b82f6"
    worklist_layout: Optional[Dict[str, Any]] = None


class UserSettingsResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    is_global_admin: bool
    slack_notifications: bool
    teams_notifications: bool
    email_notifications: bool
    theme: str
    primary_color: str
    worklist_layout: Optional[Dict[str, Any]] = None

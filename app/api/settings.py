"""
Settings & UI Presets API Router for ETMS
Provides global theme configuration, worklist layout customization, and admin transfer endpoints.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, status

from app.models.settings import (
    UIPreset,
    PresetCreateRequest,
    PresetUpdateRequest,
    ActiveSettingsResponse,
    PresetType,
)
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings & Presets"])


@router.get("/active", response_model=ActiveSettingsResponse)
def get_active_settings():
    """Retrieve current system-wide active theme and worklist layout presets."""
    return SettingsService.get_active_settings()


@router.get("/presets", response_model=Dict[str, Any])
def list_presets(preset_type: Optional[PresetType] = Query(None, description="Filter by THEME_COLOR or WORKLIST_LAYOUT")):
    """List available UI presets."""
    presets = SettingsService.list_presets(preset_type=preset_type)
    return {
        "presets": presets,
        "total": len(presets)
    }


@router.get("/presets/{preset_id}", response_model=UIPreset)
def get_preset(preset_id: str):
    """Retrieve details of a single preset by ID."""
    preset = SettingsService.get_preset_by_id(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")
    return preset


@router.post("/presets", response_model=UIPreset, status_code=status.HTTP_201_CREATED)
def create_preset(req: PresetCreateRequest):
    """Create a new theme color or worklist layout preset."""
    return SettingsService.create_preset(req)


@router.put("/presets/{preset_id}", response_model=UIPreset)
def update_preset(preset_id: str, req: PresetUpdateRequest):
    """Update preset configuration and metadata."""
    return SettingsService.update_preset(preset_id, req)


@router.post("/presets/{preset_id}/apply-global", response_model=Dict[str, Any])
def apply_preset_globally(preset_id: str):
    """Global Admin Action: Transfer and activate preset for ALL users across the organization."""
    updated = SettingsService.apply_preset_as_global(preset_id)
    return {
        "status": "SUCCESS",
        "message": f"Preset '{updated.name}' has been transferred and activated globally for all users.",
        "preset": updated
    }


@router.delete("/presets/{preset_id}", response_model=Dict[str, Any])
def delete_preset(preset_id: str):
    """Delete a UI preset."""
    SettingsService.delete_preset(preset_id)
    return {
        "status": "SUCCESS",
        "message": f"Preset {preset_id} deleted successfully."
    }

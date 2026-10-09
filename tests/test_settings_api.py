"""
Test Settings & UI Presets API (ARCH-1517: Global Theme & Worklist Layout Presets)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database(reset=True)


client = TestClient(app)


def test_get_active_settings():
    """Verify GET /api/v1/settings/active returns default active theme and layout presets."""
    res = client.get("/api/v1/settings/active")
    assert res.status_code == 200
    data = res.json()
    assert "theme" in data
    assert "worklist_layout" in data
    assert data["theme"] is not None
    assert data["theme"]["preset_type"] == "THEME_COLOR"
    assert "primary" in data["theme"]["config"]
    assert data["worklist_layout"] is not None
    assert data["worklist_layout"]["preset_type"] == "WORKLIST_LAYOUT"
    assert "visible_columns" in data["worklist_layout"]["config"]


def test_list_presets_and_filtering():
    """Verify listing presets and filtering by preset_type."""
    # List all
    res = client.get("/api/v1/settings/presets")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 4
    assert len(data["presets"]) >= 4

    # Filter by THEME_COLOR
    res_theme = client.get("/api/v1/settings/presets?preset_type=THEME_COLOR")
    assert res_theme.status_code == 200
    themes = res_theme.json()["presets"]
    assert all(t["preset_type"] == "THEME_COLOR" for t in themes)
    assert len(themes) >= 2

    # Filter by WORKLIST_LAYOUT
    res_layout = client.get("/api/v1/settings/presets?preset_type=WORKLIST_LAYOUT")
    assert res_layout.status_code == 200
    layouts = res_layout.json()["presets"]
    assert all(l["preset_type"] == "WORKLIST_LAYOUT" for l in layouts)
    assert len(layouts) >= 2


def test_create_and_apply_global_theme_preset():
    """Verify Global Admin can create and transfer/activate a new theme preset for all users."""
    payload = {
        "preset_type": "THEME_COLOR",
        "name": "Cyberpunk Neon Blue",
        "config": {
            "primary": "#00f0ff",
            "primary_hover": "#00c8d7",
            "bg_primary": "#05050d",
            "bg_secondary": "#0d0d1a",
            "bg_card": "#181829",
            "border": "#00f0ff",
            "text_primary": "#ffffff",
            "text_muted": "#8a8aa3"
        },
        "is_global_default": False
    }

    # 1. Create preset
    create_res = client.post("/api/v1/settings/presets", json=payload)
    assert create_res.status_code == 201
    preset_data = create_res.json()
    preset_id = preset_data["id"]
    assert preset_data["name"] == "Cyberpunk Neon Blue"
    assert preset_data["is_global_default"] is False

    # 2. Global Admin transfers & activates preset globally
    apply_res = client.post(f"/api/v1/settings/presets/{preset_id}/apply-global")
    assert apply_res.status_code == 200
    assert apply_res.json()["status"] == "SUCCESS"
    assert apply_res.json()["preset"]["is_global_default"] is True

    # 3. Active settings now reflects the newly transferred global theme preset
    active_res = client.get("/api/v1/settings/active")
    assert active_res.status_code == 200
    assert active_res.json()["theme"]["id"] == preset_id
    assert active_res.json()["theme"]["name"] == "Cyberpunk Neon Blue"
    assert active_res.json()["theme"]["config"]["primary"] == "#00f0ff"


def test_create_and_save_worklist_layout_preset_for_all():
    """Verify Global Admin can save a worklist layout setting for all users."""
    payload = {
        "preset_type": "WORKLIST_LAYOUT",
        "name": "Urgent Outage Triage Matrix",
        "config": {
            "visible_columns": ["ticket_number", "priority", "status", "sla_deadline_resolution", "actions"],
            "density": "compact",
            "sort_by": "sla_deadline_resolution",
            "sort_order": "asc",
            "page_size": 50,
            "show_quick_filters": True
        },
        "is_global_default": True
    }

    create_res = client.post("/api/v1/settings/presets", json=payload)
    assert create_res.status_code == 201
    layout_data = create_res.json()
    assert layout_data["is_global_default"] is True

    # Verify active layout is updated
    active_res = client.get("/api/v1/settings/active")
    assert active_res.status_code == 200
    assert active_res.json()["worklist_layout"]["name"] == "Urgent Outage Triage Matrix"
    assert active_res.json()["worklist_layout"]["config"]["density"] == "compact"
    assert len(active_res.json()["worklist_layout"]["config"]["visible_columns"]) == 5


def test_update_and_delete_preset():
    """Verify updating and deleting presets."""
    create_res = client.post("/api/v1/settings/presets", json={
        "preset_type": "THEME_COLOR",
        "name": "Temporary Theme",
        "config": {"primary": "#123456"}
    })
    preset_id = create_res.json()["id"]

    # Update
    update_res = client.put(f"/api/v1/settings/presets/{preset_id}", json={
        "name": "Updated Theme Name",
        "config": {"primary": "#654321"}
    })
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Theme Name"
    assert update_res.json()["config"]["primary"] == "#654321"

    # Delete
    del_res = client.delete(f"/api/v1/settings/presets/{preset_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "SUCCESS"

    # Verify 404 on get
    get_res = client.get(f"/api/v1/settings/presets/{preset_id}")
    assert get_res.status_code == 404

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_get_system_presets():
    res = client.get("/api/v1/system/presets")
    assert res.status_code == 200
    data = res.json()
    assert "presets" in data
    assert "theme" in data["presets"]
    assert "worklist" in data["presets"]
    assert data["presets"]["theme"]["config"]["primary_color"] is not None


def test_update_and_transfer_theme_color_preset():
    # Update global preset and transfer to all users
    payload = {
        "preset_name": "Emerald Cyber",
        "category": "theme",
        "apply_to_all": True,
        "actor": "Global Admin",
        "config": {
            "theme_mode": "dark",
            "primary_color": "#10b981",
            "slack_notifications": True,
            "teams_notifications": False,
            "email_notifications": True
        }
    }
    res = client.put("/api/v1/system/presets/theme", json=payload)
    assert res.status_code == 200
    assert res.json()["applied_to_all"] is True

    # Verify user profile inherited transferred preset
    user_res = client.get("/api/v1/user/settings")
    assert user_res.status_code == 200
    user_data = user_res.json()
    assert user_data["primary_color"] == "#10b981"
    assert user_data["teams_notifications"] is False


def test_update_and_transfer_worklist_layout_preset():
    custom_cols = ["ticket_number", "title", "priority", "sla_status", "actions"]
    payload = {
        "preset_name": "Compact Triage View",
        "category": "worklist",
        "apply_to_all": True,
        "actor": "Global Admin",
        "config": {
            "density": "compact",
            "page_size": 50,
            "sort_field": "priority",
            "sort_order": "asc",
            "columns": custom_cols
        }
    }
    res = client.put("/api/v1/system/presets/worklist", json=payload)
    assert res.status_code == 200

    # Verify user profile has updated worklist layout
    user_res = client.get("/api/v1/user/settings")
    assert user_res.status_code == 200
    user_data = user_res.json()
    assert user_data["worklist_layout"]["density"] == "compact"
    assert user_data["worklist_layout"]["page_size"] == 50
    assert user_data["worklist_layout"]["columns"] == custom_cols


def test_user_reset_to_global_preset():
    # Modify personal settings
    update_res = client.put("/api/v1/user/settings", json={
        "slack_notifications": False,
        "teams_notifications": False,
        "email_notifications": False,
        "theme": "light",
        "primary_color": "#ff0077"
    })
    assert update_res.status_code == 200

    # Verify personal override took effect
    check_res = client.get("/api/v1/user/settings")
    assert check_res.json()["primary_color"] == "#ff0077"

    # Reset back to global preset
    reset_res = client.post("/api/v1/user/settings/reset-preset")
    assert reset_res.status_code == 200

    # Verify restored to active preset
    final_res = client.get("/api/v1/user/settings")
    assert final_res.json()["primary_color"] != "#ff0077"


def test_apply_all_endpoint_and_audit():
    res = client.post("/api/v1/system/presets/theme/apply-all?actor=OpsLead")
    assert res.status_code == 200
    assert "transferred over" in res.json()["message"]

    audit_res = client.get("/api/v1/audit/logs?limit=5")
    assert audit_res.status_code == 200
    actions = [log["action"] for log in audit_res.json()["logs"]]
    assert "PRESET_APPLIED_ALL" in actions

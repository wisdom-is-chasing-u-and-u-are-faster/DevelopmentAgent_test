"""
Privacy settings, connected apps, and GDPR account deletion routes:
- GET  /api/v1/privacy/settings
- PUT  /api/v1/privacy/settings
- POST /api/v1/account/deletion
- GET  /api/v1/connected-apps
"""

from flask import Blueprint, request, jsonify
from app.models import repo
from app.services.gdpr import GDPRService

privacy_bp = Blueprint("privacy", __name__, url_prefix="/api/v1")

@privacy_bp.route("/privacy/settings", methods=["GET"])
def get_privacy_settings():
    user_id = int(request.args.get("user_id", 1))
    with repo._lock:
        settings = repo.privacy_settings.get(user_id)
        if not settings:
            settings = {
                "user_id": user_id,
                "mask_radius_meters": 500,
                "share_activities_publicly": True,
                "sensitive_locations": []
            }
        return jsonify(settings), 200

@privacy_bp.route("/privacy/settings", methods=["PUT"])
def update_privacy_settings():
    data = request.get_json(silent=True) or {}
    user_id = int(data.get("user_id", 1))

    with repo._lock:
        current = repo.privacy_settings.setdefault(user_id, {
            "user_id": user_id,
            "mask_radius_meters": 500,
            "share_activities_publicly": True,
            "sensitive_locations": []
        })
        if "mask_radius_meters" in data:
            current["mask_radius_meters"] = int(data["mask_radius_meters"])
        if "share_activities_publicly" in data:
            current["share_activities_publicly"] = bool(data["share_activities_publicly"])
        if "sensitive_locations" in data:
            current["sensitive_locations"] = data["sensitive_locations"]

    return jsonify({
        "status": "SUCCESS",
        "updated_at": "2026-06-10T14:30:00Z"
    }), 200

@privacy_bp.route("/account/deletion", methods=["POST"])
def delete_account():
    data = request.get_json(silent=True) or {}
    user_id = int(data.get("user_id", 1))
    confirm_email = data.get("confirm_email", "")
    reason = data.get("reason", "")

    res, status_code, err = GDPRService.execute_cascading_deletion(user_id, confirm_email, reason)
    if err:
        return jsonify({
            "type": "about:blank",
            "title": "Bad Request" if status_code == 400 else "Error",
            "status": status_code,
            "detail": err
        }), status_code

    return jsonify(res), 200

@privacy_bp.route("/connected-apps", methods=["GET"])
def list_connected_apps():
    with repo._lock:
        return jsonify({
            "providers": repo.connected_apps
        }), 200

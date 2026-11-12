"""
Telemetry ingestion and anti-cheat verification route:
- POST /api/v1/telemetry/ingest
"""

from flask import Blueprint, request, jsonify
from app.services.anti_cheat import AntiCheatService
from app.models import repo
from datetime import datetime

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/api/v1")

@telemetry_bp.route("/telemetry/ingest", methods=["POST"])
def ingest_telemetry():
    data = request.get_json(silent=True) or {}
    provider = data.get("provider", "Garmin Connect")
    user_id = data.get("user_id", "1")
    activity_type = data.get("activity_type", "running")
    points = data.get("telemetry_points", [])

    is_verified, reason = AntiCheatService.verify_telemetry(activity_type, points)

    if not is_verified:
        return jsonify({
            "type": "about:blank",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": f"Fraudulent or synthetic telemetry detected by anti-cheat engine: {reason}"
        }), 422

    submission_id = f"sub_{int(datetime.now().timestamp())}"
    return jsonify({
        "submission_id": submission_id,
        "status": "ACCEPTED",
        "verified": True,
        "quarantined": False
    }), 202

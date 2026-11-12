"""
Social feed and activity post routes matching api_contract.json:
- GET  /api/v1/social/feed
- POST /api/v1/social/posts
"""

from flask import Blueprint, request, jsonify
from app.models import repo
from app.services.privacy import PrivacyService

social_bp = Blueprint("social", __name__, url_prefix="/api/v1")

@social_bp.route("/social/feed", methods=["GET"])
def get_feed():
    with repo._lock:
        return jsonify({
            "activities": repo.social_posts,
            "total_count": len(repo.social_posts)
        }), 200

@social_bp.route("/social/posts", methods=["POST"])
def create_post():
    data = request.get_json(silent=True) or {}
    user_id = int(data.get("user_id", 1))
    title = data.get("activity_title") or "Morning Workout"
    distance = float(data.get("distance_km", 5.0))
    duration = int(data.get("duration_minutes", 30))
    raw_gps = data.get("gps_points") or []

    # Apply 500m residential geofence masking
    sensitive_zones = []
    with repo._lock:
        prof = repo.profiles.get(user_id, {})
        screen_name = prof.get("screen_name", "Athlete")
        avatar_url = prof.get("avatar_url", "")
        if user_id in repo.privacy_settings:
            sensitive_zones = repo.privacy_settings[user_id].get("sensitive_locations", [])

    masked_gps, masked_count = PrivacyService.mask_gps_track(raw_gps, sensitive_zones)

    new_post = {
        "post_id": f"post_{len(repo.social_posts) + 1}",
        "user_id": user_id,
        "screen_name": screen_name,
        "avatar_url": avatar_url,
        "activity_title": title,
        "distance_km": distance,
        "duration_minutes": duration,
        "masked_gps_points": masked_gps,
        "likes_count": 0,
        "created_at": "2026-06-10T14:00:00Z"
    }

    with repo._lock:
        repo.social_posts.insert(0, new_post)

    return jsonify({
        "post_id": new_post["post_id"],
        "activity_title": title,
        "masked_points_count": masked_count,
        "published_at": new_post["created_at"]
    }), 201

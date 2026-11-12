"""
User profile, badges, and admin user routes matching api_contract.json:
- GET /api/v1/users/profile
- GET /api/v1/badges
- GET /api/v1/admin/users
"""

from flask import Blueprint, request, jsonify
from app.models import repo
from app.services.streaks import StreakService

users_bp = Blueprint("users", __name__, url_prefix="/api/v1")

@users_bp.route("/users/profile", methods=["GET"])
def get_user_profile():
    user_id = int(request.args.get("user_id", 1))
    with repo._lock:
        profile = repo.profiles.get(user_id)
        if not profile:
            return jsonify({
                "type": "about:blank",
                "title": "Not Found",
                "status": 404,
                "detail": f"User profile for ID {user_id} not found"
            }), 404

        badges_count = len([b for b in repo.badges if b.get("unlocked")])
        res = dict(profile)
        res["badges_count"] = badges_count
        return jsonify(res), 200

@users_bp.route("/badges", methods=["GET"])
def list_badges():
    user_id = int(request.args.get("user_id", 1))
    with repo._lock:
        profile = repo.profiles.get(user_id, {})
        badges_eval = StreakService.evaluate_badges(profile, repo.badges)
        return jsonify({"badges": badges_eval}), 200

@users_bp.route("/admin/users", methods=["GET"])
def admin_list_users():
    with repo._lock:
        enriched_users = []
        for u in repo.users:
            u_copy = dict(u)
            prof = repo.profiles.get(u["id"], {})
            u_copy["screen_name"] = prof.get("screen_name", u["username"])
            u_copy["avatar_url"] = prof.get("avatar_url", "")
            enriched_users.append(u_copy)
        return jsonify({
            "users": enriched_users,
            "total_count": len(enriched_users)
        }), 200

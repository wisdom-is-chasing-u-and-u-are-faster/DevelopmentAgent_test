"""
Leaderboard routes matching api_contract.json:
- GET /api/v1/leaderboard
"""

from flask import Blueprint, request, jsonify
from app.services.leaderboard import LeaderboardService

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api/v1")

@leaderboard_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    challenge_id = int(request.args.get("challenge_id", 1))
    ranking_type = request.args.get("type", "global")
    current_user_id = int(request.args.get("user_id", 1))

    res = LeaderboardService.get_leaderboard(
        challenge_id=challenge_id,
        ranking_type=ranking_type,
        current_user_id=current_user_id
    )
    return jsonify(res), 200

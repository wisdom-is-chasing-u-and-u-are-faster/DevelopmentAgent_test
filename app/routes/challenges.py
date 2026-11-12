"""
Challenge routes matching api_contract.json:
- GET  /api/v1/challenges
- POST /api/v1/challenges
- GET  /api/v1/challenges/<id>
- POST /api/v1/challenges/<id>/enroll
- GET  /api/v1/admin/challenges
"""

from flask import Blueprint, request, jsonify
from app.services.challenges import ChallengeService
from app.models import repo

challenges_bp = Blueprint("challenges", __name__, url_prefix="/api/v1")

@challenges_bp.route("/challenges", methods=["GET"])
def list_challenges():
    sport = request.args.get("sport_type")
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    res = ChallengeService.get_challenges(sport_type=sport, status=status, page=page, page_size=page_size)
    return jsonify(res), 200

@challenges_bp.route("/challenges", methods=["POST"])
def create_challenge():
    data = request.get_json(silent=True) or {}
    if not data.get("title") or not data.get("sport_type"):
        return jsonify({
            "type": "about:blank",
            "title": "Bad Request",
            "status": 400,
            "detail": "Title and sport_type are required"
        }), 400

    new_c = ChallengeService.create_challenge(data)
    return jsonify(new_c), 201

@challenges_bp.route("/challenges/<int:challenge_id>", methods=["GET"])
def get_challenge(challenge_id):
    c = ChallengeService.get_challenge_by_id(challenge_id)
    if not c:
        return jsonify({
            "type": "about:blank",
            "title": "Not Found",
            "status": 404,
            "detail": f"Challenge with id {challenge_id} not found"
        }), 404
    return jsonify(c), 200

@challenges_bp.route("/challenges/<int:challenge_id>/enroll", methods=["POST"])
def enroll_challenge(challenge_id):
    data = request.get_json(silent=True) or {}
    user_id = int(data.get("user_id", 1))
    team_code = data.get("team_code")

    res, status_code, err = ChallengeService.enroll_participant(challenge_id, user_id, team_code)
    if err:
        return jsonify({
            "type": "about:blank",
            "title": "Conflict" if status_code == 409 else "Error",
            "status": status_code,
            "detail": err
        }), status_code

    return jsonify(res), 200

@challenges_bp.route("/admin/challenges", methods=["GET"])
def admin_list_challenges():
    with repo._lock:
        return jsonify({
            "challenges": repo.challenges,
            "total_count": len(repo.challenges)
        }), 200

"""
Comprehensive API integration test suite covering all 17 endpoints declared in api_contract.json.
Tests status codes, RFC 7807 error envelopes, challenge enrollment caps, and GDPR cascading erasure.
"""

import pytest
from app.main import create_app
from app.models import repo

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        repo.reset()
        yield client

def test_health(client):
    """GET /health returns 200 OK with container probe payload."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "version" in data

def test_list_challenges(client):
    """GET /api/v1/challenges returns challenge catalog with pagination."""
    res = client.get("/api/v1/challenges")
    assert res.status_code == 200
    data = res.get_json()
    assert "challenges" in data
    assert data["total_count"] >= 1
    assert len(data["challenges"]) > 0

def test_create_challenge(client):
    """POST /api/v1/challenges creates a new challenge."""
    payload = {
        "title": "Autumn Marathon 42K",
        "description": "Full 42.195 km marathon challenge.",
        "sport_type": "Running",
        "target_value": 42.195,
        "capacity_cap": 250
    }
    res = client.post("/api/v1/challenges", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == payload["title"]
    assert data["status"] == "UPCOMING"

def test_create_challenge_bad_request(client):
    """POST /api/v1/challenges returns RFC 7807 400 on missing title."""
    res = client.post("/api/v1/challenges", json={"description": "No title"})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == 400
    assert "detail" in data

def test_get_challenge_details(client):
    """GET /api/v1/challenges/<id> returns specific challenge specifications."""
    res = client.get("/api/v1/challenges/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == 1
    assert "title" in data

def test_get_challenge_not_found(client):
    """GET /api/v1/challenges/<id> returns RFC 7807 404 for non-existent challenge."""
    res = client.get("/api/v1/challenges/9999")
    assert res.status_code == 404
    data = res.get_json()
    assert data["status"] == 404

def test_enroll_challenge(client):
    """POST /api/v1/challenges/<id>/enroll enrolls user in challenge."""
    res = client.post("/api/v1/challenges/1/enroll", json={"user_id": 5})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ENROLLED"

def test_enroll_challenge_capacity_cap_conflict(client):
    """POST /api/v1/challenges/<id>/enroll returns 409 Conflict when capacity cap is reached."""
    # Find or set a challenge at capacity
    with repo._lock:
        repo.challenges[0]["capacity_cap"] = 10
        repo.challenges[0]["enrolled_count"] = 10

    res = client.post("/api/v1/challenges/1/enroll", json={"user_id": 99})
    assert res.status_code == 409
    data = res.get_json()
    assert data["status"] == 409
    assert "Cap Reached" in data["detail"]

def test_leaderboard_global(client):
    """GET /api/v1/leaderboard delivers global rankings with profile display metadata."""
    res = client.get("/api/v1/leaderboard?challenge_id=1&type=global")
    assert res.status_code == 200
    data = res.get_json()
    assert "rankings" in data
    assert "user_rank" in data
    if len(data["rankings"]) > 1:
        assert data["rankings"][0]["score_value"] >= data["rankings"][1]["score_value"]

def test_leaderboard_relative(client):
    """GET /api/v1/leaderboard?type=relative delivers user-centric +/- 5 ranks."""
    res = client.get("/api/v1/leaderboard?challenge_id=1&type=relative&user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "relative"

def test_social_feed(client):
    """GET /api/v1/social/feed delivers chronological social activities."""
    res = client.get("/api/v1/social/feed")
    assert res.status_code == 200
    data = res.get_json()
    assert "activities" in data
    assert data["total_count"] > 0

def test_create_social_post_with_geofence_masking(client):
    """POST /api/v1/social/posts publishes workout and masks GPS points within 500m of Home."""
    payload = {
        "user_id": 1,
        "activity_title": "Morning Run around Home",
        "distance_km": 5.2,
        "duration_minutes": 26,
        "gps_points": [
            {"lat": 40.712776, "lng": -74.005974}, # Exact home coordinate
            {"lat": 40.750000, "lng": -73.900000}  # Safe coordinate > 5km away
        ]
    }
    res = client.post("/api/v1/social/posts", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["masked_points_count"] >= 1

def test_user_profile(client):
    """GET /api/v1/users/profile returns athlete profile, streaks, and stats."""
    res = client.get("/api/v1/users/profile?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["screen_name"] == "Alex Rivers"
    assert "daily_streak" in data
    assert "badges_count" in data

def test_badges_list(client):
    """GET /api/v1/badges returns dynamic badges showcase."""
    res = client.get("/api/v1/badges?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert "badges" in data
    assert len(data["badges"]) >= 3

def test_privacy_settings(client):
    """GET and PUT /api/v1/privacy/settings updates sensitive location radius."""
    res = client.get("/api/v1/privacy/settings?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["mask_radius_meters"] == 500

    put_res = client.put("/api/v1/privacy/settings", json={"user_id": 1, "mask_radius_meters": 750})
    assert put_res.status_code == 200

def test_connected_apps(client):
    """GET /api/v1/connected-apps lists wearable providers."""
    res = client.get("/api/v1/connected-apps")
    assert res.status_code == 200
    data = res.get_json()
    assert "providers" in data

def test_account_deletion_gdpr(client):
    """POST /api/v1/account/deletion executes cascading GDPR erasure."""
    payload = {
        "user_id": 1,
        "confirm_email": "alex@example.com",
        "reason": "Exercising GDPR Right to be Forgotten"
    }
    res = client.post("/api/v1/account/deletion", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "COMPLETED"
    assert data["records_purged"] >= 1

def test_account_deletion_email_mismatch(client):
    """POST /api/v1/account/deletion returns 400 when email does not match user."""
    payload = {
        "user_id": 2,
        "confirm_email": "wrong_email@example.com"
    }
    res = client.post("/api/v1/account/deletion", json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == 400
    assert "Email confirmation" in data["detail"]

def test_admin_users(client):
    """GET /api/v1/admin/users lists platform users with RBAC roles."""
    res = client.get("/api/v1/admin/users")
    assert res.status_code == 200
    data = res.get_json()
    assert "users" in data

def test_admin_challenges(client):
    """GET /api/v1/admin/challenges lists administrative challenges."""
    res = client.get("/api/v1/admin/challenges")
    assert res.status_code == 200
    data = res.get_json()
    assert "challenges" in data

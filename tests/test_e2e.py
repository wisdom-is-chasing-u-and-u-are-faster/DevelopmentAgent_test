"""
End-to-end fullstack user journey test.
Validates the entire lifecycle: Health probe -> Challenge Discovery -> Enrollment
-> Ingestion -> Anti-Cheat -> Social Feed with Geofence Masking -> Leaderboard -> Profile -> GDPR Erasure.
"""

import pytest
from app.main import create_app
from app.models import repo

@pytest.fixture
def app_client():
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        repo.reset()
        yield client

def test_fullstack_e2e_lifecycle_journey(app_client):
    """Executes the complete end-to-end athlete journey across all platform tiers."""
    # 1. Health Probe
    res_health = app_client.get("/health")
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "ok"

    # 2. Challenge Discovery
    res_challenges = app_client.get("/api/v1/challenges?sport_type=Cycling")
    assert res_challenges.status_code == 200
    challenges = res_challenges.get_json()["challenges"]
    assert len(challenges) >= 1
    target_id = challenges[0]["id"]

    # 3. View Challenge Details
    res_details = app_client.get(f"/api/v1/challenges/{target_id}")
    assert res_details.status_code == 200
    assert res_details.get_json()["sport_type"] == "Cycling"

    # 4. Athlete Enrollment
    res_enroll = app_client.post(f"/api/v1/challenges/{target_id}/enroll", json={"user_id": 1})
    assert res_enroll.status_code == 200
    assert res_enroll.get_json()["status"] == "ENROLLED"

    # 5. Submit Verified Telemetry
    telemetry_payload = {
        "provider": "Apple HealthKit",
        "user_id": "1",
        "activity_type": "Cycling",
        "telemetry_points": [
            {"speed_mps": 8.5, "heart_rate": 140, "elevation": 50, "timestamp_epoch": 1000},
            {"speed_mps": 9.0, "heart_rate": 145, "elevation": 52, "timestamp_epoch": 1005}
        ]
    }
    res_ingest = app_client.post("/api/v1/telemetry/ingest", json=telemetry_payload)
    assert res_ingest.status_code == 202
    assert res_ingest.get_json()["verified"] is True

    # 6. Publish Workout to Social Feed with 500m Residential Masking
    social_payload = {
        "user_id": 1,
        "activity_title": "Coastal Century Leg 1",
        "distance_km": 25.0,
        "duration_minutes": 55,
        "gps_points": [
            {"lat": 40.712776, "lng": -74.005974}, # Residential Home coordinate
            {"lat": 40.850000, "lng": -73.950000}
        ]
    }
    res_post = app_client.post("/api/v1/social/posts", json=social_payload)
    assert res_post.status_code == 201
    assert res_post.get_json()["masked_points_count"] >= 1

    # 7. Check Leaderboard
    res_leaderboard = app_client.get(f"/api/v1/leaderboard?challenge_id={target_id}&type=global")
    assert res_leaderboard.status_code == 200
    leaderboard = res_leaderboard.get_json()
    assert len(leaderboard["rankings"]) > 0

    # 8. Check Athlete Profile & Streaks
    res_profile = app_client.get("/api/v1/users/profile?user_id=1")
    assert res_profile.status_code == 200
    profile = res_profile.get_json()
    assert profile["daily_streak"] >= 14

    # 9. Verify Privacy Settings Update
    res_priv = app_client.put("/api/v1/privacy/settings", json={"user_id": 1, "mask_radius_meters": 600})
    assert res_priv.status_code == 200

    # 10. GDPR Cascading Erasure Verification
    res_delete = app_client.post("/api/v1/account/deletion", json={
        "user_id": 1,
        "confirm_email": "alex@example.com",
        "reason": "Test lifecycle completion"
    })
    assert res_delete.status_code == 200
    assert res_delete.get_json()["status"] == "COMPLETED"

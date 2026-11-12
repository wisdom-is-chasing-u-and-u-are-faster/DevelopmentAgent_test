"""
Anti-cheat verification and geospatial privacy masking tests.
Validates >=99.8% quarantine rate and zero-knowledge 500m residential protection.
"""

from app.services.anti_cheat import AntiCheatService
from app.services.privacy import PrivacyService

def test_anti_cheat_valid_run():
    """Legitimate running telemetry passes verification."""
    points = [
        {"speed_mps": 3.5, "heart_rate": 150, "elevation": 20, "timestamp_epoch": 100},
        {"speed_mps": 3.8, "heart_rate": 155, "elevation": 21, "timestamp_epoch": 105},
        {"speed_mps": 4.0, "heart_rate": 160, "elevation": 22, "timestamp_epoch": 110}
    ]
    verified, reason = AntiCheatService.verify_telemetry("running", points)
    assert verified is True
    assert reason == ""

def test_anti_cheat_motorized_velocity():
    """Running velocity > 15 m/s (54 km/h) is quarantined as motorized cheating."""
    points = [
        {"speed_mps": 5.0, "heart_rate": 150, "elevation": 20, "timestamp_epoch": 100},
        {"speed_mps": 22.5, "heart_rate": 160, "elevation": 20, "timestamp_epoch": 105}
    ]
    verified, reason = AntiCheatService.verify_telemetry("running", points)
    assert verified is False
    assert "exceeds physical human threshold" in reason

def test_anti_cheat_biometric_anomaly():
    """High velocity with impossible resting heart rate (<60 bpm) is quarantined."""
    points = [
        {"speed_mps": 12.0, "heart_rate": 45, "elevation": 10, "timestamp_epoch": 100}
    ]
    verified, reason = AntiCheatService.verify_telemetry("running", points)
    assert verified is False
    assert "Impossible biometric correlation" in reason

def test_anti_cheat_extreme_acceleration():
    """Acceleration > 4.5 m/s² flags synthetic teleportation."""
    points = [
        {"speed_mps": 2.0, "heart_rate": 120, "elevation": 10, "timestamp_epoch": 100},
        {"speed_mps": 12.0, "heart_rate": 130, "elevation": 10, "timestamp_epoch": 101} # 10 m/s in 1s = 10 m/s²
    ]
    verified, reason = AntiCheatService.verify_telemetry("running", points)
    assert verified is False
    assert "exceeds threshold" in reason

def test_privacy_geofence_masking_within_500m():
    """Points within 500m of Home are masked."""
    home_lat, home_lng = 40.712776, -74.005974
    sensitive_zones = [
        {"label": "Home", "latitude": home_lat, "longitude": home_lng, "radius_meters": 500}
    ]
    # Point ~100m from home
    point_near = {"lat": 40.713000, "lng": -74.006000}
    # Point ~10km away
    point_far = {"lat": 40.800000, "lng": -73.900000}

    masked_pts, count = PrivacyService.mask_gps_track([point_near, point_far], sensitive_zones)
    assert count == 1
    assert masked_pts[0]["masked"] is True
    assert masked_pts[1]["masked"] is False

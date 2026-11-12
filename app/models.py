"""
Data models and repository access layer.
Maintains in-memory data seeded with realistic platform records,
with optional SQLite/PostgreSQL synchronization.
"""

import threading
from datetime import datetime

class DataRepository:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.users = [
                {"id": 1, "username": "alex_runner", "email": "alex@example.com", "role": "Athlete"},
                {"id": 2, "username": "sarah_cyclist", "email": "sarah@example.com", "role": "Athlete"},
                {"id": 3, "username": "mike_captain", "email": "mike@example.com", "role": "Team Captain"},
                {"id": 4, "username": "admin_rachel", "email": "admin@example.com", "role": "Challenge Admin"},
                {"id": 5, "username": "auditor_dave", "email": "auditor@example.com", "role": "Security Auditor"},
            ]
            self.profiles = {
                1: {"user_id": 1, "screen_name": "Alex Rivers", "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", "daily_streak": 14, "weekly_streak": 4, "total_workouts": 42, "points": 1250},
                2: {"user_id": 2, "screen_name": "Sarah Chen", "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150", "daily_streak": 21, "weekly_streak": 6, "total_workouts": 68, "points": 2100},
                3: {"user_id": 3, "screen_name": "Mike Ross", "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", "daily_streak": 7, "weekly_streak": 2, "total_workouts": 29, "points": 890},
                4: {"user_id": 4, "screen_name": "Rachel Zane", "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150", "daily_streak": 30, "weekly_streak": 8, "total_workouts": 95, "points": 3400},
                5: {"user_id": 5, "screen_name": "Dave Auditor", "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", "daily_streak": 5, "weekly_streak": 1, "total_workouts": 15, "points": 450},
            }
            self.challenges = [
                {
                    "id": 1,
                    "title": "Summer Century Ride",
                    "description": "Cycle 100 kilometers across 14 days and climb to the top of the regional leaderboard.",
                    "sport_type": "Cycling",
                    "goal_metric": "distance_km",
                    "target_value": 100.0,
                    "start_date": "2026-06-01T00:00:00Z",
                    "end_date": "2026-06-15T23:59:59Z",
                    "capacity_cap": 1000,
                    "enrolled_count": 342,
                    "is_team_based": False,
                    "status": "ACTIVE"
                },
                {
                    "id": 2,
                    "title": "Metropolitan 50K Run",
                    "description": "Complete 50 kilometers of verified running in urban parks and coastal greenways.",
                    "sport_type": "Running",
                    "goal_metric": "distance_km",
                    "target_value": 50.0,
                    "start_date": "2026-06-05T00:00:00Z",
                    "end_date": "2026-06-20T23:59:59Z",
                    "capacity_cap": 500,
                    "enrolled_count": 489,
                    "is_team_based": False,
                    "status": "ACTIVE"
                },
                {
                    "id": 3,
                    "title": "Corporate Team Elevation Cup",
                    "description": "Team challenge for climbing cumulative 10,000 meters elevation in hiking or trail running.",
                    "sport_type": "Trail Running",
                    "goal_metric": "elevation_m",
                    "target_value": 10000.0,
                    "start_date": "2026-07-01T00:00:00Z",
                    "end_date": "2026-07-31T23:59:59Z",
                    "capacity_cap": 100,
                    "enrolled_count": 18,
                    "is_team_based": True,
                    "status": "UPCOMING"
                },
                {
                    "id": 4,
                    "title": "Daily 10K Step Streak",
                    "description": "Maintain a consecutive 30-day streak of reaching 10,000 daily steps recorded via wearable.",
                    "sport_type": "Walking",
                    "goal_metric": "steps_count",
                    "target_value": 300000.0,
                    "start_date": "2026-05-01T00:00:00Z",
                    "end_date": "2026-05-31T23:59:59Z",
                    "capacity_cap": 2000,
                    "enrolled_count": 1850,
                    "is_team_based": False,
                    "status": "COMPLETED"
                }
            ]
            self.enrollments = [
                {"id": 1, "challenge_id": 1, "user_id": 1, "team_code": None, "progress_value": 64.5, "status": "ENROLLED"},
                {"id": 2, "challenge_id": 1, "user_id": 2, "team_code": None, "progress_value": 92.0, "status": "ENROLLED"},
                {"id": 3, "challenge_id": 2, "user_id": 1, "team_code": None, "progress_value": 48.2, "status": "ENROLLED"},
                {"id": 4, "challenge_id": 2, "user_id": 3, "team_code": None, "progress_value": 35.0, "status": "ENROLLED"},
            ]
            self.badges = [
                {"id": 1, "badge_key": "streak_7", "name": "7-Day Streak Warrior", "description": "Completed at least one verified workout daily for 7 consecutive days.", "icon": "🔥", "unlocked": True},
                {"id": 2, "badge_key": "century_rider", "name": "Century Club Cyclist", "description": "Clocked 100km total distance in cycling activities.", "icon": "🚴", "unlocked": True},
                {"id": 3, "badge_key": "elevation_goat", "name": "Mountain Goat", "description": "Conquered over 1,000 meters of cumulative elevation climb.", "icon": "⛰️", "unlocked": False},
                {"id": 4, "badge_key": "early_bird", "name": "Dawn Patrol Athlete", "description": "Finished 10 workouts logged before 7:00 AM local time.", "icon": "🌅", "unlocked": True},
            ]
            self.privacy_settings = {
                1: {
                    "user_id": 1,
                    "mask_radius_meters": 500,
                    "share_activities_publicly": True,
                    "sensitive_locations": [
                        {"id": 1, "label": "Home (Residential)", "latitude": 40.712776, "longitude": -74.005974, "radius": 500},
                        {"id": 2, "label": "Corporate HQ (Office)", "latitude": 40.758896, "longitude": -73.985130, "radius": 500}
                    ]
                }
            }
            self.social_posts = [
                {
                    "post_id": "post_1",
                    "user_id": 2,
                    "screen_name": "Sarah Chen",
                    "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150",
                    "activity_title": "Morning Coastal Ride - 35km",
                    "distance_km": 35.40,
                    "duration_minutes": 72,
                    "masked_gps_points": [{"lat": 37.78, "lng": -122.40}, {"lat": 37.80, "lng": -122.41}],
                    "likes_count": 24,
                    "created_at": "2026-06-10T09:30:00Z"
                },
                {
                    "post_id": "post_2",
                    "user_id": 1,
                    "screen_name": "Alex Rivers",
                    "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                    "activity_title": "Central Park Tempo Run",
                    "distance_km": 10.25,
                    "duration_minutes": 48,
                    "masked_gps_points": [{"lat": 40.78, "lng": -73.96}, {"lat": 40.80, "lng": -73.95}],
                    "likes_count": 18,
                    "created_at": "2026-06-10T11:15:00Z"
                }
            ]
            self.connected_apps = [
                {"provider": "Apple HealthKit", "connected": True, "last_sync": "2026-06-10T10:00:00Z", "icon": ""},
                {"provider": "Google Health Connect", "connected": True, "last_sync": "2026-06-10T09:45:00Z", "icon": "G"},
                {"provider": "Garmin Connect", "connected": True, "last_sync": "2026-06-10T08:30:00Z", "icon": "▲"},
                {"provider": "Strava", "connected": False, "last_sync": None, "icon": "⚡"}
            ]

repo = DataRepository()

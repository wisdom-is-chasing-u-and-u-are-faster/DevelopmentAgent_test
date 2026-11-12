-- SQL DML Seed Data
-- Enterprise Fitness Challenge Platform (ARCH-7452 / ARCH-7372)

INSERT INTO users (id, username, email, role) VALUES
    (1, 'alex_runner', 'alex@example.com', 'Athlete'),
    (2, 'sarah_cyclist', 'sarah@example.com', 'Athlete'),
    (3, 'mike_captain', 'mike@example.com', 'Team Captain'),
    (4, 'admin_rachel', 'admin@example.com', 'Challenge Admin'),
    (5, 'auditor_dave', 'auditor@example.com', 'Security Auditor')
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_profiles (id, user_id, screen_name, avatar_url, daily_streak, weekly_streak, total_workouts, points) VALUES
    (1, 1, 'Alex Rivers', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', 14, 4, 42, 1250),
    (2, 2, 'Sarah Chen', 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150', 21, 6, 68, 2100),
    (3, 3, 'Mike Ross', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150', 7, 2, 29, 890),
    (4, 4, 'Rachel Zane', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150', 30, 8, 95, 3400),
    (5, 5, 'Dave Auditor', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150', 5, 1, 15, 450)
ON CONFLICT (id) DO NOTHING;

INSERT INTO challenges (id, title, description, sport_type, goal_metric, target_value, start_date, end_date, capacity_cap, enrolled_count, is_team_based, status) VALUES
    (1, 'Summer Century Ride', 'Cycle 100 kilometers across 14 days and climb to the top of the regional leaderboard.', 'Cycling', 'distance_km', 100.0, '2026-06-01 00:00:00', '2026-06-15 23:59:59', 1000, 342, FALSE, 'ACTIVE'),
    (2, 'Metropolitan 50K Run', 'Complete 50 kilometers of verified running in urban parks and coastal greenways.', 'Running', 'distance_km', 50.0, '2026-06-05 00:00:00', '2026-06-20 23:59:59', 500, 489, FALSE, 'ACTIVE'),
    (3, 'Corporate Team Elevation Cup', 'Team challenge for climbing cumulative 10,000 meters elevation in hiking or trail running.', 'Trail Running', 'elevation_m', 10000.0, '2026-07-01 00:00:00', '2026-07-31 23:59:59', 100, 18, TRUE, 'UPCOMING'),
    (4, 'Daily 10K Step Streak', 'Maintain a consecutive 30-day streak of reaching 10,000 daily steps recorded via wearable.', 'Walking', 'steps_count', 300000.0, '2026-05-01 00:00:00', '2026-05-31 23:59:59', 2000, 1850, FALSE, 'COMPLETED')
ON CONFLICT (id) DO NOTHING;

INSERT INTO teams (id, name, team_code, captain_id) VALUES
    (1, 'Velocity Striders', 'TEAM-VELO', 3),
    (2, 'Summit Seekers', 'TEAM-PEAK', 1),
    (3, 'Urban Sprinters', 'TEAM-URBN', 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO challenge_enrollments (id, challenge_id, user_id, team_code, progress_value, status) VALUES
    (1, 1, 1, NULL, 64.5, 'ENROLLED'),
    (2, 1, 2, NULL, 92.0, 'ENROLLED'),
    (3, 2, 1, NULL, 48.2, 'ENROLLED'),
    (4, 2, 3, NULL, 35.0, 'ENROLLED'),
    (5, 3, 3, 'TEAM-VELO', 2500.0, 'ENROLLED')
ON CONFLICT (id) DO NOTHING;

INSERT INTO leaderboard (id, challenge_id, user_id, screen_name, avatar_url, rank_position, score_value, unit) VALUES
    (1, 1, 2, 'Sarah Chen', 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150', 1, 98.4, 'km'),
    (2, 1, 4, 'Rachel Zane', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150', 2, 85.2, 'km'),
    (3, 1, 1, 'Alex Rivers', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', 3, 64.5, 'km'),
    (4, 1, 3, 'Mike Ross', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150', 4, 45.0, 'km'),
    (5, 1, 5, 'Dave Auditor', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150', 5, 32.1, 'km')
ON CONFLICT (id) DO NOTHING;

INSERT INTO badges (id, badge_key, name, description, icon_url, required_metric, threshold_value) VALUES
    (1, 'streak_7', '7-Day Streak Warrior', 'Completed at least one verified workout daily for 7 consecutive days.', '🔥', 'streak_days', 7.0),
    (2, 'century_rider', 'Century Club Cyclist', 'Clocked 100km total distance in cycling activities.', '🚴', 'cycling_km', 100.0),
    (3, 'elevation_goat', 'Mountain Goat', 'Conquered over 1,000 meters of cumulative elevation climb.', '⛰️', 'elevation_m', 1000.0),
    (4, 'early_bird', 'Dawn Patrol Athlete', 'Finished 10 workouts logged before 7:00 AM local time.', '🌅', 'early_workouts', 10.0)
ON CONFLICT (id) DO NOTHING;

INSERT INTO user_badges (id, user_id, badge_id) VALUES
    (1, 1, 1),
    (2, 1, 2),
    (3, 2, 1),
    (4, 2, 2),
    (5, 2, 3),
    (6, 4, 1),
    (7, 4, 4)
ON CONFLICT (id) DO NOTHING;

INSERT INTO workout_streaks (id, user_id, last_activity_date, consecutive_days, consecutive_weeks, timezone) VALUES
    (1, 1, '2026-06-10', 14, 4, 'America/New_York'),
    (2, 2, '2026-06-10', 21, 6, 'America/Los_Angeles'),
    (3, 3, '2026-06-09', 7, 2, 'Europe/London'),
    (4, 4, '2026-06-10', 30, 8, 'Asia/Tokyo'),
    (5, 5, '2026-06-08', 5, 1, 'UTC')
ON CONFLICT (id) DO NOTHING;

INSERT INTO privacy_zones (id, user_id, label, latitude, longitude, radius_meters) VALUES
    (1, 1, 'Home (Residential)', 40.712776, -74.005974, 500),
    (2, 1, 'Corporate HQ (Office)', 40.758896, -73.985130, 500),
    (3, 2, 'Home Residence', 37.774929, -122.419418, 500)
ON CONFLICT (id) DO NOTHING;

INSERT INTO social_posts (id, user_id, screen_name, avatar_url, activity_title, distance_km, duration_minutes, masked_gps_points, likes_count) VALUES
    (1, 2, 'Sarah Chen', 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150', 'Morning Coastal Ride - 35km', 35.40, 72, '[{"lat": 37.78, "lng": -122.40}, {"lat": 37.80, "lng": -122.41}]', 24),
    (2, 1, 'Alex Rivers', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150', 'Central Park Tempo Run', 10.25, 48, '[{"lat": 40.78, "lng": -73.96}, {"lat": 40.80, "lng": -73.95}]', 18),
    (3, 4, 'Rachel Zane', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150', 'Weekend Trail Exploration', 18.50, 95, '[{"lat": 40.85, "lng": -73.90}, {"lat": 40.88, "lng": -73.88}]', 32)
ON CONFLICT (id) DO NOTHING;

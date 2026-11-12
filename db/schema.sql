-- PostgreSQL 16 / ANSI SQL DDL Schema Definition
-- Enterprise Fitness Challenge Platform (ARCH-7452 / ARCH-7372)

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) DEFAULT 'Athlete',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    screen_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    daily_streak INTEGER DEFAULT 0,
    weekly_streak INTEGER DEFAULT 0,
    total_workouts INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sport_type VARCHAR(100) NOT NULL,
    goal_metric VARCHAR(100) DEFAULT 'distance_km',
    target_value NUMERIC(12, 4) DEFAULT 100.0,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    capacity_cap INTEGER DEFAULT 1000,
    enrolled_count INTEGER DEFAULT 0,
    is_team_based BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team_code VARCHAR(50) UNIQUE,
    captain_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenge_enrollments (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    team_code VARCHAR(50),
    progress_value NUMERIC(12, 4) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'ENROLLED',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    screen_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    rank_position INTEGER DEFAULT 1,
    score_value NUMERIC(12, 4) DEFAULT 0.0,
    unit VARCHAR(50) DEFAULT 'km',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    badge_key VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    required_metric VARCHAR(100),
    threshold_value NUMERIC(12, 4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workout_streaks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    last_activity_date DATE NOT NULL,
    consecutive_days INTEGER DEFAULT 1,
    consecutive_weeks INTEGER DEFAULT 1,
    timezone VARCHAR(50) DEFAULT 'UTC',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS privacy_zones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    label VARCHAR(100) NOT NULL,
    latitude NUMERIC(10, 6) NOT NULL,
    longitude NUMERIC(10, 6) NOT NULL,
    radius_meters INTEGER DEFAULT 500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    screen_name VARCHAR(100),
    avatar_url VARCHAR(500),
    activity_title VARCHAR(255) NOT NULL,
    distance_km NUMERIC(10, 2) DEFAULT 0.0,
    duration_minutes INTEGER DEFAULT 0,
    masked_gps_points TEXT,
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    activity_type VARCHAR(50),
    raw_points_count INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT TRUE,
    quarantined BOOLEAN DEFAULT FALSE,
    fraud_reason VARCHAR(255),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS account_deletions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    confirm_email VARCHAR(255) NOT NULL,
    reason TEXT,
    records_purged INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

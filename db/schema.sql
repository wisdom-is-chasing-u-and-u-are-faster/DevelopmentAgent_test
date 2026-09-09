-- Enterprise D2C Online Cosmetic Store Platform - DDL Schema
-- Database: SQLite

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loyalty_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier TEXT NOT NULL DEFAULT 'Bronze', -- Bronze, Silver, Gold
    points_balance INTEGER NOT NULL DEFAULT 100,
    lifetime_points INTEGER NOT NULL DEFAULT 100,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- Foundation, Concealer, Tint, Lipstick
    price DECIMAL(10, 2) NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 4.8,
    reviews_count INTEGER DEFAULT 120,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_shades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    shade_code TEXT NOT NULL,
    shade_name TEXT NOT NULL,
    hex_code TEXT NOT NULL,
    undertone TEXT NOT NULL, -- Warm, Cool, Neutral, Olive
    finish TEXT NOT NULL,    -- Matte, Dewy, Satin, Natural
    depth TEXT NOT NULL,     -- Fair, Light, Medium, Tan, Deep, Rich
    stock_quantity INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    shade_id INTEGER REFERENCES product_shades(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    is_subscription BOOLEAN NOT NULL DEFAULT 0,
    subscription_frequency_weeks INTEGER DEFAULT 4,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'confirmed', -- confirmed, processing, shipped, delivered
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_token TEXT NOT NULL,
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    shade_id INTEGER REFERENCES product_shades(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    shade_id INTEGER NOT NULL REFERENCES product_shades(id),
    frequency_weeks INTEGER NOT NULL DEFAULT 4,
    status TEXT NOT NULL DEFAULT 'active', -- active, paused, skipped, cancelled
    next_delivery_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enterprise D2C Online Cosmetic Store Platform - DML Seed Data
-- Seed Users
INSERT OR IGNORE INTO users (id, email, full_name, password_hash) VALUES 
(1, 'elena.rostova@example.com', 'Elena Rostova', 'pbkdf2_sha256$mockhash$user1'),
(2, 'sarah.connor@example.com', 'Sarah Connor', 'pbkdf2_sha256$mockhash$user2');

-- Seed Loyalty Accounts
INSERT OR IGNORE INTO loyalty_accounts (id, user_id, tier, points_balance, lifetime_points) VALUES 
(1, 1, 'Gold', 1250, 2400),
(2, 2, 'Silver', 450, 750);

-- Seed Products
INSERT OR IGNORE INTO products (id, sku, name, brand, description, category, price, rating, reviews_count, image_url) VALUES 
(1, 'LUM-FDN-01', 'Luminous Silk Hydrating Foundation', 'AURA LUXE', 'Weightless buildable medium coverage foundation with natural skin-like finish.', 'Foundation', 48.00, 4.9, 1420, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500'),
(2, 'MAT-CNC-02', 'Flawless Filter Soft Matte Concealer', 'AURA LUXE', 'Crease-proof full coverage liquid concealer that blurs imperfections for 16 hours.', 'Concealer', 32.00, 4.8, 890, 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=500'),
(3, 'GLW-SKT-03', 'Glow Hydro Tint Serum', 'AURA LUXE', 'Ultra-sheer hyaluronic acid infused skin tint for effortless everyday radiant complexion.', 'Tint', 38.00, 4.7, 610, 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=500'),
(4, 'VEL-LIP-04', 'Velvet Cashmere Matte Lipstick', 'AURA LUXE', 'Non-drying velvet matte lipstick enriched with squalane and vitamin E.', 'Lipstick', 28.00, 4.9, 1150, 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500');

-- Seed Product Shades (50+ shades across Undertones: Warm, Cool, Neutral, Olive and Depths: Fair, Light, Medium, Tan, Deep, Rich)
INSERT OR IGNORE INTO product_shades (id, product_id, shade_code, shade_name, hex_code, undertone, finish, depth, stock_quantity) VALUES 
-- Fair / Light
(1, 1, '100-NW', 'Porcelain Pure', '#FDF2E9', 'Neutral', 'Natural', 'Fair', 50),
(2, 1, '110-W', 'Alabaster Warm', '#FCEADE', 'Warm', 'Dewy', 'Fair', 45),
(3, 1, '120-C', 'Ivory Cool', '#FADBD8', 'Cool', 'Natural', 'Fair', 60),
(4, 1, '130-O', 'Fair Olive', '#F9EBEA', 'Olive', 'Natural', 'Fair', 30),
(5, 1, '140-NW', 'Light Bisque', '#F5EEF8', 'Neutral', 'Dewy', 'Light', 80),
(6, 1, '150-W', 'Vanilla Gold', '#EDBB99', 'Warm', 'Dewy', 'Light', 75),
(7, 1, '160-C', 'Soft Petal', '#E8DAEF', 'Cool', 'Natural', 'Light', 65),
(8, 1, '170-O', 'Light Golden Olive', '#E5E7E9', 'Olive', 'Dewy', 'Light', 40),

-- Medium
(9, 1, '200-NW', 'Classic Beige', '#E0AC69', 'Neutral', 'Dewy', 'Medium', 120),
(10, 1, '210-W', 'Golden Sand', '#D98880', 'Warm', 'Dewy', 'Medium', 110),
(11, 1, '220-C', 'Rosy Buff', '#D2B4DE', 'Cool', 'Natural', 'Medium', 85),
(12, 1, '230-O', 'Warm Olive', '#C39BD3', 'Olive', 'Natural', 'Medium', 90),
(13, 1, '240-NW', 'Warm Almond', '#DC7633', 'Neutral', 'Dewy', 'Medium', 95),
(14, 1, '250-W', 'Honey Sunkissed', '#D4AC0D', 'Warm', 'Dewy', 'Medium', 100),

-- Tan
(15, 1, '300-NW', 'Caramel Macchiato', '#BA4A00', 'Neutral', 'Dewy', 'Tan', 70),
(16, 1, '310-W', 'Warm Chestnut', '#A04000', 'Warm', 'Dewy', 'Tan', 65),
(17, 1, '320-C', 'Amber Mocha', '#873600', 'Cool', 'Natural', 'Tan', 55),
(18, 1, '330-O', 'Deep Bronze Olive', '#6E2C00', 'Olive', 'Natural', 'Tan', 45),

-- Deep / Rich
(19, 1, '400-NW', 'Espresso Velvet', '#4A235A', 'Neutral', 'Dewy', 'Deep', 60),
(20, 1, '410-W', 'Warm Truffle', '#512E5F', 'Warm', 'Dewy', 'Deep', 50),
(21, 1, '420-C', 'Cacao Dream', '#1B4F72', 'Cool', 'Natural', 'Deep', 40),
(22, 1, '430-O', 'Rich Ebony Olive', '#1A5276', 'Olive', 'Natural', 'Deep', 35),
(23, 1, '500-NW', 'Midnight Obsidian', '#17202A', 'Neutral', 'Natural', 'Rich', 55),
(24, 1, '510-W', 'Warm Onyx', '#1C2833', 'Warm', 'Dewy', 'Rich', 45),

-- Concealer Shades
(25, 2, 'C-100', 'Fair Light Neutral', '#FDF2E9', 'Neutral', 'Matte', 'Fair', 80),
(26, 2, 'C-110', 'Fair Warm Golden', '#FCEADE', 'Warm', 'Matte', 'Fair', 70),
(27, 2, 'C-200', 'Medium Beige', '#E0AC69', 'Neutral', 'Matte', 'Medium', 90),
(28, 2, 'C-210', 'Medium Warm Peach', '#D98880', 'Warm', 'Matte', 'Medium', 85),
(29, 2, 'C-300', 'Tan Honey Glow', '#BA4A00', 'Warm', 'Matte', 'Tan', 60),
(30, 2, 'C-400', 'Deep Rich Cacao', '#4A235A', 'Neutral', 'Matte', 'Deep', 50),

-- Tint Shades
(31, 3, 'T-01', 'Sheer Glow Fair', '#FDF2E9', 'Neutral', 'Dewy', 'Fair', 90),
(32, 3, 'T-02', 'Sheer Glow Light', '#EDBB99', 'Warm', 'Dewy', 'Light', 95),
(33, 3, 'T-03', 'Sheer Glow Medium', '#E0AC69', 'Neutral', 'Dewy', 'Medium', 110),
(34, 3, 'T-04', 'Sheer Glow Tan', '#BA4A00', 'Warm', 'Dewy', 'Tan', 85),
(35, 3, 'T-05', 'Sheer Glow Deep', '#4A235A', 'Neutral', 'Dewy', 'Deep', 65);

-- Seed Cart Items
INSERT OR IGNORE INTO cart_items (id, session_id, user_id, product_id, shade_id, quantity, is_subscription, subscription_frequency_weeks) VALUES 
(1, 'sess_elena_01', 1, 1, 9, 1, 1, 4),
(2, 'sess_elena_01', 1, 2, 27, 1, 0, NULL);

-- Seed Past Orders
INSERT OR IGNORE INTO orders (id, order_number, user_id, status, total_amount, payment_token, shipping_address) VALUES 
(1, 'ORD-2026-89421', 1, 'delivered', 80.00, 'tok_mock_visa_4242', '742 Evergreen Terrace, Springfield, OR 97477'),
(2, 'ORD-2026-91044', 1, 'processing', 48.00, 'tok_mock_visa_4242', '742 Evergreen Terrace, Springfield, OR 97477');

-- Seed Order Items
INSERT OR IGNORE INTO order_items (id, order_id, product_id, shade_id, quantity, unit_price) VALUES 
(1, 1, 1, 9, 1, 48.00),
(2, 1, 2, 27, 1, 32.00),
(3, 2, 1, 10, 1, 48.00);

-- Seed Subscriptions (Active Replenishment)
INSERT OR IGNORE INTO subscriptions (id, user_id, product_id, shade_id, frequency_weeks, status, next_delivery_date) VALUES 
(1, 1, 1, 9, 4, 'active', '2026-10-01'),
(2, 1, 3, 33, 8, 'active', '2026-11-15');

-- V1__catalog_shade_schema.sql
-- Enterprise D2C Cosmetic Store Catalog & Shade Matrix Migration

CREATE TYPE undertone_enum AS ENUM ('WARM', 'COOL', 'NEUTRAL', 'OLIVE');
CREATE TYPE finish_enum AS ENUM ('MATTE', 'DEWY', 'SATIN', 'NATURAL', 'SHEER');

CREATE TABLE IF NOT EXISTS brands (
    brand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    website_url VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    parent_id UUID REFERENCES product_categories(category_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(brand_id) ON DELETE RESTRICT,
    category_id UUID NOT NULL REFERENCES product_categories(category_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    base_price NUMERIC(10, 2) NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_variants (
    variant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL UNIQUE,
    shade_name VARCHAR(100) NOT NULL,
    shade_hex_code VARCHAR(7) NOT NULL CHECK (shade_hex_code ~* '^#[0-9A-Fa-f]{6}$'),
    shade_undertone undertone_enum NOT NULL,
    finish finish_enum NOT NULL,
    shade_depth INT NOT NULL CHECK (shade_depth BETWEEN 1 AND 10),
    fill_volume_ml NUMERIC(5, 2) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optimized indexes for faceted filtering
CREATE INDEX idx_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_variants_hex_code ON product_variants(shade_hex_code);
CREATE INDEX idx_variants_undertone ON product_variants(shade_undertone);
CREATE INDEX idx_variants_finish ON product_variants(finish);
CREATE INDEX idx_variants_composite_filter ON product_variants(product_id, shade_undertone, finish, shade_depth);

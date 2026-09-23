-- U1__catalog_shade_schema.sql
-- Rollback for V1__catalog_shade_schema.sql

DROP TABLE IF EXISTS product_variants CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

DROP TYPE IF EXISTS finish_enum;
DROP TYPE IF EXISTS undertone_enum;

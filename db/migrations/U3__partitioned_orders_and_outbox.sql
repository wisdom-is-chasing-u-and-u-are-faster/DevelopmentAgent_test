-- U3__partitioned_orders_and_outbox.sql
-- Rollback for V3__partitioned_orders_and_outbox.sql

DROP TABLE IF EXISTS transactional_outbox CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;

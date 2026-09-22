-- U4__customer_subscriptions.sql
-- Rollback for V4__customer_subscriptions.sql

DROP TABLE IF EXISTS customer_subscriptions CASCADE;
DROP TYPE IF EXISTS subscription_status_enum;

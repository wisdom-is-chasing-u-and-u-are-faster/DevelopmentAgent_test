# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **[ARCH-1087]** Execute Distributed High-Concurrency Load Testing (50k VUs) with k6
  - *Key modifications:*
    - `tests/load/flash_sale_surge.js`
    - `reports/k6_flash_drop_results.json`
### Added
- **[ARCH-1093]** Automate Subscription Lifecycle Testing and Stripe Test Clock Integration
  - *Key modifications:*
    - `tests/integration/subscription_clock_test.go`
    - `tests/e2e/subscription_portal.spec.ts`
### Added
- **[ARCH-1088]** Implement End-to-End Test Suite and Contract Testing for Catalog Domain
  - *Key modifications:*
    - `tests/contract/catalog_pact_test.go`
    - `tests/e2e/shade_finder.spec.ts`
    - `tests/load/catalog_stress.js`
### Added
- **[ARCH-1096]** Implement Stripe Elements Hosted Checkout and 1-Click Pay UI in Next.js
  - *Key modifications:*
    - `storefront/src/types/checkout.ts`
    - `storefront/src/app/checkout/page.tsx`
    - `storefront/src/components/checkout/StripeElementsWrapper.tsx`
    - `storefront/src/components/checkout/DigitalWalletButton.tsx`
### Added
- **[ARCH-1092]** Develop Customer Subscription & Regimen Management Portal UI in Next.js
  - *Key modifications:*
    - `storefront/src/types/subscription.ts`
    - `storefront/src/app/account/subscriptions/page.tsx`
    - `storefront/src/components/account/SubscriptionCard.tsx`
    - `storefront/src/components/account/SwapShadeModal.tsx`
### Added
- **[ARCH-1090]** Build High-Concurrency Slide Cart and 10-Minute Countdown Timer in Storefront
  - *Key modifications:*
    - `storefront/src/types/cart.ts`
    - `storefront/src/components/cart/SlideCartDrawer.tsx`
    - `storefront/src/components/cart/ReservationCountdown.tsx`
    - `storefront/src/hooks/useCartReservation.ts`
### Added
- **[ARCH-1085]** Implement Faceted Shade Selector and Camera AR Matcher UI in Next.js 19
  - *Key modifications:*
    - `storefront/package.json`
    - `storefront/tsconfig.json`
    - `storefront/src/types/catalog.ts`
    - `storefront/src/components/pdp/ShadeSwatchGrid.tsx`
    - `storefront/src/components/shade-finder/CameraSamplerModal.tsx`
    - `storefront/src/hooks/useShadeSelection.ts`
### Added
- **[ARCH-1095]** Configure Apache Kafka Event Bus, Debezium CDC and Stripe Webhook Worker
  - *Key modifications:*
    - `k8s/kafka/topics.yaml`
    - `k8s/debezium/pg-outbox-connector.json`
    - `services/event-bus/src/main/java/com/cosmetics/webhook/controller/StripeWebhookController.java`
    - `services/event-bus/src/main/java/com/cosmetics/webhook/service/WebhookEventDispatcher.java`
    - `services/event-bus/src/test/java/com/cosmetics/webhook/StripeWebhookControllerTest.java`
### Added
- **[ARCH-1094]** Build Spring Boot Subscription Replenishment Engine & Billing Scheduler
  - *Key modifications:*
    - `services/subscription-service/pom.xml`
    - `services/subscription-service/src/main/java/com/cosmetics/subscription/SubscriptionServiceApplication.java`
    - `services/subscription-service/src/main/java/com/cosmetics/subscription/controller/SubscriptionController.java`
    - `services/subscription-service/src/main/java/com/cosmetics/subscription/service/SubscriptionReplenishmentService.java`
    - `services/subscription-service/src/main/java/com/cosmetics/subscription/scheduler/DailySubscriptionBillingScheduler.java`
    - `services/subscription-service/src/main/java/com/cosmetics/subscription/model/SubscriptionDto.java`
    - `services/subscription-service/src/test/java/com/cosmetics/subscription/SubscriptionControllerTest.java`
### Added
- **[ARCH-1098]** Develop Spring Boot 3 Order Saga Orchestrator & Stripe Integration
  - *Key modifications:*
    - `services/order-service/pom.xml`
    - `services/order-service/src/main/java/com/cosmetics/order/OrderServiceApplication.java`
    - `services/order-service/src/main/java/com/cosmetics/order/controller/OrderCheckoutController.java`
    - `services/order-service/src/main/java/com/cosmetics/order/saga/OrderSagaCoordinator.java`
    - `services/order-service/src/main/java/com/cosmetics/order/service/StripePaymentGatewayService.java`
    - `services/order-service/src/main/java/com/cosmetics/order/model/OrderCheckoutRequest.java`
    - `services/order-service/src/main/java/com/cosmetics/order/model/OrderCheckoutResponse.java`
    - `services/order-service/src/test/java/com/cosmetics/order/OrderSagaCoordinatorTest.java`
### Added
- **[ARCH-1086]** Develop High-Throughput Catalog & Shade Matcher REST Microservice in Go/Gin
  - *Key modifications:*
    - `services/catalog-service/go.mod`
    - `services/catalog-service/cmd/catalog-service/main.go`
    - `services/catalog-service/internal/catalog/domain/color_matcher.go`
    - `services/catalog-service/internal/catalog/repository/cache_repo.go`
    - `services/catalog-service/internal/catalog/delivery/http/shade_handler.go`
    - `services/catalog-service/internal/catalog/domain/color_matcher_test.go`
### Added
- **[ARCH-1083]** Implement Redis 7 Redlock Atomic Reservation Service in Node.js/Fastify
  - *Key modifications:*
    - `services/inventory-reservation/package.json`
    - `services/inventory-reservation/src/scripts/reserve_stock.lua`
    - `services/inventory-reservation/src/routes/reservation.ts`
    - `services/inventory-reservation/src/config/redis_cluster.ts`
    - `services/inventory-reservation/src/workers/ttl_expiry_listener.ts`
    - `services/inventory-reservation/src/server.ts`
    - `services/inventory-reservation/test/reservation.test.ts`
### Added
- **[ARCH-1084]** Implement PostgreSQL Non-Locking Inventory Ledger and Reconciliation Worker
  - *Key modifications:*
    - `db/migrations/V2__inventory_ledger.sql`
    - `jobs/inventory_reconciler.go`
### Added
- **[ARCH-1097]** Deploy PostgreSQL Range-Partitioned Orders Table and Transactional Outbox
  - *Key modifications:*
    - `db/migrations/V3__partitioned_orders_and_outbox.sql`
    - `db/migrations/U3__partitioned_orders_and_outbox.sql`
### Added
- **[ARCH-1091]** Deploy PostgreSQL Customer Subscriptions Schema and Indexes
  - *Key modifications:*
    - `db/migrations/V4__customer_subscriptions.sql`
    - `db/migrations/U4__customer_subscriptions.sql`
### Added
- **[ARCH-1089]** Deploy PostgreSQL 16 Catalog & Shade Matrix Schema Migrations
  - *Key modifications:*
    - `db/migrations/V1__catalog_shade_schema.sql`
    - `db/migrations/U1__catalog_shade_schema.sql`

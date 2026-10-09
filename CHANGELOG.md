# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-29

### Added
- **Global Theme & Color Preset Manager (`ARCH-1517`)**: Global administrator configuration of system theme color palettes (`--primary`, `--bg-primary`, `--bg-secondary`, `--bg-card`, `--border`, `--text-primary`, `--text-muted`) with organization-wide transfer (`POST /api/v1/settings/presets/{id}/apply-global`) and dynamic client-side CSS hydration.
- **Worklist Layout Customization & Global Default Presets (`ARCH-1517`)**: Custom column visibility (Ticket #, Title, Category, Priority, Status, Agent, SLA Deadline, Created Date, Actions), table density selector (Compact / Normal / Comfortable), custom sorting, and "Save for All like Preset" feature enabling global administrators to enforce organization-wide default triage views.
- **Settings & Presets REST API (`/api/v1/settings/*`)**: Full CRUD and active configuration endpoints (`/api/v1/settings/active`, `/api/v1/settings/presets`) supporting both FastAPI and Express runtimes.

## [1.0.0] - 2026-09-28

### Added
- **Core Ticketing Schema & Migrations (`ARCH-1524`, `ARCH-1525`, `ARCH-1535`, `ARCH-1548`)**: Relational DDL tables for tickets, categories, departments, agents, skills taxonomy, SLA tracking, and audit ledger.
- **Idempotent Ingestion Engine (`ARCH-1518`, `ARCH-1528`, `ARCH-1529`)**: Multi-channel REST intake endpoint with `X-Idempotency-Key` deduplication and SLA deadline initialization.
- **7-State Lifecycle State Machine (`ARCH-1520`, `ARCH-1538`, `ARCH-1539`)**: State transition validator with optimistic concurrency locking and `409 Conflict` resolution.
- **SLA Calculation & Callback Engine (`ARCH-1519`, `ARCH-1526`, `ARCH-1531`)**: Real-time SLA elapsed time evaluation and multi-threshold milestone alerts (50%, 75%, 100%).
- **Skill-Based Automated Routing (`ARCH-1521`, `ARCH-1537`, `ARCH-1536`)**: Dynamic agent matching algorithm combining category skills and active workload capacity.
- **Omnichannel Notification Dispatcher (`ARCH-1530`)**: Multi-channel notification pipeline for Slack webhooks, Microsoft Teams, and Email.
- **Faceted Search & Discovery Service (`ARCH-1522`, `ARCH-1540`, `ARCH-1541`, `ARCH-1542`)**: Tokenized full-text search with dynamic status, priority, and category faceting.
- **Cryptographic Audit Ledger (`ARCH-1523`, `ARCH-1533`, `ARCH-1546`)**: SHA-256 hash chaining engine for tamper-evident compliance.
- **Modern Full-Stack Web Console (`ARCH-1527`, `ARCH-1532`, `ARCH-1534`, `ARCH-1543`)**: Unified interactive frontend featuring Requester Intake, Agent Workbench, Triage Dashboard, and Audit Drawer.
- **STRIDE Security Verification Suite (`ARCH-1549`)**: Automated tests verifying SQL injection immunity, XSS mitigation, and tenant authorization.

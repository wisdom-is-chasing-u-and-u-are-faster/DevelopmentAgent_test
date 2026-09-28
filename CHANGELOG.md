# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [Unreleased]

### Added
- **[fleet]** Automated feature implementation
  - *Key modifications:*
    - `.env.example`
    - `docker-compose.yml`
    - `requirements.txt`
    - `pyproject.toml`
    - `db/schema.sql`
    - `db/seed.sql`
    - `app/db/__init__.py`
    - `app/db/init_db.py`

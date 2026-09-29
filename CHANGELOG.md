# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-29

### Added
- **STP Digital Savings Account Opening Platform**: Complete implementation of straight-through customer onboarding platform (`ARCH-1849`).
- **Distributed Saga Orchestration Engine**: 7-state transactional state machine with compensating rollback handlers (`app/services/saga_orchestrator.py`).
- **OCR & ICAO Doc 9303 Checksum Engine**: Real-time document scanning and MRZ parsing with checksum verification (`app/services/ocr_service.py`).
- **3D Passive Biometric Liveness Verification**: Facial depth analysis and anti-spoofing defense service (`app/services/biometrics_service.py`).
- **Automated AML/PEP Watchlist Screening**: Automated real-time sanction list screening (`app/services/compliance_service.py`).
- **Core Banking System (CBS) Adapter**: CIF generation and savings account provisioning (`app/services/cbs_adapter.py`).
- **Card Management System (CMS) & HSM Adapter**: Instant virtual debit card generation and push tokenization for Apple Wallet and Google Pay (`app/services/cms_hsm_adapter.py`).
- **Cryptographic Audit Ledger**: Immutable SHA-256 chained transaction audit trail (`app/services/audit_service.py`).
- **Responsive Web/Mobile SPA Frontend**: Multi-step interactive onboarding portal mounted at `/` with modular page views in `public/pages/` and client API layer in `public/js/api.js`.
- **12-Factor Local Infrastructure**: Root `.env.example`, `.gitignore`, and `docker-compose.yml`.
- **Automated Test Suite**: Unit, integration, fullstack wiring, and E2E smoke verification tests achieving 100% AC coverage.

## [Unreleased]

### Added
- **[ARCH-1849]** UI Pages + Requirements: Digital Savings Account Opening Platform
  - *Key modifications:*
    - `.env.example`
    - `.gitignore`
    - `docker-compose.yml`
    - `db/schema.sql`
    - `db/seed.sql`
    - `app/db/init_db.py`
    - `app/models/schemas.py`
    - `app/services/saga_orchestrator.py`

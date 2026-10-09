# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **[ARCH-1596]** UI Pages + Requirements: Enterprise Ticketing Management System
  - **Feature 1**: Global Admin Settings & Color Presets Transfer (`system_presets`, dynamic CSS palette `--primary`, admin preset propagation across all user profiles).
  - **Feature 2**: Worklist Layout Settings & Save for All (`table-compact`/`table-comfortable`/`table-spacious` density, column visibility toggles, dynamic table rendering, organization layout preset saving).
  - *Key modifications:*
    - `db/schema.sql` (added `system_presets` table, `primary_color` and `worklist_layout_json` columns)
    - `db/seed.sql` (seeded default system presets for theme and worklist)
    - `app/db/init_db.py` (added SQLite migration guards for presets and user settings)
      - `app/models/audit.py` (added Pydantic schemas for system presets and user preferences)
    - `app/models/__init__.py`
    - `app/api/audit.py` (added endpoints for GET/PUT/apply-all system presets and reset-to-preset)
    - `app/main.py` (ensured `/pages` route directory mount)
    - `public/css/style.css` (added density classes, preset swatches, and layout modal styling)
    - `public/js/app.js` (added dynamic color palette propagation and user settings hydration)
    - `public/js/api.js` (added client methods for system presets)
    - `public/user_settings.html` (added corporate color presets, global admin transfer controls)
    - `public/ticket-queue.html` (added worklist layout settings modal and toolbar button)
    - `public/js/search.js` (added dynamic column rendering, density switching, save-for-all preset logic)
    - `tests/test_system_presets.py` (automated tests for presets and layout persistence)
    - `tests/test_db_schema.py`

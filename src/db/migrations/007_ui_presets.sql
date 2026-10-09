-- UI Presets Table for Theme Color & Worklist Layout Configurations
CREATE TABLE IF NOT EXISTS ui_presets (
    id VARCHAR(64) PRIMARY KEY,
    preset_type VARCHAR(32) NOT NULL, -- 'THEME_COLOR' or 'WORKLIST_LAYOUT'
    name VARCHAR(128) NOT NULL,
    config_json JSONB NOT NULL,
    is_global_default BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(128) DEFAULT 'global-admin',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ui_presets_type ON ui_presets(preset_type);

-- Seed Baseline Default Presets
INSERT INTO ui_presets (id, preset_type, name, config_json, is_global_default, created_by)
VALUES 
    (
        'preset-theme-slate-default',
        'THEME_COLOR',
        'Enterprise Slate (Default)',
        '{"primary":"#3b82f6","primary_hover":"#2563eb","bg_primary":"#0f172a","bg_secondary":"#1e293b","bg_card":"#334155","text_primary":"#f8fafc","text_muted":"#94a3b8","border":"#475569","success":"#10b981","warning":"#f59e0b","danger":"#ef4444"}'::jsonb,
        TRUE,
        'global-admin'
    ),
    (
        'preset-layout-standard-triage',
        'WORKLIST_LAYOUT',
        'Standard Triage Layout',
        '{"visible_columns":["ticket_number","title","category","priority","status","assigned_agent_name","actions"],"density":"normal","sort_by":"created_at","sort_order":"desc","page_size":20,"show_quick_filters":true}'::jsonb,
        TRUE,
        'global-admin'
    )
ON CONFLICT (id) DO NOTHING;

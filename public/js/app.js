/**
 * ETMS Main Interactive Application Controller
 * Wires UI views, event handlers, client API services, Global Theme Presets & Worklist Layouts
 */

import { api } from './api.js';

let currentTicket = null;
let allCategories = [];
let allThemePresets = [];
let allLayoutPresets = [];

// Default active layout configuration
let currentLayout = {
    visible_columns: ["ticket_number", "title", "category", "priority", "status", "assigned_agent_name", "actions"],
    density: "normal",
    sort_by: "created_at",
    sort_order: "desc",
    page_size: 20
};

// Column dictionary definition
const COLUMN_DEFS = {
    ticket_number: { label: "Ticket #", render: (t) => `<strong>${escapeHtml(t.ticket_number)}</strong>` },
    title: { label: "Title", render: (t) => escapeHtml(t.title) },
    category: { label: "Category", render: (t) => escapeHtml(t.category) },
    priority: { label: "Priority", render: (t) => `<span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span>` },
    status: { label: "Status", render: (t) => `<span class="badge badge-${t.status.toLowerCase()}">${t.status}</span>` },
    assigned_agent_name: { label: "Assigned Agent", render: (t) => t.assigned_agent_name || '<em>Unassigned</em>' },
    sla_deadline_resolution: { label: "SLA Resolve Deadline", render: (t) => t.sla_deadline_resolution ? new Date(t.sla_deadline_resolution).toLocaleString() : '-' },
    created_at: { label: "Created Date", render: (t) => t.created_at ? new Date(t.created_at).toLocaleString() : '-' },
    actions: { label: "Actions", render: (t) => `<button class="btn btn-secondary" style="padding:0.3rem 0.6rem; font-size:0.8rem;" onclick="openWorkbench('${t.id}')">Inspect</button>` }
};

document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initColorPickersSync();
    await hydrateActiveSettings();
    loadCategories();
    loadDashboardTickets();
    initIntakeForm();
    initSearchConsole();
    initWorkbenchControls();
    initLayoutControls();
    initSettingsTab();
});

function initNavigation() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const target = document.getElementById(tabId);
            if (target) target.classList.add('active');

            if (tabId === 'tab-dashboard') loadDashboardTickets();
            if (tabId === 'tab-search') executeSearch();
            if (tabId === 'tab-settings') loadSettingsPresets();
        });
    });
}

// ----------------------------------------------------------------------------
// 1. Theme & Color Presets Management (Feature 1)
// ----------------------------------------------------------------------------
function initColorPickersSync() {
    const colorFields = ['primary', 'primary-hover', 'bg-primary', 'bg-secondary', 'bg-card', 'border', 'text-primary', 'text-muted'];
    colorFields.forEach(field => {
        const picker = document.getElementById(`color-${field}`);
        const hex = document.getElementById(`hex-${field}`);
        if (picker && hex) {
            picker.addEventListener('input', () => {
                hex.value = picker.value;
            });
            hex.addEventListener('input', () => {
                if (/^#[0-9A-F]{6}$/i.test(hex.value)) {
                    picker.value = hex.value;
                }
            });
        }
    });
}

function applyThemeColors(config) {
    if (!config) return;
    const root = document.documentElement;
    if (config.primary) root.style.setProperty('--primary', config.primary);
    if (config.primary_hover) root.style.setProperty('--primary-hover', config.primary_hover);
    if (config.bg_primary) root.style.setProperty('--bg-primary', config.bg_primary);
    if (config.bg_secondary) root.style.setProperty('--bg-secondary', config.bg_secondary);
    if (config.bg_card) root.style.setProperty('--bg-card', config.bg_card);
    if (config.text_primary) root.style.setProperty('--text-primary', config.text_primary);
    if (config.text_muted) root.style.setProperty('--text-muted', config.text_muted);
    if (config.border) root.style.setProperty('--border', config.border);
    if (config.success) root.style.setProperty('--success', config.success);
    if (config.warning) root.style.setProperty('--warning', config.warning);
    if (config.danger) root.style.setProperty('--danger', config.danger);

    // Sync input controls if visible
    populateThemeInputs(config);
}

function populateThemeInputs(config) {
    const setVal = (field, val) => {
        const picker = document.getElementById(`color-${field}`);
        const hex = document.getElementById(`hex-${field}`);
        if (picker && val) picker.value = val;
        if (hex && val) hex.value = val;
    };
    if (config.primary) setVal('primary', config.primary);
    if (config.primary_hover) setVal('primary-hover', config.primary_hover);
    if (config.bg_primary) setVal('bg-primary', config.bg_primary);
    if (config.bg_secondary) setVal('bg-secondary', config.bg_secondary);
    if (config.bg_card) setVal('bg-card', config.bg_card);
    if (config.border) setVal('border', config.border);
    if (config.text_primary) setVal('text-primary', config.text_primary);
    if (config.text_muted) setVal('text-muted', config.text_muted);
}

function getThemeInputsConfig() {
    return {
        primary: document.getElementById('hex-primary')?.value || '#3b82f6',
        primary_hover: document.getElementById('hex-primary-hover')?.value || '#2563eb',
        bg_primary: document.getElementById('hex-bg-primary')?.value || '#0f172a',
        bg_secondary: document.getElementById('hex-bg-secondary')?.value || '#1e293b',
        bg_card: document.getElementById('hex-bg-card')?.value || '#334155',
        border: document.getElementById('hex-border')?.value || '#475569',
        text_primary: document.getElementById('hex-text-primary')?.value || '#f8fafc',
        text_muted: document.getElementById('hex-text-muted')?.value || '#94a3b8',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444'
    };
}

async function hydrateActiveSettings() {
    try {
        const active = await api.getActiveSettings();
        if (active.theme && active.theme.config) {
            applyThemeColors(active.theme.config);
        }
        if (active.worklist_layout && active.worklist_layout.config) {
            applyWorklistLayout(active.worklist_layout.config);
        }
    } catch (e) {
        console.warn('Could not load active presets from backend, using defaults', e);
    }
}

// ----------------------------------------------------------------------------
// 2. Worklist Layout Settings & Presets Management (Feature 2)
// ----------------------------------------------------------------------------
function applyWorklistLayout(config) {
    if (!config) return;
    currentLayout = { ...currentLayout, ...config };

    // Apply Density Class
    const table = document.getElementById('dashboard-table');
    if (table) {
        table.className = `density-${currentLayout.density || 'normal'}`;
    }

    // Update density buttons active state
    document.querySelectorAll('.density-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.density === currentLayout.density);
    });

    // Re-render table headers
    renderDashboardTableHeaders();
}

function renderDashboardTableHeaders() {
    const thead = document.getElementById('dashboard-table-head');
    if (!thead) return;

    const visibleCols = currentLayout.visible_columns || Object.keys(COLUMN_DEFS);
    let html = '<tr>';
    visibleCols.forEach(colKey => {
        const def = COLUMN_DEFS[colKey];
        if (def) {
            html += `<th>${def.label}</th>`;
        }
    });
    html += '</tr>';
    thead.innerHTML = html;
}

function initLayoutControls() {
    // Density buttons
    document.querySelectorAll('.density-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const density = btn.dataset.density;
            currentLayout.density = density;
            applyWorklistLayout(currentLayout);
        });
    });

    // Preset dropdown on Dashboard
    const presetSelect = document.getElementById('worklist-preset-select');
    if (presetSelect) {
        presetSelect.addEventListener('change', () => {
            const selectedId = presetSelect.value;
            const found = allLayoutPresets.find(p => p.id === selectedId);
            if (found && found.config) {
                applyWorklistLayout(found.config);
                loadDashboardTickets();
            }
        });
    }

    // Modal triggers
    document.getElementById('open-layout-modal-btn')?.addEventListener('click', openLayoutModal);

    // Save for All from Dashboard
    document.getElementById('save-layout-all-btn')?.addEventListener('click', async () => {
        try {
            const select = document.getElementById('worklist-preset-select');
            const currentPresetId = select?.value;
            if (currentPresetId) {
                const res = await api.applyGlobalPreset(currentPresetId);
                showBanner(res.message, 'success');
            } else {
                // Save current layout as global
                const newPreset = await api.createPreset({
                    preset_type: 'WORKLIST_LAYOUT',
                    name: 'Custom Global Default Layout',
                    config: currentLayout,
                    is_global_default: true
                });
                showBanner(`Saved '${newPreset.name}' as Global Default for all operators!`, 'success');
                await loadSettingsPresets();
            }
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        }
    });

    // Layout modal handlers
    document.getElementById('modal-apply-btn')?.addEventListener('click', () => {
        updateLayoutFromModal();
        closeLayoutModal();
        loadDashboardTickets();
    });

    document.getElementById('modal-save-all-btn')?.addEventListener('click', async () => {
        updateLayoutFromModal();
        closeLayoutModal();
        try {
            const res = await api.createPreset({
                preset_type: 'WORKLIST_LAYOUT',
                name: 'Custom Global Layout Preset',
                config: currentLayout,
                is_global_default: true
            });
            showBanner(`Preset '${res.name}' saved and applied for all users!`, 'success');
            loadSettingsPresets();
            loadDashboardTickets();
        } catch (err) {
            showBanner(`Save error: ${err.message}`, 'danger');
        }
    });
}

function openLayoutModal() {
    const modal = document.getElementById('layout-modal');
    if (!modal) return;

    // Check checkboxes according to currentLayout.visible_columns
    const cols = currentLayout.visible_columns || [];
    ['ticket_number', 'title', 'category', 'priority', 'status', 'assigned_agent_name', 'sla_deadline_resolution', 'created_at', 'actions'].forEach(c => {
        const chk = document.querySelector(`#layout-modal input[value="${c}"]`);
        if (chk) chk.checked = cols.includes(c);
    });

    modal.style.display = 'flex';
}

window.closeLayoutModal = function() {
    const modal = document.getElementById('layout-modal');
    if (modal) modal.style.display = 'none';
};

function updateLayoutFromModal() {
    const checkedCols = [];
    document.querySelectorAll('#layout-modal input[type="checkbox"]:checked').forEach(chk => {
        checkedCols.push(chk.value);
    });
    if (checkedCols.length === 0) {
        checkedCols.push('ticket_number', 'title', 'actions');
    }
    currentLayout.visible_columns = checkedCols;
    applyWorklistLayout(currentLayout);
}

// ----------------------------------------------------------------------------
// 3. Settings & Presets Tab Interactive Logic
// ----------------------------------------------------------------------------
async function loadSettingsPresets() {
    try {
        const themeData = await api.getPresets('THEME_COLOR');
        allThemePresets = themeData.presets || [];

        const layoutData = await api.getPresets('WORKLIST_LAYOUT');
        allLayoutPresets = layoutData.presets || [];

        // Populate Dashboard Layout Preset dropdown
        const dashSelect = document.getElementById('worklist-preset-select');
        if (dashSelect) {
            dashSelect.innerHTML = '';
            allLayoutPresets.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name + (p.is_global_default ? ' ★ (Global Default)' : '');
                if (p.is_global_default) opt.selected = true;
                dashSelect.appendChild(opt);
            });
        }

        // Populate Settings Theme Preset dropdown
        const themeSelect = document.getElementById('theme-preset-select');
        if (themeSelect) {
            themeSelect.innerHTML = '<option value="">Select a Theme Preset to load...</option>';
            allThemePresets.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name + (p.is_global_default ? ' ★ (Global Default)' : '');
                themeSelect.appendChild(opt);
            });
        }

        // Populate Settings Layout Preset dropdown
        const layoutSelect = document.getElementById('settings-layout-preset-select');
        if (layoutSelect) {
            layoutSelect.innerHTML = '<option value="">Select a Layout Preset to load...</option>';
            allLayoutPresets.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name + (p.is_global_default ? ' ★ (Global Default)' : '');
                layoutSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.error('Failed to load presets', err);
    }
}

function initSettingsTab() {
    // Theme preset dropdown change
    document.getElementById('theme-preset-select')?.addEventListener('change', (e) => {
        const presetId = e.target.value;
        const preset = allThemePresets.find(p => p.id === presetId);
        if (preset && preset.config) {
            document.getElementById('theme-preset-name').value = preset.name;
            applyThemeColors(preset.config);
        }
    });

    // Preview Theme Locally
    document.getElementById('theme-preview-local-btn')?.addEventListener('click', () => {
        const config = getThemeInputsConfig();
        applyThemeColors(config);
        showBanner('Theme applied locally for preview.', 'info');
    });

    // Reset Defaults
    document.getElementById('theme-reset-defaults-btn')?.addEventListener('click', () => {
        const defaultSlate = {
            primary: '#3b82f6',
            primary_hover: '#2563eb',
            bg_primary: '#0f172a',
            bg_secondary: '#1e293b',
            bg_card: '#334155',
            border: '#475569',
            text_primary: '#f8fafc',
            text_muted: '#94a3b8'
        };
        applyThemeColors(defaultSlate);
        showBanner('Reset to default Enterprise Slate palette.', 'info');
    });

    // Save as New Theme Preset
    document.getElementById('theme-save-preset-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('theme-preset-name')?.value.trim() || 'Custom Theme Preset';
        const config = getThemeInputsConfig();
        try {
            const created = await api.createPreset({
                preset_type: 'THEME_COLOR',
                name,
                config,
                is_global_default: false
            });
            showBanner(`Theme preset '${created.name}' saved successfully!`, 'success');
            await loadSettingsPresets();
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        }
    });

    // Transfer & Save for All (Global Default) - Feature 1
    document.getElementById('theme-transfer-global-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('theme-preset-name')?.value.trim() || 'Global Organization Theme';
        const config = getThemeInputsConfig();
        try {
            const created = await api.createPreset({
                preset_type: 'THEME_COLOR',
                name,
                config,
                is_global_default: true
            });
            applyThemeColors(config);
            showBanner(`🌐 Global Admin: Theme '${created.name}' has been transferred and activated for ALL users!`, 'success');
            await loadSettingsPresets();
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        }
    });

    // Settings Layout preset dropdown change
    document.getElementById('settings-layout-preset-select')?.addEventListener('change', (e) => {
        const presetId = e.target.value;
        const preset = allLayoutPresets.find(p => p.id === presetId);
        if (preset && preset.config) {
            document.getElementById('settings-layout-preset-name').value = preset.name;
            const cfg = preset.config;
            if (cfg.density) document.getElementById('settings-layout-density').value = cfg.density;
            if (cfg.sort_by) document.getElementById('settings-layout-sort-by').value = cfg.sort_by;
            if (cfg.sort_order) document.getElementById('settings-layout-sort-order').value = cfg.sort_order;
            if (cfg.page_size) document.getElementById('settings-layout-page-size').value = cfg.page_size;

            const cols = cfg.visible_columns || [];
            document.querySelectorAll('#tab-settings .col-toggle').forEach(chk => {
                chk.checked = cols.includes(chk.value);
            });
        }
    });

    // Apply Layout View from Settings Tab
    document.getElementById('layout-apply-local-btn')?.addEventListener('click', () => {
        const cols = [];
        document.querySelectorAll('#tab-settings .col-toggle:checked').forEach(chk => cols.push(chk.value));
        const density = document.getElementById('settings-layout-density').value;
        const sortBy = document.getElementById('settings-layout-sort-by').value;
        const sortOrder = document.getElementById('settings-layout-sort-order').value;
        const pageSize = parseInt(document.getElementById('settings-layout-page-size').value);

        currentLayout = {
            visible_columns: cols.length ? cols : ['ticket_number', 'title', 'actions'],
            density,
            sort_by: sortBy,
            sort_order: sortOrder,
            page_size: pageSize
        };

        applyWorklistLayout(currentLayout);
        showBanner('Worklist layout updated locally.', 'info');
    });

    // Save as New Layout Preset
    document.getElementById('layout-save-new-preset-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('settings-layout-preset-name')?.value.trim() || 'Custom Layout Preset';
        const cols = [];
        document.querySelectorAll('#tab-settings .col-toggle:checked').forEach(chk => cols.push(chk.value));

        const config = {
            visible_columns: cols.length ? cols : ['ticket_number', 'title', 'actions'],
            density: document.getElementById('settings-layout-density').value,
            sort_by: document.getElementById('settings-layout-sort-by').value,
            sort_order: document.getElementById('settings-layout-sort-order').value,
            page_size: parseInt(document.getElementById('settings-layout-page-size').value)
        };

        try {
            const created = await api.createPreset({
                preset_type: 'WORKLIST_LAYOUT',
                name,
                config,
                is_global_default: false
            });
            showBanner(`Layout preset '${created.name}' saved successfully!`, 'success');
            await loadSettingsPresets();
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        }
    });

    // Save for All like Preset (Global Default) - Feature 2
    document.getElementById('layout-transfer-global-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('settings-layout-preset-name')?.value.trim() || 'Global Default Layout';
        const cols = [];
        document.querySelectorAll('#tab-settings .col-toggle:checked').forEach(chk => cols.push(chk.value));

        const config = {
            visible_columns: cols.length ? cols : ['ticket_number', 'title', 'actions'],
            density: document.getElementById('settings-layout-density').value,
            sort_by: document.getElementById('settings-layout-sort-by').value,
            sort_order: document.getElementById('settings-layout-sort-order').value,
            page_size: parseInt(document.getElementById('settings-layout-page-size').value)
        };

        try {
            const created = await api.createPreset({
                preset_type: 'WORKLIST_LAYOUT',
                name,
                config,
                is_global_default: true
            });
            currentLayout = config;
            applyWorklistLayout(currentLayout);
            showBanner(`🌐 Global Admin: Worklist Layout preset '${created.name}' saved and activated for ALL operators!`, 'success');
            await loadSettingsPresets();
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        }
    });
}

// ----------------------------------------------------------------------------
// 4. Ticket Queue / Dashboard Dynamic Loading
// ----------------------------------------------------------------------------
async function loadCategories() {
    try {
        const data = await api.getCategories();
        allCategories = data.categories || [];
        const select = document.getElementById('intake-category');
        const filterSelect = document.getElementById('filter-category');

        if (select) {
            select.innerHTML = '<option value="">Select an Incident / Request Category...</option>';
            allCategories.forEach(c => {
                select.innerHTML += `<option value="${c.name}" data-priority="${c.default_priority}" data-dept="${c.department_id}">${c.name} (${c.department_name})</option>`;
            });

            select.addEventListener('change', () => {
                const opt = select.selectedOptions[0];
                if (opt && opt.dataset.priority) {
                    const prioSelect = document.getElementById('intake-priority');
                    if (prioSelect) prioSelect.value = opt.dataset.priority;
                }
            });
        }

        if (filterSelect) {
            filterSelect.innerHTML = '<option value="">All Categories</option>';
            allCategories.forEach(c => {
                filterSelect.innerHTML += `<option value="${c.name}">${c.name}</option>`;
            });
        }
    } catch (err) {
        console.error('Failed loading categories', err);
    }
}

function initIntakeForm() {
    const form = document.getElementById('ticket-intake-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('intake-submit-btn');
        submitBtn.disabled = true;
        submitBtn.innerText = 'Submitting...';

        const categoryOpt = document.getElementById('intake-category').selectedOptions[0];
        const deptId = categoryOpt ? categoryOpt.dataset.dept : 'dept-it-ops';

        const payload = {
            title: document.getElementById('intake-title').value,
            category: document.getElementById('intake-category').value,
            priority: document.getElementById('intake-priority').value,
            description: document.getElementById('intake-description').value,
            requester_email: document.getElementById('intake-email').value,
            department_id: deptId,
            tags: document.getElementById('intake-tags').value.split(',').map(s => s.trim()).filter(Boolean)
        };

        const idempotencyKey = 'idem-' + Math.random().toString(36).substring(2, 15);

        try {
            const created = await api.createTicket(payload, idempotencyKey);
            showBanner(`Ticket created successfully! Ref: ${created.ticket_number} (ID: ${created.id})`, 'success');
            form.reset();
            loadDashboardTickets();
        } catch (err) {
            showBanner(`Error: ${err.message}`, 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = '🚀 Submit Incident Request';
        }
    });
}

async function loadDashboardTickets() {
    const tbody = document.getElementById('dashboard-table-body');
    if (!tbody) return;

    const visibleCols = currentLayout.visible_columns || Object.keys(COLUMN_DEFS);
    renderDashboardTableHeaders();

    tbody.innerHTML = `<tr><td colspan="${visibleCols.length}" style="text-align:center;">Loading queue...</td></tr>`;

    try {
        const statusFilter = document.getElementById('filter-status')?.value || '';
        const priorityFilter = document.getElementById('filter-priority')?.value || '';
        const queryFilter = document.getElementById('filter-query')?.value || '';

        const data = await api.getTickets({
            status: statusFilter,
            priority: priorityFilter,
            query: queryFilter,
            limit: currentLayout.page_size || 20
        });
        const items = data.items || [];

        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${visibleCols.length}" style="text-align:center;">No tickets in current queue.</td></tr>`;
            return;
        }

        tbody.innerHTML = '';
        items.forEach(t => {
            let rowHtml = '<tr>';
            visibleCols.forEach(colKey => {
                const def = COLUMN_DEFS[colKey];
                if (def) {
                    rowHtml += `<td>${def.render(t)}</td>`;
                }
            });
            rowHtml += '</tr>';
            tbody.innerHTML += rowHtml;
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="${visibleCols.length}" style="color:red; text-align:center;">${err.message}</td></tr>`;
    }
}

window.openWorkbench = async function(ticketId) {
    try {
        currentTicket = await api.getTicket(ticketId);
        document.querySelector('[data-tab="tab-workbench"]').click();
        renderWorkbenchDetails(currentTicket);
    } catch (err) {
        alert('Failed to load ticket details: ' + err.message);
    }
};

function renderWorkbenchDetails(ticket) {
    document.getElementById('wb-ticket-number').innerText = ticket.ticket_number;
    document.getElementById('wb-title').innerText = ticket.title;
    document.getElementById('wb-description').innerText = ticket.description;
    document.getElementById('wb-category').innerText = ticket.category;
    document.getElementById('wb-priority').innerText = ticket.priority;
    document.getElementById('wb-status').innerText = ticket.status;
    document.getElementById('wb-assigned').innerText = ticket.assigned_agent_name || 'Unassigned';
    document.getElementById('wb-version').innerText = ticket.version;

    loadSLAWidget(ticket.id);
    loadAuditHistory(ticket.id);
}

async function loadSLAWidget(ticketId) {
    const slaContainer = document.getElementById('wb-sla-status');
    if (!slaContainer) return;

    try {
        const sla = await api.getTicketSLA(ticketId);
        let badgeColor = 'var(--success)';
        if (sla.status === 'AT_RISK') badgeColor = 'var(--warning)';
        if (sla.status === 'BREACHED') badgeColor = 'var(--danger)';

        slaContainer.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div><strong>SLA Tier:</strong> ${sla.sla_tier}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">Elapsed: ${sla.response_elapsed_mins} mins</div>
                </div>
                <div>
                    <span class="badge" style="background:${badgeColor}; color:white; font-size:0.875rem;">${sla.status}</span>
                </div>
            </div>
        `;
    } catch (e) {
        slaContainer.innerHTML = '<em>SLA tracking active</em>';
    }
}

async function loadAuditHistory(ticketId) {
    const list = document.getElementById('wb-audit-list');
    if (!list) return;

    list.innerHTML = 'Loading cryptographic audit ledger...';

    try {
        const audit = await api.getAuditTrail(ticketId);
        list.innerHTML = '';

        if (!audit.entries || audit.entries.length === 0) {
            list.innerHTML = '<div>No audit entries recorded yet.</div>';
            return;
        }

        const validBanner = audit.chain_valid 
            ? '<div style="color:var(--success); font-weight:600; margin-bottom:0.5rem;">🔒 SHA-256 Ledger Chain Valid (Tamper-Evident)</div>'
            : '<div style="color:var(--danger); font-weight:600; margin-bottom:0.5rem;">⚠️ Tamper Detected: Hash Chain Mismatch!</div>';

        list.innerHTML += validBanner;

        audit.entries.forEach((e, idx) => {
            list.innerHTML += `
                <div class="card" style="padding:0.75rem; margin-bottom:0.5rem; background:var(--bg-primary);">
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
                        <strong>#${idx + 1} ${e.action}</strong>
                        <span style="color:var(--text-muted);">${e.timestamp}</span>
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">Actor: ${e.actor_id} (${e.actor_role})</div>
                    <div class="code-block" style="margin-top:0.5rem;">SHA-256: ${e.checksum_sha256}</div>
                </div>
            `;
        });
    } catch (err) {
        list.innerHTML = `<div style="color:red;">Failed to load audit history: ${err.message}</div>`;
    }
}

function initWorkbenchControls() {
    document.getElementById('wb-route-btn')?.addEventListener('click', async () => {
        if (!currentTicket) return;
        try {
            const res = await api.routeTicket(currentTicket.id);
            alert(`Auto-assigned to ${res.agent_name} (Routing Score: ${res.routing_score})`);
            openWorkbench(currentTicket.id);
        } catch (e) {
            alert('Routing failed: ' + e.message);
        }
    });

    document.querySelectorAll('.wb-transition-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!currentTicket) return;
            const targetStatus = btn.getAttribute('data-status');
            const expectedVersion = currentTicket.version;

            try {
                await api.updateTicket(currentTicket.id, { status: targetStatus, expected_version: expectedVersion });
                showBanner(`Transitioned to ${targetStatus}!`, 'success');
                openWorkbench(currentTicket.id);
            } catch (err) {
                if (err.status === 409) {
                    showConflictDialog(err.message);
                } else {
                    alert('Transition error: ' + err.message);
                }
            }
        });
    });
}

function showConflictDialog(message) {
    const modal = document.getElementById('conflict-modal');
    const msgDiv = document.getElementById('conflict-modal-message');
    if (modal && msgDiv) {
        msgDiv.innerText = message;
        modal.style.display = 'flex';
    }
}

window.closeConflictModal = function() {
    const modal = document.getElementById('conflict-modal');
    if (modal) modal.style.display = 'none';
    if (currentTicket) openWorkbench(currentTicket.id);
};

function initSearchConsole() {
    const input = document.getElementById('search-input');
    if (!input) return;

    let timeout = null;
    input.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(executeSearch, 300);
    });

    document.getElementById('filter-category')?.addEventListener('change', executeSearch);
}

async function executeSearch() {
    const query = document.getElementById('search-input')?.value || '';
    const cat = document.getElementById('filter-category')?.value || '';
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = 'Searching...';

    try {
        const data = await api.search(query, { category: cat });
        const hits = data.hits || [];

        document.getElementById('search-meta').innerText = `Found ${data.total} result(s) in ${data.took_ms}ms`;

        if (hits.length === 0) {
            resultsContainer.innerHTML = '<div style="padding:1rem;">No matching incidents found.</div>';
            return;
        }

        resultsContainer.innerHTML = '';
        hits.forEach(h => {
            resultsContainer.innerHTML += `
                <div class="card" style="margin-bottom:0.75rem;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span class="badge badge-${h.priority.toLowerCase()}">${h.priority}</span>
                            <strong style="margin-left:0.5rem; font-size:1rem;">${h.ticket_number} - ${escapeHtml(h.title)}</strong>
                        </div>
                        <button class="btn btn-secondary" onclick="openWorkbench('${h.id}')">Inspect</button>
                    </div>
                    <div style="font-size:0.875rem; color:var(--text-muted); margin-top:0.5rem;">${escapeHtml(h.snippet)}</div>
                    <div style="font-size:0.75rem; margin-top:0.5rem; color:var(--primary);">Category: ${h.category} | Status: ${h.status}</div>
                </div>
            `;
        });
    } catch (err) {
        resultsContainer.innerHTML = `<div style="color:red;">Search error: ${err.message}</div>`;
    }
}

function showBanner(message, type = 'info') {
    const banner = document.getElementById('app-banner');
    if (!banner) return;
    banner.innerText = message;
    banner.className = `card btn-${type}`;
    banner.style.display = 'block';
    setTimeout(() => { banner.style.display = 'none'; }, 5000);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

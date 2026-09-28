/**
 * ETMS Main Interactive Application Controller
 * Wires UI views, event handlers, and client API services
 */

import { api } from './api.js';

let currentTicket = null;
let allCategories = [];

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadCategories();
    loadDashboardTickets();
    initIntakeForm();
    initSearchConsole();
    initWorkbenchControls();
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
        });
    });
}

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

            select.addEventListener('change', (e) => {
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

    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Loading queue...</td></tr>';

    try {
        const statusFilter = document.getElementById('filter-status')?.value || '';
        const priorityFilter = document.getElementById('filter-priority')?.value || '';
        const queryFilter = document.getElementById('filter-query')?.value || '';

        const data = await api.getTickets({ status: statusFilter, priority: priorityFilter, query: queryFilter });
        const items = data.items || [];

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No tickets in current queue.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        items.forEach(t => {
            const prioClass = `badge-${t.priority.toLowerCase()}`;
            const statusClass = `badge-${t.status.toLowerCase()}`;

            tbody.innerHTML += `
                <tr>
                    <td><strong>${t.ticket_number}</strong></td>
                    <td>${escapeHtml(t.title)}</td>
                    <td>${escapeHtml(t.category)}</td>
                    <td><span class="badge ${prioClass}">${t.priority}</span></td>
                    <td><span class="badge ${statusClass}">${t.status}</span></td>
                    <td>${t.assigned_agent_name || '<em>Unassigned</em>'}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="openWorkbench('${t.id}')">Inspect</button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">${err.message}</td></tr>`;
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
    document.getElementById('wb-requester').innerText = ticket.requester_email;

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

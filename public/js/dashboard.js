import { api } from './api.js';

let activeLayout = {
  density: 'normal',
  visible_columns: ['ticket_number', 'title', 'priority', 'status', 'category', 'sla_deadline_resolution', 'actions']
};

document.addEventListener('DOMContentLoaded', async () => {
  const queueBody = document.getElementById('queueBody');
  const refreshBtn = document.getElementById('refreshBtn');

  // Hydrate global theme and layout preset
  try {
    const active = await api.getActiveSettings();
    if (active.theme && active.theme.config) {
      const root = document.documentElement;
      const c = active.theme.config;
      if (c.primary) root.style.setProperty('--primary', c.primary);
      if (c.bg_primary) root.style.setProperty('--bg-primary', c.bg_primary);
      if (c.bg_secondary) root.style.setProperty('--bg-secondary', c.bg_secondary);
      if (c.text_primary) root.style.setProperty('--text-primary', c.text_primary);
      if (c.text_muted) root.style.setProperty('--text-muted', c.text_muted);
      if (c.border) root.style.setProperty('--border', c.border);
    }
    if (active.worklist_layout && active.worklist_layout.config) {
      activeLayout = { ...activeLayout, ...active.worklist_layout.config };
      const tbl = document.querySelector('table');
      if (tbl) tbl.className = `table density-${activeLayout.density || 'normal'}`;
    }
  } catch (e) {
    console.warn('Could not load global active settings', e);
  }

  async function loadQueue() {
    try {
      const data = await api.getTickets({ limit: 100 });
      const tickets = data.items || [];

      document.getElementById('statTotal').textContent = tickets.length;
      document.getElementById('statTriage').textContent = tickets.filter(t => t.status === 'SUBMITTED').length;
      document.getElementById('statProgress').textContent = tickets.filter(t => t.status === 'IN_PROGRESS').length;
      document.getElementById('statP1').textContent = tickets.filter(t => t.priority === 'P1').length;

      if (tickets.length === 0) {
        queueBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No tickets in queue.</td></tr>';
        return;
      }

      queueBody.innerHTML = tickets.map(t => `
        <tr>
          <td><strong>${t.ticket_number}</strong></td>
          <td>${t.title}</td>
          <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
          <td><strong>${t.status}</strong></td>
          <td>${t.category}</td>
          <td>${t.created_at ? new Date(t.created_at).toLocaleString() : '-'}</td>
          <td>
            <a href="/?id=${t.id}" class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Triage</a>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      queueBody.innerHTML = `<tr><td colspan="7" style="color: red; text-align: center;">Failed to load queue: ${err.message}</td></tr>`;
    }
  }

  if (refreshBtn) refreshBtn.addEventListener('click', loadQueue);
  loadQueue();
});

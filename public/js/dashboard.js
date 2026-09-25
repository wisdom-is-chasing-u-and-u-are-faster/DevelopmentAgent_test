import { ApiClient } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
  const queueBody = document.getElementById('queueBody');
  const refreshBtn = document.getElementById('refreshBtn');

  async function loadQueue() {
    try {
      const tickets = await ApiClient.listTickets(100);

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
          <td>${new Date(t.sla_resolve_deadline).toLocaleString()}</td>
          <td>
            <a href="/workbench.html?id=${t.ticket_id}" class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Triage</a>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      queueBody.innerHTML = `<tr><td colspan="7" style="color: red; text-align: center;">Failed to load queue: ${err.message}</td></tr>`;
    }
  }

  refreshBtn.addEventListener('click', loadQueue);
  loadQueue();
});

import { ApiClient } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  let ticketId = urlParams.get('id');

  const statusAlert = document.getElementById('statusAlert');
  const conflictModal = document.getElementById('conflictModal');
  const modalReloadBtn = document.getElementById('modalReloadBtn');
  const transitionForm = document.getElementById('transitionForm');

  async function loadTicket(id) {
    statusAlert.className = 'hidden';
    conflictModal.className = 'modal-backdrop hidden';

    try {
      let ticket;
      if (!id) {
        const list = await ApiClient.listTickets(1);
        if (list.length === 0) {
          document.getElementById('ticketTitle').textContent = 'No tickets available in database';
          return;
        }
        ticket = list[0];
        ticketId = ticket.ticket_id;
      } else {
        ticket = await ApiClient.getTicket(id);
      }

      document.getElementById('ticketId').value = ticket.ticket_id;
      document.getElementById('currentVersion').value = ticket.version;
      document.getElementById('ticketTitle').textContent = ticket.title;
      document.getElementById('ticketDesc').textContent = ticket.description;

      document.getElementById('metaNumber').textContent = ticket.ticket_number;
      document.getElementById('metaStatus').textContent = ticket.status;
      document.getElementById('metaPriority').textContent = ticket.priority;
      document.getElementById('metaVersion').textContent = ticket.version;
      document.getElementById('metaAck').textContent = new Date(ticket.sla_ack_deadline).toLocaleTimeString();
      document.getElementById('metaResolve').textContent = new Date(ticket.sla_resolve_deadline).toLocaleString();

      document.getElementById('auditLink').href = `/audit.html?id=${ticket.ticket_id}`;

      // Update badge
      document.getElementById('ticketBadge').innerHTML = `<span class="badge badge-${ticket.priority.toLowerCase()}">${ticket.priority}</span>`;
    } catch (err) {
      statusAlert.className = '';
      statusAlert.style.background = '#fce8e6';
      statusAlert.style.color = '#c5221f';
      statusAlert.textContent = `Error loading ticket: ${err.message}`;
    }
  }

  transitionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('ticketId').value;
    const targetStatus = document.getElementById('nextStatus').value;
    const expectedVersion = parseInt(document.getElementById('currentVersion').value);
    const comment = document.getElementById('transitionComment').value;

    try {
      const result = await ApiClient.updateStatus(id, targetStatus, expectedVersion, comment);
      statusAlert.className = '';
      statusAlert.style.background = '#e6f4ea';
      statusAlert.style.color = '#137333';
      statusAlert.textContent = `Status successfully updated to ${result.data.status} (Version ${result.data.version})`;
      document.getElementById('transitionComment').value = '';
      loadTicket(id);
    } catch (err) {
      if (err.status === 409 && err.conflict) {
        // Concurrency conflict dialog
        document.getElementById('modalExpectedVersion').textContent = err.conflict.expected_version;
        document.getElementById('modalCurrentVersion').textContent = err.conflict.current_version;
        document.getElementById('modalCurrentStatus').textContent = err.conflict.current_status;
        conflictModal.className = 'modal-backdrop';
      } else {
        statusAlert.className = '';
        statusAlert.style.background = '#fce8e6';
        statusAlert.style.color = '#c5221f';
        statusAlert.textContent = err.detail || err.message || 'Status transition failed';
      }
    }
  });

  modalReloadBtn.addEventListener('click', () => {
    loadTicket(ticketId);
  });

  loadTicket(ticketId);
});

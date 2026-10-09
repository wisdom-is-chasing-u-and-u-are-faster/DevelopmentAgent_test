import { ApiClient } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const ticketIdInput = document.getElementById('auditTicketId');
  const inspectBtn = document.getElementById('inspectBtn');
  const auditBody = document.getElementById('auditTableBody');
  const badge = document.getElementById('chainStatusBadge');

  let initialId = urlParams.get('id');
  if (initialId) {
    ticketIdInput.value = initialId;
    loadAudit(initialId);
  }

  async function loadAudit(id) {
    if (!id) return;
    auditBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Fetching audit trail...</td></tr>';
    badge.innerHTML = '';

    try {
      const res = await ApiClient.getAuditLedger(id);
      if (res.isChainValid) {
        badge.innerHTML = '<span class="badge" style="background: #e6f4ea; color: #137333; font-size: 0.9rem;">✅ SHA-256 Chain Intact & Verified</span>';
      } else {
        badge.innerHTML = `<span class="badge" style="background: #fce8e6; color: #c5221f; font-size: 0.9rem;">❌ Tamper Detected at Seq ${res.brokenAtAuditId}</span>`;
      }

      if (res.records.length === 0) {
        auditBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No audit mutations recorded for this ticket yet.</td></tr>';
        return;
      }

      auditBody.innerHTML = res.records.map((r, idx) => `
        <tr>
          <td><strong>#${r.auditId}</strong></td>
          <td><span class="badge badge-p3">${r.actionType}</span></td>
          <td>${new Date(r.timestamp).toLocaleString()}</td>
          <td><pre style="font-size: 0.75rem; max-width: 250px; overflow-x: auto;">${JSON.stringify(r.diffPayload, null, 2)}</pre></td>
          <td><span class="hash-code">${r.prevChecksum ? r.prevChecksum.substring(0, 16) + '...' : 'GENESIS'}</span></td>
          <td><span class="hash-code">${r.checksum ? r.checksum.substring(0, 16) + '...' : 'N/A'}</span></td>
        </tr>
      `).join('');
    } catch (err) {
      auditBody.innerHTML = `<tr><td colspan="6" style="color: red; text-align: center;">Failed to load audit records: ${err.message}</td></tr>`;
    }
  }

  inspectBtn.addEventListener('click', () => {
    loadAudit(ticketIdInput.value.trim());
  });
});

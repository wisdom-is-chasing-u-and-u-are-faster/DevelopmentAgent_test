async function loadAuditLedger() {
  const tbody = document.getElementById("audit-table-body");
  const statusBadge = document.getElementById("chain-status");

  try {
    const verify = await ETMS_API.verifyAuditChain();
    if (statusBadge) {
      if (verify.verified) {
        statusBadge.innerHTML = "<span class=\"badge badge-resolved\">🔒 Chain Valid & Tamper-Evident</span>";
      } else {
        statusBadge.innerHTML = "<span class=\"badge badge-p1\">⚠️ Chain Broken</span>";
      }
    }

    const data = await ETMS_API.getAuditLogs(50);
    if (tbody) {
      if (data.logs.length === 0) {
        tbody.innerHTML = "<tr><td colspan=\"6\" style=\"text-align:center; padding:2rem;\">No audit logs found.</td></tr>";
        return;
      }
      tbody.innerHTML = data.logs.map(log => `
        <tr>
          <td style="font-size:0.8125rem; color:var(--text-secondary);">${new Date(log.timestamp).toLocaleString()}</td>
          <td style="font-weight:600;">${log.entity_id}</td>
          <td><span class="badge badge-primary">${log.action}</span></td>
          <td>${log.actor}</td>
          <td style="font-family:monospace; font-size:0.75rem; color:var(--text-muted);">${log.previous_hash.substring(0, 16)}...</td>
          <td style="font-family:monospace; font-size:0.75rem; color:#60a5fa; font-weight:600;">${log.current_hash.substring(0, 16)}...</td>
        </tr>
      `).join("");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", loadAuditLedger);

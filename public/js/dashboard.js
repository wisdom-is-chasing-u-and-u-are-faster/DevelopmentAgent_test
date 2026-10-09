async function loadDashboardMetrics() {
  try {
    const metrics = await ETMS_API.getMetrics();
    const mttaEl = document.getElementById("kpi-mtta");
    const mttrEl = document.getElementById("kpi-mttr");
    const slaEl = document.getElementById("kpi-sla");
    const openEl = document.getElementById("kpi-open");
    const outagesEl = document.getElementById("kpi-outages");

    if (mttaEl) mttaEl.textContent = `${metrics.mtta_minutes}m`;
    if (mttrEl) mttrEl.textContent = `${metrics.mttr_minutes}m`;
    if (slaEl) slaEl.textContent = `${metrics.sla_adherence_percent}%`;
    if (openEl) openEl.textContent = metrics.open_incidents_count;
    if (outagesEl) outagesEl.textContent = metrics.critical_outages_count;

    const ticketData = await ETMS_API.listTickets({ limit: 5 });
    const tbody = document.getElementById("recent-tickets-tbody");
    if (tbody) {
      if (ticketData.items.length === 0) {
        tbody.innerHTML = "<tr><td colspan=\"6\" style=\"text-align:center; padding:2rem;\">No active incidents.</td></tr>";
      } else {
        tbody.innerHTML = ticketData.items.map(t => `
          <tr>
            <td><a href="/ticket-detail.html?id=${t.id}" style="color:var(--primary); font-weight:600; text-decoration:none;">${t.ticket_number}</a></td>
            <td style="font-weight:500;">${t.title}</td>
            <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
            <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
            <td>${t.assigned_agent || "<span style=\"color:var(--text-muted);\">Unassigned</span>"}</td>
            <td><a href="/ticket-detail.html?id=${t.id}" class="btn btn-secondary btn-sm">Triage</a></td>
          </tr>
        `).join("");
      }
    }
  } catch (err) {
    showToast(`Error loading dashboard: ${err.message}`, "error");
  }
}

document.addEventListener("DOMContentLoaded", loadDashboardMetrics);

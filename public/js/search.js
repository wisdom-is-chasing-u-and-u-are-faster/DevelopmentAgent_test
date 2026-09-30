async function executeTicketSearch() {
  const q = document.getElementById("search-query")?.value.trim() || "";
  const status = document.getElementById("filter-status")?.value || "";
  const priority = document.getElementById("filter-priority")?.value || "";
  const department = document.getElementById("filter-department")?.value || "";

  const tbody = document.getElementById("tickets-table-body");
  const countBadge = document.getElementById("results-count");

  if (tbody) {
    tbody.innerHTML = "<tr><td colspan=\"7\" style=\"text-align:center; padding:2rem;\">Loading tickets...</td></tr>";
  }

  try {
    const data = await ETMS_API.listTickets({ q, status, priority, department });
    if (countBadge) countBadge.textContent = `${data.total} tickets found`;

    if (tbody) {
      if (data.items.length === 0) {
        tbody.innerHTML = "<tr><td colspan=\"7\" style=\"text-align:center; padding:2rem;\">No matching tickets found.</td></tr>";
        return;
      }

      tbody.innerHTML = data.items.map(t => `
        <tr>
          <td><a href="/ticket-detail.html?id=${t.id}" style="color:var(--primary); font-weight:600; text-decoration:none;">${t.ticket_number}</a></td>
          <td style="font-weight:600;">${t.title}</td>
          <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
          <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
          <td>${t.department}</td>
          <td>${t.assigned_agent || "<span style=\"color:var(--text-muted);\">Unassigned</span>"}</td>
          <td><a href="/ticket-detail.html?id=${t.id}" class="btn btn-secondary btn-sm">Inspect</a></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-query");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(window._searchDebounce);
      window._searchDebounce = setTimeout(executeTicketSearch, 300);
    });
  }
  ["filter-status", "filter-priority", "filter-department"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", executeTicketSearch);
  });
  executeTicketSearch();
});

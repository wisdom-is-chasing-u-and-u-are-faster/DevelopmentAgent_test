const DEFAULT_WORKLIST_LAYOUT = {
  density: "comfortable",
  page_size: 20,
  sort_field: "created_at",
  sort_order: "desc",
  columns: ["ticket_number", "title", "priority", "status", "department", "assigned_agent", "sla_status", "actions"]
};

let currentLayout = { ...DEFAULT_WORKLIST_LAYOUT };
let isUserAdmin = false;

const COLUMN_DEFS = {
  ticket_number: {
    label: "Ticket #",
    render: t => `<a href="/ticket-detail.html?id=${t.id}" style="color:var(--primary); font-weight:600; text-decoration:none;">${t.ticket_number}</a>`
  },
  title: {
    label: "Incident Summary",
    render: t => `<span style="font-weight:600;">${t.title}</span>`
  },
  priority: {
    label: "Priority",
    render: t => `<span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span>`
  },
  status: {
    label: "Status",
    render: t => `<span class="badge badge-${t.status.toLowerCase()}">${t.status}</span>`
  },
  department: {
    label: "Department",
    render: t => `${t.department}`
  },
  category: {
    label: "Category",
    render: t => `${t.category || "--"}`
  },
  assigned_agent: {
    label: "Assigned Specialist",
    render: t => t.assigned_agent || `<span style="color:var(--text-muted);">Unassigned</span>`
  },
  sla_status: {
    label: "SLA Status",
    render: t => `<span class="badge" style="background:var(--bg-subtle);">${t.sla_status || "WITHIN_SLA"}</span>`
  },
  version: {
    label: "Version",
    render: t => `v${t.version}`
  },
  created_at: {
    label: "Created At",
    render: t => new Date(t.created_at).toLocaleDateString()
  },
  actions: {
    label: "Actions",
    render: t => `<a href="/ticket-detail.html?id=${t.id}" class="btn btn-secondary btn-sm">Inspect</a>`
  }
};

function renderTableHeader() {
  const thead = document.getElementById("tickets-table-head");
  if (!thead) return;

  const activeCols = currentLayout.columns.filter(c => COLUMN_DEFS[c]);
  thead.innerHTML = `<tr>${activeCols.map(c => `<th>${COLUMN_DEFS[c].label}</th>`).join("")}</tr>`;
}

function applyTableDensity(density) {
  const table = document.getElementById("tickets-table");
  if (!table) return;
  table.className = `table-${density}`;
}

async function executeTicketSearch() {
  const q = document.getElementById("search-query")?.value.trim() || "";
  const status = document.getElementById("filter-status")?.value || "";
  const priority = document.getElementById("filter-priority")?.value || "";
  const department = document.getElementById("filter-department")?.value || "";

  const tbody = document.getElementById("tickets-table-body");
  const countBadge = document.getElementById("results-count");
  const activeCols = currentLayout.columns.filter(c => COLUMN_DEFS[c]);

  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="${activeCols.length}" style="text-align:center; padding:2rem;">Loading tickets...</td></tr>`;
  }

  try {
    const data = await ETMS_API.listTickets({
      q,
      status: status === "ALL" ? "" : status,
      priority: priority === "ALL" ? "" : priority,
      department: department === "ALL" ? "" : department,
      limit: currentLayout.page_size || 20
    });

    if (countBadge) countBadge.textContent = `${data.total} tickets found`;

    if (tbody) {
      if (data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${activeCols.length}" style="text-align:center; padding:2rem;">No matching tickets found.</td></tr>`;
        return;
      }

      // Client-side sorting if needed
      let items = [...data.items];
      if (currentLayout.sort_field && currentLayout.sort_field !== "created_at") {
        const sf = currentLayout.sort_field;
        items.sort((a, b) => (a[sf] > b[sf] ? 1 : -1));
        if (currentLayout.sort_order === "desc") items.reverse();
      }

      tbody.innerHTML = items.map(t => `
        <tr>
          ${activeCols.map(c => `<td>${COLUMN_DEFS[c].render(t)}</td>`).join("")}
        </tr>
      `).join("");
    }
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ============================================================================
// Layout Modal & Preset Management
// ============================================================================

function openLayoutModal() {
  const modal = document.getElementById("layout-modal");
  if (!modal) return;

  // Sync checkboxes
  Object.keys(COLUMN_DEFS).forEach(colKey => {
    const cb = document.getElementById(`col-${colKey}`);
    if (cb) {
      cb.checked = currentLayout.columns.includes(colKey);
    }
  });

  // Always keep ticket_number checked
  const tktCb = document.getElementById("col-ticket_number");
  if (tktCb) tktCb.checked = true;

  // Sync density
  setDensity(currentLayout.density || "comfortable");

  // Sync page size & sort
  const ps = document.getElementById("layout-page-size");
  if (ps) ps.value = String(currentLayout.page_size || 20);

  const sf = document.getElementById("layout-sort-field")?.value || "created_at";
  if (sf) sf.value = currentLayout.sort_field || "created_at";

  // Admin controls
  const adminBox = document.getElementById("admin-layout-box");
  const saveAllBtn = document.getElementById("btn-save-all");
  if (adminBox) adminBox.style.display = isUserAdmin ? "block" : "none";
  if (saveAllBtn) saveAllBtn.style.display = isUserAdmin ? "inline-flex" : "none";

  modal.style.display = "flex";
}

function closeLayoutModal() {
  const modal = document.getElementById("layout-modal");
  if (modal) modal.style.display = "none";
}

function setDensity(density) {
  currentLayout.density = density;
  document.querySelectorAll(".density-btn").forEach(btn => btn.classList.remove("active"));
  const activeBtn = document.getElementById(`density-${density}`);
  if (activeBtn) activeBtn.classList.add("active");
}

function harvestModalLayout() {
  const cols = ["ticket_number"];
  Object.keys(COLUMN_DEFS).forEach(colKey => {
    if (colKey === "ticket_number") return;
    const cb = document.getElementById(`col-${colKey}`);
    if (cb && cb.checked) {
      cols.push(colKey);
    }
  });

  return {
    density: currentLayout.density || "comfortable",
    page_size: parseInt(document.getElementById("layout-page-size")?.value || "20", 10),
    sort_field: document.getElementById("layout-sort-field")?.value || "created_at",
    sort_order: "desc",
    columns: cols
  };
}

async function savePersonalLayout() {
  const newLayout = harvestModalLayout();
  currentLayout = newLayout;
  applyTableDensity(currentLayout.density);
  renderTableHeader();
  closeLayoutModal();

 try {
    const s = await ETMS_API.getUserSettings();
    await ETMS_API.updateUserSettings({
      ...s,
      worklist_layout: newLayout
    });
    showToast("Worklist layout preference saved!", "success");
    executeTicketSearch();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function saveLayoutForAll() {
  const newLayout = harvestModalLayout();
  currentLayout = newLayout;
  applyTableDensity(currentLayout.density);
  renderTableHeader();

  const payload = {
    preset_name: "Organization Worklist Preset",
    category: "worklist",
    apply_to_all: true,
    actor: "Global Admin",
    config: newLayout
  };

  try {
    const res = await ETMS_API.updateSystemPreset("worklist", payload, true);
    closeLayoutModal();
    showToast(res.message || "Worklist preset saved for all users!", "success");
    executeTicketSearch();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function resetWorklistPreset() {
  try {
    const res = await ETMS_API.getSystemPreset("worklist");
    if (res && res.config && res.config.columns) {
      currentLayout = { ...res.config };
      applyTableDensity(currentLayout.density || "comfortable");
      renderTableHeader();
      openLayoutModal(); // refresh checkboxes in modal
      showToast("Reset to organization preset!", "info");
    }
  } catch (err) {
    currentLayout = { ...DEFAULT_WORKLIST_LAYOUT };
    applyTableDensity(currentLayout.density);
    renderTableHeader();
    openLayoutModal();
    showToast("Reverted to standard layout.", "info");
  }
}

async function initWorklist() {
  try {
    const s = await ETMS_API.getUserSettings();
    isUserAdmin = Boolean(s.is_global_admin);
    if (s.worklist_layout && Array.isArray(s.worklist_layout.columns)) {
      currentLayout = { ...s.worklist_layout };
    }
  } catch (err) {
    // fallback to defaults
  }

  applyTableDensity(currentLayout.density || "comfortable");
  renderTableHeader();

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

  // Check URL params for ?open_layout=true
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("open_layout") === "true") {
    openLayoutModal();
  }
}

document.addEventListener("DOMContentLoaded", initWorklist);

window.openLayoutModal = openLayoutModal;
window.closeLayoutModal = closeLayoutModal;
window.setDensity = setDensity;
window.savePersonalLayout = savePersonalLayout;
window.saveLayoutForAll = saveLayoutForAll;
window.resetWorklistPreset = resetWorklistPreset;
window.executeTicketSearch = executeTicketSearch;

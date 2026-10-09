const STATES_ORDER = ["NEW", "TRIAGED", "ASSIGNED", "IN_PROGRESS", "PENDING_CUSTOMER", "RESOLVED", "CLOSED"];

async function loadTicketDetail() {
  const urlParams = new URLSearchParams(window.location.search);
  const ticketId = urlParams.get("id") || "tkt-1001";

  try {
    const tkt = await ETMS_API.getTicket(ticketId);
    window.CURRENT_TICKET = tkt;

    document.getElementById("tkt-number").textContent = tkt.ticket_number;
    document.getElementById("tkt-title").textContent = tkt.title;
    document.getElementById("tkt-description").textContent = tkt.description;
    document.getElementById("tkt-priority").innerHTML = `<span class="badge badge-${tkt.priority.toLowerCase()}">${tkt.priority}</span>`;
    document.getElementById("tkt-status").innerHTML = `<span class="badge badge-${tkt.status.toLowerCase()}">${tkt.status}</span>`;
    document.getElementById("tkt-department").textContent = tkt.department;
    document.getElementById("tkt-category").textContent = tkt.category;
    document.getElementById("tkt-requester").textContent = `${tkt.requester_name} (${tkt.requester_email})`;
    document.getElementById("tkt-agent").textContent = tkt.assigned_agent || "Unassigned";
    document.getElementById("tkt-version").textContent = `v${tkt.version}`;
    document.getElementById("tkt-sla").textContent = `${tkt.sla_elapsed_hours}h / ${tkt.sla_target_hours}h (${tkt.sla_status})`;

    renderStepper(tkt.status);
    renderHistory(tkt.history);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderStepper(currentStatus) {
  const stepper = document.getElementById("lifecycle-stepper");
  if (!stepper) return;
  const currentIndex = STATES_ORDER.indexOf(currentStatus);
  stepper.innerHTML = STATES_ORDER.map((s, idx) => {
    let cls = "step-item";
    if (idx < currentIndex) cls += " completed";
    else if (idx === currentIndex) cls += " active";
    return `
      <div class="${cls}">
        <div class="step-circle">${idx < currentIndex ? "✓" : idx + 1}</div>
        <div class="step-label">${s}</div>
      </div>
    `;
  }).join("");
}

function renderHistory(history = []) {
  const container = document.getElementById("history-timeline");
  if (!container) return;
  if (history.length === 0) {
    container.innerHTML = "<div style=\"color:var(--text-muted); font-size:0.875rem;\">No audit history recorded.</div>";
    return;
  }
  container.innerHTML = history.map(h => `
    <div style="padding:0.75rem 0; border-bottom:1px solid var(--border-color);">
      <div style="display:flex; justify-content:space-between; font-size:0.8125rem; color:var(--text-secondary);">
        <span><strong>${h.actor}</strong> (${h.action})</span>
        <span>${new Date(h.timestamp).toLocaleTimeString()}</span>
      </div>
      <div style="font-size:0.875rem; margin-top:0.25rem;">
        ${h.from_status ? `Transitioned: <span class="badge badge-${h.from_status.toLowerCase()}">${h.from_status}</span> ➔ ` : ""}
        ${h.to_status ? `<span class="badge badge-${h.to_status.toLowerCase()}">${h.to_status}</span>` : ""}
      </div>
      <div style="font-family:monospace; font-size:0.75rem; color:var(--text-muted); margin-top:0.25rem;">
        SHA-256: ${h.hash.substring(0, 24)}...
      </div>
    </div>
  `).join("");
}

async function triggerStatusTransition(targetStatus) {
  if (!window.CURRENT_TICKET) return;
  const comment = prompt(`Enter optional comment for transition to ${targetStatus}:`) || "";
  try {
    const res = await ETMS_API.updateStatus(
      window.CURRENT_TICKET.id,
      targetStatus,
      window.CURRENT_TICKET.version,
      comment,
      "Support Agent"
    );
    showToast(`Status updated to ${res.status}!`, "success");
    loadTicketDetail();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function triggerDispatch() {
  if (!window.CURRENT_TICKET) return;
  try {
    const res = await ETMS_API.dispatchTicket(window.CURRENT_TICKET.id);
    showToast(`Assigned to ${res.assigned_agent_name} (${res.dispatch_reason})`, "success");
    loadTicketDetail();
  } catch (err) {
    showToast(err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", loadTicketDetail);
window.triggerStatusTransition = triggerStatusTransition;
window.triggerDispatch = triggerDispatch;

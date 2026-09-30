const API_BASE = "/api/v1";

const ETMS_API = {
  async getHealth() { const res = await fetch("/health"); return res.json(); },
  async getMetrics() { const res = await fetch(`${API_BASE}/metrics`); if (!res.ok) throw new Error("Failed to load metrics"); return res.json(); },
  async listTickets(params = {}) {
    const query = new URLSearchParams();
    if (params.q) query.append("q", params.q);
    if (params.status) query.append("status", params.status);
    if (params.priority) query.append("priority", params.priority);
    if (params.department) query.append("department", params.department);
    if (params.page) query.append("page", params.page);
    if (params.limit) query.append("limit", params.limit);
    const res = await fetch(`${API_BASE}/tickets?${query.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch tickets");
    return res.json();
  },
  async getTicket(ticketId) {
    const res = await fetch(`${API_BASE}/tickets/${ticketId}`);
    if (!res.ok) throw new Error(`Ticket ${ticketId} not found`);
    return res.json();
  },
  async createTicket(payload) {
    const res = await fetch(`${API_BASE}/tickets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to submit ticket");
    }
    return res.json();
  },
  async updateStatus(ticketId, status, expectedVersion, comment = "", actor = "Operator") {
    const res = await fetch(`${API_BASE}/tickets/${ticketId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, expected_version: expectedVersion, comment, actor })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Status transition failed");
    }
    return res.json();
  },
  async dispatchTicket(ticketId, preferredAgentId = null) {
    const res = await fetch(`${API_BASE}/tickets/${ticketId}/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preferred_agent_id: preferredAgentId })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Dispatch failed");
    }
    return res.json();
  },
  async listAgents() {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error("Failed to fetch agents");
    return res.json();
  },
  async getAuditLogs(limit = 50) {
    const res = await fetch(`${API_BASE}/audit/logs?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch audit logs");
    return res.json();
  },
  async verifyAuditChain() {
    const res = await fetch(`${API_BASE}/audit/verify`);
    if (!res.ok) throw new Error("Failed to verify audit ledger");
    return res.json();
  },
  async getUserSettings() {
    const res = await fetch(`${API_BASE}/user/settings`);
    if (!res.ok) throw new Error("Failed to fetch settings");
    return res.json();
  },
  async updateUserSettings(payload) {
    const res = await fetch(`${API_BASE}/user/settings`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Failed to save settings");
    return res.json();
  }
};

window.ETMS_API = ETMS_API;

/**
 * Enterprise Ticketing Client API Layer
 */
const API_BASE = '/api/v1';

export const ApiClient = {
  async getDepartments() {
    const res = await fetch(`${API_BASE}/departments`);
    if (!res.ok) throw new Error('Failed to load departments');
    return (await res.json()).data;
  },

  async createTicket(payload, idempotencyKey) {
    const headers = {
      'Content-Type': 'application/json',
      'X-Idempotency-Key': idempotencyKey || ('key-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9))
    };

    const res = await fetch(`${API_BASE}/tickets`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    const body = await res.json();
    if (!res.ok) {
      throw { status: res.status, ...body };
    }
    return body;
  },

  async listTickets(limit = 50, offset = 0) {
    const res = await fetch(`${API_BASE}/tickets?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return (await res.json()).data;
  },

  async getTicket(id) {
    const res = await fetch(`${API_BASE}/tickets/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch ticket ${id}`);
    return (await res.json()).data;
  },

  async updateStatus(id, targetStatus, expectedVersion, comment) {
    const res = await fetch(`${API_BASE}/tickets/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: targetStatus,
        expected_version: expectedVersion,
        comment
      })
    });

    const body = await res.json();
    if (!res.ok) {
      throw { status: res.status, ...body };
    }
    return body;
  },

  async searchTickets(query, status, priority, departmentId) {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    if (departmentId) params.append('department_id', departmentId);

    const res = await fetch(`${API_BASE}/tickets/search?${params.toString()}`);
    if (!res.ok) throw new Error('Search failed');
    return (await res.json()).data;
  },

  async getAuditLedger(ticketId) {
    const res = await fetch(`${API_BASE}/audit/${ticketId}`);
    if (!res.ok) throw new Error('Failed to fetch audit ledger');
    return await res.json();
  }
};

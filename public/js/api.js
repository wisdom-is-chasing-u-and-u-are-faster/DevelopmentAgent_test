/**
 * ETMS Client API Service Layer
 * Interfaces directly with REST API routes declared in api_contract.json
 */

const API_BASE = '/api/v1';

export const api = {
    async getCategories() {
        const res = await fetch(`${API_BASE}/categories`);
        if (!res.ok) throw new Error('Failed to load categories');
        return await res.json();
    },

    async createTicket(payload, idempotencyKey = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (idempotencyKey) {
            headers['X-Idempotency-Key'] = idempotencyKey;
        }

        const res = await fetch(`${API_BASE}/tickets`, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Ticket submission failed');
        }
        return data;
    },

    async getTickets(params = {}) {
        const url = new URL(`${window.location.origin}${API_BASE}/tickets`);
        Object.entries(params).forEach(([k, v]) => {
            if (v !== undefined && v !== null && v !== '') {
                url.searchParams.append(k, v);
            }
        });
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error('Failed to fetch ticket queue');
        return await res.json();
    },

    async getTicket(ticketId) {
        const res = await fetch(`${API_BASE}/tickets/${ticketId}`);
        if (!res.ok) throw new Error('Failed to fetch ticket details');
        return await res.json();
    },

    async updateTicket(ticketId, payload, expectedVersion = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (expectedVersion !== null) {
            headers['If-Match'] = `W/"${expectedVersion}"`;
        }

        const res = await fetch(`${API_BASE}/tickets/${ticketId}`, {
            method: 'PATCH',
            headers,
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            const err = new Error(data.detail || 'Status transition failed');
            err.status = res.status;
            err.data = data;
            throw err;
        }
        return data;
    },

    async routeTicket(ticketId) {
        const res = await fetch(`${API_BASE}/tickets/${ticketId}/route`, {
            method: 'POST'
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Automated routing failed');
        return data;
    },

    async getTicketSLA(ticketId) {
        const res = await fetch(`${API_BASE}/tickets/${ticketId}/sla`);
        if (!res.ok) throw new Error('Failed to fetch SLA metrics');
        return await res.json();
    },

    async getAuditTrail(ticketId) {
        const res = await fetch(`${API_BASE}/tickets/${ticketId}/audit-trail`);
        if (!res.ok) throw new Error('Failed to fetch audit ledger');
        return await res.json();
    },

    async search(query, filters = {}) {
        const url = new URL(`${window.location.origin}${API_BASE}/search`);
        url.searchParams.append('q', query || '');
        Object.entries(filters).forEach(([k, v]) => {
            if (v) url.searchParams.append(k, v);
        });

        const res = await fetch(url.toString());
        if (!res.ok) throw new Error('Search failed');
        return await res.json();
    },

    async getAgents() {
        const res = await fetch(`${API_BASE}/agents`);
        if (!res.ok) throw new Error('Failed to fetch agent taxonomy');
        return await res.json();
    },

    async dispatchNotification(payload) {
        const res = await fetch(`${API_BASE}/notifications/dispatch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return await res.json();
    },

    async getHealth() {
        const res = await fetch('/health');
        return await res.json();
    }
};

window.api = api;

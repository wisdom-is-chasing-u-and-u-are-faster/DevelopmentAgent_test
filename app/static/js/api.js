/**
 * app/static/js/api.js — Centralized Client API Module for Agent Evaluation Platform.
 * Communicates with backend endpoints declared in api_contract.json.
 */

const API_BASE = '/api/v1';

class ApiClient {
  static async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') || endpoint.startsWith('/health')
      ? endpoint
      : `${API_BASE}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errData;
        try {
          errData = await response.json();
        } catch (e) {
          errData = { detail: response.statusText, status: response.status };
        }
        throw new Error(errData.detail || errData.title || `Request failed with status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${options.method || 'GET'} ${url}]:`, err);
      throw err;
    }
  }

  // Health
  static async getHealth() {
    return this.request('/health');
  }

  // Agents
  static async getAgents() {
    return this.request('/agents');
  }

  static async createAgent(agentData) {
    return this.request('/agents', {
      method: 'POST',
      body: JSON.stringify(agentData)
    });
  }

  // Datasets
  static async getDatasets() {
    return this.request('/datasets');
  }

  static async createDataset(datasetData) {
    return this.request('/datasets', {
      method: 'POST',
      body: JSON.stringify(datasetData)
    });
  }

  // Runs
  static async getRuns() {
    return this.request('/runs');
  }

  static async getRun(runId) {
    return this.request(`/runs/${encodeURIComponent(runId)}`);
  }

  static async createRun(runData) {
    return this.request('/runs', {
      method: 'POST',
      body: JSON.stringify(runData)
    });
  }

  // Trajectories
  static async getTrajectories(filters = {}) {
    const query = new URLSearchParams();
    if (filters.run_id) query.append('run_id', filters.run_id);
    if (filters.agent_id) query.append('agent_id', filters.agent_id);
    if (filters.status) query.append('status', filters.status);
    const qs = query.toString();
    return this.request(`/trajectories${qs ? '?' + qs : ''}`);
  }

  static async getTrajectory(trajectoryId) {
    return this.request(`/trajectories/${encodeURIComponent(trajectoryId)}`);
  }

  // Annotations
  static async getAnnotations() {
    return this.request('/annotations');
  }

  static async createAnnotation(annotationData) {
    return this.request('/annotations', {
      method: 'POST',
      body: JSON.stringify(annotationData)
    });
  }

  // Telemetry
  static async getCollaborationTelemetry() {
    return this.request('/telemetry/collaboration');
  }
}

// Export for module systems or attach to window
if (typeof window !== 'undefined') {
  window.ApiClient = ApiClient;
}

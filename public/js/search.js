import { ApiClient } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('searchForm');
  const queryInput = document.getElementById('searchQuery');
  const statusInput = document.getElementById('searchStatus');
  const priorityInput = document.getElementById('searchPriority');
  const resultsBody = document.getElementById('searchResultsBody');
  const resultsCount = document.getElementById('resultsCount');

  async function executeSearch() {
    resultsBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Searching...</td></tr>';
    try {
      const tickets = await ApiClient.searchTickets(
        queryInput.value,
        statusInput.value,
        priorityInput.value
      );

      resultsCount.textContent = `Found ${tickets.length} matching tickets`;

      if (tickets.length === 0) {
        resultsBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No tickets matched your query.</td></tr>';
        return;
      }

      resultsBody.innerHTML = tickets.map(t => `
        <tr>
          <td><strong>${t.ticket_number}</strong></td>
          <td>${t.title}</td>
          <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
          <td><strong>${t.status}</strong></td>
          <td>${new Date(t.created_at).toLocaleString()}</td>
          <td>
            <a href="/workbench.html?id=${t.ticket_id}" class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">View</a>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      resultsBody.innerHTML = `<tr><td colspan="6" style="color: red; text-align: center;">Search failed: ${err.message}</td></tr>`;
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    executeSearch();
  });

  // Initial load
  executeSearch();
});

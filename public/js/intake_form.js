import { ApiClient } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
  const deptSelect = document.getElementById('department');
  const form = document.getElementById('ticketForm');
  const alertBox = document.getElementById('alertBox');
  const submitBtn = document.getElementById('submitBtn');

  // Load departments
  try {
    const departments = await ApiClient.getDepartments();
    departments.forEach(dept => {
      const opt = document.createElement('option');
      opt.value = dept.department_id;
      opt.textContent = `${dept.department_name} (${dept.department_code})`;
      deptSelect.appendChild(opt);
    });
  } catch (err) {
    console.warn('Could not fetch departments, adding mock default:', err);
    const opt = document.createElement('option');
    opt.value = '11111111-1111-1111-1111-111111111111';
    opt.textContent = 'IT Support & Infrastructure (IT_SUPPORT)';
    deptSelect.appendChild(opt);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    alertBox.className = 'hidden';

    const payload = {
      department_id: deptSelect.value,
      category: document.getElementById('category').value,
      priority: document.getElementById('priority').value,
      title: document.getElementById('title').value,
      description: document.getElementById('description').value
    };

    try {
      const res = await ApiClient.createTicket(payload);
      alertBox.className = '';
      alertBox.style.background = '#e6f4ea';
      alertBox.style.color = '#137333';
      alertBox.style.border = '1px solid #ceead6';
      alertBox.innerHTML = `<strong>Ticket Submitted Successfully!</strong> Ticket Number: <code>${res.data.ticket_number}</code>. Status: <strong>${res.data.status}</strong>.`;
      form.reset();
    } catch (err) {
      alertBox.className = '';
      alertBox.style.background = '#fce8e6';
      alertBox.style.color = '#c5221f';
      alertBox.style.border = '1px solid #fad2cf';
      alertBox.innerHTML = `<strong>Submission Failed:</strong> ${err.detail || err.message || JSON.stringify(err)}`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Ticket';
    }
  });
});

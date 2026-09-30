function initIntakeForm() {
  const form = document.getElementById("new-ticket-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type=\"submit\"]");
    btn.disabled = true;
    btn.textContent = "Submitting...";

    const payload = {
      title: document.getElementById("ticket-title").value.trim(),
      description: document.getElementById("ticket-description").value.trim(),
      priority: document.getElementById("ticket-priority").value,
      department: document.getElementById("ticket-department").value,
      category: document.getElementById("ticket-category").value,
      requester_name: document.getElementById("requester-name").value.trim(),
      requester_email: document.getElementById("requester-email").value.trim(),
      idempotency_key: `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    try {
      const res = await ETMS_API.createTicket(payload);
      showToast(`Ticket ${res.ticket_number} created successfully!`, "success");
      form.reset();
      setTimeout(() => {
        window.location.href = `/ticket-detail.html?id=${res.id}`;
      }, 1500);
    } catch (err) {
      showToast(err.message, "error");
      btn.disabled = false;
      btn.textContent = "Submit Ticket";
    }
  });
}

document.addEventListener("DOMContentLoaded", initIntakeForm);

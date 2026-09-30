function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${type === "success" ? "✅" : (type === "error" ? "❌" : "ℹ️")}</span><div>${message}</div>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function initTheme() {
  const saved = localStorage.getItem("etms-theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("etms-theme", next);
}

document.addEventListener("DOMContentLoaded", initTheme);
window.showToast = showToast;
window.toggleTheme = toggleTheme;

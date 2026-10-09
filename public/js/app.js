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

function applyColorPalette(primaryHex) {
  if (!primaryHex) return;
  document.documentElement.style.setProperty("--primary", primaryHex);
  let hex = primaryHex.replace("#", "");
  if (hex.length === 3) hex = hex.split("").map(c => c + c).join("");
  const r = parseInt(hex.substring(0, 2), 16) || 59;
  const g = parseInt(hex.substring(2, 4), 16) || 130;
  const b = parseInt(hex.substring(4, 6), 16) || 246;
  document.documentElement.style.setProperty("--primary-light", `rgba(${r}, ${g}, ${b}, 0.18)`);
  const hr = Math.max(0, Math.floor(r * 0.85));
  const hg = Math.max(0, Math.floor(g * 0.85));
  const hb = Math.max(0, Math.floor(b * 0.85));
  document.documentElement.style.setProperty("--primary-hover", `rgb(${hr}, ${hg}, ${hb})`);
  localStorage.setItem("etms-primary-color", primaryHex);
}

async function initTheme() {
  const savedTheme = localStorage.getItem("etms-theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  const savedColor = localStorage.getItem("etms-primary-color");
  if (savedColor) {
    applyColorPalette(savedColor);
  }

  if (window.ETMS_API && typeof window.ETMS_API.getUserSettings === "function") {
    try {
      const s = await window.ETMS_API.getUserSettings();
      if (s.theme) {
        document.documentElement.setAttribute("data-theme", s.theme);
        localStorage.setItem("etms-theme", s.theme);
      }
      if (s.primary_color) {
        applyColorPalette(s.primary_color);
      }
      window.CURRENT_USER_SETTINGS = s;
    } catch (e) {
      // graceful fallback
    }
  }
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
window.applyColorPalette = applyColorPalette;
window.initTheme = initTheme;

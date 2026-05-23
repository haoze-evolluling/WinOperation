import { apiFetch, showToast, bindEvent } from "./utils.js";

export async function loadUpdate() {
  const data = await apiFetch("/api/update/status", { silent: true });
  if (!data || !data.success) return;

  const u = data.data;
  const statusEl = document.getElementById("update-status");
  const infoEl = document.getElementById("update-info");
  if (!statusEl || !infoEl) return;

  if (u.paused) {
    statusEl.textContent = "已暂停";
    statusEl.className = "status-tag paused";
    const expiry = u.expiry_time_local || u.expiry_time || "未知";
    infoEl.innerHTML = '<span style="color:var(--text-secondary);">到期时间: </span><span style="color:var(--text);font-weight:600;font-variant-numeric:tabular-nums;">' + expiry + "</span>";
  } else {
    statusEl.textContent = "正常";
    statusEl.className = "status-tag normal";
    infoEl.textContent = "Windows 更新处于默认状态";
  }
}

export function initUpdate() {
  loadUpdate();

  bindEvent("update-delay", "click", async () => {
    const btn = document.getElementById("update-delay");
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = "正在推迟...";

    try {
      const res = await apiFetch("/api/update/delay", { method: "POST" });
      if (res) {
        showToast(res.message, res.success ? "success" : "error");
        loadUpdate();
      }
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  });

  bindEvent("update-restore", "click", async () => {
    const btn = document.getElementById("update-restore");
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = "正在还原...";

    try {
      const res = await apiFetch("/api/update/restore", { method: "POST" });
      if (res) {
        showToast(res.message, res.success ? "success" : "error");
        loadUpdate();
      }
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  });
}

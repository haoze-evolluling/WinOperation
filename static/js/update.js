import { apiFetch, showToast, bindEvent, escapeHtml } from "./utils.js";

export async function loadUpdate() {
  const [data] = await Promise.allSettled([
    apiFetch("/api/update/status", { silent: true }),
    loadUpdateHealth(),
  ]).then(results => [results[0].value]);
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
  bindEvent("update-health-refresh", "click", loadUpdateHealth);

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

export async function loadUpdateHealth() {
  const data = await apiFetch("/api/update/health", { silent: true });
  if (!data || !data.success) return;
  const panel = document.getElementById("update-health-panel");
  if (!panel) return;
  const d = data.data;
  const services = d.services || [];
  const recommendations = d.recommendations || [];
  panel.innerHTML = `
    <div class="module-result-head">
      <strong>${d.paused ? "已检测到暂停策略" : "未检测到暂停策略"}</strong>
      <span>${escapeHtml(d.expiry_time_local || "默认更新")}</span>
    </div>
    <div class="module-kv-grid">
      <span>NoAutoUpdate</span><strong>${escapeHtml(d.policy.NoAutoUpdate || "-")}</strong>
      <span>AUOptions</span><strong>${escapeHtml(d.policy.AUOptions || "-")}</strong>
    </div>
    <div class="module-service-list">
      ${services.map(service => `
        <div>
          <span>${escapeHtml(service.display_name || service.name)}</span>
          <strong>${escapeHtml(service.status || "-")} · ${escapeHtml(service.start_type || "-")}</strong>
        </div>
      `).join("")}
    </div>
    <div class="module-tip-list">
      ${recommendations.map(item => `<div class="module-tip">${escapeHtml(item)}</div>`).join("")}
    </div>
  `;
}

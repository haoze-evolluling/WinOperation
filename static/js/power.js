import { apiFetch, showToast, bindEvent, escapeHtml } from "./utils.js";

export async function loadPower() {
  const data = await apiFetch("/api/power/status", { silent: true });
  if (!data || !data.success) return;

  const p = data.data;
  const currentEl = document.getElementById("power-scheme-current");
  if (currentEl) currentEl.textContent = p.current_scheme || "N/A";

  const sel = document.getElementById("power-scheme-select");
  if (!sel) return;
  sel.innerHTML = "";
  const schemes = p.schemes || [];
  if (schemes.length === 0) {
    sel.appendChild(new Option("无可用电源方案", ""));
    sel.disabled = true;
  } else {
    sel.disabled = false;
    schemes.forEach(s => {
      const opt = new Option(s.name, s.guid);
      if (p.current_scheme && p.current_scheme.indexOf(s.guid) !== -1) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  const fsEl = document.getElementById("fast-startup-status");
  if (fsEl) {
    fsEl.innerHTML = '<span class="status-dot ' + (p.fast_startup ? "green" : "red") + '"></span> ' + (p.fast_startup ? "已启用" : "已禁用");
  }

  const enableBtn = document.getElementById("fast-startup-enable");
  const disableBtn = document.getElementById("fast-startup-disable");
  if (enableBtn) enableBtn.disabled = p.fast_startup;
  if (disableBtn) disableBtn.disabled = !p.fast_startup;

  loadBatteryInsights();
}

export async function loadBatteryInsights() {
  const data = await apiFetch("/api/power/battery-insights", { silent: true });
  if (!data || !data.success) return;
  const d = data.data;

  const percent = d.present ? d.percentage + "%" : "无电池";
  const statusEl = document.getElementById("battery-insight-status");
  const percentEl = document.getElementById("battery-insight-percent");
  const remainingEl = document.getElementById("battery-insight-remaining");
  const tipsEl = document.getElementById("battery-insight-tips");

  if (statusEl) statusEl.textContent = d.status || "-";
  if (percentEl) percentEl.textContent = percent;
  if (remainingEl) remainingEl.textContent = d.remaining_label || "-";
  if (tipsEl) {
    const tips = d.tips || [];
    tipsEl.innerHTML = tips.length
      ? tips.map(tip => `<div class="module-tip">${escapeHtml(tip)}</div>`).join("")
      : '<div class="empty-hint">暂无电源建议</div>';
  }
}

export function initPower() {
  loadPower();
  bindEvent("battery-insights-refresh", "click", loadBatteryInsights);

  bindEvent("power-apply", "click", async () => {
    const guid = document.getElementById("power-scheme-select").value;
    if (!guid) return showToast("请选择电源方案", "error");
    const res = await apiFetch("/api/power/scheme", { method: "POST", body: JSON.stringify({ scheme_guid: guid }) });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });

  bindEvent("fast-startup-enable", "click", async () => {
    const res = await apiFetch("/api/power/faststartup", { method: "POST", body: JSON.stringify({ enable: true }) });
    if (res) {
      showToast(res.message, res.success ? "success" : "error");
      if (res.success) loadPower();
    }
  });

  bindEvent("fast-startup-disable", "click", async () => {
    const res = await apiFetch("/api/power/faststartup", { method: "POST", body: JSON.stringify({ enable: false }) });
    if (res) {
      showToast(res.message, res.success ? "success" : "error");
      if (res.success) loadPower();
    }
  });
}

import { apiFetch, showToast, bindEvent } from "./utils.js";

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
}

export function initPower() {
  loadPower();

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
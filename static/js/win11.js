import { apiFetch, showToast, bindEvent } from "./utils.js";

async function loadState() {
  const [menu, taskbar, search] = await Promise.all([
    apiFetch("/api/win11/classic-menu", { silent: true }),
    apiFetch("/api/win11/taskbar-align", { silent: true }),
    apiFetch("/api/win11/disable-search", { silent: true }),
  ]);

  const menuCb = document.getElementById("win11-classic-menu");
  const taskbarCb = document.getElementById("win11-taskbar-left");
  const searchCb = document.getElementById("win11-disable-search");

  if (menu && menu.success && menuCb) menuCb.checked = menu.data.enabled;
  if (taskbar && taskbar.success && taskbarCb) taskbarCb.checked = taskbar.data.left;
  if (search && search.success && searchCb) searchCb.checked = search.data.enabled;
}

function bindToggle(id, enableUrl, disableUrl) {
  const cb = document.getElementById(id);
  if (!cb) return;
  cb.addEventListener("change", async (e) => {
    const prev = !e.target.checked;
    const url = e.target.checked ? enableUrl : disableUrl;
    const res = await apiFetch(url, { method: "POST" });
    if (res && res.success) {
      showToast(res.message, "success");
    } else {
      e.target.checked = prev;
      showToast(res ? res.message : "操作失败", "error");
    }
  });
}

export function initWin11() {
  loadState();

  bindToggle("win11-classic-menu", "/api/win11/classic-menu/enable", "/api/win11/classic-menu/disable");
  bindToggle("win11-taskbar-left", "/api/win11/taskbar-align/left", "/api/win11/taskbar-align/center");
  bindToggle("win11-disable-search", "/api/win11/disable-search/enable", "/api/win11/disable-search/disable");

  bindEvent("win11-restart-explorer", "click", async () => {
    const btn = document.getElementById("win11-restart-explorer");
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = "正在重启...";
    try {
      const res = await apiFetch("/api/win11/restart-explorer", { method: "POST" });
      showToast(res ? res.message : "操作失败", res && res.success ? "success" : "error");
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  });
}

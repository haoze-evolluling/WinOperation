import { Dashboard } from "./dashboard.js";
import { stopShutdownCountdown } from "./shutdown.js";
import { initQuickSettings } from "./quicksettings.js";
import { initSpeedtest } from "./speedtest.js";
import { initActivation } from "./activation.js";
import { initAppUninstall } from "./app_uninstall.js";
import { initTabs } from "./tabs.js";
import { startGlobalRefresh, stopGlobalRefresh } from "./global.js";
import { bindEvent } from "./utils.js";
import { initTheme, toggleTheme, getStoredTheme } from './theme.js';

document.addEventListener("DOMContentLoaded", async () => {
  initTheme();

  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', toggleTheme);
  }

  const themeMedia = window.matchMedia('(prefers-color-scheme: dark)');
  themeMedia.addEventListener('change', () => {
    if (!getStoredTheme()) {
      initTheme();
    }
  });

  initQuickSettings();
  initSpeedtest();
  initActivation();
  initAppUninstall();
  initTabs();
  startGlobalRefresh();

  bindEvent("dash-refresh-btn", "click", () => Dashboard.refreshDashboard());

  const exitModal = document.getElementById("exit-modal");
  const exitBtn = document.getElementById("exit-btn");
  const exitConfirm = document.getElementById("exit-confirm-btn");
  const exitCancel = document.getElementById("exit-cancel-btn");

  if (exitBtn && exitModal) {
    exitBtn.addEventListener("click", () => exitModal.classList.add("active"));
  }

  if (exitCancel && exitModal) {
    exitCancel.addEventListener("click", () => exitModal.classList.remove("active"));
  }

  if (exitConfirm && exitModal) {
    exitConfirm.addEventListener("click", async () => {
      exitModal.classList.remove("active");
      await fetch("/api/system/exit", { method: "POST", headers: { "Content-Type": "application/json" } });
      document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:\'Microsoft YaHei\',sans-serif;font-size:1.15rem;color:var(--text-muted,#94A3B8);background:var(--bg,#F4F6F9);">程序已退出，请关闭此标签页</div>';
      window.close();
    });
  }

  if (exitModal) {
    exitModal.addEventListener("click", (e) => {
      if (e.target === exitModal) exitModal.classList.remove("active");
    });
  }
});

window.addEventListener("beforeunload", () => {
  Dashboard.stop();
  stopShutdownCountdown();
  stopGlobalRefresh();
});

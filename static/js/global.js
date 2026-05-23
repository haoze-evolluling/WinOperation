import { loadNetwork } from "./network.js";
import { loadPower } from "./power.js";
import { loadShutdown } from "./shutdown.js";
import { currentTab } from "./tabs.js";

const GLOBAL_REFRESH_INTERVAL = 30000;
let globalRefreshInterval = null;

export function startGlobalRefresh() {
  if (globalRefreshInterval) return;
  globalRefreshInterval = setInterval(async () => {
    if (currentTab === "tab-network") await loadNetwork();
    if (currentTab === "tab-power") await loadPower();
    if (currentTab === "tab-shutdown") await loadShutdown();
  }, GLOBAL_REFRESH_INTERVAL);
}

export function stopGlobalRefresh() {
  if (globalRefreshInterval) {
    clearInterval(globalRefreshInterval);
    globalRefreshInterval = null;
  }
}
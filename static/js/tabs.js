import { Dashboard } from "./dashboard.js";
import { loadNetwork, initNetwork } from "./network.js";
import { loadPower, initPower } from "./power.js";
import { loadShutdown, initShutdown } from "./shutdown.js";
import { loadUpdate, initUpdate } from "./update.js";
import { initWin11 } from "./win11.js";

export let currentTab = "tab-dashboard";
const initialized = new Set();

function ensureInit(name, initFn, loadFn) {
  if (!initialized.has(name)) {
    initialized.add(name);
    initFn();
  } else if (loadFn) {
    loadFn();
  }
}

function closeAllDropdowns() {
  document.querySelectorAll(".topnav-dropdown.open").forEach(el => el.classList.remove("open"));
  document.querySelectorAll(".topnav-item.dropdown-open").forEach(el => el.classList.remove("dropdown-open"));
}

export function switchTab(tabId, pushState = true) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".topnav-item.active, .topnav-dropdown-item.active").forEach(el => el.classList.remove("active"));

  const targetContent = document.getElementById(tabId);
  if (targetContent) targetContent.classList.add("active");

  // Direct nav item (概览)
  const directNav = document.querySelector(`.topnav-item[data-tab="${tabId}"]`);
  if (directNav) {
    directNav.classList.add("active");
  } else {
    // Sub-item inside a dropdown category
    const dropdownItem = document.querySelector(`.topnav-dropdown-item[data-tab="${tabId}"]`);
    if (dropdownItem) {
      dropdownItem.classList.add("active");
      const parentCategory = dropdownItem.closest(".topnav-item.has-dropdown");
      if (parentCategory) parentCategory.classList.add("active");
    }
  }

  if (pushState) {
    history.pushState(null, "", "#" + tabId);
  }

  currentTab = tabId;

  if (tabId === "tab-dashboard") {
    Dashboard.startDashboard();
  } else if (tabId === "tab-system-status") {
    Dashboard.startSystemStatus();
  } else if (tabId === "tab-network") {
    Dashboard.stop();
    ensureInit("tab-network", initNetwork, loadNetwork);
  } else if (tabId === "tab-power") {
    Dashboard.stop();
    ensureInit("tab-power", initPower, loadPower);
  } else if (tabId === "tab-shutdown") {
    Dashboard.stop();
    ensureInit("tab-shutdown", initShutdown, loadShutdown);
  } else if (tabId === "tab-update") {
    Dashboard.stop();
    ensureInit("tab-update", initUpdate, loadUpdate);
  } else if (tabId === "tab-win11") {
    Dashboard.stop();
    ensureInit("tab-win11", initWin11);
  } else {
    Dashboard.stop();
  }
}

function restoreTabFromHash() {
  const hash = window.location.hash.replace("#", "");
  if (hash && document.getElementById(hash)) {
    switchTab(hash, false);
  } else {
    switchTab("tab-dashboard", false);
  }
}

export function initTabs() {
  restoreTabFromHash();

  window.addEventListener("popstate", () => {
    const hash = window.location.hash.replace("#", "");
    if (hash && document.getElementById(hash)) {
      switchTab(hash, false);
    } else {
      switchTab("tab-dashboard", false);
    }
  });

  const topnavList = document.querySelector(".topnav-list");
  if (topnavList) {
    topnavList.addEventListener("click", e => {
      // Sub-item in a dropdown
      const dropdownItem = e.target.closest(".topnav-dropdown-item[data-tab]");
      if (dropdownItem) {
        closeAllDropdowns();
        switchTab(dropdownItem.getAttribute("data-tab"));
        return;
      }

      // Direct nav item (概览)
      const tabItem = e.target.closest(".topnav-item[data-tab]");
      if (tabItem) {
        closeAllDropdowns();
        switchTab(tabItem.getAttribute("data-tab"));
        return;
      }

      // Category toggle (has-dropdown)
      const categoryItem = e.target.closest(".topnav-item.has-dropdown");
      if (categoryItem) {
        const wasOpen = categoryItem.classList.contains("dropdown-open");
        closeAllDropdowns();
        if (!wasOpen) {
          categoryItem.classList.add("dropdown-open");
          const dd = categoryItem.querySelector(".topnav-dropdown");
          if (dd) dd.classList.add("open");
        }
      }
    });
  }

  // Close dropdowns when clicking outside
  document.addEventListener("click", e => {
    if (!e.target.closest(".topnav-item.has-dropdown, .topnav-dropdown")) {
      closeAllDropdowns();
    }
  });
}
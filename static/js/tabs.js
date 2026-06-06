import { Dashboard } from "./dashboard.js";
import { loadNetwork, initNetwork } from "./network.js";
import { loadPower, initPower } from "./power.js";
import { loadShutdown, initShutdown } from "./shutdown.js";
import { loadUpdate, initUpdate } from "./update.js";
import { initWin11 } from "./win11.js";

export let currentTab = "tab-dashboard";
const initialized = new Set();
const MOBILE_DROPDOWN_QUERY = "(max-width: 768px)";

function ensureInit(name, initFn, loadFn) {
  if (!initialized.has(name)) {
    initialized.add(name);
    initFn();
  } else if (loadFn) {
    loadFn();
  }
}

function isMobileTopnav() {
  return window.matchMedia && window.matchMedia(MOBILE_DROPDOWN_QUERY).matches;
}

function resetDropdownPosition(dropdown) {
  if (!dropdown) return;
  dropdown.classList.remove("mobile-floating");
  dropdown.style.removeProperty("--dropdown-left");
  dropdown.style.removeProperty("--dropdown-top");
  dropdown.style.removeProperty("--dropdown-max-width");
}

function positionOpenDropdown(categoryItem) {
  const dropdown = categoryItem && categoryItem.querySelector(".topnav-dropdown");
  if (!dropdown) return;

  resetDropdownPosition(dropdown);
  if (!isMobileTopnav() || !dropdown.classList.contains("open")) return;

  const nav = document.querySelector(".topnav");
  const navRect = nav ? nav.getBoundingClientRect() : null;
  const itemRect = categoryItem.getBoundingClientRect();
  const maxWidth = Math.max(140, window.innerWidth - 16);
  const dropdownWidth = Math.min(Math.max(dropdown.offsetWidth || 160, 140), maxWidth);
  const left = Math.min(
    Math.max(itemRect.left, 8),
    Math.max(8, window.innerWidth - dropdownWidth - 8),
  );
  const top = (navRect ? navRect.bottom : itemRect.bottom) + 6;

  dropdown.style.setProperty("--dropdown-left", Math.round(left) + "px");
  dropdown.style.setProperty("--dropdown-top", Math.round(top) + "px");
  dropdown.style.setProperty("--dropdown-max-width", Math.round(maxWidth) + "px");
  dropdown.classList.add("mobile-floating");
}

function closeAllDropdowns() {
  document.querySelectorAll(".topnav-dropdown").forEach(resetDropdownPosition);
  document.querySelectorAll(".topnav-dropdown.open").forEach(el => el.classList.remove("open"));
  document.querySelectorAll(".topnav-item.dropdown-open").forEach(el => el.classList.remove("dropdown-open"));
}

function switchTab(tabId, pushState = true) {
  if (tabId === "tab-insights") tabId = "tab-dashboard";

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
          if (dd) {
            dd.classList.add("open");
            positionOpenDropdown(categoryItem);
          }
        }
      }
    });

    const repositionOpenDropdown = () => {
      const openCategory = document.querySelector(".topnav-item.dropdown-open");
      if (openCategory) positionOpenDropdown(openCategory);
    };
    topnavList.addEventListener("scroll", repositionOpenDropdown, { passive: true });

    const topnav = document.querySelector(".topnav");
    if (topnav) topnav.addEventListener("scroll", repositionOpenDropdown, { passive: true });
  }

  // Close dropdowns when clicking outside
  document.addEventListener("click", e => {
    if (!e.target.closest(".topnav-item.has-dropdown, .topnav-dropdown")) {
      closeAllDropdowns();
    }
  });

  window.addEventListener("resize", () => {
    const openCategory = document.querySelector(".topnav-item.dropdown-open");
    if (openCategory) positionOpenDropdown(openCategory);
  });
}

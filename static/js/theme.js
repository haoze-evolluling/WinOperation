/**
 * WinOperation — Theme Manager
 * Handles dark/light mode with system preference detection
 * and localStorage persistence.
 */

const STORAGE_KEY = 'winoperation-theme';
const THEME_DARK = 'dark';
const THEME_LIGHT = 'light';

function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function setStoredTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch { /* noop */ }
}

function getSystemTheme() {
  if (!window.matchMedia) return THEME_LIGHT;
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? THEME_DARK
    : THEME_LIGHT;
}

function resolveTheme() {
  const stored = getStoredTheme();
  if (stored === THEME_DARK || stored === THEME_LIGHT) return stored;
  return getSystemTheme();
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || THEME_LIGHT;
  const next = current === THEME_DARK ? THEME_LIGHT : THEME_DARK;
  applyTheme(next);
  setStoredTheme(next);
}

/**
 * Initialize theme before DOM paints (called from inline script in <head>).
 * Export as global so inline script can call it.
 */
function initTheme() {
  applyTheme(resolveTheme());
}

// Export for module use
export { initTheme, toggleTheme, resolveTheme, applyTheme, getStoredTheme };

export function escapeHtml(text) {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

export function showToast(message, type) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = "toast " + type + " toast-enter";
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.classList.replace("toast-enter", "toast-exit");
    setTimeout(() => el.remove(), 200);
  }, 2800);
}

export async function apiFetch(url, options = {}) {
  const { method = "GET", body = null, signal = null, silent = false } = options;
  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      method,
      body,
      signal,
    });
    const data = await res.json();
    return data;
  } catch (err) {
    if (err.name === "AbortError") return null;
    if (!silent) {
      showToast("网络错误: " + err.message, "error");
    }
    return null;
  }
}

export function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

export function setBar(id, pct) {
  const el = document.getElementById(id);
  if (!el) return;
  const v = Math.min(100, Math.max(0, pct));
  el.style.width = v + "%";
  el.classList.remove("low", "mid", "high");
  if (v < 50) el.classList.add("low");
  else if (v < 80) el.classList.add("mid");
  else el.classList.add("high");
}

export function bindEvent(id, event, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(event, fn);
}

export function pad(n) { return n < 10 ? "0" + n : "" + n; }

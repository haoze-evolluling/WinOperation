import { apiFetch, showToast, escapeHtml, bindEvent, pad } from "./utils.js";

let shutdownTimerInterval = null;

export async function loadShutdown() {
  const data = await apiFetch("/api/shutdown/status", { silent: true });
  if (!data) return;
  const s = data.data;
  const el = document.getElementById("shutdown-status");
  if (!el) return;
  if (s.active) {
    el.innerHTML = '<span class="status-dot green"></span> 有活动的关机任务';
    if (s.remaining_seconds > 0) startShutdownCountdown(s.remaining_seconds);
  } else {
    el.innerHTML = '<span class="status-dot red"></span> 无活动任务';
    stopShutdownCountdown();
  }

  const startBtn = document.getElementById("shutdown-start");
  const cancelBtn = document.getElementById("shutdown-cancel");
  if (startBtn) startBtn.disabled = s.active;
  if (cancelBtn) cancelBtn.disabled = !s.active;
}

export async function loadSchedules() {
  const data = await apiFetch("/api/shutdown/schedules", { silent: true });
  if (!data || !data.success) return;

  const list = document.getElementById("schedule-list");
  if (!list) return;
  list.textContent = "";
  const items = data.data || [];
  items.forEach((s, idx) => {
    const div = document.createElement("div");
    div.className = "schedule-item";
    div.innerHTML = '<span>' + escapeHtml(s.TaskName || s.taskName || "Unknown") + ' &mdash; ' + escapeHtml(s.State || s.state || "") + '</span><button class="btn btn-sm btn-danger" data-schedule-id="' + idx + '">删除</button>';
    div.querySelector("button").addEventListener("click", async () => {
      const res = await apiFetch("/api/shutdown/schedule/" + idx, { method: "DELETE" });
      if (res) {
        showToast(res.message, res.success ? "success" : "error");
        if (res.success) loadSchedules();
      }
    });
    list.appendChild(div);
  });
}

export function initShutdown() {
  loadShutdown();
  loadSchedules();
  bindShutdownPresets();

  bindEvent("shutdown-start", "click", async function () {
    const mode = document.querySelector('input[name="shutdown-mode"]:checked');
    if (!mode) return;
    if (mode.value === "countdown") {
      const hours = parseInt(document.getElementById("shutdown-hours").value) || 0;
      const mins = parseInt(document.getElementById("shutdown-mins").value) || 0;
      const seconds = hours * 3600 + mins * 60;
      if (seconds < 60) return showToast("请设置至少 1 分钟", "error");
      const res = await apiFetch("/api/shutdown/timer", { method: "POST", body: JSON.stringify({ seconds }) });
      if (res) {
        showToast(res.message, res.success ? "success" : "error");
        if (res.success) { loadShutdown(); startShutdownCountdown(res.data.remaining_seconds); }
      }
    } else {
      const timeVal = document.getElementById("shutdown-time").value;
      if (!timeVal) return showToast("请选择时间", "error");
      const res = await apiFetch("/api/shutdown/timer", { method: "POST", body: JSON.stringify({ time: timeVal }) });
      if (res) showToast(res.message, res.success ? "success" : "error");
      if (res && res.success) { loadShutdown(); startShutdownCountdown(res.data.remaining_seconds); }
    }
  });

  bindEvent("shutdown-cancel", "click", async () => {
    const res = await apiFetch("/api/shutdown/cancel", { method: "POST" });
    if (res) {
      showToast(res.message, res.success ? "success" : "error");
      if (res.success) { loadShutdown(); stopShutdownCountdown(); }
    }
  });

  document.querySelectorAll('input[name="shutdown-mode"]').forEach(radio => {
    radio.addEventListener("change", function () {
      document.getElementById("countdown-inputs").style.display = this.value === "countdown" ? "flex" : "none";
      document.getElementById("time-input").style.display = this.value === "time" ? "flex" : "none";
    });
  });

  bindEvent("schedule-create", "click", async () => {
    const days = Array.from(document.querySelectorAll("#schedule-days input:checked")).map(cb => cb.value);
    const time = document.getElementById("schedule-time").value;
    if (!days.length) return showToast("请选择至少一天", "error");
    if (!time) return showToast("请选择时间", "error");
    const res = await apiFetch("/api/shutdown/schedule", { method: "POST", body: JSON.stringify({ days, time }) });
    if (res) {
      showToast(res.message, res.success ? "success" : "error");
      if (res.success) loadSchedules();
    }
  });
}

function bindShutdownPresets() {
  const presets = document.getElementById("shutdown-presets");
  if (!presets) return;
  presets.addEventListener("click", event => {
    const btn = event.target.closest(".module-preset[data-minutes]");
    if (!btn) return;
    const minutes = parseInt(btn.getAttribute("data-minutes"), 10);
    if (!minutes || minutes < 1) return;
    const countdownRadio = document.querySelector('input[name="shutdown-mode"][value="countdown"]');
    if (countdownRadio) {
      countdownRadio.checked = true;
      document.getElementById("countdown-inputs").style.display = "flex";
      document.getElementById("time-input").style.display = "none";
    }
    document.getElementById("shutdown-hours").value = Math.floor(minutes / 60);
    document.getElementById("shutdown-mins").value = minutes % 60;
    document.querySelectorAll("#shutdown-presets .module-preset").forEach(item => item.classList.remove("active"));
    btn.classList.add("active");
    showToast("已填入 " + btn.textContent + " 倒计时", "success");
  });
}

export function startShutdownCountdown(seconds) {
  stopShutdownCountdown();
  const display = document.getElementById("shutdown-timer-display");
  if (!display) return;
  const update = () => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    display.textContent = pad(h) + ":" + pad(m) + ":" + pad(s);
    if (seconds <= 0) { stopShutdownCountdown(); return; }
    seconds--;
  };
  update();
  shutdownTimerInterval = setInterval(update, 1000);
}

export function stopShutdownCountdown() {
  if (shutdownTimerInterval) { clearInterval(shutdownTimerInterval); shutdownTimerInterval = null; }
  const display = document.getElementById("shutdown-timer-display");
  if (display) display.textContent = "--:--:--";
}

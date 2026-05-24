import { apiFetch, setText, setBar, escapeHtml, bindEvent } from "./utils.js";

const CACHE_KEY = 'winoperation_dashboard_data';

function loadDashboardCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch(e) {
    return null;
  }
}

function saveDashboardCache() {
  const cache = { texts: {}, htmls: {}, bars: {}, props: {}, timestamp: Date.now() };

  const textIds = [
    'dash-os', 'dash-hostname', 'dash-uptime', 'dash-boot-time',
    'dash-login-user', 'dash-arch', 'dash-ip', 'dash-public-ip',
    'dash-ram-text', 'dash-ram-pct', 'dash-disk-text', 'dash-disk-pct',
    'dash-cpu', 'dash-gpu-vram', 'dash-gpu-temp', 'dash-gpu-driver',
    'dash-battery-pct', 'dash-battery-status',
    'dash-temp-cpu', 'dash-temp-gpu',
    'load-ram-text', 'load-disk-text', 'load-swap-text', 'load-cpu-text',
    'dash-adapter', 'dash-ssid', 'dash-signal-text',
    'dash-gateway-delay', 'dash-latency', 'dash-packet-loss', 'dash-dns'
  ];
  textIds.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.textContent && el.textContent !== '-') {
      cache.texts[id] = el.textContent;
    }
  });

  const onlineEl = document.getElementById('dash-online');
  if (onlineEl && onlineEl.textContent !== '-') {
    cache.texts['dash-online'] = onlineEl.textContent;
    if (onlineEl.style.color) {
      cache.props['dash-online'] = { color: onlineEl.style.color };
    }
  }

  ['dash-gpu', 'dash-disk-list', 'dash-proc-tbody'].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.innerHTML && !el.innerHTML.includes('-')) {
      cache.htmls[id] = el.innerHTML;
    }
  });

  const barIds = ['dash-ram-bar', 'dash-disk-bar', 'load-ram-bar', 'load-disk-bar', 'load-swap-bar', 'load-cpu-bar'];
  barIds.forEach(id => {
    const el = document.getElementById(id);
    if (el && el.style.width && el.style.width !== '0%') {
      cache.bars[id] = { width: el.style.width, classList: el.className };
    }
  });

  try { localStorage.setItem(CACHE_KEY, JSON.stringify(cache)); } catch(e) {}
}

function renderDashboardCache() {
  const cache = loadDashboardCache();
  if (!cache) return false;

  Object.entries(cache.texts || {}).forEach(([id, text]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  });

  Object.entries(cache.htmls || {}).forEach(([id, html]) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  });

  Object.entries(cache.bars || {}).forEach(([id, {width, classList}]) => {
    const el = document.getElementById(id);
    if (el) {
      el.style.width = width;
      el.className = classList || '';
    }
  });

  Object.entries(cache.props || {}).forEach(([id, props]) => {
    const el = document.getElementById(id);
    if (el) {
      Object.entries(props).forEach(([k, v]) => { el.style[k] = v; });
    }
  });

  // 恢复 Wi-Fi 节 visible
  const ssidEl = document.getElementById("dash-ssid");
  const wifiSection = document.getElementById("net-wifi-section");
  if (wifiSection && ssidEl && ssidEl.textContent !== "-") {
    wifiSection.style.display = "";
  }

  return true;
}

export const Dashboard = {
  systemStatusIntervalId: null,

  startDashboard() {
    this.stop();
    renderDashboardCache();
    this.fetchAll();
  },

  refreshDashboard() {
    const btn = document.getElementById('dash-refresh-btn');
    if (btn) btn.classList.add('spinning');
    this.fetchAll().then(() => {
      if (btn) btn.classList.remove('spinning');
    });
  },

  async fetchAll() {
    await Promise.allSettled([
      loadDashboard(),
      loadDashboardPublicIP(),
      loadDashboardResources(),
      loadDashboardHardware(),
      loadDashboardGpuDetail(),
      loadDashboardBattery(),
      loadDashboardTemps(),
      loadDashboardWifiDetail(),
      loadDashboardLatency(),
      loadDashboardGatewayDelay(),
    ]);
    saveDashboardCache();
  },

  startSystemStatus() {
    this.stop();
    const tick = async () => { await loadDashboardResources(); };
    tick();
    this.systemStatusIntervalId = setInterval(tick, 5000);
  },

  stop() {
    if (this.systemStatusIntervalId) {
      clearInterval(this.systemStatusIntervalId);
      this.systemStatusIntervalId = null;
    }
  }
};

// 基础信息
export async function loadDashboard() {
  const [sysData, netData] = await Promise.all([
    apiFetch("/api/system/info", { silent: true }),
    apiFetch("/api/network/status", { silent: true }),
  ]);

  if (sysData && sysData.success) {
    setText("dash-os", sysData.data.os);
    setText("dash-hostname", sysData.data.hostname);
    setText("dash-uptime", sysData.data.uptime);
    setText("dash-boot-time", sysData.data.boot_time || "N/A");
    setText("dash-login-user", sysData.data.login_user || "N/A");
    setText("dash-arch", sysData.data.architecture || "N/A");
  }

  if (netData && netData.success) {
    const conns = netData.data.connections;
    if (conns && conns.length > 0) {
      const c = conns[0];
      setText("dash-ip", c.IPv4Address || "N/A");
      setText("dash-adapter", c.InterfaceDescription || "N/A");
      setText("dash-dns", c.DNSServer || "N/A");
      const onlineEl = document.getElementById("dash-online");
      if (onlineEl) { onlineEl.textContent = "已联网"; onlineEl.style.color = "var(--success)"; }
    } else {
      setText("dash-ip", "N/A");
      setText("dash-adapter", "N/A");
      setText("dash-dns", "N/A");
      const onlineEl = document.getElementById("dash-online");
      if (onlineEl) { onlineEl.textContent = "未联网"; onlineEl.style.color = "var(--error)"; }
    }
  }
}

// 公网IP
export async function loadDashboardPublicIP() {
  const data = await apiFetch("/api/system/public-ip", { silent: true });
  if (data && data.success) setText("dash-public-ip", data.data.ip || "N/A");
}

// Wi-Fi 详情
export async function loadDashboardWifiDetail() {
  const data = await apiFetch("/api/system/wifi-detail", { silent: true });
  if (!data || !data.success) return;

  const wifiSection = document.getElementById("net-wifi-section");
  if (!wifiSection) return;

  if (data.data.connected && data.data.ssid) {
    wifiSection.style.display = "";
    setText("dash-ssid", data.data.ssid);
    setText("dash-signal-text", (data.data.signal || 0) + "%");
  } else {
    wifiSection.style.display = "none";
    setText("dash-ssid", "-");
    setText("dash-signal-text", "-");
  }
}

// 外网延迟 & 丢包率
export async function loadDashboardLatency() {
  const data = await apiFetch("/api/system/latency", { silent: true });
  if (data && data.success) {
    const d = data.data;
    setText("dash-latency", d.latency_ms !== null && d.latency_ms !== undefined ? d.latency_ms + " ms" : "N/A");
    setText("dash-packet-loss", d.loss_rate !== null && d.loss_rate !== undefined ? d.loss_rate + "%" : "N/A");
  }
}

// 内网网关延迟
export async function loadDashboardGatewayDelay() {
  const data = await apiFetch("/api/system/gateway-delay", { silent: true });
  if (data && data.success) {
    const d = data.data;
    if (d.delay_ms !== null && d.delay_ms !== undefined) {
      setText("dash-gateway-delay", d.gateway + " → " + d.delay_ms + " ms");
    } else {
      setText("dash-gateway-delay", d.error || "N/A");
    }
  }
}

// 硬件信息
export async function loadDashboardHardware(signal) {
  const data = await apiFetch("/api/system/hardware", { signal, silent: true });
  if (!data || !data.success) return;

  setText("dash-cpu", data.data.cpu || "N/A");

  const gpuContainer = document.getElementById("dash-gpu");
  if (gpuContainer) {
    const gpus = data.data.gpus || [];
    if (gpus.length === 0) {
      gpuContainer.innerHTML = '<span class="dash-val-sm">N/A</span>';
    } else {
      gpuContainer.textContent = "";
      gpus.forEach(g => {
        const div = document.createElement("div");
        div.className = "dash-val-sm";
        div.textContent = g.name || "N/A";
        gpuContainer.appendChild(div);
      });
    }
  }
}

let prevResources = null;

function resourcesChanged(r) {
  if (!prevResources) return true;
  if (prevResources.cpu_usage !== r.cpu_usage) return true;
  if (Math.abs(prevResources.ram_percent - r.ram_percent) > 1) return true;
  if (Math.abs(prevResources.disk_percent - r.disk_percent) > 1) return true;
  if ((prevResources.swap_percent || 0) !== (r.swap_percent || 0)) return true;

  const prevProcs = prevResources.top_processes || [];
  const curProcs = r.top_processes || [];
  if (prevProcs.length !== curProcs.length) return true;
  for (let i = 0; i < prevProcs.length; i++) {
    if (prevProcs[i].pid !== curProcs[i].pid ||
        prevProcs[i].cpu !== curProcs[i].cpu ||
        (prevProcs[i].memory_mb || 0) !== (curProcs[i].memory_mb || 0)) {
      return true;
    }
  }

  const prevDisks = prevResources.disks || [];
  const curDisks = r.disks || [];
  if (prevDisks.length !== curDisks.length) return true;
  for (let i = 0; i < prevDisks.length; i++) {
    if (Math.abs((prevDisks[i].percent || 0) - (curDisks[i].percent || 0)) > 1) return true;
  }

  return false;
}

// 资源与进程
export async function loadDashboardResources(signal) {
  const data = await apiFetch("/api/system/resources", { signal, silent: true });
  if (!data || !data.success) return;
  const r = data.data;

  if (!resourcesChanged(r)) return;
  prevResources = r;

  setText("dash-ram-text", r.ram_total + " GB (可用 " + r.ram_available + " GB)");
  setText("dash-ram-pct", r.ram_percent);
  setBar("dash-ram-bar", r.ram_percent);
  setBar("load-ram-bar", r.ram_percent);
  setText("load-ram-text", r.ram_percent + "%");

  setText("dash-disk-text", r.disk_total + " GB (可用 " + r.disk_free + " GB)");
  setText("dash-disk-pct", r.disk_percent);
  setBar("dash-disk-bar", r.disk_percent);
  setBar("load-disk-bar", r.disk_percent);
  setText("load-disk-text", r.disk_percent + "%");

  if (r.swap_total > 0) {
    setText("load-swap-text", r.swap_percent + "%");
    setBar("load-swap-bar", r.swap_percent);
  } else {
    setText("load-swap-text", "不可用");
    setBar("load-swap-bar", 0);
  }

  const diskList = document.getElementById("dash-disk-list");
  if (diskList) {
    const disks = r.disks || [];
    if (disks.length > 1) {
      diskList.textContent = "";
      const fragment = document.createDocumentFragment();
      disks.forEach(d => {
        const pct = Math.min(100, Math.max(0, d.percent || 0));
        let barClass = "bar-fill";
        if (pct < 50) barClass += " low";
        else if (pct < 80) barClass += " mid";
        else barClass += " high";
        const row = document.createElement("div");
        row.className = "dash-sub-row";
        row.innerHTML = `<span class="dash-sub-label">${escapeHtml(d.device || "?")}</span><span class="dash-sub-bar"><span class="bar-track"><span class="${barClass}" style="width:${pct}%"></span></span></span><span class="dash-sub-val-sm">${d.total || 0} GB / ${d.used || 0} GB (${d.percent || 0}%)</span>`;
        fragment.appendChild(row);
      });
      diskList.appendChild(fragment);
    } else {
      diskList.textContent = "";
    }
  }

  setBar("load-cpu-bar", r.cpu_usage);
  setText("load-cpu-text", r.cpu_usage + "%");

  renderProcessTable(r.top_processes || []);
}

function renderProcessTable(procs) {
  const tbody = document.getElementById("dash-proc-tbody");
  if (!tbody) return;
  tbody.textContent = "";
  if (procs.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="4" class="empty-hint">暂无进程数据</td>';
    tbody.appendChild(tr);
    return;
  }
  const fragment = document.createDocumentFragment();
  procs.forEach(p => {
    const tr = document.createElement("tr");
    const cpuPct = Math.min(100, Math.max(0, p.cpu || 0));
    const memPct = Math.min(100, Math.max(0, (p.memory_mb || 0) / 100));
    let cpuBarClass = "proc-bar-mini-fill";
    if (cpuPct < 50) cpuBarClass += " low";
    else if (cpuPct < 80) cpuBarClass += " mid";
    else cpuBarClass += " high";
    let memBarClass = "proc-bar-mini-fill";
    if (memPct < 50) memBarClass += " low";
    else if (memPct < 80) memBarClass += " mid";
    else memBarClass += " high";

    tr.innerHTML = `<td><span class="proc-name">${escapeHtml(p.name || "")}</span></td><td><span class="proc-pid">${p.pid || 0}</span></td><td><span class="proc-bar-mini"><span class="${cpuBarClass}" style="width:${Math.min(100, cpuPct)}%"></span></span>${p.cpu || 0}</td><td><span class="proc-bar-mini"><span class="${memBarClass}" style="width:${Math.min(100, memPct)}%"></span></span>${p.memory_mb || 0} MB</td>`;
    fragment.appendChild(tr);
  });
  tbody.appendChild(fragment);
}

// GPU 详情
export async function loadDashboardGpuDetail(signal) {
  const data = await apiFetch("/api/system/gpu-detail", { signal, silent: true });
  if (data && data.success) {
    const d = data.data;
    setText("dash-gpu-vram", d.vram_total ? d.vram_used + " / " + d.vram_total + " MB (" + d.vram_percent + "%)" : "-");
    setText("dash-gpu-temp", d.temp ? d.temp + "°C" : "-");
    setText("dash-gpu-driver", d.driver_version || "-");
  }
}

// 电池
export async function loadDashboardBattery() {
  const data = await apiFetch("/api/system/battery", { silent: true });
  if (data && data.success) {
    const d = data.data;
    if (d.present) {
      setText("dash-battery-pct", d.percentage + "%");
      setText("dash-battery-status", d.charging ? "充电中" : "未充电");
      const statusEl = document.getElementById("dash-battery-status");
      if (statusEl) statusEl.style.color = d.charging ? "var(--success)" : "var(--text-secondary)";
    }
  }
}

// 温度
export async function loadDashboardTemps() {
  const data = await apiFetch("/api/system/temps", { silent: true });
  if (data && data.success) {
    const d = data.data;
    const cpuEl = document.getElementById("dash-temp-cpu");
    const gpuEl = document.getElementById("dash-temp-gpu");
    if (cpuEl && d.cpu_temp != null) {
      cpuEl.textContent = d.cpu_temp + "°C";
      cpuEl.className = "temp-value" + (d.cpu_temp > 70 ? " hot" : d.cpu_temp > 50 ? " warm" : "");
    }
    if (gpuEl && d.gpu_temp != null) {
      gpuEl.textContent = d.gpu_temp + "°C";
      gpuEl.className = "temp-value" + (d.gpu_temp > 70 ? " hot" : d.gpu_temp > 50 ? " warm" : "");
    }
  }
}

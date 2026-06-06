import { apiFetch, setText, setBar, escapeHtml, bindEvent } from "./utils.js";
import { initInsights, loadInsights } from "./insights.js";

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
    'dash-cpu',
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

  ['dash-gpu-body', 'dash-disk-list', 'dash-proc-tbody'].forEach(id => {
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
    initInsights();
    this.fetchAll();
  },

  refreshDashboard() {
    const btn = document.getElementById('dash-refresh-btn');
    if (btn) btn.classList.add('spinning');
    Promise.allSettled([this.fetchAll(), loadInsights(true)]).then(() => {
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
    const tick = async () => {
      await Promise.allSettled([loadDashboardResources(), loadProcessSummary()]);
    };
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
    if (sysData.data.boot_time) setText("dash-boot-time", sysData.data.boot_time);
    if (sysData.data.login_user) setText("dash-login-user", sysData.data.login_user);
    if (sysData.data.architecture) setText("dash-arch", sysData.data.architecture);
  }

  if (netData && netData.success) {
    const conns = netData.data.connections;
    if (conns && conns.length > 0) {
      const c = conns[0];
      if (c.IPv4Address) setText("dash-ip", c.IPv4Address);
      if (c.InterfaceDescription) setText("dash-adapter", c.InterfaceDescription);
      if (c.DNSServer) setText("dash-dns", c.DNSServer);
      const onlineEl = document.getElementById("dash-online");
      if (onlineEl) { onlineEl.textContent = "已联网"; onlineEl.style.color = "var(--success)"; }
    }
  }
}

// 公网IP
export async function loadDashboardPublicIP() {
  const data = await apiFetch("/api/system/public-ip", { silent: true });
  if (data && data.success && data.data.ip) setText("dash-public-ip", data.data.ip);
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
    if (d.latency_ms != null) setText("dash-latency", d.latency_ms + " ms");
    if (d.loss_rate != null) setText("dash-packet-loss", d.loss_rate + "%");
  }
}

// 内网网关延迟
export async function loadDashboardGatewayDelay() {
  const data = await apiFetch("/api/system/gateway-delay", { silent: true });
  if (data && data.success) {
    const d = data.data;
    if (d.delay_ms != null) {
      setText("dash-gateway-delay", d.gateway + " → " + d.delay_ms + " ms");
    }
  }
}

// 硬件信息
export async function loadDashboardHardware(signal) {
  const data = await apiFetch("/api/system/hardware", { signal, silent: true });
  if (!data || !data.success) return;

  if (data.data.cpu) setText("dash-cpu", data.data.cpu);

  const gpuContainer = document.getElementById("dash-gpu");
  if (gpuContainer) {
    const gpus = data.data.gpus || [];
    gpuContainer.textContent = "";
    gpus.forEach(g => {
      if (!g.name) return;
      const div = document.createElement("div");
      div.className = "dash-val-sm";
      div.textContent = g.name;
      gpuContainer.appendChild(div);
    });
  }
}

let prevResources = null;
const resourceTrend = {
  cpu: [],
  ram: [],
  disk: [],
};

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

  if (r.ram_total > 0) {
    setText("dash-ram-text", r.ram_total + " GB (可用 " + r.ram_available + " GB)");
    setText("dash-ram-pct", r.ram_percent);
    setBar("dash-ram-bar", r.ram_percent);
  }
  setBar("load-ram-bar", r.ram_percent);
  setText("load-ram-text", r.ram_percent + "%");

  if (r.disk_total > 0) {
    setText("dash-disk-text", r.disk_total + " GB (可用 " + r.disk_free + " GB)");
    setText("dash-disk-pct", r.disk_percent);
    setBar("dash-disk-bar", r.disk_percent);
  }
  setBar("load-disk-bar", r.disk_percent);
  setText("load-disk-text", r.disk_percent + "%");

  if (r.swap_total > 0) {
    setText("load-swap-text", r.swap_percent + "%");
    setBar("load-swap-bar", r.swap_percent);
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
  renderResourceTrend(r);
}

export async function loadProcessSummary() {
  const data = await apiFetch("/api/system/process-summary", { silent: true });
  if (!data || !data.success) return;
  const d = data.data;
  setText("proc-summary-count", d.process_count);
  setText("proc-summary-threads", d.thread_count);
  setText("proc-summary-handles", d.handle_count);
}

function pushTrend(key, value) {
  const arr = resourceTrend[key];
  arr.push(Math.max(0, Math.min(100, Number(value) || 0)));
  while (arr.length > 18) arr.shift();
}

function renderSpark(id, values) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!values.length) {
    el.innerHTML = '<span class="module-spark-empty"></span>';
    return;
  }
  el.innerHTML = values.map(value => {
    const tone = value >= 90 ? "critical" : value >= 75 ? "warning" : "ok";
    return `<span class="${tone}" style="height:${Math.max(8, value)}%"></span>`;
  }).join("");
}

function renderResourceTrend(r) {
  if (!document.getElementById("resource-trend-grid")) return;
  pushTrend("cpu", r.cpu_usage);
  pushTrend("ram", r.ram_percent);
  pushTrend("disk", r.disk_percent);
  renderSpark("trend-cpu", resourceTrend.cpu);
  renderSpark("trend-ram", resourceTrend.ram);
  renderSpark("trend-disk", resourceTrend.disk);
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

// GPU 详情（多 GPU 支持 · 单列行布局 · 有数据才显示）
export async function loadDashboardGpuDetail(signal) {
  const data = await apiFetch("/api/system/gpu-detail", { signal, silent: true });
  const body = document.getElementById("dash-gpu-body");
  if (!body) return;
  if (!data || !data.success) {
    body.innerHTML = '<div class="gpu-empty">无法获取 GPU 数据</div>';
    return;
  }

  const gpus = data.data.gpus || [];
  if (gpus.length === 0) {
    body.textContent = "";
    return;
  }

  const fragment = document.createDocumentFragment();
  gpus.forEach((g, idx) => {
    const vendorClass = (g.vendor || "").toLowerCase();
    const badgeLabel = g.dedicated ? g.vendor : (g.vendor + " 集成");

    const card = document.createElement("div");
    card.className = "gpu-card-item";

    const cells = [];
    // 利用率
    if (g.load != null) {
      const barClass = "bar-fill" + (g.load < 50 ? " low" : g.load < 80 ? " mid" : " high");
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">利用率</div>
        <div class="gpu-stat-value">${g.load}%</div>
        <div class="bar-track"><div class="${barClass}" style="width:${Math.min(100, g.load)}%"></div></div>
      </div>`);
    }
    // 温度
    if (g.temperature != null) {
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">温度</div>
        <div class="gpu-stat-value">${g.temperature}°C</div>
      </div>`);
    }
    // 总显存
    if (g.vram_total != null && g.vram_total > 0) {
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">总显存</div>
        <div class="gpu-stat-value">${g.vram_total} MB</div>
      </div>`);
    } else if (g.vram_total === null) {
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">显存</div>
        <div class="gpu-stat-value">动态共享</div>
      </div>`);
    }
    // 占用显存
    if (g.vram_used != null && g.vram_total != null && g.vram_total > 0) {
      const barClass = "bar-fill" + ((g.vram_percent || 0) < 50 ? " low" : (g.vram_percent || 0) < 80 ? " mid" : " high");
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">占用显存</div>
        <div class="gpu-stat-value">${g.vram_used} MB (${g.vram_percent}%)</div>
        <div class="bar-track"><div class="${barClass}" style="width:${Math.min(100, g.vram_percent || 0)}%"></div></div>
      </div>`);
    }
    // 驱动版本
    if (g.driver_version) {
      cells.push(`<div class="gpu-stat-cell">
        <div class="gpu-stat-label">驱动版本</div>
        <div class="gpu-stat-value">${escapeHtml(g.driver_version)}</div>
      </div>`);
    }

    card.innerHTML = `
      <div class="gpu-card-header">
        <span class="gpu-vendor-badge ${vendorClass}">${badgeLabel}</span>
        <span class="gpu-card-title">${escapeHtml(g.name)}</span>
      </div>
      <div class="gpu-stat-grid">${cells.length ? cells.join('') : '<div class="gpu-stat-cell gpu-stat-cell--empty">暂无详细数据</div>'}</div>
    `;
    fragment.appendChild(card);
  });

  body.textContent = "";
  body.appendChild(fragment);
}

// 电池
export async function loadDashboardBattery() {
  const data = await apiFetch("/api/system/battery", { silent: true });
  if (data && data.success && data.data.present) {
    const d = data.data;
    setText("dash-battery-pct", d.percentage + "%");
    const statusEl = document.getElementById("dash-battery-status");
    if (statusEl) {
      statusEl.textContent = d.charging ? "充电中" : "未充电";
      statusEl.style.color = d.charging ? "var(--success)" : "var(--text-secondary)";
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

import { apiFetch, showToast, escapeHtml, bindEvent } from "./utils.js";

let currentAdapters = [];

function startAdapterLoading() {
  const bar = document.getElementById("adapter-loading-bar");
  const fill = document.getElementById("adapter-loading-fill");
  if (!bar || !fill) return { done() {} };
  bar.style.display = "block";
  fill.style.width = "0%";
  const start = Date.now();
  const timer = setInterval(() => {
    if (bar.style.display === "none") { clearInterval(timer); return; }
    const elapsed = (Date.now() - start) / 1000;
    const p = Math.min(99, 100 * (1 - Math.pow(0.65, elapsed)));
    fill.style.width = p + "%";
  }, 120);
  return {
    done() {
      clearInterval(timer);
      const elapsed = Date.now() - start;
      const minShow = 1500;
      const delay = Math.max(0, minShow - elapsed);
      setTimeout(() => {
        fill.style.width = "100%";
        setTimeout(() => { bar.style.display = "none"; }, 400);
      }, delay);
    }
  };
}

export async function loadNetwork() {
  const loading = startAdapterLoading();
  const data = await apiFetch("/api/network/status", { silent: true }).catch(() => null);
  if (!data || !data.success) { loading.done(); return; }

  const netData = data.data;
  currentAdapters = netData.adapters || [];

  const sel = document.getElementById("adapter-select");
  if (sel) {
    sel.innerHTML = '<option value="">-- 选择适配器 --</option>';
    currentAdapters.forEach(a => {
      const opt = document.createElement("option");
      opt.value = a.Name;
      opt.textContent = a.Name + " (" + (a.InterfaceDescription || "") + ") - " + a.Status;
      sel.appendChild(opt);
    });
  }

  const conns = netData.connections || [];
  const infoEl = document.getElementById("net-info");
  if (infoEl) {
    if (conns.length > 0) {
      const c = conns[0];
      let dnsVal = "";
      if (c.DNSServer) {
        dnsVal = Array.isArray(c.DNSServer)
          ? c.DNSServer.map(d => d.ServerAddresses || d).join(", ")
          : c.DNSServer;
      }
      infoEl.innerHTML = `<div class="info-grid"><span class="label">适配器</span><span class="value">${escapeHtml(c.InterfaceAlias || "")}</span><span class="label">IP</span><span class="value">${escapeHtml(c.IPv4Address || "")}</span><span class="label">网关</span><span class="value">${escapeHtml(c.IPv4DefaultGateway || "")}</span><span class="label">DNS</span><span class="value">${escapeHtml(dnsVal)}</span></div>`;
    } else {
      infoEl.innerHTML = "<p class='empty-hint'>未获取到活动连接</p>";
    }
  }

  const hasWifi = currentAdapters.some(a => /wi-fi|无线|wlan/i.test(a.Name));
  const wifiSection = document.getElementById("wifi-section");
  if (wifiSection) wifiSection.style.display = hasWifi ? "block" : "none";

  loading.done();
}

export function initNetwork() {
  loadNetwork();

  bindEvent("net-refresh-btn", "click", () => loadNetwork());
  bindEvent("network-diagnostic-run", "click", runNetworkDiagnostics);

  bindEvent("adapter-select", "change", function () {
    const adapter = currentAdapters.find(a => a.Name === this.value);
    if (adapter) {
      document.getElementById("net-info").innerHTML = `<div class="info-grid"><span class="label">名称</span><span class="value">${escapeHtml(adapter.Name)}</span><span class="label">描述</span><span class="value">${escapeHtml(adapter.InterfaceDescription || "")}</span><span class="label">状态</span><span class="value">${escapeHtml(adapter.Status)}</span><span class="label">索引</span><span class="value">${adapter.InterfaceIndex || ""}</span></div>`;
    }
  });

  bindEvent("wifi-enable", "click", async () => {
    const res = await apiFetch("/api/network/wifi", { method: "POST", body: JSON.stringify({ action: "enable" }) });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });

  bindEvent("wifi-disable", "click", async () => {
    const res = await apiFetch("/api/network/wifi", { method: "POST", body: JSON.stringify({ action: "disable" }) });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });

  function isValidIPv4(ip) {
    const parts = ip.trim().split(".");
    if (parts.length !== 4) return false;
    return parts.every(p => {
      const n = parseInt(p, 10);
      return !isNaN(n) && n >= 0 && n <= 255 && String(n) === p;
    });
  }

  function isValidIPv6(ip) {
    const s = ip.trim().toLowerCase();
    if (s.length < 2) return false;
    if (/[^0-9a-f:]/.test(s)) return false;
    const groups = s.split(":");
    if (groups.length < 3 || groups.length > 8) return false;
    let emptyCount = 0;
    for (const g of groups) {
      if (g === "") {
        emptyCount++;
        if (emptyCount > 2) return false;
      } else if (g.length > 4 || !/^[0-9a-f]{1,4}$/.test(g)) {
        return false;
      }
    }
    return true;
  }

  function isValidIP(ip) { return isValidIPv4(ip) || isValidIPv6(ip); }

  function fillDnsFromProvider(btn) {
    const protocol = document.querySelector('input[name="dns-protocol"]:checked');
    if (!protocol) return;
    const key = protocol.value === "v4" ? "data-dns-v4" : "data-dns-v6";
    const raw = btn.getAttribute(key);
    if (!raw) return showToast("该提供商不支持当前协议", "error");
    const servers = raw.split(",");
    document.getElementById("dns1").value = servers[0] || "";
    document.getElementById("dns2").value = servers[1] || "";
  }

  document.querySelectorAll(".dns-tag").forEach(btn => {
    btn.addEventListener("click", () => fillDnsFromProvider(btn));
  });

  document.querySelectorAll('input[name="dns-protocol"]').forEach(radio => {
    radio.addEventListener("change", function () {
      document.querySelectorAll(".protocol-option").forEach(o => o.classList.remove("active"));
      this.parentElement.classList.add("active");
    });
  });

  bindEvent("dns-auto", "click", async () => {
    const adapter = document.getElementById("adapter-select").value;
    if (!adapter) return showToast("请先选择适配器", "error");
    const res = await apiFetch("/api/network/dns", { method: "POST", body: JSON.stringify({ adapter_name: adapter, dns_servers: [] }) });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });

  bindEvent("dns-apply", "click", async () => {
    const adapter = document.getElementById("adapter-select").value;
    if (!adapter) return showToast("请先选择适配器", "error");
    const v1 = document.getElementById("dns1").value.trim();
    const v2 = document.getElementById("dns2").value.trim();
    if (v1 && !isValidIP(v1)) return showToast("首选 DNS 地址格式不正确", "error");
    if (v2 && !isValidIP(v2)) return showToast("备用 DNS 地址格式不正确", "error");
    const servers = [];
    if (v1) servers.push(v1);
    if (v2) servers.push(v2);
    if (servers.length === 0) return showToast("请输入 DNS 地址", "error");
    const res = await apiFetch("/api/network/dns", { method: "POST", body: JSON.stringify({ adapter_name: adapter, dns_servers: servers }) });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });

  bindEvent("flush-dns", "click", async () => {
    const res = await apiFetch("/api/network/flushdns", { method: "POST" });
    if (res) showToast(res.message, res.success ? "success" : "error");
  });
}

async function runNetworkDiagnostics() {
  const input = document.getElementById("network-diagnostic-target");
  const resultEl = document.getElementById("network-diagnostic-result");
  const btn = document.getElementById("network-diagnostic-run");
  if (!input || !resultEl) return;
  const target = input.value.trim();
  if (!target) return showToast("请输入诊断目标", "error");

  if (btn) {
    btn.disabled = true;
    btn.textContent = "诊断中...";
  }
  resultEl.innerHTML = '<div class="empty-hint">正在执行 Python 网络诊断...</div>';

  try {
    const res = await apiFetch("/api/network/diagnostics", {
      method: "POST",
      body: JSON.stringify({ target }),
    });
    if (!res || !res.success) {
      resultEl.innerHTML = '<div class="empty-hint">诊断失败</div>';
      return;
    }
    resultEl.innerHTML = renderNetworkDiagnostics(res.data);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "开始诊断";
    }
  }
}

function renderNetworkDiagnostics(data) {
  const ips = data.resolved_ips || [];
  const checks = data.tcp_checks || [];
  return `
    <div class="module-result-head">
      <strong>${escapeHtml(data.target)}</strong>
      <span>${data.elapsed_ms || 0} ms</span>
    </div>
    ${data.dns_error ? `<div class="module-alert warning">${escapeHtml(data.dns_error)}</div>` : ""}
    <div class="module-chip-row">
      ${ips.length ? ips.map(ip => `<span>${escapeHtml(ip.family)} · ${escapeHtml(ip.ip)}</span>`).join("") : "<span>无解析结果</span>"}
    </div>
    <div class="module-port-grid">
      ${checks.map(item => `
        <div class="module-port ${item.open ? "ok" : "closed"}">
          <span>TCP ${item.port}</span>
          <strong>${item.open ? "可连接" : "未开放"}</strong>
          <small>${item.elapsed_ms} ms</small>
        </div>
      `).join("")}
    </div>
  `;
}

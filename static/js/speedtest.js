import { apiFetch, showToast, escapeHtml, bindEvent } from "./utils.js";

let speedtestRunning = false;

export function initSpeedtest() {
  bindEvent("speedtest-start", "click", async function () {
    if (speedtestRunning) return;
    speedtestRunning = true;
    const btn = document.getElementById("speedtest-start");
    btn.disabled = true;
    btn.textContent = "测速中...";

    const progress = document.getElementById("speedtest-progress");
    progress.classList.add("active");

    const activeTab = document.querySelector(".speedtest-tab.active");
    const group = activeTab ? activeTab.getAttribute("data-group") : "all";

    const res = await apiFetch("/api/speedtest", {
      method: "POST",
      body: JSON.stringify({ group }),
    });

    if (res && res.success) {
      renderSpeedtestResults(res.data);
    }

    progress.classList.remove("active");
    btn.disabled = false;
    btn.textContent = "开始测速";
    speedtestRunning = false;
  });

  bindEvent("custom-ping-btn", "click", () => runCustomTest("ping"));
  bindEvent("custom-nslookup-btn", "click", () => runCustomTest("nslookup"));
  bindEvent("resolve-run-btn", "click", runResolveTest);

  bindEvent("custom-target", "keydown", (e) => {
    if (e.key === "Enter") runCustomTest("ping");
  });
  bindEvent("resolve-target", "keydown", (e) => {
    if (e.key === "Enter") runResolveTest();
  });

  document.querySelectorAll(".speedtest-tab").forEach(tab => {
    tab.addEventListener("click", function () {
      if (speedtestRunning) return;
      document.querySelectorAll(".speedtest-tab").forEach(t => t.classList.remove("active"));
      this.classList.add("active");
    });
  });
}

function getLatencyClass(avgMs) {
  if (avgMs == null) return "";
  if (avgMs < 50) return "latency-fast";
  if (avgMs < 150) return "latency-mid";
  return "latency-slow";
}

function renderSpeedtestResults(data) {
  const tbody = document.getElementById("speedtest-tbody");
  if (!tbody) return;
  tbody.textContent = "";

  const all = [
    ...(data.domestic || []).map(r => ({ ...r, _region: "domestic" })),
    ...(data.foreign || []).map(r => ({ ...r, _region: "foreign" })),
  ];

  const activeTab = document.querySelector(".speedtest-tab.active");
  const filter = activeTab ? activeTab.getAttribute("data-group") : "all";

  let filtered;
  if (filter === "all") filtered = all;
  else filtered = (filter === "domestic" ? data.domestic || [] : data.foreign || []).map(r => ({ ...r, _region: filter }));

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-hint">暂无数据</td></tr>';
    return;
  }

  const fragment = document.createDocumentFragment();
  filtered.forEach(r => {
    const tr = document.createElement("tr");
    const regionLabel = r._region === "domestic" ? "国内" : "国外";
    const regionClass = r._region === "domestic" ? "badge-domestic" : "badge-foreign";
    const latencies = r.min_ms != null ? r.min_ms + " / " + r.avg_ms + " / " + r.max_ms + " ms" : "-";
    const avgMs = r.avg_ms;
    const latencyClass = avgMs != null ? getLatencyClass(avgMs) : "";

    let statusText, statusClass;
    switch (r.status) {
      case "ok": statusText = "正常"; statusClass = "status-ok"; break;
      case "partial": statusText = "部分丢包"; statusClass = "status-partial"; break;
      case "timeout": statusText = "超时"; statusClass = "status-timeout"; break;
      case "dns_fail": statusText = "解析失败"; statusClass = "status-dnsfail"; break;
      default: statusText = "错误"; statusClass = "status-error";
    }

    tr.innerHTML = `<td><span class="region-badge ${regionClass}">${regionLabel}</span></td><td>${escapeHtml(r.name)}</td><td>${escapeHtml(r.host)}</td><td>${escapeHtml(r.ip || "-")}</td><td class="${latencyClass}">${latencies}</td><td>${r.loss_rate}%</td><td><span class="status-badge ${statusClass}">${statusText}</span></td>`;
    fragment.appendChild(tr);
  });
  tbody.appendChild(fragment);
}

async function runCustomTest(action) {
  const target = document.getElementById("custom-target").value.trim();
  if (!target) {
    showToast("请输入 IP 或域名", "error");
    return;
  }

  const pingBtn = document.getElementById("custom-ping-btn");
  const nslookupBtn = document.getElementById("custom-nslookup-btn");
  const btns = [pingBtn, nslookupBtn];
  btns.forEach(b => { if (b) b.disabled = true; });

  try {
    const res = await apiFetch("/api/speedtest/custom", {
      method: "POST",
      body: JSON.stringify({ target, action }),
    });

    if (res && res.success) {
      renderCustomResult(res.data, action);
    }
  } finally {
    btns.forEach(b => { if (b) b.disabled = false; });
  }
}

function renderCustomResult(data, action) {
  const container = document.getElementById("custom-result");
  if (!container) return;
  container.style.display = "";

  const nslookupCard = document.getElementById("custom-result-nslookup");
  const pingCard = document.getElementById("custom-result-ping");
  const nslookupBody = document.getElementById("nslookup-body");
  const pingBody = document.getElementById("ping-body");

  if (action === "nslookup" || action === "all") {
    if (data.nslookup) {
      nslookupCard.style.display = "";
      nslookupBody.innerHTML = renderNslookup(data.nslookup);
    }
  }

  if (action === "ping" || action === "all") {
    if (data.ping) {
      pingCard.style.display = "";
      pingBody.innerHTML = renderPing(data.ping);
    }
  }
}

function renderNslookup(raw) {
  const lines = raw.split("\n");
  let server = "";
  const addresses = [];
  let inRecord = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    const lower = line.toLowerCase();
    if (!line) continue;

    if (lower.includes("dns request timed out") || lower.includes("timed out")) {
      return '<div class="result-empty">DNS 请求超时，请检查网络连接</div>';
    }
    if (lower.includes("can't find") || lower.includes("non-existent domain") || lower.includes("找不到") || lower.includes("不存在")) {
      return '<div class="result-empty">域名解析失败，请检查域名是否正确</div>';
    }

    const serverMatch = line.match(/^(?:默认服务器|default server|server)\s*:\s*(.+)/i);
    if (serverMatch) {
      if (!server) server = serverMatch[1];
      continue;
    }

    const nameMatch = line.match(/^(?:名称|name)\s*:\s*(.+)/i);
    if (nameMatch) {
      inRecord = true;
      continue;
    }

    if (!inRecord) continue;

    const addrMatch = line.match(/^address(?:es)?\s*:\s*(.+)/i);
    if (addrMatch) {
      const parts = addrMatch[1].split(/[\s,]+/).filter(p => p);
      parts.forEach(addr => {
        const clean = addr.replace(/,$/, "").trim();
        if (clean && isValidIp(clean)) {
          addresses.push({ addr: clean, type: clean.includes(":") ? "IPv6" : "IPv4" });
        }
      });
      continue;
    }

    if (isValidIp(line)) {
      addresses.push({ addr: line, type: line.includes(":") ? "IPv6" : "IPv4" });
    }
  }

  if (addresses.length === 0) {
    if (server) {
      return '<div class="result-empty">未找到解析记录</div>';
    }
    return '<div class="result-empty">暂无测试结果，请点击 Ping/Nslookup 按钮开始测试</div>';
  }

  let html = "";

  if (server) {
    html += '<div class="result-section">';
    html += '<div class="result-server">';
    html += '<span class="result-server-label">DNS 服务器</span>';
    html += '<span class="result-server-value">' + escapeHtml(server) + "</span>";
    html += "</div>";
    html += "</div>";
  }

  html += '<div class="result-section">';
  html += '<div class="result-addr-header">解析结果</div>';
  html += '<div class="result-addr-list">';
  addresses.forEach((a, i) => {
    const cls = i % 2 === 1 ? "result-addr-row alt" : "result-addr-row";
    const typeClass = a.type === "IPv6" ? "addr-type-ipv6" : "addr-type-ipv4";
    html += '<div class="' + cls + '">';
    html += '<span class="result-addr-ip">' + escapeHtml(a.addr) + "</span>";
    html += '<span class="result-addr-type ' + typeClass + '">' + a.type + "</span>";
    html += "</div>";
  });
  html += "</div>";
  html += "</div>";

  return html;
}

function isValidIp(s) {
  if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(s)) {
    return s.split(".").every(n => parseInt(n, 10) <= 255);
  }
  if (/^[0-9a-f:]+$/i.test(s) && s.includes(":")) {
    return true;
  }
  return false;
}

function renderPing(p) {
  if (p.status === "error") {
    return '<div class="result-empty">Ping 执行失败，请检查目标地址</div>';
  }
  if (p.status === "dns_fail" || p.status === "timeout") {
    return '<div class="result-empty">无法连通目标主机</div>';
  }

  const latencies = p.min_ms != null ? `${p.min_ms} / ${p.avg_ms} / ${p.max_ms}` : "—";
  const hasLatency = p.avg_ms != null;
  const latencyLevel = hasLatency ? getLatencyLevel(p.avg_ms) : "none";
  const lossLevel = getLossLevel(p.loss_rate);

  let html = "";

  html += '<div class="result-section">';
  html += '<div class="result-grid">';

  html += '<div class="result-grid-item">';
  html += '<div class="rgi-label">目标</div>';
  html += '<div class="rgi-value">' + escapeHtml(p.host) + "</div>";
  html += "</div>";

  html += '<div class="result-grid-item">';
  html += '<div class="rgi-label">IP 地址</div>';
  html += '<div class="rgi-value rgi-value-mono">' + escapeHtml(p.ip || "—") + "</div>";
  html += "</div>";

  html += '<div class="result-grid-item">';
  html += '<div class="rgi-label">发送 / 接收</div>';
  html += '<div class="rgi-value">' + p.sent + " / " + (p.received != null ? p.received : 0) + "</div>";
  html += "</div>";

  html += '<div class="result-grid-item">';
  html += '<div class="rgi-label">丢包率</div>';
  html += '<div class="rgi-value">';
  html += '<div class="loss-bar-wrap">';
  html += '<div class="loss-bar-track">';
  html += '<div class="loss-bar-fill ' + lossLevel + '" style="width:' + p.loss_rate + '%"></div>';
  html += "</div>";
  html += '<span class="loss-bar-text ' + lossLevel + '">' + p.loss_rate + "%</span>";
  html += "</div>";
  html += "</div>";
  html += "</div>";

  html += '<div class="result-grid-item result-grid-full">';
  html += '<div class="rgi-label">延迟（最小 / 平均 / 最大）</div>';
  html += '<div class="rgi-value">';
  if (hasLatency) {
    html += '<span class="latency-display">';
    html += '<span class="latency-val">' + latencies + '</span>';
    html += '<span class="latency-unit"> ms</span>';
    html += '<span class="latency-badge ' + latencyLevel + '">' + latencyLabel(latencyLevel) + "</span>";
    html += "</span>";
  } else {
    html += '<span class="rgi-value-mono">—</span>';
  }
  html += "</div>";
  html += "</div>";

  html += '<div class="result-grid-item result-grid-full">';
  html += '<div class="rgi-label">状态</div>';
  html += '<div class="rgi-value"><span class="result-status-tag ' + p.status + '">' + statusText(p.status) + "</span></div>";
  html += "</div>";

  html += "</div>";
  html += "</div>";

  return html;
}

function getLatencyLevel(ms) {
  if (ms < 50) return "low";
  if (ms < 150) return "mid";
  return "high";
}

function latencyLabel(level) {
  switch (level) {
    case "low": return "低延迟";
    case "mid": return "中等延迟";
    case "high": return "高延迟";
    default: return "";
  }
}

function getLossLevel(pct) {
  if (pct === 0) return "none";
  if (pct < 10) return "low";
  if (pct < 50) return "mid";
  return "high";
}

function statusText(status) {
  switch (status) {
    case "ok": return "正常";
    case "partial": return "部分丢包";
    case "timeout": return "超时";
    case "dns_fail": return "解析失败";
    default: return "错误";
  }
}

async function runResolveTest() {
  const input = document.getElementById("resolve-target");
  const resultEl = document.getElementById("resolve-result");
  const btn = document.getElementById("resolve-run-btn");
  if (!input || !resultEl) return;
  const target = input.value.trim();
  if (!target) return showToast("请输入要解析的域名或 IP", "error");

  if (btn) {
    btn.disabled = true;
    btn.textContent = "解析中...";
  }
  resultEl.innerHTML = '<div class="empty-hint">正在解析...</div>';
  try {
    const res = await apiFetch("/api/speedtest/resolve", {
      method: "POST",
      body: JSON.stringify({ target }),
    });
    if (!res || !res.success) {
      resultEl.innerHTML = '<div class="empty-hint">解析失败</div>';
      return;
    }
    resultEl.innerHTML = renderResolveResult(res.data);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "解析测速";
    }
  }
}

function renderResolveResult(data) {
  const addresses = data.addresses || [];
  const addrHtml = addresses.length
    ? addresses.map(item => `<span>${escapeHtml(item.family)} · ${escapeHtml(item.ip)}</span>`).join("")
    : "<span>无解析结果</span>";
  return `
    <div class="module-result-head">
      <strong>${escapeHtml(data.target)}</strong>
      <span>${data.elapsed_ms || 0} ms</span>
    </div>
    ${data.error ? `<div class="module-alert warning">${escapeHtml(data.error)}</div>` : ""}
    <div class="module-chip-row">${addrHtml}</div>
  `;
}

import { apiFetch, escapeHtml, showToast, setText, bindEvent } from "./utils.js";

const CACHE_KEY = "winoperation_insights_snapshot";

let lastSnapshot = null;
let activeFilter = "all";
let searchTerm = "";
let insightsInitialized = false;

function readCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function saveCache(snapshot) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(snapshot));
  } catch (e) {}
}

function severityText(severity) {
  return {
    critical: "紧急",
    warning: "关注",
    ok: "正常",
    info: "信息",
  }[severity] || "信息";
}

function scoreClass(score) {
  if (score >= 85) return "ok";
  if (score >= 70) return "warning";
  return "critical";
}

function primitiveEntries(metrics) {
  return Object.entries(metrics || {})
    .filter(([, value]) => value == null || ["string", "number", "boolean"].includes(typeof value))
    .slice(0, 8);
}

function renderProcessRows(processes) {
  if (!processes || processes.length === 0) return "";
  const rows = processes.slice(0, 5).map(proc => `
    <tr>
      <td><span class="proc-name">${escapeHtml(proc.name || "")}</span></td>
      <td><span class="proc-pid">${proc.pid || 0}</span></td>
      <td>${proc.cpu || 0}%</td>
      <td>${proc.memory_mb || 0} MB</td>
    </tr>
  `).join("");
  return `
    <div class="insight-table-wrap">
      <table class="proc-table insight-mini-table">
        <thead><tr><th>进程</th><th>PID</th><th>CPU</th><th>内存</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderCoreHeatmap(cores) {
  if (!cores || cores.length === 0) return "";
  const cells = cores.map(core => {
    const load = Math.max(0, Math.min(100, Number(core.load || 0)));
    const tone = load >= 90 ? "critical" : load >= 75 ? "warning" : "ok";
    return `
      <div class="insight-core-cell ${tone}" title="Core ${escapeHtml(core.core_index || "")}: ${load}%">
        <span style="height:${Math.max(8, load)}%"></span>
        <small>${escapeHtml(core.core_index || "")}</small>
      </div>
    `;
  }).join("");
  return `<div class="insight-core-grid">${cells}</div>`;
}

function renderDiskRows(disks) {
  if (!disks || disks.length === 0) return "";
  return `
    <div class="insight-disk-list">
      ${disks.slice(0, 5).map(disk => {
        const pct = Math.max(0, Math.min(100, Number(disk.percent || 0)));
        const tone = pct >= 90 ? "critical" : pct >= 80 ? "warning" : "ok";
        return `
          <div class="insight-disk-row">
            <span>${escapeHtml(disk.device || "?")}</span>
            <div class="bar-track"><div class="bar-fill ${tone === "critical" ? "high" : tone === "warning" ? "mid" : "low"}" style="width:${pct}%"></div></div>
            <strong>${pct}%</strong>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderChips(values) {
  if (!values || values.length === 0) return "";
  return `<div class="insight-chip-row">${values.slice(0, 8).map(value => `<span>${escapeHtml(value)}</span>`).join("")}</div>`;
}

function renderAdapterRows(adapters) {
  if (!adapters || adapters.length === 0) return "";
  const rows = adapters.slice(0, 5).map(adapter => `
    <div class="insight-adapter-row">
      <span>${escapeHtml(adapter.Name || adapter.InterfaceDescription || "Adapter")}</span>
      <strong>${escapeHtml(adapter.Status || "-")}</strong>
    </div>
  `).join("");
  return `<div class="insight-adapter-list">${rows}</div>`;
}

function renderAlertList(alerts) {
  if (!alerts || alerts.length === 0) return "";
  return `<ul class="insight-alert-list">${alerts.slice(0, 5).map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderKeyValues(metrics) {
  const entries = primitiveEntries(metrics);
  if (entries.length === 0) return "";
  return `
    <div class="insight-kv-grid">
      ${entries.map(([key, value]) => `
        <span>${escapeHtml(key)}</span>
        <strong>${escapeHtml(String(value == null ? "-" : value))}</strong>
      `).join("")}
    </div>
  `;
}

function renderFeatureDetails(feature) {
  const metrics = feature.metrics || {};
  if (metrics.processes) return renderProcessRows(metrics.processes);
  if (metrics.cores) return renderCoreHeatmap(metrics.cores);
  if (metrics.disks) return renderDiskRows(metrics.disks);
  if (metrics.critical || metrics.warning) return renderDiskRows([...(metrics.critical || []), ...(metrics.warning || [])]);
  if (metrics.servers) return renderChips(metrics.servers);
  if (metrics.adapters) return renderAdapterRows(metrics.adapters);
  if (metrics.alerts) return renderAlertList(metrics.alerts);
  return renderKeyValues(metrics);
}

function featureMatches(feature) {
  const filterOk = activeFilter === "all" || feature.severity === activeFilter;
  if (!filterOk) return false;
  if (!searchTerm) return true;
  const haystack = [
    feature.title,
    feature.value,
    feature.detail,
    feature.status_label,
    JSON.stringify(feature.metrics || {}),
  ].join(" ").toLowerCase();
  return haystack.includes(searchTerm.toLowerCase());
}

function renderSummary(snapshot) {
  const summary = snapshot.summary || {};
  const score = Number(summary.health_score || 0);
  const tone = scoreClass(score);
  const panel = document.getElementById("insights-score-panel");
  if (panel) {
    panel.classList.remove("ok", "warning", "critical");
    panel.classList.add(tone);
  }
  setText("insights-score", score + "");
  setText("insights-status", summary.status || "-");
  setText("insights-generated", snapshot.generated_at || "-");
  setText("insights-critical-count", summary.critical_count || 0);
  setText("insights-warning-count", summary.warning_count || 0);
  setText("insights-feature-count", snapshot.feature_count || 0);

  const recEl = document.getElementById("insights-recommendations");
  if (!recEl) return;
  const recommendations = summary.recommendations || [];
  if (recommendations.length === 0) {
    recEl.innerHTML = '<div class="empty-hint">暂无特别建议，系统状态保持良好。</div>';
    return;
  }
  recEl.innerHTML = recommendations.map(item => `
    <div class="insight-recommendation">
      <span></span>
      <p>${escapeHtml(item)}</p>
    </div>
  `).join("");
}

function renderFeatures(snapshot) {
  const grid = document.getElementById("insights-feature-grid");
  if (!grid) return;

  const features = (snapshot.features || []).filter(featureMatches);
  if (features.length === 0) {
    grid.innerHTML = `
      <div class="insights-loading-card">
        <div class="empty-hint">没有匹配的巡检项</div>
      </div>
    `;
    return;
  }

  grid.innerHTML = features.map((feature, idx) => {
    const featureId = feature.id || ("feature-" + idx);
    return `
    <article class="insight-card preview-insight-card ${escapeHtml(feature.severity || "info")}" data-feature-id="${escapeHtml(featureId)}">
      <div class="insight-card-head">
        <div>
          <span class="insight-status ${escapeHtml(feature.severity || "info")}">${severityText(feature.severity)}</span>
          <h3>${escapeHtml(feature.title || "")}</h3>
        </div>
        <strong>${escapeHtml(feature.value || "-")}</strong>
      </div>
      <p class="insight-detail">${escapeHtml(feature.detail || "")}</p>
      ${renderFeatureDetails(feature)}
    </article>
  `;
  }).join("");
}

function renderSnapshot(snapshot) {
  if (!snapshot) return;
  lastSnapshot = snapshot;
  renderSummary(snapshot);
  renderFeatures(snapshot);
}

export async function loadInsights(force = false) {
  if (!force && !lastSnapshot) {
    const cache = readCache();
    if (cache) renderSnapshot(cache);
  }

  const btn = document.getElementById("insights-refresh-btn");
  if (btn) btn.classList.add("spinning");

  const payload = await apiFetch("/api/insights/snapshot", { silent: true });
  if (btn) btn.classList.remove("spinning");

  if (!payload || !payload.success) {
    showToast("巡检数据获取失败", "error");
    return;
  }
  saveCache(payload.data);
  renderSnapshot(payload.data);
}

function exportReport() {
  if (!lastSnapshot) {
    showToast("请先生成巡检报告", "error");
    return;
  }
  const blob = new Blob([JSON.stringify(lastSnapshot, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `winoperation-inspection-${Date.now()}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast("巡检报告已导出", "success");
}

function bindFilters() {
  const group = document.getElementById("insights-filter-group");
  if (!group) return;
  group.addEventListener("click", event => {
    const btn = event.target.closest(".insights-filter");
    if (!btn) return;
    activeFilter = btn.getAttribute("data-filter") || "all";
    group.querySelectorAll(".insights-filter").forEach(item => item.classList.remove("active"));
    btn.classList.add("active");
    renderFeatures(lastSnapshot || { features: [] });
  });
}

export function initInsights() {
  if (insightsInitialized) {
    loadInsights();
    return;
  }
  insightsInitialized = true;
  bindEvent("insights-refresh-btn", "click", () => loadInsights(true));
  bindEvent("insights-export-btn", "click", exportReport);
  bindEvent("insights-search", "input", event => {
    searchTerm = event.target.value.trim();
    renderFeatures(lastSnapshot || { features: [] });
  });
  bindFilters();
  loadInsights();
}

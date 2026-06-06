# Merge Inspection Into Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the inspection module into the overview dashboard while preserving inspection refresh, export, filter, search, and detail rendering.

**Architecture:** Keep the existing `/api/insights/snapshot` backend and `static/js/insights.js` renderer. Move the inspection DOM into `templates/_tab_dashboard.html`, remove the standalone navigation entry and standalone include, and let `Dashboard.startDashboard()` initialize/load inspection data alongside dashboard data.

**Tech Stack:** Flask/Jinja templates, vanilla ES modules, CSS, Python `unittest`, Node syntax checks, in-app Browser verification.

---

## File Structure

- Modify `templates/_topnav.html`: remove the direct `巡检` top navigation item.
- Modify `templates/dashboard.html`: remove the standalone `_tab_insights.html` include.
- Modify `templates/_tab_dashboard.html`: embed the inspection summary, controls, and detail grid as an overview card.
- Modify `static/js/dashboard.js`: import inspection initialization/loading and run inspection as part of dashboard start/refresh.
- Modify `static/js/tabs.js`: remove normal `tab-insights` switching and redirect old `#tab-insights` routes to `tab-dashboard`.
- Modify `static/css/tab-insights.css`: make inspection cards fit overview card styling.
- Add `tests/test_dashboard_insights_merge.py`: structural tests for navigation, dashboard template, dashboard JS, and tab routing.

---

### Task 1: Add Failing Merge Tests

**Files:**
- Create: `tests/test_dashboard_insights_merge.py`

- [ ] **Step 1: Write the failing tests**

```python
import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


class DashboardInsightsMergeTests(unittest.TestCase):
    def test_topnav_no_longer_exposes_standalone_insights(self):
        topnav = read_file("templates/_topnav.html")

        self.assertNotIn('data-tab="tab-insights"', topnav)
        self.assertNotRegex(topnav, r">\s*巡检\s*<")

    def test_dashboard_embeds_inspection_card_and_controls(self):
        dashboard = read_file("templates/_tab_dashboard.html")
        outer = read_file("templates/dashboard.html")

        self.assertIn("dashboard-insights-card", dashboard)
        self.assertIn("insights-score-panel", dashboard)
        self.assertIn("insights-filter-group", dashboard)
        self.assertIn("insights-search", dashboard)
        self.assertIn("insights-feature-grid", dashboard)
        self.assertNotIn('{% include "_tab_insights.html" %}', outer)

    def test_dashboard_starts_and_refreshes_inspection_data(self):
        script = read_file("static/js/dashboard.js")

        self.assertIn('import { initInsights, loadInsights } from "./insights.js";', script)
        self.assertRegex(script, r"startDashboard\(\)\s*\{(?P<body>.*?)initInsights\(\)", re.S)
        self.assertRegex(script, r"refreshDashboard\(\)\s*\{(?P<body>.*?)loadInsights\(true\)", re.S)

    def test_old_inspection_hash_redirects_to_dashboard(self):
        script = read_file("static/js/tabs.js")

        self.assertIn('if (tabId === "tab-insights") tabId = "tab-dashboard";', script)
        self.assertNotIn('ensureInit("tab-insights"', script)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_dashboard_insights_merge -v`

Expected: FAIL because the standalone inspection nav/include still exists and dashboard does not initialize inspection.

---

### Task 2: Merge Inspection Markup Into Overview

**Files:**
- Modify: `templates/_topnav.html`
- Modify: `templates/dashboard.html`
- Modify: `templates/_tab_dashboard.html`

- [ ] **Step 1: Remove standalone inspection navigation**

Delete the top navigation block whose direct item has `data-tab="tab-insights"` and text `巡检`.

- [ ] **Step 2: Remove standalone inspection tab include**

Delete this line from `templates/dashboard.html`:

```jinja
{% include "_tab_insights.html" %}
```

- [ ] **Step 3: Embed inspection card in the dashboard tab**

Add this card inside `templates/_tab_dashboard.html` under the existing dashboard cards:

```html
        <div class="card dashboard-insights-card">
          <div class="card-header">
            <span class="card-number">Inspect</span>
            <h3>系统巡检 <span class="badge-live">Python</span></h3>
            <div class="card-actions">
              <button id="insights-export-btn" class="btn btn-sm btn-secondary">导出报告</button>
              <button id="insights-refresh-btn" class="dash-refresh-btn" title="刷新巡检">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              </button>
            </div>
          </div>
          <div class="card-body">
            <div class="insights-summary-grid dashboard-insights-summary">
              <div class="insights-score-panel" id="insights-score-panel">
                <div class="insights-score-label">健康评分</div>
                <div class="insights-score-value" id="insights-score">--</div>
                <div class="insights-score-status" id="insights-status">等待巡检</div>
              </div>
              <div class="insights-summary-metrics">
                <div class="insights-mini-stat">
                  <span class="stat-label">生成时间</span>
                  <strong id="insights-generated">-</strong>
                </div>
                <div class="insights-mini-stat">
                  <span class="stat-label">紧急项</span>
                  <strong id="insights-critical-count">0</strong>
                </div>
                <div class="insights-mini-stat">
                  <span class="stat-label">关注项</span>
                  <strong id="insights-warning-count">0</strong>
                </div>
                <div class="insights-mini-stat">
                  <span class="stat-label">功能项</span>
                  <strong id="insights-feature-count">20</strong>
                </div>
              </div>
            </div>

            <div class="insights-recommendations" id="insights-recommendations">
              <div class="empty-hint">正在生成巡检建议...</div>
            </div>

            <div class="insights-toolbar dashboard-insights-toolbar">
              <div class="insights-filter-group" id="insights-filter-group">
                <button class="insights-filter active" data-filter="all">全部</button>
                <button class="insights-filter" data-filter="critical">紧急</button>
                <button class="insights-filter" data-filter="warning">关注</button>
                <button class="insights-filter" data-filter="ok">正常</button>
                <button class="insights-filter" data-filter="info">信息</button>
              </div>
              <input id="insights-search" class="insights-search" type="search" placeholder="搜索巡检项、进程、网卡、DNS">
            </div>

            <div id="insights-feature-grid" class="insights-feature-grid">
              <div class="card insights-loading-card">
                <div class="card-body">
                  <div class="empty-hint">正在载入 20 项智能巡检...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
```

- [ ] **Step 4: Run merge tests**

Run: `python -m unittest tests.test_dashboard_insights_merge -v`

Expected: tests still fail until JS is updated.

---

### Task 3: Wire Inspection Into Dashboard Lifecycle

**Files:**
- Modify: `static/js/dashboard.js`
- Modify: `static/js/tabs.js`

- [ ] **Step 1: Import inspection functions into dashboard JS**

Change the first import in `static/js/dashboard.js` to include the inspection module:

```javascript
import { apiFetch, setText, setBar, escapeHtml, bindEvent } from "./utils.js";
import { initInsights, loadInsights } from "./insights.js";
```

- [ ] **Step 2: Initialize inspection when the dashboard starts**

Add `initInsights();` inside `Dashboard.startDashboard()` after `renderDashboardCache();`:

```javascript
  startDashboard() {
    this.stop();
    renderDashboardCache();
    initInsights();
    this.fetchAll();
  },
```

- [ ] **Step 3: Refresh inspection with the dashboard refresh button**

Add `loadInsights(true)` to `Dashboard.refreshDashboard()`:

```javascript
  refreshDashboard() {
    const btn = document.getElementById('dash-refresh-btn');
    if (btn) btn.classList.add('spinning');
    Promise.allSettled([this.fetchAll(), loadInsights(true)]).then(() => {
      if (btn) btn.classList.remove('spinning');
    });
  },
```

- [ ] **Step 4: Prevent duplicate inspection fetches during background dashboard fetches**

Keep `Dashboard.fetchAll()` focused on current overview data and do not add `loadInsights()` there. This avoids double inspection calls because `initInsights()` already loads inspection once.

- [ ] **Step 5: Redirect old inspection tab IDs**

At the start of `switchTab(tabId, updateHash = true)` in `static/js/tabs.js`, add:

```javascript
  if (tabId === "tab-insights") tabId = "tab-dashboard";
```

Remove the branch that calls:

```javascript
ensureInit("tab-insights", initInsights, loadInsights);
```

- [ ] **Step 6: Run merge tests**

Run: `python -m unittest tests.test_dashboard_insights_merge -v`

Expected: PASS.

---

### Task 4: Align Inspection Styles With Overview

**Files:**
- Modify: `static/css/tab-insights.css`
- Modify: `static/css/tab-dashboard-overview.css`

- [ ] **Step 1: Add overview-specific inspection layout styles**

Add these selectors to `static/css/tab-dashboard-overview.css`:

```css
.card-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.dashboard-insights-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dashboard-insights-summary {
  grid-template-columns: minmax(180px, 240px) 1fr;
}

.dashboard-insights-toolbar {
  margin-top: 0;
}
```

- [ ] **Step 2: Ensure inspection detail cards look like overview mini-cards**

Adjust `static/css/tab-insights.css` so `.insight-card` uses overview-compatible `background: var(--surface)`, `border: 1px solid var(--border)`, `border-radius: var(--radius)`, compact padding, and no oversized standalone-report treatment.

- [ ] **Step 3: Ensure mobile layout stays single-column**

Add or keep responsive rules so `.dashboard-insights-summary`, `.insights-summary-metrics`, `.insights-toolbar`, and `.insights-feature-grid` collapse cleanly below `768px`.

- [ ] **Step 4: Run CSS structural check**

Run: `python -m unittest tests.test_dashboard_insights_merge -v`

Expected: PASS.

---

### Task 5: Full Verification

**Files:**
- Verify: all touched files

- [ ] **Step 1: Run Python tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 2: Run JavaScript syntax checks**

Run:

```powershell
node --check static\js\dashboard.js
node --check static\js\tabs.js
node --check static\js\insights.js
```

Expected: each command exits with code 0 and prints no syntax errors.

- [ ] **Step 3: Compile Python sources**

Run: `python -m compileall src tests`

Expected: compile succeeds with no Python syntax errors.

- [ ] **Step 4: Verify in the in-app Browser**

Open `http://127.0.0.1:2234/`, inspect the overview tab, and verify:

- The top nav has no standalone `巡检` item.
- The overview tab shows a `系统巡检` card.
- The inspection score and feature count render from `/api/insights/snapshot`.
- The inspection refresh button works.
- The filter buttons and search input update the embedded detail grid.
- Visiting `#tab-insights` displays the overview tab.

# HTML 模板解耦合 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `templates/dashboard.html` (851 lines) into focused Jinja2 partial templates, keeping DOM structure and JS behavior unchanged.

**Architecture:** Extract each tab-content `<div>` and shared sections (nav, modal) into separate `_*.html` partials in `templates/`, then reassemble them in `dashboard.html` via `{% include %}`. Flask backend, CSS, JS, and build script are untouched.

**Tech Stack:** Flask 2.x / Jinja2 (included in the existing project)

---

### Task 1: Extract exit modal

**Files:**
- Create: `templates/_modals.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_modals.html`**

Copy the exit modal block from `dashboard.html` lines 841-849 into a new file:

```html
<!-- Exit confirmation modal -->
<div id="exit-modal" class="modal-overlay">
  <div class="modal-box">
    <p class="modal-text">是否确认退出？</p>
    <div class="modal-actions">
      <button id="exit-confirm-btn" class="btn btn-danger">确认</button>
      <button id="exit-cancel-btn" class="btn btn-secondary">取消</button>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Replace modal block in `dashboard.html` with include**

In `dashboard.html`, replace lines 841-849 with:

```jinja2
{% include "_modals.html" %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/_modals.html templates/dashboard.html
git commit -m "refactor: extract exit modal into _modals.html partial"
```

---

### Task 2: Extract top navigation

**Files:**
- Create: `templates/_topnav.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_topnav.html`**

Copy the `<nav class="topnav">` block from `dashboard.html` lines 5-75 into a new file. Content is the entire `<nav>...</nav>` element.

- [ ] **Step 2: Replace nav block in `dashboard.html` with include**

In `dashboard.html`, replace the nav block with:

```jinja2
{% include "_topnav.html" %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/_topnav.html templates/dashboard.html
git commit -m "refactor: extract top navigation into _topnav.html partial"
```

---

### Task 3: Extract quick settings tab (smallest tab)

**Files:**
- Create: `templates/_tab_quick.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_quick.html`**

Copy the `<div id="tab-quick" class="tab-content">...</div>` block from `dashboard.html` lines 532-546 into a new file.

- [ ] **Step 2: Replace with include in `dashboard.html`**

Replace the tab-quick block with:

```jinja2
{% include "_tab_quick.html" %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_quick.html templates/dashboard.html
git commit -m "refactor: extract quick settings tab into _tab_quick.html"
```

---

### Task 4: Extract app uninstall tab

**Files:**
- Create: `templates/_tab_app_uninstall.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_app_uninstall.html`**

Copy tab-app-uninstall block (`dashboard.html` lines 702-716).

- [ ] **Step 2: Replace with include**

```jinja2
{% include "_tab_app_uninstall.html" %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_app_uninstall.html templates/dashboard.html
git commit -m "refactor: extract app uninstall tab into _tab_app_uninstall.html"
```

---

### Task 5: Extract update tab

**Files:**
- Create: `templates/_tab_update.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_update.html`**

Copy tab-update block (`dashboard.html` lines 719-754).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_update.html templates/dashboard.html
git commit -m "refactor: extract update tab into _tab_update.html"
```

---

### Task 6: Extract Win11 tab

**Files:**
- Create: `templates/_tab_win11.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_win11.html`**

Copy tab-win11 block (`dashboard.html` lines 757-837).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_win11.html templates/dashboard.html
git commit -m "refactor: extract Win11 tab into _tab_win11.html"
```

---

### Task 7: Extract power tab

**Files:**
- Create: `templates/_tab_power.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_power.html`**

Copy tab-power block (`dashboard.html` lines 426-460).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_power.html templates/dashboard.html
git commit -m "refactor: extract power tab into _tab_power.html"
```

---

### Task 8: Extract shutdown tab

**Files:**
- Create: `templates/_tab_shutdown.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_shutdown.html`**

Copy tab-shutdown block (`dashboard.html` lines 463-529).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_shutdown.html templates/dashboard.html
git commit -m "refactor: extract shutdown tab into _tab_shutdown.html"
```

---

### Task 9: Extract system status tab

**Files:**
- Create: `templates/_tab_system_status.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_system_status.html`**

Copy tab-system-status block (`dashboard.html` lines 282-341).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_system_status.html templates/dashboard.html
git commit -m "refactor: extract system status tab into _tab_system_status.html"
```

---

### Task 10: Extract speedtest tab

**Files:**
- Create: `templates/_tab_speedtest.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_speedtest.html`**

Copy tab-speedtest block (`dashboard.html` lines 549-625).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_speedtest.html templates/dashboard.html
git commit -m "refactor: extract speedtest tab into _tab_speedtest.html"
```

---

### Task 11: Extract network tab

**Files:**
- Create: `templates/_tab_network.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_network.html`**

Copy tab-network block (`dashboard.html` lines 344-423).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_network.html templates/dashboard.html
git commit -m "refactor: extract network tab into _tab_network.html"
```

---

### Task 12: Extract activation tab

**Files:**
- Create: `templates/_tab_activation.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_activation.html`**

Copy tab-activation block (`dashboard.html` lines 628-699).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_activation.html templates/dashboard.html
git commit -m "refactor: extract activation tab into _tab_activation.html"
```

---

### Task 13: Extract dashboard tab (largest tab)

**Files:**
- Create: `templates/_tab_dashboard.html`
- Modify: `templates/dashboard.html`

- [ ] **Step 1: Create `_tab_dashboard.html`**

Copy tab-dashboard block (`dashboard.html` lines 81-279).

- [ ] **Step 2: Replace with include**

- [ ] **Step 3: Commit**

```bash
git add templates/_tab_dashboard.html templates/dashboard.html
git commit -m "refactor: extract dashboard tab into _tab_dashboard.html"
```

---

### Task 14: Final cleanup and verification

**Files:**
- Modify: none (read-only verification)

- [ ] **Step 1: Verify `dashboard.html` structure**

Read the final `dashboard.html` — it should contain only:

```jinja2
{% extends "base.html" %}
{% block content %}
<div class="dashboard">
  {% include "_topnav.html" %}
  <div class="main-content">
    {% include "_tab_dashboard.html" %}
    {% include "_tab_system_status.html" %}
    {% include "_tab_network.html" %}
    {% include "_tab_power.html" %}
    {% include "_tab_shutdown.html" %}
    {% include "_tab_quick.html" %}
    {% include "_tab_speedtest.html" %}
    {% include "_tab_activation.html" %}
    {% include "_tab_app_uninstall.html" %}
    {% include "_tab_update.html" %}
    {% include "_tab_win11.html" %}
  </div>
  {% include "_modals.html" %}
</div>
{% endblock %}
```

- [ ] **Step 2: Verify line count**

```bash
wc -l templates/*.html
```

Expected: `dashboard.html` ~25 lines, no single file over ~200 lines.

- [ ] **Step 3: Final commit**

```bash
git add templates/ docs/superpowers/plans/
git commit -m "refactor: complete HTML template decoupling into 14 partials"
```

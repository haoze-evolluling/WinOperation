# Font Size Unification & Redundant Code Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify 30+ scattered font-size values into an 8-level CSS variable system, remove deprecated sidebar variables, redundant font-family declarations, and non-standard font-weight values.

**Architecture:** Define 8 `--text-*` CSS custom properties in `theme.css`, then replace hardcoded values across 14 CSS files. Simultaneously clean up deprecated variables and redundant declarations.

**Tech Stack:** CSS custom properties, no build tools required.

---

## File Map

| File | Responsibility | Changes |
|------|---------------|---------|
| `static/css/theme.css` | Central theme variables | Add 8 `--text-*` vars, remove 6 `--sidebar-*` vars |
| `static/css/dark-theme.css` | Dark mode overrides | Remove 4 sidebar var overrides |
| `static/css/base-reset-typography.css` | Global reset & typography | Form input `font-size` → variable |
| `static/css/components-buttons.css` | Button & toggle system | Font sizes → vars, remove redundant `font-family` |
| `static/css/components-cards-info.css` | Cards, stats, form layout | Font sizes → vars, remove redundant `font-family`, fix `font-weight: 450` |
| `static/css/components-toast.css` | Toast notifications | Remove redundant `font-family`, font-size → var |
| `static/css/components-animations.css` | Animation system | `font-size` → variable |
| `static/css/layout-topnav.css` | Top navigation layout | Font sizes → vars, remove redundant `font-family` |
| `static/css/tab-dashboard-overview.css` | Dashboard overview tab | Many font sizes → vars |
| `static/css/tab-network-dns.css` | Network & DNS tab | Font sizes → vars, remove redundant `font-family` |
| `static/css/tab-quick-settings.css` | Quick settings tab | Font sizes → vars, remove redundant `font-family` |
| `static/css/tab-shutdown-scheduler.css` | Shutdown scheduler tab | Font sizes → vars, remove redundant `font-family` |
| `static/css/tab-speedtest.css` | Speed test tab | Many font sizes → vars |
| `static/css/tab-activation.css` | Activation wizard tab | Font sizes → vars, remove redundant `font-family` |
| `static/css/tab-app-uninstall.css` | App uninstall tab | Font size → variable |
| `static/css/responsive-breakpoints.css` | Responsive overrides | Responsive font-size overrides → vars |

---

### Task 1: Add font-size variables to theme.css

**Files:**
- Modify: `static/css/theme.css`

- [ ] **Step 1: Add 8 `--text-*` variables to `:root`**

Add the font size variables right after the existing `--font-mono` line and before the Spacing & Sizing section:

```css
  /* ---- Font Sizes ---- */
  --text-xs:   .68rem;
  --text-sm:   .75rem;
  --text-base: .82rem;
  --text-md:   .88rem;
  --text-lg:   1rem;
  --text-xl:   1.15rem;
  --text-2xl:  1.6rem;
  --text-3xl:  2rem;
```

- [ ] **Step 2: Remove deprecated sidebar variables**

Remove these 7 lines from `:root`:

```css
  /* ---- Sidebar (deprecated, kept for compat) ---- */
  --sidebar-bg: #ffffff;
  --sidebar-hover: #f1f5f9;
  --sidebar-active-bg: #cffafe;
  --sidebar-text: #64748b;
  --sidebar-active: #06b6d4;
```

Also remove `--sidebar-divider: #e2e8f0;` from the Surfaces section (line 70).

- [ ] **Step 3: Commit**

```bash
git add static/css/theme.css
git commit -m "feat(css): add 8-level font-size variables, remove deprecated sidebar vars"
```

---

### Task 2: Remove sidebar overrides from dark-theme.css

**Files:**
- Modify: `static/css/dark-theme.css`

- [ ] **Step 1: Remove sidebar variable overrides**

Remove these lines (around lines 33-37):

```css
  /* ---- Sidebar (deprecated) ---- */
  --sidebar-bg: #1a1a1a;
  --sidebar-hover: #2a2a2a;
  --sidebar-active-bg: rgba(6, 182, 212, 0.12);
  --sidebar-text: #94a3b8;
```

- [ ] **Step 2: Commit**

```bash
git add static/css/dark-theme.css
git commit -m "refactor(css): remove deprecated sidebar variable overrides from dark theme"
```

---

### Task 3: Update base-reset-typography.css

**Files:**
- Modify: `static/css/base-reset-typography.css`

- [ ] **Step 1: Replace hardcoded form input font-size**

Change line 70:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 2: Commit**

```bash
git add static/css/base-reset-typography.css
git commit -m "refactor(css): use --text-md variable for form input font-size"
```

---

### Task 4: Update components-buttons.css

**Files:**
- Modify: `static/css/components-buttons.css`

- [ ] **Step 1: Replace `.btn` font-size**

Change line 16:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Remove redundant `font-family` from `.btn`**

Remove line 18:
```css
  font-family: var(--font-sans);
```

- [ ] **Step 3: Replace `.btn-sm` font-size**

Change line 118:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 4: Replace `select` font-size and remove redundant `font-family`**

Change the `select` rule (line 154):
```css
  color: var(--text); font-size: .88rem;
```
To:
```css
  color: var(--text); font-size: var(--text-md);
```

Remove `font-family: var(--font-sans);` from line 157.

- [ ] **Step 5: Replace `.toggle-label` font-size**

Change line 168:
```css
.toggle-label { font-size: .9rem; color: var(--text); font-weight: 500; }
```
To:
```css
.toggle-label { font-size: var(--text-md); color: var(--text); font-weight: 500; }
```

- [ ] **Step 6: Commit**

```bash
git add static/css/components-buttons.css
git commit -m "refactor(css): buttons — use font-size vars, remove redundant font-family"
```

---

### Task 5: Update components-cards-info.css

**Files:**
- Modify: `static/css/components-cards-info.css`

- [ ] **Step 1: Replace `.card-header h3` font-size**

Change line 49:
```css
  font-size: 1.1rem;
```
To:
```css
  font-size: var(--text-lg);
```

- [ ] **Step 2: Replace `.card-number` font-size and remove redundant `font-family`**

Change line 57:
```css
  font-size: .6rem;
```
To:
```css
  font-size: var(--text-xs);
```

Remove `font-family: var(--font-sans);` from line 56.

- [ ] **Step 3: Replace `.card-body` font-size**

Change line 70:
```css
  font-size: .9rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 4: Replace `.info-grid` font-size**

Change line 121:
```css
  font-size: .9rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 5: Replace `.info-grid .label` font-size**

Change line 127:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 6: Fix `.info-grid .value` font-weight**

Change line 134:
```css
  font-weight: 450;
```
To:
```css
  font-weight: 400;
```

- [ ] **Step 7: Replace `.stat-large` font-size**

Change line 179:
```css
  font-size: 1.6rem;
```
To:
```css
  font-size: var(--text-2xl);
```

- [ ] **Step 8: Replace `.stat-label` font-size**

Change line 187:
```css
  font-size: .68rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 9: Replace `.status-indicator` font-size**

Change line 200:
```css
  font-size: .9rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 10: Replace `.status-tag` font-size**

Change line 238:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 11: Commit**

```bash
git add static/css/components-cards-info.css
git commit -m "refactor(css): cards — use font-size vars, remove redundant font-family, fix font-weight"
```

---

### Task 6: Update components-toast.css

**Files:**
- Modify: `static/css/components-toast.css`

- [ ] **Step 1: Replace `.toast` font-size and remove redundant `font-family`**

Change line 21-23:
```css
  font-family: var(--font-sans);
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Commit**

```bash
git add static/css/components-toast.css
git commit -m "refactor(css): toast — use font-size var, remove redundant font-family"
```

---

### Task 7: Update components-animations.css

**Files:**
- Modify: `static/css/components-animations.css`

- [ ] **Step 1: Replace `.loading-spinner` font-size**

Change line 123:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Commit**

```bash
git add static/css/components-animations.css
git commit -m "refactor(css): animations — use font-size var for loading spinner"
```

---

### Task 8: Update layout-topnav.css

**Files:**
- Modify: `static/css/layout-topnav.css`

- [ ] **Step 1: Replace `.topnav-brand-icon` font-size**

Change line 37:
```css
  font-size: 1.2rem;
```
To:
```css
  font-size: var(--text-xl);
```

- [ ] **Step 2: Replace `.topnav-brand h2` font-size and remove redundant `font-family`**

Change line 44:
```css
  font-size: 1.05rem;
```
To:
```css
  font-size: var(--text-lg);
```

Remove `font-family: var(--font-sans);` from line 49.

- [ ] **Step 3: Replace `.topnav-item` font-size and remove redundant `font-family`**

Change line 75:
```css
  font-size: 0.82rem;
```
To:
```css
  font-size: var(--text-base);
```

Remove `font-family: var(--font-sans);` from line 83.

- [ ] **Step 4: Replace `.topnav-item .topnav-icon` font-size**

Change line 99:
```css
  font-size: 0.85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 5: Replace `.topnav-dropdown-item` font-size and remove redundant `font-family`**

Change line 159:
```css
  font-size: 0.8rem;
```
To:
```css
  font-size: var(--text-base);
```

Remove `font-family: var(--font-sans);` from line 160.

- [ ] **Step 6: Replace `.topnav-exit` font-size and remove redundant `font-family`**

Change line 194:
```css
  font-size: 0.75rem;
```
To:
```css
  font-size: var(--text-sm);
```

Remove `font-family: var(--font-sans);` from line 196.

- [ ] **Step 7: Replace `.section-head h2` font-size and remove redundant `font-family`**

Change line 244:
```css
  font-size: 1.6rem;
```
To:
```css
  font-size: var(--text-2xl);
```

Remove `font-family: var(--font-sans);` from line 243.

- [ ] **Step 8: Replace `.modal-text` font-size and remove redundant `font-family`**

Change line 282:
```css
  font-size: 1.05rem;
```
To:
```css
  font-size: var(--text-lg);
```

Remove `font-family: var(--font-sans);` from line 281.

- [ ] **Step 9: Commit**

```bash
git add static/css/layout-topnav.css
git commit -m "refactor(css): topnav — use font-size vars, remove redundant font-family"
```

---

### Task 9: Update tab-dashboard-overview.css

**Files:**
- Modify: `static/css/tab-dashboard-overview.css`

- [ ] **Step 1: Replace `.dash-val` font-size**

Change line 21:
```css
  font-size: 1.3rem; font-weight: 700;
```
To:
```css
  font-size: var(--text-xl); font-weight: 700;
```

- [ ] **Step 2: Replace `.dash-val-sm` font-size**

Change line 27:
```css
  font-size: .92rem; font-weight: 600;
```
To:
```css
  font-size: var(--text-md); font-weight: 600;
```

- [ ] **Step 3: Replace `.bar-label` font-size**

Change line 53:
```css
  font-size: .68rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 4: Replace `.dash-sub-item` font-size**

Change line 63:
```css
  font-size: .8rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 5: Replace `.dash-sub-badge` font-size**

Change line 70:
```css
  font-size: .6rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 6: Replace `.dash-sub-row` font-size**

Change line 78:
```css
  font-size: .78rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 7: Replace `.load-row-label` font-size**

Change line 102:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 8: Replace `.load-row-pct` font-size**

Change line 105:
```css
  font-size: .9rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 9: Replace `.badge-live` font-size**

Change line 114:
```css
  font-size: .58rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 10: Replace `.core-label` font-size**

Change line 148:
```css
  font-size: .55rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 11: Replace `.proc-table` font-size**

Change line 156:
```css
  font-size: .8rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 12: Replace `.proc-table thead th` font-size**

Change line 161:
```css
  font-size: .65rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 13: Replace `.proc-pid` font-size**

Change line 175:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 14: Replace `.gpu-vendor-badge` font-size**

Change line 205:
```css
  font-size: .55rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 15: Replace `.gpu-card-title` font-size**

Change line 216:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 16: Replace `.gpu-stat-cell--empty` font-size**

Change line 231:
```css
  font-size: .78rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 17: Replace `.gpu-stat-label` font-size**

Change line 236:
```css
  font-size: .62rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 18: Replace `.gpu-stat-value` font-size**

Change line 243:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 19: Replace `.gpu-empty` font-size**

Change line 252:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 20: Replace `.load-speed-value` font-size**

Change line 261:
```css
  font-size: .8rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 21: Replace `.temp-value` font-size**

Change line 266:
```css
  font-size: 1rem;
```
To:
```css
  font-size: var(--text-lg);
```

- [ ] **Step 22: Replace responsive `.dash-val` override**

Change line 299:
```css
  .dash-val { font-size: 1.1rem; }
```
To:
```css
  .dash-val { font-size: var(--text-lg); }
```

- [ ] **Step 23: Replace responsive `.dash-val-sm` override**

Change line 300:
```css
  .dash-val-sm { font-size: .85rem; }
```
To:
```css
  .dash-val-sm { font-size: var(--text-base); }
```

- [ ] **Step 24: Replace responsive `.proc-table` override**

Change line 303:
```css
  .proc-table { font-size: .75rem; }
```
To:
```css
  .proc-table { font-size: var(--text-sm); }
```

- [ ] **Step 25: Replace `.net-card-header` font-size**

Change line 330:
```css
  font-size: .65rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 26: Replace `.net-label` font-size**

Change line 359:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 27: Replace `.net-value` font-size and fix font-weight**

Change line 368-369:
```css
  font-size: .85rem;
  font-weight: 650;
```
To:
```css
  font-size: var(--text-base);
  font-weight: 600;
```

- [ ] **Step 28: Commit**

```bash
git add static/css/tab-dashboard-overview.css
git commit -m "refactor(css): dashboard — use font-size vars, fix font-weight 650→600"
```

---

### Task 10: Update tab-network-dns.css

**Files:**
- Modify: `static/css/tab-network-dns.css`

- [ ] **Step 1: Replace `.protocol-label` font-size**

Change line 9:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Replace `.protocol-option` font-size**

Change line 12:
```css
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 3: Replace `.dns-group-title` font-size**

Change line 24:
```css
  font-size: .73rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 4: Replace `.dns-tag` font-size and remove redundant `font-family`**

Change line 35:
```css
  font-size: .78rem;
```
To:
```css
  font-size: var(--text-sm);
```

Remove `font-family: var(--font-sans);` from line 36.

- [ ] **Step 5: Replace `.dns-fields input` font-size and remove redundant `font-family`**

Change line 64:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

Remove `font-family: var(--font-sans);` from line 67.

- [ ] **Step 6: Replace `.dns-input-group.single-row > input` font-size and remove redundant `font-family`**

Change line 84:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

Remove `font-family: var(--font-sans);` from line 86.

- [ ] **Step 7: Replace `.empty-hint` font-size**

Change line 100:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 8: Commit**

```bash
git add static/css/tab-network-dns.css
git commit -m "refactor(css): network-dns — use font-size vars, remove redundant font-family"
```

---

### Task 11: Update tab-quick-settings.css

**Files:**
- Modify: `static/css/tab-quick-settings.css`

- [ ] **Step 1: Replace `.quick-item` font-size and remove redundant `font-family`**

Change line 22-23:
```css
  font-family: var(--font-sans);
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Replace `.quick-item .icon` font-size**

Change line 34:
```css
  font-size: 1.15rem;
```
To:
```css
  font-size: var(--text-xl);
```

- [ ] **Step 3: Replace `.quick-category-title` font-size**

Change line 47:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 4: Commit**

```bash
git add static/css/tab-quick-settings.css
git commit -m "refactor(css): quick-settings — use font-size vars, remove redundant font-family"
```

---

### Task 12: Update tab-shutdown-scheduler.css

**Files:**
- Modify: `static/css/tab-shutdown-scheduler.css`

- [ ] **Step 1: Replace `.mode-radio label` font-size**

Change line 8:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 2: Replace `.shutdown-inputs input` font-size and remove redundant `font-family`**

Change line 20:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

Remove `font-family: var(--font-sans);` from line 22.

- [ ] **Step 3: Replace `.schedule-days label` font-size**

Change line 34:
```css
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 4: Replace `.schedule-item` font-size**

Change line 39:
```css
  font-size: .88rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 5: Commit**

```bash
git add static/css/tab-shutdown-scheduler.css
git commit -m "refactor(css): shutdown — use font-size vars, remove redundant font-family"
```

---

### Task 13: Update tab-speedtest.css

**Files:**
- Modify: `static/css/tab-speedtest.css`

- [ ] **Step 1: Replace `.speedtest-progress-text` font-size**

Change line 26:
```css
  font-size: .8rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 2: Replace `.speedtest-tab` font-size and remove redundant `font-family`**

Change line 38:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

Remove `font-family: var(--font-sans);` from line 44.

- [ ] **Step 3: Replace `.tab-count` font-size**

Change line 54:
```css
  font-size: .62rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 4: Replace `.th-sub` font-size**

Change line 68:
```css
  font-size: .62rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 5: Replace `.data-table` font-size**

Change line 77:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 6: Replace `.data-table thead th` font-size**

Change line 82:
```css
  font-size: .68rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 7: Replace `.data-table .empty-hint` font-size**

Change line 98:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 8: Replace `.empty-icon` font-size**

Change line 100:
```css
  font-size: 1.3rem;
```
To:
```css
  font-size: var(--text-xl);
```

- [ ] **Step 9: Replace `.region-badge` font-size**

Change line 104:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 10: Replace `.status-badge` font-size**

Change line 112:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 11: Replace `.result-card-header` font-size**

Change line 132:
```css
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 12: Replace `.result-card-body` font-size**

Change line 140:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 13: Replace `.result-empty` font-size**

Change line 149:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 14: Replace `.result-server-label` font-size**

Change line 152:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 15: Replace `.result-server-value` font-size**

Change line 153:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 16: Replace `.result-addr-header` font-size**

Change line 155:
```css
  font-size: .78rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 17: Replace `.result-addr-ip` font-size** (keep `font-family: var(--font-mono)`)

Change line 159:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 18: Replace `.result-addr-type` font-size**

Change line 160:
```css
  font-size: .62rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 19: Replace `.rgi-label` font-size**

Change line 166:
```css
  font-size: .7rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 20: Replace `.rgi-value` font-size**

Change line 167:
```css
  font-size: .9rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 21: Replace `.rgi-value-mono` font-size** (keep `font-family: var(--font-mono)`)

Change line 168:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 22: Replace `.loss-bar-text` font-size**

Change line 177:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 23: Replace `.latency-val` font-size**

Change line 184:
```css
  font-size: 1.1rem;
```
To:
```css
  font-size: var(--text-lg);
```

- [ ] **Step 24: Replace `.latency-unit` font-size**

Change line 185:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 25: Replace `.latency-badge` font-size**

Change line 186:
```css
  font-size: .65rem;
```
To:
```css
  font-size: var(--text-xs);
```

- [ ] **Step 26: Replace `.status-tag` font-size**

Change line 191:
```css
  font-size:.8rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 27: Replace `.result-status-tag` font-size**

Change line 195:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 28: Commit**

```bash
git add static/css/tab-speedtest.css
git commit -m "refactor(css): speedtest — use font-size vars, remove redundant font-family"
```

---

### Task 14: Update tab-activation.css

**Files:**
- Modify: `static/css/tab-activation.css`

- [ ] **Step 1: Replace `.wizard-step` font-size and remove redundant `font-family`**

Change line 20:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

Remove `font-family: var(--font-sans);` — note: `.wizard-step` doesn't have an explicit `font-family` in this file, skip if not present.

- [ ] **Step 2: Replace `.wizard-step-num` font-size and remove redundant `font-family`**

Change line 43:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

Remove `font-family: var(--font-sans);` from line 45.

- [ ] **Step 3: Remove redundant `font-family` from `.wizard-step-label`**

Remove `font-family: var(--font-sans);` from line 63.

- [ ] **Step 4: Replace `.version-group-title` font-size**

Change line 114:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 5: Replace `.version-btn` font-size and remove redundant `font-family`**

Change line 135:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

Remove `font-family: var(--font-sans);` from line 137.

- [ ] **Step 6: Replace `.kms-pill` font-size**

Change line 177:
```css
  font-size: .82rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 7: Replace `.summary-item` font-size**

Change line 241:
```css
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 8: Replace `.summary-arrow` font-size**

Change line 251:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 9: Replace `.activation-trigger-row .btn-primary` font-size**

Change line 264:
```css
  font-size: .92rem;
```
To:
```css
  font-size: var(--text-md);
```

- [ ] **Step 10: Replace `.timeline-icon` font-size**

Change line 301:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 11: Replace `.timeline-label` font-size**

Change line 325:
```css
  font-size: .85rem;
```
To:
```css
  font-size: var(--text-base);
```

- [ ] **Step 12: Replace `.timeline-status-text` font-size**

Change line 332:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 13: Replace `.timeline-toggle` font-size and remove redundant `font-family`**

Change line 341:
```css
  font-size: .75rem;
```
To:
```css
  font-size: var(--text-sm);
```

Remove `font-family: var(--font-sans);` from line 342.

- [ ] **Step 14: Replace `.timeline-detail` font-size** (keep `font-family: var(--font-mono)`)

Change line 354:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 15: Replace `.activation-complete-badge` font-size**

Change line 381:
```css
  font-size: .72rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 16: Commit**

```bash
git add static/css/tab-activation.css
git commit -m "refactor(css): activation — use font-size vars, remove redundant font-family"
```

---

### Task 15: Update tab-app-uninstall.css

**Files:**
- Modify: `static/css/tab-app-uninstall.css`

- [ ] **Step 1: Replace `.quick-category-desc` font-size**

Change line 7:
```css
  font-size: 0.78rem;
```
To:
```css
  font-size: var(--text-sm);
```

- [ ] **Step 2: Commit**

```bash
git add static/css/tab-app-uninstall.css
git commit -m "refactor(css): app-uninstall — use font-size var"
```

---

### Task 16: Update responsive-breakpoints.css

**Files:**
- Modify: `static/css/responsive-breakpoints.css`

- [ ] **Step 1: Replace 1024px breakpoint font-sizes**

Change line 11:
```css
  .section-head h2 { font-size: 1.4rem; }
```
To:
```css
  .section-head h2 { font-size: var(--text-2xl); }
```

Change line 13:
```css
  .topnav-item { padding: 0 10px; font-size: .78rem; }
```
To:
```css
  .topnav-item { padding: 0 10px; font-size: var(--text-sm); }
```

- [ ] **Step 2: Replace 768px breakpoint font-sizes**

Change line 27:
```css
  .topnav-brand h2 { font-size: .9rem; }
```
To:
```css
  .topnav-brand h2 { font-size: var(--text-md); }
```

Change line 28:
```css
  .topnav-brand-icon { font-size: 1rem; }
```
To:
```css
  .topnav-brand-icon { font-size: var(--text-lg); }
```

Change line 37:
```css
    font-size: .75rem;
```
To:
```css
    font-size: var(--text-sm);
```

Change line 46:
```css
    font-size: .7rem;
```
To:
```css
    font-size: var(--text-sm);
```

Change line 50:
```css
  .topnav-dropdown-item { padding: 10px 14px; font-size: .8rem; }
```
To:
```css
  .topnav-dropdown-item { padding: 10px 14px; font-size: var(--text-base); }
```

Change line 55:
```css
  .section-head h2 { font-size: 1.2rem; }
```
To:
```css
  .section-head h2 { font-size: var(--text-xl); }
```

Change line 58:
```css
  .stat-large { font-size: 1.3rem; }
```
To:
```css
  .stat-large { font-size: var(--text-xl); }
```

Change line 59:
```css
  .timer-display { font-size: 2.2rem; padding: 14px; }
```
Keep as-is — `timer-display` is an exception per spec.

Change line 62:
```css
  .quick-item { height: 44px; font-size: .8rem; padding: 0 12px; }
```
To:
```css
  .quick-item { height: 44px; font-size: var(--text-base); padding: 0 12px; }
```

Change line 64:
```css
  .btn { padding: 0 16px; font-size: .8rem; --btn-h: 38px; }
```
To:
```css
  .btn { padding: 0 16px; font-size: var(--text-base); --btn-h: 38px; }
```

Change line 65:
```css
  .btn-sm { padding: 0 10px; font-size: .73rem; --btn-sm-h: 32px; }
```
To:
```css
  .btn-sm { padding: 0 10px; font-size: var(--text-sm); --btn-sm-h: 32px; }
```

Change line 72:
```css
  .version-btn { height: 36px; font-size: .72rem; }
```
To:
```css
  .version-btn { height: 36px; font-size: var(--text-sm); }
```

- [ ] **Step 3: Replace 480px breakpoint font-sizes**

Change line 82:
```css
  .section-head h2 { font-size: 1.05rem; }
```
To:
```css
  .section-head h2 { font-size: var(--text-lg); }
```

Change line 84:
```css
  .quick-item { height: 40px; font-size: .76rem; padding: 0 10px; }
```
To:
```css
  .quick-item { height: 40px; font-size: var(--text-sm); padding: 0 10px; }
```

- [ ] **Step 4: Commit**

```bash
git add static/css/responsive-breakpoints.css
git commit -m "refactor(css): responsive — use font-size vars for breakpoint overrides"
```

---

### Task 17: Final verification

- [ ] **Step 1: Grep for any remaining hardcoded font-size values**

Run:
```bash
grep -rn "font-size:" static/css/ --include="*.css" | grep -v "var(--text-" | grep -v "3.2rem" | grep -v "16px"
```

Expected: No output (all font-sizes should use variables except `timer-display` at `3.2rem` and `html { font-size: 16px }`).

- [ ] **Step 2: Grep for any remaining `--sidebar-` references**

Run:
```bash
grep -rn "sidebar" static/css/ --include="*.css"
```

Expected: No output.

- [ ] **Step 3: Grep for non-standard font-weight values**

Run:
```bash
grep -rn "font-weight: 450\|font-weight: 650" static/css/ --include="*.css"
```

Expected: No output.

- [ ] **Step 4: Commit final state**

```bash
git add -A
git commit -m "chore: font unification and redundant code cleanup complete"
```

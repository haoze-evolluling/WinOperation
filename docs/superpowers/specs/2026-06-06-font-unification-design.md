# Font Size Unification & Redundant Code Cleanup

**Date:** 2026-06-06
**Status:** Approved
**Scope:** Frontend CSS only (no JS/HTML changes)

## Goal

1. Unify 30+ scattered `font-size` values into an 8-level CSS custom property system
2. Remove deprecated sidebar variables and redundant `font-family` declarations
3. Normalize non-standard `font-weight` values (450, 650)

## 1. Font Size Variable System

Add 8 CSS custom properties to `:root` in `theme.css`:

```css
--text-xs:   .68rem;   /* core labels, badges, auxiliary text */
--text-sm:   .75rem;   /* secondary labels, small buttons, wizard step numbers */
--text-base: .82rem;   /* body baseline, normal buttons, form row labels */
--text-md:   .88rem;   /* inputs, selects, dropdowns */
--text-lg:   1rem;     /* h4, card subtitles, temperature values */
--text-xl:   1.15rem;  /* h3, card titles, stat values */
--text-2xl:  1.6rem;   /* h2, stat-large, section headings */
--text-3xl:  2rem;     /* h1 */
```

### Mapping Table

| Original  | Target      | Contexts                                      |
|-----------|-------------|-----------------------------------------------|
| `.55rem`  | `--text-xs` | core-label, gpu-vendor-badge                  |
| `.58rem`  | `--text-xs` | badge-live                                    |
| `.6rem`   | `--text-xs` | card-number, dash-sub-badge                   |
| `.62rem`  | `--text-xs` | gpu-stat-label, result-addr-type              |
| `.65rem`  | `--text-xs` | proc-table thead, net-card-header             |
| `.68rem`  | `--text-xs` | stat-label, bar-label                         |
| `.7rem`   | `--text-sm` | rgi-label                                     |
| `.72rem`  | `--text-sm` | version-group-title, proc-pid, net-label      |
| `.73rem`  | `--text-sm` | btn-sm (responsive)                           |
| `.75rem`  | `--text-sm` | btn-sm, wizard-step-num, info-grid label      |
| `.78rem`  | `--text-sm` | dash-sub-row, result-addr-header              |
| `.8rem`   | `--text-base` | dash-sub-item, proc-table, status-tag       |
| `.82rem`  | `--text-base` | btn, wizard-step, kms-pill, load-row-label  |
| `.85rem`  | `--text-base` | summary-item, net-value                     |
| `.88rem`  | `--text-md` | input/select, gpu-stat-value                  |
| `.9rem`   | `--text-md` | card-body, info-grid, toggle-label            |
| `.92rem`  | `--text-md` | dash-val-sm                                   |
| `1rem`    | `--text-lg` | h4, temp-value                                |
| `1.1rem`  | `--text-lg` | card-header h3, latency-val                   |
| `1.15rem` | `--text-xl` | h3, quick-settings icon                       |
| `1.3rem`  | `--text-xl` | dash-val                                      |
| `1.4rem`  | `--text-2xl` | section-head h2 (responsive)                |
| `1.6rem`  | `--text-2xl` | h2, stat-large                              |
| `2rem`    | `--text-3xl` | h1                                          |
| `3.2rem`  | keep as-is  | timer-display (special showcase, not part of system) |

### Exception

`timer-display` uses `3.2rem` for a large countdown display — this is a special-purpose showcase size and remains hardcoded.

## 2. Redundant Code Cleanup

### 2a. Remove deprecated sidebar variables

Remove from `theme.css` `:root`:

```css
--sidebar-bg, --sidebar-hover, --sidebar-active-bg,
--sidebar-text, --sidebar-active, --sidebar-divider
```

Remove from `dark-theme.css`:

```css
--sidebar-bg, --sidebar-hover, --sidebar-active-bg, --sidebar-text
```

**Pre-check:** Grep confirms no references to `--sidebar-` in any HTML or JS file before removal.

### 2b. Remove redundant `font-family` declarations

`base-reset-typography.css` already sets `font-family: var(--font-sans)` globally on `body` and on `p, li, label, input, select, textarea, button`. The following files redundantly redeclare it — remove:

- `components-buttons.css` — `.btn`, `select`
- `components-cards-info.css` — `.card-number`
- `components-toast.css` — `.toast`
- `tab-activation.css` — `.wizard-step`, `.wizard-step-num`, `.wizard-step-label`, `.version-btn`
- `tab-network-dns.css` — `.dns-protocol-btn`, `.dns-add-btn`
- `tab-quick-settings.css` — `.quick-icon`
- `tab-shutdown-scheduler.css` — select elements
- `layout-topnav.css` — multiple topnav elements

**Keep:** All `font-family: var(--font-mono)` declarations (explicit monospace overrides).

### 2c. Normalize non-standard font-weight

| Original | Normalized | Location               |
|----------|------------|------------------------|
| `450`    | `400`      | `.info-grid .value`    |
| `650`    | `600`      | `.net-value`           |

## 3. Affected Files (14 CSS files)

| File | Changes |
|------|---------|
| `theme.css` | Add 8 `--text-*` vars, remove 6 `--sidebar-*` vars |
| `dark-theme.css` | Remove 4 sidebar var overrides |
| `base-reset-typography.css` | Form input `font-size` → variable |
| `components-buttons.css` | Font sizes → vars, remove redundant `font-family` |
| `components-cards-info.css` | Font sizes → vars, remove redundant `font-family`, fix `font-weight: 450` |
| `components-toast.css` | Remove redundant `font-family` |
| `components-animations.css` | `font-size` → variable |
| `layout-topnav.css` | Font sizes → vars, remove redundant `font-family` |
| `tab-dashboard-overview.css` | Many font sizes → vars |
| `tab-network-dns.css` | Font sizes → vars, remove redundant `font-family` |
| `tab-quick-settings.css` | Font sizes → vars, remove redundant `font-family` |
| `tab-shutdown-scheduler.css` | Font sizes → vars, remove redundant `font-family` |
| `tab-speedtest.css` | Many font sizes → vars |
| `tab-activation.css` | Font sizes → vars, remove redundant `font-family` |
| `tab-app-uninstall.css` | Font size → variable |
| `tab-win11.css` | Check for scattered values |
| `responsive-breakpoints.css` | Responsive override values → vars |

### Not touched

- All JS files
- All HTML templates
- `style.css` (import entry only)

## 4. Execution Order

1. `theme.css` — add variables, delete deprecated sidebar
2. `dark-theme.css` — delete sidebar overrides
3. `base-reset-typography.css` — base typography
4. Component layer (buttons → cards → toast → animations)
5. Layout layer (topnav)
6. Tab layer (one tab at a time)
7. Responsive layer (responsive-breakpoints)

Visual check after each step.

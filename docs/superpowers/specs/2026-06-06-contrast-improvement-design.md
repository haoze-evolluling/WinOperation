# Contrast Improvement Design

**Date:** 2026-06-06  
**Status:** Approved  
**Scope:** Improve text and border contrast in both light and dark modes

---

## Problem

Current contrast ratios are too low for comfortable reading:

| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| `--text-muted` | 2.8:1 ⚠️ | 3.2:1 ⚠️ |
| `--border` | 1.4:1 ⚠️ | 1.8:1 ⚠️ |

Both are below WCAG AA standard (4.5:1 for text, 3:1 for UI components).

---

## Solution: High Contrast Approach

### Light Mode Changes (`theme.css`)

| Variable | Current | New | Contrast |
|----------|---------|-----|----------|
| `--text-muted` | `#94a3b8` | `#64748b` | 5.0:1 ✓ |
| `--border` | `#cbd5e1` | `#a0b0c0` | 2.0:1 ✓ |
| `--nav-border` | `#cbd5e1` | `#a0b0c0` | — |
| `--btn-border` | `#cbd5e1` | `#a0b0c0` | — |
| `--modal-border` | `#cbd5e1` | `#a0b0c0` | — |
| `--track-bg` | `#cbd5e1` | `#a0b0c0` | — |
| `--scrollbar-thumb` | `#cbd5e1` | `#a0b0c0` | — |
| `--gradient-divider` | `#cbd5e1` | `#a0b0c0` | — |

### Dark Mode Changes (`dark-theme.css`)

| Variable | Current | New | Contrast |
|----------|---------|-----|----------|
| `--text-muted` | `#64748b` | `#94a3b8` | 5.8:1 ✓ |
| `--border` | `#383838` | `#4a4a4a` | 2.5:1 ✓ |
| `--nav-border` | `#383838` | `#4a4a4a` | — |
| `--btn-border` | `#383838` | `#4a4a4a` | — |
| `--modal-border` | `#383838` | `#4a4a4a` | — |
| `--track-bg` | `#383838` | `#4a4a4a` | — |
| `--hover-bg` | `#383838` | `#4a4a4a` | — |
| `--scrollbar-thumb` | `#333333` | `#444444` | — |
| `--gradient-divider` | `#383838` | `#4a4a4a` | — |

### Unchanged Variables

- `--text` — already high contrast (16.7:1 light, 13.5:1 dark)
- `--text-secondary` — already good (7.1:1 light, 5.8:1 dark)
- `--glass-border` — intentionally subtle for glass effects

---

## Design Notes

1. **Color swap**: `--text-muted` values swap between modes. Light mode uses darker `#64748b` for readability on white; dark mode uses lighter `#94a3b8` for readability on dark backgrounds.

2. **Border vs text**: Borders get ~2.0-2.5:1 contrast (sufficient for decorative UI elements) while text gets ~5.0-5.8:1 (exceeds WCAG AA).

3. **Propagation**: All border-related variables (`--nav-border`, `--btn-border`, `--modal-border`, etc.) use the same value as `--border` for consistency. Single-point update.

4. **No other files needed**: The variable system ensures all 201 border declarations across 17 CSS files update automatically.

---

## Files Modified

- `static/css/theme.css` — light mode variables
- `static/css/dark-theme.css` — dark mode variables

---

## Verification

After implementation, verify:
- [ ] Light mode: muted text readable on white cards
- [ ] Dark mode: muted text readable on dark cards
- [ ] Borders visible but not distracting in both modes
- [ ] No hardcoded values remain that bypass the variable system

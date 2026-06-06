# Contrast Improvement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve text and border contrast ratios in both light and dark modes for better readability.

**Architecture:** Update CSS custom properties in `theme.css` (light mode) and `dark-theme.css` (dark mode). All 201 border declarations across 17 CSS files reference these variables, so no other files need modification.

**Tech Stack:** CSS Custom Properties

**Design Spec:** `docs/superpowers/specs/2026-06-06-contrast-improvement-design.md`

---

## Files Modified

- `static/css/theme.css` — Light mode variables (8 changes)
- `static/css/dark-theme.css` — Dark mode variables (9 changes)

---

### Task 1: Update Light Mode Text Contrast

**Files:**
- Modify: `static/css/theme.css:15`

- [ ] **Step 1: Change `--text-muted` value**

In `static/css/theme.css`, line 15:

```css
/* Before */
--text-muted: #94a3b8;

/* After */
--text-muted: #64748b;
```

This improves contrast from 2.8:1 to 5.0:1 (exceeds WCAG AA 4.5:1).

- [ ] **Step 2: Verify the change**

Open the app in light mode and confirm muted text (secondary labels, placeholders, timestamps) is now clearly readable.

- [ ] **Step 3: Commit**

```bash
git add static/css/theme.css
git commit -m "fix(css): improve light mode --text-muted contrast to 5.0:1"
```

---

### Task 2: Update Light Mode Border Contrast

**Files:**
- Modify: `static/css/theme.css:11,44,62,72,79,100`

- [ ] **Step 1: Change all border-related variables**

In `static/css/theme.css`, update these lines:

```css
/* Line 11: --border */
--border: #cbd5e1;  →  --border: #a0b0c0;

/* Line 44: --nav-border */
--nav-border: #cbd5e1;  →  --nav-border: #a0b0c0;

/* Line 62: --track-bg */
--track-bg: #cbd5e1;  →  --track-bg: #a0b0c0;

/* Line 72: --modal-border */
--modal-border: #cbd5e1;  →  --modal-border: #a0b0c0;

/* Line 79: --gradient-divider */
--gradient-divider: linear-gradient(90deg, #cbd5e1 0%, transparent 100%);
→
--gradient-divider: linear-gradient(90deg, #a0b0c0 0%, transparent 100%);

/* Line 100: --btn-border */
--btn-border: #cbd5e1;  →  --btn-border: #a0b0c0;
```

Also update `--scrollbar-thumb` (line 51):
```css
--scrollbar-thumb: #cbd5e1;  →  --scrollbar-thumb: #a0b0c0;
```

- [ ] **Step 2: Verify the change**

Open the app in light mode and confirm card borders, navigation borders, and form input borders are now visible but not distracting.

- [ ] **Step 3: Commit**

```bash
git add static/css/theme.css
git commit -m "fix(css): improve light mode --border contrast to 2.0:1"
```

---

### Task 3: Update Dark Mode Text Contrast

**Files:**
- Modify: `static/css/dark-theme.css:16`

- [ ] **Step 1: Change `--text-muted` value**

In `static/css/dark-theme.css`, line 16:

```css
/* Before */
--text-muted: #64748b;

/* After */
--text-muted: #94a3b8;
```

This improves contrast from 3.2:1 to 5.8:1 (exceeds WCAG AA 4.5:1).

- [ ] **Step 2: Verify the change**

Open the app in dark mode and confirm muted text is now clearly readable on dark backgrounds.

- [ ] **Step 3: Commit**

```bash
git add static/css/dark-theme.css
git commit -m "fix(css): improve dark mode --text-muted contrast to 5.8:1"
```

---

### Task 4: Update Dark Mode Border Contrast

**Files:**
- Modify: `static/css/dark-theme.css:12,22,28,30,45,46,57,65`

- [ ] **Step 1: Change all border-related variables**

In `static/css/dark-theme.css`, update these lines:

```css
/* Line 12: --border */
--border: #383838;  →  --border: #4a4a4a;

/* Line 22: --btn-border */
--btn-border: #383838;  →  --btn-border: #4a4a4a;

/* Line 28: --nav-border */
--nav-border: #383838;  →  --nav-border: #4a4a4a;

/* Line 30: --nav-hover-bg */
--nav-hover-bg: #383838;  →  --nav-hover-bg: #4a4a4a;

/* Line 45: --track-bg */
--track-bg: #383838;  →  --track-bg: #4a4a4a;

/* Line 46: --hover-bg */
--hover-bg: #383838;  →  --hover-bg: #4a4a4a;

/* Line 57: --modal-border */
--modal-border: #383838;  →  --modal-border: #4a4a4a;

/* Line 65: --gradient-divider */
--gradient-divider: linear-gradient(90deg, #383838 0%, transparent 100%);
→
--gradient-divider: linear-gradient(90deg, #4a4a4a 0%, transparent 100%);
```

Also update `--scrollbar-thumb` (line 34):
```css
--scrollbar-thumb: #333333;  →  --scrollbar-thumb: #444444;
```

- [ ] **Step 2: Verify the change**

Open the app in dark mode and confirm card borders, navigation borders, and form input borders are now visible but not distracting.

- [ ] **Step 3: Commit**

```bash
git add static/css/dark-theme.css
git commit -m "fix(css): improve dark mode --border contrast to 2.5:1"
```

---

### Task 5: Final Verification

- [ ] **Step 1: Toggle between modes**

Switch between light and dark mode multiple times. Verify:
- Muted text is readable in both modes
- Borders are visible but subtle in both modes
- No visual glitches or color mismatches

- [ ] **Step 2: Check for hardcoded values**

Run a grep to ensure no hardcoded `#cbd5e1` or `#383838` remain:

```bash
grep -r "#cbd5e1\|#383838" static/css/
```

Expected: No matches (all values should now be `#a0b0c0` or `#4a4a4a`).

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "fix(css): improve text and border contrast in both modes"
```

---

## Summary

| Variable | Light Mode | Dark Mode | Improvement |
|----------|-----------|-----------|-------------|
| `--text-muted` | `#64748b` (5.0:1) | `#94a3b8` (5.8:1) | +78% / +81% |
| `--border` | `#a0b0c0` (2.0:1) | `#4a4a4a` (2.5:1) | +43% / +39% |

Total changes: 2 files, 17 variable updates.

# Dropdown Menu Highlight Size Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce dropdown menu highlight size by decreasing horizontal padding and adding spacing between items.

**Architecture:** Modify CSS in layout-topnav.css to reduce item padding and add gap to dropdown container.

**Tech Stack:** CSS

---

### Task 1: Adjust Dropdown Highlight Size

**Files:**
- Modify: `static/css/layout-topnav.css`

- [ ] **Step 1: Reduce horizontal padding in dropdown items**

In `static/css/layout-topnav.css`, find `.topnav-dropdown-item` (around line 154) and change:
```css
padding: 7px 14px;
```
to:
```css
padding: 7px 10px;
```

- [ ] **Step 2: Add gap and flex layout to dropdown container**

In `static/css/layout-topnav.css`, find `.topnav-dropdown` (around line 130) and:
1. Change `display: none;` to `display: none;` (keep as is for hiding)
2. Add `gap: 2px;` after `padding: 6px;`
3. Add `display: flex;` and `flex-direction: column;` to `.topnav-dropdown.open`

The `.topnav-dropdown.open` rule should become:
```css
.topnav-dropdown.open {
  display: flex;
  flex-direction: column;
  animation: dropdownFadeIn 0.15s ease;
}
```

- [ ] **Step 3: Commit**

```bash
git add static/css/layout-topnav.css
git commit -m "feat(css): reduce dropdown highlight size — smaller padding, add gap"
```

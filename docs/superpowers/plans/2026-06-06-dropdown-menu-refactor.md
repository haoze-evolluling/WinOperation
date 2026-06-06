# Dropdown Menu Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor dropdown menu UI with left border selection indicator, background hover effect, and proper spacing.

**Architecture:** Update CSS in layout-topnav.css to change active state to left border indicator and hover to background color change.

**Tech Stack:** CSS

---

### Task 1: Update Dropdown Item Active State

**Files:**
- Modify: `static/css/layout-topnav.css`

- [ ] **Step 1: Update active state for dropdown items**

In `static/css/layout-topnav.css`, find `.topnav-dropdown-item.active` (around line 179) and replace it with:

```css
.topnav-dropdown-item.active {
  border-left: 3px solid var(--accent);
  background: var(--accent-subtle);
  color: var(--accent-light);
  font-weight: 600;
  padding-left: 7px;
}
```

- [ ] **Step 2: Update hover state for dropdown items**

In `static/css/layout-topnav.css`, find `.topnav-dropdown-item:hover` (around line 174) and replace it with:

```css
.topnav-dropdown-item:hover {
  background: var(--hover-bg);
  color: var(--text);
}
```

- [ ] **Step 3: Commit**

```bash
git add static/css/layout-topnav.css
git commit -m "feat(css): dropdown menu — left border active indicator, background hover"
```

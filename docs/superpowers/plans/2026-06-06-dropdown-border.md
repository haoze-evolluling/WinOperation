# Dropdown Menu Border Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bottom border separators between dropdown menu items in the top navigation.

**Architecture:** Add CSS border-bottom to `.topnav-dropdown-item` with `:last-child` exception.

**Tech Stack:** CSS

---

### Task 1: Add Border to Dropdown Items

**Files:**
- Modify: `static/css/layout-topnav.css`

- [ ] **Step 1: Add border-bottom to dropdown items**

In `static/css/layout-topnav.css`, find the `.topnav-dropdown-item` rule (around line 154) and add `border-bottom: 1px solid var(--border);` to it:

```css
.topnav-dropdown-item {
  display: block;
  padding: 7px 14px;
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, color 0.15s ease;
  text-decoration: none;
  border-bottom: 1px solid var(--border);
}
```

- [ ] **Step 2: Remove border from last item**

Add a new rule after `.topnav-dropdown-item` to remove the border from the last child:

```css
.topnav-dropdown-item:last-child {
  border-bottom: none;
}
```

- [ ] **Step 3: Commit**

```bash
git add static/css/layout-topnav.css
git commit -m "feat(css): add border separators between dropdown menu items"
```

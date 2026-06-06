# Contrast Golden Ratio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adjust light and dark mode contrast for a clean, high-contrast look with pure black text on cold white background.

**Architecture:** Update CSS custom properties in theme.css and dark-theme.css to use pure black/white text and cold white background.

**Tech Stack:** CSS Custom Properties

---

### Task 1: Update Light Mode Colors

**Files:**
- Modify: `static/css/theme.css`

- [ ] **Step 1: Change text color to pure black**

In `static/css/theme.css`, change:
```css
--text: #1e293b;
```
to:
```css
--text: #000000;
```

- [ ] **Step 2: Change background to cold white**

In `static/css/theme.css`, change:
```css
--bg: #f0f4f8;
```
to:
```css
--bg: #f8fafc;
```

- [ ] **Step 3: Adjust card hover background**

In `static/css/theme.css`, change:
```css
--bg-card-hover: #f8fafc;
```
to:
```css
--bg-card-hover: #f1f5f9;
```

- [ ] **Step 4: Commit**

```bash
git add static/css/theme.css
git commit -m "feat(css): light mode — pure black text, cold white background"
```

---

### Task 2: Update Dark Mode Colors

**Files:**
- Modify: `static/css/dark-theme.css`

- [ ] **Step 1: Change text color to pure white**

In `static/css/dark-theme.css`, change:
```css
--text: #f1f5f9;
```
to:
```css
--text: #ffffff;
```

- [ ] **Step 2: Commit**

```bash
git add static/css/dark-theme.css
git commit -m "feat(css): dark mode — pure white text"
```

---

### Task 3: Verify and Push

**Files:** None

- [ ] **Step 1: Verify changes in browser**

Open the application and verify:
- Light mode: Pure black text on cold white background
- Dark mode: Pure white text on deep dark background
- No "silvery" appearance in light mode

- [ ] **Step 2: Push to remote**

```bash
git push
```

# Dropdown Menu Border Design

**Date:** 2026-06-06  
**Status:** Approved  
**Author:** Claude (brainstorming session)

## Problem Statement

When expanding the top navigation dropdown menus (系统, 网络, 电源, 工具), the secondary menu items are visually merged together without clear separation. This makes it harder to distinguish between individual menu items.

## Design Goals

1. **Clear Separation**: Each dropdown item should be visually distinct from adjacent items
2. **Theme Consistency**: Use existing theme border colors for consistency
3. **Subtle Appearance**: Borders should be visible but not overwhelming
4. **Last Item Exception**: The last item in each dropdown should not have a bottom border

## Implementation Specification

### CSS Change

**File:** `static/css/layout-topnav.css`

**Target:** `.topnav-dropdown-item` (line 154-165)

**Change:** Add bottom border to all dropdown items except the last one

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
  border-bottom: 1px solid var(--border);  /* NEW */
}

.topnav-dropdown-item:last-child {
  border-bottom: none;  /* NEW - remove border from last item */
}
```

### Border Specifications

| Property | Value | Rationale |
|----------|-------|-----------|
| `border-bottom-width` | `1px` | Thin, subtle line |
| `border-bottom-style` | `solid` | Clean, consistent |
| `border-bottom-color` | `var(--border)` | Theme-consistent (`#a0b0c0` light, `#4a4a4a` dark) |

### Affected Dropdown Menus

All four dropdown menus will have this border:
1. **系统** — 系统状态, 延迟更新, 系统激活, Win11 专区
2. **网络** — 网络设置, 网站测速
3. **电源** — 电源选项, 定时关机
4. **工具** — 快捷设置, 应用卸载

## Success Criteria

1. Each dropdown item has a visible bottom border separating it from the next item
2. The last item in each dropdown has no bottom border
3. Borders use theme colors and adapt to light/dark mode
4. Visual appearance is clean and professional

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Border might look too heavy | Use 1px width, which is standard for UI separators |
| Border might conflict with hover states | Border is on bottom, hover background is on the item itself |
| Dark mode border might be too subtle | `--border: #4a4a4a` has sufficient contrast on dark backgrounds |

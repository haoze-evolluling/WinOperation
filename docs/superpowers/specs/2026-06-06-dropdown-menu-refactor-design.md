# Dropdown Menu Refactor Design

**Date:** 2026-06-06  
**Status:** Approved  
**Author:** Claude (brainstorming session)

## Problem Statement

The current dropdown menu UI needs optimization for better visual clarity and user experience. The selection effect and current page indicator need to be more distinctive.

## Design Goals

1. **Clear Selection Indicator**: Current page should be clearly indicated in both top nav and dropdown
2. **Consistent Hover Effects**: Hover states should be visually consistent across all menu items
3. **Professional Appearance**: Dropdown should look polished with proper borders, shadows, and spacing
4. **Functional Preservation**: All existing functionality (click, dropdown, page switching) must remain unchanged

## Design Specifications

### Top Navigation Bar (一级菜单)

**Current Page Indicator:**
- Style: Bottom border (2px solid)
- Color: `var(--accent)` (cyan)
- Applies to: The active `.topnav-item`

**Hover Effect:**
- Background: `var(--nav-hover-bg)`
- Text color: `var(--text)`
- Transition: smooth (0.2s ease)

**Active State:**
- Text color: `var(--nav-active)` (cyan)
- Border bottom: `var(--nav-active-border)` (cyan)
- Font weight: 600

### Dropdown Menu (二级菜单)

**Container:**
- Background: `var(--card)`
- Border: `1px solid var(--border)`
- Border radius: `var(--radius)` (8px)
- Box shadow: `0 8px 32px rgba(15, 43, 74, 0.12)`
- Padding: `6px`
- Gap: `2px` (between items)

**Menu Items:**
- Padding: `7px 10px`
- Border radius: `4px`
- Font size: `var(--text-base)`
- Font weight: 500
- Color: `var(--text-secondary)`
- Separator: `1px solid var(--border)` bottom border (except last item)

**Current Page Indicator (选中效果):**
- Left border: `3px solid var(--accent)` (cyan)
- Background: `var(--accent-subtle)` (light cyan)
- Text color: `var(--accent-light)` (cyan)
- Font weight: 600

**Hover Effect:**
- Background: `var(--hover-bg)`
- Text color: `var(--text)`
- Transition: smooth (0.15s ease)

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│ 概览  系统▼  网络▼  电源▼  工具▼        │  ← Top nav with bottom underline for active
├─────────────────────────────────────────┤
│ ┌─────────────────┐                     │
│ │ 系统状态        │  ← Dropdown with    │
│ │─────────────────│    border + shadow  │
│ │ 延迟更新        │                     │
│ │─────────────────│                     │
│ │ █ 系统激活      │  ← Left border for  │
│ │─────────────────│    active item      │
│ │ Win11 专区      │                     │
│ └─────────────────┘                     │
└─────────────────────────────────────────┘
```

## CSS Changes Required

### File: `static/css/layout-topnav.css`

**1. Top Nav Active State (already exists, keep as-is):**
```css
.topnav-item.active {
  color: var(--nav-active);
  border-bottom-color: var(--nav-active-border);
  font-weight: 600;
}
```

**2. Dropdown Container (already exists, keep as-is):**
```css
.topnav-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 160px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 8px 32px rgba(15, 43, 74, 0.12);
  padding: 6px;
  gap: 2px;
  display: none;
  z-index: 200;
}
```

**3. Dropdown Item Active State (needs update):**
```css
.topnav-dropdown-item.active {
  border-left: 3px solid var(--accent);
  background: var(--accent-subtle);
  color: var(--accent-light);
  font-weight: 600;
  padding-left: 7px; /* Adjust for border */
}
```

**4. Dropdown Item Hover (needs update):**
```css
.topnav-dropdown-item:hover {
  background: var(--hover-bg);
  color: var(--text);
}
```

## Success Criteria

1. Active dropdown items have a clear left border indicator
2. Hover effects are consistent and visually appealing
3. Dropdown has proper border, shadow, and spacing
4. All functionality remains unchanged
5. Visual hierarchy is clear and professional

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Left border might shift content | Adjust padding to compensate |
| Active state might be too prominent | Use subtle accent colors |
| Hover might conflict with active | Ensure proper specificity |

# Dropdown Menu Highlight Size Design

**Date:** 2026-06-06  
**Status:** Approved  
**Author:** Claude (brainstorming session)

## Problem Statement

When hovering over dropdown menu items, the highlight background is too wide. When moving the cursor between adjacent items, the highlight backgrounds merge together, creating a visual blob instead of distinct highlights.

## Design Goals

1. **Separate Highlights**: Adjacent items' highlight backgrounds should not merge
2. **Compact Appearance**: Highlight should be narrower than the full dropdown width
3. **Visual Clarity**: Each item should be clearly distinguishable when hovered

## Implementation Specification

### CSS Changes

**File:** `static/css/layout-topnav.css`

**Change 1:** Reduce horizontal padding in `.topnav-dropdown-item`

```css
/* Before */
padding: 7px 14px;

/* After */
padding: 7px 10px;
```

**Change 2:** Add gap between items in `.topnav-dropdown`

```css
.topnav-dropdown {
  /* ... existing properties ... */
  padding: 6px;
  gap: 2px;  /* NEW */
  display: flex;
  flex-direction: column;
}
```

Note: Adding `gap` requires changing `display: block` to `display: flex` with `flex-direction: column` on the dropdown container.

### Specifications

| Property | Before | After | Rationale |
|----------|--------|-------|-----------|
| Item horizontal padding | `14px` | `10px` | Narrower highlight background |
| Dropdown gap | `0px` | `2px` | Visual separation between items |
| Dropdown display | `block` | `flex` | Required for `gap` to work |
| Dropdown flex-direction | N/A | `column` | Maintain vertical stacking |

## Success Criteria

1. Adjacent dropdown items' highlight backgrounds do not merge when hovering
2. Each item has a distinct, compact highlight appearance
3. The dropdown menu maintains its vertical stacking layout
4. Visual appearance is clean and professional

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| `gap` might affect dropdown layout | Using `flex-direction: column` maintains vertical stacking |
| Reduced padding might make text feel cramped | 10px is still comfortable for the font size used |
| `gap` might not work in older browsers | Flexbox gap is supported in all modern browsers |

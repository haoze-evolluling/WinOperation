# Contrast Golden Ratio Design

**Date:** 2026-06-06  
**Status:** Approved  
**Author:** Claude (brainstorming session)

## Problem Statement

Current light mode contrast is too high and looks "silvery" rather than clean white. The background color `#f0f4f8` has a blue tint that makes it look metallic. User wants:
1. Pure black text on white background for a clean, professional look
2. Contrast ratio around 4.5:1 (WCAG AA) — but accepts higher ratio for visual clarity
3. Symmetric adjustment for both light and dark modes

## Design Goals

1. **Clean White Feel**: Background should be cold white `#f8fafc`, not blue-tinted silver
2. **Pure Black Text**: Text color should be pure black `#000000` for maximum clarity
3. **Symmetric Design**: Both light and dark modes should have similar contrast feel
4. **Visual Comfort**: High contrast but not harsh — cold white reduces glare

## Color Specifications

### Light Mode

| Token | Current | New | Rationale |
|-------|---------|-----|-----------|
| `--text` | `#1e293b` | `#000000` | Pure black for maximum clarity |
| `--text-muted` | `#64748b` | `#64748b` | Keep muted text at 5:1 contrast |
| `--bg` | `#f0f4f8` | `#f8fafc` | Cold white, not blue-tinted silver |
| `--bg-card` | `#ffffff` | `#ffffff` | Keep pure white for cards |
| `--bg-card-hover` | `#f8fafc` | `#f1f5f9` | Slightly darker hover for contrast |
| `--border` | `#a0b0c0` | `#a0b0c0` | Keep current border contrast |

**Contrast Ratios:**
- Text on Background: `#000000` on `#f8fafc` = ~18:1 (WCAG AAA ✓)
- Text on Card: `#000000` on `#ffffff` = 21:1 (WCAG AAA ✓)
- Muted Text on Background: `#64748b` on `#f8fafc` = ~5:1 (WCAG AA ✓)

### Dark Mode

| Token | Current | New | Rationale |
|-------|---------|-----|-----------|
| `--text` | `#f1f5f9` | `#ffffff` | Pure white for maximum clarity |
| `--text-muted` | `#94a3b8` | `#94a3b8` | Keep muted text at 5.8:1 contrast |
| `--bg` | `#0f172a` | `#0f172a` | Keep deep dark blue |
| `--bg-card` | `#1e293b` | `#1e293b` | Keep dark blue-gray cards |
| `--bg-card-hover` | `#2d3a4f` | `#2d3a4f` | Keep hover state |
| `--border` | `#4a4a4a` | `#4a4a4a` | Keep border contrast |

**Contrast Ratios:**
- Text on Background: `#ffffff` on `#0f172a` = ~16:1 (WCAG AAA ✓)
- Text on Card: `#ffffff` on `#1e293b` = ~12:1 (WCAG AAA ✓)
- Muted Text on Background: `#94a3b8` on `#0f172a` = ~5.8:1 (WCAG AA ✓)

## Implementation Plan

1. **Update `static/css/theme.css`**:
   - Change `--text: #1e293b` to `--text: #000000`
   - Change `--bg: #f0f4f8` to `--bg: #f8fafc`
   - Change `--bg-card-hover: #f8fafc` to `--bg-card-hover: #f1f5f9`

2. **Update `static/css/dark-theme.css`**:
   - Change `--text: #f1f5f9` to `--text: #ffffff`

3. **Verify contrast ratios** using a contrast checker tool

## Success Criteria

1. Light mode has clean white background, not silvery
2. Text is pure black in light mode, pure white in dark mode
3. All text meets WCAG AA contrast requirements (4.5:1 minimum)
4. Visual feel is "high contrast but comfortable"

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Pure black on white might be too harsh | Cold white `#f8fafc` reduces glare |
| Dark mode pure white might be too bright | Deep dark background `#0f172a` balances it |
| Muted text might become too low contrast | Keep at 5:1+ ratio (WCAG AA compliant) |

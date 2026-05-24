# Project Rename: WinMaster → WinOperation

## Objective
Rename the project from "WinMaster" to "WinOperation" across the entire codebase, updating all references while preserving functionality.

## Scope
- Replace all display names (`WinMaster` → `WinOperation`) in UI, docs, and output
- Replace all internal identifiers (`winmaster_*`, `winmaster-*` → `winoperation_*`, `winoperation-*`)
- Preserve `static/logo.png` as-is (keep existing logo file)

## Files to Modify

### Display Name Changes
| File | Changes |
|------|---------|
| `README.md` | Project title, descriptions, URLs, FAQ |
| `build.py` | `OUTPUT_NAME = "WinOperation"` |
| `start.bat` | `title`, `echo` messages |
| `templates/base.html` | `<title>` tag |
| `templates/_topnav.html` | `<h2>` title |
| `static/css/*.css` (16 files) | File header comments |
| `static/js/theme.js` | Comment header |
| `src/services/shutdown_mgmt.py` | Task name, folder name, comments |

### Internal Identifier Changes
| File | Changes |
|------|---------|
| `src/config.py` | `SECRET_KEY = "winoperation-fixed-key"` |
| `templates/base.html` | `localStorage` key `winmaster-theme` → `winoperation-theme` |
| `static/js/dashboard.js` | `CACHE_KEY` → `winoperation_dashboard_data` |
| `static/js/utils.js` | `CACHE_STORE` → `winoperation-media` |
| `static/js/theme.js` | `STORAGE_KEY` → `winoperation-theme` |

### Documentation
| File | Changes |
|------|---------|
| `docs/superpowers/specs/2026-05-24-html-decoupling-design.md` | All references |

## Non-Goals
- No functional changes
- No architecture changes
- Logo image file retained as-is

## Verification
- `grep -ri "winmaster" .` returns no results (excluding `.git` and logo binary)
- App starts and runs correctly

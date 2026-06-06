# Merge Inspection Into Overview Design

## Goal

Move the inspection module into the overview module so users see inspection health, recommendations, filters, search, and detail results directly on the overview page. The resulting UI should follow the overview module's card-based visual language.

## Current State

- The overview tab is rendered by `templates/_tab_dashboard.html`, styled mainly by `static/css/tab-dashboard-overview.css`, and loaded by `static/js/dashboard.js`.
- The inspection tab is currently a separate top navigation item rendered by `templates/_tab_insights.html`, styled by `static/css/tab-insights.css`, and loaded by `static/js/insights.js`.
- The inspection backend already exposes `/api/insights/snapshot`; no backend data model change is required.

## Proposed Approach

Use a full merge into the overview tab:

- Remove the standalone inspection top navigation item.
- Include the inspection UI inside the overview tab.
- Keep `/api/insights/snapshot` as the data source.
- Adapt inspection markup and styles to reuse overview card, grid, small-stat, table, and progress patterns.
- Preserve inspection refresh, export, filter, search, cached render, and detail rendering.
- Redirect any old `#tab-insights` route to `#tab-dashboard` so old links do not leave users on a missing tab.

This approach best matches the requested behavior because inspection becomes part of the overview workflow instead of remaining a separate destination.

## UI Design

The overview tab gets a new `System Inspect` card after the main system/network/hardware cards. The card header uses the existing `card-header`, `card-number`, and compact button style. The card body contains:

- A health score panel aligned with overview typography.
- Four compact metrics: generated time, urgent count, warning count, and feature count.
- A recommendation area using compact overview rows.
- A filter/search toolbar inside the same card.
- A responsive detail grid that uses overview-like bordered mini-cards.

The inspection detail cards keep their severity state, but their shape, spacing, borders, typography, and responsive behavior should visually match the overview module.

## Frontend Data Flow

- `Dashboard.startDashboard()` loads existing overview data and then loads inspection data.
- `Dashboard.refreshDashboard()` refreshes overview data and inspection data together.
- `insights.js` remains the renderer for inspection data but must work when its DOM is embedded in the overview tab.
- `tabs.js` no longer treats `tab-insights` as a normal direct tab. If `#tab-insights` appears in the URL, it switches to `tab-dashboard`.

## Backend Data Flow

- Keep the existing `insights_bp` registration and `/api/insights/snapshot`.
- No PowerShell-based backend work is needed for this change.
- No new backend endpoint is required.

## Error Handling

- If inspection data fails, show the existing toast and leave cached or placeholder content in place.
- If no matching inspection items exist after filtering/searching, render an empty hint inside the overview card.
- If the old route `#tab-insights` is requested, gracefully show the overview tab.

## Testing

Add or update tests to verify:

- The top navigation no longer exposes a standalone inspection item.
- The overview template contains the embedded inspection card and controls.
- `dashboard.js` loads inspection data during overview load/refresh.
- `tabs.js` redirects `tab-insights` to `tab-dashboard`.

Run the existing Python unit tests, JavaScript syntax checks, and a browser check against the local Flask app to verify the overview tab renders and the embedded inspection controls work.

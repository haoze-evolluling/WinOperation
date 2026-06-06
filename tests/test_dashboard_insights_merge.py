import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


class DashboardInsightsMergeTests(unittest.TestCase):
    def test_topnav_no_longer_exposes_standalone_insights(self):
        topnav = read_file("templates/_topnav.html")

        self.assertNotIn('data-tab="tab-insights"', topnav)
        self.assertNotRegex(topnav, r">\s*巡检\s*<")

    def test_dashboard_splits_inspection_sections_into_preview_panels(self):
        dashboard = read_file("templates/_tab_dashboard.html")
        outer = read_file("templates/dashboard.html")

        self.assertNotIn("dashboard-insights-card", dashboard)
        self.assertIn("preview-panel--insights-summary", dashboard)
        self.assertIn("preview-panel--insights-recommendations", dashboard)
        self.assertIn("preview-panel--insights-controls", dashboard)
        self.assertIn("insights-score-panel", dashboard)
        self.assertIn("insights-filter-group", dashboard)
        self.assertIn("insights-search", dashboard)
        self.assertIn("preview-insight-grid", dashboard)
        self.assertNotIn('{% include "_tab_insights.html" %}', outer)

    def test_dashboard_starts_and_refreshes_inspection_data(self):
        script = read_file("static/js/dashboard.js")

        self.assertIn('import { initInsights, loadInsights } from "./insights.js";', script)
        self.assertRegex(script, r"startDashboard\(\)\s*\{[\s\S]*?initInsights\(\)")
        self.assertRegex(script, r"refreshDashboard\(\)\s*\{[\s\S]*?loadInsights\(true\)")

    def test_old_inspection_hash_redirects_to_dashboard(self):
        script = read_file("static/js/tabs.js")

        self.assertIn('if (tabId === "tab-insights") tabId = "tab-dashboard";', script)
        self.assertNotIn('ensureInit("tab-insights"', script)

    def test_embedded_inspection_initialization_is_idempotent(self):
        script = read_file("static/js/insights.js")

        self.assertIn("let insightsInitialized = false;", script)
        self.assertRegex(script, r"export function initInsights\(\) \{[\s\S]*?if \(insightsInitialized\)")
        self.assertRegex(script, r"export function initInsights\(\) \{[\s\S]*?insightsInitialized = true;")

    def test_dashboard_replaces_legacy_preview_shell(self):
        dashboard = read_file("templates/_tab_dashboard.html")

        self.assertIn('class="tab-content active preview-dashboard"', dashboard)
        self.assertIn("preview-toolbar", dashboard)
        self.assertIn('id="dashboard-preview-grid"', dashboard)
        self.assertNotIn("preview-draggable", dashboard)
        self.assertIn("preview-panel--system", dashboard)
        self.assertIn("preview-panel--hardware", dashboard)
        self.assertIn("preview-panel--network", dashboard)
        self.assertIn("preview-panel--battery", dashboard)
        self.assertIn("preview-panel--gpu", dashboard)
        self.assertIn("preview-panel--insights-summary", dashboard)
        self.assertIn("preview-panel--insights-recommendations", dashboard)
        self.assertIn("preview-panel--insights-controls", dashboard)
        self.assertNotIn("dashboard-overview", dashboard)
        self.assertNotIn("dashboard-hero", dashboard)
        self.assertNotIn("dashboard-pinboard", dashboard)
        self.assertNotIn("dashboard-note", dashboard)
        self.assertNotIn("dash-card--", dashboard)

    def test_dashboard_inspection_detail_grid_uses_independent_preview_cards(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r"\.preview-insight-grid\s*\{[\s\S]*?width:\s*100%",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid\.insights-feature-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid\s*\{[\s\S]*?gap:\s*14px",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid\.insights-feature-grid\s*\{[\s\S]*?gap:\s*14px",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid \.insight-card\s*\{[\s\S]*?min-width:\s*0",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid \.insight-card\s*\{[\s\S]*?min-height:\s*132px",
        )
        self.assertRegex(
            css,
            r"\.preview-insight-grid \.insight-card\s*\{[\s\S]*?padding:\s*12px\s*14px",
        )

    def test_dashboard_preview_panel_headers_remove_legacy_markers(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r"\.preview-panel \.card-header::after\s*\{[\s\S]*?display:\s*none",
        )

    def test_dashboard_preview_uses_single_column_rows_on_all_viewports(self):
        css = read_file("static/css/tab-dashboard-overview.css")
        layout_css = read_file("static/css/layout-topnav.css")

        four_col = r"grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)"
        self.assertRegex(
            layout_css,
            r"\.main-content:has\(\.preview-dashboard\.active\)\s*\{[\s\S]*?max-width:\s*1840px",
        )
        self.assertRegex(css, r"\.preview-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.preview-grid\s*\{[\s\S]*?grid-auto-rows:\s*auto")
        self.assertNotRegex(css, r"\.preview-grid\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)")
        self.assertNotRegex(css, r"\.preview-grid\s*\{[\s\S]*?" + four_col)
        self.assertRegex(
            css,
            r"\.preview-panel \.card-body\s*\{[\s\S]*?min-height:\s*0[\s\S]*?overflow:\s*auto",
        )
        for panel_class in [
            "system",
            "hardware",
            "network",
            "battery",
            "gpu",
            "insights-summary",
            "insights-recommendations",
        ]:
            self.assertRegex(
                css,
                rf"\.preview-grid > \.preview-panel--{panel_class}\s*\{{[^}}]*grid-column:\s*span\s*1",
            )
            self.assertRegex(
                css,
                rf"\.preview-grid > \.preview-panel--{panel_class}\s*\{{[^}}]*grid-row:\s*span\s*1",
            )
        self.assertRegex(css, r"\.preview-grid > \.preview-panel--insights-controls\s*\{[^}]*grid-column:\s*span\s*1")
        self.assertRegex(css, r"\.preview-grid > \.preview-panel--insights-controls\s*\{[^}]*grid-row:\s*span\s*1")
        self.assertNotRegex(css, r"preview-panel--(?:system|hardware|network|battery|gpu|insights-summary|insights-recommendations)[\s\S]*?grid-column:\s*span\s*(?:[2-9]|1[0-2])")
        two_col = r"grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)"
        self.assertRegex(css, r"\.dash-col-2\s*\{[^}]*" + two_col)
        self.assertRegex(css, r"\.dash-col-3\s*\{[^}]*" + two_col)
        self.assertRegex(css, r"\.net-grid\s*\{[\s\S]*?" + two_col)

    def test_dark_preview_panels_use_solid_surfaces(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r'\[data-theme="dark"\] \.preview-panel\s*\{[^}]*background:\s*var\(--card\)',
        )
        self.assertRegex(
            css,
            r'\[data-theme="dark"\] \.preview-insight-grid \.insight-card\s*\{[^}]*background:\s*var\(--surface\)',
        )
        self.assertNotRegex(
            css,
            r'\[data-theme="dark"\] \.preview-panel[\s\S]*?var\(--note-paper',
        )

    def test_dashboard_inspection_summary_fits_equal_width_card(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-summary-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-summary-metrics\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-mini-stat strong\s*\{[\s\S]*?font-size:\s*clamp",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-score-panel\s*\{[\s\S]*?min-height:\s*104px",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-score-value\s*\{[\s\S]*?font-size:\s*2\.1rem",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-summary \.insights-mini-stat\s*\{[\s\S]*?min-height:\s*58px",
        )
        self.assertRegex(
            css,
            r"\.preview-panel--insights-controls \.insights-toolbar\s*\{[\s\S]*?grid-template-columns:\s*1fr",
        )

    def test_dashboard_gpu_detail_matches_hardware_load_layout(self):
        css = read_file("static/css/tab-dashboard-overview.css")
        responsive_css = read_file("static/css/responsive-breakpoints.css")
        script = read_file("static/js/dashboard.js")

        self.assertRegex(
            css,
            r"\.gpu-card-item\s*\{[\s\S]*?background:\s*var\(--surface\)",
        )
        self.assertRegex(
            css,
            r"\.gpu-card-header\s*\{[\s\S]*?grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)",
        )
        self.assertRegex(
            css,
            r"\.gpu-stat-grid\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        )
        self.assertNotRegex(
            css,
            r"\.gpu-stat-grid\s*\{[^}]*auto-fit",
        )
        self.assertRegex(
            responsive_css,
            r"\.gpu-stat-grid\s*\{[^}]*grid-template-columns:\s*1fr",
        )
        self.assertIn("gpu-stat-cell gpu-stat-cell--meter", script)

    def test_dashboard_preview_dragging_is_removed(self):
        dashboard = read_file("templates/_tab_dashboard.html")
        script = read_file("static/js/dashboard.js")
        insights_script = read_file("static/js/insights.js")
        css = read_file("static/css/tab-dashboard-overview.css")

        for source in [dashboard, insights_script, css]:
            self.assertNotIn("preview-draggable", source)
        self.assertNotIn("data-note-id", dashboard)
        self.assertNotIn("data-note-id", insights_script)
        for removed in [
            "PREVIEW_POSITIONS_KEY",
            "PREVIEW_ITEM_SELECTOR",
            "initDashboardPreviewGrid",
            "preview-draggable--dragging",
            "localStorage.setItem(PREVIEW_POSITIONS_KEY",
            "pointerdown",
            "pointermove",
            "pointercancel",
        ]:
            self.assertNotIn(removed, script)
        self.assertNotRegex(script, r"startDashboard\(\)\s*\{[\s\S]*?initDashboardPreviewGrid\(\)")
        self.assertNotIn("cursor: grab", css)
        self.assertNotIn("--preview-x", css)

    def test_responsive_breakpoints_collapse_dashboard_safely(self):
        css = read_file("static/css/responsive-breakpoints.css")
        dashboard_css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(css, r"\.dash-cards\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(dashboard_css, r"\.preview-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr")
        self.assertRegex(dashboard_css, r"\.preview-insight-grid\.insights-feature-grid\s*\{[\s\S]*?grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.dash-col-2\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.dash-col-3\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.net-grid\s*\{[^}]*grid-template-columns:\s*1fr")

    def test_dashboard_two_column_content_can_shrink_without_page_overflow(self):
        dashboard_css = read_file("static/css/tab-dashboard-overview.css")
        insights_css = read_file("static/css/tab-insights.css")

        self.assertRegex(dashboard_css, r"\.preview-grid > \.preview-panel\s*\{[^}]*min-width:\s*0")
        self.assertRegex(dashboard_css, r"\.preview-field-value\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(dashboard_css, r"\.net-value\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(dashboard_css, r"\.dash-sub-val-sm\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(dashboard_css, r"\.dash-sub-bar\s*\{[^}]*min-width:\s*0")
        self.assertRegex(
            insights_css,
            r"\.insight-kv-grid\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        )
        self.assertRegex(insights_css, r"\.insight-card-head strong\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(insights_css, r"\.insight-kv-grid span\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(insights_css, r"\.insight-kv-grid strong\s*\{[^}]*overflow-wrap:\s*anywhere")


if __name__ == "__main__":
    unittest.main()

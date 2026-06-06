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

    def test_dashboard_embeds_inspection_card_and_controls(self):
        dashboard = read_file("templates/_tab_dashboard.html")
        outer = read_file("templates/dashboard.html")

        self.assertIn("dashboard-insights-card", dashboard)
        self.assertIn("insights-score-panel", dashboard)
        self.assertIn("insights-filter-group", dashboard)
        self.assertIn("insights-search", dashboard)
        self.assertIn("insights-feature-grid", dashboard)
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

    def test_dashboard_uses_responsive_overview_shell(self):
        dashboard = read_file("templates/_tab_dashboard.html")

        self.assertIn('class="tab-content active dashboard-overview"', dashboard)
        self.assertIn("dashboard-hero", dashboard)
        self.assertIn("dash-card--system", dashboard)
        self.assertIn("dash-card--hardware", dashboard)
        self.assertIn("dash-card--network", dashboard)
        self.assertIn("dash-card--battery", dashboard)
        self.assertIn("dash-card--gpu", dashboard)

    def test_dashboard_inspection_detail_grid_uses_responsive_cards(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.insights-feature-grid\s*\{[\s\S]*?width:\s*100%",
        )
        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.insights-feature-grid\s*\{[\s\S]*?grid-template-columns:\s*repeat\(auto-fit,\s*minmax\(min\(260px,\s*100%\),\s*1fr\)\)",
        )
        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.insight-card\s*\{[\s\S]*?min-width:\s*0",
        )

    def test_dashboard_inspection_header_marker_aligns_with_inspect_label(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.card-header::after\s*\{[\s\S]*?top:\s*2px",
        )
        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.card-header::after\s*\{[\s\S]*?bottom:\s*auto",
        )
        self.assertRegex(
            css,
            r"\.dashboard-insights-card \.card-header::after\s*\{[\s\S]*?margin:\s*0",
        )

    def test_dashboard_overview_information_layouts_have_desktop_grid(self):
        css = read_file("static/css/tab-dashboard-overview.css")

        two_col = r"grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)"
        twelve_col = r"grid-template-columns:\s*repeat\(12,\s*minmax\(0,\s*1fr\)\)"
        self.assertRegex(css, r"\.dash-cards\s*\{[\s\S]*?" + twelve_col)
        self.assertRegex(css, r"\.dash-cards > \.dash-card--system\s*\{[^}]*grid-column:\s*span\s*5")
        self.assertRegex(css, r"\.dash-cards > \.dash-card--hardware\s*\{[^}]*grid-column:\s*span\s*7")
        self.assertRegex(css, r"\.dash-cards > \.dash-card--network\s*\{[^}]*grid-column:\s*span\s*8")
        self.assertRegex(css, r"\.dash-cards > \.dash-card--battery\s*\{[^}]*grid-column:\s*span\s*4")
        self.assertRegex(css, r"\.dash-cards > \.dash-card--gpu\s*\{[^}]*grid-column:\s*1\s*/\s*-1")
        self.assertRegex(css, r"\.dash-cards > \.dash-card--insights\s*\{[^}]*grid-column:\s*1\s*/\s*-1")
        self.assertRegex(css, r"\.dash-col-2\s*\{[^}]*" + two_col)
        self.assertRegex(css, r"\.dash-col-3\s*\{[^}]*" + two_col)
        self.assertRegex(css, r"\.net-grid\s*\{[\s\S]*?" + two_col)
        self.assertRegex(css, r"\.dashboard-insights-card \.dashboard-insights-summary\s*\{[\s\S]*?" + two_col)
        self.assertRegex(css, r"\.dashboard-insights-card \.insights-summary-metrics\s*\{[\s\S]*?" + two_col)

    def test_responsive_breakpoints_collapse_dashboard_safely(self):
        css = read_file("static/css/responsive-breakpoints.css")

        self.assertRegex(css, r"\.dash-cards\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.dash-col-2\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.dash-col-3\s*\{[^}]*grid-template-columns:\s*1fr")
        self.assertRegex(css, r"\.net-grid\s*\{[^}]*grid-template-columns:\s*1fr")

    def test_dashboard_two_column_content_can_shrink_without_page_overflow(self):
        dashboard_css = read_file("static/css/tab-dashboard-overview.css")
        insights_css = read_file("static/css/tab-insights.css")

        self.assertRegex(dashboard_css, r"\.dash-cards > \.card\s*\{[^}]*min-width:\s*0")
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

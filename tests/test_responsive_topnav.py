import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


class ResponsiveTopnavTests(unittest.TestCase):
    def test_mobile_dropdown_escapes_scroll_container(self):
        css = read_file("static/css/layout-topnav.css")
        self.assertRegex(
            css,
            r"\.topnav-dropdown\.mobile-floating\s*\{[^}]*position:\s*fixed",
        )

    def test_dropdown_opening_positions_mobile_floating_menu(self):
        script = read_file("static/js/tabs.js")
        self.assertIn("positionOpenDropdown", script)
        self.assertIn("mobile-floating", script)
        self.assertIn("--dropdown-left", script)
        self.assertIn("--dropdown-top", script)

    def test_closing_dropdowns_clears_mobile_positioning(self):
        script = read_file("static/js/tabs.js")
        close_body = re.search(r"function closeAllDropdowns\(\) \{(?P<body>.*?)\n\}", script, re.S)
        self.assertIsNotNone(close_body)
        self.assertIn("resetDropdownPosition", close_body.group("body"))


if __name__ == "__main__":
    unittest.main()

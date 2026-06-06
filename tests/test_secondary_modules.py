import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


class SecondaryModuleRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from main import create_app

        cls.client = create_app().test_client()

    def test_system_process_summary_contract(self):
        response = self.client.get("/api/system/process-summary")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("process_count", data)
        self.assertIn("top_cpu", data)
        self.assertIn("top_memory", data)
        self.assertGreaterEqual(data["process_count"], 0)

    def test_network_python_diagnostics_contract(self):
        response = self.client.post("/api/network/diagnostics", json={"target": "localhost"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertEqual(data["target"], "localhost")
        self.assertIn("resolved_ips", data)
        self.assertIn("tcp_checks", data)
        self.assertIn("elapsed_ms", data)

    def test_power_battery_insights_contract(self):
        response = self.client.get("/api/power/battery-insights")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("present", data)
        self.assertIn("status", data)
        self.assertIn("tips", data)

    def test_speedtest_resolve_contract(self):
        response = self.client.post("/api/speedtest/resolve", json={"target": "localhost"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertEqual(data["target"], "localhost")
        self.assertIn("addresses", data)
        self.assertIn("elapsed_ms", data)

    def test_app_uninstall_catalog_contract(self):
        response = self.client.get("/api/app-uninstall/catalog")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertGreater(data["category_count"], 0)
        self.assertGreater(data["item_count"], 0)
        self.assertIn("categories", data)

    def test_update_health_contract(self):
        response = self.client.get("/api/update/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("paused", data)
        self.assertIn("policy", data)
        self.assertIn("services", data)
        self.assertIn("recommendations", data)

    def test_win11_summary_contract(self):
        response = self.client.get("/api/win11/summary")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("items", data)
        self.assertIn("enabled_count", data)
        self.assertEqual(len(data["items"]), 3)


if __name__ == "__main__":
    unittest.main()

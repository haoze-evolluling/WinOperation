import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


class InsightCompositionTests(unittest.TestCase):
    def test_composes_exactly_twenty_operational_features(self):
        from services.system_insights import compose_insights

        raw = {
            "system": {
                "os": "Windows 11",
                "hostname": "OPS-PC",
                "architecture": "AMD64",
                "login_user": "haoze",
                "uptime_seconds": 15 * 24 * 3600,
                "boot_time": "2026-05-22 09:00:00",
                "admin": True,
                "python_version": "3.12.0",
                "executable": "python.exe",
            },
            "cpu": {
                "usage": 92,
                "physical_cores": 8,
                "logical_cores": 16,
                "frequency_current": 3300,
                "frequency_max": 4200,
                "cores": [{"core_index": str(i), "load": 90} for i in range(4)],
            },
            "memory": {
                "total_gb": 32,
                "used_gb": 27,
                "available_gb": 5,
                "percent": 84,
            },
            "swap": {"total_gb": 8, "used_gb": 5, "percent": 62},
            "disks": [
                {"device": "C:", "total": 200, "used": 192, "free": 8, "percent": 96},
                {"device": "D:", "total": 500, "used": 200, "free": 300, "percent": 40},
            ],
            "disk_io": {
                "read_mb": 2048,
                "write_mb": 1024,
                "read_count": 300,
                "write_count": 150,
            },
            "network": {
                "adapters": [
                    {
                        "Name": "Ethernet",
                        "InterfaceDescription": "Intel Ethernet",
                        "Status": "Connected",
                        "InterfaceIndex": 7,
                    }
                ],
                "connections": [
                    {
                        "InterfaceAlias": "Intel Ethernet",
                        "IPv4Address": "192.168.1.20",
                        "IPv4DefaultGateway": "192.168.1.1",
                        "DNSServer": "223.5.5.5, 1.1.1.1",
                    }
                ],
            },
            "net_io": {
                "bytes_sent_mb": 120,
                "bytes_recv_mb": 900,
                "packets_sent": 1000,
                "packets_recv": 2000,
                "errin": 2,
                "errout": 1,
                "dropin": 0,
                "dropout": 0,
            },
            "connections": {"total": 42, "listening": 8, "established": 11},
            "processes": [
                {"pid": 101, "name": "build.exe", "cpu": 50, "memory_mb": 700},
                {"pid": 102, "name": "browser.exe", "cpu": 12, "memory_mb": 1600},
            ],
            "services": {
                "supported": True,
                "total": 120,
                "running": 85,
                "stopped": 35,
                "paused": 0,
            },
            "battery": {
                "present": True,
                "percentage": 31,
                "charging": False,
                "secsleft": 7200,
            },
        }

        snapshot = compose_insights(raw)

        expected_ids = {
            "health_score",
            "risk_alerts",
            "system_profile",
            "uptime_analysis",
            "cpu_load",
            "cpu_core_heatmap",
            "memory_pressure",
            "swap_pressure",
            "disk_summary",
            "disk_low_space",
            "storage_io",
            "network_throughput",
            "network_errors",
            "active_connections",
            "interface_inventory",
            "dns_snapshot",
            "top_cpu_processes",
            "top_memory_processes",
            "service_summary",
            "battery_runtime",
        }
        feature_ids = {item["id"] for item in snapshot["features"]}

        self.assertEqual(snapshot["feature_count"], 20)
        self.assertEqual(feature_ids, expected_ids)
        self.assertLess(snapshot["summary"]["health_score"], 100)
        self.assertIn("critical", {item["severity"] for item in snapshot["features"]})
        self.assertGreaterEqual(len(snapshot["summary"]["recommendations"]), 3)


class InsightRouteTests(unittest.TestCase):
    def test_snapshot_route_returns_frontend_contract(self):
        from main import create_app

        app = create_app()
        client = app.test_client()

        response = client.get("/api/insights/snapshot")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["feature_count"], 20)
        self.assertIn("summary", payload["data"])
        self.assertIn("features", payload["data"])
        self.assertEqual(len(payload["data"]["features"]), 20)


if __name__ == "__main__":
    unittest.main()

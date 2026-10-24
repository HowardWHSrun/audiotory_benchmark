"""Exercise local API safety/lifecycle with a fake engine; no audio devices."""
import http.client
import json
import threading
import time
import unittest

from bench_app.server import BenchServer


class FakeEngine:
    def __init__(self):
        self.state = "idle"
        self.starts = []
        self.stops = 0

    def status(self):
        return {"state": self.state, "result": None}

    def devices(self):
        return {"devices": [], "backend_available": True, "errors": []}

    def start(self, config):
        if self.state == "running":
            raise RuntimeError("A run is already active")
        self.starts.append(config)
        self.state = "running"
        return self.status()

    def stop(self):
        self.stops += 1
        self.state = "cancelled"
        return self.status()


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.engine = FakeEngine()
        self.server = BenchServer(("127.0.0.1", 0), self.engine, heartbeat_timeout=.1)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        payload = response.read()
        result = response.status, payload, dict(response.getheaders())
        connection.close()
        return result

    def post(self, path, config, **headers):
        base = {"Content-Type": "application/json", "X-SONIC-Token": self.server.token}
        base.update(headers)
        return self.request("POST", path, json.dumps(config), base)

    def test_startup_and_gets_do_not_start_audio(self):
        self.assertEqual(self.request("GET", "/api/session")[0], 200)
        self.assertEqual(self.request("GET", "/api/devices")[0], 200)
        self.assertEqual(self.request("GET", "/api/status")[0], 200)
        self.assertEqual(self.engine.starts, [])
        self.assertEqual(self.engine.state, "idle")

    def test_tokens_origins_and_hosts_required(self):
        for headers in ({"X-SONIC-Token": "wrong"}, {"Origin": "https://other.example"},
                        {"Host": "evil.example"}, {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.post("/api/start", {"action": "stimulus"}, **headers)[0], 403)
        self.assertEqual(self.engine.starts, [])
        self.assertEqual(self.request("GET", "/api/session", headers={"Host": "evil.example"})[0], 403)

    def test_start_stop_and_busy_are_explicit(self):
        self.assertEqual(self.post("/api/start", {"action": "calibrate"})[0], 200)
        self.assertEqual(self.post("/api/start", {"action": "stimulus"})[0], 409)
        self.assertEqual(len(self.engine.starts), 1)
        self.assertEqual(self.post("/api/stop", {})[0], 200)
        self.assertEqual(self.engine.state, "cancelled")

    def test_no_arbitrary_file_serving_or_raw_audio(self):
        for path in ("/../README.md", "/.work/latency/runs/a.wav", "/api/result", "/api/start"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_json_body_validation(self):
        self.assertEqual(self.post("/api/start", ["bad"])[0], 400)
        self.assertEqual(self.post("/api/start", {})[0], 200)
        code, _, headers = self.request("GET", "/api/status")
        self.assertEqual(code, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_lost_browser_heartbeat_stops_active_audio(self):
        self.post("/api/start", {"action": "stimulus"})
        deadline = time.monotonic() + 2
        while self.engine.state == "running" and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertEqual(self.engine.state, "cancelled")
        self.assertGreaterEqual(self.engine.stops, 1)


if __name__ == "__main__":
    unittest.main()

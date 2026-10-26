"""Loopback-only UI for native audio; never opens audio on launch."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
import signal
import sys
import threading
import time
import webbrowser


def data_root():
    if getattr(sys, "frozen", False):
        return Path.home() / "SONIC Bench" / "runs"
    return Path(__file__).resolve().parents[1] / ".work/bench_app/runs"


class BenchServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, engine, *, heartbeat_timeout=12):
        super().__init__(address, Handler)
        self.engine = engine
        self.token = secrets.token_urlsafe(32)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.ui_root = Path(__file__).resolve().parent / "ui"
        self.last_heartbeat = time.monotonic()
        self.heartbeat_timeout = heartbeat_timeout
        self.closed = threading.Event()
        self.watchdog = threading.Thread(target=self._watchdog, daemon=True)
        self.watchdog.start()

    def _watchdog(self):
        while not self.closed.wait(.5):
            if (time.monotonic() - self.last_heartbeat > self.heartbeat_timeout
                    and self.engine.status()["state"] in ("running", "stopping")):
                self.engine.stop()

    def server_close(self):
        self.closed.set()
        self.engine.stop()
        deadline = time.monotonic() + 8
        while self.engine.status()["state"] in ("running", "stopping") and time.monotonic() < deadline:
            time.sleep(.05)
        super().server_close()


class Handler(BaseHTTPRequestHandler):
    server_version = "SONICBench/1"

    def log_message(self, *_):
        pass

    def _trusted_request(self):
        # Host validation blocks DNS rebinding; no CORS, arbitrary file access,
        # or unauthenticated mutations are exposed to other websites.
        expected = f"127.0.0.1:{self.server.server_port}"
        origin = self.headers.get("Origin")
        return (self.headers.get("Host") == expected
                and origin in (None, self.server.origin)
                and self.headers.get("Sec-Fetch-Site") != "cross-site")

    def _send(self, status, body, content_type="application/json"):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        if not self._trusted_request():
            return self._send(403, {"error": "Open the app using its local 127.0.0.1 address."})
        if self.path == "/api/session":
            return self._send(200, {"token": self.server.token, "app": "sonic-bench"})
        if self.path == "/api/status":
            self.server.last_heartbeat = time.monotonic()
            return self._send(200, self.server.engine.status())
        if self.path == "/api/live":
            return self._send(200, self.server.engine.live())
        if self.path == "/api/devices":
            try:
                return self._send(200, self.server.engine.devices())
            except Exception as error:
                return self._send(503, {"error": str(error)})
        if self.path == "/api/result":
            state = self.server.engine.status()
            if state.get("result") is None:
                return self._send(404, {"error": "No completed result is available yet."})
            return self._send(200, state)
        # Explicit asset allowlist: never serve raw room audio or the repository.
        names = {"/": "index.html", "/index.html": "index.html",
                 "/app.js": "app.js", "/styles.css": "styles.css"}
        filename = names.get(self.path)
        if not filename:
            return self._send(404, {"error": "Not found"})
        path = self.server.ui_root / filename
        return self._send(200, path.read_bytes(), mimetypes.guess_type(filename)[0] or "text/plain")

    def do_POST(self):
        # A peer that sends fewer bytes than Content-Length must not retain a
        # request thread indefinitely. Native audio has its own watchdog.
        self.connection.settimeout(3)
        if (not self._trusted_request()
                or not secrets.compare_digest(self.headers.get("X-SONIC-Token", ""), self.server.token)):
            return self._send(403, {"error": "This request needs the current local app session."})
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self._send(415, {"error": "Expected JSON"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 8192:
                raise ValueError("Request body must contain 1–8192 bytes")
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict):
                raise ValueError("Expected a JSON object")
            if self.path == "/api/start":
                self.server.last_heartbeat = time.monotonic()
                return self._send(200, self.server.engine.start(value))
            if self.path == "/api/live/probe":
                self.server.last_heartbeat = time.monotonic()
                return self._send(200, self.server.engine.play_live_probe())
            if self.path == "/api/live/sonic":
                if set(value) != {"enabled"}:
                    raise ValueError("SONIC loop request requires only enabled")
                self.server.last_heartbeat = time.monotonic()
                return self._send(200, self.server.engine.set_live_sonic(value["enabled"]))
            if self.path == "/api/stop":
                return self._send(200, self.server.engine.stop())
            if self.path == "/api/quit":
                self.server.engine.stop()
                self._send(200, {"state": "closed", "message": "SONIC Bench is closing. You can close this tab."})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            return self._send(404, {"error": "Not found"})
        except (ValueError, TypeError, KeyError) as error:
            return self._send(400, {"error": str(error)})
        except RuntimeError as error:
            return self._send(409, {"error": str(error)})
        except Exception as error:
            return self._send(500, {"error": f"Audio operation failed: {error}"})


def smoke_test():
    """Packaged offline check: imports/assets/generator, no device enumeration."""
    import numpy as np
    from latency.stimulus import make_sonic_e_block
    from .engine import AudioEngine, source_provenance
    samples, plan = make_sonic_e_block(96000, tones_per_frequency=1)
    assert samples.shape == (13440,) and np.isfinite(samples).all()
    assert plan["tone_count"] == 14 and plan["exact_original_waveform"] is False
    assert all((Path(__file__).parent / "ui" / name).is_file()
               for name in ("index.html", "app.js", "styles.css"))
    assert AudioEngine(data_root()).status()["state"] == "idle"
    assert len(source_provenance()) == 6
    # Explicitly import the native dependency so a frozen build cannot pass
    # while omitting the lazy sounddevice import or its PortAudio library.
    assert hasattr(AudioEngine(data_root())._audio(), "Stream")
    print("SONIC Bench offline smoke test passed; no audio opened.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0, help="Local port; default chooses an available port")
    parser.add_argument("--no-open", action="store_true", help="Do not open the default browser")
    parser.add_argument("--smoke-test", action="store_true", help="Check packaged assets offline; no audio")
    args = parser.parse_args()
    if args.smoke_test:
        return smoke_test()
    from .engine import AudioEngine
    engine = AudioEngine(data_root())
    with BenchServer(("127.0.0.1", args.port), engine) as server:
        print(f"SONIC Bench: {server.origin}/\nNo sound starts automatically. Ctrl+C quits.", flush=True)
        # Signal handlers run on the main thread; shutdown must run separately.
        def close(*_):
            engine.stop()
            threading.Thread(target=server.shutdown, daemon=True).start()
        for name in ("SIGINT", "SIGTERM"):
            if hasattr(signal, name):
                signal.signal(getattr(signal, name), close)
        if not args.no_open:
            webbrowser.open(server.origin + "/")
        server.serve_forever(poll_interval=.2)


if __name__ == "__main__":
    main()

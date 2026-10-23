"""Serve the local speaker-check player on loopback only; never auto-play audio."""

import argparse
import errno
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.request import urlopen
import webbrowser

from sound_output import CoreAudio


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/output":
            try:
                status = CoreAudio().status()
            except (RuntimeError, OSError) as error:
                status = {"ready": False, "error": str(error)}
            status["player"] = "sonic-speaker-check"
            body = json.dumps(status).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--configure", action="store_true", help="Select Audient output at 96 kHz before serving.")
    parser.add_argument("--open", action="store_true", help="Open the player in your default browser.")
    args = parser.parse_args()
    try:
        audio = CoreAudio()
        if args.configure:
            print(json.dumps(audio.configure(), indent=2), flush=True)
        print(json.dumps(audio.status(), indent=2), flush=True)
    except (RuntimeError, OSError) as error:
        parser.exit(1, f"{error}\n")
    folder = Path(__file__).resolve().parents[1] / "playback"
    handler = partial(Handler, directory=str(folder))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as error:
        if error.errno == errno.EADDRINUSE and args.open:
            try:
                with urlopen(f"http://127.0.0.1:{args.port}/api/output", timeout=2) as response:
                    existing = json.load(response)
                if existing.get("player") == "sonic-speaker-check":
                    webbrowser.open(f"http://127.0.0.1:{args.port}/")
                    print("Opened the already-running sound player.", flush=True)
                    return
            except (OSError, ValueError):
                pass
        parser.exit(1, f"Cannot start the local player on port {args.port}: {error}\n")
    with server:
        print(f"Sound player: http://127.0.0.1:{args.port}/ — Ctrl+C stops the server.", flush=True)
        if args.open:
            webbrowser.open(f"http://127.0.0.1:{args.port}/")
        server.serve_forever()


if __name__ == "__main__":
    main()

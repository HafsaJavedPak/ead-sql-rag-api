"""Static file server for the ead_web console.

The console is a plain browser client of the authenticated HTTP API, so it
only needs to be served as files. Port 3000 is used because it is the origin
already present in CORS_ORIGINS; serving it elsewhere requires adding that
origin to .env before the browser will accept API responses.
"""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "ead_web"


class Handler(SimpleHTTPRequestHandler):
    """Serves ead_web without caching, so edits appear on reload."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()

    if not (ROOT / "index.html").is_file():
        raise SystemExit(f"Console assets not found under {ROOT}")

    handler = partial(Handler, directory=str(ROOT))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"EAD console -> http://localhost:{args.port}")
    print("Requires the API on http://127.0.0.1:8000 (uvicorn ead_api.main:app).")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()

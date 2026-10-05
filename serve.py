"""Serve the course site locally and save progress to progress.json.

    python serve.py          # http://127.0.0.1:8000
    python serve.py 8080     # another port
"""
import http.server
import json
import pathlib
import sys
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent
PROGRESS = ROOT / "progress.json"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/progress":
            return self.send_error(404)
        size = int(self.headers.get("Content-Length", 0))
        if size > 100_000:
            return self.send_error(413)
        try:
            data = json.loads(self.rfile.read(size))
            assert isinstance(data.get("done"), list)
        except Exception:
            return self.send_error(400)
        PROGRESS.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.send_response(204)
        self.end_headers()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # always load the latest pages
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    url = f"http://127.0.0.1:{port}/"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)  # local only
    print(f"Course running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

"""Local demo. The page can change the role; the question cannot."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from safe_agent.access import Principal
from safe_agent.engine import answer
from safe_agent.schema import STATES, YEARS

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "index.html"


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8642), Handler)
    print("Safe generation agent: http://127.0.0.1:8642/")
    server.serve_forever()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            body = PAGE.read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
            return
        if self.path == "/api/schema":
            payload = {
                "years": list(YEARS),
                "states": [{"code": code, "name": name} for code, name in STATES.items() if code != "US"],
                "roles": ["analyst", "state_reader"],
            }
            self._send(200, "application/json", json.dumps(payload).encode())
            return
        self._send(404, "text/plain", b"Not found")

    def do_POST(self) -> None:
        if self.path != "/api/ask":
            self._send(404, "text/plain", b"Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = answer(
                str(payload.get("question", "")),
                Principal(str(payload.get("role", "analyst")), payload.get("state")),
            )
            self._send(200, "application/json", json.dumps(result.to_dict()).encode())
        except json.JSONDecodeError:
            self._send(400, "application/json", b'{"ok": false, "explanation": "The request was not valid JSON."}')

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}")

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    main()

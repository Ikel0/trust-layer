#!/usr/bin/env python3
"""Trust Layer's local web application."""
import argparse
import csv
import io
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from run_quality import analyze

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = {"order_id", "customer_email", "amount", "order_date"}


def read_dataset(content: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(content))
    columns = set(reader.fieldnames or [])
    missing = EXPECTED_COLUMNS - columns
    if missing:
        raise ValueError("Colonnes attendues : " + ", ".join(sorted(EXPECTED_COLUMNS)) + ". Colonnes manquantes : " + ", ".join(sorted(missing)))
    rows = list(reader)
    if not rows:
        raise ValueError("Le fichier ne contient aucune ligne de données.")
    return rows


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/health":
            return self.send_json({"status": "ok", "service": "trust-layer", "checks": ["order_id", "customer_email", "amount", "order_date"]})
        return super().do_GET()
    def do_POST(self):
        if self.path != "/api/check": return self.send_json({"error": "unknown endpoint"}, HTTPStatus.NOT_FOUND)
        try:
            content = self.rfile.read(int(self.headers.get("Content-Length",0))).decode("utf-8-sig")
            return self.send_json(analyze(read_dataset(content), "uploaded.csv"))
        except (UnicodeDecodeError, ValueError) as error:
            return self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--port",type=int,default=int(os.getenv("PORT","8000")));args=parser.parse_args()
    with ThreadingHTTPServer(("0.0.0.0",args.port),Handler) as server: print(f"Trust Layer is running on port {args.port}");server.serve_forever()
if __name__=="__main__":main()

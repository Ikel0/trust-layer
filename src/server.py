#!/usr/bin/env python3
"""Trust Layer's local web application."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from run_quality import analyze

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = {"order_id", "customer_email", "amount", "order_date"}
WORLD_BANK_URL = "https://api.worldbank.org/v2/country/FRA/indicator/SP.POP.TOTL?format=json&per_page=8"
ORDERS_CONTRACT = {
    "id": "orders.v1",
    "version": "1.0.0",
    "owner": "analytics",
    "fields": ["order_id", "customer_email", "amount", "order_date"],
    "controls": ["order_id_not_empty", "order_id_unique", "email_valid", "amount_positive", "order_date_iso"],
}


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


def profile_world_bank_population() -> dict:
    """Fetch a documented public series and profile it like a data source."""
    try:
        with urlopen(WORLD_BANK_URL, timeout=6) as response:
            payload = json.load(response)
        records = [
            {"year": row["date"], "value": row["value"]}
            for row in payload[1]
            if row.get("value") is not None
        ]
        values = [record["value"] for record in records]
        return {
            "status": "ok",
            "live": True,
            "source": "World Bank · World Development Indicators",
            "source_url": WORLD_BANK_URL,
            "dataset": "Population totale, France (SP.POP.TOTL)",
            "records": records,
            "profile": {
                "rows": len(payload[1]),
                "missing_values": len(payload[1]) - len(records),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
            },
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return {
            "status": "unavailable",
            "live": False,
            "source": "World Bank · World Development Indicators",
            "source_url": WORLD_BANK_URL,
            "message": "La source publique est momentanément indisponible. Réessaie dans quelques instants.",
        }


def analyze_upload(content: str) -> dict:
    report = analyze(read_dataset(content), "uploaded.csv")
    report["contract"] = ORDERS_CONTRACT
    report["source_fingerprint"] = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    report["issue_summary"] = dict(Counter(issue["rule"] for issue in report["issues"]))
    return report


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/health":
            return self.send_json({"status": "ok", "service": "trust-layer", "checks": ["order_id", "customer_email", "amount", "order_date"]})
        if self.path == "/api/open-data/world-bank":
            return self.send_json(profile_world_bank_population())
        if self.path == "/api/contracts/orders":
            return self.send_json(ORDERS_CONTRACT)
        return super().do_GET()
    def do_POST(self):
        if self.path != "/api/check": return self.send_json({"error": "unknown endpoint"}, HTTPStatus.NOT_FOUND)
        try:
            content = self.rfile.read(int(self.headers.get("Content-Length",0))).decode("utf-8-sig")
            return self.send_json(analyze_upload(content))
        except (UnicodeDecodeError, ValueError) as error:
            return self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--port",type=int,default=int(os.getenv("PORT","8000")));args=parser.parse_args()
    with ThreadingHTTPServer(("0.0.0.0",args.port),Handler) as server: print(f"Trust Layer is running on port {args.port}");server.serve_forever()
if __name__=="__main__":main()

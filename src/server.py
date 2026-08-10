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
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_POST(self):
        if self.path != "/api/check": self.send_error(HTTPStatus.NOT_FOUND); return
        try:
            content = self.rfile.read(int(self.headers.get("Content-Length",0))).decode("utf-8-sig")
            report = analyze(list(csv.DictReader(io.StringIO(content))), "uploaded.csv")
            body = json.dumps(report,ensure_ascii=False).encode(); self.send_response(HTTPStatus.OK); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
        except Exception as error: self.send_error(HTTPStatus.BAD_REQUEST, str(error))
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--port",type=int,default=int(os.getenv("PORT","8000")));args=parser.parse_args()
    with ThreadingHTTPServer(("0.0.0.0",args.port),Handler) as server: print(f"Trust Layer is running on port {args.port}");server.serve_forever()
if __name__=="__main__":main()

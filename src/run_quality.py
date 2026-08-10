#!/usr/bin/env python3
"""Trust Layer — dependency-free checks for an order CSV."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def analyze(rows: list[dict[str, str]], dataset: str = "dataset.csv") -> dict:
    issues, seen = [], set()
    for line, row in enumerate(rows, start=2):
        order_id = row.get("order_id", "").strip()
        if not order_id: issues.append({"rule":"order_id_not_empty", "line":line, "detail":"Identifiant obligatoire"})
        elif order_id in seen: issues.append({"rule":"order_id_unique", "line":line, "detail":"Identifiant dupliqué"})
        seen.add(order_id)
        if not EMAIL.match(row.get("customer_email", "").strip()): issues.append({"rule":"email_valid", "line":line, "detail":"Email invalide"})
        try:
            if float(row.get("amount", "")) < 0: issues.append({"rule":"amount_positive", "line":line, "detail":"Montant négatif"})
        except ValueError: issues.append({"rule":"amount_numeric", "line":line, "detail":"Montant non numérique"})
        try: datetime.strptime(row.get("order_date", ""), "%Y-%m-%d")
        except ValueError: issues.append({"rule":"order_date_iso", "line":line, "detail":"Date attendue : YYYY-MM-DD"})
    return {"dataset":dataset, "rows":len(rows), "status":"failed" if issues else "passed", "issues":issues}

def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, default=root / "data/orders.csv"); parser.add_argument("--output", type=Path, default=root / "out"); args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as handle: report = analyze(list(csv.DictReader(handle)), args.input.name)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = "# Trust Layer report\n\n" + "\n".join(f"- Ligne {i['line']} · `{i['rule']}` : {i['detail']}" for i in report["issues"])
    (args.output / "report.md").write_text(markdown + "\n", encoding="utf-8")
    print(json.dumps({"status":report["status"], "issues":len(report["issues"])}, ensure_ascii=False))
    return 1 if report["issues"] else 0

if __name__ == "__main__": sys.exit(main())

#!/usr/bin/env python3
"""Trust Layer — dependency-free CSV quality checks."""
import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def add_issue(issues, rule, line, detail):
    issues.append({"rule": rule, "line": line, "detail": detail})

def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=root / "data/orders.csv")
    parser.add_argument("--output", type=Path, default=root / "out")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    issues, seen = [], set()
    for line, row in enumerate(rows, start=2):
        order_id = row["order_id"].strip()
        if not order_id:
            add_issue(issues, "order_id_not_empty", line, "Identifiant obligatoire")
        elif order_id in seen:
            add_issue(issues, "order_id_unique", line, "Identifiant dupliqué")
        seen.add(order_id)
        if not EMAIL.match(row["customer_email"].strip()):
            add_issue(issues, "email_valid", line, "Email invalide")
        try:
            if float(row["amount"]) < 0:
                add_issue(issues, "amount_positive", line, "Montant négatif")
        except ValueError:
            add_issue(issues, "amount_numeric", line, "Montant non numérique")
        try:
            datetime.strptime(row["order_date"], "%Y-%m-%d")
        except ValueError:
            add_issue(issues, "order_date_iso", line, "Date attendue : YYYY-MM-DD")
    report = {"dataset": args.input.name, "rows": len(rows), "status": "failed" if issues else "passed", "issues": issues}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = "# Trust Layer report\n\n" + "\n".join(f"- Ligne {i['line']} · `{i['rule']}` : {i['detail']}" for i in issues)
    (args.output / "report.md").write_text(markdown + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "issues": len(issues)}, ensure_ascii=False))
    return 1 if issues else 0

if __name__ == "__main__":
    sys.exit(main())

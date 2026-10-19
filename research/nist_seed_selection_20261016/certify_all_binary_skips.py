#!/usr/bin/env python3
"""Construct subgroup points for every earlier binary X9.62 survivor."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari

from certify_binary_orders import build_field, certify


ROOT = Path(__file__).resolve().parent


def main():
    targets = [row for row in json.loads((ROOT / "targets.json").read_text()) if row["kind"] == "binary"]
    pari = Pari()
    records = []
    for target in targets:
        field = build_field(target)
        path = ROOT / "raw" / "evaluations" / target["name"] / f"{1:05d}-{target['candidate_index']:05d}.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()[1:]]
        for row in rows[:-1]:
            if row["status"] == "COUNTED" and row["checks"]["x9_reference_accept"]:
                records.append(certify(target, row, field, pari))
    if not records or not all(row["group_order_certified"] for row in records):
        raise ArithmeticError("binary skipped-candidate certificate failed")
    output = ROOT / "raw" / "binary_all_skipped_x9_certificates.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps({"method": "independent_scalar_multiplication_plus_hasse",
                                  "certificates": records}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"certificates": len(records), "all_certified": True,
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare torsion shortcuts with the full P-192 and P-256 counts."""

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()[1:]]


def main():
    full = ROOT / "raw" / "evaluations" / "P-192" / "00001-00139.jsonl"
    fast = ROOT / "raw" / "family_evaluations" / "P-192" / "00001-00139.jsonl"
    a, b = rows(full), rows(fast)
    if len(a) != len(b) or len(a) != 139:
        raise ArithmeticError("P-192 control cardinality changed")
    for earlier, screened in zip(a, b):
        if earlier["index"] != screened["index"]:
            raise ArithmeticError("candidate alignment changed")
        if screened["status"] == "COUNTED" and (
            earlier["canonical"]["order"] != screened["canonical"]["order"] or
            earlier["other"]["order"] != screened["other"]["order"]
        ):
            raise ArithmeticError("point count mismatch")
        full_accept = earlier["status"] == "COUNTED" and (
            earlier["canonical"]["family_accept"] or earlier["other"]["family_accept"])
        fast_accept = screened["family_accept_canonical"] or screened["family_accept_other"]
        if full_accept != fast_accept:
            raise ArithmeticError(f"family decision mismatch at {earlier['index']}")
    p256_full = rows(ROOT / "raw" / "evaluations" / "P-256" / "00876-00876.jsonl")[0]
    p256_fast = rows(ROOT / "raw" / "family_evaluations" / "P-256" / "00876-00876.jsonl")[0]
    if p256_full["canonical"]["order"] != p256_fast["canonical"]["order"] or p256_full["other"]["order"] != p256_fast["other"]["order"]:
        raise ArithmeticError("P-256 index 876 control mismatch")
    output = ROOT / "raw" / "fast_evaluator_controls.json"
    if output.exists():
        raise FileExistsError(output)
    result = {"p192_full_grid": 139, "p192_family_decisions_match": True,
              "p192_fast_statuses": dict(Counter(row["status"] for row in b)),
              "p256_876_both_branch_orders_match": True,
              "source_sha256": {"p192_full": hashlib.sha256(full.read_bytes()).hexdigest(),
                                "p192_fast": hashlib.sha256(fast.read_bytes()).hexdigest()}}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": True, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

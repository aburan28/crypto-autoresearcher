#!/usr/bin/env python3
"""Bounded controls for both prime seed mappings and count reuse."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari
from sage.all import EllipticCurve, GF

from evaluate_x9_remaining import evaluate


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # The first control record binds the pre-retry family loader. Keep it
    # immutable and issue a new control after the loader gained segments.
    output = ROOT / "raw" / "x9_evaluator_controls_v2.json"
    if output.exists():
        raise FileExistsError(output)
    target = next(row for row in json.loads((ROOT / "targets.json").read_text()) if row["name"] == "P-192")
    p = int(target["p"])
    indices = (6, 7, 15, 139)
    candidates = {}
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        row = json.loads(line)
        if row["target"] == "P-192" and row["index"] in indices:
            candidates[row["index"]] = row
    family_path = ROOT / "raw" / "evaluations" / "P-192" / "00001-00139.jsonl"
    family = {row["index"]: row for row in
              (json.loads(line) for line in family_path.read_text().splitlines()[1:]) if row["index"] in indices}
    if set(candidates) != set(indices) or set(family) != set(indices):
        raise ArithmeticError("control rows missing")
    pari = Pari()
    records = []
    for index in indices:
        row = candidates[index]
        observed = evaluate(row, family[index], p, pari)
        unmasked = observed["unmasked"]
        strict = observed["strict_x9"]
        if family[index]["status"] == "COUNTED":
            reused = unmasked["status"] == "REUSED_FAMILY_COUNT" and all(
                unmasked[side]["order"] == family[index][side]["order"]
                for side in ("canonical", "other"))
        else:
            reused = unmasked["status"].startswith("NO_CURVE_")
        if strict["status"] == "REUSED_UNMASKED":
            strict = unmasked
        if strict["status"] == "COUNTED" or strict["status"] == "REUSED_FAMILY_COUNT":
            curve = EllipticCurve(GF(p), [-3, int(strict["canonical_b"], 16)])
            sage_order = int(curve.cardinality())
            sage_match = sage_order == int(strict["canonical"]["order"])
        else:
            sage_match = False
        records.append({"index": index, "unmasked_reuse_or_no_curve": reused,
                        "strict_status": observed["strict_x9"]["status"],
                        "strict_sage_order_matches": sage_match,
                        "strict_c_same": observed["strict_x9_same_c"]})
    if not all(item["unmasked_reuse_or_no_curve"] and item["strict_sage_order_matches"] for item in records):
        raise ArithmeticError("X9 evaluator control failed")
    result = {"candidate_sha256": digest(ROOT / "raw" / "candidates.jsonl"),
              "family_sha256": digest(family_path),
              "evaluator_sha256": digest(ROOT / "evaluate_x9_remaining.py"),
              "controls": records, "all_passed": True}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"controls": len(records), "all_passed": True,
                      "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()

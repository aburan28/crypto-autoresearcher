#!/usr/bin/env python3
"""Sensitivity of complete-stream X9.62 survivors to public free parameters."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def largest_prime_factor(value):
    largest = 1
    remainder = value
    for prime in range(2, 256):
        if all(prime % d for d in range(2, math.isqrt(prime) + 1)):
            while remainder % prime == 0:
                remainder //= prime
                largest = prime
    if remainder != 1:
        raise ArithmeticError("reference smooth cofactor has factor above 255")
    return largest


def main():
    source = ROOT / "raw" / "analysis_summary.json"
    summary = json.loads(source.read_text())
    candidates = []
    for name, item in summary["binary"].items():
        for row in item["earlier_x9_255_reference"]:
            candidates.append({"target": name, "index": row["index"], "cofactor": int(row["cofactor"]),
                               "subgroup": int(row["prime_subgroup"])})
    for row in summary["P-192"]["earlier_strict_x9_255_reference"]:
        candidates.append({"target": "P-192", "index": row["index"], "cofactor": int(row["cofactor"]),
                           "subgroup": int(row["prime_subgroup"])})
    rows = []
    for candidate in candidates:
        rows.append({**{key: candidate[key] for key in ("target", "index", "cofactor")},
                     "largest_cofactor_prime": largest_prime_factor(candidate["cofactor"]),
                     "subgroup_bits": candidate["subgroup"].bit_length()})
    grid = {}
    for limit in (7, 15, 31, 63, 127, 255):
        for minimum_exponent in (160, 180, 200):
            selected = [row for row, candidate in zip(rows, candidates) if row["largest_cofactor_prime"] <= limit and candidate["subgroup"] > 2**minimum_exponent]
            grid[f"lmax_{limit}_r_gt_2pow{minimum_exponent}"] = {
                "count": len(selected),
                "ids": [f"{row['target']}:{row['index']}" for row in selected],
            }
    output = ROOT / "raw" / "x9_sensitivity.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps({"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                  "eligible_at_reference_255_160": len(rows),
                                  "candidate_requirements": rows, "grid": grid}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"candidates": len(rows), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

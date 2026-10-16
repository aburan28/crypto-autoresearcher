#!/usr/bin/env python3
"""Exact 3-divisibility screen for odd-order prime-field candidates."""

import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

from cypari2 import Pari


ROOT = Path(__file__).resolve().parent


def has_rational_three_torsion(pari, variable, p, b):
    # The 3-division polynomial for y^2=x^3-3x+b is
    # 3x^4-18x^2+12bx-9. A root lifts to an F_p point iff its RHS is square.
    polynomial = 3 * variable**4 - 18 * variable**2 + 12 * b * variable - 9
    roots = []
    for root in pari.polrootsmod(polynomial, p):
        x = int(root)
        rhs = (x**3 - 3 * x + b) % p
        if rhs == 0 or pow(rhs, (p - 1) // 2, p) == 1:
            roots.append(x)
    return roots


def main():
    candidates = ROOT / "raw" / "candidates.jsonl"
    previous = ROOT / "raw" / "prime_2torsion_screen.jsonl"
    output = ROOT / "raw" / "prime_3torsion_screen.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    pari = Pari()
    variable = pari("x")
    cache = {}
    counts = Counter()
    started = time.monotonic()
    with candidates.open() as source, previous.open() as prev, partial.open("w") as sink:
        prev.readline()
        sink.write(json.dumps({"record": "run", "candidate_sha256": hashlib.sha256(candidates.read_bytes()).hexdigest(),
                               "previous_sha256": hashlib.sha256(previous.read_bytes()).hexdigest(),
                               "method": "PARI_3division_polynomial_and_quadratic_residue", "pid": os.getpid()}, sort_keys=True) + "\n")
        for line in source:
            row = json.loads(line)
            if row["kind"] != "prime":
                continue
            prior = json.loads(prev.readline())
            if prior["target"] != row["target"] or prior["index"] != row["index"]:
                raise ArithmeticError("candidate and prior screen differ")
            result = {"target": row["target"], "index": row["index"], "prior_status": prior["status"]}
            if prior["status"] == "ODD_ORDER_PENDING_COUNT":
                p = int(targets[row["target"]]["p"])
                roots = [int(b, 16) for b in row["variants"]["nist_fips_186_2"]["b_roots"]]
                for label, b in zip(("root_low", "root_high"), roots):
                    key = (p, b)
                    if key not in cache:
                        cache[key] = has_rational_three_torsion(pari, variable, p, b)
                    result[label] = "DIVISIBLE_BY_3" if cache[key] else "PENDING_COUNT"
                    result[label + "_point_x"] = [hex(x) for x in cache[key]]
                    counts[result[label]] += 1
            sink.write(json.dumps(result, sort_keys=True) + "\n")
        sink.write(json.dumps({"record": "finish", "counts": dict(counts),
                               "elapsed_seconds": round(time.monotonic() - started, 6)}, sort_keys=True) + "\n")
    os.replace(partial, output)
    print(json.dumps({"counts": dict(counts), "output": str(output),
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()

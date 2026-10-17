"""Save exact p-1 divisor fit for public ICPERF prime-curve fixtures.

Run with Sage Python. This is a derived capacity/eligibility record, not a
relation yield, degree-of-regularity, or complete-cost measurement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.index_calculus.factor_base import default_fb_size  # noqa: E402
from tools.icperf_prime_fixture import verify_record  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    from sage.all import Integer  # type: ignore
    from sage.version import version as sage_version  # type: ignore

    rows = []
    for bits in (50, 53, 63):
        path = args.fixture_dir / f"n{bits}_seed20261017.json"
        fixture = json.loads(path.read_text())
        verify_record(fixture)
        p, order = fixture["curve"]["p"], fixture["curve"]["order"]
        factors = [(int(q), int(e)) for q, e in Integer(p - 1).factor()]
        if not all(Integer(q).is_prime(proof=True) for q, _ in factors):
            raise AssertionError("unproved p-1 factor")
        product = 1
        for q, e in factors:
            product *= q**e
        if product != p - 1:
            raise AssertionError("factorization does not reconstruct p-1")
        divisors = [int(d) for d in Integer(p - 1).divisors()]
        cells = []
        for m in range(2, 9):
            target_size = default_fb_size(order, m)
            twice = 2 * target_size
            d = min(divisors, key=lambda value: (abs(value - twice), value))
            cells.append({"m": m, "target_base_size": target_size,
                          "nearest_divisor": d,
                          "absolute_divisor_gap": abs(d - twice),
                          "relative_gap_numerator": abs(d - twice),
                          "relative_gap_denominator": twice,
                          "within_15_percent": 20 * abs(d - twice) <= 3 * twice})
        rows.append({"bits": bits, "fixture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "p": p, "group_order": order, "p_minus_one_factors": factors,
                     "divisor_count": len(divisors), "cells": cells})
    output = {"schema": "icperf-prime-divisor-fit-v1", "seed": 20261017,
              "arity_range": [2, 8], "sage_version": sage_version,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rows": rows,
              "scope": "exact field-divisor eligibility only; no realized factor-base, relation, DREG or cost claim"}
    with args.out.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "rows": len(rows), "status": "written"},
                     sort_keys=True))


if __name__ == "__main__":
    main()

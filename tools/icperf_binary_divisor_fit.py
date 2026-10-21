"""Exact multiplicative-divisor eligibility screen for binary-field IC bases.

This screens field orders only. It constructs no binary curve or factor base and
does not measure relation yield, degree of regularity, or end-to-end cost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from sympy import __version__ as sympy_version
from sympy import divisors, factorint, isprime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.index_calculus.factor_base import default_fb_size  # noqa: E402


def screen(bits: int) -> dict:
    q = 1 << bits
    order_radius = math.isqrt(4 * q)
    order_min, order_max = q + 1 - order_radius, q + 1 + order_radius
    factors = factorint(q - 1)
    if math.prod(int(p) ** int(e) for p, e in factors.items()) != q - 1:
        raise AssertionError("incomplete factorization")
    if not all(isprime(p) for p in factors):
        raise AssertionError("unproved prime factor")
    ds = [int(d) for d in divisors(q - 1)]
    cells = []
    for m in range(2, 9):
        b_min = default_fb_size(order_min, m)
        b_max = default_fb_size(order_max, m)
        b_nominal = default_fb_size(q, m)
        d = min(ds, key=lambda value: (abs(value - 2 * b_nominal), value))
        # Report both endpoint distances so a curve's actual group order can be
        # checked against this screen without pretending the nominal size exact.
        cells.append({"m": m, "base_size_at_order_min": b_min,
                      "base_size_at_order_max": b_max,
                      "nominal_base_size": b_nominal, "nearest_divisor": d,
                      "nominal_gap_numerator": abs(d - 2 * b_nominal),
                      "nominal_gap_denominator": 2 * b_nominal,
                      "within_15_percent_nominal": 20 * abs(d - 2 * b_nominal) <= 3 * 2 * b_nominal})
    return {"bits": bits, "field_order": q, "multiplicative_order": q - 1,
            "hasse_group_order_interval": [order_min, order_max],
            "factorization": [[int(p), int(e)] for p, e in sorted(factors.items())],
            "divisor_count": len(ds), "cells": cells}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    record = {"schema": "icperf-binary-field-divisor-fit-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "sympy_version": sympy_version, "arity_range": [2, 8],
              "rows": [screen(bits) for bits in (50, 53, 63)],
              "scope": "field eligibility only; no binary curve, realized base, system or cost measurement"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "status": "written", "rows": len(record["rows"])}, sort_keys=True))


if __name__ == "__main__":
    main()

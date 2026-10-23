"""Exact group-order and prime-subgroup screen for binary Koblitz E_a/F_2.

E_a: y^2 + xy = x^3 + a*x^2 + 1, a in {0,1}.  Over F_2, the
Frobenius trace is -1 for a=0 and +1 for a=1.  The trace recurrence gives
the order over F_(2^n).  This is input selection, not an ECDLP trial.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from sympy import __version__ as sympy_version
from sympy import factorint
from sympy.ntheory.primetest import mr

MR64_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def prime64(n: int) -> bool:
    """Deterministic Miller–Rabin for n < 2^64, independent of GMPY paths."""
    if not 2 <= n < 1 << 64:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    return bool(mr(n, MR64_BASES))


def count_over_f2(a: int) -> int:
    count = 1  # identity
    for x in (0, 1):
        for y in (0, 1):
            if (y * y + x * y - x * x * x - a * x * x - 1) % 2 == 0:
                count += 1
    return count


def rows_for(a: int) -> list[dict]:
    t1 = 3 - count_over_f2(a)
    assert t1 == (-1 if a == 0 else 1)
    tm2, tm1 = 2, t1
    rows = []
    for n in range(2, 64):
        tm2, tm1 = tm1, t1 * tm1 - 2 * tm2
        if n < 50:
            continue
        order = (1 << n) + 1 - tm1
        factors = factorint(order)
        assert all(prime64(int(p)) for p in factors)
        assert order == math.prod(int(p) ** int(e) for p, e in factors.items())
        r = max(int(p) for p in factors)
        rows.append({"a": a, "field_degree": n, "trace": tm1,
                     "group_order": order,
                     "prime_factorization": [[int(p), int(e)] for p, e in sorted(factors.items())],
                     "largest_prime_subgroup_order": r,
                     "largest_prime_subgroup_bits": r.bit_length(),
                     "cofactor_for_largest_prime": order // r,
                     "has_subgroup_at_least_2pow50": r >= 1 << 50})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = {"schema": "icperf-koblitz-size-screen-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "sympy_version": sympy_version, "field_degree_range": [50, 63],
              "primality_witnesses": list(MR64_BASES),
              "curves": [{"a": a, "f2_points": count_over_f2(a),
                          "f2_trace": 3 - count_over_f2(a),
                          "rows": rows_for(a)} for a in (0, 1)],
              "scope": "exact group-order selection for E_a over F_2; no run, cost, or DLP claim"}
    assert all(not row["has_subgroup_at_least_2pow50"]
               for curve in record["curves"] for row in curve["rows"])
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "rows": 28, "status": "written"}, sort_keys=True))


if __name__ == "__main__":
    main()

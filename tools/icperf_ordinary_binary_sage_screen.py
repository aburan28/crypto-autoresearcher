"""Bounded, deterministic ordinary-binary group-order input screen.

Run with Sage Python. This selects a public curve; it does not run an ECDLP
experiment. Search b=2..33 in the fixed polynomial basis and stop at the first
certified prime factor in [2^50,2^63]. Preserve every attempted row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, PolynomialRing
from sage.version import version as sage_version
from sympy import factorint
from sympy.ntheory.primetest import mr

MR64_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def prime64(n: int) -> bool:
    if not 2 <= n < 1 << 64:
        return False
    return bool(mr(n, MR64_BASES))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    polynomial_ring = PolynomialRing(GF(2), "t")
    t = polynomial_ring.gen()
    polynomial = t**61 + t**5 + t**2 + t + 1
    assert polynomial.is_irreducible()
    field = GF(2**61, name="z", modulus=polynomial)
    z = field.gen()

    def field_element(bits: int):
        return sum((z**i for i in range(61) if (bits >> i) & 1), field.zero())

    rows = []
    for b_bits in range(2, 34):
        b = field_element(b_bits)
        assert b != 0 and b not in GF(2)  # j=1/b is outside F_2.
        curve = EllipticCurve(field, [1, 0, 0, 0, b])
        order = int(curve.cardinality())
        attempted = factorint(order, limit=100_000)
        assert math.prod(int(p) ** int(e) for p, e in attempted.items()) == order
        factors = [{"factor": int(p), "exponent": int(e),
                    "prime64": prime64(int(p))} for p, e in sorted(attempted.items())]
        assert all(item["prime64"] for item in factors)
        candidates = [int(p) for p in attempted
                      if (1 << 50) <= int(p) <= (1 << 63) and prime64(int(p))]
        rows.append({"b_polynomial_bits": b_bits, "group_order": order,
                     "exact_prime_factorization": factors,
                     "certified_prime_candidates": sorted(candidates),
                     "no_prime_in_target_interval": not candidates})
        if candidates:
            break
    assert rows[-1]["b_polynomial_bits"] == 31
    assert rows[-1]["certified_prime_candidates"] == [576460752557211763]
    record = {"schema": "icperf-ordinary-binary-screen-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version, "sage_version": sage_version,
              "field_degree": 61, "field_polynomial_exponents": [61, 5, 2, 1, 0],
              "curve_equation": "y^2 + xy = x^3 + b",
              "b_search": {"first": 2, "last_allowed": 33,
                           "stop": "first certified prime factor in [2^50,2^63]"},
              "primality_witnesses": list(MR64_BASES), "rows": rows,
              "scope": "bounded 30-curve public input selection; all attempted group orders fully factored and prime-checked; no DLP or performance measurement"}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "attempted_curves": len(rows),
                      "selected_b": rows[-1]["b_polynomial_bits"]}, sort_keys=True))


if __name__ == "__main__":
    main()

"""Independently replay the ordinary-binary fixture in Sage curve arithmetic."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from math import isqrt
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing
from sage.version import version as sage_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    rec = json.loads(fixture_bytes)
    n = rec["field_degree"]
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    polynomial = sum(t**i for i in rec["field_polynomial_exponents"])
    assert polynomial.is_irreducible()
    field = GF(2**n, name="z", modulus=polynomial)
    z = field.gen()

    def field_element(bits: int):
        return sum((z**i for i in range(n) if (int(bits) >> i) & 1), field.zero())

    b = field_element(rec["b_polynomial_bits"])
    curve = EllipticCurve(field, [1, 0, 0, 0, b])
    j = curve.j_invariant()
    assert j**2 != j  # Not defined over F_2 up to algebraic-closure isomorphism.
    source = curve(field_element(rec["source_point"][0]),
                   field_element(rec["source_point"][1]))
    generator = curve(field_element(rec["generator"][0]),
                      field_element(rec["generator"][1]))
    r = Integer(rec["prime_order"])
    h = Integer(rec["cofactor"])
    assert r.is_prime(proof=True)
    assert h * source == generator and generator != curve(0)
    assert r * generator == curve(0)
    q = 1 << n
    bound = isqrt(4 * q)
    assert (q + 1 - bound + int(r) - 1) // int(r) == (q + 1 + bound) // int(r) == int(h)
    assert int(curve.cardinality()) == int(h * r)
    record = {"schema": "icperf-ordinary-binary-sage-replay-v1",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "python_version": sys.version, "sage_version": sage_version,
              "checks": {"field_irreducible": True, "j_outside_f2": True,
                         "source_and_generator_valid": True, "r_prime_proved": True,
                         "cofactor_projection": True, "r_times_generator_identity": True,
                         "hasse_unique_multiple": True, "sage_cardinality_agrees": True},
              "field_degree": n, "prime_order": int(r),
              "group_order": int(h * r)}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "verified": True}, sort_keys=True))


if __name__ == "__main__":
    main()

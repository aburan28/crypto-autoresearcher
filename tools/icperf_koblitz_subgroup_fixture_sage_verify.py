"""Independently replay Koblitz subgroup fixtures in Sage's curve arithmetic."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing


def field_element(bits: int, generator, degree: int, field):
    return sum((generator**i for i in range(degree) if (bits >> i) & 1), field.zero())


def check(rec: dict) -> dict:
    n = rec["field_degree"]
    poly_ring = PolynomialRing(GF(2), "t")
    t = poly_ring.gen()
    polynomial = t**n + t**rec["field_polynomial_exponents"][1] + 1
    assert polynomial.is_irreducible()
    field = GF(2**n, name="z", modulus=polynomial)
    z = field.gen()
    convert = lambda bits: field_element(int(bits), z, n, field)
    curve = EllipticCurve(field, [1, rec["a"], 0, 0, 1])
    source = curve(convert(rec["source_point"][0]), convert(rec["source_point"][1]))
    generator = curve(convert(rec["generator"][0]), convert(rec["generator"][1]))
    r = Integer(rec["prime_order"])
    assert r.is_prime(proof=True)
    assert Integer(rec["cofactor"]) * source == generator
    assert r * generator == curve(0)
    assert Integer(rec["group_order"]) * source == curve(0)
    assert generator != curve(0)
    return {"a": rec["a"], "field_degree": n, "prime_order": int(r),
            "irreducible": True, "prime_proven": True, "curve_points_valid": True,
            "cofactor_projection_valid": True, "generator_order_valid": True,
            "source_group_order_valid": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes = args.fixtures.read_bytes()
    fixtures = json.loads(fixture_bytes)["fixtures"]
    checks = [check(rec) for rec in fixtures]
    assert len(checks) == 3
    record = {"schema": "icperf-koblitz-subgroup-sage-replay-v1",
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version,
              "method": "Sage finite fields, irreducibility, primality proof, and elliptic-curve scalar arithmetic",
              "checks": checks}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "verified_fixtures": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()

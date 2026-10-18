"""Independent Sage replay of the target-blind Koblitz orbit-base input screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing


def bits_of(element) -> int:
    return sum(int(coefficient) << exponent
               for exponent, coefficient in enumerate(element.polynomial()))


def poly_bits(polynomial) -> int:
    return sum(int(coefficient) << exponent
               for exponent, coefficient in enumerate(polynomial))


def binary_product(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def replay(record: dict, fixture: dict) -> dict:
    n = fixture["field_degree"]
    assert (fixture["a"], n, fixture["cofactor"], fixture["prime_order"]) == (
        1, 73, 1754, 5384682420498870703)
    ring = PolynomialRing(GF(2), "t")
    t = ring.gen()
    modulus = t**n + t**fixture["field_polynomial_exponents"][1] + 1
    assert modulus.is_irreducible()
    field = GF(2**n, name="z", modulus=modulus)
    z = field.gen()
    def field_of(bits: int):
        return sum((z**i for i in range(n) if (int(bits) >> i) & 1), field.zero())
    curve = EllipticCurve(field, [1, fixture["a"], 0, 0, 1])
    zero = curve(0)
    h = Integer(fixture["cofactor"])
    r = Integer(fixture["prime_order"])
    assert r.is_prime(proof=True)
    generator = curve(field_of(fixture["generator"][0]),
                      field_of(fixture["generator"][1]))
    assert r * generator == zero
    lam = Integer(record["frobenius_scalar_mod_r"])
    tau_g = curve(generator[0]**2, generator[1]**2)
    assert lam * generator == tau_g
    assert (lam**2 - lam + 2) % r == 0 and pow(lam, n, r) == 1

    seen_keys: set[int] = set()
    candidates: list[dict] = []
    counts = {"raw_x_attempts": 0, "nonliftable": 0,
              "projection_identity": 0, "duplicate_x_orbit": 0}
    for raw_x in range(record["parameters"]["raw_x_min"],
                       record["parameters"]["raw_x_max"] + 1):
        counts["raw_x_attempts"] += 1
        lifts = curve.lift_x(field_of(raw_x), all=True)
        if not lifts:
            counts["nonliftable"] += 1
            continue
        projected = h * lifts[0]
        if projected == zero:
            counts["projection_identity"] += 1
            continue
        x = projected[0]
        conjugates = [x**(2**j) for j in range(n)]
        assert conjugates[-1]**2 == x
        assert len(set(conjugates)) == n
        key = min(bits_of(value) for value in conjugates)
        if key in seen_keys:
            counts["duplicate_x_orbit"] += 1
            continue
        seen_keys.add(key)
        minimal = poly_bits(x.minpoly())
        assert minimal.bit_length() - 1 == n
        candidates.append({"raw_x": raw_x, "orbit_key": key,
                           "minpoly": minimal, "minpoly_weight": minimal.bit_count()})
    counts["distinct_orbits"] = len(candidates)
    assert counts == record["counts"]
    assert len(candidates) == len(record["candidate_orbits"])
    for derived, archived in zip(candidates, record["candidate_orbits"]):
        assert (derived["raw_x"], derived["orbit_key"], hex(derived["minpoly"]),
                derived["minpoly_weight"]) == (
                    archived["raw_x"], archived["orbit_key"],
                    archived["minpoly_hex"], archived["minpoly_weight"])

    product = 1
    remaining = list(candidates)
    selected = []
    for _ in range(record["parameters"]["selected_orbits"]):
        chosen = min(remaining, key=lambda row: (
            binary_product(product, row["minpoly"]).bit_count(), row["raw_x"]))
        selected.append(chosen)
        remaining.remove(chosen)
        product = binary_product(product, chosen["minpoly"])
    assert [row["raw_x"] for row in selected] == [
        row["raw_x"] for row in record["selected"]]
    assert hex(product) == record["membership"]["polynomial_hex"]
    assert product.bit_count() == record["membership"]["term_count"]
    assert product.bit_length() - 1 == record["membership"]["degree"]

    first_product = 1
    for row in candidates[:len(selected)]:
        first_product = binary_product(first_product, row["minpoly"])
    assert first_product.bit_count() == record["controls"]["first_five_term_count"]
    for archived in record["controls"]["random_orbit_panels"]:
        rows = random.Random(archived["seed"]).sample(candidates, len(selected))
        control = 1
        for row in rows:
            control = binary_product(control, row["minpoly"])
        assert sorted(row["raw_x"] for row in rows) == archived["raw_x"]
        assert control.bit_count() == archived["term_count"]

    base_rows = record["base_points"]
    assert len(base_rows) == len(selected) * n
    product_polynomial = sum((t**exponent for exponent in range(product.bit_length())
                              if (product >> exponent) & 1), ring.zero())
    for slot, archived in enumerate(record["selected"]):
        raw = curve(field_of(archived["raw_point"][0]),
                    field_of(archived["raw_point"][1]))
        point = curve(field_of(archived["projected_point"][0]),
                      field_of(archived["projected_point"][1]))
        assert h * raw == point and r * point == zero
        assert lam * point == curve(point[0]**2, point[1]**2)
        current = point
        for phase in range(n):
            row = base_rows[slot * n + phase]
            assert row["orbit"] == slot and row["phase"] == phase
            assert [bits_of(current[0]), bits_of(current[1])] == row["point"]
            assert product_polynomial(current[0]) == 0
            current = curve(current[0]**2, current[1]**2)
        assert current == point
    assert len({row["point"][0] for row in base_rows}) == len(base_rows)
    return {"candidate_orbits": len(candidates), "selected_orbits": len(selected),
            "base_representatives": len(base_rows),
            "membership_degree": product.bit_length() - 1,
            "membership_terms": product.bit_count(),
            "first_control_terms": first_product.bit_count(),
            "random_controls": len(record["controls"]["random_orbit_panels"]),
            "group_and_polynomial_checks": "PASS"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_bytes = args.base.read_bytes()
    fixture_bytes = args.fixture.read_bytes()
    record = json.loads(base_bytes)
    fixture = next(row for row in json.loads(fixture_bytes)["fixtures"]
                   if (row["a"], row["field_degree"]) == (1, 73))
    result = {"schema": "icperf-koblitz-orbit-base-sage-replay-v1",
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version,
              "method": "independent Sage field, point, minimal-polynomial and selection replay",
              "result": replay(record, fixture)}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result["result"], sort_keys=True))


if __name__ == "__main__":
    main()

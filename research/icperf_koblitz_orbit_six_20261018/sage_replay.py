"""Independent Sage replay of the six-orbit Koblitz input successor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer, PolynomialRing


def bits_of(element) -> int:
    return sum(int(c) << i for i, c in enumerate(element.polynomial()))


def poly_bits(polynomial) -> int:
    return sum(int(c) << i for i, c in enumerate(polynomial))


def binary_product(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def product(rows: list[dict]) -> int:
    value = 1
    for row in rows:
        value = binary_product(value, row["minimal"])
    return value


def replay(record: dict, parent: dict, fixture: dict) -> dict:
    assert (fixture["a"], fixture["field_degree"], fixture["prime_order"]) == (
        1, 73, 5384682420498870703)
    n = fixture["field_degree"]
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
    r = Integer(fixture["prime_order"])
    h = Integer(fixture["cofactor"])
    assert r.is_prime(proof=True)
    generator = curve(field_of(fixture["generator"][0]),
                      field_of(fixture["generator"][1]))
    assert r * generator == zero
    lam = Integer(parent["frobenius_scalar_mod_r"])
    assert lam * generator == curve(generator[0]**2, generator[1]**2)

    candidates = []
    seen = set()
    for raw_x in range(parent["parameters"]["raw_x_min"],
                       parent["parameters"]["raw_x_max"] + 1):
        lifts = curve.lift_x(field_of(raw_x), all=True)
        if not lifts:
            continue
        projected = h * lifts[0]
        if projected == zero:
            continue
        conjugates = [projected[0]**(2**i) for i in range(n)]
        assert len(set(conjugates)) == n
        key = min(bits_of(value) for value in conjugates)
        if key in seen:
            continue
        seen.add(key)
        minimal = poly_bits(projected[0].minpoly())
        candidates.append({"raw_x": raw_x, "key": key,
                           "minimal": minimal, "projected": projected})
    assert len(candidates) == len(parent["candidate_orbits"]) == 220
    for fresh, archived in zip(candidates, parent["candidate_orbits"]):
        assert (fresh["raw_x"], fresh["key"], hex(fresh["minimal"])) == (
            archived["raw_x"], archived["orbit_key"], archived["minpoly_hex"])

    remaining = list(candidates)
    selected = []
    current = 1
    for _ in range(6):
        chosen = min(remaining, key=lambda row: (
            binary_product(current, row["minimal"]).bit_count(), row["raw_x"]))
        selected.append(chosen)
        remaining.remove(chosen)
        current = binary_product(current, chosen["minimal"])
    assert [row["raw_x"] for row in selected[:5]] == [
        row["raw_x"] for row in parent["selected"]]
    assert [row["raw_x"] for row in selected] == [
        row["raw_x"] for row in record["selected"]]
    assert hex(current) == record["membership"]["polynomial_hex"]
    assert current.bit_count() == record["membership"]["term_count"]
    assert current.bit_length() - 1 == record["membership"]["degree"] == 438

    base_rows = record["base_points"]
    assert len(base_rows) == 438
    polynomial = sum((t**i for i in range(current.bit_length())
                      if (current >> i) & 1), ring.zero())
    for slot, fresh in enumerate(selected):
        archived = record["selected"][slot]
        raw = curve(field_of(archived["raw_point"][0]),
                    field_of(archived["raw_point"][1]))
        point = curve(field_of(archived["projected_point"][0]),
                      field_of(archived["projected_point"][1]))
        assert h * raw == point
        assert point == fresh["projected"] or point == -fresh["projected"]
        assert r * point == zero
        assert lam * point == curve(point[0]**2, point[1]**2)
        for phase in range(n):
            row = base_rows[slot * n + phase]
            assert (row["orbit"], row["phase"]) == (slot, phase)
            assert [bits_of(point[0]), bits_of(point[1])] == row["point"]
            assert polynomial(point[0]) == 0
            point = curve(point[0]**2, point[1]**2)
        assert [bits_of(point[0]), bits_of(point[1])] == archived["projected_point"]
    assert len({row["point"][0] for row in base_rows}) == 438

    first = candidates[:6]
    assert [row["raw_x"] for row in first] == record["controls"]["first_six_raw_x"]
    assert product(first).bit_count() == record["controls"]["first_six_term_count"]
    for archived in record["controls"]["random_orbit_panels"]:
        rows = random.Random(archived["seed"]).sample(candidates, 6)
        assert sorted(row["raw_x"] for row in rows) == archived["raw_x"]
        assert product(rows).bit_count() == archived["term_count"]
    for m in range(1, 9):
        assert math.comb(876 + m - 1, m) == record["signed_multiset_upper_counts"][str(m)]
    assert record["signed_multiset_upper_counts"]["8"] >= r
    return {"candidate_orbits": len(candidates), "selected_orbits": len(selected),
            "selected_raw_x": [row["raw_x"] for row in selected],
            "base_representatives": len(base_rows),
            "membership_terms": current.bit_count(),
            "first_control_terms": product(first).bit_count(),
            "random_controls": len(record["controls"]["random_orbit_panels"]),
            "group_polynomial_and_count_checks": "PASS"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_bytes, parent_bytes, fixture_bytes = (
        args.base.read_bytes(), args.parent.read_bytes(), args.fixture.read_bytes())
    record, parent = json.loads(base_bytes), json.loads(parent_bytes)
    assert record["parent_base_sha256"] == hashlib.sha256(parent_bytes).hexdigest()
    assert record["fixture_sha256"] == hashlib.sha256(fixture_bytes).hexdigest()
    fixture = next(row for row in json.loads(fixture_bytes)["fixtures"]
                   if (row["a"], row["field_degree"]) == (1, 73))
    result = {"schema": "icperf-koblitz-six-orbit-sage-replay-v1",
              "base_sha256": hashlib.sha256(base_bytes).hexdigest(),
              "parent_base_sha256": hashlib.sha256(parent_bytes).hexdigest(),
              "fixture_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python_version": sys.version,
              "method": "independent Sage candidate scan, greedy step, full-point and control replay",
              "result": replay(record, parent, fixture)}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result["result"], sort_keys=True))


if __name__ == "__main__":
    main()

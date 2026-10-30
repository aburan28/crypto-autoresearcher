"""Target-blind Frobenius-orbit factor-base input screen on a certified Koblitz curve.

This constructs subgroup points and exact membership polynomials. It does not
solve a decomposition system or estimate index-calculus running time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

from sympy.ntheory.residue_ntheory import sqrt_mod

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import icperf_koblitz_subgroup_fixture as ec  # noqa: E402

FIXTURES = ROOT / "research/icperf_koblitz_subgroup_fixtures_20261017/fixtures.json"
RAW_X_MAX = 512
ORBIT_COUNT = 5
CONTROL_SEED = 20261018
CONTROL_COUNT = 32


def binary_polynomial_product(a: int, b: int) -> int:
    """Multiply bit-packed polynomials in F_2[X], with no reduction."""
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def frobenius_point(point: ec.Point, field_polynomial: int) -> ec.Point:
    assert point is not None
    return (ec.square(point[0], field_polynomial),
            ec.square(point[1], field_polynomial))


def point_orbit(point: ec.Point, n: int, field_polynomial: int) -> list[tuple[int, int]]:
    assert point is not None
    orbit: list[tuple[int, int]] = []
    current = point
    for _ in range(n):
        assert current is not None
        orbit.append(current)
        current = frobenius_point(current, field_polynomial)
    assert current == point
    assert len({p[0] for p in orbit}) == n
    return orbit


def minimal_polynomial(x_orbit: list[int], field_polynomial: int) -> int:
    """Return the exact F_2[X] polynomial with the specified conjugate roots."""
    coefficients = [1]
    for root in x_orbit:
        next_coefficients = [0] * (len(coefficients) + 1)
        for exponent, coefficient in enumerate(coefficients):
            next_coefficients[exponent] ^= ec.mul(coefficient, root, field_polynomial)
            next_coefficients[exponent + 1] ^= coefficient
        coefficients = next_coefficients
    assert all(c in (0, 1) for c in coefficients)
    return sum(c << exponent for exponent, c in enumerate(coefficients))


def polynomial_weight(poly: int) -> int:
    return poly.bit_count()


def polynomial_degree(poly: int) -> int:
    return poly.bit_length() - 1


def polynomial_max_binary_exponent_weight(poly: int) -> int:
    return max((exponent.bit_count() for exponent in range(poly.bit_length())
                if (poly >> exponent) & 1), default=0)


def frobenius_scalar(generator: tuple[int, int], r: int, a: int, f: int) -> int:
    # E_1(F_2) has trace +1, so tau^2-tau+2=0 on E[r]. Resolve the two
    # possible roots by full-point multiplication rather than choosing a sign.
    roots = sqrt_mod(-7 % r, r, all_roots=True)
    assert roots and len(roots) == 2
    inverse_two = pow(2, -1, r)
    tau_g = frobenius_point(generator, f)
    matches = [((1 + int(root)) * inverse_two) % r for root in roots
               if ec.scale(((1 + int(root)) * inverse_two) % r, generator, a, f)
               == tau_g]
    assert len(matches) == 1
    lam = matches[0]
    assert (lam * lam - lam + 2) % r == 0
    assert pow(lam, 73, r) == 1
    return lam


def scan(fixture: dict) -> dict:
    a = fixture["a"]
    n = fixture["field_degree"]
    f = fixture["field_polynomial"]
    h = fixture["cofactor"]
    r = fixture["prime_order"]
    assert (a, n, h, r) == (1, 73, 1754, 5384682420498870703)
    candidates: list[dict] = []
    seen_x_orbits: set[int] = set()
    counts = {"raw_x_attempts": 0, "nonliftable": 0,
              "projection_identity": 0, "duplicate_x_orbit": 0}
    for raw_x in range(1, RAW_X_MAX + 1):
        counts["raw_x_attempts"] += 1
        raw_point = ec.lift_x(raw_x, a, n, f)
        if raw_point is None:
            counts["nonliftable"] += 1
            continue
        projected = ec.scale(h, raw_point, a, f)
        if projected is None:
            counts["projection_identity"] += 1
            continue
        orbit = point_orbit(projected, n, f)
        key = min(p[0] for p in orbit)
        if key in seen_x_orbits:
            counts["duplicate_x_orbit"] += 1
            continue
        seen_x_orbits.add(key)
        polynomial = minimal_polynomial([p[0] for p in orbit], f)
        assert polynomial_degree(polynomial) == n
        candidates.append({"raw_x": raw_x, "raw_point": list(raw_point),
                           "projected_point": list(projected),
                           "orbit_key": key, "minpoly_hex": hex(polynomial),
                           "minpoly_weight": polynomial_weight(polynomial),
                           "minpoly": polynomial})
    assert len(candidates) >= ORBIT_COUNT
    counts["distinct_orbits"] = len(candidates)

    selected: list[dict] = []
    remaining = list(candidates)
    product = 1
    for _ in range(ORBIT_COUNT):
        chosen = min(remaining, key=lambda row: (
            polynomial_weight(binary_polynomial_product(product, row["minpoly"])),
            row["raw_x"]))
        selected.append(chosen)
        remaining.remove(chosen)
        product = binary_polynomial_product(product, chosen["minpoly"])
    assert polynomial_degree(product) == ORBIT_COUNT * n

    first = candidates[:ORBIT_COUNT]
    first_product = 1
    for row in first:
        first_product = binary_polynomial_product(first_product, row["minpoly"])
    random_controls = []
    for index in range(CONTROL_COUNT):
        rows = random.Random(CONTROL_SEED + index).sample(candidates, ORBIT_COUNT)
        control_product = 1
        for row in rows:
            control_product = binary_polynomial_product(
                control_product, row["minpoly"])
        random_controls.append({"index": index, "seed": CONTROL_SEED + index,
                                "raw_x": sorted(row["raw_x"] for row in rows),
                                "term_count": polynomial_weight(control_product)})

    generator = tuple(fixture["generator"])
    lam = frobenius_scalar(generator, r, a, f)
    base_points = []
    for orbit_index, row in enumerate(selected):
        seed_point = tuple(row["projected_point"])
        assert ec.on_curve(seed_point, a, f)
        assert ec.scale(r, seed_point, a, f) is None
        assert ec.scale(lam, seed_point, a, f) == frobenius_point(seed_point, f)
        for phase, point in enumerate(point_orbit(seed_point, n, f)):
            base_points.append({"orbit": orbit_index, "phase": phase,
                                "point": list(point)})
    assert len({tuple(row["point"]) for row in base_points}) == ORBIT_COUNT * n
    assert len({row["point"][0] for row in base_points}) == ORBIT_COUNT * n

    def public_candidate(row: dict) -> dict:
        return {key: value for key, value in row.items() if key != "minpoly"}

    return {"schema": "icperf-koblitz-orbit-base-v1",
            "scope": "target-blind input construction and exact algebraic screen only",
            "fixture_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "parameters": {"a": a, "field_degree": n, "field_polynomial": f,
                           "subgroup_order": r, "cofactor": h,
                           "raw_x_min": 1, "raw_x_max": RAW_X_MAX,
                           "selected_orbits": ORBIT_COUNT,
                           "random_control_seed": CONTROL_SEED,
                           "random_control_count": CONTROL_COUNT},
            "counts": counts, "candidate_orbits": [public_candidate(row) for row in candidates],
            "selection_rule": "greedy minimum F2 membership-product term count; ties by raw_x",
            "selected": [public_candidate(row) for row in selected],
            "base_points": base_points, "frobenius_scalar_mod_r": lam,
            "membership": {"polynomial_hex": hex(product),
                           "degree": polynomial_degree(product),
                           "term_count": polynomial_weight(product),
                           "max_binary_exponent_weight":
                               polynomial_max_binary_exponent_weight(product)},
            "controls": {"first_five_raw_x": [row["raw_x"] for row in first],
                         "first_five_term_count": polynomial_weight(first_product),
                         "random_orbit_panels": random_controls},
            "claims_excluded": ["solver degree", "relation yield", "useful rank",
                                "linear algebra", "target recovery", "end-to-end speed"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    fixtures = json.loads(FIXTURES.read_text())["fixtures"]
    fixture = next(row for row in fixtures
                   if (row["a"], row["field_degree"]) == (1, 73))
    started = time.perf_counter()
    result = scan(fixture)
    result["construction_wall_seconds"] = time.perf_counter() - started
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"candidate_orbits": result["counts"]["distinct_orbits"],
                      "selected_terms": result["membership"]["term_count"],
                      "control_min_terms": min(row["term_count"] for row in
                                               result["controls"]["random_orbit_panels"]),
                      "out": str(args.out)}, sort_keys=True))


if __name__ == "__main__":
    main()

"""Extend the archived target-blind Koblitz input screen to six full orbits.

This consumes the complete archived candidate pool, preserves the first five
greedy selections, and makes one predeclared greedy step. It is input
construction only; no decomposition or unknown-scalar solver is called.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import icperf_koblitz_orbit_base as previous  # noqa: E402
import icperf_koblitz_subgroup_fixture as ec  # noqa: E402

PARENT = ROOT / "research/icperf_koblitz_orbit_base_20261018/base.json"
FIXTURES = ROOT / "research/icperf_koblitz_subgroup_fixtures_20261017/fixtures.json"
CONTROL_SEED = 20261050
CONTROL_COUNT = 32
ORBIT_COUNT = 6


def product(rows: list[dict]) -> int:
    value = 1
    for row in rows:
        value = previous.binary_polynomial_product(value, int(row["minpoly_hex"], 16))
    return value


def evaluate(polynomial: int, x: int, field_polynomial: int) -> int:
    value = 0
    for exponent in range(polynomial.bit_length() - 1, -1, -1):
        value = ec.mul(value, x, field_polynomial) ^ ((polynomial >> exponent) & 1)
    return value


def scan(parent: dict, fixture: dict) -> dict:
    assert parent["parameters"]["selected_orbits"] == 5
    assert (fixture["a"], fixture["field_degree"], fixture["prime_order"]) == (
        1, 73, 5384682420498870703)
    candidates = parent["candidate_orbits"]
    assert len(candidates) == parent["counts"]["distinct_orbits"] == 220
    selected = list(parent["selected"])
    assert product(selected) == int(parent["membership"]["polynomial_hex"], 16)
    used = {row["raw_x"] for row in selected}
    parent_polynomial = product(selected)
    remaining = [row for row in candidates if row["raw_x"] not in used]
    sixth = min(remaining, key=lambda row: (
        previous.binary_polynomial_product(
            parent_polynomial, int(row["minpoly_hex"], 16)).bit_count(),
        row["raw_x"]))
    selected.append(sixth)
    membership = product(selected)
    n = fixture["field_degree"]
    assert previous.polynomial_degree(membership) == ORBIT_COUNT * n

    controls = []
    for index in range(CONTROL_COUNT):
        rows = random.Random(CONTROL_SEED + index).sample(candidates, ORBIT_COUNT)
        controls.append({"index": index, "seed": CONTROL_SEED + index,
                         "raw_x": sorted(row["raw_x"] for row in rows),
                         "term_count": product(rows).bit_count()})
    first = candidates[:ORBIT_COUNT]

    a = fixture["a"]
    f = fixture["field_polynomial"]
    r = fixture["prime_order"]
    h = fixture["cofactor"]
    lam = parent["frobenius_scalar_mod_r"]
    points = []
    for orbit_index, row in enumerate(selected):
        raw = tuple(row["raw_point"])
        seed = tuple(row["projected_point"])
        assert ec.on_curve(raw, a, f) and ec.on_curve(seed, a, f)
        assert ec.scale(h, raw, a, f) == seed
        assert ec.scale(r, seed, a, f) is None
        assert ec.scale(lam, seed, a, f) == previous.frobenius_point(seed, f)
        for phase, point in enumerate(previous.point_orbit(seed, n, f)):
            assert evaluate(membership, point[0], f) == 0
            points.append({"orbit": orbit_index, "phase": phase,
                           "point": list(point)})
    assert len(points) == ORBIT_COUNT * n
    assert len({row["point"][0] for row in points}) == len(points)

    signed = 2 * len(points)
    counts = {str(m): math.comb(signed + m - 1, m) for m in range(1, 9)}
    assert counts["8"] >= r
    return {
        "schema": "icperf-koblitz-six-orbit-input-v1",
        "scope": "target-blind algebraic input screen; no solver or ECDLP cost result",
        "parent_base_sha256": hashlib.sha256(PARENT.read_bytes()).hexdigest(),
        "fixture_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "parameters": {"field_degree": n, "subgroup_order": r,
                       "candidate_orbits": len(candidates),
                       "selected_orbits": ORBIT_COUNT,
                       "selection_rule": "retain parent five; greedily minimize F2 product terms for sixth; tie by raw_x",
                       "random_control_seed": CONTROL_SEED,
                       "random_control_count": CONTROL_COUNT},
        "selected": selected,
        "added_raw_x": sixth["raw_x"],
        "base_points": points,
        "membership": {"degree": previous.polynomial_degree(membership),
                       "polynomial_hex": hex(membership),
                       "term_count": membership.bit_count(),
                       "max_binary_exponent_weight":
                           previous.polynomial_max_binary_exponent_weight(membership)},
        "controls": {"first_six_raw_x": [row["raw_x"] for row in first],
                     "first_six_term_count": product(first).bit_count(),
                     "random_orbit_panels": controls},
        "signed_multiset_upper_counts": counts,
        "parent_construction_wall_seconds": parent["construction_wall_seconds"],
        "claims_excluded": ["solver degree", "relation yield", "useful rank",
                            "target coverage", "end-to-end speed"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    parent = json.loads(PARENT.read_text())
    fixture = next(row for row in json.loads(FIXTURES.read_text())["fixtures"]
                   if (row["a"], row["field_degree"]) == (1, 73))
    started = time.perf_counter()
    result = scan(parent, fixture)
    result["incremental_construction_wall_seconds"] = time.perf_counter() - started
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"selected_raw_x": [row["raw_x"] for row in result["selected"]],
                      "terms": result["membership"]["term_count"],
                      "random_min_terms": min(row["term_count"] for row in
                                              result["controls"]["random_orbit_panels"]),
                      "out": str(args.out)}, sort_keys=True))


if __name__ == "__main__":
    main()

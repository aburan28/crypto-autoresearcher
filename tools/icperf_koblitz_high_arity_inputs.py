"""Build planted Koblitz S3 chains and specialized direct S3..S9 root loci.

The direct polynomials fix every base x coordinate and leave only target x
variable. They are correctness inputs, not full multivariate solver systems.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import icperf_koblitz_orbit_six as six  # noqa: E402
import icperf_koblitz_subgroup_fixture as ec  # noqa: E402

BASE = ROOT / "research/icperf_koblitz_orbit_six_20261018/base.json"
FIXTURES = ROOT / "research/icperf_koblitz_subgroup_fixtures_20261017/fixtures.json"
POINT_INDICES = (0, 73, 146, 219, 292, 365, 1, 74)


def negative(point: tuple[int, int]) -> tuple[int, int]:
    return point[0], point[1] ^ point[0]


def semaev3(x: int, y: int, z: int, f: int) -> int:
    e2 = ec.mul(x, y, f) ^ ec.mul(x, z, f) ^ ec.mul(y, z, f)
    return ec.square(e2, f) ^ ec.mul(ec.mul(x, y, f), z, f) ^ 1


def polynomial_from_roots(roots: list[int], f: int) -> list[int]:
    coefficients = [1]
    for root in roots:
        newer = [0] * (len(coefficients) + 1)
        for i, coefficient in enumerate(coefficients):
            newer[i] ^= ec.mul(coefficient, root, f)
            newer[i + 1] ^= coefficient
        coefficients = newer
    return coefficients


def polynomial_at(coefficients: list[int], x: int, f: int) -> int:
    value = 0
    for coefficient in reversed(coefficients):
        value = ec.mul(value, x, f) ^ coefficient
    return value


def signed_roots(points: list[tuple[int, int]], a: int, f: int) -> tuple[list[int], int]:
    values = []
    for mask in range(1 << len(points)):
        total = None
        for index, point in enumerate(points):
            term = negative(point) if (mask >> index) & 1 else point
            total = ec.add(total, term, a, f)
        assert total is not None
        values.append(total[0])
    roots = sorted(set(values))
    assert len(roots) == 1 << (len(points) - 1)
    return roots, len(values)


def scan(base: dict, fixture: dict) -> dict:
    a, f, r = fixture["a"], fixture["field_polynomial"], fixture["prime_order"]
    assert (a, fixture["field_degree"], r) == (1, 73, 5384682420498870703)
    membership = int(base["membership"]["polynomial_hex"], 16)
    points = [tuple(base["base_points"][index]["point"]) for index in POINT_INDICES]
    assert len({point[0] for point in points}) == 8
    assert all(ec.on_curve(point, a, f) and ec.scale(r, point, a, f) is None
               and six.evaluate(membership, point[0], f) == 0 for point in points)
    generator = tuple(fixture["generator"])
    rows = []
    prefixes = []
    total = None
    for point in points:
        total = ec.add(total, point, a, f)
        assert total is not None
        prefixes.append(total)
    for m in range(2, 9):
        selected = points[:m]
        target = prefixes[m - 1]
        triples = []
        for j in range(2, m + 1):
            if j == 2:
                triple = [points[0][0], points[1][0], prefixes[1][0]]
            else:
                triple = [prefixes[j - 2][0], points[j - 1][0], prefixes[j - 1][0]]
            assert semaev3(*triple, f) == 0
            triples.append(triple)
        assert len(triples) == m - 1

        roots, assignments = signed_roots(selected, a, f)
        coefficients = polynomial_from_roots(roots, f)
        assert len(coefficients) - 1 == 1 << (m - 1)
        assert coefficients[-1] == 1
        assert polynomial_at(coefficients, target[0], f) == 0
        if m == 2:
            x, y = selected[0][0], selected[1][0]
            lead = ec.square(x ^ y, f)
            middle = ec.mul(x, y, f)
            constant = ec.square(middle, f) ^ 1
            inv_lead = ec.inv(lead, f)
            assert coefficients == [ec.mul(constant, inv_lead, f),
                                    ec.mul(middle, inv_lead, f), 1]
        negative_control = None
        for k in range(1, 33):
            probe = ec.scale(k, generator, a, f)
            assert probe is not None
            if probe[0] not in roots:
                negative_control = {"scalar": k, "point": list(probe),
                                    "evaluation": polynomial_at(coefficients, probe[0], f)}
                break
        assert negative_control and negative_control["evaluation"] != 0
        rows.append({"m": m, "direct_label": f"S{m + 1}_point_specialized",
                     "chain_label": "chained_S3",
                     "chain_triples": triples,
                     "chain_equations": len(triples),
                     "target": list(target),
                     "signed_assignments": assignments,
                     "distinct_target_x_roots": len(roots),
                     "root_x": roots,
                     "direct_polynomial_coefficients": coefficients,
                     "direct_polynomial_degree": len(coefficients) - 1,
                     "direct_polynomial_nonzero_terms": sum(c != 0 for c in coefficients),
                     "negative_control": negative_control})
    return {"schema": "icperf-koblitz-high-arity-input-v1",
            "scope": "planted S3 and point-specialized S3..S9 correctness inputs; no full multivariate construction or solver trial",
            "base_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
            "fixture_sha256": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "semaev3_formula": "(x1*x2+x1*x3+x2*x3)^2+x1*x2*x3+1 over GF(2^73)",
            "point_indices": list(POINT_INDICES),
            "base_points": [list(point) for point in points],
            "rows": rows,
            "claims_excluded": ["full multivariate S8 or S9 construction", "observed solving degree",
                                "relation yield", "useful rank", "end-to-end speed"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads(BASE.read_text())
    fixture = next(row for row in json.loads(FIXTURES.read_text())["fixtures"]
                   if (row["a"], row["field_degree"]) == (1, 73))
    started = time.perf_counter()
    result = scan(base, fixture)
    result["construction_wall_seconds"] = time.perf_counter() - started
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"rows": len(result["rows"]),
                      "direct_s8_degree": result["rows"][5]["direct_polynomial_degree"],
                      "direct_s9_degree": result["rows"][6]["direct_polynomial_degree"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()

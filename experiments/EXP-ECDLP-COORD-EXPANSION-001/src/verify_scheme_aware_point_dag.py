#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("scheme_aware_point_dag.py")
Point = tuple[int, int] | None
K = tuple[int, int]


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    ).hexdigest()


def point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if value is None else (1, value[0], value[1])


def ec_add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        numerator = (3 * x1 * x1 + a) % p
        denominator = 2 * y1 % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def ec_sum(values: Iterable[Point], p: int, a: int) -> Point:
    result: Point = None
    for value in values:
        result = ec_add(result, value, p, a)
    return result


def scalar_mul(value: Point, scalar: int, p: int, a: int) -> Point:
    result: Point = None
    current = value
    while scalar:
        if scalar & 1:
            result = ec_add(result, current, p, a)
        current = ec_add(current, current, p, a)
        scalar >>= 1
    return result


def insert(
    cycle: dict[Point, list[Any]],
    image: Point,
    route: tuple[int, ...],
) -> None:
    if image not in cycle:
        cycle[image] = [0, route]
    cycle[image][0] += 1


def reconstruct_cycles(
    points: list[Point], p: int, a: int
) -> tuple[dict[str, dict[Point, list[Any]]], int]:
    canonical: dict[Point, list[Any]] = {}
    for route in itertools.combinations_with_replacement(
        range(len(points)), 4
    ):
        insert(
            canonical,
            ec_sum((points[index] for index in route), p, a),
            route,
        )
    ordered: dict[Point, list[Any]] = {}
    for route in itertools.product(range(len(points)), repeat=4):
        insert(
            ordered,
            ec_sum((points[index] for index in route), p, a),
            route,
        )
    d2: dict[Point, tuple[int, int]] = {}
    for route in itertools.combinations_with_replacement(
        range(len(points)), 2
    ):
        image = ec_sum((points[index] for index in route), p, a)
        d2.setdefault(image, route)
    d2_points = sorted(d2, key=point_key)
    unique: dict[Point, list[Any]] = {}
    for left, right in itertools.combinations_with_replacement(
        range(len(d2_points)), 2
    ):
        insert(
            unique,
            ec_add(d2_points[left], d2_points[right], p, a),
            (*d2[d2_points[left]], *d2[d2_points[right]]),
        )
    reduced = {
        image: [1, record[1]] for image, record in canonical.items()
    }
    return {
        "reduced": reduced,
        "canonical": canonical,
        "ordered": ordered,
        "unique_d2_pair": unique,
    }, len(d2)


def payload(cycle: dict[Point, list[Any]]) -> list[dict[str, Any]]:
    return [
        {
            "point": point_json(image),
            "multiplicity": cycle[image][0],
            "first_route": list(cycle[image][1]),
        }
        for image in sorted(cycle, key=point_key)
    ]


def k_add(left: K, right: K, p: int) -> K:
    return (left[0] + right[0]) % p, (left[1] + right[1]) % p


def k_mul(left: K, right: K, p: int, delta: int) -> K:
    return (
        left[0] * right[0] + delta * left[1] * right[1]
    ) % p, (
        left[0] * right[1] + left[1] * right[0]
    ) % p


def polynomial_mul(
    left: list[K], right: list[K], p: int, delta: int
) -> list[K]:
    result = [(0, 0)] * (len(left) + len(right) - 1)
    for i, lvalue in enumerate(left):
        for j, rvalue in enumerate(right):
            result[i + j] = k_add(
                result[i + j],
                k_mul(lvalue, rvalue, p, delta),
                p,
            )
    return result


def characteristic(
    roots: list[K], p: int, delta: int
) -> list[K]:
    level = [
        [((-root[0]) % p, (-root[1]) % p), (1, 0)]
        for root in roots
    ]
    if not level:
        return [(1, 0)]
    while len(level) > 1:
        level = [
            (
                polynomial_mul(
                    level[index], level[index + 1], p, delta
                )
                if index + 1 < len(level)
                else level[index]
            )
            for index in range(0, len(level), 2)
        ]
    return level[0]


def polynomial_eval(
    polynomial: list[K], value: K, p: int, delta: int
) -> K:
    result = (0, 0)
    for coefficient in reversed(polynomial):
        result = k_add(
            k_mul(result, value, p, delta), coefficient, p
        )
    return result


def select_queries(
    support: set[Point],
    generator: Point,
    q: int,
    p: int,
    a: int,
) -> tuple[list[Point], list[Point]]:
    positives = sorted(support, key=point_key)[:16]
    negatives = []
    scalar = 1
    while len(negatives) < min(16, q - len(support)):
        candidate = scalar_mul(generator, scalar, p, a)
        if candidate not in support:
            negatives.append(candidate)
        scalar += 1
    return positives, negatives


def cycle_checks(
    recorded: dict[str, Any],
    cycle: dict[Point, list[Any]],
    points: list[Point],
    generator: Point,
    q: int,
    p: int,
    a: int,
    delta: int,
) -> dict[str, bool]:
    cycle_payload = payload(cycle)
    degree = sum(record[0] for record in cycle.values())
    infinity = cycle.get(None, [0])[0]
    roots = [
        (image[0], image[1])
        for image, record in cycle.items()
        if image is not None
        for _ in range(record[0])
    ]
    polynomial = characteristic(roots, p, delta)
    polynomial_json = [[left, right] for left, right in polynomial]
    histogram = Counter(record[0] for record in cycle.values())
    positives, negatives = select_queries(
        set(cycle), generator, q, p, a
    )
    expected_positive = []
    for image in positives:
        route = cycle[image][1]
        replay = ec_sum((points[index] for index in route), p, a)
        expected_positive.append(
            {
                "point": point_json(image),
                "polynomial_hit": (
                    infinity > 0
                    if image is None
                    else polynomial_eval(
                        polynomial, image, p, delta
                    )
                    == (0, 0)
                ),
                "route": list(route),
                "witness_replay": point_json(replay),
                "witness_valid": replay == image,
            }
        )
    expected_negative = [
        {
            "point": point_json(image),
            "polynomial_hit": polynomial_eval(
                polynomial, image, p, delta
            )
            == (0, 0),
        }
        for image in negatives
    ]
    return {
        "degree": recorded["degree"] == degree,
        "point_support": recorded["point_support"] == len(cycle),
        "x_support": recorded["x_support"]
        == len({image[0] for image in cycle if image is not None}),
        "infinity": recorded["infinity_multiplicity"] == infinity,
        "histogram": recorded["multiplicity_histogram"]
        == {str(key): value for key, value in sorted(histogram.items())},
        "cycle_digest": recorded["cycle_digest"] == digest(cycle_payload),
        "witness_digest": recorded["witness_digest"]
        == digest(
            [
                [item["point"], item["first_route"]]
                for item in cycle_payload
            ]
        ),
        "polynomial": recorded["characteristic_polynomial"]
        == polynomial_json,
        "polynomial_digest": recorded["characteristic_polynomial_digest"]
        == digest(polynomial_json),
        "polynomial_degree": recorded[
            "characteristic_polynomial_degree"
        ]
        == degree - infinity,
        "positive_queries": recorded["positive_checks"]
        == expected_positive,
        "negative_queries": recorded["negative_checks"]
        == expected_negative,
        "recorded_valid": recorded["valid"] is True,
    }


def verify_row(
    recorded: dict[str, Any],
    curve: dict[str, Any],
    family: dict[str, Any],
) -> dict[str, Any]:
    p, q, a = curve["p"], curve["q"], curve["a"]
    points = [
        point(value)
        for value in family["factor_base"]["points"][
            : recorded["b_size"]
        ]
    ]
    cycles, d2_support = reconstruct_cycles(points, p, a)
    checks = {
        name: cycle_checks(
            recorded["cycles"][name],
            cycle,
            points,
            point(curve["generator"]),
            q,
            p,
            a,
            recorded["delta"],
        )
        for name, cycle in cycles.items()
    }
    supports = [set(cycle) for cycle in cycles.values()]
    degree_checks = {
        "reduced": sum(record[0] for record in cycles["reduced"].values())
        == len(cycles["canonical"]),
        "canonical": sum(
            record[0] for record in cycles["canonical"].values()
        )
        == math.comb(recorded["b_size"] + 3, 4),
        "ordered": sum(
            record[0] for record in cycles["ordered"].values()
        )
        == recorded["b_size"] ** 4,
        "unique_d2_pair": sum(
            record[0] for record in cycles["unique_d2_pair"].values()
        )
        == math.comb(d2_support + 1, 2),
    }
    row_checks = {
        "factor_base": recorded["factor_base"]
        == [point_json(value) for value in points],
        "d2_support": recorded["build"]["d2_support"] == d2_support,
        "support_equal": recorded["support_equal"]
        and all(support == supports[0] for support in supports),
        "degree_checks": recorded["degree_checks"] == degree_checks
        and all(degree_checks.values()),
        "oriented_injective": recorded["oriented_encoding_injective"]
        and len(
            {
                image
                for image in cycles["canonical"]
                if image is not None
            }
        )
        == len(
            [
                image
                for image in cycles["canonical"]
                if image is not None
            ]
        ),
        "cycles": all(
            all(cycle.values()) for cycle in checks.values()
        ),
        "recorded_valid": recorded["valid"] is True,
    }
    return {
        "curve_id": recorded["curve_id"],
        "family": recorded["family"],
        "b_size": recorded["b_size"],
        "row_checks": row_checks,
        "cycle_checks": checks,
        "valid": all(row_checks.values()),
    }


def envelope(
    raw: dict[str, Any], typed: dict[str, Any]
) -> dict[str, bool]:
    instance = typed["instances"][raw["config"]["curve_index"]]
    expected = [
        (instance["curve"]["id"], family, b_size)
        for family in raw["config"]["families"]
        for b_size in raw["config"]["b_values"]
    ]
    actual = [
        (row["curve_id"], row["family"], row["b_size"])
        for row in raw["rows"]
    ]
    rows_exact = actual == expected and len(actual) == len(set(actual))
    summary = raw["summary"]
    return {
        "expected_rows_exact": rows_exact,
        "summary_exact": rows_exact
        and summary["cells"] == len(raw["rows"])
        and summary["all_cells_valid"]
        == all(row["valid"] for row in raw["rows"])
        and summary["all_supports_equal"]
        == all(row["support_equal"] for row in raw["rows"])
        and summary["all_degrees_valid"]
        == all(
            all(row["degree_checks"].values()) for row in raw["rows"]
        )
        and summary["all_witnesses_valid"]
        == all(
            all(
                all(
                    check["witness_valid"]
                    for check in cycle["positive_checks"]
                )
                for cycle in row["cycles"].values()
            )
            for row in raw["rows"]
        ),
    }


def mutation_suite(
    raw: dict[str, Any], typed: dict[str, Any]
) -> dict[str, bool]:
    candidates: dict[str, dict[str, Any]] = {}
    dropped = copy.deepcopy(raw)
    dropped["rows"].pop()
    candidates["dropped_row"] = dropped
    duplicate = copy.deepcopy(raw)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    candidates["duplicate_row"] = duplicate
    total = copy.deepcopy(raw)
    total["summary"]["cells"] += 1
    candidates["summary"] = total
    validity = copy.deepcopy(raw)
    validity["rows"][0]["valid"] = False
    candidates["row_validity"] = validity
    return {
        name: not all(envelope(candidate, typed).values())
        for name, candidate in candidates.items()
    }


def verify(
    raw_path: Path, typed_override: Path | None
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    instance = typed["instances"][raw["config"]["curve_index"]]
    by_family = {
        family["family"]: family for family in instance["families"]
    }
    receipts = [
        verify_row(row, instance["curve"], by_family[row["family"]])
        for row in raw["rows"]
    ]
    top = {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "scheme-aware-point-dag-v1"
        ),
        "producer_hash": raw["source"]["generator_sha256"]
        == file_hash(PRODUCER_PATH),
        "input_hash": raw["source"]["typed_input_sha256"]
        == file_hash(typed_path),
        **envelope(raw, typed),
        "all_rows_reconstructed": all(
            receipt["valid"] for receipt in receipts
        ),
        "resultant_gate_false": raw["summary"][
            "resultant_constructed"
        ]
        is False,
        "compression_gate_false": raw["summary"]["compression_gate"]
        is False,
        "promotion_gate_false": raw["summary"][
            "algorithm_promotion_gate"
        ]
        is False,
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    mutations = mutation_suite(raw, typed)
    valid = all(top.values()) and all(mutations.values())
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "scheme-aware-point-dag-v1-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "producer_sha256": file_hash(PRODUCER_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "top_checks": top,
        "mutation_rejections": mutations,
        "row_receipts": receipts,
        "valid": valid,
        "boundary": (
            "Independent explicit point-cycle and Fp2 polynomial replay. "
            "No resultant or compression is certified."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--typed-input", type=Path)
    args = parser.parse_args()
    result = verify(args.raw_result, args.typed_input)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

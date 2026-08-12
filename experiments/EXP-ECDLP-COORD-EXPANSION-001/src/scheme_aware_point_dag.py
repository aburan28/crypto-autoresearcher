#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import resource
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None
Fp2 = tuple[int, int]


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


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def decode_point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def encode_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if point is None else (1, point[0], point[1])


@dataclass
class CurveCounter:
    additions: int = 0
    doublings: int = 0
    inversions: int = 0
    identity_returns: int = 0
    inverse_returns: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "additions": self.additions,
            "doublings": self.doublings,
            "inversions": self.inversions,
            "identity_returns": self.identity_returns,
            "inverse_returns": self.inverse_returns,
        }


def add(
    left: Point,
    right: Point,
    p: int,
    a: int,
    counter: CurveCounter | None = None,
) -> Point:
    if counter is not None:
        counter.additions += 1
    if left is None:
        if counter is not None:
            counter.identity_returns += 1
        return right
    if right is None:
        if counter is not None:
            counter.identity_returns += 1
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        if counter is not None:
            counter.inverse_returns += 1
        return None
    if counter is not None:
        counter.inversions += 1
        counter.doublings += int(left == right)
    numerator = (
        3 * x1 * x1 + a if left == right else y2 - y1
    ) % p
    denominator = (
        2 * y1 if left == right else x2 - x1
    ) % p
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def sum_points(
    points: Iterable[Point],
    p: int,
    a: int,
    counter: CurveCounter | None = None,
) -> Point:
    result: Point = None
    for point in points:
        result = add(result, point, p, a, counter)
    return result


def scalar_mul(point: Point, scalar: int, p: int, a: int) -> Point:
    result: Point = None
    addend = point
    value = scalar
    while value:
        if value & 1:
            result = add(result, addend, p, a)
        addend = add(addend, addend, p, a)
        value >>= 1
    return result


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise AssertionError("no nonsquare")


@dataclass
class Fp2Counter:
    additions: int = 0
    multiplications: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "additions": self.additions,
            "multiplications": self.multiplications,
        }


def k_add(
    left: Fp2, right: Fp2, p: int, counter: Fp2Counter | None = None
) -> Fp2:
    if counter is not None:
        counter.additions += 1
    return (left[0] + right[0]) % p, (left[1] + right[1]) % p


def k_mul(
    left: Fp2,
    right: Fp2,
    p: int,
    delta: int,
    counter: Fp2Counter | None = None,
) -> Fp2:
    if counter is not None:
        counter.multiplications += 1
    return (
        left[0] * right[0] + delta * left[1] * right[1]
    ) % p, (
        left[0] * right[1] + left[1] * right[0]
    ) % p


def poly_mul(
    left: list[Fp2],
    right: list[Fp2],
    p: int,
    delta: int,
    counter: Fp2Counter,
) -> list[Fp2]:
    result = [(0, 0)] * (len(left) + len(right) - 1)
    for i, lvalue in enumerate(left):
        for j, rvalue in enumerate(right):
            result[i + j] = k_add(
                result[i + j],
                k_mul(lvalue, rvalue, p, delta, counter),
                p,
                counter,
            )
    return result


def product_tree(
    roots: list[Fp2], p: int, delta: int
) -> tuple[list[Fp2], dict[str, Any]]:
    counter = Fp2Counter()
    level = [
        [((-root[0]) % p, (-root[1]) % p), (1, 0)]
        for root in roots
    ]
    nodes = len(level)
    peak_live = sum(len(poly) for poly in level)
    if not level:
        return [(1, 0)], {
            "nodes": 0,
            "levels": 0,
            "peak_live_coefficients": 1,
            "operations": counter.as_dict(),
        }
    levels = 1
    while len(level) > 1:
        next_level = []
        for index in range(0, len(level), 2):
            if index + 1 == len(level):
                next_level.append(level[index])
            else:
                next_level.append(
                    poly_mul(
                        level[index],
                        level[index + 1],
                        p,
                        delta,
                        counter,
                    )
                )
                nodes += 1
        peak_live = max(
            peak_live,
            sum(len(poly) for poly in level)
            + sum(len(poly) for poly in next_level),
        )
        level = next_level
        levels += 1
    return level[0], {
        "nodes": nodes,
        "levels": levels,
        "peak_live_coefficients": peak_live,
        "operations": counter.as_dict(),
    }


def poly_eval(
    polynomial: list[Fp2],
    value: Fp2,
    p: int,
    delta: int,
    counter: Fp2Counter,
) -> Fp2:
    result = (0, 0)
    for coefficient in reversed(polynomial):
        result = k_add(
            k_mul(result, value, p, delta, counter),
            coefficient,
            p,
            counter,
        )
    return result


def encode_oriented(point: Point) -> Fp2 | None:
    return None if point is None else (point[0], point[1])


def store_route(
    cycle: dict[Point, dict[str, Any]],
    point: Point,
    route: tuple[int, ...],
    multiplicity: int = 1,
) -> None:
    if point not in cycle:
        cycle[point] = {
            "multiplicity": 0,
            "first_route": route,
        }
    cycle[point]["multiplicity"] += multiplicity


def build_cycles(
    points: list[Point], p: int, a: int
) -> tuple[dict[str, dict[Point, dict[str, Any]]], dict[str, Any]]:
    counters = {
        "canonical": CurveCounter(),
        "ordered": CurveCounter(),
        "unique_d2_pair": CurveCounter(),
    }
    canonical: dict[Point, dict[str, Any]] = {}
    for route in itertools.combinations_with_replacement(
        range(len(points)), 4
    ):
        image = sum_points(
            (points[index] for index in route),
            p,
            a,
            counters["canonical"],
        )
        store_route(canonical, image, route)

    ordered: dict[Point, dict[str, Any]] = {}
    for route in itertools.product(range(len(points)), repeat=4):
        image = sum_points(
            (points[index] for index in route),
            p,
            a,
            counters["ordered"],
        )
        store_route(ordered, image, route)

    d2: dict[Point, tuple[int, int]] = {}
    d2_counter = counters["unique_d2_pair"]
    for route in itertools.combinations_with_replacement(
        range(len(points)), 2
    ):
        image = sum_points(
            (points[index] for index in route), p, a, d2_counter
        )
        d2.setdefault(image, route)
    unique_d2_pair: dict[Point, dict[str, Any]] = {}
    d2_points = sorted(d2, key=point_sort_key)
    for left_index, right_index in itertools.combinations_with_replacement(
        range(len(d2_points)), 2
    ):
        left = d2_points[left_index]
        right = d2_points[right_index]
        image = add(left, right, p, a, d2_counter)
        route = (*d2[left], *d2[right])
        store_route(unique_d2_pair, image, route)

    reduced = {
        point: {
            "multiplicity": 1,
            "first_route": record["first_route"],
        }
        for point, record in canonical.items()
    }
    return {
        "reduced": reduced,
        "canonical": canonical,
        "ordered": ordered,
        "unique_d2_pair": unique_d2_pair,
    }, {
        "curve_operations": {
            name: counter.as_dict() for name, counter in counters.items()
        },
        "d2_support": len(d2),
    }


def cycle_payload(cycle: dict[Point, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "point": encode_point(point),
            "multiplicity": cycle[point]["multiplicity"],
            "first_route": list(cycle[point]["first_route"]),
        }
        for point in sorted(cycle, key=point_sort_key)
    ]


def select_queries(
    support: set[Point],
    generator: Point,
    q: int,
    p: int,
    a: int,
    limit: int = 16,
) -> tuple[list[Point], list[Point]]:
    positives = sorted(support, key=point_sort_key)[:limit]
    negatives = []
    scalar = 1
    while len(negatives) < min(limit, q - len(support)):
        point = scalar_mul(generator, scalar, p, a)
        if point not in support:
            negatives.append(point)
        scalar += 1
    return positives, negatives


def cycle_record(
    name: str,
    cycle: dict[Point, dict[str, Any]],
    points: list[Point],
    generator: Point,
    q: int,
    p: int,
    a: int,
    delta: int,
) -> dict[str, Any]:
    payload = cycle_payload(cycle)
    infinity_multiplicity = (
        cycle.get(None, {}).get("multiplicity", 0)
    )
    finite_roots = [
        encode_oriented(point)
        for point, record in cycle.items()
        for _ in range(record["multiplicity"])
        if point is not None
    ]
    assert all(root is not None for root in finite_roots)
    polynomial, dag = product_tree(
        [root for root in finite_roots if root is not None], p, delta
    )
    positives, negatives = select_queries(
        set(cycle), generator, q, p, a
    )
    query_counter = Fp2Counter()
    positive_checks = []
    witness_counter = CurveCounter()
    for point in positives:
        if point is None:
            polynomial_hit = infinity_multiplicity > 0
        else:
            polynomial_hit = (
                poly_eval(
                    polynomial,
                    encode_oriented(point),
                    p,
                    delta,
                    query_counter,
                )
                == (0, 0)
            )
        route = cycle[point]["first_route"]
        replay = sum_points(
            (points[index] for index in route),
            p,
            a,
            witness_counter,
        )
        positive_checks.append(
            {
                "point": encode_point(point),
                "polynomial_hit": polynomial_hit,
                "route": list(route),
                "witness_replay": encode_point(replay),
                "witness_valid": replay == point,
            }
        )
    negative_checks = []
    for point in negatives:
        negative_checks.append(
            {
                "point": encode_point(point),
                "polynomial_hit": (
                    poly_eval(
                        polynomial,
                        encode_oriented(point),
                        p,
                        delta,
                        query_counter,
                    )
                    == (0, 0)
                ),
            }
        )
    histogram = Counter(
        record["multiplicity"] for record in cycle.values()
    )
    degree = sum(record["multiplicity"] for record in cycle.values())
    polynomial_json = [[left, right] for left, right in polynomial]
    return {
        "type": name,
        "degree": degree,
        "point_support": len(cycle),
        "x_support": len(
            {point[0] for point in cycle if point is not None}
        ),
        "infinity_multiplicity": infinity_multiplicity,
        "multiplicity_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "cycle_digest": digest(payload),
        "witness_digest": digest(
            [
                [item["point"], item["first_route"]]
                for item in payload
            ]
        ),
        "characteristic_polynomial_degree": len(polynomial) - 1,
        "characteristic_polynomial_digest": digest(polynomial_json),
        "characteristic_polynomial": polynomial_json,
        "dag": dag,
        "serialized_polynomial_field_elements": 2 * len(polynomial),
        "positive_checks": positive_checks,
        "negative_checks": negative_checks,
        "query_operations": query_counter.as_dict(),
        "witness_replay_operations": witness_counter.as_dict(),
        "valid": (
            len(polynomial) - 1 == degree - infinity_multiplicity
            and all(
                check["polynomial_hit"] and check["witness_valid"]
                for check in positive_checks
            )
            and not any(
                check["polynomial_hit"] for check in negative_checks
            )
        ),
    }


def run_cell(
    curve: dict[str, Any],
    family: dict[str, Any],
    b_size: int,
) -> dict[str, Any]:
    p, q, a = curve["p"], curve["q"], curve["a"]
    generator = decode_point(curve["generator"])
    points = [
        decode_point(value)
        for value in family["factor_base"]["points"][:b_size]
    ]
    delta = nonsquare(p)
    cycles, build = build_cycles(points, p, a)
    records = {
        name: cycle_record(
            name,
            cycle,
            points,
            generator,
            q,
            p,
            a,
            delta,
        )
        for name, cycle in cycles.items()
    }
    supports = {
        name: set(cycle) for name, cycle in cycles.items()
    }
    support_equal = all(
        support == supports["canonical"]
        for support in supports.values()
    )
    degree_checks = {
        "reduced": records["reduced"]["degree"]
        == records["canonical"]["point_support"],
        "canonical": records["canonical"]["degree"]
        == math.comb(b_size + 3, 4),
        "ordered": records["ordered"]["degree"] == b_size**4,
        "unique_d2_pair": records["unique_d2_pair"]["degree"]
        == math.comb(build["d2_support"] + 1, 2),
    }
    finite_encodings = [
        encode_oriented(point)
        for point in supports["canonical"]
        if point is not None
    ]
    valid = (
        support_equal
        and all(degree_checks.values())
        and len(finite_encodings) == len(set(finite_encodings))
        and all(record["valid"] for record in records.values())
    )
    return {
        "curve_id": curve["id"],
        "p": p,
        "q": q,
        "family": family["family"],
        "b_size": b_size,
        "delta": delta,
        "factor_base": [encode_point(point) for point in points],
        "support_equal": support_equal,
        "oriented_encoding_injective": (
            len(finite_encodings) == len(set(finite_encodings))
        ),
        "degree_checks": degree_checks,
        "build": build,
        "cycles": records,
        "baselines": {
            "sqrt_q": math.sqrt(q),
            "balanced_bsgs_records": math.ceil(math.sqrt(q)),
            "canonical_routes": math.comb(b_size + 3, 4),
            "ordered_routes": b_size**4,
            "direct_mitm_pairs": b_size**2,
        },
        "valid": valid,
        "peak_rss_bytes_after_cell": rss_bytes(),
    }


def run(
    typed_path: Path,
    families: list[str],
    b_values: list[int],
) -> dict[str, Any]:
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    instance = typed["instances"][0]
    by_family = {
        family["family"]: family for family in instance["families"]
    }
    started = time.perf_counter()
    rows = []
    for family in families:
        for b_size in b_values:
            row = run_cell(
                instance["curve"], by_family[family], b_size
            )
            rows.append(row)
            print(
                f"built {family} B={b_size}", file=sys.stderr, flush=True
            )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "scheme-aware-point-dag-v1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "generator_sha256": file_hash(SCRIPT_PATH),
            "typed_input_sha256": file_hash(typed_path),
        },
        "config": {
            "typed_input": str(typed_path.resolve()),
            "families": families,
            "b_values": b_values,
            "curve_index": 0,
        },
        "rows": rows,
        "summary": {
            "cells": len(rows),
            "all_cells_valid": all(row["valid"] for row in rows),
            "all_supports_equal": all(
                row["support_equal"] for row in rows
            ),
            "all_degrees_valid": all(
                all(row["degree_checks"].values()) for row in rows
            ),
            "all_witnesses_valid": all(
                all(
                    all(
                        check["witness_valid"]
                        for check in cycle["positive_checks"]
                    )
                    for cycle in row["cycles"].values()
                )
                for row in rows
            ),
            "resultant_constructed": False,
            "compression_gate": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("typed_result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--b-values", nargs="+", type=int, required=True)
    args = parser.parse_args()
    result = run(args.typed_result, args.families, args.b_values)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["summary"]["all_cells_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

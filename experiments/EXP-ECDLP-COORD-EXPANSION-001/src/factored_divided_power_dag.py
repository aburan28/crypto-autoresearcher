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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
Point = tuple[int, int] | None


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


def point_json(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if value is None else (1, value[0], value[1])


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


def negate(value: Point, p: int) -> Point:
    return None if value is None else (value[0], (-value[1]) % p)


def subtract(
    left: Point,
    right: Point,
    p: int,
    a: int,
    counter: CurveCounter | None = None,
) -> Point:
    return add(left, negate(right, p), p, a, counter)


def sum_points(
    values: Iterable[Point],
    p: int,
    a: int,
    counter: CurveCounter | None = None,
) -> Point:
    result: Point = None
    for value in values:
        result = add(result, value, p, a, counter)
    return result


def scalar_mul(value: Point, scalar: int, p: int, a: int) -> Point:
    return sum_points((value for _ in range(scalar)), p, a)


@dataclass
class CycleRecord:
    multiplicity: int
    first_route: tuple[int, ...]


Cycle = dict[Point, CycleRecord]


@dataclass
class BuildCounter:
    pair_attempts: int = 0
    hash_lookups: int = 0
    record_writes: int = 0
    curve: CurveCounter = field(default_factory=CurveCounter)

    def as_dict(self) -> dict[str, Any]:
        return {
            "pair_attempts": self.pair_attempts,
            "hash_lookups": self.hash_lookups,
            "record_writes": self.record_writes,
            "curve": self.curve.as_dict(),
        }


@dataclass
class Node:
    node_id: str
    start: int
    stop: int
    left: Node | None
    right: Node | None
    cycles: dict[int, Cycle]


def insert(
    cycle: Cycle,
    image: Point,
    multiplicity: int,
    route: tuple[int, ...],
    counter: BuildCounter,
) -> None:
    counter.hash_lookups += 1
    if image not in cycle:
        cycle[image] = CycleRecord(0, route)
        counter.record_writes += 1
    cycle[image].multiplicity += multiplicity


def leaf_node(
    index: int,
    value: Point,
    p: int,
    a: int,
) -> Node:
    cycles = {}
    for degree in range(5):
        image = scalar_mul(value, degree, p, a)
        cycles[degree] = {
            image: CycleRecord(
                multiplicity=1,
                first_route=(index,) * degree,
            )
        }
    return Node(
        node_id=f"L{index}",
        start=index,
        stop=index + 1,
        left=None,
        right=None,
        cycles=cycles,
    )


def combine_nodes(
    left: Node,
    right: Node,
    p: int,
    a: int,
    counter: BuildCounter,
) -> Node:
    cycles: dict[int, Cycle] = {}
    for degree in range(5):
        cycle: Cycle = {}
        for left_degree in range(degree + 1):
            right_degree = degree - left_degree
            for left_point, left_record in left.cycles[
                left_degree
            ].items():
                for right_point, right_record in right.cycles[
                    right_degree
                ].items():
                    counter.pair_attempts += 1
                    image = add(
                        left_point,
                        right_point,
                        p,
                        a,
                        counter.curve,
                    )
                    insert(
                        cycle,
                        image,
                        left_record.multiplicity
                        * right_record.multiplicity,
                        (
                            *left_record.first_route,
                            *right_record.first_route,
                        ),
                        counter,
                    )
        cycles[degree] = cycle
    return Node(
        node_id=f"N{left.start}-{right.stop}",
        start=left.start,
        stop=right.stop,
        left=left,
        right=right,
        cycles=cycles,
    )


def build_tree(
    points: list[Point],
    start: int,
    stop: int,
    p: int,
    a: int,
    counter: BuildCounter,
) -> Node:
    if stop - start == 1:
        return leaf_node(start, points[start], p, a)
    middle = (start + stop) // 2
    return combine_nodes(
        build_tree(points, start, middle, p, a, counter),
        build_tree(points, middle, stop, p, a, counter),
        p,
        a,
        counter,
    )


def all_nodes(root: Node) -> list[Node]:
    result = [root]
    if root.left is not None:
        result.extend(all_nodes(root.left))
    if root.right is not None:
        result.extend(all_nodes(root.right))
    return result


def cycle_payload(cycle: Cycle) -> list[dict[str, Any]]:
    return [
        {
            "point": point_json(image),
            "multiplicity": cycle[image].multiplicity,
            "first_route": list(cycle[image].first_route),
        }
        for image in sorted(cycle, key=point_key)
    ]


def coefficient_payload(cycle: Cycle) -> list[list[Any]]:
    return [
        [point_json(image), cycle[image].multiplicity]
        for image in sorted(cycle, key=point_key)
    ]


def direct_canonical(
    points: list[Point], p: int, a: int
) -> Cycle:
    cycle: Cycle = {}
    counter = BuildCounter()
    for route in itertools.combinations_with_replacement(
        range(len(points)), 4
    ):
        image = sum_points(
            (points[index] for index in route), p, a
        )
        insert(cycle, image, 1, route, counter)
    return cycle


@dataclass
class QueryCounter:
    split_attempts: int = 0
    point_scans: int = 0
    hash_lookups: int = 0
    recursion_nodes: int = 0
    curve: CurveCounter = field(default_factory=CurveCounter)

    def as_dict(self) -> dict[str, Any]:
        return {
            "split_attempts": self.split_attempts,
            "point_scans": self.point_scans,
            "hash_lookups": self.hash_lookups,
            "recursion_nodes": self.recursion_nodes,
            "curve": self.curve.as_dict(),
        }


def query(
    node: Node,
    degree: int,
    target: Point,
    p: int,
    a: int,
    counter: QueryCounter,
) -> tuple[int, ...] | None:
    counter.recursion_nodes += 1
    counter.hash_lookups += 1
    if target not in node.cycles[degree]:
        return None
    if node.left is None or node.right is None:
        return node.cycles[degree][target].first_route
    for left_degree in range(degree + 1):
        counter.split_attempts += 1
        right_degree = degree - left_degree
        left_cycle = node.left.cycles[left_degree]
        right_cycle = node.right.cycles[right_degree]
        scan_left = len(left_cycle) <= len(right_cycle)
        scan_cycle = left_cycle if scan_left else right_cycle
        for scanned_point in sorted(scan_cycle, key=point_key):
            counter.point_scans += 1
            complement = subtract(
                target,
                scanned_point,
                p,
                a,
                counter.curve,
            )
            counter.hash_lookups += 1
            other_cycle = right_cycle if scan_left else left_cycle
            if complement not in other_cycle:
                continue
            left_point = scanned_point if scan_left else complement
            right_point = complement if scan_left else scanned_point
            left_route = query(
                node.left,
                left_degree,
                left_point,
                p,
                a,
                counter,
            )
            if left_route is None:
                continue
            right_route = query(
                node.right,
                right_degree,
                right_point,
                p,
                a,
                counter,
            )
            if right_route is not None:
                return (*left_route, *right_route)
    return None


def select_queries(
    root_cycle: Cycle,
    generator: Point,
    q: int,
    p: int,
    a: int,
) -> tuple[list[Point], list[Point]]:
    positives = sorted(root_cycle, key=point_key)[:16]
    negatives = []
    scalar = 1
    while len(negatives) < min(16, q - len(root_cycle)):
        candidate = scalar_mul(generator, scalar, p, a)
        if candidate not in root_cycle:
            negatives.append(candidate)
        scalar += 1
    return positives, negatives


def node_receipt(node: Node) -> dict[str, Any]:
    degrees = {}
    for degree, cycle in node.cycles.items():
        degrees[str(degree)] = {
            "route_degree": sum(
                record.multiplicity for record in cycle.values()
            ),
            "support": len(cycle),
            "infinity_multiplicity": (
                cycle.get(None, CycleRecord(0, ())).multiplicity
            ),
            "cycle_digest": digest(cycle_payload(cycle)),
        }
    return {
        "node_id": node.node_id,
        "start": node.start,
        "stop": node.stop,
        "left": None if node.left is None else node.left.node_id,
        "right": None if node.right is None else node.right.node_id,
        "degrees": degrees,
    }


def run_cell(
    curve: dict[str, Any],
    family: dict[str, Any],
    b_size: int,
) -> dict[str, Any]:
    p, q, a = curve["p"], curve["q"], curve["a"]
    points = [
        decode_point(value)
        for value in family["factor_base"]["points"][:b_size]
    ]
    build_counter = BuildCounter()
    root = build_tree(points, 0, len(points), p, a, build_counter)
    nodes = all_nodes(root)
    root_cycle = root.cycles[4]
    oracle = direct_canonical(points, p, a)
    oracle_match = (
        coefficient_payload(root_cycle) == coefficient_payload(oracle)
    )
    retained_records = sum(
        len(cycle) for node in nodes for cycle in node.cycles.values()
    )
    retained_point_field_elements = sum(
        2
        for node in nodes
        for cycle in node.cycles.values()
        for image in cycle
        if image is not None
    )
    retained_route_indices = sum(
        len(record.first_route)
        for node in nodes
        for cycle in node.cycles.values()
        for record in cycle.values()
    )
    positives, negatives = select_queries(
        root_cycle,
        decode_point(curve["generator"]),
        q,
        p,
        a,
    )
    positive_receipts = []
    worst_scans = 0
    for target in positives:
        counter = QueryCounter()
        route = query(root, 4, target, p, a, counter)
        replay = (
            None
            if route is None
            else sum_points(
                (points[index] for index in route), p, a
            )
        )
        worst_scans = max(worst_scans, counter.point_scans)
        positive_receipts.append(
            {
                "target": point_json(target),
                "route": None if route is None else list(route),
                "replay": point_json(replay),
                "valid": route is not None
                and tuple(sorted(route)) == route
                and replay == target,
                "operations": counter.as_dict(),
            }
        )
    negative_receipts = []
    for target in negatives:
        counter = QueryCounter()
        route = query(root, 4, target, p, a, counter)
        worst_scans = max(worst_scans, counter.point_scans)
        negative_receipts.append(
            {
                "target": point_json(target),
                "route": None if route is None else list(route),
                "valid": route is None,
                "operations": counter.as_dict(),
            }
        )
    finite_degree = sum(
        record.multiplicity
        for image, record in root_cycle.items()
        if image is not None
    )
    expanded_oriented_field_elements = 2 * (finite_degree + 1)
    sqrt_q = math.sqrt(q)
    signal_gate = (
        retained_records < expanded_oriented_field_elements
        and worst_scans < sqrt_q
    )
    valid = (
        oracle_match
        and all(receipt["valid"] for receipt in positive_receipts)
        and all(receipt["valid"] for receipt in negative_receipts)
    )
    return {
        "curve_id": curve["id"],
        "p": p,
        "q": q,
        "family": family["family"],
        "b_size": b_size,
        "factor_base": [point_json(value) for value in points],
        "nodes": [node_receipt(node) for node in nodes],
        "node_count": len(nodes),
        "edge_count": 2 * (len(points) - 1),
        "root_cycle": cycle_payload(root_cycle),
        "root_cycle_digest": digest(cycle_payload(root_cycle)),
        "root_coefficient_digest": digest(
            coefficient_payload(root_cycle)
        ),
        "oracle_coefficient_digest": digest(
            coefficient_payload(oracle)
        ),
        "oracle_match": oracle_match,
        "retained_records": retained_records,
        "retained_point_field_elements": retained_point_field_elements,
        "retained_route_indices": retained_route_indices,
        "logical_words": (
            retained_point_field_elements
            + retained_records
            + retained_route_indices
        ),
        "build_operations": build_counter.as_dict(),
        "positive_queries": positive_receipts,
        "negative_queries": negative_receipts,
        "worst_online_point_scans": worst_scans,
        "expanded_oriented_field_elements": (
            expanded_oriented_field_elements
        ),
        "sqrt_q": sqrt_q,
        "membership_tradeoff_diagnostic": (
            retained_records * worst_scans * worst_scans / q
        ),
        "signal_gate": signal_gate,
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
                f"built {family} B={b_size}",
                file=sys.stderr,
                flush=True,
            )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "factored-divided-power-dag-v1"
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
            "all_oracles_match": all(
                row["oracle_match"] for row in rows
            ),
            "signal_cells": sum(row["signal_gate"] for row in rows),
            "all_positive_queries_valid": all(
                all(query["valid"] for query in row["positive_queries"])
                for row in rows
            ),
            "all_negative_queries_valid": all(
                all(query["valid"] for query in row["negative_queries"])
                for row in rows
            ),
            "relation_rank_tested": False,
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

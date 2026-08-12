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


def canonical_json_bytes(value: Any) -> int:
    return len(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    )


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

    def absorb(self, other: CurveCounter) -> None:
        self.additions += other.additions
        self.doublings += other.doublings
        self.inversions += other.inversions
        self.identity_returns += other.identity_returns
        self.inverse_returns += other.inverse_returns


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


def scalar_mul(
    value: Point,
    scalar: int,
    p: int,
    a: int,
    counter: CurveCounter | None = None,
) -> Point:
    return sum_points(
        (value for _ in range(scalar)), p, a, counter
    )


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
    leaf_scalar_steps: int = 0
    leaf_record_writes: int = 0
    curve: CurveCounter = field(default_factory=CurveCounter)

    def as_dict(self) -> dict[str, Any]:
        return {
            "pair_attempts": self.pair_attempts,
            "hash_lookups": self.hash_lookups,
            "record_writes": self.record_writes,
            "leaf_scalar_steps": self.leaf_scalar_steps,
            "leaf_record_writes": self.leaf_record_writes,
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
    counter: BuildCounter,
) -> Node:
    cycles = {}
    for degree in range(5):
        image = scalar_mul(
            value, degree, p, a, counter.curve
        )
        counter.leaf_scalar_steps += degree
        counter.leaf_record_writes += 1
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
        return leaf_node(start, points[start], p, a, counter)
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


def direct_degree(
    points: list[Point], degree: int, p: int, a: int
) -> Cycle:
    cycle: Cycle = {}
    counter = BuildCounter()
    for route in itertools.combinations_with_replacement(
        range(len(points)), degree
    ):
        image = sum_points(
            (points[index] for index in route), p, a
        )
        insert(cycle, image, 1, route, counter)
    return cycle


def direct_canonical(
    points: list[Point], p: int, a: int
) -> Cycle:
    return direct_degree(points, 4, p, a)


def reduced_cycle(cycle: Cycle) -> Cycle:
    return {
        image: CycleRecord(1, record.first_route)
        for image, record in cycle.items()
    }


def cycle_state(cycle: Cycle) -> dict[str, int]:
    point_fields = 2 * sum(image is not None for image in cycle)
    route_indices = sum(
        len(record.first_route) for record in cycle.values()
    )
    return {
        "records": len(cycle),
        "point_field_elements": point_fields,
        "route_indices": route_indices,
        "logical_words": len(cycle) + point_fields + route_indices,
        "canonical_json_bytes": canonical_json_bytes(
            cycle_payload(cycle)
        ),
    }


@dataclass
class QueryCounter:
    split_attempts: int = 0
    point_scans: int = 0
    hash_lookups: int = 0
    recursion_nodes: int = 0
    sort_calls: int = 0
    sort_items: int = 0
    route_indices_copied: int = 0
    curve: CurveCounter = field(default_factory=CurveCounter)

    def as_dict(self) -> dict[str, Any]:
        return {
            "split_attempts": self.split_attempts,
            "point_scans": self.point_scans,
            "hash_lookups": self.hash_lookups,
            "recursion_nodes": self.recursion_nodes,
            "sort_calls": self.sort_calls,
            "sort_items": self.sort_items,
            "route_indices_copied": self.route_indices_copied,
            "curve": self.curve.as_dict(),
        }

    def absorb(self, other: QueryCounter) -> None:
        self.split_attempts += other.split_attempts
        self.point_scans += other.point_scans
        self.hash_lookups += other.hash_lookups
        self.recursion_nodes += other.recursion_nodes
        self.sort_calls += other.sort_calls
        self.sort_items += other.sort_items
        self.route_indices_copied += other.route_indices_copied
        self.curve.absorb(other.curve)


def query(
    node: Node,
    degree: int,
    target: Point,
    p: int,
    a: int,
    counter: QueryCounter,
    membership_prefilter: bool = True,
) -> tuple[int, ...] | None:
    counter.recursion_nodes += 1
    if membership_prefilter:
        counter.hash_lookups += 1
        if target not in node.cycles[degree]:
            return None
    if node.left is None or node.right is None:
        if not membership_prefilter:
            return None
        return node.cycles[degree][target].first_route
    for left_degree in range(degree + 1):
        counter.split_attempts += 1
        right_degree = degree - left_degree
        left_cycle = node.left.cycles[left_degree]
        right_cycle = node.right.cycles[right_degree]
        scan_left = len(left_cycle) <= len(right_cycle)
        scan_cycle = left_cycle if scan_left else right_cycle
        counter.sort_calls += 1
        counter.sort_items += len(scan_cycle)
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
                route = (*left_route, *right_route)
                counter.route_indices_copied += len(route)
                return route
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


def d2_mitm_query(
    cycle: Cycle,
    target: Point,
    p: int,
    a: int,
) -> tuple[tuple[int, ...] | None, int, int]:
    scans = 0
    lookups = 0
    for left in sorted(cycle, key=point_key):
        scans += 1
        complement = subtract(target, left, p, a)
        lookups += 1
        if complement in cycle:
            route = (
                *cycle[left].first_route,
                *cycle[complement].first_route,
            )
            return tuple(sorted(route)), scans, lookups
    return None, scans, lookups


def same_function_baselines(
    root_cycle: Cycle,
    points: list[Point],
    positives: list[Point],
    negatives: list[Point],
    all_targets: list[Point],
    p: int,
    a: int,
) -> dict[str, Any]:
    root_support = reduced_cycle(root_cycle)
    d2_support = reduced_cycle(direct_degree(points, 2, p, a))
    d2_receipts = []
    sample_worst_scans = 0
    all_valid = True
    for target, expected_hit in (
        *((target, True) for target in positives),
        *((target, False) for target in negatives),
    ):
        route, scans, lookups = d2_mitm_query(
            d2_support, target, p, a
        )
        replay_counter = CurveCounter()
        replay = (
            None
            if route is None
            else sum_points(
                (points[index] for index in route),
                p,
                a,
                replay_counter,
            )
        )
        valid = (
            route is not None
            and replay == target
            if expected_hit
            else route is None
        )
        all_valid = all_valid and valid
        sample_worst_scans = max(sample_worst_scans, scans)
        d2_receipts.append(
            {
                "target": point_json(target),
                "expected_hit": expected_hit,
                "route": None if route is None else list(route),
                "replay": point_json(replay),
                "point_scans": scans,
                "hash_lookups": lookups,
                "witness_replay_operations": (
                    replay_counter.as_dict()
                ),
                "valid": valid,
            }
        )
    exhaustive_worst_scans = 0
    exhaustive_hits = 0
    exhaustive_valid = True
    exhaustive_scans = 0
    exhaustive_lookups = 0
    exhaustive_receipts = []
    for target in all_targets:
        route, scans, lookups = d2_mitm_query(
            d2_support, target, p, a
        )
        expected_hit = target in root_support
        replay_counter = CurveCounter()
        replay = (
            None
            if route is None
            else sum_points(
                (points[index] for index in route),
                p,
                a,
                replay_counter,
            )
        )
        valid = (
            route is not None and replay == target
            if expected_hit
            else route is None
        )
        exhaustive_hits += int(route is not None)
        exhaustive_valid = exhaustive_valid and valid
        exhaustive_worst_scans = max(
            exhaustive_worst_scans, scans
        )
        exhaustive_scans += scans
        exhaustive_lookups += lookups
        exhaustive_receipts.append(
            [
                point_json(target),
                None if route is None else list(route),
                scans,
                lookups,
                replay_counter.as_dict(),
                valid,
            ]
        )
    root_state = cycle_state(root_support)
    d2_state = cycle_state(d2_support)
    return {
        "exact_support_hash": {
            **root_state,
            "online_hash_lookups": 1,
            "online_point_scans": 0,
            "returns_source_route": True,
        },
        "exact_support_sorted": {
            **root_state,
            "online_comparison_upper_bound": math.ceil(
                math.log2(max(1, len(root_support)))
            ),
            "returns_source_route": True,
        },
        "reduced_d2_mitm": {
            **d2_state,
            "sample_worst_online_point_scans": sample_worst_scans,
            "exhaustive_worst_online_point_scans": (
                exhaustive_worst_scans
            ),
            "exhaustive_targets": len(all_targets),
            "exhaustive_hits": exhaustive_hits,
            "exhaustive_total_point_scans": exhaustive_scans,
            "exhaustive_total_hash_lookups": exhaustive_lookups,
            "exhaustive_receipt_digest": digest(
                exhaustive_receipts
            ),
            "all_exhaustive_queries_valid": exhaustive_valid,
            "queries": d2_receipts,
            "all_queries_valid": all_valid,
            "returns_source_route": True,
        },
        "boundary": (
            "Same-function fixed-factor-base D4 membership and first-route "
            "recovery. Logical words are typed values, not measured bytes."
        ),
    }


def subgroup_points(
    generator: Point, q: int, p: int, a: int
) -> list[Point]:
    points: list[Point] = []
    current: Point = None
    for _ in range(q):
        points.append(current)
        current = add(current, generator, p, a)
    if current is not None or len(set(points)) != q:
        raise ValueError("generator does not enumerate the subgroup")
    return points


def exhaustive_rootless_queries(
    query_root: Node,
    root_cycle: Cycle,
    points: list[Point],
    targets: list[Point],
    p: int,
    a: int,
) -> dict[str, Any]:
    totals = QueryCounter()
    replay_totals = CurveCounter()
    worst_scans = 0
    hits = 0
    valid = True
    receipts = []
    for target in targets:
        counter = QueryCounter()
        route = query(
            query_root,
            4,
            target,
            p,
            a,
            counter,
            membership_prefilter=False,
        )
        replay_counter = CurveCounter()
        replay = (
            None
            if route is None
            else sum_points(
                (points[index] for index in route),
                p,
                a,
                replay_counter,
            )
        )
        expected_hit = target in root_cycle
        query_valid = (
            route is not None
            and tuple(sorted(route)) == route
            and replay == target
            if expected_hit
            else route is None
        )
        totals.absorb(counter)
        replay_totals.absorb(replay_counter)
        worst_scans = max(worst_scans, counter.point_scans)
        hits += int(route is not None)
        valid = valid and query_valid
        receipts.append(
            [
                point_json(target),
                None if route is None else list(route),
                point_json(replay),
                counter.as_dict(),
                replay_counter.as_dict(),
                query_valid,
            ]
        )
    return {
        "targets": len(targets),
        "hits": hits,
        "misses": len(targets) - hits,
        "worst_online_point_scans": worst_scans,
        "total_query_operations": totals.as_dict(),
        "total_witness_replay_operations": replay_totals.as_dict(),
        "target_order_digest": digest(
            [point_json(target) for target in targets]
        ),
        "receipt_digest": digest(receipts),
        "all_queries_valid": valid,
        "fixture_generation_boundary": (
            "Subgroup target enumeration is diagnostic fixture work and is "
            "not included in online query operations."
        ),
    }


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
    advice_nodes = nodes[1:]
    root_cycle = root.cycles[4]
    oracle = direct_canonical(points, p, a)
    oracle_match = (
        coefficient_payload(root_cycle) == coefficient_payload(oracle)
    )
    build_peak_cycle_records = sum(
        len(cycle) for node in nodes for cycle in node.cycles.values()
    )
    build_peak_point_field_elements = sum(
        2
        for node in nodes
        for cycle in node.cycles.values()
        for image in cycle
        if image is not None
    )
    build_peak_route_indices = sum(
        len(record.first_route)
        for node in nodes
        for cycle in node.cycles.values()
        for record in cycle.values()
    )
    retained_records = sum(
        len(cycle)
        for node in advice_nodes
        for cycle in node.cycles.values()
    )
    retained_point_field_elements = sum(
        2
        for node in advice_nodes
        for cycle in node.cycles.values()
        for image in cycle
        if image is not None
    )
    retained_route_indices = sum(
        len(record.first_route)
        for node in advice_nodes
        for cycle in node.cycles.values()
        for record in cycle.values()
    )
    generator = decode_point(curve["generator"])
    positives, negatives = select_queries(
        root_cycle,
        generator,
        q,
        p,
        a,
    )
    positive_receipts = []
    sample_worst_scans = 0
    query_root = Node(
        node_id=root.node_id,
        start=root.start,
        stop=root.stop,
        left=root.left,
        right=root.right,
        cycles={},
    )
    for target in positives:
        counter = QueryCounter()
        route = query(
            query_root,
            4,
            target,
            p,
            a,
            counter,
            membership_prefilter=False,
        )
        replay_counter = CurveCounter()
        replay = (
            None
            if route is None
            else sum_points(
                (points[index] for index in route),
                p,
                a,
                replay_counter,
            )
        )
        sample_worst_scans = max(
            sample_worst_scans, counter.point_scans
        )
        positive_receipts.append(
            {
                "target": point_json(target),
                "route": None if route is None else list(route),
                "replay": point_json(replay),
                "valid": route is not None
                and tuple(sorted(route)) == route
                and replay == target,
                "operations": counter.as_dict(),
                "witness_replay_operations": (
                    replay_counter.as_dict()
                ),
            }
        )
    negative_receipts = []
    for target in negatives:
        counter = QueryCounter()
        route = query(
            query_root,
            4,
            target,
            p,
            a,
            counter,
            membership_prefilter=False,
        )
        sample_worst_scans = max(
            sample_worst_scans, counter.point_scans
        )
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
    retained_payload = [
        {
            "node_id": node.node_id,
            "degrees": {
                str(degree): cycle_payload(cycle)
                for degree, cycle in node.cycles.items()
            },
        }
        for node in advice_nodes
    ]
    build_payload = [
        {
            "node_id": node.node_id,
            "degrees": {
                str(degree): cycle_payload(cycle)
                for degree, cycle in node.cycles.items()
            },
        }
        for node in nodes
    ]
    all_targets = subgroup_points(generator, q, p, a)
    exhaustive = exhaustive_rootless_queries(
        query_root,
        root_cycle,
        points,
        all_targets,
        p,
        a,
    )
    worst_scans = exhaustive["worst_online_point_scans"]
    baselines = same_function_baselines(
        root_cycle,
        points,
        positives,
        negatives,
        all_targets,
        p,
        a,
    )
    sqrt_q = math.sqrt(q)
    signal_gate = (
        retained_records < expanded_oriented_field_elements
        and worst_scans < sqrt_q
    )
    valid = (
        oracle_match
        and all(receipt["valid"] for receipt in positive_receipts)
        and all(receipt["valid"] for receipt in negative_receipts)
        and exhaustive["all_queries_valid"]
        and baselines["reduced_d2_mitm"][
            "all_exhaustive_queries_valid"
        ]
    )
    posthoc_same_function_gate = (
        (
            retained_records
            + retained_point_field_elements
            + retained_route_indices
        )
        < baselines["exact_support_hash"]["logical_words"]
        and worst_scans
        < baselines["exact_support_sorted"][
            "online_comparison_upper_bound"
        ]
        and retained_records
        < baselines["reduced_d2_mitm"]["records"]
        and worst_scans
        < baselines["reduced_d2_mitm"][
            "exhaustive_worst_online_point_scans"
        ]
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
        "online_advice_node_count": len(advice_nodes),
        "online_advice_edge_count": max(
            0, 2 * (len(points) - 1) - 2
        ),
        "root_cycle_discarded_for_query": True,
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
        "retained_canonical_json_bytes": canonical_json_bytes(
            retained_payload
        ),
        "build_peak_canonical_json_bytes": canonical_json_bytes(
            build_payload
        ),
        "build_peak_cycle_records": build_peak_cycle_records,
        "build_peak_point_field_elements": (
            build_peak_point_field_elements
        ),
        "build_peak_route_indices": build_peak_route_indices,
        "build_peak_logical_words": (
            build_peak_cycle_records
            + build_peak_point_field_elements
            + build_peak_route_indices
        ),
        "build_operations": build_counter.as_dict(),
        "positive_queries": positive_receipts,
        "negative_queries": negative_receipts,
        "sample_worst_online_point_scans": sample_worst_scans,
        "exhaustive_queries": exhaustive,
        "worst_online_point_scans": worst_scans,
        "expanded_oriented_field_elements": (
            expanded_oriented_field_elements
        ),
        "sqrt_q": sqrt_q,
        "membership_tradeoff_diagnostic": (
            retained_records * worst_scans * worst_scans / q
        ),
        "same_function_baselines": baselines,
        "posthoc_same_function_gate": posthoc_same_function_gate,
        "generic_numerical_references": {
            "ceil_sqrt_q": math.ceil(sqrt_q),
            "bsgs_baby_group_records": math.ceil(sqrt_q),
            "rho_expected_group_work_scale": sqrt_q,
            "commensurate_with_logical_words": False,
        },
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
            "posthoc_same_function_signal_cells": sum(
                row["posthoc_same_function_gate"] for row in rows
            ),
            "all_d2_mitm_queries_valid": all(
                row["same_function_baselines"]["reduced_d2_mitm"][
                    "all_exhaustive_queries_valid"
                ]
                for row in rows
            ),
            "all_exhaustive_rootless_queries_valid": all(
                row["exhaustive_queries"]["all_queries_valid"]
                for row in rows
            ),
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

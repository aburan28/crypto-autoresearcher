#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
PRODUCER_PATH = SCRIPT_PATH.with_name("factored_divided_power_dag.py")
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


def decode_point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def encode_point(value: Point) -> list[int] | None:
    return None if value is None else [value[0], value[1]]


def point_key(value: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if value is None else (1, value[0], value[1])


@dataclass
class CurveCounts:
    additions: int = 0
    doublings: int = 0
    inversions: int = 0
    identity_returns: int = 0
    inverse_returns: int = 0

    def payload(self) -> dict[str, int]:
        return {
            "additions": self.additions,
            "doublings": self.doublings,
            "inversions": self.inversions,
            "identity_returns": self.identity_returns,
            "inverse_returns": self.inverse_returns,
        }

    def absorb(self, other: CurveCounts) -> None:
        self.additions += other.additions
        self.doublings += other.doublings
        self.inversions += other.inversions
        self.identity_returns += other.identity_returns
        self.inverse_returns += other.inverse_returns


def ec_add(
    left: Point,
    right: Point,
    p: int,
    a: int,
    counts: CurveCounts | None = None,
) -> Point:
    if counts is not None:
        counts.additions += 1
    if left is None:
        if counts is not None:
            counts.identity_returns += 1
        return right
    if right is None:
        if counts is not None:
            counts.identity_returns += 1
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        if counts is not None:
            counts.inverse_returns += 1
        return None
    if counts is not None:
        counts.inversions += 1
        counts.doublings += int(left == right)
    if left == right:
        numerator = (3 * x1 * x1 + a) % p
        denominator = 2 * y1 % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def ec_sum(
    values: Iterable[Point],
    p: int,
    a: int,
    counts: CurveCounts | None = None,
) -> Point:
    result: Point = None
    for value in values:
        result = ec_add(result, value, p, a, counts)
    return result


def ec_negate(value: Point, p: int) -> Point:
    return None if value is None else (value[0], (-value[1]) % p)


def scalar_mul(value: Point, scalar: int, p: int, a: int) -> Point:
    result: Point = None
    current = value
    while scalar:
        if scalar & 1:
            result = ec_add(result, current, p, a)
        current = ec_add(current, current, p, a)
        scalar >>= 1
    return result


def repeated_mul(
    value: Point,
    scalar: int,
    p: int,
    a: int,
    counts: CurveCounts,
) -> Point:
    return ec_sum(
        (value for _ in range(scalar)), p, a, counts
    )


@dataclass
class Record:
    multiplicity: int
    route: tuple[int, ...]


Cycle = dict[Point, Record]


@dataclass
class BuildCounts:
    pair_attempts: int = 0
    hash_lookups: int = 0
    record_writes: int = 0
    leaf_scalar_steps: int = 0
    leaf_record_writes: int = 0
    curve: CurveCounts = field(default_factory=CurveCounts)

    def payload(self) -> dict[str, Any]:
        return {
            "pair_attempts": self.pair_attempts,
            "hash_lookups": self.hash_lookups,
            "record_writes": self.record_writes,
            "leaf_scalar_steps": self.leaf_scalar_steps,
            "leaf_record_writes": self.leaf_record_writes,
            "curve": self.curve.payload(),
        }


@dataclass
class VerifiedNode:
    node_id: str
    start: int
    stop: int
    left: VerifiedNode | None
    right: VerifiedNode | None
    cycles: dict[int, Cycle]


def put(
    cycle: Cycle,
    image: Point,
    multiplicity: int,
    route: tuple[int, ...],
    counts: BuildCounts | None = None,
) -> None:
    if counts is not None:
        counts.hash_lookups += 1
    if image not in cycle:
        cycle[image] = Record(0, route)
        if counts is not None:
            counts.record_writes += 1
    cycle[image].multiplicity += multiplicity


def leaf(
    index: int,
    value: Point,
    p: int,
    a: int,
    counts: BuildCounts,
) -> VerifiedNode:
    cycles: dict[int, Cycle] = {}
    for degree in range(5):
        image = repeated_mul(
            value, degree, p, a, counts.curve
        )
        counts.leaf_scalar_steps += degree
        counts.leaf_record_writes += 1
        cycles[degree] = {
            image: Record(1, (index,) * degree)
        }
    return VerifiedNode(
        f"L{index}", index, index + 1, None, None, cycles
    )


def merge(
    left: VerifiedNode,
    right: VerifiedNode,
    p: int,
    a: int,
    counts: BuildCounts,
) -> VerifiedNode:
    cycles: dict[int, Cycle] = {}
    for degree in range(5):
        cycle: Cycle = {}
        for left_degree in range(degree + 1):
            right_degree = degree - left_degree
            for left_image, left_record in left.cycles[
                left_degree
            ].items():
                for right_image, right_record in right.cycles[
                    right_degree
                ].items():
                    counts.pair_attempts += 1
                    image = ec_add(
                        left_image,
                        right_image,
                        p,
                        a,
                        counts.curve,
                    )
                    put(
                        cycle,
                        image,
                        (
                            left_record.multiplicity
                            * right_record.multiplicity
                        ),
                        (*left_record.route, *right_record.route),
                        counts,
                    )
        cycles[degree] = cycle
    return VerifiedNode(
        f"N{left.start}-{right.stop}",
        left.start,
        right.stop,
        left,
        right,
        cycles,
    )


def rebuild(
    points: list[Point],
    start: int,
    stop: int,
    p: int,
    a: int,
    counts: BuildCounts,
) -> VerifiedNode:
    if stop - start == 1:
        return leaf(start, points[start], p, a, counts)
    middle = (start + stop) // 2
    return merge(
        rebuild(points, start, middle, p, a, counts),
        rebuild(points, middle, stop, p, a, counts),
        p,
        a,
        counts,
    )


def flatten(node: VerifiedNode) -> list[VerifiedNode]:
    result = [node]
    if node.left is not None:
        result.extend(flatten(node.left))
    if node.right is not None:
        result.extend(flatten(node.right))
    return result


def cycle_payload(cycle: Cycle) -> list[dict[str, Any]]:
    return [
        {
            "point": encode_point(image),
            "multiplicity": cycle[image].multiplicity,
            "first_route": list(cycle[image].route),
        }
        for image in sorted(cycle, key=point_key)
    ]


def coefficient_payload(cycle: Cycle) -> list[list[Any]]:
    return [
        [encode_point(image), cycle[image].multiplicity]
        for image in sorted(cycle, key=point_key)
    ]


def direct_cycle(
    points: list[Point], p: int, a: int, degree: int = 4
) -> Cycle:
    result: Cycle = {}
    for route in itertools.combinations_with_replacement(
        range(len(points)), degree
    ):
        put(
            result,
            ec_sum((points[index] for index in route), p, a),
            1,
            route,
        )
    return result


def reduce_support(cycle: Cycle) -> Cycle:
    return {
        image: Record(1, record.route)
        for image, record in cycle.items()
    }


def cycle_state(cycle: Cycle) -> dict[str, int]:
    point_fields = 2 * sum(image is not None for image in cycle)
    route_indices = sum(len(record.route) for record in cycle.values())
    return {
        "records": len(cycle),
        "point_field_elements": point_fields,
        "route_indices": route_indices,
        "logical_words": len(cycle) + point_fields + route_indices,
        "canonical_json_bytes": canonical_json_bytes(
            cycle_payload(cycle)
        ),
    }


def node_receipt(node: VerifiedNode) -> dict[str, Any]:
    degrees = {}
    for degree, cycle in node.cycles.items():
        degrees[str(degree)] = {
            "route_degree": sum(
                record.multiplicity for record in cycle.values()
            ),
            "support": len(cycle),
            "infinity_multiplicity": (
                cycle[None].multiplicity if None in cycle else 0
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


@dataclass
class QueryCounts:
    split_attempts: int = 0
    point_scans: int = 0
    hash_lookups: int = 0
    recursion_nodes: int = 0
    sort_calls: int = 0
    sort_items: int = 0
    route_indices_copied: int = 0
    curve: CurveCounts = field(default_factory=CurveCounts)

    def payload(self) -> dict[str, Any]:
        return {
            "split_attempts": self.split_attempts,
            "point_scans": self.point_scans,
            "hash_lookups": self.hash_lookups,
            "recursion_nodes": self.recursion_nodes,
            "sort_calls": self.sort_calls,
            "sort_items": self.sort_items,
            "route_indices_copied": self.route_indices_copied,
            "curve": self.curve.payload(),
        }

    def absorb(self, other: QueryCounts) -> None:
        self.split_attempts += other.split_attempts
        self.point_scans += other.point_scans
        self.hash_lookups += other.hash_lookups
        self.recursion_nodes += other.recursion_nodes
        self.sort_calls += other.sort_calls
        self.sort_items += other.sort_items
        self.route_indices_copied += other.route_indices_copied
        self.curve.absorb(other.curve)


def descend(
    node: VerifiedNode,
    degree: int,
    target: Point,
    p: int,
    a: int,
    counts: QueryCounts,
    membership_prefilter: bool = True,
) -> tuple[int, ...] | None:
    counts.recursion_nodes += 1
    if membership_prefilter:
        counts.hash_lookups += 1
        if target not in node.cycles[degree]:
            return None
    if node.left is None or node.right is None:
        if not membership_prefilter:
            return None
        return node.cycles[degree][target].route
    for left_degree in range(degree + 1):
        counts.split_attempts += 1
        right_degree = degree - left_degree
        left_cycle = node.left.cycles[left_degree]
        right_cycle = node.right.cycles[right_degree]
        scan_left = len(left_cycle) <= len(right_cycle)
        scan_cycle = left_cycle if scan_left else right_cycle
        counts.sort_calls += 1
        counts.sort_items += len(scan_cycle)
        for scanned in sorted(scan_cycle, key=point_key):
            counts.point_scans += 1
            complement = ec_add(
                target,
                ec_negate(scanned, p),
                p,
                a,
                counts.curve,
            )
            counts.hash_lookups += 1
            other = right_cycle if scan_left else left_cycle
            if complement not in other:
                continue
            left_image = scanned if scan_left else complement
            right_image = complement if scan_left else scanned
            left_route = descend(
                node.left,
                left_degree,
                left_image,
                p,
                a,
                counts,
            )
            if left_route is None:
                continue
            right_route = descend(
                node.right,
                right_degree,
                right_image,
                p,
                a,
                counts,
            )
            if right_route is not None:
                route = (*left_route, *right_route)
                counts.route_indices_copied += len(route)
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
    negatives: list[Point] = []
    scalar = 1
    while len(negatives) < min(16, q - len(root_cycle)):
        candidate = scalar_mul(generator, scalar, p, a)
        if candidate not in root_cycle:
            negatives.append(candidate)
        scalar += 1
    return positives, negatives


def route_valid(
    route: tuple[int, ...],
    image: Point,
    degree: int,
    start: int,
    stop: int,
    points: list[Point],
    p: int,
    a: int,
) -> bool:
    return (
        len(route) == degree
        and tuple(sorted(route)) == route
        and all(start <= index < stop for index in route)
        and ec_sum((points[index] for index in route), p, a) == image
    )


def recorded_queries(
    root: VerifiedNode,
    points: list[Point],
    generator: Point,
    q: int,
    p: int,
    a: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    positives, negatives = select_queries(
        root.cycles[4], generator, q, p, a
    )
    query_root = VerifiedNode(
        root.node_id,
        root.start,
        root.stop,
        root.left,
        root.right,
        {},
    )
    positive_receipts = []
    negative_receipts = []
    worst_scans = 0
    for target in positives:
        counts = QueryCounts()
        route = descend(
            query_root,
            4,
            target,
            p,
            a,
            counts,
            membership_prefilter=False,
        )
        replay_counts = CurveCounts()
        replay = (
            None
            if route is None
            else ec_sum(
                (points[index] for index in route),
                p,
                a,
                replay_counts,
            )
        )
        worst_scans = max(worst_scans, counts.point_scans)
        positive_receipts.append(
            {
                "target": encode_point(target),
                "route": None if route is None else list(route),
                "replay": encode_point(replay),
                "valid": route is not None
                and tuple(sorted(route)) == route
                and replay == target,
                "operations": counts.payload(),
                "witness_replay_operations": (
                    replay_counts.payload()
                ),
            }
        )
    for target in negatives:
        counts = QueryCounts()
        route = descend(
            query_root,
            4,
            target,
            p,
            a,
            counts,
            membership_prefilter=False,
        )
        worst_scans = max(worst_scans, counts.point_scans)
        negative_receipts.append(
            {
                "target": encode_point(target),
                "route": None if route is None else list(route),
                "valid": route is None,
                "operations": counts.payload(),
            }
        )
    return positive_receipts, negative_receipts, worst_scans


def d2_lookup(
    cycle: Cycle,
    target: Point,
    p: int,
    a: int,
) -> tuple[tuple[int, ...] | None, int, int]:
    scans = 0
    lookups = 0
    for left in sorted(cycle, key=point_key):
        scans += 1
        complement = ec_add(target, ec_negate(left, p), p, a)
        lookups += 1
        if complement in cycle:
            route = (*cycle[left].route, *cycle[complement].route)
            return tuple(sorted(route)), scans, lookups
    return None, scans, lookups


def reconstruct_baselines(
    root_cycle: Cycle,
    points: list[Point],
    positives: list[Point],
    negatives: list[Point],
    all_targets: list[Point],
    p: int,
    a: int,
) -> dict[str, Any]:
    root_support = reduce_support(root_cycle)
    d2_support = reduce_support(direct_cycle(points, p, a, degree=2))
    receipts = []
    sample_worst_scans = 0
    all_valid = True
    cases = [
        *((target, True) for target in positives),
        *((target, False) for target in negatives),
    ]
    for target, expected_hit in cases:
        route, scans, lookups = d2_lookup(
            d2_support, target, p, a
        )
        replay_counts = CurveCounts()
        replay = (
            None
            if route is None
            else ec_sum(
                (points[index] for index in route),
                p,
                a,
                replay_counts,
            )
        )
        valid = (
            route is not None and replay == target
            if expected_hit
            else route is None
        )
        all_valid = all_valid and valid
        sample_worst_scans = max(sample_worst_scans, scans)
        receipts.append(
            {
                "target": encode_point(target),
                "expected_hit": expected_hit,
                "route": None if route is None else list(route),
                "replay": encode_point(replay),
                "point_scans": scans,
                "hash_lookups": lookups,
                "witness_replay_operations": (
                    replay_counts.payload()
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
        route, scans, lookups = d2_lookup(
            d2_support, target, p, a
        )
        expected_hit = target in root_support
        replay_counts = CurveCounts()
        replay = (
            None
            if route is None
            else ec_sum(
                (points[index] for index in route),
                p,
                a,
                replay_counts,
            )
        )
        valid = (
            route is not None and replay == target
            if expected_hit
            else route is None
        )
        exhaustive_worst_scans = max(
            exhaustive_worst_scans, scans
        )
        exhaustive_hits += int(route is not None)
        exhaustive_valid = exhaustive_valid and valid
        exhaustive_scans += scans
        exhaustive_lookups += lookups
        exhaustive_receipts.append(
            [
                encode_point(target),
                None if route is None else list(route),
                scans,
                lookups,
                replay_counts.payload(),
                valid,
            ]
        )
    root_state = cycle_state(root_support)
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
            **cycle_state(d2_support),
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
            "queries": receipts,
            "all_queries_valid": all_valid,
            "returns_source_route": True,
        },
        "boundary": (
            "Same-function fixed-factor-base D4 membership and first-route "
            "recovery. Logical words are typed values, not measured bytes."
        ),
    }


def enumerate_subgroup(
    generator: Point, q: int, p: int, a: int
) -> list[Point]:
    result: list[Point] = []
    current: Point = None
    for _ in range(q):
        result.append(current)
        current = ec_add(current, generator, p, a)
    if current is not None or len(set(result)) != q:
        raise ValueError("invalid subgroup enumeration")
    return result


def exhaustive_queries(
    root: VerifiedNode,
    root_cycle: Cycle,
    points: list[Point],
    targets: list[Point],
    p: int,
    a: int,
) -> dict[str, Any]:
    query_root = VerifiedNode(
        root.node_id,
        root.start,
        root.stop,
        root.left,
        root.right,
        {},
    )
    totals = QueryCounts()
    replay_totals = CurveCounts()
    worst_scans = 0
    hits = 0
    valid = True
    receipts = []
    for target in targets:
        counts = QueryCounts()
        route = descend(
            query_root,
            4,
            target,
            p,
            a,
            counts,
            membership_prefilter=False,
        )
        replay_counts = CurveCounts()
        replay = (
            None
            if route is None
            else ec_sum(
                (points[index] for index in route),
                p,
                a,
                replay_counts,
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
        totals.absorb(counts)
        replay_totals.absorb(replay_counts)
        worst_scans = max(worst_scans, counts.point_scans)
        hits += int(route is not None)
        valid = valid and query_valid
        receipts.append(
            [
                encode_point(target),
                None if route is None else list(route),
                encode_point(replay),
                counts.payload(),
                replay_counts.payload(),
                query_valid,
            ]
        )
    return {
        "targets": len(targets),
        "hits": hits,
        "misses": len(targets) - hits,
        "worst_online_point_scans": worst_scans,
        "total_query_operations": totals.payload(),
        "total_witness_replay_operations": replay_totals.payload(),
        "target_order_digest": digest(
            [encode_point(target) for target in targets]
        ),
        "receipt_digest": digest(receipts),
        "all_queries_valid": valid,
        "fixture_generation_boundary": (
            "Subgroup target enumeration is diagnostic fixture work and is "
            "not included in online query operations."
        ),
    }


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def verify_row(
    recorded: dict[str, Any],
    curve: dict[str, Any],
    family: dict[str, Any],
) -> dict[str, Any]:
    p, q, a = curve["p"], curve["q"], curve["a"]
    points = [
        decode_point(value)
        for value in family["factor_base"]["points"][
            : recorded["b_size"]
        ]
    ]
    counts = BuildCounts()
    root = rebuild(points, 0, len(points), p, a, counts)
    nodes = flatten(root)
    advice_nodes = nodes[1:]
    oracle = direct_cycle(points, p, a)
    positives, negatives, worst_scans = recorded_queries(
        root,
        points,
        decode_point(curve["generator"]),
        q,
        p,
        a,
    )
    all_targets = enumerate_subgroup(
        decode_point(curve["generator"]), q, p, a
    )
    exhaustive = exhaustive_queries(
        root, root.cycles[4], points, all_targets, p, a
    )
    build_peak_records = sum(
        len(cycle) for node in nodes for cycle in node.cycles.values()
    )
    build_peak_point_fields = sum(
        2
        for node in nodes
        for cycle in node.cycles.values()
        for image in cycle
        if image is not None
    )
    build_peak_route_indices = sum(
        len(record.route)
        for node in nodes
        for cycle in node.cycles.values()
        for record in cycle.values()
    )
    retained_records = sum(
        len(cycle)
        for node in advice_nodes
        for cycle in node.cycles.values()
    )
    point_fields = sum(
        2
        for node in advice_nodes
        for cycle in node.cycles.values()
        for image in cycle
        if image is not None
    )
    route_indices = sum(
        len(record.route)
        for node in advice_nodes
        for cycle in node.cycles.values()
        for record in cycle.values()
    )
    finite_degree = sum(
        record.multiplicity
        for image, record in root.cycles[4].items()
        if image is not None
    )
    expanded = 2 * (finite_degree + 1)
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
    baselines = reconstruct_baselines(
        root.cycles[4],
        points,
        [decode_point(item["target"]) for item in positives],
        [decode_point(item["target"]) for item in negatives],
        all_targets,
        p,
        a,
    )
    sqrt_q = math.sqrt(q)
    exhaustive_worst_scans = exhaustive[
        "worst_online_point_scans"
    ]
    diagnostic = retained_records * exhaustive_worst_scans**2 / q
    signal = (
        retained_records < expanded
        and exhaustive_worst_scans < sqrt_q
    )
    logical_words = retained_records + point_fields + route_indices
    posthoc_same_function_gate = (
        logical_words
        < baselines["exact_support_hash"]["logical_words"]
        and exhaustive_worst_scans
        < baselines["exact_support_sorted"][
            "online_comparison_upper_bound"
        ]
        and retained_records
        < baselines["reduced_d2_mitm"]["records"]
        and exhaustive_worst_scans
        < baselines["reduced_d2_mitm"][
            "exhaustive_worst_online_point_scans"
        ]
    )
    route_checks = [
        route_valid(
            record.route,
            image,
            degree,
            node.start,
            node.stop,
            points,
            p,
            a,
        )
        for node in nodes
        for degree, cycle in node.cycles.items()
        for image, record in cycle.items()
    ]
    all_support_queries = []
    query_root = VerifiedNode(
        root.node_id,
        root.start,
        root.stop,
        root.left,
        root.right,
        {},
    )
    for target in root.cycles[4]:
        query_counts = QueryCounts()
        route = descend(
            query_root,
            4,
            target,
            p,
            a,
            query_counts,
            membership_prefilter=False,
        )
        all_support_queries.append(
            route is not None
            and route_valid(
                route,
                target,
                4,
                0,
                len(points),
                points,
                p,
                a,
            )
        )
    coefficient = coefficient_payload(root.cycles[4])
    oracle_coefficient = coefficient_payload(oracle)
    expected_nodes = [node_receipt(node) for node in nodes]
    checks = {
        "identity": (
            recorded["curve_id"] == curve["id"]
            and recorded["p"] == p
            and recorded["q"] == q
            and recorded["family"] == family["family"]
        ),
        "factor_base": recorded["factor_base"]
        == [encode_point(value) for value in points],
        "factor_base_on_curve": all(
            value is not None
            and (value[1] ** 2 - value[0] ** 3 - a * value[0] - curve["b"])
            % p
            == 0
            for value in points
        ),
        "tree_shape": (
            recorded["node_count"] == len(nodes)
            and recorded["edge_count"] == 2 * (len(points) - 1)
            and recorded["nodes"] == expected_nodes
        ),
        "online_advice_shape": (
            recorded["online_advice_node_count"]
            == len(advice_nodes)
            and recorded["online_advice_edge_count"]
            == max(0, 2 * (len(points) - 1) - 2)
            and recorded["root_cycle_discarded_for_query"] is True
        ),
        "all_stored_routes_valid": all(route_checks),
        "all_root_support_queries_valid": all(all_support_queries),
        "root_cycle": recorded["root_cycle"]
        == cycle_payload(root.cycles[4]),
        "root_cycle_digest": recorded["root_cycle_digest"]
        == digest(cycle_payload(root.cycles[4])),
        "root_coefficient_digest": recorded["root_coefficient_digest"]
        == digest(coefficient),
        "oracle_coefficient_digest": recorded["oracle_coefficient_digest"]
        == digest(oracle_coefficient),
        "oracle_match": (
            recorded["oracle_match"] is True
            and coefficient == oracle_coefficient
        ),
        "retained_records": recorded["retained_records"]
        == retained_records,
        "retained_point_field_elements": (
            recorded["retained_point_field_elements"] == point_fields
        ),
        "retained_route_indices": (
            recorded["retained_route_indices"] == route_indices
        ),
        "logical_words": recorded["logical_words"]
        == logical_words,
        "retained_canonical_json_bytes": (
            recorded["retained_canonical_json_bytes"]
            == canonical_json_bytes(retained_payload)
        ),
        "build_peak_canonical_json_bytes": (
            recorded["build_peak_canonical_json_bytes"]
            == canonical_json_bytes(build_payload)
        ),
        "build_peak_cycle_records": (
            recorded["build_peak_cycle_records"] == build_peak_records
        ),
        "build_peak_point_field_elements": (
            recorded["build_peak_point_field_elements"]
            == build_peak_point_fields
        ),
        "build_peak_route_indices": (
            recorded["build_peak_route_indices"]
            == build_peak_route_indices
        ),
        "build_peak_logical_words": (
            recorded["build_peak_logical_words"]
            == build_peak_records
            + build_peak_point_fields
            + build_peak_route_indices
        ),
        "build_operations": recorded["build_operations"]
        == counts.payload(),
        "positive_queries": recorded["positive_queries"] == positives,
        "negative_queries": recorded["negative_queries"] == negatives,
        "sample_worst_online_point_scans": (
            recorded["sample_worst_online_point_scans"]
            == worst_scans
        ),
        "exhaustive_queries": (
            recorded["exhaustive_queries"] == exhaustive
        ),
        "worst_online_point_scans": (
            recorded["worst_online_point_scans"]
            == exhaustive_worst_scans
        ),
        "expanded_oriented_field_elements": (
            recorded["expanded_oriented_field_elements"] == expanded
        ),
        "sqrt_q": close(recorded["sqrt_q"], sqrt_q),
        "membership_tradeoff_diagnostic": close(
            recorded["membership_tradeoff_diagnostic"], diagnostic
        ),
        "same_function_baselines": (
            recorded["same_function_baselines"] == baselines
        ),
        "posthoc_same_function_gate": (
            recorded["posthoc_same_function_gate"]
            is posthoc_same_function_gate
        ),
        "generic_numerical_references": (
            recorded["generic_numerical_references"]
            == {
                "ceil_sqrt_q": math.ceil(sqrt_q),
                "bsgs_baby_group_records": math.ceil(sqrt_q),
                "rho_expected_group_work_scale": sqrt_q,
                "commensurate_with_logical_words": False,
            }
        ),
        "signal_gate": recorded["signal_gate"] is signal,
        "recorded_valid": recorded["valid"] is True,
    }
    return {
        "curve_id": curve["id"],
        "family": family["family"],
        "b_size": recorded["b_size"],
        "checks": checks,
        "node_count": len(nodes),
        "root_support": len(root.cycles[4]),
        "all_stored_routes_checked": len(route_checks),
        "all_root_support_queries_checked": len(all_support_queries),
        "valid": all(checks.values()),
    }


EXPECTED_FAMILIES = [
    "x_interval",
    "scalar_progression_control",
    "random_x",
    "source_prf_x",
]
EXPECTED_B_VALUES = [2, 3, 4, 5]


def envelope(
    raw: dict[str, Any], typed: dict[str, Any]
) -> dict[str, bool]:
    config = raw["config"]
    config_exact = (
        config["curve_index"] == 0
        and config["families"] == EXPECTED_FAMILIES
        and config["b_values"] == EXPECTED_B_VALUES
    )
    instance = typed["instances"][0]
    expected = [
        (instance["curve"]["id"], family, b_size)
        for family in EXPECTED_FAMILIES
        for b_size in EXPECTED_B_VALUES
    ]
    actual = [
        (row["curve_id"], row["family"], row["b_size"])
        for row in raw["rows"]
    ]
    rows_exact = actual == expected and len(actual) == len(set(actual))
    summary = raw["summary"]
    return {
        "config_exact": config_exact,
        "expected_rows_exact": rows_exact,
        "summary_exact": (
            rows_exact
            and summary["cells"] == len(raw["rows"])
            and summary["all_cells_valid"]
            == all(row["valid"] for row in raw["rows"])
            and summary["all_oracles_match"]
            == all(row["oracle_match"] for row in raw["rows"])
            and summary["signal_cells"]
            == sum(row["signal_gate"] for row in raw["rows"])
            and summary["posthoc_same_function_signal_cells"]
            == sum(
                row["posthoc_same_function_gate"]
                for row in raw["rows"]
            )
            and summary["all_d2_mitm_queries_valid"]
            == all(
                row["same_function_baselines"]["reduced_d2_mitm"][
                    "all_exhaustive_queries_valid"
                ]
                for row in raw["rows"]
            )
            and summary["all_exhaustive_rootless_queries_valid"]
            == all(
                row["exhaustive_queries"]["all_queries_valid"]
                for row in raw["rows"]
            )
            and summary["all_positive_queries_valid"]
            == all(
                all(query["valid"] for query in row["positive_queries"])
                for row in raw["rows"]
            )
            and summary["all_negative_queries_valid"]
            == all(
                all(query["valid"] for query in row["negative_queries"])
                for row in raw["rows"]
            )
        ),
    }


def core_checks(
    raw: dict[str, Any], typed: dict[str, Any], typed_path: Path
) -> tuple[dict[str, bool], list[dict[str, Any]]]:
    instance = typed["instances"][0]
    by_family = {
        family["family"]: family for family in instance["families"]
    }
    row_receipts = [
        verify_row(row, instance["curve"], by_family[row["family"]])
        for row in raw["rows"]
        if row.get("family") in by_family
    ]
    top = {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "factored-divided-power-dag-v1"
        ),
        "claim_status": raw.get("claim_status")
        == [
            "HYPOTHESIS",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "producer_hash": raw["source"]["generator_sha256"]
        == file_hash(PRODUCER_PATH),
        "input_hash": raw["source"]["typed_input_sha256"]
        == file_hash(typed_path),
        "configured_input_path": (
            Path(raw["config"]["typed_input"]).resolve()
            == typed_path.resolve()
        ),
        "telemetry_nonnegative": (
            raw["peak_rss_bytes"] >= 0
            and raw["total_wall_seconds"] >= 0
            and all(
                row["peak_rss_bytes_after_cell"] >= 0
                for row in raw["rows"]
            )
        ),
        **envelope(raw, typed),
        "all_rows_reconstructed": (
            len(row_receipts) == len(raw["rows"])
            and all(receipt["valid"] for receipt in row_receipts)
        ),
        "relation_rank_false": raw["summary"][
            "relation_rank_tested"
        ]
        is False,
        "promotion_gate_false": raw["summary"][
            "algorithm_promotion_gate"
        ]
        is False,
        "breakthrough_claim_false": raw["summary"][
            "breakthrough_claim"
        ]
        is False,
    }
    return top, row_receipts


def accepted(
    raw: dict[str, Any], typed: dict[str, Any], typed_path: Path
) -> bool:
    try:
        top, _ = core_checks(raw, typed, typed_path)
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return all(top.values())


def mutation_suite(
    raw: dict[str, Any], typed: dict[str, Any], typed_path: Path
) -> dict[str, bool]:
    candidates: dict[str, dict[str, Any]] = {}
    dropped = copy.deepcopy(raw)
    dropped["rows"].pop()
    candidates["dropped_row"] = dropped
    duplicate = copy.deepcopy(raw)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    candidates["duplicate_row"] = duplicate
    summary = copy.deepcopy(raw)
    summary["summary"]["signal_cells"] += 1
    candidates["summary"] = summary
    node = copy.deepcopy(raw)
    node["rows"][0]["nodes"][0]["degrees"]["4"]["cycle_digest"] = "0" * 64
    candidates["node_cycle_digest"] = node
    route = copy.deepcopy(raw)
    route["rows"][0]["root_cycle"][0]["first_route"][0] += 1
    candidates["root_route"] = route
    target = copy.deepcopy(raw)
    target["rows"][0]["positive_queries"][0]["target"] = None
    candidates["query_target"] = target
    operations = copy.deepcopy(raw)
    operations["rows"][0]["positive_queries"][0]["operations"][
        "point_scans"
    ] += 1
    candidates["query_operations"] = operations
    retained = copy.deepcopy(raw)
    retained["rows"][0]["retained_records"] += 1
    candidates["retained_metric"] = retained
    build_peak = copy.deepcopy(raw)
    build_peak["rows"][0]["build_peak_cycle_records"] += 1
    candidates["build_peak_metric"] = build_peak
    root_prefilter = copy.deepcopy(raw)
    root_prefilter["rows"][0]["root_cycle_discarded_for_query"] = False
    candidates["root_prefilter_boundary"] = root_prefilter
    baseline = copy.deepcopy(raw)
    baseline["rows"][0]["same_function_baselines"][
        "exact_support_hash"
    ]["logical_words"] += 1
    candidates["same_function_baseline"] = baseline
    serialized = copy.deepcopy(raw)
    serialized["rows"][0]["retained_canonical_json_bytes"] += 1
    candidates["serialized_state"] = serialized
    build_serialized = copy.deepcopy(raw)
    build_serialized["rows"][0][
        "build_peak_canonical_json_bytes"
    ] += 1
    candidates["build_serialized_state"] = build_serialized
    exhaustive = copy.deepcopy(raw)
    exhaustive["rows"][0]["exhaustive_queries"][
        "receipt_digest"
    ] = "0" * 64
    candidates["exhaustive_query_digest"] = exhaustive
    generic = copy.deepcopy(raw)
    generic["rows"][0]["generic_numerical_references"][
        "commensurate_with_logical_words"
    ] = True
    candidates["generic_boundary"] = generic
    source = copy.deepcopy(raw)
    source["source"]["generator_sha256"] = "0" * 64
    candidates["source_hash"] = source
    configured_path = copy.deepcopy(raw)
    configured_path["config"]["typed_input"] = "/tmp/false-input.json"
    candidates["configured_input_path"] = configured_path
    telemetry = copy.deepcopy(raw)
    telemetry["total_wall_seconds"] = -1
    candidates["top_telemetry"] = telemetry
    row_telemetry = copy.deepcopy(raw)
    row_telemetry["rows"][0]["peak_rss_bytes_after_cell"] = -1
    candidates["row_telemetry"] = row_telemetry
    promotion = copy.deepcopy(raw)
    promotion["summary"]["algorithm_promotion_gate"] = True
    candidates["promotion_gate"] = promotion
    return {
        name: not accepted(candidate, typed, typed_path)
        for name, candidate in candidates.items()
    }


def verify(
    raw_path: Path, typed_override: Path | None
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    top, row_receipts = core_checks(raw, typed, typed_path)
    mutations = mutation_suite(raw, typed, typed_path)
    valid = all(top.values()) and all(mutations.values())
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "factored-divided-power-dag-v1-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "producer_sha256": file_hash(PRODUCER_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "top_checks": top,
        "mutation_rejections": mutations,
        "row_receipts": row_receipts,
        "valid": valid,
        "boundary": (
            "Independent balanced-tree, coefficient, route, deterministic "
            "query, and operation-count replay for fixed toy D4 membership. "
            "No A+4R relation rank, target descent, or exponent improvement "
            "is certified."
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

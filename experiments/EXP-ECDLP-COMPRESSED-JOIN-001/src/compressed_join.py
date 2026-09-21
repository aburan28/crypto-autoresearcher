#!/usr/bin/env python3
"""Coordinate-routed compressed joins for authorized toy ECDLP research."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


PROTOCOL = "EXP-ECDLP-COMPRESSED-JOIN-001-development-v1"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
BASE_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-FIXED-COMPILER-001"
    / "src"
    / "fixed_curve_compiler.py"
)
VERIFIER_PATH = SCRIPT_PATH.with_name("verify_compressed_join.py")
CONTRACT_PATH = EXPERIMENT_ROOT / "contract.md"
HYPOTHESIS_PATH = EXPERIMENT_ROOT / "hypothesis.json"
THEORY_PATH = EXPERIMENT_ROOT / "theory.md"
LITERATURE_PATH = REPO_ROOT / "notes" / "compressed_join_literature_addendum_20260717.md"

CANDIDATE_ROUTERS = ["x_mod", "x_interval", "xy_linear_mod", "legendre_vector"]
NEGATIVE_CONTROL = "random_label"
POSITIVE_CONTROL = "scalar_interval"
ALL_ROUTERS = CANDIDATE_ROUTERS + [NEGATIVE_CONTROL, POSITIVE_CONTROL]
SUPPORTED_FAMILIES = [
    "x_interval",
    "square_map",
    "rational_union",
    "random_x",
    "random_scalar",
]
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [3572001, 3572011, 3572029],
    "families": SUPPORTED_FAMILIES,
    "routers": ALL_ROUTERS,
    "bucket_counts": [4, 8, 16, 32, 64],
    "occupancy_lambda": 0.5,
    "query_samples": 16,
    "descent_challenges": 4,
    "descent_attempt_limit": 32,
    "rho_trials": 2,
}


def load_base_module() -> Any:
    spec = importlib.util.spec_from_file_location("compressed_join_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fixed-compiler source: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base_module()
Curve = BASE.Curve
Ops = BASE.Ops
Point = tuple[int, int] | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json_bytes(value)).hexdigest()


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def exact_int_list(values: Iterable[int], label: str, minimum: int) -> list[int]:
    result = [
        exact_int(value, f"{label}[{index}]", minimum)
        for index, value in enumerate(values)
    ]
    if not result:
        raise ValueError(f"{label} must not be empty")
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def point_bytes(point: Point, p: int) -> bytes:
    width = max(1, math.ceil(p.bit_length() / 8))
    if point is None:
        return b"\x00" + b"\x00" * (2 * width)
    return b"\x01" + point[0].to_bytes(width, "big") + point[1].to_bytes(width, "big")


def sum_ops(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {key: sum(record.get(key, 0) for record in records) for key in sorted(keys)}


def mean_or_zero(values: list[int | float]) -> float:
    return statistics.fmean(values) if values else 0.0


def fit_log_slope(rows: list[tuple[int, float]]) -> float | None:
    if len(rows) < 3 or any(value <= 0 for _, value in rows):
        return None
    xs = [math.log(q) for q, _ in rows]
    ys = [math.log(value) for _, value in rows]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


@dataclass
class D2Support:
    points: list[Point]
    witnesses: list[tuple[int, int]]
    multiplicities: list[int]
    point_to_index: dict[Point, int]
    build_ops: Ops
    attempts: int


@dataclass
class D4Support:
    points: list[Point]
    point_to_pair: dict[Point, tuple[int, int]]
    pair_records: list[tuple[int, int, Point]]
    multiplicities: dict[Point, int]
    build_ops: Ops


@dataclass
class RouterAdvice:
    name: str
    bucket_count: int
    point_buckets: list[int]
    bucket_contents: dict[int, list[int]]
    routes: dict[tuple[int, int], tuple[int, ...]]
    record: dict[str, Any]
    scalar_oracle_required: bool


def build_d2(curve: Any, points: list[Point]) -> D2Support:
    ops = Ops()
    witness_by_point: dict[Point, tuple[int, int]] = {}
    multiplicity_by_point: dict[Point, int] = {}
    attempts = 0
    for left in range(len(points)):
        for right in range(left, len(points)):
            attempts += 1
            total = curve.add(points[left], points[right], ops)
            multiplicity_by_point[total] = multiplicity_by_point.get(total, 0) + 1
            witness_by_point.setdefault(total, (left, right))
    ordered_points = sorted(witness_by_point, key=BASE.point_sort_key)
    witnesses = [witness_by_point[point] for point in ordered_points]
    multiplicities = [multiplicity_by_point[point] for point in ordered_points]
    return D2Support(
        points=ordered_points,
        witnesses=witnesses,
        multiplicities=multiplicities,
        point_to_index={point: index for index, point in enumerate(ordered_points)},
        build_ops=ops,
        attempts=attempts,
    )


def build_d4(curve: Any, d2: D2Support) -> D4Support:
    ops = Ops()
    point_to_pair: dict[Point, tuple[int, int]] = {}
    multiplicities: dict[Point, int] = {}
    pair_records: list[tuple[int, int, Point]] = []
    for left in range(len(d2.points)):
        for right in range(left, len(d2.points)):
            total = curve.add(d2.points[left], d2.points[right], ops)
            pair_records.append((left, right, total))
            multiplicities[total] = multiplicities.get(total, 0) + 1
            point_to_pair.setdefault(total, (left, right))
    return D4Support(
        points=sorted(point_to_pair, key=BASE.point_sort_key),
        point_to_pair=point_to_pair,
        pair_records=pair_records,
        multiplicities=multiplicities,
        build_ops=ops,
    )


def build_d5_support(
    curve: Any,
    factor_points: list[Point],
    d4: D4Support,
) -> tuple[dict[Point, tuple[int, int, int]], Ops]:
    ops = Ops()
    support: dict[Point, tuple[int, int, int]] = {}
    for d4_point in d4.points:
        left, right = d4.point_to_pair[d4_point]
        for final_index, final_point in enumerate(factor_points):
            total = curve.add(d4_point, final_point, ops)
            support.setdefault(total, (left, right, final_index))
    return support, ops


def enumerate_scalar_index(
    curve: Any,
    q: int,
    generator: Point,
) -> tuple[dict[Point, int], Ops]:
    """Build an exhaustive toy DLP table used only by private audit controls."""
    ops = Ops()
    result: dict[Point, int] = {}
    current: Point = None
    for scalar in range(q):
        if current in result:
            raise AssertionError("generator repeated before the prime group order")
        result[current] = scalar
        current = curve.add(current, generator, ops)
    if current is not None or len(result) != q:
        raise AssertionError("exhaustive scalar index did not close at group order")
    return result, ops


def router_bucket(
    name: str,
    point: Point,
    bucket_count: int,
    curve: Any,
    q: int,
    seed: int,
    scalar_index: dict[Point, int] | None = None,
) -> int:
    if name not in ALL_ROUTERS:
        raise ValueError(f"unsupported router: {name}")
    if not is_power_of_two(bucket_count):
        raise ValueError("bucket_count must be a power of two")
    if name == POSITIVE_CONTROL:
        if scalar_index is None:
            raise ValueError("scalar_interval requires a private audit scalar index")
        return scalar_index[point] * bucket_count // q
    if name == NEGATIVE_CONTROL:
        digest = hashlib.sha256(
            seed.to_bytes(16, "big", signed=False)
            + bucket_count.to_bytes(8, "big")
            + point_bytes(point, curve.p)
        ).digest()
        return int.from_bytes(digest[:8], "big") % bucket_count
    if point is None:
        return 0
    x, y = point
    if name == "x_mod":
        return (x + 1) % bucket_count
    if name == "x_interval":
        return min(bucket_count - 1, (x + 1) * bucket_count // (curve.p + 1))
    if name == "xy_linear_mod":
        coefficient = 2 * (seed % max(1, curve.p // 2)) + 1
        return (x + coefficient * y + 1) % bucket_count
    if name == "legendre_vector":
        bits = bucket_count.bit_length() - 1
        value = 0
        for index in range(bits):
            offset = (seed + index * 0x9E3779B1) % curve.p
            symbol = pow((x + offset) % curve.p, (curve.p - 1) // 2, curve.p)
            value |= int(symbol == 1) << index
        return value
    raise AssertionError("unreachable router")


def shannon_entropy(counts: Iterable[int]) -> float:
    values = [value for value in counts if value > 0]
    total = sum(values)
    if total == 0:
        return 0.0
    return -sum((value / total) * math.log2(value / total) for value in values)


def compile_router(
    curve: Any,
    q: int,
    factor_points: list[Point],
    d2: D2Support,
    d4: D4Support,
    name: str,
    bucket_count: int,
    seed: int,
    scalar_index: dict[Point, int] | None,
) -> RouterAdvice:
    point_buckets = [
        router_bucket(name, point, bucket_count, curve, q, seed, scalar_index)
        for point in d2.points
    ]
    bucket_contents: dict[int, list[int]] = {index: [] for index in range(bucket_count)}
    for point_index, bucket in enumerate(point_buckets):
        bucket_contents[bucket].append(point_index)

    reverse: dict[tuple[int, int], set[int]] = {}
    forward_counts: dict[tuple[int, int], dict[int, int]] = {}
    route_coverage = 0
    for left, right, output in d4.pair_records:
        output_bucket = router_bucket(
            name, output, bucket_count, curve, q, seed, scalar_index
        )
        orientations = [(left, right)]
        if left != right:
            orientations.append((right, left))
        for oriented_left, oriented_right in orientations:
            left_bucket = point_buckets[oriented_left]
            right_bucket = point_buckets[oriented_right]
            reverse.setdefault((output_bucket, left_bucket), set()).add(right_bucket)
            output_counts = forward_counts.setdefault(
                (left_bucket, right_bucket), {}
            )
            output_counts[output_bucket] = output_counts.get(output_bucket, 0) + 1
            route_coverage += 1
    routes = {key: tuple(sorted(values)) for key, values in reverse.items()}

    for left, right, output in d4.pair_records:
        output_bucket = router_bucket(
            name, output, bucket_count, curve, q, seed, scalar_index
        )
        if point_buckets[right] not in routes[(output_bucket, point_buckets[left])]:
            raise AssertionError("router omitted a forward D4 pair")
        if point_buckets[left] not in routes[(output_bucket, point_buckets[right])]:
            raise AssertionError("router omitted a reverse D4 pair")

    ordered_pair_count = len(d2.points) ** 2
    weighted_entropy = sum(
        sum(output_counts.values()) * shannon_entropy(output_counts.values())
        for output_counts in forward_counts.values()
    ) / ordered_pair_count
    forward_widths = [len(values) for values in forward_counts.values()]
    reverse_widths = [len(values) for values in routes.values()]
    route_triples = sum(reverse_widths)

    point_bits = 1 + 2 * curve.p.bit_length()
    factor_index_bits = max(1, (len(factor_points) - 1).bit_length())
    d2_index_bits = max(1, (len(d2.points) - 1).bit_length())
    bucket_bits = max(1, (bucket_count - 1).bit_length())
    directory_bits = (bucket_count + 1) * max(1, len(d2.points).bit_length())
    hash_parameter_bits = 128
    payload_bits = (
        len(factor_points) * point_bits
        + len(d2.points) * (point_bits + 2 * factor_index_bits + bucket_bits)
        + directory_bits
        + route_triples * 3 * bucket_bits
        + hash_parameter_bits
    )
    artifact = {
        "factor_points": [BASE.point_json(point) for point in factor_points],
        "d2": [
            {
                "point": BASE.point_json(point),
                "witness": list(witness),
                "bucket": bucket,
            }
            for point, witness, bucket in zip(
                d2.points, d2.witnesses, point_buckets
            )
        ],
        "routes": [
            [output_bucket, left_bucket, right_bucket]
            for (output_bucket, left_bucket), right_buckets in sorted(routes.items())
            for right_bucket in right_buckets
        ],
    }
    record = {
        "router": name,
        "eligibility": (
            "positive_control_only" if name == POSITIVE_CONTROL else "candidate_or_null"
        ),
        "bucket_count": bucket_count,
        "occupied_d2_buckets": sum(bool(values) for values in bucket_contents.values()),
        "maximum_d2_bucket_size": max(len(values) for values in bucket_contents.values()),
        "mean_occupied_d2_bucket_size": mean_or_zero(
            [len(values) for values in bucket_contents.values() if values]
        ),
        "occupied_forward_bucket_pairs": len(forward_counts),
        "occupied_reverse_route_keys": len(routes),
        "distinct_route_triples": route_triples,
        "route_coverage_oriented_pairs": route_coverage,
        "expected_oriented_pairs": ordered_pair_count,
        "average_forward_output_width": mean_or_zero(forward_widths),
        "maximum_forward_output_width": max(forward_widths),
        "average_reverse_right_bucket_width": mean_or_zero(reverse_widths),
        "maximum_reverse_right_bucket_width": max(reverse_widths),
        "conditional_output_entropy_bits": weighted_entropy,
        "normalized_conditional_output_entropy": (
            weighted_entropy / math.log2(bucket_count) if bucket_count > 1 else 0.0
        ),
        "payload_bit_lower_estimate": payload_bits,
        "payload_model": (
            "factor points, unique D2 points and pair witnesses, bucket labels and "
            "directory, exact fixed-width route triples, and public hash parameters"
        ),
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": BASE.deep_size(
            {
                "points": d2.points,
                "witnesses": d2.witnesses,
                "buckets": bucket_contents,
                "routes": routes,
            }
        ),
        "route_digest": stable_digest(artifact["routes"]),
        "artifact_digest": stable_digest(artifact),
        "first_routes": artifact["routes"][:8],
        "scalar_oracle_required": name == POSITIVE_CONTROL,
        "hidden_scalar_metadata_emitted": False,
    }
    return RouterAdvice(
        name=name,
        bucket_count=bucket_count,
        point_buckets=point_buckets,
        bucket_contents=bucket_contents,
        routes=routes,
        record=record,
        scalar_oracle_required=name == POSITIVE_CONTROL,
    )


def query_d4(
    curve: Any,
    q: int,
    target: Point,
    d2: D2Support,
    router: RouterAdvice,
    seed: int,
    scalar_index: dict[Point, int] | None,
) -> dict[str, Any]:
    output_bucket = router_bucket(
        router.name,
        target,
        router.bucket_count,
        curve,
        q,
        seed,
        scalar_index,
    )
    ops = Ops()
    route_probes = 0
    bucket_reads = 0
    point_reads = 0
    witness: tuple[int, int, int, int] | None = None
    d2_pair: tuple[int, int] | None = None
    for left, left_point in enumerate(d2.points):
        route_probes += 1
        right_buckets = router.routes.get(
            (output_bucket, router.point_buckets[left]), ()
        )
        for right_bucket in right_buckets:
            bucket_reads += 1
            for right in router.bucket_contents[right_bucket]:
                point_reads += 1
                if curve.add(left_point, d2.points[right], ops) != target:
                    continue
                witness = tuple(sorted(d2.witnesses[left] + d2.witnesses[right]))
                d2_pair = (left, right)
                break
            if witness is not None:
                break
        if witness is not None:
            break
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "d2_pair": list(d2_pair) if d2_pair is not None else None,
        "ops": asdict(ops),
        "route_probes": route_probes,
        "bucket_reads": bucket_reads,
        "point_reads": point_reads,
        "target_bucket": output_bucket,
    }


def query_d5(
    curve: Any,
    q: int,
    target: Point,
    factor_points: list[Point],
    d2: D2Support,
    router: RouterAdvice,
    seed: int,
    scalar_index: dict[Point, int] | None,
) -> dict[str, Any]:
    outer_ops = Ops()
    aggregate_inner_ops = asdict(Ops())
    route_probes = 0
    bucket_reads = 0
    point_reads = 0
    witness: tuple[int, ...] | None = None
    final_index: int | None = None
    for index, final_point in enumerate(factor_points):
        partial_target = curve.add(target, curve.neg(final_point), outer_ops)
        result = query_d4(
            curve,
            q,
            partial_target,
            d2,
            router,
            seed,
            scalar_index,
        )
        aggregate_inner_ops = sum_ops(aggregate_inner_ops, result["ops"])
        route_probes += result["route_probes"]
        bucket_reads += result["bucket_reads"]
        point_reads += result["point_reads"]
        if result["success"]:
            witness = tuple(sorted(tuple(result["witness"]) + (index,)))
            final_index = index
            break
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "final_index": final_index,
        "outer_ops": asdict(outer_ops),
        "inner_ops": aggregate_inner_ops,
        "ops": sum_ops(asdict(outer_ops), aggregate_inner_ops),
        "route_probes": route_probes,
        "bucket_reads": bucket_reads,
        "point_reads": point_reads,
    }


def verify_factor_witness(
    curve: Any,
    factor_points: list[Point],
    witness: list[int] | None,
    target: Point,
) -> tuple[bool, dict[str, int]]:
    if witness is None:
        return False, asdict(Ops())
    ops = Ops()
    recovered: Point = None
    for index in witness:
        recovered = curve.add(recovered, factor_points[index], ops)
    return recovered == target, asdict(ops)


def deterministic_sample(values: list[Point], count: int, seed: int) -> list[Point]:
    if count >= len(values):
        return list(values)
    rng = random.Random(seed)
    return [values[index] for index in rng.sample(range(len(values)), count)]


def run_query_samples(
    curve: Any,
    q: int,
    generator: Point,
    factor_points: list[Point],
    d2: D2Support,
    d4: D4Support,
    d5_support: dict[Point, tuple[int, int, int]],
    router: RouterAdvice,
    router_seed: int,
    sample_seed: int,
    scalar_index: dict[Point, int] | None,
    sample_count: int,
) -> dict[str, Any]:
    d4_targets = deterministic_sample(
        d4.points, sample_count, sample_seed ^ 0x243F6A88
    )
    d5_targets = deterministic_sample(
        sorted(d5_support, key=BASE.point_sort_key),
        sample_count,
        sample_seed ^ 0x85A308D3,
    )
    rng = random.Random(sample_seed ^ 0x13198A2E)
    generation_ops = Ops()
    random_targets = [
        curve.mul(rng.randrange(q), generator, generation_ops)
        for _ in range(sample_count)
    ]

    def run_d4(targets: list[Point]) -> tuple[list[dict[str, Any]], dict[str, int]]:
        records = []
        audit_ops = asdict(Ops())
        for target in targets:
            result = query_d4(
                curve, q, target, d2, router, router_seed, scalar_index
            )
            verified, verify_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            audit_ops = sum_ops(audit_ops, verify_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records.append(result)
        return records, audit_ops

    def run_d5(targets: list[Point]) -> tuple[list[dict[str, Any]], dict[str, int]]:
        records = []
        audit_ops = asdict(Ops())
        for target in targets:
            result = query_d5(
                curve,
                q,
                target,
                factor_points,
                d2,
                router,
                router_seed,
                scalar_index,
            )
            verified, verify_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            audit_ops = sum_ops(audit_ops, verify_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records.append(result)
        return records, audit_ops

    supported_d4, d4_audit_ops = run_d4(d4_targets)
    supported_d5, d5_audit_ops = run_d5(d5_targets)
    random_d5, random_audit_ops = run_d5(random_targets)

    def summarize(records: list[dict[str, Any]], require_success: bool) -> dict[str, Any]:
        if require_success and not all(record["success"] for record in records):
            raise AssertionError("router missed a supported target")
        if any(record["success"] and not record["verified"] for record in records):
            raise AssertionError("router returned an invalid factor-base witness")
        return {
            "sample_count": len(records),
            "successes": sum(int(record["success"]) for record in records),
            "all_successes_verified": all(
                not record["success"] or record["verified"] for record in records
            ),
            "average_group_operations": mean_or_zero(
                [record["ops"]["group_operations"] for record in records]
            ),
            "maximum_group_operations": max(
                record["ops"]["group_operations"] for record in records
            ),
            "average_point_reads": mean_or_zero(
                [record["point_reads"] for record in records]
            ),
            "maximum_point_reads": max(record["point_reads"] for record in records),
            "average_route_probes": mean_or_zero(
                [record["route_probes"] for record in records]
            ),
            "records": records,
        }

    return {
        "supported_d4": summarize(supported_d4, True),
        "supported_d5": summarize(supported_d5, True),
        "random_d5": summarize(random_d5, False),
        "random_target_generation_audit_ops": asdict(generation_ops),
        "witness_verification_audit_ops": sum_ops(
            d4_audit_ops, d5_audit_ops, random_audit_ops
        ),
    }


def run_descent_challenges(
    curve: Any,
    q: int,
    generator: Point,
    factor_points: list[Point],
    factor_logs: list[int],
    d2: D2Support,
    router: RouterAdvice,
    router_seed: int,
    scalar_index: dict[Point, int] | None,
    target_seed: int,
    challenge_count: int,
    attempt_limit: int,
) -> dict[str, Any]:
    rng = random.Random(target_seed ^ 0x1F83D9AB)
    challenge_generation_ops = Ops()
    verification_ops = Ops()
    challenges = []
    for challenge_index in range(challenge_count):
        known_scalar = rng.randrange(q)
        target = curve.mul(known_scalar, generator, challenge_generation_ops)
        attempt_rng = random.Random(
            target_seed ^ (challenge_index + 1) * 0x9E3779B1
        )
        attack_ops = asdict(Ops())
        route_probes = 0
        point_reads = 0
        recovered: int | None = None
        witness: list[int] | None = None
        attempts = 0
        for attempt in range(1, attempt_limit + 1):
            attempts = attempt
            offset = attempt_rng.randrange(q)
            randomization_ops = Ops()
            shifted = curve.add(
                target,
                curve.mul(offset, generator, randomization_ops),
                randomization_ops,
            )
            result = query_d5(
                curve,
                q,
                shifted,
                factor_points,
                d2,
                router,
                router_seed,
                scalar_index,
            )
            attack_ops = sum_ops(attack_ops, asdict(randomization_ops), result["ops"])
            route_probes += result["route_probes"]
            point_reads += result["point_reads"]
            if not result["success"]:
                continue
            witness = result["witness"]
            recovered = (sum(factor_logs[index] for index in witness) - offset) % q
            break
        verified = (
            recovered is not None
            and recovered == known_scalar
            and curve.mul(recovered, generator, verification_ops) == target
        )
        challenges.append(
            {
                "challenge_index": challenge_index,
                "target": BASE.point_json(target),
                "known_scalar_private_audit": known_scalar,
                "attempts": attempts,
                "success": recovered is not None,
                "witness": witness,
                "recovered_scalar": recovered,
                "verified": verified,
                "attack_ops": attack_ops,
                "route_probes": route_probes,
                "point_reads": point_reads,
            }
        )
    return {
        "challenge_count": challenge_count,
        "attempt_limit": attempt_limit,
        "challenges": challenges,
        "all_verified": all(challenge["verified"] for challenge in challenges),
        "average_online_group_operations": mean_or_zero(
            [challenge["attack_ops"]["group_operations"] for challenge in challenges]
        ),
        "maximum_online_group_operations": max(
            challenge["attack_ops"]["group_operations"] for challenge in challenges
        ),
        "average_attempts": mean_or_zero(
            [challenge["attempts"] for challenge in challenges]
        ),
        "challenge_generation_audit_ops": asdict(challenge_generation_ops),
        "verification_audit_ops": asdict(verification_ops),
        "factor_logs_source": (
            "private exhaustive toy audit standing in for the independently verified "
            "relation solver retained from EXP-ECDLP-FIXED-COMPILER-001"
        ),
    }


def compile_family(
    curve_record: dict[str, Any],
    family: str,
    factor_size: int,
    family_seed: int,
    target_seed: int,
    routers: list[str],
    bucket_counts: list[int],
    query_samples: int,
    descent_challenges: int,
    descent_attempt_limit: int,
    scalar_index: dict[Point, int],
) -> dict[str, Any]:
    curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    q = curve_record["q"]
    generator = BASE.point_from_json(curve_record["generator"])
    factor_base = BASE.make_factor_base(
        family, curve, q, generator, factor_size, family_seed
    )
    factor_points = [BASE.point_from_json(point) for point in factor_base["points"]]
    factor_logs = [scalar_index[point] for point in factor_points]
    d2 = build_d2(curve, factor_points)
    d4 = build_d4(curve, d2)
    d5_support, d5_ops = build_d5_support(curve, factor_points, d4)

    d2_point_bits = 1 + 2 * curve.p.bit_length()
    factor_index_bits = max(1, (len(factor_points) - 1).bit_length())
    d2_baseline_bits = (
        len(factor_points) * d2_point_bits
        + len(d2.points) * (d2_point_bits + 2 * factor_index_bits)
    )
    brute_pair_worst_group_ops = len(factor_points) * (1 + len(d2.points) ** 2)
    materialized = BASE.compile_four_sum_advice(curve, factor_points, 1)
    if set(materialized.mapping) != set(d4.points):
        raise AssertionError("D2+D2 support differs from direct four-term support")

    rows = []
    for bucket_count in bucket_counts:
        if bucket_count > 2 ** math.ceil(math.log2(max(2, len(d2.points)))):
            continue
        by_router: dict[str, dict[str, Any]] = {}
        for router_index, router_name in enumerate(routers):
            router_seed = (
                family_seed
                ^ bucket_count * 0xA4093822
                ^ router_index * 0x299F31D0
            ) & ((1 << 128) - 1)
            advice = compile_router(
                curve,
                q,
                factor_points,
                d2,
                d4,
                router_name,
                bucket_count,
                router_seed,
                scalar_index if router_name == POSITIVE_CONTROL else None,
            )
            samples = run_query_samples(
                curve,
                q,
                generator,
                factor_points,
                d2,
                d4,
                d5_support,
                advice,
                router_seed,
                target_seed,
                scalar_index if router_name == POSITIVE_CONTROL else None,
                query_samples,
            )
            full_advice_bits = (
                advice.record["payload_bit_lower_estimate"]
                + len(factor_points) * q.bit_length()
            )
            descent = run_descent_challenges(
                curve,
                q,
                generator,
                factor_points,
                factor_logs,
                d2,
                advice,
                router_seed,
                scalar_index if router_name == POSITIVE_CONTROL else None,
                target_seed,
                descent_challenges,
                descent_attempt_limit,
            )
            bsgs = BASE.run_matched_bsgs_preprocessing(
                curve,
                q,
                generator,
                full_advice_bits,
                target_seed,
                descent_challenges,
            )
            worst_case_d5_group_ops = len(factor_points) * (
                1 + len(d2.points) ** 2
            )
            row = {
                "router": router_name,
                "router_seed": router_seed,
                "bucket_count": bucket_count,
                "eligibility": advice.record["eligibility"],
                "advice": advice.record,
                "query_samples": samples,
                "descent": descent,
                "full_online_advice_bits": full_advice_bits,
                "factor_base_log_advice_bits": len(factor_points) * q.bit_length(),
                "worst_case_d5_group_operation_bound": worst_case_d5_group_ops,
                "matched_bsgs": {
                    **bsgs,
                    "candidate_to_bsgs_average_online_group_operation_ratio": (
                        descent["average_online_group_operations"]
                        / bsgs["average_online_group_operations"]
                        if bsgs["average_online_group_operations"]
                        else None
                    ),
                    "candidate_to_bsgs_worst_case_group_operation_ratio": (
                        worst_case_d5_group_ops
                        / bsgs["worst_case_online_group_operation_bound"]
                        if bsgs["worst_case_online_group_operation_bound"]
                        else None
                    ),
                    "candidate_online_dominates_at_equal_advice": (
                        descent["average_online_group_operations"]
                        < bsgs["average_online_group_operations"]
                        and worst_case_d5_group_ops
                        < bsgs["worst_case_online_group_operation_bound"]
                    ),
                },
                "ratios_to_random_label": None,
                "instance_signal_gate_passed": False,
                "routing_gate_passed": False,
                "claim_boundary": (
                    "router preflight only; relation collection cost is inherited, "
                    "not rerun, and no exponent or ECDLP break is claimed"
                ),
            }
            rows.append(row)
            by_router[router_name] = row

        random_row = by_router.get(NEGATIVE_CONTROL)
        if random_row is None:
            raise ValueError("random_label is required at every bucket count")
        scalar_row = by_router.get(POSITIVE_CONTROL)
        scalar_calibration_passed = (
            scalar_row is not None
            and scalar_row["advice"]["average_forward_output_width"]
            < random_row["advice"]["average_forward_output_width"]
        )
        for row in by_router.values():
            random_payload = random_row["advice"]["payload_bit_lower_estimate"]
            random_candidates = random_row["query_samples"]["supported_d5"][
                "average_point_reads"
            ]
            ratios = {
                "route_payload_bits": (
                    row["advice"]["payload_bit_lower_estimate"] / random_payload
                ),
                "route_triples": (
                    row["advice"]["distinct_route_triples"]
                    / random_row["advice"]["distinct_route_triples"]
                ),
                "supported_d4_point_reads": (
                    row["query_samples"]["supported_d4"]["average_point_reads"]
                    / random_row["query_samples"]["supported_d4"]["average_point_reads"]
                ),
                "supported_d5_point_reads": (
                    row["query_samples"]["supported_d5"]["average_point_reads"]
                    / random_candidates
                ),
                "canonical_serialized_bytes": (
                    row["advice"]["canonical_serialized_bytes"]
                    / random_row["advice"]["canonical_serialized_bytes"]
                ),
                "python_deep_bytes": (
                    row["advice"]["python_deep_bytes"]
                    / random_row["advice"]["python_deep_bytes"]
                ),
            }
            row["ratios_to_random_label"] = ratios
            row["scalar_calibration_passed"] = scalar_calibration_passed
            row["instance_signal_gate_passed"] = (
                row["router"] in CANDIDATE_ROUTERS
                and scalar_calibration_passed
                and row["descent"]["all_verified"]
                and ratios["route_payload_bits"] <= 0.8
                and ratios["supported_d4_point_reads"] <= 0.8
                and ratios["supported_d5_point_reads"] <= 0.8
                and ratios["canonical_serialized_bytes"] <= 1.25
                and ratios["python_deep_bytes"] <= 1.25
                and row["matched_bsgs"]["candidate_online_dominates_at_equal_advice"]
            )

    return {
        "family": family,
        "factor_base": factor_base,
        "factor_base_logs_private_audit_digest": stable_digest(factor_logs),
        "factor_base_logs_emitted": False,
        "d2": {
            "support_size": len(d2.points),
            "attempts": d2.attempts,
            "build_ops": asdict(d2.build_ops),
            "maximum_multiplicity": max(d2.multiplicities),
            "mean_multiplicity": statistics.fmean(d2.multiplicities),
            "support_digest": stable_digest(
                [BASE.point_json(point) for point in d2.points]
            ),
            "baseline_payload_bits": d2_baseline_bits,
        },
        "d4": {
            "support_size": len(d4.points),
            "unordered_d2_pair_attempts": len(d4.pair_records),
            "build_ops": asdict(d4.build_ops),
            "maximum_d2_pair_multiplicity": max(d4.multiplicities.values()),
            "mean_d2_pair_multiplicity": statistics.fmean(d4.multiplicities.values()),
            "support_digest": stable_digest(
                [BASE.point_json(point) for point in d4.points]
            ),
        },
        "d5": {
            "support_size": len(d5_support),
            "exact_success_probability": len(d5_support) / q,
            "build_ops": asdict(d5_ops),
            "support_digest": stable_digest(
                [
                    BASE.point_json(point)
                    for point in sorted(d5_support, key=BASE.point_sort_key)
                ]
            ),
        },
        "baselines": {
            "brute_pair_worst_d5_group_operations": brute_pair_worst_group_ops,
            "materialized_d4": materialized.record,
        },
        "rows": rows,
    }


def attach_aggregate_routing(
    instances: list[dict[str, Any]],
    bit_sizes: list[int],
    seeds: list[int],
    bucket_counts: list[int],
) -> dict[str, Any]:
    passing: dict[tuple[str, str, int, int], set[int]] = {}
    for instance in instances:
        bits = instance["curve"]["bits"]
        seed = instance["seed"]
        for family_record in instance["families"]:
            family = family_record["family"]
            for row in family_record["rows"]:
                key = (family, row["router"], row["bucket_count"], bits)
                passing.setdefault(key, set())
                if row["instance_signal_gate_passed"]:
                    passing[key].add(seed)
    promoted: set[tuple[str, str, int]] = set()
    for family in SUPPORTED_FAMILIES:
        for router in CANDIDATE_ROUTERS:
            for bucket_count in bucket_counts:
                if len(seeds) >= 2 and all(
                    len(passing.get((family, router, bucket_count, bits), set())) >= 2
                    for bits in bit_sizes
                ):
                    promoted.add((family, router, bucket_count))
    for instance in instances:
        for family_record in instance["families"]:
            for row in family_record["rows"]:
                row["routing_gate_passed"] = (
                    row["instance_signal_gate_passed"]
                    and (
                        family_record["family"],
                        row["router"],
                        row["bucket_count"],
                    )
                    in promoted
                )
    return {
        "required_passing_seeds_per_size": 2,
        "configured_seed_count": len(seeds),
        "promoted": [
            {"family": family, "router": router, "bucket_count": bucket_count}
            for family, router, bucket_count in sorted(promoted)
        ],
        "passing_seeds": {
            "|".join(map(str, key)): sorted(values)
            for key, values in sorted(passing.items())
            if values
        },
    }


def run_experiment(config: dict[str, Any]) -> dict[str, Any]:
    bit_sizes = exact_int_list(config["bit_sizes"], "bit_sizes", 5)
    seeds = exact_int_list(config["seeds"], "seeds", 0)
    bucket_counts = exact_int_list(config["bucket_counts"], "bucket_counts", 2)
    if any(not is_power_of_two(value) for value in bucket_counts):
        raise ValueError("all bucket counts must be powers of two")
    families = list(config["families"])
    routers = list(config["routers"])
    if not families or len(families) != len(set(families)):
        raise ValueError("families must be nonempty and distinct")
    if not routers or len(routers) != len(set(routers)):
        raise ValueError("routers must be nonempty and distinct")
    if any(family not in SUPPORTED_FAMILIES for family in families):
        raise ValueError("unsupported factor-base family")
    if any(router not in ALL_ROUTERS for router in routers):
        raise ValueError("unsupported router")
    if NEGATIVE_CONTROL not in routers or POSITIVE_CONTROL not in routers:
        raise ValueError("random_label and scalar_interval controls are mandatory")
    occupancy_lambda = BASE.exact_probability(
        config["occupancy_lambda"], "occupancy_lambda"
    )
    query_samples = exact_int(config["query_samples"], "query_samples", 1)
    descent_challenges = exact_int(
        config["descent_challenges"], "descent_challenges", 1
    )
    descent_attempt_limit = exact_int(
        config["descent_attempt_limit"], "descent_attempt_limit", 1
    )
    rho_trials = exact_int(config["rho_trials"], "rho_trials", 1)

    instances = []
    used_primes: set[int] = set()
    for bits in bit_sizes:
        for seed in seeds:
            curve_record = BASE.generate_clean_curve(bits, seed + bits * 1009)
            if curve_record["p"] in used_primes:
                raise AssertionError("field modulus repeated across scheduled curves")
            used_primes.add(curve_record["p"])
            curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
            generator = BASE.point_from_json(curve_record["generator"])
            scalar_index, scalar_audit_ops = enumerate_scalar_index(
                curve, curve_record["q"], generator
            )
            factor_size = BASE.choose_factor_base_size(
                curve_record["q"], occupancy_lambda
            )
            target_seed = seed ^ bits * 0x7FEB352D
            family_records = []
            for family_index, family in enumerate(families):
                family_seed = (
                    seed ^ bits * 0x45D9F3B ^ family_index * 0x9E3779B1
                )
                family_records.append(
                    compile_family(
                        curve_record,
                        family,
                        factor_size,
                        family_seed,
                        target_seed,
                        routers,
                        bucket_counts,
                        query_samples,
                        descent_challenges,
                        descent_attempt_limit,
                        scalar_index,
                    )
                )
            rho = BASE.run_rho_baseline(curve_record, seed, rho_trials)
            instances.append(
                {
                    "seed": seed,
                    "curve": curve_record,
                    "factor_base_size": factor_size,
                    "target_seed": target_seed,
                    "scalar_index_private_audit_ops": asdict(scalar_audit_ops),
                    "scalar_index_emitted": False,
                    "families": family_records,
                    "rho": rho,
                }
            )

    routing_summary = attach_aggregate_routing(
        instances, bit_sizes, seeds, bucket_counts
    )
    slopes: dict[str, Any] = {}
    for family in families:
        slopes[family] = {}
        for router in routers:
            slopes[family][router] = {}
            for bucket_count in bucket_counts:
                selected = [
                    (instance["curve"]["q"], row)
                    for instance in instances
                    for family_record in instance["families"]
                    if family_record["family"] == family
                    for row in family_record["rows"]
                    if row["router"] == router
                    and row["bucket_count"] == bucket_count
                ]
                slopes[family][router][str(bucket_count)] = {
                    "route_payload_bits": fit_log_slope(
                        [
                            (q, row["advice"]["payload_bit_lower_estimate"])
                            for q, row in selected
                        ]
                    ),
                    "route_triples": fit_log_slope(
                        [
                            (q, row["advice"]["distinct_route_triples"])
                            for q, row in selected
                        ]
                    ),
                    "supported_d5_group_operations": fit_log_slope(
                        [
                            (
                                q,
                                row["query_samples"]["supported_d5"][
                                    "average_group_operations"
                                ],
                            )
                            for q, row in selected
                        ]
                    ),
                    "descent_group_operations": fit_log_slope(
                        [
                            (q, row["descent"]["average_online_group_operations"])
                            for q, row in selected
                        ]
                    ),
                }

    frozen = config == FROZEN_CONFIG
    source_hashes = {
        "compressed_join_sha256": sha256_file(SCRIPT_PATH),
        "compressed_join_verifier_sha256": sha256_file(VERIFIER_PATH),
        "fixed_curve_compiler_sha256": sha256_file(BASE_PATH),
        "coordinate_energy_sha256": sha256_file(BASE.ENERGY_PATH),
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "hypothesis_sha256": sha256_file(HYPOTHESIS_PATH),
        "theory_sha256": sha256_file(THEORY_PATH),
        "literature_sha256": sha256_file(LITERATURE_PATH),
    }
    return {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "configuration": config,
        "configuration_is_frozen": frozen,
        "development_only": not frozen,
        "source_hashes": source_hashes,
        "instances": instances,
        "exploratory_slopes": slopes,
        "routing_summary": routing_summary,
        "routing_rows": [
            {
                "curve_id": instance["curve"]["id"],
                "family": family_record["family"],
                "router": row["router"],
                "bucket_count": row["bucket_count"],
            }
            for instance in instances
            for family_record in instance["families"]
            for row in family_record["rows"]
            if row["routing_gate_passed"]
        ],
        "global_controls": {
            "all_curves_clean": all(
                instance["curve"]["trace"] not in (0, 1)
                and instance["curve"]["j_invariant"]
                not in (0, 1728 % instance["curve"]["p"])
                for instance in instances
            ),
            "all_fields_distinct": len(used_primes) == len(instances),
            "all_rho_verified": all(instance["rho"]["all_verified"] for instance in instances),
            "scalar_index_not_emitted": all(
                not instance["scalar_index_emitted"] for instance in instances
            ),
            "factor_logs_not_emitted": all(
                not family_record["factor_base_logs_emitted"]
                for instance in instances
                for family_record in instance["families"]
            ),
            "controls_present": NEGATIVE_CONTROL in routers and POSITIVE_CONTROL in routers,
        },
        "interpretation": {
            "theorem": (
                "Direct exact routing through a smaller group quotient is unavailable "
                "for a prime-order subgroup; nonlinear coordinate routing remains open."
            ),
            "positive_result": (
                "A routing row would justify restoring the complete relation pipeline "
                "on a larger replicated experiment, not an ECDLP-break claim."
            ),
            "negative_result": (
                "No routing row narrows only the tested features, factor bases, bucket "
                "counts, and toy regime."
            ),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-sizes", type=int, nargs="+", default=FROZEN_CONFIG["bit_sizes"])
    parser.add_argument("--seeds", type=int, nargs="+", default=FROZEN_CONFIG["seeds"])
    parser.add_argument("--families", nargs="+", default=FROZEN_CONFIG["families"])
    parser.add_argument("--routers", nargs="+", default=FROZEN_CONFIG["routers"])
    parser.add_argument(
        "--bucket-counts", type=int, nargs="+", default=FROZEN_CONFIG["bucket_counts"]
    )
    parser.add_argument(
        "--occupancy-lambda", type=float, default=FROZEN_CONFIG["occupancy_lambda"]
    )
    parser.add_argument("--query-samples", type=int, default=FROZEN_CONFIG["query_samples"])
    parser.add_argument(
        "--descent-challenges", type=int, default=FROZEN_CONFIG["descent_challenges"]
    )
    parser.add_argument(
        "--descent-attempt-limit", type=int, default=FROZEN_CONFIG["descent_attempt_limit"]
    )
    parser.add_argument("--rho-trials", type=int, default=FROZEN_CONFIG["rho_trials"])
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = {
        "bit_sizes": args.bit_sizes,
        "seeds": args.seeds,
        "families": args.families,
        "routers": args.routers,
        "bucket_counts": args.bucket_counts,
        "occupancy_lambda": args.occupancy_lambda,
        "query_samples": args.query_samples,
        "descent_challenges": args.descent_challenges,
        "descent_attempt_limit": args.descent_attempt_limit,
        "rho_trials": args.rho_trials,
    }
    result = run_experiment(config)
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

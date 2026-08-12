#!/usr/bin/env python3
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
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()
RECURSIVE_SOURCE_PATH = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)


def sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_recursive_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "recursive_expansion_coordinate_profile", RECURSIVE_SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {RECURSIVE_SOURCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RECURSIVE = load_recursive_module()
ENERGY = RECURSIVE.ENERGY
Curve = RECURSIVE.Curve
Ops = RECURSIVE.Ops


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    seen = seen or set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(
            deep_size(key, seen) + deep_size(item, seen)
            for key, item in value.items()
        )
    elif isinstance(value, (list, tuple, set, frozenset, Counter)):
        size += sum(deep_size(item, seen) for item in value)
    return size


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def signed_formal_class_count(fiber_count: int, depth: int) -> int:
    exact_int(fiber_count, "fiber_count", 1)
    exact_int(depth, "depth", 1)
    total = 1 if depth % 2 == 0 else 0
    for l1_norm in range(depth % 2 or 2, depth + 1, 2):
        for support_size in range(1, min(fiber_count, l1_norm) + 1):
            total += (
                (2**support_size)
                * math.comb(fiber_count, support_size)
                * math.comb(l1_norm - 1, support_size - 1)
            )
    return total


def formal_class_count(
    factor_base_size: int, depth: int, symmetry_mode: str
) -> int:
    if symmetry_mode == "sign_canonical":
        return math.comb(factor_base_size + depth - 1, depth)
    if symmetry_mode == "sign_complete":
        if factor_base_size % 2:
            raise ValueError("sign-complete factor-base size must be even")
        return signed_formal_class_count(factor_base_size // 2, depth)
    raise ValueError(f"unsupported symmetry mode: {symmetry_mode}")


def choose_factor_base_size(
    q: int, depth: int, occupancy_lambda: float, symmetry_mode: str
) -> int:
    size = 2
    while (
        formal_class_count(size, depth, symmetry_mode) / q
        < occupancy_lambda
    ):
        size += 2
    return size


def positive_compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for suffix in positive_compositions(total - first, parts - 1):
            yield (first,) + suffix


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        raise ValueError("percentile requires a nonempty list")
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def fit_exponent(points: list[tuple[int, float]]) -> float | None:
    grouped: dict[int, list[float]] = {}
    for q, cost in points:
        if q > 1 and cost > 0:
            grouped.setdefault(q, []).append(cost)
    usable = sorted(
        (q, statistics.median(costs)) for q, costs in grouped.items()
    )
    if len(usable) < 3:
        return None
    xs = [math.log2(q) for q, _ in usable]
    ys = [math.log2(cost) for _, cost in usable]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        return None
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / denominator


def curve_j_invariant(curve_record: dict[str, Any]) -> int:
    p = curve_record["p"]
    numerator = 1728 * 4 * pow(curve_record["a"], 3, p)
    denominator = (
        4 * pow(curve_record["a"], 3, p)
        + 27 * pow(curve_record["b"], 2, p)
    ) % p
    return numerator * pow(denominator, -1, p) % p


def generate_admissible_curve(bits: int, seed: int) -> dict[str, Any]:
    for retry in range(32):
        curve_record = RECURSIVE.generate_prime_order_curve(
            bits, seed + retry * 1_000_003
        )
        j_invariant = curve_j_invariant(curve_record)
        if curve_record["trace"] in (0, 1):
            continue
        if j_invariant in (0, 1728 % curve_record["p"]):
            continue
        curve_record["j_invariant"] = j_invariant
        curve_record["admissibility_retry"] = retry
        curve_record["special_case_exclusions"] = {
            "anomalous_trace_1": True,
            "trace_zero": True,
            "j_0": True,
            "j_1728": True,
            "non_prime_order": True,
            "nontrivial_cofactor": True,
        }
        return curve_record
    raise RuntimeError(f"admissible curve search exhausted at {bits} bits")


def subgroup_log_census(
    curve: Any, q: int, generator: Point
) -> tuple[dict[Point, int], dict[str, Any]]:
    point_to_scalar: dict[Point, int] = {}
    point: Point = None
    ops = Ops()
    for scalar in range(q):
        if point in point_to_scalar:
            raise AssertionError("subgroup census repeated before q")
        point_to_scalar[point] = scalar
        point = curve.add(point, generator, ops)
    if point is not None or len(point_to_scalar) != q:
        raise AssertionError("subgroup census did not close at q")
    return point_to_scalar, {
        "classification": "DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE",
        "entries": len(point_to_scalar),
        "deep_bytes": deep_size(point_to_scalar),
        "ops": asdict(ops),
    }


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def factor_base_scalars(
    factor_base: dict[str, Any], point_to_scalar: dict[Point, int]
) -> list[int]:
    scalars = [
        point_to_scalar[point_from_json(point)] for point in factor_base["points"]
    ]
    if len(set(scalars)) != len(scalars):
        raise AssertionError("factor base contains duplicate subgroup points")
    return scalars


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def factor_base_digest(factor_base: dict[str, Any]) -> str:
    return canonical_json_sha256(factor_base)


def make_hash_ranked_x_factor_base(
    curve: Any,
    q: int,
    size: int,
    seed: int,
    symmetry_mode: str,
) -> dict[str, Any]:
    if size % 2:
        raise ValueError("hash-ranked x factor-base size must be even")
    fiber_count = size // 2 if symmetry_mode == "sign_complete" else size
    ranked_x = sorted(
        range(curve.p),
        key=lambda x: hashlib.sha256(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|SOURCE-PRF-X|"
                f"{seed}|{x}"
            ).encode("ascii")
        ).digest(),
    )
    ops = Ops()
    diagnostics = {
        "x_candidates": 0,
        "square_root_tests": 0,
        "subgroup_tests": 0,
    }
    fibers = []
    for rank, x in enumerate(ranked_x):
        point = ENERGY.point_for_x(curve, q, x, ops, diagnostics)
        if point is None:
            continue
        pair = ENERGY.canonical_fiber(curve, point)
        fibers.append(
            {
                "points": [point_json(pair[0]), point_json(pair[1])],
                "source": {
                    "kind": "source_prf_x",
                    "rank": rank,
                    "x": x,
                },
            }
        )
        if len(fibers) == fiber_count:
            break
    if len(fibers) != fiber_count:
        raise RuntimeError("source-PRF x generation exhausted")
    points = (
        [fiber["points"][0] for fiber in fibers]
        if symmetry_mode == "sign_canonical"
        else [point for fiber in fibers for point in fiber["points"]]
    )
    return {
        "name": "source_prf_x",
        "symmetry_mode": symmetry_mode,
        "size": size,
        "points": points,
        "fibers": fibers,
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
        "raw_sign_complete_size": 2 * fiber_count,
    }


def make_public_factor_base(
    family: str,
    symmetry_mode: str,
    curve: Any,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    if family == "source_prf_x":
        return make_hash_ranked_x_factor_base(
            curve, q, size, seed, symmetry_mode
        )
    return RECURSIVE.make_factor_base(
        family, symmetry_mode, curve, q, generator, size, seed
    )


def build_point_levels(
    curve: Any, factor_points: list[Point], maximum_depth: int
) -> dict[str, Any]:
    levels: list[dict[Point, tuple[int, ...]]] = [{None: ()}]
    ordered_counts: list[Counter[Point]] = [Counter({None: 1})]
    profiles = []
    ops_by_depth = []
    for depth in range(1, maximum_depth + 1):
        ops = Ops()
        witnesses: dict[Point, tuple[int, ...]] = {}
        counts: Counter[Point] = Counter()
        previous_witnesses = levels[-1]
        previous_counts = ordered_counts[-1]
        for partial in sorted(previous_witnesses, key=point_sort_key):
            prefix = previous_witnesses[partial]
            multiplicity = previous_counts[partial]
            for leaf_index, leaf in enumerate(factor_points):
                total = curve.add(partial, leaf, ops)
                candidate = prefix + (leaf_index,)
                counts[total] += multiplicity
                incumbent = witnesses.get(total)
                if incumbent is None or candidate < incumbent:
                    witnesses[total] = candidate
        if sum(counts.values()) != len(factor_points) ** depth:
            raise AssertionError("ordered point multiplicity mismatch")
        levels.append(witnesses)
        ordered_counts.append(counts)
        ops_by_depth.append(asdict(ops))
        profiles.append(
            {
                "depth": depth,
                "support_size": len(witnesses),
                "attempted_transitions": len(previous_witnesses)
                * len(factor_points),
                "unique_state_writes": len(witnesses),
                "deduplicated_transitions": (
                    len(previous_witnesses) * len(factor_points)
                    - len(witnesses)
                ),
                "ordered_representation_total": sum(counts.values()),
                "ordered_collision_energy": sum(
                    value * value for value in counts.values()
                ),
                "ordered_maximum_multiplicity": max(counts.values()),
                "point_state_deep_bytes": deep_size(witnesses),
                "point_counter_deep_bytes": deep_size(counts),
                "build_ops": asdict(ops),
            }
        )
    return {
        "levels": levels,
        "ordered_counts": ordered_counts,
        "profiles": profiles,
        "ops_by_depth": ops_by_depth,
    }


def sign_complete_canonical_counter(
    oriented_scalars: list[int], q: int, depth: int
) -> Counter[int]:
    counter: Counter[int] = Counter()
    if depth % 2 == 0:
        counter[0] += 1
    for l1_norm in range(depth % 2 or 2, depth + 1, 2):
        for support_size in range(
            1, min(len(oriented_scalars), l1_norm) + 1
        ):
            for support in itertools.combinations(
                range(len(oriented_scalars)), support_size
            ):
                for magnitudes in positive_compositions(
                    l1_norm, support_size
                ):
                    for signs in itertools.product((-1, 1), repeat=support_size):
                        total = sum(
                            sign
                            * magnitude
                            * oriented_scalars[index]
                            for index, magnitude, sign in zip(
                                support, magnitudes, signs
                            )
                        )
                        counter[total % q] += 1
    return counter


def canonical_counter(
    scalars: list[int], q: int, depth: int, symmetry_mode: str
) -> Counter[int]:
    if symmetry_mode == "sign_canonical":
        return Counter(
            sum(scalars[index] for index in indices) % q
            for indices in itertools.combinations_with_replacement(
                range(len(scalars)), depth
            )
        )
    if symmetry_mode == "sign_complete":
        if len(scalars) % 2:
            raise ValueError("sign-complete scalar list must be even")
        for index in range(0, len(scalars), 2):
            if (scalars[index] + scalars[index + 1]) % q:
                raise AssertionError("sign-complete fibers are not inverse pairs")
        return sign_complete_canonical_counter(scalars[::2], q, depth)
    raise ValueError(f"unsupported symmetry mode: {symmetry_mode}")


def audit_scalar_geometry(
    scalars: list[int],
    q: int,
    symmetry_mode: str,
    point_levels: dict[str, Any],
) -> dict[str, Any]:
    ordered: list[Counter[int]] = [Counter({0: 1})]
    canonical: list[Counter[int]] = [Counter({0: 1})]
    profiles = []
    for depth in range(1, 6):
        next_ordered: Counter[int] = Counter()
        for partial, multiplicity in ordered[-1].items():
            for scalar in scalars:
                next_ordered[(partial + scalar) % q] += multiplicity
        next_canonical = canonical_counter(
            scalars, q, depth, symmetry_mode
        )
        point_support = point_levels["levels"][depth]
        if set(next_ordered) != set(next_canonical):
            raise AssertionError("canonical and ordered supports differ")
        if len(point_support) != len(next_ordered):
            raise AssertionError("point and scalar support sizes differ")
        formal_total = formal_class_count(
            len(scalars), depth, symmetry_mode
        )
        if sum(next_canonical.values()) != formal_total:
            raise AssertionError("canonical formal-class total mismatch")
        profiles.append(
            {
                "depth": depth,
                "support_size": len(next_canonical),
                "support_fraction": len(next_canonical) / q,
                "canonical_formal_class_total": formal_total,
                "canonical_formal_defect": formal_total
                - len(next_canonical),
                "canonical_collision_energy": sum(
                    value * value for value in next_canonical.values()
                ),
                "canonical_maximum_multiplicity": max(
                    next_canonical.values()
                ),
                "ordered_representation_total": sum(next_ordered.values()),
                "ordered_collision_energy": sum(
                    value * value for value in next_ordered.values()
                ),
                "ordered_maximum_multiplicity": max(next_ordered.values()),
            }
        )
        ordered.append(next_ordered)
        canonical.append(next_canonical)
    d1 = set(canonical[1])
    d2 = set(canonical[2])
    d3 = set(canonical[3])
    d5 = set(canonical[5])
    d5_new = d5 - d1 - d3
    split_hits: Counter[int] = Counter(
        (left + right) % q for left in d2 for right in d3
    )
    if set(split_hits) != d5:
        raise AssertionError("D2+D3 audit support differs from D5")
    nonzero_targets = range(1, q)

    def expected_random_scan(target: int, scan_size: int) -> float:
        hits = split_hits.get(target, 0)
        return (
            (scan_size + 1) / (hits + 1)
            if hits
            else float(scan_size)
        )

    t_perm_d2 = statistics.fmean(
        expected_random_scan(target, len(d2))
        for target in nonzero_targets
    )
    t_perm_d3 = statistics.fmean(
        expected_random_scan(target, len(d3))
        for target in nonzero_targets
    )
    epsilon_nonidentity = len(d5 - {0}) / (q - 1)
    support_mass = len(d2) + len(d3)
    return {
        "profiles": profiles,
        "d1": d1,
        "d2": d2,
        "d3": d3,
        "d5": d5,
        "d5_new": d5_new,
        "split_hits": split_hits,
        "d5_nonidentity_size": len(d5 - {0}),
        "d5_new_size": len(d5_new),
        "epsilon_nonidentity": epsilon_nonidentity,
        "split_redundancy": len(d2) * len(d3) / max(1, len(d5)),
        "split_hit_mean_on_support": statistics.fmean(split_hits.values()),
        "split_hit_maximum": max(split_hits.values()),
        "t_perm_store_d3_scan_d2": t_perm_d2,
        "t_perm_store_d2_scan_d3": t_perm_d3,
        "support_mass_entries": support_mass,
        "phi_store_d3_scan_d2": (
            support_mass * t_perm_d2**2 / max(1, len(d5))
        ),
        "phi_store_d2_scan_d3": (
            support_mass * t_perm_d3**2 / max(1, len(d5))
        ),
        "classification": "AUDIT_ORACLE_NOT_ATTACK_ADVICE",
    }


def serialized_compiler_bytes(
    d2: dict[Point, tuple[int, ...]],
    d3: dict[Point, tuple[int, ...]],
) -> int:
    payload = {
        "D2": [
            [point_json(point), list(witness)]
            for point, witness in sorted(d2.items(), key=lambda item: point_sort_key(item[0]))
        ],
        "D3": [
            [point_json(point), list(witness)]
            for point, witness in sorted(d3.items(), key=lambda item: point_sort_key(item[0]))
        ],
    }
    return len(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    )


def scan_orders(points: list[Point], seed: int) -> dict[str, list[Point]]:
    canonical = sorted(points, key=point_sort_key)
    reverse = list(reversed(canonical))
    hashed = sorted(
        canonical,
        key=lambda point: hashlib.sha256(
            (
                f"EXP-ECDLP-COORD-EXPANSION-001|SCAN|{seed}|"
                + json.dumps(point_json(point), separators=(",", ":"))
            ).encode("ascii")
        ).digest(),
    )
    shuffled = canonical[:]
    random.Random(seed ^ 0xC2B2AE35).shuffle(shuffled)
    return {
        "canonical": canonical,
        "reverse": reverse,
        "hash": hashed,
        "shuffle": shuffled,
    }


def point_only_query(
    curve: Any,
    factor_points: list[Point],
    d2: dict[Point, tuple[int, ...]],
    d3: dict[Point, tuple[int, ...]],
    targets: list[Point],
    seed: int,
) -> dict[str, Any]:
    order_results = {}
    first_witness = None
    for order_name, order in scan_orders(list(d2), seed).items():
        probes = []
        successes = 0
        ops = Ops()
        for target_index, target in enumerate(targets):
            found = None
            for probe_index, partial in enumerate(order, 1):
                complement = curve.add(target, curve.neg(partial), ops)
                other = d3.get(complement)
                if other is None:
                    continue
                found = d2[partial] + other
                probes.append(probe_index)
                successes += 1
                recovered = None
                verify_ops = Ops()
                for leaf_index in found:
                    recovered = curve.add(
                        recovered, factor_points[leaf_index], verify_ops
                    )
                if recovered != target:
                    raise AssertionError("point-only witness verification failed")
                if first_witness is None:
                    first_witness = {
                        "target_index": target_index,
                        "factor_base_indices": list(found),
                    }
                break
            if found is None:
                probes.append(len(order))
        order_results[order_name] = {
            "target_count": len(targets),
            "successful_targets": successes,
            "sampled_success_probability": successes / len(targets),
            "probes_total": sum(probes),
            "probes_per_target_mean": statistics.fmean(probes),
            "probes_per_target_median": statistics.median(probes),
            "probes_per_target_p95": percentile(probes, 0.95),
            "probes_per_target_maximum": max(probes),
            "query_ops": asdict(ops),
        }
    return {
        "api_boundary": "TARGET_POINTS_AND_POINT_ADVICE_ONLY",
        "scan_orders": order_results,
        "first_witness": first_witness,
    }


def prepare_compiler(
    curve: Any,
    q: int,
    generator: Point,
    family: str,
    label: str,
    symmetry_mode: str,
    size: int,
    seed: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    factor_base = make_public_factor_base(
        family, symmetry_mode, curve, q, generator, size, seed
    )
    digest = factor_base_digest(factor_base)
    factor_points = [
        point_from_json(point) for point in factor_base["points"]
    ]
    compiler_levels = build_point_levels(curve, factor_points, 3)
    d2 = compiler_levels["levels"][2]
    d3 = compiler_levels["levels"][3]
    factor_base_json_bytes = len(
        json.dumps(
            factor_base,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    )
    support_json_bytes = serialized_compiler_bytes(d2, d3)
    return {
        "label": label,
        "family": family,
        "symmetry_mode": symmetry_mode,
        "seed": seed,
        "factor_base": factor_base,
        "factor_base_digest_before_audit": digest,
        "factor_points_internal": factor_points,
        "compiler_levels_internal": compiler_levels,
        "compiler": {
            "d2_entries": len(d2),
            "d3_entries": len(d3),
            "support_mass_entries": len(d2) + len(d3),
            "factor_base_json_bytes": factor_base_json_bytes,
            "support_json_bytes": support_json_bytes,
            "persistent_json_bytes": (
                factor_base_json_bytes + support_json_bytes
            ),
            "builder_deep_bytes": deep_size(compiler_levels),
            "build_profiles": compiler_levels["profiles"],
            "build_wall_seconds": time.perf_counter() - started,
            "attack_advice_contains": [
                "factor-base points and source records",
                "D2 point keys and witnesses",
                "D3 point keys and witnesses",
            ],
            "attack_advice_excludes": [
                "subgroup scalar census",
                "D4 support",
                "D5 support",
                "split-hit census",
            ],
        },
    }


def finish_audit(
    curve: Any,
    q: int,
    point_to_scalar: dict[Point, int],
    prepared: dict[str, Any],
    target_points: list[Point],
) -> dict[str, Any]:
    factor_base = prepared["factor_base"]
    if factor_base_digest(factor_base) != prepared[
        "factor_base_digest_before_audit"
    ]:
        raise AssertionError("factor base mutated before audit")
    factor_points = prepared.pop("factor_points_internal")
    compiler_levels = prepared.pop("compiler_levels_internal")
    audit_levels = build_point_levels(curve, factor_points, 5)
    for depth in range(1, 4):
        if audit_levels["levels"][depth] != compiler_levels["levels"][depth]:
            raise AssertionError("independent audit and compiler levels differ")
    scalars = factor_base_scalars(factor_base, point_to_scalar)
    audit = audit_scalar_geometry(
        scalars,
        q,
        prepared["symmetry_mode"],
        audit_levels,
    )
    d2 = compiler_levels["levels"][2]
    d3 = compiler_levels["levels"][3]
    query = point_only_query(
        curve,
        factor_points,
        d2,
        d3,
        target_points,
        prepared["seed"],
    )
    after_digest = factor_base_digest(factor_base)
    if after_digest != prepared["factor_base_digest_before_audit"]:
        raise AssertionError("factor base mutated during audit")
    prepared["factor_base_digest_after_audit"] = after_digest
    prepared["factor_base_scalars_diagnostic"] = scalars
    prepared["audit"] = {
        key: value
        for key, value in audit.items()
        if key not in ("d1", "d2", "d3", "d5", "d5_new", "split_hits")
    }
    prepared["audit"]["audit_point_build_profiles"] = audit_levels["profiles"]
    prepared["audit"]["audit_deep_bytes"] = deep_size(audit_levels) + deep_size(audit)
    prepared["query"] = query
    return prepared


def median_metric(
    records: list[dict[str, Any]], getter: Any
) -> float:
    return statistics.median(getter(record) for record in records)


def attach_null_ratios(configurations: list[dict[str, Any]]) -> None:
    for symmetry_mode in ("sign_canonical", "sign_complete"):
        group = [
            record
            for record in configurations
            if record["symmetry_mode"] == symmetry_mode
        ]
        if not group:
            continue
        null_groups = {
            family: [
                record for record in group if record["family"] == family
            ]
            for family in ("random_x", "source_prf_x", "random")
        }
        if any(not records for records in null_groups.values()):
            raise AssertionError("all three null families are required")
        metrics = {
            "d2": lambda record: record["compiler"]["d2_entries"],
            "d3": lambda record: record["compiler"]["d3_entries"],
            "d5_nonidentity": lambda record: record["audit"][
                "d5_nonidentity_size"
            ],
            "d5_new": lambda record: record["audit"]["d5_new_size"],
            "t_perm": lambda record: record["audit"][
                "t_perm_store_d3_scan_d2"
            ],
            "phi": lambda record: record["audit"][
                "phi_store_d3_scan_d2"
            ],
            "persistent_bytes": lambda record: record["compiler"][
                "persistent_json_bytes"
            ],
        }
        null_medians = {
            family: {
                metric_name: median_metric(records, getter)
                for metric_name, getter in metrics.items()
            }
            for family, records in null_groups.items()
        }
        coordinate_nulls = (
            null_groups["random_x"] + null_groups["source_prf_x"]
        )

        def normalized_effect_score(
            candidate: dict[str, Any], null_family: str
        ) -> float:
            ratios = {
                metric_name: getter(candidate)
                / max(null_medians[null_family][metric_name], 1e-300)
                for metric_name, getter in metrics.items()
            }
            return max(
                ratios["d2"] / 0.8,
                ratios["d3"] / 0.8,
                0.9 / max(ratios["d5_nonidentity"], 1e-300),
                0.9 / max(ratios["d5_new"], 1e-300),
            )

        for record in group:
            observed = {
                metric_name: getter(record)
                for metric_name, getter in metrics.items()
            }
            record["null_medians"] = null_medians
            record["ratios_to_null_medians"] = {
                family: {
                    metric_name: observed[metric_name]
                    / max(null_medians[family][metric_name], 1e-300)
                    for metric_name in metrics
                }
                for family in null_medians
            }
            domination_count = sum(
                null["audit"]["d5_nonidentity_size"]
                >= record["audit"]["d5_nonidentity_size"]
                and null["audit"]["d5_new_size"]
                >= record["audit"]["d5_new_size"]
                and null["compiler"]["d2_entries"]
                <= record["compiler"]["d2_entries"]
                and null["compiler"]["d3_entries"]
                <= record["compiler"]["d3_entries"]
                and null["audit"]["phi_store_d3_scan_d2"]
                <= record["audit"]["phi_store_d3_scan_d2"]
                for null in coordinate_nulls
            )
            record["uncalibrated_joint_dominance_score"] = (
                1 + domination_count
            ) / (1 + len(coordinate_nulls))
            null_tail_p = {}
            for family in ("random_x", "source_prf_x"):
                candidate_score = normalized_effect_score(record, family)
                null_scores = [
                    normalized_effect_score(null, family)
                    for null in null_groups[family]
                ]
                null_tail_p[family] = (
                    1
                    + sum(
                        null_score <= candidate_score
                        for null_score in null_scores
                    )
                ) / (1 + len(null_scores))
            record["development_null_tail_p"] = null_tail_p
            record["development_conservative_null_tail_p"] = max(
                null_tail_p.values()
            )
            scan_means = [
                value["probes_per_target_mean"]
                for value in record["query"]["scan_orders"].values()
            ]
            record["scan_order_mean_spread_ratio"] = max(scan_means) / max(
                min(scan_means), 1e-300
            )
            coordinate_ratios = [
                record["ratios_to_null_medians"][family]
                for family in ("random_x", "source_prf_x")
            ]
            record["stage_a_joint_gate"] = (
                record["family"]
                in ("x_interval", "square_map", "rational_union")
                and all(
                    ratios["d5_nonidentity"] >= 0.9
                    and ratios["d5_new"] >= 0.9
                    and ratios["d2"] <= 0.8
                    and ratios["d3"] <= 0.8
                    for ratios in coordinate_ratios
                )
                and record[
                    "development_conservative_null_tail_p"
                ]
                <= 0.05
                and record["query"]["first_witness"] is not None
            )
            record["cancellation_artifact_flag"] = (
                min(
                    ratios["d5_nonidentity"]
                    for ratios in coordinate_ratios
                )
                >= 0.9
                and min(ratios["d5_new"] for ratios in coordinate_ratios)
                < 0.9
            )


def measured_rho(
    curve: Any,
    q: int,
    generator: Point,
    targets: list[int],
    seed: int,
    trials: int,
) -> dict[str, Any]:
    results = []
    for trial_index in range(trials):
        known_scalar = targets[trial_index]
        target = curve.mul(known_scalar, generator)
        result = ENERGY.pollard_rho(
            curve,
            q,
            generator,
            target,
            seed ^ (trial_index * 0x9E3779B1),
        )
        if result["recovered_scalar"] != known_scalar or not result["verified"]:
            raise AssertionError("rho baseline recovered the wrong scalar")
        result["known_scalar"] = known_scalar
        results.append(result)
    return {
        "trials": results,
        "median_group_operations": statistics.median(
            result["ops"]["group_operations"] for result in results
        ),
        "analytic_sqrt_q": math.sqrt(q),
    }


def summarize(
    instances: list[dict[str, Any]], interpretation_eligible: bool
) -> dict[str, Any]:
    candidates = ("x_interval", "square_map", "rational_union")
    cell_counts: dict[str, dict[str, Any]] = {}
    scaling_points: dict[str, dict[str, list[tuple[int, float]]]] = {}
    for instance in instances:
        q = instance["curve"]["q"]
        for record in instance["configurations"]:
            if record["family"] in candidates:
                key = f"{record['family']}|{record['symmetry_mode']}"
                cell = cell_counts.setdefault(
                    key,
                    {
                        "instances": 0,
                        "joint_passes": 0,
                        "cancellation_artifact_cells": 0,
                        "bit_sizes": set(),
                        "seeds": set(),
                    },
                )
                cell["instances"] += 1
                cell["joint_passes"] += int(record["stage_a_joint_gate"])
                cell["cancellation_artifact_cells"] += int(
                    record["cancellation_artifact_flag"]
                )
                cell["bit_sizes"].add(instance["curve"]["bits"])
                cell["seeds"].add(instance["seed"])
            scaling_label = (
                record["family"]
                if record["family"]
                in ("random", "random_x", "source_prf_x")
                else record["label"]
            )
            scaling_key = f"{scaling_label}|{record['symmetry_mode']}"
            scaling = scaling_points.setdefault(
                scaling_key,
                {
                    "d2": [],
                    "d3": [],
                    "t_perm": [],
                    "persistent_bytes": [],
                    "compiler": [],
                },
            )
            scaling["d2"].append((q, record["compiler"]["d2_entries"]))
            scaling["d3"].append((q, record["compiler"]["d3_entries"]))
            scaling["t_perm"].append(
                (
                    q,
                    record["audit"]["t_perm_store_d3_scan_d2"],
                )
            )
            scaling["persistent_bytes"].append(
                (q, record["compiler"]["persistent_json_bytes"])
            )
            build_ops = sum(
                profile["build_ops"]["group_operations"]
                for profile in record["compiler"]["build_profiles"]
            )
            scaling["compiler"].append(
                (q, build_ops)
            )

    promoted = []
    serializable_cells: dict[str, Any] = {}
    for key, cell in sorted(cell_counts.items()):
        pass_fraction = cell["joint_passes"] / cell["instances"]
        serializable_cells[key] = {
            **cell,
            "bit_sizes": sorted(cell["bit_sizes"]),
            "seeds": sorted(cell["seeds"]),
            "joint_pass_fraction": pass_fraction,
        }
        if (
            pass_fraction >= 0.75
            and len(cell["bit_sizes"]) >= 4
            and len(cell["seeds"]) >= 2
        ):
            promoted.append(key)

    fitted_exponents = {
        key: {
            metric_name: fit_exponent(points)
            for metric_name, points in metrics.items()
        }
        for key, metrics in scaling_points.items()
    }
    rho_points = [
        (instance["curve"]["q"], instance["rho"]["median_group_operations"])
        for instance in instances
    ]
    return {
        "instances_completed": len(instances),
        "candidate_cells": serializable_cells,
        "promoted_candidate_cells": promoted,
        "fitted_exponents": fitted_exponents,
        "measured_rho_exponent": fit_exponent(rho_points),
        "breakthrough_claim": False,
        "rank_measured": False,
        "descent_measured": False,
        "result_classification": (
            "STAGE_A_SIGNAL"
            if promoted
            else (
                "DEVELOPMENT_SCOPED_NEGATIVE_NO_FROZEN_FAMILY_CROSSED_STAGE_A_GATE"
                if interpretation_eligible
                else "INCONCLUSIVE_INSUFFICIENT_NULLS_OR_SCALES"
            )
        ),
        "interpretation": (
            "A joint pass authorizes codec, relation-matrix, and descent "
            "successors only. Absence of a pass is not a coordinate barrier."
        ),
    }


def run_experiment(
    bit_sizes: list[int],
    seeds: list[int],
    null_draws: int,
    targets: int,
    rho_trials: int,
    occupancy_lambda: float,
) -> dict[str, Any]:
    for index, bits in enumerate(bit_sizes):
        exact_int(bits, f"bit_sizes[{index}]", 8)
    for index, seed in enumerate(seeds):
        exact_int(seed, f"seeds[{index}]")
    exact_int(null_draws, "null_draws", 1)
    exact_int(targets, "targets", 1)
    exact_int(rho_trials, "rho_trials", 1)
    if rho_trials > targets:
        raise ValueError("rho_trials must not exceed targets")
    if type(occupancy_lambda) not in (int, float) or isinstance(
        occupancy_lambda, bool
    ):
        raise ValueError("occupancy_lambda must be numeric")
    if occupancy_lambda <= 0:
        raise ValueError("occupancy_lambda must be positive")

    started = time.perf_counter()
    instances = []
    for seed in seeds:
        for bits in bit_sizes:
            curve_record = generate_admissible_curve(
                bits, seed + bits * 1009
            )
            curve = Curve(
                curve_record["p"], curve_record["a"], curve_record["b"]
            )
            q = curve_record["q"]
            generator = point_from_json(curve_record["generator"])
            if targets > q - 1:
                raise ValueError("targets must not exceed q-1")
            prepared_configurations = []
            sizes = {}
            for symmetry_index, symmetry_mode in enumerate(
                ("sign_canonical", "sign_complete")
            ):
                size = choose_factor_base_size(
                    q, 5, occupancy_lambda, symmetry_mode
                )
                sizes[symmetry_mode] = size
                for null_index in range(null_draws):
                    for family_index, family in enumerate(
                        ("random", "random_x", "source_prf_x")
                    ):
                        family_seed = (
                            seed
                            ^ (bits << 24)
                            ^ (symmetry_index << 16)
                            ^ (null_index << 8)
                            ^ (family_index * 0x9E3779B1)
                        )
                        prepared_configurations.append(
                            prepare_compiler(
                                curve,
                                q,
                                generator,
                                family,
                                f"{family}_null_{null_index}",
                                symmetry_mode,
                                size,
                                family_seed,
                            )
                        )
                for family_index, family in enumerate(
                    (
                        "x_interval",
                        "square_map",
                        "rational_union",
                        "scalar_progression_positive_control",
                    )
                ):
                    family_seed = (
                        seed
                        ^ (bits << 24)
                        ^ (symmetry_index << 16)
                        ^ (family_index * 0x85EBCA6B)
                    )
                    prepared_configurations.append(
                        prepare_compiler(
                            curve,
                            q,
                            generator,
                            family,
                            family,
                            symmetry_mode,
                            size,
                            family_seed,
                        )
                    )
            prepared_digest = canonical_json_sha256(
                [
                    record["factor_base_digest_before_audit"]
                    for record in prepared_configurations
                ]
            )
            target_rng = random.Random(seed ^ (bits << 20) ^ 0xA54FF53A)
            target_scalars = target_rng.sample(range(1, q), targets)
            target_points = [
                curve.mul(scalar, generator) for scalar in target_scalars
            ]
            point_to_scalar, census = subgroup_log_census(
                curve, q, generator
            )
            configurations = [
                finish_audit(
                    curve,
                    q,
                    point_to_scalar,
                    prepared,
                    target_points,
                )
                for prepared in prepared_configurations
            ]
            finished_digest = canonical_json_sha256(
                [
                    record["factor_base_digest_after_audit"]
                    for record in configurations
                ]
            )
            if finished_digest != prepared_digest:
                raise AssertionError("factor-base digest set changed")
            attach_null_ratios(configurations)
            instances.append(
                {
                    "seed": seed,
                    "curve": curve_record,
                    "factor_base_sizes": sizes,
                    "factor_base_digest_set_before_audit": prepared_digest,
                    "factor_base_digest_set_after_audit": finished_digest,
                    "target_scalars": target_scalars,
                    "target_points": [point_json(point) for point in target_points],
                    "diagnostic_subgroup_log_census": census,
                    "configurations": configurations,
                    "rho": measured_rho(
                        curve,
                        q,
                        generator,
                        target_scalars,
                        seed ^ (bits << 12),
                        rho_trials,
                    ),
                }
            )

    interpretation_eligible = null_draws >= 31 and len(bit_sizes) >= 3
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-development-v2",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "HEURISTIC",
            "NOVELTY-UNVERIFIED",
        ],
        "valid": True,
        "source": {
            "coordinate_expansion_sha256": sha256_file(SCRIPT_PATH),
            "recursive_expansion_sha256": sha256_file(
                RECURSIVE_SOURCE_PATH
            ),
            "coordinate_energy_sha256": sha256_file(
                RECURSIVE.ENERGY_SOURCE_PATH
            ),
        },
        "config": {
            "bit_sizes": bit_sizes,
            "seeds": seeds,
            "null_draws": null_draws,
            "targets": targets,
            "rho_trials": rho_trials,
            "occupancy_lambda": occupancy_lambda,
            "maximum_depth": 5,
            "candidate_families": [
                "x_interval",
                "square_map",
                "rational_union",
            ],
            "null_families": ["random", "random_x", "source_prf_x"],
            "coordinate_null_families": ["random_x", "source_prf_x"],
            "positive_control": "scalar_progression_positive_control",
            "symmetry_modes": ["sign_canonical", "sign_complete"],
            "minimum_null_draws_for_development_interpretation": 31,
            "minimum_null_draws_for_confirmatory_interpretation": 63,
        },
        "instances": instances,
        "summary": summarize(instances, interpretation_eligible),
        "total_wall_seconds": time.perf_counter() - started,
        "boundary": (
            "The compiler and online query are point-only. D4, D5, split "
            "hits, and subgroup logs are charged audit artifacts only. Rank, "
            "linear algebra, and individual descent remain unmeasured."
        ),
        "interpretation_eligible": interpretation_eligible,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bit-sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--null-draws", type=int, default=4)
    parser.add_argument("--targets", type=int, default=128)
    parser.add_argument("--rho-trials", type=int, default=2)
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_experiment(
        args.bit_sizes,
        args.seeds,
        args.null_draws,
        args.targets,
        args.rho_trials,
        args.occupancy_lambda,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

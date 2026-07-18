#!/usr/bin/env python3
"""Source-tagged recursive joins for authorized toy ECDLP research."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


PROTOCOL = "EXP-ECDLP-SOURCE-TAG-JOIN-001-development-v2"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
PREDECESSOR_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-COMPRESSED-JOIN-001"
    / "src"
    / "compressed_join.py"
)
VERIFIER_PATH = SCRIPT_PATH.with_name("verify_source_tag_join.py")
CONTRACT_PATH = EXPERIMENT_ROOT / "contract.md"
CONTRACT_V1_PATH = EXPERIMENT_ROOT / "contract-v1.md"
HYPOTHESIS_PATH = EXPERIMENT_ROOT / "hypothesis.json"
QUESTION_PATH = EXPERIMENT_ROOT / "research-question.json"
THEORY_PATH = EXPERIMENT_ROOT / "theory.md"
IMPLEMENTATION_PATH = EXPERIMENT_ROOT / "implementation.md"
PRE_RUN_RED_TEAM_PATH = EXPERIMENT_ROOT / "pre-run-red-team-v1.md"
PRE_RUN_REVIEW_V2_PATH = EXPERIMENT_ROOT / "pre-run-review-v2.md"

CANDIDATE_TAGS = ["ordinal_sum", "source_x_sum", "parameter_mix"]
WITNESS_POLICIES = ["symmetry_lex", "symmetry_hash"]
PUBLIC_OUTPUT_ROUTERS = ["x_interval", "random_x_fiber"]
POSITIVE_CONTROL = "scalar_interval"
MARGIN_NULL_KIND = "multiplicity_orbit_shuffle"
SOURCE_NULL_KIND = "source_record_permutation"
SUPPORTED_FAMILIES = [
    "x_interval",
    "square_map",
    "rational_union",
    "random_x",
    "random_scalar",
]
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [3317584535, 967613517, 3537188825],
    "families": SUPPORTED_FAMILIES,
    "witness_policies": WITNESS_POLICIES,
    "source_tags": CANDIDATE_TAGS,
    "tag_counts": [4, 8, 16, 32],
    "output_routers": PUBLIC_OUTPUT_ROUTERS,
    "null_seeds": [7301, 7307, 7321, 7331, 7349, 7351, 7369, 7393],
    "occupancy_lambda": 0.5,
    "query_samples": 8,
    "descent_challenges": 2,
    "descent_attempt_limit": 16,
    "rho_trials": 2,
}


def load_predecessor() -> Any:
    spec = importlib.util.spec_from_file_location(
        "source_tag_join_predecessor", PREDECESSOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load predecessor source: {PREDECESSOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRE = load_predecessor()
BASE = PRE.BASE
Curve = PRE.Curve
Ops = PRE.Ops
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


def mean_or_zero(values: list[int | float]) -> float:
    return statistics.fmean(values) if values else 0.0


def sum_ops(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {key: sum(record.get(key, 0) for record in records) for key in sorted(keys)}


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


def histogram(values: Iterable[int]) -> dict[str, int]:
    items = list(values)
    return {str(value): items.count(value) for value in sorted(set(items))}


def shannon_entropy(counts: Iterable[int]) -> float:
    values = [value for value in counts if value > 0]
    total = sum(values)
    if total == 0:
        return 0.0
    return -sum((value / total) * math.log2(value / total) for value in values)


@dataclass
class SourceD2Support:
    points: list[Point]
    witnesses: list[tuple[int, int]]
    all_witnesses: list[tuple[tuple[int, int], ...]]
    multiplicities: list[int]
    point_to_index: dict[Point, int]
    inversion_indices: list[int]
    build_ops: Ops
    attempts: int
    witness_policy: str
    witness_seed: int


@dataclass
class SourceAdvice:
    source_tag: str
    variant_kind: str
    witness_policy: str
    tag_count: int
    output_router: str
    output_seed: int
    tags: list[int]
    bucket_contents: dict[int, list[int]]
    routes: dict[tuple[int, int], tuple[int, ...]]
    record: dict[str, Any]
    scalar_oracle_required: bool


def negate_factor_index(index: int) -> int:
    return index ^ 1


def normalized_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def select_witness(
    witnesses: tuple[tuple[int, int], ...],
    policy: str,
    seed: int,
) -> tuple[int, int]:
    if policy == "symmetry_lex":
        return min(witnesses)
    if policy == "symmetry_hash":
        return min(
            witnesses,
            key=lambda pair: (
                hashlib.sha256(
                    seed.to_bytes(16, "big", signed=False)
                    + pair[0].to_bytes(8, "big")
                    + pair[1].to_bytes(8, "big")
                ).digest(),
                pair,
            ),
        )
    raise ValueError(f"unsupported witness policy: {policy}")


def build_source_d2(
    curve: Any,
    factor_points: list[Point],
    witness_policy: str,
    witness_seed: int,
) -> SourceD2Support:
    if witness_policy not in WITNESS_POLICIES:
        raise ValueError(f"unsupported witness policy: {witness_policy}")
    if len(factor_points) % 2:
        raise ValueError("factor base must contain complete sign pairs")
    for index in range(0, len(factor_points), 2):
        if curve.neg(factor_points[index]) != factor_points[index + 1]:
            raise AssertionError("factor-base sign pair is not adjacent")

    ops = Ops()
    witnesses_by_point: dict[Point, list[tuple[int, int]]] = {}
    attempts = 0
    for left in range(len(factor_points)):
        for right in range(left, len(factor_points)):
            attempts += 1
            total = curve.add(factor_points[left], factor_points[right], ops)
            witnesses_by_point.setdefault(total, []).append((left, right))

    points = sorted(witnesses_by_point, key=BASE.point_sort_key)
    point_to_index = {point: index for index, point in enumerate(points)}
    all_witnesses = [tuple(witnesses_by_point[point]) for point in points]
    multiplicities = [len(witnesses) for witnesses in all_witnesses]
    inversion_indices = [point_to_index[curve.neg(point)] for point in points]
    bound: list[tuple[int, int] | None] = [None] * len(points)

    for index, negative_index in enumerate(inversion_indices):
        if index > negative_index or bound[index] is not None:
            continue
        selected = select_witness(all_witnesses[index], witness_policy, witness_seed)
        negated = normalized_pair(
            negate_factor_index(selected[0]), negate_factor_index(selected[1])
        )
        if negated not in all_witnesses[negative_index]:
            raise AssertionError("negated D2 witness is absent")
        bound[index] = selected
        bound[negative_index] = negated

    if any(witness is None for witness in bound):
        raise AssertionError("a D2 point was not assigned a symmetry-bound witness")
    for index, negative_index in enumerate(inversion_indices):
        if multiplicities[index] != multiplicities[negative_index]:
            raise AssertionError("D2 multiplicity is not inversion invariant")
        witness = bound[index]
        assert witness is not None
        expected = normalized_pair(
            negate_factor_index(witness[0]), negate_factor_index(witness[1])
        )
        if bound[negative_index] != expected:
            raise AssertionError("symmetry-bound witness relation failed")

    return SourceD2Support(
        points=points,
        witnesses=[witness for witness in bound if witness is not None],
        all_witnesses=all_witnesses,
        multiplicities=multiplicities,
        point_to_index=point_to_index,
        inversion_indices=inversion_indices,
        build_ops=ops,
        attempts=attempts,
        witness_policy=witness_policy,
        witness_seed=witness_seed,
    )


def public_factor_sources(
    factor_base: dict[str, Any],
    curve: Any,
) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for ordinal, fiber in enumerate(factor_base["fibers"]):
        source = dict(fiber["source"])
        if source.get("ordinal") != ordinal:
            raise AssertionError("factor source ordinal is inconsistent")
        points = [BASE.point_from_json(point) for point in fiber["points"]]
        if len(points) != 2 or curve.neg(points[0]) != points[1]:
            raise AssertionError("factor source is not a sign-complete fiber")
        x_value = exact_int(source.get("x", points[0][0]), "source x", 0)
        parameter = exact_int(source.get("t", ordinal), "source parameter", 0)
        map_branch = 1 if source.get("map") == "mobius" else 0
        sources.append(
            {
                "ordinal": ordinal,
                "x": x_value,
                "parameter": parameter,
                "map_branch": map_branch,
                "source": source,
            }
        )
    return sources


def source_tag_for_witness(
    name: str,
    witness: tuple[int, int],
    factor_sources: list[dict[str, Any]],
    tag_count: int,
) -> int:
    if name not in CANDIDATE_TAGS:
        raise ValueError(f"unsupported source tag: {name}")
    if not is_power_of_two(tag_count):
        raise ValueError("tag count must be a power of two")
    left, right = witness
    left_source = factor_sources[left // 2]
    right_source = factor_sources[right // 2]
    sign_parity = (left & 1) ^ (right & 1)
    sign_term = sign_parity * (tag_count // 2 + 1)
    if name == "ordinal_sum":
        value = left_source["ordinal"] + right_source["ordinal"] + sign_term
    elif name == "source_x_sum":
        value = left_source["x"] + right_source["x"] + sign_term
    else:
        left_parameter = left_source["parameter"]
        right_parameter = right_source["parameter"]
        value = (
            left_parameter
            + right_parameter
            + 3 * abs(left_parameter - right_parameter)
            + 5 * (left_source["map_branch"] + right_source["map_branch"])
            + sign_term
        )
    return value % tag_count


def candidate_tag_assignment(
    name: str,
    d2: SourceD2Support,
    factor_sources: list[dict[str, Any]],
    tag_count: int,
) -> list[int]:
    tags = [
        source_tag_for_witness(name, witness, factor_sources, tag_count)
        for witness in d2.witnesses
    ]
    for index, negative_index in enumerate(d2.inversion_indices):
        if tags[index] != tags[negative_index]:
            raise AssertionError("eligible source tag is not inversion invariant")
    return tags


def all_witness_tag_diagnostic(
    name: str,
    d2: SourceD2Support,
    factor_sources: list[dict[str, Any]],
    tag_count: int,
) -> dict[str, Any]:
    per_point = [
        sorted(
            source_tag_for_witness(name, witness, factor_sources, tag_count)
            for witness in witnesses
        )
        for witnesses in d2.all_witnesses
    ]
    for index, negative_index in enumerate(d2.inversion_indices):
        if per_point[index] != per_point[negative_index]:
            raise AssertionError("all-witness tag multiset is not inversion invariant")
    distinct_counts = [len(set(values)) for values in per_point]
    return {
        "source_tag": name,
        "tag_count": tag_count,
        "per_point_multiset_digest": stable_digest(per_point),
        "points_with_multiple_source_tags": sum(count > 1 for count in distinct_counts),
        "distinct_tag_count_histogram": histogram(distinct_counts),
        "total_provenance_states": sum(len(values) for values in per_point),
        "semantic_d2_points": len(per_point),
        "credited_as_support": False,
    }


def multiplicity_by_tag_histogram(
    tags: list[int],
    multiplicities: list[int],
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for tag, multiplicity in zip(tags, multiplicities):
        bucket = result.setdefault(str(tag), {})
        key = str(multiplicity)
        bucket[key] = bucket.get(key, 0) + 1
    return result


def source_witness_class(witness: tuple[int, int]) -> str:
    left, right = witness
    if left == right:
        return "repeated_leaf"
    if negate_factor_index(left) == right:
        return "inverse_pair"
    if left // 2 == right // 2:
        return "same_fiber_other"
    if (left & 1) == (right & 1):
        return "distinct_fibers_same_sign"
    return "distinct_fibers_mixed_sign"


def witness_class_by_tag_histogram(
    tags: list[int],
    witnesses: list[tuple[int, int]],
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for tag, witness in zip(tags, witnesses):
        bucket = result.setdefault(str(tag), {})
        key = source_witness_class(witness)
        bucket[key] = bucket.get(key, 0) + 1
    return result


def shuffled_tag_assignment(
    candidate_tags: list[int],
    d2: SourceD2Support,
    null_seed: int,
) -> tuple[list[int], dict[str, Any]]:
    if len(candidate_tags) != len(d2.points):
        raise ValueError("candidate tag assignment length differs from D2")
    rng = random.Random(null_seed)
    orbits: list[tuple[int, ...]] = []
    seen: set[int] = set()
    for index, negative_index in enumerate(d2.inversion_indices):
        if index in seen:
            continue
        orbit = (index,) if index == negative_index else tuple(sorted((index, negative_index)))
        seen.update(orbit)
        if len({candidate_tags[item] for item in orbit}) != 1:
            raise AssertionError("candidate tag differs inside an inversion orbit")
        orbits.append(orbit)

    strata: dict[tuple[int, int, str], list[tuple[int, ...]]] = {}
    for orbit in orbits:
        multiplicity = d2.multiplicities[orbit[0]]
        if any(d2.multiplicities[item] != multiplicity for item in orbit):
            raise AssertionError("multiplicity differs inside an inversion orbit")
        witness_class = source_witness_class(d2.witnesses[orbit[0]])
        if any(
            source_witness_class(d2.witnesses[item]) != witness_class
            for item in orbit
        ):
            raise AssertionError("source witness class differs inside inversion orbit")
        strata.setdefault((multiplicity, len(orbit), witness_class), []).append(orbit)

    shuffled = list(candidate_tags)
    moved_points = 0
    movable_points = 0
    permutation_rows = []
    for stratum_key in sorted(strata):
        stratum_orbits = strata[stratum_key]
        source_positions = list(range(len(stratum_orbits)))
        rng.shuffle(source_positions)
        if len(source_positions) > 1 and source_positions == list(range(len(source_positions))):
            source_positions = source_positions[1:] + source_positions[:1]
        distinct_tags = {candidate_tags[orbit[0]] for orbit in stratum_orbits}
        if len(stratum_orbits) > 1 and len(distinct_tags) > 1:
            movable_points += sum(len(orbit) for orbit in stratum_orbits)
        for destination_position, source_position in enumerate(source_positions):
            destination = stratum_orbits[destination_position]
            source = stratum_orbits[source_position]
            tag = candidate_tags[source[0]]
            for point_index in destination:
                shuffled[point_index] = tag
                moved_points += int(tag != candidate_tags[point_index])
        permutation_rows.append(
            {
                "multiplicity": stratum_key[0],
                "orbit_size": stratum_key[1],
                "witness_class": stratum_key[2],
                "orbit_count": len(stratum_orbits),
                "permutation": source_positions,
            }
        )

    for index, negative_index in enumerate(d2.inversion_indices):
        if shuffled[index] != shuffled[negative_index]:
            raise AssertionError("shuffled tag broke inversion symmetry")
    candidate_histogram = histogram(candidate_tags)
    shuffled_histogram = histogram(shuffled)
    candidate_multiplicity = multiplicity_by_tag_histogram(
        candidate_tags, d2.multiplicities
    )
    shuffled_multiplicity = multiplicity_by_tag_histogram(shuffled, d2.multiplicities)
    candidate_classes = witness_class_by_tag_histogram(candidate_tags, d2.witnesses)
    shuffled_classes = witness_class_by_tag_histogram(shuffled, d2.witnesses)
    if candidate_histogram != shuffled_histogram:
        raise AssertionError("matched null changed the tag histogram")
    if candidate_multiplicity != shuffled_multiplicity:
        raise AssertionError("matched null changed multiplicity by tag")
    if candidate_classes != shuffled_classes:
        raise AssertionError("matched null changed witness class by tag")
    return shuffled, {
        "kind": MARGIN_NULL_KIND,
        "seed": null_seed,
        "tag_histogram_preserved": True,
        "multiplicity_by_tag_preserved": True,
        "witness_class_by_tag_preserved": True,
        "inversion_symmetry_preserved": True,
        "moved_points": moved_points,
        "movable_points": movable_points,
        "moved_fraction_of_all_points": moved_points / len(shuffled),
        "moved_fraction_of_movable_points": (
            moved_points / movable_points if movable_points else 0.0
        ),
        "permutation_digest": stable_digest(permutation_rows),
    }


def source_permuted_tag_assignment(
    source_tag: str,
    d2: SourceD2Support,
    factor_sources: list[dict[str, Any]],
    tag_count: int,
    null_seed: int,
) -> tuple[list[int], list[dict[str, Any]], dict[str, Any]]:
    rng = random.Random(null_seed ^ 0x8CB92BA72F3D8DD7)
    permutation = list(range(len(factor_sources)))
    rng.shuffle(permutation)
    if len(permutation) > 1 and permutation == list(range(len(permutation))):
        permutation = permutation[1:] + permutation[:1]
    permuted_sources = [factor_sources[source] for source in permutation]
    if stable_digest(sorted(factor_sources, key=stable_digest)) != stable_digest(
        sorted(permuted_sources, key=stable_digest)
    ):
        raise AssertionError("source permutation changed the source-record multiset")
    tags = candidate_tag_assignment(source_tag, d2, permuted_sources, tag_count)
    moved_fibers = sum(
        int(destination != source)
        for destination, source in enumerate(permutation)
    )
    return tags, permuted_sources, {
        "kind": SOURCE_NULL_KIND,
        "seed": null_seed,
        "source_multiset_preserved": True,
        "compositional_recompute": True,
        "inversion_symmetry_preserved": True,
        "moved_fibers": moved_fibers,
        "movable_fibers": len(factor_sources),
        "moved_fraction_of_movable_fibers": moved_fibers / len(factor_sources),
        "permutation_digest": stable_digest(permutation),
    }


def output_bucket(
    name: str,
    point: Point,
    bucket_count: int,
    curve: Any,
    q: int,
    seed: int,
    scalar_index: dict[Point, int] | None = None,
) -> int:
    if not is_power_of_two(bucket_count):
        raise ValueError("output bucket count must be a power of two")
    if name == POSITIVE_CONTROL:
        if scalar_index is None:
            raise ValueError("scalar_interval requires a private scalar index")
        return scalar_index[point] * bucket_count // q
    if name not in PUBLIC_OUTPUT_ROUTERS:
        raise ValueError(f"unsupported output router: {name}")
    if point is None:
        return 0
    x = point[0]
    if name == "x_interval":
        return min(bucket_count - 1, (x + 1) * bucket_count // (curve.p + 1))
    width = max(1, math.ceil(curve.p.bit_length() / 8))
    digest = hashlib.sha256(
        seed.to_bytes(16, "big", signed=False) + x.to_bytes(width, "big")
    ).digest()
    return int.from_bytes(digest[:8], "big") % bucket_count


def scalar_tag_assignment(
    d2: SourceD2Support,
    scalar_index: dict[Point, int],
    q: int,
    tag_count: int,
) -> list[int]:
    return [scalar_index[point] * tag_count // q for point in d2.points]


def compile_source_advice(
    curve: Any,
    q: int,
    factor_points: list[Point],
    factor_sources: list[dict[str, Any]],
    d2: SourceD2Support,
    source_tag: str,
    variant_kind: str,
    tags: list[int],
    tag_count: int,
    output_router_name: str,
    output_seed: int,
    null_record: dict[str, Any] | None,
    scalar_index: dict[Point, int] | None,
) -> SourceAdvice:
    if len(tags) != len(d2.points):
        raise ValueError("tag assignment length differs from D2")
    if any(type(tag) is not int or not 0 <= tag < tag_count for tag in tags):
        raise ValueError("tag assignment contains an invalid tag")
    scalar_required = source_tag == POSITIVE_CONTROL
    if scalar_required != (output_router_name == POSITIVE_CONTROL):
        raise ValueError("scalar control must use scalar tags and scalar output together")
    if scalar_required and scalar_index is None:
        raise ValueError("scalar control requires private scalar index")
    if not scalar_required and scalar_index is not None:
        raise ValueError("eligible or null advice received private scalar index")

    bucket_contents: dict[int, list[int]] = {tag: [] for tag in range(tag_count)}
    for point_index, tag in enumerate(tags):
        bucket_contents[tag].append(point_index)

    reverse: dict[tuple[int, int], set[int]] = {}
    forward_counts: dict[tuple[int, int], dict[int, int]] = {}
    route_coverage = 0
    route_build_ops = Ops()
    pair_attempts = 0
    for left in range(len(d2.points)):
        for right in range(left, len(d2.points)):
            pair_attempts += 1
            output = curve.add(d2.points[left], d2.points[right], route_build_ops)
            output_tag = output_bucket(
                output_router_name,
                output,
                tag_count,
                curve,
                q,
                output_seed,
                scalar_index,
            )
            orientations = (
                [(left, right)] if left == right else [(left, right), (right, left)]
            )
            for oriented_left, oriented_right in orientations:
                left_tag = tags[oriented_left]
                right_tag = tags[oriented_right]
                reverse.setdefault((output_tag, left_tag), set()).add(right_tag)
                counts = forward_counts.setdefault((left_tag, right_tag), {})
                counts[output_tag] = counts.get(output_tag, 0) + 1
                route_coverage += 1
    routes = {key: tuple(sorted(values)) for key, values in reverse.items()}

    coverage_audit_ops = Ops()
    for left in range(len(d2.points)):
        for right in range(left, len(d2.points)):
            output = curve.add(d2.points[left], d2.points[right], coverage_audit_ops)
            output_tag = output_bucket(
                output_router_name,
                output,
                tag_count,
                curve,
                q,
                output_seed,
                scalar_index,
            )
            if tags[right] not in routes[(output_tag, tags[left])]:
                raise AssertionError("source route omitted a forward D4 pair")
            if tags[left] not in routes[(output_tag, tags[right])]:
                raise AssertionError("source route omitted a reverse D4 pair")

    ordered_pair_count = len(d2.points) ** 2
    if route_coverage != ordered_pair_count:
        raise AssertionError("source route coverage differs from ordered D2 pairs")
    reverse_widths = [len(values) for values in routes.values()]
    weighted_entropy = sum(
        sum(counts.values()) * shannon_entropy(counts.values())
        for counts in forward_counts.values()
    ) / ordered_pair_count
    route_triples = sum(reverse_widths)

    point_bits = 1 + 2 * curve.p.bit_length()
    factor_index_bits = max(1, (len(factor_points) - 1).bit_length())
    tag_bits = max(1, (tag_count - 1).bit_length())
    multiplicity_bits = max(1, max(d2.multiplicities).bit_length())
    directory_bits = (tag_count + 1) * max(1, len(d2.points).bit_length())
    source_record_bits = 8 * len(stable_json_bytes(factor_sources))
    payload_bits = (
        len(factor_points) * point_bits
        + source_record_bits
        + len(d2.points)
        * (point_bits + 2 * factor_index_bits + tag_bits + multiplicity_bits)
        + directory_bits
        + route_triples * 3 * tag_bits
        + 128
    )
    artifact = {
        "factor_points": [BASE.point_json(point) for point in factor_points],
        "factor_sources": factor_sources,
        "d2": [
            {
                "point": BASE.point_json(point),
                "witness": list(witness),
                "multiplicity": multiplicity,
                "tag": tag,
            }
            for point, witness, multiplicity, tag in zip(
                d2.points, d2.witnesses, d2.multiplicities, tags
            )
        ],
        "routes": [
            [output_tag, left_tag, right_tag]
            for (output_tag, left_tag), right_tags in sorted(routes.items())
            for right_tag in right_tags
        ],
    }
    tag_counts = [len(bucket_contents[tag]) for tag in range(tag_count)]
    multiplicity_tag = multiplicity_by_tag_histogram(tags, d2.multiplicities)
    witness_class_tag = witness_class_by_tag_histogram(tags, d2.witnesses)
    record = {
        "source_tag": source_tag,
        "variant_kind": variant_kind,
        "eligibility": "positive_control_only" if scalar_required else (
            "matched_null" if variant_kind in ("margin_null", "source_null") else "candidate"
        ),
        "witness_policy": d2.witness_policy,
        "tag_count": tag_count,
        "output_router": output_router_name,
        "output_seed": output_seed,
        "occupied_tag_buckets": sum(bool(count) for count in tag_counts),
        "tag_histogram": histogram(tags),
        "multiplicity_by_tag_histogram": multiplicity_tag,
        "witness_class_by_tag_histogram": witness_class_tag,
        "maximum_tag_bucket_size": max(tag_counts),
        "mean_occupied_tag_bucket_size": mean_or_zero(
            [count for count in tag_counts if count]
        ),
        "occupied_forward_tag_pairs": len(forward_counts),
        "occupied_reverse_route_keys": len(routes),
        "distinct_route_triples": route_triples,
        "route_universe_size": tag_count**3,
        "route_universe_saturated": route_triples == tag_count**3,
        "route_coverage_oriented_pairs": route_coverage,
        "expected_oriented_pairs": ordered_pair_count,
        "average_reverse_right_tag_width": mean_or_zero(reverse_widths),
        "maximum_reverse_right_tag_width": max(reverse_widths),
        "conditional_output_entropy_bits": weighted_entropy,
        "normalized_conditional_output_entropy": (
            weighted_entropy / math.log2(tag_count) if tag_count > 1 else 0.0
        ),
        "payload_bit_lower_estimate": payload_bits,
        "payload_model": (
            "factor points and public source records; unique D2 points, symmetry-bound "
            "witnesses, multiplicities, and tags; tag directory; fixed-width route "
            "triples; and public hash parameters"
        ),
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": BASE.deep_size(
            {
                "factor_sources": factor_sources,
                "points": d2.points,
                "witnesses": d2.witnesses,
                "multiplicities": d2.multiplicities,
                "tags": tags,
                "buckets": bucket_contents,
                "routes": routes,
            }
        ),
        "tag_assignment_digest": stable_digest(tags),
        "multiplicity_by_tag_digest": stable_digest(multiplicity_tag),
        "witness_class_by_tag_digest": stable_digest(witness_class_tag),
        "route_digest": stable_digest(artifact["routes"]),
        "artifact_digest": stable_digest(artifact),
        "first_tags": tags[:8],
        "first_routes": artifact["routes"][:8],
        "tag_evaluations": len(d2.points),
        "route_compile_output_evaluations": pair_attempts,
        "route_compile_ops": asdict(route_build_ops),
        "route_coverage_audit_ops": asdict(coverage_audit_ops),
        "streaming_build": True,
        "materialized_d4_workspace_used_by_candidate": False,
        "null": null_record,
        "scalar_oracle_required": scalar_required,
        "hidden_scalar_metadata_emitted": False,
    }
    return SourceAdvice(
        source_tag=source_tag,
        variant_kind=variant_kind,
        witness_policy=d2.witness_policy,
        tag_count=tag_count,
        output_router=output_router_name,
        output_seed=output_seed,
        tags=tags,
        bucket_contents=bucket_contents,
        routes=routes,
        record=record,
        scalar_oracle_required=scalar_required,
    )


def query_d4(
    curve: Any,
    q: int,
    target: Point,
    d2: SourceD2Support,
    advice: SourceAdvice,
    scalar_index: dict[Point, int] | None,
) -> dict[str, Any]:
    if advice.scalar_oracle_required != (scalar_index is not None):
        raise ValueError("query scalar-index boundary differs from advice eligibility")
    target_tag = output_bucket(
        advice.output_router,
        target,
        advice.tag_count,
        curve,
        q,
        advice.output_seed,
        scalar_index,
    )
    ops = Ops()
    route_probes = 0
    bucket_reads = 0
    tag_reads = 0
    point_reads = 0
    witness_reads = 0
    witness: tuple[int, int, int, int] | None = None
    d2_pair: tuple[int, int] | None = None
    for left, left_point in enumerate(d2.points):
        route_probes += 1
        tag_reads += 1
        point_reads += 1
        right_tags = advice.routes.get((target_tag, advice.tags[left]), ())
        for right_tag in right_tags:
            bucket_reads += 1
            for right in advice.bucket_contents[right_tag]:
                point_reads += 1
                if curve.add(left_point, d2.points[right], ops) != target:
                    continue
                witness_reads += 2
                witness = tuple(sorted(d2.witnesses[left] + d2.witnesses[right]))
                d2_pair = (left, right)
                break
            if witness is not None:
                break
        if witness is not None:
            break
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    tag_bytes = max(1, math.ceil((advice.tag_count - 1).bit_length() / 8))
    factor_index_bytes = max(
        1,
        math.ceil(2 * max(1, max(index for pair in d2.witnesses for index in pair).bit_length()) / 8),
    )
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "d2_pair": list(d2_pair) if d2_pair is not None else None,
        "ops": asdict(ops),
        "route_probes": route_probes,
        "bucket_reads": bucket_reads,
        "tag_reads": tag_reads,
        "point_reads": point_reads,
        "witness_reads": witness_reads,
        "logical_point_bytes_read": point_reads * point_bytes,
        "logical_tag_bytes_read": (tag_reads + bucket_reads) * tag_bytes,
        "logical_route_bytes_read": (
            2 * route_probes + bucket_reads
        ) * tag_bytes,
        "logical_witness_bytes_read": witness_reads * factor_index_bytes,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
        "target_output_tag": target_tag,
    }


def query_d5(
    curve: Any,
    q: int,
    target: Point,
    factor_points: list[Point],
    d2: SourceD2Support,
    advice: SourceAdvice,
    scalar_index: dict[Point, int] | None,
) -> dict[str, Any]:
    outer_ops = Ops()
    inner_ops = asdict(Ops())
    totals = {
        "route_probes": 0,
        "bucket_reads": 0,
        "tag_reads": 0,
        "point_reads": 0,
        "witness_reads": 0,
        "logical_point_bytes_read": 0,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": 0,
        "logical_witness_bytes_read": 0,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
    }
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness: tuple[int, ...] | None = None
    final_index: int | None = None
    for index, final_point in enumerate(factor_points):
        totals["point_reads"] += 1
        totals["logical_point_bytes_read"] += point_bytes
        totals["outer_factor_point_reads"] += 1
        totals["outer_factor_logical_bytes_read"] += point_bytes
        partial_target = curve.add(target, curve.neg(final_point), outer_ops)
        result = query_d4(curve, q, partial_target, d2, advice, scalar_index)
        inner_ops = sum_ops(inner_ops, result["ops"])
        for key in totals:
            totals[key] += result[key]
        if not result["success"]:
            continue
        witness = tuple(sorted(tuple(result["witness"]) + (index,)))
        final_index = index
        break
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "final_index": final_index,
        "outer_ops": asdict(outer_ops),
        "inner_ops": inner_ops,
        "ops": sum_ops(asdict(outer_ops), inner_ops),
        **totals,
    }


def query_d2_complement_d4(
    curve: Any,
    target: Point,
    d2: SourceD2Support,
) -> dict[str, Any]:
    ops = Ops()
    probes = 0
    point_reads = 0
    witness_reads = 0
    witness: tuple[int, int, int, int] | None = None
    d2_pair: tuple[int, int] | None = None
    for left, left_point in enumerate(d2.points):
        probes += 1
        point_reads += 1
        complement = curve.add(target, curve.neg(left_point), ops)
        right = d2.point_to_index.get(complement)
        if right is None:
            continue
        point_reads += 1
        witness_reads = 2
        witness = tuple(sorted(d2.witnesses[left] + d2.witnesses[right]))
        d2_pair = (left, right)
        break
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    factor_index_bytes = max(
        1,
        math.ceil(
            2
            * max(
                1,
                max(index for pair in d2.witnesses for index in pair).bit_length(),
            )
            / 8
        ),
    )
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "d2_pair": list(d2_pair) if d2_pair is not None else None,
        "ops": asdict(ops),
        "route_probes": probes,
        "bucket_reads": probes,
        "tag_reads": 0,
        "point_reads": point_reads,
        "witness_reads": witness_reads,
        "logical_point_bytes_read": point_reads * point_bytes,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": 0,
        "logical_witness_bytes_read": witness_reads * factor_index_bytes,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
    }


def query_d2_complement_d5(
    curve: Any,
    target: Point,
    factor_points: list[Point],
    d2: SourceD2Support,
) -> dict[str, Any]:
    outer_ops = Ops()
    inner_ops = asdict(Ops())
    totals = {
        "route_probes": 0,
        "bucket_reads": 0,
        "tag_reads": 0,
        "point_reads": 0,
        "witness_reads": 0,
        "logical_point_bytes_read": 0,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": 0,
        "logical_witness_bytes_read": 0,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
    }
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness: tuple[int, ...] | None = None
    for final_index, final_point in enumerate(factor_points):
        totals["point_reads"] += 1
        totals["logical_point_bytes_read"] += point_bytes
        totals["outer_factor_point_reads"] += 1
        totals["outer_factor_logical_bytes_read"] += point_bytes
        partial_target = curve.add(target, curve.neg(final_point), outer_ops)
        result = query_d2_complement_d4(curve, partial_target, d2)
        inner_ops = sum_ops(inner_ops, result["ops"])
        for key in totals:
            totals[key] += result[key]
        if result["success"]:
            witness = tuple(sorted(tuple(result["witness"]) + (final_index,)))
            break
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "ops": sum_ops(asdict(outer_ops), inner_ops),
        "outer_ops": asdict(outer_ops),
        "inner_ops": inner_ops,
        **totals,
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
        if type(index) is not int or not 0 <= index < len(factor_points):
            return False, asdict(ops)
        recovered = curve.add(recovered, factor_points[index], ops)
    return recovered == target, asdict(ops)


def deterministic_sample(values: list[Point], count: int, seed: int) -> list[Point]:
    if count >= len(values):
        return list(values)
    rng = random.Random(seed)
    return [values[index] for index in rng.sample(range(len(values)), count)]


def build_target_schedules(
    curve: Any,
    q: int,
    generator: Point,
    d4_points: list[Point],
    d5_points: list[Point],
    sample_count: int,
    seed: int,
) -> tuple[dict[str, list[Point]], dict[str, int]]:
    generation_ops = Ops()
    rng = random.Random(seed ^ 0x13198A2E)
    random_targets = [
        curve.mul(rng.randrange(q), generator, generation_ops)
        for _ in range(sample_count)
    ]
    return {
        "supported_d4": deterministic_sample(
            d4_points, sample_count, seed ^ 0x243F6A88
        ),
        "supported_d5": deterministic_sample(
            d5_points, sample_count, seed ^ 0x85A308D3
        ),
        "random_d5": random_targets,
    }, asdict(generation_ops)


def summarize_query_records(
    records: list[dict[str, Any]],
    require_success: bool,
) -> dict[str, Any]:
    if require_success and not all(record["success"] for record in records):
        raise AssertionError("compiled join missed a supported target")
    if any(record["success"] and not record["verified"] for record in records):
        raise AssertionError("compiled join returned an invalid witness")
    metric_keys = [
        "route_probes",
        "bucket_reads",
        "tag_reads",
        "point_reads",
        "witness_reads",
        "logical_point_bytes_read",
        "logical_tag_bytes_read",
        "logical_route_bytes_read",
        "logical_witness_bytes_read",
        "outer_factor_point_reads",
        "outer_factor_logical_bytes_read",
    ]
    summary = {
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
        "records": records,
    }
    for key in metric_keys:
        summary[f"average_{key}"] = mean_or_zero([record[key] for record in records])
        summary[f"maximum_{key}"] = max(record[key] for record in records)
    return summary


def run_query_samples(
    curve: Any,
    q: int,
    factor_points: list[Point],
    d2: SourceD2Support,
    advice: SourceAdvice,
    schedules: dict[str, list[Point]],
    scalar_index: dict[Point, int] | None,
) -> dict[str, Any]:
    verification_ops = asdict(Ops())

    def run_d4(targets: list[Point]) -> list[dict[str, Any]]:
        nonlocal verification_ops
        records = []
        for target in targets:
            result = query_d4(curve, q, target, d2, advice, scalar_index)
            verified, audit_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            verification_ops = sum_ops(verification_ops, audit_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records.append(result)
        return records

    def run_d5(targets: list[Point]) -> list[dict[str, Any]]:
        nonlocal verification_ops
        records = []
        for target in targets:
            result = query_d5(
                curve, q, target, factor_points, d2, advice, scalar_index
            )
            verified, audit_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            verification_ops = sum_ops(verification_ops, audit_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records.append(result)
        return records

    supported_d4 = run_d4(schedules["supported_d4"])
    supported_d5 = run_d5(schedules["supported_d5"])
    random_d5 = run_d5(schedules["random_d5"])
    return {
        "supported_d4": summarize_query_records(supported_d4, True),
        "supported_d5": summarize_query_records(supported_d5, True),
        "random_d5": summarize_query_records(random_d5, False),
        "witness_verification_audit_ops": verification_ops,
    }


def d2_complement_advice_record(
    curve: Any,
    factor_points: list[Point],
    d2: SourceD2Support,
) -> dict[str, Any]:
    point_bits = 1 + 2 * curve.p.bit_length()
    factor_index_bits = max(1, (len(factor_points) - 1).bit_length())
    multiplicity_bits = max(1, max(d2.multiplicities).bit_length())
    payload_bits = len(factor_points) * point_bits + len(d2.points) * (
        point_bits + 2 * factor_index_bits + multiplicity_bits
    )
    artifact = {
        "factor_points": [BASE.point_json(point) for point in factor_points],
        "d2": [
            {
                "point": BASE.point_json(point),
                "witness": list(witness),
                "multiplicity": multiplicity,
            }
            for point, witness, multiplicity in zip(
                d2.points, d2.witnesses, d2.multiplicities
            )
        ],
    }
    return {
        "payload_bit_lower_estimate": payload_bits,
        "payload_model": (
            "factor points plus exact D2 point keys, symmetry-bound pair witnesses, "
            "and multiplicities; expected constant-time exact point dictionary"
        ),
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": BASE.deep_size(
            {
                "factor_points": factor_points,
                "d2_points": d2.points,
                "d2_witnesses": d2.witnesses,
                "d2_multiplicities": d2.multiplicities,
                "point_to_index": d2.point_to_index,
            }
        ),
        "artifact_digest": stable_digest(artifact),
        "support_size": len(d2.points),
    }


def run_d2_complement_samples(
    curve: Any,
    factor_points: list[Point],
    d2: SourceD2Support,
    schedules: dict[str, list[Point]],
) -> dict[str, Any]:
    verification_ops = asdict(Ops())
    records_by_name: dict[str, list[dict[str, Any]]] = {}
    for name in ("supported_d4", "supported_d5", "random_d5"):
        records_by_name[name] = []
        for target in schedules[name]:
            if name == "supported_d4":
                result = query_d2_complement_d4(curve, target, d2)
            else:
                result = query_d2_complement_d5(curve, target, factor_points, d2)
            verified, audit_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            verification_ops = sum_ops(verification_ops, audit_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records_by_name[name].append(result)
    return {
        "supported_d4": summarize_query_records(
            records_by_name["supported_d4"], True
        ),
        "supported_d5": summarize_query_records(
            records_by_name["supported_d5"], True
        ),
        "random_d5": summarize_query_records(records_by_name["random_d5"], False),
        "witness_verification_audit_ops": verification_ops,
    }


def materialized_query_d4(
    curve: Any,
    factor_points: list[Point],
    mapping: dict[Point, list[tuple[int, int, int, int]]],
    target: Point,
) -> dict[str, Any]:
    bucket = mapping.get(target)
    witness = list(bucket[0]) if bucket else None
    verified, audit_ops = verify_factor_witness(curve, factor_points, witness, target)
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness_bytes = math.ceil(
        4 * max(1, (len(factor_points) - 1).bit_length()) / 8
    )
    return {
        "success": witness is not None,
        "witness": witness,
        "verified": verified if witness is not None else None,
        "ops": asdict(Ops()),
        "route_probes": 1,
        "bucket_reads": int(bucket is not None),
        "tag_reads": 0,
        "point_reads": 0,
        "witness_reads": int(bucket is not None),
        "logical_point_bytes_read": point_bytes,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": point_bytes,
        "logical_witness_bytes_read": witness_bytes if bucket else 0,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
        "target": BASE.point_json(target),
        "witness_verification_audit_ops": audit_ops,
    }


def materialized_query_d5(
    curve: Any,
    factor_points: list[Point],
    mapping: dict[Point, list[tuple[int, int, int, int]]],
    target: Point,
) -> dict[str, Any]:
    query = BASE.query_target(curve, target, factor_points, mapping, 1)
    witness = list(query["relations"][0]) if query["relations"] else None
    verified, audit_ops = verify_factor_witness(curve, factor_points, witness, target)
    return {
        "success": witness is not None,
        "witness": witness,
        "verified": verified if witness is not None else None,
        "ops": asdict(query["ops"]),
        "route_probes": query["probes"],
        "bucket_reads": query["probes"],
        "tag_reads": 0,
        "point_reads": query["probes"],
        "witness_reads": query["witness_reads"],
        "logical_point_bytes_read": query["logical_key_bytes_read"]
        + query["probes"] * math.ceil((1 + 2 * curve.p.bit_length()) / 8),
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": query["logical_key_bytes_read"],
        "logical_witness_bytes_read": query["logical_witness_bytes_read"],
        "outer_factor_point_reads": query["probes"],
        "outer_factor_logical_bytes_read": query["probes"]
        * math.ceil((1 + 2 * curve.p.bit_length()) / 8),
        "target": BASE.point_json(target),
        "witness_verification_audit_ops": sum_ops(
            asdict(query["witness_verification_audit_ops"]), audit_ops
        ),
    }


def run_materialized_samples(
    curve: Any,
    factor_points: list[Point],
    mapping: dict[Point, list[tuple[int, int, int, int]]],
    schedules: dict[str, list[Point]],
) -> dict[str, Any]:
    verification_ops = asdict(Ops())
    d4_records = []
    for target in schedules["supported_d4"]:
        record = materialized_query_d4(curve, factor_points, mapping, target)
        verification_ops = sum_ops(
            verification_ops, record.pop("witness_verification_audit_ops")
        )
        d4_records.append(record)
    d5_records: dict[str, list[dict[str, Any]]] = {}
    for name in ("supported_d5", "random_d5"):
        d5_records[name] = []
        for target in schedules[name]:
            record = materialized_query_d5(curve, factor_points, mapping, target)
            verification_ops = sum_ops(
                verification_ops, record.pop("witness_verification_audit_ops")
            )
            d5_records[name].append(record)
    return {
        "supported_d4": summarize_query_records(d4_records, True),
        "supported_d5": summarize_query_records(d5_records["supported_d5"], True),
        "random_d5": summarize_query_records(d5_records["random_d5"], False),
        "witness_verification_audit_ops": verification_ops,
    }


def hybrid_query_d4(
    curve: Any,
    factor_points: list[Point],
    cache: dict[Point, tuple[int, int, int, int]],
    target: Point,
    d2: SourceD2Support,
) -> dict[str, Any]:
    cached = cache.get(target)
    if cached is None:
        result = query_d2_complement_d4(curve, target, d2)
        result["route_probes"] += 1
        result["bucket_reads"] += 1
        point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
        result["logical_route_bytes_read"] += point_bytes
        return result
    witness = list(cached)
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness_bytes = math.ceil(
        4 * max(1, (len(factor_points) - 1).bit_length()) / 8
    )
    return {
        "success": True,
        "witness": witness,
        "d2_pair": None,
        "ops": asdict(Ops()),
        "route_probes": 1,
        "bucket_reads": 1,
        "tag_reads": 0,
        "point_reads": 0,
        "witness_reads": 1,
        "logical_point_bytes_read": point_bytes,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": point_bytes,
        "logical_witness_bytes_read": witness_bytes,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
    }


def hybrid_query_d5(
    curve: Any,
    factor_points: list[Point],
    cache: dict[Point, tuple[int, int, int, int]],
    target: Point,
    d2: SourceD2Support,
) -> dict[str, Any]:
    outer_ops = Ops()
    inner_ops = asdict(Ops())
    totals = {
        "route_probes": 0,
        "bucket_reads": 0,
        "tag_reads": 0,
        "point_reads": 0,
        "witness_reads": 0,
        "logical_point_bytes_read": 0,
        "logical_tag_bytes_read": 0,
        "logical_route_bytes_read": 0,
        "logical_witness_bytes_read": 0,
        "outer_factor_point_reads": 0,
        "outer_factor_logical_bytes_read": 0,
    }
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness: tuple[int, ...] | None = None
    for final_index, final_point in enumerate(factor_points):
        totals["point_reads"] += 1
        totals["logical_point_bytes_read"] += point_bytes
        totals["outer_factor_point_reads"] += 1
        totals["outer_factor_logical_bytes_read"] += point_bytes
        partial_target = curve.add(target, curve.neg(final_point), outer_ops)
        result = hybrid_query_d4(curve, factor_points, cache, partial_target, d2)
        inner_ops = sum_ops(inner_ops, result["ops"])
        for key in totals:
            totals[key] += result[key]
        if result["success"]:
            witness = tuple(sorted(tuple(result["witness"]) + (final_index,)))
            break
    return {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "ops": sum_ops(asdict(outer_ops), inner_ops),
        "outer_ops": asdict(outer_ops),
        "inner_ops": inner_ops,
        **totals,
    }


def build_hybrid_cache(
    curve: Any,
    factor_points: list[Point],
    d2: SourceD2Support,
    materialized_mapping: dict[Point, list[tuple[int, int, int, int]]],
    payload_budget_bits: int,
    seed: int,
) -> tuple[dict[Point, tuple[int, int, int, int]], dict[str, Any]]:
    d2_record = d2_complement_advice_record(curve, factor_points, d2)
    point_bits = 1 + 2 * curve.p.bit_length()
    factor_index_bits = max(1, (len(factor_points) - 1).bit_length())
    entry_bits = point_bits + 4 * factor_index_bits + 1
    available = max(0, payload_budget_bits - d2_record["payload_bit_lower_estimate"])
    capacity = min(len(materialized_mapping), available // entry_bits)
    width = max(1, math.ceil(curve.p.bit_length() / 8))

    def rank(point: Point) -> tuple[bytes, tuple[int, int, int]]:
        if point is None:
            encoded = b"\x00" + b"\x00" * (2 * width)
        else:
            encoded = (
                b"\x01"
                + point[0].to_bytes(width, "big")
                + point[1].to_bytes(width, "big")
            )
        return (
            hashlib.sha256(seed.to_bytes(16, "big", signed=False) + encoded).digest(),
            BASE.point_sort_key(point),
        )

    selected = sorted(materialized_mapping, key=rank)[:capacity]
    cache = {point: materialized_mapping[point][0] for point in selected}
    payload_bits = d2_record["payload_bit_lower_estimate"] + capacity * entry_bits
    artifact = {
        "d2_artifact_digest": d2_record["artifact_digest"],
        "cache": [
            {
                "point": BASE.point_json(point),
                "witness": list(cache[point]),
            }
            for point in sorted(cache, key=BASE.point_sort_key)
        ],
    }
    return cache, {
        "policy": "public_sha256_ranked_d4_cache_with_exact_d2_fallback",
        "seed": seed,
        "capacity": capacity,
        "d4_support_size": len(materialized_mapping),
        "cache_fraction": capacity / len(materialized_mapping),
        "entry_bits": entry_bits,
        "payload_bit_lower_estimate": payload_bits,
        "payload_budget_bits": payload_budget_bits,
        "within_payload_budget": payload_bits <= payload_budget_bits,
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": BASE.deep_size(
            {"d2": d2.point_to_index, "witnesses": d2.witnesses, "cache": cache}
        ),
        "artifact_digest": stable_digest(artifact),
    }


def run_hybrid_samples(
    curve: Any,
    factor_points: list[Point],
    d2: SourceD2Support,
    cache: dict[Point, tuple[int, int, int, int]],
    schedules: dict[str, list[Point]],
) -> dict[str, Any]:
    verification_ops = asdict(Ops())
    records_by_name: dict[str, list[dict[str, Any]]] = {}
    for name in ("supported_d4", "supported_d5", "random_d5"):
        records_by_name[name] = []
        for target in schedules[name]:
            if name == "supported_d4":
                result = hybrid_query_d4(curve, factor_points, cache, target, d2)
            else:
                result = hybrid_query_d5(curve, factor_points, cache, target, d2)
            verified, audit_ops = verify_factor_witness(
                curve, factor_points, result["witness"], target
            )
            verification_ops = sum_ops(verification_ops, audit_ops)
            result.update(
                {
                    "target": BASE.point_json(target),
                    "verified": verified if result["success"] else None,
                }
            )
            records_by_name[name].append(result)
    return {
        "supported_d4": summarize_query_records(
            records_by_name["supported_d4"], True
        ),
        "supported_d5": summarize_query_records(
            records_by_name["supported_d5"], True
        ),
        "random_d5": summarize_query_records(records_by_name["random_d5"], False),
        "witness_verification_audit_ops": verification_ops,
    }


def build_descent_schedule(
    curve: Any,
    q: int,
    generator: Point,
    seed: int,
    challenge_count: int,
    attempt_limit: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rng = random.Random(seed ^ 0x1F83D9AB)
    generation_ops = Ops()
    schedule = []
    for challenge_index in range(challenge_count):
        scalar = rng.randrange(q)
        target = curve.mul(scalar, generator, generation_ops)
        attempt_rng = random.Random(seed ^ (challenge_index + 1) * 0x9E3779B1)
        schedule.append(
            {
                "challenge_index": challenge_index,
                "known_scalar_private_audit": scalar,
                "target": target,
                "offsets": [attempt_rng.randrange(q) for _ in range(attempt_limit)],
            }
        )
    return schedule, asdict(generation_ops)


def run_descent(
    curve: Any,
    q: int,
    generator: Point,
    factor_logs: list[int],
    schedule: list[dict[str, Any]],
    query: Callable[[Point], dict[str, Any]],
) -> dict[str, Any]:
    verification_ops = Ops()
    challenges = []
    for item in schedule:
        attack_ops = asdict(Ops())
        recovered: int | None = None
        witness: list[int] | None = None
        attempts = 0
        metrics = {
            "route_probes": 0,
            "bucket_reads": 0,
            "tag_reads": 0,
            "point_reads": 0,
            "witness_reads": 0,
            "logical_point_bytes_read": 0,
            "logical_tag_bytes_read": 0,
            "logical_route_bytes_read": 0,
            "logical_witness_bytes_read": 0,
            "outer_factor_point_reads": 0,
            "outer_factor_logical_bytes_read": 0,
        }
        for attempts, offset in enumerate(item["offsets"], start=1):
            randomization_ops = Ops()
            shifted = curve.add(
                item["target"],
                curve.mul(offset, generator, randomization_ops),
                randomization_ops,
            )
            result = query(shifted)
            attack_ops = sum_ops(attack_ops, asdict(randomization_ops), result["ops"])
            for key in metrics:
                metrics[key] += result[key]
            if not result["success"]:
                continue
            witness = result["witness"]
            recovered = (sum(factor_logs[index] for index in witness) - offset) % q
            break
        verified = (
            recovered is not None
            and recovered == item["known_scalar_private_audit"]
            and curve.mul(recovered, generator, verification_ops) == item["target"]
        )
        challenges.append(
            {
                "challenge_index": item["challenge_index"],
                "target": BASE.point_json(item["target"]),
                "known_scalar_private_audit": item["known_scalar_private_audit"],
                "offset_schedule_digest": stable_digest(item["offsets"]),
                "attempts": attempts,
                "success": recovered is not None,
                "witness": witness,
                "recovered_scalar": recovered,
                "verified": verified,
                "attack_ops": attack_ops,
                **metrics,
            }
        )
    return {
        "challenge_count": len(schedule),
        "attempt_limit": len(schedule[0]["offsets"]) if schedule else 0,
        "challenges": challenges,
        "all_challenges_solved": all(challenge["success"] for challenge in challenges),
        "all_successes_verified": all(
            not challenge["success"] or challenge["verified"] for challenge in challenges
        ),
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
        "verification_audit_ops": asdict(verification_ops),
        "factor_logs_source": (
            "private exhaustive toy audit standing in for the independently verified "
            "relation solver retained from EXP-ECDLP-FIXED-COMPILER-001"
        ),
    }


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_source_signal_gate(candidate: dict[str, Any]) -> bool:
    comparisons = candidate["ratios_to_matched_nulls"]

    def all_ratios_at_most(key: str, threshold: float) -> bool:
        return all(
            comparison[key] is not None and comparison[key] <= threshold
            for comparison in comparisons
        )

    return (
        candidate["null_invariants_passed"]
        and candidate["scalar_calibration_passed"]
        and all(
            comparison["null_moved_fraction"] >= 0.5
            for comparison in comparisons
        )
        and not candidate["advice"]["route_universe_saturated"]
        and all_ratios_at_most("payload_bits", 0.8)
        and all_ratios_at_most("route_triples", 0.8)
        and all_ratios_at_most("supported_d4_point_reads", 0.8)
        and all_ratios_at_most("supported_d4_group_operations", 0.8)
        and all_ratios_at_most("supported_d5_point_reads", 0.8)
        and all_ratios_at_most("supported_d5_group_operations", 0.8)
        and all_ratios_at_most("random_d5_point_reads", 0.8)
        and all_ratios_at_most("random_d5_group_operations", 0.8)
        and all_ratios_at_most("canonical_serialized_bytes", 1.25)
        and all_ratios_at_most("python_deep_bytes", 1.25)
    )


def compile_family(
    curve_record: dict[str, Any],
    family: str,
    factor_size: int,
    family_seed: int,
    target_seed: int,
    witness_policies: list[str],
    source_tags: list[str],
    tag_counts: list[int],
    output_routers: list[str],
    null_seeds: list[int],
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
    factor_sources = public_factor_sources(factor_base, curve)
    factor_logs = [scalar_index[point] for point in factor_points]

    policy_objects: dict[str, tuple[SourceD2Support, Any]] = {}
    d2_support_reference: set[Point] | None = None
    d4_support_reference: set[Point] | None = None
    for policy_index, policy in enumerate(witness_policies):
        witness_seed = (
            family_seed ^ (policy_index + 1) * 0xD1B54A32D192ED03
        ) & ((1 << 128) - 1)
        d2 = build_source_d2(curve, factor_points, policy, witness_seed)
        d4 = PRE.build_d4(curve, d2)
        current_d2 = set(d2.points)
        current_d4 = set(d4.points)
        if d2_support_reference is None:
            d2_support_reference = current_d2
            d4_support_reference = current_d4
        elif current_d2 != d2_support_reference or current_d4 != d4_support_reference:
            raise AssertionError("witness policy changed exact D2 or D4 support")
        policy_objects[policy] = (d2, d4)

    first_d2, first_d4 = policy_objects[witness_policies[0]]
    d5_support, d5_build_ops = PRE.build_d5_support(curve, factor_points, first_d4)
    d5_points = sorted(d5_support, key=BASE.point_sort_key)
    schedules, target_generation_ops = build_target_schedules(
        curve,
        q,
        generator,
        first_d4.points,
        d5_points,
        query_samples,
        target_seed,
    )
    descent_schedule, challenge_generation_ops = build_descent_schedule(
        curve,
        q,
        generator,
        target_seed,
        descent_challenges,
        descent_attempt_limit,
    )

    materialized = BASE.compile_four_sum_advice(curve, factor_points, 1)
    if set(materialized.mapping) != set(first_d4.points):
        raise AssertionError("D2+D2 support differs from materialized D4")
    materialized_samples = run_materialized_samples(
        curve, factor_points, materialized.mapping, schedules
    )
    materialized_descent = run_descent(
        curve,
        q,
        generator,
        factor_logs,
        descent_schedule,
        lambda target: materialized_query_d5(
            curve, factor_points, materialized.mapping, target
        ),
    )
    factor_log_bits = len(factor_points) * q.bit_length()
    materialized_full_advice_bits = (
        materialized.record["payload_bit_lower_estimate"] + factor_log_bits
    )
    d2_complement_baselines: dict[str, dict[str, Any]] = {}
    for policy in witness_policies:
        policy_d2, _ = policy_objects[policy]
        d2_advice = d2_complement_advice_record(curve, factor_points, policy_d2)
        d2_samples = run_d2_complement_samples(
            curve, factor_points, policy_d2, schedules
        )
        d2_descent = run_descent(
            curve,
            q,
            generator,
            factor_logs,
            descent_schedule,
            lambda target, selected_d2=policy_d2: query_d2_complement_d5(
                curve, target, factor_points, selected_d2
            ),
        )
        d2_complement_baselines[policy] = {
            "witness_policy": policy,
            "advice": d2_advice,
            "full_online_advice_bits": d2_advice["payload_bit_lower_estimate"]
            + factor_log_bits,
            "query_samples": d2_samples,
            "descent": d2_descent,
            "offline_attack_group_ops": factor_base["build_ops"]["group_operations"]
            + policy_d2.build_ops.group_operations,
        }

    bsgs_cache: dict[int, dict[str, Any]] = {}
    hybrid_baseline_cache: dict[tuple[str, int], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    control_rows: dict[tuple[str, int], dict[str, Any]] = {}

    def execute_row(
        d2: SourceD2Support,
        d4: Any,
        advice: SourceAdvice,
    ) -> dict[str, Any]:
        private_index = scalar_index if advice.scalar_oracle_required else None
        samples = run_query_samples(
            curve,
            q,
            factor_points,
            d2,
            advice,
            schedules,
            private_index,
        )
        descent = run_descent(
            curve,
            q,
            generator,
            factor_logs,
            descent_schedule,
            lambda target: query_d5(
                curve,
                q,
                target,
                factor_points,
                d2,
                advice,
                private_index,
            ),
        )
        full_advice_bits = advice.record["payload_bit_lower_estimate"] + factor_log_bits
        if full_advice_bits not in bsgs_cache:
            bsgs_cache[full_advice_bits] = BASE.run_matched_bsgs_preprocessing(
                curve,
                q,
                generator,
                full_advice_bits,
                target_seed,
                descent_challenges,
            )
        bsgs = dict(bsgs_cache[full_advice_bits])
        hybrid_key = (d2.witness_policy, advice.record["payload_bit_lower_estimate"])
        if hybrid_key not in hybrid_baseline_cache:
            hybrid_cache, hybrid_advice = build_hybrid_cache(
                curve,
                factor_points,
                d2,
                materialized.mapping,
                advice.record["payload_bit_lower_estimate"],
                target_seed ^ 0x6A09E667,
            )
            hybrid_samples = run_hybrid_samples(
                curve, factor_points, d2, hybrid_cache, schedules
            )
            hybrid_descent = run_descent(
                curve,
                q,
                generator,
                factor_logs,
                descent_schedule,
                lambda target, selected_cache=hybrid_cache, selected_d2=d2: hybrid_query_d5(
                    curve,
                    factor_points,
                    selected_cache,
                    target,
                    selected_d2,
                ),
            )
            hybrid_baseline_cache[hybrid_key] = {
                "key": stable_digest(list(hybrid_key)),
                "witness_policy": d2.witness_policy,
                "advice": hybrid_advice,
                "full_online_advice_bits": hybrid_advice[
                    "payload_bit_lower_estimate"
                ]
                + factor_log_bits,
                "query_samples": hybrid_samples,
                "descent": hybrid_descent,
            }
        hybrid_baseline = hybrid_baseline_cache[hybrid_key]
        worst_case_d5_group_ops = len(factor_points) * (1 + len(d2.points) ** 2)
        shift_group_operation_bound = 2 * q.bit_length() + 1
        complete_descent_worst_case_group_ops = descent_attempt_limit * (
            shift_group_operation_bound + worst_case_d5_group_ops
        )
        candidate_query_average = samples["supported_d5"]["average_group_operations"]
        candidate_descent_average = descent["average_online_group_operations"]
        bsgs_average = bsgs["average_online_group_operations"]
        bsgs_worst = bsgs["worst_case_online_group_operation_bound"]
        materialized_average = materialized_samples["supported_d5"][
            "average_group_operations"
        ]
        d2_baseline = d2_complement_baselines[d2.witness_policy]
        d2_average = d2_baseline["query_samples"]["supported_d5"][
            "average_group_operations"
        ]
        hybrid_average = hybrid_baseline["query_samples"]["supported_d5"][
            "average_group_operations"
        ]
        materialized_descent_average = materialized_descent[
            "average_online_group_operations"
        ]
        d2_descent_average = d2_baseline["descent"][
            "average_online_group_operations"
        ]
        hybrid_descent_average = hybrid_baseline["descent"][
            "average_online_group_operations"
        ]
        decomposition_options = [
            ("d2_complement", d2_average),
            ("partial_d4_cache", hybrid_average),
        ]
        if materialized.record["payload_bit_lower_estimate"] <= advice.record[
            "payload_bit_lower_estimate"
        ]:
            decomposition_options.append(("materialized_d4", materialized_average))
        dlp_options = [
            ("d2_complement_descent", d2_descent_average),
            ("partial_d4_cache_descent", hybrid_descent_average),
            ("equal_advice_bsgs", bsgs_average),
        ]
        if materialized_full_advice_bits <= full_advice_bits:
            dlp_options.append(
                ("materialized_d4_descent", materialized_descent_average)
            )
        decomposition_envelope_average = min(value for _, value in decomposition_options)
        dlp_envelope_average = min(value for _, value in dlp_options)
        candidate_query_st2 = (
            advice.record["payload_bit_lower_estimate"]
            * max(1.0, candidate_query_average) ** 2
        )
        d2_query_st2 = d2_baseline["advice"][
            "payload_bit_lower_estimate"
        ] * max(1.0, d2_average) ** 2
        candidate_descent_st2 = (
            full_advice_bits * max(1.0, candidate_descent_average) ** 2
        )
        d2_descent_st2 = d2_baseline["full_online_advice_bits"] * max(
            1.0, d2_descent_average
        ) ** 2
        candidate_beats_materialized = (
            full_advice_bits < materialized_full_advice_bits
            and samples["supported_d5"]["average_group_operations"]
            < materialized_average
        )
        return {
            "source_tag": advice.source_tag,
            "variant_kind": advice.variant_kind,
            "witness_policy": advice.witness_policy,
            "tag_count": advice.tag_count,
            "output_router": advice.output_router,
            "eligibility": advice.record["eligibility"],
            "advice": advice.record,
            "query_samples": samples,
            "descent": descent,
            "full_online_advice_bits": full_advice_bits,
            "factor_base_log_advice_bits": factor_log_bits,
            "offline": {
                "factor_base_group_ops": factor_base["build_ops"]["group_operations"],
                "d2_group_ops": d2.build_ops.group_operations,
                "route_compile_group_ops": advice.record["route_compile_ops"][
                    "group_operations"
                ],
                "route_tag_evaluations": advice.record["tag_evaluations"],
                "route_output_evaluations": advice.record[
                    "route_compile_output_evaluations"
                ],
                "total_attack_group_ops": (
                    factor_base["build_ops"]["group_operations"]
                    + d2.build_ops.group_operations
                    + advice.record["route_compile_ops"]["group_operations"]
                ),
                "factor_base_charged_diagnostics": factor_base[
                    "charged_build_diagnostics"
                ],
                "full_d5_support_build_audit_ops": asdict(d5_build_ops),
                "materialized_d4_support_audit_ops": asdict(d4.build_ops),
                "route_coverage_audit_ops": advice.record[
                    "route_coverage_audit_ops"
                ],
            },
            "worst_case_d5_group_operation_bound": worst_case_d5_group_ops,
            "descent_worst_case": {
                "attempt_limit": descent_attempt_limit,
                "shift_group_operation_bound_per_attempt": shift_group_operation_bound,
                "d5_group_operation_bound_per_attempt": worst_case_d5_group_ops,
                "complete_group_operation_bound": complete_descent_worst_case_group_ops,
                "bound_model": (
                    "each attempt charges at most two group operations per scalar "
                    "bit, one target shift addition, and a complete D5 scan"
                ),
            },
            "matched_bsgs": {
                **bsgs,
                "candidate_to_bsgs_average_online_group_operation_ratio": ratio(
                    candidate_descent_average, bsgs_average
                ),
                "candidate_to_bsgs_worst_case_group_operation_ratio": ratio(
                    complete_descent_worst_case_group_ops, bsgs_worst
                ),
                "candidate_online_dominates_at_equal_advice": (
                    candidate_descent_average < bsgs_average
                    and complete_descent_worst_case_group_ops < bsgs_worst
                ),
            },
            "materialized_comparison": {
                "candidate_to_materialized_full_advice_ratio": ratio(
                    full_advice_bits, materialized_full_advice_bits
                ),
                "candidate_to_materialized_supported_d5_group_operation_ratio": ratio(
                    samples["supported_d5"]["average_group_operations"],
                    materialized_average,
                ),
                "candidate_has_lower_advice_and_online_work": candidate_beats_materialized,
            },
            "d2_complement_comparison": {
                "candidate_to_d2_full_advice_ratio": ratio(
                    full_advice_bits, d2_baseline["full_online_advice_bits"]
                ),
                "candidate_to_d2_supported_d5_group_operation_ratio": ratio(
                    samples["supported_d5"]["average_group_operations"],
                    d2_average,
                ),
                "candidate_to_d2_query_st2_diagnostic_ratio": ratio(
                    candidate_query_st2, d2_query_st2
                ),
                "candidate_to_d2_descent_st2_diagnostic_ratio": ratio(
                    candidate_descent_st2, d2_descent_st2
                ),
                "candidate_has_lower_advice_and_online_work": (
                    full_advice_bits < d2_baseline["full_online_advice_bits"]
                    and samples["supported_d5"]["average_group_operations"]
                    < d2_average
                ),
            },
            "partial_d4_comparison": {
                "baseline_key": hybrid_baseline["key"],
                "cache_capacity": hybrid_baseline["advice"]["capacity"],
                "candidate_to_hybrid_full_advice_ratio": ratio(
                    full_advice_bits, hybrid_baseline["full_online_advice_bits"]
                ),
                "candidate_to_hybrid_supported_d5_group_operation_ratio": ratio(
                    candidate_query_average, hybrid_average
                ),
                "candidate_to_hybrid_descent_group_operation_ratio": ratio(
                    candidate_descent_average, hybrid_descent_average
                ),
                "hybrid_uses_no_more_advice": (
                    hybrid_baseline["full_online_advice_bits"] <= full_advice_bits
                ),
                "candidate_query_beats_hybrid_using_no_more_advice": (
                    hybrid_baseline["full_online_advice_bits"] <= full_advice_bits
                    and candidate_query_average < hybrid_average
                ),
                "candidate_descent_beats_hybrid_using_no_more_advice": (
                    hybrid_baseline["full_online_advice_bits"] <= full_advice_bits
                    and candidate_descent_average < hybrid_descent_average
                ),
            },
            "decomposition_envelope": {
                "supported_d5_group_operations": decomposition_envelope_average,
                "candidate_to_envelope_ratio": ratio(
                    candidate_query_average,
                    decomposition_envelope_average,
                ),
                "includes": [
                    name for name, _ in decomposition_options
                ],
                "excluded_for_advice": (
                    []
                    if any(name == "materialized_d4" for name, _ in decomposition_options)
                    else ["materialized_d4"]
                ),
            },
            "dlp_envelope": {
                "average_online_group_operations": dlp_envelope_average,
                "candidate_to_envelope_ratio": ratio(
                    candidate_descent_average,
                    dlp_envelope_average,
                ),
                "includes": [name for name, _ in dlp_options],
                "excluded_for_advice": (
                    []
                    if any(
                        name == "materialized_d4_descent" for name, _ in dlp_options
                    )
                    else ["materialized_d4_descent"]
                ),
            },
            "ratios_to_matched_nulls": None,
            "scalar_calibration_passed": False,
            "null_invariants_passed": None,
            "instance_signal_gate_passed": False,
            "source_signal_gate_passed": False,
            "compiler_gate_passed": False,
            "routing_gate_passed": False,
            "compiler_routing_gate_passed": False,
            "rho_comparison": None,
            "claim_boundary": (
                "source-tag development preflight only; relation collection and "
                "factor logs are inherited audit surfaces, not an exponent claim"
            ),
        }

    for policy in witness_policies:
        d2, d4 = policy_objects[policy]
        for tag_count in tag_counts:
            control_seed = (
                family_seed ^ tag_count * 0xA4093822 ^ 0xC0DEC0DE
            ) & ((1 << 128) - 1)
            control_advice = compile_source_advice(
                curve,
                q,
                factor_points,
                factor_sources,
                d2,
                POSITIVE_CONTROL,
                "positive_control",
                scalar_tag_assignment(d2, scalar_index, q, tag_count),
                tag_count,
                POSITIVE_CONTROL,
                control_seed,
                None,
                scalar_index,
            )
            control_row = execute_row(d2, d4, control_advice)
            rows.append(control_row)
            control_rows[(policy, tag_count)] = control_row

        for output_index, output_router_name in enumerate(output_routers):
            for tag_count in tag_counts:
                output_seed = (
                    family_seed
                    ^ tag_count * 0xA4093822
                    ^ (output_index + 1) * 0x299F31D0
                ) & ((1 << 128) - 1)
                for source_tag in source_tags:
                    candidate_tags = candidate_tag_assignment(
                        source_tag, d2, factor_sources, tag_count
                    )
                    candidate_advice = compile_source_advice(
                        curve,
                        q,
                        factor_points,
                        factor_sources,
                        d2,
                        source_tag,
                        "candidate",
                        candidate_tags,
                        tag_count,
                        output_router_name,
                        output_seed,
                        None,
                        None,
                    )
                    rows.append(execute_row(d2, d4, candidate_advice))
                    for null_seed in null_seeds:
                        margin_tags, margin_record = shuffled_tag_assignment(
                            candidate_tags, d2, null_seed
                        )
                        margin_advice = compile_source_advice(
                            curve,
                            q,
                            factor_points,
                            factor_sources,
                            d2,
                            source_tag,
                            "margin_null",
                            margin_tags,
                            tag_count,
                            output_router_name,
                            output_seed,
                            margin_record,
                            None,
                        )
                        rows.append(execute_row(d2, d4, margin_advice))
                        source_null_tags, permuted_sources, source_null_record = (
                            source_permuted_tag_assignment(
                                source_tag,
                                d2,
                                factor_sources,
                                tag_count,
                                null_seed,
                            )
                        )
                        source_null_advice = compile_source_advice(
                            curve,
                            q,
                            factor_points,
                            permuted_sources,
                            d2,
                            source_tag,
                            "source_null",
                            source_null_tags,
                            tag_count,
                            output_router_name,
                            output_seed,
                            source_null_record,
                            None,
                        )
                        rows.append(execute_row(d2, d4, source_null_advice))

    candidate_rows = [row for row in rows if row["variant_kind"] == "candidate"]
    for candidate in candidate_rows:
        matched = [
            row
            for row in rows
            if row["variant_kind"] in ("margin_null", "source_null")
            and row["witness_policy"] == candidate["witness_policy"]
            and row["source_tag"] == candidate["source_tag"]
            and row["tag_count"] == candidate["tag_count"]
            and row["output_router"] == candidate["output_router"]
        ]
        if len(matched) != 2 * len(null_seeds):
            raise AssertionError("candidate does not have the configured null count")
        margin_nulls = [row for row in matched if row["variant_kind"] == "margin_null"]
        source_nulls = [row for row in matched if row["variant_kind"] == "source_null"]
        margin_invariants = all(
            row["advice"]["tag_histogram"] == candidate["advice"]["tag_histogram"]
            and row["advice"]["multiplicity_by_tag_histogram"]
            == candidate["advice"]["multiplicity_by_tag_histogram"]
            and row["advice"]["witness_class_by_tag_histogram"]
            == candidate["advice"]["witness_class_by_tag_histogram"]
            and row["advice"]["null"]["tag_histogram_preserved"]
            and row["advice"]["null"]["multiplicity_by_tag_preserved"]
            and row["advice"]["null"]["witness_class_by_tag_preserved"]
            and row["advice"]["null"]["inversion_symmetry_preserved"]
            for row in margin_nulls
        )
        source_invariants = all(
            row["advice"]["null"]["source_multiset_preserved"]
            and row["advice"]["null"]["compositional_recompute"]
            and row["advice"]["null"]["inversion_symmetry_preserved"]
            for row in source_nulls
        )
        null_invariants = margin_invariants and source_invariants
        comparisons = []
        for null in matched:
            comparisons.append(
                {
                    "null_kind": null["advice"]["null"]["kind"],
                    "null_seed": null["advice"]["null"]["seed"],
                    "null_moved_fraction": (
                        null["advice"]["null"]["moved_fraction_of_movable_points"]
                        if null["variant_kind"] == "margin_null"
                        else null["advice"]["null"][
                            "moved_fraction_of_movable_fibers"
                        ]
                    ),
                    "payload_bits": ratio(
                        candidate["advice"]["payload_bit_lower_estimate"],
                        null["advice"]["payload_bit_lower_estimate"],
                    ),
                    "route_triples": ratio(
                        candidate["advice"]["distinct_route_triples"],
                        null["advice"]["distinct_route_triples"],
                    ),
                    "supported_d4_point_reads": ratio(
                        candidate["query_samples"]["supported_d4"][
                            "average_point_reads"
                        ],
                        null["query_samples"]["supported_d4"]["average_point_reads"],
                    ),
                    "supported_d4_group_operations": ratio(
                        candidate["query_samples"]["supported_d4"][
                            "average_group_operations"
                        ],
                        null["query_samples"]["supported_d4"][
                            "average_group_operations"
                        ],
                    ),
                    "supported_d5_point_reads": ratio(
                        candidate["query_samples"]["supported_d5"][
                            "average_point_reads"
                        ],
                        null["query_samples"]["supported_d5"]["average_point_reads"],
                    ),
                    "supported_d5_group_operations": ratio(
                        candidate["query_samples"]["supported_d5"][
                            "average_group_operations"
                        ],
                        null["query_samples"]["supported_d5"][
                            "average_group_operations"
                        ],
                    ),
                    "random_d5_point_reads": ratio(
                        candidate["query_samples"]["random_d5"][
                            "average_point_reads"
                        ],
                        null["query_samples"]["random_d5"]["average_point_reads"],
                    ),
                    "random_d5_group_operations": ratio(
                        candidate["query_samples"]["random_d5"][
                            "average_group_operations"
                        ],
                        null["query_samples"]["random_d5"][
                            "average_group_operations"
                        ],
                    ),
                    "canonical_serialized_bytes": ratio(
                        candidate["advice"]["canonical_serialized_bytes"],
                        null["advice"]["canonical_serialized_bytes"],
                    ),
                    "python_deep_bytes": ratio(
                        candidate["advice"]["python_deep_bytes"],
                        null["advice"]["python_deep_bytes"],
                    ),
                }
            )
        candidate["ratios_to_matched_nulls"] = comparisons
        candidate["null_invariants_passed"] = null_invariants
        control = control_rows[(candidate["witness_policy"], candidate["tag_count"])]
        candidate["scalar_calibration_passed"] = (
            control["advice"]["average_reverse_right_tag_width"]
            < candidate["advice"]["average_reverse_right_tag_width"]
            and control["query_samples"]["supported_d4"]["average_point_reads"]
            < candidate["query_samples"]["supported_d4"]["average_point_reads"]
        )

        candidate["source_signal_gate_passed"] = evaluate_source_signal_gate(candidate)
        candidate["instance_signal_gate_passed"] = candidate[
            "source_signal_gate_passed"
        ]
        candidate["compiler_gate_passed"] = (
            candidate["source_signal_gate_passed"]
            and candidate["descent"]["all_verified"]
            and candidate["d2_complement_comparison"][
                "candidate_to_d2_query_st2_diagnostic_ratio"
            ]
            is not None
            and candidate["d2_complement_comparison"][
                "candidate_to_d2_query_st2_diagnostic_ratio"
            ]
            <= 0.8
            and candidate["d2_complement_comparison"][
                "candidate_to_d2_descent_st2_diagnostic_ratio"
            ]
            is not None
            and candidate["d2_complement_comparison"][
                "candidate_to_d2_descent_st2_diagnostic_ratio"
            ]
            <= 0.8
            and candidate["partial_d4_comparison"][
                "candidate_query_beats_hybrid_using_no_more_advice"
            ]
            and candidate["partial_d4_comparison"][
                "candidate_descent_beats_hybrid_using_no_more_advice"
            ]
            and candidate["matched_bsgs"][
                "candidate_online_dominates_at_equal_advice"
            ]
            and candidate["decomposition_envelope"]["candidate_to_envelope_ratio"]
            is not None
            and candidate["decomposition_envelope"]["candidate_to_envelope_ratio"]
            <= 0.8
            and candidate["dlp_envelope"]["candidate_to_envelope_ratio"]
            is not None
            and candidate["dlp_envelope"]["candidate_to_envelope_ratio"]
            <= 0.8
        )

    policy_records = []
    for policy in witness_policies:
        d2, d4 = policy_objects[policy]
        policy_records.append(
            {
                "witness_policy": policy,
                "witness_seed": d2.witness_seed,
                "d2": {
                    "support_size": len(d2.points),
                    "attempts": d2.attempts,
                    "build_ops": asdict(d2.build_ops),
                    "maximum_multiplicity": max(d2.multiplicities),
                    "mean_multiplicity": statistics.fmean(d2.multiplicities),
                    "multiplicity_histogram": histogram(d2.multiplicities),
                    "inversion_orbit_count": sum(
                        int(index <= negative)
                        for index, negative in enumerate(d2.inversion_indices)
                    ),
                    "support_digest": stable_digest(
                        [BASE.point_json(point) for point in d2.points]
                    ),
                    "bound_witness_digest": stable_digest(d2.witnesses),
                    "all_witness_digest": stable_digest(d2.all_witnesses),
                },
                "d4": {
                    "support_size": len(d4.points),
                    "unordered_d2_pair_attempts": len(d4.pair_records),
                    "build_ops": asdict(d4.build_ops),
                    "maximum_d2_pair_multiplicity": max(d4.multiplicities.values()),
                    "mean_d2_pair_multiplicity": statistics.fmean(
                        d4.multiplicities.values()
                    ),
                    "support_digest": stable_digest(
                        [BASE.point_json(point) for point in d4.points]
                    ),
                },
                "all_witness_tag_diagnostics": [
                    all_witness_tag_diagnostic(
                        source_tag, d2, factor_sources, tag_count
                    )
                    for source_tag in source_tags
                    for tag_count in tag_counts
                ],
            }
        )

    return {
        "family": family,
        "factor_base": factor_base,
        "public_factor_sources": factor_sources,
        "factor_base_logs_private_audit_digest": stable_digest(factor_logs),
        "factor_base_logs_emitted": False,
        "policy_supports": policy_records,
        "d5": {
            "support_size": len(d5_support),
            "exact_success_probability": len(d5_support) / q,
            "build_audit_ops": asdict(d5_build_ops),
            "support_digest": stable_digest(
                [BASE.point_json(point) for point in d5_points]
            ),
        },
        "target_schedule": {
            "supported_d4_digest": stable_digest(
                [BASE.point_json(point) for point in schedules["supported_d4"]]
            ),
            "supported_d5_digest": stable_digest(
                [BASE.point_json(point) for point in schedules["supported_d5"]]
            ),
            "random_d5_digest": stable_digest(
                [BASE.point_json(point) for point in schedules["random_d5"]]
            ),
            "target_generation_audit_ops": target_generation_ops,
            "descent_schedule_digest": stable_digest(
                [
                    {
                        "target": BASE.point_json(item["target"]),
                        "offsets": item["offsets"],
                    }
                    for item in descent_schedule
                ]
            ),
            "challenge_generation_audit_ops": challenge_generation_ops,
        },
        "baselines": {
            "d2_complement": [
                d2_complement_baselines[policy] for policy in witness_policies
            ],
            "partial_d4": [
                hybrid_baseline_cache[key] for key in sorted(hybrid_baseline_cache)
            ],
            "materialized_d4": {
                "advice": materialized.record,
                "full_online_advice_bits": materialized_full_advice_bits,
                "query_samples": materialized_samples,
                "descent": materialized_descent,
            },
            "brute_pair_worst_d5_group_operations": len(factor_points)
            * (1 + len(first_d2.points) ** 2),
        },
        "rows": rows,
    }


def attach_aggregate_routing(
    instances: list[dict[str, Any]],
    bit_sizes: list[int],
    seeds: list[int],
    witness_policies: list[str],
) -> dict[str, Any]:
    passing: dict[tuple[str, str, str, int, str, int], set[int]] = {}
    compiler_passing: dict[tuple[str, str, str, int, str, int], set[int]] = {}
    for instance in instances:
        bits = instance["curve"]["bits"]
        seed = instance["seed"]
        for family in instance["families"]:
            for row in family["rows"]:
                if row["variant_kind"] != "candidate":
                    continue
                key = (
                    family["family"],
                    row["witness_policy"],
                    row["source_tag"],
                    row["tag_count"],
                    row["output_router"],
                    bits,
                )
                passing.setdefault(key, set())
                compiler_passing.setdefault(key, set())
                if row["instance_signal_gate_passed"]:
                    passing[key].add(seed)
                if row["compiler_gate_passed"]:
                    compiler_passing[key].add(seed)

    base_candidates = {
        (
            family["family"],
            row["source_tag"],
            row["tag_count"],
            row["output_router"],
        )
        for instance in instances
        for family in instance["families"]
        for row in family["rows"]
        if row["variant_kind"] == "candidate"
    }
    promoted = {
        base_key
        for base_key in base_candidates
        if len(seeds) >= 2
        and all(
            len(
                passing.get(
                    (
                        base_key[0],
                        policy,
                        base_key[1],
                        base_key[2],
                        base_key[3],
                        bits,
                    ),
                    set(),
                )
            )
            >= 2
            for policy in witness_policies
            for bits in bit_sizes
        )
    }
    compiler_promoted = {
        base_key
        for base_key in base_candidates
        if len(seeds) >= 2
        and all(
            len(
                compiler_passing.get(
                    (
                        base_key[0],
                        policy,
                        base_key[1],
                        base_key[2],
                        base_key[3],
                        bits,
                    ),
                    set(),
                )
            )
            >= 2
            for policy in witness_policies
            for bits in bit_sizes
        )
    }
    for instance in instances:
        for family in instance["families"]:
            for row in family["rows"]:
                if row["variant_kind"] != "candidate":
                    continue
                row["routing_gate_passed"] = (
                    row["instance_signal_gate_passed"]
                    and (
                        family["family"],
                        row["source_tag"],
                        row["tag_count"],
                        row["output_router"],
                    )
                    in promoted
                )
                row["compiler_routing_gate_passed"] = (
                    row["compiler_gate_passed"]
                    and (
                        family["family"],
                        row["source_tag"],
                        row["tag_count"],
                        row["output_router"],
                    )
                    in compiler_promoted
                )
    return {
        "required_passing_seeds_per_size": 2,
        "requires_all_witness_policies": True,
        "configured_seed_count": len(seeds),
        "promoted": [
            {
                "family": key[0],
                "source_tag": key[1],
                "tag_count": key[2],
                "output_router": key[3],
            }
            for key in sorted(promoted)
        ],
        "compiler_promoted": [
            {
                "family": key[0],
                "source_tag": key[1],
                "tag_count": key[2],
                "output_router": key[3],
            }
            for key in sorted(compiler_promoted)
        ],
        "passing_seeds": {
            "|".join(map(str, key)): sorted(values)
            for key, values in sorted(passing.items())
            if values
        },
        "compiler_passing_seeds": {
            "|".join(map(str, key)): sorted(values)
            for key, values in sorted(compiler_passing.items())
            if values
        },
    }


def exploratory_slopes(
    instances: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    identities = {
        (
            family["family"],
            row["witness_policy"],
            row["source_tag"],
            row["tag_count"],
            row["output_router"],
            row["variant_kind"],
            row["advice"]["null"]["seed"]
            if row["advice"]["null"] is not None
            else None,
        )
        for instance in instances
        for family in instance["families"]
        for row in family["rows"]
    }
    result = []
    for identity in sorted(
        identities, key=lambda item: tuple("" if value is None else str(value) for value in item)
    ):
        selected = [
            (instance["curve"]["q"], row)
            for instance in instances
            for family in instance["families"]
            if family["family"] == identity[0]
            for row in family["rows"]
            if row["witness_policy"] == identity[1]
            and row["source_tag"] == identity[2]
            and row["tag_count"] == identity[3]
            and row["output_router"] == identity[4]
            and row["variant_kind"] == identity[5]
            and (
                row["advice"]["null"]["seed"]
                if row["advice"]["null"] is not None
                else None
            )
            == identity[6]
        ]
        result.append(
            {
                "family": identity[0],
                "witness_policy": identity[1],
                "source_tag": identity[2],
                "tag_count": identity[3],
                "output_router": identity[4],
                "variant_kind": identity[5],
                "null_seed": identity[6],
                "payload_bits": fit_log_slope(
                    [
                        (q, row["advice"]["payload_bit_lower_estimate"])
                        for q, row in selected
                    ]
                ),
                "route_triples": (
                    None
                    if any(row["advice"]["route_universe_saturated"] for _, row in selected)
                    else fit_log_slope(
                        [
                            (q, row["advice"]["distinct_route_triples"])
                            for q, row in selected
                        ]
                    )
                ),
                "route_slope_eligible": not any(
                    row["advice"]["route_universe_saturated"] for _, row in selected
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
        )
    return result


def run_experiment(config: dict[str, Any]) -> dict[str, Any]:
    bit_sizes = exact_int_list(config["bit_sizes"], "bit_sizes", 5)
    seeds = exact_int_list(config["seeds"], "seeds", 0)
    tag_counts = exact_int_list(config["tag_counts"], "tag_counts", 2)
    null_seeds = exact_int_list(config["null_seeds"], "null_seeds", 0)
    if any(not is_power_of_two(value) for value in tag_counts):
        raise ValueError("all tag counts must be powers of two")
    families = list(config["families"])
    witness_policies = list(config["witness_policies"])
    source_tags = list(config["source_tags"])
    output_routers = list(config["output_routers"])
    for label, values, supported in (
        ("families", families, SUPPORTED_FAMILIES),
        ("witness_policies", witness_policies, WITNESS_POLICIES),
        ("source_tags", source_tags, CANDIDATE_TAGS),
        ("output_routers", output_routers, PUBLIC_OUTPUT_ROUTERS),
    ):
        if not values or len(values) != len(set(values)):
            raise ValueError(f"{label} must be nonempty and distinct")
        if any(value not in supported for value in values):
            raise ValueError(f"unsupported value in {label}")
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
            scalar_index, scalar_index_ops = PRE.enumerate_scalar_index(
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
                        witness_policies,
                        source_tags,
                        tag_counts,
                        output_routers,
                        null_seeds,
                        query_samples,
                        descent_challenges,
                        descent_attempt_limit,
                        scalar_index,
                    )
                )
            rho = BASE.run_rho_baseline(curve_record, seed, rho_trials)
            for family in family_records:
                for row in family["rows"]:
                    row["rho_comparison"] = {
                        "rho_average_group_operations": rho["average_group_operations"],
                        "candidate_descent_to_rho_average_group_operation_ratio": ratio(
                            row["descent"]["average_online_group_operations"],
                            rho["average_group_operations"],
                        ),
                    }
            instances.append(
                {
                    "seed": seed,
                    "curve": curve_record,
                    "factor_base_size": factor_size,
                    "target_seed": target_seed,
                    "scalar_index_private_audit_ops": asdict(scalar_index_ops),
                    "scalar_index_emitted": False,
                    "families": family_records,
                    "rho": rho,
                }
            )

    routing_summary = attach_aggregate_routing(
        instances, bit_sizes, seeds, witness_policies
    )
    frozen = config == FROZEN_CONFIG
    source_hashes = {
        "source_tag_join_sha256": sha256_file(SCRIPT_PATH),
        "source_tag_join_verifier_sha256": sha256_file(VERIFIER_PATH),
        "compressed_join_sha256": sha256_file(PREDECESSOR_PATH),
        "fixed_curve_compiler_sha256": sha256_file(PRE.BASE_PATH),
        "coordinate_energy_sha256": sha256_file(BASE.ENERGY_PATH),
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "contract_v1_sha256": sha256_file(CONTRACT_V1_PATH),
        "hypothesis_sha256": sha256_file(HYPOTHESIS_PATH),
        "research_question_sha256": sha256_file(QUESTION_PATH),
        "theory_sha256": sha256_file(THEORY_PATH),
        "implementation_sha256": sha256_file(IMPLEMENTATION_PATH),
        "pre_run_red_team_v1_sha256": sha256_file(PRE_RUN_RED_TEAM_PATH),
        "pre_run_review_v2_sha256": sha256_file(PRE_RUN_REVIEW_V2_PATH),
    }
    return {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "configuration": config,
        "configuration_is_frozen": frozen,
        "development_only": not frozen,
        "source_hashes": source_hashes,
        "instances": instances,
        "exploratory_slopes": exploratory_slopes(instances),
        "routing_summary": routing_summary,
        "routing_rows": [
            {
                "curve_id": instance["curve"]["id"],
                "family": family["family"],
                "witness_policy": row["witness_policy"],
                "source_tag": row["source_tag"],
                "tag_count": row["tag_count"],
                "output_router": row["output_router"],
            }
            for instance in instances
            for family in instance["families"]
            for row in family["rows"]
            if row["routing_gate_passed"]
        ],
        "compiler_rows": [
            {
                "curve_id": instance["curve"]["id"],
                "family": family["family"],
                "witness_policy": row["witness_policy"],
                "source_tag": row["source_tag"],
                "tag_count": row["tag_count"],
                "output_router": row["output_router"],
            }
            for instance in instances
            for family in instance["families"]
            for row in family["rows"]
            if row["compiler_routing_gate_passed"]
        ],
        "global_controls": {
            "all_curves_clean": all(
                instance["curve"]["trace"] not in (0, 1)
                and instance["curve"]["j_invariant"]
                not in (0, 1728 % instance["curve"]["p"])
                for instance in instances
            ),
            "all_fields_distinct": len(used_primes) == len(instances),
            "all_rho_verified": all(
                instance["rho"]["all_verified"] for instance in instances
            ),
            "scalar_index_not_emitted": all(
                not instance["scalar_index_emitted"] for instance in instances
            ),
            "factor_logs_not_emitted": all(
                not family["factor_base_logs_emitted"]
                for instance in instances
                for family in instance["families"]
            ),
            "positive_controls_present": all(
                any(row["variant_kind"] == "positive_control" for row in family["rows"])
                for instance in instances
                for family in instance["families"]
            ),
            "matched_nulls_present": all(
                {row["variant_kind"] for row in family["rows"]}.issuperset(
                    {"margin_null", "source_null"}
                )
                for instance in instances
                for family in instance["families"]
            ),
        },
        "interpretation": {
            "restricted_theorem": (
                "With the same outer factor scan, exact materialized D4 performs "
                "the same outer EC subtractions and no nonnegative inner candidate "
                "verification work; strict online dominance therefore requires an "
                "outer-routing, batching, or different-cost-model escape."
            ),
            "positive_result": (
                "A routing row would establish a toy source/addition correlation under "
                "the matched null and justify an outer-aware or batch successor."
            ),
            "negative_result": (
                "No routing row narrows only the tested source tags, witness policies, "
                "null construction, factor bases, output routers, and toy regime."
            ),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-sizes", type=int, nargs="+", default=FROZEN_CONFIG["bit_sizes"])
    parser.add_argument("--seeds", type=int, nargs="+", default=FROZEN_CONFIG["seeds"])
    parser.add_argument("--families", nargs="+", default=FROZEN_CONFIG["families"])
    parser.add_argument(
        "--witness-policies", nargs="+", default=FROZEN_CONFIG["witness_policies"]
    )
    parser.add_argument("--source-tags", nargs="+", default=FROZEN_CONFIG["source_tags"])
    parser.add_argument("--tag-counts", type=int, nargs="+", default=FROZEN_CONFIG["tag_counts"])
    parser.add_argument(
        "--output-routers", nargs="+", default=FROZEN_CONFIG["output_routers"]
    )
    parser.add_argument("--null-seeds", type=int, nargs="+", default=FROZEN_CONFIG["null_seeds"])
    parser.add_argument(
        "--occupancy-lambda", type=float, default=FROZEN_CONFIG["occupancy_lambda"]
    )
    parser.add_argument("--query-samples", type=int, default=FROZEN_CONFIG["query_samples"])
    parser.add_argument(
        "--descent-challenges", type=int, default=FROZEN_CONFIG["descent_challenges"]
    )
    parser.add_argument(
        "--descent-attempt-limit",
        type=int,
        default=FROZEN_CONFIG["descent_attempt_limit"],
    )
    parser.add_argument("--rho-trials", type=int, default=FROZEN_CONFIG["rho_trials"])
    parser.add_argument(
        "--authorize-canonical",
        action="store_true",
        help="required in addition to external approval when using the frozen configuration",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = {
        "bit_sizes": args.bit_sizes,
        "seeds": args.seeds,
        "families": args.families,
        "witness_policies": args.witness_policies,
        "source_tags": args.source_tags,
        "tag_counts": args.tag_counts,
        "output_routers": args.output_routers,
        "null_seeds": args.null_seeds,
        "occupancy_lambda": args.occupancy_lambda,
        "query_samples": args.query_samples,
        "descent_challenges": args.descent_challenges,
        "descent_attempt_limit": args.descent_attempt_limit,
        "rho_trials": args.rho_trials,
    }
    if config == FROZEN_CONFIG and not args.authorize_canonical:
        raise SystemExit(
            "frozen canonical configuration requires --authorize-canonical and "
            "separate explicit user/runner approval"
        )
    result = run_experiment(config)
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

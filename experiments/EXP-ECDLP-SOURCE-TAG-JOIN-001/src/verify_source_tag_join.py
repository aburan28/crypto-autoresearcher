#!/usr/bin/env python3
"""Replay and independently audit source-tagged join artifacts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("source_tag_join.py")
Point = tuple[int, int] | None


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "source_tag_join_verifier_generator", GENERATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


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


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_constant,
    )


def compare_exact(actual: Any, expected: Any, path: str = "$") -> None:
    if type(actual) is not type(expected):
        raise AssertionError(
            f"type mismatch at {path}: {type(actual).__name__} != "
            f"{type(expected).__name__}"
        )
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"mapping keys differ at {path}")
        for key in sorted(expected):
            compare_exact(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"list length differs at {path}")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_exact(actual_item, expected_item, f"{path}[{index}]")
        return
    if isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"float differs at {path}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"value differs at {path}: {actual!r} != {expected!r}")


def point_from_json(value: list[int] | None) -> Point:
    if value is None:
        return None
    if type(value) is not list or len(value) != 2:
        raise AssertionError("point must be null or an exact two-coordinate list")
    if any(type(coordinate) is not int for coordinate in value):
        raise AssertionError("point coordinates must be exact integers")
    return value[0], value[1]


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def local_histogram(values: list[int]) -> dict[str, int]:
    return {str(value): values.count(value) for value in sorted(set(values))}


def normalized_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def source_witness_class(witness: tuple[int, int]) -> str:
    left, right = witness
    if left == right:
        return "repeated_leaf"
    if (left ^ 1) == right:
        return "inverse_pair"
    if left // 2 == right // 2:
        return "same_fiber_other"
    if (left & 1) == (right & 1):
        return "distinct_fibers_same_sign"
    return "distinct_fibers_mixed_sign"


def multiplicity_by_tag_histogram(
    tags: list[int], multiplicities: list[int]
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for tag, multiplicity in zip(tags, multiplicities):
        bucket = result.setdefault(str(tag), {})
        key = str(multiplicity)
        bucket[key] = bucket.get(key, 0) + 1
    return result


def witness_class_by_tag_histogram(
    tags: list[int], witnesses: list[tuple[int, int]]
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for tag, witness in zip(tags, witnesses):
        bucket = result.setdefault(str(tag), {})
        key = source_witness_class(witness)
        bucket[key] = bucket.get(key, 0) + 1
    return result


class IndependentCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a
        self.b = b
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise AssertionError("independent verifier received a singular curve")

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return 0 <= x < self.p and 0 <= y < self.p and (
            y * y - x * x * x - self.a * x - self.b
        ) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.on_curve(result):
            raise AssertionError("independent addition left the curve")
        return result

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            scalar >>= 1
        return result

    def order(self) -> int:
        total = 1
        exponent = (self.p - 1) // 2
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0:
                total += 1
                continue
            symbol = pow(rhs, exponent, self.p)
            if symbol == 1:
                total += 2
            elif symbol != self.p - 1:
                raise AssertionError("invalid independent Legendre symbol")
        return total


def independent_scalar_index(
    curve: IndependentCurve,
    q: int,
    generator: Point,
) -> dict[Point, int]:
    result: dict[Point, int] = {}
    point: Point = None
    for scalar in range(q):
        if point in result:
            raise AssertionError("independent scalar index repeated early")
        result[point] = scalar
        point = curve.add(point, generator)
    if point is not None or len(result) != q:
        raise AssertionError("independent scalar index did not close")
    return result


def independent_select_witness(
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
    raise AssertionError("unknown independent witness policy")


def independent_d2_witness_data(
    curve: IndependentCurve,
    factor_points: list[Point],
    policy: str,
    seed: int,
) -> dict[str, Any]:
    by_point: dict[Point, list[tuple[int, int]]] = {}
    for left in range(len(factor_points)):
        for right in range(left, len(factor_points)):
            total = curve.add(factor_points[left], factor_points[right])
            by_point.setdefault(total, []).append((left, right))
    points = sorted(by_point, key=point_sort_key)
    point_to_index = {point: index for index, point in enumerate(points)}
    all_witnesses = [tuple(by_point[point]) for point in points]
    multiplicities = [len(values) for values in all_witnesses]
    inversion = [point_to_index[curve.neg(point)] for point in points]
    bound: list[tuple[int, int] | None] = [None] * len(points)
    for index, negative_index in enumerate(inversion):
        if index > negative_index or bound[index] is not None:
            continue
        selected = independent_select_witness(all_witnesses[index], policy, seed)
        negated = normalized_pair(selected[0] ^ 1, selected[1] ^ 1)
        if negated not in all_witnesses[negative_index]:
            raise AssertionError("independent negated witness is absent")
        bound[index] = selected
        bound[negative_index] = negated
    if any(value is None for value in bound):
        raise AssertionError("independent witness binding is incomplete")
    return {
        "points": points,
        "point_to_index": point_to_index,
        "all_witnesses": all_witnesses,
        "multiplicities": multiplicities,
        "inversion": inversion,
        "witnesses": [value for value in bound if value is not None],
    }


def independent_source_tag(
    name: str,
    witness: tuple[int, int],
    sources: list[dict[str, Any]],
    tag_count: int,
) -> int:
    left, right = witness
    left_source = sources[left // 2]
    right_source = sources[right // 2]
    sign_parity = (left & 1) ^ (right & 1)
    sign_term = sign_parity * (tag_count // 2 + 1)
    if name == "ordinal_sum":
        value = left_source["ordinal"] + right_source["ordinal"] + sign_term
    elif name == "source_x_sum":
        value = left_source["x"] + right_source["x"] + sign_term
    elif name == "parameter_mix":
        left_parameter = left_source["parameter"]
        right_parameter = right_source["parameter"]
        value = (
            left_parameter
            + right_parameter
            + 3 * abs(left_parameter - right_parameter)
            + 5 * (left_source["map_branch"] + right_source["map_branch"])
            + sign_term
        )
    else:
        raise AssertionError("unknown independent source tag")
    return value % tag_count


def independent_candidate_tags(
    name: str,
    d2: dict[str, Any],
    sources: list[dict[str, Any]],
    tag_count: int,
) -> list[int]:
    tags = [
        independent_source_tag(name, witness, sources, tag_count)
        for witness in d2["witnesses"]
    ]
    for index, negative_index in enumerate(d2["inversion"]):
        if tags[index] != tags[negative_index]:
            raise AssertionError("independent candidate tag is not sign invariant")
    return tags


def independent_margin_shuffle(
    candidate_tags: list[int],
    d2: dict[str, Any],
    seed: int,
) -> tuple[list[int], str]:
    rng = random.Random(seed)
    orbits: list[tuple[int, ...]] = []
    seen: set[int] = set()
    for index, negative_index in enumerate(d2["inversion"]):
        if index in seen:
            continue
        orbit = (
            (index,)
            if index == negative_index
            else tuple(sorted((index, negative_index)))
        )
        seen.update(orbit)
        orbits.append(orbit)
    strata: dict[tuple[int, int, str], list[tuple[int, ...]]] = {}
    for orbit in orbits:
        key = (
            d2["multiplicities"][orbit[0]],
            len(orbit),
            source_witness_class(d2["witnesses"][orbit[0]]),
        )
        strata.setdefault(key, []).append(orbit)
    shuffled = list(candidate_tags)
    rows = []
    for key in sorted(strata):
        stratum = strata[key]
        permutation = list(range(len(stratum)))
        rng.shuffle(permutation)
        if len(permutation) > 1 and permutation == list(range(len(permutation))):
            permutation = permutation[1:] + permutation[:1]
        for destination_position, source_position in enumerate(permutation):
            tag = candidate_tags[stratum[source_position][0]]
            for point_index in stratum[destination_position]:
                shuffled[point_index] = tag
        rows.append(
            {
                "multiplicity": key[0],
                "orbit_size": key[1],
                "witness_class": key[2],
                "orbit_count": len(stratum),
                "permutation": permutation,
            }
        )
    return shuffled, stable_digest(rows)


def independent_source_permutation(
    sources: list[dict[str, Any]], seed: int
) -> tuple[list[dict[str, Any]], str]:
    rng = random.Random(seed ^ 0x8CB92BA72F3D8DD7)
    permutation = list(range(len(sources)))
    rng.shuffle(permutation)
    if len(permutation) > 1 and permutation == list(range(len(permutation))):
        permutation = permutation[1:] + permutation[:1]
    return [sources[source] for source in permutation], stable_digest(permutation)


def independent_output_bucket(
    name: str,
    point: Point,
    bucket_count: int,
    curve: IndependentCurve,
    q: int,
    seed: int,
    scalar_index: dict[Point, int],
) -> int:
    if name == "scalar_interval":
        return scalar_index[point] * bucket_count // q
    if point is None:
        return 0
    x = point[0]
    if name == "x_interval":
        return min(bucket_count - 1, (x + 1) * bucket_count // (curve.p + 1))
    if name != "random_x_fiber":
        raise AssertionError("unknown independent output router")
    width = max(1, math.ceil(curve.p.bit_length() / 8))
    digest = hashlib.sha256(
        seed.to_bytes(16, "big", signed=False) + x.to_bytes(width, "big")
    ).digest()
    return int.from_bytes(digest[:8], "big") % bucket_count


def independently_verify_route_row(
    curve: IndependentCurve,
    q: int,
    factor_points: list[Point],
    original_sources: list[dict[str, Any]],
    scalar_index: dict[Point, int],
    d2: dict[str, Any],
    row: dict[str, Any],
) -> None:
    advice = row["advice"]
    tag_count = row["tag_count"]
    sources = original_sources
    if row["variant_kind"] == "positive_control":
        tags = [scalar_index[point] * tag_count // q for point in d2["points"]]
    else:
        candidate_tags = independent_candidate_tags(
            row["source_tag"], d2, original_sources, tag_count
        )
        if row["variant_kind"] == "candidate":
            tags = candidate_tags
        elif row["variant_kind"] == "margin_null":
            tags, permutation_digest = independent_margin_shuffle(
                candidate_tags, d2, advice["null"]["seed"]
            )
            if permutation_digest != advice["null"]["permutation_digest"]:
                raise AssertionError("independent margin permutation differs")
        elif row["variant_kind"] == "source_null":
            sources, permutation_digest = independent_source_permutation(
                original_sources, advice["null"]["seed"]
            )
            if permutation_digest != advice["null"]["permutation_digest"]:
                raise AssertionError("independent source permutation differs")
            tags = independent_candidate_tags(
                row["source_tag"], d2, sources, tag_count
            )
        else:
            raise AssertionError("unknown route-row variant")
    if stable_digest(tags) != advice["tag_assignment_digest"]:
        raise AssertionError("independent tag assignment differs")
    if local_histogram(tags) != advice["tag_histogram"]:
        raise AssertionError("independent tag histogram differs")
    if multiplicity_by_tag_histogram(tags, d2["multiplicities"]) != advice[
        "multiplicity_by_tag_histogram"
    ]:
        raise AssertionError("independent multiplicity-by-tag differs")
    if witness_class_by_tag_histogram(tags, d2["witnesses"]) != advice[
        "witness_class_by_tag_histogram"
    ]:
        raise AssertionError("independent witness-class-by-tag differs")

    routes: dict[tuple[int, int], set[int]] = {}
    coverage = 0
    for left in range(len(d2["points"])):
        for right in range(left, len(d2["points"])):
            output = curve.add(d2["points"][left], d2["points"][right])
            output_tag = independent_output_bucket(
                row["output_router"],
                output,
                tag_count,
                curve,
                q,
                advice["output_seed"],
                scalar_index,
            )
            orientations = (
                [(left, right)] if left == right else [(left, right), (right, left)]
            )
            for oriented_left, oriented_right in orientations:
                routes.setdefault((output_tag, tags[oriented_left]), set()).add(
                    tags[oriented_right]
                )
                coverage += 1
    triples = [
        [output_tag, left_tag, right_tag]
        for (output_tag, left_tag), right_tags in sorted(routes.items())
        for right_tag in sorted(right_tags)
    ]
    artifact = {
        "factor_points": [
            None if point is None else [point[0], point[1]] for point in factor_points
        ],
        "factor_sources": sources,
        "d2": [
            {
                "point": None if point is None else [point[0], point[1]],
                "witness": list(witness),
                "multiplicity": multiplicity,
                "tag": tag,
            }
            for point, witness, multiplicity, tag in zip(
                d2["points"], d2["witnesses"], d2["multiplicities"], tags
            )
        ],
        "routes": triples,
    }
    if len(triples) != advice["distinct_route_triples"]:
        raise AssertionError("independent route-triple count differs")
    if coverage != advice["route_coverage_oriented_pairs"]:
        raise AssertionError("independent route coverage differs")
    if stable_digest(triples) != advice["route_digest"]:
        raise AssertionError("independent route digest differs")
    if stable_digest(artifact) != advice["artifact_digest"]:
        raise AssertionError("independent advice artifact differs")
    if triples[:8] != advice["first_routes"] or tags[:8] != advice["first_tags"]:
        raise AssertionError("independent route/tag prefix differs")


def independent_supports(
    curve: IndependentCurve,
    factor_points: list[Point],
) -> tuple[list[Point], list[int], list[Point], list[Point]]:
    multiplicities: dict[Point, int] = {}
    for left in range(len(factor_points)):
        for right in range(left, len(factor_points)):
            total = curve.add(factor_points[left], factor_points[right])
            multiplicities[total] = multiplicities.get(total, 0) + 1
    d2 = sorted(multiplicities, key=point_sort_key)
    d4 = sorted(
        {
            curve.add(d2[left], d2[right])
            for left in range(len(d2))
            for right in range(left, len(d2))
        },
        key=point_sort_key,
    )
    d5 = sorted(
        {curve.add(partial, point) for partial in d4 for point in factor_points},
        key=point_sort_key,
    )
    return d2, [multiplicities[point] for point in d2], d4, d5


def verify_witness(
    curve: IndependentCurve,
    factor_points: list[Point],
    witness: list[int],
    target: Point,
) -> None:
    total: Point = None
    for index in witness:
        if type(index) is not int or not 0 <= index < len(factor_points):
            raise AssertionError("factor witness index is out of range")
        total = curve.add(total, factor_points[index])
    if total != target:
        raise AssertionError("independent factor witness verification failed")


def reject_private_source_fields(value: Any, path: str) -> None:
    forbidden = {
        "scalar",
        "sampled_scalar",
        "canonical_scalar",
        "discrete_log",
        "scalar_index",
        "factor_log",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            if key in forbidden:
                raise AssertionError(f"private scalar source field at {path}.{key}")
            reject_private_source_fields(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_private_source_fields(item, f"{path}[{index}]")


def verify_semantics(document: dict[str, Any]) -> dict[str, int]:
    verified_families = 0
    verified_rows = 0
    verified_route_rows = 0
    verified_witnesses = 0
    verified_nulls = 0
    for instance in document["instances"]:
        curve_record = instance["curve"]
        curve = IndependentCurve(
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        if curve.order() != curve_record["q"]:
            raise AssertionError("independent curve order differs")
        generator = point_from_json(curve_record["generator"])
        if not curve.on_curve(generator) or curve.mul(curve_record["q"], generator) is not None:
            raise AssertionError("generator failed independent subgroup verification")
        scalar_index = independent_scalar_index(curve, curve_record["q"], generator)

        for family in instance["families"]:
            verified_families += 1
            reject_private_source_fields(
                family["public_factor_sources"], "$.public_factor_sources"
            )
            factor_points = [
                point_from_json(point) for point in family["factor_base"]["points"]
            ]
            if not all(curve.on_curve(point) for point in factor_points):
                raise AssertionError("factor base contains an off-curve point")
            for index in range(0, len(factor_points), 2):
                if curve.neg(factor_points[index]) != factor_points[index + 1]:
                    raise AssertionError("factor base is not sign complete")
            d2, multiplicities, d4, d5 = independent_supports(curve, factor_points)
            d2_digest = stable_digest(
                [None if point is None else [point[0], point[1]] for point in d2]
            )
            d4_digest = stable_digest(
                [None if point is None else [point[0], point[1]] for point in d4]
            )
            d5_digest = stable_digest(
                [None if point is None else [point[0], point[1]] for point in d5]
            )
            policy_data: dict[str, dict[str, Any]] = {}
            for policy in family["policy_supports"]:
                independent_policy = independent_d2_witness_data(
                    curve,
                    factor_points,
                    policy["witness_policy"],
                    policy["witness_seed"],
                )
                policy_data[policy["witness_policy"]] = independent_policy
                if policy["d2"]["support_size"] != len(d2):
                    raise AssertionError("independent D2 support size differs")
                if policy["d2"]["support_digest"] != d2_digest:
                    raise AssertionError("independent D2 support digest differs")
                if policy["d2"]["multiplicity_histogram"] != local_histogram(
                    multiplicities
                ):
                    raise AssertionError("independent D2 multiplicity differs")
                if policy["d2"]["bound_witness_digest"] != stable_digest(
                    independent_policy["witnesses"]
                ):
                    raise AssertionError("independent bound-witness digest differs")
                if policy["d2"]["all_witness_digest"] != stable_digest(
                    independent_policy["all_witnesses"]
                ):
                    raise AssertionError("independent all-witness digest differs")
                if policy["d4"]["support_size"] != len(d4):
                    raise AssertionError("independent D4 support size differs")
                if policy["d4"]["support_digest"] != d4_digest:
                    raise AssertionError("independent D4 support digest differs")
            if family["d5"]["support_size"] != len(d5):
                raise AssertionError("independent D5 support size differs")
            if family["d5"]["support_digest"] != d5_digest:
                raise AssertionError("independent D5 support digest differs")

            schedules: dict[str, tuple[str, ...]] = {}
            descent_schedule: tuple[str, ...] | None = None
            candidates: dict[tuple[str, str, int, str], dict[str, Any]] = {}
            for row in family["rows"]:
                verified_rows += 1
                independently_verify_route_row(
                    curve,
                    curve_record["q"],
                    factor_points,
                    family["public_factor_sources"],
                    scalar_index,
                    policy_data[row["witness_policy"]],
                    row,
                )
                verified_route_rows += 1
                if row["variant_kind"] == "positive_control":
                    if row["eligibility"] != "positive_control_only":
                        raise AssertionError("scalar control became eligible")
                    if not row["advice"]["scalar_oracle_required"]:
                        raise AssertionError("scalar control lost its oracle label")
                else:
                    if row["advice"]["scalar_oracle_required"]:
                        raise AssertionError("eligible or null row requires scalar oracle")
                    if row["advice"]["hidden_scalar_metadata_emitted"]:
                        raise AssertionError("eligible advice reports hidden scalar metadata")
                if row["advice"]["route_coverage_oriented_pairs"] != row["advice"][
                    "expected_oriented_pairs"
                ]:
                    raise AssertionError("route coverage count differs")
                for sample_name in ("supported_d4", "supported_d5", "random_d5"):
                    records = row["query_samples"][sample_name]["records"]
                    current_schedule = tuple(repr(record["target"]) for record in records)
                    previous = schedules.setdefault(sample_name, current_schedule)
                    if current_schedule != previous:
                        raise AssertionError("row target schedules differ")
                    for record in records:
                        if record["success"]:
                            target = point_from_json(record["target"])
                            verify_witness(curve, factor_points, record["witness"], target)
                            verified_witnesses += 1
                current_descent = tuple(
                    repr(challenge["target"])
                    for challenge in row["descent"]["challenges"]
                )
                if descent_schedule is None:
                    descent_schedule = current_descent
                elif current_descent != descent_schedule:
                    raise AssertionError("row descent schedules differ")
                for challenge in row["descent"]["challenges"]:
                    if challenge["success"]:
                        recovered = challenge["recovered_scalar"]
                        target = point_from_json(challenge["target"])
                        if recovered != challenge["known_scalar_private_audit"]:
                            raise AssertionError("private descent scalar differs")
                        if curve.mul(recovered, generator) != target:
                            raise AssertionError("independent descent scalar verification failed")
                key = (
                    row["witness_policy"],
                    row["source_tag"],
                    row["tag_count"],
                    row["output_router"],
                )
                if row["variant_kind"] == "candidate":
                    candidates[key] = row

            for row in family["rows"]:
                if row["variant_kind"] not in ("margin_null", "source_null"):
                    continue
                verified_nulls += 1
                key = (
                    row["witness_policy"],
                    row["source_tag"],
                    row["tag_count"],
                    row["output_router"],
                )
                candidate = candidates[key]
                null = row["advice"]["null"]
                if row["variant_kind"] == "margin_null":
                    if row["advice"]["tag_histogram"] != candidate["advice"][
                        "tag_histogram"
                    ]:
                        raise AssertionError("margin-null tag histogram differs")
                    if row["advice"]["multiplicity_by_tag_histogram"] != candidate[
                        "advice"
                    ]["multiplicity_by_tag_histogram"]:
                        raise AssertionError("margin-null multiplicity-by-tag differs")
                    if row["advice"]["witness_class_by_tag_histogram"] != candidate[
                        "advice"
                    ]["witness_class_by_tag_histogram"]:
                        raise AssertionError("margin-null witness-class-by-tag differs")
                    required = (
                        "tag_histogram_preserved",
                        "multiplicity_by_tag_preserved",
                        "witness_class_by_tag_preserved",
                        "inversion_symmetry_preserved",
                    )
                else:
                    required = (
                        "source_multiset_preserved",
                        "compositional_recompute",
                        "inversion_symmetry_preserved",
                    )
                if not all(null[key] for key in required):
                    raise AssertionError("null invariant flag is false")

            materialized = family["baselines"]["materialized_d4"]
            baselines = [materialized]
            baselines.extend(family["baselines"]["d2_complement"])
            baselines.extend(family["baselines"]["partial_d4"])
            for baseline in baselines:
                for sample_name in ("supported_d4", "supported_d5", "random_d5"):
                    records = baseline["query_samples"][sample_name]["records"]
                    if tuple(repr(record["target"]) for record in records) != schedules[
                        sample_name
                    ]:
                        raise AssertionError("baseline target schedule differs")
                    for record in records:
                        if record["success"]:
                            verify_witness(
                                curve,
                                factor_points,
                                record["witness"],
                                point_from_json(record["target"]),
                            )
                            verified_witnesses += 1
    return {
        "verified_instances": len(document["instances"]),
        "verified_families": verified_families,
        "verified_rows": verified_rows,
        "verified_route_rows": verified_route_rows,
        "verified_matched_nulls": verified_nulls,
        "verified_factor_witnesses": verified_witnesses,
    }


def verify_source_hashes(document: dict[str, Any]) -> None:
    expected = {
        "source_tag_join_sha256": sha256_file(GENERATOR_PATH),
        "source_tag_join_verifier_sha256": sha256_file(SCRIPT_PATH),
        "compressed_join_sha256": sha256_file(GENERATOR.PREDECESSOR_PATH),
        "fixed_curve_compiler_sha256": sha256_file(GENERATOR.PRE.BASE_PATH),
        "coordinate_energy_sha256": sha256_file(GENERATOR.BASE.ENERGY_PATH),
        "contract_sha256": sha256_file(GENERATOR.CONTRACT_PATH),
        "contract_v1_sha256": sha256_file(GENERATOR.CONTRACT_V1_PATH),
        "hypothesis_sha256": sha256_file(GENERATOR.HYPOTHESIS_PATH),
        "research_question_sha256": sha256_file(GENERATOR.QUESTION_PATH),
        "theory_sha256": sha256_file(GENERATOR.THEORY_PATH),
        "implementation_sha256": sha256_file(GENERATOR.IMPLEMENTATION_PATH),
        "pre_run_red_team_v1_sha256": sha256_file(
            GENERATOR.PRE_RUN_RED_TEAM_PATH
        ),
        "pre_run_review_v2_sha256": sha256_file(
            GENERATOR.PRE_RUN_REVIEW_V2_PATH
        ),
    }
    compare_exact(document["source_hashes"], expected, "$.source_hashes")


def verify_document(
    document: dict[str, Any],
    enforce_frozen: bool = True,
) -> dict[str, Any]:
    if type(document) is not dict:
        raise AssertionError("top-level document must be a mapping")
    if document.get("protocol") != GENERATOR.PROTOCOL:
        raise AssertionError("protocol mismatch")
    verify_source_hashes(document)
    if enforce_frozen:
        compare_exact(document["configuration"], GENERATOR.FROZEN_CONFIG, "$.configuration")
        if not document["configuration_is_frozen"] or document["development_only"]:
            raise AssertionError("canonical verification requires frozen configuration")
    elif document["configuration_is_frozen"] != (
        document["configuration"] == GENERATOR.FROZEN_CONFIG
    ):
        raise AssertionError("configuration freeze label is inconsistent")
    replayed = GENERATOR.run_experiment(document["configuration"])
    compare_exact(document, replayed)
    independent = verify_semantics(document)
    return {
        "status": "verified",
        "protocol": document["protocol"],
        "development_only": document["development_only"],
        "canonical_configuration": document["configuration_is_frozen"],
        "canonical_document_sha256": hashlib.sha256(
            stable_json_bytes(document)
        ).hexdigest(),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "generator_sha256": sha256_file(GENERATOR_PATH),
        "routing_rows": document["routing_rows"],
        **independent,
        "boundary": (
            "Deterministic full replay plus independent affine/order/support/witness "
            "and matched-null audit; a verified development artifact is not a "
            "canonical run, exponent improvement, or ECDLP break."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--allow-development",
        action="store_true",
        help="verify a non-frozen development configuration",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    document = load_json_strict(args.input)
    certificate = verify_document(
        document, enforce_frozen=not args.allow_development
    )
    certificate["input_file_sha256"] = sha256_file(args.input)
    encoded = json.dumps(certificate, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

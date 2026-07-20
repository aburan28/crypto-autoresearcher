#!/usr/bin/env python3
"""Independent development verifier for EXP-SGCP-EMBED-002.

This verifier does not import or execute the producer. It reconstructs the EC
objects, predicate selection, collision graph, retained embedding, and primary
coverage optimum from the emitted coordinates.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


EXPECTED_SCHEMAS = {
    "sgcp-embed-002-development-v1",
    "sgcp-embed-002-density-frontier-development-v2",
    "sgcp-embed-002-density-frontier-candidate-v3",
}
VERIFICATION_SCHEMA = "sgcp-embed-002-development-verification-v3"
EXPERIMENT_ID = "EXP-SGCP-EMBED-002"
PROTOCOL_VERSION = 3
REPRESENTATIVE_COMPILER = (
    "lexicographically_least_formal_per_nonidentity_2F_output_v1"
)
COORDINATE_FAMILIES = (
    "least_x_interval",
    "mobius_interval",
    "two_mobius_union",
)
NULL_FAMILY = "hash_x_null"
CANONICAL_BITS = (5, 6, 7, 8)
CANONICAL_SEEDS = (101, 211)
CANONICAL_FACTOR_BASE_SIZES = (4, 6, 8)
CANONICAL_NULL_REPLICATES = 4
CANONICAL_NODE_CAP = 2_000_000
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND", "NOVELTY-UNVERIFIED"]
FROZEN_FIXTURE = {
    "bits": 5,
    "p": 19,
    "a": 2,
    "b": 9,
    "q": 23,
    "trace": -3,
    "generator": [0, 3],
}
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
DEVELOPMENT_ROOT = EXPERIMENT_ROOT / "development"
Point = tuple[int, int] | None
Formal = tuple[int, ...]
OPERATION_COUNTER_KEYS = {
    "point_additions",
    "point_doublings",
    "field_inversions",
    "field_multiplications",
    "multiset_evaluations",
    "injectivity_checks",
    "conflict_pair_checks",
    "hash_calls",
    "optimizer_nodes",
    "optimizer_bound_calls",
}


def stable_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(stable_bytes(value)).hexdigest()


def hash_mod(domain: str, fields: Sequence[Any], modulus: int) -> int:
    payload = {"domain": domain, "fields": list(fields)}
    return int.from_bytes(hashlib.sha256(stable_bytes(payload)).digest(), "big") % modulus


def require_keys(value: Any, expected: set[str], label_name: str) -> None:
    if not isinstance(value, dict):
        raise AssertionError(f"{label_name} is not an object")
    observed = set(value)
    if observed != expected:
        raise AssertionError(
            f"{label_name} keys mismatch: missing={sorted(expected - observed)!r} "
            f"extra={sorted(observed - expected)!r}"
        )


def forbidden_material(value: Any, path: str = "row") -> list[str]:
    forbidden = ("scalar", "discrete_log", "dlog", "log_table", "secret")
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if any(token in lowered for token in forbidden):
                errors.append(f"forbidden material key at {path}.{key}")
            errors.extend(forbidden_material(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(forbidden_material(child, f"{path}[{index}]"))
    return errors


def file_digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            state.update(block)
    return state.hexdigest()


def strict_load(path: Path) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate key {key!r} in {path}")
            result[key] = value
        return result

    def constant(value: str) -> Any:
        raise ValueError(f"non-finite constant {value!r} in {path}")

    return json.loads(
        path.read_text(encoding="ascii"),
        object_pairs_hook=pairs,
        parse_constant=constant,
    )


def is_prime(value: int) -> bool:
    if type(value) is not int or value < 2:
        return False
    for divisor in range(2, math.isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def point_order(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def decode_point(value: Any) -> Point:
    if value == "O":
        return None
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        raise ValueError(f"invalid point encoding {value!r}")
    return value[0], value[1]


def label(point: Point) -> str:
    return "O" if point is None else f"{point[0]}:{point[1]}"


def bits(mask: int) -> Iterator[int]:
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        if not is_prime(p) or p <= 3:
            raise ValueError("invalid prime field")
        self.p = p
        self.a = a % p
        self.b = b % p
        if self.discriminant() == 0:
            raise ValueError("singular curve")

    def discriminant(self) -> int:
        return (4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)) % self.p

    def j(self) -> int:
        return (
            1728
            * 4
            * pow(self.a, 3, self.p)
            * pow(self.discriminant(), -1, self.p)
            % self.p
        )

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def negate(self, point: Point) -> Point:
        return None if point is None else (point[0], -point[1] % self.p)

    def plus(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = 2 * y1 % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        result = (x3, (slope * (x1 - x3) - y1) % self.p)
        if not self.contains(result):
            raise AssertionError("independent addition left curve")
        return result

    def points(self) -> list[Point]:
        roots: dict[int, list[int]] = defaultdict(list)
        for y in range(self.p):
            roots[y * y % self.p].append(y)
        result: list[Point] = [None]
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            result.extend((x, y) for y in roots.get(rhs, []))
        return sorted(result, key=point_order)


def independent_rejection_reasons(
    p: int, a: int, b: int, bits_value: int
) -> tuple[list[str], int | None]:
    discriminant = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if discriminant == 0:
        return ["singular"], None
    curve = Curve(p, a, b)
    q = len(curve.points())
    trace = p + 1 - q
    reasons: list[str] = []
    if q.bit_length() != bits_value:
        reasons.append("wrong_q_bit_length")
    if not is_prime(q):
        reasons.append("nonprime_group_order")
    if trace == 0:
        reasons.append("trace_zero")
    if trace == 1:
        reasons.append("anomalous_trace_one")
    if curve.j() == 0:
        reasons.append("j_zero")
    if curve.j() == 1728 % p:
        reasons.append("j_1728")
    return reasons, q


def independent_curve_record(
    curve: Curve, group: Sequence[Point], bits_value: int, seed: int
) -> dict[str, Any]:
    generator = next(point for point in group if point is not None)
    q = len(group)
    return {
        "bits": bits_value,
        "seed": seed,
        "p": curve.p,
        "a": curve.a,
        "b": curve.b,
        "q": q,
        "trace": curve.p + 1 - q,
        "j": curve.j(),
        "generator": [generator[0], generator[1]],
    }


def verify_curve_provenance(info: dict[str, Any]) -> Curve:
    require_keys(
        info,
        {
            "bits",
            "seed",
            "p",
            "a",
            "b",
            "q",
            "trace",
            "j",
            "generator",
            "draw",
            "rejected_draws",
            "rejection_count",
            "rejection_digest",
        },
        "curve record",
    )
    bits_value = info["bits"]
    seed = info["seed"]
    if type(bits_value) is not int or type(seed) is not int:
        raise AssertionError("curve bits/seed are not exact integers")
    if info["draw"] is None:
        curve = Curve(FROZEN_FIXTURE["p"], FROZEN_FIXTURE["a"], FROZEN_FIXTURE["b"])
        group = curve.points()
        expected = independent_curve_record(curve, group, FROZEN_FIXTURE["bits"], 5)
        expected.update(
            {
                "draw": None,
                "rejected_draws": [],
                "rejection_count": 0,
                "rejection_digest": digest([]),
            }
        )
        if info != expected:
            raise AssertionError("frozen curve provenance mismatch")
        return curve

    if type(info["draw"]) is not int or info["draw"] < 0:
        raise AssertionError("generated curve draw is invalid")
    primes = [
        value
        for value in range(1 << (bits_value - 1), 1 << bits_value)
        if value > 3 and is_prime(value)
    ]
    seen: set[tuple[int, int, int]] = set()
    rejections: list[dict[str, Any]] = []
    for draw in range(info["draw"] + 1):
        p = primes[hash_mod("sgcp-002-curve-p", [bits_value, seed, draw], len(primes))]
        a = hash_mod("sgcp-002-curve-a", [bits_value, seed, draw, p], p)
        b = hash_mod("sgcp-002-curve-b", [bits_value, seed, draw, p], p)
        key = (p, a, b)
        if key in seen:
            rejections.append(
                {"draw": draw, "p": p, "a": a, "b": b, "reasons": ["duplicate_candidate"]}
            )
            continue
        seen.add(key)
        reasons, rejection_q = independent_rejection_reasons(p, a, b, bits_value)
        if reasons == ["singular"]:
            rejections.append(
                {"draw": draw, "p": p, "a": a, "b": b, "reasons": reasons}
            )
            continue
        curve = Curve(p, a, b)
        group = curve.points()
        if rejection_q != len(group):
            raise AssertionError("independent rejection recount mismatch")
        if reasons:
            rejections.append(
                {
                    "draw": draw,
                    "p": p,
                    "a": a,
                    "b": b,
                    "q": len(group),
                    "reasons": reasons,
                }
            )
            continue
        expected = independent_curve_record(curve, group, bits_value, seed)
        expected.update(
            {
                "draw": draw,
                "rejected_draws": rejections,
                "rejection_count": len(rejections),
                "rejection_digest": digest(rejections),
            }
        )
        if draw != info["draw"] or info != expected:
            raise AssertionError("generated curve transcript mismatch")
        return curve
    raise AssertionError("declared accepted draw is not independently accepted")


def derive_mobius(
    curve_info: dict[str, Any], B: int, tag: str, map_index: int
) -> dict[str, int]:
    p = curve_info["p"]
    token = [curve_info[key] for key in ("p", "a", "b", "q", "seed")]
    for nonce in range(1024):
        u = hash_mod("sgcp-002-mobius-u", [token, B, tag, map_index, nonce], p)
        v = hash_mod("sgcp-002-mobius-v", [token, B, tag, map_index, nonce], p)
        w = hash_mod("sgcp-002-mobius-w", [token, B, tag, map_index, nonce], p)
        determinant = (u * w - v) % p
        if determinant:
            return {
                "u": u,
                "v": v,
                "w": w,
                "determinant": determinant,
                "nonce": nonce,
            }
    raise AssertionError("independent Mobius derivation failed")


def polynomial(roots: Sequence[int], p: int) -> list[int]:
    result = [1]
    for root in roots:
        next_result = [0] * (len(result) + 1)
        for degree, coefficient in enumerate(result):
            next_result[degree] = (next_result[degree] - coefficient * root) % p
            next_result[degree + 1] = (next_result[degree + 1] + coefficient) % p
        result = next_result
    return result


def admissible(curve: Curve, group: Sequence[Point]) -> dict[int, tuple[Point, Point]]:
    fibers: dict[int, list[Point]] = defaultdict(list)
    for point in group:
        if point is not None:
            fibers[point[0]].append(point)
    result: dict[int, tuple[Point, Point]] = {}
    for x, values in fibers.items():
        ordered = tuple(sorted(values, key=point_order))
        if len(ordered) == 2 and curve.negate(ordered[0]) == ordered[1]:
            result[x] = (ordered[0], ordered[1])
    return result


def map_ranking(roots: Sequence[int], p: int, params: dict[str, Any]) -> tuple[list[int], list[int]]:
    u = params["u"]
    v = params["v"]
    w = params["w"]
    if any(type(value) is not int for value in (u, v, w, params["determinant"], params["nonce"])):
        raise ValueError("noninteger Mobius parameter")
    if (u * w - v) % p == 0 or params["determinant"] != (u * w - v) % p:
        raise ValueError("degenerate or inconsistent Mobius map")
    scored: list[tuple[int, int]] = []
    poles: list[int] = []
    for x in roots:
        denominator = (x + w) % p
        if denominator == 0:
            poles.append(x)
        else:
            scored.append(((u * x + v) * pow(denominator, -1, p) % p, x))
    return [x for _, x in sorted(scored)], sorted(poles)


def verify_factor_base(curve: Curve, group: Sequence[Point], row: dict[str, Any]) -> list[Point]:
    record = row["public_model"]["factor_base"]
    require_keys(
        record,
        {
            "family",
            "null_replicate",
            "B",
            "admissible_root_count",
            "selected_roots",
            "selected_root_count",
            "excluded_poles",
            "parameters",
            "root_polynomial_coefficients_ascending_mod_p",
            "points",
            "negation_symmetric",
            "selection_sha256",
        },
        "factor-base record",
    )
    digest_payload = dict(record)
    supplied_selection_digest = digest_payload.pop("selection_sha256", None)
    if supplied_selection_digest != digest(digest_payload):
        raise AssertionError("factor-base selection digest mismatch")
    B = row["B"]
    family = row["family"]
    replicate = row["null_replicate"]
    if (
        type(B) is not int
        or B < 4
        or B % 2
        or record["B"] != B
        or record["family"] != family
        or record["null_replicate"] != replicate
    ):
        raise AssertionError("factor-base row binding mismatch")
    if family in COORDINATE_FAMILIES and replicate is not None:
        raise AssertionError("coordinate family carries a null replicate")
    if family == NULL_FAMILY and (
        type(replicate) is not int or not 0 <= replicate < CANONICAL_NULL_REPLICATES
    ):
        raise AssertionError("hash-null replicate is outside the frozen range")
    fibers = admissible(curve, group)
    roots = sorted(fibers)
    required = B // 2
    if family == "least_x_interval":
        if record["parameters"] != {}:
            raise AssertionError("least-x parameters are not empty")
        expected = roots[:required]
        poles: list[int] = []
    elif family == "mobius_interval":
        require_keys(record["parameters"], {"map"}, "Mobius parameters")
        expected_map = derive_mobius(row["curve"], B, family, 0)
        if record["parameters"]["map"] != expected_map:
            raise AssertionError("Mobius derivation transcript mismatch")
        ranking, poles = map_ranking(roots, curve.p, expected_map)
        expected = ranking[:required]
    elif family == "two_mobius_union":
        require_keys(
            record["parameters"], {"maps", "alternating_positions"}, "two-map parameters"
        )
        expected_maps = [derive_mobius(row["curve"], B, family, index) for index in range(2)]
        if record["parameters"]["maps"] != expected_maps:
            raise AssertionError("two-map derivation transcript mismatch")
        rankings: list[list[int]] = []
        pole_set: set[int] = set()
        for params in expected_maps:
            ranking, map_poles = map_ranking(roots, curve.p, params)
            rankings.append(ranking)
            pole_set.update(map_poles)
        expected = []
        positions = [0, 0]
        while len(expected) < required:
            changed = False
            for index in range(2):
                while positions[index] < len(rankings[index]):
                    candidate = rankings[index][positions[index]]
                    positions[index] += 1
                    if candidate not in expected:
                        expected.append(candidate)
                        changed = True
                        break
                if len(expected) == required:
                    break
            if not changed:
                raise AssertionError("independent two-map selection stalled")
        if positions != record["parameters"]["alternating_positions"]:
            raise AssertionError("two-map positions mismatch")
        poles = sorted(pole_set)
    elif family == "hash_x_null":
        if record["parameters"] != {"replicate": replicate}:
            raise AssertionError("hash-null parameter mismatch")
        curve_info = row["curve"]
        token = [curve_info[key] for key in ("p", "a", "b", "q", "seed")]
        ranked = []
        for x in roots:
            value = hashlib.sha256(
                stable_bytes(
                    {
                        "domain": "sgcp-002-hash-x-null",
                        "curve": token,
                        "B": B,
                        "replicate": replicate,
                        "x": x,
                    }
                )
            ).hexdigest()
            ranked.append((value, x))
        expected = [x for _, x in sorted(ranked)[:required]]
        poles = []
    else:
        raise ValueError(f"unknown family {family!r}")
    if sorted(expected) != record["selected_roots"]:
        raise AssertionError("predicate selected-root mismatch")
    if poles != record["excluded_poles"]:
        raise AssertionError("predicate pole audit mismatch")
    if polynomial(sorted(expected), curve.p) != record["root_polynomial_coefficients_ascending_mod_p"]:
        raise AssertionError("root polynomial mismatch")
    factors = sorted(
        (point for root in expected for point in fibers[root]), key=point_order
    )
    if ["O" if point is None else [point[0], point[1]] for point in factors] != record["points"]:
        raise AssertionError("factor point list mismatch")
    if len(factors) != B or any(curve.negate(point) not in factors for point in factors):
        raise AssertionError("factor-base cardinality or sign mismatch")
    if (
        record["admissible_root_count"] != len(roots)
        or record["selected_root_count"] != required
        or record["negation_symmetric"] is not True
    ):
        raise AssertionError("factor-base count/flag mismatch")
    return factors


def subsets(formal: Formal) -> set[Formal]:
    result: set[Formal] = {()}
    for degree in range(1, len(formal) + 1):
        result.update(itertools.combinations(formal, degree))
    return result


def ideal(B: int, maxima: Iterable[Formal]) -> set[Formal]:
    result: set[Formal] = {(), *((index,) for index in range(B))}
    for maximum in maxima:
        result.update(subsets(tuple(sorted(maximum))))
    return result


def evaluate(curve: Curve, factors: Sequence[Point], formal: Formal) -> Point:
    result: Point = None
    for index in formal:
        result = curve.plus(result, factors[index])
    return result


def injective_map(
    curve: Curve, factors: Sequence[Point], family: Iterable[Formal]
) -> tuple[dict[Point, Formal], bool]:
    by_point: dict[Point, Formal] = {}
    for formal in sorted(set(family), key=lambda value: (len(value), value)):
        point = evaluate(curve, factors, formal)
        if point in by_point and by_point[point] != formal:
            return by_point, False
        by_point[point] = formal
    return by_point, True


def point_record(point: Point) -> str | list[int]:
    return "O" if point is None else [point[0], point[1]]


def collision_record(left: Formal, right: Formal, point: Point) -> dict[str, Any]:
    return {
        "left": list(left),
        "right": list(right),
        "point": point_record(point),
    }


def reconstruct_graph(
    curve: Curve, factors: Sequence[Point]
) -> tuple[
    list[dict[str, Any]],
    list[int],
    int,
    int,
    list[Point],
    dict[str, Any],
    list[int],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    degree2: dict[Point, list[Formal]] = defaultdict(list)
    for formal in itertools.combinations_with_replacement(range(len(factors)), 2):
        degree2[evaluate(curve, factors, formal)].append(formal)
    canonical2 = [
        (point, min(degree2[point]))
        for point in sorted(degree2, key=point_order)
        if point is not None
    ]
    representative_records = [
        {
            "point": [point[0], point[1]],
            "formal": list(formal),
        }
        for point, formal in canonical2
    ]
    compiler = {
        "id": REPRESENTATIVE_COMPILER,
        "identity_output_excluded": True,
        "representative_count": len(representative_records),
        "representatives": representative_records,
        "representatives_sha256": digest(representative_records),
    }
    by_formal: dict[Formal, list[tuple[Point, tuple[Formal, Formal]]]] = defaultdict(list)
    raw_a4: set[Point] = set()
    for left_index, right_index in itertools.combinations_with_replacement(
        range(len(canonical2)), 2
    ):
        left_point, left_formal = canonical2[left_index]
        right_point, right_formal = canonical2[right_index]
        formal = tuple(sorted(left_formal + right_formal))
        point = curve.plus(left_point, right_point)
        by_formal[formal].append((point, tuple(sorted((left_formal, right_formal)))))
        raw_a4.add(point)
    candidates: list[dict[str, Any]] = []
    for formal in sorted(by_formal):
        points = {entry[0] for entry in by_formal[formal]}
        if len(points) != 1:
            raise AssertionError("inconsistent formal evaluation")
        candidates.append({"formal": formal, "point": next(iter(points))})
    eligible: list[dict[str, Any]] = []
    eligible_universe_indices: list[int] = []
    rejected: list[dict[str, Any]] = []
    maps: list[dict[Point, Formal]] = []
    for universe_index, candidate in enumerate(candidates):
        family = ideal(len(factors), [candidate["formal"]])
        mapping: dict[Point, Formal] = {}
        first_collision: tuple[Formal, Formal, Point] | None = None
        for formal in sorted(family, key=lambda value: (len(value), value)):
            point = evaluate(curve, factors, formal)
            if point in mapping:
                first_collision = (mapping[point], formal, point)
                break
            mapping[point] = formal
        valid = first_collision is None
        if valid:
            eligible.append(candidate)
            eligible_universe_indices.append(universe_index)
            maps.append(mapping)
        else:
            assert first_collision is not None
            rejected.append(
                {
                    "universe_index": universe_index,
                    "formal": list(candidate["formal"]),
                    "point": point_record(candidate["point"]),
                    "first_collision": collision_record(*first_collision),
                }
            )
    conflicts = [0] * len(eligible)
    conflict_records: list[dict[str, Any]] = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            first_collision = next(
                (
                    (maps[left][point], maps[right][point], point)
                    for point in sorted(
                        set(maps[left]).intersection(maps[right]), key=point_order
                    )
                    if maps[left][point] != maps[right][point]
                ),
                None,
            )
            if first_collision is not None:
                conflicts[left] |= 1 << right
                conflicts[right] |= 1 << left
                conflict_records.append(
                    {
                        "left": left,
                        "right": right,
                        "left_universe_index": eligible_universe_indices[left],
                        "right_universe_index": eligible_universe_indices[right],
                        "first_collision": collision_record(*first_collision),
                    }
                )
    return (
        eligible,
        conflicts,
        len(candidates),
        len(conflict_records),
        sorted(raw_a4, key=point_order),
        compiler,
        eligible_universe_indices,
        rejected,
        conflict_records,
    )


def independent_graph_metrics(conflicts: Sequence[int]) -> dict[str, Any]:
    count = len(conflicts)
    degrees = [(mask & ((1 << count) - 1)).bit_count() for mask in conflicts]
    unseen = set(range(count))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        component: list[int] = []
        while stack:
            vertex = stack.pop()
            component.append(vertex)
            neighbors = set(bits(conflicts[vertex])) & unseen
            unseen.difference_update(neighbors)
            stack.extend(sorted(neighbors, reverse=True))
        components.append(sorted(component))
    remaining = set(range(count))
    degeneracy = 0
    while remaining:
        vertex = min(
            remaining,
            key=lambda item: (
                sum(neighbor in remaining for neighbor in bits(conflicts[item])),
                item,
            ),
        )
        degree = sum(neighbor in remaining for neighbor in bits(conflicts[vertex]))
        degeneracy = max(degeneracy, degree)
        remaining.remove(vertex)
    histogram = Counter(degrees)
    return {
        "vertices": count,
        "edges": sum(degrees) // 2,
        "components": [len(component) for component in components],
        "component_count": len(components),
        "degree_min": min(degrees, default=0),
        "degree_max": max(degrees, default=0),
        "degree_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        "degeneracy": degeneracy,
    }


def support_counter(curve: Curve, values: Sequence[Point]) -> Counter[Point]:
    ordered = sorted(set(values), key=point_order)
    result: Counter[Point] = Counter()
    for left_index, left in enumerate(ordered):
        for right in ordered[left_index:]:
            result[curve.plus(left, right)] += 1
    return result


def expansion_metrics(curve: Curve, factors: Sequence[Point]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for degree in (1, 2, 4, 8):
        formal_multiplicities: Counter[Point] = Counter()
        ordered_multiplicities: Counter[Point] = Counter()
        for formal in itertools.combinations_with_replacement(range(len(factors)), degree):
            point = evaluate(curve, factors, formal)
            formal_multiplicities[point] += 1
            orderings = math.factorial(degree)
            for count in Counter(formal).values():
                orderings //= math.factorial(count)
            ordered_multiplicities[point] += orderings
        formal_histogram = Counter(formal_multiplicities.values())
        ordered_histogram = Counter(ordered_multiplicities.values())
        if sum(ordered_multiplicities.values()) != len(factors) ** degree:
            raise AssertionError("independent ordered-tuple recount mismatch")
        result[str(degree)] = {
            "support": len(formal_multiplicities),
            "formal_multiset_witness_count": sum(formal_multiplicities.values()),
            "formal_multiset_collision_energy": sum(
                value * value for value in formal_multiplicities.values()
            ),
            "formal_multiset_maximum_multiplicity": max(
                formal_multiplicities.values(), default=0
            ),
            "formal_multiset_multiplicity_histogram": {
                str(key): formal_histogram[key] for key in sorted(formal_histogram)
            },
            "ordered_tuple_witness_count": sum(ordered_multiplicities.values()),
            "ordered_tuple_additive_energy": sum(
                value * value for value in ordered_multiplicities.values()
            ),
            "ordered_tuple_maximum_multiplicity": max(
                ordered_multiplicities.values(), default=0
            ),
            "ordered_tuple_multiplicity_histogram": {
                str(key): ordered_histogram[key] for key in sorted(ordered_histogram)
            },
        }
    return result


def clique_cover(mask: int, conflicts: Sequence[int]) -> int:
    groups: list[int] = []
    order = sorted(bits(mask), key=lambda vertex: (-(conflicts[vertex] & mask).bit_count(), vertex))
    for vertex in order:
        for index, group in enumerate(groups):
            if conflicts[vertex] & group == group:
                groups[index] |= 1 << vertex
                break
        else:
            groups.append(1 << vertex)
    return len(groups)


def verify_frontier_certificate(
    pair_outputs: Sequence[Sequence[int]],
    point_count: int,
    conflicts: Sequence[int],
    optimizer: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    candidate_count = len(conflicts)
    all_mask = (1 << candidate_count) - 1
    global_output_masks = [0] * candidate_count
    for left in range(candidate_count):
        for right in range(candidate_count):
            global_output_masks[left] |= 1 << pair_outputs[left][right]

    states = optimizer.get("frontier_states")
    if not isinstance(states, list):
        return ["optimizer frontier_states is not a list"]
    if digest(states) != optimizer.get("frontier_sha256"):
        errors.append("optimizer frontier digest mismatch")
    if len(states) != optimizer.get("remaining_frontier_nodes"):
        errors.append("optimizer frontier count mismatch")

    observed_upper = optimizer["retained_support_lower_bound"]
    for position, state in enumerate(states):
        try:
            selected = int(state["selected_mask_hex"], 16)
            available = int(state["available_mask_hex"], 16)
            selected_support = int(state["selected_support_mask_hex"], 16)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"frontier[{position}] malformed masks: {error}")
            continue
        if selected & available or (selected | available) & ~all_mask:
            errors.append(f"frontier[{position}] mask-domain mismatch")
        if any(conflicts[vertex] & selected for vertex in bits(selected)):
            errors.append(f"frontier[{position}] selected set is not independent")
        if any(conflicts[vertex] & selected for vertex in bits(available)):
            errors.append(f"frontier[{position}] available vertex conflicts with selected")
        expected_support = 0
        selected_vertices = list(bits(selected))
        for left_index, left in enumerate(selected_vertices):
            for right in selected_vertices[left_index:]:
                expected_support |= 1 << pair_outputs[left][right]
        if selected_support != expected_support:
            errors.append(f"frontier[{position}] selected support mismatch")
        alpha = clique_cover(available, conflicts)
        pair_capacity = selected.bit_count() * alpha + alpha * (alpha + 1) // 2
        output_upper = selected_support
        for vertex in bits(available):
            output_upper |= global_output_masks[vertex]
        support_upper = min(
            point_count,
            selected_support.bit_count() + pair_capacity,
            output_upper.bit_count(),
        )
        count_upper = selected.bit_count() + alpha
        if support_upper != state.get("support_upper_bound"):
            errors.append(f"frontier[{position}] support upper-bound mismatch")
        if count_upper != state.get("selected_count_upper_bound"):
            errors.append(f"frontier[{position}] count upper-bound mismatch")
        observed_upper = max(observed_upper, support_upper)
    if observed_upper != optimizer.get("retained_support_upper_bound"):
        errors.append("optimizer aggregate frontier upper-bound mismatch")
    return errors


def replay_density_search(
    pair_outputs: Sequence[Sequence[int]],
    point_count: int,
    conflicts: Sequence[int],
    node_cap: int,
    constrained_cap: int,
    tiebreak: Any,
) -> dict[str, Any]:
    candidate_count = len(conflicts)
    metric_cache: dict[int, dict[str, Any]] = {}

    def metrics(mask: int) -> dict[str, Any]:
        if mask not in metric_cache:
            metric_cache[mask] = tiebreak(mask)
        return metric_cache[mask]

    def feasible(mask: int) -> bool:
        return metrics(mask)["constrained_count"] <= constrained_cap

    global_outputs = [0] * candidate_count
    for left in range(candidate_count):
        for right in range(candidate_count):
            global_outputs[left] |= 1 << pair_outputs[left][right]

    best_mask = 0
    best_support = 0
    best_metrics = metrics(0)
    if not feasible(0):
        raise AssertionError("replay cap does not admit empty operation")
    incumbent_updates = 0

    def objective(mask: int, support: int, row_metrics: dict[str, Any]) -> tuple[int, int, int, int]:
        return (
            support.bit_count(),
            -row_metrics["constrained_count"],
            -row_metrics["public_edge_count"],
            mask.bit_count(),
        )

    def better(mask: int, support: int, row_metrics: dict[str, Any]) -> bool:
        candidate_key = objective(mask, support, row_metrics)
        best_key = objective(best_mask, best_support, best_metrics)
        if candidate_key != best_key:
            return candidate_key > best_key
        return tuple(row_metrics["witness_list"]) < tuple(best_metrics["witness_list"])

    def update(mask: int, support: int) -> None:
        nonlocal best_mask, best_support, best_metrics, incumbent_updates
        row_metrics = metrics(mask)
        if row_metrics["constrained_count"] > constrained_cap:
            return
        if better(mask, support, row_metrics):
            best_mask = mask
            best_support = support
            best_metrics = row_metrics
            incumbent_updates += 1

    def add(mask: int, support: int, vertex: int) -> tuple[int, int]:
        for selected in bits(mask):
            support |= 1 << pair_outputs[selected][vertex]
        support |= 1 << pair_outputs[vertex][vertex]
        return mask | (1 << vertex), support

    def greedy(order: Sequence[int]) -> None:
        mask = 0
        support = 0
        blocked = 0
        for vertex in order:
            bit = 1 << vertex
            if blocked & bit:
                continue
            candidate_mask, candidate_support = add(mask, support, vertex)
            if not feasible(candidate_mask):
                continue
            mask, support = candidate_mask, candidate_support
            blocked |= conflicts[vertex] | bit
        update(mask, support)

    natural = list(range(candidate_count))
    greedy(natural)
    greedy(list(reversed(natural)))
    greedy(sorted(natural, key=lambda vertex: (conflicts[vertex].bit_count(), vertex)))
    greedy(sorted(natural, key=lambda vertex: (-conflicts[vertex].bit_count(), vertex)))

    mask = 0
    support = 0
    allowed = (1 << candidate_count) - 1
    while allowed:
        choices: list[tuple[int, int, int, int]] = []
        for vertex in bits(allowed):
            candidate_mask, candidate_support = add(mask, support, vertex)
            if not feasible(candidate_mask):
                continue
            choices.append(
                (
                    (candidate_support ^ support).bit_count(),
                    -(conflicts[vertex] & allowed).bit_count(),
                    -vertex,
                    vertex,
                )
            )
        if not choices:
            break
        vertex = max(choices)[-1]
        mask, support = add(mask, support, vertex)
        allowed &= ~(conflicts[vertex] | (1 << vertex))
    update(mask, support)

    bound_calls = 0

    def bounds_for(mask: int, allowed: int, support: int) -> tuple[int, int]:
        nonlocal bound_calls
        bound_calls += 1
        alpha = clique_cover(allowed, conflicts)
        pair_capacity = mask.bit_count() * alpha + alpha * (alpha + 1) // 2
        output_upper = support
        for vertex in bits(allowed):
            output_upper |= global_outputs[vertex]
        return (
            min(
                point_count,
                support.bit_count() + pair_capacity,
                output_upper.bit_count(),
            ),
            mask.bit_count() + alpha,
        )

    def can_improve(upper_support: int, upper_count: int, mask: int) -> bool:
        best_support_count = best_support.bit_count()
        if upper_support < best_support_count:
            return False
        if upper_support > best_support_count:
            return True
        current = metrics(mask)
        if current["constrained_count"] > best_metrics["constrained_count"]:
            return False
        if (
            current["constrained_count"] == best_metrics["constrained_count"]
            and current["public_edge_count"] > best_metrics["public_edge_count"]
        ):
            return False
        if (
            current["constrained_count"] == best_metrics["constrained_count"]
            and current["public_edge_count"] == best_metrics["public_edge_count"]
            and upper_count < best_mask.bit_count()
        ):
            return False
        return True

    frontier: list[tuple[int, int, int, int, int, int]] = []
    sequence = 0

    def push(mask: int, allowed: int, support: int) -> None:
        nonlocal sequence
        if not feasible(mask):
            return
        if allowed == 0:
            update(mask, support)
            return
        upper_support, upper_count = bounds_for(mask, allowed, support)
        if not can_improve(upper_support, upper_count, mask):
            return
        sequence += 1
        heapq.heappush(
            frontier,
            (-upper_support, -upper_count, sequence, mask, allowed, support),
        )

    push(0, (1 << candidate_count) - 1, 0)
    explored = 0
    while frontier and explored < node_cap:
        neg_support, neg_count, _, mask, allowed, support = heapq.heappop(frontier)
        if not can_improve(-neg_support, -neg_count, mask):
            continue
        explored += 1
        vertex = max(
            bits(allowed),
            key=lambda item: (
                (conflicts[item] & allowed).bit_count(),
                sum(
                    1
                    for selected in bits(mask)
                    if not (support & (1 << pair_outputs[selected][item]))
                ),
                -item,
            ),
        )
        include_mask, include_support = add(mask, support, vertex)
        without = allowed & ~(1 << vertex)
        push(include_mask, without & ~conflicts[vertex], include_support)
        push(mask, without, support)

    frontier = [
        node
        for node in frontier
        if can_improve(-node[0], -node[1], node[3])
    ]
    heapq.heapify(frontier)
    states = [
        {
            "selected_mask_hex": hex(node[3]),
            "available_mask_hex": hex(node[4]),
            "selected_support_mask_hex": hex(node[5]),
            "support_upper_bound": -node[0],
            "selected_count_upper_bound": -node[1],
        }
        for node in sorted(frontier, key=lambda item: (item[3], item[4], item[5], item[0], item[1]))
    ]
    upper = max(best_support.bit_count(), max((-node[0] for node in frontier), default=0))
    return {
        "selected_indices": list(bits(best_mask)),
        "selected_mask_hex": hex(best_mask),
        "retained_support_lower_bound": best_support.bit_count(),
        "retained_support_upper_bound": upper,
        "absolute_gap": upper - best_support.bit_count(),
        "primary_exact": upper == best_support.bit_count(),
        "full_objective_exact": not frontier,
        "selected_count": best_mask.bit_count(),
        "constrained_count": best_metrics["constrained_count"],
        "public_edge_count": best_metrics["public_edge_count"],
        "witness_list": best_metrics["witness_list"],
        "explored_nodes": explored,
        "remaining_frontier_nodes": len(frontier),
        "frontier_states": states,
        "frontier_sha256": digest(states),
        "incumbent_updates": incumbent_updates,
        "bound_calls": bound_calls,
        "termination_reason": "full_objective_proved" if not frontier else "node_cap",
    }


def independent_primary_optimum(
    curve: Curve,
    candidates: Sequence[dict[str, Any]],
    conflicts: Sequence[int],
    incumbent_mask: int,
    maximum_nodes: int = 5000000,
) -> tuple[int, int, bool]:
    points = [candidate["point"] for candidate in candidates]
    group = curve.points()
    point_index = {point: index for index, point in enumerate(group)}
    outputs = [
        [point_index[curve.plus(left, right)] for right in points]
        for left in points
    ]

    def selected_support(mask: int) -> int:
        selected = list(bits(mask))
        result = 0
        for position, left in enumerate(selected):
            for right in selected[position:]:
                result |= 1 << outputs[left][right]
        return result

    best = selected_support(incumbent_mask).bit_count()
    all_mask = (1 << len(candidates)) - 1
    stack: list[tuple[int, int]] = [(0, all_mask)]
    explored = 0
    while stack and explored < maximum_nodes:
        chosen, available = stack.pop()
        explored += 1
        active = chosen | available
        possible_outputs = 0
        active_vertices = list(bits(active))
        for position, left in enumerate(active_vertices):
            for right in active_vertices[position:]:
                possible_outputs |= 1 << outputs[left][right]
        chosen_support = selected_support(chosen)
        alpha = clique_cover(available, conflicts)
        selected_count = chosen.bit_count()
        pair_capacity = selected_count * alpha + alpha * (alpha + 1) // 2
        upper = min(
            possible_outputs.bit_count(),
            chosen_support.bit_count() + pair_capacity,
            len(group),
        )
        if upper <= best:
            continue
        if available == 0:
            best = max(best, chosen_support.bit_count())
            continue
        vertex = max(
            bits(available),
            key=lambda item: ((conflicts[item] & available).bit_count(), -item),
        )
        without = available & ~(1 << vertex)
        stack.append((chosen, without))
        stack.append(
            (
                chosen | (1 << vertex),
                without & ~conflicts[vertex],
            )
        )
    return best, explored, not stack


def independent_density_primary_optimum(
    curve: Curve,
    factors: Sequence[Point],
    candidates: Sequence[dict[str, Any]],
    conflicts: Sequence[int],
    incumbent_mask: int,
    constrained_cap: int,
    maximum_nodes: int,
) -> tuple[int, int, bool]:
    points = [candidate["point"] for candidate in candidates]
    group = curve.points()
    point_index = {point: index for index, point in enumerate(group)}
    outputs = [
        [point_index[curve.plus(left, right)] for right in points]
        for left in points
    ]
    support_cache: dict[int, int] = {}
    constrained_cache: dict[int, int] = {}

    def selected_support(mask: int) -> int:
        if mask not in support_cache:
            selected = list(bits(mask))
            value = 0
            for position, left in enumerate(selected):
                for right in selected[position:]:
                    value |= 1 << outputs[left][right]
            support_cache[mask] = value
        return support_cache[mask]

    def constrained(mask: int) -> int:
        if mask not in constrained_cache:
            maxima = [candidates[index]["formal"] for index in bits(mask)]
            constrained_cache[mask] = retained_model(curve, factors, maxima)[0]
        return constrained_cache[mask]

    if constrained(incumbent_mask) > constrained_cap:
        raise AssertionError("producer incumbent exceeds independent density cap")
    best = selected_support(incumbent_mask).bit_count()
    stack: list[tuple[int, int]] = [(0, (1 << len(candidates)) - 1)]
    explored = 0
    while stack and explored < maximum_nodes:
        chosen, available = stack.pop()
        explored += 1
        if constrained(chosen) > constrained_cap:
            continue
        chosen_support = selected_support(chosen)
        best = max(best, chosen_support.bit_count())
        active = chosen | available
        possible_outputs = 0
        active_vertices = list(bits(active))
        for position, left in enumerate(active_vertices):
            for right in active_vertices[position:]:
                possible_outputs |= 1 << outputs[left][right]
        alpha = clique_cover(available, conflicts)
        pair_capacity = chosen.bit_count() * alpha + alpha * (alpha + 1) // 2
        upper = min(
            possible_outputs.bit_count(),
            chosen_support.bit_count() + pair_capacity,
            len(group),
        )
        if upper <= best or available == 0:
            continue
        vertex = max(
            bits(available),
            key=lambda item: ((conflicts[item] & available).bit_count(), -item),
        )
        without = available & ~(1 << vertex)
        stack.append((chosen, without))
        stack.append((chosen | (1 << vertex), without & ~conflicts[vertex]))
    return best, explored, not stack


def retained_model(
    curve: Curve, factors: Sequence[Point], maxima: Sequence[Formal]
) -> tuple[
    int,
    int,
    int,
    dict[str, Any],
    list[dict[str, str]],
    list[dict[str, Any]],
]:
    family = ideal(len(factors), maxima)
    mapping, injective = injective_map(curve, factors, family)
    inverse = {formal: point for point, formal in mapping.items()}
    nonempty = sorted((formal for formal in family if formal), key=lambda value: (len(value), value))
    edges: list[tuple[Formal, Formal, Formal]] = []
    compatible = True
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union not in family:
                continue
            edges.append((left, right, union))
            if curve.plus(inverse[left], inverse[right]) != inverse[union]:
                compatible = False
    constrained: set[Point] = {None}
    for left, right, output in edges:
        constrained.update((inverse[left], inverse[right], inverse[output]))
    forbidden_count = sum(
        len(left) == 4 and len(right) == 4 for left, right, _ in edges
    )
    source_table = [
        {"label": label(point), "formal": list(mapping[point])}
        for point in sorted(constrained, key=point_order)
    ]
    source_table_valid = (
        len(source_table) == len(constrained)
        and len({entry["label"] for entry in source_table}) == len(constrained)
    )
    axioms = {
        "identity": True,
        "commutativity": True,
        "associativity": all(subsets(formal).issubset(family) for formal in family),
        "associativity_method": "downward-closed formal multiset union",
        "compatibility_coordinates": compatible,
        "injective_evaluation": injective,
        "unique_prime_multiset_factorization": injective,
        "acyclic_by_formal_degree": all(
            len(output) > max(len(left), len(right)) for left, right, output in edges
        ),
        "source_recovery": all(tuple(sorted(formal)) == formal for formal in family),
        "source_recovery_via_public_table": source_table_valid,
        "direct_final_edge_excluded": forbidden_count == 0,
        "direct_final_edge_absent_by_construction": forbidden_count == 0,
        "forbidden_final_edge_count": forbidden_count,
    }
    public_edges = [
        {
            "left": label(inverse[left]),
            "right": label(inverse[right]),
            "output": label(inverse[output]),
        }
        for left, right, output in edges
    ]
    return (
        len(constrained),
        len(edges),
        len(family),
        axioms,
        public_edges,
        source_table,
    )


def verify_row(row: dict[str, Any], maximum_nodes: int) -> dict[str, Any]:
    errors: list[str] = []
    supplied_digest = row.get("row_sha256")
    payload = dict(row)
    payload.pop("row_sha256", None)
    if supplied_digest != digest(payload):
        errors.append("row digest mismatch")
    info = row["curve"]
    curve = Curve(info["p"], info["a"], info["b"])
    group = curve.points()
    q = len(group)
    expected_curve = {
        "q": q,
        "trace": curve.p + 1 - q,
        "j": curve.j(),
        "generator": "O" if group[1] is None else [group[1][0], group[1][1]],
    }
    for key, value in expected_curve.items():
        if info.get(key) != value:
            errors.append(f"curve {key} mismatch")
    if not is_prime(q) or q.bit_length() != info["bits"]:
        errors.append("curve group-order acceptance mismatch")
    if info["trace"] in (0, 1) or info["j"] in (0, 1728 % curve.p):
        errors.append("curve special-case rejection mismatch")
    try:
        factors = verify_factor_base(curve, group, row)
    except Exception as error:
        errors.append(f"factor base: {error}")
        factors = []
    if not factors:
        return {"valid": False, "errors": errors, "primary_nodes": 0}

    eligible, conflicts, candidate_count, conflict_count, raw_a4, *_ = reconstruct_graph(
        curve, factors
    )
    graph = row["private_audit"]["graph"]
    observed_graph = (
        graph["candidate_count"],
        graph["eligible_candidate_count"],
        graph["conflict_count"],
    )
    expected_graph = (candidate_count, len(eligible), conflict_count)
    if observed_graph != expected_graph:
        errors.append(f"graph count mismatch: {observed_graph!r} != {expected_graph!r}")

    by_formal = {candidate["formal"]: index for index, candidate in enumerate(eligible)}
    selected_formals = [tuple(value) for value in row["public_model"]["selected_maxima"]]
    try:
        selected_indices = [by_formal[formal] for formal in selected_formals]
    except KeyError as error:
        errors.append(f"selected maximum is not independently eligible: {error}")
        selected_indices = []
    selected_mask = sum(1 << index for index in selected_indices)
    if any(conflicts[index] & selected_mask for index in selected_indices):
        errors.append("selected maxima are not graph independent")
    selected_points = [eligible[index]["point"] for index in selected_indices]
    retained = support_counter(curve, selected_points)
    raw = support_counter(curve, raw_a4)
    retention = row["private_audit"]["retention"]
    if (len(raw), len(retained)) != (
        retention["raw_final_support"],
        retention["retained_final_support"],
    ):
        errors.append("retention support mismatch")
    if (
        max(raw.values(), default=0),
        max(retained.values(), default=0),
    ) != (
        retention["raw_maximum_multiplicity"],
        retention["retained_maximum_multiplicity"],
    ):
        errors.append("retention multiplicity mismatch")
    if expansion_metrics(curve, factors) != row["private_audit"]["expansion"]:
        errors.append("additive expansion mismatch")

    constrained, edge_count, family_count, axioms, public_edges, _ = retained_model(
        curve, factors, selected_formals
    )
    public = row["public_model"]
    if (constrained, edge_count, family_count) != (
        public["constrained_count"],
        public["public_edge_count"],
        public["formal_family_count"],
    ):
        errors.append("retained model count mismatch")
    for key, value in axioms.items():
        if public["axioms"].get(key) != value:
            errors.append(f"axiom mismatch: {key}")
    if public_edges != public["public_edges"]:
        errors.append("public edge table mismatch")
    if digest(public_edges) != public["public_edges_sha256"]:
        errors.append("public edge digest mismatch")
    expected_delta_divisor = math.gcd(constrained, q)
    expected_delta = {
        "numerator": constrained // expected_delta_divisor,
        "denominator": q // expected_delta_divisor,
    }
    if public["delta"] != expected_delta:
        errors.append("constrained-density ratio mismatch")

    if selected_indices != row["private_audit"]["optimizer"]["selected_indices"]:
        errors.append("optimizer selected-index mismatch")
    if hex(selected_mask) != row["private_audit"]["optimizer"]["selected_mask_hex"]:
        errors.append("optimizer selected-mask mismatch")

    optimum, primary_nodes, complete = independent_primary_optimum(
        curve, eligible, conflicts, selected_mask, maximum_nodes
    )
    optimizer = row["private_audit"]["optimizer"]
    lower = optimizer["retained_support_lower_bound"]
    upper = optimizer["retained_support_upper_bound"]
    if complete:
        if not lower <= optimum <= upper:
            errors.append("producer optimizer interval excludes independent optimum")
        if optimizer["primary_exact"] and not (lower == upper == optimum):
            errors.append("producer exact primary optimum mismatch")
    return {
        "valid": not errors and complete,
        "errors": errors,
        "curve": {"p": curve.p, "a": curve.a, "b": curve.b, "q": q},
        "B": row["B"],
        "family": row["family"],
        "null_replicate": row["null_replicate"],
        "candidate_count": candidate_count,
        "eligible_candidate_count": len(eligible),
        "conflict_count": conflict_count,
        "independent_primary_optimum": optimum,
        "producer_primary_interval": [lower, upper],
        "primary_nodes": primary_nodes,
        "primary_proof_complete": complete,
    }


def v3_row_schema_errors(row: Any) -> list[str]:
    errors: list[str] = []
    try:
        require_keys(
            row,
            {
                "protocol_version",
                "curve",
                "B",
                "family",
                "null_replicate",
                "valid",
                "public_model",
                "private_audit",
                "structural_work",
                "wall_time_seconds",
                "accounting",
                "row_sha256",
            },
            "density row",
        )
        require_keys(
            row["public_model"],
            {
                "factor_base",
                "representative_compiler",
                "constrained_budget_caps",
                "density_frontier",
            },
            "public model",
        )
        require_keys(
            row["public_model"]["representative_compiler"],
            {
                "id",
                "identity_output_excluded",
                "representative_count",
                "representatives",
                "representatives_sha256",
            },
            "representative compiler",
        )
        for index, record in enumerate(
            row["public_model"]["representative_compiler"]["representatives"]
        ):
            require_keys(record, {"point", "formal"}, f"representative[{index}]")
        axiom_keys = {
            "identity",
            "commutativity",
            "associativity",
            "associativity_method",
            "compatibility_coordinates",
            "injective_evaluation",
            "unique_prime_multiset_factorization",
            "acyclic_by_formal_degree",
            "source_recovery",
            "source_recovery_via_public_table",
            "direct_final_edge_excluded",
            "direct_final_edge_absent_by_construction",
            "forbidden_final_edge_count",
        }
        public_cap_keys = {
            "constrained_cap",
            "selected_maxima",
            "formal_family_count",
            "formal_degree_histogram",
            "axioms",
            "constrained_count",
            "delta",
            "public_edge_count",
            "public_edges",
            "public_edges_sha256",
            "source_table",
            "source_table_sha256",
        }
        for index, public in enumerate(row["public_model"]["density_frontier"]):
            require_keys(public, public_cap_keys, f"public cap[{index}]")
            require_keys(public["axioms"], axiom_keys, f"public cap[{index}] axioms")
            require_keys(public["delta"], {"numerator", "denominator"}, f"cap[{index}] delta")
            for edge_index, edge in enumerate(public["public_edges"]):
                require_keys(
                    edge,
                    {"left", "right", "output"},
                    f"cap[{index}] edge[{edge_index}]",
                )
            for source_index, source in enumerate(public["source_table"]):
                require_keys(
                    source,
                    {"label", "formal"},
                    f"cap[{index}] source[{source_index}]",
                )
        require_keys(
            row["private_audit"],
            {
                "graph",
                "eligible_universe_indices",
                "individually_rejected",
                "conflicts",
                "density_frontier",
                "expansion",
            },
            "private audit",
        )
        require_keys(
            row["private_audit"]["graph"],
            {
                "candidate_count",
                "eligible_candidate_count",
                "individually_rejected_count",
                "conflict_count",
                "vertices",
                "edges",
                "components",
                "component_count",
                "degree_min",
                "degree_max",
                "degree_histogram",
                "degeneracy",
            },
            "graph metrics",
        )
        collision_keys = {"left", "right", "point"}
        for index, rejected in enumerate(row["private_audit"]["individually_rejected"]):
            require_keys(
                rejected,
                {"universe_index", "formal", "point", "first_collision"},
                f"individually rejected[{index}]",
            )
            require_keys(
                rejected["first_collision"],
                collision_keys,
                f"individually rejected[{index}] collision",
            )
        for index, conflict in enumerate(row["private_audit"]["conflicts"]):
            require_keys(
                conflict,
                {
                    "left",
                    "right",
                    "left_universe_index",
                    "right_universe_index",
                    "first_collision",
                },
                f"conflict[{index}]",
            )
            require_keys(
                conflict["first_collision"],
                collision_keys,
                f"conflict[{index}] collision",
            )
        optimizer_keys = {
            "objective_mode",
            "max_constrained",
            "objective_order",
            "selected_indices",
            "selected_mask_hex",
            "retained_support_lower_bound",
            "retained_support_upper_bound",
            "absolute_gap",
            "primary_exact",
            "full_objective_exact",
            "selected_count",
            "constrained_count",
            "public_edge_count",
            "witness_list",
            "explored_nodes",
            "remaining_frontier_nodes",
            "frontier_states",
            "frontier_sha256",
            "incumbent_updates",
            "bound_calls",
            "termination_reason",
            "node_cap",
            "bound_method",
        }
        retention_keys = {
            "balanced_raw_final_support",
            "eight_fold_support",
            "retained_final_support",
            "retained_to_balanced_raw",
            "retained_to_eight_fold",
            "absolute_group_coverage",
            "balanced_raw_maximum_multiplicity",
            "retained_maximum_multiplicity",
        }
        cap_work_keys = {
            "optimizer_nodes",
            "optimizer_bound_calls",
            "serialized_frontier_states",
            "selected_maxima",
            "retained_final_pair_cells",
            "public_edges",
            "source_table_entries",
        }
        for index, private in enumerate(row["private_audit"]["density_frontier"]):
            require_keys(
                private,
                {
                    "constrained_cap",
                    "optimizer",
                    "retention",
                    "structural_work",
                    "wall_time_seconds",
                },
                f"private cap[{index}]",
            )
            require_keys(private["optimizer"], optimizer_keys, f"optimizer[{index}]")
            for state_index, state in enumerate(private["optimizer"]["frontier_states"]):
                require_keys(
                    state,
                    {
                        "selected_mask_hex",
                        "available_mask_hex",
                        "selected_support_mask_hex",
                        "support_upper_bound",
                        "selected_count_upper_bound",
                    },
                    f"frontier[{index}][{state_index}]",
                )
            require_keys(private["retention"], retention_keys, f"retention[{index}]")
            for ratio_name in (
                "retained_to_balanced_raw",
                "retained_to_eight_fold",
                "absolute_group_coverage",
            ):
                require_keys(
                    private["retention"][ratio_name],
                    {"numerator", "denominator"},
                    f"retention[{index}].{ratio_name}",
                )
            require_keys(private["structural_work"], cap_work_keys, f"cap work[{index}]")
        expansion_keys = {
            "support",
            "formal_multiset_witness_count",
            "formal_multiset_collision_energy",
            "formal_multiset_maximum_multiplicity",
            "formal_multiset_multiplicity_histogram",
            "ordered_tuple_witness_count",
            "ordered_tuple_additive_energy",
            "ordered_tuple_maximum_multiplicity",
            "ordered_tuple_multiplicity_histogram",
        }
        if set(row["private_audit"]["expansion"]) != {"1", "2", "4", "8"}:
            raise AssertionError("expansion degree keys mismatch")
        for degree, expansion in row["private_audit"]["expansion"].items():
            require_keys(expansion, expansion_keys, f"expansion[{degree}]")
        require_keys(
            row["structural_work"],
            {
                "scope",
                "degree_multiset_evaluations",
                "balanced_degree2_formals",
                "balanced_nonidentity_2F_representatives",
                "balanced_degree4_parent_pairs",
                "degree4_candidates",
                "individual_injectivity_checks",
                "conflict_pair_checks",
                "pair_output_cells",
                "balanced_final_pair_cells",
            },
            "row structural work",
        )
        require_keys(
            row["accounting"],
            {
                "scope",
                "public_model_json_bytes",
                "private_audit_json_bytes",
                "row_payload_without_accounting_or_digest_json_bytes",
                "nested_per_cap_json_bytes",
            },
            "row accounting",
        )
        for index, receipt in enumerate(row["accounting"]["nested_per_cap_json_bytes"]):
            require_keys(
                receipt,
                {
                    "constrained_cap",
                    "public_embedding_json_bytes",
                    "private_cap_json_bytes",
                },
                f"nested byte receipt[{index}]",
            )
    except (AssertionError, KeyError, TypeError) as error:
        errors.append(f"closed row schema: {error}")
    errors.extend(forbidden_material(row))
    return errors


def verify_density_row(row: dict[str, Any], maximum_nodes: int) -> dict[str, Any]:
    errors = v3_row_schema_errors(row)
    if errors:
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}
    supplied_digest = row.get("row_sha256")
    payload = dict(row)
    payload.pop("row_sha256", None)
    if supplied_digest != digest(payload):
        errors.append("row digest mismatch")
    if row.get("protocol_version") != PROTOCOL_VERSION:
        errors.append("density row protocol version mismatch")
    if row.get("valid") is not True:
        errors.append("density row does not claim local validity")

    info = row["curve"]
    try:
        curve = verify_curve_provenance(info)
    except Exception as error:
        errors.append(f"curve provenance: {error}")
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}
    group = curve.points()
    q = len(group)
    try:
        factors = verify_factor_base(curve, group, row)
    except Exception as error:
        errors.append(f"factor base: {error}")
        factors = []
    if not factors:
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}

    (
        eligible,
        conflicts,
        candidate_count,
        conflict_count,
        raw_a4,
        representative_compiler,
        eligible_universe_indices,
        rejected,
        conflict_records,
    ) = reconstruct_graph(curve, factors)
    graph = row["private_audit"]["graph"]
    expected_graph = {
        "candidate_count": candidate_count,
        "eligible_candidate_count": len(eligible),
        "individually_rejected_count": candidate_count - len(eligible),
        "conflict_count": conflict_count,
        **independent_graph_metrics(conflicts),
    }
    if graph != expected_graph:
        errors.append("graph metric mismatch")
    if row["private_audit"]["eligible_universe_indices"] != eligible_universe_indices:
        errors.append("eligible universe-index list mismatch")
    if row["private_audit"]["individually_rejected"] != rejected:
        errors.append("individual rejection transcript mismatch")
    if row["private_audit"]["conflicts"] != conflict_records:
        errors.append("conflict transcript mismatch")
    if row["public_model"]["representative_compiler"] != representative_compiler:
        errors.append("representative compiler mismatch")
    expansion = expansion_metrics(curve, factors)
    if expansion != row["private_audit"]["expansion"]:
        errors.append("additive expansion mismatch")
    balanced_raw = support_counter(curve, raw_a4)

    points = [candidate["point"] for candidate in eligible]
    point_index = {point: index for index, point in enumerate(group)}
    pair_outputs = [
        [point_index[curve.plus(left, right)] for right in points]
        for left in points
    ]
    by_formal = {candidate["formal"]: index for index, candidate in enumerate(eligible)}
    public_frontier = row["public_model"]["density_frontier"]
    private_frontier = row["private_audit"]["density_frontier"]
    caps = row["public_model"]["constrained_budget_caps"]
    expected_caps = sorted({max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q})
    if caps != expected_caps:
        errors.append("constrained-budget cap schedule mismatch")
    if len(public_frontier) != len(private_frontier) or len(caps) != len(public_frontier):
        errors.append("density frontier length mismatch")

    accounting = row["accounting"]
    expected_cap_accounting = [
        {
            "constrained_cap": public["constrained_cap"],
            "public_embedding_json_bytes": len(stable_bytes(public)),
            "private_cap_json_bytes": len(stable_bytes(private)),
        }
        for public, private in zip(public_frontier, private_frontier)
    ]
    row_payload = dict(row)
    row_payload.pop("row_sha256")
    row_payload.pop("accounting")
    if accounting != {
        "scope": "nested canonical-JSON byte measures; fields are nonadditive",
        "public_model_json_bytes": len(stable_bytes(row["public_model"])),
        "private_audit_json_bytes": len(stable_bytes(row["private_audit"])),
        "row_payload_without_accounting_or_digest_json_bytes": len(
            stable_bytes(row_payload)
        ),
        "nested_per_cap_json_bytes": expected_cap_accounting,
    }:
        errors.append("cost-accounting byte receipt mismatch")
    expected_structural_work = {
        "scope": "deterministic combinatorial cells; not CPU instructions",
        "degree_multiset_evaluations": sum(
            expansion[str(degree)]["formal_multiset_witness_count"]
            for degree in (1, 2, 4, 8)
        ),
        "balanced_degree2_formals": math.comb(row["B"] + 1, 2),
        "balanced_nonidentity_2F_representatives": representative_compiler[
            "representative_count"
        ],
        "balanced_degree4_parent_pairs": math.comb(
            representative_compiler["representative_count"] + 1, 2
        ),
        "degree4_candidates": candidate_count,
        "individual_injectivity_checks": candidate_count,
        "conflict_pair_checks": len(eligible) * (len(eligible) - 1) // 2,
        "pair_output_cells": len(eligible) * (len(eligible) + 1) // 2,
        "balanced_final_pair_cells": len(raw_a4) * (len(raw_a4) + 1) // 2,
    }
    if row["structural_work"] != expected_structural_work:
        errors.append("row structural-work receipt mismatch")
    cap_wall_times = [private.get("wall_time_seconds") for private in private_frontier]
    row_wall_time = row.get("wall_time_seconds")
    if (
        type(row_wall_time) not in {int, float}
        or not math.isfinite(row_wall_time)
        or row_wall_time < 0
        or any(
            type(value) not in {int, float}
            or not math.isfinite(value)
            or value < 0
            for value in cap_wall_times
        )
        or sum(cap_wall_times) > row_wall_time + 1e-12
    ):
        errors.append("invalid wall-time decomposition")

    cap_reports: list[dict[str, Any]] = []
    for index, (public, private) in enumerate(zip(public_frontier, private_frontier)):
        cap_errors: list[str] = []
        cap = caps[index]
        if public["constrained_cap"] != cap or private["constrained_cap"] != cap:
            cap_errors.append("cap association mismatch")
        selected_formals = [tuple(value) for value in public["selected_maxima"]]
        try:
            selected_indices = [by_formal[formal] for formal in selected_formals]
        except KeyError as error:
            cap_errors.append(f"selected maximum is not eligible: {error}")
            selected_indices = []
        selected_mask = sum(1 << candidate for candidate in selected_indices)
        if any(conflicts[candidate] & selected_mask for candidate in selected_indices):
            cap_errors.append("selected maxima are not graph independent")
        optimizer = private["optimizer"]
        if optimizer.get("objective_mode") != "density" or optimizer.get(
            "max_constrained"
        ) != cap:
            cap_errors.append("optimizer density objective/cap mismatch")
        if optimizer.get("objective_order") != [
            "retained_support:max",
            "constrained_count:min",
            "public_edges:min",
            "retained_maxima:max",
            "witness_list:lex_min",
        ]:
            cap_errors.append("optimizer objective-order mismatch")
        if optimizer.get("bound_method") != (
            "conflict-clique-cover cardinality plus global pair-output union"
        ):
            cap_errors.append("optimizer bound-method mismatch")
        if not (
            optimizer.get("primary_exact") is True
            and optimizer.get("full_objective_exact") is True
            and optimizer.get("absolute_gap") == 0
            and optimizer.get("remaining_frontier_nodes") == 0
            and optimizer.get("frontier_states") == []
            and optimizer.get("termination_reason") == "full_objective_proved"
        ):
            cap_errors.append("V3 requires an exhausted exact optimizer cell")
        if optimizer.get("selected_indices") != selected_indices:
            cap_errors.append("optimizer selected-index mismatch")
        if optimizer.get("selected_mask_hex") != hex(selected_mask):
            cap_errors.append("optimizer selected-mask mismatch")
        if (
            optimizer.get("constrained_count"),
            optimizer.get("public_edge_count"),
            optimizer.get("witness_list"),
        ) != (
            public["constrained_count"],
            public["public_edge_count"],
            public["selected_maxima"],
        ):
            cap_errors.append("optimizer/public model objective-field mismatch")
        cap_errors.extend(
            verify_frontier_certificate(pair_outputs, q, conflicts, optimizer)
        )

        replay_metric_cache: dict[int, dict[str, Any]] = {}

        def replay_metrics(mask: int) -> dict[str, Any]:
            if mask not in replay_metric_cache:
                maxima = [eligible[candidate]["formal"] for candidate in bits(mask)]
                replay_constrained, replay_edges, _, _, _, _ = retained_model(
                    curve, factors, maxima
                )
                replay_metric_cache[mask] = {
                    "constrained_count": replay_constrained,
                    "public_edge_count": replay_edges,
                    "witness_list": [list(formal) for formal in sorted(maxima)],
                }
            return replay_metric_cache[mask]

        replay = replay_density_search(
            pair_outputs,
            q,
            conflicts,
            optimizer["node_cap"],
            cap,
            replay_metrics,
        )
        replay_keys = [
            "selected_indices",
            "selected_mask_hex",
            "retained_support_lower_bound",
            "retained_support_upper_bound",
            "absolute_gap",
            "primary_exact",
            "full_objective_exact",
            "selected_count",
            "constrained_count",
            "public_edge_count",
            "witness_list",
            "explored_nodes",
            "remaining_frontier_nodes",
            "frontier_states",
            "frontier_sha256",
            "incumbent_updates",
            "bound_calls",
            "termination_reason",
        ]
        for key in replay_keys:
            if replay[key] != optimizer.get(key):
                cap_errors.append(f"deterministic search replay mismatch: {key}")

        (
            constrained,
            edge_count,
            family_count,
            axioms,
            public_edges,
            source_table,
        ) = retained_model(
            curve, factors, selected_formals
        )
        if constrained > cap:
            cap_errors.append("attained constrained count exceeds cap")
        if (constrained, edge_count, family_count) != (
            public["constrained_count"],
            public["public_edge_count"],
            public["formal_family_count"],
        ):
            cap_errors.append("retained model count mismatch")
        expected_histogram = Counter(len(formal) for formal in ideal(row["B"], selected_formals))
        if public["formal_degree_histogram"] != {
            str(degree): expected_histogram[degree] for degree in sorted(expected_histogram)
        }:
            cap_errors.append("formal degree histogram mismatch")
        for key, value in axioms.items():
            if public["axioms"].get(key) != value:
                cap_errors.append(f"axiom mismatch: {key}")
        if public_edges != public["public_edges"] or digest(public_edges) != public[
            "public_edges_sha256"
        ]:
            cap_errors.append("public edge table/digest mismatch")
        if source_table != public["source_table"] or digest(source_table) != public[
            "source_table_sha256"
        ]:
            cap_errors.append("public source table/digest mismatch")
        delta_divisor = math.gcd(constrained, q)
        if public["delta"] != {
            "numerator": constrained // delta_divisor,
            "denominator": q // delta_divisor,
        }:
            cap_errors.append("attained density ratio mismatch")

        selected_points = [eligible[candidate]["point"] for candidate in selected_indices]
        retained = support_counter(curve, selected_points)
        retention = private["retention"]
        if (
            len(balanced_raw),
            expansion["8"]["support"],
            len(retained),
        ) != (
            retention["balanced_raw_final_support"],
            retention["eight_fold_support"],
            retention["retained_final_support"],
        ):
            cap_errors.append("retention support mismatch")
        if (
            max(balanced_raw.values(), default=0),
            max(retained.values(), default=0),
        ) != (
            retention["balanced_raw_maximum_multiplicity"],
            retention["retained_maximum_multiplicity"],
        ):
            cap_errors.append("retention multiplicity mismatch")
        balanced_denominator = max(1, len(balanced_raw))
        eight_denominator = max(1, expansion["8"]["support"])
        balanced_divisor = math.gcd(len(retained), balanced_denominator)
        eight_divisor = math.gcd(len(retained), eight_denominator)
        group_divisor = math.gcd(len(retained), q)
        expected_ratios = (
            {
                "numerator": len(retained) // balanced_divisor,
                "denominator": balanced_denominator // balanced_divisor,
            },
            {
                "numerator": len(retained) // eight_divisor,
                "denominator": eight_denominator // eight_divisor,
            },
            {
                "numerator": len(retained) // group_divisor,
                "denominator": q // group_divisor,
            },
        )
        if expected_ratios != (
            retention["retained_to_balanced_raw"],
            retention["retained_to_eight_fold"],
            retention["absolute_group_coverage"],
        ):
            cap_errors.append("retention ratio mismatch")

        expected_cap_work = {
            "optimizer_nodes": optimizer["explored_nodes"],
            "optimizer_bound_calls": optimizer["bound_calls"],
            "serialized_frontier_states": len(optimizer["frontier_states"]),
            "selected_maxima": len(selected_indices),
            "retained_final_pair_cells": len(selected_indices)
            * (len(selected_indices) + 1)
            // 2,
            "public_edges": edge_count,
            "source_table_entries": len(source_table),
        }
        if private["structural_work"] != expected_cap_work:
            cap_errors.append("cap structural-work receipt mismatch")

        optimum, primary_nodes, complete = independent_density_primary_optimum(
            curve,
            factors,
            eligible,
            conflicts,
            selected_mask,
            cap,
            maximum_nodes,
        )
        lower = optimizer["retained_support_lower_bound"]
        upper = optimizer["retained_support_upper_bound"]
        if complete and not (lower == upper == optimum):
            cap_errors.append("producer exact density optimum mismatch")
        cap_reports.append(
            {
                "constrained_cap": cap,
                "valid": not cap_errors and complete,
                "errors": cap_errors,
                "independent_primary_optimum": optimum,
                "producer_primary_interval": [lower, upper],
                "primary_nodes": primary_nodes,
                "primary_proof_complete": complete,
            }
        )
        errors.extend(f"cap[{cap}]: {error}" for error in cap_errors)
        if not complete:
            errors.append(f"cap[{cap}]: independent primary proof hit node cap")

    return {
        "valid": not errors and all(report["valid"] for report in cap_reports),
        "errors": errors,
        "curve": {"p": curve.p, "a": curve.a, "b": curve.b, "q": q},
        "B": row["B"],
        "family": row["family"],
        "null_replicate": row["null_replicate"],
        "candidate_count": candidate_count,
        "eligible_candidate_count": len(eligible),
        "conflict_count": conflict_count,
        "primary_nodes": sum(report["primary_nodes"] for report in cap_reports),
        "cap_reports": cap_reports,
    }


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def fraction_from_record(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def independent_median(values: Sequence[Fraction]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        raise AssertionError("empty median input")
    midpoint = len(ordered) // 2
    if len(ordered) & 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def private_cap(row: dict[str, Any], cap: int) -> dict[str, Any]:
    matches = [
        value
        for value in row["private_audit"]["density_frontier"]
        if value["constrained_cap"] == cap
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one private cap {cap}, found {len(matches)}")
    return matches[0]


def independent_family_gate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    index: dict[tuple[int, int, int, str, int | None], dict[str, Any]] = {}
    for row in rows:
        for cell in row["private_audit"]["density_frontier"]:
            optimizer = cell["optimizer"]
            if not (
                optimizer["primary_exact"] is True
                and optimizer["full_objective_exact"] is True
                and optimizer["absolute_gap"] == 0
            ):
                raise AssertionError("family gate received an unresolved optimizer cell")
        key = (
            row["curve"]["bits"],
            row["curve"]["seed"],
            row["B"],
            row["family"],
            row["null_replicate"],
        )
        if key in index:
            raise AssertionError(f"duplicate family-gate row {key!r}")
        index[key] = row

    reports: list[dict[str, Any]] = []
    winners: list[dict[str, str]] = []
    for family in COORDINATE_FAMILIES:
        persistence_rows: list[dict[str, Any]] = []
        all_persistent = True
        for bit_size in CANONICAL_BITS:
            observed_ratios = [
                fraction_from_record(
                    private_cap(
                        index[(bit_size, seed, B, family, None)],
                        index[(bit_size, seed, B, family, None)]["curve"]["q"],
                    )["retention"]["retained_to_balanced_raw"]
                )
                for seed in CANONICAL_SEEDS
                for B in CANONICAL_FACTOR_BASE_SIZES
            ]
            median_ratio = independent_median(observed_ratios)
            passes = median_ratio >= Fraction(1, 4)
            all_persistent = all_persistent and passes
            persistence_rows.append(
                {
                    "bits": bit_size,
                    "median_retained_to_balanced_raw": fraction_record(median_ratio),
                    "pass": passes,
                }
            )

        tested_caps: list[dict[str, Any]] = []
        for cap_name, cap_multiplier, cap_divisor in (("1/2", 1, 2), ("3/4", 3, 4)):
            positives = 0
            passing_strata = 0
            strata: list[dict[str, Any]] = []
            for bit_size in CANONICAL_BITS:
                threshold_margins: list[Fraction] = []
                for seed in CANONICAL_SEEDS:
                    for B in CANONICAL_FACTOR_BASE_SIZES:
                        candidate = index[(bit_size, seed, B, family, None)]
                        q = candidate["curve"]["q"]
                        cap = cap_multiplier * q // cap_divisor
                        candidate_support = private_cap(candidate, cap)["optimizer"][
                            "retained_support_lower_bound"
                        ]
                        null_values = [
                            private_cap(
                                index[(bit_size, seed, B, NULL_FAMILY, replicate)], cap
                            )["optimizer"]["retained_support_lower_bound"]
                            for replicate in range(CANONICAL_NULL_REPLICATES)
                        ]
                        null_median = independent_median(
                            [Fraction(value, 1) for value in null_values]
                        )
                        difference = Fraction(candidate_support, 1) - null_median
                        positives += int(difference > 0)
                        threshold = max(1, (q + 19) // 20)
                        threshold_margins.append(difference - threshold)
                median_margin = independent_median(threshold_margins)
                stratum_pass = median_margin >= 0
                passing_strata += int(stratum_pass)
                strata.append(
                    {
                        "bits": bit_size,
                        "median_threshold_margin": fraction_record(median_margin),
                        "pass": stratum_pass,
                    }
                )
            cap_pass = passing_strata >= 3 and positives >= 18
            tested_caps.append(
                {
                    "cap_fraction": cap_name,
                    "passing_bit_strata": passing_strata,
                    "positive_comparisons": positives,
                    "comparison_count": 24,
                    "strata": strata,
                    "pass": cap_pass,
                }
            )
            if all_persistent and cap_pass:
                winners.append({"family": family, "cap_fraction": cap_name})
        reports.append(
            {
                "family": family,
                "full_cap_persistence": persistence_rows,
                "full_cap_persistence_pass": all_persistent,
                "matched_null_cap_tests": tested_caps,
            }
        )
    return {
        "criterion_version": "sgcp-embed-002-family-gate-v3",
        "null_median": "exact arithmetic mean of the middle two of four precommitted null supports",
        "null_duplicate_policy": "retain duplicate precommitted null selections without resampling",
        "unresolved_policy": "any nonexact primary or secondary cell invalidates the matrix before gate evaluation",
        "cap_selection_policy": "one fixed family and one fixed cap fraction must pass across strata",
        "status": "PASS" if winners else "FAIL",
        "passing_family_cap_pairs": winners,
        "families": reports,
    }


def expected_canonical_parameters() -> dict[str, Any]:
    return {
        "bits": list(CANONICAL_BITS),
        "seeds": list(CANONICAL_SEEDS),
        "factor_base_sizes": list(CANONICAL_FACTOR_BASE_SIZES),
        "coordinate_families": list(COORDINATE_FAMILIES),
        "null_family": NULL_FAMILY,
        "null_replicates": CANONICAL_NULL_REPLICATES,
        "node_cap_per_cap": CANONICAL_NODE_CAP,
        "representative_compiler": REPRESENTATIVE_COMPILER,
        "constrained_budget_rule": "floor(q/4),floor(q/2),floor(3q/4),q",
    }


def independent_document_summary(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    cap_cells = [
        cap
        for row in rows
        for cap in row["private_audit"]["density_frontier"]
    ]
    return {
        "row_count": len(rows),
        "valid_rows": sum(row["valid"] is True for row in rows),
        "unique_curve_records": len({digest(row["curve"]) for row in rows}),
        "cap_cell_count": len(cap_cells),
        "primary_exact_cap_cells": sum(
            cap["optimizer"]["primary_exact"] is True for cap in cap_cells
        ),
        "full_objective_exact_cap_cells": sum(
            cap["optimizer"]["full_objective_exact"] is True for cap in cap_cells
        ),
        "maximum_primary_gap": max(
            (cap["optimizer"]["absolute_gap"] for cap in cap_cells), default=0
        ),
    }


def expected_row_keys() -> list[tuple[int, int, int, str, int | None]]:
    result: list[tuple[int, int, int, str, int | None]] = []
    for bits_value in CANONICAL_BITS:
        for seed in CANONICAL_SEEDS:
            for B in CANONICAL_FACTOR_BASE_SIZES:
                result.extend(
                    (bits_value, seed, B, family, None)
                    for family in COORDINATE_FAMILIES
                )
                result.extend(
                    (bits_value, seed, B, NULL_FAMILY, replicate)
                    for replicate in range(CANONICAL_NULL_REPLICATES)
                )
    return result


def verify_v3_document_value(
    document: dict[str, Any], maximum_nodes: int
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    try:
        require_keys(
            document,
            {
                "schema",
                "experiment_id",
                "protocol_version",
                "scope",
                "canonical",
                "claim_status",
                "interpretation",
                "parameters",
                "rows",
                "summary",
                "family_gate",
                "document_sha256",
            },
            "V3 document",
        )
    except AssertionError as error:
        return [f"closed document schema: {error}"], []
    supplied = document["document_sha256"]
    payload = dict(document)
    payload.pop("document_sha256")
    if supplied != digest(payload):
        errors.append("document digest mismatch")
    if (
        document["schema"] != "sgcp-embed-002-density-frontier-candidate-v3"
        or document["experiment_id"] != EXPERIMENT_ID
        or document["protocol_version"] != PROTOCOL_VERSION
        or document["claim_status"] != CLAIM_STATUS
    ):
        errors.append("document protocol identity mismatch")

    scope = document["scope"]
    rows = document["rows"]
    if not isinstance(rows, list):
        return [*errors, "document rows is not a list"], []
    if scope == "frozen_fixture":
        node_cap = document["parameters"].get("node_cap_per_cap")
        expected_parameters = {
            "curve": dict(FROZEN_FIXTURE),
            "B": 4,
            "family": "least_x_interval",
            "null_replicate": None,
            "node_cap_per_cap": node_cap,
            "representative_compiler": REPRESENTATIVE_COMPILER,
        }
        if (
            document["canonical"] is not False
            or document["interpretation"]
            != "frozen-fixture implementation evidence only"
            or document["parameters"] != expected_parameters
            or len(rows) != 1
        ):
            errors.append("frozen document envelope mismatch")
        elif not (
            rows[0].get("curve", {}).get("draw") is None
            and rows[0].get("B") == 4
            and rows[0].get("family") == "least_x_interval"
            and rows[0].get("null_replicate") is None
            and all(
                cap.get("optimizer", {}).get("node_cap") == node_cap
                for cap in rows[0].get("private_audit", {}).get("density_frontier", [])
            )
        ):
            errors.append("frozen row association mismatch")
        expected_gate = {
            "status": "NOT_APPLICABLE",
            "reason": "frozen fixture is not a family matrix",
        }
    elif scope == "canonical":
        if (
            document["canonical"] is not True
            or document["interpretation"]
            != "canonical candidate; coordinator interpretation still required"
            or document["parameters"] != expected_canonical_parameters()
        ):
            errors.append("canonical document envelope mismatch")
        observed_keys = [
            (
                row.get("curve", {}).get("bits"),
                row.get("curve", {}).get("seed"),
                row.get("B"),
                row.get("family"),
                row.get("null_replicate"),
            )
            for row in rows
        ]
        if observed_keys != expected_row_keys():
            errors.append("canonical row grid/order mismatch")
        curve_by_seed: dict[tuple[int, int], tuple[int, int, int, int]] = {}
        for row in rows:
            curve_info = row.get("curve", {})
            key = (curve_info.get("bits"), curve_info.get("seed"))
            value = tuple(curve_info.get(name) for name in ("p", "a", "b", "q"))
            if key in curve_by_seed and curve_by_seed[key] != value:
                errors.append(f"inconsistent curve record for {key!r}")
            curve_by_seed[key] = value
        if len(set(curve_by_seed.values())) != len(curve_by_seed):
            errors.append("cross-seed duplicate accepted curve")
        if any(
            cap.get("optimizer", {}).get("node_cap") != CANONICAL_NODE_CAP
            for row in rows
            for cap in row.get("private_audit", {}).get("density_frontier", [])
        ):
            errors.append("canonical node-cap mismatch")
        try:
            expected_gate = independent_family_gate(rows)
        except Exception as error:
            errors.append(f"family gate reconstruction: {error}")
            expected_gate = None
    else:
        errors.append("unknown document scope")
        expected_gate = None

    row_reports = [verify_density_row(row, maximum_nodes) for row in rows]
    if any(not report["valid"] for report in row_reports):
        errors.append("one or more V3 row verifications failed")
    if document["summary"] != independent_document_summary(rows):
        errors.append("document summary mismatch")
    if expected_gate is not None and document["family_gate"] != expected_gate:
        errors.append("family gate mismatch")
    return errors, row_reports


def verify_document(path: Path, maximum_nodes: int) -> dict[str, Any]:
    document = strict_load(path)
    supplied = document.get("document_sha256")
    if document.get("schema") == "sgcp-embed-002-density-frontier-candidate-v3":
        errors, row_reports = verify_v3_document_value(document, maximum_nodes)
        claim_boundary = (
            "frozen-fixture implementation verification only"
            if document.get("scope") == "frozen_fixture"
            else "canonical matrix verification; coordinator interpretation still required"
        )
    else:
        errors = []
        if document.get("schema") not in EXPECTED_SCHEMAS:
            errors.append("unexpected document schema")
        if document.get("canonical") is not False:
            errors.append("development document claims canonical status")
        payload = dict(document)
        payload.pop("document_sha256", None)
        if supplied != digest(payload):
            errors.append("document digest mismatch")
        row_reports = [
            verify_row(row, maximum_nodes) for row in document.get("rows", [])
        ]
        if any(not report["valid"] for report in row_reports):
            errors.append("one or more row verifications failed")
        claim_boundary = "legacy development verification only"
    report = {
        "schema": VERIFICATION_SCHEMA,
        "verifier_source_path": str(SCRIPT_PATH),
        "verifier_source_sha256": file_digest(SCRIPT_PATH),
        "input_path": str(path.resolve()),
        "input_file_sha256": file_digest(path),
        "input_document_sha256": supplied,
        "valid": not errors,
        "errors": errors,
        "row_count": len(row_reports),
        "valid_row_count": sum(bool(row["valid"]) for row in row_reports),
        "total_primary_nodes": sum(row["primary_nodes"] for row in row_reports),
        "rows": row_reports,
        "independent_checks": [
            "strict JSON and document/row digests",
            "closed V3 row/document schemas and forbidden scalar-material keys",
            "independent curve draw and rejection transcript derivation",
            "predicate roots, hash-derived Mobius maps, poles, hash-null ranking, signs, and root polynomial",
            "complete canonical row grid, cross-seed curve uniqueness, and exact four-null gate",
            "frozen degree-two representative compiler and public source table",
            "balanced candidate universe, individual eligibility, and pair-conflict graph",
            "selected graph independence, formal closure, public edges, axioms, density, and retention",
            "degree-1/2/4/8 support under formal-multiset and ordered-tuple source measures",
            "deterministic optimizer replay plus independent exhaustive primary proof",
            "reconstructed structural-work and nested serialized-byte receipts",
        ],
        "claim_boundary": claim_boundary,
    }
    report["verification_sha256"] = digest(report)
    return report


def output_path(path: Path) -> Path:
    resolved = path.resolve()
    if DEVELOPMENT_ROOT.resolve() not in resolved.parents:
        raise ValueError("verification output must be below the development directory")
    if resolved.exists():
        raise FileExistsError(resolved)
    return resolved


def write_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as handle:
        handle.write(stable_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-primary-nodes", type=int, default=5000000)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = verify_document(args.input.resolve(strict=True), args.maximum_primary_nodes)
    write_atomic(output_path(args.output), report)
    print(
        json.dumps(
            {
                "valid": report["valid"],
                "row_count": report["row_count"],
                "valid_row_count": report["valid_row_count"],
                "total_primary_nodes": report["total_primary_nodes"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

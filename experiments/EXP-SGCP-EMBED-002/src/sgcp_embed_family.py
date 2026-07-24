#!/usr/bin/env python3
"""Development builder for EXP-SGCP-EMBED-002.

The builder uses affine coordinates and EC addition only. It deliberately has
no scalar-multiplication routine and constructs no discrete-log table.
Canonical execution remains disabled by the version-18 experiment contract.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence


SCHEMA = "sgcp-embed-002-density-frontier-candidate-v18"
EXPERIMENT_ID = "EXP-SGCP-EMBED-002"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "MODEL-BOUND", "NOVELTY-UNVERIFIED"]
PROTOCOL_VERSION = 18
REPRESENTATIVE_COMPILER = (
    "lexicographically_least_formal_per_nonidentity_2F_output_v2"
)
ORDERING_CONTRACT = {
    "factor_points": "ascending affine (x,y), coordinates reduced to 0..p-1",
    "formal_indices": "zero-based positions in factor_points; formal tuples nondecreasing",
    "formal_order": "shorter degree first where mixed, then integer-tuple lexicographic order",
    "point_order": "identity first, then ascending affine (x,y)",
    "point_labels": "identity is O; affine is canonical unsigned decimal x:y",
    "least_x_tie": "ascending integer x",
    "mobius_tie": "ascending (score,x); poles excluded from that map ranking",
    "two_mobius_tie": "alternate map 0 then 1, skip selected duplicates, preserve per-map order",
    "hash_x_tie": "ascending (64-character lowercase SHA-256 hex digest,x)",
    "representative_tie": "lexicographically least nondecreasing formal tuple per EC output",
}
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
FROZEN_NODE_CAP = 100_000
FROZEN_FIXTURE = {
    "bits": 5,
    "p": 19,
    "a": 2,
    "b": 9,
    "q": 23,
    "trace": -3,
    "generator": [0, 3],
}

Point = tuple[int, int] | None
Formal = tuple[int, ...]
FROZEN_POINTS: tuple[Point, ...] = (
    None,
    (0, 3),
    (0, 16),
    (3, 2),
    (3, 17),
    (4, 9),
    (4, 10),
    (5, 7),
    (5, 12),
    (6, 3),
    (6, 16),
    (7, 9),
    (7, 10),
    (8, 9),
    (8, 10),
    (13, 3),
    (13, 16),
    (14, 8),
    (14, 11),
    (17, 4),
    (17, 15),
    (18, 5),
    (18, 14),
)


@dataclass
class OperationCounts:
    point_additions: int = 0
    point_doublings: int = 0
    field_inversions: int = 0
    field_multiplications: int = 0
    multiset_evaluations: int = 0
    injectivity_checks: int = 0
    conflict_pair_checks: int = 0
    hash_calls: int = 0
    optimizer_nodes: int = 0
    optimizer_bound_calls: int = 0


class Curve:
    def __init__(
        self, p: int, a: int, b: int, ops: OperationCounts | None = None
    ) -> None:
        if type(p) is not int or p <= 3 or not is_prime(p):
            raise ValueError("p must be a prime greater than three")
        self.p = p
        self.a = require_int(a, "a") % p
        self.b = require_int(b, "b") % p
        self.ops = ops
        if self.discriminant() == 0:
            raise ValueError("singular curve")

    def discriminant(self) -> int:
        return (4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)) % self.p

    def j_invariant(self) -> int:
        numerator = 1728 * 4 * pow(self.a, 3, self.p)
        return numerator * pow(self.discriminant(), -1, self.p) % self.p

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if self.ops is not None:
            self.ops.point_additions += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if self.ops is not None:
                self.ops.point_doublings += 1
                self.ops.field_inversions += 1
                self.ops.field_multiplications += 4
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            if self.ops is not None:
                self.ops.field_inversions += 1
                self.ops.field_multiplications += 3
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.on_curve(result):
            raise AssertionError("affine addition left the curve")
        return result


def require_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def is_prime(value: int) -> bool:
    if type(value) is not int or value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    for divisor in range(3, math.isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


def stable_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json(value)).hexdigest()


def frozen_curve_record_contract() -> dict[str, Any]:
    return {
        "bits": FROZEN_FIXTURE["bits"],
        "seed": 5,
        "p": FROZEN_FIXTURE["p"],
        "a": FROZEN_FIXTURE["a"],
        "b": FROZEN_FIXTURE["b"],
        "q": FROZEN_FIXTURE["q"],
        "trace": FROZEN_FIXTURE["trace"],
        "j": 8,
        "generator": FROZEN_FIXTURE["generator"],
        "draw": None,
        "rejected_draws": [],
        "rejection_count": 0,
        "rejection_digest": stable_digest([]),
    }


def exact_json_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            exact_json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            exact_json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def point_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def point_json(point: Point) -> str | list[int]:
    return "O" if point is None else [point[0], point[1]]


def point_label(point: Point) -> str:
    return "O" if point is None else f"{point[0]}:{point[1]}"


def iter_mask(mask: int) -> Iterator[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def deep_size(value: Any) -> int:
    seen: set[int] = set()

    def visit(item: Any) -> int:
        identity = id(item)
        if identity in seen:
            return 0
        seen.add(identity)
        total = sys.getsizeof(item)
        if isinstance(item, dict):
            total += sum(visit(key) + visit(child) for key, child in item.items())
        elif isinstance(item, (list, tuple, set, frozenset)):
            total += sum(visit(child) for child in item)
        return total

    return visit(value)


def exact_ratio(numerator: int, denominator: int) -> dict[str, int]:
    require_int(numerator, "ratio numerator", 0)
    require_int(denominator, "ratio denominator", 1)
    divisor = math.gcd(numerator, denominator)
    return {"numerator": numerator // divisor, "denominator": denominator // divisor}


def hash_int(
    domain: str, fields: Sequence[Any], modulus: int, ops: OperationCounts | None = None
) -> int:
    if modulus <= 0:
        raise ValueError("hash modulus must be positive")
    if ops is not None:
        ops.hash_calls += 1
    payload = {"domain": domain, "fields": list(fields)}
    return int.from_bytes(hashlib.sha256(stable_json(payload)).digest(), "big") % modulus


def enumerate_points(curve: Curve) -> list[Point]:
    by_square: dict[int, list[int]] = defaultdict(list)
    for y in range(curve.p):
        by_square[y * y % curve.p].append(y)
    points: list[Point] = [None]
    for x in range(curve.p):
        rhs = (x * x * x + curve.a * x + curve.b) % curve.p
        points.extend((x, y) for y in by_square.get(rhs, []))
    return sorted(points, key=point_key)


def curve_record(curve: Curve, points: Sequence[Point], bits: int, seed: int) -> dict[str, Any]:
    q = len(points)
    generator = next(point for point in points if point is not None)
    return {
        "bits": bits,
        "seed": seed,
        "p": curve.p,
        "a": curve.a,
        "b": curve.b,
        "q": q,
        "trace": curve.p + 1 - q,
        "j": curve.j_invariant(),
        "generator": point_json(generator),
    }


def curve_rejection_reasons(
    p: int, a: int, b: int, bits: int
) -> tuple[list[str], int | None]:
    discriminant = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if discriminant == 0:
        return ["singular"], None
    curve = Curve(p, a, b)
    q = len(enumerate_points(curve))
    trace = p + 1 - q
    reasons: list[str] = []
    if q.bit_length() != bits:
        reasons.append("wrong_q_bit_length")
    if not is_prime(q):
        reasons.append("nonprime_group_order")
    if trace == 0:
        reasons.append("trace_zero")
    if trace == 1:
        reasons.append("anomalous_trace_one")
    if curve.j_invariant() == 0:
        reasons.append("j_zero")
    if curve.j_invariant() == 1728 % p:
        reasons.append("j_1728")
    return reasons, q


def ordered_curve_rejection_reasons(
    p: int, a: int, b: int, bits: int, duplicate: bool
) -> tuple[list[str], int | None]:
    reasons, q = curve_rejection_reasons(p, a, b, bits)
    return (["duplicate_candidate"] if duplicate else []) + reasons, q


def _generated_curve_for_controls(
    bits: int, seed: int, ops: OperationCounts | None = None
) -> tuple[Curve, list[Point], dict[str, Any]]:
    bits = require_int(bits, "bits", 5)
    seed = require_int(seed, "seed", 0)
    primes = [
        value
        for value in range(1 << (bits - 1), 1 << bits)
        if value > 3 and is_prime(value)
    ]
    if not primes:
        raise AssertionError(f"no prime field candidates for {bits} bits")
    seen: set[tuple[int, int, int]] = set()
    rejections: list[dict[str, Any]] = []
    for draw in range(100000):
        p = primes[hash_int("sgcp-002-curve-p", [bits, seed, draw], len(primes), ops)]
        a = hash_int("sgcp-002-curve-a", [bits, seed, draw, p], p, ops)
        b = hash_int("sgcp-002-curve-b", [bits, seed, draw, p], p, ops)
        key = (p, a, b)
        duplicate = key in seen
        if not duplicate:
            seen.add(key)
        reasons, rejection_q = ordered_curve_rejection_reasons(
            p, a, b, bits, duplicate
        )
        if rejection_q is None:
            rejections.append(
                {"draw": draw, "p": p, "a": a, "b": b, "reasons": reasons}
            )
            continue
        curve = Curve(p, a, b, ops)
        points = enumerate_points(curve)
        q = len(points)
        if rejection_q != q:
            raise AssertionError("curve rejection recount mismatch")
        if reasons:
            rejections.append(
                {
                    "draw": draw,
                    "p": p,
                    "a": a,
                    "b": b,
                    "q": q,
                    "reasons": reasons,
                }
            )
            continue
        record = curve_record(curve, points, bits, seed)
        record["draw"] = draw
        record["rejected_draws"] = rejections
        record["rejection_count"] = len(rejections)
        record["rejection_digest"] = stable_digest(rejections)
        return curve, points, record
    raise RuntimeError(f"no accepted curve after 100000 draws for bits={bits}, seed={seed}")


def generated_curve(
    bits: int, seed: int, ops: OperationCounts | None = None
) -> tuple[Curve, list[Point], dict[str, Any]]:
    raise PermissionError(
        "version-18 public generated-curve construction is disabled; "
        "private factor-base controls do not authorize density rows"
    )


def frozen_curve(
    ops: OperationCounts | None = None,
) -> tuple[Curve, list[Point], dict[str, Any]]:
    curve = Curve(FROZEN_FIXTURE["p"], FROZEN_FIXTURE["a"], FROZEN_FIXTURE["b"], ops)
    points = enumerate_points(curve)
    record = curve_record(curve, points, FROZEN_FIXTURE["bits"], 5)
    record["draw"] = None
    record["rejected_draws"] = []
    record["rejection_count"] = 0
    record["rejection_digest"] = stable_digest([])
    if tuple(points) != FROZEN_POINTS or not exact_json_equal(
        record, frozen_curve_record_contract()
    ):
        raise AssertionError("frozen curve recount mismatch")
    return curve, points, record


def admissible_fibers(curve: Curve, points: Sequence[Point]) -> dict[int, tuple[Point, Point]]:
    by_x: dict[int, list[Point]] = defaultdict(list)
    for point in points:
        if point is not None:
            by_x[point[0]].append(point)
    result: dict[int, tuple[Point, Point]] = {}
    for x, fiber in by_x.items():
        ordered = tuple(sorted(fiber, key=point_key))
        if len(ordered) != 2:
            continue
        if ordered[0] is None or ordered[1] is None:
            raise AssertionError("affine fiber contains identity")
        if curve.neg(ordered[0]) != ordered[1]:
            raise AssertionError("two-point fiber is not negation symmetric")
        result[x] = (ordered[0], ordered[1])
    return result


def polynomial_from_roots(roots: Sequence[int], modulus: int) -> list[int]:
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] = (updated[degree] - root * coefficient) % modulus
            updated[degree + 1] = (updated[degree + 1] + coefficient) % modulus
        coefficients = updated
    return coefficients


def derive_mobius(
    curve_info: dict[str, Any], B: int, tag: str, map_index: int, ops: OperationCounts
) -> dict[str, int]:
    p = curve_info["p"]
    curve_token = [curve_info[key] for key in ("p", "a", "b", "q", "seed")]
    for nonce in range(1024):
        u = hash_int("sgcp-002-mobius-u", [curve_token, B, tag, map_index, nonce], p, ops)
        v = hash_int("sgcp-002-mobius-v", [curve_token, B, tag, map_index, nonce], p, ops)
        w = hash_int("sgcp-002-mobius-w", [curve_token, B, tag, map_index, nonce], p, ops)
        determinant = (u * w - v) % p
        if determinant != 0:
            return {"u": u, "v": v, "w": w, "determinant": determinant, "nonce": nonce}
    raise AssertionError("could not derive a nondegenerate Mobius map")


def mobius_ranking(roots: Sequence[int], p: int, params: dict[str, int]) -> tuple[list[int], list[int]]:
    scored: list[tuple[int, int]] = []
    poles: list[int] = []
    for x in roots:
        denominator = (x + params["w"]) % p
        if denominator == 0:
            poles.append(x)
            continue
        score = (params["u"] * x + params["v"]) * pow(denominator, -1, p) % p
        scored.append((score, x))
    return [x for _, x in sorted(scored)], sorted(poles)


def factor_base(
    curve: Curve,
    points: Sequence[Point],
    curve_info: dict[str, Any],
    B: int,
    family: str,
    null_replicate: int | None,
    ops: OperationCounts,
) -> tuple[list[Point], dict[str, Any]]:
    B = require_int(B, "B", 4)
    if B % 2:
        raise ValueError("B must be even")
    fibers = admissible_fibers(curve, points)
    roots = sorted(fibers)
    required = B // 2
    if len(roots) < required:
        raise ValueError(f"only {len(roots)} admissible roots for B={B}")
    if family in COORDINATE_FAMILIES and null_replicate is not None:
        raise ValueError("coordinate families require null_replicate=None")
    if family == NULL_FAMILY and (
        type(null_replicate) is not int
        or not 0 <= null_replicate < CANONICAL_NULL_REPLICATES
    ):
        raise ValueError("hash_x_null replicate is outside the frozen range")
    parameters: dict[str, Any] = {}
    excluded_poles: list[int] = []
    if family == "least_x_interval":
        selected = roots[:required]
    elif family == "mobius_interval":
        params = derive_mobius(curve_info, B, family, 0, ops)
        ranking, poles = mobius_ranking(roots, curve.p, params)
        if len(ranking) < required:
            raise AssertionError("Mobius pole handling left too few roots")
        selected = ranking[:required]
        parameters = {"map": params}
        excluded_poles = poles
    elif family == "two_mobius_union":
        maps = [derive_mobius(curve_info, B, family, index, ops) for index in range(2)]
        rankings: list[list[int]] = []
        poles: set[int] = set()
        for params in maps:
            ranking, map_poles = mobius_ranking(roots, curve.p, params)
            rankings.append(ranking)
            poles.update(map_poles)
        selected = []
        positions = [0, 0]
        while len(selected) < required:
            progressed = False
            for index in range(2):
                while positions[index] < len(rankings[index]):
                    candidate = rankings[index][positions[index]]
                    positions[index] += 1
                    if candidate not in selected:
                        selected.append(candidate)
                        progressed = True
                        break
                if len(selected) == required:
                    break
            if not progressed:
                raise AssertionError("two-map union could not fill the factor base")
        parameters = {"maps": maps, "alternating_positions": positions}
        excluded_poles = sorted(poles)
    elif family == "hash_x_null":
        if null_replicate is None or null_replicate < 0:
            raise ValueError("hash_x_null requires a nonnegative replicate")
        curve_token = [curve_info[key] for key in ("p", "a", "b", "q", "seed")]
        ranked = []
        for x in roots:
            ops.hash_calls += 1
            digest = hashlib.sha256(
                stable_json(
                    {
                        "domain": "sgcp-002-hash-x-null",
                        "curve": curve_token,
                        "B": B,
                        "replicate": null_replicate,
                        "x": x,
                    }
                )
            ).hexdigest()
            ranked.append((digest, x))
        selected = [x for _, x in sorted(ranked)[:required]]
        parameters = {"replicate": null_replicate}
    else:
        raise ValueError(f"unknown factor-base family {family!r}")

    if len(selected) != required or len(set(selected)) != required:
        raise AssertionError("factor-base root cardinality mismatch")
    factor_points = sorted(
        (point for root in selected for point in fibers[root]), key=point_key
    )
    if len(factor_points) != B:
        raise AssertionError("factor-base point cardinality mismatch")
    for point in factor_points:
        if point is None or curve.neg(point) not in factor_points:
            raise AssertionError("factor base is not negation symmetric")
    selected_sorted = sorted(selected)
    record = {
        "family": family,
        "null_replicate": null_replicate,
        "B": B,
        "admissible_root_count": len(roots),
        "selected_roots": selected_sorted,
        "selected_root_count": len(selected_sorted),
        "excluded_poles": excluded_poles,
        "parameters": parameters,
        "root_polynomial_coefficients_ascending_mod_p": polynomial_from_roots(
            selected_sorted, curve.p
        ),
        "points": [point_json(point) for point in factor_points],
        "negation_symmetric": True,
    }
    record["selection_sha256"] = stable_digest(record)
    return factor_points, record


def evaluate_formal(curve: Curve, factors: Sequence[Point], formal: Formal) -> Point:
    if curve.ops is not None:
        curve.ops.multiset_evaluations += 1
    result: Point = None
    for index in formal:
        result = curve.add(result, factors[index])
    return result


def submultisets(formal: Formal) -> set[Formal]:
    result: set[Formal] = {()}
    for degree in range(1, len(formal) + 1):
        result.update(itertools.combinations(formal, degree))
    return result


def order_ideal(B: int, maxima: Iterable[Formal]) -> set[Formal]:
    family: set[Formal] = {(), *((index,) for index in range(B))}
    for maximum in maxima:
        family.update(submultisets(tuple(sorted(maximum))))
    return family


def evaluate_family(
    curve: Curve, factors: Sequence[Point], family: Iterable[Formal]
) -> tuple[dict[Formal, Point], list[tuple[Formal, Formal, Point]]]:
    if curve.ops is not None:
        curve.ops.injectivity_checks += 1
    evaluations: dict[Formal, Point] = {}
    first_by_point: dict[Point, Formal] = {}
    collisions: list[tuple[Formal, Formal, Point]] = []
    for formal in sorted(set(family), key=lambda item: (len(item), item)):
        point = evaluate_formal(curve, factors, formal)
        evaluations[formal] = point
        previous = first_by_point.get(point)
        if previous is not None:
            collisions.append((previous, formal, point))
        else:
            first_by_point[point] = formal
    return evaluations, collisions


def balanced_universe(curve: Curve, factors: Sequence[Point]) -> dict[str, Any]:
    degree2 = list(itertools.combinations_with_replacement(range(len(factors)), 2))
    degree2_by_point: dict[Point, list[Formal]] = defaultdict(list)
    for formal in degree2:
        degree2_by_point[evaluate_formal(curve, factors, formal)].append(formal)
    canonical2: list[dict[str, Any]] = []
    for point in sorted(degree2_by_point, key=point_key):
        if point is None:
            continue
        witnesses = sorted(degree2_by_point[point])
        canonical2.append({"point": point, "formal": witnesses[0]})

    raw4: list[dict[str, Any]] = []
    for left_index, right_index in itertools.combinations_with_replacement(
        range(len(canonical2)), 2
    ):
        left = canonical2[left_index]
        right = canonical2[right_index]
        formal = tuple(sorted(left["formal"] + right["formal"]))
        raw4.append(
            {
                "point": curve.add(left["point"], right["point"]),
                "formal": formal,
                "parents": tuple(sorted((left["formal"], right["formal"]))),
            }
        )

    by_formal: dict[Formal, list[dict[str, Any]]] = defaultdict(list)
    for witness in raw4:
        by_formal[witness["formal"]].append(witness)
    candidates: list[dict[str, Any]] = []
    for formal in sorted(by_formal):
        witnesses = sorted(by_formal[formal], key=lambda item: item["parents"])
        points = {item["point"] for item in witnesses}
        if len(points) != 1:
            raise AssertionError("formal degree-four evaluation is inconsistent")
        candidates.append(
            {
                "formal": formal,
                "point": witnesses[0]["point"],
                "parent_pairs": [item["parents"] for item in witnesses],
            }
        )
    raw_a4 = sorted({item["point"] for item in raw4}, key=point_key)
    representative_records = [
        {"point": point_json(item["point"]), "formal": list(item["formal"])}
        for item in canonical2
    ]
    return {
        "representative_compiler": {
            "id": REPRESENTATIVE_COMPILER,
            "identity_output_excluded": True,
            "representative_count": len(representative_records),
            "representatives": representative_records,
            "representatives_sha256": stable_digest(representative_records),
        },
        "degree2_count": len(degree2),
        "canonical2_count": len(canonical2),
        "raw4_count": len(raw4),
        "candidates": candidates,
        "raw_a4": raw_a4,
    }


def collision_json(collision: tuple[Formal, Formal, Point]) -> dict[str, Any]:
    left, right, point = collision
    return {"left": list(left), "right": list(right), "point": point_json(point)}


def candidate_graph(
    curve: Curve, factors: Sequence[Point], candidates: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    universe_indices: list[int] = []
    closure_maps: list[dict[Point, Formal]] = []
    for universe_index, candidate in enumerate(candidates):
        family = order_ideal(len(factors), [candidate["formal"]])
        evaluations, collisions = evaluate_family(curve, factors, family)
        if collisions:
            rejected.append(
                {
                    "universe_index": universe_index,
                    "formal": list(candidate["formal"]),
                    "point": point_json(candidate["point"]),
                    "first_collision": collision_json(collisions[0]),
                }
            )
            continue
        eligible.append(candidate)
        universe_indices.append(universe_index)
        closure_maps.append({point: formal for formal, point in evaluations.items()})

    conflict_masks = [0] * len(eligible)
    conflicts: list[dict[str, Any]] = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            if curve.ops is not None:
                curve.ops.conflict_pair_checks += 1
            common = sorted(
                set(closure_maps[left]).intersection(closure_maps[right]), key=point_key
            )
            first: tuple[Formal, Formal, Point] | None = None
            for point in common:
                left_formal = closure_maps[left][point]
                right_formal = closure_maps[right][point]
                if left_formal != right_formal:
                    first = (left_formal, right_formal, point)
                    break
            if first is None:
                continue
            conflict_masks[left] |= 1 << right
            conflict_masks[right] |= 1 << left
            conflicts.append(
                {
                    "left": left,
                    "right": right,
                    "left_universe_index": universe_indices[left],
                    "right_universe_index": universe_indices[right],
                    "first_collision": collision_json(first),
                }
            )
    return {
        "eligible": eligible,
        "eligible_universe_indices": universe_indices,
        "rejected": rejected,
        "conflict_masks": conflict_masks,
        "conflicts": conflicts,
    }


def graph_metrics(conflict_masks: Sequence[int]) -> dict[str, Any]:
    count = len(conflict_masks)
    degrees = [(mask & ((1 << count) - 1)).bit_count() for mask in conflict_masks]
    unseen = set(range(count))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        component: list[int] = []
        while stack:
            vertex = stack.pop()
            component.append(vertex)
            neighbors = set(iter_mask(conflict_masks[vertex])) & unseen
            unseen.difference_update(neighbors)
            stack.extend(sorted(neighbors, reverse=True))
        components.append(sorted(component))

    remaining = set(range(count))
    degeneracy = 0
    while remaining:
        vertex = min(
            remaining,
            key=lambda item: (
                sum(1 for neighbor in iter_mask(conflict_masks[item]) if neighbor in remaining),
                item,
            ),
        )
        degree = sum(1 for neighbor in iter_mask(conflict_masks[vertex]) if neighbor in remaining)
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


def pair_output_table(curve: Curve, points: Sequence[Point]) -> tuple[list[list[int]], int]:
    group_points = enumerate_points(curve)
    point_index = {point: index for index, point in enumerate(group_points)}
    table = [[0] * len(points) for _ in points]
    for left in range(len(points)):
        for right in range(left, len(points)):
            output = curve.add(points[left], points[right])
            index = point_index[output]
            table[left][right] = index
            table[right][left] = index
    return table, len(group_points)


def support_mask_for_selection(selected_mask: int, pair_outputs: Sequence[Sequence[int]]) -> int:
    selected = list(iter_mask(selected_mask))
    support = 0
    for position, left in enumerate(selected):
        for right in selected[position:]:
            support |= 1 << pair_outputs[left][right]
    return support


def clique_cover_upper(allowed: int, conflicts: Sequence[int]) -> int:
    vertices = sorted(
        iter_mask(allowed),
        key=lambda vertex: (-(conflicts[vertex] & allowed).bit_count(), vertex),
    )
    cliques: list[int] = []
    for vertex in vertices:
        bit = 1 << vertex
        for index, clique in enumerate(cliques):
            if conflicts[vertex] & clique == clique:
                cliques[index] |= bit
                break
        else:
            cliques.append(bit)
    return len(cliques)


def optimize_coverage_graph(
    pair_outputs: Sequence[Sequence[int]],
    point_count: int,
    conflicts: Sequence[int],
    node_cap: int,
    tiebreak: Callable[[int], dict[str, Any]] | None = None,
    *,
    max_constrained: int | None = None,
    objective_mode: str = "legacy",
) -> dict[str, Any]:
    candidate_count = len(conflicts)
    if any(len(row) != candidate_count for row in pair_outputs):
        raise ValueError("pair-output table is not square")
    if objective_mode not in {"legacy", "density"}:
        raise ValueError(f"unknown objective mode {objective_mode!r}")
    if objective_mode == "density" and max_constrained is None:
        raise ValueError("density objective requires max_constrained")
    if max_constrained is not None:
        max_constrained = require_int(max_constrained, "constrained cap", 1)
    node_cap = require_int(node_cap, "node cap", 0)
    tiebreak = tiebreak or (
        lambda mask: {
            "constrained_count": 0,
            "public_edge_count": 0,
            "witness_list": list(iter_mask(mask)),
        }
    )
    metric_cache: dict[int, dict[str, Any]] = {}
    metric_cache_limit = node_cap + candidate_count**2 + 64

    def metrics(mask: int) -> dict[str, Any]:
        if mask not in metric_cache:
            if len(metric_cache) >= metric_cache_limit:
                raise RuntimeError("optimizer metric-cache ceiling exceeded")
            metric_cache[mask] = tiebreak(mask)
        return metric_cache[mask]

    def feasible(mask: int) -> bool:
        return max_constrained is None or metrics(mask)["constrained_count"] <= max_constrained

    global_output_masks = [0] * candidate_count
    for left in range(candidate_count):
        for right in range(candidate_count):
            global_output_masks[left] |= 1 << pair_outputs[left][right]

    best_mask = 0
    best_support_mask = 0
    best_metrics = metrics(0)
    if not feasible(0):
        raise ValueError("constrained cap does not admit the empty operation")
    incumbent_updates = 0

    def objective(mask: int, support: int, metrics: dict[str, Any]) -> tuple[int, int, int, int]:
        constrained = require_int(metrics["constrained_count"], "constrained count", 0)
        edges = require_int(metrics["public_edge_count"], "public edge count", 0)
        if objective_mode == "legacy":
            return support.bit_count(), mask.bit_count(), -constrained, -edges
        return support.bit_count(), -constrained, -edges, mask.bit_count()

    def is_better(mask: int, support: int, metrics: dict[str, Any]) -> bool:
        candidate_key = objective(mask, support, metrics)
        best_key = objective(best_mask, best_support_mask, best_metrics)
        if candidate_key != best_key:
            return candidate_key > best_key
        return tuple(metrics["witness_list"]) < tuple(best_metrics["witness_list"])

    def update(mask: int, support: int) -> None:
        nonlocal best_mask, best_support_mask, best_metrics, incumbent_updates
        candidate_metrics = metrics(mask)
        if max_constrained is not None and candidate_metrics["constrained_count"] > max_constrained:
            return
        if is_better(mask, support, candidate_metrics):
            best_mask = mask
            best_support_mask = support
            best_metrics = candidate_metrics
            incumbent_updates += 1

    def add_vertex(mask: int, support: int, vertex: int) -> tuple[int, int]:
        for selected in iter_mask(mask):
            support |= 1 << pair_outputs[selected][vertex]
        support |= 1 << pair_outputs[vertex][vertex]
        return mask | (1 << vertex), support

    def force_isolates(mask: int, allowed: int, support: int) -> tuple[int, int, int]:
        if objective_mode != "legacy" or max_constrained is not None:
            return mask, allowed, support
        while True:
            isolates = [
                vertex
                for vertex in iter_mask(allowed)
                if conflicts[vertex] & allowed == 0
            ]
            if not isolates:
                return mask, allowed, support
            for vertex in isolates:
                if not (allowed & (1 << vertex)):
                    continue
                mask, support = add_vertex(mask, support, vertex)
                allowed &= ~(1 << vertex)

    def greedy(order: Sequence[int]) -> None:
        mask = 0
        support = 0
        blocked = 0
        for vertex in order:
            bit = 1 << vertex
            if blocked & bit:
                continue
            candidate_mask, candidate_support = add_vertex(mask, support, vertex)
            if not feasible(candidate_mask):
                continue
            mask, support = candidate_mask, candidate_support
            blocked |= conflicts[vertex] | bit
        update(mask, support)

    natural = list(range(candidate_count))
    greedy(natural)
    greedy(list(reversed(natural)))
    greedy(sorted(natural, key=lambda vertex: ((conflicts[vertex]).bit_count(), vertex)))
    greedy(sorted(natural, key=lambda vertex: (-(conflicts[vertex]).bit_count(), vertex)))

    mask = 0
    support = 0
    allowed = (1 << candidate_count) - 1
    while allowed:
        choices = []
        for vertex in iter_mask(allowed):
            candidate_mask, candidate_support = add_vertex(mask, support, vertex)
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
        mask, support = add_vertex(mask, support, vertex)
        allowed &= ~(conflicts[vertex] | (1 << vertex))
    update(mask, support)

    bound_calls = 0

    def bounds(mask: int, allowed: int, support: int) -> tuple[int, int]:
        nonlocal bound_calls
        bound_calls += 1
        alpha = clique_cover_upper(allowed, conflicts)
        selected_count = mask.bit_count()
        pair_capacity = selected_count * alpha + alpha * (alpha + 1) // 2
        cardinality_upper = min(point_count, support.bit_count() + pair_capacity)
        output_upper_mask = support
        for vertex in iter_mask(allowed):
            output_upper_mask |= global_output_masks[vertex]
        return min(cardinality_upper, output_upper_mask.bit_count()), selected_count + alpha

    frontier: list[tuple[int, int, int, int, int, int]] = []
    sequence = 0

    def can_improve(upper_support: int, upper_count: int, mask: int) -> bool:
        best_support = best_support_mask.bit_count()
        if upper_support < best_support:
            return False
        if upper_support > best_support:
            return True
        current = metrics(mask)
        if objective_mode == "legacy":
            return upper_count >= best_mask.bit_count()
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

    def push(mask: int, allowed: int, support: int) -> None:
        nonlocal sequence
        mask, allowed, support = force_isolates(mask, allowed, support)
        if not feasible(mask):
            return
        if allowed == 0:
            update(mask, support)
            return
        upper_support, upper_count = bounds(mask, allowed, support)
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
        neg_upper_support, neg_upper_count, _, mask, allowed, support = heapq.heappop(frontier)
        upper_support = -neg_upper_support
        upper_count = -neg_upper_count
        if not can_improve(upper_support, upper_count, mask):
            continue
        explored += 1
        vertices = list(iter_mask(allowed))
        vertex = max(
            vertices,
            key=lambda item: (
                (conflicts[item] & allowed).bit_count(),
                sum(
                    1
                    for selected in iter_mask(mask)
                    if not (support & (1 << pair_outputs[selected][item]))
                ),
                -item,
            ),
        )
        include_mask, include_support = add_vertex(mask, support, vertex)
        include_allowed = allowed & ~(conflicts[vertex] | (1 << vertex))
        push(include_mask, include_allowed, include_support)
        push(mask, allowed & ~(1 << vertex), support)

    live_frontier: list[tuple[int, int, int, int, int, int]] = []
    for node in frontier:
        upper_support = -node[0]
        upper_count = -node[1]
        if not can_improve(upper_support, upper_count, node[3]):
            continue
        live_frontier.append(node)
    heapq.heapify(live_frontier)
    frontier = live_frontier
    upper_bound = max(
        best_support_mask.bit_count(),
        max((-node[0] for node in frontier), default=0),
    )
    termination = "full_objective_proved" if not frontier else "node_cap"
    frontier_states = [
        {
            "selected_mask_hex": hex(node[3]),
            "available_mask_hex": hex(node[4]),
            "selected_support_mask_hex": hex(node[5]),
            "support_upper_bound": -node[0],
            "selected_count_upper_bound": -node[1],
        }
        for node in sorted(frontier, key=lambda item: (item[3], item[4], item[5], item[0], item[1]))
    ]
    return {
        "objective_mode": objective_mode,
        "max_constrained": max_constrained,
        "objective_order": (
            [
                "retained_support:max",
                "retained_maxima:max",
                "constrained_count:min",
                "public_edges:min",
                "witness_list:lex_min",
            ]
            if objective_mode == "legacy"
            else [
                "retained_support:max",
                "constrained_count:min",
                "public_edges:min",
                "retained_maxima:max",
                "witness_list:lex_min",
            ]
        ),
        "selected_indices": list(iter_mask(best_mask)),
        "selected_mask_hex": hex(best_mask),
        "retained_support_lower_bound": best_support_mask.bit_count(),
        "retained_support_upper_bound": upper_bound,
        "absolute_gap": upper_bound - best_support_mask.bit_count(),
        "primary_exact": upper_bound == best_support_mask.bit_count(),
        "full_objective_exact": not frontier,
        "selected_count": best_mask.bit_count(),
        "constrained_count": best_metrics["constrained_count"],
        "public_edge_count": best_metrics["public_edge_count"],
        "witness_list": best_metrics["witness_list"],
        "explored_nodes": explored,
        "remaining_frontier_nodes": len(frontier),
        "frontier_states": frontier_states,
        "frontier_sha256": stable_digest(frontier_states),
        "incumbent_updates": incumbent_updates,
        "bound_calls": bound_calls,
        "termination_reason": termination,
        "node_cap": node_cap,
        "bound_method": "conflict-clique-cover cardinality plus global pair-output union",
        "metric_cache_entries": len(metric_cache),
    }


def closure_edges(
    family: set[Formal], evaluations: dict[Formal, Point]
) -> list[tuple[Formal, Formal, Formal, Point, Point, Point]]:
    nonempty = sorted((item for item in family if item), key=lambda item: (len(item), item))
    edges: list[tuple[Formal, Formal, Formal, Point, Point, Point]] = []
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union not in family:
                continue
            edges.append(
                (left, right, union, evaluations[left], evaluations[right], evaluations[union])
            )
    return edges


def model_metrics(
    curve: Curve, factors: Sequence[Point], selected: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    maxima = [item["formal"] for item in selected]
    family = order_ideal(len(factors), maxima)
    evaluations, collisions = evaluate_family(curve, factors, family)
    if collisions:
        raise AssertionError(f"selected graph-independent family collided: {collisions[0]!r}")
    edges = closure_edges(family, evaluations)
    compatibility = True
    for _, _, _, left_point, right_point, output_point in edges:
        if curve.add(left_point, right_point) != output_point:
            compatibility = False
            break
    constrained: set[Point] = {None}
    for _, _, _, left_point, right_point, output_point in edges:
        constrained.update((left_point, right_point, output_point))
    forbidden = [edge for edge in edges if len(edge[0]) == 4 and len(edge[1]) == 4]
    downward_closed = all(submultisets(formal).issubset(family) for formal in family)
    witness_list = [list(item["formal"]) for item in sorted(selected, key=lambda item: item["formal"])]
    source_table = [
        {"label": point_label(point), "formal": list(formal)}
        for formal, point in sorted(
            evaluations.items(), key=lambda item: point_key(item[1])
        )
        if point in constrained
    ]
    source_table_valid = (
        len(source_table) == len(constrained)
        and len({entry["label"] for entry in source_table}) == len(constrained)
    )
    public_edges = [
        {
            "left": point_label(left_point),
            "right": point_label(right_point),
            "output": point_label(output_point),
        }
        for _, _, _, left_point, right_point, output_point in edges
    ]
    return {
        "constrained_count": len(constrained),
        "public_edge_count": len(edges),
        "witness_list": witness_list,
        "formal_family_count": len(family),
        "formal_degree_histogram": {
            str(degree): sum(1 for formal in family if len(formal) == degree)
            for degree in sorted({len(formal) for formal in family})
        },
        "axioms": {
            "identity": True,
            "commutativity": True,
            "associativity": downward_closed,
            "associativity_method": "downward-closed formal multiset union",
            "compatibility_coordinates": compatibility,
            "injective_evaluation": not collisions,
            "unique_prime_multiset_factorization": not collisions,
            "acyclic_by_formal_degree": all(
                len(output) > max(len(left), len(right)) for left, right, output, *_ in edges
            ),
            "source_recovery": all(
                tuple(sorted(index for index in formal)) == formal for formal in family
            ),
            "source_recovery_via_public_table": source_table_valid,
            "direct_final_edge_excluded": not forbidden,
            "direct_final_edge_absent_by_construction": not forbidden,
            "forbidden_final_edge_count": len(forbidden),
        },
        "constrained_labels": [point_label(point) for point in sorted(constrained, key=point_key)],
        "public_edges": public_edges,
        "public_edges_sha256": stable_digest(public_edges),
        "source_table": source_table,
        "source_table_sha256": stable_digest(source_table),
    }


def degree_expansion(
    curve: Curve, factors: Sequence[Point], degrees: Sequence[int] = (1, 2, 4, 8)
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for degree in degrees:
        formal_multiplicities: Counter[Point] = Counter()
        ordered_multiplicities: Counter[Point] = Counter()
        for formal in itertools.combinations_with_replacement(range(len(factors)), degree):
            point = evaluate_formal(curve, factors, formal)
            formal_multiplicities[point] += 1
            symbol_counts = Counter(formal)
            orderings = math.factorial(degree)
            for count in symbol_counts.values():
                orderings //= math.factorial(count)
            ordered_multiplicities[point] += orderings
        formal_histogram = Counter(formal_multiplicities.values())
        ordered_histogram = Counter(ordered_multiplicities.values())
        if sum(ordered_multiplicities.values()) != len(factors) ** degree:
            raise AssertionError("multinomial ordered-tuple recount mismatch")
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


def support_from_points(curve: Curve, points: Sequence[Point]) -> tuple[set[Point], Counter[Point]]:
    ordered = sorted(set(points), key=point_key)
    multiplicities: Counter[Point] = Counter()
    for left_index, left in enumerate(ordered):
        for right in ordered[left_index:]:
            multiplicities[curve.add(left, right)] += 1
    return set(multiplicities), multiplicities


def operation_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    if set(before) != set(after):
        raise AssertionError("operation counter keys changed")
    delta = {key: after[key] - before[key] for key in before}
    if any(value < 0 for value in delta.values()):
        raise AssertionError("operation count decreased")
    return delta


def build_legacy_row(
    curve: Curve,
    points: Sequence[Point],
    curve_info: dict[str, Any],
    B: int,
    family: str,
    null_replicate: int | None,
    node_cap: int,
    ops: OperationCounts,
) -> dict[str, Any]:
    raise PermissionError(
        "version-18 public legacy-row construction is disabled; "
        "private controls do not authorize evidence rows"
    )


def _build_frozen_legacy_control_row(B: int) -> dict[str, Any]:
    if type(B) is not int or B not in CANONICAL_FACTOR_BASE_SIZES:
        raise ValueError("frozen legacy control B must be one of 4, 6, or 8")
    ops = OperationCounts()
    curve, points, curve_info = frozen_curve(ops)
    family = "least_x_interval"
    null_replicate = None
    node_cap = FROZEN_NODE_CAP
    started = time.perf_counter()
    before = asdict(ops)
    factors, factor_record = factor_base(
        curve, points, curve_info, B, family, null_replicate, ops
    )
    expansion = degree_expansion(curve, factors)
    universe = balanced_universe(curve, factors)
    graph = candidate_graph(curve, factors, universe["candidates"])
    eligible = graph["eligible"]
    pair_outputs, group_size = pair_output_table(
        curve, [item["point"] for item in eligible]
    )

    model_cache: dict[int, dict[str, Any]] = {}

    def tiebreak(mask: int) -> dict[str, Any]:
        cached = model_cache.get(mask)
        if cached is None:
            selected = [eligible[index] for index in iter_mask(mask)]
            cached = model_metrics(curve, factors, selected)
            model_cache[mask] = cached
        return {
            "constrained_count": cached["constrained_count"],
            "public_edge_count": cached["public_edge_count"],
            "witness_list": cached["witness_list"],
        }

    optimizer = optimize_coverage_graph(
        pair_outputs,
        group_size,
        graph["conflict_masks"],
        node_cap,
        tiebreak,
    )
    ops.optimizer_nodes += optimizer["explored_nodes"]
    ops.optimizer_bound_calls += optimizer["bound_calls"]
    selected = [eligible[index] for index in optimizer["selected_indices"]]
    selected_mask = sum(1 << index for index in optimizer["selected_indices"])
    model = model_cache.get(selected_mask) or model_metrics(curve, factors, selected)
    retained_support_mask = support_mask_for_selection(selected_mask, pair_outputs)
    if retained_support_mask.bit_count() != optimizer["retained_support_lower_bound"]:
        raise AssertionError("optimizer incumbent support recount mismatch")
    raw_support, raw_multiplicities = support_from_points(curve, universe["raw_a4"])
    retained_points = [item["point"] for item in selected]
    retained_support, retained_multiplicities = support_from_points(curve, retained_points)
    if len(retained_support) != optimizer["retained_support_lower_bound"]:
        raise AssertionError("retained final support mismatch")
    boolean_axioms = {
        key: value
        for key, value in model["axioms"].items()
        if key not in {"associativity_method", "forbidden_final_edge_count"}
    }
    if any(type(value) is not bool for value in boolean_axioms.values()):
        raise AssertionError("malformed Boolean axiom vector")
    if not all(boolean_axioms.values()):
        raise AssertionError("selected embedding failed an axiom")

    graph_public = {
        "candidate_count": len(universe["candidates"]),
        "eligible_candidate_count": len(eligible),
        "individually_rejected_count": len(graph["rejected"]),
        "conflict_count": len(graph["conflicts"]),
        **graph_metrics(graph["conflict_masks"]),
    }
    public_model = {
        "factor_base": factor_record,
        "selected_maxima": optimizer["witness_list"],
        "formal_family_count": model["formal_family_count"],
        "formal_degree_histogram": model["formal_degree_histogram"],
        "axioms": model["axioms"],
        "constrained_count": model["constrained_count"],
        "delta": exact_ratio(model["constrained_count"], group_size),
        "public_edge_count": model["public_edge_count"],
        "public_edges": model["public_edges"],
        "public_edges_sha256": model["public_edges_sha256"],
    }
    private_audit = {
        "graph": graph_public,
        "eligible_universe_indices": graph["eligible_universe_indices"],
        "individually_rejected": graph["rejected"],
        "conflicts": graph["conflicts"],
        "optimizer": optimizer,
        "retention": {
            "raw_final_support": len(raw_support),
            "retained_final_support": len(retained_support),
            "retained_to_raw": exact_ratio(len(retained_support), max(1, len(raw_support))),
            "absolute_group_coverage": exact_ratio(len(retained_support), group_size),
            "raw_maximum_multiplicity": max(raw_multiplicities.values(), default=0),
            "retained_maximum_multiplicity": max(retained_multiplicities.values(), default=0),
        },
        "expansion": expansion,
    }
    accounting = {
        "public_json_bytes": len(stable_json(public_model)),
        "private_audit_json_bytes": len(stable_json(private_audit)),
        "in_memory_deep_bytes": deep_size(
            {"public_model": public_model, "private_audit": private_audit}
        ),
    }
    after = asdict(ops)
    row = {
        "curve": curve_info,
        "B": B,
        "family": family,
        "null_replicate": null_replicate,
        "valid": True,
        "public_model": public_model,
        "private_audit": private_audit,
        "accounting": accounting,
        "operation_counts": operation_delta(before, after),
        "wall_time_seconds": time.perf_counter() - started,
    }
    row["row_sha256"] = stable_digest(row)
    return row


def constrained_budget_caps(group_size: int) -> list[int]:
    group_size = require_int(group_size, "group size", 2)
    return sorted(
        {
            max(1, group_size // 4),
            max(1, group_size // 2),
            max(1, 3 * group_size // 4),
            group_size,
        }
    )


def build_density_row(
    curve: Curve,
    points: Sequence[Point],
    curve_info: dict[str, Any],
    B: int,
    family: str,
    null_replicate: int | None,
    node_cap: int,
    ops: OperationCounts,
) -> dict[str, Any]:
    frozen_association = (
        type(curve) is Curve
        and type(ops) is OperationCounts
        and curve.ops is ops
        and curve.p == FROZEN_FIXTURE["p"]
        and curve.a == FROZEN_FIXTURE["a"]
        and curve.b == FROZEN_FIXTURE["b"]
        and type(points) is list
        and len(points) == len(FROZEN_POINTS)
        and all(
            point is None
            or (
                type(point) is tuple
                and len(point) == 2
                and all(type(coordinate) is int for coordinate in point)
            )
            for point in points
        )
        and tuple(points) == FROZEN_POINTS
        and type(curve_info) is dict
        and exact_json_equal(curve_info, frozen_curve_record_contract())
        and type(B) is int
        and B == 4
        and type(family) is str
        and family == "least_x_interval"
        and null_replicate is None
        and type(node_cap) is int
        and node_cap == FROZEN_NODE_CAP
    )
    if not frozen_association:
        raise PermissionError(
            "version-18 generated density-row construction is disabled; "
            "only the frozen p=19 B=4 control is admitted"
        )
    started = time.perf_counter()
    factors, factor_record = factor_base(
        curve, points, curve_info, B, family, null_replicate, ops
    )
    expansion = degree_expansion(curve, factors)
    universe = balanced_universe(curve, factors)
    graph = candidate_graph(curve, factors, universe["candidates"])
    eligible = graph["eligible"]
    pair_outputs, group_size = pair_output_table(
        curve, [item["point"] for item in eligible]
    )
    balanced_raw_support, balanced_raw_multiplicities = support_from_points(
        curve, universe["raw_a4"]
    )
    eight_fold_support = expansion["8"]["support"]

    public_frontier: list[dict[str, Any]] = []
    private_frontier: list[dict[str, Any]] = []
    for cap in constrained_budget_caps(group_size):
        cap_started = time.perf_counter()
        model_cache: dict[int, dict[str, Any]] = {}
        model_cache_limit = node_cap + len(eligible) ** 2 + 64

        def full_model(mask: int) -> dict[str, Any]:
            if mask not in model_cache:
                if len(model_cache) >= model_cache_limit:
                    raise RuntimeError("full-model cache ceiling exceeded")
                selected_for_model = [eligible[index] for index in iter_mask(mask)]
                model_cache[mask] = model_metrics(
                    curve, factors, selected_for_model
                )
            return model_cache[mask]

        def tiebreak(mask: int) -> dict[str, Any]:
            candidate_model = full_model(mask)
            return {
                "constrained_count": candidate_model["constrained_count"],
                "public_edge_count": candidate_model["public_edge_count"],
                "witness_list": candidate_model["witness_list"],
            }

        optimizer = optimize_coverage_graph(
            pair_outputs,
            group_size,
            graph["conflict_masks"],
            node_cap,
            tiebreak,
            max_constrained=cap,
            objective_mode="density",
        )
        ops.optimizer_nodes += optimizer["explored_nodes"]
        ops.optimizer_bound_calls += optimizer["bound_calls"]
        selected_mask = int(optimizer["selected_mask_hex"], 16)
        selected = [eligible[index] for index in optimizer["selected_indices"]]
        model = full_model(selected_mask)
        if model["constrained_count"] > cap:
            raise AssertionError("density optimizer exceeded constrained-label cap")
        retained_support_mask = support_mask_for_selection(selected_mask, pair_outputs)
        retained_points = [item["point"] for item in selected]
        retained_support, retained_multiplicities = support_from_points(
            curve, retained_points
        )
        if not (
            retained_support_mask.bit_count()
            == len(retained_support)
            == optimizer["retained_support_lower_bound"]
        ):
            raise AssertionError("density-frontier support recount mismatch")
        boolean_axioms = {
            key: value
            for key, value in model["axioms"].items()
            if key not in {"associativity_method", "forbidden_final_edge_count"}
        }
        if any(type(value) is not bool for value in boolean_axioms.values()) or not all(
            boolean_axioms.values()
        ):
            raise AssertionError("density-frontier embedding failed an axiom")
        public_frontier.append(
            {
                "constrained_cap": cap,
                "selected_maxima": optimizer["witness_list"],
                "formal_family_count": model["formal_family_count"],
                "formal_degree_histogram": model["formal_degree_histogram"],
                "axioms": model["axioms"],
                "constrained_count": model["constrained_count"],
                "delta": exact_ratio(model["constrained_count"], group_size),
                "public_edge_count": model["public_edge_count"],
                "public_edges": model["public_edges"],
                "public_edges_sha256": model["public_edges_sha256"],
                "source_table": model["source_table"],
                "source_table_sha256": model["source_table_sha256"],
            }
        )
        private_cap = {
            "constrained_cap": cap,
            "optimizer": optimizer,
            "retention": {
                "balanced_raw_final_support": len(balanced_raw_support),
                "eight_fold_support": eight_fold_support,
                "retained_final_support": len(retained_support),
                "retained_to_balanced_raw": exact_ratio(
                    len(retained_support), max(1, len(balanced_raw_support))
                ),
                "retained_to_eight_fold": exact_ratio(
                    len(retained_support), max(1, eight_fold_support)
                ),
                "absolute_group_coverage": exact_ratio(
                    len(retained_support), group_size
                ),
                "balanced_raw_maximum_multiplicity": max(
                    balanced_raw_multiplicities.values(), default=0
                ),
                "retained_maximum_multiplicity": max(
                    retained_multiplicities.values(), default=0
                ),
            },
            "structural_work": {
                "optimizer_nodes": optimizer["explored_nodes"],
                "optimizer_bound_calls": optimizer["bound_calls"],
                "optimizer_metric_cache_entries": optimizer[
                    "metric_cache_entries"
                ],
                "full_model_cache_entries": len(model_cache),
                "serialized_frontier_states": len(optimizer["frontier_states"]),
                "selected_maxima": len(selected),
                "retained_final_pair_cells": len(selected)
                * (len(selected) + 1)
                // 2,
                "public_edges": model["public_edge_count"],
                "source_table_entries": len(model["source_table"]),
            },
        }
        private_cap["wall_time_seconds"] = time.perf_counter() - cap_started
        private_frontier.append(private_cap)

    graph_record = {
        "candidate_count": len(universe["candidates"]),
        "eligible_candidate_count": len(eligible),
        "individually_rejected_count": len(graph["rejected"]),
        "conflict_count": len(graph["conflicts"]),
        **graph_metrics(graph["conflict_masks"]),
    }
    public_model = {
        "factor_base": factor_record,
        "ordering_contract": ORDERING_CONTRACT,
        "representative_compiler": universe["representative_compiler"],
        "constrained_budget_caps": constrained_budget_caps(group_size),
        "density_frontier": public_frontier,
    }
    private_audit = {
        "graph": graph_record,
        "eligible_universe_indices": graph["eligible_universe_indices"],
        "individually_rejected": graph["rejected"],
        "conflicts": graph["conflicts"],
        "density_frontier": private_frontier,
        "expansion": expansion,
    }
    structural_work = {
        "scope": "deterministic combinatorial cells; not CPU instructions",
        "degree_multiset_evaluations": sum(
            expansion[str(degree)]["formal_multiset_witness_count"]
            for degree in (1, 2, 4, 8)
        ),
        "balanced_degree2_formals": universe["degree2_count"],
        "balanced_nonidentity_2F_representatives": universe["canonical2_count"],
        "balanced_degree4_parent_pairs": universe["raw4_count"],
        "degree4_candidates": len(universe["candidates"]),
        "individual_injectivity_checks": len(universe["candidates"]),
        "conflict_pair_checks": len(eligible) * (len(eligible) - 1) // 2,
        "pair_output_cells": len(eligible) * (len(eligible) + 1) // 2,
        "balanced_final_pair_cells": len(universe["raw_a4"])
        * (len(universe["raw_a4"]) + 1)
        // 2,
    }
    wall_time_seconds = time.perf_counter() - started
    row_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "curve": curve_info,
        "B": B,
        "family": family,
        "null_replicate": null_replicate,
        "valid": True,
        "public_model": public_model,
        "private_audit": private_audit,
        "structural_work": structural_work,
        "wall_time_seconds": wall_time_seconds,
    }
    accounting = {
        "scope": "nested canonical-JSON byte measures; fields are nonadditive",
        "public_model_json_bytes": len(stable_json(public_model)),
        "private_audit_json_bytes": len(stable_json(private_audit)),
        "row_payload_without_accounting_or_digest_json_bytes": len(
            stable_json(row_payload)
        ),
        "nested_per_cap_json_bytes": [
            {
                "constrained_cap": public["constrained_cap"],
                "public_embedding_json_bytes": len(stable_json(public)),
                "private_cap_json_bytes": len(stable_json(private)),
            }
            for public, private in zip(public_frontier, private_frontier)
        ],
    }
    row = {**row_payload, "accounting": accounting}
    row["row_sha256"] = stable_digest(row)
    return row


def fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def ratio_fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def exact_median(values: Sequence[Fraction]) -> Fraction:
    if not values:
        raise ValueError("median requires at least one value")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def cap_pair(row: dict[str, Any], cap: int) -> tuple[dict[str, Any], dict[str, Any]]:
    pairs = [
        (public, private)
        for public, private in zip(
            row["public_model"]["density_frontier"],
            row["private_audit"]["density_frontier"],
        )
        if public["constrained_cap"] == cap
        and private["constrained_cap"] == cap
    ]
    if len(pairs) != 1:
        raise ValueError(f"row has {len(pairs)} cells for cap {cap}")
    return pairs[0]


def require_exhausted_gate_cell(optimizer: dict[str, Any]) -> None:
    integer_fields = (
        "retained_support_lower_bound",
        "retained_support_upper_bound",
        "absolute_gap",
        "remaining_frontier_nodes",
    )
    if any(type(optimizer.get(name)) is not int for name in integer_fields):
        raise ValueError("family gate optimizer exactness fields are not integers")
    if not (
        optimizer.get("primary_exact") is True
        and optimizer.get("full_objective_exact") is True
        and optimizer["retained_support_lower_bound"]
        == optimizer["retained_support_upper_bound"]
        and optimizer["absolute_gap"] == 0
        and optimizer["remaining_frontier_nodes"] == 0
        and optimizer.get("frontier_states") == []
        and optimizer.get("frontier_sha256") == stable_digest([])
        and optimizer.get("termination_reason") == "full_objective_proved"
    ):
        raise ValueError("family gate received a nonexhausted optimizer cell")


def evaluate_family_gate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[int, int, int, str, int | None], dict[str, Any]] = {}
    for row in rows:
        for cell in row["private_audit"]["density_frontier"]:
            require_exhausted_gate_cell(cell["optimizer"])
        key = (
            row["curve"]["bits"],
            row["curve"]["seed"],
            row["B"],
            row["family"],
            row["null_replicate"],
        )
        if key in by_key:
            raise ValueError(f"duplicate gate row {key!r}")
        by_key[key] = row

    family_reports: list[dict[str, Any]] = []
    passing_pairs: list[dict[str, str]] = []
    every_family_collapses = True
    for family in COORDINATE_FAMILIES:
        persistence: list[dict[str, Any]] = []
        persistence_pass = True
        for bits in CANONICAL_BITS:
            ratios: list[Fraction] = []
            for seed in CANONICAL_SEEDS:
                for B in CANONICAL_FACTOR_BASE_SIZES:
                    row = by_key[(bits, seed, B, family, None)]
                    _, private = cap_pair(row, row["curve"]["q"])
                    ratios.append(
                        ratio_fraction(private["retention"]["retained_to_balanced_raw"])
                    )
            median_ratio = exact_median(ratios)
            bit_pass = median_ratio >= Fraction(1, 4)
            persistence_pass &= bit_pass
            persistence.append(
                {
                    "bits": bits,
                    "median_retained_to_balanced_raw": fraction_json(median_ratio),
                    "pass": bit_pass,
                }
            )
        collapse_strata = sum(
            ratio_fraction(item["median_retained_to_balanced_raw"])
            < Fraction(1, 10)
            for item in persistence
        )
        family_collapses = collapse_strata >= 3
        every_family_collapses &= family_collapses

        cap_reports: list[dict[str, Any]] = []
        for cap_fraction in ("1/2", "3/4"):
            positive_count = 0
            stratum_reports: list[dict[str, Any]] = []
            passing_strata = 0
            for bits in CANONICAL_BITS:
                margins: list[Fraction] = []
                for seed in CANONICAL_SEEDS:
                    for B in CANONICAL_FACTOR_BASE_SIZES:
                        candidate = by_key[(bits, seed, B, family, None)]
                        q = candidate["curve"]["q"]
                        cap = q // 2 if cap_fraction == "1/2" else 3 * q // 4
                        null_supports = []
                        for replicate in range(CANONICAL_NULL_REPLICATES):
                            null = by_key[
                                (bits, seed, B, NULL_FAMILY, replicate)
                            ]
                            _, null_private = cap_pair(null, cap)
                            null_supports.append(
                                null_private["optimizer"][
                                    "retained_support_lower_bound"
                                ]
                            )
                        _, candidate_private = cap_pair(candidate, cap)
                        candidate_support = candidate_private["optimizer"][
                            "retained_support_lower_bound"
                        ]
                        null_median = exact_median(
                            [Fraction(value, 1) for value in null_supports]
                        )
                        difference = Fraction(candidate_support, 1) - null_median
                        if difference > 0:
                            positive_count += 1
                        threshold = max(1, (q + 19) // 20)
                        margins.append(difference - threshold)
                median_margin = exact_median(margins)
                stratum_pass = median_margin >= 0
                passing_strata += int(stratum_pass)
                stratum_reports.append(
                    {
                        "bits": bits,
                        "median_threshold_margin": fraction_json(median_margin),
                        "pass": stratum_pass,
                    }
                )
            cap_pass = passing_strata >= 3 and positive_count >= 18
            cap_reports.append(
                {
                    "cap_fraction": cap_fraction,
                    "passing_bit_strata": passing_strata,
                    "positive_comparisons": positive_count,
                    "comparison_count": 24,
                    "strata": stratum_reports,
                    "pass": cap_pass,
                }
            )
            if persistence_pass and cap_pass:
                passing_pairs.append(
                    {"family": family, "cap_fraction": cap_fraction}
                )
        family_reports.append(
            {
                "family": family,
                "full_cap_persistence": persistence,
                "full_cap_persistence_pass": persistence_pass,
                "full_cap_collapse_strata": collapse_strata,
                "full_cap_collapse": family_collapses,
                "matched_null_cap_tests": cap_reports,
            }
        )
    status = "PASS" if passing_pairs else "FAIL"
    if passing_pairs:
        negative_outcome = "NOT_APPLICABLE"
    elif every_family_collapses:
        negative_outcome = "COLLAPSE"
    else:
        negative_outcome = "WEAKEN_OR_REJECT"
    return {
        "criterion_version": "sgcp-embed-002-family-gate-v18",
        "null_median": "exact arithmetic mean of the middle two of four precommitted null supports",
        "null_duplicate_policy": "retain duplicate precommitted null selections without resampling",
        "unresolved_policy": "every cell must have equal integer bounds, zero integer gap, exact primary and full objectives, and an empty authenticated frontier",
        "cap_selection_policy": "one fixed family and one fixed cap fraction must pass across strata",
        "collapse_policy": "COLLAPSE iff every coordinate family has full-cap median retention below 1/10 in at least three bit strata",
        "status": status,
        "negative_outcome": negative_outcome,
        "passing_family_cap_pairs": passing_pairs,
        "families": family_reports,
    }


def canonical_parameters() -> dict[str, Any]:
    return {
        "bits": list(CANONICAL_BITS),
        "seeds": list(CANONICAL_SEEDS),
        "factor_base_sizes": list(CANONICAL_FACTOR_BASE_SIZES),
        "coordinate_families": list(COORDINATE_FAMILIES),
        "null_family": NULL_FAMILY,
        "null_replicates": CANONICAL_NULL_REPLICATES,
        "node_cap_per_cap": CANONICAL_NODE_CAP,
        "representative_compiler": REPRESENTATIVE_COMPILER,
        "ordering_contract_sha256": stable_digest(ORDERING_CONTRACT),
        "constrained_budget_rule": "floor(q/4),floor(q/2),floor(3q/4),q",
    }


def canonical_row_keys() -> list[tuple[int, int, int, str, int | None]]:
    keys: list[tuple[int, int, int, str, int | None]] = []
    for bits in CANONICAL_BITS:
        for seed in CANONICAL_SEEDS:
            for B in CANONICAL_FACTOR_BASE_SIZES:
                keys.extend((bits, seed, B, family, None) for family in COORDINATE_FAMILIES)
                keys.extend(
                    (bits, seed, B, NULL_FAMILY, replicate)
                    for replicate in range(CANONICAL_NULL_REPLICATES)
                )
    return keys


def validate_canonical_rows(rows: Sequence[dict[str, Any]]) -> None:
    observed = [
        (
            row["curve"]["bits"],
            row["curve"]["seed"],
            row["B"],
            row["family"],
            row["null_replicate"],
        )
        for row in rows
    ]
    if (
        observed != canonical_row_keys()
        or any(type(value) is not int for key in observed for value in key[:3])
        or any(
            type(key[3]) is not str
            or (key[4] is not None and type(key[4]) is not int)
            for key in observed
        )
    ):
        raise ValueError("canonical row grid/order mismatch")
    curves: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    curve_records: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        curve = row["curve"]
        key = (curve["bits"], curve["seed"])
        value = tuple(curve[name] for name in ("p", "a", "b", "q"))
        if any(type(item) is not int for item in (*key, *value)):
            raise ValueError("canonical curve key/value has a noninteger type")
        if key in curves and curves[key] != value:
            raise ValueError(f"inconsistent canonical curve record for {key!r}")
        if key in curve_records and not exact_json_equal(curve_records[key], curve):
            raise ValueError(f"inconsistent canonical curve transcript for {key!r}")
        curves[key] = value
        curve_records[key] = curve
        caps = constrained_budget_caps(curve["q"])
        if not exact_json_equal(
            row["public_model"]["constrained_budget_caps"], caps
        ):
            raise ValueError("canonical constrained-cap schedule mismatch")
        public_caps = [
            cell["constrained_cap"]
            for cell in row["public_model"]["density_frontier"]
        ]
        private_caps = [
            cell["constrained_cap"]
            for cell in row["private_audit"]["density_frontier"]
        ]
        if not exact_json_equal(public_caps, caps) or not exact_json_equal(
            private_caps, caps
        ):
            raise ValueError("canonical cap-cell association mismatch")
        for cell in row["private_audit"]["density_frontier"]:
            optimizer = cell["optimizer"]
            if (
                type(optimizer["node_cap"]) is not int
                or optimizer["node_cap"] != CANONICAL_NODE_CAP
            ):
                raise ValueError("canonical optimizer node-cap mismatch")
            require_exhausted_gate_cell(optimizer)
    if len(set(curves.values())) != len(curves):
        raise ValueError("cross-seed duplicate accepted curve")


def frozen_parameters(node_cap: int) -> dict[str, Any]:
    if type(node_cap) is not int or node_cap != FROZEN_NODE_CAP:
        raise ValueError(f"frozen node cap must equal {FROZEN_NODE_CAP}")
    return {
        "curve": dict(FROZEN_FIXTURE),
        "B": 4,
        "family": "least_x_interval",
        "null_replicate": None,
        "node_cap_per_cap": FROZEN_NODE_CAP,
        "representative_compiler": REPRESENTATIVE_COMPILER,
        "ordering_contract_sha256": stable_digest(ORDERING_CONTRACT),
    }


def document_summary(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    cap_cells = [
        cell
        for row in rows
        for cell in row["private_audit"]["density_frontier"]
    ]
    return {
        "row_count": len(rows),
        "valid_rows": sum(row["valid"] is True for row in rows),
        "unique_curve_records": len(
            {
                stable_digest(row["curve"])
                for row in rows
            }
        ),
        "cap_cell_count": len(cap_cells),
        "primary_exact_cap_cells": sum(
            cell["optimizer"]["primary_exact"] is True for cell in cap_cells
        ),
        "full_objective_exact_cap_cells": sum(
            cell["optimizer"]["full_objective_exact"] is True
            for cell in cap_cells
        ),
        "maximum_primary_gap": max(
            (cell["optimizer"]["absolute_gap"] for cell in cap_cells), default=0
        ),
    }


def build_document(
    rows: Sequence[dict[str, Any]], scope: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    if scope not in {"canonical", "frozen_fixture"}:
        raise ValueError(f"unknown document scope {scope!r}")
    if scope == "canonical":
        validate_canonical_rows(rows)
    document = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "protocol_version": PROTOCOL_VERSION,
        "scope": scope,
        "canonical": scope == "canonical",
        "claim_status": CLAIM_STATUS,
        "interpretation": (
            "canonical candidate; coordinator interpretation still required"
            if scope == "canonical"
            else "frozen-fixture implementation evidence only"
        ),
        "parameters": parameters,
        "rows": list(rows),
        "summary": document_summary(rows),
        "family_gate": (
            evaluate_family_gate(rows)
            if scope == "canonical"
            else {
                "status": "NOT_APPLICABLE",
                "reason": "frozen fixture is not a family matrix",
            }
        ),
    }
    document["document_sha256"] = stable_digest(document)
    return document


def build_frozen_control_document(node_cap: int = FROZEN_NODE_CAP) -> dict[str, Any]:
    if type(node_cap) is not int or node_cap != FROZEN_NODE_CAP:
        raise ValueError(f"frozen node cap must equal {FROZEN_NODE_CAP}")
    ops = OperationCounts()
    curve, points, record = frozen_curve(ops)
    row = build_density_row(
        curve,
        points,
        record,
        4,
        "least_x_interval",
        None,
        node_cap,
        ops,
    )
    return build_document([row], "frozen_fixture", frozen_parameters(node_cap))


def build_development_document(args: argparse.Namespace) -> dict[str, Any]:
    raise PermissionError(
        "version-18 development curve-row budget is zero; use the frozen control only"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--bits", nargs="+", type=int, default=[5, 6])
    parser.add_argument("--seeds", nargs="+", type=int, default=[101])
    parser.add_argument("--factor-base-sizes", nargs="+", type=int, default=[4, 6])
    parser.add_argument(
        "--families",
        nargs="+",
        default=["least_x_interval", "mobius_interval", "two_mobius_union"],
    )
    parser.add_argument("--null-replicates", type=int, default=1)
    parser.add_argument("--node-cap", type=int, default=200000)
    parser.add_argument("--max-rows", type=int, default=18)
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.development:
        raise PermissionError(
            "canonical execution is disabled: specification status is review_required and maximum_runs is zero"
        )
    raise PermissionError(
        "version-18 development curve-row budget is zero; run unit and frozen-fixture controls only"
    )


if __name__ == "__main__":
    raise SystemExit(main())

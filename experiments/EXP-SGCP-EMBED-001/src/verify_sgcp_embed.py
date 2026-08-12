#!/usr/bin/env python3
"""Independent verifier for the SGCP-EMBED-001 five-bit preflight.

This module intentionally shares no code with the certificate builder.  It
reconstructs the p=19 fixture, every formal object, all exhaustive-search proof
rows, and all registered controls using only Python's standard library.

The builder certificate must not contain a scalar table or scalar indices.
Only the SHA-256 of the independently reconstructed scalar table is emitted by
this verifier.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import math
import os
import platform
import re
import resource
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence


CERTIFICATE_SCHEMA = "sgcp-embed-001-certificate-v1"
REPORT_SCHEMA = "sgcp-embed-001-verification-report-v1"
EXPERIMENT_ID = "SGCP-EMBED-001"
RUNNER_EXPERIMENT_ID = "EXP-SGCP-EMBED-001"
CLAIM_STATUS = "HYPOTHESIS"
CONTROL_REGISTRY_SHA256 = (
    "cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca"
)
LITERATURE_SHA256 = (
    "169604e8e0c2bf13cfc2d14067868af2e8c41b8346395e160b2d9103f1e31a60"
)
PAPER_SHA256 = (
    "82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f"
)
MATHEMATICAL_CONTRACT_SHA256 = (
    "f2f7c897bfb240708055fc06e09f4bba68b2e35703e02585b564761474a71e73"
)
EXPERIMENT_CONTRACT_SHA256 = (
    "36e624cc53d45e46fffcf520e18bd8f54e87275f86b71ef94d2d6af7ed4a69c4"
)
SCALAR_TABLE_SHA256 = (
    "c73fdf6300e4d83ac581a07935a31dbaf6c4af3fb6b3cbe762f4266170c3f44c"
)
SCALAR_INDEX_ORACLE_SOURCE_SHA256 = (
    "a2e5af8c3fab960ec663c08fbdecf869262088ac5c5b628fb967d89a561b5fb6"
)
SCALAR_INDEX_ORACLE_ARTIFACT_SHA256 = (
    "830e96d8e8095960d31e51c9af1d9afaf14990e209a7a113648cef79feb87f3e"
)

CURVE_P = 19
CURVE_A = 2
CURVE_B = 9
CURVE_Q = 23
CURVE_G = (0, 3)
FACTOR_BASE_SIZES = (4, 6, 8)
SCRIPT_PATH = Path(__file__).resolve()
BUILDER_PATH = SCRIPT_PATH.with_name("sgcp_embed.py")
SCALAR_INDEX_ORACLE_SOURCE_PATH = SCRIPT_PATH.with_name(
    "verify_sgcp_scalar_index.py"
)
SCALAR_INDEX_ORACLE_ARTIFACT_PATH = (
    SCRIPT_PATH.parents[1] / "oracles" / "scalar-index-oracle-v1.json"
)
CONTROL_REGISTRY_PATH = SCRIPT_PATH.parents[1] / "control-registry-v2.json"
REPO_ROOT = SCRIPT_PATH.parents[3]
MATHEMATICAL_CONTRACT_PATH = (
    REPO_ROOT / "notes" / "sgcp_embed_001_contract_20260717.md"
)
EXPERIMENT_CONTRACT_PATH = SCRIPT_PATH.parents[1] / "contract.md"
LITERATURE_PATH = (
    REPO_ROOT / "notes" / "structured_group_coordinate_predicates_literature_20260717.md"
)
PREFLIGHT_DIR = SCRIPT_PATH.parents[1] / "preflight"
CERTIFICATE_PATH = PREFLIGHT_DIR / "sgcp-embed-001-5bit.json"
REPORT_PATH = PREFLIGHT_DIR / "sgcp-embed-001-5bit-verification.json"
EXPECTED_BRANCH = "codex/sgcp-embed-001"
EXPECTED_BUILDER_OPERATIONS = {
    "point_add_calls": 1612220,
    "point_doublings": 302627,
    "field_inversions": 967579,
    "field_multiplications": 3205364,
    "multiset_evaluations": 664529,
    "injectivity_checks": 21161,
    "associativity_triples": 106863,
    "optimizer_nodes": 20736,
}
EXPECTED_ROW_OPERATIONS = {
    4: {
        "point_add_calls": 261596,
        "point_doublings": 60082,
        "field_inversions": 163196,
        "field_multiplications": 549670,
        "multiset_evaluations": 102271,
        "injectivity_checks": 4197,
        "associativity_triples": 12725,
        "optimizer_nodes": 4096,
    },
    6: {
        "point_add_calls": 17745,
        "point_doublings": 3682,
        "field_inversions": 10489,
        "field_multiplications": 35149,
        "multiset_evaluations": 7181,
        "injectivity_checks": 356,
        "associativity_triples": 12722,
        "optimizer_nodes": 256,
    },
    8: {
        "point_add_calls": 1332354,
        "point_doublings": 238791,
        "field_inversions": 793559,
        "field_multiplications": 2619468,
        "multiset_evaluations": 554921,
        "injectivity_checks": 16603,
        "associativity_triples": 12722,
        "optimizer_nodes": 16384,
    },
}
FROZEN_REVIEW_ROOT = Path(
    "/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy"
)

PREDICATE_ORDER = (
    "source_gate",
    "evaluation_injective",
    "identity",
    "commutativity",
    "associativity",
    "compatibility_coordinates",
    "compatibility_scalars",
    "unique_factorization",
    "acyclic_reduced",
    "direct_final_edge_excluded",
    "optimizer_exact",
)

TRUE = "true"
FALSE = "false"
NA = "not-applicable"
VERIFIER_ONLY = "verifier-only"
HEX_256_RE = re.compile(r"^[0-9a-f]{64}$")

Point = tuple[int, int] | None
Formal = tuple[int, ...]


class StrictJSONError(ValueError):
    """Raised when a JSON artifact violates strict parsing requirements."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _parse_finite_float(token: str) -> Decimal:
    try:
        value = Decimal(token)
    except InvalidOperation as exc:
        raise StrictJSONError(f"invalid JSON number: {token!r}") from exc
    if not value.is_finite():
        raise StrictJSONError(f"non-finite JSON number: {token!r}")
    return value


def _reject_json_constant(token: str) -> None:
    raise StrictJSONError(f"non-finite JSON constant: {token!r}")


def strict_json_load_bytes(raw: bytes, source: str) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise StrictJSONError(f"{source}: input is not UTF-8: {exc}") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_parse_finite_float,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, StrictJSONError) as exc:
        raise StrictJSONError(f"{source}: {exc}") from exc


def read_strict_json(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    return strict_json_load_bytes(raw, str(path)), raw


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize deterministic verifier data; Decimal is deliberately absent."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def set_fixed_point_json_size(record: dict[str, Any], field: str) -> None:
    if field in record:
        raise ValueError(f"fixed-point JSON size field already exists: {field}")
    candidate = 0
    for _ in range(32):
        record[field] = candidate
        observed = len(canonical_json_bytes(record))
        if observed == candidate:
            return
        candidate = observed
    raise AssertionError(f"fixed-point JSON size did not converge for {field}")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require_bound_file(
    path: Path, expected: Path, expected_sha256: str, label: str
) -> Path:
    resolved = path.resolve(strict=True)
    expected_resolved = expected.resolve(strict=True)
    if resolved != expected_resolved:
        raise AssertionError(
            f"{label} path mismatch: expected {expected_resolved}, observed {resolved}"
        )
    actual = file_sha256(resolved)
    if actual != expected_sha256:
        raise AssertionError(
            f"{label} hash mismatch: expected {expected_sha256}, observed {actual}"
        )
    return resolved


def git_text(*args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def is_exact_int(value: Any) -> bool:
    return type(value) is int


def require_exact_int(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    if not is_exact_int(value):
        errors.append(
            f"{path}: expected exact JSON integer, got {type(value).__name__}"
        )
        return None
    if minimum is not None and value < minimum:
        errors.append(f"{path}: expected integer >= {minimum}, got {value}")
    if maximum is not None and value > maximum:
        errors.append(f"{path}: expected integer <= {maximum}, got {value}")
    return value


def status(value: bool) -> str:
    return TRUE if value else FALSE


def ratio(numerator: int, denominator: int) -> dict[str, int]:
    if denominator <= 0:
        raise ValueError("ratio denominator must be positive")
    divisor = math.gcd(numerator, denominator)
    report = {
        "numerator": numerator // divisor,
        "denominator": denominator // divisor,
    }
    return report


def compact_value(value: Any, limit: int = 320) -> str:
    try:
        rendered = canonical_json_bytes(value).decode("utf-8")
    except (TypeError, ValueError):
        rendered = repr(value)
    if len(rendered) > limit:
        return rendered[: limit - 3] + "..."
    return rendered


def compare_exact(expected: Any, actual: Any, path: str, errors: list[str]) -> None:
    """Deep comparison that treats bool, int, and Decimal as distinct types."""
    if type(expected) is not type(actual):
        errors.append(
            f"{path}: type mismatch; expected {type(expected).__name__}, "
            f"got {type(actual).__name__} ({compact_value(actual)})"
        )
        return
    if isinstance(expected, dict):
        expected_keys = set(expected)
        actual_keys = set(actual)
        for key in sorted(expected_keys - actual_keys):
            errors.append(f"{path}.{key}: missing key")
        for key in sorted(actual_keys - expected_keys):
            errors.append(f"{path}.{key}: unexpected key")
        for key in sorted(expected_keys & actual_keys):
            compare_exact(expected[key], actual[key], f"{path}.{key}", errors)
        return
    if isinstance(expected, list):
        if len(expected) != len(actual):
            errors.append(
                f"{path}: list length mismatch; expected {len(expected)}, "
                f"got {len(actual)}"
            )
        for index, (expected_item, actual_item) in enumerate(
            zip(expected, actual)
        ):
            compare_exact(
                expected_item, actual_item, f"{path}[{index}]", errors
            )
        return
    if expected != actual:
        errors.append(
            f"{path}: value mismatch; expected {compact_value(expected)}, "
            f"got {compact_value(actual)}"
        )


def point_json(point: Point) -> str | list[int]:
    if point is None:
        return "O"
    return [point[0], point[1]]


def point_registry_text(point: Point) -> str:
    if point is None:
        return "O"
    return f"{point[0]}:{point[1]}"


def point_sort_key(point: Point) -> tuple[int, int, int]:
    if point is None:
        return (0, -1, -1)
    return (1, point[0], point[1])


def canonical_pair_indices(i: int, j: int) -> tuple[int, int]:
    return (i, j) if i <= j else (j, i)


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        return (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        if not self.on_curve(left) or not self.on_curve(right):
            raise ValueError("attempted EC addition with an off-curve point")
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            denominator = (2 * y1) % self.p
            if denominator == 0:
                return None
            slope = ((3 * x1 * x1 + self.a) * pow(denominator, -1, self.p)) % self.p
        else:
            denominator = (x2 - x1) % self.p
            if denominator == 0:
                return None
            slope = ((y2 - y1) * pow(denominator, -1, self.p)) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.on_curve(result):
            raise AssertionError("independent EC arithmetic produced off-curve output")
        return result

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        if type(scalar) is not int or scalar < 0:
            raise ValueError("scalar_mul requires a nonnegative exact integer")
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            remaining >>= 1
        return result

    def enumerate_affine_points(self) -> list[Point]:
        points: list[Point] = []
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y) % self.p == rhs:
                    points.append((x, y))
        return sorted(points, key=point_sort_key)


def independently_build_curve() -> tuple[Curve, list[Point], list[Point], dict[Point, int]]:
    curve = Curve(CURVE_P, CURVE_A, CURVE_B)
    discriminant_factor = (4 * CURVE_A**3 + 27 * CURVE_B**2) % CURVE_P
    if discriminant_factor == 0:
        raise AssertionError("registered curve is singular")
    affine = curve.enumerate_affine_points()
    labels: list[Point] = [None, *affine]
    if len(labels) != CURVE_Q:
        raise AssertionError(
            f"curve recount mismatch: expected {CURVE_Q}, found {len(labels)}"
        )
    if affine[0] != CURVE_G:
        raise AssertionError(
            f"generator is not lexicographically first affine point: {affine[0]}"
        )
    scalar_table = [curve.scalar_mul(k, CURVE_G) for k in range(CURVE_Q)]
    if curve.scalar_mul(CURVE_Q, CURVE_G) is not None:
        raise AssertionError("registered generator does not have order q")
    if len(set(scalar_table)) != CURVE_Q or set(scalar_table) != set(labels):
        raise AssertionError("scalar table is not a bijection onto E(F_p)")
    scalar_by_point = {point: scalar for scalar, point in enumerate(scalar_table)}
    return curve, labels, scalar_table, scalar_by_point


def polynomial_from_roots_mod_p(roots: Sequence[int], p: int) -> list[int]:
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] = (updated[degree] - root * coefficient) % p
            updated[degree + 1] = (updated[degree + 1] + coefficient) % p
        coefficients = updated
    return coefficients


def build_factor_base(
    curve: Curve, labels: Sequence[Point], size: int
) -> tuple[list[Point], dict[str, Any]]:
    if size not in FACTOR_BASE_SIZES or size % 2:
        raise ValueError(f"unsupported factor-base size: {size}")
    affine = [point for point in labels if point is not None]
    point_bearing_x = sorted({point[0] for point in affine})
    roots = point_bearing_x[: size // 2]
    factors = sorted(
        [point for point in affine if point[0] in set(roots)],
        key=point_sort_key,
    )
    if len(factors) != size or len(set(factors)) != size:
        raise AssertionError("coordinate factor base does not contain exactly B points")
    source_records: list[dict[str, int]] = []
    for factor in factors:
        assert factor is not None
        x, y = factor
        smaller_y = min(y, (-y) % curve.p)
        sign_bit = 0 if y == smaller_y else 1
        source_records.append(
            {
                "root_index": roots.index(x),
                "x": x,
                "sign_bit": sign_bit,
                "y": y,
            }
        )
    factor_base_json = {
        "size": size,
        "root_x_coordinates": roots,
        "polynomial_coefficients_ascending_mod_p": polynomial_from_roots_mod_p(
            roots, curve.p
        ),
        "points": [point_json(point) for point in factors],
        "source_records": source_records,
        "source_gate": TRUE,
    }
    return factors, factor_base_json


def builder_factor_base_json(factors: Sequence[Point], size: int) -> dict[str, Any]:
    roots = sorted({point[0] for point in factors if point is not None})
    sources = []
    for index, point in enumerate(factors):
        if point is None:
            raise AssertionError("factor base contains identity")
        x, y = point
        smaller_y = min(y, (-y) % CURVE_P)
        sources.append(
            {
                "factor_index": index,
                "root_index": roots.index(x),
                "x": x,
                "sign_bit": 0 if y == smaller_y else 1,
                "y": y,
                "point": [x, y],
                "source_tag": f"x={x}|y={y}",
            }
        )
    return {
        "B": size,
        "L_roots": roots,
        "L_polynomial_coefficients_ascending_mod_p": polynomial_from_roots_mod_p(
            roots, CURVE_P
        ),
        "labels": [point_registry_text(point) for point in factors],
        "canonical_sources": sources,
        "discarded_source_tags": [],
        "source_gate": {"valid": True, "counterexample": None},
    }


def all_formal_multisets(prime_count: int, maximum_degree: int) -> list[Formal]:
    result: list[Formal] = []
    for degree in range(maximum_degree + 1):
        result.extend(itertools.combinations_with_replacement(range(prime_count), degree))
    return result


def submultisets(formal: Formal) -> set[Formal]:
    counts = Counter(formal)
    primes = sorted(counts)
    result: set[Formal] = set()
    for exponents in itertools.product(*(range(counts[p] + 1) for p in primes)):
        expanded: list[int] = []
        for prime, exponent in zip(primes, exponents):
            expanded.extend([prime] * exponent)
        result.add(tuple(expanded))
    if not primes:
        result.add(())
    return result


def base_order_ideal(prime_count: int) -> set[Formal]:
    return {(), *((index,) for index in range(prime_count))}


def candidate_order_ideal(prime_count: int, formal: Formal) -> set[Formal]:
    return base_order_ideal(prime_count) | submultisets(formal)


def selected_order_ideal(prime_count: int, selected: Iterable[Formal]) -> set[Formal]:
    family = base_order_ideal(prime_count)
    for formal in selected:
        family.update(submultisets(formal))
    return family


def eval_ec_formal(curve: Curve, factors: Sequence[Point], formal: Formal) -> Point:
    result: Point = None
    for index in formal:
        result = curve.add(result, factors[index])
    return result


def normalized_collision_pair(left: Formal, right: Formal) -> tuple[Formal, Formal]:
    if left == right:
        raise ValueError("a collision requires two distinct formal multisets")
    if not left or not right:
        return (left, right) if not left else (right, left)
    if (len(left) == 1) != (len(right) == 1):
        return (left, right) if len(left) == 1 else (right, left)
    left_key = (len(left), left)
    right_key = (len(right), right)
    return (left, right) if left_key <= right_key else (right, left)


def collision_kind(left: Formal, right: Formal) -> str:
    if (not left) != (not right):
        return "nonempty_identity"
    if (len(left) == 1) != (len(right) == 1):
        return "singleton_composite"
    if len(left) == len(right):
        return "same_degree"
    return "cross_degree"


def evaluation_collisions(
    family: Iterable[Formal], eval_fn: Callable[[Formal], Hashable]
) -> list[tuple[Formal, Formal, Hashable, str]]:
    buckets: dict[Hashable, list[Formal]] = defaultdict(list)
    for formal in sorted(set(family), key=lambda item: (len(item), item)):
        buckets[eval_fn(formal)].append(formal)
    collisions: list[tuple[Formal, Formal, Hashable, str]] = []
    for output, formals in buckets.items():
        if len(formals) < 2:
            continue
        for raw_left, raw_right in itertools.combinations(formals, 2):
            left, right = normalized_collision_pair(raw_left, raw_right)
            collisions.append((left, right, output, collision_kind(left, right)))
    collisions.sort(key=lambda item: (len(item[0]), item[0], len(item[1]), item[1]))
    return collisions


def collision_json(
    collision: tuple[Formal, Formal, Hashable, str],
    encode_output: Callable[[Hashable], Any],
) -> dict[str, Any]:
    left, right, output, kind = collision
    return {
        "kind": kind,
        "left": list(left),
        "right": list(right),
        "point": encode_output(output),
    }


def serialize_family(family: Iterable[Formal], maximum_degree: int = 4) -> dict[str, Any]:
    unique = sorted(set(family), key=lambda item: (len(item), item))
    by_degree: dict[str, list[list[int]]] = {}
    counts: dict[str, int] = {}
    for degree in range(maximum_degree + 1):
        members = [list(item) for item in unique if len(item) == degree]
        by_degree[str(degree)] = members
        counts[str(degree)] = len(members)
    return {
        "formal_multisets_by_degree": by_degree,
        "counts_by_degree": counts,
        "total_count": len(unique),
    }


def multiplicity_histogram(groups: Mapping[Hashable, Sequence[Any]]) -> dict[str, int]:
    histogram = Counter(len(items) for items in groups.values())
    return {str(multiplicity): histogram[multiplicity] for multiplicity in sorted(histogram)}


@dataclass
class RawWitnessData:
    raw2: list[Formal]
    canonical2: list[Formal]
    degree2_groups: dict[Point, list[Formal]]
    u4: list[Formal]
    parent_pairs: dict[Formal, list[tuple[Formal, Formal]]]
    canonical4: list[Formal]
    degree4_groups: dict[Point, list[Formal]]
    serialized: dict[str, Any]
    candidate_universe_sha256: str


def build_raw_witness_data(curve: Curve, factors: Sequence[Point]) -> RawWitnessData:
    size = len(factors)
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    raw2 = list(itertools.combinations_with_replacement(range(size), 2))
    degree2_groups: dict[Point, list[Formal]] = defaultdict(list)
    for formal in raw2:
        degree2_groups[evaluate(formal)].append(formal)
    for witnesses in degree2_groups.values():
        witnesses.sort()
    canonical2 = sorted(
        min(witnesses)
        for output, witnesses in degree2_groups.items()
        if output is not None
    )

    parent_pairs: dict[Formal, list[tuple[Formal, Formal]]] = defaultdict(list)
    for left_index, left in enumerate(canonical2):
        for right in canonical2[left_index:]:
            formal = tuple(sorted(left + right))
            parent_pairs[formal].append((left, right))
    for pairs in parent_pairs.values():
        pairs.sort()
    u4 = sorted(parent_pairs)

    degree4_groups: dict[Point, list[Formal]] = defaultdict(list)
    for formal in u4:
        degree4_groups[evaluate(formal)].append(formal)
    for witnesses in degree4_groups.values():
        witnesses.sort()
    canonical4 = sorted(
        min(witnesses)
        for output, witnesses in degree4_groups.items()
        if output is not None
    )

    canonical2_records: list[dict[str, Any]] = []
    for formal in canonical2:
        output = evaluate(formal)
        witnesses = degree2_groups[output]
        canonical2_records.append(
            {
                "formal_multiset": list(formal),
                "output": point_json(output),
                "alternates": [list(item) for item in witnesses if item != formal],
                "raw_witness_count_for_output": len(witnesses),
            }
        )

    candidate_records: list[dict[str, Any]] = []
    for formal in u4:
        candidate_records.append(
            {
                "formal_multiset": list(formal),
                "output": point_json(evaluate(formal)),
                "parent_pairs": [
                    [list(left), list(right)] for left, right in parent_pairs[formal]
                ],
            }
        )

    canonical4_records: list[dict[str, Any]] = []
    for formal in canonical4:
        output = evaluate(formal)
        witnesses = degree4_groups[output]
        canonical4_records.append(
            {
                "formal_multiset": list(formal),
                "output": point_json(output),
                "alternates": [list(item) for item in witnesses if item != formal],
                "balanced_parent_pairs": [
                    [list(left), list(right)]
                    for left, right in parent_pairs[formal]
                ],
                "raw_witness_count_for_output": len(witnesses),
            }
        )

    serialized = {
        "degree2": {
            "all_unordered_multisets": [list(item) for item in raw2],
            "witness_count": len(raw2),
            "identity_witnesses": [
                list(item) for item in degree2_groups.get(None, [])
            ],
            "canonical_nonidentity_nodes": canonical2_records,
            "canonical_nonidentity_node_count": len(canonical2),
            "semantic_output_count": len(degree2_groups),
            "output_multiplicity_histogram": multiplicity_histogram(degree2_groups),
        },
        "balanced_degree4": {
            "candidate_universe": candidate_records,
            "candidate_count": len(u4),
            "balanced_parent_pair_count": sum(
                len(parent_pairs[item]) for item in u4
            ),
            "identity_candidates": [
                list(item) for item in degree4_groups.get(None, [])
            ],
            "canonical_nonidentity_nodes": canonical4_records,
            "canonical_nonidentity_node_count": len(canonical4),
            "semantic_output_count": len(degree4_groups),
            "output_multiplicity_histogram": multiplicity_histogram(degree4_groups),
        },
    }
    universe_sha256 = digest_json([list(item) for item in u4])
    return RawWitnessData(
        raw2=raw2,
        canonical2=canonical2,
        degree2_groups=dict(degree2_groups),
        u4=u4,
        parent_pairs=dict(parent_pairs),
        canonical4=canonical4,
        degree4_groups=dict(degree4_groups),
        serialized=serialized,
        candidate_universe_sha256=universe_sha256,
    )


def builder_candidate_universe(
    curve: Curve, factors: Sequence[Point], raw: RawWitnessData
) -> list[dict[str, Any]]:
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    return [
        {
            "index": index,
            "multiset": list(formal),
            "point": point_registry_text(evaluate(formal)),
            "parent_pairs": [
                [list(left), list(right)] for left, right in raw.parent_pairs[formal]
            ],
        }
        for index, formal in enumerate(raw.u4)
    ]


def builder_raw_witness_json(
    curve: Curve, factors: Sequence[Point], raw: RawWitnessData
) -> dict[str, Any]:
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    canonical2_records = []
    canonical2_by_output: list[tuple[Point, Formal]] = []
    for output in sorted(raw.degree2_groups, key=point_sort_key):
        if output is None:
            continue
        canonical2_by_output.append((output, min(raw.degree2_groups[output])))
    for output, formal in canonical2_by_output:
        witnesses = sorted(raw.degree2_groups[output])
        canonical2_records.append(
            {
                "point": point_registry_text(output),
                "multiset": list(formal),
                "alternate_multisets": [list(value) for value in witnesses[1:]],
            }
        )

    raw4_by_output: dict[Point, list[tuple[Formal, tuple[Formal, Formal]]]] = defaultdict(list)
    for formal in raw.u4:
        output = evaluate(formal)
        for parents in raw.parent_pairs[formal]:
            raw4_by_output[output].append((formal, parents))
    for witnesses in raw4_by_output.values():
        witnesses.sort(key=lambda item: (item[0], item[1]))

    canonical4_records = []
    alternate_degree4_count = 0
    for output in sorted(raw4_by_output, key=point_sort_key):
        if output is None:
            continue
        witnesses = raw4_by_output[output]
        formal, parents = witnesses[0]
        alternatives = witnesses[1:]
        alternate_degree4_count += len(alternatives)
        canonical4_records.append(
            {
                "point": point_registry_text(output),
                "multiset": list(formal),
                "parents": [list(parent) for parent in parents],
                "alternate_witnesses": [
                    {
                        "multiset": list(other_formal),
                        "parents": [list(parent) for parent in other_parents],
                    }
                    for other_formal, other_parents in alternatives
                ],
            }
        )

    degree2_histogram = Counter(
        len(values) for values in raw.degree2_groups.values()
    )
    degree4_histogram = Counter(len(values) for values in raw4_by_output.values())
    universe = builder_candidate_universe(curve, factors, raw)
    semantic_outputs = {evaluate(formal) for formal in raw.u4}
    return {
        "degree2_count": len(raw.raw2),
        "degree4_count": sum(len(values) for values in raw.parent_pairs.values()),
        "canonical_degree2_count": len(raw.canonical2),
        "canonical_degree4_count": len(raw.canonical4),
        "balanced_degree4_candidate_count": len(raw.u4),
        "multiplicity_histograms": {
            "degree2": {
                str(key): degree2_histogram[key] for key in sorted(degree2_histogram)
            },
            "degree4": {
                str(key): degree4_histogram[key] for key in sorted(degree4_histogram)
            },
        },
        "support_sizes": {
            "degree2_including_identity": len(raw.degree2_groups),
            "degree2_nonidentity": len(raw.canonical2),
            "degree4_including_identity": len(semantic_outputs),
            "degree4_nonidentity": sum(point is not None for point in semantic_outputs),
        },
        "degree2_identity_witnesses": [
            list(formal) for formal in sorted(raw.degree2_groups.get(None, []))
        ],
        "canonical_degree2": canonical2_records,
        "canonical_degree4": canonical4_records,
        "balanced_candidate_universe": universe,
        "balanced_candidate_universe_sha256": digest_json(universe),
        "p1_alternate_degree2_discarded": sum(
            len(values) - 1
            for output, values in raw.degree2_groups.items()
            if output is not None
        ),
        "p1_alternate_degree4_witness_count": alternate_degree4_count,
        "balanced_parent_pair_count": sum(
            len(values) for values in raw.parent_pairs.values()
        ),
        "balanced_parent_pair_multiplicity_histogram": multiplicity_histogram(
            raw.parent_pairs
        ),
    }


@dataclass
class StarModel:
    labels: list[Hashable]
    identity_index: int
    edges: dict[tuple[int, int], int]
    degree_sets: dict[int, set[int]]

    def __post_init__(self) -> None:
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("star labels must be unique")
        if not (0 <= self.identity_index < len(self.labels)):
            raise ValueError("identity index outside label space")
        for (left, right), output in self.edges.items():
            if left > right:
                raise ValueError("star edge keys must be unordered/canonical")
            if self.identity_index in (left, right):
                raise ValueError("nonidentity edge map contains identity")
            if not all(0 <= item < len(self.labels) for item in (left, right, output)):
                raise ValueError("star edge references an unknown label")

    def call_index(self, left: int, right: int) -> int | None:
        if left == self.identity_index:
            return right
        if right == self.identity_index:
            return left
        return self.edges.get(canonical_pair_indices(left, right))

    def ordered_nonidentity_domain_count(self) -> int:
        return sum(1 if left == right else 2 for left, right in self.edges)

    def ordered_domain_count(self) -> int:
        identity_entries = 2 * len(self.labels) - 1
        return identity_entries + self.ordered_nonidentity_domain_count()


def build_star_from_family(
    labels: Sequence[Hashable],
    identity: Hashable,
    family: Iterable[Formal],
    eval_fn: Callable[[Formal], Hashable],
) -> StarModel:
    label_list = list(labels)
    index_by_label = {label: index for index, label in enumerate(label_list)}
    if identity not in index_by_label:
        raise ValueError("identity is absent from label space")
    formal_family = set(family)
    evaluation: dict[Formal, Hashable] = {}
    inverse: dict[Hashable, Formal] = {}
    for formal in formal_family:
        output = eval_fn(formal)
        if output not in index_by_label:
            raise ValueError("formal evaluation is absent from label space")
        if output in inverse and inverse[output] != formal:
            raise ValueError("cannot construct star from noninjective formal family")
        evaluation[formal] = output
        inverse[output] = formal
    if evaluation.get(()) != identity:
        raise ValueError("empty formal multiset does not evaluate to identity")

    nonempty = sorted(
        [formal for formal in formal_family if formal],
        key=lambda item: (len(item), item),
    )
    edges: dict[tuple[int, int], int] = {}
    for left_index, left in enumerate(nonempty):
        for right in nonempty[left_index:]:
            union = tuple(sorted(left + right))
            if union not in formal_family:
                continue
            left_label = index_by_label[evaluation[left]]
            right_label = index_by_label[evaluation[right]]
            output_label = index_by_label[evaluation[union]]
            key = canonical_pair_indices(left_label, right_label)
            previous = edges.get(key)
            if previous is not None and previous != output_label:
                raise AssertionError("formal union assigned two outputs to one star edge")
            edges[key] = output_label

    degree_sets: dict[int, set[int]] = defaultdict(set)
    for formal, output in evaluation.items():
        degree_sets[index_by_label[output]].add(len(formal))
    return StarModel(
        labels=label_list,
        identity_index=index_by_label[identity],
        edges=edges,
        degree_sets=dict(degree_sets),
    )


def build_star_from_explicit_edges(
    labels: Sequence[Hashable],
    identity: Hashable,
    explicit_edges: Iterable[tuple[Hashable, Hashable, Hashable]],
    degree_sets_by_label: Mapping[Hashable, set[int]] | None = None,
) -> StarModel:
    label_list = list(labels)
    index_by_label = {label: index for index, label in enumerate(label_list)}
    edges: dict[tuple[int, int], int] = {}
    for left, right, output in explicit_edges:
        key = canonical_pair_indices(index_by_label[left], index_by_label[right])
        output_index = index_by_label[output]
        previous = edges.get(key)
        if previous is not None and previous != output_index:
            raise ValueError("explicit star edge has two distinct outputs")
        edges[key] = output_index
    degree_sets: dict[int, set[int]] = {}
    if degree_sets_by_label is not None:
        degree_sets = {
            index_by_label[label]: set(degrees)
            for label, degrees in degree_sets_by_label.items()
        }
    return StarModel(
        labels=label_list,
        identity_index=index_by_label[identity],
        edges=edges,
        degree_sets=degree_sets,
    )


def serialize_star(
    model: StarModel, encode_label: Callable[[Hashable], Any]
) -> dict[str, Any]:
    edge_rows: list[dict[str, Any]] = []
    for (left, right), output in sorted(model.edges.items()):
        edge_rows.append(
            {
                "left": encode_label(model.labels[left]),
                "right": encode_label(model.labels[right]),
                "output": encode_label(model.labels[output]),
            }
        )
    return {
        "identity_edges_implicit": True,
        "unordered_nonidentity_edges": edge_rows,
        "unordered_nonidentity_edge_count": len(edge_rows),
        "ordered_nonidentity_domain_entry_count": (
            model.ordered_nonidentity_domain_count()
        ),
        "ordered_domain_entry_count": model.ordered_domain_count(),
        "edge_table_sha256": digest_json(edge_rows),
    }


def constrained_indices(model: StarModel) -> tuple[set[int], set[int], set[int]]:
    first_clause: set[int] = set()
    second_clause: set[int] = set()
    if len(model.labels) > 1:
        first_clause.add(model.identity_index)
    for (left, right), output in model.edges.items():
        first_clause.add(left)
        first_clause.add(right)
        if left != output and right != output:
            second_clause.add(output)
    return first_clause | second_clause, first_clause, second_clause


def serialize_constrained(
    model: StarModel, encode_label: Callable[[Hashable], Any]
) -> dict[str, Any]:
    constrained, first_clause, second_clause = constrained_indices(model)
    overlap = first_clause & second_clause
    by_degree: Counter[str] = Counter()
    for label_index in constrained:
        degrees = model.degree_sets.get(label_index)
        if not degrees:
            by_degree["outside_formal_family"] += 1
        elif len(degrees) == 1:
            by_degree[str(next(iter(degrees)))] += 1
        else:
            by_degree["semantic_degree_overlap"] += 1
    possible_nonidentity_edges = (len(model.labels) - 1) * len(model.labels) // 2
    return {
        "labels": [
            encode_label(model.labels[index]) for index in sorted(constrained)
        ],
        "count": len(constrained),
        "delta": ratio(len(constrained), len(model.labels)),
        "first_clause_count": len(first_clause),
        "second_clause_count": len(second_clause),
        "clause_overlap_count": len(overlap),
        "role_counts_by_formal_degree": {
            key: by_degree[key] for key in sorted(by_degree)
        },
        "edges_per_constrained_label": ratio(
            len(model.edges), max(1, len(constrained))
        ),
        "normalized_nonidentity_edge_density": ratio(
            len(model.edges), max(1, possible_nonidentity_edges)
        ),
    }


def _reduction_graph(model: StarModel) -> dict[int, list[tuple[int, int]]]:
    parents: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (left, right), output in sorted(model.edges.items()):
        if left != output and right != output:
            parents[output].append((left, right))
    return dict(parents)


def _acyclic_reduced(
    model: StarModel, parents: Mapping[int, Sequence[tuple[int, int]]]
) -> tuple[bool, list[int] | None]:
    state = [0] * len(model.labels)
    stack: list[int] = []

    def visit(label: int) -> list[int] | None:
        if state[label] == 2:
            return None
        if state[label] == 1:
            start = stack.index(label)
            return stack[start:] + [label]
        state[label] = 1
        stack.append(label)
        for left, right in parents.get(label, ()):
            for child in (left, right):
                cycle = visit(child)
                if cycle is not None:
                    return cycle
        stack.pop()
        state[label] = 2
        return None

    for index in range(len(model.labels)):
        cycle = visit(index)
        if cycle is not None:
            return False, cycle
    return True, None


def _unique_factorizations(
    model: StarModel, parents: Mapping[int, Sequence[tuple[int, int]]]
) -> tuple[bool, tuple[int, set[tuple[int, ...]]] | None]:
    memo: dict[int, set[tuple[int, ...]]] = {}
    active: set[int] = set()

    def recurse(label: int) -> set[tuple[int, ...]]:
        if label in memo:
            return memo[label]
        if label in active:
            return set()
        if label == model.identity_index:
            memo[label] = {()}
            return memo[label]
        reductions = parents.get(label, ())
        if not reductions:
            memo[label] = {(label,)}
            return memo[label]
        active.add(label)
        factorizations: set[tuple[int, ...]] = set()
        for left, right in reductions:
            for left_factors in recurse(left):
                for right_factors in recurse(right):
                    factorizations.add(tuple(sorted(left_factors + right_factors)))
        active.remove(label)
        memo[label] = factorizations
        return factorizations

    for label in range(len(model.labels)):
        factorizations = recurse(label)
        if len(factorizations) != 1:
            return False, (label, factorizations)
    return True, None


def check_axioms(
    model: StarModel,
    encode_label: Callable[[Hashable], Any],
    *,
    evaluation_injective: bool,
    source_gate: bool | None,
    coordinate_add: Callable[[Hashable, Hashable], Hashable] | None,
    scalar_by_label: Mapping[Hashable, int] | None,
    scalar_modulus: int | None,
    final_input_degree: int = 4,
    optimizer_exact: bool | None = None,
) -> dict[str, Any]:
    counterexamples: dict[str, Any] = {key: None for key in PREDICATE_ORDER}

    identity_ok = True
    for label in range(len(model.labels)):
        if model.call_index(model.identity_index, label) != label:
            identity_ok = False
            counterexamples["identity"] = {
                "side": "left",
                "label": encode_label(model.labels[label]),
            }
            break
        if model.call_index(label, model.identity_index) != label:
            identity_ok = False
            counterexamples["identity"] = {
                "side": "right",
                "label": encode_label(model.labels[label]),
            }
            break
    if identity_ok:
        for (left, right), output in sorted(model.edges.items()):
            if output == model.identity_index:
                identity_ok = False
                counterexamples["identity"] = {
                    "nonidentity_inputs": [
                        encode_label(model.labels[left]),
                        encode_label(model.labels[right]),
                    ],
                    "output": encode_label(model.labels[output]),
                }
                break

    commutative_ok = True
    for left in range(len(model.labels)):
        for right in range(len(model.labels)):
            if model.call_index(left, right) != model.call_index(right, left):
                commutative_ok = False
                counterexamples["commutativity"] = {
                    "left": encode_label(model.labels[left]),
                    "right": encode_label(model.labels[right]),
                }
                break
        if not commutative_ok:
            break

    associative_ok = True
    for left in range(len(model.labels)):
        if not associative_ok:
            break
        for middle in range(len(model.labels)):
            if not associative_ok:
                break
            for right in range(len(model.labels)):
                left_inner = model.call_index(left, middle)
                left_outer = (
                    None
                    if left_inner is None
                    else model.call_index(left_inner, right)
                )
                right_inner = model.call_index(middle, right)
                right_outer = (
                    None
                    if right_inner is None
                    else model.call_index(left, right_inner)
                )
                if (left_outer is None) != (right_outer is None) or (
                    left_outer is not None and left_outer != right_outer
                ):
                    associative_ok = False
                    counterexamples["associativity"] = {
                        "triple": [
                            encode_label(model.labels[left]),
                            encode_label(model.labels[middle]),
                            encode_label(model.labels[right]),
                        ],
                        "left_inner": (
                            None
                            if left_inner is None
                            else encode_label(model.labels[left_inner])
                        ),
                        "left_outer": (
                            None
                            if left_outer is None
                            else encode_label(model.labels[left_outer])
                        ),
                        "right_inner": (
                            None
                            if right_inner is None
                            else encode_label(model.labels[right_inner])
                        ),
                        "right_outer": (
                            None
                            if right_outer is None
                            else encode_label(model.labels[right_outer])
                        ),
                    }
                    break

    coordinate_ok: bool | None = None
    if coordinate_add is not None:
        coordinate_ok = True
        for left in range(len(model.labels)):
            if not coordinate_ok:
                break
            for right in range(len(model.labels)):
                output = model.call_index(left, right)
                if output is None:
                    continue
                expected_output = coordinate_add(
                    model.labels[left], model.labels[right]
                )
                if model.labels[output] != expected_output:
                    coordinate_ok = False
                    counterexamples["compatibility_coordinates"] = {
                        "inputs": [
                            encode_label(model.labels[left]),
                            encode_label(model.labels[right]),
                        ],
                        "stored_output": encode_label(model.labels[output]),
                        "independent_sum": encode_label(expected_output),
                    }
                    break

    scalar_ok: bool | None = None
    if scalar_by_label is not None:
        if scalar_modulus is None:
            raise ValueError("scalar modulus required with scalar ground truth")
        scalar_ok = True
        for left in range(len(model.labels)):
            if not scalar_ok:
                break
            for right in range(len(model.labels)):
                output = model.call_index(left, right)
                if output is None:
                    continue
                left_label = model.labels[left]
                right_label = model.labels[right]
                output_label = model.labels[output]
                expected_scalar = (
                    scalar_by_label[left_label] + scalar_by_label[right_label]
                ) % scalar_modulus
                if scalar_by_label[output_label] != expected_scalar:
                    scalar_ok = False
                    counterexamples["compatibility_scalars"] = {
                        "inputs": [
                            encode_label(left_label),
                            encode_label(right_label),
                        ],
                        "stored_output": encode_label(output_label),
                        "stored_output_scalar": scalar_by_label[output_label],
                        "expected_output_scalar": expected_scalar,
                    }
                    break

    parents = _reduction_graph(model)
    acyclic_ok, cycle = _acyclic_reduced(model, parents)
    if not acyclic_ok and cycle is not None:
        counterexamples["acyclic_reduced"] = {
            "cycle": [encode_label(model.labels[index]) for index in cycle]
        }
    unique_ok, unique_failure = _unique_factorizations(model, parents)
    if not unique_ok and unique_failure is not None:
        failed_label, factorizations = unique_failure
        counterexamples["unique_factorization"] = {
            "label": encode_label(model.labels[failed_label]),
            "prime_multisets": [
                [encode_label(model.labels[index]) for index in factorization]
                for factorization in sorted(factorizations)
            ],
        }

    direct_final_ok = True
    for left, right in sorted(model.edges):
        if final_input_degree in model.degree_sets.get(left, set()) and (
            final_input_degree in model.degree_sets.get(right, set())
        ):
            direct_final_ok = False
            output = model.edges[(left, right)]
            counterexamples["direct_final_edge_excluded"] = {
                "inputs": [
                    encode_label(model.labels[left]),
                    encode_label(model.labels[right]),
                ],
                "output": encode_label(model.labels[output]),
                "edge_degrees": [
                    final_input_degree,
                    final_input_degree,
                    max(model.degree_sets.get(output, {0})),
                ],
            }
            break

    predicates = {
        "source_gate": NA if source_gate is None else status(source_gate),
        "evaluation_injective": status(evaluation_injective),
        "identity": status(identity_ok),
        "commutativity": status(commutative_ok),
        "associativity": status(associative_ok),
        "compatibility_coordinates": (
            NA if coordinate_ok is None else status(coordinate_ok)
        ),
        "compatibility_scalars": NA if scalar_ok is None else status(scalar_ok),
        "unique_factorization": status(unique_ok),
        "acyclic_reduced": status(acyclic_ok),
        "direct_final_edge_excluded": status(direct_final_ok),
        "optimizer_exact": NA if optimizer_exact is None else status(optimizer_exact),
    }
    return {"predicates": predicates, "counterexamples": counterexamples}


def rejected_embedding_axioms(
    source_gate: bool,
    collision: dict[str, Any] | None,
) -> dict[str, Any]:
    predicates = {key: NA for key in PREDICATE_ORDER}
    predicates["source_gate"] = status(source_gate)
    predicates["evaluation_injective"] = FALSE
    counterexamples = {key: None for key in PREDICATE_ORDER}
    counterexamples["evaluation_injective"] = collision
    return {"predicates": predicates, "counterexamples": counterexamples}


def replace_scalar_predicate_with_placeholder(axioms: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(axioms)
    scalar_value = result["predicates"].get("compatibility_scalars")
    if scalar_value in (TRUE, FALSE):
        result["predicates"]["compatibility_scalars"] = VERIFIER_ONLY
        result["counterexamples"]["compatibility_scalars"] = None
    return result


def degree_sets_for_family(
    family: Iterable[Formal],
    eval_fn: Callable[[Formal], Hashable],
    labels: Sequence[Hashable],
) -> dict[int, set[int]]:
    index_by_label = {label: index for index, label in enumerate(labels)}
    result: dict[int, set[int]] = defaultdict(set)
    for formal in family:
        result[index_by_label[eval_fn(formal)]].add(len(formal))
    return dict(result)


def builder_collision_kind(left: Formal, right: Formal, point: Point) -> str:
    if point is None:
        return "nonempty_identity"
    if 1 in (len(left), len(right)):
        return "singleton_composite"
    if len(left) == len(right):
        return f"same_degree_{len(left)}"
    return f"cross_degree_{min(len(left), len(right))}_{max(len(left), len(right))}"


def builder_family_state(
    curve: Curve, factors: Sequence[Point], family: Iterable[Formal]
) -> tuple[dict[Formal, Point], list[dict[str, Any]]]:
    evaluations: dict[Formal, Point] = {}
    buckets: dict[Point, list[Formal]] = defaultdict(list)
    for formal in sorted(set(family), key=lambda item: (len(item), item)):
        output = eval_ec_formal(curve, factors, formal)
        evaluations[formal] = output
        buckets[output].append(formal)
    collisions: list[dict[str, Any]] = []
    for output in sorted(buckets, key=point_sort_key):
        for left, right in itertools.combinations(buckets[output], 2):
            collisions.append(
                {
                    "kind": builder_collision_kind(left, right, output),
                    "left": list(left),
                    "right": list(right),
                    "point": point_registry_text(output),
                }
            )
    return evaluations, collisions


def builder_formal_family_json(
    family: Iterable[Formal],
    evaluations: Mapping[Formal, Point],
    collisions: Sequence[dict[str, Any]],
    maxima: Iterable[Formal],
    *,
    sort_maxima: bool = True,
) -> dict[str, Any]:
    family_set = set(family)
    maxima_values = list(maxima)
    if sort_maxima:
        maxima_values = sorted(set(maxima_values))
    return {
        "downward_closure_by_degree": {
            str(degree): [
                list(item)
                for item in sorted(value for value in family_set if len(value) == degree)
            ]
            for degree in range(5)
        },
        "evaluation_map": [
            {
                "multiset": list(item),
                "point": point_registry_text(evaluations[item]),
            }
            for item in sorted(family_set, key=lambda value: (len(value), value))
        ],
        "evaluation_injective": not collisions,
        "evaluation_collisions": list(collisions),
        "maximal_multisets": [list(item) for item in maxima_values],
    }


def builder_edge_rows(model: StarModel) -> list[list[str]]:
    return [
        [
            point_registry_text(model.labels[left]),
            point_registry_text(model.labels[right]),
            point_registry_text(model.labels[output]),
        ]
        for (left, right), output in sorted(model.edges.items())
    ]


def builder_star_json(model: StarModel) -> dict[str, Any]:
    edge_rows = builder_edge_rows(model)
    ordered_rows: list[list[str]] = []
    for left in range(len(model.labels)):
        for right in range(len(model.labels)):
            output = model.call_index(left, right)
            if output is not None:
                ordered_rows.append(
                    [
                        point_registry_text(model.labels[left]),
                        point_registry_text(model.labels[right]),
                        point_registry_text(model.labels[output]),
                    ]
                )
    return {
        "identity_rule_total": True,
        "unordered_nonidentity_edges": edge_rows,
        "ordered_domain_sha256": digest_json(ordered_rows),
        "ordered_domain_entries": len(ordered_rows),
        "description_bits": 8 * len(canonical_json_bytes(edge_rows)),
    }


def builder_factorization_json(model: StarModel) -> dict[str, Any]:
    encoded = [point_registry_text(label) for label in model.labels]
    parents: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for (left, right), output in model.edges.items():
        left_label, right_label, output_label = encoded[left], encoded[right], encoded[output]
        if left_label != output_label and right_label != output_label:
            parents[output_label].add(tuple(sorted((left_label, right_label))))
    identity = encoded[model.identity_index]
    primes = sorted(label for label in encoded if label != identity and not parents[label])
    facts: dict[str, set[tuple[str, ...]]] = {identity: {()}}
    for prime in primes:
        facts[prime] = {(prime,)}
    changed = True
    rounds = 0
    while changed and rounds <= len(encoded):
        changed = False
        rounds += 1
        for output, pairs in parents.items():
            output_set = facts.setdefault(output, set())
            before = len(output_set)
            for left, right in pairs:
                for left_factors in facts.get(left, set()):
                    for right_factors in facts.get(right, set()):
                        output_set.add(tuple(sorted(left_factors + right_factors)))
                        if len(output_set) > 64:
                            break
                    if len(output_set) > 64:
                        break
                if len(output_set) > 64:
                    break
            changed |= len(output_set) != before
    failures = []
    for label in encoded:
        values = facts.get(label, set())
        if len(values) != 1:
            failures.append(
                {
                    "label": label,
                    "factorization_count": len(values),
                    "prime_multisets": [list(value) for value in sorted(values)[:8]],
                    "truncated": len(values) > 8,
                }
            )
    return {
        "valid": not failures,
        "prime_labels": primes,
        "prime_count": len(primes),
        "failures": failures,
        "fixed_point_rounds": rounds,
    }


def builder_acyclic_json(model: StarModel) -> dict[str, Any]:
    adjacency: dict[int, set[int]] = defaultdict(set)
    for (left, right), output in model.edges.items():
        adjacency[left].add(output)
        adjacency[right].add(output)
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(label: int, path: list[int]) -> list[int] | None:
        if label in visiting:
            start = path.index(label)
            return path[start:] + [label]
        if label in visited:
            return None
        visiting.add(label)
        path.append(label)
        for child in sorted(
            adjacency[label], key=lambda index: point_registry_text(model.labels[index])
        ):
            cycle = visit(child, path)
            if cycle is not None:
                return cycle
        path.pop()
        visiting.remove(label)
        visited.add(label)
        return None

    for label in range(len(model.labels)):
        cycle = visit(label, [])
        if cycle is not None:
            return {
                "valid": False,
                "cycle": [point_registry_text(model.labels[index]) for index in cycle],
            }
    return {"valid": True, "cycle": None}


def builder_canonical4_order(raw: RawWitnessData) -> list[Formal]:
    return [
        min(raw.degree4_groups[output])
        for output in sorted(raw.degree4_groups, key=point_sort_key)
        if output is not None
    ]


def builder_axioms_json(
    model: StarModel,
    curve: Curve,
    scalar_by_point: Mapping[Point, int],
    final_labels: set[Point],
) -> tuple[dict[str, Any], bool]:
    identity_failures = []
    for index, label in enumerate(model.labels):
        if (
            model.call_index(model.identity_index, index) != index
            or model.call_index(index, model.identity_index) != index
        ):
            identity_failures.append(point_registry_text(label))
    to_identity = [row for row in builder_edge_rows(model) if row[2] == "O"]

    comm_failure = None
    for left in range(len(model.labels)):
        for right in range(len(model.labels)):
            if model.call_index(left, right) != model.call_index(right, left):
                comm_failure = [
                    point_registry_text(model.labels[left]),
                    point_registry_text(model.labels[right]),
                ]
                break
        if comm_failure is not None:
            break

    assoc_counterexample = None
    checked = 0
    for left, middle, right in itertools.product(range(len(model.labels)), repeat=3):
        checked += 1
        left_inner = model.call_index(left, middle)
        left_outer = None if left_inner is None else model.call_index(left_inner, right)
        right_inner = model.call_index(middle, right)
        right_outer = None if right_inner is None else model.call_index(left, right_inner)
        if (left_outer is None) != (right_outer is None) or (
            left_outer is not None and left_outer != right_outer
        ):
            encode_index = lambda index: (
                None if index is None else point_registry_text(model.labels[index])
            )
            assoc_counterexample = {
                "triple": [
                    point_registry_text(model.labels[left]),
                    point_registry_text(model.labels[middle]),
                    point_registry_text(model.labels[right]),
                ],
                "left_inner": encode_index(left_inner),
                "left_outer": encode_index(left_outer),
                "right_inner": encode_index(right_inner),
                "right_outer": encode_index(right_outer),
            }
            break

    coordinate_counterexample = None
    coordinate_checked = 2 * len(model.labels) - 1
    scalar_valid = True
    for (left, right), output in sorted(model.edges.items()):
        coordinate_checked += 1
        expected_point = curve.add(model.labels[left], model.labels[right])
        if model.labels[output] != expected_point and coordinate_counterexample is None:
            coordinate_counterexample = {
                "left": point_registry_text(model.labels[left]),
                "right": point_registry_text(model.labels[right]),
                "stored_output": point_registry_text(model.labels[output]),
                "coordinate_output": point_registry_text(expected_point),
            }
        expected_scalar = (
            scalar_by_point[model.labels[left]] + scalar_by_point[model.labels[right]]
        ) % CURVE_Q
        if scalar_by_point[model.labels[output]] != expected_scalar:
            scalar_valid = False

    final_indices = {
        index for index, label in enumerate(model.labels) if label in final_labels
    }
    forbidden = [
        row
        for ((left, right), _), row in zip(
            sorted(model.edges.items()), builder_edge_rows(model)
        )
        if left in final_indices and right in final_indices
    ]
    factorization = builder_factorization_json(model)
    return (
        {
            "identity": {
                "valid": not identity_failures and not to_identity,
                "failed_labels": identity_failures,
                "nonidentity_products_to_identity": to_identity,
            },
            "commutativity": {
                "valid": comm_failure is None,
                "counterexample": comm_failure,
            },
            "associativity": {
                "valid": assoc_counterexample is None,
                "method": "literal_cubic",
                "checked_triples": checked,
                "counterexample": assoc_counterexample,
            },
            "compatibility_coordinates": {
                "valid": coordinate_counterexample is None,
                "checked_edges": coordinate_checked,
                "counterexample": coordinate_counterexample,
            },
            "compatibility_scalars": {"status": "VERIFIER_ONLY"},
            "unique_prime_multiset_factorization": factorization,
            "binary_tree_multiplicity": {
                "immediate_parent_pairs": {
                    point_registry_text(label): sum(
                        output == index for output in model.edges.values()
                    )
                    for index, label in enumerate(model.labels)
                }
            },
            "acyclic": builder_acyclic_json(model),
            "direct_final_edge_excluded": {
                "valid": not forbidden,
                "forbidden_edges": forbidden,
            },
        },
        scalar_valid,
    )


def builder_role_counts(
    constrained: set[int], model: StarModel, evaluations: Mapping[Formal, Point]
) -> dict[str, int]:
    represented = {
        point_registry_text(point): len(formal) for formal, point in evaluations.items()
    }
    counts: Counter[str] = Counter()
    for index in constrained:
        label = point_registry_text(model.labels[index])
        degree = represented.get(label)
        counts["outside_formal_family" if degree is None else f"degree_{degree}"] += 1
    return dict(sorted(counts.items()))


def builder_constrained_json(
    model: StarModel, evaluations: Mapping[Formal, Point]
) -> dict[str, Any]:
    constrained, _, _ = constrained_indices(model)
    ordered = sorted(constrained)
    return {
        "labels": [point_registry_text(model.labels[index]) for index in ordered],
        "count": len(ordered),
        "delta": ratio(len(ordered), len(model.labels)),
        "role_counts": builder_role_counts(set(ordered), model, evaluations),
        "edge_density": {
            "nonidentity_unordered_edges": len(model.edges),
            "edges_per_constrained_label": ratio(len(model.edges), len(ordered)),
            "normalized_against_unordered_label_pairs": ratio(
                len(model.edges), (len(model.labels) - 1) * len(model.labels) // 2
            ),
        },
    }


def support_and_histogram_independent(
    curve: Curve, points: Sequence[Point]
) -> tuple[set[Point], Counter[Point]]:
    support: set[Point] = set()
    histogram: Counter[Point] = Counter()
    for left_index, left in enumerate(points):
        for right in points[left_index:]:
            output = curve.add(left, right)
            support.add(output)
            histogram[output] += 1
    return support, histogram


def target_witness_map_independent(
    curve: Curve, points: Sequence[Point]
) -> dict[Point, list[list[str]]]:
    witnesses: dict[Point, list[list[str]]] = defaultdict(list)
    ordered_points = sorted(points, key=point_sort_key)
    for left_index, left in enumerate(ordered_points):
        for right in ordered_points[left_index:]:
            output = curve.add(left, right)
            witnesses[output].append(
                [point_registry_text(left), point_registry_text(right)]
            )
    return dict(witnesses)


def builder_retention_json(
    curve: Curve,
    raw_support: set[Point],
    raw_histogram: Counter[Point],
    retained_support: set[Point],
    retained_histogram: Counter[Point],
    raw_points: Sequence[Point],
    retained_points: Sequence[Point],
) -> dict[str, Any]:
    raw_witnesses = target_witness_map_independent(curve, raw_points)
    retained_witnesses = target_witness_map_independent(curve, retained_points)
    return {
        "pair_convention": "unordered_with_replacement",
        "raw_final_support": len(raw_support),
        "retained_final_support": len(retained_support),
        "support_ratio": ratio(len(retained_support), len(raw_support) or 1),
        "raw_absolute_group_coverage": ratio(len(raw_support), CURVE_Q),
        "retained_absolute_group_coverage": ratio(len(retained_support), CURVE_Q),
        "raw_target_witness_histogram": {
            str(key): value
            for key, value in sorted(Counter(raw_histogram.values()).items())
        },
        "retained_target_witness_histogram": {
            str(key): value
            for key, value in sorted(Counter(retained_histogram.values()).items())
        },
        "raw_target_witness_counts": {
            point_registry_text(point): raw_histogram[point]
            for point in sorted(raw_histogram, key=point_sort_key)
        },
        "retained_target_witness_counts": {
            point_registry_text(point): retained_histogram[point]
            for point in sorted(retained_histogram, key=point_sort_key)
        },
        "raw_target_witness_map": {
            point_registry_text(point): raw_witnesses[point]
            for point in sorted(raw_witnesses, key=point_sort_key)
        },
        "retained_target_witness_map": {
            point_registry_text(point): retained_witnesses[point]
            for point in sorted(retained_witnesses, key=point_sort_key)
        },
        "raw_support_labels": [
            point_registry_text(point) for point in sorted(raw_support, key=point_sort_key)
        ],
        "retained_support_labels": [
            point_registry_text(point)
            for point in sorted(retained_support, key=point_sort_key)
        ],
    }


def builder_skipped_axioms(reason: str) -> dict[str, Any]:
    names = (
        "identity",
        "commutativity",
        "associativity",
        "compatibility_coordinates",
        "compatibility_scalars",
        "unique_prime_multiset_factorization",
        "binary_tree_multiplicity",
        "acyclic",
    )
    return {name: {"status": "NOT_APPLICABLE", "reason": reason} for name in names}


def expected_builder_p0(
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
    factors: Sequence[Point],
    raw: RawWitnessData,
) -> tuple[dict[str, Any], bool]:
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    canonical4_ordered = builder_canonical4_order(raw)
    family = base_order_ideal(len(factors)) | set(raw.canonical2) | set(canonical4_ordered)
    evaluations, collisions = builder_family_state(curve, factors, family)
    explicit_edges = []
    for formal in raw.canonical2:
        explicit_edges.append((factors[formal[0]], factors[formal[1]], evaluate(formal)))
    for formal in canonical4_ordered:
        left, right = raw.parent_pairs[formal][0]
        explicit_edges.append((evaluate(left), evaluate(right), evaluate(formal)))
    degree_sets: dict[Point, set[int]] = defaultdict(set)
    for formal, output in evaluations.items():
        degree_sets[output].add(len(formal))
    model = build_star_from_explicit_edges(labels, None, explicit_edges, degree_sets)
    selected_points = [evaluate(formal) for formal in canonical4_ordered]
    axioms, scalar_valid = builder_axioms_json(
        model, curve, scalar_by_point, set(selected_points)
    )
    raw_points = sorted({evaluate(formal) for formal in raw.u4}, key=point_sort_key)
    raw_support, raw_histogram = support_and_histogram_independent(curve, raw_points)
    retained_support, retained_histogram = support_and_histogram_independent(
        curve, selected_points
    )
    return (
        {
            "name": "P0-BALANCED-ONLY",
            "embedding_defined": True,
            "formal_family": builder_formal_family_json(
                family,
                evaluations,
                collisions,
                canonical4_ordered,
                sort_maxima=False,
            ),
            "star": builder_star_json(model),
            "axioms": axioms,
            "constrained": builder_constrained_json(model, evaluations),
            "retention": builder_retention_json(
                curve,
                raw_support,
                raw_histogram,
                retained_support,
                retained_histogram,
                raw_points,
                selected_points,
            ),
            "search": None,
        },
        scalar_valid,
    )


def expected_builder_p1(
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
    factors: Sequence[Point],
    raw: RawWitnessData,
) -> tuple[dict[str, Any], bool | None]:
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    maxima = [*raw.canonical2, *raw.canonical4]
    family = selected_order_ideal(len(factors), maxima)
    evaluations, collisions = builder_family_state(curve, factors, family)
    selected_points = [evaluate(formal) for formal in raw.canonical4]
    raw_points = sorted({evaluate(formal) for formal in raw.u4}, key=point_sort_key)
    raw_support, raw_histogram = support_and_histogram_independent(curve, raw_points)
    retained_support, retained_histogram = support_and_histogram_independent(
        curve, selected_points
    )
    formal_json = builder_formal_family_json(family, evaluations, collisions, maxima)
    if collisions:
        return (
            {
                "name": "P1-CANONICAL-CLOSURE",
                "embedding_defined": False,
                "formal_family": formal_json,
                "star": {
                    "identity_rule_total": True,
                    "unordered_nonidentity_edges": [],
                    "ordered_domain_sha256": None,
                    "ordered_domain_entries": 0,
                    "description_bits": 0,
                },
                "axioms": builder_skipped_axioms("evaluation map is not injective"),
                "constrained": None,
                "retention": builder_retention_json(
                    curve,
                    raw_support,
                    raw_histogram,
                    retained_support,
                    retained_histogram,
                    raw_points,
                    selected_points,
                ),
                "search": None,
            },
            None,
        )
    model = build_star_from_family(labels, None, family, evaluate)
    axioms, scalar_valid = builder_axioms_json(
        model, curve, scalar_by_point, set(selected_points)
    )
    return (
        {
            "name": "P1-CANONICAL-CLOSURE",
            "embedding_defined": True,
            "formal_family": formal_json,
            "star": builder_star_json(model),
            "axioms": axioms,
            "constrained": builder_constrained_json(model, evaluations),
            "retention": builder_retention_json(
                curve,
                raw_support,
                raw_histogram,
                retained_support,
                retained_histogram,
                raw_points,
                selected_points,
            ),
            "search": None,
        },
        scalar_valid,
    )


def independently_optimize_p2(
    curve: Curve,
    labels: Sequence[Point],
    factors: Sequence[Point],
    raw: RawWitnessData,
) -> tuple[list[Formal], dict[str, Any]]:
    universe = builder_candidate_universe(curve, factors, raw)
    eligible: list[Formal] = []
    eligible_universe_indices: list[int] = []
    closures: list[set[Formal]] = []
    rejected = []
    for universe_index, formal in enumerate(raw.u4):
        family = candidate_order_ideal(len(factors), formal)
        _, collisions = builder_family_state(curve, factors, family)
        if collisions:
            rejected.append(
                {
                    "universe_index": universe_index,
                    "multiset": list(formal),
                    "point": point_registry_text(
                        eval_ec_formal(curve, factors, formal)
                    ),
                    "first_collision": collisions[0],
                    "collision_replayed": True,
                }
            )
        else:
            eligible.append(formal)
            eligible_universe_indices.append(universe_index)
            closures.append(family)

    conflict_masks = [0] * len(eligible)
    conflicts = []
    for left in range(len(eligible)):
        for right in range(left + 1, len(eligible)):
            _, collisions = builder_family_state(
                curve, factors, closures[left] | closures[right]
            )
            if collisions:
                conflict_masks[left] |= 1 << right
                conflict_masks[right] |= 1 << left
                conflicts.append(
                    {
                        "left_universe_index": eligible_universe_indices[left],
                        "right_universe_index": eligible_universe_indices[right],
                        "left": list(eligible[left]),
                        "right": list(eligible[right]),
                        "first_collision": collisions[0],
                    }
                )

    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    raw_points = sorted({evaluate(formal) for formal in raw.u4}, key=point_sort_key)
    raw_support, _ = support_and_histogram_independent(curve, raw_points)
    empty_family = base_order_ideal(len(factors))
    empty_evaluations, empty_collisions = builder_family_state(
        curve, factors, empty_family
    )
    if empty_collisions:
        raise AssertionError("independent factor-base singleton family collides")
    empty_model = build_star_from_family(labels, None, empty_family, evaluate)
    empty_constrained, _, _ = constrained_indices(empty_model)
    best_key = (0, 0, -len(empty_constrained), -len(empty_model.edges))
    best_lex: tuple[Formal, ...] = ()
    best_indices: tuple[int, ...] = ()
    outcome_rows = []
    feasible_count = 0
    mismatches = []
    for mask in range(1 << len(eligible)):
        chosen = tuple(index for index in range(len(eligible)) if mask & (1 << index))
        graph_feasible = all(not (conflict_masks[index] & mask) for index in chosen)
        maxima = [eligible[index] for index in chosen]
        family = selected_order_ideal(len(factors), maxima)
        evaluations, collisions = builder_family_state(curve, factors, family)
        direct_feasible = not collisions
        outcome = {
            "subset_universe_indices": [
                eligible_universe_indices[index] for index in chosen
            ],
            "graph_feasible": graph_feasible,
            "direct_feasible": direct_feasible,
        }
        outcome_rows.append(outcome)
        if graph_feasible != direct_feasible:
            mismatch = dict(outcome)
            mismatch["first_collision"] = collisions[:1]
            mismatches.append(mismatch)
            continue
        if not direct_feasible:
            continue
        feasible_count += 1
        model = build_star_from_family(labels, None, family, evaluate)
        constrained, _, _ = constrained_indices(model)
        selected_points = [evaluate(eligible[index]) for index in chosen]
        support, _ = support_and_histogram_independent(curve, selected_points)
        key = (len(support), len(chosen), -len(constrained), -len(model.edges))
        lexical = tuple(eligible[index] for index in chosen)
        if key > best_key or (key == best_key and lexical < best_lex):
            best_key = key
            best_lex = lexical
            best_indices = chosen
    if mismatches:
        raise AssertionError(f"independent graph mismatch: {mismatches[0]!r}")
    outcome_rows.sort(key=lambda row: row["subset_universe_indices"])
    selected = [eligible[index] for index in best_indices]
    search = {
        "method": "invalid_witness_replay_plus_exhaustive_valid_vertex_subsets",
        "candidate_count": len(raw.u4),
        "candidate_universe": universe,
        "candidate_universe_sha256": digest_json(universe),
        "eligible_candidate_count": len(eligible),
        "eligible_universe_indices": eligible_universe_indices,
        "individually_rejected": rejected,
        "invalid_witnesses_replayed": len(rejected),
        "supersets_rejected_by_invalid_vertex_monotonicity": (
            (1 << len(raw.u4)) - (1 << len(eligible))
        ),
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "direct_subset_comparisons": 1 << len(eligible),
        "expected_direct_subset_comparisons": 1 << len(eligible),
        "feasible_subset_count": feasible_count,
        "graph_direct_mismatch_count": 0,
        "graph_direct_outcomes_order": "lexicographic_subset_universe_indices",
        "graph_direct_outcomes_sha256": digest_json(outcome_rows),
        "explored_nodes": 1 << len(eligible),
        "raw_final_support": len(raw_support),
        "optimal_objective": {
            "retained_final_support": best_key[0],
            "retained_degree4_formal_multisets": best_key[1],
            "constrained_count": -best_key[2],
            "unordered_nonidentity_edges": -best_key[3],
            "witness_list": [list(item) for item in best_lex],
        },
        "completeness_argument": (
            "invalid-vertex collisions reject every containing superset by monotonicity; "
            "every subset of valid vertices is directly compared with graph independence"
        ),
    }
    return selected, search


def expected_builder_p2(
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
    factors: Sequence[Point],
    raw: RawWitnessData,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    selected, search = independently_optimize_p2(curve, labels, factors, raw)
    family = selected_order_ideal(len(factors), selected)
    evaluations, collisions = builder_family_state(curve, factors, family)
    if collisions:
        raise AssertionError("independent P2 optimum is noninjective")
    model = build_star_from_family(labels, None, family, evaluate)
    selected_points = [evaluate(formal) for formal in selected]
    axioms, scalar_valid = builder_axioms_json(
        model, curve, scalar_by_point, set(selected_points)
    )
    public = {
        "labeling": {
            "label_order": [point_registry_text(point) for point in labels],
            "identity_label": "O",
            "injective": len(labels) == len(set(labels)),
            "scalar_material_attestation": {
                "forbidden_named_fields_absent_by_construction": True,
                "covert_encoding_excluded": False,
            },
        },
        "selected_formal_family": builder_formal_family_json(
            family, evaluations, collisions, selected
        ),
        "star": builder_star_json(model),
        "axioms": axioms,
        "constrained": builder_constrained_json(model, evaluations),
    }
    raw_points = sorted({evaluate(formal) for formal in raw.u4}, key=point_sort_key)
    raw_support, raw_histogram = support_and_histogram_independent(curve, raw_points)
    retained_support, retained_histogram = support_and_histogram_independent(
        curve, selected_points
    )
    return (
        public,
        {
            "optimizer_proof": search,
            "retention": builder_retention_json(
                curve,
                raw_support,
                raw_histogram,
                retained_support,
                retained_histogram,
                raw_points,
                selected_points,
            ),
        },
        scalar_valid,
    )


def control_predicates(
    *,
    source_gate: str = NA,
    evaluation_injective: str = NA,
    identity: str = NA,
    commutativity: str = NA,
    associativity: str = NA,
    compatibility_coordinates: str = NA,
    compatibility_scalars: str = NA,
    unique_factorization: str = NA,
    acyclic_reduced: str = NA,
    direct_final_edge_excluded: str = NA,
    optimizer_exact: str = NA,
) -> dict[str, str]:
    return {
        "acyclic_reduced": acyclic_reduced,
        "associativity": associativity,
        "commutativity": commutativity,
        "compatibility_coordinates": compatibility_coordinates,
        "compatibility_scalars": compatibility_scalars,
        "direct_final_edge_excluded": direct_final_edge_excluded,
        "evaluation_injective": evaluation_injective,
        "identity": identity,
        "optimizer_exact": optimizer_exact,
        "source_gate": source_gate,
        "unique_factorization": unique_factorization,
    }


def abstract_formal_model(
    prime_count: int, maximum_degree: int
) -> tuple[list[Formal], StarModel]:
    family = all_formal_multisets(prime_count, maximum_degree)
    labels = sorted(family, key=lambda item: (len(item), item))
    model = build_star_from_family(labels, (), family, lambda formal: formal)
    return labels, model


def control_checks_for_model(
    model: StarModel,
    encode_label: Callable[[Hashable], Any],
    *,
    source_gate: bool | None = None,
    coordinate_add: Callable[[Hashable, Hashable], Hashable] | None = None,
    scalar_by_label: Mapping[Hashable, int] | None = None,
    scalar_modulus: int | None = None,
    final_input_degree: int = 4,
) -> dict[str, Any]:
    return check_axioms(
        model,
        encode_label,
        evaluation_injective=True,
        source_gate=source_gate,
        coordinate_add=coordinate_add,
        scalar_by_label=scalar_by_label,
        scalar_modulus=scalar_modulus,
        final_input_degree=final_input_degree,
    )


def cyclic_control_predicates(
    model: StarModel, represented_indices: set[int], modulus: int
) -> dict[str, str]:
    identity_ok = all(
        model.call_index(model.identity_index, index) == index
        and model.call_index(index, model.identity_index) == index
        for index in range(len(model.labels))
    ) and all(output != model.identity_index for output in model.edges.values())
    commutative_ok = all(
        model.call_index(left, right) == model.call_index(right, left)
        for left in range(len(model.labels))
        for right in range(len(model.labels))
    )
    active = sorted(represented_indices)
    associative_ok = True
    for left in active:
        for middle in active:
            for right in active:
                left_inner = model.call_index(left, middle)
                left_outer = (
                    None
                    if left_inner is None
                    else model.call_index(left_inner, right)
                )
                right_inner = model.call_index(middle, right)
                right_outer = (
                    None
                    if right_inner is None
                    else model.call_index(left, right_inner)
                )
                if left_outer != right_outer:
                    associative_ok = False
                    break
            if not associative_ok:
                break
        if not associative_ok:
            break
    if any(
        index not in represented_indices
        for edge in model.edges.items()
        for index in (*edge[0], edge[1])
    ):
        raise AssertionError("cyclic control edge escaped represented labels")
    scalar_ok = all(
        model.labels[output]
        == (model.labels[left] + model.labels[right]) % modulus
        for (left, right), output in model.edges.items()
    )
    parents = _reduction_graph(model)
    acyclic_ok, _ = _acyclic_reduced(model, parents)
    unique_ok, _ = _unique_factorizations(model, parents)
    direct_final_ok = all(
        not (
            4 in model.degree_sets.get(left, set())
            and 4 in model.degree_sets.get(right, set())
        )
        for left, right in model.edges
    )
    return control_predicates(
        evaluation_injective=TRUE,
        identity=status(identity_ok),
        commutativity=status(commutative_ok),
        associativity=status(associative_ok),
        compatibility_scalars=status(scalar_ok),
        unique_factorization=status(unique_ok),
        acyclic_reduced=status(acyclic_ok),
        direct_final_edge_excluded=status(direct_final_ok),
    )


def rejected_control_predicates(*, source_gate: bool) -> dict[str, str]:
    return control_predicates(
        source_gate=status(source_gate), evaluation_injective=FALSE
    )


def independently_reconstruct_control_expectations(
    registry: Mapping[str, Any],
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
) -> list[dict[str, Any]]:
    entries = {entry["name"]: entry for entry in registry["controls"]}
    results: list[dict[str, Any]] = []

    free_family, free_model = abstract_formal_model(3, 4)
    free_checks = control_checks_for_model(free_model, lambda value: value)
    free_constrained, _, _ = constrained_indices(free_model)
    results.append(
        {
            "counterexample": None,
            "counts": {
                "constrained_labels": len(free_constrained),
                "labels": len(free_family),
                "unordered_nonidentity_edges": len(free_model.edges),
            },
            "predicates": free_checks["predicates"],
        }
    )

    cyclic_q = 509
    cyclic_weights = (1, 5, 25, 125)
    cyclic_family = all_formal_multisets(4, 4)

    def cyclic_eval(formal: Formal) -> int:
        return sum(cyclic_weights[index] for index in formal) % cyclic_q

    represented_values = {cyclic_eval(formal) for formal in cyclic_family}
    if len(represented_values) != len(cyclic_family):
        raise AssertionError("cyclic control formal evaluator is noninjective")
    cyclic_model = build_star_from_family(
        list(range(cyclic_q)), 0, cyclic_family, cyclic_eval
    )
    cyclic_constrained, _, _ = constrained_indices(cyclic_model)
    results.append(
        {
            "counterexample": None,
            "counts": {
                "constrained_labels": len(cyclic_constrained),
                "labels": cyclic_q,
                "maximum_unreduced_sum": 4 * max(cyclic_weights),
                "represented_labels": len(represented_values),
                "unordered_nonidentity_edges": len(cyclic_model.edges),
            },
            "delta": ratio(len(cyclic_constrained), cyclic_q),
            "predicates": cyclic_control_predicates(
                cyclic_model, represented_values, cyclic_q
            ),
        }
    )

    factors8, _ = build_factor_base(curve, labels, 8)
    forest_maximum = (1, 6, 6, 6)
    forest_family = candidate_order_ideal(8, forest_maximum)
    forest_evaluations, forest_collisions = builder_family_state(
        curve, factors8, forest_family
    )
    if forest_collisions:
        raise AssertionError("positive EC forest control is noninjective")
    forest_model = build_star_from_family(
        labels,
        None,
        forest_family,
        lambda formal: forest_evaluations[formal],
    )
    forest_checks = control_checks_for_model(
        forest_model,
        point_json,
        source_gate=True,
        coordinate_add=curve.add,
        scalar_by_label=scalar_by_point,
        scalar_modulus=CURVE_Q,
    )
    forest_constrained, _, _ = constrained_indices(forest_model)
    results.append(
        {
            "counterexample": None,
            "counts": {
                "constrained_labels": len(forest_constrained),
                "formal_family_by_degree": {
                    str(degree): sum(
                        len(formal) == degree for formal in forest_family
                    )
                    for degree in range(5)
                },
                "formal_family_total": len(forest_family),
                "unordered_nonidentity_edges": len(forest_model.edges),
            },
            "predicates": forest_checks["predicates"],
            "selected_output": list(forest_evaluations[forest_maximum]),
        }
    )

    repeated_family, repeated_model = abstract_formal_model(1, 4)
    repeated_checks = control_checks_for_model(repeated_model, lambda value: value)
    repeated_constrained, _, _ = constrained_indices(repeated_model)
    results.append(
        {
            "counterexample": None,
            "counts": {
                "constrained_labels": len(repeated_constrained),
                "immediate_parent_pairs_by_degree": [
                    sum(
                        len(repeated_model.labels[output]) == degree
                        for output in repeated_model.edges.values()
                    )
                    for degree in range(5)
                ],
                "labels": len(repeated_family),
                "unordered_nonidentity_edges": len(repeated_model.edges),
            },
            "predicates": repeated_checks["predicates"],
        }
    )

    balanced_fixture = entries["NC-BALANCED-ONLY"]["fixture"]
    balanced_model = build_star_from_explicit_edges(
        balanced_fixture["labels"],
        balanced_fixture["identity"],
        [tuple(edge) for edge in balanced_fixture["edges"]],
    )
    balanced_checks = control_checks_for_model(balanced_model, lambda value: value)
    balanced_constrained, _, _ = constrained_indices(balanced_model)
    results.append(
        {
            "counterexample": balanced_checks["counterexamples"]["associativity"],
            "counts": {
                "constrained_labels": len(balanced_constrained),
                "labels": len(balanced_model.labels),
                "unordered_nonidentity_edges": len(balanced_model.edges),
            },
            "predicates": balanced_checks["predicates"],
        }
    )

    factors4, _ = build_factor_base(curve, labels, 4)
    all_family = set(all_formal_multisets(4, 4))
    _, all_collisions = builder_family_state(curve, factors4, all_family)
    results.append(
        {
            "counterexample": all_collisions[0],
            "counts": {
                "collision_pairs": len(all_collisions),
                "formal_family_total": len(all_family),
            },
            "predicates": rejected_control_predicates(source_gate=True),
        }
    )

    factor_base4 = builder_factor_base_json(factors4, 4)
    duplicate_source = copy.deepcopy(factor_base4["canonical_sources"][0])
    duplicate_source["source_tag"] += "|duplicate"
    results.append(
        {
            "counterexample": {
                "first_tag": factor_base4["canonical_sources"][0]["source_tag"],
                "point": factor_base4["canonical_sources"][0]["point"],
                "second_tag": duplicate_source["source_tag"],
            },
            "predicates": control_predicates(source_gate=FALSE),
        }
    )

    decoded = {point: point for point in labels}
    true_output = forest_evaluations[forest_maximum]
    decoded[true_output] = (6, 16)
    coordinate_compatible = True
    scalar_compatible = True
    for left in range(len(forest_model.labels)):
        for right in range(len(forest_model.labels)):
            output = forest_model.call_index(left, right)
            if output is None:
                continue
            decoded_left = decoded[forest_model.labels[left]]
            decoded_right = decoded[forest_model.labels[right]]
            decoded_output = decoded[forest_model.labels[output]]
            if decoded_output != curve.add(decoded_left, decoded_right):
                coordinate_compatible = False
            if scalar_by_point[decoded_output] != (
                scalar_by_point[decoded_left] + scalar_by_point[decoded_right]
            ) % CURVE_Q:
                scalar_compatible = False
    mutation_predicates = copy.deepcopy(forest_checks["predicates"])
    mutation_predicates["compatibility_coordinates"] = status(
        coordinate_compatible
    )
    mutation_predicates["compatibility_scalars"] = status(scalar_compatible)
    results.append(
        {
            "counterexample": {
                "formal_label": list(forest_maximum),
                "mutated_decode": [6, 16],
                "true_decode": list(true_output),
            },
            "predicates": mutation_predicates,
        }
    )

    degree8_family, degree8_model = abstract_formal_model(1, 8)
    degree8_checks = control_checks_for_model(
        degree8_model, lambda value: value, final_input_degree=4
    )
    degree8_constrained, _, _ = constrained_indices(degree8_model)
    results.append(
        {
            "counterexample": {"edge_degrees": [4, 4, 8]},
            "counts": {
                "constrained_labels": len(degree8_constrained),
                "labels": len(degree8_family),
                "unordered_nonidentity_edges": len(degree8_model.edges),
            },
            "delta": ratio(len(degree8_constrained), len(degree8_family)),
            "predicates": degree8_checks["predicates"],
        }
    )

    factors6, _ = build_factor_base(curve, labels, 6)
    b6_family = candidate_order_ideal(6, (0, 3))
    _, b6_collisions = builder_family_state(curve, factors6, b6_family)
    results.append(
        {
            "counterexample": b6_collisions[0],
            "predicates": rejected_control_predicates(source_gate=True),
        }
    )

    canonical = (0, 0, 0, 4)
    alternate = forest_maximum
    raw8 = build_raw_witness_data(curve, factors8)
    if canonical not in raw8.u4 or alternate not in raw8.u4:
        raise AssertionError("B8 control witnesses are absent from U4_BAL")
    canonical_family = candidate_order_ideal(8, canonical)
    canonical_evaluations, canonical_collisions = builder_family_state(
        curve, factors8, canonical_family
    )
    if canonical_evaluations[canonical] != forest_evaluations[alternate]:
        raise AssertionError("B8 control witnesses do not share an output")
    results.append(
        {
            "cases": [
                {
                    "counterexample": canonical_collisions[0],
                    "formal_multiset": list(canonical),
                    "predicates": rejected_control_predicates(source_gate=True),
                },
                {
                    "counts": {
                        "constrained_labels": len(forest_constrained),
                        "formal_family_total": len(forest_family),
                        "unordered_nonidentity_edges": len(forest_model.edges),
                    },
                    "counterexample": None,
                    "formal_multiset": list(alternate),
                    "predicates": forest_checks["predicates"],
                },
            ],
            "common_output": list(canonical_evaluations[canonical]),
        }
    )

    optimizer_fixture = entries["NC-OPTIMIZER-FIXTURE"]["fixture"]
    conflict_edges = {tuple(edge) for edge in optimizer_fixture["conflict_edges"]}
    optimizer_rows = []
    best_subset: tuple[int, ...] | None = None
    best_key: tuple[int, int, int, int] | None = None
    for mask in range(1 << len(optimizer_fixture["vertices"])):
        subset = tuple(
            vertex
            for vertex in optimizer_fixture["vertices"]
            if mask & (1 << vertex)
        )
        if any(left in subset and right in subset for left, right in conflict_edges):
            continue
        outputs = [optimizer_fixture["outputs"][index] for index in subset]
        support = {
            (outputs[left] + outputs[right]) % 17
            for left in range(len(outputs))
            for right in range(left, len(outputs))
        }
        constrained_count = 1 if not subset else 4 * len(subset) + 1
        edge_count = 4 * len(subset)
        objective = [len(support), len(subset), constrained_count, edge_count]
        optimizer_rows.append({"objective": objective, "subset": list(subset)})
        key = (objective[0], objective[1], -objective[2], -objective[3])
        if best_key is None or key > best_key or (
            key == best_key and (best_subset is None or subset < best_subset)
        ):
            best_key = key
            best_subset = subset
    optimizer_rows.sort(key=lambda row: (len(row["subset"]), row["subset"]))
    results.append(
        {
            "counterexample": None,
            "feasible_subset_objectives": optimizer_rows,
            "predicates": control_predicates(optimizer_exact=TRUE),
            "winner": list(best_subset or ()),
        }
    )

    names = [entry["name"] for entry in registry["controls"]]
    if len(results) != len(names):
        raise AssertionError("independent control count mismatch")
    return [
        {"name": name, "observed": observed}
        for name, observed in zip(names, results)
    ]


def replace_deferred_control_predicates(
    value: Any, deferred: set[str]
) -> Any:
    result = copy.deepcopy(value)

    def visit(current: Any) -> None:
        if isinstance(current, dict):
            predicates = current.get("predicates")
            if isinstance(predicates, dict):
                for predicate in deferred:
                    if predicates.get(predicate) not in (None, NA):
                        predicates[predicate] = VERIFIER_ONLY
            for child in current.values():
                visit(child)
        elif isinstance(current, list):
            for child in current:
                visit(child)

    visit(result)
    return result


def independently_verify_controls(
    registry: Mapping[str, Any],
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reconstructed = independently_reconstruct_control_expectations(
        registry, curve, labels, scalar_by_point
    )
    entries = list(registry["controls"])
    errors: list[str] = []
    deferred_by_name = {
        "PC-EC-FOREST": {"compatibility_scalars"},
        "NC-COMPAT-MUTATION": {"compatibility_scalars"},
        "NC-B8-CANONICAL-LOSS": {"compatibility_scalars"},
    }
    certificate_controls = []
    report_rows = []
    for entry, actual in zip(entries, reconstructed):
        name = entry["name"]
        compare_errors: list[str] = []
        compare_exact(entry["expected"], actual["observed"], name, compare_errors)
        errors.extend(compare_errors)
        deferred = deferred_by_name.get(name, set())
        builder_observed = replace_deferred_control_predicates(
            actual["observed"], deferred
        )
        certificate_controls.append(
            {
                "name": name,
                "fixture_sha256": digest_json(entry["fixture"]),
                "expected": copy.deepcopy(entry["expected"]),
                "observed": builder_observed,
                "deferred_predicates": sorted(deferred),
                "builder_passed": not compare_errors,
            }
        )
        report_rows.append(
            {
                "name": name,
                "valid": not compare_errors,
                "deferred_predicates_resolved": sorted(deferred),
                "errors": compare_errors,
            }
        )
    if errors:
        raise AssertionError("control registry mismatch: " + errors[0])
    return certificate_controls, report_rows


def expected_minimized_policy_failures(
    policies: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for policy in policies:
        collisions = policy["formal_family"]["evaluation_collisions"]
        if collisions:
            failures.append(
                {
                    "policy": policy["name"],
                    "predicate": "evaluation_injective",
                    "counterexample": collisions[0],
                }
            )
        for name, record in policy["axioms"].items():
            if not isinstance(record, dict) or record.get("valid") is not False:
                continue
            witness = record.get("counterexample")
            if witness is None:
                for key in ("failures", "cycle", "forbidden_edges"):
                    values = record.get(key)
                    if values:
                        witness = values[0] if isinstance(values, list) else values
                        break
            failures.append(
                {
                    "policy": policy["name"],
                    "predicate": name,
                    "counterexample": witness,
                }
            )
    return failures


def expected_builder_row(
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
    factor_base_size: int,
    controls: Sequence[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    factors, _ = build_factor_base(curve, labels, factor_base_size)
    raw = build_raw_witness_data(curve, factors)
    p0, p0_scalar_valid = expected_builder_p0(
        curve, labels, scalar_by_point, factors, raw
    )
    p1, p1_scalar_valid = expected_builder_p1(
        curve, labels, scalar_by_point, factors, raw
    )
    public_model, p2_private, p2_scalar_valid = expected_builder_p2(
        curve, labels, scalar_by_point, factors, raw
    )
    raw_witnesses = builder_raw_witness_json(curve, factors, raw)
    counterexamples = expected_minimized_policy_failures(
        [
            p0,
            p1,
            {
                "name": "P2-BALANCED-UNIVERSE-OPTIMUM",
                "formal_family": public_model["selected_formal_family"],
                "axioms": public_model["axioms"],
            },
        ]
    )
    private_audit = {
        "raw_witnesses": raw_witnesses,
        "baseline_policies": [p0, p1],
        "optimizer_proof": p2_private["optimizer_proof"],
        "retention": p2_private["retention"],
        "minimized_policy_counterexamples": counterexamples,
        "charged_operations": copy.deepcopy(
            EXPECTED_ROW_OPERATIONS[factor_base_size]
        ),
    }
    set_fixed_point_json_size(private_audit, "charged_canonical_json_bytes")
    factor_base = builder_factor_base_json(factors, factor_base_size)
    row = {
        "factor_base": factor_base,
        "raw_witnesses": copy.deepcopy(raw_witnesses),
        "public_model": public_model,
        "private_audit": private_audit,
        "accounting": {
            "public_model_canonical_json_bytes": len(
                canonical_json_bytes(public_model)
            ),
            "source_witness_canonical_json_bytes": len(
                canonical_json_bytes(factor_base["canonical_sources"])
            ),
            "distinct_balanced_candidates_per_constrained_label": ratio(
                raw_witnesses["balanced_degree4_candidate_count"],
                public_model["constrained"]["count"],
            ),
            "raw_balanced_parent_pairs_per_constrained_label": ratio(
                raw_witnesses["balanced_parent_pair_count"],
                public_model["constrained"]["count"],
            ),
            "source_tag_multiplicity_histogram": {
                "1": len(factor_base["canonical_sources"])
            },
            "discarded_source_tag_count": len(factor_base["discarded_source_tags"]),
            "minimized_counterexample_sha256": digest_json(counterexamples),
        },
        "controls": copy.deepcopy(list(controls)),
        "control_summary": {
            "all_registered_behaviors_observed": all(
                control["builder_passed"] for control in controls
            ),
            "unexpected_failures": [
                control["name"]
                for control in controls
                if not control["builder_passed"]
            ],
        },
        "claim_boundary": (
            "five-bit implementation preflight only; no ECDLP, exponent, relation, "
            "rank, descent, or conventional-coordinate lower-bound claim"
        ),
    }
    return (
        row,
        {
            "B": factor_base_size,
            "p0_scalar_compatibility_valid": p0_scalar_valid,
            "p1_scalar_compatibility_valid": p1_scalar_valid,
            "p2_scalar_compatibility_valid": p2_scalar_valid,
            "selected_degree4_count": len(
                public_model["selected_formal_family"]["maximal_multisets"]
            ),
            "retained_final_support": p2_private["optimizer_proof"][
                "optimal_objective"
            ]["retained_final_support"],
        },
    )


def semantic_model_record(
    model: StarModel,
    family: set[Formal],
    evaluations: Mapping[Formal, Point],
    collisions: Sequence[dict[str, Any]],
    curve: Curve,
    scalar_by_point: Mapping[Point, int],
    source_gate: bool,
) -> dict[str, Any]:
    checks = check_axioms(
        model,
        point_registry_text,
        evaluation_injective=not collisions,
        source_gate=source_gate,
        coordinate_add=curve.add,
        scalar_by_label=scalar_by_point,
        scalar_modulus=CURVE_Q,
    )
    constrained, _, _ = constrained_indices(model)
    possible_edges = (len(model.labels) - 1) * len(model.labels) // 2
    return {
        "family": [
            list(formal) for formal in sorted(family, key=lambda item: (len(item), item))
        ],
        "evaluation": [
            [list(formal), point_registry_text(evaluations[formal])]
            for formal in sorted(family, key=lambda item: (len(item), item))
        ],
        "collisions": list(collisions),
        "edges_by_label_index": [
            [left, right, output]
            for (left, right), output in sorted(model.edges.items())
        ],
        "constrained_label_indices": sorted(constrained),
        "normalized_nonidentity_edge_density": ratio(
            len(model.edges), max(1, possible_edges)
        ),
        "predicates": {
            key: checks["predicates"][key]
            for key in (
                "identity",
                "commutativity",
                "associativity",
                "compatibility_coordinates",
                "compatibility_scalars",
                "unique_factorization",
                "acyclic_reduced",
                "direct_final_edge_excluded",
            )
        },
    }


def certificate_model_record(
    family_record: Mapping[str, Any],
    star_record: Mapping[str, Any],
    axioms: Mapping[str, Any],
    constrained_record: Mapping[str, Any],
    label_to_index: Mapping[str, int],
    scalar_status: str,
) -> dict[str, Any]:
    family = [
        formal
        for degree in range(5)
        for formal in family_record["downward_closure_by_degree"][str(degree)]
    ]
    return {
        "family": family,
        "evaluation": [
            [entry["multiset"], entry["point"]]
            for entry in family_record["evaluation_map"]
        ],
        "collisions": family_record["evaluation_collisions"],
        "edges_by_label_index": [
            [label_to_index[left], label_to_index[right], label_to_index[output]]
            for left, right, output in star_record["unordered_nonidentity_edges"]
        ],
        "constrained_label_indices": [
            label_to_index[label] for label in constrained_record["labels"]
        ],
        "normalized_nonidentity_edge_density": constrained_record["edge_density"][
            "normalized_against_unordered_label_pairs"
        ],
        "predicates": {
            "identity": status(axioms["identity"]["valid"]),
            "commutativity": status(axioms["commutativity"]["valid"]),
            "associativity": status(axioms["associativity"]["valid"]),
            "compatibility_coordinates": status(
                axioms["compatibility_coordinates"]["valid"]
            ),
            "compatibility_scalars": scalar_status,
            "unique_factorization": status(
                axioms["unique_prime_multiset_factorization"]["valid"]
            ),
            "acyclic_reduced": status(axioms["acyclic"]["valid"]),
            "direct_final_edge_excluded": status(
                axioms["direct_final_edge_excluded"]["valid"]
            ),
        },
    }


def semantic_differential_check(
    actual_row: Mapping[str, Any],
    curve: Curve,
    labels: Sequence[Point],
    scalar_by_point: Mapping[Point, int],
    factor_base_size: int,
) -> dict[str, Any]:
    errors: list[str] = []
    factors, factor_contract = build_factor_base(curve, labels, factor_base_size)
    raw = build_raw_witness_data(curve, factors)
    label_to_index = {
        point_registry_text(point): index for index, point in enumerate(labels)
    }
    expected_sources = factor_contract["source_records"]
    observed_sources = [
        {
            "root_index": record["root_index"],
            "x": record["x"],
            "sign_bit": record["sign_bit"],
            "y": record["y"],
        }
        for record in actual_row["factor_base"]["canonical_sources"]
    ]
    compare_exact(
        expected_sources,
        observed_sources,
        f"semantic.B{factor_base_size}.source_records",
        errors,
    )

    evaluate = lambda formal: eval_ec_formal(curve, factors, formal)
    canonical4 = builder_canonical4_order(raw)
    p0_family = base_order_ideal(factor_base_size) | set(raw.canonical2) | set(
        canonical4
    )
    p0_evaluations, p0_collisions = builder_family_state(
        curve, factors, p0_family
    )
    p0_edges = []
    for formal in raw.canonical2:
        p0_edges.append((factors[formal[0]], factors[formal[1]], evaluate(formal)))
    for formal in canonical4:
        left, right = raw.parent_pairs[formal][0]
        p0_edges.append((evaluate(left), evaluate(right), evaluate(formal)))
    p0_degrees: dict[Point, set[int]] = defaultdict(set)
    for formal, output in p0_evaluations.items():
        p0_degrees[output].add(len(formal))
    p0_model = build_star_from_explicit_edges(labels, None, p0_edges, p0_degrees)
    p0_oracle = semantic_model_record(
        p0_model,
        p0_family,
        p0_evaluations,
        p0_collisions,
        curve,
        scalar_by_point,
        True,
    )
    p0_actual = actual_row["private_audit"]["baseline_policies"][0]
    p0_certificate = certificate_model_record(
        p0_actual["formal_family"],
        p0_actual["star"],
        p0_actual["axioms"],
        p0_actual["constrained"],
        label_to_index,
        TRUE,
    )
    compare_exact(
        p0_oracle,
        p0_certificate,
        f"semantic.B{factor_base_size}.P0",
        errors,
    )

    p1_maxima = set(raw.canonical2) | set(builder_canonical4_order(raw))
    p1_family = selected_order_ideal(factor_base_size, p1_maxima)
    p1_evaluations, p1_collisions = builder_family_state(curve, factors, p1_family)
    p1_actual = actual_row["private_audit"]["baseline_policies"][1]
    expected_p1_family = [
        list(formal)
        for formal in sorted(p1_family, key=lambda item: (len(item), item))
    ]
    actual_p1_family = [
        formal
        for degree in range(5)
        for formal in p1_actual["formal_family"]["downward_closure_by_degree"][
            str(degree)
        ]
    ]
    compare_exact(
        expected_p1_family,
        actual_p1_family,
        f"semantic.B{factor_base_size}.P1.family",
        errors,
    )
    compare_exact(
        p1_collisions,
        p1_actual["formal_family"]["evaluation_collisions"],
        f"semantic.B{factor_base_size}.P1.collisions",
        errors,
    )
    if not p1_collisions or p1_actual["embedding_defined"] is not False:
        errors.append(f"semantic.B{factor_base_size}.P1: expected rejected embedding")

    selected, search = independently_optimize_p2(curve, labels, factors, raw)
    p2_family = selected_order_ideal(factor_base_size, selected)
    p2_evaluations, p2_collisions = builder_family_state(curve, factors, p2_family)
    p2_model = build_star_from_family(labels, None, p2_family, evaluate)
    p2_oracle = semantic_model_record(
        p2_model,
        p2_family,
        p2_evaluations,
        p2_collisions,
        curve,
        scalar_by_point,
        True,
    )
    public = actual_row["public_model"]
    p2_certificate = certificate_model_record(
        public["selected_formal_family"],
        public["star"],
        public["axioms"],
        public["constrained"],
        label_to_index,
        TRUE,
    )
    compare_exact(
        p2_oracle,
        p2_certificate,
        f"semantic.B{factor_base_size}.P2",
        errors,
    )
    compare_exact(
        search["optimal_objective"],
        actual_row["private_audit"]["optimizer_proof"]["optimal_objective"],
        f"semantic.B{factor_base_size}.optimizer_objective",
        errors,
    )
    raw_points = sorted(
        {evaluate(formal) for formal in raw.u4}, key=point_sort_key
    )
    selected_points = [evaluate(formal) for formal in selected]
    raw_support, raw_histogram = support_and_histogram_independent(
        curve, raw_points
    )
    retained_support, retained_histogram = support_and_histogram_independent(
        curve, selected_points
    )
    retention_oracle = builder_retention_json(
        curve,
        raw_support,
        raw_histogram,
        retained_support,
        retained_histogram,
        raw_points,
        selected_points,
    )
    compare_exact(
        retention_oracle,
        actual_row["private_audit"]["retention"],
        f"semantic.B{factor_base_size}.retention",
        errors,
    )
    constrained_count = len(p2_oracle["constrained_label_indices"])
    accounting_oracle = {
        "distinct_balanced_candidates_per_constrained_label": ratio(
            len(raw.u4), constrained_count
        ),
        "raw_balanced_parent_pairs_per_constrained_label": ratio(
            sum(len(values) for values in raw.parent_pairs.values()),
            constrained_count,
        ),
    }
    accounting_certificate = {
        key: actual_row["accounting"][key] for key in accounting_oracle
    }
    compare_exact(
        accounting_oracle,
        accounting_certificate,
        f"semantic.B{factor_base_size}.accounting",
        errors,
    )
    identity_witnesses = [
        list(formal) for formal in sorted(raw.degree2_groups.get(None, []))
    ]
    compare_exact(
        identity_witnesses,
        actual_row["private_audit"]["raw_witnesses"][
            "degree2_identity_witnesses"
        ],
        f"semantic.B{factor_base_size}.degree2_identity_witnesses",
        errors,
    )
    semantic_payload = {
        "B": factor_base_size,
        "source_records": expected_sources,
        "P0": p0_oracle,
        "P1_family": expected_p1_family,
        "P1_collisions": p1_collisions,
        "P2": p2_oracle,
        "optimizer_objective": search["optimal_objective"],
        "retention": retention_oracle,
        "accounting": accounting_oracle,
        "degree2_identity_witnesses": identity_witnesses,
    }
    return {
        "B": factor_base_size,
        "valid": not errors,
        "semantic_oracle_sha256": digest_json(semantic_payload),
        "errors": errors,
    }


def validate_exact_keys(
    value: Any, expected_keys: set[str], path: str, errors: list[str]
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object, got {type(value).__name__}")
        return False
    actual_keys = set(value)
    for key in sorted(expected_keys - actual_keys):
        errors.append(f"{path}.{key}: missing key")
    for key in sorted(actual_keys - expected_keys):
        errors.append(f"{path}.{key}: unexpected key")
    return actual_keys == expected_keys


def validate_json_number_types(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Decimal):
        errors.append(f"{path}: floating-point JSON numbers are forbidden")
    elif isinstance(value, float):
        errors.append(f"{path}: native floating-point values are forbidden")
    elif isinstance(value, dict):
        for key, child in value.items():
            validate_json_number_types(child, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_json_number_types(child, f"{path}[{index}]", errors)


def scalar_material_errors(value: Any) -> list[str]:
    forbidden_keys = {
        "discrete_log_table",
        "label_to_scalar",
        "scalar_by_label",
        "scalar_by_point",
        "scalar_indices",
        "scalar_table",
        "scalar_to_label",
        "sigma_scalar_to_label",
    }
    errors: list[str] = []

    def visit(current: Any, path: str) -> None:
        if isinstance(current, dict):
            for key, child in current.items():
                if key.lower() in forbidden_keys:
                    errors.append(f"{path}.{key}: builder-visible scalar material")
                visit(child, f"{path}.{key}")
        elif isinstance(current, list):
            for index, child in enumerate(current):
                visit(child, f"{path}[{index}]")

    visit(value, "certificate")
    return errors


def independent_j_invariant(curve: Curve) -> int:
    c4 = (4 * pow(curve.a, 3, curve.p)) % curve.p
    discriminant_factor = (c4 + 27 * pow(curve.b, 2, curve.p)) % curve.p
    return (1728 * c4 * pow(discriminant_factor, -1, curve.p)) % curve.p


def expected_curve_record(curve: Curve, labels: Sequence[Point]) -> dict[str, Any]:
    label_text = [point_registry_text(point) for point in labels]
    return {
        "bits": 5,
        "p": CURVE_P,
        "a": CURVE_A,
        "b": CURVE_B,
        "q": CURVE_Q,
        "trace": CURVE_P + 1 - CURVE_Q,
        "j_invariant": independent_j_invariant(curve),
        "generator": list(CURVE_G),
        "point_table_labels": label_text,
        "point_table_sha256": digest_json(label_text),
        "group_order_proof": {
            "method": "exhaustive_affine_coordinate_enumeration",
            "affine_points": CURVE_Q - 1,
            "identity_points": 1,
            "order_is_prime": True,
            "cofactor": 1,
        },
    }


_SCALAR_INDEX_ORACLE_CACHE: dict[str, Any] | None = None


def load_scalar_index_oracle() -> dict[str, Any]:
    global _SCALAR_INDEX_ORACLE_CACHE
    source_hash = file_sha256(SCALAR_INDEX_ORACLE_SOURCE_PATH)
    artifact_hash = file_sha256(SCALAR_INDEX_ORACLE_ARTIFACT_PATH)
    if source_hash != SCALAR_INDEX_ORACLE_SOURCE_SHA256:
        raise AssertionError(
            "scalar-index oracle source hash mismatch: "
            f"expected {SCALAR_INDEX_ORACLE_SOURCE_SHA256}, got {source_hash}"
        )
    if artifact_hash != SCALAR_INDEX_ORACLE_ARTIFACT_SHA256:
        raise AssertionError(
            "scalar-index oracle artifact hash mismatch: "
            f"expected {SCALAR_INDEX_ORACLE_ARTIFACT_SHA256}, got {artifact_hash}"
        )
    artifact, _ = read_strict_json(SCALAR_INDEX_ORACLE_ARTIFACT_PATH)
    validate_errors: list[str] = []
    validate_json_number_types(artifact, "scalar_index_oracle", validate_errors)
    if validate_errors:
        raise AssertionError(validate_errors[0])
    expected_top_keys = {
        "schema",
        "experiment_id",
        "status",
        "claim_boundary",
        "implementation",
        "fixture",
        "rows",
        "frozen_expectation_checks",
        "valid",
    }
    if not isinstance(artifact, dict) or set(artifact) != expected_top_keys:
        raise AssertionError("scalar-index oracle top-level schema mismatch")
    if artifact["schema"] != "sgcp-embed-001-scalar-index-oracle-v1":
        raise AssertionError("scalar-index oracle schema mismatch")
    if artifact["experiment_id"] != RUNNER_EXPERIMENT_ID:
        raise AssertionError("scalar-index oracle experiment ID mismatch")
    if artifact["fixture"]["scalar_table_sha256"] != SCALAR_TABLE_SHA256:
        raise AssertionError("scalar-index oracle scalar-table digest mismatch")
    if [row["B"] for row in artifact["rows"]] != list(FACTOR_BASE_SIZES):
        raise AssertionError("scalar-index oracle factor-base rows mismatch")
    if _SCALAR_INDEX_ORACLE_CACHE is None:
        specification = importlib.util.spec_from_file_location(
            "_sgcp_scalar_index_oracle_frozen",
            SCALAR_INDEX_ORACLE_SOURCE_PATH,
        )
        if specification is None or specification.loader is None:
            raise ImportError("cannot load frozen scalar-index oracle source")
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        runtime_document = module.build_oracle_document()
        if canonical_json_bytes(runtime_document) != canonical_json_bytes(artifact):
            raise AssertionError(
                "runtime scalar-index oracle differs from its frozen artifact"
            )
        _SCALAR_INDEX_ORACLE_CACHE = runtime_document
    elif canonical_json_bytes(_SCALAR_INDEX_ORACLE_CACHE) != canonical_json_bytes(
        artifact
    ):
        raise AssertionError("cached scalar-index oracle differs from frozen artifact")
    if artifact.get("valid") is not True:
        raise AssertionError("frozen scalar-index oracle is not exact valid=true")
    return artifact


def scalar_index_oracle_row_check(
    actual_row: Mapping[str, Any],
    oracle_row: Mapping[str, Any],
    scalar_table: Sequence[Point],
    factor_base_size: int,
) -> dict[str, Any]:
    errors: list[str] = []
    proof = actual_row["private_audit"]["optimizer_proof"]
    public = actual_row["public_model"]
    raw = actual_row["private_audit"]["raw_witnesses"]
    retention = actual_row["private_audit"]["retention"]

    scalar_counts = {
        "candidate_count": proof["candidate_count"],
        "valid_candidate_count": proof["eligible_candidate_count"],
        "invalid_candidate_count": len(proof["individually_rejected"]),
        "conflict_count": proof["conflict_count"],
        "direct_subset_count": proof["direct_subset_comparisons"],
        "feasible_subset_count": proof["feasible_subset_count"],
        "graph_direct_mismatch_count": proof["graph_direct_mismatch_count"],
    }
    compare_exact(
        scalar_counts,
        {key: oracle_row[key] for key in scalar_counts},
        f"scalar_index.B{factor_base_size}.counts",
        errors,
    )
    compare_exact(
        proof["eligible_universe_indices"],
        oracle_row["valid_universe_indices"],
        f"scalar_index.B{factor_base_size}.valid_universe_indices",
        errors,
    )
    compare_exact(
        [row["universe_index"] for row in proof["individually_rejected"]],
        [row["universe_index"] for row in oracle_row["individually_invalid"]],
        f"scalar_index.B{factor_base_size}.invalid_universe_indices",
        errors,
    )
    compare_exact(
        [
            [row["left_universe_index"], row["right_universe_index"]]
            for row in proof["conflicts"]
        ],
        [
            [row["left_universe_index"], row["right_universe_index"]]
            for row in oracle_row["conflicts"]
        ],
        f"scalar_index.B{factor_base_size}.conflict_pairs",
        errors,
    )
    compare_exact(
        proof["graph_direct_outcomes_sha256"],
        oracle_row["lexicographic_outcome_sha256"],
        f"scalar_index.B{factor_base_size}.outcome_sha256",
        errors,
    )
    oracle_objective = oracle_row["objective"]
    certificate_objective = {
        key: proof["optimal_objective"][key] for key in oracle_objective
    }
    compare_exact(
        certificate_objective,
        oracle_objective,
        f"scalar_index.B{factor_base_size}.objective",
        errors,
    )
    selected_witnesses = public["selected_formal_family"]["maximal_multisets"]
    compare_exact(
        selected_witnesses,
        oracle_row["selected"]["witnesses"],
        f"scalar_index.B{factor_base_size}.selected_witnesses",
        errors,
    )
    selected_set = {tuple(witness) for witness in selected_witnesses}
    selected_indices = [
        row["index"]
        for row in raw["balanced_candidate_universe"]
        if tuple(row["multiset"]) in selected_set
    ]
    compare_exact(
        selected_indices,
        oracle_row["selected"]["universe_indices"],
        f"scalar_index.B{factor_base_size}.selected_universe_indices",
        errors,
    )

    certificate_universe = raw["balanced_candidate_universe"]
    oracle_universe = oracle_row["candidate_universe"]
    universe_projection = [
        {
            "universe_index": row["index"],
            "witness": row["multiset"],
            "point": row["point"],
            "parent_pairs": row["parent_pairs"],
        }
        for row in certificate_universe
    ]
    oracle_projection = [
        {
            "universe_index": row["universe_index"],
            "witness": row["witness"],
            "point": point_registry_text(scalar_table[row["scalar_output"]]),
            "parent_pairs": row["parent_pairs"],
        }
        for row in oracle_universe
    ]
    compare_exact(
        universe_projection,
        oracle_projection,
        f"scalar_index.B{factor_base_size}.candidate_universe",
        errors,
    )

    def translated_count_map(value: Mapping[str, Any]) -> dict[str, Any]:
        return {
            point_registry_text(scalar_table[int(index)]): count
            for index, count in value.items()
        }

    def translated_witness_map(value: Mapping[str, Any]) -> dict[str, Any]:
        translated: dict[str, Any] = {}
        for target_index, scalar_pairs in value.items():
            ordered_pairs = []
            for left_index, right_index in scalar_pairs:
                pair_points = sorted(
                    (scalar_table[left_index], scalar_table[right_index]),
                    key=point_sort_key,
                )
                ordered_pairs.append(
                    (
                        tuple(point_sort_key(point) for point in pair_points),
                        [point_registry_text(point) for point in pair_points],
                    )
                )
            ordered_pairs.sort(key=lambda row: row[0])
            translated[point_registry_text(scalar_table[int(target_index)])] = [
                labels for _, labels in ordered_pairs
            ]
        return translated

    oracle_retention = oracle_row["retention"]
    compare_exact(
        retention["raw_target_witness_counts"],
        translated_count_map(oracle_retention["raw_target_witness_counts"]),
        f"scalar_index.B{factor_base_size}.raw_target_witness_counts",
        errors,
    )
    compare_exact(
        retention["retained_target_witness_counts"],
        translated_count_map(oracle_retention["retained_target_witness_counts"]),
        f"scalar_index.B{factor_base_size}.retained_target_witness_counts",
        errors,
    )
    compare_exact(
        retention["raw_target_witness_map"],
        translated_witness_map(oracle_retention["raw_target_witness_map"]),
        f"scalar_index.B{factor_base_size}.raw_target_witness_map",
        errors,
    )
    compare_exact(
        retention["retained_target_witness_map"],
        translated_witness_map(oracle_retention["retained_target_witness_map"]),
        f"scalar_index.B{factor_base_size}.retained_target_witness_map",
        errors,
    )
    for key in (
        "raw_final_support",
        "retained_final_support",
        "support_ratio",
        "raw_absolute_group_coverage",
        "retained_absolute_group_coverage",
        "raw_target_witness_histogram",
        "retained_target_witness_histogram",
    ):
        compare_exact(
            retention[key],
            oracle_retention[key],
            f"scalar_index.B{factor_base_size}.retention.{key}",
            errors,
        )

    constrained_count = public["constrained"]["count"]
    parent_pair_count = sum(
        len(row["parent_pairs"]) for row in oracle_universe
    )
    accounting_oracle = {
        "distinct_balanced_candidates_per_constrained_label": ratio(
            len(oracle_universe), constrained_count
        ),
        "raw_balanced_parent_pairs_per_constrained_label": ratio(
            parent_pair_count, constrained_count
        ),
    }
    compare_exact(
        {key: actual_row["accounting"][key] for key in accounting_oracle},
        accounting_oracle,
        f"scalar_index.B{factor_base_size}.accounting",
        errors,
    )
    return {
        "B": factor_base_size,
        "valid": not errors,
        "oracle_row_sha256": digest_json(oracle_row),
        "candidate_count": oracle_row["candidate_count"],
        "valid_candidate_count": oracle_row["valid_candidate_count"],
        "conflict_count": oracle_row["conflict_count"],
        "direct_subset_count": oracle_row["direct_subset_count"],
        "objective": copy.deepcopy(oracle_objective),
        "lexicographic_outcome_sha256": oracle_row[
            "lexicographic_outcome_sha256"
        ],
        "errors": errors,
    }


def git_head(repo_root: Path) -> str:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def source_independence_errors() -> list[str]:
    errors: list[str] = []
    if not BUILDER_PATH.is_file():
        return [f"builder source missing: {BUILDER_PATH}"]
    if not SCALAR_INDEX_ORACLE_SOURCE_PATH.is_file():
        return [f"scalar-index oracle source missing: {SCALAR_INDEX_ORACLE_SOURCE_PATH}"]
    if os.path.samefile(BUILDER_PATH, SCRIPT_PATH):
        errors.append("builder and verifier resolve to the same file")
        return errors
    if os.path.samefile(SCALAR_INDEX_ORACLE_SOURCE_PATH, SCRIPT_PATH) or os.path.samefile(
        SCALAR_INDEX_ORACLE_SOURCE_PATH, BUILDER_PATH
    ):
        errors.append("scalar-index oracle aliases an existing SGCP implementation")
        return errors
    builder_tree = ast.parse(BUILDER_PATH.read_text(encoding="utf-8"))
    verifier_tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    scalar_oracle_tree = ast.parse(
        SCALAR_INDEX_ORACLE_SOURCE_PATH.read_text(encoding="utf-8")
    )
    builder_function_names = {
        node.name
        for node in ast.walk(builder_tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    builder_assigned_names = {
        node.id
        for node in ast.walk(builder_tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    for forbidden in ("mul", "scalar_mul", "scalar_table", "discrete_log_table"):
        if forbidden in builder_function_names:
            errors.append(f"builder defines forbidden scalar helper {forbidden!r}")
    for forbidden in ("scalar_table", "discrete_log_table", "scalar_by_point"):
        if forbidden in builder_assigned_names:
            errors.append(f"builder assigns forbidden scalar state {forbidden!r}")
    for node in ast.walk(verifier_tree):
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported = [node.module or ""]
        else:
            continue
        if any(name.rsplit(".", 1)[-1] == "sgcp_embed" for name in imported):
            errors.append("verifier imports the certificate builder")
    for node in ast.walk(scalar_oracle_tree):
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported = [node.module or ""]
        else:
            continue
        forbidden = {"sgcp_embed", "verify_sgcp_embed"}
        if any(name.rsplit(".", 1)[-1] in forbidden for name in imported):
            errors.append("scalar-index oracle imports an existing SGCP implementation")
    return errors


def validate_builder_argv(
    argv: Any,
    contract_path: Path,
    literature_path: Path,
    input_path: Path,
    locked_runner: bool,
    errors: list[str],
) -> None:
    if not isinstance(argv, list) or not argv or any(type(item) is not str for item in argv):
        errors.append("implementation.command_argv: expected nonempty string list")
        return
    if len(argv) < 2:
        errors.append("implementation.command_argv: builder script is absent")
        return
    script_index = 4 if locked_runner else 1
    try:
        script_argument = Path(argv[script_index]).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"implementation.command_argv[1]: cannot resolve builder: {exc}")
    else:
        if script_argument != BUILDER_PATH:
            errors.append(
                "implementation.command_argv[1]: does not resolve to frozen builder"
            )
    expected_length = 16 if locked_runner else 12
    if len(argv) != expected_length:
        errors.append(
            "implementation.command_argv: unexpected or missing tokens; "
            f"expected {expected_length}, got {len(argv)}"
        )
        return
    if locked_runner:
        expected_literals = {
            1: "-I",
            2: "-S",
            3: "-B",
            5: "--contract",
            7: "--literature",
            9: "--toy-bits",
            10: "5",
            11: "--factor-base-sizes",
            12: "4",
            13: "6",
            14: "8",
            15: "--runner-json",
        }
        path_records = (
            (6, contract_path, "--contract"),
            (8, literature_path, "--literature"),
        )
    else:
        expected_literals = {
            2: "--contract",
            4: "--literature",
            6: "--toy-bits",
            7: "5",
            8: "--factor-base-sizes",
            9: "4",
            10: "6",
            11: "8",
        }
        path_records = (
            (3, contract_path, "--contract"),
            (5, literature_path, "--literature"),
        )
    for index, expected in expected_literals.items():
        if argv[index] != expected:
            errors.append(
                f"implementation.command_argv[{index}]: expected {expected!r}, "
                f"got {argv[index]!r}"
            )
    for index, expected_path, label in path_records:
        try:
            actual_path = Path(argv[index]).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            errors.append(f"implementation.command_argv {label}: {exc}")
            continue
        if actual_path != expected_path:
            errors.append(f"implementation.command_argv {label}: path binding mismatch")


def validate_resource_metrics(value: Any, errors: list[str]) -> None:
    keys = {
        "builder_operations",
        "memory_measurement",
        "wall_clock_ns",
        "diagnostic_only",
        "attestation",
    }
    if not validate_exact_keys(value, keys, "resource_metrics", errors):
        return
    operation_keys = {
        "point_add_calls",
        "point_doublings",
        "field_inversions",
        "field_multiplications",
        "multiset_evaluations",
        "injectivity_checks",
        "associativity_triples",
        "optimizer_nodes",
    }
    operations = value["builder_operations"]
    if validate_exact_keys(
        operations, operation_keys, "resource_metrics.builder_operations", errors
    ):
        for key, item in operations.items():
            require_exact_int(
                item,
                f"resource_metrics.builder_operations.{key}",
                errors,
                minimum=0,
            )
        compare_exact(
            EXPECTED_BUILDER_OPERATIONS,
            operations,
            "resource_metrics.builder_operations",
            errors,
        )
    expected_memory_keys = {"kind", "bytes", "is_peak_process_memory"}
    memory = value["memory_measurement"]
    if validate_exact_keys(
        memory, expected_memory_keys, "resource_metrics.memory_measurement", errors
    ):
        compare_exact(
            "deep_size_of_final_document_object_graph_before_resource_record",
            memory["kind"],
            "resource_metrics.memory_measurement.kind",
            errors,
        )
        require_exact_int(
            memory["bytes"],
            "resource_metrics.memory_measurement.bytes",
            errors,
            minimum=1,
            maximum=1_073_741_824,
        )
        if memory["is_peak_process_memory"] is not False:
            errors.append(
                "resource_metrics.memory_measurement.is_peak_process_memory: expected false"
            )
    require_exact_int(
        value["wall_clock_ns"],
        "resource_metrics.wall_clock_ns",
        errors,
        minimum=1,
        maximum=300_000_000_000,
    )
    if value["diagnostic_only"] is not True:
        errors.append("resource_metrics.diagnostic_only: expected exact true")
    compare_exact(
        "BUILDER_SELF_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
        value["attestation"],
        "resource_metrics.attestation",
        errors,
    )


def scalar_gate_errors(row_reports: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for row_report in row_reports:
        factor_base_size = row_report["B"]
        for key in (
            "p0_scalar_compatibility_valid",
            "p2_scalar_compatibility_valid",
        ):
            if row_report[key] is not True:
                errors.append(
                    f"B={factor_base_size} {key}: expected independently verified true"
                )
        if row_report["p1_scalar_compatibility_valid"] is not None:
            errors.append(
                f"B={factor_base_size} P1 scalar result must be not-applicable after rejection"
            )
    return errors


def verify_certificate_document(
    certificate: Any,
    *,
    certificate_sha256: str,
    input_path: Path,
    contract_path: Path,
    literature_path: Path,
    enforce_execution_context: bool = True,
    external_runner_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    started_ns = time.perf_counter_ns()
    errors: list[str] = []
    validate_json_number_types(certificate, "certificate", errors)
    independence_errors = source_independence_errors()
    named_scalar_material_errors = scalar_material_errors(certificate)
    errors.extend(independence_errors)
    errors.extend(named_scalar_material_errors)

    try:
        contract_path = require_bound_file(
            contract_path,
            MATHEMATICAL_CONTRACT_PATH,
            MATHEMATICAL_CONTRACT_SHA256,
            "mathematical contract",
        )
    except Exception as exc:
        errors.append(str(exc))
        contract_path = MATHEMATICAL_CONTRACT_PATH.resolve(strict=True)
    try:
        experiment_contract_path = require_bound_file(
            EXPERIMENT_CONTRACT_PATH,
            EXPERIMENT_CONTRACT_PATH,
            EXPERIMENT_CONTRACT_SHA256,
            "experiment contract",
        )
    except Exception as exc:
        errors.append(str(exc))
        experiment_contract_path = EXPERIMENT_CONTRACT_PATH.resolve(strict=True)
    try:
        literature_path = require_bound_file(
            literature_path, LITERATURE_PATH, LITERATURE_SHA256, "literature note"
        )
    except Exception as exc:
        errors.append(str(exc))
        literature_path = LITERATURE_PATH.resolve(strict=True)
    contract_relative = str(contract_path.relative_to(REPO_ROOT))
    experiment_contract_relative = str(
        experiment_contract_path.relative_to(REPO_ROOT)
    )
    literature_relative = str(literature_path.relative_to(REPO_ROOT))

    literature_hash = file_sha256(literature_path)
    if literature_hash != LITERATURE_SHA256:
        errors.append(
            "literature hash mismatch: "
            f"expected {LITERATURE_SHA256}, got {literature_hash}"
        )
    registry_hash = file_sha256(CONTROL_REGISTRY_PATH)
    if registry_hash != CONTROL_REGISTRY_SHA256:
        errors.append(
            "control registry hash mismatch: "
            f"expected {CONTROL_REGISTRY_SHA256}, got {registry_hash}"
        )
    registry_document, _ = read_strict_json(CONTROL_REGISTRY_PATH)
    validate_json_number_types(registry_document, "control_registry", errors)
    if not isinstance(registry_document, dict) or set(registry_document) != {"registry"}:
        errors.append("control registry top-level shape mismatch")
        registry: Mapping[str, Any] = {}
    else:
        registry = registry_document["registry"]
    if isinstance(registry, dict):
        if registry.get("schema") != "sgcp-embed-001-control-registry-v2":
            errors.append("control registry schema mismatch")
        if registry.get("version") != 2:
            errors.append("control registry version mismatch")
        if registry.get("predicate_order") != list(PREDICATE_ORDER):
            errors.append("control registry predicate order mismatch")

    curve, labels, scalar_table, scalar_by_point = independently_build_curve()
    scalar_table_digest = digest_json(
        [point_registry_text(point) for point in scalar_table]
    )
    if scalar_table_digest != SCALAR_TABLE_SHA256:
        errors.append(
            "independent scalar-table digest mismatch: "
            f"expected {SCALAR_TABLE_SHA256}, got {scalar_table_digest}"
        )
    scalar_index_oracle: dict[str, Any] | None = None
    try:
        scalar_index_oracle = load_scalar_index_oracle()
    except Exception as exc:
        errors.append(f"independent scalar-index oracle failed: {exc}")
    control_reports: list[dict[str, Any]] = []
    expected_controls: list[dict[str, Any]] = []
    try:
        expected_controls, control_reports = independently_verify_controls(
            registry, curve, labels, scalar_by_point
        )
    except Exception as exc:
        errors.append(f"independent control reconstruction failed: {exc}")

    expected_rows: list[dict[str, Any]] = []
    row_reports: list[dict[str, Any]] = []
    semantic_reports: list[dict[str, Any]] = []
    scalar_index_reports: list[dict[str, Any]] = []
    if expected_controls:
        for factor_base_size in FACTOR_BASE_SIZES:
            try:
                row, row_report = expected_builder_row(
                    curve,
                    labels,
                    scalar_by_point,
                    factor_base_size,
                    expected_controls,
                )
            except Exception as exc:
                errors.append(
                    f"independent row reconstruction failed for B={factor_base_size}: {exc}"
                )
                continue
            expected_rows.append(row)
            row_reports.append(row_report)
        errors.extend(scalar_gate_errors(row_reports))

    top_keys = {
        "schema",
        "experiment_id",
        "claim_status",
        "bindings",
        "implementation",
        "curve",
        "rows",
        "preflight_boundary",
        "resource_metrics",
        "artifact_digests",
    }
    if validate_exact_keys(certificate, top_keys, "certificate", errors):
        compare_exact(CERTIFICATE_SCHEMA, certificate["schema"], "schema", errors)
        compare_exact(EXPERIMENT_ID, certificate["experiment_id"], "experiment_id", errors)
        compare_exact(CLAIM_STATUS, certificate["claim_status"], "claim_status", errors)
        expected_bindings = {
            "contract_path": contract_relative,
            "contract_sha256": file_sha256(contract_path),
            "experiment_contract_path": experiment_contract_relative,
            "experiment_contract_sha256": file_sha256(experiment_contract_path),
            "literature_path": literature_relative,
            "literature_sha256": literature_hash,
            "sggm_pdf_sha256": PAPER_SHA256,
            "control_registry_path": str(CONTROL_REGISTRY_PATH.relative_to(REPO_ROOT)),
            "control_registry_sha256": CONTROL_REGISTRY_SHA256,
        }
        compare_exact(expected_bindings, certificate["bindings"], "bindings", errors)
        compare_exact(
            expected_curve_record(curve, labels), certificate["curve"], "curve", errors
        )
        if len(expected_rows) == len(FACTOR_BASE_SIZES):
            compare_exact(expected_rows, certificate["rows"], "rows", errors)
            if isinstance(certificate["rows"], list) and len(certificate["rows"]) == len(
                FACTOR_BASE_SIZES
            ):
                for factor_base_size, actual_row in zip(
                    FACTOR_BASE_SIZES, certificate["rows"]
                ):
                    try:
                        semantic_report = semantic_differential_check(
                            actual_row,
                            curve,
                            labels,
                            scalar_by_point,
                            factor_base_size,
                        )
                    except Exception as exc:
                        semantic_report = {
                            "B": factor_base_size,
                            "valid": False,
                            "semantic_oracle_sha256": None,
                            "errors": [f"semantic differential aborted: {exc}"],
                        }
                    semantic_reports.append(semantic_report)
                    errors.extend(semantic_report["errors"])
                    if scalar_index_oracle is not None:
                        oracle_row = next(
                            row
                            for row in scalar_index_oracle["rows"]
                            if row["B"] == factor_base_size
                        )
                        try:
                            scalar_index_report = scalar_index_oracle_row_check(
                                actual_row,
                                oracle_row,
                                scalar_table,
                                factor_base_size,
                            )
                        except Exception as exc:
                            scalar_index_report = {
                                "B": factor_base_size,
                                "valid": False,
                                "oracle_row_sha256": None,
                                "errors": [
                                    f"scalar-index differential aborted: {exc}"
                                ],
                            }
                        scalar_index_reports.append(scalar_index_report)
                        errors.extend(scalar_index_report["errors"])
        expected_boundary = {
            "contract_version": "3a",
            "toy_bits": [5],
            "factor_base_sizes": [4, 6, 8],
            "larger_rows_executed": False,
            "canonical_run_authorized": False,
        }
        compare_exact(
            expected_boundary,
            certificate["preflight_boundary"],
            "preflight_boundary",
            errors,
        )

        implementation = certificate["implementation"]
        implementation_keys = {
            "execution_mode",
            "provenance",
            "git_commit",
            "git_branch",
            "launch_cwd",
            "tree_clean_before_launch",
            "tree_status_porcelain_v1_before_launch",
            "runtime_isolation",
            "builder_sha256",
            "verifier_sha256",
            "command_argv",
            "timestamp_utc",
        }
        if validate_exact_keys(
            implementation, implementation_keys, "implementation", errors
        ):
            expected_mode = (
                "locked_runner_stdout_json"
                if enforce_execution_context
                else "development_direct"
            )
            expected_provenance = (
                "EXTERNAL_LOCKED_RUNNER_RECEIPT_ONLY"
                if enforce_execution_context
                else "BUILDER_SELF_REPORTED_DEVELOPMENT_CONTEXT"
            )
            compare_exact(
                expected_mode,
                implementation["execution_mode"],
                "implementation.execution_mode",
                errors,
            )
            compare_exact(
                expected_provenance,
                implementation["provenance"],
                "implementation.provenance",
                errors,
            )
            compare_exact(
                str(REPO_ROOT.resolve()),
                implementation["launch_cwd"],
                "implementation.launch_cwd",
                errors,
            )
            if enforce_execution_context:
                compare_exact(
                    None,
                    implementation["git_commit"],
                    "implementation.git_commit",
                    errors,
                )
                compare_exact(
                    None,
                    implementation["git_branch"],
                    "implementation.git_branch",
                    errors,
                )
                compare_exact(
                    None,
                    implementation["tree_clean_before_launch"],
                    "implementation.tree_clean_before_launch",
                    errors,
                )
                compare_exact(
                    None,
                    implementation["tree_status_porcelain_v1_before_launch"],
                    "implementation.tree_status_porcelain_v1_before_launch",
                    errors,
                )
                expected_runtime = {
                    "isolated": True,
                    "no_site": True,
                    "dont_write_bytecode": True,
                }
            else:
                compare_exact(
                    git_head(REPO_ROOT),
                    implementation["git_commit"],
                    "implementation.git_commit",
                    errors,
                )
                compare_exact(
                    git_text("branch", "--show-current"),
                    implementation["git_branch"],
                    "implementation.git_branch",
                    errors,
                )
                current_status = git_text(
                    "status", "--porcelain=v1", "--untracked-files=all"
                )
                compare_exact(
                    current_status == "",
                    implementation["tree_clean_before_launch"],
                    "implementation.tree_clean_before_launch",
                    errors,
                )
                compare_exact(
                    current_status,
                    implementation["tree_status_porcelain_v1_before_launch"],
                    "implementation.tree_status_porcelain_v1_before_launch",
                    errors,
                )
                expected_runtime = {
                    "isolated": bool(sys.flags.isolated),
                    "no_site": bool(sys.flags.no_site),
                    "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
                }
            compare_exact(
                expected_runtime,
                implementation["runtime_isolation"],
                "implementation.runtime_isolation",
                errors,
            )
            compare_exact(
                file_sha256(BUILDER_PATH),
                implementation["builder_sha256"],
                "implementation.builder_sha256",
                errors,
            )
            compare_exact(
                file_sha256(SCRIPT_PATH),
                implementation["verifier_sha256"],
                "implementation.verifier_sha256",
                errors,
            )
            validate_builder_argv(
                implementation["command_argv"],
                contract_path,
                literature_path,
                input_path,
                enforce_execution_context,
                errors,
            )
            timestamp = implementation["timestamp_utc"]
            if not isinstance(timestamp, str) or re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", timestamp
            ) is None:
                errors.append(
                    "implementation.timestamp_utc: expected second-resolution UTC timestamp"
                )
            elif enforce_execution_context:
                if external_runner_provenance is None:
                    errors.append(
                        "locked-run verification requires predecessor runner provenance"
                    )
                else:
                    compare_exact(
                        implementation["command_argv"],
                        external_runner_provenance["argv"],
                        "external_runner_provenance.argv",
                        errors,
                    )
                    started_at = datetime.fromisoformat(
                        external_runner_provenance["started_at"].replace("Z", "+00:00")
                    )
                    finished_at = datetime.fromisoformat(
                        external_runner_provenance["finished_at"].replace("Z", "+00:00")
                    )
                    certificate_time = datetime.strptime(
                        timestamp, "%Y-%m-%dT%H:%M:%SZ"
                    ).replace(tzinfo=timezone.utc)
                    if not (
                        started_at - timedelta(seconds=1)
                        <= certificate_time
                        <= finished_at
                    ):
                        errors.append(
                            "implementation.timestamp_utc: outside predecessor runner interval"
                        )

        validate_resource_metrics(certificate["resource_metrics"], errors)
        if len(expected_rows) == len(FACTOR_BASE_SIZES):
            deterministic_payload = {
                key: value
                for key, value in certificate.items()
                if key not in {"implementation", "resource_metrics", "artifact_digests"}
            }
            expected_artifact_digests = {
                "public_model_sha256": digest_json(
                    [row["public_model"] for row in expected_rows]
                ),
                "private_audit_sha256": digest_json(
                    [row["private_audit"] for row in expected_rows]
                ),
                "controls_sha256": digest_json(expected_controls),
                "deterministic_payload_sha256": digest_json(deterministic_payload),
                "execution_receipt_sha256": digest_json(
                    {
                        "implementation": certificate["implementation"],
                        "resource_metrics": certificate["resource_metrics"],
                    }
                ),
                "builder_sha256": file_sha256(BUILDER_PATH),
                "verifier_sha256": file_sha256(SCRIPT_PATH),
            }
            compare_exact(
                expected_artifact_digests,
                certificate["artifact_digests"],
                "artifact_digests",
                errors,
            )

    report = {
        "schema": REPORT_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "claim_status": CLAIM_STATUS,
        "valid": not errors,
        "input": {
            "path": str(input_path),
            "sha256": certificate_sha256,
        },
        "bindings": {
            "contract_sha256": file_sha256(contract_path),
            "experiment_contract_sha256": file_sha256(experiment_contract_path),
            "literature_sha256": literature_hash,
            "control_registry_sha256": registry_hash,
            "builder_sha256": file_sha256(BUILDER_PATH),
            "verifier_sha256": file_sha256(SCRIPT_PATH),
            "scalar_index_oracle_source_sha256": file_sha256(
                SCALAR_INDEX_ORACLE_SOURCE_PATH
            ),
            "scalar_index_oracle_artifact_sha256": file_sha256(
                SCALAR_INDEX_ORACLE_ARTIFACT_PATH
            ),
            "git_commit": None if enforce_execution_context else git_head(REPO_ROOT),
            "git_provenance": (
                "EXTERNAL_LOCKED_RUNNER_RECEIPT_ONLY"
                if enforce_execution_context
                else "DEVELOPMENT_GIT_QUERY"
            ),
        },
        "independent_ground_truth": {
            "curve_order": CURVE_Q,
            "scalar_table_entry_count": len(scalar_table),
            "scalar_table_sha256": scalar_table_digest,
            "scalar_table_representation": "canonical JSON array of O-or-x:y labels in scalar order",
            "certificate_forbidden_scalar_named_fields_absent": not named_scalar_material_errors,
            "covert_scalar_encoding_excluded": False,
            "diagnostic_integer_channels_range_bounded": True,
            "scope": (
                "syntactic forbidden-field gate plus bounded diagnostic integers; "
                "no general information-flow or covert-channel attestation"
            ),
        },
        "source_independence": {
            "valid": not independence_errors,
            "builder_imported_by_verifier": False,
            "shared_scalar_table": False,
            "scalar_index_oracle_imports_existing_implementations": False,
        },
        "external_runner_provenance": (
            None
            if external_runner_provenance is None
            else {
                key: external_runner_provenance[key]
                for key in (
                    "run_id",
                    "raw_result_sha256",
                    "manifest_sha256",
                    "receipt_sha256",
                    "approved_base_commit",
                    "launch_commit",
                    "started_at",
                    "finished_at",
                )
            }
        ),
        "controls": control_reports,
        "rows": row_reports,
        "semantic_differential": semantic_reports,
        "scalar_index_differential": {
            "source_sha256": file_sha256(SCALAR_INDEX_ORACLE_SOURCE_PATH),
            "artifact_sha256": file_sha256(SCALAR_INDEX_ORACLE_ARTIFACT_PATH),
            "runtime_matches_frozen_artifact": scalar_index_oracle is not None,
            "representation": "independent_scalar_indices_mod_q",
            "rows": scalar_index_reports,
        },
        "errors": errors,
        "claim_boundary": (
            "verification of a five-bit implementation preflight only; no ECDLP, "
            "exponent, relation, rank, descent, or conventional-coordinate lower-bound claim"
        ),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    report["verification_resource_metrics"] = {
        "operation_counts": {
            "scalar_multiplication_ground_truth_calls": CURVE_Q + 1,
            "exact_row_reconstructions": len(row_reports),
            "semantic_differential_reconstructions": len(semantic_reports),
            "scalar_index_oracle_reconstructions": (
                1 if scalar_index_oracle is not None else 0
            ),
            "exhaustive_valid_subset_comparisons": 2
            * sum(
                row["private_audit"]["optimizer_proof"][
                    "direct_subset_comparisons"
                ]
                for row in expected_rows
            ),
        },
        "wall_clock_ns": time.perf_counter_ns() - started_ns,
        "process_ru_maxrss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "process_ru_maxrss_units": (
            "bytes" if sys.platform == "darwin" else "platform-dependent"
        ),
        "diagnostic_only": True,
    }
    return report


def ensure_report_output(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != REPORT_PATH.resolve():
        raise ValueError(f"verification output must be exactly {REPORT_PATH}")
    if not resolved.is_relative_to(REPO_ROOT.resolve()) or resolved.is_relative_to(
        FROZEN_REVIEW_ROOT.resolve()
    ):
        raise ValueError("verification output resolves outside the SGCP evidence directory")
    if resolved.exists():
        raise FileExistsError(f"refusing to overwrite existing report: {resolved}")
    return resolved


def require_locked_runner_runtime() -> None:
    if Path.cwd().resolve() != REPO_ROOT.resolve():
        raise AssertionError(f"locked runner cwd must be {REPO_ROOT}")
    observed = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "dont_write_bytecode": bool(sys.flags.dont_write_bytecode),
    }
    if observed != {"isolated": True, "no_site": True, "dont_write_bytecode": True}:
        raise AssertionError(
            "locked runner requires Python isolation flags -I -S -B; "
            f"observed {observed}"
        )


def load_locked_runner_predecessor(
    input_path: Path,
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    lexical_input = input_path if input_path.is_absolute() else Path.cwd() / input_path
    if lexical_input.is_symlink() or lexical_input.parent.is_symlink():
        raise ValueError("locked verifier input and run directory must not be symlinks")
    resolved = input_path.resolve(strict=True)
    runs_root = (SCRIPT_PATH.parents[1] / "runs").resolve()
    if resolved.parent.parent != runs_root or resolved.name != "raw-result.json":
        raise ValueError("locked verifier input must be a predecessor run raw-result.json")
    run_id = resolved.parent.name
    if re.fullmatch(r"RUN-SGCP-EMBED-[0-9]{3,}", run_id) is None:
        raise ValueError(f"unexpected SGCP predecessor run ID: {run_id}")
    wrapper, raw = read_strict_json(resolved)
    expected_wrapper_keys = {
        "valid",
        "artifact_kind",
        "certificate",
        "summary",
        "claim_boundary",
    }
    wrapper_errors: list[str] = []
    validate_exact_keys(wrapper, expected_wrapper_keys, "predecessor", wrapper_errors)
    if wrapper_errors:
        raise AssertionError(wrapper_errors[0])
    if wrapper["valid"] is not True:
        raise AssertionError("predecessor builder result is not exact valid=true")
    if wrapper["artifact_kind"] != "sgcp-embed-001-builder-certificate":
        raise AssertionError("predecessor artifact kind mismatch")

    manifest_path = resolved.parent / "manifest.json"
    receipt_path = resolved.parent / "runner-receipt.json"
    if manifest_path.is_symlink() or receipt_path.is_symlink():
        raise ValueError("locked predecessor records must not be symlinks")
    manifest, manifest_raw = read_strict_json(manifest_path)
    receipt, receipt_raw = read_strict_json(receipt_path)
    run = manifest["run"]
    runner_receipt = receipt["runner_receipt"]
    raw_sha256 = sha256_bytes(raw)
    if run["id"] != run_id or run["experiment_id"] != RUNNER_EXPERIMENT_ID:
        raise AssertionError("predecessor manifest identity mismatch")
    if run["status"] != "completed_valid" or run["result"]["valid"] is not True:
        raise AssertionError("predecessor manifest is not completed_valid")
    if run["code"]["dirty"] is not False:
        raise AssertionError("predecessor manifest records a dirty launch")
    if runner_receipt["run_id"] != run_id or runner_receipt["role"] != "generator":
        raise AssertionError("predecessor runner receipt identity/role mismatch")
    if runner_receipt["status"] != "completed_valid":
        raise AssertionError("predecessor runner receipt is not completed_valid")
    if runner_receipt["predecessor"] is not None:
        raise AssertionError("generator receipt unexpectedly has a predecessor")
    if runner_receipt["process_group"]["quiescent"] is not True:
        raise AssertionError("predecessor process group is not quiescent")
    if runner_receipt["process_group"]["descendant_policy"] != (
        "forbidden-via-rlimit-nproc-zero"
    ):
        raise AssertionError("predecessor descendant policy mismatch")
    if not all(runner_receipt["post_run_checks"].values()):
        raise AssertionError("predecessor runner post-run checks did not all pass")
    if runner_receipt["artifacts"]["raw-result.json"]["sha256"] != raw_sha256:
        raise AssertionError("predecessor receipt raw-result hash mismatch")
    if run["artifacts"]["raw-result.json"]["sha256"] != raw_sha256:
        raise AssertionError("predecessor manifest raw-result hash mismatch")
    provenance = {
        "run_id": run_id,
        "raw_result_sha256": raw_sha256,
        "manifest_sha256": sha256_bytes(manifest_raw),
        "receipt_sha256": sha256_bytes(receipt_raw),
        "approved_base_commit": runner_receipt["approved_base_commit"],
        "launch_commit": runner_receipt["launch_commit"],
        "argv": runner_receipt["argv"],
        "started_at": run["timing"]["started_at"],
        "finished_at": run["timing"]["finished_at"],
    }
    return wrapper["certificate"], raw, provenance


def require_verification_context(input_path: Path, output_path: Path) -> tuple[Path, Path]:
    resolved_input = input_path.resolve(strict=True)
    resolved_output = output_path.resolve()
    if Path.cwd().resolve() != REPO_ROOT.resolve():
        raise AssertionError(f"canonical verifier cwd must be {REPO_ROOT}")
    if git_text("branch", "--show-current") != EXPECTED_BRANCH:
        raise AssertionError(f"canonical verifier branch must be {EXPECTED_BRANCH}")
    if resolved_input != CERTIFICATE_PATH.resolve():
        raise ValueError(f"verification input must be exactly {CERTIFICATE_PATH}")
    resolved_output = ensure_report_output(resolved_output)
    expected_status = f"?? {resolved_input.relative_to(REPO_ROOT)}"
    actual_status = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if actual_status != expected_status:
        raise AssertionError(
            "verifier worktree must differ from the frozen source commit only by "
            f"the input certificate; expected {expected_status!r}, got {actual_status!r}"
        )
    return resolved_input, resolved_output


def write_report_atomic(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="ascii",
        dir=path.parent,
        prefix=f".{path.name}.tmp-",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(
            report,
            handle,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
        )
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--literature", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--runner-json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.runner_json:
        require_locked_runner_runtime()
        input_path = args.input.resolve(strict=True)
        output_path = None
    else:
        assert args.output is not None
        input_path, output_path = require_verification_context(
            args.input, args.output
        )
    raw = input_path.read_bytes()
    try:
        if args.runner_json:
            certificate, loaded_raw, provenance = load_locked_runner_predecessor(
                input_path
            )
            if loaded_raw != raw:
                raise AssertionError("predecessor raw-result changed while loading")
        else:
            certificate = strict_json_load_bytes(raw, str(input_path))
            provenance = None
        report = verify_certificate_document(
            certificate,
            certificate_sha256=sha256_bytes(raw),
            input_path=input_path,
            contract_path=args.contract,
            literature_path=args.literature,
            enforce_execution_context=args.runner_json,
            external_runner_provenance=provenance,
        )
    except Exception as exc:
        report = {
            "schema": REPORT_SCHEMA,
            "experiment_id": EXPERIMENT_ID,
            "claim_status": CLAIM_STATUS,
            "valid": False,
            "input": {"path": str(input_path), "sha256": sha256_bytes(raw)},
            "errors": [f"verification aborted: {type(exc).__name__}: {exc}"],
            "claim_boundary": (
                "invalid five-bit implementation preflight; no cryptanalytic claim"
            ),
        }
    if args.runner_json:
        print(
            json.dumps(
                report,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
        )
    else:
        assert output_path is not None
        write_report_atomic(output_path, report)
        print(output_path)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

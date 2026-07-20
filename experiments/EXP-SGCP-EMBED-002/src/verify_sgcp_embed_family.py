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
import stat
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


LEGACY_SCHEMAS = {
    "sgcp-embed-002-development-v1",
    "sgcp-embed-002-density-frontier-development-v2",
    "sgcp-embed-002-density-frontier-candidate-v3",
    "sgcp-embed-002-density-frontier-candidate-v4",
    "sgcp-embed-002-density-frontier-candidate-v5",
}
CURRENT_SCHEMA = "sgcp-embed-002-density-frontier-candidate-v6"
VERIFICATION_SCHEMA = "sgcp-embed-002-development-verification-v6"
EXPERIMENT_ID = "EXP-SGCP-EMBED-002"
PROTOCOL_VERSION = 6
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
MAXIMUM_INPUT_BYTES = 268_435_456
MAXIMUM_JSON_NODES = 2_000_000
MAXIMUM_JSON_DEPTH = 64
MAXIMUM_JSON_STRING_BYTES = 8_388_608
MAXIMUM_PRIMARY_NODES = 5_000_000
MAXIMUM_REPLAY_NODES_PER_CAP = CANONICAL_NODE_CAP
MAXIMUM_ROW_FACTOR_BASE_SIZE = max(CANONICAL_FACTOR_BASE_SIZES)
MAXIMUM_CANONICAL_ROWS = (
    len(CANONICAL_BITS)
    * len(CANONICAL_SEEDS)
    * len(CANONICAL_FACTOR_BASE_SIZES)
    * (len(COORDINATE_FAMILIES) + CANONICAL_NULL_REPLICATES)
)
MAXIMUM_CAPS_PER_ROW = 4
MAXIMUM_TOTAL_REPLAY_NODES = (
    MAXIMUM_CANONICAL_ROWS * MAXIMUM_CAPS_PER_ROW * MAXIMUM_REPLAY_NODES_PER_CAP
)
MAXIMUM_TOTAL_PRIMARY_NODES = (
    MAXIMUM_CANONICAL_ROWS * MAXIMUM_CAPS_PER_ROW * MAXIMUM_PRIMARY_NODES
)
MAXIMUM_EXPANSION_CELLS_PER_ROW = sum(
    math.comb(MAXIMUM_ROW_FACTOR_BASE_SIZE + degree - 1, degree)
    for degree in (1, 2, 4, 8)
)
MAXIMUM_TOTAL_EXPANSION_CELLS = (
    MAXIMUM_CANONICAL_ROWS * MAXIMUM_EXPANSION_CELLS_PER_ROW
)
_MAXIMUM_DEGREE4_CANDIDATES = math.comb(MAXIMUM_ROW_FACTOR_BASE_SIZE + 3, 4)
MAXIMUM_GRAPH_CELLS_PER_ROW = (
    _MAXIMUM_DEGREE4_CANDIDATES
    + math.comb(_MAXIMUM_DEGREE4_CANDIDATES, 2)
    + _MAXIMUM_DEGREE4_CANDIDATES**2
)
MAXIMUM_TOTAL_GRAPH_CELLS = MAXIMUM_CANONICAL_ROWS * MAXIMUM_GRAPH_CELLS_PER_ROW
MAXIMUM_REPLAY_CACHE_ENTRIES_PER_CAP = (
    MAXIMUM_REPLAY_NODES_PER_CAP + _MAXIMUM_DEGREE4_CANDIDATES**2 + 64
)
MAXIMUM_PRIMARY_CACHE_ENTRIES_PER_CAP = 2 * (MAXIMUM_PRIMARY_NODES + 1)
MAXIMUM_TOTAL_METRIC_CACHE_ENTRIES = (
    MAXIMUM_CANONICAL_ROWS
    * MAXIMUM_CAPS_PER_ROW
    * (
        2 * MAXIMUM_REPLAY_CACHE_ENTRIES_PER_CAP
        + MAXIMUM_PRIMARY_CACHE_ENTRIES_PER_CAP
    )
)
MAXIMUM_RETAINED_MODEL_CALLS_PER_CAP = (
    MAXIMUM_REPLAY_CACHE_ENTRIES_PER_CAP + MAXIMUM_PRIMARY_NODES + 2
)
_MAXIMUM_FORMAL_FAMILY_SIZE = sum(
    math.comb(MAXIMUM_ROW_FACTOR_BASE_SIZE + degree - 1, degree)
    for degree in range(5)
)
MAXIMUM_RETAINED_MODEL_CELLS_PER_CALL = (
    _MAXIMUM_FORMAL_FAMILY_SIZE
    + math.comb(_MAXIMUM_FORMAL_FAMILY_SIZE, 2)
)
MAXIMUM_TOTAL_RETAINED_MODEL_CALLS = (
    MAXIMUM_CANONICAL_ROWS
    * MAXIMUM_CAPS_PER_ROW
    * MAXIMUM_RETAINED_MODEL_CALLS_PER_CAP
)
MAXIMUM_TOTAL_RETAINED_MODEL_CELLS = (
    MAXIMUM_TOTAL_RETAINED_MODEL_CALLS
    * MAXIMUM_RETAINED_MODEL_CELLS_PER_CALL
)
MAXIMUM_REGISTERED_CURVE_DRAWS = (
    len(CANONICAL_BITS) * len(CANONICAL_SEEDS) * 100_000
)
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


def bounded_json_errors(value: Any, path: str = "document") -> list[str]:
    """Validate a finite JSON-shaped value without recursive traversal."""
    errors: list[str] = []
    nodes = 0
    stack: list[tuple[Any, str, int]] = [(value, path, 0)]
    while stack:
        child, child_path, depth = stack.pop()
        nodes += 1
        if nodes > MAXIMUM_JSON_NODES:
            return [f"JSON node ceiling exceeded at {child_path}"]
        if depth > MAXIMUM_JSON_DEPTH:
            return [f"JSON depth ceiling exceeded at {child_path}"]
        if child is None or type(child) in {bool, int, float}:
            if type(child) is float and not math.isfinite(child):
                errors.append(f"non-finite JSON number at {child_path}")
            continue
        if type(child) is str:
            try:
                encoded_length = len(child.encode("ascii"))
            except UnicodeEncodeError:
                errors.append(f"non-ASCII JSON string at {child_path}")
                continue
            if encoded_length > MAXIMUM_JSON_STRING_BYTES:
                errors.append(f"JSON string ceiling exceeded at {child_path}")
            continue
        if type(child) is list:
            if len(child) > MAXIMUM_JSON_NODES - nodes:
                return [f"JSON node ceiling exceeded at {child_path}"]
            for index in range(len(child) - 1, -1, -1):
                stack.append((child[index], f"{child_path}[{index}]", depth + 1))
            continue
        if type(child) is dict:
            if len(child) > MAXIMUM_JSON_NODES - nodes:
                return [f"JSON node ceiling exceeded at {child_path}"]
            for key, item in reversed(child.items()):
                if type(key) is not str:
                    errors.append(f"non-string JSON object key at {child_path}")
                    continue
                try:
                    key_length = len(key.encode("ascii"))
                except UnicodeEncodeError:
                    errors.append(f"non-ASCII JSON object key at {child_path}")
                    continue
                if key_length > MAXIMUM_JSON_STRING_BYTES:
                    errors.append(f"JSON object-key ceiling exceeded at {child_path}")
                    continue
                stack.append((item, f"{child_path}.{key}", depth + 1))
            continue
        errors.append(f"non-JSON value of type {type(child).__name__} at {child_path}")
    return errors


def maximum_nodes_errors(maximum_nodes: Any) -> list[str]:
    if type(maximum_nodes) is not int:
        return ["maximum primary nodes is not an exact integer"]
    if not 0 <= maximum_nodes <= MAXIMUM_PRIMARY_NODES:
        return [
            f"maximum primary nodes is outside 0..{MAXIMUM_PRIMARY_NODES}"
        ]
    return []


def exact_type(value: Any, expected: type, path: str, errors: list[str]) -> bool:
    if type(value) is not expected:
        errors.append(
            f"exact type mismatch at {path}: expected {expected.__name__}, "
            f"got {type(value).__name__}"
        )
        return False
    return True


def exact_integer(value: Any, path: str, errors: list[str]) -> bool:
    return exact_type(value, int, path, errors)


def exact_boolean(value: Any, path: str, errors: list[str]) -> bool:
    return exact_type(value, bool, path, errors)


def exact_string(value: Any, path: str, errors: list[str]) -> bool:
    return exact_type(value, str, path, errors)


def exact_float(value: Any, path: str, errors: list[str]) -> bool:
    return exact_type(value, float, path, errors)


def exact_integer_list(value: Any, path: str, errors: list[str]) -> None:
    if not exact_type(value, list, path, errors):
        return
    for index, child in enumerate(value):
        exact_integer(child, f"{path}[{index}]", errors)


def exact_string_list(value: Any, path: str, errors: list[str]) -> None:
    if not exact_type(value, list, path, errors):
        return
    for index, child in enumerate(value):
        exact_string(child, f"{path}[{index}]", errors)


def exact_formal(value: Any, path: str, errors: list[str]) -> None:
    exact_integer_list(value, path, errors)


def exact_point_record(value: Any, path: str, errors: list[str]) -> None:
    if type(value) is str:
        if value != "O":
            errors.append(f"invalid identity point record at {path}")
        return
    if not exact_type(value, list, path, errors):
        return
    if len(value) != 2:
        errors.append(f"affine point record at {path} does not have two coordinates")
        return
    exact_integer(value[0], f"{path}[0]", errors)
    exact_integer(value[1], f"{path}[1]", errors)


def exact_ratio_record(value: Any, path: str, errors: list[str]) -> None:
    if not exact_type(value, dict, path, errors):
        return
    if set(value) != {"numerator", "denominator"}:
        errors.append(f"ratio keys mismatch at {path}")
        return
    exact_integer(value["numerator"], f"{path}.numerator", errors)
    exact_integer(value["denominator"], f"{path}.denominator", errors)


def exact_integer_histogram(value: Any, path: str, errors: list[str]) -> None:
    if not exact_type(value, dict, path, errors):
        return
    for key, count in value.items():
        exact_string(key, f"{path}.key", errors)
        exact_integer(count, f"{path}[{key!r}]", errors)


def exact_digest(value: Any, path: str, errors: list[str]) -> None:
    if not exact_string(value, path, errors):
        return
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        errors.append(f"invalid lowercase SHA-256 digest at {path}")


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


def strict_json_load(raw: bytes, source: Path) -> Any:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate key {key!r} in {source}")
            result[key] = value
        return result

    def constant(value: str) -> Any:
        raise ValueError(f"non-finite constant {value!r} in {source}")

    text = raw.decode("ascii")
    return json.loads(
        text,
        object_pairs_hook=pairs,
        parse_constant=constant,
    )


def read_input_snapshot(path: Path) -> tuple[bytes, str]:
    """Read one regular-file snapshot used for both hashing and parsing."""
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if not hasattr(os, "O_NOFOLLOW"):
        raise RuntimeError("platform lacks the required no-follow open flag")
    flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("input is not a regular file")
        blocks: list[bytes] = []
        size = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            size += len(block)
            if size > MAXIMUM_INPUT_BYTES:
                raise ValueError(
                    f"input byte ceiling exceeded: {size} > {MAXIMUM_INPUT_BYTES}"
                )
            blocks.append(block)
        after = os.fstat(descriptor)
        before_identity = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if before_identity != after_identity or size != after.st_size:
            raise ValueError("input changed while its snapshot was read")
        raw = b"".join(blocks)
        return raw, hashlib.sha256(raw).hexdigest()
    finally:
        os.close(descriptor)


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


def ordered_independent_rejection_reasons(
    p: int, a: int, b: int, bits_value: int, duplicate: bool
) -> tuple[list[str], int | None]:
    reasons, q = independent_rejection_reasons(p, a, b, bits_value)
    return (["duplicate_candidate"] if duplicate else []) + reasons, q


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


_REGISTERED_CURVE_CACHE: dict[
    tuple[int, int], tuple[Curve, tuple[Point, ...], dict[str, Any]]
] = {}


def registered_curve_bundle(
    bits_value: int, seed: int
) -> tuple[Curve, tuple[Point, ...], dict[str, Any]]:
    """Derive one preregistered curve without following an input draw count."""
    key = (bits_value, seed)
    if bits_value not in CANONICAL_BITS or seed not in CANONICAL_SEEDS:
        raise AssertionError("curve bits/seed are outside the registered grid")
    if key in _REGISTERED_CURVE_CACHE:
        return _REGISTERED_CURVE_CACHE[key]

    primes = [
        value
        for value in range(1 << (bits_value - 1), 1 << bits_value)
        if value > 3 and is_prime(value)
    ]
    seen: set[tuple[int, int, int]] = set()
    rejections: list[dict[str, Any]] = []
    for draw in range(100000):
        p = primes[hash_mod("sgcp-002-curve-p", [bits_value, seed, draw], len(primes))]
        a = hash_mod("sgcp-002-curve-a", [bits_value, seed, draw, p], p)
        b = hash_mod("sgcp-002-curve-b", [bits_value, seed, draw, p], p)
        curve_key = (p, a, b)
        duplicate = curve_key in seen
        if not duplicate:
            seen.add(curve_key)
        reasons, rejection_q = ordered_independent_rejection_reasons(
            p, a, b, bits_value, duplicate
        )
        if rejection_q is None:
            rejections.append(
                {"draw": draw, "p": p, "a": a, "b": b, "reasons": reasons}
            )
            continue
        curve = Curve(p, a, b)
        group = tuple(curve.points())
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
        record = independent_curve_record(curve, group, bits_value, seed)
        record.update(
            {
                "draw": draw,
                "rejected_draws": rejections,
                "rejection_count": len(rejections),
                "rejection_digest": digest(rejections),
            }
        )
        _REGISTERED_CURVE_CACHE[key] = (curve, group, record)
        return _REGISTERED_CURVE_CACHE[key]
    raise AssertionError("registered curve derivation exhausted its fixed draw ceiling")


def frozen_curve_record() -> tuple[Curve, tuple[Point, ...], dict[str, Any]]:
    curve = Curve(FROZEN_FIXTURE["p"], FROZEN_FIXTURE["a"], FROZEN_FIXTURE["b"])
    group = tuple(curve.points())
    expected = independent_curve_record(curve, group, FROZEN_FIXTURE["bits"], 5)
    expected.update(
        {
            "draw": None,
            "rejected_draws": [],
            "rejection_count": 0,
            "rejection_digest": digest([]),
        }
    )
    return curve, group, expected


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
        curve, _, expected = frozen_curve_record()
        if not exact_json_equal(info, expected):
            raise AssertionError("frozen curve provenance mismatch")
        return curve

    if type(info["draw"]) is not int or info["draw"] < 0:
        raise AssertionError("generated curve draw is invalid")
    curve, _, expected = registered_curve_bundle(bits_value, seed)
    if not exact_json_equal(info, expected):
        raise AssertionError("generated curve transcript mismatch")
    return curve


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
        if not exact_json_equal(record["parameters"], {}):
            raise AssertionError("least-x parameters are not empty")
        expected = roots[:required]
        poles: list[int] = []
    elif family == "mobius_interval":
        require_keys(record["parameters"], {"map"}, "Mobius parameters")
        expected_map = derive_mobius(row["curve"], B, family, 0)
        if not exact_json_equal(record["parameters"]["map"], expected_map):
            raise AssertionError("Mobius derivation transcript mismatch")
        ranking, poles = map_ranking(roots, curve.p, expected_map)
        expected = ranking[:required]
    elif family == "two_mobius_union":
        require_keys(
            record["parameters"], {"maps", "alternating_positions"}, "two-map parameters"
        )
        expected_maps = [derive_mobius(row["curve"], B, family, index) for index in range(2)]
        if not exact_json_equal(record["parameters"]["maps"], expected_maps):
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
        if not exact_json_equal(
            positions, record["parameters"]["alternating_positions"]
        ):
            raise AssertionError("two-map positions mismatch")
        poles = sorted(pole_set)
    elif family == "hash_x_null":
        if not exact_json_equal(record["parameters"], {"replicate": replicate}):
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
    if not exact_json_equal(sorted(expected), record["selected_roots"]):
        raise AssertionError("predicate selected-root mismatch")
    if not exact_json_equal(poles, record["excluded_poles"]):
        raise AssertionError("predicate pole audit mismatch")
    if not exact_json_equal(
        polynomial(sorted(expected), curve.p),
        record["root_polynomial_coefficients_ascending_mod_p"],
    ):
        raise AssertionError("root polynomial mismatch")
    factors = sorted(
        (point for root in expected for point in fibers[root]), key=point_order
    )
    if not exact_json_equal(
        ["O" if point is None else [point[0], point[1]] for point in factors],
        record["points"],
    ):
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
    maximum_metric_cache_entries: int | None = None,
) -> dict[str, Any]:
    candidate_count = len(conflicts)
    if maximum_metric_cache_entries is None:
        maximum_metric_cache_entries = (
            node_cap + candidate_count * candidate_count + 64
        )
    metric_cache: dict[int, dict[str, Any]] = {}

    def metrics(mask: int) -> dict[str, Any]:
        if mask not in metric_cache:
            if len(metric_cache) >= maximum_metric_cache_entries:
                raise AssertionError("replay metric-cache entry ceiling exceeded")
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
        "metric_cache_entries": len(metric_cache),
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


def _verify_legacy_row_unchecked(
    row: dict[str, Any], maximum_nodes: int
) -> dict[str, Any]:
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


def verify_row(row: Any, maximum_nodes: Any) -> dict[str, Any]:
    errors = bounded_json_errors(row, "legacy_row")
    errors.extend(maximum_nodes_errors(maximum_nodes))
    if errors:
        return {"valid": False, "errors": errors, "primary_nodes": 0}
    if type(row) is not dict:
        return {
            "valid": False,
            "errors": ["legacy row is not an object"],
            "primary_nodes": 0,
        }
    try:
        return _verify_legacy_row_unchecked(row, maximum_nodes)
    except Exception as error:
        return {
            "valid": False,
            "errors": [
                f"legacy row verifier failure: {type(error).__name__}: {error}"
            ],
            "primary_nodes": 0,
        }


def v6_row_schema_errors(row: Any) -> list[str]:
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
            row["curve"],
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
        for index, rejection in enumerate(row["curve"]["rejected_draws"]):
            expected_rejection_keys = {"draw", "p", "a", "b", "reasons"}
            if isinstance(rejection, dict) and "q" in rejection:
                expected_rejection_keys.add("q")
            require_keys(
                rejection,
                expected_rejection_keys,
                f"curve rejection[{index}]",
            )
        require_keys(
            row["public_model"],
            {
                "factor_base",
                "ordering_contract",
                "representative_compiler",
                "constrained_budget_caps",
                "density_frontier",
            },
            "public model",
        )
        factor = row["public_model"]["factor_base"]
        require_keys(
            factor,
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
        family = row["family"]
        parameters = factor["parameters"]
        if family == "least_x_interval":
            require_keys(parameters, set(), "least-x parameters")
        elif family == "mobius_interval":
            require_keys(parameters, {"map"}, "Mobius parameters")
            require_keys(
                parameters["map"],
                {"u", "v", "w", "determinant", "nonce"},
                "Mobius map",
            )
        elif family == "two_mobius_union":
            require_keys(
                parameters,
                {"maps", "alternating_positions"},
                "two-map parameters",
            )
            for index, map_record in enumerate(parameters["maps"]):
                require_keys(
                    map_record,
                    {"u", "v", "w", "determinant", "nonce"},
                    f"two-map parameters[{index}]",
                )
        elif family == NULL_FAMILY:
            require_keys(parameters, {"replicate"}, "hash-null parameters")
        require_keys(
            row["public_model"]["ordering_contract"],
            set(ORDERING_CONTRACT),
            "ordering contract",
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


def v6_row_type_errors(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for name in ("protocol_version", "B"):
        exact_integer(row[name], f"row.{name}", errors)
    exact_string(row["family"], "row.family", errors)
    if row["null_replicate"] is not None:
        exact_integer(row["null_replicate"], "row.null_replicate", errors)
    exact_boolean(row["valid"], "row.valid", errors)
    exact_float(row["wall_time_seconds"], "row.wall_time_seconds", errors)
    exact_digest(row["row_sha256"], "row.row_sha256", errors)

    curve = row["curve"]
    if exact_type(curve, dict, "row.curve", errors):
        for name in ("bits", "seed", "p", "a", "b", "q", "trace", "j"):
            if name in curve:
                exact_integer(curve[name], f"row.curve.{name}", errors)
        if "generator" in curve:
            exact_point_record(curve["generator"], "row.curve.generator", errors)
        if curve.get("draw") is not None:
            exact_integer(curve["draw"], "row.curve.draw", errors)
        for name in ("rejection_count",):
            if name in curve:
                exact_integer(curve[name], f"row.curve.{name}", errors)
        if "rejection_digest" in curve:
            exact_digest(curve["rejection_digest"], "row.curve.rejection_digest", errors)
        rejected_draws = curve.get("rejected_draws")
        if exact_type(rejected_draws, list, "row.curve.rejected_draws", errors):
            for index, rejection in enumerate(rejected_draws):
                path = f"row.curve.rejected_draws[{index}]"
                if not exact_type(rejection, dict, path, errors):
                    continue
                for name in ("draw", "p", "a", "b"):
                    if name in rejection:
                        exact_integer(rejection[name], f"{path}.{name}", errors)
                if "q" in rejection:
                    exact_integer(rejection["q"], f"{path}.q", errors)
                if "reasons" in rejection:
                    exact_string_list(rejection["reasons"], f"{path}.reasons", errors)

    public_model = row["public_model"]
    factor = public_model["factor_base"]
    for name in ("family",):
        exact_string(factor[name], f"row.public_model.factor_base.{name}", errors)
    if factor["null_replicate"] is not None:
        exact_integer(
            factor["null_replicate"],
            "row.public_model.factor_base.null_replicate",
            errors,
        )
    for name in ("B", "admissible_root_count", "selected_root_count"):
        exact_integer(factor[name], f"row.public_model.factor_base.{name}", errors)
    for name in ("selected_roots", "excluded_poles", "root_polynomial_coefficients_ascending_mod_p"):
        exact_integer_list(factor[name], f"row.public_model.factor_base.{name}", errors)
    if exact_type(factor["points"], list, "row.public_model.factor_base.points", errors):
        for index, point in enumerate(factor["points"]):
            exact_point_record(
                point, f"row.public_model.factor_base.points[{index}]", errors
            )
    exact_boolean(
        factor["negation_symmetric"],
        "row.public_model.factor_base.negation_symmetric",
        errors,
    )
    exact_digest(
        factor["selection_sha256"],
        "row.public_model.factor_base.selection_sha256",
        errors,
    )
    parameters = factor["parameters"]
    if exact_type(parameters, dict, "row.public_model.factor_base.parameters", errors):
        maps: list[tuple[str, Any]] = []
        if "map" in parameters:
            maps.append(("map", parameters["map"]))
        if "maps" in parameters:
            if exact_type(
                parameters["maps"],
                list,
                "row.public_model.factor_base.parameters.maps",
                errors,
            ):
                maps.extend(
                    (f"maps[{index}]", value)
                    for index, value in enumerate(parameters["maps"])
                )
        for suffix, map_record in maps:
            path = f"row.public_model.factor_base.parameters.{suffix}"
            if not exact_type(map_record, dict, path, errors):
                continue
            for name in ("u", "v", "w", "determinant", "nonce"):
                if name in map_record:
                    exact_integer(map_record[name], f"{path}.{name}", errors)
        if "alternating_positions" in parameters:
            exact_integer_list(
                parameters["alternating_positions"],
                "row.public_model.factor_base.parameters.alternating_positions",
                errors,
            )
        if "replicate" in parameters:
            exact_integer(
                parameters["replicate"],
                "row.public_model.factor_base.parameters.replicate",
                errors,
            )

    ordering = public_model["ordering_contract"]
    if exact_type(ordering, dict, "row.public_model.ordering_contract", errors):
        for name in ORDERING_CONTRACT:
            exact_string(
                ordering[name], f"row.public_model.ordering_contract.{name}", errors
            )

    compiler = public_model["representative_compiler"]
    exact_string(compiler["id"], "row.public_model.representative_compiler.id", errors)
    exact_boolean(
        compiler["identity_output_excluded"],
        "row.public_model.representative_compiler.identity_output_excluded",
        errors,
    )
    exact_integer(
        compiler["representative_count"],
        "row.public_model.representative_compiler.representative_count",
        errors,
    )
    if exact_type(
        compiler["representatives"],
        list,
        "row.public_model.representative_compiler.representatives",
        errors,
    ):
        for index, representative in enumerate(compiler["representatives"]):
            path = f"row.public_model.representative_compiler.representatives[{index}]"
            exact_point_record(representative["point"], f"{path}.point", errors)
            exact_formal(representative["formal"], f"{path}.formal", errors)
    exact_digest(
        compiler["representatives_sha256"],
        "row.public_model.representative_compiler.representatives_sha256",
        errors,
    )
    exact_integer_list(
        public_model["constrained_budget_caps"],
        "row.public_model.constrained_budget_caps",
        errors,
    )

    axiom_boolean_names = (
        "identity",
        "commutativity",
        "associativity",
        "compatibility_coordinates",
        "injective_evaluation",
        "unique_prime_multiset_factorization",
        "acyclic_by_formal_degree",
        "source_recovery",
        "source_recovery_via_public_table",
        "direct_final_edge_excluded",
        "direct_final_edge_absent_by_construction",
    )
    public_caps = public_model["density_frontier"]
    if exact_type(public_caps, list, "row.public_model.density_frontier", errors):
        for cap_index, public in enumerate(public_caps):
            path = f"row.public_model.density_frontier[{cap_index}]"
            for name in ("constrained_cap", "formal_family_count", "constrained_count", "public_edge_count"):
                exact_integer(public[name], f"{path}.{name}", errors)
            if exact_type(public["selected_maxima"], list, f"{path}.selected_maxima", errors):
                for index, formal in enumerate(public["selected_maxima"]):
                    exact_formal(formal, f"{path}.selected_maxima[{index}]", errors)
            exact_integer_histogram(
                public["formal_degree_histogram"],
                f"{path}.formal_degree_histogram",
                errors,
            )
            axioms = public["axioms"]
            for name in axiom_boolean_names:
                exact_boolean(axioms[name], f"{path}.axioms.{name}", errors)
            exact_string(
                axioms["associativity_method"],
                f"{path}.axioms.associativity_method",
                errors,
            )
            exact_integer(
                axioms["forbidden_final_edge_count"],
                f"{path}.axioms.forbidden_final_edge_count",
                errors,
            )
            exact_ratio_record(public["delta"], f"{path}.delta", errors)
            for edge_index, edge in enumerate(public["public_edges"]):
                for name in ("left", "right", "output"):
                    exact_string(
                        edge[name], f"{path}.public_edges[{edge_index}].{name}", errors
                    )
            exact_digest(
                public["public_edges_sha256"],
                f"{path}.public_edges_sha256",
                errors,
            )
            for source_index, source in enumerate(public["source_table"]):
                exact_string(
                    source["label"],
                    f"{path}.source_table[{source_index}].label",
                    errors,
                )
                exact_formal(
                    source["formal"],
                    f"{path}.source_table[{source_index}].formal",
                    errors,
                )
            exact_digest(
                public["source_table_sha256"],
                f"{path}.source_table_sha256",
                errors,
            )

    private_audit = row["private_audit"]
    graph = private_audit["graph"]
    for name in (
        "candidate_count",
        "eligible_candidate_count",
        "individually_rejected_count",
        "conflict_count",
        "vertices",
        "edges",
        "component_count",
        "degree_min",
        "degree_max",
        "degeneracy",
    ):
        exact_integer(graph[name], f"row.private_audit.graph.{name}", errors)
    exact_integer_list(graph["components"], "row.private_audit.graph.components", errors)
    exact_integer_histogram(
        graph["degree_histogram"], "row.private_audit.graph.degree_histogram", errors
    )
    exact_integer_list(
        private_audit["eligible_universe_indices"],
        "row.private_audit.eligible_universe_indices",
        errors,
    )
    for index, rejected in enumerate(private_audit["individually_rejected"]):
        path = f"row.private_audit.individually_rejected[{index}]"
        exact_integer(rejected["universe_index"], f"{path}.universe_index", errors)
        exact_formal(rejected["formal"], f"{path}.formal", errors)
        exact_point_record(rejected["point"], f"{path}.point", errors)
        collision = rejected["first_collision"]
        exact_formal(collision["left"], f"{path}.first_collision.left", errors)
        exact_formal(collision["right"], f"{path}.first_collision.right", errors)
        exact_point_record(collision["point"], f"{path}.first_collision.point", errors)
    for index, conflict in enumerate(private_audit["conflicts"]):
        path = f"row.private_audit.conflicts[{index}]"
        for name in ("left", "right", "left_universe_index", "right_universe_index"):
            exact_integer(conflict[name], f"{path}.{name}", errors)
        collision = conflict["first_collision"]
        exact_formal(collision["left"], f"{path}.first_collision.left", errors)
        exact_formal(collision["right"], f"{path}.first_collision.right", errors)
        exact_point_record(collision["point"], f"{path}.first_collision.point", errors)

    private_caps = private_audit["density_frontier"]
    if exact_type(private_caps, list, "row.private_audit.density_frontier", errors):
        for cap_index, private in enumerate(private_caps):
            path = f"row.private_audit.density_frontier[{cap_index}]"
            exact_integer(private["constrained_cap"], f"{path}.constrained_cap", errors)
            exact_float(private["wall_time_seconds"], f"{path}.wall_time_seconds", errors)
            optimizer = private["optimizer"]
            for name in ("objective_mode", "selected_mask_hex", "frontier_sha256", "termination_reason", "bound_method"):
                exact_string(optimizer[name], f"{path}.optimizer.{name}", errors)
            exact_integer(optimizer["max_constrained"], f"{path}.optimizer.max_constrained", errors)
            exact_string_list(
                optimizer["objective_order"], f"{path}.optimizer.objective_order", errors
            )
            exact_integer_list(
                optimizer["selected_indices"], f"{path}.optimizer.selected_indices", errors
            )
            for name in (
                "retained_support_lower_bound",
                "retained_support_upper_bound",
                "absolute_gap",
                "selected_count",
                "constrained_count",
                "public_edge_count",
                "explored_nodes",
                "remaining_frontier_nodes",
                "incumbent_updates",
                "bound_calls",
                "node_cap",
            ):
                exact_integer(optimizer[name], f"{path}.optimizer.{name}", errors)
            for name in ("primary_exact", "full_objective_exact"):
                exact_boolean(optimizer[name], f"{path}.optimizer.{name}", errors)
            if exact_type(optimizer["witness_list"], list, f"{path}.optimizer.witness_list", errors):
                for index, formal in enumerate(optimizer["witness_list"]):
                    exact_formal(formal, f"{path}.optimizer.witness_list[{index}]", errors)
            if exact_type(optimizer["frontier_states"], list, f"{path}.optimizer.frontier_states", errors):
                for state_index, state in enumerate(optimizer["frontier_states"]):
                    state_path = f"{path}.optimizer.frontier_states[{state_index}]"
                    for name in ("selected_mask_hex", "available_mask_hex", "selected_support_mask_hex"):
                        exact_string(state[name], f"{state_path}.{name}", errors)
                    for name in ("support_upper_bound", "selected_count_upper_bound"):
                        exact_integer(state[name], f"{state_path}.{name}", errors)
            exact_digest(optimizer["frontier_sha256"], f"{path}.optimizer.frontier_sha256", errors)

            retention = private["retention"]
            for name in (
                "balanced_raw_final_support",
                "eight_fold_support",
                "retained_final_support",
                "balanced_raw_maximum_multiplicity",
                "retained_maximum_multiplicity",
            ):
                exact_integer(retention[name], f"{path}.retention.{name}", errors)
            for name in (
                "retained_to_balanced_raw",
                "retained_to_eight_fold",
                "absolute_group_coverage",
            ):
                exact_ratio_record(retention[name], f"{path}.retention.{name}", errors)
            for name, value in private["structural_work"].items():
                exact_integer(value, f"{path}.structural_work.{name}", errors)

    for degree, expansion in private_audit["expansion"].items():
        path = f"row.private_audit.expansion[{degree}]"
        for name in (
            "support",
            "formal_multiset_witness_count",
            "formal_multiset_collision_energy",
            "formal_multiset_maximum_multiplicity",
            "ordered_tuple_witness_count",
            "ordered_tuple_additive_energy",
            "ordered_tuple_maximum_multiplicity",
        ):
            exact_integer(expansion[name], f"{path}.{name}", errors)
        exact_integer_histogram(
            expansion["formal_multiset_multiplicity_histogram"],
            f"{path}.formal_multiset_multiplicity_histogram",
            errors,
        )
        exact_integer_histogram(
            expansion["ordered_tuple_multiplicity_histogram"],
            f"{path}.ordered_tuple_multiplicity_histogram",
            errors,
        )

    structural = row["structural_work"]
    exact_string(structural["scope"], "row.structural_work.scope", errors)
    for name, value in structural.items():
        if name != "scope":
            exact_integer(value, f"row.structural_work.{name}", errors)

    accounting = row["accounting"]
    exact_string(accounting["scope"], "row.accounting.scope", errors)
    for name in (
        "public_model_json_bytes",
        "private_audit_json_bytes",
        "row_payload_without_accounting_or_digest_json_bytes",
    ):
        exact_integer(accounting[name], f"row.accounting.{name}", errors)
    if exact_type(
        accounting["nested_per_cap_json_bytes"],
        list,
        "row.accounting.nested_per_cap_json_bytes",
        errors,
    ):
        for index, receipt in enumerate(accounting["nested_per_cap_json_bytes"]):
            for name, value in receipt.items():
                exact_integer(
                    value,
                    f"row.accounting.nested_per_cap_json_bytes[{index}].{name}",
                    errors,
                )
    return errors


def require_independent_exhausted_gate_cell(optimizer: dict[str, Any]) -> None:
    integer_fields = (
        "retained_support_lower_bound",
        "retained_support_upper_bound",
        "absolute_gap",
        "remaining_frontier_nodes",
    )
    if any(type(optimizer.get(name)) is not int for name in integer_fields):
        raise AssertionError("family gate optimizer exactness fields are not integers")
    if type(optimizer.get("frontier_states")) is not list:
        raise AssertionError("family gate optimizer frontier is not a list")
    if not (
        optimizer.get("primary_exact") is True
        and optimizer.get("full_objective_exact") is True
        and optimizer["retained_support_lower_bound"]
        == optimizer["retained_support_upper_bound"]
        and optimizer["absolute_gap"] == 0
        and optimizer["remaining_frontier_nodes"] == 0
        and optimizer["frontier_states"] == []
        and optimizer.get("frontier_sha256") == digest([])
        and optimizer.get("termination_reason") == "full_objective_proved"
    ):
        raise AssertionError("family gate received a nonexhausted optimizer cell")


def expected_caps_for_group(group_size: int) -> list[int]:
    return sorted(
        {
            max(1, group_size // 4),
            max(1, group_size // 2),
            max(1, 3 * group_size // 4),
            group_size,
        }
    )


def registered_row_envelope_errors(
    row: dict[str, Any],
    scope: str,
    maximum_nodes: int,
    expected_node_cap: int | None = None,
) -> list[str]:
    """Reject every nonregistered row association before EC reconstruction."""
    errors: list[str] = []
    curve_info = row["curve"]
    bits_value = curve_info["bits"]
    seed = curve_info["seed"]
    B = row["B"]
    family = row["family"]
    replicate = row["null_replicate"]

    if scope == "frozen_fixture":
        _, _, expected_curve = frozen_curve_record()
        if not exact_json_equal(curve_info, expected_curve):
            errors.append("frozen row curve is not the registered fixture")
        if (B, family, replicate) != (4, "least_x_interval", None):
            errors.append("frozen row grid association mismatch")
    elif scope == "canonical":
        if (
            bits_value not in CANONICAL_BITS
            or seed not in CANONICAL_SEEDS
            or B not in CANONICAL_FACTOR_BASE_SIZES
            or family not in (*COORDINATE_FAMILIES, NULL_FAMILY)
            or (
                family == NULL_FAMILY
                and replicate not in range(CANONICAL_NULL_REPLICATES)
            )
            or (family != NULL_FAMILY and replicate is not None)
        ):
            errors.append("row is outside the registered canonical grid")
        else:
            try:
                _, _, expected_curve = registered_curve_bundle(bits_value, seed)
            except Exception as error:
                errors.append(f"registered curve derivation: {error}")
            else:
                if not exact_json_equal(curve_info, expected_curve):
                    errors.append("canonical row curve transcript mismatch")
    else:
        errors.append("row scope is not registered")

    caps = row["public_model"]["constrained_budget_caps"]
    expected_caps = expected_caps_for_group(curve_info["q"])
    if not exact_json_equal(caps, expected_caps):
        errors.append("registered constrained-cap schedule mismatch")
    for index, cell in enumerate(row["private_audit"]["density_frontier"]):
        node_cap = cell["optimizer"]["node_cap"]
        if node_cap > MAXIMUM_REPLAY_NODES_PER_CAP or node_cap > maximum_nodes:
            errors.append(f"cap[{index}] replay node cap exceeds trusted verifier limit")
        if expected_node_cap is not None and node_cap != expected_node_cap:
            errors.append(f"cap[{index}] registered node-cap association mismatch")
    return errors


def density_row_envelope_errors(
    row: dict[str, Any], maximum_nodes: int
) -> list[str]:
    errors: list[str] = []
    B = row["B"]
    if not 4 <= B <= MAXIMUM_ROW_FACTOR_BASE_SIZE or B % 2:
        errors.append(
            f"factor-base size is outside the even 4..{MAXIMUM_ROW_FACTOR_BASE_SIZE} range"
        )
    caps = row["public_model"]["constrained_budget_caps"]
    public_frontier = row["public_model"]["density_frontier"]
    private_frontier = row["private_audit"]["density_frontier"]
    if not (len(caps) == len(public_frontier) == len(private_frontier) == 4):
        errors.append("density frontier length mismatch")
        return errors
    for index, (cap, public, private) in enumerate(
        zip(caps, public_frontier, private_frontier)
    ):
        if cap <= 0:
            errors.append(f"cap[{index}] is outside 1..q")
        selected_formals = [tuple(value) for value in public["selected_maxima"]]
        if len(selected_formals) != len(set(selected_formals)):
            errors.append(f"cap[{cap}] selected maxima are not unique")
        if selected_formals != sorted(selected_formals):
            errors.append(f"cap[{cap}] selected maxima are not lexicographically ordered")
        for formal in selected_formals:
            if (
                len(formal) != 4
                or formal != tuple(sorted(formal))
                or any(not 0 <= factor_index < B for factor_index in formal)
            ):
                errors.append(f"cap[{cap}] selected maximum is out of range")
        optimizer = private["optimizer"]
        if not 0 <= optimizer["node_cap"] <= min(
            MAXIMUM_REPLAY_NODES_PER_CAP, maximum_nodes
        ):
            errors.append(f"cap[{cap}] optimizer node cap is out of range")
        if optimizer["max_constrained"] <= 0:
            errors.append(f"cap[{cap}] optimizer cap association mismatch")
        selected_indices = optimizer["selected_indices"]
        if selected_indices != sorted(selected_indices) or len(selected_indices) != len(
            set(selected_indices)
        ):
            errors.append(f"cap[{cap}] optimizer indices are not unique and ordered")
        if any(candidate < 0 for candidate in selected_indices):
            errors.append(f"cap[{cap}] optimizer index is out of range")
        try:
            selected_mask = int(optimizer["selected_mask_hex"], 16)
        except ValueError:
            errors.append(f"cap[{cap}] optimizer mask is not hexadecimal")
        else:
            if selected_mask < 0 or optimizer["selected_mask_hex"] != hex(selected_mask):
                errors.append(f"cap[{cap}] optimizer mask is out of range")
    return errors


def density_row_preflight_errors(
    row: dict[str, Any],
    group_size: int,
    eligible: Sequence[dict[str, Any]],
    maximum_nodes: int,
) -> list[str]:
    errors: list[str] = []
    B = row["B"]
    if not 4 <= B <= MAXIMUM_ROW_FACTOR_BASE_SIZE or B % 2:
        errors.append(
            f"factor-base size is outside the even 4..{MAXIMUM_ROW_FACTOR_BASE_SIZE} range"
        )
    expected_caps = expected_caps_for_group(group_size)
    public_model = row["public_model"]
    private_audit = row["private_audit"]
    caps = public_model["constrained_budget_caps"]
    public_frontier = public_model["density_frontier"]
    private_frontier = private_audit["density_frontier"]
    if not exact_json_equal(caps, expected_caps):
        errors.append("constrained-budget cap schedule mismatch")
    if not (
        len(caps) == len(public_frontier) == len(private_frontier) == len(expected_caps)
    ):
        errors.append("density frontier length mismatch")
        return errors

    by_formal = {candidate["formal"]: index for index, candidate in enumerate(eligible)}
    for index, expected_cap in enumerate(expected_caps):
        public = public_frontier[index]
        private = private_frontier[index]
        cap = caps[index]
        if cap <= 0 or cap > group_size:
            errors.append(f"cap[{index}] is outside 1..q")
        if not (
            cap == expected_cap
            and public["constrained_cap"] == expected_cap
            and private["constrained_cap"] == expected_cap
        ):
            errors.append(f"cap[{index}] association mismatch")

        selected_values = public["selected_maxima"]
        selected_formals = [tuple(value) for value in selected_values]
        if len(selected_formals) != len(set(selected_formals)):
            errors.append(f"cap[{expected_cap}] selected maxima are not unique")
        if selected_formals != sorted(selected_formals):
            errors.append(f"cap[{expected_cap}] selected maxima are not lexicographically ordered")
        for formal in selected_formals:
            if (
                len(formal) != 4
                or formal != tuple(sorted(formal))
                or any(not 0 <= factor_index < B for factor_index in formal)
            ):
                errors.append(f"cap[{expected_cap}] selected maximum is out of range")
                continue
            if formal not in by_formal:
                errors.append(f"cap[{expected_cap}] selected maximum is not eligible")

        optimizer = private["optimizer"]
        node_cap = optimizer["node_cap"]
        if not 0 <= node_cap <= min(MAXIMUM_REPLAY_NODES_PER_CAP, maximum_nodes):
            errors.append(f"cap[{expected_cap}] optimizer node cap is out of range")
        if optimizer["max_constrained"] != expected_cap:
            errors.append(f"cap[{expected_cap}] optimizer cap association mismatch")
        selected_indices = optimizer["selected_indices"]
        if selected_indices != sorted(selected_indices) or len(selected_indices) != len(
            set(selected_indices)
        ):
            errors.append(f"cap[{expected_cap}] optimizer indices are not unique and ordered")
        if any(not 0 <= candidate < len(eligible) for candidate in selected_indices):
            errors.append(f"cap[{expected_cap}] optimizer index is out of range")
        try:
            selected_mask = int(optimizer["selected_mask_hex"], 16)
        except ValueError:
            errors.append(f"cap[{expected_cap}] optimizer mask is not hexadecimal")
        else:
            if (
                selected_mask < 0
                or optimizer["selected_mask_hex"] != hex(selected_mask)
                or selected_mask >= 1 << len(eligible)
            ):
                errors.append(f"cap[{expected_cap}] optimizer mask is out of range")
    return errors


def _verify_density_row_unchecked(
    row: dict[str, Any],
    maximum_nodes: int,
    scope: str,
    expected_node_cap: int | None,
) -> dict[str, Any]:
    errors = v6_row_schema_errors(row)
    if errors:
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}
    errors.extend(v6_row_type_errors(row))
    if errors:
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}
    errors.extend(density_row_envelope_errors(row, maximum_nodes))
    errors.extend(
        registered_row_envelope_errors(
            row, scope, maximum_nodes, expected_node_cap
        )
    )
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
    if not exact_json_equal(
        row["public_model"]["ordering_contract"], ORDERING_CONTRACT
    ):
        errors.append("ordering contract mismatch")
    if errors:
        return {"valid": False, "errors": errors, "primary_nodes": 0, "cap_reports": []}

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
    if not exact_json_equal(graph, expected_graph):
        errors.append("graph metric mismatch")
    if not exact_json_equal(
        row["private_audit"]["eligible_universe_indices"],
        eligible_universe_indices,
    ):
        errors.append("eligible universe-index list mismatch")
    if not exact_json_equal(row["private_audit"]["individually_rejected"], rejected):
        errors.append("individual rejection transcript mismatch")
    if not exact_json_equal(row["private_audit"]["conflicts"], conflict_records):
        errors.append("conflict transcript mismatch")
    if not exact_json_equal(
        row["public_model"]["representative_compiler"], representative_compiler
    ):
        errors.append("representative compiler mismatch")
    expansion = expansion_metrics(curve, factors)
    if not exact_json_equal(expansion, row["private_audit"]["expansion"]):
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
    expected_caps = expected_caps_for_group(q)
    errors.extend(density_row_preflight_errors(row, q, eligible, maximum_nodes))
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "curve": {"p": curve.p, "a": curve.a, "b": curve.b, "q": q},
            "B": row["B"],
            "family": row["family"],
            "null_replicate": row["null_replicate"],
            "candidate_count": candidate_count,
            "eligible_candidate_count": len(eligible),
            "conflict_count": conflict_count,
            "primary_nodes": 0,
            "cap_reports": [],
        }
    if not exact_json_equal(caps, expected_caps):
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
    expected_accounting = {
        "scope": "nested canonical-JSON byte measures; fields are nonadditive",
        "public_model_json_bytes": len(stable_bytes(row["public_model"])),
        "private_audit_json_bytes": len(stable_bytes(row["private_audit"])),
        "row_payload_without_accounting_or_digest_json_bytes": len(
            stable_bytes(row_payload)
        ),
        "nested_per_cap_json_bytes": expected_cap_accounting,
    }
    if not exact_json_equal(accounting, expected_accounting):
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
    if not exact_json_equal(row["structural_work"], expected_structural_work):
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
        if not exact_json_equal(
            optimizer.get("objective_order"),
            [
                "retained_support:max",
                "constrained_count:min",
                "public_edges:min",
                "retained_maxima:max",
                "witness_list:lex_min",
            ],
        ):
            cap_errors.append("optimizer objective-order mismatch")
        if optimizer.get("bound_method") != (
            "conflict-clique-cover cardinality plus global pair-output union"
        ):
            cap_errors.append("optimizer bound-method mismatch")
        try:
            require_independent_exhausted_gate_cell(optimizer)
        except AssertionError as error:
            cap_errors.append(f"V6 requires an exhausted exact optimizer cell: {error}")
        if not exact_json_equal(optimizer.get("selected_indices"), selected_indices):
            cap_errors.append("optimizer selected-index mismatch")
        if optimizer.get("selected_mask_hex") != hex(selected_mask):
            cap_errors.append("optimizer selected-mask mismatch")
        if not exact_json_equal(
            {
                "constrained_count": optimizer.get("constrained_count"),
                "public_edge_count": optimizer.get("public_edge_count"),
                "witness_list": optimizer.get("witness_list"),
            },
            {
                "constrained_count": public["constrained_count"],
                "public_edge_count": public["public_edge_count"],
                "witness_list": public["selected_maxima"],
            },
        ):
            cap_errors.append("optimizer/public model objective-field mismatch")
        cap_errors.extend(
            verify_frontier_certificate(pair_outputs, q, conflicts, optimizer)
        )

        replay_metric_cache: dict[int, dict[str, Any]] = {}

        def replay_metrics(mask: int) -> dict[str, Any]:
            if mask not in replay_metric_cache:
                if len(replay_metric_cache) >= (
                    optimizer["node_cap"] + len(eligible) * len(eligible) + 64
                ):
                    raise AssertionError("retained-model replay cache ceiling exceeded")
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
            optimizer["node_cap"] + len(eligible) * len(eligible) + 64,
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
            if not exact_json_equal(replay[key], optimizer.get(key)):
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
        if not exact_json_equal(
            public["formal_degree_histogram"],
            {
                str(degree): expected_histogram[degree]
                for degree in sorted(expected_histogram)
            },
        ):
            cap_errors.append("formal degree histogram mismatch")
        for key, value in axioms.items():
            if public["axioms"].get(key) != value:
                cap_errors.append(f"axiom mismatch: {key}")
        if not exact_json_equal(public_edges, public["public_edges"]) or digest(
            public_edges
        ) != public["public_edges_sha256"]:
            cap_errors.append("public edge table/digest mismatch")
        if not exact_json_equal(source_table, public["source_table"]) or digest(
            source_table
        ) != public["source_table_sha256"]:
            cap_errors.append("public source table/digest mismatch")
        delta_divisor = math.gcd(constrained, q)
        if not exact_json_equal(
            public["delta"],
            {
                "numerator": constrained // delta_divisor,
                "denominator": q // delta_divisor,
            },
        ):
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
        if not exact_json_equal(
            list(expected_ratios),
            [
                retention["retained_to_balanced_raw"],
                retention["retained_to_eight_fold"],
                retention["absolute_group_coverage"],
            ],
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
        if not exact_json_equal(private["structural_work"], expected_cap_work):
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
                "replay_nodes": replay["explored_nodes"],
                "replay_metric_cache_entries": replay["metric_cache_entries"],
                "retained_model_replay_cache_entries": len(replay_metric_cache),
                "primary_cache_entries_upper_bound": 2 * (primary_nodes + 1),
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
        "replay_nodes": sum(report["replay_nodes"] for report in cap_reports),
        "primary_nodes": sum(report["primary_nodes"] for report in cap_reports),
        "cap_reports": cap_reports,
    }


def verify_density_row(
    row: Any,
    maximum_nodes: Any,
    scope: str | None = None,
) -> dict[str, Any]:
    errors = bounded_json_errors(row, "row")
    errors.extend(maximum_nodes_errors(maximum_nodes))
    if scope not in {"frozen_fixture", "canonical"}:
        errors.append("density row scope must be explicitly registered")
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "primary_nodes": 0,
            "cap_reports": [],
        }
    if type(row) is not dict:
        return {
            "valid": False,
            "errors": ["density row is not an object"],
            "primary_nodes": 0,
            "cap_reports": [],
        }
    try:
        _REGISTERED_CURVE_CACHE.clear()
        expected_node_cap = (
            FROZEN_NODE_CAP if scope == "frozen_fixture" else CANONICAL_NODE_CAP
        )
        return _verify_density_row_unchecked(
            row,
            maximum_nodes,
            scope,
            expected_node_cap,
        )
    except Exception as error:
        return {
            "valid": False,
            "errors": [
                f"density row verifier failure: {type(error).__name__}: {error}"
            ],
            "primary_nodes": 0,
            "cap_reports": [],
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
            require_independent_exhausted_gate_cell(cell["optimizer"])
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
    every_family_collapses = True
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
        collapse_strata = sum(
            fraction_from_record(item["median_retained_to_balanced_raw"])
            < Fraction(1, 10)
            for item in persistence_rows
        )
        family_collapses = collapse_strata >= 3
        every_family_collapses = every_family_collapses and family_collapses

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
                "full_cap_collapse_strata": collapse_strata,
                "full_cap_collapse": family_collapses,
                "matched_null_cap_tests": tested_caps,
            }
        )
    status = "PASS" if winners else "FAIL"
    if winners:
        negative_outcome = "NOT_APPLICABLE"
    elif every_family_collapses:
        negative_outcome = "COLLAPSE"
    else:
        negative_outcome = "WEAKEN_OR_REJECT"
    return {
        "criterion_version": "sgcp-embed-002-family-gate-v6",
        "null_median": "exact arithmetic mean of the middle two of four precommitted null supports",
        "null_duplicate_policy": "retain duplicate precommitted null selections without resampling",
        "unresolved_policy": "every cell must have equal integer bounds, zero integer gap, exact primary and full objectives, and an empty authenticated frontier",
        "cap_selection_policy": "one fixed family and one fixed cap fraction must pass across strata",
        "collapse_policy": "COLLAPSE iff every coordinate family has full-cap median retention below 1/10 in at least three bit strata",
        "status": status,
        "negative_outcome": negative_outcome,
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
        "ordering_contract_sha256": digest(ORDERING_CONTRACT),
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


def v6_document_schema_errors(document: Any) -> list[str]:
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
            "V6 document",
        )
        require_keys(
            document["summary"],
            {
                "row_count",
                "valid_rows",
                "unique_curve_records",
                "cap_cell_count",
                "primary_exact_cap_cells",
                "full_objective_exact_cap_cells",
                "maximum_primary_gap",
            },
            "V6 document summary",
        )
    except (AssertionError, KeyError, TypeError) as error:
        errors.append(f"closed document schema: {error}")
    errors.extend(forbidden_material(document, "document"))
    return errors


def v6_document_type_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for name in ("schema", "experiment_id", "scope", "interpretation"):
        exact_string(document[name], f"document.{name}", errors)
    exact_integer(document["protocol_version"], "document.protocol_version", errors)
    exact_boolean(document["canonical"], "document.canonical", errors)
    exact_string_list(document["claim_status"], "document.claim_status", errors)
    exact_type(document["parameters"], dict, "document.parameters", errors)
    if exact_type(document["rows"], list, "document.rows", errors):
        for index, row in enumerate(document["rows"]):
            exact_type(row, dict, f"document.rows[{index}]", errors)
    exact_type(document["family_gate"], dict, "document.family_gate", errors)
    exact_digest(document["document_sha256"], "document.document_sha256", errors)
    if exact_type(document["summary"], dict, "document.summary", errors):
        for name, value in document["summary"].items():
            exact_integer(value, f"document.summary.{name}", errors)
    return errors


def append_phase(
    phases: list[dict[str, str]] | None,
    name: str,
    status: str,
) -> None:
    if phases is not None:
        phases.append({"name": name, "status": status})


def static_row_errors(
    row: Any,
    row_index: int,
    scope: str,
    maximum_nodes: int,
    expected_node_cap: int | None,
) -> list[str]:
    prefix = f"row[{row_index}]"
    errors = [f"{prefix}: {error}" for error in v6_row_schema_errors(row)]
    if errors or type(row) is not dict:
        return errors or [f"{prefix}: row is not an object"]
    type_errors = v6_row_type_errors(row)
    if type_errors:
        return [f"{prefix}: {error}" for error in type_errors]
    envelope_errors = density_row_envelope_errors(row, maximum_nodes)
    envelope_errors.extend(
        registered_row_envelope_errors(
            row, scope, maximum_nodes, expected_node_cap
        )
    )
    supplied = row["row_sha256"]
    payload = dict(row)
    payload.pop("row_sha256")
    if supplied != digest(payload):
        envelope_errors.append("row digest mismatch")
    if row["protocol_version"] != PROTOCOL_VERSION:
        envelope_errors.append("row protocol version mismatch")
    if row["valid"] is not True:
        envelope_errors.append("row does not claim local validity")
    if not exact_json_equal(
        row["public_model"]["ordering_contract"], ORDERING_CONTRACT
    ):
        envelope_errors.append("ordering contract mismatch")
    return [f"{prefix}: {error}" for error in envelope_errors]


def resource_envelope(
    rows: Sequence[dict[str, Any]], maximum_nodes: int
) -> tuple[dict[str, int], list[str]]:
    cap_cells = sum(len(row["private_audit"]["density_frontier"]) for row in rows)
    replay_nodes = sum(
        cell["optimizer"]["node_cap"]
        for row in rows
        for cell in row["private_audit"]["density_frontier"]
    )
    expansion_cells = sum(
        sum(math.comb(row["B"] + degree - 1, degree) for degree in (1, 2, 4, 8))
        for row in rows
    )
    graph_cells = 0
    metric_cache_entries = 0
    retained_model_calls = 0
    retained_model_cells = 0
    for row in rows:
        candidate_bound = math.comb(row["B"] + 3, 4)
        graph_cells += (
            candidate_bound
            + math.comb(candidate_bound, 2)
            + candidate_bound**2
        )
        family_bound = sum(
            math.comb(row["B"] + degree - 1, degree)
            for degree in range(5)
        )
        retained_cells_per_call = family_bound + math.comb(family_bound, 2)
        for cell in row["private_audit"]["density_frontier"]:
            replay_cache_bound = (
                cell["optimizer"]["node_cap"] + candidate_bound**2 + 64
            )
            primary_cache_bound = 2 * (maximum_nodes + 1)
            metric_cache_entries += 2 * replay_cache_bound + primary_cache_bound
            cap_retained_calls = replay_cache_bound + maximum_nodes + 2
            retained_model_calls += cap_retained_calls
            retained_model_cells += cap_retained_calls * retained_cells_per_call
    primary_nodes = cap_cells * maximum_nodes
    unique_curves = {
        digest(row["curve"]): row["curve"] for row in rows
    }
    curve_draws = sum(
        1 if curve["draw"] is None else curve["draw"] + 1
        for curve in unique_curves.values()
    )
    receipt = {
        "row_count": len(rows),
        "cap_cell_count": cap_cells,
        "registered_curve_cache_entries": len(unique_curves),
        "registered_curve_draws_upper_bound": curve_draws,
        "expansion_cells_upper_bound": expansion_cells,
        "graph_cells_upper_bound": graph_cells,
        "replay_nodes_upper_bound": replay_nodes,
        "independent_primary_nodes_upper_bound": primary_nodes,
        "metric_cache_entries_upper_bound": metric_cache_entries,
        "retained_model_calls_upper_bound": retained_model_calls,
        "retained_model_cells_upper_bound": retained_model_cells,
    }
    errors: list[str] = []
    if len(rows) > MAXIMUM_CANONICAL_ROWS:
        errors.append("row count exceeds the trusted verifier limit")
    if cap_cells > MAXIMUM_CANONICAL_ROWS * MAXIMUM_CAPS_PER_ROW:
        errors.append("cap-cell count exceeds the trusted verifier limit")
    if expansion_cells > MAXIMUM_TOTAL_EXPANSION_CELLS:
        errors.append("expansion-cell bound exceeds the trusted verifier limit")
    if graph_cells > MAXIMUM_TOTAL_GRAPH_CELLS:
        errors.append("graph-cell bound exceeds the trusted verifier limit")
    if replay_nodes > MAXIMUM_TOTAL_REPLAY_NODES:
        errors.append("replay-node bound exceeds the trusted verifier limit")
    if primary_nodes > MAXIMUM_TOTAL_PRIMARY_NODES:
        errors.append("primary-proof bound exceeds the trusted verifier limit")
    if curve_draws > MAXIMUM_REGISTERED_CURVE_DRAWS:
        errors.append("curve-draw bound exceeds the trusted verifier limit")
    if metric_cache_entries > MAXIMUM_TOTAL_METRIC_CACHE_ENTRIES:
        errors.append("metric-cache bound exceeds the trusted verifier limit")
    if retained_model_calls > MAXIMUM_TOTAL_RETAINED_MODEL_CALLS:
        errors.append("retained-model call bound exceeds the trusted verifier limit")
    if retained_model_cells > MAXIMUM_TOTAL_RETAINED_MODEL_CELLS:
        errors.append("retained-model cell bound exceeds the trusted verifier limit")
    return receipt, errors


def canonical_matrix_errors(rows: Any) -> list[str]:
    errors: list[str] = []
    if type(rows) is not list:
        return ["canonical rows are not a list"]
    observed_keys: list[tuple[Any, Any, Any, Any, Any]] = []
    curve_records: dict[tuple[int, int], dict[str, Any]] = {}
    accepted_curves: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    for index, row in enumerate(rows):
        path = f"canonical row[{index}]"
        if type(row) is not dict:
            errors.append(f"{path} is not an object")
            continue
        curve = row.get("curve")
        if type(curve) is not dict:
            errors.append(f"{path} curve is not an object")
            continue
        key_values = (
            curve.get("bits"),
            curve.get("seed"),
            row.get("B"),
            row.get("family"),
            row.get("null_replicate"),
        )
        observed_keys.append(key_values)
        if any(type(value) is not int for value in key_values[:3]):
            errors.append(f"{path} grid integers have noninteger types")
        if type(key_values[3]) is not str:
            errors.append(f"{path} family is not a string")
        if key_values[4] is not None and type(key_values[4]) is not int:
            errors.append(f"{path} null replicate has a noninteger type")

        bits_value, seed = key_values[:2]
        q = curve.get("q")
        curve_tuple = tuple(curve.get(name) for name in ("p", "a", "b", "q"))
        if type(bits_value) is int and type(seed) is int:
            seed_key = (bits_value, seed)
            if seed_key in curve_records and not exact_json_equal(
                curve_records[seed_key], curve
            ):
                errors.append(f"inconsistent curve record for {seed_key!r}")
            else:
                curve_records.setdefault(seed_key, curve)
            if all(type(value) is int for value in curve_tuple):
                accepted_curves.setdefault(seed_key, curve_tuple)
                if accepted_curves[seed_key] != curve_tuple:
                    errors.append(f"inconsistent accepted curve for {seed_key!r}")
            else:
                errors.append(f"{path} accepted-curve tuple has noninteger types")

        if type(q) is not int or q < 2:
            errors.append(f"{path} group order is not a valid integer")
            continue
        expected_caps = sorted(
            {max(1, q // 4), max(1, q // 2), max(1, 3 * q // 4), q}
        )
        public_model = row.get("public_model")
        private_audit = row.get("private_audit")
        if type(public_model) is not dict or type(private_audit) is not dict:
            errors.append(f"{path} public/private envelope is malformed")
            continue
        if not exact_json_equal(
            public_model.get("constrained_budget_caps"), expected_caps
        ):
            errors.append(f"{path} constrained-cap schedule mismatch")
        public_frontier = public_model.get("density_frontier")
        private_frontier = private_audit.get("density_frontier")
        if type(public_frontier) is not list or type(private_frontier) is not list:
            errors.append(f"{path} cap frontier is not a list")
            continue
        public_caps = [
            cell.get("constrained_cap") if type(cell) is dict else None
            for cell in public_frontier
        ]
        private_caps = [
            cell.get("constrained_cap") if type(cell) is dict else None
            for cell in private_frontier
        ]
        if not exact_json_equal(public_caps, expected_caps) or not exact_json_equal(
            private_caps, expected_caps
        ):
            errors.append(f"{path} cap-cell association mismatch")
        for cap_index, cell in enumerate(private_frontier):
            if type(cell) is not dict or type(cell.get("optimizer")) is not dict:
                errors.append(f"{path} private cap[{cap_index}] is malformed")
                continue
            optimizer = cell["optimizer"]
            if (
                type(optimizer.get("node_cap")) is not int
                or optimizer["node_cap"] != CANONICAL_NODE_CAP
            ):
                errors.append(f"{path} canonical node-cap mismatch")
            try:
                require_independent_exhausted_gate_cell(optimizer)
            except AssertionError as error:
                errors.append(f"{path} cap[{cap_index}] exactness: {error}")

    if observed_keys != expected_row_keys():
        errors.append("canonical row grid/order mismatch")
    owners: dict[tuple[int, int, int, int], tuple[int, int]] = {}
    for seed_key, curve_tuple in accepted_curves.items():
        if curve_tuple in owners and owners[curve_tuple] != seed_key:
            errors.append("cross-seed duplicate accepted curve")
            break
        owners[curve_tuple] = seed_key
    return errors


def _verify_v6_document_value_unchecked(
    document: dict[str, Any],
    maximum_nodes: int,
    phases: list[dict[str, str]] | None = None,
) -> tuple[list[str], list[dict[str, Any]], dict[str, int] | None]:
    _REGISTERED_CURVE_CACHE.clear()
    errors = v6_document_schema_errors(document)
    append_phase(phases, "closed_document_schema", "failed" if errors else "passed")
    if errors:
        return errors, [], None

    type_errors = v6_document_type_errors(document)
    errors.extend(type_errors)
    append_phase(phases, "exact_document_types", "failed" if type_errors else "passed")
    if errors:
        return errors, [], None

    authentication_errors: list[str] = []
    supplied = document["document_sha256"]
    payload = dict(document)
    payload.pop("document_sha256")
    if supplied != digest(payload):
        authentication_errors.append("document digest mismatch")
    if not exact_json_equal(
        {
            "schema": document["schema"],
            "experiment_id": document["experiment_id"],
            "protocol_version": document["protocol_version"],
            "claim_status": document["claim_status"],
        },
        {
            "schema": CURRENT_SCHEMA,
            "experiment_id": EXPERIMENT_ID,
            "protocol_version": PROTOCOL_VERSION,
            "claim_status": CLAIM_STATUS,
        },
    ):
        authentication_errors.append("document protocol identity mismatch")
    errors.extend(authentication_errors)
    append_phase(
        phases,
        "document_digest_and_protocol_identity",
        "failed" if authentication_errors else "passed",
    )
    if errors:
        return errors, [], None

    scope = document["scope"]
    rows = document["rows"]
    expected_gate: dict[str, Any] | None = None
    expected_node_cap: int | None = None
    scope_errors: list[str] = []
    if scope == "frozen_fixture":
        expected_parameters = {
            "curve": dict(FROZEN_FIXTURE),
            "B": 4,
            "family": "least_x_interval",
            "null_replicate": None,
            "node_cap_per_cap": FROZEN_NODE_CAP,
            "representative_compiler": REPRESENTATIVE_COMPILER,
            "ordering_contract_sha256": digest(ORDERING_CONTRACT),
        }
        if (
            maximum_nodes < FROZEN_NODE_CAP
            or document["canonical"] is not False
            or document["interpretation"]
            != "frozen-fixture implementation evidence only"
            or not exact_json_equal(document["parameters"], expected_parameters)
            or len(rows) != 1
        ):
            scope_errors.append("frozen document envelope mismatch")
        else:
            expected_node_cap = FROZEN_NODE_CAP
        expected_gate = {
            "status": "NOT_APPLICABLE",
            "reason": "frozen fixture is not a family matrix",
        }
    elif scope == "canonical":
        if (
            maximum_nodes < CANONICAL_NODE_CAP
            or document["canonical"] is not True
            or document["interpretation"]
            != "canonical candidate; coordinator interpretation still required"
            or not exact_json_equal(
                document["parameters"], expected_canonical_parameters()
            )
            or len(rows) != MAXIMUM_CANONICAL_ROWS
        ):
            scope_errors.append("canonical document envelope mismatch")
        expected_node_cap = CANONICAL_NODE_CAP
    else:
        scope_errors.append("unknown document scope")
    errors.extend(scope_errors)
    append_phase(
        phases,
        "registered_document_envelope",
        "failed" if scope_errors else "passed",
    )
    if errors:
        return errors, [], None

    row_errors: list[str] = []
    for index, row in enumerate(rows):
        row_errors.extend(
            static_row_errors(
                row,
                index,
                scope,
                maximum_nodes,
                expected_node_cap,
            )
        )
    errors.extend(row_errors)
    append_phase(
        phases,
        "closed_registered_row_preflight",
        "failed" if row_errors else "passed",
    )
    if errors:
        return errors, [], None

    matrix_errors = canonical_matrix_errors(rows) if scope == "canonical" else []
    errors.extend(matrix_errors)
    append_phase(
        phases,
        "registered_matrix_preflight",
        "failed" if matrix_errors else "passed",
    )
    if errors:
        return errors, [], None

    envelope, budget_errors = resource_envelope(rows, maximum_nodes)
    errors.extend(budget_errors)
    append_phase(
        phases,
        "trusted_resource_reservation",
        "failed" if budget_errors else "passed",
    )
    if errors:
        return errors, [], envelope

    row_reports = [
        _verify_density_row_unchecked(
            row, maximum_nodes, scope, expected_node_cap
        )
        for row in rows
    ]
    semantic_errors = (
        ["one or more V6 row verifications failed"]
        if any(not report["valid"] for report in row_reports)
        else []
    )
    errors.extend(semantic_errors)
    append_phase(
        phases,
        "row_semantic_verification",
        "failed" if semantic_errors else "passed",
    )
    if errors:
        return errors, row_reports, envelope
    for completed_phase in (
        "curve_factor_graph_and_expansion_reconstruction",
        "deterministic_optimizer_replay",
        "retained_model_transcript_reconstruction",
        "independent_primary_proof",
    ):
        append_phase(phases, completed_phase, "passed")

    summary_errors: list[str] = []
    try:
        expected_summary = independent_document_summary(rows)
    except (AttributeError, KeyError, TypeError) as error:
        summary_errors.append(f"document summary reconstruction failed: {error}")
    else:
        if not exact_json_equal(document["summary"], expected_summary):
            summary_errors.append("document summary mismatch")
    errors.extend(summary_errors)
    append_phase(
        phases,
        "document_summary_reconstruction",
        "failed" if summary_errors else "passed",
    )
    if errors:
        return errors, row_reports, envelope

    gate_errors: list[str] = []
    if scope == "canonical":
        try:
            expected_gate = independent_family_gate(rows)
        except Exception as error:
            gate_errors.append(f"family gate reconstruction: {error}")
    if expected_gate is not None and not exact_json_equal(
        document["family_gate"], expected_gate
    ):
        gate_errors.append("family gate mismatch")
    errors.extend(gate_errors)
    append_phase(
        phases,
        "family_gate_reconstruction",
        "failed" if gate_errors else "passed",
    )
    return errors, row_reports, envelope


def verify_v6_document_value(
    document: Any, maximum_nodes: Any
) -> tuple[list[str], list[dict[str, Any]]]:
    errors = bounded_json_errors(document, "document")
    errors.extend(maximum_nodes_errors(maximum_nodes))
    if errors:
        return errors, []
    if type(document) is not dict:
        return ["V6 document is not an object"], []
    try:
        errors, rows, _ = _verify_v6_document_value_unchecked(
            document, maximum_nodes
        )
        return errors, rows
    except Exception as error:
        return [
            f"V6 document verifier failure: {type(error).__name__}: {error}"
        ], []


def verification_report(
    path: Path,
    supplied: Any,
    input_file_sha256: str | None,
    errors: list[str],
    row_reports: Sequence[dict[str, Any]],
    phases: Sequence[dict[str, str]],
    claim_boundary: str,
    resource_receipt: dict[str, int] | None = None,
) -> dict[str, Any]:
    cap_reports = [
        cap
        for row in row_reports
        for cap in row.get("cap_reports", [])
        if type(cap) is dict
    ]
    report = {
        "schema": VERIFICATION_SCHEMA,
        "verifier_source_path": str(SCRIPT_PATH),
        "verifier_source_sha256": file_digest(SCRIPT_PATH),
        "input_path": str(path.absolute()),
        "input_file_sha256": input_file_sha256,
        "input_document_sha256": supplied,
        "valid": not errors,
        "errors": errors,
        "row_count": len(row_reports),
        "valid_row_count": sum(row.get("valid") is True for row in row_reports),
        "total_replay_nodes": sum(
            row.get("replay_nodes", 0)
            for row in row_reports
            if type(row.get("replay_nodes", 0)) is int
        ),
        "total_primary_nodes": sum(
            row.get("primary_nodes", 0)
            for row in row_reports
            if type(row.get("primary_nodes", 0)) is int
        ),
        "rows": list(row_reports),
        "phases": list(phases),
        "independent_checks": [
            phase["name"] for phase in phases if phase["status"] == "passed"
        ],
        "resource_reservation": resource_receipt,
        "actual_work": {
            "registered_curve_cache_entries": len(_REGISTERED_CURVE_CACHE),
            "replay_nodes": sum(
                cap.get("replay_nodes", 0)
                for cap in cap_reports
                if type(cap.get("replay_nodes", 0)) is int
            ),
            "replay_metric_cache_entries": sum(
                cap.get("replay_metric_cache_entries", 0)
                + cap.get("retained_model_replay_cache_entries", 0)
                for cap in cap_reports
                if type(cap.get("replay_metric_cache_entries", 0)) is int
                and type(cap.get("retained_model_replay_cache_entries", 0)) is int
            ),
            "independent_primary_nodes": sum(
                cap.get("primary_nodes", 0)
                for cap in cap_reports
                if type(cap.get("primary_nodes", 0)) is int
            ),
            "primary_cache_entries_observed_upper_bound": sum(
                cap.get("primary_cache_entries_upper_bound", 0)
                for cap in cap_reports
                if type(cap.get("primary_cache_entries_upper_bound", 0)) is int
            ),
        },
        "claim_boundary": claim_boundary,
    }
    report["verification_sha256"] = digest(report)
    return report


def verify_document(path: Path, maximum_nodes: Any) -> dict[str, Any]:
    _REGISTERED_CURVE_CACHE.clear()
    phases: list[dict[str, str]] = []
    errors = maximum_nodes_errors(maximum_nodes)
    append_phase(
        phases,
        "verifier_budget_preflight",
        "failed" if errors else "passed",
    )
    document: Any = None
    input_file_sha256: str | None = None
    if errors:
        return verification_report(
            path,
            None,
            input_file_sha256,
            errors,
            [],
            phases,
            "input could not enter schema verification",
        )

    try:
        raw, input_file_sha256 = read_input_snapshot(path)
    except Exception as error:
        errors.append(f"input snapshot failure: {type(error).__name__}: {error}")
        append_phase(phases, "single_regular_file_snapshot", "failed")
        return verification_report(
            path,
            None,
            input_file_sha256,
            errors,
            [],
            phases,
            "input could not enter JSON parsing",
        )
    append_phase(phases, "single_regular_file_snapshot", "passed")

    try:
        document = strict_json_load(raw, path)
    except Exception as error:
        errors.append(f"strict JSON parse failure: {type(error).__name__}: {error}")
        append_phase(phases, "strict_json_parse", "failed")
        return verification_report(
            path,
            None,
            input_file_sha256,
            errors,
            [],
            phases,
            "input could not enter schema verification",
        )
    append_phase(phases, "strict_json_parse", "passed")

    shape_errors = bounded_json_errors(document)
    errors.extend(shape_errors)
    append_phase(
        phases,
        "bounded_json_shape",
        "failed" if shape_errors else "passed",
    )
    supplied = document.get("document_sha256") if type(document) is dict else None
    if errors:
        return verification_report(
            path,
            supplied,
            input_file_sha256,
            errors,
            [],
            phases,
            "input rejected before schema verification",
        )
    if type(document) is not dict:
        append_phase(phases, "exact_schema_routing", "failed")
        return verification_report(
            path,
            supplied,
            input_file_sha256,
            ["input document is not an object"],
            [],
            phases,
            "input rejected before protocol verification",
        )

    schema = document.get("schema")
    resource_receipt: dict[str, int] | None = None
    if type(schema) is not str:
        errors = [f"document schema is not a string: {type(schema).__name__}"]
        row_reports = []
        claim_boundary = "malformed schema; no mathematical checks executed"
        append_phase(phases, "exact_schema_routing", "failed")
    elif schema == CURRENT_SCHEMA:
        append_phase(phases, "exact_schema_routing", "passed")
        try:
            errors, row_reports, resource_receipt = (
                _verify_v6_document_value_unchecked(
                    document, maximum_nodes, phases
                )
            )
        except Exception as error:
            errors = [
                f"V6 document verifier failure: {type(error).__name__}: {error}"
            ]
            row_reports = []
            append_phase(phases, "verifier_exception_boundary", "failed")
        claim_boundary = (
            "invalid V6 document; no mathematical interpretation"
            if errors
            else (
                "frozen-fixture implementation verification only"
                if document.get("scope") == "frozen_fixture"
                else "canonical matrix verification; coordinator interpretation still required"
            )
        )
    elif schema in LEGACY_SCHEMAS:
        append_phase(phases, "exact_schema_routing", "passed")
        append_phase(phases, "unsupported_legacy_rejection", "passed")
        errors = [
            f"unsupported legacy document schema {schema!r}; V6 performs no legacy row verification"
        ]
        row_reports = []
        claim_boundary = "unsupported legacy input; no mathematical checks executed"
    else:
        append_phase(phases, "exact_schema_routing", "failed")
        errors = [f"unexpected document schema {schema!r}"]
        row_reports = []
        claim_boundary = "unknown input schema; no mathematical checks executed"
    return verification_report(
        path,
        supplied,
        input_file_sha256,
        errors,
        row_reports,
        phases,
        claim_boundary,
        resource_receipt,
    )


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
    report = verify_document(args.input, args.maximum_primary_nodes)
    write_atomic(output_path(args.output), report)
    print(
        json.dumps(
            {
                "valid": report["valid"],
                "row_count": report["row_count"],
                "valid_row_count": report["valid_row_count"],
                "total_replay_nodes": report["total_replay_nodes"],
                "total_primary_nodes": report["total_primary_nodes"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

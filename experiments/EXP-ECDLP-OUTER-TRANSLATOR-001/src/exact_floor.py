#!/usr/bin/env python3
"""Exact, dependency-free D2+D3 floor primitives.

The module deliberately imports no experiment harness.  Callers provide the
repository ``Curve`` and either an ``Ops`` class/factory, an Ops-like instance,
or a D2 object whose ``build_ops`` identifies the Ops type.  Query work,
fallback work, affine-equality controls, and witness-verification audits are
kept in separate records.

Points use the repository convention ``None`` for infinity and ``(x, y)`` for
affine points.  A D2 object must expose aligned ``points`` and ``witnesses``
sequences; each D2 witness is a pair of factor-base indices.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, TypeAlias


Point: TypeAlias = tuple[int, int] | None
Witness2: TypeAlias = tuple[int, int]
Witness3: TypeAlias = tuple[int, int, int]
Witness5: TypeAlias = tuple[int, int, int, int, int]

DEFAULT_INVERSION_WEIGHTS = (10, 50, 100)
_NATIVE_OP_FIELDS = (
    "group_operations",
    "point_additions",
    "point_doublings",
    "field_multiplications",
    "field_inversions",
)


@dataclass
class _FallbackOps:
    """Minimum Ops protocol used only when a harness type cannot be inferred."""

    group_operations: int = 0
    point_additions: int = 0
    point_doublings: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0


@dataclass
class D3Support:
    """Every distinct D2+factor point with one canonical three-leaf witness."""

    p: int
    points: list[Point]
    witnesses: list[Witness3]
    multiplicities: list[int]
    point_to_index: dict[Point, int]
    point_to_witness: dict[Point, Witness3]
    build_ops: Any
    attempts: int
    record: dict[str, Any]


@dataclass
class D5AuditSupport:
    """Audit-only exact five-sum support; never eligible query advice."""

    p: int
    points: list[Point]
    witnesses: list[Witness5]
    multiplicities: list[int]
    point_to_index: dict[Point, int]
    point_to_witness: dict[Point, Witness5]
    build_ops: Any
    attempts: int
    record: dict[str, Any]

    def __contains__(self, point: object) -> bool:
        return point in self.point_to_index


@dataclass
class PartialD3Cache:
    """A target-independent, SHA-256-ranked subset of an exact D3 support."""

    p: int
    points: list[Point]
    witnesses: list[Witness3]
    point_to_index: dict[Point, int]
    point_to_witness: dict[Point, Witness3]
    source_indices: list[int]
    numerator: int
    denominator: int
    seed: int
    record: dict[str, Any]


@dataclass
class TargetSchedule(Sequence[Point]):
    """Public point-only schedule.  Constructor scalars are never retained."""

    kind: str
    points: list[Point]
    record: dict[str, Any]
    build_ops: Any | None = None

    def __getitem__(self, index: int | slice) -> Point | list[Point]:
        return self.points[index]

    def __len__(self) -> int:
        return len(self.points)

    def __iter__(self):  # type annotation would obscure Sequence covariance
        return iter(self.points)


def stable_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json_bytes(value)).hexdigest()


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def logical_point_bytes(p: int) -> int:
    """Bit-packed infinity flag plus two fixed-width field elements."""

    _exact_int(p, "p", 2)
    return math.ceil((1 + 2 * p.bit_length()) / 8)


def logical_factor_index_bytes(factor_count: int) -> int:
    _exact_int(factor_count, "factor_count", 1)
    bits = max(1, (factor_count - 1).bit_length())
    return math.ceil(bits / 8)


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, Mapping):
        size += sum(
            deep_size(key, seen) + deep_size(item, seen)
            for key, item in value.items()
        )
    elif isinstance(value, (list, tuple, set, frozenset)):
        size += sum(deep_size(item, seen) for item in value)
    return size


def ops_record(ops: Any) -> dict[str, int]:
    """Return all public exact-integer Ops fields, including required zeros."""

    record: dict[str, int] = {}
    try:
        values = vars(ops)
    except TypeError:
        values = {}
    for name, value in values.items():
        if not name.startswith("_") and type(value) is int:
            record[name] = value
    for name in _NATIVE_OP_FIELDS:
        value = getattr(ops, name, 0)
        if type(value) is not int:
            raise TypeError(f"Ops field {name} must be an exact integer")
        record[name] = value
    return {name: record[name] for name in sorted(record)}


def weighted_field_work(
    operations: Mapping[str, int] | Any,
    weights: Iterable[int] = DEFAULT_INVERSION_WEIGHTS,
) -> dict[str, int]:
    """Compute M+wI while preserving the unweighted vector elsewhere."""

    record = dict(operations) if isinstance(operations, Mapping) else ops_record(operations)
    multiplications = _exact_int(
        record.get("field_multiplications", 0),
        "field_multiplications",
        0,
    )
    inversions = _exact_int(
        record.get("field_inversions", 0),
        "field_inversions",
        0,
    )
    result: dict[str, int] = {}
    for index, weight in enumerate(weights):
        exact_weight = _exact_int(weight, f"weights[{index}]", 0)
        if str(exact_weight) in result:
            raise ValueError("inversion weights must be distinct")
        result[str(exact_weight)] = multiplications + exact_weight * inversions
    if not result:
        raise ValueError("at least one inversion weight is required")
    return result


def _exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def _member(value: Any, name: str) -> Any:
    if isinstance(value, Mapping):
        if name not in value:
            raise AttributeError(f"D2 object is missing {name}")
        return value[name]
    if not hasattr(value, name):
        raise AttributeError(f"D2 object is missing {name}")
    return getattr(value, name)


def _new_ops(ops_like: Any | None, *sources: Any) -> Any:
    candidate = ops_like
    if candidate is None:
        for source in sources:
            if source is None:
                continue
            try:
                candidate = _member(source, "build_ops")
            except AttributeError:
                candidate = getattr(source, "build_ops", None)
            if candidate is not None:
                break
    if candidate is None:
        return _FallbackOps()
    if isinstance(candidate, type):
        return candidate()
    if callable(candidate) and not any(
        hasattr(candidate, field) for field in _NATIVE_OP_FIELDS
    ):
        return candidate()
    try:
        return type(candidate)()
    except TypeError as error:
        raise TypeError("Ops-like object must have a zero-argument constructor") from error


def _increment_ops(ops: Any, name: str, amount: int) -> None:
    if amount == 0:
        return
    current = getattr(ops, name, None)
    if type(current) is not int:
        raise TypeError(f"Ops-like object has no exact-integer {name} field")
    setattr(ops, name, current + amount)


def _ops_from_record(record: Mapping[str, int], ops_like: Any | None, *sources: Any) -> Any:
    ops = _new_ops(ops_like, *sources)
    for name in _NATIVE_OP_FIELDS:
        _increment_ops(ops, name, _exact_int(record.get(name, 0), name, 0))
    return ops


def _validate_factor_points(factor_points: Sequence[Point]) -> list[Point]:
    points = list(factor_points)
    if not points:
        raise ValueError("factor_points must not be empty")
    for index, point in enumerate(points):
        if point is None:
            continue
        if (
            not isinstance(point, tuple)
            or len(point) != 2
            or type(point[0]) is not int
            or type(point[1]) is not int
        ):
            raise TypeError(f"factor_points[{index}] must be None or an integer pair")
    return points


def _d2_parts(d2: Any, factor_count: int) -> tuple[list[Point], list[Witness2]]:
    points = list(_member(d2, "points"))
    witnesses_raw = list(_member(d2, "witnesses"))
    if len(points) != len(witnesses_raw):
        raise ValueError("D2 points and witnesses must be aligned")
    if len(points) != len(set(points)):
        raise ValueError("D2 points must be unique")
    witnesses: list[Witness2] = []
    for ordinal, raw in enumerate(witnesses_raw):
        candidate = tuple(raw)
        if len(candidate) != 2:
            raise ValueError(f"D2 witness {ordinal} must have two leaves")
        left = _exact_int(candidate[0], f"D2 witness {ordinal}[0]", 0)
        right = _exact_int(candidate[1], f"D2 witness {ordinal}[1]", 0)
        if left >= factor_count or right >= factor_count:
            raise ValueError(f"D2 witness {ordinal} is out of factor-base range")
        witnesses.append(tuple(sorted((left, right))))
    return points, witnesses


def _advice_record(
    *,
    p: int,
    factor_count: int,
    leaf_count: int,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    point_bytes = logical_point_bytes(p)
    index_bytes = logical_factor_index_bytes(factor_count)
    logical_bytes = len(entries) * (point_bytes + leaf_count * index_bytes)
    return {
        "entry_count": len(entries),
        "point_encoding_bytes": point_bytes,
        "factor_index_encoding_bytes": index_bytes,
        "witness_leaf_count": leaf_count,
        "logical_advice_bytes": logical_bytes,
        "canonical_serialized_bytes": len(stable_json_bytes(entries)),
        "advice_digest": stable_digest(entries),
        "advice_model": (
            "fixed-width point key plus raw fixed-width factor indices; "
            "excludes allocator and hash-table overhead"
        ),
    }


def build_exact_d3(
    curve: Any,
    factor_points: Sequence[Point],
    d2: Any,
    ops_like: Any | None = None,
) -> D3Support:
    """Construct exact unique D3 with the lexicographically least witness.

    Every D2/factor attempt is executed and charged, even after its output has
    appeared.  Thus multiplicities and collision counts are exact.
    """

    start = time.perf_counter()
    points = _validate_factor_points(factor_points)
    d2_points, d2_witnesses = _d2_parts(d2, len(points))
    p = _exact_int(getattr(curve, "p", None), "curve.p", 2)
    ops = _new_ops(ops_like, d2)
    witness_by_point: dict[Point, Witness3] = {}
    multiplicity_by_point: dict[Point, int] = {}

    for d2_index, partial in enumerate(d2_points):
        pair_witness = d2_witnesses[d2_index]
        for factor_index, factor in enumerate(points):
            total = curve.add(partial, factor, ops)
            candidate = tuple(sorted(pair_witness + (factor_index,)))
            multiplicity_by_point[total] = multiplicity_by_point.get(total, 0) + 1
            previous = witness_by_point.get(total)
            if previous is None or candidate < previous:
                witness_by_point[total] = candidate

    ordered = sorted(witness_by_point, key=point_sort_key)
    witnesses = [witness_by_point[point] for point in ordered]
    multiplicities = [multiplicity_by_point[point] for point in ordered]
    advice_entries = [
        {
            "point": point_json(point),
            "witness": list(witness_by_point[point]),
        }
        for point in ordered
    ]
    multiplicity_artifact = [
        {"point": point_json(point), "multiplicity": multiplicity_by_point[point]}
        for point in ordered
    ]
    advice = _advice_record(
        p=p,
        factor_count=len(points),
        leaf_count=3,
        entries=advice_entries,
    )
    attempts = len(d2_points) * len(points)
    point_bytes = logical_point_bytes(p)
    index_bytes = logical_factor_index_bytes(len(points))
    operation_record = ops_record(ops)
    record = {
        "kind": "exact_unique_d3",
        "factor_count": len(points),
        "d2_size": len(d2_points),
        "attempts": attempts,
        "unique_points": len(ordered),
        "collisions": attempts - len(ordered),
        "identity_present": None in witness_by_point,
        "maximum_multiplicity": max(multiplicities, default=0),
        "deterministic_witness_policy": "lexicographically_least_sorted_factor_indices",
        "multiplicities_are_audit_only": True,
        "multiplicity_digest": stable_digest(multiplicity_artifact),
        "build_ops": operation_record,
        "d2_point_reads": len(d2_points),
        "d2_witness_reads": len(d2_points),
        "factor_point_reads": attempts,
        "logical_build_point_bytes_read": (len(d2_points) + attempts) * point_bytes,
        "logical_build_witness_bytes_read": len(d2_points) * 2 * index_bytes,
        **advice,
        "first_entries": advice_entries[:8],
        "python_deep_bytes": deep_size(
            {"points": ordered, "witnesses": witnesses, "mapping": witness_by_point}
        ),
        "wall_time_seconds": time.perf_counter() - start,
    }
    return D3Support(
        p=p,
        points=ordered,
        witnesses=witnesses,
        multiplicities=multiplicities,
        point_to_index={point: index for index, point in enumerate(ordered)},
        point_to_witness=dict(witness_by_point),
        build_ops=ops,
        attempts=attempts,
        record=record,
    )


def build_d5_audit_support(
    curve: Any,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_factory: Any | None = None,
) -> D5AuditSupport:
    """Materialize exact D2+D3 support as a segregated audit object."""

    start = time.perf_counter()
    factors = _validate_factor_points(factor_points)
    d2_points, d2_witnesses = _d2_parts(d2, len(factors))
    if d3.p != getattr(curve, "p", None):
        raise ValueError("D3 field does not match curve")
    if len(d3.points) != len(d3.witnesses):
        raise ValueError("D3 points and witnesses must be aligned")
    ops = _new_ops(ops_factory, d2, d3)
    witness_by_point: dict[Point, Witness5] = {}
    multiplicity_by_point: dict[Point, int] = {}

    for d2_index, left in enumerate(d2_points):
        left_witness = d2_witnesses[d2_index]
        for d3_index, right in enumerate(d3.points):
            total = curve.add(left, right, ops)
            candidate = tuple(sorted(left_witness + d3.witnesses[d3_index]))
            multiplicity_by_point[total] = multiplicity_by_point.get(total, 0) + 1
            previous = witness_by_point.get(total)
            if previous is None or candidate < previous:
                witness_by_point[total] = candidate

    ordered = sorted(witness_by_point, key=point_sort_key)
    witnesses = [witness_by_point[point] for point in ordered]
    multiplicities = [multiplicity_by_point[point] for point in ordered]
    support_artifact = [point_json(point) for point in ordered]
    witness_artifact = [
        {"point": point_json(point), "witness": list(witness_by_point[point])}
        for point in ordered
    ]
    attempts = len(d2_points) * len(d3.points)
    point_bytes = logical_point_bytes(d3.p)
    index_bytes = logical_factor_index_bytes(len(factors))
    record = {
        "kind": "audit_only_exact_d5_support",
        "eligible_query_advice": False,
        "factor_count": len(factors),
        "d2_size": len(d2_points),
        "d3_size": len(d3.points),
        "attempts": attempts,
        "support_size": len(ordered),
        "collisions": attempts - len(ordered),
        "identity_present": None in witness_by_point,
        "maximum_multiplicity": max(multiplicities, default=0),
        "deterministic_witness_policy": "lexicographically_least_sorted_factor_indices",
        "build_ops": ops_record(ops),
        "d2_point_reads": len(d2_points),
        "d2_witness_reads": len(d2_points),
        "d3_point_reads": attempts,
        "d3_witness_reads": attempts,
        "logical_build_point_bytes_read": (len(d2_points) + attempts) * point_bytes,
        "logical_build_witness_bytes_read": (
            len(d2_points) * 2 + attempts * 3
        ) * index_bytes,
        "support_digest": stable_digest(support_artifact),
        "support_canonical_serialized_bytes": len(stable_json_bytes(support_artifact)),
        "witness_digest": stable_digest(witness_artifact),
        "python_deep_bytes": deep_size(
            {"points": ordered, "witnesses": witnesses, "mapping": witness_by_point}
        ),
        "wall_time_seconds": time.perf_counter() - start,
    }
    return D5AuditSupport(
        p=d3.p,
        points=ordered,
        witnesses=witnesses,
        multiplicities=multiplicities,
        point_to_index={point: index for index, point in enumerate(ordered)},
        point_to_witness=dict(witness_by_point),
        build_ops=ops,
        attempts=attempts,
        record=record,
    )


def _sha_rank(seed: int, label: str, p: int, point: Point) -> bytes:
    width = max(1, math.ceil(p.bit_length() / 8))
    if point is None:
        encoded = b"\x00" + b"\x00" * (2 * width)
    else:
        encoded = (
            b"\x01"
            + point[0].to_bytes(width, "big")
            + point[1].to_bytes(width, "big")
        )
    payload = (
        b"EXP-ECDLP-OUTER-TRANSLATOR-001\x00"
        + str(seed).encode("ascii")
        + b"\x00"
        + label.encode("utf-8")
        + b"\x00"
        + encoded
    )
    return hashlib.sha256(payload).digest()


def supported_target_schedule(
    support: D5AuditSupport,
    count: int,
    seed: int,
    *,
    label: str = "supported",
) -> TargetSchedule:
    """Select distinct nonidentity supported points by public SHA-256 rank."""

    exact_count = _exact_int(count, "count", 1)
    exact_seed = _exact_int(seed, "seed", 0)
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a nonempty string")
    candidates = [point for point in support.points if point is not None]
    if exact_count > len(candidates):
        raise ValueError("supported schedule exceeds nonidentity D5 support")
    ranked = sorted(
        candidates,
        key=lambda point: (_sha_rank(exact_seed, label, support.p, point), point_sort_key(point)),
    )
    selected = ranked[:exact_count]
    artifact = [point_json(point) for point in selected]
    record = {
        "kind": "supported",
        "count": exact_count,
        "seed": exact_seed,
        "label": label,
        "selection": "SHA-256 rank over unique nonidentity exact D5 support",
        "support_digest": support.record["support_digest"],
        "target_digest": stable_digest(artifact),
        "target_scalars_emitted": False,
        "construction_witnesses_emitted": False,
    }
    return TargetSchedule("supported", selected, record)


def _sha_uniform_scalar(seed: int, label: str, counter: int, q: int) -> int | None:
    payload = (
        b"EXP-ECDLP-OUTER-TRANSLATOR-001-uniform\x00"
        + str(seed).encode("ascii")
        + b"\x00"
        + label.encode("utf-8")
        + b"\x00"
        + counter.to_bytes(16, "big")
    )
    raw = int.from_bytes(hashlib.sha256(payload).digest(), "big")
    span = q - 1
    ceiling = 1 << 256
    limit = ceiling - ceiling % span
    if raw >= limit:
        return None
    return 1 + raw % span


def uniform_target_schedule(
    curve: Any,
    q: int,
    generator: Point,
    count: int,
    seed: int,
    *,
    ops_like: Any | None = None,
    label: str = "uniform",
) -> TargetSchedule:
    """Sample nonidentity group points without retaining target scalars.

    SHA-256 rejection sampling avoids modular bias.  The derived scalars are
    ephemeral local variables: neither values nor hashes of values enter the
    returned schedule or any eligible advice.
    """

    exact_q = _exact_int(q, "q", 2)
    exact_count = _exact_int(count, "count", 1)
    exact_seed = _exact_int(seed, "seed", 0)
    if exact_count > exact_q - 1:
        raise ValueError("uniform schedule exceeds nonidentity group size")
    if generator is None:
        raise ValueError("generator must be nonidentity")
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a nonempty string")

    ops = _new_ops(ops_like)
    selected: list[Point] = []
    seen_points: set[Point] = set()
    seen_scalars: set[int] = set()
    counter = 0
    while len(selected) < exact_count:
        scalar = _sha_uniform_scalar(exact_seed, label, counter, exact_q)
        counter += 1
        if scalar is None or scalar in seen_scalars:
            continue
        seen_scalars.add(scalar)
        point = curve.mul(scalar, generator, ops)
        if point is None:
            raise AssertionError("nonzero schedule scalar produced identity")
        if point in seen_points:
            raise AssertionError("generator does not provide distinct nonzero scalar points")
        seen_points.add(point)
        selected.append(point)

    artifact = [point_json(point) for point in selected]
    record = {
        "kind": "uniform_nonidentity",
        "count": exact_count,
        "q": exact_q,
        "seed": exact_seed,
        "label": label,
        "sampler": "SHA-256 rejection sampling without replacement",
        "hash_draws": counter,
        "target_digest": stable_digest(artifact),
        "target_scalars_emitted": False,
        "target_scalar_hashes_emitted": False,
        "build_ops": ops_record(ops),
    }
    return TargetSchedule("uniform", selected, record, ops)


def verify_five_leaf_witness(
    curve: Any,
    factor_points: Sequence[Point],
    witness: Sequence[int],
    target: Point,
    ops_like: Any | None = None,
) -> dict[str, Any]:
    """Independently replay one five-leaf witness with segregated counters."""

    factors = _validate_factor_points(factor_points)
    candidate = tuple(witness)
    if len(candidate) != 5:
        raise ValueError("a five-leaf witness must contain exactly five indices")
    indices: list[int] = []
    for ordinal, value in enumerate(candidate):
        index = _exact_int(value, f"witness[{ordinal}]", 0)
        if index >= len(factors):
            raise ValueError(f"witness[{ordinal}] is out of factor-base range")
        indices.append(index)
    ops = _new_ops(ops_like)
    recovered: Point = None
    for index in indices:
        recovered = curve.add(recovered, factors[index], ops)
    point_bytes = logical_point_bytes(curve.p)
    index_bytes = logical_factor_index_bytes(len(factors))
    counters = {
        **ops_record(ops),
        "factor_point_reads": 5,
        "witness_index_reads": 5,
        "logical_factor_point_bytes_read": 5 * point_bytes,
        "logical_witness_index_bytes_read": 5 * index_bytes,
        "logical_bytes_read": 5 * (point_bytes + index_bytes),
    }
    return {
        "performed": True,
        "verified": recovered == target,
        "recovered": point_json(recovered),
        "ops": ops,
        "counters": counters,
    }


def _empty_audit(ops_like: Any | None = None, *sources: Any) -> dict[str, Any]:
    ops = _new_ops(ops_like, *sources)
    return {
        "performed": False,
        "verified": None,
        "recovered": None,
        "ops": ops,
        "counters": {
            **ops_record(ops),
            "factor_point_reads": 0,
            "witness_index_reads": 0,
            "logical_factor_point_bytes_read": 0,
            "logical_witness_index_bytes_read": 0,
            "logical_bytes_read": 0,
        },
    }


def _scalar_subtraction_extras(target: Point, subtrahend: Point, p: int) -> dict[str, int]:
    """Executed branch/addition/zero-test counts for Curve.add(Q, -A)."""

    result = {
        "point_identity_tests": 1,
        "field_additions": 0,
        "field_zero_tests": 0,
        "identity_routes": 0,
        "inverse_routes": 0,
        "doubling_routes": 0,
        "ordinary_routes": 0,
    }
    if target is None:
        result["identity_routes"] = 1
        return result
    result["point_identity_tests"] += 1
    if subtrahend is None:
        result["identity_routes"] = 1
        return result
    right = (subtrahend[0], (-subtrahend[1]) % p)
    result["field_zero_tests"] += 1  # x-coordinate equality
    if target[0] == right[0]:
        result["field_additions"] += 1  # y1+y2
        result["field_zero_tests"] += 1
        if (target[1] + right[1]) % p == 0:
            result["inverse_routes"] = 1
            return result
    if target == right:
        result["doubling_routes"] = 1
        result["field_additions"] += 5  # numerator, x3 twice, y3 twice
    else:
        result["ordinary_routes"] = 1
        result["field_additions"] += 6  # numerator/denominator and output formula
    return result


def _new_query_counters() -> dict[str, int]:
    fields = list(_NATIVE_OP_FIELDS) + [
        "field_additions",
        "field_zero_tests",
        "point_identity_tests",
        "identity_routes",
        "inverse_routes",
        "doubling_routes",
        "ordinary_routes",
        "complement_tests",
        "dictionary_probes",
        "d2_point_reads",
        "target_point_reads",
        "d3_key_reads",
        "d2_witness_reads",
        "d3_witness_reads",
        "inversion_batches",
        "batch_denominators",
        "prefix_multiplications",
        "backward_multiplications",
        "peak_batch_pending_entries",
        "peak_batch_workspace_logical_bytes",
        "logical_d2_point_bytes_read",
        "logical_target_point_bytes_read",
        "logical_d3_key_bytes_read",
        "logical_d2_witness_bytes_read",
        "logical_d3_witness_bytes_read",
    ]
    return {field: 0 for field in fields}


def _add_counts(target: dict[str, int], source: Mapping[str, int]) -> None:
    for key, value in source.items():
        if type(value) is int:
            target[key] = target.get(key, 0) + value


def _finalize_query_counters(counters: dict[str, int]) -> dict[str, int]:
    counters["probes"] = counters.get("dictionary_probes", 0)
    counters["point_reads"] = (
        counters.get("d2_point_reads", 0)
        + counters.get("target_point_reads", 0)
        + counters.get("d3_key_reads", 0)
    )
    counters["witness_reads"] = (
        counters.get("d2_witness_reads", 0)
        + counters.get("d3_witness_reads", 0)
    )
    counters["logical_point_bytes_read"] = (
        counters.get("logical_d2_point_bytes_read", 0)
        + counters.get("logical_target_point_bytes_read", 0)
        + counters.get("logical_d3_key_bytes_read", 0)
    )
    counters["logical_witness_bytes_read"] = (
        counters.get("logical_d2_witness_bytes_read", 0)
        + counters.get("logical_d3_witness_bytes_read", 0)
    )
    counters["logical_key_bytes_read"] = counters.get("logical_d3_key_bytes_read", 0)
    counters["logical_bytes_read"] = (
        counters["logical_point_bytes_read"]
        + counters["logical_witness_bytes_read"]
    )
    return counters


def _result_aliases(result: dict[str, Any], counters: Mapping[str, int]) -> None:
    for field in (
        "probes",
        "dictionary_probes",
        "point_reads",
        "witness_reads",
        "logical_point_bytes_read",
        "logical_key_bytes_read",
        "logical_witness_bytes_read",
        "logical_bytes_read",
    ):
        result[field] = counters.get(field, 0)


def _query_support(
    curve: Any,
    target: Point,
    factor_points: Sequence[Point],
    d2: Any,
    support: D3Support | PartialD3Cache,
    *,
    ops_like: Any | None,
    verify_witness: bool,
) -> dict[str, Any]:
    start = time.perf_counter()
    factors = _validate_factor_points(factor_points)
    d2_points, d2_witnesses = _d2_parts(d2, len(factors))
    if support.p != getattr(curve, "p", None):
        raise ValueError("D3 support field does not match curve")
    ops = _new_ops(ops_like, d2, support)
    counters = _new_query_counters()
    point_bytes = logical_point_bytes(support.p)
    index_bytes = logical_factor_index_bytes(len(factors))
    witness: Witness5 | None = None
    d2_index: int | None = None
    d3_index: int | None = None
    complement: Point = None

    for index, partial in enumerate(d2_points):
        counters["d2_point_reads"] += 1
        counters["target_point_reads"] += 1
        counters["logical_d2_point_bytes_read"] += point_bytes
        counters["logical_target_point_bytes_read"] += point_bytes
        extras = _scalar_subtraction_extras(target, partial, support.p)
        _add_counts(counters, extras)
        complement = curve.add(target, curve.neg(partial), ops)
        counters["complement_tests"] += 1
        counters["dictionary_probes"] += 1
        counters["d3_key_reads"] += 1
        counters["logical_d3_key_bytes_read"] += point_bytes
        found = support.point_to_index.get(complement)
        if found is None:
            continue
        counters["d2_witness_reads"] += 1
        counters["d3_witness_reads"] += 1
        counters["logical_d2_witness_bytes_read"] += 2 * index_bytes
        counters["logical_d3_witness_bytes_read"] += 3 * index_bytes
        witness = tuple(sorted(d2_witnesses[index] + support.witnesses[found]))
        d2_index = index
        d3_index = found
        break

    operation_record = ops_record(ops)
    for field in _NATIVE_OP_FIELDS:
        counters[field] = operation_record[field]
    _finalize_query_counters(counters)
    audit = _empty_audit(ops_like, d2, support)
    if witness is not None and verify_witness:
        audit = verify_five_leaf_witness(curve, factors, witness, target, ops_like)
        if not audit["verified"]:
            raise AssertionError("D2+D3 query reconstructed an invalid five-leaf witness")
    result: dict[str, Any] = {
        "success": witness is not None,
        "witness": list(witness) if witness is not None else None,
        "d2_index": d2_index,
        "d3_index": d3_index,
        "complement": point_json(complement) if d2_index is not None else None,
        "ops": ops,
        "operation_record": operation_record,
        "counters": counters,
        "weighted_field_work": weighted_field_work(operation_record),
        "witness_verification_audit": audit,
        "witness_verification_audit_ops": audit["ops"],
        "wall_time_seconds": time.perf_counter() - start,
    }
    _result_aliases(result, counters)
    return result


def query_scalar_d2_d3(
    curve: Any,
    target: Point,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_like: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Exact target-major scalar D2 scan against full D3 advice."""

    return _query_support(
        curve,
        target,
        factor_points,
        d2,
        d3,
        ops_like=ops_like,
        verify_witness=verify_witness,
    )


def build_partial_d3_cache(
    d3: D3Support,
    numerator: int,
    denominator: int,
    seed: int,
    *,
    label: str = "partial-d3",
) -> PartialD3Cache:
    """Retain floor(|D3|*numerator/denominator) points by public SHA rank."""

    exact_numerator = _exact_int(numerator, "numerator", 1)
    exact_denominator = _exact_int(denominator, "denominator", 1)
    exact_seed = _exact_int(seed, "seed", 0)
    if exact_numerator > exact_denominator:
        raise ValueError("partial D3 numerator must not exceed denominator")
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a nonempty string")
    keep = len(d3.points) * exact_numerator // exact_denominator
    ranked_indices = sorted(
        range(len(d3.points)),
        key=lambda index: (
            _sha_rank(exact_seed, label, d3.p, d3.points[index]),
            point_sort_key(d3.points[index]),
        ),
    )
    selected_indices = ranked_indices[:keep]
    selected_indices.sort(key=lambda index: point_sort_key(d3.points[index]))
    points = [d3.points[index] for index in selected_indices]
    witnesses = [d3.witnesses[index] for index in selected_indices]
    entries = [
        {"point": point_json(point), "witness": list(witness)}
        for point, witness in zip(points, witnesses)
    ]
    factor_count = _exact_int(
        d3.record.get(
            "factor_count",
            max(
                (index for witness in d3.witnesses for index in witness),
                default=0,
            )
            + 1,
        ),
        "D3 factor_count",
        1,
    )
    advice = _advice_record(
        p=d3.p,
        factor_count=factor_count,
        leaf_count=3,
        entries=entries,
    )
    ranking_artifact = [
        {
            "point": point_json(d3.points[index]),
            "rank": _sha_rank(exact_seed, label, d3.p, d3.points[index]).hex(),
        }
        for index in ranked_indices
    ]
    record = {
        "kind": "sha256_ranked_partial_d3",
        "source_advice_digest": d3.record["advice_digest"],
        "source_size": len(d3.points),
        "retained_size": keep,
        "numerator": exact_numerator,
        "denominator": exact_denominator,
        "retention_rounding": "floor",
        "seed": exact_seed,
        "label": label,
        "target_independent": True,
        "ranking_digest": stable_digest(ranking_artifact),
        **advice,
        "python_deep_bytes": deep_size(
            {"points": points, "witnesses": witnesses, "source_indices": selected_indices}
        ),
    }
    return PartialD3Cache(
        p=d3.p,
        points=points,
        witnesses=witnesses,
        point_to_index={point: index for index, point in enumerate(points)},
        point_to_witness={point: witness for point, witness in zip(points, witnesses)},
        source_indices=selected_indices,
        numerator=exact_numerator,
        denominator=exact_denominator,
        seed=exact_seed,
        record=record,
    )


def query_partial_d3_cache(
    curve: Any,
    target: Point,
    factor_points: Sequence[Point],
    d2: Any,
    cache: PartialD3Cache,
    fallback: Callable[[Point], Mapping[str, Any]],
    ops_like: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Query partial advice, invoking and charging a complete fallback on miss."""

    start = time.perf_counter()
    if not callable(fallback):
        raise TypeError("fallback must be callable")
    cache_stage = _query_support(
        curve,
        target,
        factor_points,
        d2,
        cache,
        ops_like=ops_like,
        verify_witness=verify_witness,
    )
    if cache_stage["success"]:
        cache_stage["source"] = "partial_cache"
        cache_stage["cache_hit"] = True
        cache_stage["fallback_used"] = False
        cache_stage["cache_stage"] = cache_stage.copy()
        cache_stage["fallback_stage"] = None
        cache_stage["wall_time_seconds"] = time.perf_counter() - start
        return cache_stage

    fallback_stage = fallback(target)
    if not isinstance(fallback_stage, Mapping):
        raise TypeError("fallback must return a mapping with success and counters")
    if "success" not in fallback_stage or "counters" not in fallback_stage:
        raise ValueError("fallback result must expose success and counters")
    fallback_stage = dict(fallback_stage)
    fallback_counters = fallback_stage["counters"]
    if not isinstance(fallback_counters, Mapping):
        raise TypeError("fallback counters must be a mapping")

    combined = _new_query_counters()
    _add_counts(combined, cache_stage["counters"])
    _add_counts(combined, fallback_counters)
    _finalize_query_counters(combined)
    combined_ops = _ops_from_record(combined, ops_like, d2)
    witness_raw = fallback_stage.get("witness")
    success = bool(fallback_stage["success"])
    if success != (witness_raw is not None):
        raise ValueError("fallback success flag and witness disagree")
    boundary_audit = _empty_audit(ops_like, d2)
    if success and verify_witness:
        boundary_audit = verify_five_leaf_witness(
            curve,
            factor_points,
            tuple(witness_raw),
            target,
            ops_like,
        )
        if not boundary_audit["verified"]:
            raise AssertionError("complete fallback returned an invalid witness")
    result: dict[str, Any] = {
        "success": success,
        "witness": list(witness_raw) if witness_raw is not None else None,
        "d2_index": fallback_stage.get("d2_index"),
        "d3_index": fallback_stage.get("d3_index"),
        "complement": fallback_stage.get("complement"),
        "source": "complete_fallback",
        "cache_hit": False,
        "fallback_used": True,
        "cache_stage": cache_stage,
        "fallback_stage": fallback_stage,
        "ops": combined_ops,
        "operation_record": ops_record(combined_ops),
        "counters": combined,
        "weighted_field_work": weighted_field_work(combined),
        "witness_verification_audit": boundary_audit,
        "witness_verification_audit_ops": boundary_audit["ops"],
        "wall_time_seconds": time.perf_counter() - start,
    }
    _result_aliases(result, combined)
    return result


def montgomery_batch_inverse(values: Sequence[int], p: int) -> dict[str, Any]:
    """Invert nonzero field values with one inversion and exact mult counts."""

    modulus = _exact_int(p, "p", 2)
    normalized: list[int] = []
    for index, value in enumerate(values):
        exact = _exact_int(value, f"values[{index}]") % modulus
        if exact == 0:
            raise ZeroDivisionError("Montgomery batch inversion input contains zero")
        normalized.append(exact)
    if not normalized:
        return {
            "inverses": [],
            "field_inversions": 0,
            "prefix_multiplications": 0,
            "backward_multiplications": 0,
            "field_multiplications": 0,
        }

    prefixes = [normalized[0]]
    for value in normalized[1:]:
        prefixes.append(prefixes[-1] * value % modulus)
    accumulator = pow(prefixes[-1], -1, modulus)
    inverses = [0] * len(normalized)
    backward = 0
    for index in range(len(normalized) - 1, 0, -1):
        inverses[index] = accumulator * prefixes[index - 1] % modulus
        accumulator = accumulator * normalized[index] % modulus
        backward += 2
    inverses[0] = accumulator
    prefix = len(normalized) - 1
    return {
        "inverses": inverses,
        "field_inversions": 1,
        "prefix_multiplications": prefix,
        "backward_multiplications": backward,
        "field_multiplications": prefix + backward,
    }


def batch_affine_subtract(
    curve: Any,
    targets: Sequence[Point],
    subtrahend: Point,
    ops_like: Any | None = None,
    *,
    verify_scalar: bool = False,
) -> dict[str, Any]:
    """Compute all Q-A using one Montgomery inversion for nonexceptional rows.

    Identity and inverse routes need no denominator.  Q=-A is a doubling route
    for Q+(-A); Q=A is the inverse route yielding infinity.
    """

    start = time.perf_counter()
    p = _exact_int(getattr(curve, "p", None), "curve.p", 2)
    target_list = list(targets)
    ops = _new_ops(ops_like)
    counters = _new_query_counters()
    counters["group_operations"] = len(target_list)
    counters["complement_tests"] = len(target_list)
    counters["target_point_reads"] = len(target_list)
    counters["d2_point_reads"] = 1 if target_list else 0
    counters["point_identity_tests"] = len(target_list)
    results: list[Point] = [None] * len(target_list)
    pending: list[dict[str, Any]] = []
    right = curve.neg(subtrahend)

    for ordinal, target in enumerate(target_list):
        if target is None:
            counters["identity_routes"] += 1
            results[ordinal] = right
            continue
        counters["point_identity_tests"] += 1
        if subtrahend is None:
            counters["identity_routes"] += 1
            results[ordinal] = target
            continue
        assert right is not None
        x1, y1 = target
        x2, y2 = right
        counters["field_zero_tests"] += 1
        if x1 == x2:
            counters["field_additions"] += 1
            counters["field_zero_tests"] += 1
            if (y1 + y2) % p == 0:
                counters["inverse_routes"] += 1
                results[ordinal] = None
                continue
        if target == right:
            denominator = 2 * y1 % p
            if denominator == 0:
                raise AssertionError("zero doubling denominator escaped inverse route")
            x_square = x1 * x1 % p
            numerator = (3 * x_square + curve.a) % p
            counters["doubling_routes"] += 1
            counters["point_doublings"] += 1
            counters["field_multiplications"] += 4
            counters["field_additions"] += 5
            pending.append(
                {
                    "ordinal": ordinal,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "numerator": numerator,
                    "denominator": denominator,
                }
            )
        else:
            denominator = (x2 - x1) % p
            if denominator == 0:
                raise AssertionError("invalid affine pair has a zero ordinary denominator")
            numerator = (y2 - y1) % p
            counters["ordinary_routes"] += 1
            counters["point_additions"] += 1
            counters["field_multiplications"] += 3
            counters["field_additions"] += 6
            pending.append(
                {
                    "ordinal": ordinal,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "numerator": numerator,
                    "denominator": denominator,
                }
            )

    inversion = montgomery_batch_inverse(
        [entry["denominator"] for entry in pending],
        p,
    )
    field_bytes = max(1, math.ceil(p.bit_length() / 8))
    target_index_bytes = max(
        1,
        math.ceil(max(1, (len(target_list) - 1).bit_length()) / 8),
    )
    counters["peak_batch_pending_entries"] = len(pending)
    counters["peak_batch_workspace_logical_bytes"] = (
        len(pending) * (8 * field_bytes + target_index_bytes)
        + len(target_list) * target_index_bytes
    )
    counters["field_inversions"] = inversion["field_inversions"]
    counters["inversion_batches"] = inversion["field_inversions"]
    counters["batch_denominators"] = len(pending)
    counters["prefix_multiplications"] = inversion["prefix_multiplications"]
    counters["backward_multiplications"] = inversion["backward_multiplications"]
    counters["field_multiplications"] += inversion["field_multiplications"]
    for entry, inverse in zip(pending, inversion["inverses"]):
        slope = entry["numerator"] * inverse % p
        x3 = (slope * slope - entry["x1"] - entry["x2"]) % p
        y3 = (slope * (entry["x1"] - x3) - entry["y1"]) % p
        results[entry["ordinal"]] = (x3, y3)

    for field in _NATIVE_OP_FIELDS:
        _increment_ops(ops, field, counters[field])
    point_bytes = logical_point_bytes(p)
    counters["logical_d2_point_bytes_read"] = counters["d2_point_reads"] * point_bytes
    counters["logical_target_point_bytes_read"] = counters["target_point_reads"] * point_bytes
    _finalize_query_counters(counters)

    audit_ops = _new_ops(ops_like)
    audit_record = {
        "performed": verify_scalar,
        "exact": None,
        "ops": audit_ops,
        "counters": {
            **ops_record(audit_ops),
            "target_point_reads": 0,
            "subtrahend_point_reads": 0,
            "logical_bytes_read": 0,
        },
    }
    if verify_scalar:
        expected = [curve.add(target, curve.neg(subtrahend), audit_ops) for target in target_list]
        exact = expected == results
        audit_record = {
            "performed": True,
            "exact": exact,
            "ops": audit_ops,
            "counters": {
                **ops_record(audit_ops),
                "target_point_reads": len(target_list),
                "subtrahend_point_reads": len(target_list),
                "logical_bytes_read": 2 * len(target_list) * point_bytes,
            },
        }
        if not exact:
            raise AssertionError("batched affine subtraction disagrees with scalar Curve.add")

    return {
        "points": results,
        "ops": ops,
        "operation_record": ops_record(ops),
        "counters": counters,
        "weighted_field_work": weighted_field_work(counters),
        "scalar_equality_audit": audit_record,
        "wall_time_seconds": time.perf_counter() - start,
    }


def _target_points(targets: Sequence[Point] | TargetSchedule) -> list[Point]:
    return list(targets.points if isinstance(targets, TargetSchedule) else targets)


def query_d2_major_batch(
    curve: Any,
    targets: Sequence[Point] | TargetSchedule,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_like: Any | None = None,
    *,
    verify_witness: bool = True,
    verify_affine: bool = False,
) -> dict[str, Any]:
    """D2-major exact batch query with one D2 point read per processed row."""

    start = time.perf_counter()
    target_list = _target_points(targets)
    factors = _validate_factor_points(factor_points)
    d2_points, d2_witnesses = _d2_parts(d2, len(factors))
    if d3.p != getattr(curve, "p", None):
        raise ValueError("D3 field does not match curve")
    point_bytes = logical_point_bytes(d3.p)
    index_bytes = logical_factor_index_bytes(len(factors))
    counters = _new_query_counters()
    per_target: list[dict[str, Any]] = [
        {
            "success": False,
            "witness": None,
            "d2_index": None,
            "d3_index": None,
            "complement": None,
        }
        for _ in target_list
    ]
    active = list(range(len(target_list)))
    affine_audit_counters: dict[str, int] = {}
    affine_audit_performed = verify_affine

    for d2_index, partial in enumerate(d2_points):
        if not active:
            break
        active_targets = [target_list[index] for index in active]
        row = batch_affine_subtract(
            curve,
            active_targets,
            partial,
            ops_like,
            verify_scalar=verify_affine,
        )
        for field in _NATIVE_OP_FIELDS:
            counters[field] += row["operation_record"][field]
        for field in (
            "field_additions",
            "field_zero_tests",
            "point_identity_tests",
            "identity_routes",
            "inverse_routes",
            "doubling_routes",
            "ordinary_routes",
            "complement_tests",
            "inversion_batches",
            "batch_denominators",
            "prefix_multiplications",
            "backward_multiplications",
        ):
            counters[field] += row["counters"][field]
        counters["peak_batch_pending_entries"] = max(
            counters["peak_batch_pending_entries"],
            row["counters"]["peak_batch_pending_entries"],
        )
        counters["peak_batch_workspace_logical_bytes"] = max(
            counters["peak_batch_workspace_logical_bytes"],
            row["counters"]["peak_batch_workspace_logical_bytes"],
        )
        counters["d2_point_reads"] += 1
        counters["target_point_reads"] += len(active)
        counters["logical_d2_point_bytes_read"] += point_bytes
        counters["logical_target_point_bytes_read"] += len(active) * point_bytes
        if verify_affine:
            _add_counts(
                affine_audit_counters,
                row["scalar_equality_audit"]["counters"],
            )

        row_witness: Witness2 | None = None
        solved_this_row: set[int] = set()
        for target_index, complement in zip(active, row["points"]):
            counters["dictionary_probes"] += 1
            counters["d3_key_reads"] += 1
            counters["logical_d3_key_bytes_read"] += point_bytes
            d3_index = d3.point_to_index.get(complement)
            if d3_index is None:
                continue
            if row_witness is None:
                row_witness = d2_witnesses[d2_index]
                counters["d2_witness_reads"] += 1
                counters["logical_d2_witness_bytes_read"] += 2 * index_bytes
            counters["d3_witness_reads"] += 1
            counters["logical_d3_witness_bytes_read"] += 3 * index_bytes
            witness = tuple(sorted(row_witness + d3.witnesses[d3_index]))
            per_target[target_index] = {
                "success": True,
                "witness": list(witness),
                "d2_index": d2_index,
                "d3_index": d3_index,
                "complement": point_json(complement),
            }
            solved_this_row.add(target_index)
        if solved_this_row:
            active = [index for index in active if index not in solved_this_row]

    _finalize_query_counters(counters)
    ops = _ops_from_record(counters, ops_like, d2, d3)
    witness_audit_ops = _new_ops(ops_like, d2, d3)
    witness_audit_counters: dict[str, int] = {}
    all_verified: bool | None = None
    if verify_witness:
        all_verified = True
        for target, result in zip(target_list, per_target):
            if not result["success"]:
                continue
            audit = verify_five_leaf_witness(
                curve,
                factors,
                tuple(result["witness"]),
                target,
                ops_like,
            )
            _add_counts(witness_audit_counters, audit["counters"])
            if not audit["verified"]:
                all_verified = False
                raise AssertionError("batched D2+D3 query returned an invalid witness")
        witness_audit_ops = _ops_from_record(witness_audit_counters, ops_like, d2, d3)

    solved_indices = [index for index, result in enumerate(per_target) if result["success"]]
    result = {
        "mode": "d2_major_montgomery_batch",
        "target_count": len(target_list),
        "success_count": len(solved_indices),
        "solved_indices": solved_indices,
        "per_target": per_target,
        "ops": ops,
        "operation_record": ops_record(ops),
        "counters": counters,
        "weighted_field_work": weighted_field_work(counters),
        "witness_verification_audit": {
            "performed": verify_witness,
            "verified": all_verified,
            "ops": witness_audit_ops,
            "counters": witness_audit_counters,
        },
        "witness_verification_audit_ops": witness_audit_ops,
        "affine_equality_audit": {
            "performed": affine_audit_performed,
            "exact": True if affine_audit_performed else None,
            "counters": affine_audit_counters,
        },
        "wall_time_seconds": time.perf_counter() - start,
    }
    _result_aliases(result, counters)
    return result


def query_target_major_batch(
    curve: Any,
    targets: Sequence[Point] | TargetSchedule,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_like: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Run independent scalar queries and return one honest batch summary."""

    start = time.perf_counter()
    target_list = _target_points(targets)
    per_target = [
        query_scalar_d2_d3(
            curve,
            target,
            factor_points,
            d2,
            d3,
            ops_like,
            verify_witness=verify_witness,
        )
        for target in target_list
    ]
    counters = _new_query_counters()
    audit_counters: dict[str, int] = {}
    for result in per_target:
        _add_counts(counters, result["counters"])
        _add_counts(
            audit_counters,
            result["witness_verification_audit"]["counters"],
        )
    _finalize_query_counters(counters)
    ops = _ops_from_record(counters, ops_like, d2, d3)
    audit_ops = _ops_from_record(audit_counters, ops_like, d2, d3)
    solved_indices = [index for index, result in enumerate(per_target) if result["success"]]
    summary = {
        "mode": "target_major_scalar_batch",
        "target_count": len(target_list),
        "success_count": len(solved_indices),
        "solved_indices": solved_indices,
        "per_target": per_target,
        "ops": ops,
        "operation_record": ops_record(ops),
        "counters": counters,
        "weighted_field_work": weighted_field_work(counters),
        "witness_verification_audit": {
            "performed": verify_witness,
            "verified": all(
                (not result["success"])
                or result["witness_verification_audit"]["verified"]
                for result in per_target
            ) if verify_witness else None,
            "ops": audit_ops,
            "counters": audit_counters,
        },
        "witness_verification_audit_ops": audit_ops,
        "wall_time_seconds": time.perf_counter() - start,
    }
    _result_aliases(summary, counters)
    return summary


def build_d3(
    curve: Any,
    factor_points: Sequence[Point],
    d2: Any,
    ops_factory: Any | None = None,
) -> D3Support:
    """Concise public wrapper for :func:`build_exact_d3`."""

    return build_exact_d3(curve, factor_points, d2, ops_factory)


def make_target_schedule(
    kind: str,
    count: int,
    seed: int,
    *,
    d5_support: D5AuditSupport | None = None,
    curve: Any | None = None,
    q: int | None = None,
    generator: Point = None,
    ops_factory: Any | None = None,
    label: str | None = None,
) -> TargetSchedule:
    """Build a point-only ``supported`` or ``uniform`` target schedule.

    Supported schedules require ``d5_support``.  Uniform schedules require
    ``curve``, ``q``, and a nonidentity ``generator``.  No scalar is returned.
    """

    if kind == "supported":
        if d5_support is None:
            raise ValueError("supported target schedule requires d5_support")
        return supported_target_schedule(
            d5_support,
            count,
            seed,
            label=label or "supported",
        )
    if kind == "uniform":
        if curve is None or q is None or generator is None:
            raise ValueError("uniform target schedule requires curve, q, and generator")
        return uniform_target_schedule(
            curve,
            q,
            generator,
            count,
            seed,
            ops_like=ops_factory,
            label=label or "uniform",
        )
    raise ValueError("target schedule kind must be 'supported' or 'uniform'")


def query_d2_d3(
    curve: Any,
    target: Point,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_factory: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Concise public wrapper for one exact scalar D2+D3 query."""

    return query_scalar_d2_d3(
        curve,
        target,
        factor_points,
        d2,
        d3,
        ops_factory,
        verify_witness=verify_witness,
    )


def build_partial_d3(
    d3: D3Support,
    numerator: int,
    denominator: int,
    seed: int,
    *,
    label: str = "partial-d3",
) -> PartialD3Cache:
    """Concise public wrapper for deterministic partial-D3 construction."""

    return build_partial_d3_cache(
        d3,
        numerator,
        denominator,
        seed,
        label=label,
    )


def query_partial_d3(
    curve: Any,
    target: Point,
    factor_points: Sequence[Point],
    d2: Any,
    cache: PartialD3Cache,
    fallback: Callable[[Point], Mapping[str, Any]],
    ops_factory: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Concise public partial-cache query with a charged complete fallback."""

    return query_partial_d3_cache(
        curve,
        target,
        factor_points,
        d2,
        cache,
        fallback,
        ops_factory,
        verify_witness=verify_witness,
    )


def run_target_major_batch(
    curve: Any,
    targets: Sequence[Point] | TargetSchedule,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_factory: Any | None = None,
    *,
    verify_witness: bool = True,
) -> dict[str, Any]:
    """Concise public target-major scalar-batch entry point."""

    return query_target_major_batch(
        curve,
        targets,
        factor_points,
        d2,
        d3,
        ops_factory,
        verify_witness=verify_witness,
    )


def run_d2_major_batch(
    curve: Any,
    targets: Sequence[Point] | TargetSchedule,
    factor_points: Sequence[Point],
    d2: Any,
    d3: D3Support,
    ops_factory: Any | None = None,
    *,
    verify_witness: bool = True,
    verify_affine: bool = False,
) -> dict[str, Any]:
    """Concise public D2-major Montgomery-batch entry point."""

    return query_d2_major_batch(
        curve,
        targets,
        factor_points,
        d2,
        d3,
        ops_factory,
        verify_witness=verify_witness,
        verify_affine=verify_affine,
    )


# Longer compatibility names retained for explicit callers.
build_exact_d5_support = build_d5_audit_support
deterministic_supported_targets = supported_target_schedule
deterministic_uniform_targets = uniform_target_schedule
query_d2_d3_scalar = query_scalar_d2_d3
query_d2_major_batched = query_d2_major_batch
query_target_major = query_target_major_batch


__all__ = [
    "DEFAULT_INVERSION_WEIGHTS",
    "D3Support",
    "D5AuditSupport",
    "PartialD3Cache",
    "Point",
    "TargetSchedule",
    "batch_affine_subtract",
    "build_d3",
    "build_d5_audit_support",
    "build_exact_d3",
    "build_exact_d5_support",
    "build_partial_d3",
    "build_partial_d3_cache",
    "deterministic_supported_targets",
    "deterministic_uniform_targets",
    "logical_factor_index_bytes",
    "logical_point_bytes",
    "montgomery_batch_inverse",
    "make_target_schedule",
    "ops_record",
    "point_json",
    "point_sort_key",
    "query_d2_d3",
    "query_d2_d3_scalar",
    "query_d2_major_batch",
    "query_d2_major_batched",
    "query_partial_d3",
    "query_partial_d3_cache",
    "query_scalar_d2_d3",
    "query_target_major",
    "query_target_major_batch",
    "run_d2_major_batch",
    "run_target_major_batch",
    "stable_digest",
    "supported_target_schedule",
    "uniform_target_schedule",
    "verify_five_leaf_witness",
    "weighted_field_work",
]

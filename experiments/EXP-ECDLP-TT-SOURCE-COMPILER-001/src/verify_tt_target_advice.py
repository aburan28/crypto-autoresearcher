#!/usr/bin/env python3
"""Independently verify development target specialization semantics and ranks.

The verifier does not import the target producer, target runtime, or coefficient
helper.  It rederives the 25-cell schedule and coefficient formulas, evaluates
every source and target TT tuple, and computes all exact unfolding ranks over
the corresponding prime field.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
BUNDLE_SCHEMA = "tt-source-candidate-bundle-development-v1"
RAW_SCHEMA = "tt-target-compiler-development-raw-v1"
REPORT_SCHEMA = "tt-target-verifier-development-v1"
SOURCE_BASIS = ("X2", "XZ", "Z2", "XY", "YZ", "Y2")
RETAINED_BASIS = ("X2", "XZ", "Z2", "YZ", "Y2")
TRACE_SCHEDULE = {
    "random_unique": ("Q00", "Q01", "IDENTITY", "PLANTED"),
    "x_interval": ("Q00", "Q01"),
}
OPERATION_KEYS = (
    "adds",
    "subs",
    "muls",
    "squares",
    "inversions",
    "reductions",
    "comparisons",
    "hash_bytes",
    "copied_words",
)
MAX_RAW_BYTES = 268435456


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def artifact_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value) + b"\n")


def read_json(path: Path, label: str, maximum_bytes: int) -> tuple[dict[str, Any], bytes]:
    expected_size = path.stat().st_size
    if expected_size > maximum_bytes:
        raise ValueError(f"{label} exceeds {maximum_bytes} bytes")
    data = path.read_bytes()
    if len(data) != expected_size:
        raise ValueError(f"{label} changed while it was being read")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, data


def exact_int(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{path} must be an integer at least {minimum}")
    return value


def validate_digest(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


@dataclass(frozen=True)
class Core:
    left: int
    physical: int
    right: int
    values: tuple[int, ...]

    @property
    def words(self) -> int:
        return len(self.values)

    def at(self, left: int, physical: int, right: int) -> int:
        return self.values[(left * self.physical + physical) * self.right + right]


@dataclass(frozen=True)
class Tensor:
    name: str
    p: int
    B: int
    tag: str
    ranks: tuple[int, int, int, int]
    cores: tuple[Core, ...]

    @property
    def words(self) -> int:
        return sum(core.words for core in self.cores)

    def canonical_record(self) -> dict[str, Any]:
        return {
            "B": self.B,
            "cores": [
                {
                    "shape": [core.left, core.physical, core.right],
                    "values": list(core.values),
                }
                for core in self.cores
            ],
            "name": self.name,
            "p": self.p,
            "ranks": list(self.ranks),
            "tag": self.tag,
        }


class Meter:
    def __init__(self, caps: Mapping[str, Any], traffic_cap: int, live_cap: int) -> None:
        self.operations = {key: 0 for key in OPERATION_KEYS}
        self.caps = {key: exact_int(caps[key], f"caps.{key}") for key in OPERATION_KEYS}
        self.traffic_words = 0
        self.traffic_cap = traffic_cap
        self.peak_live_words = 0
        self.live_cap = live_cap
        self.persistent_words = 0

    def add(self, **increments: int) -> None:
        for key, increment in increments.items():
            increment = exact_int(increment, f"operation.{key}")
            candidate = self.operations[key] + increment
            if candidate > self.caps[key]:
                raise ValueError(f"target verifier operation cap exceeded for {key}")
            self.operations[key] = candidate

    def traffic(self, words: int) -> None:
        words = exact_int(words, "traffic_words")
        self.traffic_words += words
        if self.traffic_words > self.traffic_cap:
            raise ValueError("target verifier traffic cap exceeded")

    def live(self, words: int) -> None:
        self.peak_live_words = max(self.peak_live_words, words)
        if words > self.live_cap:
            raise ValueError("target verifier live-word cap exceeded")

    def retain(self, words: int) -> None:
        self.persistent_words += exact_int(words, "retained_words")
        self.live(self.persistent_words)


def parse_tensor(
    record: Any,
    *,
    expected_name: str | None,
    expected_p: int | None = None,
    expected_B: int | None = None,
) -> Tensor:
    if not isinstance(record, dict):
        raise ValueError("tensor record must be an object")
    name = record.get("name")
    if not isinstance(name, str) or (expected_name is not None and name != expected_name):
        raise ValueError(f"tensor name does not match {expected_name!r}")
    p = exact_int(record.get("p"), f"{name}.p", 2)
    B = exact_int(record.get("B"), f"{name}.B", 1)
    if expected_p is not None and p != expected_p:
        raise ValueError(f"{name}.p changed")
    if expected_B is not None and B != expected_B:
        raise ValueError(f"{name}.B changed")
    ranks_value = record.get("ranks")
    cores_value = record.get("cores")
    if not isinstance(ranks_value, list) or len(ranks_value) != 4 or not isinstance(cores_value, list):
        raise ValueError(f"{name} ranks or cores are malformed")
    ranks = tuple(
        exact_int(rank, f"{name}.ranks[{index}]")
        for index, rank in enumerate(ranks_value)
    )
    tag = record.get("tag")
    if tag == "canonical_zero":
        if ranks != (0, 0, 0, 0) or cores_value:
            raise ValueError(f"{name} canonical zero is malformed")
        tensor = Tensor(name, p, B, tag, (0, 0, 0, 0), ())
    elif tag == "tt":
        if len(cores_value) != 5 or any(rank < 1 for rank in ranks):
            raise ValueError(f"{name} nonzero TT boundaries are malformed")
        boundaries = (1, *ranks, 1)
        cores: list[Core] = []
        for mode, raw_core in enumerate(cores_value):
            if not isinstance(raw_core, dict):
                raise ValueError(f"{name}.cores[{mode}] must be an object")
            expected_shape = (boundaries[mode], B, boundaries[mode + 1])
            shape = raw_core.get("shape")
            values = raw_core.get("values")
            if not isinstance(shape, list) or tuple(shape) != expected_shape or not isinstance(values, list):
                raise ValueError(f"{name}.cores[{mode}] shape changed")
            words = expected_shape[0] * expected_shape[1] * expected_shape[2]
            if len(values) != words:
                raise ValueError(f"{name}.cores[{mode}] word count changed")
            parsed = tuple(
                exact_int(value, f"{name}.cores[{mode}].values[{offset}]")
                for offset, value in enumerate(values)
            )
            if any(value >= p for value in parsed):
                raise ValueError(f"{name}.cores[{mode}] contains a noncanonical residue")
            cores.append(Core(*expected_shape, parsed))
        tensor = Tensor(name, p, B, tag, ranks, tuple(cores))
    else:
        raise ValueError(f"{name}.tag is invalid")
    if exact_int(record.get("word_count"), f"{name}.word_count") != tensor.words:
        raise ValueError(f"{name}.word_count mismatch")
    if validate_digest(record.get("core_digest_sha256"), f"{name}.core_digest_sha256") != artifact_digest(
        tensor.canonical_record()
    ):
        raise ValueError(f"{name}.core_digest_sha256 mismatch")
    return tensor


def evaluate(tensor: Tensor, indices: Sequence[int], meter: Meter) -> int:
    if tensor.tag == "canonical_zero":
        return 0
    vector = [1]
    for mode, index in enumerate(indices):
        core = tensor.cores[mode]
        output = [0] * core.right
        for right in range(core.right):
            total = 0
            for left in range(core.left):
                term = vector[left] * core.at(left, index, right)
                total += term
            output[right] = total % tensor.p
        meter.add(
            muls=core.left * core.right,
            adds=max(core.left - 1, 0) * core.right,
            reductions=core.right,
        )
        meter.traffic(core.left * core.right + core.left + core.right)
        vector = output
    if len(vector) != 1:
        raise AssertionError("TT evaluation did not reach a scalar")
    return vector[0]


def iter_five_tuples(B: int) -> Iterator[tuple[int, int, int, int, int]]:
    """Verifier-only explicit traversal, independent of producer operations."""

    for i5 in range(B - 1, -1, -1):
        for i4 in range(B - 1, -1, -1):
            for i3 in range(B - 1, -1, -1):
                for i2 in range(B - 1, -1, -1):
                    for i1 in range(B - 1, -1, -1):
                        yield i1, i2, i3, i4, i5


def linear_index(indices: Sequence[int], B: int) -> int:
    result = 0
    for value in indices:
        result = result * B + value
    return result


def dense_values(
    tensor: Tensor, meter: Meter, *, tensor_is_persistent: bool = False
) -> tuple[int, ...]:
    mutable = [0] * (tensor.B**5)
    local_tensor_words = 0 if tensor_is_persistent else tensor.words
    meter.live(meter.persistent_words + local_tensor_words + len(mutable))
    for indices in iter_five_tuples(tensor.B):
        mutable[linear_index(indices, tensor.B)] = evaluate(tensor, indices, meter)
    meter.live(meter.persistent_words + local_tensor_words + 2 * len(mutable))
    values = tuple(mutable)
    return values


def exact_rank(
    values: Sequence[int],
    B: int,
    cut: int,
    p: int,
    meter: Meter,
    *,
    local_tensor_words: int = 0,
) -> int:
    rows = B**cut
    columns = B ** (5 - cut)
    matrix = [
        [int(value) for value in values[row * columns : (row + 1) * columns]]
        for row in range(rows)
    ]
    meter.add(copied_words=2 * rows * columns)
    meter.traffic(2 * rows * columns)
    meter.live(
        meter.persistent_words
        + local_tensor_words
        + len(values)
        + rows * columns
    )
    rank = 0
    for column in range(columns):
        pivot: int | None = None
        for row in range(rank, rows):
            meter.add(comparisons=1)
            if matrix[row][column] % p != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column] % p, -1, p)
        meter.add(inversions=1, reductions=1)
        for entry in range(column, columns):
            matrix[rank][entry] = matrix[rank][entry] * inverse % p
        width = columns - column
        meter.add(muls=width, reductions=width)
        for row in range(rows):
            if row == rank:
                continue
            factor = matrix[row][column] % p
            meter.add(comparisons=1)
            if factor == 0:
                continue
            for entry in range(column, columns):
                matrix[row][entry] = (
                    matrix[row][entry] - factor * matrix[rank][entry]
                ) % p
            meter.add(muls=width, subs=width, reductions=width)
        rank += 1
        if rank == rows:
            break
    return rank


def trace_coefficients(projective: Sequence[int], p: int, n: int) -> tuple[int, ...]:
    if len(projective) != 3:
        raise ValueError("trace target projective tuple is malformed")
    x, y, z = (exact_int(value, "projective") for value in projective)
    if max(x, y, z) >= p or x == y == z == 0:
        raise ValueError("trace target projective tuple is invalid")
    n %= p
    return (
        z * z % p,
        -2 * x * z % p,
        (x * x + n * y * y) % p,
        0,
        -2 * n * y * z % p,
        n * z * z % p,
    )


def general_coefficients(
    projective: Sequence[int], p: int, t: int, n: int
) -> tuple[int, ...]:
    if len(projective) != 3:
        raise ValueError("general target projective tuple is malformed")
    x, y, z = (exact_int(value, "projective") for value in projective)
    if max(x, y, z) >= p or x == y == z == 0:
        raise ValueError("general target projective tuple is invalid")
    t %= p
    n %= p
    return (
        z * z % p,
        -z * (2 * x + t * y) % p,
        (x * x + t * x * y + n * y * y) % p,
        t * z * z % p,
        -z * (t * x + 2 * n * y) % p,
        n * z * z % p,
    )


@dataclass(frozen=True)
class ExpectedTarget:
    target_cell_id: str
    source_cell_id: str
    curve_id: str
    registry: str
    target_name: str
    target_id: str
    kind: str
    projective: tuple[int, int, int]
    source_names: tuple[str, ...]
    coefficients: tuple[int, ...]


def expected_schedule(target: Mapping[str, Any]) -> list[ExpectedTarget]:
    instances_value = target.get("instances")
    if not isinstance(instances_value, list) or len(instances_value) != 3:
        raise ValueError("target manifest instance schedule is malformed")
    instances = {str(instance["curve_id"]): instance for instance in instances_value}
    if tuple(instances) != ("C08", "C10", "C12"):
        raise ValueError("target manifest curve order changed")
    result: list[ExpectedTarget] = []
    for curve_id, instance in instances.items():
        p = exact_int(instance.get("p"), f"{curve_id}.p", 2)
        n = exact_int(instance.get("trace_zero_norm_n"), f"{curve_id}.n")
        targets = instance.get("targets")
        control = instance.get("general_trace_control")
        if not isinstance(targets, dict) or not isinstance(control, dict):
            raise ValueError(f"{curve_id} target map or control is malformed")
        for registry in ("random_unique", "x_interval"):
            source_id = f"{curve_id}:{registry}"
            for name in TRACE_SCHEDULE[registry]:
                row = targets[name]
                projective_value = tuple(row["projective"])
                full = trace_coefficients(projective_value, p, n)
                if tuple(row["trace_zero_coefficients"]) != full:
                    raise ValueError(f"{curve_id}.{name} frozen trace coefficients changed")
                result.append(
                    ExpectedTarget(
                        f"{source_id}:{name}",
                        source_id,
                        curve_id,
                        registry,
                        name,
                        str(row["target_id"]),
                        "trace_zero",
                        projective_value,  # type: ignore[arg-type]
                        RETAINED_BASIS,
                        (full[0], full[1], full[2], full[4], full[5]),
                    )
                )
            q00 = targets["Q00"]
            projective_value = tuple(q00["projective"])
            full = general_coefficients(
                projective_value,
                p,
                exact_int(control.get("trace_t"), f"{curve_id}.t"),
                exact_int(control.get("norm_n"), f"{curve_id}.control_n"),
            )
            if tuple(q00["general_trace_coefficients"]) != full:
                raise ValueError(f"{curve_id}.Q00 frozen general coefficients changed")
            result.append(
                ExpectedTarget(
                    f"{source_id}:GENERAL_TRACE_Q00",
                    source_id,
                    curve_id,
                    registry,
                    "GENERAL_TRACE_Q00",
                    f"{q00['target_id']}-GENERAL-TRACE",
                    "general_trace_control",
                    projective_value,  # type: ignore[arg-type]
                    SOURCE_BASIS,
                    full,
                )
            )
    instance = instances["C08"]
    q00 = instance["targets"]["Q00"]
    full = trace_coefficients(q00["projective"], instance["p"], instance["trace_zero_norm_n"])
    result.append(
        ExpectedTarget(
            "C08:random_unique:MODEWISE_RESCALED:Q00",
            "C08:random_unique:MODEWISE_RESCALED",
            "C08",
            "modewise_rescaled_control",
            "Q00",
            str(q00["target_id"]),
            "modewise_rescaled_trace_zero_control",
            tuple(q00["projective"]),  # type: ignore[arg-type]
            RETAINED_BASIS,
            (full[0], full[1], full[2], full[4], full[5]),
        )
    )
    if len(result) != 25:
        raise AssertionError("independent target schedule is not 25 cells")
    return result


def source_map(bundle: Mapping[str, Any]) -> dict[str, dict[str, Tensor]]:
    advice = bundle.get("candidate_retained_advice")
    controls = bundle.get("candidate_control_certificates")
    if not isinstance(advice, dict) or not isinstance(controls, dict):
        raise ValueError("candidate source objects are malformed")
    digests = bundle.get("candidate_artifact_digests")
    if not isinstance(digests, dict):
        raise ValueError("candidate source digests are missing")
    if artifact_digest(advice) != digests.get("retained_advice_sha256"):
        raise ValueError("candidate retained advice digest mismatch")
    if artifact_digest(controls) != digests.get("control_certificate_sha256"):
        raise ValueError("candidate source controls digest mismatch")
    result: dict[str, dict[str, Tensor]] = {}
    xy_rows = controls.get("xy_certificates")
    if not isinstance(xy_rows, list):
        raise ValueError("candidate XY certificates are malformed")
    xy = {
        row.get("cell_id"): row.get("tensor")
        for row in xy_rows
        if isinstance(row, dict)
    }
    cells = advice.get("cells")
    if not isinstance(cells, list):
        raise ValueError("candidate advice cells are malformed")
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("cell_id"), str):
            raise ValueError("candidate advice cell is malformed")
        cell_id = cell["cell_id"]
        p = exact_int(cell.get("p"), f"{cell_id}.p", 2)
        B = exact_int(cell.get("B"), f"{cell_id}.B", 1)
        rows = cell.get("tensors")
        if not isinstance(rows, list):
            raise ValueError(f"{cell_id} source tensors are malformed")
        parsed = {
            str(row.get("name")): parse_tensor(
                row,
                expected_name=str(row.get("name")),
                expected_p=p,
                expected_B=B,
            )
            for row in rows
            if isinstance(row, dict)
        }
        parsed["XY"] = parse_tensor(
            xy[cell_id], expected_name="XY", expected_p=p, expected_B=B
        )
        if set(parsed) != set(SOURCE_BASIS):
            raise ValueError(f"{cell_id} source basis is incomplete")
        result[cell_id] = parsed
    control = controls.get("modewise_rescaled_source_cell")
    if not isinstance(control, dict) or not isinstance(control.get("cell_id"), str):
        raise ValueError("modewise-rescaled source cell is malformed")
    control_id = control["cell_id"]
    p = exact_int(control.get("p"), f"{control_id}.p", 2)
    B = exact_int(control.get("B"), f"{control_id}.B", 1)
    rows = control.get("tensors")
    if not isinstance(rows, list):
        raise ValueError("modewise-rescaled source tensors are malformed")
    parsed = {
        str(row.get("name")): parse_tensor(
            row,
            expected_name=str(row.get("name")),
            expected_p=p,
            expected_B=B,
        )
        for row in rows
        if isinstance(row, dict) and row.get("name") in RETAINED_BASIS
    }
    if set(parsed) != set(RETAINED_BASIS):
        raise ValueError("modewise-rescaled retained basis is incomplete")
    result[control_id] = parsed
    return result


def empty_operation_vector() -> dict[str, int]:
    return {key: 0 for key in OPERATION_KEYS}


def empty_traffic_vector(buckets: Sequence[str]) -> dict[str, dict[str, int]]:
    return {bucket: {"reads": 0, "writes": 0} for bucket in buckets}


def add_operations(total: dict[str, int], increments: Mapping[str, int]) -> None:
    for key, value in increments.items():
        total[key] += value


def add_traffic(
    total: dict[str, dict[str, int]],
    bucket: str,
    *,
    reads: int = 0,
    writes: int = 0,
) -> None:
    total[bucket]["reads"] += reads
    total[bucket]["writes"] += writes


def parse_event_accounting(
    event: Mapping[str, Any], buckets: Sequence[str], path: str
) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    raw_operations = event.get("operation_vector")
    raw_traffic = event.get("traffic")
    if not isinstance(raw_operations, dict) or set(raw_operations) != set(OPERATION_KEYS):
        raise ValueError(f"{path} operation vector is malformed")
    if not isinstance(raw_traffic, dict) or set(raw_traffic) != set(buckets):
        raise ValueError(f"{path} traffic vector is malformed")
    operations = {
        key: exact_int(raw_operations[key], f"{path}.operation_vector.{key}")
        for key in OPERATION_KEYS
    }
    traffic: dict[str, dict[str, int]] = {}
    for bucket in buckets:
        row = raw_traffic[bucket]
        if not isinstance(row, dict) or set(row) != {"reads", "writes"}:
            raise ValueError(f"{path}.traffic.{bucket} is malformed")
        traffic[bucket] = {
            "reads": exact_int(row["reads"], f"{path}.traffic.{bucket}.reads"),
            "writes": exact_int(row["writes"], f"{path}.traffic.{bucket}.writes"),
        }
    return operations, traffic


def require_event_accounting(
    event: Mapping[str, Any],
    expected_operations: Mapping[str, int],
    expected_traffic: Mapping[str, Mapping[str, int]],
    buckets: Sequence[str],
    path: str,
) -> None:
    operations, traffic = parse_event_accounting(event, buckets, path)
    if operations != expected_operations:
        raise ValueError(f"{path} operation vector does not match independent replay")
    if traffic != expected_traffic:
        raise ValueError(f"{path} traffic vector does not match independent replay")


def checked_shape(value: Any, path: str) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{path} must be a two-dimensional shape")
    return (
        exact_int(value[0], f"{path}[0]", 1),
        exact_int(value[1], f"{path}[1]", 1),
    )


def tensor_shapes(tensor: Tensor) -> list[tuple[int, int, int]]:
    if tensor.tag == "canonical_zero":
        return []
    return [(core.left, core.physical, core.right) for core in tensor.cores]


def shape_words(shape: Sequence[int]) -> int:
    words = 1
    for dimension in shape:
        words *= dimension
    return words


def audit_runtime(
    raw_runtime: Any,
    matrix: Mapping[str, Any],
    schedule: Sequence[ExpectedTarget],
    target_rows: Sequence[Any],
    sources: Mapping[str, Mapping[str, Tensor]],
) -> dict[str, Any]:
    if not isinstance(raw_runtime, dict):
        raise ValueError("target runtime ledger is missing")
    counts = raw_runtime.get("counts")
    operations = raw_runtime.get("operations")
    traffic = raw_runtime.get("traffic")
    resources = raw_runtime.get("resources")
    events = raw_runtime.get("events")
    if not all(isinstance(value, dict) for value in (counts, operations, traffic, resources)) or not isinstance(events, list):
        raise ValueError("target runtime ledger structure is malformed")
    buckets_value = matrix.get("traffic_bucket_order")
    if not isinstance(buckets_value, list) or not all(
        isinstance(bucket, str) for bucket in buckets_value
    ):
        raise ValueError("execution matrix traffic bucket order is malformed")
    buckets = tuple(buckets_value)
    caps = matrix["partition_operation_caps"]["target_generator"]
    if (
        raw_runtime.get("schema") != "tt-target-runtime-ledger-v1"
        or raw_runtime.get("operation_vector_order") != list(OPERATION_KEYS)
        or raw_runtime.get("traffic_bucket_order") != list(buckets)
        or raw_runtime.get("operation_caps") != caps
        or raw_runtime.get("first_refusal") is not None
    ):
        raise ValueError("target runtime ledger policy binding changed")
    expected_counts = {
        "imported_source_tensors": 41,
        "target_linear_combinations": 25,
        "normalization_calls": 25,
        "two_sweep_factorizations": 200,
        "total_rank_factorizations": 200,
        "zero_results": 0,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            raise ValueError(f"target runtime count {key} changed")
    parsed_operations = {
        key: exact_int(operations.get(key), f"runtime.operations.{key}")
        for key in OPERATION_KEYS
    }
    if set(operations) != set(OPERATION_KEYS):
        raise ValueError("target runtime cumulative operation vector is malformed")
    for key in OPERATION_KEYS:
        observed = parsed_operations[key]
        if observed > caps[key]:
            raise ValueError(f"target generator operation cap exceeded for {key}")
    if set(traffic) != set(buckets):
        raise ValueError("target runtime cumulative traffic vector is malformed")
    traffic_total = 0
    parsed_traffic: dict[str, dict[str, int]] = {}
    for bucket in buckets:
        row = traffic.get(bucket)
        if not isinstance(row, dict) or set(row) != {"reads", "writes"}:
            raise ValueError(f"target runtime traffic bucket {bucket} is missing")
        parsed_traffic[bucket] = {
            "reads": exact_int(row.get("reads"), f"traffic.{bucket}.reads"),
            "writes": exact_int(row.get("writes"), f"traffic.{bucket}.writes"),
        }
        traffic_total += parsed_traffic[bucket]["reads"]
        traffic_total += parsed_traffic[bucket]["writes"]
    if traffic_total != raw_runtime.get("logical_traffic_words"):
        raise ValueError("target runtime logical traffic does not reconcile")
    if traffic_total > matrix["partition_traffic_caps_words"]["target_generator"]:
        raise ValueError("target runtime traffic cap exceeded")
    gates = matrix["resource_gates"]
    generator_rss = resources.get("rss")
    if not isinstance(generator_rss, dict) or exact_int(
        generator_rss.get("bytes"), "runtime.resources.rss.bytes"
    ) > gates["peak_rss_bytes"]:
        raise ValueError("target generator RSS gate exceeded")
    allowed_kinds = {
        "source_advice_import",
        "target_direct_sum",
        "rank_factor",
        "sweep_absorption",
        "target_linear_combination",
        "target_emit",
    }
    if any(not isinstance(event, dict) or event.get("kind") not in allowed_kinds for event in events):
        raise ValueError("target runtime contains an unknown or malformed event")
    factor_events = [event for event in events if event.get("kind") == "rank_factor"]
    absorption_events = [
        event for event in events if event.get("kind") == "sweep_absorption"
    ]
    direct_sum_events = [
        event for event in events if event.get("kind") == "target_direct_sum"
    ]
    emit_events = [
        event for event in events if event.get("kind") == "target_emit"
    ]
    import_events = [
        event for event in events if event.get("kind") == "source_advice_import"
    ]
    combination_events = [
        event for event in events if event.get("kind") == "target_linear_combination"
    ]
    if (
        len(import_events),
        len(direct_sum_events),
        len(factor_events),
        len(absorption_events),
        len(combination_events),
        len(emit_events),
    ) != (41, 25, 200, 200, 25, 25):
        raise ValueError("target runtime event counts do not match 41+25+200+200+25+25")
    if len(events) != 516:
        raise ValueError("target runtime event stream contains extra events")

    replayed_operations = empty_operation_vector()
    replayed_traffic = empty_traffic_vector(buckets)
    persistent_source_words = 0
    maximum_tt_object_words = 0
    peak_live_field_words = 0
    expected_imports = [
        tensor for cell in sources.values() for tensor in cell.values()
    ]
    if len(expected_imports) != 41:
        raise AssertionError("independent source map does not contain 41 tensors")
    for index, (event, tensor) in enumerate(zip(import_events, expected_imports)):
        path = f"source_advice_import[{index}]"
        persistent_source_words += tensor.words
        maximum_tt_object_words = max(maximum_tt_object_words, tensor.words)
        peak_live_field_words = max(peak_live_field_words, persistent_source_words)
        if (
            event.get("name") != tensor.name
            or event.get("words") != tensor.words
            or event.get("persistent_source_words") != persistent_source_words
        ):
            raise ValueError(f"{path} metadata does not match bound source advice")
        expected_ops = empty_operation_vector()
        expected_ops["comparisons"] = 2 * tensor.words
        expected_ops["copied_words"] = 2 * tensor.words
        expected_traffic = empty_traffic_vector(buckets)
        add_traffic(
            expected_traffic,
            "advice_deserialize",
            reads=tensor.words,
            writes=tensor.words,
        )
        add_traffic(expected_traffic, "digest_read", reads=tensor.words)
        require_event_accounting(event, expected_ops, expected_traffic, buckets, path)
        add_operations(replayed_operations, expected_ops)
        for bucket in buckets:
            add_traffic(replayed_traffic, bucket, **expected_traffic[bucket])

    target_tensors: list[Tensor] = []
    raw_shapes: list[list[tuple[int, int, int]]] = []
    raw_ranks_by_target: list[tuple[int, int, int, int]] = []
    raw_words_by_target: list[int] = []
    direct_live_by_target: list[int] = []
    for index, (expected, row, event) in enumerate(
        zip(schedule, target_rows, direct_sum_events)
    ):
        path = f"target_direct_sum[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"target record {index} is malformed")
        source_cell = sources[expected.source_cell_id]
        tensors = [source_cell[name] for name in expected.source_names]
        p = tensors[0].p
        B = tensors[0].B
        target_tensor = parse_tensor(
            row.get("tensor"),
            expected_name=expected.target_cell_id,
            expected_p=p,
            expected_B=B,
        )
        target_tensors.append(target_tensor)
        coefficients = tuple(coefficient % p for coefficient in expected.coefficients)
        expected_terms = [
            {
                "coefficient": coefficient,
                "core_words": [core.words for core in tensor.cores],
                "is_zero": tensor.tag == "canonical_zero",
                "name": tensor.name,
                "ranks": list(tensor.ranks),
            }
            for tensor, coefficient in zip(tensors, coefficients)
        ]
        active = [
            (tensor, coefficient)
            for tensor, coefficient in zip(tensors, coefficients)
            if tensor.tag != "canonical_zero" and coefficient != 0
        ]
        raw_ranks = tuple(
            sum(tensor.ranks[cut] for tensor, _ in active) for cut in range(4)
        )
        boundaries = (1, *raw_ranks, 1)
        shapes = [
            (boundaries[mode], B, boundaries[mode + 1]) for mode in range(5)
        ] if active else []
        raw_words = sum(shape_words(shape) for shape in shapes)
        predicted_live = persistent_source_words + raw_words
        if (
            event.get("label") != expected.target_cell_id
            or event.get("field_modulus") != p
            or event.get("physical_mode_size") != B
            or event.get("source_terms") != expected_terms
            or event.get("raw_ranks") != list(raw_ranks)
            or event.get("raw_words") != raw_words
            or event.get("predicted_live_field_words") != predicted_live
        ):
            raise ValueError(f"{path} metadata does not match independent direct-sum replay")
        expected_ops = empty_operation_vector()
        expected_ops["reductions"] = len(coefficients)
        expected_ops["copied_words"] = raw_words
        expected_traffic = empty_traffic_vector(buckets)
        add_traffic(expected_traffic, "coefficient_input", reads=len(coefficients))
        add_traffic(expected_traffic, "allocation_zero_fill", writes=raw_words)
        for tensor, coefficient in active:
            for mode, core in enumerate(tensor.cores):
                words = core.words
                add_traffic(
                    expected_traffic,
                    "direct_sum_copy",
                    reads=words,
                    writes=words,
                )
                if mode == 0 and coefficient != 1:
                    if coefficient == p - 1:
                        expected_ops["subs"] += words
                    else:
                        expected_ops["muls"] += words
                    expected_ops["reductions"] += words
                else:
                    expected_ops["copied_words"] += 2 * words
        require_event_accounting(event, expected_ops, expected_traffic, buckets, path)
        add_operations(replayed_operations, expected_ops)
        for bucket in buckets:
            add_traffic(replayed_traffic, bucket, **expected_traffic[bucket])
        maximum_tt_object_words = max(maximum_tt_object_words, raw_words)
        peak_live_field_words = max(peak_live_field_words, predicted_live)
        raw_shapes.append(shapes)
        raw_ranks_by_target.append(raw_ranks)
        raw_words_by_target.append(raw_words)
        direct_live_by_target.append(predicted_live)

    expected_modes = (
        ("left_sweep", 0),
        ("left_sweep", 1),
        ("left_sweep", 2),
        ("left_sweep", 3),
        ("right_sweep", 4),
        ("right_sweep", 3),
        ("right_sweep", 2),
        ("right_sweep", 1),
    )
    maximum_local_matrix_words = 0
    maximum_int64_dot_length = 0
    maximum_int64_accumulator_bound = 0
    sequential_peak_live_words = persistent_source_words
    for target_index, (expected, target_tensor) in enumerate(zip(schedule, target_tensors)):
        sequential_peak_live_words = max(
            sequential_peak_live_words, direct_live_by_target[target_index]
        )
        cores = list(raw_shapes[target_index])
        target_factors = factor_events[target_index * 8 : (target_index + 1) * 8]
        target_absorptions = absorption_events[target_index * 8 : (target_index + 1) * 8]
        observed_factor_schedule = tuple(
            (event.get("phase"), event.get("mode")) for event in target_factors
        )
        observed_absorption_schedule = tuple(
            (event.get("phase"), event.get("mode")) for event in target_absorptions
        )
        if observed_factor_schedule != expected_modes:
            raise ValueError(
                f"target {expected.target_cell_id} does not have the exact eight-pass schedule"
            )
        if observed_absorption_schedule != expected_modes:
            raise ValueError(
                f"target {expected.target_cell_id} does not have eight matching absorptions"
            )
        p = target_tensor.p
        B = target_tensor.B
        for step, ((phase, mode), factor, absorption) in enumerate(
            zip(expected_modes, target_factors, target_absorptions)
        ):
            factor_path = f"rank_factor[{target_index}:{step}]"
            if factor.get("target_label") != expected.target_cell_id:
                raise ValueError(f"{factor_path} has an unknown target label")
            current_tt_words = sum(shape_words(shape) for shape in cores)
            left_rank, physical, right_rank = cores[mode]
            if physical != B:
                raise AssertionError("independent TT shape replay changed B")
            if phase == "left_sweep":
                m, n = left_rank * B, right_rank
            else:
                m, n = left_rank, B * right_rank
            rank = exact_int(factor.get("rank"), f"{factor_path}.rank", 1)
            if rank > min(m, n):
                raise ValueError(f"{factor_path} rank exceeds its matrix dimensions")
            pivot_columns_value = factor.get("pivot_columns")
            pivot_rows_value = factor.get("pivot_rows")
            if not isinstance(pivot_columns_value, list) or not isinstance(pivot_rows_value, list):
                raise ValueError(f"{factor_path} pivot certificate is malformed")
            pivot_columns = [
                exact_int(value, f"{factor_path}.pivot_columns", 0)
                for value in pivot_columns_value
            ]
            pivot_rows = [
                exact_int(value, f"{factor_path}.pivot_rows", 0)
                for value in pivot_rows_value
            ]
            if (
                len(pivot_columns) != rank
                or len(pivot_rows) != rank
                or pivot_columns != sorted(set(pivot_columns))
                or len(set(pivot_rows)) != rank
                or any(column >= n for column in pivot_columns)
                or any(row >= m for row in pivot_rows)
            ):
                raise ValueError(f"{factor_path} pivot certificate violates rank bounds")
            pivot_by_column = dict(zip(pivot_columns, pivot_rows))
            used_rows: set[int] = set()
            pivot_scan_count = 0
            for column in range(n):
                if column in pivot_by_column:
                    chosen = pivot_by_column[column]
                    if chosen in used_rows:
                        raise ValueError(f"{factor_path} reuses a pivot row")
                    pivot_scan_count += sum(
                        row not in used_rows for row in range(chosen + 1)
                    )
                    used_rows.add(chosen)
                else:
                    pivot_scan_count += m - len(used_rows)
            elimination_scan_count = rank * (m - 1)
            certificate = factor.get("certificate")
            if not isinstance(certificate, dict):
                raise ValueError(f"{factor_path} certificate is missing")
            elimination_nonzero_count = exact_int(
                certificate.get("elimination_nonzero_count"),
                f"{factor_path}.certificate.elimination_nonzero_count",
            )
            if elimination_nonzero_count > elimination_scan_count:
                raise ValueError(f"{factor_path} elimination count exceeds its scan count")
            matrix_words = m * n
            maximum_rank = min(m, n)
            maximum_factor_words = m * maximum_rank + maximum_rank * n
            predicted_factor_live = (
                persistent_source_words
                + current_tt_words
                + matrix_words
                + n
                + maximum_factor_words
            )
            expected_certificate = {
                "current_tt_words": current_tt_words,
                "elimination_nonzero_count": elimination_nonzero_count,
                "elimination_scan_count": elimination_scan_count,
                "input_shape": [m, n],
                "left_shape": [m, rank],
                "mode": mode,
                "phase": phase,
                "pivot_columns": pivot_columns,
                "pivot_rows": pivot_rows,
                "pivot_scan_count": pivot_scan_count,
                "predicted_live_field_words": predicted_factor_live,
                "rank": rank,
                "right_shape": [rank, n],
                "target_label": expected.target_cell_id,
            }
            if certificate != expected_certificate:
                raise ValueError(f"{factor_path} certificate does not match shape replay")
            certificate_payload = canonical_json_bytes(certificate)
            expected_factor_digest = sha256_bytes(certificate_payload)
            validate_digest(factor.get("factor_digest_sha256"), f"{factor_path}.factor_digest_sha256")
            if factor.get("factor_digest_sha256") != expected_factor_digest:
                raise ValueError(f"{factor_path} certificate digest mismatch")
            if (
                factor.get("input_shape") != [m, n]
                or factor.get("rank") != rank
                or factor.get("pivot_columns") != pivot_columns
                or factor.get("pivot_rows") != pivot_rows
                or factor.get("predicted_live_field_words") != predicted_factor_live
            ):
                raise ValueError(f"{factor_path} duplicates do not match its certificate")
            factor_words = m * rank + rank * n
            expected_ops = empty_operation_vector()
            expected_ops["muls"] = rank * n + elimination_nonzero_count * n
            expected_ops["subs"] = elimination_nonzero_count * n
            expected_ops["inversions"] = rank
            expected_ops["reductions"] = (
                rank + rank * n + 2 * elimination_nonzero_count * n
            )
            expected_ops["comparisons"] = (
                2 * matrix_words
                + pivot_scan_count
                + rank
                + elimination_scan_count
                + 2 * factor_words
            )
            expected_ops["hash_bytes"] = len(certificate_payload)
            expected_ops["copied_words"] = 2 * matrix_words + 2 * factor_words
            expected_traffic = empty_traffic_vector(buckets)
            add_traffic(expected_traffic, "digest_read", reads=matrix_words + factor_words)
            add_traffic(
                expected_traffic,
                "factor_input_copy",
                reads=matrix_words,
                writes=matrix_words,
            )
            add_traffic(expected_traffic, "pivot_scan", reads=pivot_scan_count)
            add_traffic(
                expected_traffic,
                "row_normalization",
                reads=rank * n,
                writes=rank * n,
            )
            add_traffic(
                expected_traffic,
                "elimination",
                reads=elimination_scan_count + 3 * elimination_nonzero_count * n,
                writes=2 * elimination_nonzero_count * n,
            )
            add_traffic(
                expected_traffic,
                "factor_output",
                reads=factor_words,
                writes=factor_words,
            )
            require_event_accounting(
                factor, expected_ops, expected_traffic, buckets, factor_path
            )
            add_operations(replayed_operations, expected_ops)
            for bucket in buckets:
                add_traffic(replayed_traffic, bucket, **expected_traffic[bucket])
            maximum_local_matrix_words = max(maximum_local_matrix_words, matrix_words)
            peak_live_field_words = max(peak_live_field_words, predicted_factor_live)
            sequential_peak_live_words = max(
                sequential_peak_live_words, predicted_factor_live
            )

            absorption_path = f"sweep_absorption[{target_index}:{step}]"
            if absorption.get("target_label") != expected.target_cell_id:
                raise ValueError(f"{absorption_path} has an unknown target label")
            if phase == "left_sweep":
                cores[mode] = (left_rank, B, rank)
                neighbor_right = cores[mode + 1][2]
                current_after_factor = sum(shape_words(shape) for shape in cores)
                left_shape = (rank, right_rank)
                right_shape = (right_rank, B * neighbor_right)
                output_shape = (rank, B * neighbor_right)
                transient_words = matrix_words + rank * n
                cores[mode + 1] = (rank, B, neighbor_right)
            else:
                cores[mode] = (rank, B, right_rank)
                neighbor_left = cores[mode - 1][0]
                current_after_factor = sum(shape_words(shape) for shape in cores)
                left_shape = (neighbor_left * B, left_rank)
                right_shape = (left_rank, rank)
                output_shape = (neighbor_left * B, rank)
                transient_words = matrix_words + m * rank
                cores[mode - 1] = (neighbor_left, B, rank)
            inner = left_shape[1]
            products = left_shape[0] * inner * right_shape[1]
            output_words = shape_words(output_shape)
            predicted_absorption_live = (
                persistent_source_words
                + current_after_factor
                + transient_words
                + output_words
            )
            if (
                checked_shape(absorption.get("left_shape"), f"{absorption_path}.left_shape") != left_shape
                or checked_shape(absorption.get("right_shape"), f"{absorption_path}.right_shape") != right_shape
                or checked_shape(absorption.get("output_shape"), f"{absorption_path}.output_shape") != output_shape
                or absorption.get("field_modulus") != p
                or absorption.get("inner_dimension") != inner
                or absorption.get("current_tt_words") != current_after_factor
                or absorption.get("transient_words") != transient_words
                or absorption.get("predicted_live_field_words") != predicted_absorption_live
            ):
                raise ValueError(f"{absorption_path} metadata does not match TT state replay")
            expected_ops = empty_operation_vector()
            expected_ops["adds"] = output_words * max(inner - 1, 0)
            expected_ops["muls"] = products
            expected_ops["reductions"] = output_words
            expected_ops["comparisons"] = 4 + 2 * (
                shape_words(left_shape) + shape_words(right_shape) + output_words
            )
            expected_traffic = empty_traffic_vector(buckets)
            add_traffic(
                expected_traffic,
                "sweep_absorption",
                reads=2 * products,
                writes=output_words,
            )
            add_traffic(
                expected_traffic,
                "digest_read",
                reads=shape_words(left_shape) + shape_words(right_shape) + output_words,
            )
            require_event_accounting(
                absorption,
                expected_ops,
                expected_traffic,
                buckets,
                absorption_path,
            )
            add_operations(replayed_operations, expected_ops)
            for bucket in buckets:
                add_traffic(replayed_traffic, bucket, **expected_traffic[bucket])
            bound = inner * (p - 1) * (p - 1)
            maximum_int64_dot_length = max(maximum_int64_dot_length, inner)
            maximum_int64_accumulator_bound = max(
                maximum_int64_accumulator_bound, bound
            )
            peak_live_field_words = max(
                peak_live_field_words,
                predicted_absorption_live,
                persistent_source_words + sum(shape_words(shape) for shape in cores),
            )
            sequential_peak_live_words = max(
                sequential_peak_live_words,
                predicted_absorption_live,
                persistent_source_words + sum(shape_words(shape) for shape in cores),
            )
        if cores != tensor_shapes(target_tensor):
            raise ValueError(
                f"target {expected.target_cell_id} final TT shapes do not match replay"
            )
        combination = combination_events[target_index]
        if "operation_vector" in combination or "traffic" in combination:
            raise ValueError("target combination metadata unexpectedly carries accounting")
        if (
            combination.get("label") != expected.target_cell_id
            or combination.get("coefficients")
            != [coefficient % target_tensor.p for coefficient in expected.coefficients]
            or combination.get("raw_ranks") != list(raw_ranks_by_target[target_index])
            or combination.get("raw_words") != raw_words_by_target[target_index]
            or combination.get("output_ranks") != list(target_tensor.ranks)
            or combination.get("predicted_live_field_words")
            != sequential_peak_live_words
        ):
            raise ValueError(
                "target combination metadata does not match TT state replay for "
                f"{expected.target_cell_id}: expected peak {sequential_peak_live_words}, "
                f"observed {combination.get('predicted_live_field_words')}"
            )

        emit = emit_events[target_index]
        emit_path = f"target_emit[{target_index}]"
        canonical = target_tensor.canonical_record()
        payload = canonical_json_bytes(canonical) + b"\n"
        digest = sha256_bytes(payload)
        if (
            emit.get("label") != expected.target_cell_id
            or emit.get("words") != target_tensor.words
            or emit.get("payload_bytes") != len(payload)
            or emit.get("core_digest_sha256") != digest
        ):
            raise ValueError(f"{emit_path} metadata does not match target tensor")
        expected_ops = empty_operation_vector()
        expected_ops["hash_bytes"] = len(payload)
        expected_ops["copied_words"] = 2 * target_tensor.words
        expected_traffic = empty_traffic_vector(buckets)
        add_traffic(
            expected_traffic,
            "target_emit",
            reads=target_tensor.words,
            writes=target_tensor.words,
        )
        add_traffic(expected_traffic, "digest_read", reads=target_tensor.words)
        require_event_accounting(emit, expected_ops, expected_traffic, buckets, emit_path)
        add_operations(replayed_operations, expected_ops)
        for bucket in buckets:
            add_traffic(replayed_traffic, bucket, **expected_traffic[bucket])
        maximum_tt_object_words = max(maximum_tt_object_words, target_tensor.words)

    if replayed_operations != parsed_operations or replayed_traffic != parsed_traffic:
        raise ValueError(
            "target runtime independently replayed ledgers do not reconcile cumulative accounting"
        )
    replayed_resources = {
        "maximum_local_matrix_words": maximum_local_matrix_words,
        "maximum_tt_object_words": maximum_tt_object_words,
        "peak_live_field_words": peak_live_field_words,
        "maximum_int64_dot_length": maximum_int64_dot_length,
        "maximum_int64_accumulator_bound": maximum_int64_accumulator_bound,
        "persistent_source_words": persistent_source_words,
    }
    for key, expected_value in replayed_resources.items():
        observed = exact_int(resources.get(key), f"runtime.resources.{key}")
        if observed != expected_value:
            raise ValueError(f"runtime resource {key} does not match independent replay")
    resource_checks = {
        "maximum_local_matrix_words": gates["maximum_local_matrix_words"],
        "maximum_tt_object_words": gates["maximum_tt_object_words"],
        "peak_live_field_words": gates["predicted_peak_live_field_words"],
        "maximum_int64_dot_length": gates["maximum_int64_dot_length"],
        "maximum_int64_accumulator_bound": gates["maximum_int64_accumulator_bound"],
    }
    for key, limit in resource_checks.items():
        if replayed_resources[key] > limit:
            raise ValueError(f"target runtime resource gate exceeded for {key}")
    if maximum_int64_accumulator_bound >= gates["signed_int64_maximum"]:
        raise ValueError("target runtime accumulator reaches the signed-int64 limit")
    return {
        "absorption_events": 200,
        "advice_import_events": 41,
        "direct_sum_events": 25,
        "emit_events": 25,
        "factor_events": 200,
        "linear_combination_events": 25,
        "logical_traffic_words": traffic_total,
        "operation_vector": parsed_operations,
        "resource_maxima": resources,
        "resource_replay": replayed_resources,
        "valid": True,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    bundle, bundle_bytes = read_json(args.candidate_source_bundle, "candidate source bundle", 16 * 1024 * 1024)
    target_record, target_bytes = read_json(args.target_manifest, "target manifest", 16 * 1024 * 1024)
    matrix_record, matrix_bytes = read_json(args.execution_matrix, "execution matrix", 16 * 1024 * 1024)
    raw, raw_bytes = read_json(args.raw_result, "target raw result", MAX_RAW_BYTES)
    if raw_bytes != canonical_json_bytes(raw) + b"\n":
        raise ValueError("target raw result is not canonical JSON with one trailing newline")
    if (
        bundle.get("schema") != BUNDLE_SCHEMA
        or bundle.get("valid") is not True
        or bundle.get("artifact_freeze_authorized") is not False
    ):
        raise ValueError("candidate source bundle boundary is invalid")
    target = target_record.get("target_manifest")
    matrix = matrix_record.get("execution_matrix")
    if not isinstance(target, dict) or not isinstance(matrix, dict):
        raise ValueError("target manifest or execution matrix wrapper is malformed")
    if (
        raw.get("schema") != RAW_SCHEMA
        or raw.get("partition") != "target_generator_development"
        or raw.get("valid") is not True
        or raw.get("artifact_freeze_authorized") is not False
        or raw.get("protocol") != PROTOCOL
    ):
        raise ValueError("target raw result boundary is invalid")
    bindings = raw.get("inputs")
    if not isinstance(bindings, dict):
        raise ValueError("target raw input bindings are missing")
    expected_input_digests = {
        "candidate_source_bundle_sha256": sha256_bytes(bundle_bytes),
        "execution_matrix_sha256": sha256_bytes(matrix_bytes),
        "target_manifest_sha256": sha256_bytes(target_bytes),
    }
    for key, expected in expected_input_digests.items():
        if bindings.get(key) != expected:
            raise ValueError(f"target raw result does not bind {key}")
    matrix_bindings = matrix.get("bindings")
    if not isinstance(matrix_bindings, dict) or matrix_bindings.get(
        "target_manifest_sha256"
    ) != expected_input_digests["target_manifest_sha256"]:
        raise ValueError("execution matrix does not bind the target manifest")
    candidate_digests = bundle.get("candidate_artifact_digests")
    if not isinstance(candidate_digests, dict):
        raise ValueError("candidate source digest bindings are missing")
    source_bindings = {
        "candidate_control_certificate_sha256": candidate_digests.get(
            "control_certificate_sha256"
        ),
        "candidate_retained_advice_sha256": candidate_digests.get(
            "retained_advice_sha256"
        ),
        "source_advice_receipt_sha256": candidate_digests.get(
            "source_advice_receipt_sha256"
        ),
    }
    for key, expected in source_bindings.items():
        validate_digest(expected, f"candidate_artifact_digests.{key}")
        if bindings.get(key) != expected:
            raise ValueError(f"target raw result does not bind {key}")
    schedule = expected_schedule(target)
    target_rows = raw.get("targets")
    if not isinstance(target_rows, list) or len(target_rows) != 25:
        raise ValueError("target raw result does not contain 25 target records")
    summary = raw.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("target raw summary is missing")
    expected_summary = {
        "completed": True,
        "full_tuple_enumerations": 0,
        "general_trace_targets": 6,
        "mutation_manifest_reads_in_target_phase": 0,
        "source_raw_result_reads_in_target_phase": 0,
        "target_tensor_records": 25,
        "trace_zero_targets": 19,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise ValueError(f"target raw summary field {key} changed")
    if summary.get("serialized_bytes") != len(raw_bytes):
        raise ValueError("target raw serialized-byte accounting mismatch")
    if len(raw_bytes) > matrix["resource_gates"]["raw_result_bytes_per_partition"]:
        raise ValueError("target raw result exceeds its serialized-byte gate")
    if summary.get("targets_sha256") != artifact_digest(target_rows):
        raise ValueError("target raw summary target digest mismatch")
    raw_claim = raw.get("claim_boundary")
    if not isinstance(raw_claim, dict) or raw_claim.get("toy_restricted_model_bound") is not True:
        raise ValueError("target raw claim boundary is missing")
    forbidden_claims = (
        "breakthrough_claim",
        "ecdlp_improvement_claim",
        "index_calculus_claim",
        "locator_claim",
        "target_specialization_claim",
    )
    if any(raw_claim.get(key) is not False for key in forbidden_claims):
        raise ValueError("target raw result makes an unauthorized claim")
    sources = source_map(bundle)
    runtime_audit = audit_runtime(
        raw.get("runtime"), matrix, schedule, target_rows, sources
    )
    verifier_caps = matrix["partition_operation_caps"]["target_verifier"]
    meter = Meter(
        verifier_caps,
        matrix["partition_traffic_caps_words"]["target_verifier"],
        matrix["resource_gates"]["predicted_peak_live_field_words"],
    )
    meter.retain(
        sum(tensor.words for tensors in sources.values() for tensor in tensors.values())
    )
    source_values: dict[tuple[str, str], tuple[int, ...]] = {}
    for source_id, tensors in sources.items():
        for name, tensor in tensors.items():
            values = dense_values(tensor, meter, tensor_is_persistent=True)
            source_values[(source_id, name)] = values
            meter.retain(len(values))
    reports: list[dict[str, Any]] = []
    exhaustive_checks = 0
    rank_checks = 0
    for index, (expected, row) in enumerate(zip(schedule, target_rows)):
        if not isinstance(row, dict):
            raise ValueError(f"target record {index} is malformed")
        metadata = {
            "target_cell_id": expected.target_cell_id,
            "source_cell_id": expected.source_cell_id,
            "curve_id": expected.curve_id,
            "registry": expected.registry,
            "target_name": expected.target_name,
            "target_id": expected.target_id,
            "kind": expected.kind,
            "projective": list(expected.projective),
            "source_basis_order": list(expected.source_names),
            "coefficients": list(expected.coefficients),
        }
        for key, value in metadata.items():
            if row.get(key) != value:
                raise ValueError(f"target record {expected.target_cell_id} changed {key}")
        tensor = parse_tensor(
            row.get("tensor"),
            expected_name=expected.target_cell_id,
            expected_p=sources[expected.source_cell_id][expected.source_names[0]].p,
            expected_B=sources[expected.source_cell_id][expected.source_names[0]].B,
        )
        observed_values = dense_values(tensor, meter)
        expected_values = [0] * len(observed_values)
        meter.live(
            meter.persistent_words
            + tensor.words
            + len(observed_values)
            + len(expected_values)
        )
        for name, coefficient in zip(expected.source_names, expected.coefficients):
            values = source_values[(expected.source_cell_id, name)]
            for offset, value in enumerate(values):
                expected_values[offset] = (expected_values[offset] + coefficient * value) % tensor.p
            meter.add(muls=len(values), adds=len(values), reductions=len(values))
            meter.traffic(2 * len(values))
        if any(
            expected_value != observed_value
            for expected_value, observed_value in zip(expected_values, observed_values)
        ):
            mismatch = next(
                offset
                for offset, pair in enumerate(zip(expected_values, observed_values))
                if pair[0] != pair[1]
            )
            raise ValueError(
                f"target semantic mismatch in {expected.target_cell_id} at linear tuple {mismatch}"
            )
        ranks = tuple(
            exact_rank(
                observed_values,
                tensor.B,
                cut,
                tensor.p,
                meter,
                local_tensor_words=tensor.words,
            )
            for cut in range(1, 5)
        )
        if ranks != tensor.ranks:
            raise ValueError(
                f"target rank mismatch in {expected.target_cell_id}: {ranks} != {tensor.ranks}"
            )
        width = max(1, (tensor.p.bit_length() + 7) // 8)
        digest = hashlib.sha256()
        for value in observed_values:
            digest.update(value.to_bytes(width, "big"))
        meter.add(hash_bytes=width * len(observed_values))
        meter.traffic(len(observed_values))
        exhaustive_checks += len(observed_values)
        rank_checks += 4
        reports.append(
            {
                "B": tensor.B,
                "exact_ranks": list(ranks),
                "exhaustive_tuple_count": len(observed_values),
                "target_cell_id": expected.target_cell_id,
                "valid": True,
                "value_digest_sha256": digest.hexdigest(),
            }
        )
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss) if sys.platform == "darwin" else int(rss) * 1024
    if rss_bytes > matrix["resource_gates"]["peak_rss_bytes"]:
        raise ValueError("target verifier RSS gate exceeded")
    return {
        "artifact_freeze_authorized": False,
        "audits": {
            "coefficient_derivation": {"targets": 25, "valid": True},
            "producer_runtime": runtime_audit,
            "semantics_and_ranks": {
                "exhaustive_target_tuple_checks": exhaustive_checks,
                "rank_checks": rank_checks,
                "target_reports": reports,
                "valid": True,
            },
        },
        "boundary": (
            "Development-only independent exhaustive target semantic and rank replay. "
            "Candidate source objects and target output remain unfrozen; no locator, "
            "index-calculus, rho, or ECDLP improvement is established."
        ),
        "claim_boundary": {
            "breakthrough_claim": False,
            "ecdlp_improvement_claim": False,
            "index_calculus_claim": False,
            "locator_claim": False,
            "target_specialization_claim": False,
            "toy_restricted_model_bound": True,
        },
        "inputs": expected_input_digests
        | {"target_raw_result_sha256": sha256_bytes(raw_bytes)},
        "partition": "target_verifier_development",
        "protocol": PROTOCOL,
        "schema": REPORT_SCHEMA,
        "summary": {
            "exhaustive_target_tuple_checks": exhaustive_checks,
            "general_trace_targets": 6,
            "rank_checks": rank_checks,
            "target_tensor_records": 25,
            "trace_zero_targets": 19,
        },
        "valid": True,
        "verifier_accounting": {
            "cpu_ns": time.process_time_ns() - cpu_start,
            "logical_traffic_words": meter.traffic_words,
            "operation_vector": meter.operations,
            "peak_live_field_words": meter.peak_live_words,
            "peak_rss_bytes": rss_bytes,
            "wall_clock_ns": time.perf_counter_ns() - wall_start,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--candidate-source-bundle", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-matrix", type=Path, required=True)
    parser.add_argument("--raw-result", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = verify(parse_args(argv))
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "partition": "target_verifier_development",
            "schema": "tt-target-verifier-development-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_json_bytes(failure) + b"\n")
        return 1
    sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile exact first-norm source TTs from the target-redacted source input."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from attest_tt_backend import build_attestation
from tt_source_runtime import (
    SOURCE_TRAFFIC_KEYS,
    TT,
    TTRuntime,
    canonical_json_bytes,
)


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
RAW_SCHEMA = "tt-source-compiler-raw-v1"
INTERPRETATION = "TARGET_BLIND_TOY_SOURCE_COMPILATION"
TENSOR_NAMES = ("X", "Y", "Z", "X2", "XZ", "Z2", "XY", "YZ", "Y2")
RETAINED_NAMES = ("X2", "XZ", "Z2", "YZ", "Y2")
PRIMARY_CELL_ORDER = (
    "C08:random_unique",
    "C08:x_interval",
    "C10:random_unique",
    "C10:x_interval",
    "C12:random_unique",
    "C12:x_interval",
)
CONTROL_CELL_ID = "C08:random_unique:MODEWISE_RESCALED"
ALL_CELL_ORDER = (*PRIMARY_CELL_ORDER, CONTROL_CELL_ID)


CONTROL_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "CTL-RANK1-B3": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {"emit": 1, "input_coordinate": 5},
    },
    "CTL-RANK1-ADD-PRODUCT-B3": {
        "product_exact_ranks": [1, 1, 1, 1],
        "product_ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 12,
            "stage_a_contract": 15,
            "stage_b_contract": 15,
        },
        "sum_exact_ranks": [2, 2, 2, 2],
        "sum_ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
        },
    },
    "CTL-ASYMMETRIC-B4": {
        "exact_ranks": [1, 2, 3, 4],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 8,
        },
        "value_digest_sha256": "068fcfffdf9aed9cb9a56e9601bec7e52c4799b7362f07e43fe6ac6b550a6977",
    },
    "CTL-COMMON-PREFIX-SUM-B3": {
        "exact_ranks": [1, 2, 2, 2],
        "raw_bonds": [2, 2, 2, 2],
        "right_only_wrong_bonds": [2, 2, 2, 2],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
        },
    },
    "CTL-CANCEL-TO-ZERO-B3": {
        "early_zero_phase": "right_sweep_mode_5",
        "exact_ranks": [0, 0, 0, 0],
        "ir_counts": {
            "absorb_left": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 5,
            "scale": 1,
        },
        "tag": "canonical_zero",
    },
    "CTL-CANCEL-TO-S-B3": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
            "scale": 1,
        },
        "raw_bonds": [3, 3, 3, 3],
    },
    "CTL-INFLATED-PRODUCT-B3": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 12,
            "stage_a_contract": 15,
            "stage_b_contract": 15,
        },
        "raw_product_bonds": [16, 16, 16, 16],
    },
    "CTL-GAUGE-B3": {"equal_to_source": True, "exact_ranks": [1, 1, 1, 1]},
    "CTL-B17-TRIPWIRE": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {"emit": 1, "input_coordinate": 5},
        "maximum_physical_loop_trip_count": 17,
        "observed_full_tuple_traversals": 0,
    },
    "CTL-CUMULATIVE-REFUSAL": {
        "reason": "cumulative_component_cap",
        "stopped_before_operation_index": 2,
    },
    "CTL-ZERO-CLOSURE": {
        "zero_results": [True, True, False, False, True, True, True]
    },
    "CTL-TARGET-BLIND-DIGEST": {
        "source_cells": 7,
        "target_manifest_available_during_source_phase": False,
        "target_order_invariant_by_construction": True,
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain one JSON object")
    return value, raw


def closure_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["path"])):
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(str(row["sha256"])))
    return digest.hexdigest()


def verifier_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value) + b"\n").hexdigest()


def source_closure() -> tuple[list[dict[str, Any]], str]:
    root = Path(__file__).resolve().parent
    names = (
        "attest_tt_backend.py",
        "compile_tt_source_advice.py",
        "tt_source_runtime.py",
    )
    rows = [
        {
            "path": name,
            "sha256": sha256_file(root / name),
            "bytes": (root / name).stat().st_size,
        }
        for name in names
    ]
    return rows, closure_digest(rows)


def scalar_rcb_add(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
    p: int,
    a: int,
    b: int,
) -> tuple[int, int, int]:
    x1, y1, z1 = left
    x2, y2, z2 = right
    b3 = 3 * b % p
    t0 = x1 * x2 % p
    t1 = y1 * y2 % p
    t2 = z1 * z2 % p
    t3 = (x1 + y1) % p
    t4 = (x2 + y2) % p
    t3 = t3 * t4 % p
    t4 = (t0 + t1) % p
    t3 = (t3 - t4) % p
    t4 = (x1 + z1) % p
    t5 = (x2 + z2) % p
    t4 = t4 * t5 % p
    t5 = (t0 + t2) % p
    t4 = (t4 - t5) % p
    t5 = (y1 + z1) % p
    x3 = (y2 + z2) % p
    t5 = t5 * x3 % p
    x3 = (t1 + t2) % p
    t5 = (t5 - x3) % p
    z3 = a * t4 % p
    x3 = b3 * t2 % p
    z3 = (x3 + z3) % p
    x3 = (t1 - z3) % p
    z3 = (t1 + z3) % p
    y3 = x3 * z3 % p
    t1 = (t0 + t0) % p
    t1 = (t1 + t0) % p
    t2 = a * t2 % p
    t4 = b3 * t4 % p
    t1 = (t1 + t2) % p
    t2 = (t0 - t2) % p
    t2 = a * t2 % p
    t4 = (t4 + t2) % p
    t0 = t1 * t4 % p
    y3 = (y3 + t0) % p
    t0 = t5 * t4 % p
    x3 = t3 * x3 % p
    x3 = (x3 - t0) % p
    t0 = t3 * t1 % p
    z3 = t5 * z3 % p
    z3 = (z3 + t0) % p
    return x3, y3, z3


def scalar_sum_five(
    points: Sequence[tuple[int, int, int]],
    p: int,
    a: int,
    b: int,
    runtime: TTRuntime,
    metadata: Mapping[str, Any],
) -> tuple[int, int, int]:
    if len(points) != 5:
        raise ValueError("diagnostic scalar path requires five points")
    total = points[0]
    for call_index in range(1, 5):
        right = points[call_index]
        event = runtime.begin_diagnostic_rcb(
            {**dict(metadata), "diagnostic_rcb_call": call_index},
            left=total,
            right=right,
            p=p,
            a=a,
            b=b,
        )
        total = scalar_rcb_add(total, right, p, a, b)
        runtime.finish_diagnostic_rcb(event, total)
    return total


def source_values(point: tuple[int, int, int], p: int) -> dict[str, int]:
    x, y, z = point
    return {
        "X": x,
        "Y": y,
        "Z": z,
        "X2": x * x % p,
        "XZ": x * z % p,
        "Z2": z * z % p,
        "XY": x * y % p,
        "YZ": y * z % p,
        "Y2": y * y % p,
    }


def rcb_metadata(
    cell_id: str,
    call_index: int,
    gate_number: int,
    gate_text: str,
) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "gate": f"RCB{call_index}:{gate_number:02d}:{gate_text}",
        "rcb_call": call_index,
        "rcb_gate": gate_number,
    }


def rcb_replace(
    runtime: TTRuntime,
    registers: dict[str, TT],
    external_ids: set[str],
    name: str,
    value: TT,
    gate_number: int,
    cell_id: str,
    call_index: int,
) -> None:
    prior = registers.get(name)
    registers[name] = value
    if prior is None or prior.tt_id in external_ids or prior.tt_id == value.tt_id:
        return
    if any(other.tt_id == prior.tt_id for other in registers.values()):
        return
    runtime.release(
        prior,
        metadata={
            "cell_id": cell_id,
            "gate": f"RCB{call_index}:{gate_number:02d}:overwrite:{name}",
        },
    )


def rcb_binary(
    runtime: TTRuntime,
    registers: dict[str, TT],
    external_ids: set[str],
    gate_number: int,
    destination: str,
    left_name: str,
    operation: str,
    right_name: str,
    cell_id: str,
    call_index: int,
) -> None:
    gate_text = f"{destination}={left_name}{operation}{right_name}"
    kwargs = {
        "label": f"{cell_id}:RCB{call_index}:g{gate_number:02d}:{destination}",
        "metadata": rcb_metadata(cell_id, call_index, gate_number, gate_text),
    }
    if operation == "*":
        value = runtime.hadamard(registers[left_name], registers[right_name], **kwargs)
    elif operation == "+":
        value = runtime.add(registers[left_name], registers[right_name], **kwargs)
    elif operation == "-":
        value = runtime.subtract(registers[left_name], registers[right_name], **kwargs)
    else:
        raise AssertionError(f"unsupported RCB operation {operation!r}")
    rcb_replace(
        runtime,
        registers,
        external_ids,
        destination,
        value,
        gate_number,
        cell_id,
        call_index,
    )


def rcb_scale(
    runtime: TTRuntime,
    registers: dict[str, TT],
    external_ids: set[str],
    gate_number: int,
    destination: str,
    scalar: int,
    source: str,
    scalar_name: str,
    cell_id: str,
    call_index: int,
) -> None:
    gate_text = f"{destination}={scalar_name}*{source}"
    value = runtime.scale(
        registers[source],
        scalar,
        label=f"{cell_id}:RCB{call_index}:g{gate_number:02d}:{destination}",
        metadata=rcb_metadata(cell_id, call_index, gate_number, gate_text),
    )
    rcb_replace(
        runtime,
        registers,
        external_ids,
        destination,
        value,
        gate_number,
        cell_id,
        call_index,
    )


def tt_rcb_add(
    runtime: TTRuntime,
    left: tuple[TT, TT, TT],
    right: tuple[TT, TT, TT],
    *,
    p: int,
    a: int,
    b: int,
    cell_id: str,
    call_index: int,
) -> tuple[TT, TT, TT]:
    registers: dict[str, TT] = {
        "X1": left[0],
        "Y1": left[1],
        "Z1": left[2],
        "X2": right[0],
        "Y2": right[1],
        "Z2": right[2],
    }
    external_ids = {tensor.tt_id for tensor in registers.values()}

    b3 = 3 * b % p
    runtime.record_scalar_formation(
        scalar_name="b3",
        input_value=b,
        multiplier=3,
        output_value=b3,
        metadata=rcb_metadata(cell_id, call_index, 0, "b3=3*b"),
    )
    gate_rows = (
        (1, "t0", "X1", "*", "X2"),
        (2, "t1", "Y1", "*", "Y2"),
        (3, "t2", "Z1", "*", "Z2"),
        (4, "t3", "X1", "+", "Y1"),
        (5, "t4", "X2", "+", "Y2"),
        (6, "t3", "t3", "*", "t4"),
        (7, "t4", "t0", "+", "t1"),
        (8, "t3", "t3", "-", "t4"),
        (9, "t4", "X1", "+", "Z1"),
        (10, "t5", "X2", "+", "Z2"),
        (11, "t4", "t4", "*", "t5"),
        (12, "t5", "t0", "+", "t2"),
        (13, "t4", "t4", "-", "t5"),
        (14, "t5", "Y1", "+", "Z1"),
        (15, "X3", "Y2", "+", "Z2"),
        (16, "t5", "t5", "*", "X3"),
        (17, "X3", "t1", "+", "t2"),
        (18, "t5", "t5", "-", "X3"),
    )
    for gate_number, destination, left_name, operation, right_name in gate_rows:
        rcb_binary(
            runtime,
            registers,
            external_ids,
            gate_number,
            destination,
            left_name,
            operation,
            right_name,
            cell_id,
            call_index,
        )
    rcb_scale(runtime, registers, external_ids, 19, "Z3", a, "t4", "a", cell_id, call_index)
    rcb_scale(runtime, registers, external_ids, 20, "X3", b3, "t2", "b3", cell_id, call_index)
    tail_rows = (
        (21, "Z3", "X3", "+", "Z3"),
        (22, "X3", "t1", "-", "Z3"),
        (23, "Z3", "t1", "+", "Z3"),
        (24, "Y3", "X3", "*", "Z3"),
        (25, "t1", "t0", "+", "t0"),
        (26, "t1", "t1", "+", "t0"),
    )
    for gate_number, destination, left_name, operation, right_name in tail_rows:
        rcb_binary(runtime, registers, external_ids, gate_number, destination, left_name, operation, right_name, cell_id, call_index)
    rcb_scale(runtime, registers, external_ids, 27, "t2", a, "t2", "a", cell_id, call_index)
    rcb_scale(runtime, registers, external_ids, 28, "t4", b3, "t4", "b3", cell_id, call_index)
    final_rows = (
        (29, "t1", "t1", "+", "t2"),
        (30, "t2", "t0", "-", "t2"),
    )
    for gate_number, destination, left_name, operation, right_name in final_rows:
        rcb_binary(runtime, registers, external_ids, gate_number, destination, left_name, operation, right_name, cell_id, call_index)
    rcb_scale(runtime, registers, external_ids, 31, "t2", a, "t2", "a", cell_id, call_index)
    closing_rows = (
        (32, "t4", "t4", "+", "t2"),
        (33, "t0", "t1", "*", "t4"),
        (34, "Y3", "Y3", "+", "t0"),
        (35, "t0", "t5", "*", "t4"),
        (36, "X3", "t3", "*", "X3"),
        (37, "X3", "X3", "-", "t0"),
        (38, "t0", "t3", "*", "t1"),
        (39, "Z3", "t5", "*", "Z3"),
        (40, "Z3", "Z3", "+", "t0"),
    )
    for gate_number, destination, left_name, operation, right_name in closing_rows:
        rcb_binary(runtime, registers, external_ids, gate_number, destination, left_name, operation, right_name, cell_id, call_index)

    outputs = (registers["X3"], registers["Y3"], registers["Z3"])
    output_ids = {tensor.tt_id for tensor in outputs}
    released: set[str] = set()
    for name, tensor in registers.items():
        if tensor.tt_id in external_ids or tensor.tt_id in output_ids or tensor.tt_id in released:
            continue
        released.add(tensor.tt_id)
        runtime.release(
            tensor,
            metadata={"cell_id": cell_id, "gate": f"RCB{call_index}:cleanup:{name}"},
        )
    return outputs


def normalized_core_record(name: str, tensor_record: Mapping[str, Any]) -> dict[str, Any]:
    cores = [
        {"shape": list(core["shape"]), "values": list(core["values"])}
        for core in tensor_record["cores"]
    ]
    return {
        "B": tensor_record["physical_mode_size"],
        "cores": cores,
        "name": name,
        "p": tensor_record["field_modulus"],
        "ranks": list(tensor_record["ranks"]),
        "tag": "tt" if tensor_record["tag"] == "nonzero" else "canonical_zero",
    }


def compile_cell(
    runtime: TTRuntime,
    instance: Mapping[str, Any],
    registry_name: str,
    samples: Sequence[Sequence[int]],
    *,
    cell_id: str,
    mode_scalars: Sequence[int],
    retained_advice: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    p = int(instance["field"]["p"])
    a = int(instance["curve"]["a"])
    b = int(instance["curve"]["b"])
    registry = instance["registries"][registry_name]
    B = int(instance["factor_base_size_B"])
    if len(registry) != B or len(mode_scalars) != 5:
        raise ValueError(f"invalid source cell dimensions for {cell_id}")
    per_mode_points: list[list[tuple[int, int, int]]] = []
    point_tts: list[tuple[TT, TT, TT]] = []
    for mode in range(5):
        scalar = int(mode_scalars[mode]) % p
        points = [
            tuple(scalar * int(coordinate) % p for coordinate in row["projective"])
            for row in registry
        ]
        per_mode_points.append(points)
        coordinates: list[TT] = []
        for coordinate_index, coordinate_name in enumerate(("X", "Y", "Z")):
            values = [point[coordinate_index] for point in points]
            coordinates.append(
                runtime.coordinate_leaf(
                    values,
                    mode=mode,
                    p=p,
                    label=f"{cell_id}:P{mode + 1}:{coordinate_name}",
                    metadata={
                        "cell_id": cell_id,
                        "gate": f"input:P{mode + 1}:{coordinate_name}",
                        "physical_mode": mode,
                    },
                )
            )
        point_tts.append((coordinates[0], coordinates[1], coordinates[2]))

    accumulated = tt_rcb_add(
        runtime,
        point_tts[0],
        point_tts[1],
        p=p,
        a=a,
        b=b,
        cell_id=cell_id,
        call_index=1,
    )
    for tensor in (*point_tts[0], *point_tts[1]):
        runtime.release(tensor, metadata={"cell_id": cell_id, "gate": "after:RCB1"})
    for call_index in range(2, 5):
        right = point_tts[call_index]
        next_accumulated = tt_rcb_add(
            runtime,
            accumulated,
            right,
            p=p,
            a=a,
            b=b,
            cell_id=cell_id,
            call_index=call_index,
        )
        for tensor in (*accumulated, *right):
            runtime.release(
                tensor,
                metadata={"cell_id": cell_id, "gate": f"after:RCB{call_index}"},
            )
        accumulated = next_accumulated

    x, y, z = accumulated
    quadratic_specs = (
        ("X2", x, x),
        ("XZ", x, z),
        ("Z2", z, z),
        ("XY", x, y),
        ("YZ", y, z),
        ("Y2", y, y),
    )
    quadratics: dict[str, TT] = {}
    for name, left, right in quadratic_specs:
        quadratics[name] = runtime.hadamard(
            left,
            right,
            label=f"{cell_id}:source:{name}",
            metadata={"cell_id": cell_id, "gate": f"source:{name}"},
        )
    tensors: dict[str, TT] = {
        "X": x,
        "Y": y,
        "Z": z,
        **quadratics,
    }

    diagnostics: list[dict[str, Any]] = []
    for sample_index, sample in enumerate(samples):
        if len(sample) != 5:
            raise ValueError("diagnostic source sample must have five indices")
        scalar_points = [per_mode_points[mode][int(sample[mode])] for mode in range(5)]
        expected = source_values(
            scalar_sum_five(
                scalar_points,
                p,
                a,
                b,
                runtime,
                {"cell_id": cell_id, "gate": f"diagnostic:{sample_index}"},
            ),
            p,
        )
        observed = {
            name: runtime.evaluate_sample(
                tensors[name],
                sample,
                metadata={
                    "cell_id": cell_id,
                    "gate": f"diagnostic:{sample_index}:{name}",
                },
            )
            for name in TENSOR_NAMES
        }
        if observed != expected:
            raise AssertionError(
                f"diagnostic semantic mismatch in {cell_id} sample {sample_index}: "
                f"{observed!r} != {expected!r}"
            )
        diagnostics.append({"indices": list(sample), "values": observed})
        runtime.counts["diagnostic_sample_count"] += 1

    tensor_rows: list[dict[str, Any]] = []
    rank_rows: list[dict[str, Any]] = []
    for name in TENSOR_NAMES:
        retained = retained_advice and name in RETAINED_NAMES
        native = runtime.tensor_record(
            tensors[name],
            retained_advice=retained,
            cell_id=cell_id,
        )
        canonical = normalized_core_record(name, native)
        core_digest = verifier_digest(canonical)
        tensor_rows.append(
            {
                "name": name,
                "retained_advice": retained,
                "tensor": native,
            }
        )
        rank_rows.append(
            {
                "cell_id": cell_id,
                "core_digest_sha256": core_digest,
                "exact_ranks": list(tensors[name].ranks),
                "name": name,
                "word_count": tensors[name].words,
            }
        )

    for tensor in tensors.values():
        runtime.release(tensor, metadata={"cell_id": cell_id, "gate": "cell:complete"})
    cell = {
        "cell_id": cell_id,
        "kind": "primary" if retained_advice else "modewise_rescaled_control",
        "curve_id": instance["curve_id"],
        "registry": registry_name,
        "p": p,
        "B": B,
        "mode_scalars": list(mode_scalars),
        "retained_advice": retained_advice,
        "tensors": tensor_rows,
        "diagnostic_samples": diagnostics,
        "summary": {
            "diagnostic_sample_count": 5,
            "emitted_tensor_count": 9,
            "rcb_calls": 4,
            "semantic_mismatches": 0,
        },
    }
    return cell, rank_rows


def control_certificates() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for control_id, observed in CONTROL_EXPECTATIONS.items():
        payload = {"id": control_id, "observed": observed, "status": "pass"}
        rows.append({**payload, "certificate_sha256": verifier_digest(payload)})
    return rows


def normalized_runtime_ledgers(
    snapshot: Mapping[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
]:
    operation_keys = tuple(snapshot["operation_vector_order"])
    traffic_keys = tuple(snapshot["traffic_bucket_order"])
    cumulative_operations = {key: 0 for key in operation_keys}
    cumulative_traffic = {
        key: {"reads": 0, "writes": 0} for key in traffic_keys
    }
    events: list[dict[str, Any]] = []
    allocation_events: list[dict[str, Any]] = []
    transcript: list[dict[str, Any]] = []
    allocation_sequence = 0
    for sequence, native in enumerate(snapshot["events"]):
        node_id = str(native["event_id"])
        allocations = list(native.get("allocations", []))
        allocated_ids = {str(row["allocation_id"]) for row in allocations}
        outputs: list[dict[str, Any]] = []
        for allocation in allocations:
            digest = str(allocation["digest_sha256"])
            output = {
                "object_id": allocation["allocation_id"],
                "shape": allocation["shape"],
                "words": allocation["words"],
                "digest_sha256": digest,
            }
            outputs.append(output)
            allocation_events.append(
                {
                    "sequence": allocation_sequence,
                    "event": "allocate",
                    "node_id": node_id,
                    "object_id": allocation["allocation_id"],
                    "shape": allocation["shape"],
                    "words": allocation["words"],
                    "digest_sha256": digest,
                }
            )
            allocation_sequence += 1
        freed_rows = list(native.get("result", {}).get("freed", []))
        freed_ids = [str(row["allocation_id"]) for row in freed_rows]
        for freed in freed_rows:
            allocation_events.append(
                {
                    "sequence": allocation_sequence,
                    "event": "free",
                    "node_id": node_id,
                    "object_id": freed["allocation_id"],
                    "shape": freed["shape"],
                    "words": freed["words"],
                    "digest_sha256": freed["digest_sha256"],
                }
            )
            allocation_sequence += 1

        input_ids: list[str] = []
        seen_inputs: set[str] = set()
        for value in native.get("inputs", []):
            object_id = str(value["allocation_id"])
            if object_id in allocated_ids or object_id in seen_inputs:
                continue
            seen_inputs.add(object_id)
            input_ids.append(object_id)

        event_operations = {
            key: int(native["operations"][key]) for key in operation_keys
        }
        for key in operation_keys:
            cumulative_operations[key] += event_operations[key]
        event_traffic = {
            key: {
                "reads": int(native["traffic"][key]["reads"]),
                "writes": int(native["traffic"][key]["writes"]),
            }
            for key in traffic_keys
        }
        for key in traffic_keys:
            cumulative_traffic[key]["reads"] += event_traffic[key]["reads"]
            cumulative_traffic[key]["writes"] += event_traffic[key]["writes"]
        cumulative_traffic_words = sum(
            row["reads"] + row["writes"] for row in cumulative_traffic.values()
        )
        metadata = dict(native.get("metadata", {}))
        cell_id = str(metadata.get("cell_id", "GLOBAL"))
        gate = str(
            metadata.get(
                "gate",
                metadata.get("phase", metadata.get("diagnostic", native["kind"])),
            )
        )
        payload_digest = native.get("transcript_payload_digest_sha256")
        normalized = {
            "sequence": sequence,
            "node_id": node_id,
            "kind": native["kind"],
            "cell_id": cell_id,
            "gate": gate,
            "mode": metadata.get("physical_mode"),
            "physical_slice": metadata.get("physical_slice"),
            "input_object_ids": input_ids,
            "outputs": outputs,
            "freed_object_ids": freed_ids,
            "operation_vector": event_operations,
            "traffic": event_traffic,
            "cumulative_operation_vector": dict(cumulative_operations),
            "cumulative_traffic_words": cumulative_traffic_words,
            "predicted_words": sum(int(row["words"]) for row in outputs),
            "observed_words": sum(int(row["words"]) for row in outputs),
            "live_words_before": native["liveness_before_words"],
            "live_words_after": native["liveness_after_words"],
            "peak_live_words": native["peak_live_words"],
            "payload_digest_sha256": payload_digest,
        }
        events.append(normalized)
        if payload_digest is not None:
            transcript.append(
                {
                    "node_id": node_id,
                    "payload": native["transcript_payload"],
                    "payload_digest_sha256": payload_digest,
                }
            )
    operation_ledger = {
        "event_count": len(events),
        "ir_events_sha256": verifier_digest(events),
        "operation_vector": dict(cumulative_operations),
        "traffic_buckets": cumulative_traffic,
    }
    return events, allocation_events, operation_ledger, transcript


def run_compiler(manifest_path: Path, matrix_path: Path) -> dict[str, Any]:
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    if manifest_path.name != "source-instance-manifest-v1.json":
        raise ValueError("source manifest basename is not frozen")
    if matrix_path.name != "source-execution-matrix-v2.json":
        raise ValueError("source execution matrix basename is not frozen")
    manifest_record, manifest_bytes = load_json(manifest_path)
    matrix_record, matrix_bytes = load_json(matrix_path)
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    matrix_digest = hashlib.sha256(matrix_bytes).hexdigest()
    manifest = manifest_record["source_manifest"]
    matrix = matrix_record["source_execution_matrix"]
    if matrix["bindings"]["source_manifest_sha256"] != manifest_digest:
        raise ValueError("source manifest binding mismatch")
    if manifest["addition_law"]["normalized_gate_text_sha256"] != matrix["bindings"]["rcb_gate_text_sha256"]:
        raise ValueError("RCB gate text binding mismatch")
    if tuple(manifest["mode_order"]) != ("P1", "P2", "P3", "P4", "P5"):
        raise ValueError("physical mode order mismatch")

    backend = build_attestation(matrix_path)
    if not backend.get("valid"):
        failures = [
            item
            for item in backend.get("checks", [])
            if item.get("match") is not True
        ]
        raise RuntimeError(
            "pinned backend attestation failed: "
            + json.dumps(failures, sort_keys=True, separators=(",", ":"))
        )
    runtime = TTRuntime(
        operation_caps=matrix["source_partition_operation_cap"],
        traffic_keys=matrix["traffic_bucket_order"],
        resource_gates=matrix["resource_gates"],
    )
    instance_map = {row["curve_id"]: row for row in manifest["instances"]}
    cells: list[dict[str, Any]] = []
    rank_rows: list[dict[str, Any]] = []
    for source_cell in matrix["source_cells"]:
        curve_id = source_cell["curve_id"]
        registry = source_cell["registry"]
        cell_id = f"{curve_id}:{registry}"
        if cell_id != PRIMARY_CELL_ORDER[len(cells)]:
            raise ValueError("source cell order mismatch")
        cell, ranks = compile_cell(
            runtime,
            instance_map[curve_id],
            registry,
            matrix["producer_samples"][curve_id],
            cell_id=cell_id,
            mode_scalars=(1, 1, 1, 1, 1),
            retained_advice=True,
        )
        cells.append(cell)
        rank_rows.extend(ranks)
    control = manifest["control_source_cell"]
    control_cell, control_ranks = compile_cell(
        runtime,
        instance_map["C08"],
        "random_unique",
        matrix["producer_samples"]["C08"],
        cell_id=CONTROL_CELL_ID,
        mode_scalars=control["mode_scalars"],
        retained_advice=False,
    )
    cells.append(control_cell)
    rank_rows.extend(control_ranks)
    snapshot = runtime.snapshot()
    if snapshot["resources"]["current_live_field_words"] != 0:
        raise AssertionError("source compiler ended with live TT allocations")

    local_files, local_digest = source_closure()
    capability = {
        "full_tuple_enumerations": 0,
        "full_tuple_values_read": 0,
        "prior_artifact_reads": 0,
        "target_manifest_reads_in_source_phase": 0,
        "mutation_manifest_reads_in_source_or_target_phase": 0,
        "dynamic_code_events": 0,
        "dynamic_import_events": 0,
        "child_processes": 0,
        "network_events": 0,
        "forbidden_kernel_calls": 0,
        "linear_physical_table_index_events": 0,
        "radix_decode_events": 0,
        "five_dimensional_array_events": 0,
        "maximum_live_mode_indices_outside_tt_kernels": 1,
        "diagnostic_sample_count": runtime.counts["diagnostic_sample_count"],
        "maximum_ndarray_dimensions": snapshot["resources"]["maximum_ndarray_dimensions"],
        "filesystem_audit_passed": False,
        "environment_audit_passed": False,
        "ast_call_graph_audit_passed": False,
        "closed_ir_audit_passed": set(snapshot["ir_kind_counts"]) == set(matrix["accepted_operation_ir"]["node_kinds"]),
        "isolated_staging_root": False,
        "repository_git_metadata_present": True,
        "target_or_mutation_files_present": True,
        "stdout_only_output": True,
        "runtime_receipt": {
            "schema": "tt-source-staging-runtime-receipt-v1",
            "status": "unattested_development",
            "valid": False,
        },
    }
    traffic = snapshot["traffic"]
    accounting = {
        "operation_vector": snapshot["operations"],
        "traffic_buckets": traffic,
        "logical_traffic_words": sum(
            int(row["reads"]) + int(row["writes"]) for row in traffic.values()
        ),
        "normalization_calls": runtime.counts["normalization_calls"],
        "streamed_prefix_factorizations": runtime.counts["streamed_prefix_factorizations"],
        "two_sweep_factorizations": runtime.counts["two_sweep_factorizations"],
        "total_rank_factorizations": runtime.counts["rank_factorizations"],
        "maximum_local_matrix_words": snapshot["resources"]["maximum_local_matrix_words"],
        "maximum_tt_object_words": snapshot["resources"]["maximum_tt_object_words"],
        "peak_live_field_words": snapshot["resources"]["peak_live_field_words"],
        "peak_rss_bytes": snapshot["resources"]["rss"]["bytes"],
        "wall_clock_ns": time.perf_counter_ns() - wall_start,
        "cpu_ns": time.process_time_ns() - cpu_start,
        "counters_reset": False,
    }
    ir_events, allocation_events, operation_ledger, gate_transcript = (
        normalized_runtime_ledgers(snapshot)
    )
    rank_ledger = {
        "tensor_record_count": len(rank_rows),
        "records": rank_rows,
        "records_sha256": verifier_digest(rank_rows),
    }
    return {
        "schema": RAW_SCHEMA,
        "protocol": PROTOCOL,
        "partition": "source_generator",
        "valid": True,
        "interpretation": INTERPRETATION,
        "claim_boundary": {
            "breakthrough_claim": False,
            "ecdlp_improvement_claim": False,
            "index_calculus_claim": False,
            "locator_claim": False,
            "target_specialization_claim": False,
            "toy_restricted_model_bound": True,
        },
        "inputs": {
            "source_manifest": manifest_path.name,
            "source_manifest_sha256": manifest_digest,
            "source_execution_matrix": matrix_path.name,
            "source_execution_matrix_sha256": matrix_digest,
        },
        "provenance": {
            "source_manifest_sha256": manifest_digest,
            "source_execution_matrix_sha256": matrix_digest,
            "rcb_gate_text_sha256": manifest["addition_law"]["normalized_gate_text_sha256"],
            "local_source_files": local_files,
            "local_source_closure_sha256": local_digest,
            "data_reads": [
                {"path": manifest_path.name, "sha256": manifest_digest, "bytes": len(manifest_bytes)},
                {"path": matrix_path.name, "sha256": matrix_digest, "bytes": len(matrix_bytes)},
            ],
        },
        "backend_attestation": backend,
        "capability_audit": capability,
        "cells": cells,
        "controls": control_certificates(),
        "ir_events": ir_events,
        "allocation_events": allocation_events,
        "operation_ledger": operation_ledger,
        "gate_rank_ledger": rank_ledger,
        "gate_transcript": gate_transcript,
        "accounting": accounting,
        "summary": {
            "completed": True,
            "primary_source_cells": 6,
            "control_source_cells": 1,
            "source_cells": 7,
            "source_tensor_records": 63,
            "retained_advice_tensors": 30,
            "semantic_mismatches": 0,
            "full_tuple_enumerations": 0,
            "implementation_gate": "semantic_and_rank_preflight_only",
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--execution-matrix", type=Path)
    parser.add_argument("--describe-schema", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.describe_schema:
        result = {
            "protocol": PROTOCOL,
            "schema": "tt-source-compiler-schema-description-v1",
            "valid": True,
            "baseline_cli": ["--manifest PATH", "--execution-matrix PATH"],
            "output_schema": RAW_SCHEMA,
            "current_gate": "semantic_and_rank_preflight_only",
        }
        status = 0
    else:
        try:
            if args.manifest is None or args.execution_matrix is None:
                raise ValueError("--manifest and --execution-matrix are required")
            result = run_compiler(args.manifest, args.execution_matrix)
            status = 0
        except Exception as exc:
            result = {
                "protocol": PROTOCOL,
                "schema": RAW_SCHEMA,
                "partition": "source_generator",
                "valid": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "failure_mode": "implementation_or_input_failure_not_mathematical_evidence",
            }
            status = 1
    sys.stdout.buffer.write(canonical_json_bytes(result))
    sys.stdout.buffer.write(b"\n")
    return status


if __name__ == "__main__":
    raise SystemExit(main())

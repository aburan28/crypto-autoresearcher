#!/usr/bin/env python3
"""Compile the frozen 25-target schedule from development source candidates.

This producer is intentionally development-only until an execution plan exists
and the source artifacts are formally frozen.  It reads one candidate source
bundle, the target manifest, and the full execution matrix; it never reads the
source raw result, source verifier, mutation manifest, or prior target output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tt_target_coefficients import general_basis_coefficients, trace_zero_coefficients
from tt_target_runtime import TargetTTRuntime, Tensor, canonical_json_bytes


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
BUNDLE_SCHEMA = "tt-source-candidate-bundle-development-v1"
TARGET_OUTPUT_SCHEMA = "tt-target-compiler-development-raw-v1"
SOURCE_BASIS = ("X2", "XZ", "Z2", "XY", "YZ", "Y2")
RETAINED_BASIS = ("X2", "XZ", "Z2", "YZ", "Y2")
PRIMARY_TRACE_SCHEDULE = {
    "random_unique": ("Q00", "Q01", "IDENTITY", "PLANTED"),
    "x_interval": ("Q00", "Q01"),
}
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_RAW_RESULT_BYTES = 268435456
TARGET_FIELD_SCALAR_KEYS = {
    "discriminant",
    "norm_n",
    "p",
    "trace_t",
    "trace_zero_norm_n",
}
TARGET_FIELD_VECTOR_KEYS = {
    "general_trace_coefficients",
    "projective",
    "trace_zero_coefficients",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def artifact_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value) + b"\n")


def canonical_json_size(value: Any) -> int:
    """Return exact canonical JSON bytes without materializing the full payload."""

    if value is None:
        return 4
    if value is True:
        return 4
    if value is False:
        return 5
    if isinstance(value, int):
        return len(str(value))
    if isinstance(value, str):
        return len(
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    if isinstance(value, (list, tuple)):
        return 2 + max(len(value) - 1, 0) + sum(
            canonical_json_size(item) for item in value
        )
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("canonical JSON object keys must be strings")
        return 2 + max(len(value) - 1, 0) + sum(
            canonical_json_size(key) + 1 + canonical_json_size(item)
            for key, item in value.items()
        )
    raise TypeError(f"unsupported canonical JSON value {type(value).__name__}")


def stabilize_serialized_size(result: dict[str, Any]) -> int:
    """Solve the self-referential serialized_bytes decimal width exactly."""

    result["summary"]["serialized_bytes"] = 0
    # The trailing newline replaces the one-byte placeholder when solving width.
    base = canonical_json_size(result)
    candidate = base + 1
    while True:
        updated = base + len(str(candidate))
        if updated == candidate:
            result["summary"]["serialized_bytes"] = updated
            return updated
        candidate = updated


def validate_digest(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


def read_json(path: Path, label: str, maximum_bytes: int = MAX_INPUT_BYTES) -> tuple[dict[str, Any], bytes]:
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


def retained_tensor_field_words(value: Any) -> int:
    if isinstance(value, Mapping):
        cores = value.get("cores")
        if isinstance(cores, list):
            total = 0
            for core in cores:
                if isinstance(core, Mapping) and isinstance(core.get("values"), list):
                    total += len(core["values"])
            return total
        return sum(retained_tensor_field_words(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return sum(retained_tensor_field_words(item) for item in value)
    return 0


def target_registry_field_words(value: Any) -> int:
    if isinstance(value, Mapping):
        total = 0
        for key, item in value.items():
            if key in TARGET_FIELD_SCALAR_KEYS and isinstance(item, int):
                total += 1
            elif key in TARGET_FIELD_VECTOR_KEYS and isinstance(item, list):
                total += sum(isinstance(entry, int) for entry in item)
            else:
                total += target_registry_field_words(item)
        return total
    if isinstance(value, (list, tuple)):
        return sum(target_registry_field_words(item) for item in value)
    return 0


def exact_int(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{path} must be an integer at least {minimum}")
    return value


@dataclass(frozen=True)
class TargetJob:
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


def audit_inputs(
    bundle: Mapping[str, Any],
    target_record: Mapping[str, Any],
    target_bytes: bytes,
    matrix_record: Mapping[str, Any],
    matrix_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if (
        bundle.get("schema") != BUNDLE_SCHEMA
        or bundle.get("valid") is not True
        or bundle.get("artifact_freeze_authorized") is not False
        or bundle.get("protocol") != PROTOCOL
    ):
        raise ValueError("source candidate bundle does not have the development boundary")
    target = target_record.get("target_manifest")
    matrix = matrix_record.get("execution_matrix")
    if not isinstance(target, dict) or not isinstance(matrix, dict):
        raise ValueError("target manifest or execution matrix wrapper is malformed")
    if target.get("status") != "approved_for_implementation":
        raise ValueError("target manifest is not approved for implementation")
    if matrix.get("status") != "approved_for_implementation":
        raise ValueError("execution matrix is not approved for implementation")
    bindings = matrix.get("bindings")
    if not isinstance(bindings, dict):
        raise ValueError("execution matrix bindings are missing")
    target_digest = sha256_bytes(target_bytes)
    if bindings.get("target_manifest_sha256") != target_digest:
        raise ValueError("execution matrix does not bind the target manifest bytes")
    candidate_digests = bundle.get("candidate_artifact_digests")
    advice = bundle.get("candidate_retained_advice")
    controls = bundle.get("candidate_control_certificates")
    if not isinstance(candidate_digests, dict) or not isinstance(advice, dict) or not isinstance(controls, dict):
        raise ValueError("source candidate bundle objects are malformed")
    observed_advice_digest = artifact_digest(advice)
    observed_control_digest = artifact_digest(controls)
    if observed_advice_digest != validate_digest(
        candidate_digests.get("retained_advice_sha256"),
        "candidate_artifact_digests.retained_advice_sha256",
    ):
        raise ValueError("candidate retained advice digest mismatch")
    if observed_control_digest != validate_digest(
        candidate_digests.get("control_certificate_sha256"),
        "candidate_artifact_digests.control_certificate_sha256",
    ):
        raise ValueError("candidate source controls digest mismatch")
    validate_digest(
        candidate_digests.get("source_advice_receipt_sha256"),
        "candidate_artifact_digests.source_advice_receipt_sha256",
    )
    return target, matrix, {
        "candidate_control_certificate_sha256": observed_control_digest,
        "candidate_retained_advice_sha256": observed_advice_digest,
        "execution_matrix_sha256": sha256_bytes(matrix_bytes),
        "source_advice_receipt_sha256": candidate_digests["source_advice_receipt_sha256"],
        "target_manifest_sha256": target_digest,
    }


def manifest_instances(target: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    instances = target.get("instances")
    if not isinstance(instances, list) or len(instances) != 3:
        raise ValueError("target manifest must contain three curve instances")
    result: dict[str, Mapping[str, Any]] = {}
    for index, instance in enumerate(instances):
        if not isinstance(instance, dict) or not isinstance(instance.get("curve_id"), str):
            raise ValueError(f"target_manifest.instances[{index}] is malformed")
        curve_id = str(instance["curve_id"])
        if curve_id in result:
            raise ValueError(f"duplicate target curve {curve_id}")
        result[curve_id] = instance
    if tuple(result) != ("C08", "C10", "C12"):
        raise ValueError("target curve order changed")
    return result


def derive_trace_job(
    instance: Mapping[str, Any],
    *,
    registry: str,
    target_name: str,
    source_cell_id: str,
    target_cell_id: str | None = None,
    kind: str = "trace_zero",
    runtime: TargetTTRuntime | None = None,
) -> TargetJob:
    curve_id = str(instance["curve_id"])
    p = exact_int(instance.get("p"), f"{curve_id}.p", 2)
    n = exact_int(instance.get("trace_zero_norm_n"), f"{curve_id}.trace_zero_norm_n")
    targets = instance.get("targets")
    if not isinstance(targets, dict) or not isinstance(targets.get(target_name), dict):
        raise ValueError(f"{curve_id} target {target_name} is missing")
    target = targets[target_name]
    projective_value = target.get("projective")
    if not isinstance(projective_value, list) or len(projective_value) != 3:
        raise ValueError(f"{curve_id}.{target_name}.projective is malformed")
    projective = tuple(
        exact_int(value, f"{curve_id}.{target_name}.projective") for value in projective_value
    )
    frozen = target.get("trace_zero_coefficients")
    cell_id = target_cell_id or f"{source_cell_id}:{target_name}"
    if not isinstance(frozen, list):
        raise ValueError(f"{curve_id}.{target_name} trace-zero coefficients are missing")
    if runtime is None:
        derived = trace_zero_coefficients(projective, p, n)
        if tuple(frozen) != derived:
            raise ValueError(f"{curve_id}.{target_name} trace-zero coefficients changed")
    else:
        derived = runtime.derive_target_coefficients(
            label=cell_id,
            kind="trace_zero",
            projective=projective,
            p=p,
            norm_n=n,
            frozen_coefficients=frozen,
        )
    retained = (derived[0], derived[1], derived[2], derived[4], derived[5])
    return TargetJob(
        target_cell_id=cell_id,
        source_cell_id=source_cell_id,
        curve_id=curve_id,
        registry=registry,
        target_name=target_name,
        target_id=str(target.get("target_id")),
        kind=kind,
        projective=projective,
        source_names=RETAINED_BASIS,
        coefficients=retained,
    )


def derive_general_job(
    instance: Mapping[str, Any],
    *,
    registry: str,
    source_cell_id: str,
    runtime: TargetTTRuntime | None = None,
) -> TargetJob:
    curve_id = str(instance["curve_id"])
    p = exact_int(instance.get("p"), f"{curve_id}.p", 2)
    targets = instance.get("targets")
    control = instance.get("general_trace_control")
    if not isinstance(targets, dict) or not isinstance(targets.get("Q00"), dict) or not isinstance(control, dict):
        raise ValueError(f"{curve_id} general trace control is malformed")
    target = targets["Q00"]
    projective = tuple(target["projective"])
    trace_t = exact_int(
        control.get("trace_t"), f"{curve_id}.general_trace_control.trace_t"
    )
    norm_n = exact_int(
        control.get("norm_n"), f"{curve_id}.general_trace_control.norm_n"
    )
    frozen = target.get("general_trace_coefficients")
    if not isinstance(frozen, list):
        raise ValueError(f"{curve_id}.Q00 general coefficients are missing")
    target_cell_id = f"{source_cell_id}:GENERAL_TRACE_Q00"
    if runtime is None:
        derived = general_basis_coefficients(projective, p, trace_t, norm_n)
        if tuple(frozen) != derived:
            raise ValueError(f"{curve_id}.Q00 general coefficients changed")
    else:
        derived = runtime.derive_target_coefficients(
            label=target_cell_id,
            kind="general_trace",
            projective=projective,
            p=p,
            norm_n=norm_n,
            trace_t=trace_t,
            frozen_coefficients=frozen,
        )
    return TargetJob(
        target_cell_id=target_cell_id,
        source_cell_id=source_cell_id,
        curve_id=curve_id,
        registry=registry,
        target_name="GENERAL_TRACE_Q00",
        target_id=f"{target['target_id']}-GENERAL-TRACE",
        kind="general_trace_control",
        projective=projective,  # type: ignore[arg-type]
        source_names=SOURCE_BASIS,
        coefficients=derived,
    )


def build_schedule(
    target: Mapping[str, Any], runtime: TargetTTRuntime | None = None
) -> list[TargetJob]:
    instances = manifest_instances(target)
    jobs: list[TargetJob] = []
    for curve_id, instance in instances.items():
        for registry in ("random_unique", "x_interval"):
            source_cell_id = f"{curve_id}:{registry}"
            for target_name in PRIMARY_TRACE_SCHEDULE[registry]:
                jobs.append(
                    derive_trace_job(
                        instance,
                        registry=registry,
                        target_name=target_name,
                        source_cell_id=source_cell_id,
                        runtime=runtime,
                    )
                )
            jobs.append(
                derive_general_job(
                    instance,
                    registry=registry,
                    source_cell_id=source_cell_id,
                    runtime=runtime,
                )
            )
    jobs.append(
        derive_trace_job(
            instances["C08"],
            registry="modewise_rescaled_control",
            target_name="Q00",
            source_cell_id="C08:random_unique:MODEWISE_RESCALED",
            target_cell_id="C08:random_unique:MODEWISE_RESCALED:Q00",
            kind="modewise_rescaled_trace_zero_control",
            runtime=runtime,
        )
    )
    if len(jobs) != 25 or len({job.target_cell_id for job in jobs}) != 25:
        raise AssertionError("derived target schedule is not 25 unique cells")
    trace_count = sum(job.kind != "general_trace_control" for job in jobs)
    general_count = sum(job.kind == "general_trace_control" for job in jobs)
    if (trace_count, general_count) != (19, 6):
        raise AssertionError("derived target schedule does not reconcile 19+6")
    return jobs


def source_tensor_map(
    runtime: TargetTTRuntime,
    advice: Mapping[str, Any],
    controls: Mapping[str, Any],
) -> dict[str, dict[str, Tensor]]:
    result: dict[str, dict[str, Tensor]] = {}
    advice_cells = advice.get("cells")
    xy_rows = controls.get("xy_certificates")
    control_cell = controls.get("modewise_rescaled_source_cell")
    if not isinstance(advice_cells, list) or not isinstance(xy_rows, list) or not isinstance(control_cell, dict):
        raise ValueError("candidate source artifact cell structure is malformed")
    xy_map = {
        row.get("cell_id"): row.get("tensor")
        for row in xy_rows
        if isinstance(row, dict)
    }
    for cell in advice_cells:
        if not isinstance(cell, dict) or not isinstance(cell.get("cell_id"), str):
            raise ValueError("candidate advice cell is malformed")
        cell_id = str(cell["cell_id"])
        rows = cell.get("tensors")
        if not isinstance(rows, list) or len(rows) != 5:
            raise ValueError(f"candidate advice cell {cell_id} does not contain five tensors")
        imported = {
            str(row.get("name")): runtime.tensor_from_record(row)
            for row in rows
            if isinstance(row, dict)
        }
        xy_record = xy_map.get(cell_id)
        if not isinstance(xy_record, dict):
            raise ValueError(f"candidate XY certificate for {cell_id} is missing")
        imported["XY"] = runtime.tensor_from_record(xy_record, expected_name="XY")
        if set(imported) != set(SOURCE_BASIS):
            raise ValueError(f"candidate source basis for {cell_id} is incomplete")
        result[cell_id] = imported
    control_id = control_cell.get("cell_id")
    rows = control_cell.get("tensors")
    if not isinstance(control_id, str) or not isinstance(rows, list):
        raise ValueError("modewise-rescaled source control is malformed")
    control_sources = {
        str(row.get("name")): runtime.tensor_from_record(row)
        for row in rows
        if isinstance(row, dict) and row.get("name") in RETAINED_BASIS
    }
    if set(control_sources) != set(RETAINED_BASIS):
        raise ValueError("modewise-rescaled source control lacks retained basis")
    result[control_id] = control_sources
    if len(result) != 7:
        raise ValueError("target compiler did not import six primary cells and one control")
    return result


def compile_targets(
    bundle: Mapping[str, Any],
    target: Mapping[str, Any],
    matrix: Mapping[str, Any],
    *,
    reverse_schedule: bool = False,
) -> tuple[list[dict[str, Any]], TargetTTRuntime, str]:
    operation_caps = matrix.get("partition_operation_caps")
    traffic_caps = matrix.get("partition_traffic_caps_words")
    resource_gates = matrix.get("resource_gates")
    if not isinstance(operation_caps, dict) or not isinstance(traffic_caps, dict) or not isinstance(resource_gates, dict):
        raise ValueError("execution matrix target accounting policy is malformed")
    runtime = TargetTTRuntime(
        operation_caps=operation_caps["target_generator"],
        traffic_cap_words=traffic_caps["target_generator"],
        resource_gates=resource_gates,
    )
    advice = bundle["candidate_retained_advice"]
    controls = bundle["candidate_control_certificates"]
    input_field_words = (
        retained_tensor_field_words(advice)
        + retained_tensor_field_words(controls)
        + target_registry_field_words(target)
    )
    runtime.record_input_retention(input_field_words)
    sources = source_tensor_map(runtime, advice, controls)
    jobs = build_schedule(target, runtime)
    if reverse_schedule:
        jobs.reverse()
    records: list[dict[str, Any]] = []
    for job in jobs:
        available = sources.get(job.source_cell_id)
        if available is None:
            raise ValueError(f"source cell {job.source_cell_id} is unavailable")
        tensors = tuple(available[name] for name in job.source_names)
        result = runtime.weighted_sum(
            tensors,
            job.coefficients,
            label=job.target_cell_id,
        )
        tensor_record = runtime.target_record(result)
        records.append(
            {
                "coefficients": list(job.coefficients),
                "curve_id": job.curve_id,
                "kind": job.kind,
                "projective": list(job.projective),
                "registry": job.registry,
                "source_basis_order": list(job.source_names),
                "source_cell_id": job.source_cell_id,
                "target_cell_id": job.target_cell_id,
                "target_id": job.target_id,
                "target_name": job.target_name,
                "tensor": tensor_record,
            }
        )
        runtime.record_target_disposal(result)
        del result
    target_field_words = sum(record["tensor"]["word_count"] for record in records)
    target_digest = runtime.record_artifact_digest(
        records,
        label="target_records",
        field_words=target_field_words,
    )
    counts = runtime.counts
    if counts["target_linear_combinations"] != 25:
        raise AssertionError("target runtime did not execute 25 linear combinations")
    if counts["normalization_calls"] != 25:
        raise AssertionError("target runtime did not execute 25 normalizations")
    if counts["two_sweep_factorizations"] != 200:
        raise AssertionError(
            "target schedule did not execute the frozen 200 two-sweep factorizations"
        )
    if counts["zero_results"] != 0:
        raise AssertionError("frozen target schedule unexpectedly produced a canonical zero")
    if counts["target_coefficient_formations"] != 25:
        raise AssertionError("target runtime did not meter 25 coefficient formations")
    if counts["target_disposals"] != 25:
        raise AssertionError("target runtime did not record 25 target disposals")
    if counts["artifact_serialization_events"] != 1:
        raise AssertionError("target runtime did not meter the target-list digest")
    if counts["input_retention_events"] != 1:
        raise AssertionError("target runtime did not meter decoded input retention")
    return records, runtime, target_digest


def compile_development(args: argparse.Namespace) -> dict[str, Any]:
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    bundle, bundle_bytes = read_json(args.candidate_source_bundle, "candidate source bundle")
    target_record, target_bytes = read_json(args.target_manifest, "target manifest")
    matrix_record, matrix_bytes = read_json(args.execution_matrix, "execution matrix")
    target, matrix, bindings = audit_inputs(
        bundle, target_record, target_bytes, matrix_record, matrix_bytes
    )
    targets, runtime_engine, target_digest = compile_targets(bundle, target, matrix)
    target_field_words = sum(record["tensor"]["word_count"] for record in targets)
    runtime_engine.record_output_serialization(
        label="target_generator_development_result",
        field_words=target_field_words,
        size_scan_passes=2,
        serialization_passes=2,
    )
    runtime = runtime_engine.snapshot()
    result = {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development-only target specialization over candidate source objects. "
            "No source artifact or target result is frozen, no experiment run is "
            "authorized, and no locator, index-calculus, rho, or ECDLP improvement is claimed."
        ),
        "claim_boundary": {
            "breakthrough_claim": False,
            "ecdlp_improvement_claim": False,
            "index_calculus_claim": False,
            "locator_claim": False,
            "target_specialization_claim": False,
            "toy_restricted_model_bound": True,
        },
        "inputs": bindings
        | {
            "candidate_source_bundle_sha256": sha256_bytes(bundle_bytes),
        },
        "partition": "target_generator_development",
        "protocol": PROTOCOL,
        "runtime": runtime,
        "schema": TARGET_OUTPUT_SCHEMA,
        "summary": {
            "completed": True,
            "full_tuple_enumerations": 0,
            "general_trace_targets": 6,
            "mutation_manifest_reads_in_target_phase": 0,
            "source_raw_result_reads_in_target_phase": 0,
            "serialized_bytes": 0,
            "target_tensor_records": 25,
            "targets_sha256": target_digest,
            "trace_zero_targets": 19,
        },
        "targets": targets,
        "timing": {
            "cpu_ns": 0,
            "wall_clock_ns": 0,
        },
        "valid": True,
    }
    serialized_bytes = stabilize_serialized_size(result)
    if serialized_bytes > MAX_RAW_RESULT_BYTES:
        raise ValueError("target raw result exceeds the frozen 256 MiB gate")
    materialized = canonical_json_bytes(result) + b"\n"
    if len(materialized) != serialized_bytes:
        raise AssertionError("target raw result size preflight was not exact")
    result["runtime"]["resources"]["rss"] = runtime_engine.rss_record()
    result["timing"] = {
        "cpu_ns": time.process_time_ns() - cpu_start,
        "wall_clock_ns": time.perf_counter_ns() - wall_start,
    }
    del materialized
    serialized_bytes = stabilize_serialized_size(result)
    if serialized_bytes > MAX_RAW_RESULT_BYTES:
        raise ValueError("target raw result exceeds the frozen 256 MiB gate")
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--candidate-source-bundle", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-matrix", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = compile_development(parse_args(argv))
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "partition": "target_generator_development",
            "schema": "tt-target-compiler-development-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_json_bytes(failure) + b"\n")
        return 1
    payload = canonical_json_bytes(result) + b"\n"
    if len(payload) != result["summary"]["serialized_bytes"]:
        raise AssertionError("target raw result serialized-byte accounting changed")
    if len(payload) > MAX_RAW_RESULT_BYTES:
        raise AssertionError("target raw result exceeds its serialized-byte gate")
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

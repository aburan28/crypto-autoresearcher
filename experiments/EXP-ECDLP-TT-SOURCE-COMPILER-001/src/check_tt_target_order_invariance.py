#!/usr/bin/env python3
"""Check development target-order invariance in forward and reverse schedules."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from compile_tt_target_advice import (
    BUNDLE_SCHEMA,
    PROTOCOL,
    artifact_digest,
    compile_targets,
)
from tt_target_runtime import canonical_json_bytes


def read_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def target_map(records: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {str(record["target_cell_id"]): record for record in records}
    if len(result) != 25:
        raise ValueError("target order control did not receive 25 unique target records")
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    bundle = read_object(args.candidate_source_bundle, "candidate source bundle")
    target_record = read_object(args.target_manifest, "target manifest")
    matrix_record = read_object(args.execution_matrix, "execution matrix")
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
    advice = bundle["candidate_retained_advice"]
    controls = bundle["candidate_control_certificates"]
    source_digests_before = {
        "candidate_control_certificate_sha256": artifact_digest(controls),
        "candidate_retained_advice_sha256": artifact_digest(advice),
    }
    forward, forward_engine, _ = compile_targets(
        bundle, target, matrix, reverse_schedule=False
    )
    reverse, reverse_engine, _ = compile_targets(
        bundle, target, matrix, reverse_schedule=True
    )
    forward_runtime = forward_engine.snapshot()
    reverse_runtime = reverse_engine.snapshot()
    source_digests_after = {
        "candidate_control_certificate_sha256": artifact_digest(controls),
        "candidate_retained_advice_sha256": artifact_digest(advice),
    }
    if source_digests_before != source_digests_after:
        raise AssertionError("source candidate objects changed during target compilation")
    forward_map = target_map(forward)
    reverse_map = target_map(reverse)
    if forward_map != reverse_map:
        changed = sorted(
            target_id
            for target_id in forward_map
            if forward_map[target_id] != reverse_map.get(target_id)
        )
        raise AssertionError(f"target tensors changed under schedule reversal: {changed}")
    forward_operations = dict(forward_runtime["operations"])
    reverse_operations = dict(reverse_runtime["operations"])
    forward_hash_bytes = forward_operations.pop("hash_bytes")
    reverse_hash_bytes = reverse_operations.pop("hash_bytes")
    if forward_operations != reverse_operations:
        raise AssertionError("target arithmetic changed under schedule reversal")
    for field in ("traffic", "logical_traffic_words"):
        if forward_runtime[field] != reverse_runtime[field]:
            raise AssertionError(f"target runtime {field} changed under schedule reversal")
    resource_fields = (
        "maximum_int64_accumulator_bound",
        "maximum_int64_dot_length",
        "maximum_local_matrix_words",
        "maximum_tt_object_words",
        "persistent_input_field_words",
        "persistent_source_words",
        "persistent_target_output_words",
    )
    for field in resource_fields:
        if forward_runtime["resources"][field] != reverse_runtime["resources"][field]:
            raise AssertionError(f"target runtime resource {field} changed under reversal")
    return {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development-only target-order invariance control. It establishes "
            "deterministic implementation behavior for the toy schedule only."
        ),
        "forward_order": [record["target_cell_id"] for record in forward],
        "per_target_records_sha256": artifact_digest(forward_map),
        "protocol": PROTOCOL,
        "reverse_order": [record["target_cell_id"] for record in reverse],
        "schedule_peak_live_field_words": {
            "forward": forward_runtime["resources"]["peak_live_field_words"],
            "reverse": reverse_runtime["resources"]["peak_live_field_words"],
        },
        "schedule_certificate_hash_bytes": {
            "forward": forward_hash_bytes,
            "reverse": reverse_hash_bytes,
        },
        "schema": "tt-target-order-invariance-development-v1",
        "source_candidate_digests": source_digests_before,
        "summary": {
            "arithmetic_and_traffic_equal": True,
            "schedule_dependent_certificate_bytes_reported": True,
            "schedule_dependent_peaks_reported": True,
            "source_candidates_unchanged": True,
            "target_records_equal_by_id": 25,
        },
        "valid": True,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--candidate-source-bundle", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-matrix", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = run(parse_args(argv))
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-target-order-invariance-development-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_json_bytes(failure) + b"\n")
        return 1
    sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

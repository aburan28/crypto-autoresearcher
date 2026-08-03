#!/usr/bin/env python3
"""Build a development-only target input bundle from verified source output.

The bundle is a harness handoff, not a frozen source artifact.  It reconstructs
the candidate retained-advice and control objects whose digests were checked by
the strict source preflight, verifies those digests, and labels the resulting
wrapper as unauthorized for artifact freeze or experiment execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import product
from pathlib import Path
from typing import Any, Mapping, Sequence

from tt_target_runtime import OPERATION_KEYS, TargetTTRuntime, canonical_json_bytes, stable_digest


BUNDLE_SCHEMA = "tt-source-candidate-bundle-development-v1"
STRICT_REPORT_SCHEMA = "tt-source-strict-preflight-development-verification-v1"
RAW_SCHEMA = "tt-source-compiler-raw-v1"
ADVICE_SCHEMA = "frozen-source-advice-v1"
CONTROL_SCHEMA = "frozen-source-control-certificates-v1"
TENSOR_NAMES = ("X", "Y", "Z", "X2", "XZ", "Z2", "XY", "YZ", "Y2")
RETAINED_NAMES = ("X2", "XZ", "Z2", "YZ", "Y2")
SOURCE_CONTROL_PROFILE_SHA256 = (
    "7e892237657dd84d7bdff8dd77883a35ea901580a929a647b53db0cf3a4ba208"
)
MAX_RAW_BYTES = 268435456


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def artifact_digest(value: Any) -> str:
    """Digest the verifier's canonical artifact encoding, including its newline."""

    return sha256_bytes(canonical_json_bytes(value) + b"\n")


def read_canonical_json(path: Path, label: str, maximum_bytes: int) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    if len(data) > maximum_bytes:
        raise ValueError(f"{label} exceeds {maximum_bytes} bytes")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    if data != canonical_json_bytes(value) + b"\n":
        raise ValueError(f"{label} is not canonical JSON with one trailing newline")
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


def development_runtime() -> TargetTTRuntime:
    return TargetTTRuntime(
        operation_caps={key: 10**12 for key in OPERATION_KEYS},
        traffic_cap_words=10**12,
        resource_gates={
            "maximum_local_matrix_words": 1000000,
            "maximum_tt_object_words": 1000000,
            "predicted_peak_live_field_words": 500000,
            "maximum_int64_dot_length": 150,
            "maximum_int64_accumulator_bound": 2335637400,
            "signed_int64_maximum": 9223372036854775807,
            "peak_rss_bytes": 2147483648,
        },
    )


def normalized_tensor_record(
    wrapper: Mapping[str, Any],
    *,
    expected_name: str,
    expected_p: int,
    expected_B: int,
) -> dict[str, Any]:
    if wrapper.get("name") != expected_name:
        raise ValueError(f"source tensor name does not match {expected_name}")
    native = wrapper.get("tensor")
    if not isinstance(native, dict) or native.get("encoding") != "exact-fp-tt-v1":
        raise ValueError(f"{expected_name} is not an exact-fp-tt-v1 record")
    record_digest = validate_digest(native.get("record_sha256"), f"{expected_name}.record_sha256")
    without_digest = dict(native)
    without_digest.pop("record_sha256")
    if stable_digest(without_digest) != record_digest:
        raise ValueError(f"{expected_name} producer record digest mismatch")
    p = exact_int(native.get("field_modulus"), f"{expected_name}.field_modulus", 2)
    B = exact_int(native.get("physical_mode_size"), f"{expected_name}.B", 1)
    if p != expected_p or B != expected_B or native.get("physical_mode_count") != 5:
        raise ValueError(f"{expected_name} source tensor dimensions changed")
    ranks = native.get("ranks")
    cores = native.get("cores")
    if not isinstance(ranks, list) or len(ranks) != 4 or not isinstance(cores, list):
        raise ValueError(f"{expected_name} has invalid ranks or cores")
    normalized_cores: list[dict[str, Any]] = []
    width = max(1, (p.bit_length() + 7) // 8)
    for mode, core in enumerate(cores):
        if not isinstance(core, dict):
            raise ValueError(f"{expected_name}.cores[{mode}] must be an object")
        shape = core.get("shape")
        values = core.get("values")
        if not isinstance(shape, list) or len(shape) != 3 or not isinstance(values, list):
            raise ValueError(f"{expected_name}.cores[{mode}] is malformed")
        parsed_shape = [
            exact_int(dimension, f"{expected_name}.cores[{mode}].shape", 1)
            for dimension in shape
        ]
        words = parsed_shape[0] * parsed_shape[1] * parsed_shape[2]
        if len(values) != words:
            raise ValueError(f"{expected_name}.cores[{mode}] has the wrong value count")
        parsed_values = [
            exact_int(value, f"{expected_name}.cores[{mode}].values", 0)
            for value in values
        ]
        if any(value >= p for value in parsed_values):
            raise ValueError(f"{expected_name}.cores[{mode}] has a noncanonical residue")
        digest = hashlib.sha256()
        for value in parsed_values:
            digest.update(value.to_bytes(width, "big"))
        if digest.hexdigest() != validate_digest(
            core.get("value_digest_sha256"),
            f"{expected_name}.cores[{mode}].value_digest_sha256",
        ):
            raise ValueError(f"{expected_name}.cores[{mode}] value digest mismatch")
        normalized_cores.append({"shape": parsed_shape, "values": parsed_values})
    tag = native.get("tag")
    if tag not in ("nonzero", "canonical_zero"):
        raise ValueError(f"{expected_name} has an invalid producer tag")
    return {
        "B": B,
        "cores": normalized_cores,
        "name": expected_name,
        "p": p,
        "ranks": [exact_int(rank, f"{expected_name}.ranks", 0) for rank in ranks],
        "tag": "tt" if tag == "nonzero" else "canonical_zero",
    }


def dense_value_digest(record: Mapping[str, Any]) -> str:
    engine = development_runtime()
    tensor = engine.tensor_from_record(record, expected_name=str(record["name"]))
    width = max(1, (tensor.p.bit_length() + 7) // 8)
    digest = hashlib.sha256()
    for indices in product(range(tensor.B), repeat=5):
        value = engine.evaluate(tensor, indices)
        digest.update(value.to_bytes(width, "big"))
    return digest.hexdigest()


def artifact_tensor(record: Mapping[str, Any]) -> dict[str, Any]:
    canonical = dict(record)
    return canonical | {
        "core_digest_sha256": artifact_digest(canonical),
        "value_digest_sha256": dense_value_digest(canonical),
        "word_count": sum(
            len(core["values"]) for core in canonical["cores"]  # type: ignore[index]
        ),
    }


def build_candidate_artifacts(raw: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if raw.get("schema") != RAW_SCHEMA or raw.get("partition") != "source_generator":
        raise ValueError("raw result is not the expected source-generator result")
    inputs = raw.get("inputs")
    cells = raw.get("cells")
    if not isinstance(inputs, dict) or not isinstance(cells, list) or len(cells) != 7:
        raise ValueError("raw result source inputs or cell count is invalid")
    source_manifest_digest = validate_digest(
        inputs.get("source_manifest_sha256"), "raw.inputs.source_manifest_sha256"
    )
    source_matrix_digest = validate_digest(
        inputs.get("source_execution_matrix_sha256"),
        "raw.inputs.source_execution_matrix_sha256",
    )
    advice_cells: list[dict[str, Any]] = []
    xy_certificates: list[dict[str, Any]] = []
    control_cell: dict[str, Any] | None = None
    for cell_index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            raise ValueError(f"raw.cells[{cell_index}] must be an object")
        metadata = {
            "B": exact_int(cell.get("B"), f"raw.cells[{cell_index}].B", 1),
            "cell_id": cell.get("cell_id"),
            "curve_id": cell.get("curve_id"),
            "p": exact_int(cell.get("p"), f"raw.cells[{cell_index}].p", 2),
            "registry": cell.get("registry"),
        }
        if any(not isinstance(metadata[key], str) for key in ("cell_id", "curve_id", "registry")):
            raise ValueError(f"raw.cells[{cell_index}] metadata is malformed")
        tensor_rows = cell.get("tensors")
        if not isinstance(tensor_rows, list) or len(tensor_rows) != len(TENSOR_NAMES):
            raise ValueError(f"raw.cells[{cell_index}] tensor schedule is malformed")
        by_name = {
            row.get("name"): row for row in tensor_rows if isinstance(row, dict)
        }
        if tuple(by_name) != TENSOR_NAMES:
            raise ValueError(f"raw.cells[{cell_index}] tensor order changed")
        tensors = {
            name: artifact_tensor(
                normalized_tensor_record(
                    by_name[name],
                    expected_name=name,
                    expected_p=int(metadata["p"]),
                    expected_B=int(metadata["B"]),
                )
            )
            for name in TENSOR_NAMES
        }
        retained = cell.get("retained_advice")
        if retained is True:
            advice_cells.append(
                metadata | {"tensors": [tensors[name] for name in RETAINED_NAMES]}
            )
            xy_certificates.append(metadata | {"tensor": tensors["XY"]})
        elif retained is False:
            if control_cell is not None:
                raise ValueError("more than one nonretained source control cell")
            mode_scalars = cell.get("mode_scalars")
            if not isinstance(mode_scalars, list) or len(mode_scalars) != 5:
                raise ValueError("source control cell mode scalars are malformed")
            control_cell = metadata | {
                "mode_scalars": [exact_int(value, "mode_scalars", 0) for value in mode_scalars],
                "tensors": [tensors[name] for name in TENSOR_NAMES],
            }
        else:
            raise ValueError(f"raw.cells[{cell_index}].retained_advice is not boolean")
    if len(advice_cells) != 6 or control_cell is None:
        raise ValueError("candidate bundle requires six advice cells and one control cell")
    advice = {
        "cells": advice_cells,
        "retained_tensor_count": 30,
        "retained_tensor_names": list(RETAINED_NAMES),
        "schema": ADVICE_SCHEMA,
        "source_execution_matrix_sha256": source_matrix_digest,
        "source_manifest_sha256": source_manifest_digest,
    }
    controls = {
        "modewise_rescaled_source_cell": control_cell,
        "schema": CONTROL_SCHEMA,
        "source_control_profile_sha256": SOURCE_CONTROL_PROFILE_SHA256,
        "source_execution_matrix_sha256": source_matrix_digest,
        "source_manifest_sha256": source_manifest_digest,
        "xy_certificates": xy_certificates,
    }
    return advice, controls


def build_bundle(raw_path: Path, strict_report_path: Path) -> dict[str, Any]:
    raw, raw_bytes = read_canonical_json(raw_path, "source raw result", MAX_RAW_BYTES)
    report, report_bytes = read_canonical_json(
        strict_report_path, "strict source preflight report", 16 * 1024 * 1024
    )
    if (
        report.get("schema") != STRICT_REPORT_SCHEMA
        or report.get("partition") != "source_verifier_strict_preflight_development"
        or report.get("valid") is not True
        or report.get("artifact_freeze_authorized") is not False
    ):
        raise ValueError("strict source report does not have the development preflight boundary")
    raw_digest = sha256_bytes(raw_bytes)
    if report.get("raw_result_sha256") != raw_digest:
        raise ValueError("strict source report does not bind the supplied raw result")
    expected = report.get("candidate_artifact_digests")
    if not isinstance(expected, dict):
        raise ValueError("strict source report lacks candidate artifact digests")
    advice, controls = build_candidate_artifacts(raw)
    observed = {
        "control_certificate_sha256": artifact_digest(controls),
        "retained_advice_sha256": artifact_digest(advice),
        "source_advice_receipt_sha256": validate_digest(
            expected.get("source_advice_receipt_sha256"),
            "candidate_artifact_digests.source_advice_receipt_sha256",
        ),
    }
    for key in ("control_certificate_sha256", "retained_advice_sha256"):
        if observed[key] != validate_digest(expected.get(key), f"candidate_artifact_digests.{key}"):
            raise ValueError(f"reconstructed candidate {key} does not match strict preflight")
    return {
        "artifact_freeze_authorized": False,
        "boundary": (
            "Development-only harness handoff reconstructed from a strict source "
            "preflight. These candidate objects are not frozen source artifacts and "
            "do not authorize a target run or any cryptanalytic claim."
        ),
        "candidate_artifact_digests": observed,
        "candidate_control_certificates": controls,
        "candidate_retained_advice": advice,
        "protocol": raw.get("protocol"),
        "schema": BUNDLE_SCHEMA,
        "source_raw_result_sha256": raw_digest,
        "strict_source_preflight_report_sha256": sha256_bytes(report_bytes),
        "valid": True,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--strict-preflight-report", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        bundle = build_bundle(args.raw_result, args.strict_preflight_report)
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-source-candidate-bundle-development-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(canonical_json_bytes(failure) + b"\n")
        return 1
    sys.stdout.buffer.write(canonical_json_bytes(bundle) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

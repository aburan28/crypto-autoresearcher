#!/usr/bin/env python3
"""Run synthetic fail-closed mutations against the target verifier."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence

import verify_tt_target_advice as verifier


Mutation = Callable[[dict[str, Any]], None]


def rebind_targets(raw: dict[str, Any]) -> None:
    raw["summary"]["targets_sha256"] = verifier.artifact_digest(raw["targets"])
    payload = verifier.canonical_json_bytes(raw["targets"]) + b"\n"
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "target_artifact_serialization"
        and event["variant"] == "digest"
    )
    byte_delta = len(payload) - event["payload_bytes"]
    event["payload_bytes"] = len(payload)
    event["digest_sha256"] = verifier.sha256_bytes(payload)
    event["operation_vector"]["hash_bytes"] += byte_delta
    raw["runtime"]["operations"]["hash_bytes"] += byte_delta


def canonical_raw_bytes(raw: dict[str, Any]) -> bytes:
    raw["summary"]["serialized_bytes"] = 0
    for _ in range(3):
        payload = verifier.canonical_json_bytes(raw) + b"\n"
        if raw["summary"]["serialized_bytes"] == len(payload):
            return payload
        raw["summary"]["serialized_bytes"] = len(payload)
    payload = verifier.canonical_json_bytes(raw) + b"\n"
    if raw["summary"]["serialized_bytes"] != len(payload):
        raise AssertionError("mutated raw serialized-byte accounting did not stabilize")
    return payload


def mutate_coefficient(raw: dict[str, Any]) -> None:
    row = raw["targets"][0]
    row["coefficients"][0] = (row["coefficients"][0] + 1) % row["tensor"]["p"]
    rebind_targets(raw)


def mutate_core_with_rebound_digest(raw: dict[str, Any]) -> None:
    tensor = raw["targets"][0]["tensor"]
    tensor["cores"][0]["values"][0] = (
        tensor["cores"][0]["values"][0] + 1
    ) % tensor["p"]
    canonical = {
        "B": tensor["B"],
        "cores": tensor["cores"],
        "name": tensor["name"],
        "p": tensor["p"],
        "ranks": tensor["ranks"],
        "tag": tensor["tag"],
    }
    tensor["core_digest_sha256"] = verifier.artifact_digest(canonical)
    emit = next(
        event for event in raw["runtime"]["events"] if event["kind"] == "target_emit"
    )
    emit["core_digest_sha256"] = tensor["core_digest_sha256"]
    rebind_targets(raw)


def mutate_rank(raw: dict[str, Any]) -> None:
    raw["targets"][0]["tensor"]["ranks"][0] += 1
    rebind_targets(raw)


def mutate_source_receipt(raw: dict[str, Any]) -> None:
    raw["inputs"]["source_advice_receipt_sha256"] = "0" * 64


def mutate_factor_schedule(raw: dict[str, Any]) -> None:
    event = next(
        event for event in raw["runtime"]["events"] if event["kind"] == "rank_factor"
    )
    event["mode"] = 4


def mutate_factor_digest_format(raw: dict[str, Any]) -> None:
    event = next(
        event for event in raw["runtime"]["events"] if event["kind"] == "rank_factor"
    )
    event["factor_digest_sha256"] = "0" * 64


def mutate_operation_total(raw: dict[str, Any]) -> None:
    raw["runtime"]["operations"]["adds"] -= 1


def mutate_paired_operation_undercount(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "source_advice_import"
    )
    event["operation_vector"]["copied_words"] -= 1
    raw["runtime"]["operations"]["copied_words"] -= 1


def mutate_zero_accounting(raw: dict[str, Any]) -> None:
    for key in raw["runtime"]["operations"]:
        raw["runtime"]["operations"][key] = 0
    for bucket in raw["runtime"]["traffic"].values():
        bucket["reads"] = 0
        bucket["writes"] = 0
    raw["runtime"]["logical_traffic_words"] = 0
    for event in raw["runtime"]["events"]:
        if "operation_vector" not in event:
            continue
        for key in event["operation_vector"]:
            event["operation_vector"][key] = 0
        for bucket in event["traffic"].values():
            bucket["reads"] = 0
            bucket["writes"] = 0


def mutate_peak_liveness(raw: dict[str, Any]) -> None:
    raw["runtime"]["resources"]["peak_live_field_words"] = 0


def mutate_persistent_target_output(raw: dict[str, Any]) -> None:
    raw["runtime"]["resources"]["persistent_target_output_words"] = 0


def mutate_persistent_input(raw: dict[str, Any]) -> None:
    raw["runtime"]["resources"]["persistent_input_field_words"] = 0


def mutate_input_retention_event(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "target_input_retention"
    )
    event["field_words"] -= 1


def mutate_target_disposal(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "target_disposal"
    )
    event["persistent_target_output_words"] = 0


def mutate_coefficient_accounting(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "target_coefficient_formation"
    )
    event["operation_vector"]["muls"] -= 1
    raw["runtime"]["operations"]["muls"] -= 1


def mutate_output_serialization_passes(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "target_artifact_serialization"
        and event["variant"] == "output"
    )
    event["size_scan_passes"] = 1


def mutate_rss_record(raw: dict[str, Any]) -> None:
    rss = raw["runtime"]["resources"]["rss"]
    rss["bytes"] = 0
    rss["raw_ru_maxrss"] = 0


def mutate_factor_elimination_forgery(raw: dict[str, Any]) -> None:
    event = next(
        event
        for event in raw["runtime"]["events"]
        if event["kind"] == "rank_factor"
        and event["certificate"]["elimination_nonzero_count"] > 0
    )
    certificate = event["certificate"]
    eliminated = certificate["elimination_nonzero_count"]
    width = certificate["input_shape"][1]
    certificate["elimination_nonzero_count"] = 0
    old_hash_bytes = event["operation_vector"]["hash_bytes"]
    payload = verifier.canonical_json_bytes(certificate)
    event["factor_digest_sha256"] = verifier.sha256_bytes(payload)
    event["operation_vector"]["muls"] -= eliminated * width
    event["operation_vector"]["subs"] -= eliminated * width
    event["operation_vector"]["reductions"] -= 2 * eliminated * width
    event["operation_vector"]["hash_bytes"] = len(payload)
    event["traffic"]["elimination"]["reads"] -= 5 * eliminated * width
    event["traffic"]["elimination"]["writes"] -= 4 * eliminated * width
    raw["runtime"]["operations"]["muls"] -= eliminated * width
    raw["runtime"]["operations"]["subs"] -= eliminated * width
    raw["runtime"]["operations"]["reductions"] -= 2 * eliminated * width
    raw["runtime"]["operations"]["hash_bytes"] += len(payload) - old_hash_bytes
    raw["runtime"]["traffic"]["elimination"]["reads"] -= 5 * eliminated * width
    raw["runtime"]["traffic"]["elimination"]["writes"] -= 4 * eliminated * width
    raw["runtime"]["logical_traffic_words"] -= 9 * eliminated * width


def mutate_event_stream_order(raw: dict[str, Any]) -> None:
    raw["runtime"]["events"].sort(key=lambda event: event["kind"])


def mutate_target_order(raw: dict[str, Any]) -> None:
    raw["targets"][0], raw["targets"][1] = raw["targets"][1], raw["targets"][0]
    rebind_targets(raw)


def mutate_target_count(raw: dict[str, Any]) -> None:
    raw["targets"].pop()
    raw["summary"]["target_tensor_records"] = 24
    rebind_targets(raw)


def mutate_claim(raw: dict[str, Any]) -> None:
    raw["claim_boundary"]["breakthrough_claim"] = True


MUTATIONS: tuple[tuple[str, Mutation, str], ...] = (
    ("coefficient", mutate_coefficient, "changed coefficients"),
    (
        "core_with_rebound_digest",
        mutate_core_with_rebound_digest,
        "differs from numeric replay",
    ),
    ("rank", mutate_rank, "shape changed"),
    ("source_receipt", mutate_source_receipt, "does not bind source_advice_receipt_sha256"),
    ("factor_schedule", mutate_factor_schedule, "event stream changed"),
    ("factor_digest_format", mutate_factor_digest_format, "certificate digest mismatch"),
    (
        "operation_total",
        mutate_operation_total,
        "independently replayed ledgers do not reconcile",
    ),
    (
        "paired_operation_undercount",
        mutate_paired_operation_undercount,
        "operation vector does not match independent replay",
    ),
    (
        "zero_accounting",
        mutate_zero_accounting,
        "operation vector does not match independent replay",
    ),
    (
        "peak_liveness",
        mutate_peak_liveness,
        "resource peak_live_field_words does not match independent replay",
    ),
    (
        "persistent_target_output",
        mutate_persistent_target_output,
        "resource persistent_target_output_words does not match independent replay",
    ),
    (
        "persistent_input",
        mutate_persistent_input,
        "resource persistent_input_field_words does not match independent replay",
    ),
    (
        "input_retention_event",
        mutate_input_retention_event,
        "target runtime event stream changed",
    ),
    (
        "target_disposal",
        mutate_target_disposal,
        "target disposal event does not match retained output state",
    ),
    (
        "coefficient_accounting",
        mutate_coefficient_accounting,
        "operation vector does not match independent replay",
    ),
    (
        "output_serialization_passes",
        mutate_output_serialization_passes,
        "target-output serialization event changed",
    ),
    ("rss_record", mutate_rss_record, "runtime.resources.rss.bytes"),
    (
        "factor_elimination_forgery",
        mutate_factor_elimination_forgery,
        "certificate does not match shape replay",
    ),
    (
        "event_stream_order",
        mutate_event_stream_order,
        "target runtime event stream changed",
    ),
    ("target_order", mutate_target_order, "tensor name does not match"),
    ("target_count", mutate_target_count, "does not contain 25 target records"),
    ("unauthorized_claim", mutate_claim, "unauthorized claim"),
)


def verification_args(args: argparse.Namespace, raw_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        candidate_source_bundle=args.candidate_source_bundle,
        target_manifest=args.target_manifest,
        execution_matrix=args.execution_matrix,
        raw_result=raw_path,
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    raw_bytes = args.raw_result.read_bytes()
    raw = json.loads(raw_bytes)
    if raw_bytes != verifier.canonical_json_bytes(raw) + b"\n":
        raise ValueError("baseline target raw result is not canonical JSON")
    baseline = verifier.verify(verification_args(args, args.raw_result))
    controls: list[dict[str, Any]] = []
    temporary_root = args.temporary_root
    if temporary_root is not None:
        temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="tt-target-mutations-", dir=temporary_root
    ) as temporary:
        root = Path(temporary)
        for mutation_id, mutation, expected_fragment in MUTATIONS:
            candidate = copy.deepcopy(raw)
            mutation(candidate)
            candidate_path = root / f"{mutation_id}.json"
            candidate_bytes = canonical_raw_bytes(candidate)
            candidate_path.write_bytes(candidate_bytes)
            try:
                verifier.verify(verification_args(args, candidate_path))
            except Exception as error:
                message = str(error)
                if expected_fragment not in message:
                    raise AssertionError(
                        f"mutation {mutation_id} failed for the wrong reason: {message}"
                    ) from error
                controls.append(
                    {
                        "error_message": message,
                        "error_type": type(error).__name__,
                        "mutation_id": mutation_id,
                        "mutated_raw_sha256": verifier.sha256_bytes(candidate_bytes),
                        "status": "rejected",
                    }
                )
            else:
                raise AssertionError(f"mutation {mutation_id} was accepted")
    return {
        "artifact_freeze_authorized": False,
        "baseline": {
            "raw_result_sha256": verifier.sha256_bytes(raw_bytes),
            "target_tensor_records": baseline["summary"]["target_tensor_records"],
            "valid": baseline["valid"],
        },
        "boundary": (
            "Development-only synthetic verifier mutations. Rejection demonstrates "
            "fail-closed implementation behavior only; it is not cryptanalytic evidence."
        ),
        "controls": controls,
        "protocol": verifier.PROTOCOL,
        "schema": "tt-target-development-mutation-report-v1",
        "summary": {
            "accepted_mutations": 0,
            "rejected_mutations": len(controls),
            "scheduled_mutations": len(MUTATIONS),
        },
        "valid": len(controls) == len(MUTATIONS),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--candidate-source-bundle", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-matrix", type=Path, required=True)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--temporary-root", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = run(parse_args(argv))
    except Exception as error:
        failure = {
            "artifact_freeze_authorized": False,
            "error": {"message": str(error), "type": type(error).__name__},
            "schema": "tt-target-development-mutation-failure-v1",
            "valid": False,
        }
        sys.stdout.buffer.write(verifier.canonical_json_bytes(failure) + b"\n")
        return 1
    sys.stdout.buffer.write(verifier.canonical_json_bytes(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

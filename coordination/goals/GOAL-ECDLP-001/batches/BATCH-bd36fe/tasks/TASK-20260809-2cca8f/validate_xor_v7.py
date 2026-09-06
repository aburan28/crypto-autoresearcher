#!/usr/bin/env python3
"""Fail-closed v7 control validator for the synthetic EXP-XOR package.

The v7 validator first runs the immutable v6 fixture-only validator, then
checks the five residual v6 review findings against in-memory copies. It never
executes an ECDLP implementation and never writes repository artifacts.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

sys.dont_write_bytecode = True


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_schema(schema: Any, data: Any, label: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        fail(f"{label}: schema error at {list(errors[0].path)}: {errors[0].message}")


def load_v6(v6_root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("xor_validator_v6", v6_root / "validate_xor_v6.py")
    if spec is None or spec.loader is None:
        fail("cannot load immutable v6 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_v6_exact(v6: Any, v6_root: Path, repo_root: Path) -> None:
    command = [
        sys.executable,
        str(v6_root / "validate_xor_v6.py"),
        "--run-schema", str(v6_root / "run_manifest_xor_v6.schema.json"),
        "--matrix-schema", str(v6_root / "matrix_summary_xor_v6.schema.json"),
        "--event-schema", str(v6_root / "event_ledger_xor_v6.schema.json"),
        "--fixtures", str(v6_root / "fixtures/fixture_manifest_xor_v6.json"),
        "--contract", str(v6_root / "validation_contract_xor_v6.json"),
        "--arithmetic", str(v6_root / "arithmetic_fixture_xor_v6.json"),
        "--predecessor", str(v6_root / "predecessor_exclusion_xor_v6.json"),
        "--repo-root", str(repo_root),
    ]
    result = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode != 0 or result.stdout.strip() != "VALIDATION_PASS":
        fail(f"immutable v6 predecessor validator failed: exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}")


def strict_arithmetic(data: dict[str, Any], v6: Any, contract: dict[str, Any]) -> None:
    rule = contract["arithmetic_strict_contract"]
    if data["input_digest_domain"] != rule["input_digest_domain"]:
        fail("arithmetic input digest domain is not authoritative")
    p = data["input"]["p"]
    b_num = data["input"]["b_num"]
    b_den = data["input"]["b_den"]
    integer_search = data["factor_base"]["integer_search"]
    if integer_search["lower"] != rule["integer_search_lower"]:
        fail("integer-search lower bound is not authoritative")
    selected = max(i for i in range(p + 1) if i ** b_den <= p ** b_num)
    if integer_search["upper_exclusive"] != rule["integer_search_upper_exclusive"] or integer_search["selected"] != selected or data["factor_base"]["B"] != selected:
        fail("integer-search metadata is not bound to the canonical control contract")
    curve = data["curve"]
    A, B = curve["A"], curve["B"]
    expected_point: tuple[int, int] | None = None
    for x in range(p):
        for y in range(p):
            if (y * y - (x ** 3 + A * x + B)) % p != 0:
                continue
            q: tuple[int, int] | None = None
            for order in range(1, 20):
                q = v6.ec_add(q, (x, y), p, A)
                if q is None:
                    break
            if order == 6:
                expected_point = (x, y)
                break
        if expected_point is not None:
            break
    point_data = curve["first_eligible_point"]
    actual_point = (point_data["x"], point_data["y"])
    if expected_point is None or actual_point != expected_point:
        fail("first eligible order-6 point is not derived lexicographically")
    lift = data["lift_x"]
    rhs = (lift["x"] ** 3 + A * lift["x"] + B) % p
    roots = [y for y in range(p) if (y * y) % p == rhs]
    if lift["x"] != actual_point[0] or lift["roots"] != roots or lift["selected_smallest_y"] != min(roots) or lift["selected_smallest_y"] != actual_point[1]:
        fail("lift root is not bound to the selected point")
    output = data["output"]
    if output["F"] != rule["output_F"] or output["R_star_count"] != rule["output_R_star_count"]:
        fail("canonical output metrics are not bound to the synthetic control contract")


def strict_event(data: dict[str, Any], v6: Any, event_schema: dict[str, Any], expected_run_id: str) -> None:
    events = data["events"]
    if not events:
        fail("event stream is empty")
    phase_order = list(v6.PHASES)
    indices = [phase_order.index(event["phase"]) for event in events]
    if indices != sorted(indices) or set(indices) != set(range(len(phase_order))):
        fail("event phase stream is not nonempty, ordered, and complete")
    first_occurrences = []
    for phase in phase_order:
        first_occurrences.append(indices.index(phase_order.index(phase)))
    if first_occurrences != sorted(first_occurrences):
        fail("event phase first-occurrence order failed")
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
    v6.validate_event(data, event_schema, expected_run_id, hashlib.sha256(raw).hexdigest(), raw)


def strict_cases(v6_root: Path, case_schema: dict[str, Any], contract: dict[str, Any], v6_contract: dict[str, Any], fixture_root: Path) -> None:
    accepted = {entry["id"]: entry for entry in v6_contract["accepted_cases"]}
    expected_ids = contract["case_authority"]["accepted_case_files"]
    if [entry.get("path", f"{entry['id']}.json") for entry in v6_contract["accepted_cases"]] != expected_ids:
        fail("v6 accepted-case order is not bound")
    for case_id in expected_ids:
        case = read_json(fixture_root / case_id)
        check_schema(case_schema, case, f"accepted case {case_id}")
        spec = accepted[case["fixture_id"]]
        if case["kind"] != spec["kind"] or case["expected"] != spec["expected"]:
            fail(f"accepted case {case_id} does not equal its contract")
        if case["kind"] == "run" and case["patch"] != spec["patch"]:
            fail(f"accepted run case {case_id} patch is not authoritative")
        if case["kind"] == "matrix_arm":
            interval = case["timing_interval"]
            if case["terminal_reason"] is None or interval["stop_ns"] <= interval["start_ns"] or not case["rss_samples"]:
                fail("unattempted matrix-arm case contains malformed retained fields")


def strict_manifest(manifest: dict[str, Any], contract: dict[str, Any], v6_contract: dict[str, Any]) -> None:
    if manifest["schema"] != "xor-fixture-manifest/v7" or manifest["validator_version"] != contract["case_authority"]["manifest_validator_version"]:
        fail("v7 fixture manifest version is not authoritative")
    expected_cases = contract["case_authority"]["accepted_case_files"]
    if manifest["v6_accepted_case_files"] != expected_cases or manifest["v6_negative_mutation_count"] != len(v6_contract["negative_mutations"]):
        fail("v7 manifest does not bind the complete v6 control suite")
    if manifest["strict_mutation_ids"] != [item["id"] for item in contract["strict_negative_mutations"]] or not manifest["all_cases_are_applied"] or not manifest["all_negative_cases_must_fail"] or not manifest["fixture_only"] or not manifest["no_experiment_execution"]:
        fail("v7 manifest authority or no-run boundary failed")


def strict_matrix(matrix: dict[str, Any], v6: Any, contract: dict[str, Any], index: dict[str, Any], bindings: dict[str, Any], metadata: dict[str, Any], repo_root: Path) -> None:
    if index["arm_count"] != 400 or index["run_id_rule"] != contract["matrix_binding"]["run_id_rule"] or index["synthetic_fixture_index"] is not True:
        fail("per-arm run index contract is incomplete")
    if hashlib.sha256((repo_root / bindings["source_matrix"]).read_bytes()).hexdigest() != bindings["source_matrix_sha256"]:
        fail("canonical matrix source hash does not match source binding")
    for key, binding in bindings["source_blobs"].items():
        if matrix["source_blobs"].get(key) != binding["fixture_value"]:
            fail(f"matrix source blob token is not bound: {key}")
        if hashlib.sha256((repo_root / binding["path"]).read_bytes()).hexdigest() != binding["sha256"]:
            fail(f"matrix source binding hash mismatch: {key}")
    wanted = v6.expected_keys()
    if len(matrix["arms"]) != index["arm_count"]:
        fail("matrix arm count is not bound to run index")
    for ordinal, arm in enumerate(matrix["arms"], 1):
        expected_id = f"RUN-XOR-{ordinal:06d}"
        if arm["run_id"] != expected_id:
            fail("matrix arm run_id is not bound to canonical per-arm index")
        if arm["arm_key"] != wanted[ordinal - 1]:
            fail("matrix arm key is not bound to the indexed arm")
        digest = hashlib.sha256(json.dumps(arm["arm_key"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if index["key_digest"] != "SHA256(compact_sorted_json(arm_key))" or not digest:
            fail("matrix arm key digest rule is not applied")
    if metadata["schema"] != "matrix-validator-metadata/xor-v7" or metadata["validator_version"] != "xor-validator/v7" or metadata["legacy_command_is_not_authoritative"] is not True:
        fail("v7 validator metadata is not authoritative")
    if "--control-fixtures" in metadata["corrected_command"] or "--control-fixtures" not in metadata["legacy_embedded_command"] or metadata["command_scope"] != "fixture_only_no_run_or_matrix_argument":
        fail("stale validator command was not replaced by corrected metadata")


def expect_reject(name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
    except (ValueError, KeyError, TypeError, AssertionError, json.JSONDecodeError):
        return
    fail(f"strict mutation unexpectedly passed: {name}")


def strict_mutations(v6: Any, v6_root: Path, contract: dict[str, Any], case_schema: dict[str, Any], canonical_arithmetic: dict[str, Any], canonical_event: dict[str, Any], canonical_matrix: dict[str, Any], event_schema: dict[str, Any], v6_contract: dict[str, Any], fixture_root: Path, index: dict[str, Any], bindings: dict[str, Any], metadata: dict[str, Any], repo_root: Path) -> None:
    declared = [item["id"] for item in contract["strict_negative_mutations"]]
    seen: list[str] = []
    def probe(name: str, fn: Callable[[], None]) -> None:
        seen.append(name)
        expect_reject(name, fn)
    probe("arithmetic_domain_metadata", lambda: strict_arithmetic({**canonical_arithmetic, "input_digest_domain": "forged"}, v6, contract))
    def bad_integer_search() -> None:
        x = copy.deepcopy(canonical_arithmetic); x["factor_base"]["integer_search"]["upper_exclusive"] += 1; strict_arithmetic(x, v6, contract)
    probe("arithmetic_integer_search_metadata", bad_integer_search)
    def bad_point() -> None:
        x = copy.deepcopy(canonical_arithmetic); x["curve"]["first_eligible_point"]["y"] = 98; strict_arithmetic(x, v6, contract)
    probe("arithmetic_nonfirst_order6_point", bad_point)
    def bad_lift() -> None:
        x = copy.deepcopy(canonical_arithmetic); x["lift_x"]["selected_smallest_y"] = 98; strict_arithmetic(x, v6, contract)
    probe("arithmetic_lift_selected_y", bad_lift)
    def bad_f() -> None:
        x = copy.deepcopy(canonical_arithmetic); x["output"]["F"] = 999; strict_arithmetic(x, v6, contract)
    probe("arithmetic_output_F", bad_f)
    def empty_event() -> None:
        x = copy.deepcopy(canonical_event); x["events"] = []; strict_event(x, v6, event_schema, "RUN-XOR-000001")
    probe("event_empty", empty_event)
    def collapsed_event() -> None:
        x = copy.deepcopy(canonical_event)
        for event in x["events"]:
            event["phase"] = "input"
        strict_event(x, v6, event_schema, "RUN-XOR-000001")
    probe("event_phase_collapse", collapsed_event)
    def bad_case_schema() -> None:
        x = read_json(fixture_root / "completed_invalid.json"); x["schema"] = "forged"; check_schema(case_schema, x, "mutated case")
    probe("accepted_case_schema", bad_case_schema)
    def bad_unattempted() -> None:
        x = read_json(fixture_root / "unattempted_matrix_arm.json"); x["terminal_reason"] = None; x["timing_interval"]["stop_ns"] = 0; x["rss_samples"] = []; check_schema(case_schema, x, "mutated arm case")
    probe("unattempted_case_fields", bad_unattempted)
    def bad_run_binding() -> None:
        x = copy.deepcopy(canonical_matrix); x["arms"][0]["run_id"] = "RUN-XOR-unbound"; strict_matrix(x, v6, contract, index, bindings, metadata, repo_root)
    probe("matrix_run_binding", bad_run_binding)
    def bad_source_binding() -> None:
        x = copy.deepcopy(canonical_matrix); x["source_blobs"] = {key: "0" * 64 for key in x["source_blobs"]}; strict_matrix(x, v6, contract, index, bindings, metadata, repo_root)
    probe("matrix_source_binding", bad_source_binding)
    def bad_command() -> None:
        x = copy.deepcopy(metadata); x["corrected_command"] = x["legacy_embedded_command"]; strict_matrix(canonical_matrix, v6, contract, index, bindings, x, repo_root)
    probe("stale_validator_command", bad_command)
    if seen != declared:
        fail(f"strict mutation declaration mismatch: seen={seen}, declared={declared}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v6-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--case-schema", required=True, type=Path)
    parser.add_argument("--run-index", required=True, type=Path)
    parser.add_argument("--source-bindings", required=True, type=Path)
    parser.add_argument("--validator-metadata", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    v6_root = args.v6_root.resolve()
    contract = read_json(args.contract)
    manifest = read_json(args.manifest)
    case_schema = read_json(args.case_schema)
    index = read_json(args.run_index)
    bindings = read_json(args.source_bindings)
    metadata = read_json(args.validator_metadata)
    v6 = load_v6(v6_root)
    v6_contract = read_json(v6_root / "validation_contract_xor_v6.json")
    fixture_root = v6_root / "fixtures"
    run_v6_exact(v6, v6_root, repo_root)
    strict_manifest(manifest, contract, v6_contract)
    for case_id in contract["case_authority"]["accepted_case_files"]:
        if not (fixture_root / case_id).is_file():
            fail(f"accepted case file missing: {case_id}")
    strict_cases(v6_root, case_schema, contract, v6_contract, fixture_root)
    arithmetic = read_json(v6_root / "arithmetic_fixture_xor_v6.json")
    event = read_json(fixture_root / "canonical_event_ledger.json")
    matrix = read_json(fixture_root / "canonical_matrix.json")
    event_schema = read_json(v6_root / "event_ledger_xor_v6.schema.json")
    strict_arithmetic(arithmetic, v6, contract)
    strict_event(event, v6, event_schema, "RUN-XOR-000001")
    strict_matrix(matrix, v6, contract, index, bindings, metadata, repo_root)
    strict_mutations(v6, v6_root, contract, case_schema, arithmetic, event, matrix, event_schema, v6_contract, fixture_root, index, bindings, metadata, repo_root)
    print("VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

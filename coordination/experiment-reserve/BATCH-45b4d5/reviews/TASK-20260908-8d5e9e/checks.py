#!/usr/bin/env python3
"""Independent fixed checks for Validator TASK-20260908-8d5e9e.

This checker performs administrative source/runtime hash comparisons and twenty
fixed static, arithmetic, synthetic, or mock cases.  It never enumerates a
frozen interval, constructs a protocol fixture, runs a scientific control or
timing panel, creates a real launch payload/signature/lock/nonce, allocates a
RUN identifier, or accesses the private signing key.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable
from unittest import mock

import yaml


TASK_ID = "TASK-20260908-8d5e9e"
AUTHORITY_COMMIT = "6182e1dbc532512db1c78306d14f4cde42769b03"
CLAIM_COMMIT = "a91c3fdbaab6c67411e154ef389453ab467c3210"
SOURCE_SNAPSHOT = "0094bf3395a72c4c0e376945be8907c99ecde70a"
HANDOFF_PATH = "ledger/handoffs/TASK-20260908-8d5e9e.yaml"
PLAN_PATH = "coordination/experiment-reserve/BATCH-45b4d5/review-plan-TASK-20260908-8d5e9e.yaml"
SNAPSHOT_RECEIPT_PATH = "coordination/experiment-reserve/BATCH-45b4d5/archives/TASK-20260908-163823/snapshot.json"
CLAIM_PATH = "coordination/experiment-reserve/BATCH-45b4d5/claims/TASK-20260908-8d5e9e.1.claim.json"
IMPLEMENTATION_DIR = "experiments/EXP-ECDLP-1b1b99/implementation/TASK-20260908-35abb7"
DRIVER_PATH = f"{IMPLEMENTATION_DIR}/driver.py"
EXPECTED_SNAPSHOT_PATHS = {
    SNAPSHOT_RECEIPT_PATH,
    f"{IMPLEMENTATION_DIR}/driver.py",
    f"{IMPLEMENTATION_DIR}/tests.py",
    f"{IMPLEMENTATION_DIR}/README.md",
    f"{IMPLEMENTATION_DIR}/implementation-report.yaml",
    f"{IMPLEMENTATION_DIR}/execution-plan.json",
    f"{IMPLEMENTATION_DIR}/mathematical-implementation.md",
    f"{IMPLEMENTATION_DIR}/regression-receipt.json",
}
REPO = Path(__file__).resolve().parents[5]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout


def load_driver() -> Any:
    path = REPO / DRIVER_PATH
    spec = importlib.util.spec_from_file_location("cm_bound_driver_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load bound driver")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DRIVER = load_driver()


def administrative_checks() -> dict[str, Any]:
    handoff_bytes = git_bytes(AUTHORITY_COMMIT, HANDOFF_PATH)
    handoff = yaml.safe_load(handoff_bytes)["handoff"]
    plan_bytes = git_bytes(AUTHORITY_COMMIT, PLAN_PATH)
    source_results = []
    for binding in handoff["source_bindings"]:
        relative = binding["path"]
        expected = binding["sha256"]
        authority = git_bytes(AUTHORITY_COMMIT, relative)
        current = (REPO / relative).read_bytes()
        source_results.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "authority_sha256": sha256(authority),
                "current_sha256": sha256(current),
                "authority_match": sha256(authority) == expected,
                "current_match": sha256(current) == expected,
            }
        )

    receipt = json.loads((REPO / SNAPSHOT_RECEIPT_PATH).read_text())
    snapshot_results = []
    for relative, expected in receipt["source_path_sha256"].items():
        snapshot_digest = sha256(git_bytes(SOURCE_SNAPSHOT, relative))
        snapshot_results.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "snapshot_sha256": snapshot_digest,
                "match": snapshot_digest == expected,
            }
        )
    changed = set(
        line.strip()
        for line in git_text(
            "diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT
        ).splitlines()
        if line.strip()
    )
    source_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT],
        cwd=REPO,
        check=False,
    ).returncode == 0

    claim = json.loads(git_bytes(CLAIM_COMMIT, CLAIM_PATH))
    claim_ok = (
        claim.get("task_id") == TASK_ID
        and claim.get("epoch") == 1
        and claim.get("write_scope") == handoff["write_scope"]
    )

    runtime_binding_path = handoff["external_runtime_dependencies"]["binding_path"]
    runtime_binding = json.loads((REPO / runtime_binding_path).read_text())
    allowed = set(handoff["external_runtime_dependencies"]["permitted_readonly_paths"])
    runtime_results = []
    for item in runtime_binding["runtime"]["file_bindings"]:
        path = Path(item["path"])
        data = path.read_bytes()
        runtime_results.append(
            {
                "path": str(path),
                "authorized_path": str(path) in allowed,
                "expected_sha256": item["sha256"],
                "observed_sha256": sha256(data),
                "expected_bytes": item["bytes"],
                "observed_bytes": len(data),
                "resolved_path": str(path.resolve()),
                "expected_resolved_path": item["resolved_path"],
                "match": (
                    str(path) in allowed
                    and sha256(data) == item["sha256"]
                    and len(data) == item["bytes"]
                    and str(path.resolve()) == item["resolved_path"]
                ),
            }
        )

    return {
        "authority_commit": AUTHORITY_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "source_snapshot": SOURCE_SNAPSHOT,
        "handoff_authority_sha256": sha256(handoff_bytes),
        "handoff_current_sha256": sha256((REPO / HANDOFF_PATH).read_bytes()),
        "handoff_current_matches_authority": (REPO / HANDOFF_PATH).read_bytes() == handoff_bytes,
        "plan_authority_sha256": sha256(plan_bytes),
        "plan_expected_sha256": next(
            item["sha256"] for item in handoff["source_bindings"] if item["path"] == PLAN_PATH
        ),
        "plan_current_matches_authority": (REPO / PLAN_PATH).read_bytes() == plan_bytes,
        "repository_source_binding_count": len(source_results),
        "repository_source_bindings_all_match": all(
            item["authority_match"] and item["current_match"] for item in source_results
        ),
        "repository_source_observations_sha256": sha256(
            json.dumps(source_results, sort_keys=True, separators=(",", ":")).encode()
        ),
        "snapshot_parent_expected": receipt["parent_sha"],
        "snapshot_parent_observed": git_text("rev-parse", f"{SOURCE_SNAPSHOT}^").strip(),
        "snapshot_changed_paths": sorted(changed),
        "snapshot_changed_paths_exact": changed == EXPECTED_SNAPSHOT_PATHS,
        "snapshot_source_hash_count": len(snapshot_results),
        "snapshot_source_hashes_all_match": all(item["match"] for item in snapshot_results),
        "snapshot_source_observations_sha256": sha256(
            json.dumps(snapshot_results, sort_keys=True, separators=(",", ":")).encode()
        ),
        "snapshot_is_ancestor_of_authority": source_ancestor,
        "claim_epoch_one_matches_scope": claim_ok,
        "runtime_file_binding_count": len(runtime_results),
        "runtime_file_bindings_all_match": all(item["match"] for item in runtime_results),
        "runtime_file_observations_sha256": sha256(
            json.dumps(runtime_results, sort_keys=True, separators=(",", ":")).encode()
        ),
        "private_signing_key_accessed": False,
    }


def make_selection_rows() -> list[Any]:
    rows = []
    for interval in range(3):
        for fixture in range(2):
            for kernel in range(4):
                for coordinate in (1, 2, 3):
                    for arm in DRIVER.SCALAR_ARMS:
                        for block in range(7):
                            cpu = 1 if arm == 2 else 2 if arm == 3 else 20 + arm
                            rows.append(
                                DRIVER.BlockCost(
                                    f"I{interval}F{fixture}", f"K{kernel}", f"C{kernel // 2}",
                                    coordinate, 606101, 256, arm, block, 1,
                                    "scalar_multiplication", "selection", cpu, cpu, 1, False,
                                )
                            )
    return rows


def valid_payload(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    value = {
        "domain": "crypto-autoresearcher.launch.v1",
        "experiment_id": DRIVER.EXPERIMENT_ID,
        "effective_contract_sha256": DRIVER.EFFECTIVE_CONTRACT_SHA256,
        "predecessor_specification_sha256": DRIVER.SPECIFICATION_SHA256,
        "amendment_sha256": DRIVER.AMENDMENT_SHA256,
        "decision_id": DRIVER.DECISION_ID,
        "handoff_id": DRIVER.TASK_ID,
        "review_archive_commit": "f" * 40,
        "implementation_archive_commit": "e" * 40,
        "implementation_tree_or_path_hash": "d" * 64,
        "runner_sha256": DRIVER.sha256_file(Path(DRIVER.__file__)),
        "execution_plan_sha256": DRIVER.sha256_file(Path(DRIVER.__file__).with_name("execution-plan.json")),
        "trusted_verifier_sha256": DRIVER.OPENSSL_SHA256,
        "executor_role": "executor",
        "handoff_sha256": "c" * 64,
        "runtime_binding_sha256": DRIVER.RUNTIME_BINDING_SHA256,
        "provider": "local",
        "model": "fixed-mock-model",
        "run_id": "FUTURE-UNIT",
        "output_path": "runs/FUTURE-UNIT",
        "fixed_protocol": {"sentinel": "unchecked"},
        "resource_policy": {"sentinel": "unchecked"},
        "replay_reference_sha256": "b" * 64,
        "public_private_schema_sha256": "a" * 64,
        "nonce": "1" * 64,
    }
    if overrides:
        value.update(overrides)
    return value


def expect_raises(exc: type[BaseException], fn: Callable[[], Any]) -> None:
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def case_01_canonical_payload() -> dict[str, Any]:
    assert DRIVER.canonical_json({"b": 2, "a": 1}) == b'{"a":1,"b":2}\n'
    expect_raises(ValueError, lambda: DRIVER.canonical_json({"a": 1.0}))
    expect_raises(ValueError, lambda: DRIVER.strict_json(b'{"a":1,"a":2}\n'))
    expect_raises(ValueError, lambda: DRIVER.strict_json(b'{"a":1}'))
    return {"joint_result": "holds", "detail": "canonical/duplicate/float/newline rules reject as required"}


def case_02_dry_cli_and_real_pinned_scalar() -> dict[str, Any]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert DRIVER.main([]) == 0
    parsed = json.loads(output.getvalue())
    assert parsed["status"] == "dry_run_not_launched"
    curve = DRIVER.Curve(7, 0, 2)
    point = next(item for item in curve.points() if item is not None)
    outputs = DRIVER.scalar_arms(curve, 11, point)
    assert len(set(outputs.values())) == 1 and set(outputs) == set(DRIVER.SCALAR_ARMS)
    return {"joint_result": "holds", "detail": "CLI inert; fixed F7 scalar agrees across local arms and pinned PARI ellmul"}


def case_03_public_evaluator_private_argument() -> dict[str, Any]:
    signature = inspect.signature(DRIVER.evaluate_public_batch)
    source = inspect.getsource(DRIVER.evaluate_public_batch)
    assert "private" in signature.parameters and "private.expected_points" in source
    return {"joint_result": "breaks", "detail": "timed evaluator API receives PrivateVerifierBatch and reads expected_points"}


def case_04_public_schema_semantics_unchecked() -> dict[str, Any]:
    malformed = DRIVER.PublicEvaluatorBatch(
        "opaque", (7, 0, 2), (7, 0, 2), 3, 2, "phi", "psi", ("rho_1",), (), -1
    ).wire()
    DRIVER.validate_public_batch(malformed)
    return {"joint_result": "breaks", "detail": "closed top-level field set accepts q=-1 with zero query points"}


def case_05_authorized_pipeline_fails_first_stage() -> dict[str, Any]:
    authorization = DRIVER.AuthCheck(True, "AUTH_OK", "fixed mock", {"run_id": "FUTURE-UNIT"})
    with tempfile.TemporaryDirectory() as name:
        base = Path(name)
        with mock.patch.object(DRIVER, "verify_future_authorization", return_value=authorization):
            result = DRIVER.run_authorized(base / "payload", base / "signature", base / "nonce", base / "runs")
        assert result["status"] == "infrastructure_stopped"
        progress = (Path(result["partial_path"]) / "progress.jsonl").read_text()
        assert "canonical payload has unsupported value" in progress
    return {"joint_result": "breaks", "detail": "accepted AuthCheck is not json_ready; first stage receipt fails before fixture work"}


def case_06_signed_but_unbound_fields_accepted() -> dict[str, Any]:
    payload = valid_payload()
    unchecked = {
        "review_archive_commit", "implementation_archive_commit", "implementation_tree_or_path_hash",
        "handoff_sha256", "fixed_protocol", "resource_policy", "replay_reference_sha256",
        "public_private_schema_sha256",
    }
    with tempfile.TemporaryDirectory() as name:
        base = Path(name)
        payload_path = base / "payload"
        payload_path.write_bytes(DRIVER.canonical_json(payload))
        (base / "signature").write_bytes(b"fixed mock signature")
        with (
            mock.patch.object(DRIVER, "fixed_runtime_source_checks"),
            mock.patch.object(DRIVER, "verify_pinned_runtime", return_value={}),
            mock.patch.object(DRIVER.subprocess, "run", return_value=SimpleNamespace(returncode=0)),
            mock.patch.object(DRIVER, "claim_nonce", return_value=DRIVER.AuthCheck(True, "AUTH_OK", "mock")),
        ):
            result = DRIVER.verify_future_authorization(payload_path, base / "signature", base / "nonce")
    assert result.accepted
    source = inspect.getsource(DRIVER.verify_future_authorization)
    checked_mapping = source.split("bindings =", 1)[1].split("if any", 1)[0]
    assert all(field not in checked_mapping for field in unchecked)
    return {"joint_result": "breaks", "detail": "valid-signature mock accepts arbitrary review/archive/tree/handoff/protocol/resource/replay/schema bindings"}


def case_07_bedrock_and_path_refusals() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as name:
        base = Path(name)
        first = base / "bedrock"
        first.write_bytes(DRIVER.canonical_json(valid_payload({"provider": "Amazon Bedrock"})))
        denied = DRIVER.verify_future_authorization(first, base / "missing", base / "nonce")
        assert denied.code == "AUTH_RUNTIME_MISMATCH" and not denied.accepted
        second = base / "path"
        second.write_bytes(DRIVER.canonical_json(valid_payload({"output_path": "runs/OTHER"})))
        denied = DRIVER.verify_future_authorization(second, base / "missing", base / "nonce")
        assert denied.code == "AUTH_RUN_PATH_MISMATCH" and not denied.accepted
    return {"joint_result": "holds", "detail": "Bedrock and mismatched signed path are typed pre-runtime refusals"}


def case_08_nonce_replay() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as name:
        registry = Path(name) / "nonce"
        nonce = "2" * 64
        assert DRIVER.claim_nonce(registry, nonce, "FUTURE-UNIT", "3" * 64).accepted
        assert DRIVER.claim_nonce(registry, nonce, "FUTURE-UNIT", "3" * 64).code == "AUTH_NONCE_REPLAY"
    return {"joint_result": "holds", "detail": "fixed mock nonce is exclusive-created and replay refused"}


def case_09_selection_complete_and_missing() -> dict[str, Any]:
    rows = make_selection_rows()
    winners = DRIVER.select_baselines(rows)
    assert len(rows) == 3024 and len(winners) == 9 and set(winners.values()) == {2}
    expect_raises(DRIVER.InvalidMeasurement, lambda: DRIVER.select_baselines(rows[:-1]))
    return {"joint_result": "holds", "detail": "exact fixed 3024-row selection accepted and one missing cell rejected"}


def case_10_duplicate_selection_bias() -> dict[str, Any]:
    rows = make_selection_rows()
    before = DRIVER.select_baselines(rows)[("I0", 1)]
    duplicate = next(row for row in rows if row.fixture == "I0F0" and row.kernel == "K0" and row.coordinate == 1 and row.arm == 2 and row.block == 0)
    altered = DRIVER.BlockCost(**{**duplicate.__dict__, "cpu_ns": 1000, "wall_ns": 1000})
    after = DRIVER.select_baselines([*rows, altered])[("I0", 1)]
    assert before == 2 and after == 3
    return {"joint_result": "breaks", "detail": "extra duplicate index is accepted and changes frozen winner from arm2 to arm3"}


def case_11_boolean_only_hard_reducer() -> dict[str, Any]:
    receipts = [{"stage_id": stage, "status": "completed"} for stage in DRIVER.STAGES]
    coverage = {key: True for key in (
        "authorization_and_nonce_valid", "six_fixtures_valid", "four_labels_two_classes_valid",
        "exact_maps_and_conjugations_valid", "all_controls_true", "nine_freezes_valid",
        "main_rows_28224", "top_rows_2016", "identity_rows_2016", "all_blocks_typed",
        "replay_valid", "resource_custody_valid",
    )}
    assert DRIVER.hard_validity_reduce(receipts, coverage, {"synthetic": True}, True, True) == "completed_valid"
    return {"joint_result": "breaks", "detail": "hard reducer accepts asserted booleans without rows, replay artifacts, hashes, or parsed companions"}


def case_12_x_value_cap_counts_points() -> dict[str, Any]:
    points = tuple((index // 2, index % 2) for index in range(4097))
    wanted = points[-1]

    class FakeCurve:
        def affine_points(self) -> Any:
            return iter(points)

        def mul(self, scalar: int, point: Any) -> Any:
            if scalar == 1:
                return wanted if point == wanted else None
            return None

    expect_raises(DRIVER.InvalidMeasurement, lambda: DRIVER.first_generator(FakeCurve(), 127, 127))
    assert len({point[0] for point in points}) == 2049
    return {"joint_result": "breaks", "detail": "4096 affine-point cutoff rejects while only 2049 x values were examined; attempts are not returned"}


def case_13_certificate_schema_incomplete() -> dict[str, Any]:
    fields = set(DRIVER.ConductorCertificate.__dataclass_fields__)
    required_missing = {"r", "factorization", "primality_certificate", "exact_duals", "edge_counts", "within_pair_isomorphisms", "lambda", "m"}
    assert fields.isdisjoint(required_missing)
    return {"joint_result": "breaks", "detail": "fixture certificate type cannot carry multiple mandatory cross-field and map/class certificates"}


def case_14_cost_reduction_omits_charges_and_median() -> dict[str, Any]:
    source = inspect.getsource(DRIVER.reduce_future_rows)
    assert 'all_rows = [*selection["rows"], *main, *top, *identity]' in source
    assert "median" not in source and "leave" not in source
    assert "primary_ratios" in source and "allocation_ledger" not in source.split("ratios: dict", 1)[1].split("coverage =", 1)[0]
    assert 'scalar = sum(row.cpu_ns/max(1,row.repetition) for row in primary' in source
    return {"joint_result": "breaks", "detail": "primary ratio has no setup/discovery allocation, median-of-seven, leave-one-out stability, q-star, or decision branch"}


def case_15_selection_score_omits_warmup() -> dict[str, Any]:
    source = inspect.getsource(DRIVER.run_selection_matrix)
    assert 'selection_rows = [row for row in rows if row.component == "scalar_multiplication"]' in source
    return {"joint_result": "breaks", "detail": "baseline score drops scalar_warmup rows and has no explicit table/library setup rows"}


def case_16_label_permutation_is_not_join_control() -> dict[str, Any]:
    source = inspect.getsource(DRIVER.run_controls)
    assert 'fisher_yates(["K0", "K1", "K2", "K3"]' in source
    assert "reaggregate" not in source and "opaque_join" not in source
    return {"joint_result": "breaks", "detail": "control merely checks sorted label list; it never permutes private join or reaggregates raw costs"}


def case_17_query_transport_and_repetition_flag_missing() -> dict[str, Any]:
    private_source = inspect.getsource(DRIVER.private_batch)
    matrix_source = inspect.getsource(DRIVER.run_timing_matrix)
    public_fields = set(DRIVER.PublicEvaluatorBatch.__dataclass_fields__)
    assert 'state.draw("query", _parameters(fixture)' in private_source
    assert "for coordinate in (1, 2, 3)" in matrix_source and "private_batch(" in matrix_source
    assert "repetition_flag" not in public_fields
    return {"joint_result": "breaks", "detail": "each coordinate redraws from a persistent shared stream instead of transporting one base sample; repetition flag absent"}


def case_18_resource_enforcement_and_inner_cancel_missing() -> dict[str, Any]:
    module_source = inspect.getsource(DRIVER)
    evaluator_source = inspect.getsource(DRIVER.evaluate_public_batch)
    runner_source = inspect.getsource(DRIVER.run_authorized)
    assert "resource.setrlimit" not in module_source
    assert "cancel" not in inspect.signature(DRIVER.evaluate_public_batch).parameters
    assert "terminate_child_group(" not in runner_source and "maximum_workers" not in runner_source
    assert "tuple(operation(point)" in evaluator_source
    return {"joint_result": "breaks", "detail": "no memory/worker/process-group supervisor; cancellation is absent inside q-point evaluation"}


def case_19_lock_and_binding_verification_missing() -> dict[str, Any]:
    auth_source = inspect.getsource(DRIVER.verify_future_authorization)
    runner_source = inspect.getsource(DRIVER.run_authorized)
    assert "lock" not in auth_source.lower() and "signature_sha256" not in runner_source
    assert "review_archive_commit" not in auth_source.split("bindings =", 1)[1].split("if any", 1)[0]
    return {"joint_result": "breaks", "detail": "no exclusive launch lock or comparison of review/implementation archive custody to repository state"}


def case_20_artifact_manifest_and_progress_gaps() -> dict[str, Any]:
    runner_source = inspect.getsource(DRIVER.run_authorized)
    assert "hard_validity_reduce(receipts, coverage, controls, reduction[\"allocations_ok\"], True)" in runner_source
    assert "future runner output captured" in runner_source and "no stderr bytes were suppressed" in runner_source
    assert "actual_command" not in runner_source and "run_directory_path_hash" not in runner_source
    assert "stage-receipts.jsonl" not in runner_source
    return {"joint_result": "breaks", "detail": "artifact validity is hardcoded true; synthetic logs/command and incomplete manifest/progressive custody remain"}


CASES: list[tuple[str, Callable[[], dict[str, Any]]]] = [
    ("C01_CANONICAL_PAYLOAD", case_01_canonical_payload),
    ("C02_DRY_CLI_AND_PINNED_SCALAR", case_02_dry_cli_and_real_pinned_scalar),
    ("C03_PUBLIC_EVALUATOR_PRIVATE_ARGUMENT", case_03_public_evaluator_private_argument),
    ("C04_PUBLIC_SCHEMA_SEMANTICS", case_04_public_schema_semantics_unchecked),
    ("C05_FIRST_STAGE_AUTHCHECK_SERIALIZATION", case_05_authorized_pipeline_fails_first_stage),
    ("C06_UNBOUND_SIGNED_FIELDS", case_06_signed_but_unbound_fields_accepted),
    ("C07_BEDROCK_AND_PATH_REFUSALS", case_07_bedrock_and_path_refusals),
    ("C08_NONCE_REPLAY", case_08_nonce_replay),
    ("C09_SELECTION_COMPLETE_AND_MISSING", case_09_selection_complete_and_missing),
    ("C10_DUPLICATE_SELECTION_BIAS", case_10_duplicate_selection_bias),
    ("C11_BOOLEAN_ONLY_HARD_REDUCER", case_11_boolean_only_hard_reducer),
    ("C12_X_VALUE_CAP", case_12_x_value_cap_counts_points),
    ("C13_CERTIFICATE_SCHEMA", case_13_certificate_schema_incomplete),
    ("C14_COST_REDUCTION", case_14_cost_reduction_omits_charges_and_median),
    ("C15_SELECTION_SCORE", case_15_selection_score_omits_warmup),
    ("C16_LABEL_PERMUTATION", case_16_label_permutation_is_not_join_control),
    ("C17_QUERY_TRANSPORT_AND_REPETITION", case_17_query_transport_and_repetition_flag_missing),
    ("C18_RESOURCE_AND_CANCELLATION", case_18_resource_enforcement_and_inner_cancel_missing),
    ("C19_LOCK_AND_BINDINGS", case_19_lock_and_binding_verification_missing),
    ("C20_ARTIFACT_AND_MANIFEST", case_20_artifact_manifest_and_progress_gaps),
]


def main() -> int:
    started = time.perf_counter()
    administrative_started = time.perf_counter()
    administrative = administrative_checks()
    administrative_elapsed = time.perf_counter() - administrative_started
    results = []
    for case_id, function in CASES:
        case_started = time.perf_counter()
        try:
            observation = function()
            status = "PASS"
            error = None
        except Exception as exc:  # preserve every unexpected checker failure
            observation = {"joint_result": "checker_error", "detail": "unexpected checker failure"}
            status = "FAIL"
            error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - case_started
        results.append(
            {
                "case_id": case_id,
                "status": status,
                "elapsed_wall_seconds": elapsed,
                "within_10_second_watchdog": elapsed <= 10.0,
                "observation": observation,
                "error": error,
            }
        )
    payload = {
        "schema": "crypto.autoresearch.independent_fixed_checks.v1",
        "task_id": TASK_ID,
        "scientific_executions": 0,
        "fixed_case_count": len(results),
        "fixed_case_reruns": 0,
        "maximum_workers": 1,
        "administrative_elapsed_wall_seconds": administrative_elapsed,
        "total_elapsed_wall_seconds": time.perf_counter() - started,
        "administrative_checks": administrative,
        "cases": results,
        "all_checker_expectations_pass": all(
            item["status"] == "PASS" and item["within_10_second_watchdog"] for item in results
        ),
        "joint_breaks_reproduced": sum(
            item["observation"].get("joint_result") == "breaks" for item in results
        ),
        "joint_holds_reproduced": sum(
            item["observation"].get("joint_result") == "holds" for item in results
        ),
        "private_signing_key_accessed": False,
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0 if payload["all_checker_expectations_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

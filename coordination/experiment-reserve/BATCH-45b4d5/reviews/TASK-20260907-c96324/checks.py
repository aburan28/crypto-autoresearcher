#!/usr/bin/env python3
"""Fixed static/synthetic audit for TASK-20260907-c96324.

This script does not enter a frozen prime interval, discover a fixture, run a
scientific control, or collect a timing panel.  Its two runner calls use empty
mock callbacks in temporary directories.  The remaining cases inspect fixed
source paths or use tiny non-protocol objects.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import platform
import resource
import sys
import tempfile
import textwrap
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable


TASK_ID = "TASK-20260907-c96324"
ROOT = Path(__file__).resolve().parents[5]
DRIVER_PATH = ROOT / "experiments/EXP-ECDLP-1b1b99/implementation/TASK-20260907-aa1985/driver.py"
PLAN_PATH = DRIVER_PATH.with_name("execution-plan.json")


def load_driver():
    spec = importlib.util.spec_from_file_location("cm_snapshot_driver_c96324", DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bound driver")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = load_driver()
DRIVER_SOURCE = DRIVER_PATH.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_names(function: Callable[..., Any]) -> list[str]:
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.append(node.func.attr)
    return names


CASES: list[dict[str, Any]] = []


def case(case_id: str, obligation: str, attack: Callable[[], dict[str, Any]]) -> None:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    try:
        observed = attack()
        confirmed = bool(observed.pop("confirmed"))
        status = "BREAK_CONFIRMED" if confirmed else "UNEXPECTED_HOLD"
    except Exception as exc:  # A checker failure is not evidence of a producer defect.
        observed = {"checker_error": f"{type(exc).__name__}: {exc}"}
        status = "CHECKER_ERROR"
    CASES.append({
        "case_id": case_id,
        "obligation": obligation,
        "status": status,
        "wall_seconds": round(time.perf_counter() - started_wall, 6),
        "cpu_seconds": round(time.process_time() - started_cpu, 6),
        "observed": observed,
    })


def run_mock(audit_value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Path]:
    original_verify = driver.verify_launch_lock
    original_guard = driver._memory_guard
    seen: dict[str, Any] = {}
    temp = tempfile.TemporaryDirectory(prefix="cm-validator-c96324-")
    temp_path = Path(temp.name)

    def prepare() -> dict[str, Any]:
        return {"verifier_only_scalar_labels": [3, 5, 7], "certificates": {}}

    def measure(fixture: dict[str, Any]) -> list[dict[str, Any]]:
        seen["measure_received_fixture"] = fixture
        return []

    try:
        driver.verify_launch_lock = lambda *args, **kwargs: {"mock_binding": True}
        driver._memory_guard = lambda: None
        result = driver.execute_frozen_run(
            run_id="RUN-MOCK-C96324",
            run_root=temp_path,
            lock_path=temp_path / "absent-lock.json",
            authorization_path=temp_path / "absent-authorization.json",
            verifier=temp_path / "absent-verifier",
            cancel=lambda: False,
            prepare=prepare,
            audit=lambda fixture: audit_value,
            measure=measure,
        )
        out = Path(result["path"])
        snapshot = {
            "result": result,
            "manifest": json.loads((out / "manifest.yaml").read_text()),
            "controls": json.loads((out / "controls.json").read_text()),
            "raw": (out / "raw.jsonl").read_text(),
            "stdout": (out / "stdout.log").read_text(),
            "stderr": (out / "stderr.log").read_text(),
            "artifact_names": sorted(path.name for path in out.iterdir()),
        }
        return snapshot, seen, temp_path
    finally:
        driver.verify_launch_lock = original_verify
        driver._memory_guard = original_guard
        temp.cleanup()


def callback_scaffold_attack() -> dict[str, Any]:
    snapshot, seen, _ = run_mock({})
    manifest = snapshot["manifest"]
    missing_manifest = sorted({
        "run.code.commit", "run.code.dirty", "run.code.command", "run.inference",
        "run.environment", "run.inputs.seed", "run.timing", "run.resources",
        "run.result.valid", "run.artifacts",
    })
    confirmed = (
        snapshot["result"]["status"] == "completed_valid"
        and snapshot["controls"] == {}
        and snapshot["raw"] == ""
        and "verifier_only_scalar_labels" in seen["measure_received_fixture"]
        and "run" not in manifest
        and snapshot["stdout"] == snapshot["stderr"] == ""
    )
    return {
        "confirmed": confirmed,
        "terminal_status": snapshot["result"]["status"],
        "controls": snapshot["controls"],
        "raw_bytes": len(snapshot["raw"]),
        "measure_saw_verifier_only_labels": "verifier_only_scalar_labels" in seen["measure_received_fixture"],
        "manifest_top_level_keys": sorted(manifest),
        "canonical_manifest_fields_absent": missing_manifest,
        "stdout_stderr_forced_empty": snapshot["stdout"] == snapshot["stderr"] == "",
        "artifact_names": snapshot["artifact_names"],
    }


case(
    "C01",
    "A concrete runner must enforce fixtures, controls, scalar-label isolation, full matrix coverage and canonical receipt fields.",
    callback_scaffold_attack,
)


def false_control_attack() -> dict[str, Any]:
    supplied = {"composition": [{"all_checks": False, "beta_matches": False}]}
    snapshot, _, _ = run_mock(supplied)
    return {
        "confirmed": snapshot["result"]["status"] == "completed_valid" and snapshot["controls"] == supplied,
        "supplied_control": supplied,
        "terminal_status": snapshot["result"]["status"],
    }


case("C02", "A failed exact control must stop and invalidate the comparison.", false_control_attack)


def launch_gate_attack() -> dict[str, Any]:
    verify_source = inspect.getsource(driver.verify_launch_lock)
    main_source = inspect.getsource(driver.main)
    circular = (
        'lock["authorization_sha256"] != sha256_file(authorization_path)' in verify_source
        and 'authorization.get("lock_sha256") != sha256_file(lock_path)' in verify_source
    )
    verifier_unbound = "verifier_sha256" not in verify_source and "authenticator_sha256" not in verify_source
    reviews_unbound = all(token not in verify_source for token in ("review_commit", "review_sha256", "snapshot_commit"))
    no_launch_cli = "execute_frozen_run" not in main_source and "--launch" not in main_source
    return {
        "confirmed": circular and verifier_unbound and reviews_unbound and no_launch_cli,
        "mutual_hash_dependency": "lock.authorization_sha256=SHA256(authorization bytes); authorization.lock_sha256=SHA256(lock bytes)",
        "construction_path_present": False,
        "verifier_identity_or_hash_bound": not verifier_unbound,
        "snapshot_or_review_receipt_bound": not reviews_unbound,
        "launch_cli_present": not no_launch_cli,
    }


case("C03", "The future launch gate must be constructible, authenticate a fixed trust root, and bind completed reviews.", launch_gate_attack)


def malformed_lock_attack() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="cm-lock-c96324-") as directory:
        root = Path(directory)
        authorization = root / "authorization.json"
        authorization.write_text("{}\n", encoding="utf-8")
        lock = {
            "kind": "genuine_runtime_code_execution_lock",
            "experiment_id": driver.EXPERIMENT_ID,
            "approval_decision_id": driver.APPROVAL_ID,
            "implementation_approval_id": driver.IMPLEMENTATION_APPROVAL_ID,
            "spec_sha256": driver.SPEC_SHA256,
            "driver_sha256": sha256_file(DRIVER_PATH),
            "execution_plan_sha256": sha256_file(PLAN_PATH),
            "resource_limits": driver.FROZEN_LIMITS,
            "authorization_sha256": sha256_file(authorization),
            "unexpected_extra": True,
            # runtime deliberately absent; the extra key makes set(lock) < needed false.
        }
        lock_path = root / "lock.json"
        lock_path.write_text(json.dumps(lock, sort_keys=True) + "\n", encoding="utf-8")
        observed = "no_exception"
        try:
            driver.verify_launch_lock(lock_path, authorization, root / "verifier")
        except Exception as exc:
            observed = f"{type(exc).__name__}:{exc}"
        return {
            "confirmed": observed == "KeyError:'runtime'",
            "observed": observed,
            "expected_refusal_class": "LaunchRefused",
        }


case("C04", "Malformed launch records must fail closed through the declared refusal classification.", malformed_lock_attack)


def resource_attack() -> dict[str, Any]:
    memory_source = inspect.getsource(driver._memory_guard)
    execute_source = inspect.getsource(driver.execute_frozen_run)
    confirmed = (
        "RUSAGE_SELF" in memory_source
        and "* 1024" in memory_source
        and "platform" not in memory_source
        and "RUSAGE_CHILDREN" not in memory_source
        and "time.process_time" not in execute_source
        and "time.monotonic" not in execute_source
        and "subprocess" not in execute_source
        and execute_source.count("check_cancellation") == 1
    )
    return {
        "confirmed": confirmed,
        "host_platform": platform.system(),
        "rss_conversion": "ru_maxrss multiplied by 1024 without a platform branch",
        "rss_scope": "RUSAGE_SELF only",
        "wall_or_cpu_watchdog_around_callbacks": False,
        "cancellation_checks": execute_source.count("check_cancellation"),
        "cancellation_visible_inside_callback": False,
    }


case("C05", "Memory, wall/CPU watchdogs and cancellation must cover the full process group and long stages.", resource_attack)


def custody_attack() -> dict[str, Any]:
    execute_source = inspect.getsource(driver.execute_frozen_run)
    json_writer = inspect.getsource(driver._write_json)
    confirmed = (
        "out.mkdir" in execute_source
        and execute_source.index("out.mkdir") < execute_source.index("result=action()")
        and execute_source.index("_write_json(out/\"fixtures.json\"") > execute_source.index("result=action()")
        and "write_text" in json_writer
        and "replace" not in json_writer
        and "fsync" not in DRIVER_SOURCE
    )
    return {
        "confirmed": confirmed,
        "run_directory_created_before_stages": True,
        "first_receipt_write_after_all_stage_callbacks": True,
        "atomic_temp_replace": False,
        "fsync_or_hash_chain": False,
        "effect": "kill or hang inside prepare/audit/measure can leave an empty run id or lose in-stage progress",
    }


case("C06", "Run custody must publish incrementally and atomically across cancellation or failure.", custody_attack)


def rng_attack() -> dict[str, Any]:
    E = driver.Curve(7, 0, 2)
    generator = next(point for point in E.points() if point is not None)
    floor = SimpleNamespace(phi=SimpleNamespace(target=E), generator=generator)
    first = driver.query_points(floor, r=5, p=7, a=0, b=2, seed=606101, q=3)
    second = driver.query_points(floor, r=5, p=7, a=0, b=2, seed=606101, q=3)
    source = inspect.getsource(driver.query_points)
    return {
        "confirmed": first == second and "counter=0" in source,
        "duplicate_on_second_call": first == second,
        "counter_state_returned": False,
        "floor_coefficients_derived_internally": False,
        "note": "The function accepts caller supplied p,a,b and resets the frozen stream tuple on every call.",
    }


case("C07", "Random streams must persist counters for each complete tuple and bind the original floor coefficients.", rng_attack)


def domain_and_certificate_attack() -> dict[str, Any]:
    cert = driver.Conductor3Certificate(
        p=5,
        trace=999,
        frobenius_discriminant=-36,
        f_pi=3,
        v3_f_pi=1,
        inert=True,
        quotient_models=4,
        rational_isogeny_counts=(0,),
    )
    cert.validate()  # It accepts inconsistent trace/p/count cardinality.
    controls_source = inspect.getsource(driver.verify_controls)
    dual_source = inspect.getsource(driver.exact_dual)
    endpoint_mix = "points=[fixture.g0,floor.generator]" in controls_source
    reverse_absent = "floor.phi.apply(floor.dual.psi(" not in controls_source
    one_point_dual = "pair.check(certificate_point)" in dual_source
    return {
        "confirmed": endpoint_mix and reverse_absent and one_point_dual,
        "inconsistent_certificate_accepted": True,
        "certificate_trace": cert.trace,
        "certificate_p": cert.p,
        "quotient_models": cert.quotient_models,
        "rational_count_entries": len(cert.rational_isogeny_counts),
        "source_and_target_points_mixed_in_one_source_curve_loop": endpoint_mix,
        "reverse_phi_psi_identity_checked": not reverse_absent,
        "dual_selected_from_one_source_point": one_point_dual,
    }


case("C08", "Endpoint types, both dual identities, distinct models, multiplicities and level crosschecks must be enforced.", domain_and_certificate_attack)


def label_control_attack() -> dict[str, Any]:
    controls_source = inspect.getsource(driver.verify_controls)
    calls = call_names(driver.verify_controls)
    descriptive_only = '"method":"Fisher-Yates over four equal-weight floor totals; summary must be invariant"' in controls_source
    return {
        "confirmed": descriptive_only and "fisher_yates" not in calls,
        "control_value": "method description string",
        "permutation_executed": "fisher_yates" in calls,
        "reaggregation_compared": False,
    }


case("C09", "The label-permutation control must actually permute and reaggregate the same costs.", label_control_attack)


def matrix_attack() -> dict[str, Any]:
    module_tree = ast.parse(DRIVER_SOURCE)
    calls: list[str] = []
    for node in ast.walk(module_tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            calls.append(node.func.attr)
    pinned_source = inspect.getsource(driver.pinned_library_mul)
    execute_source = inspect.getsource(driver.execute_frozen_run)
    missing = {
        "timed_blocks_invoked": calls.count("timed_blocks") > 0,
        "CostLedger_instantiated": calls.count("CostLedger") > 0,
        "select_baseline_invoked": calls.count("select_baseline") > 0,
        "concrete_measure_scalar_call": "measure_scalar_workload(" in execute_source,
        "concrete_measure_transport_call": "measure_transport_workload(" in execute_source,
    }
    pinned_duplicates_binary = "return E.mul(n,P)" in pinned_source
    return {
        "confirmed": not any(missing.values()) and pinned_duplicates_binary,
        **missing,
        "pinned_library_is_same_affine_mul": pinned_duplicates_binary,
        "full_seed_class_floor_coordinate_q_arm_matrix_aggregator": False,
        "baseline_selection_confirmation_split": False,
        "below_resolution_and_seven_block_validity_path": False,
        "charged_setup_and_repetition_path": False,
    }


case("C10", "The full timing/baseline matrix and every charged cost term must have a concrete data-flow path.", matrix_attack)


def selection_and_partial_attack() -> dict[str, Any]:
    g0_source = inspect.getsource(driver.choose_g0)
    panel_source = inspect.getsource(driver.discover_frozen_panel)
    counts_points = "for P in sorted" in g0_source and "checked += 1" in g0_source
    loses_partial = "if len(interval)<2: raise InvalidMeasurement" in panel_source
    return {
        "confirmed": counts_points and loses_partial,
        "g0_cap_unit": "affine points",
        "frozen_cap_unit": "x values",
        "partial_panel_returned_on_unavailable_interval": not loses_partial,
        "rejected_candidates_survive_prepare_exception": False,
    }


case("C11", "Fixture selection caps and unavailable-fixture handling must retain all candidate work and partial coverage.", selection_and_partial_attack)


def report() -> dict[str, Any]:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak = int(ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1))
    return {
        "schema": "crypto.autoresearch.validator_static_checks.v1",
        "task_id": TASK_ID,
        "source_driver": str(DRIVER_PATH.relative_to(ROOT)),
        "source_driver_sha256": sha256_file(DRIVER_PATH),
        "scientific_runs": 0,
        "frozen_fixture_searches": 0,
        "scientific_control_panels": 0,
        "timing_measurements": 0,
        "case_count": len(CASES),
        "breaks_confirmed": sum(item["status"] == "BREAK_CONFIRMED" for item in CASES),
        "checker_errors": sum(item["status"] == "CHECKER_ERROR" for item in CASES),
        "peak_rss_bytes": peak,
        "cases": CASES,
    }


if __name__ == "__main__":
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    payload = report()
    payload["aggregate_wall_seconds"] = round(time.perf_counter() - started_wall + sum(x["wall_seconds"] for x in CASES), 6)
    payload["aggregate_cpu_seconds"] = round(time.process_time() - started_cpu + sum(x["cpu_seconds"] for x in CASES), 6)
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(0 if payload["checker_errors"] == 0 and payload["breaks_confirmed"] == payload["case_count"] else 1)

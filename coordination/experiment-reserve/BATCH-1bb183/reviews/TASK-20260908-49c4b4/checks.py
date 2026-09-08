#!/usr/bin/env python3
"""Bounded independent static/arithmetic/synthetic/mock checks for TASK-20260908-49c4b4.

This program never selects a frozen fixture, runs a collision census, evaluates
an experimental control, invokes the future-run CLI, or creates a scientific
RUN directory.  Temporary filesystem and Git objects are synthetic custody
objects only.  Each named case is limited to ten seconds.
"""
from __future__ import annotations

import ast
import base64
import contextlib
import csv
import hashlib
import importlib.util
import inspect
import io
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml


TASK_ID = "TASK-20260908-49c4b4"
AUTHORITY_COMMIT = "cc708327b8975ec827b7af6229a8a3c4797ab333"
SOURCE_SNAPSHOT = "c58ed446ac7f81ab0740bccf5a74a4d5bd523772"
CLAIM_COMMIT = "e85bbcdb67972f5a366da899ed5b06be54cea0c4"
ROOT = Path(__file__).resolve().parents[5]
HANDOFF_PATH = f"ledger/handoffs/{TASK_ID}.yaml"
PLAN_PATH = f"coordination/experiment-reserve/BATCH-1bb183/review-plan-{TASK_ID}.yaml"
QUEUE_PATH = "coordination/experiment-reserve/BATCH-1bb183/dispatch_queue.json"
CLAIM_PATH = f"coordination/experiment-reserve/BATCH-1bb183/claims/{TASK_ID}.1.claim.json"
IMPLEMENTATION_DIR = "experiments/EXP-ECDLP-651b94/implementation/TASK-20260908-6a010d"
DRIVER_PATH = ROOT / IMPLEMENTATION_DIR / "driver.py"
SOURCE_FILES = {
    f"{IMPLEMENTATION_DIR}/driver.py",
    f"{IMPLEMENTATION_DIR}/tests.py",
    f"{IMPLEMENTATION_DIR}/README.md",
    f"{IMPLEMENTATION_DIR}/implementation-report.yaml",
    f"{IMPLEMENTATION_DIR}/execution-plan.json",
    f"{IMPLEMENTATION_DIR}/regression-receipt.json",
}
SNAPSHOT_RECEIPT = "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260908-8e93d0/snapshot.json"


def run_git(*args: str, cwd: Path = ROOT, text: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text,
    )
    return result.stdout.strip() if text else result.stdout


def git_show(commit: str, path: str) -> bytes:
    return run_git("show", f"{commit}:{path}")  # type: ignore[return-value]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_ancestor(first: str, second: str, cwd: Path = ROOT) -> bool:
    result = subprocess.run(
        ["git", "-C", str(cwd), "merge-base", "--is-ancestor", first, second],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.returncode == 0


def load_driver() -> Any:
    spec = importlib.util.spec_from_file_location("spectral_second_corrected_driver", DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reviewed driver")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


driver = load_driver()
DRIVER_TEXT = DRIVER_PATH.read_text(encoding="utf-8")
DRIVER_AST = ast.parse(DRIVER_TEXT)


@contextlib.contextmanager
def patched(obj: Any, **values: Any) -> Iterator[None]:
    originals = {name: getattr(obj, name) for name in values}
    try:
        for name, value in values.items():
            setattr(obj, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(obj, name, value)


def arm(work: int, successes: int, *, failed: int = 0) -> dict[str, Any]:
    return {
        "transition_group_operations": work,
        "verification_group_operations": 0,
        "successes": successes,
        "failed_certificates": failed,
        "starts": 1,
        "group_additions": work,
        "group_doublings": 0,
        "charged_cost": None if successes == 0 else work / successes,
        "certificates": [],
        "secondary": {
            "mean_first_repeat_length": 1.0,
            "useful_fraction": 1.0 if successes else 0.0,
            "fixed_points": 0,
            "two_cycles": 0,
            "component_sizes": [1],
            "max_tail_length": 0,
            "max_cycle_length": 1,
        },
        "diagnostic_costs": {
            "diagnostic_wall_seconds": 0.01,
            "diagnostic_cpu_seconds": 0.01,
            "collision_table_peak_bytes": 64,
            "scalar_inversions": 0,
            "scalar_comparisons": 0,
        },
    }


def controls(**overrides: Any) -> dict[str, Any]:
    values = {
        "cayley": True,
        "relabel": True,
        "occupancy": True,
        "zero_denominators": 0,
        "solves": 0,
        "mutation": True,
    }
    values.update(overrides)
    return {
        "cayley": {"passed": values["cayley"]},
        "relabel": values["relabel"],
        "occupancy": values["occupancy"],
        "known_false": {
            "constant_o": {
                "nonzero_denominators": values["zero_denominators"],
                "solves": values["solves"],
            },
            "mutated_candidate_fails_certificate": values["mutation"],
        },
    }


def synthetic_cell(curve_id: str, seed: int, u: int, d: float | None, *, valid: bool = True, stream: str = "heldout") -> dict[str, Any]:
    return {
        "curve_id": curve_id,
        "seed": seed,
        "u": u,
        "stream": stream,
        "metric": {"available": d is not None, "d": d},
        "validity": {"valid": valid},
        "coordinate": arm(10, 2),
        "nulls": [{**arm(12, 2), "arm": index} for index in range(1, 8)],
        "controls": controls(),
        "diagnostic_costs": {
            "subgroup_enumeration": {"diagnostic": "subgroup_enumeration", "diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.01},
            "coordinate_partition_queries": {"diagnostic": "coordinate_partition_queries", "diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.01, "partition_queries": 1},
            "shuffle_construction": [{"diagnostic": "shuffle_construction", "arm": index, "diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.01, "partition_queries": 1, "rng_counter_end": 1} for index in range(1, 8)],
            "cayley_control": {"diagnostic": "cayley_control", "diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.01},
        },
    }


def full_panel(value: float = 0.2) -> list[dict[str, Any]]:
    return [
        synthetic_cell(f"curve-{curve}", seed, u, value)
        for curve in range(4)
        for seed in driver.HELDOUT_SEEDS
        for u in driver.US
    ]


def mock_payload(cells: list[dict[str, Any]] | None = None, *, wall_age: float = 2.0) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="validator-spectral-artifacts-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.cells.extend(cells or [synthetic_cell("curve-0", driver.HELDOUT_SEEDS[0], 1, 0.1)])
        meter = driver.ResourceMeter(
            started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=wall_age),
            started_wall=driver.time.monotonic() - wall_age,
            started_cpu=driver.time.process_time(),
        )
        with patched(driver, process_group_rss_bytes=lambda: 4096):
            return driver.artifact_bytes(
                lock={"run_id": "RUN-ECDLP-abcdef"},
                provenance={"commit": "a" * 40, "dirty": False, "command": "fixed-validator-mock"},
                meter=meter,
                sink=sink,
                status="completed_invalid",
                error="fixed synthetic outcome",
                decision={"branch": "inconclusive", "reasons": ["fixed_synthetic"], "per_u": {}},
            )


def payload_files() -> dict[str, bytes]:
    return {name: f"fixed mock {name}\n".encode("utf-8") for name in driver.EXPERIMENT_ARTIFACTS[:-1]}


def function_node(name: str) -> ast.FunctionDef:
    for node in DRIVER_AST.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} absent")


def case_source_bindings_exact() -> None:
    handoff = yaml.safe_load(git_show(AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    assert len(handoff["source_bindings"]) == len(handoff["inputs"]) == 40
    for binding in handoff["source_bindings"]:
        actual = sha256(git_show(AUTHORITY_COMMIT, binding["path"]))
        assert actual == binding["sha256"], f"authority binding mismatch: {binding['path']}"


def case_bound_control_file_drift_isolated() -> None:
    handoff = yaml.safe_load(git_show(AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    expected = {row["path"]: row["sha256"] for row in handoff["source_bindings"]}
    authority_hash = sha256(git_show(AUTHORITY_COMMIT, "tools/research_dispatch.py"))
    assert authority_hash == expected["tools/research_dispatch.py"]
    assert authority_hash == "e715a91bbba6e5f0944783ae0bd072d27332ee439dda50dd4224952dc8896cd8"


def case_source_snapshot_exact_six_files() -> None:
    handoff = yaml.safe_load(git_show(AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    expected = {row["path"]: row["sha256"] for row in handoff["source_bindings"]}
    for path in SOURCE_FILES:
        assert sha256(git_show(SOURCE_SNAPSHOT, path)) == expected[path]


def case_snapshot_archive_exact_scope_and_receipt() -> None:
    changed = set(str(run_git("diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT, text=True)).splitlines())
    assert changed == SOURCE_FILES | {SNAPSHOT_RECEIPT}
    queue = json.loads(git_show(AUTHORITY_COMMIT, QUEUE_PATH))
    task = next(item for item in queue["tasks"] if item["id"] == "TASK-20260908-8e93d0")
    archive = task["archive"]
    assert task["state"] == "completed"
    assert archive["commit_sha"] == SOURCE_SNAPSHOT
    assert archive["parent_sha"] == str(run_git("rev-parse", f"{SOURCE_SNAPSHOT}^", text=True))
    assert set(archive["path_sha256"]) == changed
    for path, digest in archive["path_sha256"].items():
        assert sha256(git_show(SOURCE_SNAPSHOT, path)) == digest


def case_review_plan_precedes_claim() -> None:
    plan = yaml.safe_load(git_show(AUTHORITY_COMMIT, PLAN_PATH))["review_plan"]
    assert plan["recorded_before_reviewers"] is True
    assert plan["source_snapshot"] == SOURCE_SNAPSHOT
    assert is_ancestor(SOURCE_SNAPSHOT, AUTHORITY_COMMIT)
    assert is_ancestor(AUTHORITY_COMMIT, CLAIM_COMMIT)
    assert is_ancestor(CLAIM_COMMIT, str(run_git("rev-parse", "HEAD", text=True)))


def case_claim_epoch_and_scope() -> None:
    claim = json.loads(git_show(CLAIM_COMMIT, CLAIM_PATH))
    handoff = yaml.safe_load(git_show(AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    assert claim["task_id"] == TASK_ID and claim["epoch"] == 1
    assert claim["owner"] == "coordinator-reserve-admission-20260907"
    assert claim["write_scope"] == handoff["write_scope"]


def case_approval_and_amendment_chain() -> None:
    spec = yaml.safe_load(git_show(AUTHORITY_COMMIT, "experiments/EXP-ECDLP-651b94/specification.yaml"))["experiment"]
    approval = yaml.safe_load(git_show(AUTHORITY_COMMIT, "experiments/EXP-ECDLP-651b94/approvals/DEC-20260906-f73475.yaml"))["experiment_approval"]
    amendment = yaml.safe_load(git_show(AUTHORITY_COMMIT, "experiments/EXP-ECDLP-651b94/amendments/DEC-20260907-38017a.yaml"))["protocol_amendment"]
    assert spec["frozen"] is True and spec["id"] == "EXP-ECDLP-651b94"
    assert approval["status"] == "approved" and approval["source_specification"]["sha256"] == driver.SPEC_SHA256
    assert amendment["approved_by"] == driver.AMENDMENT_ID


def case_execution_plan_binds_final_driver() -> None:
    plan = json.loads(git_show(SOURCE_SNAPSHOT, f"{IMPLEMENTATION_DIR}/execution-plan.json"))
    assert plan["driver"]["sha256"] == sha256(git_show(SOURCE_SNAPSHOT, f"{IMPLEMENTATION_DIR}/driver.py"))


def case_regression_receipt_is_bounded_and_final() -> None:
    receipt = json.loads(git_show(SOURCE_SNAPSHOT, f"{IMPLEMENTATION_DIR}/regression-receipt.json"))
    assert receipt["scientific_runs"] == 0
    assert receipt["allowance"]["actual_total_case_executions_including_reruns"] == 102
    assert receipt["allowance"]["actual_total_case_executions_including_reruns"] <= 160
    assert receipt["final_code_hashes_before_report_and_receipt"]["driver.py"] == sha256(git_show(SOURCE_SNAPSHOT, f"{IMPLEMENTATION_DIR}/driver.py"))


def case_rng_canonical_vector_and_n_one() -> None:
    params = (17, 1, 2, 19, 0, 1, 1)
    assert driver.canonical_json({"b": 1, "a": 2}) == b'{"a":2,"b":1}'
    assert driver.rejection_draw(purpose="query", params=params, seed=1, counter=4, n=1) == (0, 5)


def case_target_rng_uses_unscaled_tuple() -> None:
    source = ast.get_source_segment(DRIVER_TEXT, function_node("future_cell")) or ""
    assert "target_params = (curve.p, curve.A, curve.B, r, 0, 0, 0)" in source


def case_control_rng_uses_frozen_u_zero_tuple() -> None:
    node = function_node("future_cell")
    calls = [item for item in ast.walk(node) if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "deterministic_shuffle"]
    control_calls = [item for item in calls if any(keyword.arg == "purpose" and isinstance(keyword.value, ast.Constant) and keyword.value.value == "control" for keyword in item.keywords)]
    assert len(control_calls) == 1
    params = next(keyword.value for keyword in control_calls[0].keywords if keyword.arg == "params")
    assert isinstance(params, ast.Tuple) and len(params.elts) == 7
    assert isinstance(params.elts[5], ast.Constant) and params.elts[5].value == 0, "control stream uses actual u instead of frozen u=0"


def case_subgroup_repeated_addition_certificate() -> None:
    class CyclicMock:
        def __init__(self, modulus: int):
            self.modulus = modulus
            self.additions = 0

        def add(self, left: Any, right: Any) -> Any:
            self.additions += 1
            lv = 0 if left is None else left[1]
            rv = 0 if right is None else right[1]
            value = (lv + rv) % self.modulus
            return None if value == 0 else (1, value)

    curve = CyclicMock(5)
    points, certificate = driver.enumerate_subgroup(curve, (1, 1), 5, lambda: None)
    assert curve.additions == 5 and points[0] is None
    assert certificate == {
        "method": "checked_repeated_addition",
        "enumerated_scalars": [0, 4],
        "points_enumerated": 5,
        "starts_at_infinity": True,
        "distinct": True,
        "r_times_G_is_O": True,
    }


def case_fixture_path_records_rejections_before_selection() -> None:
    source = ast.get_source_segment(DRIVER_TEXT, function_node("fixture_scan")) or ""
    assert source.index("discriminator == 0") < source.index("curve = Curve")
    assert "on_rejection(record)" in source and "on_selection(record)" in source
    assert "if len(selected) == 2" in source


def case_exploratory_precedes_heldout_and_decision_filters() -> None:
    source = ast.get_source_segment(DRIVER_TEXT, function_node("run_future_pipeline")) or ""
    assert '("exploratory", EXPLORATORY_SEEDS), ("heldout", HELDOUT_SEEDS)' in source
    assert source.index('(\"exploratory\", EXPLORATORY_SEEDS)') < source.index('cell.get("stream") == "heldout"')
    assert driver.EXPLORATORY_SEEDS == tuple(range(606300, 606308))
    assert driver.HELDOUT_SEEDS == tuple(range(606308, 606316))


def case_positive_complete_panel() -> None:
    result = driver.global_decision(full_panel(0.2))
    assert result["panel_valid"] is True and result["branch"] == "positive"


def case_negative_is_cellwise() -> None:
    result = driver.global_decision(full_panel(0.0))
    assert result["panel_valid"] is True and result["branch"] == "negative"


def case_missing_cell_refuses_complete_panel() -> None:
    result = driver.global_decision(full_panel(0.2)[:-1])
    assert result["panel_valid"] is False and result["branch"] == "inconclusive"


def case_one_u_below_threshold_refuses_positive() -> None:
    cells = full_panel(0.2)
    for row in cells:
        if row["u"] == 3:
            row["metric"]["d"] = 0.17
    assert driver.global_decision(cells)["branch"] == "inconclusive"


def case_one_curve_nonpositive_refuses_positive() -> None:
    cells = full_panel(0.25)
    for row in cells:
        if row["u"] == 3 and row["curve_id"] == "curve-0":
            row["metric"]["d"] = 0.0
    assert driver.global_decision(cells)["branch"] == "inconclusive"


def case_unavailable_cell_is_valid_inconclusive() -> None:
    cells = full_panel(0.2)
    cells[0]["metric"] = {"available": False, "d": None}
    result = driver.global_decision(cells)
    assert result["panel_valid"] is True and result["branch"] == "inconclusive"
    assert result["reasons"] == ["unavailable_inferential_cell"]


def case_invalid_cell_invalidates_panel() -> None:
    cells = full_panel(-0.1)
    cells[0]["validity"] = {"valid": False}
    result = driver.global_decision(cells)
    assert result["panel_valid"] is False and "invalid_certificate_or_control" in result["reasons"]


def case_zero_yield_null_arm_remains_charged() -> None:
    metric = driver.cell_difference(arm(50, 10), [arm(100, 0)] + [arm(60, 10) for _ in range(6)])
    assert metric["available"] is True and metric["zero_yield_null_arms"] == [1]
    assert (metric["pooled_null_work"], metric["pooled_null_successes"]) == (460, 60)


def case_zero_total_side_is_unavailable() -> None:
    assert driver.cell_difference(arm(40, 0), [arm(50, 5) for _ in range(7)])["unavailable_reason"] == "coordinate_zero_success"
    assert driver.cell_difference(arm(40, 4), [arm(50, 0) for _ in range(7)])["unavailable_reason"] == "pooled_null_zero_success"


def case_unequal_success_pool_is_total_work_over_total_success() -> None:
    rows = [arm(10, 10), arm(99, 1)] + [arm(10, 10) for _ in range(5)]
    work, successes, cost = driver.pooled_null_cost(rows)
    assert (work, successes) == (159, 61)
    assert abs(cost - 159 / 61) < 1e-12
    assert abs(cost - sum(row["charged_cost"] for row in rows) / 7) > 1e-3


def case_all_named_validity_controls_reduce() -> None:
    variants = [
        controls(cayley=False), controls(relabel=False), controls(occupancy=False),
        controls(zero_denominators=1), controls(solves=1), controls(mutation=False),
    ]
    for item in variants:
        assert driver.reduce_validity(arm(1, 1), [arm(1, 1)] * 7, item)["valid"] is False
    assert driver.reduce_validity(arm(1, 1, failed=1), [arm(1, 1)] * 7, controls())["valid"] is False


def case_constant_o_executes_all_mock_starts() -> None:
    result = driver.constant_o_census([None, (1, 1), (2, 2), (3, 3)], lambda: None)
    assert result["passed"] is True
    assert (result["starts"], len(result["collisions"]), result["nonzero_denominators"], result["solves"]) == (4, 4, 0, 0)


def run_mock_pipeline(*, fixture_action: Callable[..., Any], cell_action: Callable[..., Any] | None = None) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_artifacts(**kwargs: Any) -> dict[str, bytes]:
        captured.update({
            "status": kwargs["status"],
            "error": kwargs["error"],
            "decision": kwargs["decision"],
            "cells": len(kwargs["sink"].cells),
        })
        return {}

    replacements: dict[str, Any] = {
        "select_fixtures": fixture_action,
        "artifact_bytes": fake_artifacts,
        "atomic_publish": lambda run_root, run_id, payload: {},
        "execution_provenance": lambda command: {"commit": "a" * 40, "dirty": False, "command": command},
    }
    if cell_action is not None:
        replacements["future_cell"] = cell_action
    with tempfile.TemporaryDirectory(prefix="validator-spectral-pipeline-") as temporary:
        with patched(driver, **replacements), patched(driver.Guard, check=lambda self: None):
            driver.run_future_pipeline({"run_id": "RUN-ECDLP-abcdef"}, Path(temporary), "fixed-validator-mock")
    return captured


def case_first_invalid_cell_stops_next_cell() -> None:
    calls: list[tuple[int, int, int]] = []
    fixtures = {9: [{"p": 17, "B": 1}], 11: [{"p": 19, "B": 2}]}

    def fake_cell(fixture: dict[str, Any], seed: int, u: int, check: Any, partial: Any = None) -> dict[str, Any]:
        calls.append((fixture["p"], seed, u))
        return synthetic_cell(f"p{fixture['p']}-B{fixture['B']}", seed, u, None, valid=False, stream="exploratory")

    result = run_mock_pipeline(fixture_action=lambda check, sink=None: (fixtures, []), cell_action=fake_cell)
    assert len(calls) == 1
    assert result["status"] == "completed_invalid" and result["cells"] == 1
    assert result["decision"]["reasons"] == ["frozen_validity_failure_immediate_stop"]


def case_unavailable_fixture_is_inconclusive_not_implementation_invalid() -> None:
    def unavailable(check: Any, sink: Any = None) -> Any:
        raise driver.LaunchRefused("frozen fixture panel incomplete for b=9; no widening permitted")

    result = run_mock_pipeline(fixture_action=unavailable)
    assert result["status"] not in {"completed_invalid", "failed_implementation"}, "unavailable frozen fixture was mislabeled as implementation/data invalidity"
    assert result["decision"]["branch"] == "inconclusive"


def case_implementation_exception_is_failed_implementation() -> None:
    def broken(check: Any, sink: Any = None) -> Any:
        raise ValueError("fixed injected implementation exception")

    result = run_mock_pipeline(fixture_action=broken)
    assert result["status"] == "failed_implementation", "implementation exception was mislabeled as completed_invalid"


def case_artifact_payload_has_complete_canonical_set() -> None:
    payload = mock_payload()
    assert set(payload) == set(driver.EXPERIMENT_ARTIFACTS[:-1])
    assert {"command.txt", "environment.json", "raw-result.json"}.issubset(payload)


def case_costs_and_raw_bind_secondary_fields() -> None:
    payload = mock_payload()
    required = {
        "mean_first_repeat_length", "useful_fraction", "fixed_points", "two_cycles",
        "component_sizes", "max_tail_length", "max_cycle_length",
        "scalar_inversions", "scalar_comparisons", "diagnostic_wall_seconds",
        "diagnostic_cpu_seconds", "collision_table_peak_bytes",
    }
    fields = set(csv.DictReader(io.StringIO(payload["costs.csv"].decode("utf-8"))).fieldnames or [])
    assert required.issubset(fields)
    metrics = json.loads(payload["raw-result.json"])["metrics"]
    assert {"secondary_by_diagnostic", "diagnostic_costs"}.issubset(metrics)


def case_report_states_actual_coverage() -> None:
    payload = mock_payload([synthetic_cell("curve-0", driver.EXPLORATORY_SEEDS[0], 1, None, valid=False, stream="exploratory")])
    report = payload["report.md"].decode("utf-8")
    assert re.search(r"cells[^\n]*1", report, re.IGNORECASE), "report omits actual completed-cell coverage"
    assert not re.search(r"8 seeds retained", report), "partial run falsely reports all eight exploratory seeds retained"


def case_report_binds_secondary_and_diagnostic_values() -> None:
    report = mock_payload()["report.md"].decode("utf-8")
    for name in ("mean_first_repeat_length", "component_sizes", "scalar_inversions", "diagnostic_cpu_seconds"):
        assert name in report, f"report omits {name}"


def case_every_named_control_has_measured_diagnostic_cost() -> None:
    source = ast.get_source_segment(DRIVER_TEXT, function_node("future_cell")) or ""
    for call_name in ("relabel_control", "constant_o_census", "binary_verifier"):
        position = source.index(call_name)
        preceding = source[max(0, position - 120):position]
        assert "measured_diagnostic" in preceding, f"{call_name} is not bracketed as a diagnostic"


def case_terminal_utc_matches_monotonic_bracket() -> None:
    payload = mock_payload(wall_age=3.0)
    timing = yaml.safe_load(payload["manifest.yaml"])["run"]["timing"]
    started = datetime.fromisoformat(timing["started_at"])
    finished = datetime.fromisoformat(timing["finished_at"])
    assert abs((finished - started).total_seconds() - timing["wall_seconds"]) < 0.5
    assert timing["monotonic_finished"] >= timing["monotonic_started"]


def case_atomic_success_and_package_hashes() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-spectral-publish-") as temporary:
        root = Path(temporary)
        hashes = driver.atomic_publish(root, "RUN-ECDLP-abcdef", payload_files())
        final = root / "runs" / "RUN-ECDLP-abcdef"
        assert set(path.name for path in final.iterdir()) == set(driver.EXPERIMENT_ARTIFACTS)
        package = json.loads((final / "package-sha256.json").read_text(encoding="utf-8"))
        assert package["artifact_sha256"] == hashes


def case_missing_payload_never_exposes_final() -> None:
    payload = payload_files()
    payload.pop("raw-result.json")
    with tempfile.TemporaryDirectory(prefix="validator-spectral-missing-") as temporary:
        root = Path(temporary)
        try:
            driver.atomic_publish(root, "RUN-ECDLP-abcdef", payload)
        except ValueError:
            pass
        else:
            raise AssertionError("missing mandatory artifact was accepted")
        assert not (root / "runs" / "RUN-ECDLP-abcdef").exists()


def case_postrename_fsync_failure_quarantines() -> None:
    calls = 0

    def fail_third(_path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("fixed post-rename parent fsync failure")

    with tempfile.TemporaryDirectory(prefix="validator-spectral-postrename-") as temporary:
        root = Path(temporary)
        with patched(driver, fsync_directory=fail_third):
            try:
                driver.atomic_publish(root, "RUN-ECDLP-abcdef", payload_files())
            except driver.InfrastructureStop:
                pass
            else:
                raise AssertionError("post-rename failure was reported as success")
        assert not (root / "runs" / "RUN-ECDLP-abcdef").exists()
        retained = list((root / "runs" / "incomplete").iterdir())
        assert len(retained) == 1 and (retained[0] / "publication-failure.json").is_file()


def case_failed_failure_receipt_is_not_called_annotated() -> None:
    original_write = Path.write_bytes

    def fail_receipt(path: Path, data: bytes) -> int:
        if path.name == "publication-failure.json":
            raise OSError("fixed receipt-write failure")
        return original_write(path, data)

    with tempfile.TemporaryDirectory(prefix="validator-spectral-retain-") as temporary:
        runs = Path(temporary) / "runs"
        final = runs / "RUN-ECDLP-abcdef"
        final.mkdir(parents=True)
        (final / "manifest.yaml").write_text("fixed mock\n", encoding="utf-8")
        with patched(Path, write_bytes=fail_receipt):
            outcome = driver.retain_publication_failure(
                runs=runs,
                run_id="RUN-ECDLP-abcdef",
                staging=runs / ".absent-staging",
                final=final,
                error=OSError("fixed post-rename failure"),
                phase="post_rename_durability",
            )
        if outcome["state"] == "annotated_final":
            assert (final / "publication-failure.json").is_file(), "unwritten receipt was reported as annotated_final"


def case_run_root_is_fixed_to_experiment_directory() -> None:
    captured: dict[str, Path] = {}

    def fake_pipeline(lock: dict[str, Any], run_root: Path, command: str) -> dict[str, str]:
        captured["run_root"] = run_root
        return {}

    with tempfile.TemporaryDirectory(prefix="validator-arbitrary-run-root-") as temporary:
        arbitrary = Path(temporary)
        with patched(driver, verify_launch_admission=lambda lock, key: {"run_id": "RUN-ECDLP-abcdef"}, run_future_pipeline=fake_pipeline), contextlib.redirect_stdout(io.StringIO()):
            try:
                code = driver.main(["future-run", "--lock", str(arbitrary / "lock.json"), "--coordinator-public-key-b64", "fixed", "--run-root", str(arbitrary)])
            except driver.LaunchRefused:
                return
        assert code != 0 or "run_root" not in captured, "arbitrary non-experiment run root reached the future pipeline"


def case_new_run_id_requires_allocated_random_suffix() -> None:
    for malformed in ("RUN-anything", "RUN-ECDLP-nothex", "RUN-ECDLP-123", "RUN-ECDLP-abcdef-extra"):
        try:
            driver.canonical_run_id(malformed)
        except driver.LaunchRefused:
            continue
        raise AssertionError(f"non-allocated run-id shape accepted: {malformed}")


def make_review_repo(*, receipt_commit_sha: str | None = None, include_attestation: bool = False) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str, dict[str, Any]]:
    holder = tempfile.TemporaryDirectory(prefix="validator-spectral-review-")
    root = Path(holder.name)
    run_git("init", "-q", "-b", "main", cwd=root)
    run_git("config", "user.name", "Validator Static", cwd=root)
    run_git("config", "user.email", "validator@example.test", cwd=root)
    (root / "producer.txt").write_text("fixed reviewed source\n", encoding="utf-8")
    run_git("add", "producer.txt", cwd=root)
    run_git("commit", "-q", "-m", "fixed source snapshot", cwd=root)
    reviewed = str(run_git("rev-parse", "HEAD", cwd=root, text=True))
    report_path = "reviews/TASK-fixed/review.yaml"
    receipt_path = "archives/TASK-fixed/snapshot.json"
    (root / report_path).parent.mkdir(parents=True)
    report: dict[str, Any] = {
        "validation_report": {
            "task_id": "TASK-fixed",
            "source_snapshot_commit": reviewed,
            "owned_joint_verdict": "PASS",
            "verdict": "passed",
        }
    }
    if include_attestation:
        report["review_attestation"] = {
            "task_id": "TASK-fixed", "joints_owned": ["fixed"], "sources_read": ["producer.txt"],
            "read_sibling_reports": False, "blind_from_respected": None, "verdict": "holds",
        }
    (root / report_path).write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    report_hash = sha256((root / report_path).read_bytes())
    (root / receipt_path).parent.mkdir(parents=True)
    receipt = {
        "task_id": "TASK-archive-fixed",
        "source_task_ids": ["TASK-fixed"],
        "commit_sha": receipt_commit_sha,
        "parent_sha": reviewed,
        "path_sha256": {report_path: report_hash},
    }
    (root / receipt_path).write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    run_git("add", report_path, receipt_path, cwd=root)
    run_git("commit", "-q", "-m", "fixed synthetic review archive", cwd=root)
    archive = str(run_git("rev-parse", "HEAD", cwd=root, text=True))
    admission = {
        "archive_receipt_path": receipt_path,
        "archive_receipt_sha256": sha256((root / receipt_path).read_bytes()),
        "archive_commit": archive,
        "review_task_id": "TASK-fixed",
        "review_report_path": report_path,
        "review_report_sha256": report_hash,
        "reviewed_source_snapshot": reviewed,
        "required_verdict": "PASS",
    }
    return holder, root, reviewed, archive, admission


def case_minimal_forged_pass_report_is_rejected() -> None:
    holder, root, reviewed, archive, admission = make_review_repo(include_attestation=False)
    try:
        with patched(driver, ROOT=root):
            try:
                driver.verify_review_admission(admission, reviewed, archive)
            except driver.LaunchRefused:
                return
        raise AssertionError("minimal PASS report without review attestation or independent-policy provenance was admitted")
    finally:
        holder.cleanup()


def case_false_archive_receipt_commit_is_rejected() -> None:
    holder, root, reviewed, archive, admission = make_review_repo(receipt_commit_sha="0" * 40, include_attestation=True)
    try:
        with patched(driver, ROOT=root):
            try:
                driver.verify_review_admission(admission, reviewed, archive)
            except driver.LaunchRefused:
                return
        raise AssertionError("archive receipt whose commit_sha does not name archive_commit was admitted")
    finally:
        holder.cleanup()


def case_review_hash_mismatch_is_rejected() -> None:
    holder, root, reviewed, archive, admission = make_review_repo(include_attestation=True)
    try:
        admission["review_report_sha256"] = "f" * 64
        with patched(driver, ROOT=root):
            try:
                driver.verify_review_admission(admission, reviewed, archive)
            except driver.LaunchRefused:
                return
        raise AssertionError("mismatched report hash was admitted")
    finally:
        holder.cleanup()


def case_review_wrong_source_snapshot_is_rejected() -> None:
    holder, root, reviewed, archive, admission = make_review_repo(include_attestation=True)
    try:
        with patched(driver, ROOT=root):
            try:
                driver.verify_review_admission(admission, "f" * 40, archive)
            except driver.LaunchRefused:
                return
        raise AssertionError("wrong reviewed-source snapshot was admitted")
    finally:
        holder.cleanup()


def case_empty_process_group_measurement_is_infrastructure_failure() -> None:
    class Result:
        stdout = ""

    with patched(driver.subprocess, run=lambda *args, **kwargs: Result()):
        try:
            driver.process_group_rss_bytes()
        except driver.InfrastructureStop:
            return
    raise AssertionError("empty ps measurement was accepted as zero-byte process-group RSS")


def case_guard_cancellation_precedes_rss_probe() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-spectral-guard-") as temporary:
        guard = driver.Guard(driver.ProgressSink(Path(temporary)), cancelled=True)
        with patched(driver, process_group_rss_bytes=lambda: (_ for _ in ()).throw(AssertionError("RSS probe should not run"))):
            try:
                guard.check()
            except driver.CancellationStop:
                return
    raise AssertionError("cancelled guard did not stop")


def case_guard_enforces_process_group_limit() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-spectral-guard-") as temporary:
        guard = driver.Guard(driver.ProgressSink(Path(temporary)), limit_bytes=100)
        with patched(driver, process_group_rss_bytes=lambda: 101):
            try:
                guard.check()
            except driver.ResourceStop:
                return
    raise AssertionError("RSS above limit did not stop")


def case_dense_relabel_path_has_guard_checkpoints() -> None:
    transition = function_node("transition_table")
    relabel = function_node("relabel_control")
    transition_args = [arg.arg for arg in transition.args.args]
    relabel_args = [arg.arg for arg in relabel.args.args]
    assert "check" in transition_args and "check" in relabel_args, "quadratic relabel/table work has no guard callback"
    for node in (transition, relabel):
        assert any(isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "check" for item in ast.walk(node))


def case_shuffle_construction_has_guard_checkpoints() -> None:
    node = function_node("deterministic_shuffle")
    assert "check" in [arg.arg for arg in node.args.args + node.args.kwonlyargs]
    assert any(isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "check" for item in ast.walk(node))


def case_cayley_fourier_guard_records_progress() -> None:
    node = function_node("cayley_fourier_eigenvalues")
    assert "on_progress" in [arg.arg for arg in node.args.args + node.args.kwonlyargs], "Fourier phase cannot receive progress sink"
    checkpoints = [item for item in ast.walk(node) if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "_cayley_checkpoint"]
    assert checkpoints
    assert all(not (isinstance(item.args[3], ast.Constant) and item.args[3].value is None) for item in checkpoints if len(item.args) >= 4)


def case_nested_cayley_progress_identifies_outer_position() -> None:
    source = ast.get_source_segment(DRIVER_TEXT, function_node("cayley_tv_curve")) or ""
    assert "requested_step" in source and "iteration" in source and "destination" in source, "nested progress records omit outer loop coordinates"


def case_resource_meter_records_single_terminal_bracket() -> None:
    meter = driver.ResourceMeter(
        started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=1),
        started_wall=time.monotonic() - 1,
        started_cpu=time.process_time(),
    )
    first = meter.snapshot()
    second = meter.snapshot()
    assert first == second
    assert first["timing"]["monotonic_finished"] >= first["timing"]["monotonic_started"]
    assert first["timing"]["finished_at"] >= first["timing"]["started_at"]


def case_future_run_cli_absent_lock_fails_closed() -> None:
    try:
        driver.verify_launch_admission(Path("/definitely/not/a/coordinator-lock.json"), "not-a-key")
    except driver.LaunchRefused:
        return
    raise AssertionError("absent lock did not fail closed")


def case_source_coverage_map_names_all_corrections() -> None:
    coverage = driver.protocol_coverage()
    for number in range(1, 10):
        assert f"F-{number:02d}" in " ".join(coverage)
    for number in range(1, 9):
        assert f"V-{number:02d}" in " ".join(coverage)
    assert "pooled_side_availability" in coverage


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


CASES = [
    Case("source_bindings_exact", case_source_bindings_exact),
    Case("bound_control_file_drift_isolated", case_bound_control_file_drift_isolated),
    Case("source_snapshot_exact_six_files", case_source_snapshot_exact_six_files),
    Case("snapshot_archive_exact_scope_and_receipt", case_snapshot_archive_exact_scope_and_receipt),
    Case("review_plan_precedes_claim", case_review_plan_precedes_claim),
    Case("claim_epoch_and_scope", case_claim_epoch_and_scope),
    Case("approval_and_amendment_chain", case_approval_and_amendment_chain),
    Case("execution_plan_binds_final_driver", case_execution_plan_binds_final_driver),
    Case("regression_receipt_is_bounded_and_final", case_regression_receipt_is_bounded_and_final),
    Case("rng_canonical_vector_and_n_one", case_rng_canonical_vector_and_n_one),
    Case("target_rng_uses_unscaled_tuple", case_target_rng_uses_unscaled_tuple),
    Case("control_rng_uses_frozen_u_zero_tuple", case_control_rng_uses_frozen_u_zero_tuple),
    Case("subgroup_repeated_addition_certificate", case_subgroup_repeated_addition_certificate),
    Case("fixture_path_records_rejections_before_selection", case_fixture_path_records_rejections_before_selection),
    Case("exploratory_precedes_heldout_and_decision_filters", case_exploratory_precedes_heldout_and_decision_filters),
    Case("positive_complete_panel", case_positive_complete_panel),
    Case("negative_is_cellwise", case_negative_is_cellwise),
    Case("missing_cell_refuses_complete_panel", case_missing_cell_refuses_complete_panel),
    Case("one_u_below_threshold_refuses_positive", case_one_u_below_threshold_refuses_positive),
    Case("one_curve_nonpositive_refuses_positive", case_one_curve_nonpositive_refuses_positive),
    Case("unavailable_cell_is_valid_inconclusive", case_unavailable_cell_is_valid_inconclusive),
    Case("invalid_cell_invalidates_panel", case_invalid_cell_invalidates_panel),
    Case("zero_yield_null_arm_remains_charged", case_zero_yield_null_arm_remains_charged),
    Case("zero_total_side_is_unavailable", case_zero_total_side_is_unavailable),
    Case("unequal_success_pool_is_total_work_over_total_success", case_unequal_success_pool_is_total_work_over_total_success),
    Case("all_named_validity_controls_reduce", case_all_named_validity_controls_reduce),
    Case("constant_o_executes_all_mock_starts", case_constant_o_executes_all_mock_starts),
    Case("first_invalid_cell_stops_next_cell", case_first_invalid_cell_stops_next_cell),
    Case("unavailable_fixture_is_inconclusive_not_implementation_invalid", case_unavailable_fixture_is_inconclusive_not_implementation_invalid),
    Case("implementation_exception_is_failed_implementation", case_implementation_exception_is_failed_implementation),
    Case("artifact_payload_has_complete_canonical_set", case_artifact_payload_has_complete_canonical_set),
    Case("costs_and_raw_bind_secondary_fields", case_costs_and_raw_bind_secondary_fields),
    Case("report_states_actual_coverage", case_report_states_actual_coverage),
    Case("report_binds_secondary_and_diagnostic_values", case_report_binds_secondary_and_diagnostic_values),
    Case("every_named_control_has_measured_diagnostic_cost", case_every_named_control_has_measured_diagnostic_cost),
    Case("terminal_utc_matches_monotonic_bracket", case_terminal_utc_matches_monotonic_bracket),
    Case("atomic_success_and_package_hashes", case_atomic_success_and_package_hashes),
    Case("missing_payload_never_exposes_final", case_missing_payload_never_exposes_final),
    Case("postrename_fsync_failure_quarantines", case_postrename_fsync_failure_quarantines),
    Case("failed_failure_receipt_is_not_called_annotated", case_failed_failure_receipt_is_not_called_annotated),
    Case("run_root_is_fixed_to_experiment_directory", case_run_root_is_fixed_to_experiment_directory),
    Case("new_run_id_requires_allocated_random_suffix", case_new_run_id_requires_allocated_random_suffix),
    Case("minimal_forged_pass_report_is_rejected", case_minimal_forged_pass_report_is_rejected),
    Case("false_archive_receipt_commit_is_rejected", case_false_archive_receipt_commit_is_rejected),
    Case("review_hash_mismatch_is_rejected", case_review_hash_mismatch_is_rejected),
    Case("review_wrong_source_snapshot_is_rejected", case_review_wrong_source_snapshot_is_rejected),
    Case("empty_process_group_measurement_is_infrastructure_failure", case_empty_process_group_measurement_is_infrastructure_failure),
    Case("guard_cancellation_precedes_rss_probe", case_guard_cancellation_precedes_rss_probe),
    Case("guard_enforces_process_group_limit", case_guard_enforces_process_group_limit),
    Case("dense_relabel_path_has_guard_checkpoints", case_dense_relabel_path_has_guard_checkpoints),
    Case("shuffle_construction_has_guard_checkpoints", case_shuffle_construction_has_guard_checkpoints),
    Case("cayley_fourier_guard_records_progress", case_cayley_fourier_guard_records_progress),
    Case("nested_cayley_progress_identifies_outer_position", case_nested_cayley_progress_identifies_outer_position),
    Case("resource_meter_records_single_terminal_bracket", case_resource_meter_records_single_terminal_bracket),
    Case("future_run_cli_absent_lock_fails_closed", case_future_run_cli_absent_lock_fails_closed),
    Case("source_coverage_map_names_all_corrections", case_source_coverage_map_names_all_corrections),
]


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("case exceeded 10 seconds")


def live_drift() -> list[dict[str, str]]:
    handoff = yaml.safe_load(git_show(AUTHORITY_COMMIT, HANDOFF_PATH))["handoff"]
    expected = {row["path"]: row["sha256"] for row in handoff["source_bindings"]}
    drift: list[dict[str, str]] = []
    for path, bound_hash in expected.items():
        live = ROOT / path
        if live.is_file():
            current = sha256(live.read_bytes())
            if current != bound_hash:
                drift.append({"path": path, "authority_sha256": bound_hash, "live_sha256": current})
    return drift


def main() -> int:
    requested = sys.argv[1:]
    selected = CASES
    if requested:
        by_name = {case.name: case for case in CASES}
        unknown = [name for name in requested if name not in by_name]
        if unknown:
            raise RuntimeError(f"unknown cases: {unknown}")
        selected = [by_name[name] for name in requested]
    if len(selected) > 60:
        raise RuntimeError("case count exceeds handoff ceiling")
    signal.signal(signal.SIGALRM, timeout_handler)
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    results: list[dict[str, Any]] = []
    for case in selected:
        case_wall = time.monotonic()
        case_cpu = time.process_time()
        signal.alarm(10)
        try:
            case.action()
        except Exception as exc:
            outcome = "FAIL"
            detail = f"{type(exc).__name__}: {exc}"
        else:
            outcome = "PASS"
            detail = "obligation held in this fixed case"
        finally:
            signal.alarm(0)
        results.append({
            "name": case.name,
            "outcome": outcome,
            "detail": detail,
            "wall_seconds": round(time.monotonic() - case_wall, 6),
            "cpu_seconds": round(time.process_time() - case_cpu, 6),
        })
    failed = [row for row in results if row["outcome"] == "FAIL"]
    output = {
        "schema": "crypto.autoresearch.validator_fixed_checks.v1",
        "task_id": TASK_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "source_snapshot_commit": SOURCE_SNAPSHOT,
        "claim_commit": CLAIM_COMMIT,
        "case_executions": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "maximum_case_wall_seconds": max((row["wall_seconds"] for row in results), default=0.0),
        "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in results), default=0.0),
        "script_wall_seconds": round(time.monotonic() - started_wall, 6),
        "script_cpu_seconds": round(time.process_time() - started_cpu, 6),
        "limits": {"maximum_cases_including_reruns": 60, "maximum_seconds_per_case": 10, "maximum_workers": 1, "memory_gib": 2, "scientific_runs": 0},
        "forbidden_work_executed": {
            "fixture_selection": 0,
            "frozen_candidate_search": 0,
            "collision_census": 0,
            "cayley_calibration": 0,
            "experimental_control_or_timing_panel": 0,
            "future_run_cli": 0,
        },
        "synthetic_mock_pipeline_calls": 3 if not requested else 0,
        "mocked_future_run_entrypoint_calls": 1 if not requested else 0,
        "actual_future_run_calls": 0,
        "live_drift_from_authority_bindings": live_drift(),
        "results": results,
    }
    print(json.dumps(output, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Bounded independent admission checks for TASK-20260907-2fd901.

This script executes fixed static, arithmetic, synthetic, and mock cases only.
It never calls fixture selection, the frozen curve/collision census, the
Cayley calibration, the experimental control/timing panel, or future-run.
Each named case is serial and has a ten-second alarm.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import importlib.util
import inspect
import io
import json
import math
import os
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml


HERE = Path(__file__).resolve()
REPO = next(parent for parent in HERE.parents if (parent / "AGENTS.md").is_file())
TASK_ID = "TASK-20260907-2fd901"
CLAIM_COMMIT = "b0a8d28e9b4dbc43e5af143a44de4eea347e0705"
PLAN_COMMIT = "baefa00db9140147c9cbf11e239310bd299c37d3"
SNAPSHOT_COMMIT = "82ab1e7b3a7532158b89b626e2e7511ca416014b"
HANDOFF_PATH = REPO / "ledger/handoffs/TASK-20260907-2fd901.yaml"
PLAN_PATH = REPO / "coordination/experiment-reserve/BATCH-1bb183/review-plan-TASK-20260907-2fd901.yaml"
IMPLEMENTATION = REPO / "experiments/EXP-ECDLP-651b94/implementation/TASK-20260907-fde47b"
DRIVER_PATH = IMPLEMENTATION / "driver.py"

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("spectral_corrected_driver_review", DRIVER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load corrected driver")
driver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = driver
spec.loader.exec_module(driver)


def run_git(*args: str, cwd: Path = REPO, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def git_bytes(commit: str, relative: str) -> bytes:
    return run_git("show", f"{commit}:{relative}").stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    }


def controls(
    *, cayley: bool = True, relabel: bool = True, occupancy: bool = True,
    zero_denominators: int = 0, solves: int = 0, mutation: bool = True,
) -> dict[str, Any]:
    return {
        "cayley": {"passed": cayley, "gap": "0.1"},
        "relabel": relabel,
        "occupancy": occupancy,
        "known_false": {
            "constant_o": {"nonzero_denominators": zero_denominators, "solves": solves, "collisions": []},
            "mutated_candidate_fails_certificate": mutation,
        },
    }


def synthetic_cell(curve_id: str, seed: int, u: int, d: float | None, *, valid: bool = True) -> dict[str, Any]:
    return {
        "curve_id": curve_id,
        "seed": seed,
        "u": u,
        "metric": {"available": d is not None, "d": d},
        "validity": {"valid": valid},
        "coordinate": arm(10, 2),
        "nulls": [{**arm(12, 2), "arm": index} for index in range(1, 8)],
        "controls": controls(),
    }


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


def artifact_payload(*, wall_age: float = 0.0, cells: list[dict[str, Any]] | None = None) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="spectral-review-artifacts-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.fixtures = [{"p": 17, "B": 2}]
        sink.rejected = [{"p": 17, "B": 1, "reason": "mock"}]
        sink.cells = list(cells or [])
        meter = driver.ResourceMeter()
        meter.started_wall -= wall_age
        lock = {"run_id": "RUN-ECDLP-deadbe"}
        provenance = {"commit": "a" * 40, "dirty": False, "command": "fixed synthetic command"}
        with patched(driver, process_group_rss_bytes=lambda: 123456):
            return driver.artifact_bytes(
                lock=lock, provenance=provenance, meter=meter, sink=sink,
                status="completed_valid", error=None,
                decision={"branch": "inconclusive", "reasons": [], "per_u": {}, "panel_valid": True},
            )


def complete_payload() -> dict[str, bytes]:
    return {name: (name + "\n").encode("utf-8") for name in driver.EXPERIMENT_ARTIFACTS[:-1]}


def case_source_bindings_exact() -> None:
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))["handoff"]
    mismatches: list[str] = []
    for binding in handoff["source_bindings"]:
        relative = binding["path"]
        if relative in {"tools/validate_ledger.py", "tools/research_dispatch.py"}:
            payload = git_bytes(PLAN_COMMIT, relative)
        elif binding.get("snapshot_commit"):
            if binding["snapshot_commit"] != SNAPSHOT_COMMIT:
                mismatches.append(f"{relative}: unexpected snapshot {binding['snapshot_commit']}")
                continue
            payload = git_bytes(SNAPSHOT_COMMIT, relative)
        else:
            payload = (REPO / relative).read_bytes()
        if digest(payload) != binding["sha256"]:
            mismatches.append(f"{relative}: {digest(payload)} != {binding['sha256']}")
    if mismatches:
        raise AssertionError("; ".join(mismatches))


def case_snapshot_archive_commit_scope() -> None:
    expected = {
        "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260907-916ec4/snapshot.json",
        *{f"experiments/EXP-ECDLP-651b94/implementation/TASK-20260907-fde47b/{name}" for name in (
            "driver.py", "tests.py", "README.md", "implementation-report.yaml",
            "execution-plan.json", "regression-receipt.json",
        )},
    }
    changed = set(run_git("diff-tree", "--no-commit-id", "--name-only", "-r", SNAPSHOT_COMMIT).stdout.decode().splitlines())
    if changed != expected:
        raise AssertionError(f"snapshot changed paths differ: {sorted(changed ^ expected)}")
    run_git("merge-base", "--is-ancestor", SNAPSHOT_COMMIT, "HEAD")


def case_plan_precommitted_before_claim() -> None:
    if digest(git_bytes(PLAN_COMMIT, str(PLAN_PATH.relative_to(REPO)))) != "19bfcbfb4546990a3ce22fd07591218eeac3280406608bb66013481ce5e8e10c":
        raise AssertionError("precommitted review-plan hash differs")
    run_git("merge-base", "--is-ancestor", PLAN_COMMIT, CLAIM_COMMIT)
    run_git("merge-base", "--is-ancestor", CLAIM_COMMIT, "HEAD")


def case_rng_exact_serialization_vector() -> None:
    params = (17, 1, 2, 19, 0, 3, 7)
    frozen = b'["EXP-ECDLP-651b94","shuffle",[17,1,2,19,0,3,7],606315,9]'
    expected = int.from_bytes(hashlib.sha256(frozen).digest(), "big")
    actual = driver.stream_digest(purpose="shuffle", params=params, seed=606315, counter=9)
    if actual != expected:
        raise AssertionError("SHA-256 stream serialization differs from frozen bytes")


def case_rng_n_one_consumes_digest() -> None:
    result = driver.rejection_draw(purpose="query", params=(17, 1, 2, 19, 0, 0, 0), seed=3, counter=11, n=1)
    if result != (0, 12):
        raise AssertionError(f"n=1 returned {result}")


def case_singular_rejection_precedes_curve_construction() -> None:
    source = inspect.getsource(driver.fixture_scan)
    if source.index("discriminator == 0") >= source.index("curve = Curve"):
        raise AssertionError("singular candidate reaches Curve construction")
    if "on_rejection(record)" not in source:
        raise AssertionError("singular rejection is not emitted to progressive custody")


def case_fixture_selection_has_progress_callbacks() -> None:
    source = inspect.getsource(driver.select_fixtures)
    for needle in ("record_rejection", "record_selection", "all_rejected.extend(discards)"):
        if needle not in source:
            raise AssertionError(f"fixture custody path missing {needle}")


def case_subgroup_enumeration_uses_frozen_repeated_addition() -> None:
    source = inspect.getsource(driver.subgroup_points)
    if "curve.scalar(scalar, generator)" in source or "curve.add(current, generator)" not in source:
        raise AssertionError("subgroup_points recomputes each multiple with scalar multiplication instead of frozen repeated addition")


def case_all_sixteen_seed_streams_are_executable() -> None:
    source = inspect.getsource(driver.run_future_pipeline)
    if not hasattr(driver, "EXPLORATORY_SEEDS") or "EXPLORATORY_SEEDS" not in source:
        raise AssertionError("future pipeline executes only held-out 606308..606315 and omits exploratory 606300..606307")


def case_coefficient_recovery_identity() -> None:
    r, secret = 101, 37
    old_a, old_b, new_b = 81, 4, 19
    new_a = (old_a + secret * (old_b - new_b)) % r
    recovered = ((old_a - new_a) * pow((new_b - old_b) % r, -1, r)) % r
    if recovered != secret:
        raise AssertionError("independent coefficient recovery identity failed")


class CyclicMock:
    def __init__(self, modulus: int):
        self.modulus = modulus

    def add(self, left: int | None, right: int | None) -> int | None:
        left_value = 0 if left is None else left
        right_value = 0 if right is None else right
        value = (left_value + right_value) % self.modulus
        return None if value == 0 else value


def case_binary_verifier_exact_operation_charge() -> None:
    curve = CyclicMock(101)
    result, additions, doublings = driver.binary_verifier(curve, 37, 1)
    if result != 37 or additions != bin(37).count("1") or doublings != len(bin(37)) - 2:
        raise AssertionError((result, additions, doublings))


def case_constant_o_executes_every_mock_start() -> None:
    result = driver.constant_o_census([None, (1, 1), (2, 2), (3, 3)], lambda: None)
    if not result["passed"] or result["starts"] != 4 or len(result["collisions"]) != 4:
        raise AssertionError("constant-O mock census did not retain every start")
    if result["nonzero_denominators"] or result["solves"]:
        raise AssertionError("constant-O known-false control proved too much")


def case_failed_certificate_invalidates() -> None:
    reduced = driver.reduce_validity(arm(10, 0, failed=1), [arm(10, 1)] * 7, controls())
    if reduced["valid"] or reduced["certificate_failures"] != 1:
        raise AssertionError("failed certificate was reduced as valid/fruitless")


def case_zero_yield_null_arm_remains_charged() -> None:
    metric = driver.cell_difference(arm(50, 10), [arm(100, 0)] + [arm(60, 10) for _ in range(6)])
    if not metric["available"] or metric["pooled_null_work"] != 460 or metric["pooled_null_successes"] != 60:
        raise AssertionError(metric)


def case_zero_total_side_is_unavailable() -> None:
    coordinate_zero = driver.cell_difference(arm(40, 0), [arm(50, 5)] * 7)
    null_zero = driver.cell_difference(arm(40, 4), [arm(50, 0)] * 7)
    if coordinate_zero["available"] or null_zero["available"]:
        raise AssertionError("zero-success side produced a finite inferential cell")


def case_unequal_success_null_is_pooled_by_work_and_success() -> None:
    nulls = [arm(10, 10), arm(99, 1)] + [arm(10, 10) for _ in range(5)]
    work, successes, cost = driver.pooled_null_cost(nulls)
    if (work, successes) != (159, 61) or not math.isclose(float(cost), 159 / 61):
        raise AssertionError((work, successes, cost))


def full_panel(value: float = 0.2) -> list[dict[str, Any]]:
    return [synthetic_cell(f"curve-{curve}", seed, u, value) for curve in range(4) for seed in driver.HELDOUT_SEEDS for u in driver.US]


def case_all_u_positive_conjunction() -> None:
    decision = driver.global_decision(full_panel(0.2))
    if decision["branch"] != "positive" or not decision["panel_valid"]:
        raise AssertionError(decision)


def case_missing_cell_refuses_complete_panel_verdict() -> None:
    cells = full_panel(0.2)
    cells.pop()
    decision = driver.global_decision(cells)
    if decision["branch"] != "inconclusive" or decision["panel_valid"]:
        raise AssertionError(decision)


def case_one_coordinate_below_threshold_is_inconclusive() -> None:
    cells = full_panel(0.2)
    for row in cells:
        if row["u"] == 3:
            row["metric"]["d"] = 0.17
    if driver.global_decision(cells)["branch"] != "inconclusive":
        raise AssertionError("best-u selection or voting admitted a positive")


def case_one_curve_nonpositive_mean_is_inconclusive() -> None:
    cells = full_panel(0.25)
    for row in cells:
        if row["u"] == 3 and row["curve_id"] == "curve-0":
            row["metric"]["d"] = 0.0
    if driver.global_decision(cells)["branch"] != "inconclusive":
        raise AssertionError("strict curve-mean control was not enforced")


def case_named_control_failure_invalidates() -> None:
    reduced = driver.reduce_validity(arm(1, 1), [arm(1, 1)] * 7, controls(cayley=False, solves=1))
    if reduced["valid"] or set(reduced["failed_controls"]) != {"cayley_exact", "constant_o_zero_solves"}:
        raise AssertionError(reduced)


def case_pipeline_stops_after_first_invalid_cell() -> None:
    fixtures = {
        9: [{"curve_id": "curve-0", "p": 17, "B": 1}, {"curve_id": "curve-1", "p": 19, "B": 2}],
        11: [{"curve_id": "curve-2", "p": 23, "B": 3}, {"curve_id": "curve-3", "p": 29, "B": 4}],
    }
    calls: list[tuple[str, int, int]] = []
    captured: dict[str, Any] = {}

    def fake_cell(fixture: dict[str, Any], seed: int, u: int, check: Callable[[], None], on_partial: Any = None) -> dict[str, Any]:
        calls.append((fixture["curve_id"], seed, u))
        return synthetic_cell(fixture["curve_id"], seed, u, -0.1, valid=False)

    def fake_artifact_bytes(**kwargs: Any) -> dict[str, bytes]:
        captured.update({"status": kwargs["status"], "cells": len(kwargs["sink"].cells)})
        return {}

    def memory_record_cell(sink: Any, record: dict[str, Any]) -> None:
        sink.cells.append(record)

    with tempfile.TemporaryDirectory(prefix="spectral-review-pipeline-") as temporary:
        with patched(
            driver,
            select_fixtures=lambda check, sink=None: (fixtures, []),
            future_cell=fake_cell,
            artifact_bytes=fake_artifact_bytes,
            atomic_publish=lambda run_root, run_id, payload: {},
            execution_provenance=lambda command: {"commit": "a" * 40, "dirty": False, "command": command},
        ), patched(driver.Guard, check=lambda self: None), patched(driver.ProgressSink, record_cell=memory_record_cell):
            driver.run_future_pipeline({"run_id": "RUN-ECDLP-deadbe"}, Path(temporary), "mock-only")
    if len(calls) != 1:
        raise AssertionError(f"named control/certificate invalidity did not stop the panel; {len(calls)} mock cells executed")
    if captured.get("status") != "completed_invalid":
        raise AssertionError(captured)


def case_manifest_and_companions_are_canonical() -> None:
    payload = artifact_payload(cells=[synthetic_cell("curve-0", 606308, 1, 0.1)])
    if set(payload) != set(driver.EXPERIMENT_ARTIFACTS[:-1]):
        raise AssertionError("artifact_bytes does not create the twelve canonical payload files")
    manifest = yaml.safe_load(payload["manifest.yaml"])["run"]
    for path in ("command.txt", "environment.json", "raw-result.json", "stdout.log", "stderr.log"):
        if path not in payload:
            raise AssertionError(f"missing {path}")
    if not manifest["code"].get("commit") or not manifest["code"].get("command") or "cpu_seconds" not in manifest["resources"]:
        raise AssertionError("minimum manifest provenance/resource fields missing")


def case_complete_diagnostic_custody() -> None:
    payload = artifact_payload(cells=[synthetic_cell("curve-0", 606308, 1, 0.1)])
    reader = csv.DictReader(io.StringIO(payload["costs.csv"].decode("utf-8")))
    fields = set(reader.fieldnames or [])
    required_cost = {
        "scalar_inversions", "scalar_comparisons", "diagnostic_wall_seconds",
        "diagnostic_cpu_seconds", "collision_table_peak_bytes",
    }
    missing_cost = sorted(required_cost - fields)
    raw = json.loads(payload["raw-result.json"])
    required_secondary = {
        "mean_first_repeat_length", "useful_fraction", "fixed_points",
        "two_cycles", "component_sizes", "max_tail_length", "max_cycle_length",
    }
    metrics = raw.get("metrics", {})
    missing_secondary = sorted(required_secondary - set(metrics))
    if missing_cost or missing_secondary:
        raise AssertionError(f"missing per-diagnostic custody cost={missing_cost} secondary={missing_secondary}")


def case_manifest_utc_interval_matches_measured_wall() -> None:
    payload = artifact_payload(wall_age=10.0)
    timing = yaml.safe_load(payload["manifest.yaml"])["run"]["timing"]
    started = datetime.fromisoformat(timing["started_at"])
    finished = datetime.fromisoformat(timing["finished_at"])
    utc_delta = (finished - started).total_seconds()
    if abs(utc_delta - float(timing["wall_seconds"])) > 0.5:
        raise AssertionError(f"UTC interval {utc_delta}s does not bracket measured wall {timing['wall_seconds']}s")


def case_atomic_success_exposes_only_complete_final() -> None:
    with tempfile.TemporaryDirectory(prefix="spectral-review-publish-") as temporary:
        root = Path(temporary)
        hashes = driver.atomic_publish(root, "RUN-ECDLP-deadbe", complete_payload())
        final = root / "runs/RUN-ECDLP-deadbe"
        if set(path.name for path in final.iterdir()) != set(driver.EXPERIMENT_ARTIFACTS):
            raise AssertionError("successful atomic publish exposed an incomplete final set")
        if len(hashes) != 12:
            raise AssertionError("published hash inventory omitted payload files")


def case_atomic_missing_payload_is_refused_before_final() -> None:
    payload = complete_payload()
    payload.pop("raw-result.json")
    with tempfile.TemporaryDirectory(prefix="spectral-review-publish-") as temporary:
        root = Path(temporary)
        try:
            driver.atomic_publish(root, "RUN-ECDLP-deadbe", payload)
        except ValueError:
            pass
        else:
            raise AssertionError("missing canonical artifact was published")
        if (root / "runs/RUN-ECDLP-deadbe").exists():
            raise AssertionError("missing-artifact known-false object created final directory")


def case_postrename_fsync_failure_leaves_no_final_directory() -> None:
    calls = 0

    def fail_after_rename(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("fixed post-rename directory fsync failure")

    with tempfile.TemporaryDirectory(prefix="spectral-review-publish-") as temporary:
        root = Path(temporary)
        with patched(driver, fsync_directory=fail_after_rename):
            try:
                driver.atomic_publish(root, "RUN-ECDLP-deadbe", complete_payload())
            except driver.InfrastructureStop:
                pass
            else:
                raise AssertionError("injected post-rename failure was not classified")
        final = root / "runs/RUN-ECDLP-deadbe"
        if final.exists():
            raise AssertionError("publication reported failure but left the canonical final directory exposed")


def case_completed_looking_incomplete_final_is_refused() -> None:
    with tempfile.TemporaryDirectory(prefix="spectral-review-publish-") as temporary:
        root = Path(temporary)
        final = root / "runs/RUN-ECDLP-deadbe"
        final.mkdir(parents=True)
        (final / "manifest.yaml").write_text("run: {}\n", encoding="utf-8")
        try:
            driver.atomic_publish(root, "RUN-ECDLP-deadbe", complete_payload())
        except driver.LaunchRefused:
            return
        raise AssertionError("completed-looking incomplete final directory was accepted")


def case_arbitrary_hash_bound_text_is_not_a_review() -> None:
    try:
        driver.verify_review_admission({}, SNAPSHOT_COMMIT)
    except driver.LaunchRefused:
        return
    raise AssertionError("empty/arbitrary review admission was accepted")


def make_review_git() -> tuple[tempfile.TemporaryDirectory[str], Path, str, str, dict[str, Any]]:
    holder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="spectral-review-git-")
    root = Path(holder.name)
    run_git("init", "-q", "-b", "main", cwd=root)
    run_git("config", "user.name", "Validator Test", cwd=root)
    run_git("config", "user.email", "validator@example.test", cwd=root)
    (root / "producer.txt").write_text("corrected source\n", encoding="utf-8")
    run_git("add", "producer.txt", cwd=root)
    run_git("commit", "-q", "-m", "producer snapshot", cwd=root)
    source_commit = run_git("rev-parse", "HEAD", cwd=root).stdout.decode().strip()
    report_rel = "reviews/TASK-review/review.yaml"
    receipt_rel = "archives/TASK-archive/snapshot.json"
    (root / report_rel).parent.mkdir(parents=True)
    report = {
        "validation_report": {
            "task_id": "TASK-review", "source_snapshot_commit": source_commit,
            "owned_joint_verdict": "PASS", "verdict": "passed",
        }
    }
    (root / report_rel).write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    report_hash = digest((root / report_rel).read_bytes())
    (root / receipt_rel).parent.mkdir(parents=True)
    receipt = {"source_task_ids": ["TASK-review"], "path_sha256": {report_rel: report_hash}}
    (root / receipt_rel).write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    run_git("add", report_rel, receipt_rel, cwd=root)
    run_git("commit", "-q", "-m", "archive independent review", cwd=root)
    archive_commit = run_git("rev-parse", "HEAD", cwd=root).stdout.decode().strip()
    admission = {
        "archive_receipt_path": receipt_rel,
        "archive_receipt_sha256": digest((root / receipt_rel).read_bytes()),
        "archive_commit": archive_commit,
        "review_task_id": "TASK-review",
        "review_report_path": report_rel,
        "review_report_sha256": report_hash,
        "corrected_source_snapshot": source_commit,
        "required_verdict": "PASS",
    }
    return holder, root, source_commit, archive_commit, admission


def case_archive_head_can_admit_report_bound_to_source_snapshot() -> None:
    holder, root, source_commit, archive_commit, admission = make_review_git()
    original_root = driver.ROOT
    try:
        driver.ROOT = root
        try:
            # verify_launch_admission passes current HEAD as corrected_snapshot.
            driver.verify_review_admission(admission, archive_commit)
        except driver.LaunchRefused as exc:
            raise AssertionError(f"archive HEAD cannot admit its report bound to producer source {source_commit}: {exc}") from exc
    finally:
        driver.ROOT = original_root
        holder.cleanup()


def case_source_head_can_reach_the_review_archive() -> None:
    holder, root, source_commit, _archive_commit, admission = make_review_git()
    original_root = driver.ROOT
    try:
        run_git("checkout", "-q", "--detach", source_commit, cwd=root)
        driver.ROOT = root
        try:
            driver.verify_review_admission(admission, source_commit)
        except driver.LaunchRefused as exc:
            raise AssertionError(f"producer source HEAD cannot reach later review archive: {exc}") from exc
    finally:
        driver.ROOT = original_root
        holder.cleanup()


def case_run_id_traversal_is_rejected() -> None:
    for bad in ("RUN-../escape", "RUN-..\\escape", "not-a-run", ".."):
        try:
            driver.canonical_run_id(bad)
        except driver.LaunchRefused:
            continue
        raise AssertionError(f"unsafe run id accepted: {bad}")


def case_guard_cancellation_precedes_rss_probe() -> None:
    with tempfile.TemporaryDirectory(prefix="spectral-review-guard-") as temporary:
        guard = driver.Guard(driver.ProgressSink(Path(temporary)), cancelled=True)
        with patched(driver, process_group_rss_bytes=lambda: (_ for _ in ()).throw(AssertionError("RSS probed after cancellation"))):
            try:
                guard.check()
            except driver.CancellationStop:
                return
    raise AssertionError("cancellation did not stop at checkpoint")


def case_guard_enforces_process_group_memory() -> None:
    with tempfile.TemporaryDirectory(prefix="spectral-review-guard-") as temporary:
        guard = driver.Guard(driver.ProgressSink(Path(temporary)), limit_bytes=100)
        with patched(driver, process_group_rss_bytes=lambda: 101):
            try:
                guard.check()
            except driver.ResourceStop:
                return
    raise AssertionError("process-group RSS over limit was accepted")


def case_cayley_dense_work_has_bounded_cancellation_checks() -> None:
    weights = inspect.getsource(driver.cayley_weights)
    control = inspect.getsource(driver.cayley_control)
    tv = inspect.getsource(driver.cayley_tv_curve)
    if "check" not in inspect.signature(driver.cayley_weights).parameters:
        raise AssertionError("dense r-by-r Cayley allocation has no cancellation/RSS callback")
    if "for origin in range(r)" in tv and "check" not in tv.split("for origin in range(r)")[0].splitlines()[-1]:
        raise AssertionError("dense Cayley matrix multiply lacks inner-loop checkpoints")
    if "rows = [sum(row)" in control or "columns = [sum(" in control:
        raise AssertionError("dense row/column reductions lack bounded checkpoints")
    if not weights:
        raise AssertionError("unreachable")


def case_missing_launch_lock_fails_closed() -> None:
    try:
        driver.verify_launch_admission(Path("/definitely/not/a/coordinator-lock"), "not-a-key")
    except driver.LaunchRefused:
        return
    raise AssertionError("missing future authority was accepted")


CASES: list[tuple[str, Callable[[], None]]] = [
    ("source_bindings_exact", case_source_bindings_exact),
    ("snapshot_archive_commit_scope", case_snapshot_archive_commit_scope),
    ("plan_precommitted_before_claim", case_plan_precommitted_before_claim),
    ("rng_exact_serialization_vector", case_rng_exact_serialization_vector),
    ("rng_n_one_consumes_digest", case_rng_n_one_consumes_digest),
    ("singular_rejection_precedes_curve_construction", case_singular_rejection_precedes_curve_construction),
    ("fixture_selection_has_progress_callbacks", case_fixture_selection_has_progress_callbacks),
    ("subgroup_enumeration_uses_frozen_repeated_addition", case_subgroup_enumeration_uses_frozen_repeated_addition),
    ("all_sixteen_seed_streams_are_executable", case_all_sixteen_seed_streams_are_executable),
    ("coefficient_recovery_identity", case_coefficient_recovery_identity),
    ("binary_verifier_exact_operation_charge", case_binary_verifier_exact_operation_charge),
    ("constant_o_executes_every_mock_start", case_constant_o_executes_every_mock_start),
    ("failed_certificate_invalidates", case_failed_certificate_invalidates),
    ("zero_yield_null_arm_remains_charged", case_zero_yield_null_arm_remains_charged),
    ("zero_total_side_is_unavailable", case_zero_total_side_is_unavailable),
    ("unequal_success_null_is_pooled_by_work_and_success", case_unequal_success_null_is_pooled_by_work_and_success),
    ("all_u_positive_conjunction", case_all_u_positive_conjunction),
    ("missing_cell_refuses_complete_panel_verdict", case_missing_cell_refuses_complete_panel_verdict),
    ("one_coordinate_below_threshold_is_inconclusive", case_one_coordinate_below_threshold_is_inconclusive),
    ("one_curve_nonpositive_mean_is_inconclusive", case_one_curve_nonpositive_mean_is_inconclusive),
    ("named_control_failure_invalidates", case_named_control_failure_invalidates),
    ("pipeline_stops_after_first_invalid_cell", case_pipeline_stops_after_first_invalid_cell),
    ("manifest_and_companions_are_canonical", case_manifest_and_companions_are_canonical),
    ("complete_diagnostic_custody", case_complete_diagnostic_custody),
    ("manifest_utc_interval_matches_measured_wall", case_manifest_utc_interval_matches_measured_wall),
    ("atomic_success_exposes_only_complete_final", case_atomic_success_exposes_only_complete_final),
    ("atomic_missing_payload_is_refused_before_final", case_atomic_missing_payload_is_refused_before_final),
    ("postrename_fsync_failure_leaves_no_final_directory", case_postrename_fsync_failure_leaves_no_final_directory),
    ("completed_looking_incomplete_final_is_refused", case_completed_looking_incomplete_final_is_refused),
    ("arbitrary_hash_bound_text_is_not_a_review", case_arbitrary_hash_bound_text_is_not_a_review),
    ("archive_head_can_admit_report_bound_to_source_snapshot", case_archive_head_can_admit_report_bound_to_source_snapshot),
    ("source_head_can_reach_the_review_archive", case_source_head_can_reach_the_review_archive),
    ("run_id_traversal_is_rejected", case_run_id_traversal_is_rejected),
    ("guard_cancellation_precedes_rss_probe", case_guard_cancellation_precedes_rss_probe),
    ("guard_enforces_process_group_memory", case_guard_enforces_process_group_memory),
    ("cayley_dense_work_has_bounded_cancellation_checks", case_cayley_dense_work_has_bounded_cancellation_checks),
    ("missing_launch_lock_fails_closed", case_missing_launch_lock_fails_closed),
]


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed case exceeded 10 seconds")


def main() -> int:
    signal.signal(signal.SIGALRM, timeout_handler)
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    results: list[dict[str, Any]] = []
    for name, function in CASES:
        case_wall = time.monotonic()
        case_cpu = time.process_time()
        signal.alarm(10)
        try:
            function()
        except Exception as exc:
            status = "FAIL"
            detail = f"{type(exc).__name__}: {exc}"
        else:
            status = "PASS"
            detail = ""
        finally:
            signal.alarm(0)
        results.append({
            "name": name,
            "status": status,
            "detail": detail,
            "wall_seconds": round(time.monotonic() - case_wall, 6),
            "cpu_seconds": round(time.process_time() - case_cpu, 6),
        })
    summary = {
        "schema": "crypto.autoresearch.validator_static_checks.v1",
        "task_id": TASK_ID,
        "case_executions": len(results),
        "passed": sum(row["status"] == "PASS" for row in results),
        "failed": sum(row["status"] == "FAIL" for row in results),
        "errors": 0,
        "scientific_runs": 0,
        "forbidden_panels_invoked": 0,
        "maximum_workers": 1,
        "maximum_seconds_per_case": 10,
        "aggregate_wall_seconds": round(time.monotonic() - started_wall, 6),
        "aggregate_cpu_seconds": round(time.process_time() - started_cpu, 6),
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

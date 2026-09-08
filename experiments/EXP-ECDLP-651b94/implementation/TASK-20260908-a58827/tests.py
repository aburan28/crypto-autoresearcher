#!/usr/bin/env python3
"""Fixed static/synthetic/mock regression for TASK-20260908-111152.

The suite calls only lower-level deterministic helpers, synthetic artifact
serialization, failure custody, process telemetry parsing, and a temporary Git
review graph. It never calls fixture selection, a census, a control/timing
panel, the prospective pipeline, a lock verifier, or the measurement CLI.
"""
from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import inspect
import io
import json
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import driver  # noqa: E402


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def synthetic_arm(*, successes: int = 1) -> dict[str, Any]:
    return {
        "starts": 1, "successes": successes, "failed_certificates": 0,
        "transition_group_operations": 3, "verification_group_operations": 2,
        "group_additions": 2, "group_doublings": 1, "charged_cost": 5 / successes if successes else None,
        "secondary": {"mean_first_repeat_length": 2.0, "useful_fraction": float(successes), "fixed_points": 1, "two_cycles": 0, "component_sizes": [1], "max_tail_length": 0, "max_cycle_length": 1},
        "diagnostic_costs": {"diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.005, "collision_table_peak_bytes": 64, "scalar_inversions": 1, "scalar_comparisons": 1},
        "certificates": [],
    }


def synthetic_cell(stream: str = "exploratory") -> dict[str, Any]:
    coordinate = synthetic_arm()
    return {
        "curve_id": "fixed-curve", "seed": 606300, "u": 1, "stream": stream,
        "coordinate": coordinate, "nulls": [{**synthetic_arm(), "arm": index} for index in range(1, 8)],
        "metric": {"available": True, "d": 0.2},
        "controls": {"cayley": {"gap": "0.1"}, "known_false": {"constant_o": {"collisions": []}}},
        "validity": {"valid": True},
        "diagnostic_costs": {
            "relabel_table": {"diagnostic": "relabel_table", "diagnostic_wall_seconds": 0.02, "diagnostic_cpu_seconds": 0.01, "completed": True},
            "relabel_control": {"diagnostic": "relabel_control", "diagnostic_wall_seconds": 0.03, "diagnostic_cpu_seconds": 0.015, "completed": True},
            "constant_o_census": {"diagnostic": "constant_o_census", "diagnostic_wall_seconds": 0.04, "diagnostic_cpu_seconds": 0.02, "completed": True},
            "mutated_verifier": {"diagnostic": "mutated_verifier", "diagnostic_wall_seconds": 0.05, "diagnostic_cpu_seconds": 0.025, "completed": True},
        },
    }


def static_payload() -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="s2-artifact-static-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.cells.append(synthetic_cell())
        sink.diagnostics.append({"diagnostic": "partial_fixed", "diagnostic_wall_seconds": 0.06, "diagnostic_cpu_seconds": 0.03, "completed": False})
        meter = driver.ResourceMeter(started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=2), started_wall=time.monotonic() - 2, started_cpu=time.process_time())
        with patch.object(driver, "process_group_rss_bytes", return_value=4096):
            return driver.artifact_bytes(lock={"run_id": "RUN-ECDLP-abcdef"}, provenance={"commit": "a" * 40, "dirty": False, "command": "fixed-static-artifact"}, meter=meter, sink=sink, status="incomplete_fixture_inconclusive", error="fixed static incomplete fixture", decision={"branch": "inconclusive", "reasons": ["fixed"], "per_u": {}})


@contextlib.contextmanager
def patched_review_root(root: Path):
    source_root = root / "experiments" / driver.EXPERIMENT_ID
    driver_path = source_root / "implementation" / driver.TASK_ID / "driver.py"
    plan_path = driver_path.with_name("execution-plan.json")
    with patch.object(driver, "ROOT", root), patch.object(driver, "SPEC_PATH", source_root / "specification.yaml"), patch.object(driver, "AMENDMENT_PATH", source_root / "amendments" / f"{driver.AMENDMENT_ID}.yaml"), patch.object(driver, "PLAN_PATH", plan_path), patch.object(driver, "__file__", str(driver_path)):
        yield


def build_complete_review_repo(
    *, attested: bool = True, archive_commit_override: str | None = None,
    include_review_task: bool = True, include_checks_in_archive: bool = True,
    attestation_verdict: str = "pass", report_claim_owner: str = "fixed-owner",
) -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, Any]]:
    holder = tempfile.TemporaryDirectory(prefix="s2-review-static-")
    root = Path(holder.name)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixed Static")
    git(root, "config", "user.email", "fixed@example.test")
    source_root = root / "experiments" / driver.EXPERIMENT_ID
    driver_path = source_root / "implementation" / driver.TASK_ID / "driver.py"
    plan_path = driver_path.with_name("execution-plan.json")
    amendment_path = source_root / "amendments" / f"{driver.AMENDMENT_ID}.yaml"
    source_files = {driver_path: b"static driver bytes\n", plan_path: b'{"driver":{"sha256":"static"}}\n', source_root / "specification.yaml": b"static specification\n", amendment_path: b"static amendment\n"}
    for path, value in source_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "reviewed source")
    reviewed = git(root, "rev-parse", "HEAD")
    review_task, archive_task, joint = "TASK-review", "TASK-archive", "fixed admission/custody joint"
    plan_rel = "plans/review-plan.yaml"
    plan = {"review_plan": {"recorded_before_reviewers": True, "source_snapshot": reviewed, "joints": [{"joint": joint, "assigned_to": review_task, "attack_plan": "fixed", "breaking_artifact": "fixed"}]}}
    (root / plan_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / plan_rel).write_text(driver.yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    git(root, "add", plan_rel)
    git(root, "commit", "-q", "-m", "precommitted plan")
    plan_commit = git(root, "rev-parse", "HEAD")
    source_reads = {str(path.relative_to(root)): sha256(value) for path, value in source_files.items()}
    report_rel, check_rel, receipt_rel = "reviews/TASK-review/review.yaml", "reviews/TASK-review/checks.py", "archives/TASK-archive/snapshot.json"
    outputs = [report_rel, check_rel, receipt_rel]
    claim_rel = f"coordination/claims/{review_task}.1.claim.json"
    release_rel = f"coordination/claims/{review_task}.1.release.json"
    claim = {"schema": "crypto.autoresearch.task_claim.v1", "task_id": review_task, "epoch": 1, "owner": "fixed-owner", "session": "fixed-session", "write_scope": outputs, "acquired_at": "2026-09-08T00:00:00Z", "expires_at": "2026-09-08T01:00:00Z", "branch": "fixed", "worktree": "fixed", "forced": False, "supersedes": None}
    claim_path = root / claim_rel
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    claim_path.write_text(json.dumps(claim, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", claim_rel)
    git(root, "commit", "-q", "-m", "review claim")
    claim_commit = git(root, "rev-parse", "HEAD")
    attestation: dict[str, Any] = {"task_id": review_task, "joints_owned": [joint], "complete_source_read": True, "review_plan_path": plan_rel, "source_reads": source_reads, "sources_read": sorted(source_reads), "read_sibling_reports": False, "blind_from_respected": None, "verdict": attestation_verdict} if attested else {}
    report = {"validation_report": {"id": review_task, "task_id": review_task, "role": "validator", "source_snapshot_commit": reviewed, "review_plan_path": plan_rel, "review_plan_commit": plan_commit, "claim_commit": claim_commit, "claim_owner": report_claim_owner, "claim_session": "fixed-session", "claim_epoch": 1, "artifact_paths": outputs, "owned_joint_verdict": "PASS", "verdict": "passed", "review_attestation": attestation, "inference": {"requested_policy": "review-adversarial", "resolved_model_id": "fixed-native-reviewer", "reasoning_effort": "xhigh", "independent_session": True, "fallback_used": False, "degraded_used": False, "bedrock_used": False, "provenance": "fixed synthetic independent assignment"}}}
    for relative, value in ((report_rel, driver.yaml.safe_dump(report, sort_keys=False).encode()), (check_rel, b"# fixed static review check\n")):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    source_hashes = {report_rel: sha256((root / report_rel).read_bytes())}
    if include_checks_in_archive:
        source_hashes[check_rel] = sha256((root / check_rel).read_bytes())
    archive_parent = git(root, "rev-parse", "HEAD")
    receipt = {"schema": "crypto.autoresearch.review_snapshot.v1", "task_id": archive_task, "source_task_ids": [review_task], "parent_sha": archive_parent, "source_path_sha256": source_hashes}
    (root / receipt_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / receipt_rel).write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", report_rel, receipt_rel)
    if include_checks_in_archive:
        git(root, "add", check_rel)
    git(root, "commit", "-q", "-m", "review archive")
    archive_commit = git(root, "rev-parse", "HEAD")
    archive_hashes = {**source_hashes, receipt_rel: sha256((root / receipt_rel).read_bytes())}
    release = {"schema": "crypto.autoresearch.task_release.v1", "task_id": review_task, "epoch": 1, "owner": "fixed-owner", "outcome": "completed", "released_at": "2026-09-08T00:10:00Z"}
    release_path = root / release_rel
    release_path.write_text(json.dumps(release, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", release_rel)
    git(root, "commit", "-q", "-m", "review release")
    release_commit = git(root, "rev-parse", "HEAD")
    queue_rel = "coordination/queue.json"
    review_handoff = {"id": review_task, "to": "validator", "write_scope": outputs, "artifact_paths": outputs, "inference": {"policy": "review-adversarial", "reasoning_effort": "xhigh", "independent_session_required": True, "fallback_allowed": False, "degraded_allowed": False}}
    tasks: list[dict[str, Any]] = []
    if include_review_task:
        tasks.append({"id": review_task, "state": "completed", "role": "validator", "write_scope": outputs, "artifact_paths": outputs, "handoff": review_handoff})
    tasks.append({"id": archive_task, "state": "completed", "archive": {"kind": "snapshot", "source_task_ids": [review_task], "commit_sha": archive_commit, "parent_sha": archive_parent, "path_sha256": archive_hashes, "record_ids": [archive_task, review_task, driver.EXPERIMENT_ID]}})
    queue = {"tasks": tasks}
    (root / queue_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / queue_rel).write_text(json.dumps(queue, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", queue_rel)
    git(root, "commit", "-q", "-m", "external queue authority")
    external = git(root, "rev-parse", "HEAD")
    admission = {"external_authority_commit": external, "external_queue_path": queue_rel, "external_queue_sha256": sha256((root / queue_rel).read_bytes()), "archive_task_id": archive_task, "archive_commit": archive_commit_override or archive_commit, "snapshot_receipt_path": receipt_rel, "snapshot_receipt_sha256": archive_hashes[receipt_rel], "review_task_id": review_task, "review_report_path": report_rel, "review_report_sha256": archive_hashes[report_rel], "review_plan_path": plan_rel, "review_plan_commit": plan_commit, "review_plan_sha256": sha256((root / plan_rel).read_bytes()), "reviewed_source_snapshot": reviewed, "required_verdict": "PASS", "review_claim_path": claim_rel, "review_claim_sha256": sha256(claim_path.read_bytes()), "review_claim_commit": claim_commit, "review_release_path": release_rel, "review_release_sha256": sha256(release_path.read_bytes()), "review_release_commit": release_commit}
    return holder, root, admission


class FixedRegressionTests(unittest.TestCase):
    def test_01_rng_serialization_is_frozen(self) -> None:
        self.assertEqual(driver.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_02_n_one_consumes_exactly_one_digest(self) -> None:
        self.assertEqual(driver.rejection_draw(purpose="query", params=(17, 1, 2, 19, 0, 1, 1), seed=1, counter=4, n=1), (0, 5))

    def test_03_s2_01_control_tuple_is_frozen_at_zero(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("params=(curve.p, curve.A, curve.B, r, 0, 0, 0)", source)

    def test_04_s2_01_shuffle_stream_retains_actual_u(self) -> None:
        self.assertIn("params = (curve.p, curve.A, curve.B, r, 0, u, arm)", Path(driver.__file__).read_text(encoding="utf-8"))

    def test_05_shuffle_guard_does_not_change_fixed_rng_output(self) -> None:
        params = (17, 1, 2, 19, 0, 1, 1)
        self.assertEqual(driver.deterministic_shuffle(range(7), purpose="shuffle", params=params, seed=3), driver.deterministic_shuffle(range(7), purpose="shuffle", params=params, seed=3, check=lambda: None))

    def test_06_shuffle_records_guard_progress(self) -> None:
        progress: list[dict[str, Any]] = []
        driver.deterministic_shuffle(range(17), purpose="shuffle", params=(17, 1, 2, 19, 0, 1, 1), seed=3, check=lambda: None, on_progress=progress.append)
        self.assertEqual(progress[0]["phase"], "shuffle_construction")

    def test_07_transition_table_has_guarded_scalar_and_state_loops(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn('"relabel_scalar_table"', source)
        self.assertIn('"relabel_transition_table"', source)

    def test_08_relabel_control_has_all_start_progress(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn('"relabel_all_start"', source)
        self.assertIn("start_index=start_index", source)

    def test_09_s2_02_incomplete_fixture_has_dedicated_type(self) -> None:
        self.assertIn("raise IncompleteFixtureStop", Path(driver.__file__).read_text(encoding="utf-8"))

    def test_10_s2_02_incomplete_fixture_maps_to_inconclusive(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn('status, error = "incomplete_fixture_inconclusive"', source)
        self.assertIn('"incomplete_frozen_fixture_panel"', source)

    def test_11_s2_02_unexpected_exception_maps_to_failed_implementation(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn('status, error = "failed_implementation"', source)
        self.assertIn('"implementation_exception"', source)

    def test_12_measured_diagnostic_retains_failure_cost(self) -> None:
        rows: list[dict[str, Any]] = []
        with self.assertRaises(ValueError):
            driver.measured_diagnostic("fixed", lambda: (_ for _ in ()).throw(ValueError("fixed")), rows.append)
        self.assertEqual((rows[0]["diagnostic"], rows[0]["completed"]), ("fixed", False))

    def test_13_progress_sink_retains_fixed_diagnostic_row(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2-progress-static-") as temporary:
            sink = driver.ProgressSink(Path(temporary))
            sink.record_diagnostic({"diagnostic": "fixed", "completed": True})
            saved = json.loads((Path(temporary) / "progress.json").read_text())
        self.assertEqual(saved["counts"]["diagnostics"], 1)

    def test_14_s2_03_report_uses_actual_retained_coverage(self) -> None:
        report = static_payload()["report.md"].decode("utf-8")
        self.assertIn('"completed_cell_count": 1', report)
        self.assertIn('"exploratory": [606300]', report)

    def test_15_s2_03_report_serializes_secondary_values(self) -> None:
        report = static_payload()["report.md"].decode("utf-8")
        self.assertIn("mean_first_repeat_length", report)
        self.assertIn("component_sizes", report)

    def test_16_s2_03_report_serializes_all_diagnostic_costs(self) -> None:
        report = static_payload()["report.md"].decode("utf-8")
        for name in ("relabel_table", "relabel_control", "constant_o_census", "mutated_verifier", "partial_fixed"):
            self.assertIn(name, report)

    def test_17_s2_03_cost_csv_contains_added_diagnostics(self) -> None:
        rows = list(csv.DictReader(io.StringIO(static_payload()["costs.csv"].decode("utf-8"))))
        kinds = {row["diagnostic_kind"] for row in rows}
        self.assertTrue({"relabel_table", "relabel_control", "constant_o_census", "mutated_verifier", "partial_fixed"}.issubset(kinds))

    def test_18_s2_04_durable_receipt_can_be_quarantined(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2-retain-static-") as temporary:
            runs = Path(temporary) / "runs"
            final = runs / "exposed"
            final.mkdir(parents=True)
            result = driver.retain_publication_failure(runs=runs, run_id="unit", staging=runs / "staging", final=final, error=OSError("fixed"), phase="post")
        self.assertEqual(result["state"], "quarantined")
        self.assertTrue(result["receipt_directory_fsynced"] and result["quarantine_complete"])

    def test_19_s2_04_failed_receipt_is_explicitly_unretained(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2-retain-fail-static-") as temporary:
            runs = Path(temporary) / "runs"
            final = runs / "exposed"
            final.mkdir(parents=True)
            with patch.object(Path, "write_bytes", side_effect=OSError("fixed receipt write failure")):
                result = driver.retain_publication_failure(runs=runs, run_id="unit", staging=runs / "staging", final=final, error=OSError("fixed"), phase="post")
        self.assertEqual(result["state"], "unretained")
        self.assertFalse(result["receipt_written"])

    def test_20_s2_05_canonical_run_id_accepts_exact_allocated_shape(self) -> None:
        driver.canonical_run_id("RUN-ECDLP-abcdef")

    def test_21_s2_05_canonical_run_id_rejects_nonallocated_shapes(self) -> None:
        for value in ("RUN-anything", "RUN-ECDLP-ABCDEf", "RUN-ECDLP-abcde", "RUN-ECDLP-abcdef-extra"):
            with self.assertRaises(driver.LaunchRefused):
                driver.canonical_run_id(value)

    def test_22_s2_05_allocation_binds_exact_canonical_root(self) -> None:
        root = driver.canonical_experiment_run_root()
        lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(root), "authority_id": "DEC-fixed"}}
        self.assertEqual(driver.verify_run_allocation(lock, root), root)

    def test_23_s2_05_mismatched_root_is_refused(self) -> None:
        root = driver.canonical_experiment_run_root()
        lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(root), "authority_id": "DEC-fixed"}}
        with tempfile.TemporaryDirectory(prefix="s2-root-static-") as temporary, self.assertRaises(driver.LaunchRefused):
            driver.verify_run_allocation(lock, Path(temporary))

    def test_24_s2_05_symlink_root_is_refused(self) -> None:
        root = driver.canonical_experiment_run_root()
        lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(root), "authority_id": "DEC-fixed"}}
        with tempfile.TemporaryDirectory(prefix="s2-root-link-static-") as temporary:
            link = Path(temporary) / "root-link"
            link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(driver.LaunchRefused):
                driver.verify_run_allocation(lock, link)

    def test_25_s2_06_complete_review_graph_is_accepted(self) -> None:
        holder, root, admission = build_complete_review_repo()
        try:
            with patched_review_root(root):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_26_s2_06_missing_review_attestation_is_rejected(self) -> None:
        holder, root, admission = build_complete_review_repo(attested=False)
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_27_s2_06_false_archive_commit_is_rejected(self) -> None:
        holder, root, admission = build_complete_review_repo(archive_commit_override="0" * 40)
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_28_s2_06_requires_external_queue_and_nonself_receipt(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("external_queue_path", source)
        self.assertIn("impermissibly self-names", source)

    def test_29_s2_07_empty_process_measurement_is_infrastructure_failure(self) -> None:
        class Result:
            stdout = ""
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=Result()):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_30_s2_07_malformed_process_measurement_is_infrastructure_failure(self) -> None:
        class Result:
            stdout = "9 7 bad\n"
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=Result()):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_31_s2_07_missing_current_process_is_infrastructure_failure(self) -> None:
        class Result:
            stdout = "10 7 12\n"
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=Result()):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_32_s2_07_matching_current_group_is_summed(self) -> None:
        class Result:
            stdout = "9 7 12\n10 7 8\n11 4 99\n"
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=Result()):
            self.assertEqual(driver.process_group_rss_bytes(), 20 * 1024)

    def test_33_s2_08_fourier_accepts_progress_and_uses_it(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("on_progress: Callable[[dict[str, Any]], None] | None = None", source)
        self.assertIn('"fourier_eigenvalues", on_progress, frequency=index', source)

    def test_34_s2_08_nested_progress_records_outer_coordinates(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        for coordinate in ("requested_step=requested", "iteration=iteration", "destination=destination", "origin=origin", "state=state"):
            self.assertIn(coordinate, source)

    def test_35_prior_v01_to_v08_coverage_remains_mapped(self) -> None:
        coverage = driver.protocol_coverage()
        for number in range(1, 9):
            self.assertTrue(any(key.startswith(f"V-{number:02d}") for key in coverage))

    def test_36_s2_coverage_map_names_every_repair(self) -> None:
        coverage = driver.protocol_coverage()
        for number in range(1, 9):
            self.assertTrue(any(key.startswith(f"S2-{number:02d}") for key in coverage))

    def test_37_v01_mock_subgroup_is_one_checked_accumulator(self) -> None:
        class CyclicMock:
            def __init__(self) -> None:
                self.additions = 0

            def add(self, left: driver.Point, right: driver.Point) -> driver.Point:
                self.additions += 1
                value = ((0 if left is None else left[1]) + (0 if right is None else right[1])) % 5
                return None if value == 0 else (1, value)

        mock = CyclicMock()
        points, certificate = driver.enumerate_subgroup(mock, (1, 1), 5, lambda: None)
        self.assertEqual((points[0], mock.additions, certificate["method"], certificate["r_times_G_is_O"]), (None, 5, "checked_repeated_addition", True))

    def test_38_v02_source_keeps_exploratory_and_heldout_streams_separate(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertEqual(driver.EXPLORATORY_SEEDS, tuple(range(606300, 606308)))
        self.assertEqual(driver.HELDOUT_SEEDS, tuple(range(606308, 606316)))
        self.assertIn('("exploratory", EXPLORATORY_SEEDS)', source)
        self.assertIn('("heldout", HELDOUT_SEEDS)', source)
        self.assertIn('cell.get("stream") == "heldout"', source)

    def test_39_v03_source_records_before_immediate_invalid_stop(self) -> None:
        source = inspect.getsource(driver.run_future_pipeline)
        self.assertLess(source.index("sink.record_cell(cell)"), source.index("raise MeasurementInvalidStop"))

    def test_40_v04_static_payload_retains_secondary_and_cost_fields(self) -> None:
        metrics = json.loads(static_payload()["raw-result.json"])["metrics"]
        self.assertIn("mean_first_repeat_length", metrics)
        self.assertIn("diagnostic_costs", metrics)

    def test_41_v05_static_manifest_uses_terminal_bracket(self) -> None:
        timing = driver.yaml.safe_load(static_payload()["manifest.yaml"])["run"]["timing"]
        self.assertGreaterEqual(datetime.fromisoformat(timing["finished_at"]), datetime.fromisoformat(timing["started_at"]))
        self.assertGreaterEqual(timing["wall_seconds"], 0)

    def test_42_v06_source_uses_postrename_failure_custody(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("retain_publication_failure(", source)
        self.assertIn("post_rename_durability", source)

    def test_43_v07_complete_review_mock_requires_source_archive_execution_order(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("reviewed source snapshot precedes review archive", source)
        self.assertIn("external queue authority precedes executing commit", source)

    def test_44_v08_source_keeps_cayley_stride_and_checkpoint_phases(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertEqual(driver.CAYLEY_GUARD_STRIDE, 16)
        self.assertIn("matrix_vector_origin", source)
        self.assertIn("total_variation_reduction", source)

    def test_45_s3_01_requires_standard_review_attestation(self) -> None:
        source = inspect.getsource(driver.verify_review_admission)
        for field in ("joints_owned", "sources_read", "read_sibling_reports", "blind_from_respected", "review_claim_path", "review_release_path"):
            self.assertIn(field, source)

    def test_46_s3_01_requires_completed_validator_task_in_external_queue(self) -> None:
        holder, root, admission = build_complete_review_repo(include_review_task=False)
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_47_s3_01_rejects_contradictory_attestation_verdict(self) -> None:
        holder, root, admission = build_complete_review_repo(attestation_verdict="breaks")
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_48_s3_01_requires_archive_of_every_declared_review_output(self) -> None:
        holder, root, admission = build_complete_review_repo(include_checks_in_archive=False)
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_49_s3_01_rejects_report_control_plane_claim_mismatch(self) -> None:
        holder, root, admission = build_complete_review_repo(report_claim_owner="forged-owner")
        try:
            with patched_review_root(root), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(admission, admission["reviewed_source_snapshot"], admission["external_authority_commit"])
        finally:
            holder.cleanup()

    def test_50_s3_02_parent_fsync_failure_has_non_durable_quarantine_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s3-parent-fsync-static-") as temporary:
            runs = Path(temporary) / "runs"
            final = runs / "exposed"
            final.mkdir(parents=True)

            def fail_only_parent(path: Path) -> None:
                if path == runs:
                    raise OSError("fixed parent fsync failure")

            with patch.object(driver, "fsync_directory", side_effect=fail_only_parent):
                result = driver.retain_publication_failure(
                    runs=runs, run_id="unit", staging=runs / "staging", final=final,
                    error=OSError("fixed post-rename failure"), phase="post_rename_durability",
                )
        self.assertEqual(result["state"], "quarantine_parent_fsync_failed")
        self.assertFalse(result["quarantine_complete"])
        self.assertIn("fixed parent fsync failure", result["parent_directory_fsync_failed"])

    def test_51_s3_03_failed_scalar_certificate_is_retained_before_stop(self) -> None:
        class MockCurve:
            def scalar(self, scalar: int, _point: driver.Point) -> driver.Point:
                return (scalar, scalar)

        certificates: list[dict[str, Any]] = []
        partial_invalid: list[dict[str, Any]] = []

        def repeat_with_nonzero_denominator(_curve: Any, state: driver.Point, _g: driver.Point, _q: driver.Point, a: int, b: int, _r: int, _assignment: Any) -> tuple[driver.Point, int, int, str]:
            return state, a, b + 1, "add"

        with patch.object(driver, "rho_step", side_effect=repeat_with_nonzero_denominator), patch.object(driver, "binary_verifier", return_value=(None, 0, 1)):
            with self.assertRaises(driver.MeasurementInvalidStop):
                driver.collision_census(MockCurve(), (1, 1), (2, 2), 3, None, lambda: None, certificates.append, None, partial_invalid.append)
        self.assertEqual(len(certificates), 1)
        self.assertEqual(partial_invalid[0]["state"], "partial_invalid_cell")
        self.assertEqual(partial_invalid[0]["certificate"], certificates[0])

    def test_52_s3_04_diagnostic_records_actual_memory_on_success(self) -> None:
        records: list[dict[str, Any]] = []
        with patch.object(driver, "process_group_rss_bytes", side_effect=[101, 202]):
            value, record = driver.measured_diagnostic("fixed", lambda: "ok", records.append)
        self.assertEqual(value, "ok")
        self.assertEqual(records, [record])
        self.assertEqual((record["process_group_rss_start_bytes"], record["process_group_rss_end_bytes"], record["process_group_rss_peak_bytes"]), (101, 202, 202))

    def test_53_s3_04_interrupted_diagnostic_has_one_failure_row_and_memory(self) -> None:
        records: list[dict[str, Any]] = []
        with patch.object(driver, "process_group_rss_bytes", side_effect=[202, 101]):
            with self.assertRaises(driver.MeasurementInvalidStop):
                driver.measured_diagnostic("fixed", lambda: (_ for _ in ()).throw(driver.MeasurementInvalidStop("fixed")), records.append)
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0]["completed"])
        self.assertEqual((records[0]["process_group_rss_start_bytes"], records[0]["process_group_rss_end_bytes"]), (202, 101))

    def test_54_s3_05_coordinate_progress_precedes_guarded_partition_probe(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("coordinate_partition\", coordinate_progress", source)
        self.assertNotIn('"coordinate_partition", None', source)

    def test_55_s3_05_subgroup_and_collision_accept_progress_callbacks(self) -> None:
        self.assertIn("on_progress", inspect.signature(driver.enumerate_subgroup).parameters)
        self.assertIn("on_progress", inspect.signature(driver.collision_census).parameters)

    def test_56_s3_05_artifact_assembly_is_guarded(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("def assembly_guard", source)
        self.assertIn("artifact_cost_serialization", source)
        self.assertIn("check: Callable[[", inspect.getsource(driver.artifact_bytes))

    def test_57_s3_05_publication_is_guarded_and_keeps_failure_custody(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        self.assertIn("publication_post_rename_durability", source)
        self.assertIn("check=guard.check", source)
        self.assertIn("retain_publication_failure", source)

    def test_58_s3_coverage_map_names_every_accepted_repair(self) -> None:
        coverage = driver.protocol_coverage()
        for number in range(1, 6):
            self.assertTrue(any(key.startswith(f"S3-{number:02d}") for key in coverage))


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed regression case exceeded 10 seconds")


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.case_timings: list[dict[str, Any]] = []
        self._started: dict[str, tuple[float, float]] = {}

    def startTest(self, test: unittest.case.TestCase) -> None:
        self._started[test.id()] = (time.monotonic(), time.process_time())
        signal.alarm(10)
        super().startTest(test)

    def stopTest(self, test: unittest.case.TestCase) -> None:
        signal.alarm(0)
        wall, cpu = self._started.pop(test.id())
        self.case_timings.append({"id": test.id(), "wall_seconds": round(time.monotonic() - wall, 6), "cpu_seconds": round(time.process_time() - cpu, 6)})
        super().stopTest(test)


class TimedRunner(unittest.TextTestRunner):
    resultclass = TimedResult


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, timeout_handler)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FixedRegressionTests)
    result = TimedRunner(verbosity=2).run(suite)
    print(json.dumps({"schema": "crypto.autoresearch.fixed_regression_timing.v1", "case_executions": result.testsRun, "passed": result.testsRun - len(result.failures) - len(result.errors), "failed": len(result.failures) + len(result.errors), "maximum_case_wall_seconds": max((row["wall_seconds"] for row in result.case_timings), default=0.0), "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in result.case_timings), default=0.0), "case_timings": result.case_timings}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)

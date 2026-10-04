#!/usr/bin/env python3
"""Fixed static/synthetic/mock regression checks for TASK-20260908-6a010d.

These cases do not enumerate a frozen fixture, run a Cayley calibration, run a
collision census, create a launch lock, or publish a RUN directory.  Synthetic
rows and three-state mock labels only check correction semantics.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import inspect
import io
import json
import math
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

import driver


def arm(work: int, successes: int, *, failed: int = 0) -> dict:
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
            "mean_first_repeat_length": 1.0, "useful_fraction": 1.0 if successes else 0.0,
            "fixed_points": 0, "two_cycles": 0, "component_sizes": [1],
            "max_tail_length": 0, "max_cycle_length": 1,
        },
        "diagnostic_costs": {
            "diagnostic_wall_seconds": 0.01, "diagnostic_cpu_seconds": 0.01,
            "collision_table_peak_bytes": 64, "scalar_inversions": 0, "scalar_comparisons": 0,
        },
    }


def controls(*, cayley: bool = True, relabel: bool = True, occupancy: bool = True, zero_denominators: int = 0, solves: int = 0, mutation: bool = True) -> dict:
    return {
        "cayley": {"passed": cayley}, "relabel": relabel, "occupancy": occupancy,
        "known_false": {"constant_o": {"nonzero_denominators": zero_denominators, "solves": solves}, "mutated_candidate_fails_certificate": mutation},
    }


def synthetic_cell(curve_id: str, seed: int, u: int, d: float | None, *, valid: bool = True) -> dict:
    return {
        "curve_id": curve_id, "seed": seed, "u": u,
        "metric": {"available": d is not None, "d": d},
        "validity": {"valid": valid}, "coordinate": arm(10, 2),
        "nulls": [{**arm(12, 2), "arm": index} for index in range(1, 8)],
        "controls": controls(), "diagnostic_costs": {}, "stream": "heldout",
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


def payload_for(cells: list[dict[str, Any]] | None = None, *, wall_age: float = 0.0) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="spectral-static-artifacts-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.cells.extend(cells or [synthetic_cell("curve-0", driver.HELDOUT_SEEDS[0], 1, 0.1)])
        meter = driver.ResourceMeter(
            started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=wall_age),
            started_wall=driver.time.monotonic() - wall_age,
            started_cpu=driver.time.process_time(),
        )
        return driver.artifact_bytes(
            lock={"run_id": "RUN-ECDLP-static"},
            provenance={"commit": "a" * 40, "dirty": False, "command": "static-mock"},
            meter=meter, sink=sink, status="completed_invalid", error="static fixture", decision={"branch": "inconclusive", "per_u": {}},
        )


class CorrectionRegressionTests(unittest.TestCase):
    params = (17, 1, 2, 19, 0, 1, 1)

    def test_01_canonical_rng_serialization_is_frozen(self) -> None:
        self.assertEqual(driver.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')
        self.assertEqual(
            driver.stream_digest(purpose="query", params=self.params, seed=11, counter=0),
            driver.stream_digest(purpose="query", params=self.params, seed=11, counter=0),
        )

    def test_02_n_one_consumes_a_digest(self) -> None:
        self.assertEqual(driver.rejection_draw(purpose="query", params=self.params, seed=1, counter=4, n=1), (0, 5))

    def test_03_singular_curve_is_rejected_by_curve_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "singular"):
            driver.Curve(7, 1, 2)

    def test_04_fixture_scan_records_singular_before_curve_construction(self) -> None:
        source = inspect.getsource(driver.fixture_scan)
        self.assertLess(source.index("discriminator == 0"), source.index("curve = Curve"))
        self.assertIn('"reason": "singular"', source)

    def test_05_constant_o_census_executes_every_mock_start(self) -> None:
        result = driver.constant_o_census([None, (1, 1), (2, 2)], lambda: None)
        self.assertTrue(result["passed"])
        self.assertEqual((result["starts"], len(result["collisions"]), result["nonzero_denominators"], result["solves"]), (3, 3, 0, 0))
        self.assertTrue(all(row["classification"] == "fruitless_denominator" for row in result["collisions"]))

    def test_06_failed_certificate_is_not_fruitless(self) -> None:
        result = driver.reduce_validity(arm(10, 0, failed=1), [arm(10, 1)], controls())
        self.assertFalse(result["valid"])
        self.assertEqual(result["certificate_failures"], 1)

    def test_07_zero_denominator_is_not_a_certificate_failure(self) -> None:
        result = driver.reduce_validity(arm(10, 0), [arm(10, 1)], controls())
        self.assertTrue(result["valid"])
        self.assertEqual(result["certificate_failures"], 0)

    def test_08_pooled_side_keeps_a_zero_yield_null_arm(self) -> None:
        coordinate = arm(50, 10)
        nulls = [arm(100, 0)] + [arm(60, 10) for _ in range(6)]
        metric = driver.cell_difference(coordinate, nulls)
        self.assertTrue(metric["available"])
        self.assertEqual(metric["zero_yield_null_arms"], [1])
        self.assertEqual((metric["pooled_null_work"], metric["pooled_null_successes"]), (460, 60))
        self.assertAlmostEqual(float(metric["d"]), math.log((460 / 60) / 5))

    def test_09_zero_coordinate_side_makes_cell_unavailable(self) -> None:
        metric = driver.cell_difference(arm(40, 0), [arm(50, 5) for _ in range(7)])
        self.assertFalse(metric["available"])
        self.assertEqual(metric["unavailable_reason"], "coordinate_zero_success")

    def test_10_zero_pooled_null_side_makes_cell_unavailable(self) -> None:
        metric = driver.cell_difference(arm(40, 4), [arm(50, 0) for _ in range(7)])
        self.assertFalse(metric["available"])
        self.assertEqual(metric["unavailable_reason"], "pooled_null_zero_success")

    def test_11_pooling_is_not_mean_of_arm_ratios(self) -> None:
        nulls = [arm(10, 10), arm(99, 1)] + [arm(10, 10) for _ in range(5)]
        work, successes, cost = driver.pooled_null_cost(nulls)
        self.assertEqual((work, successes), (159, 61))
        self.assertAlmostEqual(float(cost), 159 / 61)
        self.assertNotAlmostEqual(float(cost), sum(row["charged_cost"] for row in nulls) / 7)

    def test_12_named_control_failure_invalidates_measurement(self) -> None:
        result = driver.reduce_validity(arm(1, 1), [arm(1, 1)] * 7, controls(solves=1))
        self.assertFalse(result["valid"])
        self.assertIn("constant_o_zero_solves", result["failed_controls"])

    def test_13_validity_reduction_requires_every_named_control(self) -> None:
        result = driver.reduce_validity(arm(1, 1), [arm(1, 1)] * 7, controls(cayley=False, relabel=False, occupancy=False, mutation=False))
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["failed_controls"]), 4)

    def test_14_global_positive_requires_all_three_u_and_curves(self) -> None:
        cells = [synthetic_cell(f"curve-{curve}", seed, u, 0.2) for curve in range(4) for seed in driver.HELDOUT_SEEDS for u in driver.US]
        decision = driver.global_decision(cells)
        self.assertTrue(decision["panel_valid"])
        self.assertEqual(decision["branch"], "positive")

    def test_15_global_negative_is_cellwise(self) -> None:
        cells = [synthetic_cell(f"curve-{curve}", seed, u, 0.0) for curve in range(4) for seed in driver.HELDOUT_SEEDS for u in driver.US]
        self.assertEqual(driver.global_decision(cells)["branch"], "negative")

    def test_16_unavailable_valid_panel_is_inconclusive_not_invalid(self) -> None:
        cells = [synthetic_cell(f"curve-{curve}", seed, u, 0.2) for curve in range(4) for seed in driver.HELDOUT_SEEDS for u in driver.US]
        cells[0]["metric"] = {"available": False, "d": None}
        decision = driver.global_decision(cells)
        self.assertTrue(decision["panel_valid"])
        self.assertEqual((decision["branch"], decision["reasons"]), ("inconclusive", ["unavailable_inferential_cell"]))

    def test_17_invalid_panel_is_not_a_valid_inconclusive_measurement(self) -> None:
        cells = [synthetic_cell(f"curve-{curve}", seed, u, -0.1) for curve in range(4) for seed in driver.HELDOUT_SEEDS for u in driver.US]
        cells[0]["validity"] = {"valid": False}
        decision = driver.global_decision(cells)
        self.assertFalse(decision["panel_valid"])
        self.assertIn("invalid_certificate_or_control", decision["reasons"])

    def test_18_cayley_gap_is_explicit_and_separate(self) -> None:
        source = inspect.getsource(driver.cayley_control)
        self.assertIn('"gap"', source)
        self.assertIn("separate from the rho", source)

    def test_19_progress_checkpoint_preserves_partial_mock_data(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spectral-static-progress-") as temporary:
            sink = driver.ProgressSink(Path(temporary))
            sink.record_partial({"kind": "mock", "certificate": {"start": 0}})
            saved = json.loads((Path(temporary) / "progress.json").read_text(encoding="utf-8"))
            partial = [json.loads(line) for line in (Path(temporary) / "partial-certificates.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual((saved["counts"]["partial_certificates"], partial[0]["kind"]), (1, "mock"))
        self.assertEqual(saved["events"][-1]["event"], "start_completed")

    def test_26_fixture_accumulator_is_not_shadowed_by_the_progress_callback(self) -> None:
        source = inspect.getsource(driver.select_fixtures)
        self.assertIn("all_rejected.extend(discards)", source)
        self.assertIn("record_rejection", source)

    def test_20_artifact_layout_has_all_experiment_and_schema_companions(self) -> None:
        self.assertEqual(len(driver.EXPERIMENT_ARTIFACTS), 13)
        self.assertTrue({"command.txt", "environment.json", "raw-result.json", "package-sha256.json"}.issubset(driver.EXPERIMENT_ARTIFACTS))

    def test_21_lock_path_absence_fails_closed_without_a_synthetic_lock(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.verify_launch_admission(Path("/definitely-not-a-coordinator-lock"), "not-a-key")

    def test_22_review_admission_rejects_incomplete_semantics(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.verify_review_admission({}, "deadbeef", "deadbeef")

    def test_23_atomic_publication_uses_sibling_staging_and_rename(self) -> None:
        source = inspect.getsource(driver.atomic_publish) + inspect.getsource(driver.retain_publication_failure)
        self.assertIn("dir=runs", source)
        self.assertIn("os.rename(staging, final)", source)
        self.assertIn("publication-failure.json", source)

    def test_24_process_group_guard_and_advisory_policy_are_not_old_deadlines(self) -> None:
        guard_source = inspect.getsource(driver.process_group_rss_bytes) + inspect.getsource(driver.Guard.check)
        pipeline_source = inspect.getsource(driver.artifact_bytes)
        self.assertIn("os.getpgid(0)", guard_source)
        self.assertEqual(driver.Guard.__dataclass_fields__["limit_bytes"].default, driver.MEMORY_LIMIT_BYTES)
        self.assertIn("supersedes their historical stop/invalidation semantics", pipeline_source)

    def test_25_all_accepted_findings_have_executable_coverage(self) -> None:
        coverage = driver.protocol_coverage()
        self.assertTrue(all(f"F-{number:02d}" in " ".join(coverage) for number in range(1, 10)))
        self.assertIn("pooled_side_availability", coverage)

    def test_27_v01_subgroup_is_one_repeated_addition_chain_with_retained_certificate(self) -> None:
        class CyclicPointMock:
            def __init__(self, modulus: int):
                self.modulus = modulus
                self.additions = 0

            def add(self, left: driver.Point, right: driver.Point) -> driver.Point:
                self.additions += 1
                left_value = 0 if left is None else left[1]
                right_value = 0 if right is None else right[1]
                value = (left_value + right_value) % self.modulus
                return None if value == 0 else (1, value)

        mock = CyclicPointMock(5)
        points, certificate = driver.enumerate_subgroup(mock, (1, 1), 5, lambda: None)
        self.assertEqual(points[0], None)
        self.assertEqual(mock.additions, 5)
        self.assertEqual(
            (certificate["method"], certificate["points_enumerated"], certificate["distinct"], certificate["r_times_G_is_O"]),
            ("checked_repeated_addition", 5, True, True),
        )

    def test_28_v02_all_sixteen_seeds_have_separate_exploratory_custody(self) -> None:
        self.assertEqual(driver.EXPLORATORY_SEEDS, tuple(range(606300, 606308)))
        self.assertEqual(driver.HELDOUT_SEEDS, tuple(range(606308, 606316)))
        source = inspect.getsource(driver.run_future_pipeline)
        self.assertIn('("exploratory", EXPLORATORY_SEEDS)', source)
        self.assertIn('("heldout", HELDOUT_SEEDS)', source)
        self.assertIn('cell.get("stream") == "heldout"', source)
        self.assertIn('cell["stream"] = stream', source)

    def test_29_v03_first_invalid_mock_cell_stops_before_the_next_cell(self) -> None:
        fixtures = {9: [{"p": 17, "B": 1}], 11: [{"p": 19, "B": 2}]}
        calls: list[tuple[int, int, int]] = []
        captured: dict[str, Any] = {}

        def fake_cell(fixture: dict[str, Any], seed: int, u: int, check: Any, partial: Any = None) -> dict[str, Any]:
            calls.append((fixture["p"], seed, u))
            return synthetic_cell(f"p{fixture['p']}-B{fixture['B']}", seed, u, None, valid=False)

        def fake_artifacts(**kwargs: Any) -> dict[str, bytes]:
            captured.update({"status": kwargs["status"], "cells": len(kwargs["sink"].cells), "reason": kwargs["decision"]["reasons"]})
            return {}

        def memory_record_cell(sink: Any, record: dict[str, Any]) -> None:
            sink.cells.append(record)

        with tempfile.TemporaryDirectory(prefix="spectral-static-stop-") as temporary:
            with patched(
                driver,
                select_fixtures=lambda check, sink=None: (fixtures, []), future_cell=fake_cell,
                artifact_bytes=fake_artifacts, atomic_publish=lambda run_root, run_id, payload: {},
                execution_provenance=lambda command: {"commit": "a" * 40, "dirty": False, "command": command},
            ), patched(driver.Guard, check=lambda self: None), patched(driver.ProgressSink, record_cell=memory_record_cell):
                driver.run_future_pipeline({"run_id": "RUN-ECDLP-static"}, Path(temporary), "fixed-mock-only")
        self.assertEqual(len(calls), 1)
        self.assertEqual(captured, {"status": "completed_invalid", "cells": 1, "reason": ["frozen_validity_failure_immediate_stop"]})

    def test_30_v04_all_secondary_and_diagnostic_cost_fields_are_canonical(self) -> None:
        payload = payload_for()
        fieldnames = set(csv.DictReader(io.StringIO(payload["costs.csv"].decode("utf-8"))).fieldnames or [])
        required_cost = {
            "scalar_inversions", "scalar_comparisons", "diagnostic_wall_seconds",
            "diagnostic_cpu_seconds", "collision_table_peak_bytes",
        }
        required_secondary = {
            "mean_first_repeat_length", "useful_fraction", "fixed_points", "two_cycles",
            "component_sizes", "max_tail_length", "max_cycle_length",
        }
        self.assertTrue(required_cost.issubset(fieldnames))
        self.assertTrue(required_secondary.issubset(fieldnames))
        raw = json.loads(payload["raw-result.json"])["metrics"]
        self.assertTrue(required_secondary.issubset(raw))
        self.assertIn("diagnostic_costs", raw)

    def test_31_v05_manifest_utc_interval_uses_the_terminal_resource_bracket(self) -> None:
        payload = payload_for(wall_age=3.0)
        timing = driver.yaml.safe_load(payload["manifest.yaml"])["run"]["timing"]
        started = datetime.fromisoformat(timing["started_at"])
        finished = datetime.fromisoformat(timing["finished_at"])
        self.assertLess(abs((finished - started).total_seconds() - timing["wall_seconds"]), 0.5)
        report = payload["report.md"].decode("utf-8")
        self.assertIn(timing["started_at"], report)
        self.assertIn(timing["finished_at"], report)

    def test_32_v06_postrename_failure_quarantines_the_exposed_final_tree(self) -> None:
        payload = {name: b"fixed mock payload\n" for name in driver.EXPERIMENT_ARTIFACTS[:-1]}
        calls = 0

        def fail_postrename(_path: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("fixed post-rename directory fsync failure")

        with tempfile.TemporaryDirectory(prefix="spectral-static-publish-") as temporary:
            root = Path(temporary)
            with patched(driver, fsync_directory=fail_postrename):
                with self.assertRaises(driver.InfrastructureStop):
                    driver.atomic_publish(root, "RUN-ECDLP-static", payload)
            final = root / "runs/RUN-ECDLP-static"
            retained = list((root / "runs/incomplete").iterdir())
            self.assertFalse(final.exists())
            self.assertEqual(len(retained), 1)
            receipt = json.loads((retained[0] / "publication-failure.json").read_text(encoding="utf-8"))
            self.assertEqual((receipt["publication_state"], receipt["phase"]), ("post_rename_durability_failed", "post_rename_durability"))

    def test_33_v07_reviewed_source_archive_and_executing_commit_are_distinct_and_ordered(self) -> None:
        def git(cwd: Path, *args: str) -> str:
            return subprocess.run(["git", "-C", str(cwd), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

        with tempfile.TemporaryDirectory(prefix="spectral-static-review-") as temporary:
            root = Path(temporary)
            git(root, "init", "-q", "-b", "main")
            git(root, "config", "user.name", "Static Test")
            git(root, "config", "user.email", "static@example.test")
            (root / "producer.txt").write_text("reviewed source\n", encoding="utf-8")
            git(root, "add", "producer.txt")
            git(root, "commit", "-q", "-m", "reviewed source snapshot")
            reviewed = git(root, "rev-parse", "HEAD")
            report_path = "reviews/TASK-static/review.yaml"
            receipt_path = "archives/TASK-static/snapshot.json"
            (root / report_path).parent.mkdir(parents=True)
            report = {"validation_report": {"task_id": "TASK-static", "source_snapshot_commit": reviewed, "owned_joint_verdict": "PASS", "verdict": "passed"}}
            (root / report_path).write_text(driver.yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
            report_hash = hashlib.sha256((root / report_path).read_bytes()).hexdigest()
            (root / receipt_path).parent.mkdir(parents=True)
            receipt = {"source_task_ids": ["TASK-static"], "path_sha256": {report_path: report_hash}}
            (root / receipt_path).write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
            git(root, "add", report_path, receipt_path)
            git(root, "commit", "-q", "-m", "archive static PASS review")
            executing = git(root, "rev-parse", "HEAD")
            admission = {
                "archive_receipt_path": receipt_path, "archive_receipt_sha256": hashlib.sha256((root / receipt_path).read_bytes()).hexdigest(),
                "archive_commit": executing, "review_task_id": "TASK-static", "review_report_path": report_path,
                "review_report_sha256": report_hash, "reviewed_source_snapshot": reviewed, "required_verdict": "PASS",
            }
            original_root = driver.ROOT
            try:
                driver.ROOT = root
                driver.verify_review_admission(admission, reviewed, executing)
            finally:
                driver.ROOT = original_root

    def test_34_v08_dense_cayley_paths_take_guarded_strides_and_record_progress(self) -> None:
        weights = inspect.getsource(driver.cayley_weights)
        control = inspect.getsource(driver.cayley_control)
        tv = inspect.getsource(driver.cayley_tv_curve)
        self.assertIn("check: Callable", weights)
        self.assertIn("matrix_column_allocation", weights)
        self.assertIn("row_reduction_column", control)
        self.assertIn("column_reduction_row", control)
        self.assertIn("matrix_vector_origin", tv)
        self.assertIn("on_progress", control)
        self.assertEqual(driver.CAYLEY_GUARD_STRIDE, 16)


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
        key = test.id()
        self._started[key] = (time.monotonic(), time.process_time())
        signal.alarm(10)
        super().startTest(test)

    def stopTest(self, test: unittest.case.TestCase) -> None:
        signal.alarm(0)
        started_wall, started_cpu = self._started.pop(test.id())
        self.case_timings.append({
            "id": test.id(), "wall_seconds": round(time.monotonic() - started_wall, 6),
            "cpu_seconds": round(time.process_time() - started_cpu, 6),
        })
        super().stopTest(test)


class TimedRunner(unittest.TextTestRunner):
    resultclass = TimedResult


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, timeout_handler)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CorrectionRegressionTests)
    result = TimedRunner(verbosity=2).run(suite)
    print(json.dumps({
        "schema": "crypto.autoresearch.fixed_regression_timing.v1",
        "case_executions": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures) + len(result.errors),
        "maximum_case_wall_seconds": max((row["wall_seconds"] for row in result.case_timings), default=0.0),
        "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in result.case_timings), default=0.0),
        "case_timings": result.case_timings,
    }, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)

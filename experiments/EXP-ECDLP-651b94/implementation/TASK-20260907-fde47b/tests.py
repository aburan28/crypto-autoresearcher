#!/usr/bin/env python3
"""Fixed static/synthetic regression checks for TASK-20260907-fde47b.

These cases do not enumerate a frozen fixture, run a Cayley calibration, run a
collision census, create a launch lock, or publish a RUN directory.  Synthetic
rows and three-state mock labels only check correction semantics.
"""
from __future__ import annotations

import inspect
import json
import math
import tempfile
import unittest
from pathlib import Path

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
        "validity": {"valid": valid},
    }


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
            driver.verify_review_admission({}, "deadbeef")

    def test_23_atomic_publication_uses_sibling_staging_and_rename(self) -> None:
        source = inspect.getsource(driver.atomic_publish)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

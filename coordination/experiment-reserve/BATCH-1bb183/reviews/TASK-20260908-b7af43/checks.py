#!/usr/bin/env python3
"""Independent fixed-case source-conformance checks for TASK-20260908-b7af43.

The checks import only the corrected prospective runner and invoke lower-level
fixed arithmetic, serialization, custody, telemetry-parser, and mocked review
admission helpers.  They never call fixture selection, future_cell,
cayley_control, verify_launch_admission, run_future_pipeline, driver.main, or a
measurement entrypoint.  No real key, signature, lock, allocation, RUN record,
scientific fixture, census, null/control panel, or timing panel is created.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
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
import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[5]
DRIVER_DIR = ROOT / "experiments/EXP-ECDLP-651b94/implementation/TASK-20260908-111152"
sys.path.insert(0, str(DRIVER_DIR))
import driver  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def synthetic_arm(*, transition: int = 3, verification: int = 2, successes: int = 1) -> dict[str, Any]:
    work = transition + verification
    return {
        "starts": 1,
        "successes": successes,
        "failed_certificates": 0,
        "transition_group_operations": transition,
        "verification_group_operations": verification,
        "group_additions": transition,
        "group_doublings": 0,
        "charged_cost": None if successes == 0 else work / successes,
        "secondary": {
            "mean_first_repeat_length": 1.0,
            "useful_fraction": float(successes),
            "fixed_points": 1,
            "two_cycles": 0,
            "component_sizes": [1],
            "max_tail_length": 0,
            "max_cycle_length": 1,
        },
        "diagnostic_costs": {
            "diagnostic_wall_seconds": 0.01,
            "diagnostic_cpu_seconds": 0.005,
            "collision_table_peak_bytes": 64,
            "scalar_inversions": 1,
            "scalar_comparisons": 1,
        },
        "certificates": [],
    }


def valid_controls() -> dict[str, Any]:
    return {
        "cayley": {"passed": True},
        "relabel": True,
        "occupancy": True,
        "known_false": {
            "constant_o": {"nonzero_denominators": 0, "solves": 0},
            "mutated_candidate_fails_certificate": True,
        },
    }


def panel(value: float = 0.3) -> list[dict[str, Any]]:
    return [
        {
            "curve_id": curve,
            "seed": seed,
            "u": u,
            "metric": {"available": True, "d": value},
            "validity": {"valid": True},
        }
        for curve in ("c0", "c1", "c2", "c3")
        for seed in driver.HELDOUT_SEEDS
        for u in driver.US
    ]


def artifact_payload() -> dict[str, bytes]:
    return {name: f"fixed:{name}\n".encode() for name in driver.EXPERIMENT_ARTIFACTS[:-1]}


def fixed_artifact_bytes() -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="validator-artifact-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.fixtures.append({"p": 17})
        sink.rejected.append({"p": 19, "reason": "fixed"})
        cell = {
            "curve_id": "fixed",
            "seed": 606300,
            "u": 1,
            "stream": "exploratory",
            "metric": {"available": True, "d": 0.2},
            "coordinate": synthetic_arm(),
            "nulls": [{**synthetic_arm(), "arm": index} for index in range(1, 8)],
            "controls": {"cayley": {"gap": "0.1"}, "known_false": {"constant_o": {"collisions": []}}},
            "validity": {"valid": True},
            "diagnostic_costs": {
                "relabel_control": {
                    "diagnostic": "relabel_control",
                    "diagnostic_wall_seconds": 0.01,
                    "diagnostic_cpu_seconds": 0.005,
                    "completed": True,
                }
            },
        }
        sink.cells.append(cell)
        sink.diagnostics.append(
            {
                "diagnostic": "fixed_interrupted",
                "diagnostic_wall_seconds": 0.02,
                "diagnostic_cpu_seconds": 0.01,
                "completed": False,
                "error": "fixed",
            }
        )
        meter = driver.ResourceMeter(
            started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=1),
            started_wall=time.monotonic() - 1,
            started_cpu=time.process_time(),
        )
        with patch.object(driver, "process_group_rss_bytes", return_value=4096):
            return driver.artifact_bytes(
                lock={"run_id": "UNIT-FIXED"},
                provenance={"commit": "a" * 40, "dirty": False, "command": "fixed-helper"},
                meter=meter,
                sink=sink,
                status="incomplete_fixture_inconclusive",
                error="fixed incomplete",
                decision={"branch": "inconclusive", "reasons": ["fixed"], "per_u": {}},
            )


@dataclass
class ReviewFixture:
    holder: tempfile.TemporaryDirectory[str]
    root: Path
    admission: dict[str, Any]
    source_paths: dict[Path, bytes]

    def close(self) -> None:
        self.holder.cleanup()


@contextlib.contextmanager
def patched_review_root(fixture: ReviewFixture) -> Iterator[None]:
    source_root = fixture.root / "experiments" / driver.EXPERIMENT_ID
    driver_path = source_root / "implementation" / driver.TASK_ID / "driver.py"
    with (
        patch.object(driver, "ROOT", fixture.root),
        patch.object(driver, "SPEC_PATH", source_root / "specification.yaml"),
        patch.object(driver, "AMENDMENT_PATH", source_root / "amendments" / f"{driver.AMENDMENT_ID}.yaml"),
        patch.object(driver, "PLAN_PATH", driver_path.with_name("execution-plan.json")),
        patch.object(driver, "__file__", str(driver_path)),
    ):
        yield


def build_review_fixture(
    *,
    minimal_attestation: bool = False,
    attestation_verdict: str = "holds",
    include_review_task: bool = True,
    include_checks_in_archive: bool = True,
    report_claim_owner: str = "fixed-owner",
    self_referential_receipt: bool = False,
    wrong_source_read: bool = False,
    wrong_report_snapshot: bool = False,
) -> ReviewFixture:
    holder = tempfile.TemporaryDirectory(prefix="validator-review-graph-")
    root = Path(holder.name).resolve()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Independent Fixed Validator")
    git(root, "config", "user.email", "validator@example.test")

    source_root = root / "experiments" / driver.EXPERIMENT_ID
    driver_path = source_root / "implementation" / driver.TASK_ID / "driver.py"
    plan_path = driver_path.with_name("execution-plan.json")
    source_paths = {
        driver_path: b"fixed independent driver bytes\n",
        plan_path: b'{"driver":{"sha256":"fixed"}}\n',
        source_root / "specification.yaml": b"fixed independent specification\n",
        source_root / "amendments" / f"{driver.AMENDMENT_ID}.yaml": b"fixed independent amendment\n",
    }
    for path, data in source_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "fixed reviewed source")
    reviewed = git(root, "rev-parse", "HEAD")

    review_task = "TASK-fixed-review"
    archive_task = "TASK-fixed-archive"
    joint = "Corrected executable spectral protocol and admission/custody conformance"
    plan_rel = "plans/fixed-review-plan.yaml"
    plan = {
        "review_plan": {
            "recorded_before_reviewers": True,
            "source_snapshot": reviewed,
            "joints": [{"joint": joint, "assigned_to": review_task, "attack_plan": "fixed", "breaking_artifact": "fixed"}],
            "blindness": {"mutual": False, "lifted_for": [review_task], "rationale": "fixed"},
        }
    }
    (root / plan_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / plan_rel).write_text(driver.yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    git(root, "add", plan_rel)
    git(root, "commit", "-q", "-m", "fixed precommitted review plan")
    plan_commit = git(root, "rev-parse", "HEAD")

    source_reads = {str(path.relative_to(root)): sha256(data) for path, data in source_paths.items()}
    if wrong_source_read:
        source_reads[str(driver_path.relative_to(root))] = "0" * 64
    attestation: dict[str, Any] = {
        "complete_source_read": True,
        "review_plan_path": plan_rel,
        "source_reads": source_reads,
    }
    if not minimal_attestation:
        attestation.update(
            {
                "task_id": review_task,
                "joints_owned": [joint],
                "sources_read": sorted(source_reads),
                "read_sibling_reports": False,
                "blind_from_respected": None,
                "verdict": attestation_verdict,
            }
        )

    report_rel = "reviews/TASK-fixed-review/review.yaml"
    checks_rel = "reviews/TASK-fixed-review/checks.py"
    receipt_rel = "archives/TASK-fixed-archive/snapshot.json"
    report = {
        "validation_report": {
            "task_id": review_task,
            "role": "validator",
            "source_snapshot_commit": "0" * 40 if wrong_report_snapshot else reviewed,
            "review_plan_path": plan_rel,
            "review_plan_commit": plan_commit,
            "claim_owner": report_claim_owner,
            "claim_session": "fixed-session",
            "claim_epoch": 1,
            "owned_joint_verdict": "PASS",
            "verdict": "passed",
            "inference": {
                "requested_policy": "review-adversarial",
                "resolved_model_id": "fixed-native-reviewer",
                "reasoning_effort": "xhigh",
                "independent_session": True,
                "fallback_used": False,
                "degraded_used": False,
                "bedrock_used": False,
                "provenance": "fixed independent synthetic assignment",
            },
            "review_attestation": attestation,
        }
    }
    (root / report_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / report_rel).write_text(driver.yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    (root / checks_rel).write_text("# fixed independent check source\n", encoding="utf-8")
    archived_sources = [report_rel] + ([checks_rel] if include_checks_in_archive else [])
    source_hashes = {relative: sha256((root / relative).read_bytes()) for relative in archived_sources}
    receipt: dict[str, Any] = {
        "schema": "crypto.autoresearch.review_snapshot.v1",
        "task_id": archive_task,
        "source_task_ids": [review_task],
        "parent_sha": plan_commit,
        "source_path_sha256": source_hashes,
    }
    if self_referential_receipt:
        receipt["commit_sha"] = "0" * 40
    (root / receipt_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / receipt_rel).write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", report_rel, receipt_rel)
    if include_checks_in_archive:
        git(root, "add", checks_rel)
    git(root, "commit", "-q", "-m", "fixed review archive")
    archive_commit = git(root, "rev-parse", "HEAD")
    archive_hashes = {**source_hashes, receipt_rel: sha256((root / receipt_rel).read_bytes())}

    queue_rel = "coordination/fixed-queue.json"
    tasks: list[dict[str, Any]] = []
    if include_review_task:
        tasks.append(
            {
                "id": review_task,
                "state": "completed",
                "to": "validator",
                "claim_owner": "fixed-owner",
                "claim_session": "fixed-session",
                "claim_epoch": 1,
                "write_scope": [report_rel, checks_rel],
                "inference": {"policy": "review-adversarial", "reasoning_effort": "xhigh"},
            }
        )
    tasks.append(
        {
            "id": archive_task,
            "state": "completed",
            "archive": {
                "kind": "snapshot",
                "source_task_ids": [review_task],
                "commit_sha": archive_commit,
                "parent_sha": plan_commit,
                "path_sha256": archive_hashes,
                "record_ids": [archive_task, review_task, driver.EXPERIMENT_ID],
            },
        }
    )
    queue = {"tasks": tasks}
    (root / queue_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / queue_rel).write_text(json.dumps(queue, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", queue_rel)
    git(root, "commit", "-q", "-m", "fixed external queue authority")
    external_commit = git(root, "rev-parse", "HEAD")

    admission = {
        "external_authority_commit": external_commit,
        "external_queue_path": queue_rel,
        "external_queue_sha256": sha256((root / queue_rel).read_bytes()),
        "archive_task_id": archive_task,
        "archive_commit": archive_commit,
        "snapshot_receipt_path": receipt_rel,
        "snapshot_receipt_sha256": archive_hashes[receipt_rel],
        "review_task_id": review_task,
        "review_report_path": report_rel,
        "review_report_sha256": archive_hashes[report_rel],
        "review_plan_path": plan_rel,
        "review_plan_commit": plan_commit,
        "review_plan_sha256": sha256((root / plan_rel).read_bytes()),
        "reviewed_source_snapshot": reviewed,
        "required_verdict": "PASS",
    }
    return ReviewFixture(holder, root, admission, source_paths)


class FixedConformanceChecks(unittest.TestCase):
    def test_01_rng_serialization_matches_frozen_bytes(self) -> None:
        params = (17, 1, 2, 19, 0, 0, 0)
        expected = int.from_bytes(
            hashlib.sha256(b'["EXP-ECDLP-651b94","control",[17,1,2,19,0,0,0],7,0]').digest(), "big"
        )
        self.assertEqual(driver.stream_digest(purpose="control", params=params, seed=7, counter=0), expected)

    def test_02_n_one_consumes_one_digest(self) -> None:
        self.assertEqual(
            driver.rejection_draw(purpose="query", params=(17, 1, 2, 19, 0, 0, 0), seed=7, counter=4, n=1),
            (0, 5),
        )

    def test_03_relabel_control_uses_u_zero_tuple(self) -> None:
        source = inspect.getsource(driver.future_cell)
        self.assertIn('purpose="control", params=(curve.p, curve.A, curve.B, r, 0, 0, 0)', source)

    def test_04_shuffle_uses_actual_u_and_arm(self) -> None:
        source = inspect.getsource(driver.future_cell)
        self.assertIn("params = (curve.p, curve.A, curve.B, r, 0, u, arm)", source)

    def test_05_guarded_shuffle_preserves_rng_output(self) -> None:
        params = (17, 1, 2, 19, 0, 2, 4)
        plain = driver.deterministic_shuffle(range(9), purpose="shuffle", params=params, seed=11)
        guarded = driver.deterministic_shuffle(range(9), purpose="shuffle", params=params, seed=11, check=lambda: None)
        self.assertEqual(plain, guarded)

    def test_06_subgroup_uses_one_repeated_addition_chain(self) -> None:
        class CyclicFive:
            def __init__(self) -> None:
                self.calls = 0

            def add(self, left: driver.Point, right: driver.Point) -> driver.Point:
                self.calls += 1
                value = ((0 if left is None else left[1]) + (0 if right is None else right[1])) % 5
                return None if value == 0 else (1, value)

        group = CyclicFive()
        points, certificate = driver.enumerate_subgroup(group, (1, 1), 5, lambda: None)
        self.assertEqual((group.calls, len(points), certificate["distinct"], certificate["r_times_G_is_O"]), (5, 5, True, True))

    def test_07_zero_yield_null_arm_work_is_charged(self) -> None:
        coordinate = synthetic_arm(successes=1)
        nulls = [synthetic_arm(transition=10, verification=0, successes=0), synthetic_arm(successes=2)]
        result = driver.cell_difference(coordinate, nulls)
        self.assertEqual((result["pooled_null_work"], result["pooled_null_successes"], result["zero_yield_null_arms"]), (15, 2, [1]))

    def test_08_zero_coordinate_success_is_unavailable(self) -> None:
        result = driver.cell_difference(synthetic_arm(successes=0), [synthetic_arm()])
        self.assertEqual((result["available"], result["d"], result["unavailable_reason"]), (False, None, "coordinate_zero_success"))

    def test_09_zero_pooled_null_success_is_unavailable(self) -> None:
        result = driver.cell_difference(synthetic_arm(), [synthetic_arm(successes=0)])
        self.assertEqual((result["available"], result["d"], result["unavailable_reason"]), (False, None, "pooled_null_zero_success"))

    def test_10_unequal_success_nulls_use_pooled_ratio(self) -> None:
        nulls = [synthetic_arm(transition=8, verification=0, successes=1), synthetic_arm(transition=18, verification=0, successes=3)]
        work, successes, cost = driver.pooled_null_cost(nulls)
        self.assertEqual((work, successes), (26, 4))
        self.assertAlmostEqual(float(cost), 6.5)
        self.assertNotAlmostEqual(float(cost), (8.0 + 6.0) / 2)

    def test_11_cell_difference_uses_log_cost_ratio(self) -> None:
        coordinate = synthetic_arm(transition=4, verification=0, successes=2)
        nulls = [synthetic_arm(transition=9, verification=0, successes=3)]
        self.assertAlmostEqual(driver.cell_difference(coordinate, nulls)["d"], math.log(3 / 2))

    def test_12_coordinate_certificate_failure_invalidates(self) -> None:
        coordinate = synthetic_arm()
        coordinate["failed_certificates"] = 1
        self.assertFalse(driver.reduce_validity(coordinate, [synthetic_arm()], valid_controls())["valid"])

    def test_13_null_certificate_failure_invalidates(self) -> None:
        null = synthetic_arm()
        null["failed_certificates"] = 1
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [null], valid_controls())["valid"])

    def test_14_cayley_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["cayley"]["passed"] = False
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_15_relabel_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["relabel"] = False
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_16_occupancy_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["occupancy"] = False
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_17_constant_o_denominator_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["known_false"]["constant_o"]["nonzero_denominators"] = 1
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_18_constant_o_solve_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["known_false"]["constant_o"]["solves"] = 1
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_19_mutated_candidate_failure_invalidates(self) -> None:
        controls = valid_controls()
        controls["known_false"]["mutated_candidate_fails_certificate"] = False
        self.assertFalse(driver.reduce_validity(synthetic_arm(), [synthetic_arm()], controls)["valid"])

    def test_20_missing_heldout_cell_is_inconclusive(self) -> None:
        self.assertEqual(driver.global_decision(panel()[:-1])["branch"], "inconclusive")

    def test_21_invalid_heldout_cell_is_inconclusive(self) -> None:
        cells = panel()
        cells[0]["validity"]["valid"] = False
        result = driver.global_decision(cells)
        self.assertEqual((result["branch"], result["panel_valid"]), ("inconclusive", False))

    def test_22_unavailable_heldout_cell_is_inconclusive(self) -> None:
        cells = panel()
        cells[0]["metric"]["available"] = False
        cells[0]["metric"]["d"] = None
        self.assertEqual(driver.global_decision(cells)["branch"], "inconclusive")

    def test_23_one_u_below_threshold_refuses_positive(self) -> None:
        cells = panel()
        for row in cells:
            if row["u"] == 3:
                row["metric"]["d"] = 0.1
        self.assertEqual(driver.global_decision(cells)["branch"], "inconclusive")

    def test_24_nonpositive_curve_mean_refuses_positive(self) -> None:
        cells = panel()
        for row in cells:
            if row["u"] == 1 and row["curve_id"] == "c0":
                row["metric"]["d"] = 0.0
        self.assertEqual(driver.global_decision(cells)["branch"], "inconclusive")

    def test_25_complete_positive_panel_is_positive(self) -> None:
        self.assertEqual(driver.global_decision(panel(0.3))["branch"], "positive")

    def test_26_complete_nonpositive_panel_is_negative(self) -> None:
        self.assertEqual(driver.global_decision(panel(-0.1))["branch"], "negative")

    def test_27_incomplete_canonical_payload_is_rejected(self) -> None:
        payload = artifact_payload()
        payload.pop("raw-result.json")
        with tempfile.TemporaryDirectory(prefix="validator-missing-artifact-") as temporary:
            root = Path(temporary)
            with self.assertRaises(ValueError):
                driver.atomic_publish(root, "unit-fixed", payload)
            self.assertFalse((root / "runs/unit-fixed").exists())

    def test_28_complete_synthetic_payload_publishes_exact_artifact_set(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-complete-artifact-") as temporary:
            root = Path(temporary)
            hashes = driver.atomic_publish(root, "unit-fixed", artifact_payload())
            final = root / "runs/unit-fixed"
            self.assertEqual({path.name for path in final.iterdir()}, set(driver.EXPERIMENT_ARTIFACTS))
            self.assertEqual(set(hashes), set(driver.EXPERIMENT_ARTIFACTS[:-1]))

    def test_29_artifact_report_uses_retained_coverage(self) -> None:
        report = fixed_artifact_bytes()["report.md"].decode()
        self.assertIn('"completed_cell_count": 1', report)
        self.assertIn('"accepted_fixture_count": 1', report)
        self.assertIn('"rejected_fixture_candidate_count": 1', report)

    def test_30_artifact_outputs_include_secondary_and_diagnostic_fields(self) -> None:
        payload = fixed_artifact_bytes()
        raw = json.loads(payload["raw-result.json"])
        self.assertIn("mean_first_repeat_length", raw["metrics"])
        self.assertIn("diagnostic_costs", raw["metrics"])
        self.assertIn("fixed_interrupted", payload["costs.csv"].decode())

    def test_31_resource_meter_has_one_terminal_utc_monotonic_cpu_bracket(self) -> None:
        meter = driver.ResourceMeter()
        first = meter.snapshot()
        second = meter.snapshot()
        self.assertEqual(first, second)
        self.assertGreaterEqual(datetime.fromisoformat(first["timing"]["finished_at"]), datetime.fromisoformat(first["timing"]["started_at"]))
        self.assertGreaterEqual(first["wall_seconds"], 0)
        self.assertGreaterEqual(first["cpu_seconds"], 0)

    def test_32_empty_rss_output_is_infrastructure_failure(self) -> None:
        fake = type("Result", (), {"stdout": ""})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_33_malformed_rss_row_is_infrastructure_failure(self) -> None:
        fake = type("Result", (), {"stdout": "9 7\n"})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_34_nonnumeric_rss_row_is_infrastructure_failure(self) -> None:
        fake = type("Result", (), {"stdout": "9 7 bad\n"})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_35_missing_current_process_rss_is_infrastructure_failure(self) -> None:
        fake = type("Result", (), {"stdout": "10 7 12\n"})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_36_current_process_wrong_group_is_infrastructure_failure(self) -> None:
        fake = type("Result", (), {"stdout": "9 8 12\n10 7 4\n"})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            with self.assertRaises(driver.InfrastructureStop):
                driver.process_group_rss_bytes()

    def test_37_valid_process_group_rss_is_summed(self) -> None:
        fake = type("Result", (), {"stdout": "9 7 12\n10 7 8\n11 4 99\n"})()
        with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
            self.assertEqual(driver.process_group_rss_bytes(), 20 * 1024)

    def test_38_valid_canonical_allocation_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-allocation-") as temporary:
            root = Path(temporary).resolve()
            lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(root), "authority_id": "DEC-fixed"}}
            with patch.object(driver, "canonical_experiment_run_root", return_value=root):
                self.assertEqual(driver.verify_run_allocation(lock, root), root)

    def test_39_wrong_canonical_allocation_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-allocation-a-") as first, tempfile.TemporaryDirectory(prefix="validator-allocation-b-") as second:
            canonical = Path(first).resolve()
            requested = Path(second).resolve()
            lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(canonical), "authority_id": "DEC-fixed"}}
            with patch.object(driver, "canonical_experiment_run_root", return_value=canonical), self.assertRaises(driver.LaunchRefused):
                driver.verify_run_allocation(lock, requested)

    def test_40_symlink_allocation_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-allocation-target-") as target, tempfile.TemporaryDirectory(prefix="validator-allocation-link-") as parent:
            canonical = Path(target).resolve()
            link = Path(parent) / "root-link"
            link.symlink_to(canonical, target_is_directory=True)
            lock = {"run_id": "RUN-ECDLP-abcdef", "run_allocation": {"run_id": "RUN-ECDLP-abcdef", "experiment_id": driver.EXPERIMENT_ID, "canonical_run_root": str(canonical), "authority_id": "DEC-fixed"}}
            with patch.object(driver, "canonical_experiment_run_root", return_value=canonical), self.assertRaises(driver.LaunchRefused):
                driver.verify_run_allocation(lock, link)

    def test_41_canonical_run_id_is_accepted(self) -> None:
        driver.canonical_run_id("RUN-ECDLP-abcdef")

    def test_42_uppercase_run_id_is_rejected(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.canonical_run_id("RUN-ECDLP-ABCDEf")

    def test_43_short_run_id_is_rejected(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.canonical_run_id("RUN-ECDLP-abcde")

    def test_44_surplus_run_id_is_rejected(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.canonical_run_id("RUN-ECDLP-abcdef-extra")

    def test_45_wrong_area_run_id_is_rejected(self) -> None:
        with self.assertRaises(driver.LaunchRefused):
            driver.canonical_run_id("RUN-OTHER-abcdef")

    def test_46_quarantine_parent_fsync_failure_is_not_claimed_durable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-publication-failure-") as temporary:
            runs = Path(temporary) / "runs"
            final = runs / "exposed"
            final.mkdir(parents=True)

            def fsync_with_parent_failure(path: Path) -> None:
                if path == runs:
                    raise OSError("fixed parent fsync failure")

            with patch.object(driver, "fsync_directory", side_effect=fsync_with_parent_failure):
                result = driver.retain_publication_failure(
                    runs=runs,
                    run_id="unit-fixed",
                    staging=runs / "staging",
                    final=final,
                    error=OSError("fixed post-rename failure"),
                    phase="post_rename_durability",
                )
        self.assertNotEqual(result["state"], "quarantined", "failed parent fsync cannot truthfully claim durable quarantine")

    def test_47_failed_certificate_stops_census_after_retention(self) -> None:
        class MockCurve:
            def scalar(self, scalar: int, _point: driver.Point) -> driver.Point:
                return (scalar, scalar)

        certificates: list[dict[str, Any]] = []

        def repeat_with_nonzero_denominator(_curve: Any, state: driver.Point, _g: driver.Point, _q: driver.Point, a: int, b: int, _r: int, _assignment: Any) -> tuple[driver.Point, int, int, str]:
            return state, a, b + 1, "add"

        with patch.object(driver, "rho_step", side_effect=repeat_with_nonzero_denominator), patch.object(driver, "binary_verifier", return_value=(None, 0, 1)):
            with self.assertRaises(driver.MeasurementInvalidStop):
                driver.collision_census(MockCurve(), (1, 1), (2, 2), 3, None, lambda: None, certificates.append)
        self.assertEqual(len(certificates), 1)

    def test_48_collision_censuses_have_interrupted_diagnostic_meter_wrapper(self) -> None:
        tree = ast.parse(inspect.getsource(driver.future_cell))
        direct_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "collision_census"]
        self.assertEqual(len(direct_calls), 0, "direct census calls lose interrupted CPU/wall diagnostic custody")

    def test_49_measured_diagnostic_records_memory_observation(self) -> None:
        self.assertIn("process_group_rss_bytes", inspect.getsource(driver.measured_diagnostic))

    def test_50_coordinate_partition_guard_persists_progress_coordinates(self) -> None:
        source = inspect.getsource(driver.future_cell)
        self.assertNotIn('guarded_checkpoint(check, point_index, "coordinate_partition", None', source)

    def test_51_subgroup_guard_accepts_progress_callback(self) -> None:
        self.assertIn("on_progress", inspect.signature(driver.enumerate_subgroup).parameters)

    def test_52_collision_guard_accepts_progress_callback(self) -> None:
        self.assertIn("on_progress", inspect.signature(driver.collision_census).parameters)

    def test_53_artifact_assembly_has_machine_guard(self) -> None:
        parameters = inspect.signature(driver.artifact_bytes).parameters
        source = inspect.getsource(driver.artifact_bytes)
        self.assertTrue("check" in parameters and "guarded_checkpoint" in source)

    def test_54_complete_review_graph_is_accepted(self) -> None:
        fixture = build_review_fixture()
        try:
            with patched_review_root(fixture):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_55_minimal_nonstandard_attestation_is_rejected(self) -> None:
        fixture = build_review_fixture(minimal_attestation=True)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_56_external_queue_without_review_task_is_rejected(self) -> None:
        fixture = build_review_fixture(include_review_task=False)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_57_contradictory_attestation_verdict_is_rejected(self) -> None:
        fixture = build_review_fixture(attestation_verdict="breaks")
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_58_archive_missing_declared_check_artifact_is_rejected(self) -> None:
        fixture = build_review_fixture(include_checks_in_archive=False)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_59_report_claim_mismatch_is_rejected(self) -> None:
        fixture = build_review_fixture(report_claim_owner="forged-owner")
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_60_self_referential_archive_receipt_is_rejected(self) -> None:
        fixture = build_review_fixture(self_referential_receipt=True)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_61_wrong_review_source_read_hash_is_rejected(self) -> None:
        fixture = build_review_fixture(wrong_source_read=True)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_62_wrong_report_snapshot_role_is_rejected(self) -> None:
        fixture = build_review_fixture(wrong_report_snapshot=True)
        try:
            with patched_review_root(fixture), self.assertRaises(driver.LaunchRefused):
                driver.verify_review_admission(fixture.admission, fixture.admission["reviewed_source_snapshot"], fixture.admission["external_authority_commit"])
        finally:
            fixture.close()

    def test_63_protocol_coverage_names_all_accepted_repairs(self) -> None:
        coverage = driver.protocol_coverage()
        expected = {f"V-{number:02d}" for number in range(1, 9)} | {f"S2-{number:02d}" for number in range(1, 9)}
        observed = {key.split("_")[0] for key in coverage}
        self.assertTrue(expected.issubset(observed))

    def test_64_typed_operational_outcomes_are_distinct(self) -> None:
        source = inspect.getsource(driver.run_future_pipeline)
        self.assertIn("except IncompleteFixtureStop", source)
        self.assertIn('status, error = "incomplete_fixture_inconclusive"', source)
        self.assertIn('status, error = "failed_implementation"', source)
        self.assertIn('status, error = "failed_infrastructure"', source)

    def test_65_exploratory_stream_precedes_heldout_stream(self) -> None:
        source = inspect.getsource(driver.run_future_pipeline)
        self.assertLess(source.index('(\"exploratory\", EXPLORATORY_SEEDS)'), source.index('(\"heldout\", HELDOUT_SEEDS)'))

    def test_66_cell_is_retained_before_invalid_stop(self) -> None:
        source = inspect.getsource(driver.run_future_pipeline)
        self.assertLess(source.index("sink.record_cell(cell)"), source.index("raise MeasurementInvalidStop"))

    def test_67_cayley_source_has_nested_progress_coordinates(self) -> None:
        source = inspect.getsource(driver.cayley_tv_curve)
        for text in ("requested_step=requested", "iteration=iteration", "destination=destination", "origin=origin", "state=state"):
            self.assertIn(text, source)

    def test_68_import_does_not_invoke_future_entrypoints(self) -> None:
        source = Path(driver.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        top_level_calls = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
        self.assertEqual(top_level_calls, [])


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed conformance case exceeded 10 seconds")


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
        self.case_timings.append(
            {
                "id": test.id(),
                "wall_seconds": round(time.monotonic() - wall, 6),
                "cpu_seconds": round(time.process_time() - cpu, 6),
            }
        )
        super().stopTest(test)


class TimedRunner(unittest.TextTestRunner):
    resultclass = TimedResult


def main() -> int:
    signal.signal(signal.SIGALRM, timeout_handler)
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FixedConformanceChecks)
    result: TimedResult = TimedRunner(verbosity=2).run(suite)  # type: ignore[assignment]
    summary = {
        "schema": "crypto.autoresearch.independent_fixed_conformance_timing.v1",
        "task_id": "TASK-20260908-b7af43",
        "case_executions": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures) + len(result.errors),
        "failure_ids": [test.id() for test, _trace in result.failures],
        "error_ids": [test.id() for test, _trace in result.errors],
        "maximum_case_wall_seconds": max((row["wall_seconds"] for row in result.case_timings), default=0.0),
        "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in result.case_timings), default=0.0),
        "aggregate_script_wall_seconds": round(time.monotonic() - started_wall, 6),
        "aggregate_script_cpu_seconds": round(time.process_time() - started_cpu, 6),
        "case_timings": result.case_timings,
        "scientific_runs": 0,
        "maximum_workers": 1,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

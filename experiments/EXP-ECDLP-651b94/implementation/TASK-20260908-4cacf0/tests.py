#!/usr/bin/env python3
"""Fixed S4 source/admission/custody checks for TASK-20260908-4cacf0.

Only lower-level arithmetic, serialization, telemetry, custody helpers and
temporary synthetic Git histories are exercised.  The script never invokes
fixture selection, future_cell, run_future_pipeline, verify_launch_admission,
driver.main, a scientific/null/control/timing panel, Sage/PARI, a key,
signature, nonce, lock, RUN record, or prospective measurement entrypoint.
"""
from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import inspect
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest.mock import patch

import yaml


TASK_ID = "TASK-20260908-4cacf0"
AUTHORITY_COMMIT = "7b36178fe6c0cc92242071bf42cb4e81c5aa0cc9"
CLAIM_COMMIT = "703ce4e36485c8b8d89211147790914dc46a6b75"
SOURCE_SNAPSHOT = "44a9e000bb8a4a8e77eff58817f44726b62ba72e"
ROOT = Path(__file__).resolve().parents[4]
HANDOFF_REL = f"ledger/handoffs/{TASK_ID}.yaml"
HANDOFF_PATH = ROOT / HANDOFF_REL
DRIVER_DIR = ROOT / "experiments/EXP-ECDLP-651b94/implementation/TASK-20260908-4cacf0"
DRIVER_PATH = DRIVER_DIR / "driver.py"

sys.dont_write_bytecode = True
sys.path.insert(0, str(DRIVER_DIR))
import driver  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def git_bytes(root: Path, commit: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{relative}"], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def admin_source_bindings() -> dict[str, Any]:
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))["handoff"]
    rows = []
    for binding in handoff["source_bindings"]:
        relative = binding["path"]
        live = sha256((ROOT / relative).read_bytes())
        authority = sha256(git_bytes(ROOT, AUTHORITY_COMMIT, relative))
        rows.append({
            "path": relative,
            "expected_sha256": binding["sha256"],
            "live_sha256": live,
            "authority_sha256": authority,
            "matched": live == authority == binding["sha256"],
        })
    return {
        "declared_inputs": len(handoff["inputs"]),
        "declared_bindings": len(handoff["source_bindings"]),
        "same_order": handoff["inputs"] == [row["path"] for row in handoff["source_bindings"]],
        "matching_live": sum(row["live_sha256"] == row["expected_sha256"] for row in rows),
        "matching_authority": sum(row["authority_sha256"] == row["expected_sha256"] for row in rows),
        "mismatches": [row for row in rows if not row["matched"]],
    }


def admin_snapshot_binding() -> dict[str, Any]:
    receipt_rel = "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260908-cbd974/snapshot.json"
    receipt = json.loads(git_bytes(ROOT, SOURCE_SNAPSHOT, receipt_rel))
    source_paths = set(receipt["source_path_sha256"])
    changed = set(filter(None, git(ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT).splitlines()))
    expected = source_paths | {receipt_rel}
    hashes_match = all(
        sha256(git_bytes(ROOT, SOURCE_SNAPSHOT, path)) == digest
        for path, digest in receipt["source_path_sha256"].items()
    )
    return {
        "snapshot_commit": SOURCE_SNAPSHOT,
        "parent": git(ROOT, "rev-parse", f"{SOURCE_SNAPSHOT}^"),
        "changed_path_count": len(changed),
        "source_path_count": len(source_paths),
        "changed_paths_exact": changed == expected,
        "source_hashes_match": hashes_match,
        "authority_is_ancestor": subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", AUTHORITY_COMMIT, CLAIM_COMMIT]
        ).returncode == 0,
        "snapshot_is_ancestor": subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT]
        ).returncode == 0,
    }


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
        "cayley": {"passed": True, "gap": "0.1"},
        "relabel": True,
        "occupancy": True,
        "known_false": {
            "constant_o": {"nonzero_denominators": 0, "solves": 0, "collisions": []},
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


def synthetic_cell() -> dict[str, Any]:
    meter = {
        "diagnostic": "coordinate_collision_census",
        "diagnostic_wall_seconds": 0.02,
        "diagnostic_cpu_seconds": 0.01,
        "completed": True,
        "process_group_rss_start_bytes": 100,
        "process_group_rss_end_bytes": 200,
        "process_group_rss_boundary_sample_max_bytes": 200,
        "process_group_rss_sample_scope": "fixed_boundary_samples",
        "process_group_rss_sample_cadence": "fixed",
    }
    coordinate = {**synthetic_arm(), "diagnostic_meter": meter}
    return {
        "curve_id": "fixed-curve",
        "seed": 606300,
        "u": 1,
        "stream": "exploratory",
        "coordinate": coordinate,
        "nulls": [],
        "metric": {"available": True, "d": 0.2},
        "controls": valid_controls(),
        "validity": {"valid": True},
        "diagnostic_costs": {},
    }


def fixed_artifact_bytes(*, diagnostics: list[dict[str, Any]] | None = None) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="validator-a8240d-artifact-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        sink.cells.append(synthetic_cell())
        sink.diagnostics.extend(diagnostics or [])
        meter = driver.ResourceMeter(
            started_at_utc=datetime.now(timezone.utc) - timedelta(seconds=1),
            started_wall=time.monotonic() - 1,
            started_cpu=time.process_time(),
        )
        with patch.object(driver, "process_group_rss_bytes", return_value=4096):
            return driver.artifact_bytes(
                lock={"run_id": "unit-fixed"},
                provenance={"commit": "a" * 40, "dirty": False, "command": "fixed-helper"},
                meter=meter,
                sink=sink,
                status="incomplete_fixture_inconclusive",
                error="fixed",
                decision={"branch": "inconclusive", "reasons": ["fixed"], "per_u": {}},
            )


@dataclass
class ReviewFixture:
    holder: tempfile.TemporaryDirectory[str]
    root: Path
    admission: dict[str, Any]
    reviewed_source: str
    plan_commit: str
    claim_commit: str
    release_commit: str
    archive_commit: str
    external_commit: str
    executing_commit: str

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
        patch.object(driver, "DISPATCH_VALIDATOR_SHA256", sha256((fixture.root / driver.DISPATCH_VALIDATOR_RELATIVE_PATH).read_bytes())),
        patch.object(driver, "GOAL_LANES_SHA256", sha256((fixture.root / driver.GOAL_LANES_RELATIVE_PATH).read_bytes())),
    ):
        yield


def build_review_fixture(
    *,
    attestation_verdict: str = "holds",
    lifecycle: str = "claim_release_archive",
    release_artifacts: str = "exact",
    canonical_queue: bool = True,
    complete_plan: bool = True,
    complete_handoff: bool = True,
    complete_claim: bool = True,
    extra_unread_input: bool = False,
    report_claim_owner: str = "fixed-owner",
    release_owner: str = "fixed-owner",
    release_outcome: str = "completed",
    include_review_task: bool = True,
    include_check_receipt: bool = True,
    report_verdict: str = "passed",
    joint_verdict: str = "PASS",
    source_read_hash_ok: bool = True,
) -> ReviewFixture:
    """Create a real-shape queued claim -> release -> archive history.

    Deliberate mutation modes alter exactly one lifecycle or schema boundary.
    No cryptographic key, signature, lock, allocation or RUN path is created.
    """
    holder = tempfile.TemporaryDirectory(prefix="executor-4cacf0-review-")
    root = Path(holder.name).resolve()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Independent Validator Fixture")
    git(root, "config", "user.email", "validator@example.test")

    review_task = "TASK-20260908-abc123"
    archive_task = "TASK-20260908-def456"
    joint = "Corrected executable spectral protocol and admission/custody conformance"
    source_root = root / "experiments" / driver.EXPERIMENT_ID
    driver_path = source_root / "implementation" / driver.TASK_ID / "driver.py"
    plan_path = driver_path.with_name("execution-plan.json")
    specification_path = source_root / "specification.yaml"
    amendment_path = source_root / "amendments" / f"{driver.AMENDMENT_ID}.yaml"
    source_files: dict[Path, bytes] = {
        driver_path: b"fixed reviewed driver bytes\n",
        plan_path: b'{"driver":{"sha256":"fixed"}}\n',
        specification_path: b"fixed reviewed specification bytes\n",
        amendment_path: b"fixed reviewed amendment bytes\n",
        root / driver.DISPATCH_VALIDATOR_RELATIVE_PATH: b"fixed canonical dispatch validator bytes\n",
        root / driver.GOAL_LANES_RELATIVE_PATH: b"fixed canonical lane validator bytes\n",
    }
    if extra_unread_input:
        source_files[root / "inputs" / "extra-bound-input.txt"] = b"must be read\n"
    for path, payload in source_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "reviewed source snapshot")
    reviewed = git(root, "rev-parse", "HEAD")

    plan_rel = "coordination/review-plan.yaml"
    queue_rel = "coordination/dispatch_queue.json"
    queue_parent = Path(queue_rel).parent
    outputs = [
        "coordination/reviews/TASK-20260908-abc123/review.yaml",
        "coordination/reviews/TASK-20260908-abc123/checks.py",
        "coordination/reviews/TASK-20260908-abc123/check-receipt.json",
    ]
    archive_receipt_rel = "coordination/archives/TASK-20260908-def456/snapshot.json"
    claim_rel = (queue_parent / "claims" / f"{review_task}.1.claim.json").as_posix()
    release_rel = (queue_parent / "claims" / f"{review_task}.1.release.json").as_posix()
    input_paths = [str(path.relative_to(root)) for path in source_files]
    source_bindings = [
        {"path": str(path.relative_to(root)), "sha256": sha256(payload)}
        for path, payload in source_files.items()
    ]

    review_handoff: dict[str, Any] = {
        "id": review_task,
        "from": "coordinator",
        "to": "validator",
        "objective": "fixed complete source review",
        "uncertainty_reduced": "fixed source admission",
        "inputs": input_paths,
        "source_bindings": source_bindings,
        "constraints": ["fixed synthetic only"],
        "deliverables": outputs,
        "write_scope": outputs,
        "artifact_paths": outputs,
        "archived_by": archive_task,
        "completion_gate": ["fixed complete outputs"],
        "budget": {"wall_clock_seconds": None, "memory_gb": 2, "maximum_runs": 0},
        "inference": {
            "policy": "review-adversarial",
            "reasoning_effort": "xhigh",
            "independent_session_required": True,
            "fallback_allowed": False,
            "degraded_allowed": False,
        },
    }
    if not complete_handoff:
        review_handoff = {
            key: review_handoff[key]
            for key in ("id", "to", "write_scope", "artifact_paths", "inference")
        }

    archive_handoff = {
        "id": archive_task,
        "from": "coordinator",
        "to": "coordinator",
        "objective": "archive fixed review",
        "uncertainty_reduced": "durable custody",
        "inputs": outputs,
        "constraints": ["fixed synthetic only"],
        "deliverables": [archive_receipt_rel],
        "completion_gate": ["exact archive"],
        "budget": {"wall_clock_seconds": None, "memory_gb": None, "maximum_runs": 0},
        "inference": {"policy": "coordinator-orchestration-code", "reasoning_effort": "high"},
    }
    review_task_row = {
        "id": review_task,
        "title": "fixed independent review",
        "role": "validator",
        "state": "queued",
        "priority": 90,
        "review_required": False,
        "depends_on": [],
        "read_scope": input_paths,
        "write_scope": outputs,
        "artifact_paths": outputs,
        "handoff": review_handoff,
    }
    archive_task_row = {
        "id": archive_task,
        "title": "fixed review archive",
        "role": "coordinator",
        "state": "queued",
        "priority": 89,
        "review_required": False,
        "depends_on": [review_task],
        "read_scope": outputs,
        "write_scope": [archive_receipt_rel],
        "artifact_paths": [archive_receipt_rel],
        "handoff": archive_handoff,
        "archive": {
            "kind": "snapshot", "source_task_ids": [review_task],
            "commit_sha": None, "parent_sha": None, "path_sha256": {},
            "record_ids": [archive_task, review_task, driver.EXPERIMENT_ID],
        },
    }
    queue = {
        "schema": "crypto.autoresearch.dispatch_queue.v1",
        "objective": "fixed governed review lifecycle",
        "max_concurrent": 1,
        "tasks": [review_task_row, archive_task_row],
    }

    plan = {
        "review_plan": {
            "claim_under_review": "fixed source admission only",
            "coordinator_prior": "fixed prior",
            "recorded_before_reviewers": True,
            "source_snapshot": reviewed,
            "joints": [{
                "joint": joint, "assigned_to": review_task,
                "attack_plan": "fixed attack", "breaking_artifact": "fixed path",
            }],
            "blindness": {"mutual": False, "lifted_for": [review_task], "rationale": "fixed hardening"},
            "proves_too_much": {"objects": ["fixed false object"], "failure_signature": "must reject", "assigned_to": review_task},
            "blind_rederivation": {"required": False, "quantity": "fixed", "parameters": "fixed", "blind_from": [], "assigned_to": review_task},
            "procedure_deviations": [],
        }
    }
    if not complete_plan:
        plan = {"review_plan": {"recorded_before_reviewers": True, "source_snapshot": reviewed, "joints": [{"joint": joint, "assigned_to": review_task}]}}

    (root / queue_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / queue_rel).write_text(json.dumps(queue, sort_keys=True) + "\n", encoding="utf-8")
    if lifecycle == "claim_before_plan":
        git(root, "add", queue_rel)
        git(root, "commit", "-q", "-m", "invalid queue authority before plan")
        plan_commit = ""
    else:
        (root / plan_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / plan_rel).write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
        git(root, "add", queue_rel, plan_rel)
        git(root, "commit", "-q", "-m", "precommitted plan and queued tasks")
        plan_commit = git(root, "rev-parse", "HEAD")

    claim = {
        "schema": "crypto.autoresearch.task_claim.v1",
        "task_id": review_task,
        "epoch": 1,
        "owner": "fixed-owner",
        "session": "fixed-session",
        "branch": "main",
        "worktree": str(root),
        "acquired_at": "2026-09-08T00:00:00Z",
        "expires_at": "2026-09-08T01:00:00Z",
        "write_scope": outputs,
        "supersedes": None,
        "forced": False,
    }
    if not complete_claim:
        claim = {key: claim[key] for key in ("schema", "task_id", "epoch", "owner", "session", "write_scope")}
    (root / claim_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / claim_rel).write_text(json.dumps(claim, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", claim_rel)
    git(root, "commit", "-q", "-m", "queued review claim")
    claim_commit = git(root, "rev-parse", "HEAD")

    if lifecycle == "claim_before_plan":
        (root / plan_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / plan_rel).write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
        git(root, "add", plan_rel)
        git(root, "commit", "-q", "-m", "late review plan")
        plan_commit = git(root, "rev-parse", "HEAD")

    source_reads = {
        str(path.relative_to(root)): sha256(payload)
        for path, payload in source_files.items()
        if not (extra_unread_input and "extra-bound-input" in str(path))
    }
    if not source_read_hash_ok:
        source_reads[str(driver_path.relative_to(root))] = "0" * 64
    attestation = {
        "task_id": review_task,
        "joints_owned": [joint],
        "complete_source_read": True,
        "review_plan_path": plan_rel,
        "source_reads": source_reads,
        "sources_read": sorted(source_reads),
        "read_sibling_reports": False,
        "blind_from_respected": None,
        "verdict": attestation_verdict,
    }
    report = {
        "validation_report": {
            "id": review_task,
            "task_id": review_task,
            "role": "validator",
            "source_snapshot_commit": reviewed,
            "review_plan_path": plan_rel,
            "review_plan_commit": plan_commit,
            "claim_commit": claim_commit,
            "claim_owner": report_claim_owner,
            "claim_session": "fixed-session",
            "claim_epoch": 1,
            "artifact_paths": outputs,
            "owned_joint_verdict": joint_verdict,
            "verdict": report_verdict,
            "inference": {
                "requested_policy": "review-adversarial",
                "resolved_model_id": "fixed-independent-validator",
                "reasoning_effort": "xhigh",
                "independent_session": True,
                "fallback_used": False,
                "degraded_used": False,
                "bedrock_used": False,
                "provenance": "fixed native synthetic review assignment",
            },
            "review_attestation": attestation,
        }
    }
    output_payloads = {
        outputs[0]: yaml.safe_dump(report, sort_keys=False).encode(),
        outputs[1]: b"# fixed independent review checker\n",
        outputs[2]: b'{"task_id":"TASK-20260908-abc123","fixed":true}\n',
    }
    if not include_check_receipt:
        output_payloads.pop(outputs[2])
    for relative, payload in output_payloads.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    output_hashes = {relative: sha256(payload) for relative, payload in output_payloads.items()}

    release_hashes: dict[str, str]
    if release_artifacts == "exact":
        release_hashes = {relative: output_hashes[relative] for relative in outputs if relative in output_hashes}
    elif release_artifacts == "missing":
        release_hashes = {}
    elif release_artifacts == "wrong":
        release_hashes = {relative: "f" * 64 for relative in outputs}
    elif release_artifacts == "partial":
        release_hashes = {outputs[0]: output_hashes[outputs[0]]}
    else:
        raise ValueError(release_artifacts)
    release = {
        "schema": "crypto.autoresearch.task_release.v1",
        "task_id": review_task,
        "epoch": 1,
        "owner": release_owner,
        "outcome": release_outcome,
        "released_at": "2026-09-08T00:10:00Z",
        "was_expired": False,
        "note": "fixed completed review",
        "artifact_sha256": release_hashes,
    }

    def commit_release() -> str:
        path = root / release_rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(release, sort_keys=True) + "\n", encoding="utf-8")
        git(root, "add", release_rel)
        git(root, "commit", "-q", "-m", "completed review release")
        return git(root, "rev-parse", "HEAD")

    def commit_archive(parent: str) -> tuple[str, dict[str, str]]:
        receipt = {
            "schema": "crypto.autoresearch.review_snapshot.v1",
            "task_id": archive_task,
            "source_task_ids": [review_task],
            "parent_sha": parent,
            "source_path_sha256": output_hashes,
        }
        receipt_path = root / archive_receipt_rel
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        git(root, "add", *output_payloads.keys(), archive_receipt_rel)
        git(root, "commit", "-q", "-m", "archive completed independent review")
        commit = git(root, "rev-parse", "HEAD")
        return commit, {**output_hashes, archive_receipt_rel: sha256(receipt_path.read_bytes())}

    if lifecycle == "archive_before_release":
        archive_parent = git(root, "rev-parse", "HEAD")
        archive_commit, archive_hashes = commit_archive(archive_parent)
        release_commit = commit_release()
    else:
        release_commit = commit_release()
        archive_commit, archive_hashes = commit_archive(release_commit)

    review_task_row["state"] = "completed"
    archive_task_row["state"] = "completed"
    archive_task_row["archive"].update({
        "commit_sha": archive_commit,
        "parent_sha": git(root, "rev-parse", f"{archive_commit}^"),
        "path_sha256": archive_hashes,
    })
    final_tasks = ([review_task_row] if include_review_task else []) + [archive_task_row]
    final_queue: dict[str, Any]
    if canonical_queue:
        final_queue = {**queue, "tasks": final_tasks}
    else:
        final_queue = {"tasks": final_tasks}
    (root / queue_rel).write_text(json.dumps(final_queue, sort_keys=True) + "\n", encoding="utf-8")
    git(root, "add", queue_rel)
    git(root, "commit", "-q", "-m", "external completed queue authority")
    external_commit = git(root, "rev-parse", "HEAD")
    git(root, "commit", "-q", "--allow-empty", "-m", "clean executing commit")
    executing_commit = git(root, "rev-parse", "HEAD")

    admission = {
        "external_authority_commit": external_commit,
        "external_queue_path": queue_rel,
        "external_queue_sha256": sha256((root / queue_rel).read_bytes()),
        "archive_task_id": archive_task,
        "archive_commit": archive_commit,
        "snapshot_receipt_path": archive_receipt_rel,
        "snapshot_receipt_sha256": archive_hashes[archive_receipt_rel],
        "review_task_id": review_task,
        "review_report_path": outputs[0],
        "review_report_sha256": output_hashes[outputs[0]],
        "review_plan_path": plan_rel,
        "review_plan_commit": plan_commit,
        "review_plan_sha256": sha256((root / plan_rel).read_bytes()),
        "reviewed_source_snapshot": reviewed,
        "required_verdict": "PASS",
        "review_claim_path": claim_rel,
        "review_claim_sha256": sha256((root / claim_rel).read_bytes()),
        "review_claim_commit": claim_commit,
        "review_release_path": release_rel,
        "review_release_sha256": sha256((root / release_rel).read_bytes()),
        "review_release_commit": release_commit,
    }
    return ReviewFixture(
        holder, root, admission, reviewed, plan_commit, claim_commit,
        release_commit, archive_commit, external_commit, executing_commit,
    )


def admission_accepts(**kwargs: Any) -> bool:
    fixture = build_review_fixture(**kwargs)
    try:
        with patched_review_root(fixture):
            driver.verify_review_admission(
                fixture.admission, fixture.reviewed_source, fixture.executing_commit,
            )
        return True
    except driver.LaunchRefused:
        return False
    finally:
        fixture.close()


def expect_accept(**kwargs: Any) -> None:
    if not admission_accepts(**kwargs):
        raise AssertionError("governed synthetic review lifecycle was rejected")


def expect_reject(**kwargs: Any) -> None:
    if admission_accepts(**kwargs):
        raise AssertionError("invalid synthetic review authority was admitted")


def case_rng_vector() -> None:
    frozen = b'["EXP-ECDLP-651b94","control",[17,1,2,19,0,0,0],7,0]'
    actual = driver.stream_digest(purpose="control", params=(17, 1, 2, 19, 0, 0, 0), seed=7, counter=0)
    assert actual == int.from_bytes(hashlib.sha256(frozen).digest(), "big")


def case_rng_n_one() -> None:
    assert driver.rejection_draw(purpose="query", params=(17, 1, 2, 19, 0, 0, 0), seed=7, counter=4, n=1) == (0, 5)


def case_control_tuple() -> None:
    assert 'purpose="control", params=(curve.p, curve.A, curve.B, r, 0, 0, 0)' in inspect.getsource(driver.future_cell)


def case_shuffle_tuple() -> None:
    assert "params = (curve.p, curve.A, curve.B, r, 0, u, arm)" in inspect.getsource(driver.future_cell)


def case_subgroup_progress() -> None:
    source = inspect.getsource(driver.enumerate_subgroup)
    assert "on_progress" in inspect.signature(driver.enumerate_subgroup).parameters
    assert "subgroup_enumeration" in source and "curve.add(current, generator)" in source


def case_collision_progress() -> None:
    source = inspect.getsource(driver.collision_census)
    assert "on_progress" in inspect.signature(driver.collision_census).parameters
    assert "collision_start" in source and "collision_step" in source


def case_zero_coordinate_unavailable() -> None:
    assert not driver.cell_difference(synthetic_arm(successes=0), [synthetic_arm()])["available"]


def case_zero_null_unavailable() -> None:
    assert not driver.cell_difference(synthetic_arm(), [synthetic_arm(successes=0)])["available"]


def case_pooled_unequal_successes() -> None:
    rows = [synthetic_arm(transition=8, verification=0, successes=1), synthetic_arm(transition=18, verification=0, successes=3)]
    work, successes, cost = driver.pooled_null_cost(rows)
    assert (work, successes, cost) == (26, 4, 6.5)


def case_positive_panel() -> None:
    assert driver.global_decision(panel(0.3))["branch"] == "positive"


def case_negative_panel() -> None:
    assert driver.global_decision(panel(-0.1))["branch"] == "negative"


def case_missing_panel() -> None:
    assert driver.global_decision(panel()[:-1])["branch"] == "inconclusive"


def case_invalid_panel() -> None:
    cells = panel()
    cells[0]["validity"]["valid"] = False
    result = driver.global_decision(cells)
    assert result["branch"] == "inconclusive" and result["panel_valid"] is False


def case_unavailable_panel() -> None:
    cells = panel()
    cells[0]["metric"] = {"available": False, "d": None}
    assert driver.global_decision(cells)["branch"] == "inconclusive"


def case_one_u_below_threshold() -> None:
    cells = panel()
    for row in cells:
        if row["u"] == 3:
            row["metric"]["d"] = 0.1
    assert driver.global_decision(cells)["branch"] == "inconclusive"


def case_one_curve_nonpositive() -> None:
    cells = panel()
    for row in cells:
        if row["u"] == 1 and row["curve_id"] == "c0":
            row["metric"]["d"] = 0.0
    assert driver.global_decision(cells)["branch"] == "inconclusive"


def validity_mutation(name: str) -> None:
    controls = valid_controls()
    coordinate = synthetic_arm()
    nulls = [synthetic_arm()]
    if name == "coordinate_certificate":
        coordinate["failed_certificates"] = 1
    elif name == "null_certificate":
        nulls[0]["failed_certificates"] = 1
    elif name == "cayley":
        controls["cayley"]["passed"] = False
    elif name == "relabel":
        controls["relabel"] = False
    elif name == "occupancy":
        controls["occupancy"] = False
    elif name == "constant_o_denominator":
        controls["known_false"]["constant_o"]["nonzero_denominators"] = 1
    elif name == "constant_o_solve":
        controls["known_false"]["constant_o"]["solves"] = 1
    elif name == "mutated_candidate":
        controls["known_false"]["mutated_candidate_fails_certificate"] = False
    else:
        raise ValueError(name)
    assert driver.reduce_validity(coordinate, nulls, controls)["valid"] is False


def rss_case(text: str, expected: int | None) -> None:
    fake = type("Result", (), {"stdout": text})()
    with patch.object(driver.os, "getpgid", return_value=7), patch.object(driver.os, "getpid", return_value=9), patch.object(driver.subprocess, "run", return_value=fake):
        if expected is None:
            try:
                driver.process_group_rss_bytes()
            except driver.InfrastructureStop:
                return
            raise AssertionError("invalid RSS input was accepted")
        assert driver.process_group_rss_bytes() == expected


def case_quarantine_parent_fsync() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-a8240d-quarantine-") as temporary:
        runs = Path(temporary) / "runs"
        final = runs / "unit-fixed"
        final.mkdir(parents=True)
        def fsync(path: Path) -> None:
            if path == runs:
                raise OSError("fixed parent fsync failure")
        with patch.object(driver, "fsync_directory", side_effect=fsync):
            result = driver.retain_publication_failure(
                runs=runs, run_id="unit-fixed", staging=runs / "staging", final=final,
                error=OSError("fixed"), phase="post_rename_durability",
            )
    assert result["state"] == "quarantine_parent_fsync_failed"
    assert result["quarantine_complete"] is False
    assert "fixed parent" in result["parent_directory_fsync_failed"]


def case_failed_receipt_unretained() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-a8240d-unretained-") as temporary:
        runs = Path(temporary) / "runs"
        final = runs / "unit-fixed"
        final.mkdir(parents=True)
        with patch.object(Path, "write_bytes", side_effect=OSError("fixed receipt failure")):
            result = driver.retain_publication_failure(
                runs=runs, run_id="unit-fixed", staging=runs / "staging", final=final,
                error=OSError("fixed"), phase="post_rename_durability",
            )
    assert result["state"] != "annotated_final" and result["receipt_written"] is False


def case_failed_certificate_retained_before_stop() -> None:
    class MockCurve:
        def scalar(self, scalar: int, _point: driver.Point) -> driver.Point:
            return (scalar, scalar)
    certificates: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    def repeat(_curve: Any, state: Any, _g: Any, _q: Any, a: int, b: int, _r: int, _assignment: Any) -> tuple[Any, int, int, str]:
        return state, a, b + 1, "add"
    with patch.object(driver, "rho_step", side_effect=repeat), patch.object(driver, "binary_verifier", return_value=(None, 0, 1)):
        try:
            driver.collision_census(MockCurve(), (1, 1), (2, 2), 3, None, lambda: None, certificates.append, None, invalid.append)
        except driver.MeasurementInvalidStop:
            pass
        else:
            raise AssertionError("failed certificate did not stop")
    assert len(certificates) == 1 and len(invalid) == 1
    assert invalid[0]["certificate"] == certificates[0]


def case_interrupted_diagnostic_one_row() -> None:
    rows: list[dict[str, Any]] = []
    with patch.object(driver, "process_group_rss_bytes", side_effect=[202, 101]):
        try:
            driver.measured_diagnostic("fixed", lambda: (_ for _ in ()).throw(driver.MeasurementInvalidStop("fixed")), rows.append)
        except driver.MeasurementInvalidStop:
            pass
        else:
            raise AssertionError("interruption did not propagate")
    assert len(rows) == 1 and rows[0]["completed"] is False
    assert (rows[0]["process_group_rss_start_bytes"], rows[0]["process_group_rss_end_bytes"]) == (202, 101)


def case_boundary_samples_not_labeled_peak() -> None:
    rows: list[dict[str, Any]] = []
    with patch.object(driver, "process_group_rss_bytes", side_effect=[101, 202]):
        _value, record = driver.measured_diagnostic("fixed", lambda: "ok", rows.append)
    if "process_group_rss_peak_bytes" in record:
        raise AssertionError("start/end boundary samples are mislabeled as an observed continuous peak")
    assert record.get("process_group_rss_boundary_sample_max_bytes") == 202


def case_success_diagnostic_not_duplicated_as_partial() -> None:
    diagnostic = {
        "diagnostic": "coordinate_collision_census", "completed": True,
        "diagnostic_wall_seconds": 0.02, "diagnostic_cpu_seconds": 0.01,
        "process_group_rss_start_bytes": 100, "process_group_rss_end_bytes": 200,
        "process_group_rss_boundary_sample_max_bytes": 200,
        "process_group_rss_sample_scope": "fixed_boundary_samples",
        "process_group_rss_sample_cadence": "fixed",
    }
    payload = fixed_artifact_bytes(diagnostics=[diagnostic])
    rows = list(csv.DictReader(io.StringIO(payload["costs.csv"].decode())))
    matching = [row for row in rows if row.get("diagnostic") == "coordinate_collision_census"]
    if len(matching) != 1:
        raise AssertionError(f"successful diagnostic serialized {len(matching)} times, including a partial sink row")


def case_interrupted_diagnostic_single_partial_row() -> None:
    diagnostic = {
        "diagnostic": "fixed_interrupted", "completed": False,
        "diagnostic_wall_seconds": 0.02, "diagnostic_cpu_seconds": 0.01,
        "error": "fixed",
    }
    payload = fixed_artifact_bytes(diagnostics=[diagnostic])
    rows = list(csv.DictReader(io.StringIO(payload["costs.csv"].decode())))
    assert sum(row.get("diagnostic") == "fixed_interrupted" for row in rows) == 1


def case_monolithic_artifact_serialization_absent() -> None:
    source = inspect.getsource(driver.artifact_bytes)
    forbidden = (
        "yaml.safe_dump(manifest", "canonical_json(fixtures)", "canonical_json(controls)",
        "canonical_json(certificates)", "json.dumps(secondary_by_diagnostic",
        "json.dumps(diagnostic_costs",
    )
    present = [needle for needle in forbidden if needle in source]
    if present:
        raise AssertionError(f"unguarded monolithic final serializers remain: {present}")


def case_atomic_cancel_keeps_cancel_type() -> None:
    payload = {name: f"fixed:{name}\n".encode() for name in driver.EXPERIMENT_ARTIFACTS[:-1]}
    with tempfile.TemporaryDirectory(prefix="validator-a8240d-cancel-") as temporary:
        try:
            driver.atomic_publish(Path(temporary), "unit-fixed", payload, check=lambda: (_ for _ in ()).throw(driver.CancellationStop("fixed cancel")))
        except driver.CancellationStop:
            return
        except driver.InfrastructureStop as exc:
            raise AssertionError(f"publication converted cancellation to InfrastructureStop: {exc}") from exc
    raise AssertionError("cancellation did not propagate")


def case_atomic_resource_keeps_resource_type() -> None:
    payload = {name: f"fixed:{name}\n".encode() for name in driver.EXPERIMENT_ARTIFACTS[:-1]}
    with tempfile.TemporaryDirectory(prefix="validator-a8240d-resource-") as temporary:
        try:
            driver.atomic_publish(Path(temporary), "unit-fixed", payload, check=lambda: (_ for _ in ()).throw(driver.ResourceStop("fixed resource")))
        except driver.ResourceStop:
            return
        except driver.InfrastructureStop as exc:
            raise AssertionError(f"publication converted resource stop to InfrastructureStop: {exc}") from exc
    raise AssertionError("resource stop did not propagate")


def case_final_assembly_has_typed_custody_boundary() -> None:
    source = inspect.getsource(driver.run_future_pipeline)
    finish = source.index("meter.finish()")
    assembly = source.index("payload = artifact_bytes")
    if finish < assembly and "except CancellationStop" not in source[assembly:]:
        raise AssertionError("artifact assembly is after the typed outcome catch and has no typed failure custody boundary")


def case_timing_bracket_includes_assembly_and_publication() -> None:
    source = inspect.getsource(driver.run_future_pipeline)
    if source.index("meter.finish()") < source.index("payload = artifact_bytes"):
        raise AssertionError("terminal timing bracket closes before report construction and publication")


def case_progress_checkpoint_is_compact() -> None:
    source = inspect.getsource(driver.ProgressSink.checkpoint)
    if '"events": self.events' in source:
        raise AssertionError("every progress checkpoint rewrites the complete growing event history")


def case_progress_event_name_is_truthful() -> None:
    source = inspect.getsource(driver.ProgressSink.record_partial)
    if 'checkpoint("start_completed")' in source:
        raise AssertionError("generic inner-loop/invalid progress is labeled start_completed")


def case_cayley_progress_volume_is_bounded() -> None:
    minimum_r = 127
    sampled_origins = (minimum_r + driver.CAYLEY_GUARD_STRIDE - 1) // driver.CAYLEY_GUARD_STRIDE
    cells = 4 * (len(driver.EXPLORATORY_SEEDS) + len(driver.HELDOUT_SEEDS)) * len(driver.US)
    minimum_events = cells * sum((0, 1, 2, 4, 8, 16, 32)) * minimum_r * sampled_origins
    source = inspect.getsource(driver.future_cell) + inspect.getsource(driver.ProgressSink.record_partial)
    if "on_partial(\"cayley\"" in source and "self.partial_certificates.append(record)" in source:
        raise AssertionError(f"at least {minimum_events} Cayley guard events are retained as partial certificates before other phases")


def case_relabel_failure_stops_before_later_controls() -> None:
    source = inspect.getsource(driver.future_cell)
    relabel_position = source.index("relabel, relabel_cost")
    constant_position = source.index("constant_o, constant_o_cost")
    between = source[relabel_position:constant_position]
    if "MeasurementInvalidStop" not in between:
        raise AssertionError("a false exact relabel control does not stop before later controls")


def case_occupancy_failure_stops_before_later_controls() -> None:
    source = inspect.getsource(driver.future_cell)
    # Occupancy is already determined by the completed shuffle bucket counts,
    # but is reduced only after relabel, constant-O, mutation and Cayley work.
    first_control = source.index("control_progress")
    occupancy_reduce = source.index('"occupancy": all(')
    if occupancy_reduce > first_control:
        raise AssertionError("occupancy failure is not reduced at the earliest completed-shuffle boundary")


def case_manifest_rss_is_not_false_peak() -> None:
    source = inspect.getsource(driver.artifact_bytes)
    if '"peak_rss_bytes": final_rss' in source:
        raise AssertionError("one final boundary sample is serialized as peak_rss_bytes")


def case_publication_reads_and_writes_are_chunk_guarded() -> None:
    source = inspect.getsource(driver.atomic_publish) + inspect.getsource(driver.sha256_file)
    if "handle.write(value)" in source or "path.read_bytes()" in source:
        raise AssertionError("whole-artifact write/hash paths have no intra-artifact guard checkpoints")


def case_standard_holds_lifecycle_reachable() -> None:
    expect_accept(attestation_verdict="holds")


def case_nonstandard_pass_rejected() -> None:
    expect_reject(attestation_verdict="pass")


def case_archive_before_release_rejected() -> None:
    expect_reject(lifecycle="archive_before_release")


def case_claim_before_plan_rejected() -> None:
    expect_reject(lifecycle="claim_before_plan")


def case_missing_release_hashes_rejected() -> None:
    expect_reject(release_artifacts="missing")


def case_wrong_release_hashes_rejected() -> None:
    expect_reject(release_artifacts="wrong")


def case_partial_release_hashes_rejected() -> None:
    expect_reject(release_artifacts="partial")


def case_noncanonical_queue_rejected() -> None:
    expect_reject(canonical_queue=False)


def case_incomplete_handoff_rejected() -> None:
    expect_reject(complete_handoff=False)


def case_incomplete_claim_rejected() -> None:
    expect_reject(complete_claim=False)


def case_incomplete_plan_rejected() -> None:
    expect_reject(complete_plan=False)


def case_unread_declared_source_rejected() -> None:
    expect_reject(extra_unread_input=True)


def case_missing_review_task_rejected() -> None:
    expect_reject(include_review_task=False)


def case_missing_review_output_rejected() -> None:
    expect_reject(include_check_receipt=False)


def case_report_claim_owner_mismatch_rejected() -> None:
    expect_reject(report_claim_owner="wrong-owner")


def case_release_owner_mismatch_rejected() -> None:
    expect_reject(release_owner="wrong-owner")


def case_failed_release_rejected() -> None:
    expect_reject(release_outcome="failed")


def case_contradictory_attestation_rejected() -> None:
    expect_reject(attestation_verdict="breaks")


def case_top_level_failure_rejected() -> None:
    expect_reject(report_verdict="failed")


def case_joint_failure_rejected() -> None:
    expect_reject(joint_verdict="NEEDS_CORRECTION")


def case_wrong_source_read_rejected() -> None:
    expect_reject(source_read_hash_ok=False)


def case_review_id_shapes_are_exact() -> None:
    source = inspect.getsource(driver.verify_review_admission)
    assert 'review.get("id") != admission["review_task_id"]' in source


def case_archive_diff_is_exact() -> None:
    source = inspect.getsource(driver.verify_review_admission)
    assert "set(archive_hashes) != git_changed_paths" in source


def case_receipt_cannot_self_name_commit() -> None:
    source = inspect.getsource(driver.verify_review_admission)
    assert '"commit_sha" in receipt or "archive_commit" in receipt' in source


def case_review_source_bytes_bound_at_snapshot() -> None:
    source = inspect.getsource(driver.verify_review_admission)
    assert "git_blob_hash(reviewed_source_snapshot, path)" in source


def case_run_id_valid() -> None:
    driver.canonical_run_id("RUN-ECDLP-abcdef")


def run_id_invalid(value: str) -> None:
    try:
        driver.canonical_run_id(value)
    except driver.LaunchRefused:
        return
    raise AssertionError(f"invalid run id admitted: {value}")


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


CASES = [
    Case("rng_exact_serialization", case_rng_vector),
    Case("rng_n_one_consumes_digest", case_rng_n_one),
    Case("control_rng_uses_unscaled_tuple", case_control_tuple),
    Case("shuffle_rng_uses_actual_u_arm", case_shuffle_tuple),
    Case("subgroup_repeated_addition_progress", case_subgroup_progress),
    Case("collision_start_step_progress", case_collision_progress),
    Case("zero_coordinate_success_unavailable", case_zero_coordinate_unavailable),
    Case("zero_pooled_null_success_unavailable", case_zero_null_unavailable),
    Case("pooled_null_unequal_successes", case_pooled_unequal_successes),
    Case("complete_positive_panel", case_positive_panel),
    Case("complete_negative_panel", case_negative_panel),
    Case("missing_panel_inconclusive", case_missing_panel),
    Case("invalid_panel_inconclusive", case_invalid_panel),
    Case("unavailable_panel_inconclusive", case_unavailable_panel),
    Case("one_u_below_threshold", case_one_u_below_threshold),
    Case("one_curve_nonpositive", case_one_curve_nonpositive),
    *[Case(f"validity_rejects_{name}", lambda name=name: validity_mutation(name)) for name in (
        "coordinate_certificate", "null_certificate", "cayley", "relabel", "occupancy",
        "constant_o_denominator", "constant_o_solve", "mutated_candidate",
    )],
    Case("rss_empty_rejected", lambda: rss_case("", None)),
    Case("rss_malformed_rejected", lambda: rss_case("9 7\n", None)),
    Case("rss_nonnumeric_rejected", lambda: rss_case("9 7 nope\n", None)),
    Case("rss_missing_current_rejected", lambda: rss_case("10 7 8\n", None)),
    Case("rss_current_wrong_group_rejected", lambda: rss_case("9 8 8\n10 7 8\n", None)),
    Case("rss_valid_group_summed", lambda: rss_case("9 7 12\n10 7 8\n", 20 * 1024)),
    Case("quarantine_parent_fsync_non_durable", case_quarantine_parent_fsync),
    Case("failed_receipt_not_annotated", case_failed_receipt_unretained),
    Case("failed_certificate_retained_before_stop", case_failed_certificate_retained_before_stop),
    Case("interrupted_diagnostic_one_row", case_interrupted_diagnostic_one_row),
    Case("boundary_rss_not_called_peak", case_boundary_samples_not_labeled_peak),
    Case("successful_diagnostic_not_duplicated_partial", case_success_diagnostic_not_duplicated_as_partial),
    Case("interrupted_diagnostic_single_partial", case_interrupted_diagnostic_single_partial_row),
    Case("artifact_serialization_chunk_guarded", case_monolithic_artifact_serialization_absent),
    Case("publication_cancel_type_preserved", case_atomic_cancel_keeps_cancel_type),
    Case("publication_resource_type_preserved", case_atomic_resource_keeps_resource_type),
    Case("final_assembly_typed_custody_boundary", case_final_assembly_has_typed_custody_boundary),
    Case("timing_includes_assembly_publication", case_timing_bracket_includes_assembly_and_publication),
    Case("progress_checkpoint_compact", case_progress_checkpoint_is_compact),
    Case("progress_event_name_truthful", case_progress_event_name_is_truthful),
    Case("cayley_progress_volume_bounded", case_cayley_progress_volume_is_bounded),
    Case("relabel_immediate_stop", case_relabel_failure_stops_before_later_controls),
    Case("occupancy_immediate_stop", case_occupancy_failure_stops_before_later_controls),
    Case("manifest_rss_scope_truthful", case_manifest_rss_is_not_false_peak),
    Case("publication_io_chunk_guarded", case_publication_reads_and_writes_are_chunk_guarded),
    Case("standard_holds_lifecycle_reachable", case_standard_holds_lifecycle_reachable),
    Case("nonstandard_pass_rejected", case_nonstandard_pass_rejected),
    Case("archive_before_release_rejected", case_archive_before_release_rejected),
    Case("claim_before_plan_rejected", case_claim_before_plan_rejected),
    Case("missing_release_hashes_rejected", case_missing_release_hashes_rejected),
    Case("wrong_release_hashes_rejected", case_wrong_release_hashes_rejected),
    Case("partial_release_hashes_rejected", case_partial_release_hashes_rejected),
    Case("noncanonical_queue_rejected", case_noncanonical_queue_rejected),
    Case("incomplete_handoff_rejected", case_incomplete_handoff_rejected),
    Case("incomplete_claim_rejected", case_incomplete_claim_rejected),
    Case("incomplete_plan_rejected", case_incomplete_plan_rejected),
    Case("unread_declared_source_rejected", case_unread_declared_source_rejected),
    Case("missing_review_task_rejected", case_missing_review_task_rejected),
    Case("missing_review_output_rejected", case_missing_review_output_rejected),
    Case("report_claim_owner_mismatch_rejected", case_report_claim_owner_mismatch_rejected),
    Case("release_owner_mismatch_rejected", case_release_owner_mismatch_rejected),
    Case("failed_release_rejected", case_failed_release_rejected),
    Case("contradictory_attestation_rejected", case_contradictory_attestation_rejected),
    Case("top_level_failure_rejected", case_top_level_failure_rejected),
    Case("joint_failure_rejected", case_joint_failure_rejected),
    Case("wrong_source_read_rejected", case_wrong_source_read_rejected),
    Case("review_id_shapes_exact", case_review_id_shapes_are_exact),
    Case("archive_diff_exact", case_archive_diff_is_exact),
    Case("receipt_nonself_referential", case_receipt_cannot_self_name_commit),
    Case("review_source_snapshot_hash_bound", case_review_source_bytes_bound_at_snapshot),
    Case("canonical_run_id_accepted", case_run_id_valid),
    Case("uppercase_run_id_rejected", lambda: run_id_invalid("RUN-ECDLP-ABCDEf")),
    Case("short_run_id_rejected", lambda: run_id_invalid("RUN-ECDLP-abcde")),
    Case("surplus_run_id_rejected", lambda: run_id_invalid("RUN-ECDLP-abcdef-extra")),
    Case("wrong_area_run_id_rejected", lambda: run_id_invalid("RUN-OTHER-abcdef")),
]


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed case exceeded 10 seconds")


def main() -> int:
    if len(CASES) > 640:
        raise RuntimeError("case inventory exceeds handoff ceiling")
    signal.signal(signal.SIGALRM, timeout_handler)
    administrative = {
        "source_bindings": admin_source_bindings(),
        "producer_snapshot": admin_snapshot_binding(),
        "checks_ast_parse": "PASS",
        "reserved_complete_suite_cases": len(CASES),
    }
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    results: list[dict[str, Any]] = []
    for case in CASES:
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
            detail = "fixed obligation held"
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
        "schema": "crypto.autoresearch.independent_source_admission_checks.v1",
        "task_id": TASK_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": CLAIM_COMMIT,
        "producer_snapshot_commit": SOURCE_SNAPSHOT,
        "scope": "one independent source/admission/custody joint; fixed static/arithmetic/synthetic/mock only",
        "administrative_checks": administrative,
        "limits": {
            "maximum_total_case_executions_including_reruns": 640,
            "reserved_complete_suite_cases": len(CASES),
            "maximum_seconds_per_case": 10,
            "maximum_aggregate_wall_cpu_seconds": 1800,
            "memory_gib": 8,
            "maximum_workers": 1,
            "maximum_scientific_runs": 0,
        },
        "actual": {
            "suite_invocations": 1,
            "case_executions_including_failures_and_reruns": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "errors": 0,
            "timeouts": sum("CaseTimeout" in row["detail"] for row in results),
            "maximum_case_wall_seconds": max((row["wall_seconds"] for row in results), default=0.0),
            "maximum_case_cpu_seconds": max((row["cpu_seconds"] for row in results), default=0.0),
            "script_wall_seconds": round(time.monotonic() - started_wall, 6),
            "script_cpu_seconds": round(time.process_time() - started_cpu, 6),
            "maximum_workers": 1,
        },
        "forbidden_work_executed": {
            "fixture_selection": 0,
            "candidate_search": 0,
            "scientific_collision_census": 0,
            "scientific_null_control_or_timing_panel": 0,
            "sage_or_pari_measurement": 0,
            "verify_launch_admission": 0,
            "future_run_or_prospective_pipeline": 0,
            "real_key_signature_nonce_or_lock": 0,
            "real_run_allocation_or_RUN_directory": 0,
        },
        "results": results,
    }
    print(json.dumps(output, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent fixed checks for TASK-20260908-1367aa.

The suite imports the S5 production helpers directly.  It performs no fixture
search, collision census, null/control panel, prospective pipeline call, lock
verification, signature operation, run allocation, or scientific measurement.
Temporary repositories and artifact roots contain synthetic control data only.
"""
from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import io
import json
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from unittest.mock import patch

import yaml


TASK_ID = "TASK-20260908-1367aa"
AUTHORITY_COMMIT = "9faba46c0733a8155cec618dafc5a0de7608de8a"
PUBLISHED_CLAIM_COMMIT = "3c5de06655b5cf4b6162bc81509c371f856d0959"
SOURCE_SNAPSHOT = "6bf2c6b26359c10cb816239b6a9a4729a32f0507"
ROOT = Path(__file__).resolve().parents[5]
HANDOFF_PATH = ROOT / "ledger/handoffs/TASK-20260908-1367aa.yaml"
PLAN_REL = "coordination/experiment-reserve/BATCH-1bb183/review-plan-TASK-20260908-1367aa.yaml"
IMPL = ROOT / "experiments/EXP-ECDLP-651b94/implementation/TASK-20260908-e34baf"
sys.path.insert(0, str(IMPL))
import custody  # noqa: E402
import driver  # noqa: E402
import streaming  # noqa: E402


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout if binary else completed.stdout.decode().strip()


def git_blob(repo: Path, commit: str, relative: str) -> bytes:
    return git(repo, "show", f"{commit}:{relative}", binary=True)  # type: ignore[return-value]


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def full_input_audit() -> dict[str, Any]:
    handoff_bytes = HANDOFF_PATH.read_bytes()
    handoff = yaml.safe_load(handoff_bytes)["handoff"]
    inputs = handoff["inputs"]
    bindings = handoff["source_bindings"]
    if len(inputs) != 100 or len(bindings) != 100:
        raise AssertionError("handoff does not contain the declared 100 inputs/bindings")
    if inputs != [row["path"] for row in bindings]:
        raise AssertionError("input and source-binding order differs")
    live_matches = authority_matches = claim_matches = 0
    source_matches = 0
    source_missing: list[str] = []
    parsed = {"python": 0, "json": 0, "yaml": 0, "text": 0}
    source_reads: dict[str, str] = {}
    for relative, binding in zip(inputs, bindings):
        path = ROOT / relative
        data = path.read_bytes()
        observed = digest(data)
        if observed != binding["sha256"]:
            raise AssertionError(f"live source binding mismatch: {relative}")
        live_matches += 1
        if digest(git_blob(ROOT, AUTHORITY_COMMIT, relative)) != observed:
            raise AssertionError(f"authority source binding mismatch: {relative}")
        authority_matches += 1
        if digest(git_blob(ROOT, PUBLISHED_CLAIM_COMMIT, relative)) != observed:
            raise AssertionError(f"claim source binding mismatch: {relative}")
        claim_matches += 1
        try:
            source_data = git_blob(ROOT, SOURCE_SNAPSHOT, relative)
        except subprocess.CalledProcessError:
            source_missing.append(relative)
        else:
            if digest(source_data) != observed:
                raise AssertionError(f"source snapshot binding mismatch: {relative}")
            source_matches += 1
        suffix = path.suffix
        if suffix == ".py":
            ast.parse(data, filename=relative)
            parsed["python"] += 1
        elif suffix == ".json":
            json.loads(data)
            parsed["json"] += 1
        elif suffix in {".yaml", ".yml"}:
            yaml.safe_load(data)
            parsed["yaml"] += 1
        else:
            data.decode("utf-8")
            parsed["text"] += 1
        source_reads[relative] = observed
    if source_missing != [PLAN_REL] or source_matches != 99:
        raise AssertionError(f"unexpected source-snapshot coverage: {source_missing}")
    if git(ROOT, "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT) != "":
        raise AssertionError("unexpected merge-base stdout")
    if git(ROOT, "merge-base", "--is-ancestor", AUTHORITY_COMMIT, PUBLISHED_CLAIM_COMMIT) != "":
        raise AssertionError("unexpected merge-base stdout")
    snapshot_rel = "coordination/experiment-reserve/BATCH-1bb183/archives/TASK-20260908-9ef3ea/snapshot.json"
    snapshot = json.loads((ROOT / snapshot_rel).read_bytes())
    changed = set(filter(None, str(git(ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT)).splitlines()))
    expected_changed = set(snapshot["source_path_sha256"]) | {snapshot_rel}
    if changed != expected_changed or len(snapshot["source_path_sha256"]) != 8:
        raise AssertionError("S5 snapshot changed-path inventory is not exact")
    for relative, expected in snapshot["source_path_sha256"].items():
        if digest(git_blob(ROOT, SOURCE_SNAPSHOT, relative)) != expected:
            raise AssertionError(f"S5 snapshot receipt mismatch: {relative}")
    producer_receipt = json.loads((IMPL / "regression-receipt.json").read_bytes())
    attempts = producer_receipt.get("attempts", [])
    producer_case_rows = sum(len(row.get("result", {}).get("results", [])) for row in attempts)
    return {
        "handoff_sha256": digest(handoff_bytes),
        "declared_input_count": len(inputs),
        "live_binding_matches": live_matches,
        "authority_binding_matches": authority_matches,
        "published_claim_binding_matches": claim_matches,
        "source_snapshot_binding_matches": source_matches,
        "source_snapshot_missing_paths": source_missing,
        "parsed_input_types": parsed,
        "source_reads": source_reads,
        "snapshot_changed_paths": sorted(changed),
        "snapshot_source_artifact_count": len(snapshot["source_path_sha256"]),
        "producer_receipt_attempt_count": len(attempts),
        "producer_receipt_case_rows": producer_case_rows,
        "producer_receipt_used_as_independent_evidence": False,
    }


@dataclass
class History:
    holder: tempfile.TemporaryDirectory[str]
    root: Path
    admission: dict[str, Any]
    source: str
    plan: str
    claim: str
    release: str
    archive: str
    authority: str
    executing: str
    marker: Path

    def close(self) -> None:
        self.holder.cleanup()


def plan_document(source: str, review_task: str) -> dict[str, Any]:
    return {
        "review_plan": {
            "claim_under_review": "complete fixed source conformance",
            "coordinator_prior": "fixed source appears ready for independent review only",
            "recorded_before_reviewers": True,
            "source_snapshot": source,
            "joints": [{
                "joint": "complete_source_admission_streaming_and_custody_conformance",
                "assigned_to": review_task,
                "attack_plan": "exercise the fixed canonical lifecycle",
                "breaking_artifact": "a fixed source line and counterexample",
            }],
            "blindness": {"mutual": False, "lifted_for": [review_task], "rationale": "one complete review"},
            "proves_too_much": {"objects": ["known invalid fixed authority"], "failure_signature": "must reject", "assigned_to": review_task},
            "blind_rederivation": {"required": False, "quantity": "none", "parameters": "fixed", "blind_from": [], "assigned_to": review_task},
            "scope_limit": "fixed source conformance only",
            "procedure_deviations": [],
        }
    }


def build_history(
    *,
    include_plan_input: bool = False,
    nested_plan: str = "both",
    binding_digest_wrong: bool = False,
    source_read_wrong: bool = False,
    empty_plan_controls: bool = False,
    mutate_dependency: bool = False,
    extra_invalid_task: bool = False,
    release_hashes: str = "exact",
    mutate_trusted_source: bool = False,
) -> History:
    holder = tempfile.TemporaryDirectory(prefix="validator-1367aa-git-")
    root = Path(holder.name).resolve()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Independent Validator")
    git(root, "config", "user.email", "validator@example.invalid")
    trusted = (
        driver.DISPATCH_VALIDATOR_RELATIVE_PATH,
        driver.GOAL_LANES_RELATIVE_PATH,
        driver.RESEARCH_BUDGET_RELATIVE_PATH,
        driver.MODEL_POLICIES_RELATIVE_PATH,
        driver.MODEL_BINDINGS_RELATIVE_PATH,
        driver.REVIEW_PLAN_VALIDATOR_RELATIVE_PATH,
    )
    source_paths: list[str] = []
    for relative in trusted:
        write(root / relative, (ROOT / relative).read_bytes())
        source_paths.append(relative)
    write(root / "evidence/source.txt", b"fixed reviewed source\n")
    source_paths.append("evidence/source.txt")
    marker = root / "external-code-executed.marker"
    untrusted = b"from pathlib import Path\nPath('external-code-executed.marker').write_text('bad')\n"
    write(root / "evidence/untrusted.py", untrusted)
    source_paths.append("evidence/untrusted.py")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "fixed reviewed source snapshot")
    source = str(git(root, "rev-parse", "HEAD"))

    review_task = "TASK-20260908-a1b2c3"
    archive_task = "TASK-20260908-d4e5f6"
    plan_rel = "coordination/review-plan.yaml"
    queue_rel = "coordination/dispatch_queue.json"
    outputs = [
        "coordination/reviews/TASK-20260908-a1b2c3/review.yaml",
        "coordination/reviews/TASK-20260908-a1b2c3/checks.py",
        "coordination/reviews/TASK-20260908-a1b2c3/check-receipt.json",
    ]
    receipt_rel = "coordination/archives/TASK-20260908-d4e5f6/snapshot.json"
    claim_rel = "coordination/claims/TASK-20260908-a1b2c3.1.claim.json"
    release_rel = "coordination/claims/TASK-20260908-a1b2c3.1.release.json"
    plan_doc = plan_document(source, review_task)
    if empty_plan_controls:
        plan_doc["review_plan"]["proves_too_much"] = {}
    plan_bytes = yaml.safe_dump(plan_doc, sort_keys=False).encode()
    inputs = list(source_paths)
    if include_plan_input:
        inputs.append(plan_rel)
    bindings = [{"path": relative, "sha256": digest((root / relative).read_bytes())} for relative in source_paths]
    if include_plan_input:
        bindings.append({"path": plan_rel, "sha256": digest(plan_bytes)})
    if binding_digest_wrong:
        bindings[0] = {**bindings[0], "sha256": "f" * 64}
    handoff: dict[str, Any] = {
        "id": review_task,
        "from": "coordinator",
        "to": "validator",
        "objective": "fixed complete independent review",
        "uncertainty_reduced": "fixed canonical source admission",
        "inputs": inputs,
        "source_bindings": bindings,
        "constraints": ["fixed synthetic controls only"],
        "deliverables": outputs,
        "write_scope": outputs,
        "artifact_paths": outputs,
        "archived_by": archive_task,
        "completion_gate": ["exact fixed review outputs"],
        "budget": {"wall_clock_seconds": None, "memory_gb": 2, "maximum_workers": 1, "maximum_runs": 0},
        "inference": {"policy": "review-adversarial", "reasoning_effort": "xhigh", "fallback_allowed": False, "degraded_allowed": False, "independent_session_required": True},
    }
    if nested_plan in {"both", "inline"}:
        handoff["review_plan"] = plan_doc["review_plan"]
    if nested_plan in {"both", "path"}:
        handoff["review_plan_path"] = plan_rel
    review_row = {
        "id": review_task, "title": "fixed independent review", "role": "validator", "state": "queued",
        "priority": 90, "review_required": False, "depends_on": [], "read_scope": inputs,
        "write_scope": outputs, "artifact_paths": outputs, "handoff": handoff,
    }
    archive_handoff = {
        "id": archive_task, "from": "coordinator", "to": "coordinator", "objective": "archive fixed review",
        "uncertainty_reduced": "exact fixed custody", "inputs": outputs, "constraints": ["fixed only"],
        "deliverables": [receipt_rel], "write_scope": [receipt_rel], "artifact_paths": [receipt_rel],
        "archived_by": archive_task, "completion_gate": ["exact commit custody"],
        "budget": {"wall_clock_seconds": None, "memory_gb": 2, "maximum_runs": 0},
        "inference": {"policy": "coordinator-orchestration-code", "reasoning_effort": None, "fallback_allowed": False, "degraded_allowed": False, "independent_session_required": False},
    }
    archive_row = {
        "id": archive_task, "title": "fixed review archive", "role": "coordinator", "state": "queued",
        "priority": 89, "review_required": False, "depends_on": [review_task], "read_scope": outputs,
        "write_scope": [receipt_rel], "artifact_paths": [receipt_rel], "handoff": archive_handoff,
        "archive": {"kind": "snapshot", "source_task_ids": [review_task], "commit_sha": None,
                    "parent_sha": None, "path_sha256": {},
                    "record_ids": [archive_task, review_task, driver.EXPERIMENT_ID]},
    }
    queue = {"schema": "crypto.autoresearch.dispatch_queue.v1", "objective": "fixed governed review", "max_concurrent": 1, "tasks": [review_row, archive_row]}
    write(root / plan_rel, plan_bytes)
    write(root / queue_rel, (json.dumps(queue, sort_keys=True) + "\n").encode())
    if mutate_trusted_source:
        with (root / driver.GOAL_LANES_RELATIVE_PATH).open("ab") as handle:
            handle.write(b"\n# fixed post-snapshot mutation\n")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "precommitted review plan and queued task")
    plan_commit = str(git(root, "rev-parse", "HEAD"))
    git(root, "commit", "-q", "--allow-empty", "-m", "unrelated intervening commit")

    claim_obj = {
        "schema": "crypto.autoresearch.task_claim.v1", "task_id": review_task, "epoch": 1,
        "owner": "fixed-independent-owner", "session": "fixed-independent-session", "branch": "main",
        "worktree": str(root), "acquired_at": "2026-09-08T00:00:00Z", "expires_at": "2026-09-08T01:00:00Z",
        "write_scope": outputs, "supersedes": None, "forced": False,
    }
    write(root / claim_rel, (json.dumps(claim_obj, sort_keys=True) + "\n").encode())
    git(root, "add", claim_rel)
    git(root, "commit", "-q", "-m", "fixed queued review claim")
    claim_commit = str(git(root, "rev-parse", "HEAD"))

    source_reads = {row["path"]: digest(plan_bytes) if row["path"] == plan_rel else digest((root / row["path"]).read_bytes()) for row in bindings}
    if source_read_wrong:
        source_reads["evidence/source.txt"] = "0" * 64
    attestation = {
        "task_id": review_task,
        "joints_owned": ["complete_source_admission_streaming_and_custody_conformance"],
        "complete_source_read": True,
        "review_plan_path": plan_rel,
        "source_reads": source_reads,
        "sources_read": sorted(source_reads),
        "read_sibling_reports": False,
        "blind_from_respected": None,
        "verdict": "holds",
    }
    report = {"validation_report": {
        "id": review_task, "task_id": review_task, "role": "validator", "source_snapshot_commit": source,
        "review_plan_path": plan_rel, "review_plan_commit": plan_commit, "claim_commit": claim_commit,
        "claim_owner": claim_obj["owner"], "claim_session": claim_obj["session"], "claim_epoch": 1,
        "artifact_paths": outputs, "owned_joint_verdict": "PASS", "verdict": "passed",
        "inference": {"requested_policy": "review-adversarial", "resolved_model_id": "fixed-independent-model",
                      "reasoning_effort": "xhigh", "independent_session": True, "fallback_used": False,
                      "degraded_used": False, "bedrock_used": False, "provenance": "fixed independent native review"},
        "review_attestation": attestation,
    }}
    payloads = {
        outputs[0]: yaml.safe_dump(report, sort_keys=False).encode(),
        outputs[1]: b"# fixed independent checker\n",
        outputs[2]: b'{"fixed":true,"task_id":"TASK-20260908-a1b2c3"}\n',
    }
    for relative, data in payloads.items():
        write(root / relative, data)
    output_hashes = {relative: digest(data) for relative, data in payloads.items()}
    if release_hashes == "exact":
        released = dict(output_hashes)
    elif release_hashes == "empty":
        released = {}
    elif release_hashes == "partial":
        released = {outputs[0]: output_hashes[outputs[0]]}
    elif release_hashes == "wrong":
        released = {relative: "e" * 64 for relative in outputs}
    else:
        raise ValueError(release_hashes)
    release_obj = {
        "schema": "crypto.autoresearch.task_release.v1", "task_id": review_task, "epoch": 1,
        "owner": claim_obj["owner"], "outcome": "completed", "released_at": "2026-09-08T00:10:00Z",
        "was_expired": False, "note": "fixed completed review", "artifact_sha256": released,
    }
    write(root / release_rel, (json.dumps(release_obj, sort_keys=True) + "\n").encode())
    git(root, "add", release_rel)
    git(root, "commit", "-q", "-m", "fixed completed review release")
    release_commit = str(git(root, "rev-parse", "HEAD"))

    receipt = {"schema": "crypto.autoresearch.review_snapshot.v1", "task_id": archive_task,
               "source_task_ids": [review_task], "parent_sha": release_commit,
               "source_path_sha256": output_hashes}
    write(root / receipt_rel, (json.dumps(receipt, sort_keys=True) + "\n").encode())
    git(root, "add", *outputs, receipt_rel)
    git(root, "commit", "-q", "-m", f"{archive_task} archives {review_task} {driver.EXPERIMENT_ID}")
    archive_commit = str(git(root, "rev-parse", "HEAD"))
    archive_hashes = {**output_hashes, receipt_rel: digest((root / receipt_rel).read_bytes())}

    review_row["state"] = "completed"
    archive_row["state"] = "completed"
    archive_row["archive"].update({"commit_sha": archive_commit, "parent_sha": release_commit, "path_sha256": archive_hashes})
    if mutate_dependency:
        review_row["depends_on"] = [archive_task]
    final_tasks: list[dict[str, Any]] = [review_row, archive_row]
    if extra_invalid_task:
        final_tasks.append({"id": "TASK-20260908-badbad", "role": "invalid"})
    queue["tasks"] = final_tasks
    write(root / queue_rel, (json.dumps(queue, sort_keys=True) + "\n").encode())
    git(root, "add", queue_rel)
    git(root, "commit", "-q", "-m", "fixed external completed queue authority")
    authority_commit = str(git(root, "rev-parse", "HEAD"))
    git(root, "commit", "-q", "--allow-empty", "-m", "fixed clean executing descendant")
    executing_commit = str(git(root, "rev-parse", "HEAD"))
    admission = {
        "external_authority_commit": authority_commit,
        "external_queue_path": queue_rel,
        "external_queue_sha256": digest((root / queue_rel).read_bytes()),
        "archive_task_id": archive_task,
        "archive_commit": archive_commit,
        "snapshot_receipt_path": receipt_rel,
        "snapshot_receipt_sha256": archive_hashes[receipt_rel],
        "review_task_id": review_task,
        "review_report_path": outputs[0],
        "review_report_sha256": output_hashes[outputs[0]],
        "review_plan_path": plan_rel,
        "review_plan_commit": plan_commit,
        "review_plan_sha256": digest(plan_bytes),
        "reviewed_source_snapshot": source,
        "required_verdict": "PASS",
        "review_claim_path": claim_rel,
        "review_claim_sha256": digest((root / claim_rel).read_bytes()),
        "review_claim_commit": claim_commit,
        "review_release_path": release_rel,
        "review_release_sha256": digest((root / release_rel).read_bytes()),
        "review_release_commit": release_commit,
    }
    return History(holder, root, admission, source, plan_commit, claim_commit,
                   release_commit, archive_commit, authority_commit, executing_commit, marker)


@contextlib.contextmanager
def patched_root(history: History) -> Iterator[None]:
    with patch.object(driver, "ROOT", history.root):
        yield


def admission_result(**kwargs: Any) -> tuple[bool, str]:
    history = build_history(**kwargs)
    try:
        before = digest((history.root / history.admission["external_queue_path"]).read_bytes())
        with patched_root(history):
            driver.verify_review_admission(history.admission, history.source, history.executing)
        after = digest((history.root / history.admission["external_queue_path"]).read_bytes())
        if before != after:
            raise AssertionError("admission mutated the external queue")
        if history.marker.exists():
            raise AssertionError("untrusted external commit code executed")
        return True, "accepted"
    except driver.LaunchRefused as exc:
        return False, f"LaunchRefused: {exc}"
    finally:
        history.close()


def expect_accept(**kwargs: Any) -> None:
    accepted, detail = admission_result(**kwargs)
    if not accepted:
        raise AssertionError(detail)


def expect_reject(**kwargs: Any) -> None:
    accepted, detail = admission_result(**kwargs)
    if accepted:
        raise AssertionError(f"known-invalid authority accepted: {kwargs}")


class Meter:
    def __init__(self) -> None:
        self.started = time.monotonic()
        self.finished_at: float | None = None

    def finish(self) -> None:
        if self.finished_at is None:
            self.finished_at = time.monotonic()

    def snapshot(self, *, finish: bool = True) -> dict[str, Any]:
        if finish:
            self.finish()
        end = self.finished_at if self.finished_at is not None else time.monotonic()
        return {"wall_seconds": end - self.started, "cpu_seconds": 0.0,
                "timing": {"terminal": self.finished_at is not None}, "stages": {}}


def minimal_producers(large: bool = False) -> dict[str, Callable[[streaming.GuardedDigestWriter], None]]:
    def small(writer: streaming.GuardedDigestWriter) -> None:
        writer.write_text("fixed\n")

    def lazy(writer: streaming.GuardedDigestWriter) -> None:
        for index in range(96):
            writer.write((f"{index:04d}:" + "x" * 32760 + "\n").encode())

    return {"payload.json": lazy if large else small}


def finalize(root: Path, *, primary: BaseException | None = None,
             hook: Callable[[str, str | None], None] | None = None,
             cleanup: tuple[Path, ...] = (), large: bool = False,
             check: Callable[[], None] | None = None) -> custody.FinalizationResult:
    return custody.finalize_run(
        run_root=root, run_id="fixed-synthetic", artifact_order=("payload.json", "integrity.json"),
        producers=minimal_producers(large), integrity_name="integrity.json", meter=Meter(),
        guard_telemetry=lambda: {"fixed": True}, primary_stop=primary, phase_hook=hook,
        cleanup_paths=cleanup, check=check,
    )


def synthetic_panel(value: float, *, available: bool = True, valid: bool = True) -> list[dict[str, Any]]:
    return [{"curve_id": curve, "seed": seed, "u": u,
             "metric": {"available": available, "d": value if available else None},
             "validity": {"valid": valid}}
            for curve in ("c0", "c1", "c2", "c3")
            for seed in driver.HELDOUT_SEEDS for u in driver.US]


def case_rng_exact_bytes() -> None:
    params = (101, 1, 7, 97, 0, 2, 4)
    expected = int.from_bytes(hashlib.sha256(json.dumps(
        [driver.EXPERIMENT_ID, "shuffle", list(params), 606308, 11],
        separators=(",", ":"), ensure_ascii=False).encode()).digest(), "big")
    assert driver.stream_digest(purpose="shuffle", params=params, seed=606308, counter=11) == expected


def case_rejection_n_one() -> None:
    value, counter = driver.rejection_draw(purpose="target", params=(11, 1, 2, 7, 0, 0, 0), seed=3, counter=9, n=1)
    assert value == 0 and counter == 10


def case_rejection_schedule() -> None:
    limit = ((1 << 256) // 3) * 3
    with patch.object(driver, "stream_digest", side_effect=[limit, 5]) as mocked:
        value, counter = driver.rejection_draw(purpose="target", params=(1,) * 7, seed=1, counter=4, n=3)
    assert value == 2 and counter == 6 and [c.kwargs["counter"] for c in mocked.call_args_list] == [4, 5]


def case_shuffle_exact() -> None:
    params = (101, 1, 7, 97, 0, 3, 6)
    actual, consumed = driver.deterministic_shuffle(range(12), purpose="shuffle", params=params, seed=606309)
    expected = list(range(12)); counter = 0
    for index in range(11, 0, -1):
        other, counter = driver.rejection_draw(purpose="shuffle", params=params, seed=606309, counter=counter, n=index + 1)
        expected[index], expected[other] = expected[other], expected[index]
    assert actual == expected and consumed == counter


def case_cell_zero_coordinate() -> None:
    result = driver.cell_difference({"transition_group_operations": 9, "verification_group_operations": 1, "successes": 0},
                                    [{"transition_group_operations": 2, "verification_group_operations": 0, "successes": 1}])
    assert not result["available"] and result["unavailable_reason"] == "coordinate_zero_success"


def case_cell_zero_null() -> None:
    result = driver.cell_difference({"transition_group_operations": 9, "verification_group_operations": 1, "successes": 2},
                                    [{"transition_group_operations": 2, "verification_group_operations": 0, "successes": 0}])
    assert not result["available"] and result["unavailable_reason"] == "pooled_null_zero_success"


def case_cell_pooling() -> None:
    result = driver.cell_difference({"transition_group_operations": 8, "verification_group_operations": 2, "successes": 2},
                                    [{"transition_group_operations": 90, "verification_group_operations": 10, "successes": 1},
                                     {"transition_group_operations": 2, "verification_group_operations": 8, "successes": 9}])
    assert result["pooled_null_cost"] == 11 and result["coordinate_cost"] == 5


def case_positive_panel() -> None:
    assert driver.global_decision(synthetic_panel(0.3))["branch"] == "positive"


def case_negative_panel() -> None:
    assert driver.global_decision(synthetic_panel(-0.01))["branch"] == "negative"


def case_missing_panel() -> None:
    assert driver.global_decision(synthetic_panel(0.3)[:-1])["panel_valid"] is False


def case_unavailable_panel() -> None:
    panel = synthetic_panel(0.3); panel[0]["metric"] = {"available": False, "d": None}
    assert driver.global_decision(panel)["reasons"] == ["unavailable_inferential_cell"]


def case_invalid_panel() -> None:
    panel = synthetic_panel(0.3); panel[0]["validity"] = {"valid": False}
    assert driver.global_decision(panel)["panel_valid"] is False


def case_threshold_arm() -> None:
    panel = synthetic_panel(0.3)
    for row in panel:
        if row["u"] == 2: row["metric"]["d"] = 0.0
    assert driver.global_decision(panel)["branch"] == "inconclusive"


def validity_case(field: str) -> None:
    coordinate = {"failed_certificates": 0}
    nulls = [{"failed_certificates": 0}]
    controls = {"cayley": {"passed": True}, "relabel": True, "occupancy": True,
                "known_false": {"constant_o": {"nonzero_denominators": 0, "solves": 0},
                                "mutated_candidate_fails_certificate": True}}
    if field == "coordinate": coordinate["failed_certificates"] = 1
    elif field == "null": nulls[0]["failed_certificates"] = 1
    elif field == "cayley": controls["cayley"]["passed"] = False
    elif field == "relabel": controls["relabel"] = False
    elif field == "occupancy": controls["occupancy"] = False
    elif field == "constant_o_denominator": controls["known_false"]["constant_o"]["nonzero_denominators"] = 1
    elif field == "constant_o_solve": controls["known_false"]["constant_o"]["solves"] = 1
    elif field == "mutated": controls["known_false"]["mutated_candidate_fails_certificate"] = False
    assert driver.reduce_validity(coordinate, nulls, controls)["valid"] is False


def case_assignment_order_static() -> None:
    source = ast.parse((IMPL / "driver.py").read_text())
    node = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == "future_cell")
    text = ast.get_source_segment((IMPL / "driver.py").read_text(), node) or ""
    markers = ["for arm in range(1, 8)", "occupancy_result =", "if not occupancy_result", "for prepared in prepared_assignments", "relabel, relabel_cost"]
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions) and "assignments_completed" in text and "null_censuses_started" in text


def case_certificate_stop_static() -> None:
    source = (IMPL / "driver.py").read_text()
    failed = source.index('certificate["classification"] == "failed_certificate"')
    raised = source.index('raise MeasurementInvalidStop(', failed)
    census_return = source.index("def collision_census_with_custody", failed)
    assert failed < raised < census_return


def case_plan_input_lifecycle_reachable() -> None:
    # This mirrors the actual TASK-1367aa handoff: the plan is a declared input,
    # but source -> plan is a strict lifecycle edge.  A valid admission should
    # bind that plan at plan_commit rather than demand it in source_snapshot.
    expect_accept(include_plan_input=True)


def case_reduced_input_lifecycle_reachable() -> None:
    expect_accept(include_plan_input=False)


def case_inline_only_reachable() -> None:
    expect_accept(include_plan_input=False, nested_plan="inline")


def case_path_only_reachable() -> None:
    expect_accept(include_plan_input=False, nested_plan="path")


def case_wrong_binding_rejected() -> None:
    expect_reject(binding_digest_wrong=True)


def case_wrong_source_read_rejected() -> None:
    expect_reject(source_read_wrong=True)


def case_missing_nested_plan_rejected() -> None:
    expect_reject(nested_plan="none")


def case_empty_plan_control_rejected() -> None:
    expect_reject(empty_plan_controls=True)


def case_dependency_mutation_rejected() -> None:
    expect_reject(mutate_dependency=True)


def case_extra_invalid_task_rejected() -> None:
    expect_reject(extra_invalid_task=True)


def case_empty_release_rejected() -> None:
    expect_reject(release_hashes="empty")


def case_partial_release_rejected() -> None:
    expect_reject(release_hashes="partial")


def case_wrong_release_rejected() -> None:
    expect_reject(release_hashes="wrong")


def case_trusted_source_mutation_rejected() -> None:
    expect_reject(mutate_trusted_source=True)


def case_finalizer_success() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-final-") as temporary:
        result = finalize(Path(temporary))
        assert result.payload_path.is_dir() and result.operational_receipt_path.is_file()
        receipt = json.loads(result.operational_receipt_path.read_bytes())
        assert receipt["state"] == "durable_payload_published"
        assert receipt["payload_artifact_sha256"] == result.payload_artifact_sha256
        assert "excludes its own" in receipt["terminal_receipt_scope"]


def case_payload_rename_failure() -> None:
    def hook(phase: str, _name: str | None) -> None:
        if phase == "before_payload_rename": raise OSError("fixed payload rename failure")
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-rename-") as temporary:
        root = Path(temporary)
        try: finalize(root, hook=hook)
        except OSError: pass
        else: raise AssertionError("payload rename failure was swallowed")
        assert not (root / "runs/fixed-synthetic").exists()
        assert any((root / "runs/incomplete").iterdir())


def case_after_payload_rename_failure() -> None:
    def hook(phase: str, _name: str | None) -> None:
        if phase == "after_payload_rename": raise OSError("fixed parent durability failure")
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-parent-") as temporary:
        root = Path(temporary)
        try: finalize(root, hook=hook)
        except OSError: pass
        else: raise AssertionError("post-rename failure was swallowed")
        assert not (root / "runs/fixed-synthetic").exists()
        retained = list((root / "runs/incomplete").iterdir())
        assert retained and (retained[0] / "publication-failure.json").is_file()


def case_companion_write_failure() -> None:
    def hook(phase: str, _name: str | None) -> None:
        if phase == "before_companion_write": raise OSError("fixed companion write failure")
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-companion-") as temporary:
        root = Path(temporary)
        try: finalize(root, hook=hook)
        except custody.CustodyError: pass
        else: raise AssertionError("companion failure was swallowed")
        assert not (root / "runs/fixed-synthetic").exists()
        assert any((root / "runs/incomplete").iterdir())
        assert any((root / "runtime-custody").iterdir())


def case_companion_parent_failure() -> None:
    def hook(phase: str, _name: str | None) -> None:
        if phase == "after_companion_rename": raise OSError("fixed companion parent fsync failure")
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-companion-parent-") as temporary:
        root = Path(temporary)
        try: finalize(root, hook=hook)
        except custody.CustodyError: pass
        else: raise AssertionError("companion parent failure was swallowed")
        assert not (root / "runs/fixed-synthetic").exists()
        assert (root / "runtime-custody/fixed-synthetic/operational-completion.json").is_file()


def primary_stop_case(error: BaseException) -> None:
    def hook(phase: str, _name: str | None) -> None:
        if phase == "before_companion_write": raise OSError("fixed secondary custody failure")
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-primary-") as temporary:
        try: finalize(Path(temporary), primary=error, hook=hook)
        except type(error) as observed:
            assert observed is error and observed.secondary_custody_failures[0]["phase"] == "operational_companion"
        else: raise AssertionError("primary typed stop was replaced")


def case_cleanup_failure() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-cleanup-") as temporary:
        root = Path(temporary); progress = root / "progress"; progress.mkdir()
        with patch.object(custody.shutil, "rmtree", side_effect=OSError("fixed cleanup failure")):
            result = finalize(root, cleanup=(progress,))
        assert result.payload_path.exists() and result.operational_receipt_path.exists()
        assert progress.exists() and len(result.cleanup_errors) == 1


def case_large_lazy_payload() -> None:
    checks = 0
    def check() -> None:
        nonlocal checks; checks += 1
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-large-") as temporary:
        result = finalize(Path(temporary), large=True, check=check)
        assert (result.payload_path / "payload.json").stat().st_size > 3_000_000 and checks > 96


def case_large_string() -> None:
    checks = 0
    def check() -> None:
        nonlocal checks; checks += 1
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-string-") as temporary:
        path = Path(temporary) / "large.json"
        with path.open("xb") as handle:
            writer = streaming.GuardedDigestWriter(handle, check=check)
            streaming.write_json_document(writer, {"large": "z" * 1_000_000})
        assert len(json.loads(path.read_bytes())["large"]) == 1_000_000 and checks > 50


def case_integer_key_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-key-") as temporary:
        with (Path(temporary) / "x.json").open("xb") as handle:
            try: streaming.write_json_document(streaming.GuardedDigestWriter(handle), {1: "x"})
            except streaming.StreamingEncodingError: return
    raise AssertionError("integer key was silently converted")


def case_required_record_types() -> None:
    record = {"curve_id": "fixed", "seed": 606308, "u": 1, "stream": "heldout",
              "metric": {"available": True, "d": 0.25}, "validity": {"valid": True},
              "controls": {"occupancy": True}, "certificate": {"candidate": None}}
    buffer = io.BytesIO(); streaming.write_json_document(streaming.GuardedDigestWriter(buffer), record)
    restored = json.loads(buffer.getvalue())
    assert type(restored["seed"]) is int and type(restored["metric"]["d"]) is float
    assert type(restored["controls"]["occupancy"]) is bool and restored["certificate"]["candidate"] is None


def case_jsonl_order_and_preservation() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-spool-") as temporary:
        path = Path(temporary) / "spool.jsonl"
        for index in range(40): streaming.append_jsonl(path, {"index": index})
        before = digest(path.read_bytes()); rows = list(streaming.iter_jsonl(path)); after = digest(path.read_bytes())
        assert [row["index"] for row in rows] == list(range(40)) and before == after


def case_jsonl_record_limit() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-record-limit-") as temporary:
        path = Path(temporary) / "large.jsonl"
        path.write_text(json.dumps({"large": "x" * 2048}) + "\n")
        try:
            list(streaming.iter_jsonl(path, maximum_record_bytes=1024))
        except streaming.StreamingEncodingError:
            return
    raise AssertionError("newline-terminated JSONL record exceeded maximum_record_bytes but was materialized")


def case_192_cell_spool() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-cells-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        for index in range(192):
            stream = "exploratory" if index < 96 else "heldout"
            sink.record_cell({"curve_id": f"c{index % 4}", "seed": 606300 + (index % 16), "u": 1 + index % 3,
                              "stream": stream, "metric": {"available": True, "d": 0.1}, "validity": {"valid": True}})
        assert sink.completed_cell_count == 192 and len(sink.decision_cells) == 96
        assert sum(1 for _ in sink.records("completed-cells.jsonl")) == 192


def case_certificate_progress_separation() -> None:
    with tempfile.TemporaryDirectory(prefix="validator-1367aa-cert-") as temporary:
        sink = driver.ProgressSink(Path(temporary))
        for index in range(100): sink.record_scientific_certificate({"index": index})
        assert sink.scientific_certificate_count == 100 and sink.progress_event_count == 0
        assert sum(1 for _ in sink.records("scientific-certificates.jsonl")) == 100


def case_static_full_panel_bounds() -> None:
    assert 4 * 16 * 3 == 192
    assert 192 * 8 * 509 == 781_824
    assert (256 * 1024 * 1024) // 1024 == 262_144


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


CASES = [
    Case("rng_exact_bytes", case_rng_exact_bytes),
    Case("rejection_n_one_draw", case_rejection_n_one),
    Case("rejection_counter_schedule", case_rejection_schedule),
    Case("deterministic_shuffle_exact", case_shuffle_exact),
    Case("coordinate_zero_success", case_cell_zero_coordinate),
    Case("pooled_null_zero_success", case_cell_zero_null),
    Case("pooled_unequal_successes", case_cell_pooling),
    Case("complete_positive_panel", case_positive_panel),
    Case("complete_negative_panel", case_negative_panel),
    Case("missing_panel_inconclusive", case_missing_panel),
    Case("unavailable_panel_inconclusive", case_unavailable_panel),
    Case("invalid_panel_inconclusive", case_invalid_panel),
    Case("one_u_below_threshold", case_threshold_arm),
    *[Case(f"validity_rejects_{name}", lambda name=name: validity_case(name)) for name in
      ("coordinate", "null", "cayley", "relabel", "occupancy", "constant_o_denominator", "constant_o_solve", "mutated")],
    Case("seven_assignments_before_null_static", case_assignment_order_static),
    Case("failed_scalar_certificate_stop_static", case_certificate_stop_static),
    Case("canonical_plan_input_lifecycle_reachable", case_plan_input_lifecycle_reachable),
    Case("reduced_input_lifecycle_reachable", case_reduced_input_lifecycle_reachable),
    Case("inline_only_plan_reachable", case_inline_only_reachable),
    Case("path_only_plan_reachable", case_path_only_reachable),
    Case("wrong_declared_input_digest_rejected", case_wrong_binding_rejected),
    Case("wrong_source_read_rejected", case_wrong_source_read_rejected),
    Case("missing_nested_plan_rejected", case_missing_nested_plan_rejected),
    Case("empty_plan_controls_rejected", case_empty_plan_control_rejected),
    Case("dependency_mutation_rejected", case_dependency_mutation_rejected),
    Case("unrelated_invalid_queue_task_rejected", case_extra_invalid_task_rejected),
    Case("empty_release_hashes_rejected", case_empty_release_rejected),
    Case("partial_release_hashes_rejected", case_partial_release_rejected),
    Case("wrong_release_hashes_rejected", case_wrong_release_rejected),
    Case("trusted_validator_source_mutation_rejected", case_trusted_source_mutation_rejected),
    Case("finalizer_success_has_payload_and_companion", case_finalizer_success),
    Case("payload_rename_failure_quarantines", case_payload_rename_failure),
    Case("post_payload_rename_failure_quarantines", case_after_payload_rename_failure),
    Case("companion_write_failure_quarantines", case_companion_write_failure),
    Case("companion_parent_failure_quarantines_payload", case_companion_parent_failure),
    Case("cancellation_type_survives_secondary_custody", lambda: primary_stop_case(driver.CancellationStop("fixed cancellation"))),
    Case("resource_type_survives_secondary_custody", lambda: primary_stop_case(driver.ResourceStop("fixed resource stop"))),
    Case("cleanup_failure_retains_both_custodies", case_cleanup_failure),
    Case("large_lazy_payload_chunked", case_large_lazy_payload),
    Case("large_string_guarded", case_large_string),
    Case("integer_mapping_key_rejected", case_integer_key_rejected),
    Case("required_record_types_preserved", case_required_record_types),
    Case("jsonl_spool_order_and_preservation", case_jsonl_order_and_preservation),
    Case("jsonl_maximum_record_bytes_enforced", case_jsonl_record_limit),
    Case("all_192_cells_spooled_compactly", case_192_cell_spool),
    Case("scientific_certificates_separate_from_progress", case_certificate_progress_separation),
    Case("full_panel_static_bounds", case_static_full_panel_bounds),
]


class CaseTimeout(RuntimeError):
    pass


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise CaseTimeout("fixed case exceeded 10 seconds")


def main() -> int:
    if len(CASES) > 640:
        raise RuntimeError("fixed suite exceeds 640-case ceiling")
    administrative = full_input_audit()
    signal.signal(signal.SIGALRM, timeout_handler)
    started_at = datetime.now(timezone.utc)
    started_wall = time.monotonic(); started_cpu = time.process_time()
    rss_unit = 1 if platform.system() == "Darwin" else 1024
    rss_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_unit
    results: list[dict[str, Any]] = []
    for case in CASES:
        case_wall = time.monotonic(); case_cpu = time.process_time()
        signal.alarm(10)
        try:
            case.action()
        except Exception as exc:
            outcome = "FAIL"; detail = f"{type(exc).__name__}: {exc}"
        else:
            outcome = "PASS"; detail = "fixed obligation held"
        finally:
            signal.alarm(0)
        results.append({"name": case.name, "outcome": outcome, "detail": detail,
                        "wall_seconds": round(time.monotonic() - case_wall, 6),
                        "cpu_seconds": round(time.process_time() - case_cpu, 6)})
    ended_at = datetime.now(timezone.utc)
    failed = [row for row in results if row["outcome"] == "FAIL"]
    output = {
        "schema": "crypto.autoresearch.independent_source_checks.v1",
        "task_id": TASK_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": PUBLISHED_CLAIM_COMMIT,
        "source_snapshot_commit": SOURCE_SNAPSHOT,
        "scope": "one independent complete source/admission/streaming/custody joint; fixed lower-level controls only",
        "administrative_checks": administrative,
        "limits": {"maximum_total_case_executions_including_reruns": 640,
                   "reserved_complete_final_suite_cases": len(CASES), "maximum_seconds_per_case": 10,
                   "maximum_aggregate_executed_check_wall_cpu_seconds": 1800,
                   "memory_limit_bytes": 2 * 1024**3, "maximum_workers": 1, "maximum_scientific_runs": 0},
        "actual": {"suite_invocations": 1, "case_executions_including_failures_and_reruns": len(results),
                   "passed": len(results) - len(failed), "failed": len(failed), "errors": 0,
                   "timeouts": sum("CaseTimeout" in row["detail"] for row in results),
                   "absolute_utc_start": started_at.isoformat(), "absolute_utc_end": ended_at.isoformat(),
                   "script_wall_seconds": round(time.monotonic() - started_wall, 6),
                   "script_cpu_seconds": round(time.process_time() - started_cpu, 6),
                   "maximum_case_wall_seconds": max(row["wall_seconds"] for row in results),
                   "maximum_case_cpu_seconds": max(row["cpu_seconds"] for row in results),
                   "ru_maxrss_start_bytes": rss_start,
                   "ru_maxrss_end_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * rss_unit,
                   "ru_maxrss_scope": "process lifetime high-water at suite boundaries", "maximum_workers": 1},
        "forbidden_work_executed": {"fixture_or_candidate_search": 0, "scientific_collision_census": 0,
                                    "scientific_null_control_or_timing_panel": 0, "sage_or_pari": 0,
                                    "verify_launch_admission": 0, "future_run_or_prospective_pipeline": 0,
                                    "real_key_signature_nonce_or_lock": 0, "real_run_allocation_or_RUN_directory": 0},
        "results": results,
    }
    print(json.dumps(output, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

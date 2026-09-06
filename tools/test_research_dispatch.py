#!/usr/bin/env python3
"""Tests for the artifact-driven subagent dispatch planner."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_dispatch as dispatch


def handoff() -> dict[str, Any]:
    return {
        "objective": "Reduce one bounded uncertainty.",
        "uncertainty_reduced": "Whether the frozen task completed correctly.",
        "inputs": ["experiments/EXP-TEST-001/specification.yaml"],
        "constraints": ["Preserve raw evidence."],
        "deliverables": ["report.json"],
        "budget": {
            "wall_clock_seconds": 60,
            "memory_gb": 1,
            "maximum_runs": 1,
        },
        "completion_gate": ["A machine-checkable report exists."],
    }


def lease(
    owner: str = "executor-1",
    *,
    acquired_at: str = "2026-08-16T00:00:00+00:00",
    expires_at: str = "2026-08-16T01:00:00+00:00",
    epoch: int = 1,
) -> dict[str, Any]:
    return {
        "owner": owner,
        "acquired_at": acquired_at,
        "expires_at": expires_at,
        "epoch": epoch,
    }


def task(
    identifier: str,
    priority: int,
    *,
    state: str = "queued",
    role: str = "executor",
    review_required: bool = False,
    depends_on: list[str] | None = None,
    read_scope: list[str] | None = None,
    write_scope: list[str] | None = None,
    artifact_paths: list[str] | None = None,
    task_lease: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_scope = f"coordination/tasks/{identifier}/"
    result = {
        "id": identifier,
        "title": identifier,
        "role": role,
        "state": state,
        "priority": priority,
        "review_required": review_required,
        "depends_on": depends_on or [],
        "read_scope": read_scope or ["experiments/EXP-TEST-001/specification.yaml"],
        "write_scope": write_scope or [default_scope],
        "artifact_paths": artifact_paths or [f"coordination/tasks/{identifier}/report.json"],
        "handoff": handoff(),
    }
    if task_lease is not None:
        result["lease"] = task_lease
    return result


def archive_task(
    identifier: str,
    sources: Sequence[dict[str, Any]],
    priority: int = 1,
    *,
    kind: str = "snapshot",
    state: str = "queued",
    depends_on: list[str] | None = None,
    artifact_paths: list[str] | None = None,
    write_scope: list[str] | None = None,
    read_scope: list[str] | None = None,
    record_ids: list[str] | None = None,
) -> dict[str, Any]:
    source_paths = [path for source in sources for path in source["artifact_paths"]]
    if kind == "ledger":
        own_paths = artifact_paths or [
            f"ledger/evidence/{identifier}-EVIDENCE.json",
            f"ledger/decisions/{identifier}-DECISION.json",
        ]
        own_scope = write_scope or ["ledger/evidence/", "ledger/decisions/"]
        records = (
            [f"{identifier}-EVIDENCE", f"{identifier}-DECISION"]
            if record_ids is None
            else record_ids
        )
    else:
        own_paths = artifact_paths or [f"coordination/archives/{identifier}/snapshot.json"]
        own_scope = write_scope or [f"coordination/archives/{identifier}/"]
        records = [] if record_ids is None else record_ids
    result = task(
        identifier,
        priority,
        state=state,
        role="coordinator",
        depends_on=depends_on if depends_on is not None else [source["id"] for source in sources],
        read_scope=read_scope if read_scope is not None else source_paths,
        write_scope=own_scope,
        artifact_paths=own_paths,
    )
    result["archive"] = {
        "kind": kind,
        "source_task_ids": [source["id"] for source in sources],
        "commit_sha": None,
        "parent_sha": None,
        "path_sha256": {},
        "record_ids": records,
    }
    return result


def queue(*tasks: dict[str, Any], maximum: int = 2, goal_id: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": dispatch.SCHEMA,
        "objective": "Reduce a bounded ECDLP research uncertainty.",
        "max_concurrent": maximum,
        "tasks": list(tasks),
    }
    if goal_id is not None:
        result["goal_id"] = goal_id
    return result


def deferred_by_id(plan: dict[str, Any]) -> dict[str, list[str]]:
    return {item["id"]: item["reason"] for item in plan["deferred"]}


class FakeGitVerifier:
    """A verifier fixture that models the immutable commit receipt contract."""

    def __init__(
        self,
        *,
        changed_paths: Sequence[str],
        contents: dict[str, bytes],
        message: str,
        resolves: bool = True,
        is_head_ancestor: bool = True,
        parent_matches: bool = True,
    ) -> None:
        self.changed_paths = list(changed_paths)
        self.contents = contents
        self.message = message
        self.resolves = resolves
        self.is_head_ancestor = is_head_ancestor
        self.parent_matches = parent_matches
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def verify_archive(self, task: dict[str, Any], expected_paths: Sequence[str]) -> None:
        self.calls.append((task["id"], tuple(expected_paths)))
        if not self.resolves:
            raise dispatch.DispatchError("fake archive commit does not resolve")
        if not self.is_head_ancestor:
            raise dispatch.DispatchError("fake archive commit is not an ancestor of HEAD")
        if not self.parent_matches:
            raise dispatch.DispatchError("fake archive parent mismatch")
        expected = set(expected_paths)
        actual = set(self.changed_paths)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra:
            raise dispatch.DispatchError(f"fake commit paths missing={missing} extra={extra}")
        for path in expected:
            observed = hashlib.sha256(self.contents[path]).hexdigest()
            if observed != task["archive"]["path_sha256"][path]:
                raise dispatch.DispatchError(f"fake archive hash mismatch for {path}")
        for identifier in [task["id"], *task["archive"]["record_ids"]]:
            if identifier not in self.message:
                raise dispatch.DispatchError(f"fake archive message missing {identifier}")


def completed_archive_queue() -> tuple[dict[str, Any], dict[str, bytes], dict[str, Any]]:
    worker = task("WORK", 1, state="completed")
    archive = archive_task("ARCHIVE", [worker], state="completed", record_ids=["REC-ARCHIVE"])
    contents = {
        worker["artifact_paths"][0]: b"worker receipt\n",
        archive["artifact_paths"][0]: b"archive snapshot\n",
    }
    archive["archive"].update(
        {
            "commit_sha": "a" * 40,
            "parent_sha": "b" * 40,
            "path_sha256": {
                path: hashlib.sha256(content).hexdigest() for path, content in contents.items()
            },
        }
    )
    return queue(worker, archive), contents, archive


class DispatchPlannerTests(unittest.TestCase):
    def test_selects_highest_priority_ready_tasks_under_cap(self) -> None:
        low = task("LOW", 10)
        high = task("HIGH", 90)
        middle = task("MID", 50)
        archive = archive_task("ARCHIVE", [low, high, middle])
        plan = dispatch.select(queue(low, high, middle, archive))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["HIGH", "MID"])
        self.assertEqual(deferred_by_id(plan)["LOW"], ["concurrency_cap"])
        self.assertTrue(plan["gates"]["concurrency_cap_respected"])
        self.assertTrue(plan["gates"]["archive_artifact_coverage_complete"])

    def test_completed_dependency_unblocks_successor(self) -> None:
        parent = task("PARENT", 1, state="completed")
        child = task("CHILD", 90, depends_on=["PARENT"], role="validator")
        parent_archive = archive_task("PARENT-ARCHIVE", [parent], state="blocked")
        child_archive = archive_task("CHILD-ARCHIVE", [child])
        plan = dispatch.select(queue(parent, child, parent_archive, child_archive, maximum=1))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["CHILD"])

    def test_failed_dependency_blocks_successor(self) -> None:
        parent = task("PARENT", 1, state="failed")
        child = task("CHILD", 90, depends_on=["PARENT"], role="validator")
        parent_archive = archive_task("PARENT-ARCHIVE", [parent])
        child_archive = archive_task("CHILD-ARCHIVE", [child])
        plan = dispatch.select(queue(parent, child, parent_archive, child_archive, maximum=1))
        self.assertEqual(plan["dispatches"], [])
        self.assertEqual(
            deferred_by_id(plan)["CHILD"], ["dependency_not_completed:PARENT:failed"]
        )

    def test_failure_provenance_ledger_archive_can_preserve_failed_source(self) -> None:
        failed = task("FAILED", 10, state="failed", role="validator")
        successor = task("SUCCESSOR", 20, state="completed", role="validator")
        successor["supersedes_failed_task"] = "FAILED"
        archive = archive_task(
            "LEDGER",
            [failed, successor],
            priority=90,
            kind="ledger",
        )
        archive["dispatch_exception"] = {
            "kind": "terminal_failure_provenance_archive",
            "scientific_effect": "none",
            "failed_tasks_reclassified_completed": False,
            "successor_review_completed_independently": True,
        }
        plan = dispatch.select(queue(failed, successor, archive, maximum=1))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["LEDGER"])
        self.assertTrue(plan["gates"]["all_selected_dependencies_completed"])
        self.assertTrue(plan["gates"]["terminal_noncompleted_tasks_do_not_unblock_successors"])

    def test_failure_provenance_archive_requires_completed_independent_successor(self) -> None:
        failed = task("FAILED", 10, state="failed", role="validator")
        archive = archive_task("LEDGER", [failed], priority=90, kind="ledger")
        archive["dispatch_exception"] = {
            "kind": "terminal_failure_provenance_archive",
            "scientific_effect": "none",
            "failed_tasks_reclassified_completed": False,
            "successor_review_completed_independently": True,
        }
        with self.assertRaisesRegex(
            dispatch.DispatchError, "lacks a completed independent successor"
        ):
            dispatch.select(queue(failed, archive, maximum=1))

    def test_running_task_consumes_a_slot(self) -> None:
        running = task("RUNNING", 1, state="running")
        ready = task("READY", 90)
        archive = archive_task("ARCHIVE", [running, ready])
        plan = dispatch.select(queue(running, ready, archive, maximum=1))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["RUNNING"])
        self.assertEqual(deferred_by_id(plan)["READY"], ["concurrency_cap"])

    def test_overlapping_write_scope_defers_lower_priority_task(self) -> None:
        first = task(
            "FIRST", 90, write_scope=["experiments/EXP-TEST-001/runs/"], artifact_paths=[
                "experiments/EXP-TEST-001/runs/first.json"
            ]
        )
        second = task(
            "SECOND",
            80,
            write_scope=["experiments/EXP-TEST-001/runs/RUN-2/"],
            artifact_paths=["experiments/EXP-TEST-001/runs/RUN-2/second.json"],
        )
        archive = archive_task("ARCHIVE", [first, second])
        plan = dispatch.select(queue(first, second, archive, maximum=2))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["FIRST"])
        self.assertEqual(
            deferred_by_id(plan)["SECOND"], ["write_scope_conflict:FIRST"]
        )

    def test_rejects_unsafe_write_scope(self) -> None:
        source = queue(task("BAD", 1, write_scope=["../outside/"]))
        with self.assertRaisesRegex(dispatch.DispatchError, "safe repository-relative"):
            dispatch.validate_queue(source)

    def test_rejects_missing_or_nonexact_artifact_paths(self) -> None:
        missing = task("MISSING", 1)
        del missing["artifact_paths"]
        with self.assertRaisesRegex(dispatch.DispatchError, "artifact_paths"):
            dispatch.validate_queue(queue(missing))
        directory = task("DIRECTORY", 1, artifact_paths=["coordination/tasks/DIRECTORY/"])
        with self.assertRaisesRegex(dispatch.DispatchError, "exact safe"):
            dispatch.validate_queue(queue(directory))

    def test_rejects_artifact_outside_its_write_scope(self) -> None:
        source = task("BAD", 1, artifact_paths=["ledger/evidence/EVID-BAD.json"])
        with self.assertRaisesRegex(dispatch.DispatchError, "inside its write_scope"):
            dispatch.validate_queue(queue(source))

    def test_rejects_running_write_scope_conflict(self) -> None:
        first = task(
            "FIRST",
            1,
            state="running",
            write_scope=["coordination/live/"],
            artifact_paths=["coordination/live/first.json"],
        )
        second = task(
            "SECOND",
            1,
            state="running",
            write_scope=["coordination/live/report/"],
            artifact_paths=["coordination/live/report/second.json"],
        )
        archive = archive_task("ARCHIVE", [first, second])
        with self.assertRaisesRegex(dispatch.DispatchError, "overlapping write scopes"):
            dispatch.validate_queue(queue(first, second, archive))

    def test_rejects_unarchived_and_multiply_archived_workers(self) -> None:
        source = task("SOURCE", 1)
        with self.assertRaisesRegex(dispatch.DispatchError, "assigned exactly once"):
            dispatch.validate_queue(queue(source))
        first = archive_task("FIRST-ARCHIVE", [source])
        second = archive_task("SECOND-ARCHIVE", [source])
        with self.assertRaisesRegex(dispatch.DispatchError, "assigned to both"):
            dispatch.validate_queue(queue(source, first, second))

    def test_archive_must_be_coordinator_direct_and_cover_source_artifacts(self) -> None:
        source = task("SOURCE", 1)
        archive = archive_task("ARCHIVE", [source])
        archive["role"] = "executor"
        with self.assertRaisesRegex(dispatch.DispatchError, "coordinator role"):
            dispatch.validate_queue(queue(source, archive))

        archive = archive_task("ARCHIVE", [source], depends_on=[])
        with self.assertRaisesRegex(dispatch.DispatchError, "directly depend"):
            dispatch.validate_queue(queue(source, archive))

        archive = archive_task("ARCHIVE", [source], read_scope=["coordination/other/"])
        with self.assertRaisesRegex(dispatch.DispatchError, "read_scope must cover"):
            dispatch.validate_queue(queue(source, archive))

    def test_ledger_archive_requires_decisions_and_record_ids(self) -> None:
        # CORR-20260822-7e98b5 HD-1: a ledger archive's entire content can BE
        # the decision (REVISE/block, supersede, infra pause, protocol
        # amendment, correction) -- it does not always promote an evidence
        # record. Only the decisions path is unconditionally required.
        source = task("SOURCE", 1)
        ledger = archive_task(
            "LEDGER", [source], kind="ledger", artifact_paths=["ledger/evidence/LEDGER-EVIDENCE.json"],
            record_ids=["LEDGER-EVIDENCE"],
        )
        ledger["write_scope"] = ["ledger/evidence/"]
        with self.assertRaisesRegex(dispatch.DispatchError, "ledger/decisions"):
            dispatch.validate_queue(queue(source, ledger))

        ledger = archive_task("LEDGER", [source], kind="ledger", record_ids=[])
        with self.assertRaisesRegex(dispatch.DispatchError, "record IDs"):
            dispatch.validate_queue(queue(source, ledger))

    def test_ledger_archive_decision_only_is_allowed(self) -> None:
        # The ordinary case CORR-20260822-7e98b5 identified: a decision with
        # no evidence basis (e.g. a REVISE) owns only a decisions/ path and
        # names no EV-* record_id.
        source = task("SOURCE", 1)
        ledger = archive_task(
            "LEDGER", [source], kind="ledger",
            artifact_paths=["ledger/decisions/LEDGER-DECISION.json"],
            write_scope=["ledger/decisions/"],
            record_ids=["LEDGER-DECISION"],
        )
        dispatch.validate_queue(queue(source, ledger))  # must not raise

    def test_ledger_archive_dangling_evidence_reference_still_caught(self) -> None:
        # If record_ids names an EV-* record, the archive must actually own
        # an artifact under ledger/evidence/ for it -- the dangling-reference
        # catch HD-1's proposed fix preserves.
        source = task("SOURCE", 1)
        ledger = archive_task(
            "LEDGER", [source], kind="ledger",
            artifact_paths=["ledger/decisions/LEDGER-DECISION.json"],
            write_scope=["ledger/decisions/"],
            record_ids=["LEDGER-DECISION", "EV-DREG-DANGLING"],
        )
        with self.assertRaisesRegex(dispatch.DispatchError, "EV-\\* record_id"):
            dispatch.validate_queue(queue(source, ledger))

    def test_claim_relevant_task_requires_independent_reviewer(self) -> None:
        executor = task("EXEC", 1, review_required=True)
        snapshot = archive_task("SNAPSHOT", [executor])
        with self.assertRaisesRegex(dispatch.DispatchError, "requires an independent"):
            dispatch.validate_queue(queue(executor, snapshot))

    def test_claim_relevant_task_requires_snapshot_then_ledger_review_chain(self) -> None:
        executor = task("EXEC", 1, review_required=True)
        snapshot = archive_task("SNAPSHOT", [executor])
        validator = task("VALIDATE", 1, role="validator", depends_on=["EXEC"])
        ledger = archive_task("LEDGER", [validator], kind="ledger")
        with self.assertRaisesRegex(dispatch.DispatchError, "must depend on snapshot"):
            dispatch.validate_queue(queue(executor, snapshot, validator, ledger))

        validator["depends_on"] = ["EXEC", "SNAPSHOT"]
        wrong_archive = archive_task("VALIDATE-SNAPSHOT", [validator])
        with self.assertRaisesRegex(dispatch.DispatchError, "requires a ledger archive"):
            dispatch.validate_queue(queue(executor, snapshot, validator, wrong_archive))

    def test_claim_relevant_task_accepts_snapshot_review_and_ledger_chain(self) -> None:
        executor = task("EXEC", 1, review_required=True)
        snapshot = archive_task("SNAPSHOT", [executor])
        reviewer = task("REVIEW", 1, role="reviewer", depends_on=["EXEC", "SNAPSHOT"])
        validator = task("VALIDATE", 1, role="validator", depends_on=["EXEC", "SNAPSHOT"])
        ledger = archive_task("LEDGER", [reviewer, validator], kind="ledger")
        dispatch.validate_queue(queue(executor, snapshot, reviewer, validator, ledger))

    def test_ready_archive_runs_alone_and_has_priority_over_workers(self) -> None:
        completed = task("DONE", 1, state="completed")
        ready_archive = archive_task("READY-ARCHIVE", [completed], priority=5)
        worker = task("WORKER", 99)
        worker_archive = archive_task("WORKER-ARCHIVE", [worker])
        plan = dispatch.select(queue(completed, ready_archive, worker, worker_archive, maximum=2))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["READY-ARCHIVE"])
        self.assertEqual(
            deferred_by_id(plan)["WORKER"], ["archive_requires_isolation:READY-ARCHIVE"]
        )
        self.assertTrue(plan["gates"]["archive_tasks_run_in_isolation"])

    def test_highest_priority_ready_archive_wins_and_defers_other_archives(self) -> None:
        first = task("FIRST", 1, state="completed")
        second = task("SECOND", 1, state="completed")
        lower = archive_task("LOWER", [first], priority=10)
        higher = archive_task("HIGHER", [second], priority=90)
        plan = dispatch.select(queue(first, second, lower, higher, maximum=2))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["HIGHER"])
        self.assertEqual(deferred_by_id(plan)["LOWER"], ["archive_priority_deferred:HIGHER"])

    def test_ready_archive_drains_running_workers_before_selection(self) -> None:
        completed = task("DONE", 1, state="completed")
        ready_archive = archive_task("READY-ARCHIVE", [completed], priority=90)
        running = task("RUNNING", 1, state="running")
        running_archive = archive_task("RUNNING-ARCHIVE", [running])
        waiting = task("WAITING", 80)
        waiting_archive = archive_task("WAITING-ARCHIVE", [waiting])
        plan = dispatch.select(
            queue(completed, ready_archive, running, running_archive, waiting, waiting_archive)
        )
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["RUNNING"])
        self.assertEqual(
            deferred_by_id(plan)["READY-ARCHIVE"],
            ["archive_requires_isolation:running:RUNNING"],
        )
        self.assertEqual(
            deferred_by_id(plan)["WAITING"], ["archive_pending_isolation:READY-ARCHIVE"]
        )

    def test_rejects_archive_running_beside_another_task(self) -> None:
        completed = task("DONE", 1, state="completed")
        running_archive = archive_task("RUNNING-ARCHIVE", [completed], state="running")
        worker = task("WORKER", 1, state="running")
        worker_archive = archive_task("WORKER-ARCHIVE", [worker])
        with self.assertRaisesRegex(dispatch.DispatchError, "must run alone"):
            dispatch.validate_queue(
                queue(completed, running_archive, worker, worker_archive, maximum=2)
            )

    def test_completed_archive_requires_fake_git_verification_and_exposes_gates(self) -> None:
        source, contents, archive = completed_archive_queue()
        verifier = FakeGitVerifier(
            changed_paths=list(contents),
            contents=contents,
            message="ARCHIVE REC-ARCHIVE archival receipt",
        )
        plan = dispatch.select(source, repository_verifier=verifier)
        self.assertEqual(verifier.calls, [("ARCHIVE", tuple(sorted(contents)))])
        self.assertTrue(plan["gates"]["completed_archive_commits_verified"])
        with self.assertRaisesRegex(dispatch.DispatchError, "requires a repository verifier"):
            dispatch.validate_queue(copy.deepcopy(source))

    def test_fake_git_verifier_rejects_missing_extra_and_hash_mismatch(self) -> None:
        source, contents, _ = completed_archive_queue()
        paths = list(contents)
        with self.assertRaisesRegex(dispatch.DispatchError, "missing"):
            dispatch.validate_queue(
                copy.deepcopy(source),
                repository_verifier=FakeGitVerifier(
                    changed_paths=paths[:1], contents=contents, message="ARCHIVE REC-ARCHIVE"
                ),
            )
        with self.assertRaisesRegex(dispatch.DispatchError, "extra"):
            dispatch.validate_queue(
                copy.deepcopy(source),
                repository_verifier=FakeGitVerifier(
                    changed_paths=[*paths, "unexpected.txt"],
                    contents={**contents, "unexpected.txt": b"extra"},
                    message="ARCHIVE REC-ARCHIVE",
                ),
            )
        changed = dict(contents)
        changed[paths[0]] = b"tampered"
        with self.assertRaisesRegex(dispatch.DispatchError, "hash mismatch"):
            dispatch.validate_queue(
                copy.deepcopy(source),
                repository_verifier=FakeGitVerifier(
                    changed_paths=paths, contents=changed, message="ARCHIVE REC-ARCHIVE"
                ),
            )

    def test_actual_git_repository_verifier_accepts_exact_archive_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*arguments: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                ).stdout.strip()

            git("init")
            git("config", "user.email", "dispatch@example.test")
            git("config", "user.name", "Dispatch Test")
            (root / "README.md").write_text("base\n", encoding="utf-8")
            git("add", "README.md")
            git("commit", "-m", "base")
            parent = git("rev-parse", "HEAD")

            worker = task("WORK", 1, state="completed")
            archive = archive_task("ARCHIVE", [worker], state="completed", record_ids=["REC-ARCHIVE"])
            expected = [*worker["artifact_paths"], *archive["artifact_paths"]]
            payloads = {expected[0]: b"worker\n", expected[1]: b"archive\n"}
            for path, content in payloads.items():
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
            git("add", *expected)
            git("commit", "-m", "ARCHIVE REC-ARCHIVE exact archival receipt")
            archive["archive"].update(
                {
                    "commit_sha": git("rev-parse", "HEAD"),
                    "parent_sha": parent,
                    "path_sha256": {
                        path: hashlib.sha256(content).hexdigest()
                        for path, content in payloads.items()
                    },
                }
            )
            dispatch.validate_queue(
                queue(worker, archive), repository_verifier=dispatch.GitRepositoryVerifier(root)
            )

    def test_declared_content_first_binds_faithful_split_superset_package(self) -> None:
        """Reproduce BATCH-33b207: 17 sources across two ancestors, 55-path superset."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*arguments: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                ).stdout.strip()

            def write(path: str, content: bytes) -> None:
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)

            git("init")
            git("config", "user.email", "dispatch@example.test")
            git("config", "user.name", "Dispatch Test")
            write("README.md", b"base\n")
            git("add", "README.md")
            git("commit", "-m", "base")

            source_paths = [f"experiments/EXP-ECTD/producer/{index:02d}.bin" for index in range(17)]
            first_contents = {path: f"source-{index}\n".encode() for index, path in enumerate(source_paths[:15])}
            for path, content in first_contents.items():
                write(path, content)
            for index in range(40):
                write(f"unrelated/{index:02d}.txt", f"extra-{index}\n".encode())
            git("add", *first_contents, *[f"unrelated/{index:02d}.txt" for index in range(40)])
            git("commit", "-m", "producer package superset")
            superset_commit = git("rev-parse", "HEAD")
            self.assertEqual(55, len(git("diff-tree", "--no-commit-id", "--name-only", "-r", superset_commit).splitlines()))

            second_contents = {path: f"source-{index}\n".encode() for index, path in enumerate(source_paths[15:], 15)}
            for path, content in second_contents.items():
                write(path, content)
            git("add", *second_contents)
            git("commit", "-m", "producer package remainder")
            remainder_commit = git("rev-parse", "HEAD")

            source = task("PRODUCER", 1, state="completed", artifact_paths=source_paths,
                          write_scope=["experiments/EXP-ECTD/producer/"])
            archive = archive_task("ARCHIVE", [source], state="completed", record_ids=["REC-ARCHIVE"])
            receipt_path = archive["artifact_paths"][0]
            receipt = b"content-first archive receipt\n"
            write(receipt_path, receipt)
            git("add", receipt_path)
            git("commit", "-m", "ARCHIVE REC-ARCHIVE content-first receipt")
            receipt_commit = git("rev-parse", "HEAD")
            payloads = {**first_contents, **second_contents, receipt_path: receipt}
            archive["archive"].update(
                {
                    "binding_mode": "content_first",
                    "commit_sha": receipt_commit,
                    "parent_sha": remainder_commit,
                    "path_sha256": {
                        path: hashlib.sha256(content).hexdigest()
                        for path, content in payloads.items()
                    },
                }
            )
            self.assertEqual(0, subprocess.run(
                ["git", "-C", str(root), "merge-base", "--is-ancestor", superset_commit, "HEAD"]
            ).returncode)
            self.assertEqual(0, subprocess.run(
                ["git", "-C", str(root), "merge-base", "--is-ancestor", remainder_commit, "HEAD"]
            ).returncode)
            verifier = dispatch.GitRepositoryVerifier(root)
            plan = dispatch.select(queue(source, archive), repository_verifier=verifier)
            self.assertEqual(
                [{
                    "task_id": "ARCHIVE",
                    "reason": "declared content_first binding mode",
                    "paths_verified": 18,
                    "generated_paths_skipped": [],
                }],
                plan["content_only_archives"],
            )

    def test_content_first_rejects_mismatch_partial_hashes_and_missing_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*arguments: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(root), *arguments], check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                ).stdout.strip()

            git("init")
            git("config", "user.email", "dispatch@example.test")
            git("config", "user.name", "Dispatch Test")
            worker = task("WORK", 1, state="completed")
            archive = archive_task("ARCHIVE", [worker], state="completed", record_ids=["REC-ARCHIVE"])
            payloads = {worker["artifact_paths"][0]: b"worker\n", archive["artifact_paths"][0]: b"receipt\n"}
            for path, content in payloads.items():
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
            git("add", ".")
            git("commit", "-m", "ARCHIVE REC-ARCHIVE")
            commit = git("rev-parse", "HEAD")
            archive["archive"].update({
                "binding_mode": "content_first",
                "commit_sha": commit,
                "parent_sha": None,
                "path_sha256": {path: hashlib.sha256(content).hexdigest() for path, content in payloads.items()},
            })
            damaged = copy.deepcopy(queue(worker, archive))
            damaged["tasks"][1]["archive"]["path_sha256"][worker["artifact_paths"][0]] = "0" * 64
            with self.assertRaisesRegex(dispatch.DispatchError, "content hash mismatch"):
                dispatch.validate_queue(damaged, repository_verifier=dispatch.GitRepositoryVerifier(root))

            partial = copy.deepcopy(queue(worker, archive))
            del partial["tasks"][1]["archive"]["path_sha256"][worker["artifact_paths"][0]]
            with self.assertRaisesRegex(dispatch.DispatchError, "must cover every"):
                dispatch.validate_queue(partial, repository_verifier=dispatch.GitRepositoryVerifier(root))

            missing = copy.deepcopy(queue(worker, archive))
            missing["tasks"][1]["archive"]["commit_sha"] = "f" * 40
            with self.assertRaisesRegex(dispatch.DispatchError, "requires archive.commit_sha to resolve"):
                dispatch.validate_queue(missing, repository_verifier=dispatch.GitRepositoryVerifier(root))

            wrong_parent = copy.deepcopy(queue(worker, archive))
            wrong_parent["tasks"][1]["archive"]["parent_sha"] = commit
            with self.assertRaisesRegex(dispatch.DispatchError, "parent_sha must be null"):
                dispatch.validate_queue(wrong_parent, repository_verifier=dispatch.GitRepositoryVerifier(root))

            missing_message_id = copy.deepcopy(queue(worker, archive))
            missing_message_id["tasks"][1]["archive"]["record_ids"] = ["REC-MISSING"]
            with self.assertRaisesRegex(dispatch.DispatchError, "commit message is missing IDs"):
                dispatch.validate_queue(
                    missing_message_id, repository_verifier=dispatch.GitRepositoryVerifier(root)
                )

    def test_undeclared_content_first_shape_still_requires_exact_commit_scope(self) -> None:
        source, contents, archive = completed_archive_queue()
        archive["archive"]["commit_sha"] = "a" * 40
        verifier = FakeGitVerifier(
            changed_paths=[archive["artifact_paths"][0]],
            contents=contents,
            message="ARCHIVE REC-ARCHIVE archival receipt",
        )
        with self.assertRaisesRegex(dispatch.DispatchError, "missing"):
            dispatch.validate_queue(source, repository_verifier=verifier)

    def test_legacy_archive_validation_does_not_materialize_binding_mode(self) -> None:
        worker = task("WORK", 1)
        archive = archive_task("ARCHIVE", [worker])
        source = queue(worker, archive)
        dispatch.validate_queue(source)
        self.assertNotIn("binding_mode", archive["archive"])

    def test_goal_id_is_optional_and_echoed_into_the_plan(self) -> None:
        worker = task("WORK", 1)
        archive = archive_task("ARCHIVE", [worker])
        plan = dispatch.select(queue(worker, archive, goal_id="GOAL-DISPATCH-a1b2c3"))
        self.assertEqual(plan["goal_id"], "GOAL-DISPATCH-a1b2c3")

    def test_repository_queue_template_validates(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = json.loads(
            (root / "templates" / "subagent-task-queue.json").read_text(encoding="utf-8")
        )
        plan = dispatch.select(source)
        self.assertEqual(plan["goal_id"], "GOAL-EXAMPLE-a1b2c3")
        self.assertEqual([task["id"] for task in plan["dispatches"]], ["TASK-EXEC-001"])

    def test_plan_is_stable_for_identical_input(self) -> None:
        first_worker = task("ONE", 10)
        second_worker = task("TWO", 20)
        archive = archive_task("ARCHIVE", [first_worker, second_worker])
        source = queue(first_worker, second_worker, archive)
        first = dispatch.select(copy.deepcopy(source))
        second = dispatch.select(copy.deepcopy(source))
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])


class LeaseTests(unittest.TestCase):
    """A `running` task's optional lease, and what expiry does and does not do."""

    def test_lease_is_optional_and_never_expires_without_now(self) -> None:
        # Every task record written before this field existed has no lease.
        # That must keep behaving exactly as it always did: a running task
        # with no lease -- or one with a lease nobody asked to check -- is
        # never reclaimed, `--now` omitted or not.
        running = task("RUNNING", 1, state="running")
        ready = task("READY", 1, write_scope=["coordination/tasks/RUNNING/"],
                     artifact_paths=["coordination/tasks/RUNNING/other.json"])
        archive = archive_task("ARCHIVE", [running, ready])
        plan = dispatch.select(queue(running, ready, archive, maximum=2))
        self.assertEqual([item["id"] for item in plan["dispatches"]], ["RUNNING"])
        self.assertEqual(deferred_by_id(plan)["READY"], ["write_scope_conflict:RUNNING"])
        self.assertEqual(plan["expired_leases"], [])

        leased = task("RUNNING", 1, state="running", task_lease=lease())
        plan_with_lease_but_no_now = dispatch.select(
            queue(leased, ready, archive, maximum=2)
        )
        self.assertEqual(
            [item["id"] for item in plan_with_lease_but_no_now["dispatches"]], ["RUNNING"]
        )
        self.assertEqual(plan_with_lease_but_no_now["expired_leases"], [])

    def test_expired_lease_frees_the_write_scope_for_a_queued_successor(self) -> None:
        stale = task(
            "STALE", 1, state="running",
            write_scope=["coordination/tasks/STALE/"],
            artifact_paths=["coordination/tasks/STALE/report.json"],
            task_lease=lease(
                owner="executor-1",
                acquired_at="2026-08-16T00:00:00+00:00",
                expires_at="2026-08-16T01:00:00+00:00",
            ),
        )
        successor = task(
            "SUCCESSOR", 1,
            write_scope=["coordination/tasks/STALE/"],
            artifact_paths=["coordination/tasks/STALE/retry-report.json"],
        )
        archive = archive_task("ARCHIVE", [stale, successor])
        source = queue(stale, successor, archive, maximum=2)

        before_expiry = dispatch.select(
            copy.deepcopy(source), now=datetime.fromisoformat("2026-08-16T00:30:00+00:00")
        )
        self.assertEqual(
            [item["id"] for item in before_expiry["dispatches"]], ["STALE"]
        )
        self.assertEqual(
            deferred_by_id(before_expiry)["SUCCESSOR"], ["write_scope_conflict:STALE"]
        )
        self.assertEqual(before_expiry["expired_leases"], [])

        after_expiry = dispatch.select(
            copy.deepcopy(source), now=datetime.fromisoformat("2026-08-16T02:00:00+00:00")
        )
        dispatched_ids = [item["id"] for item in after_expiry["dispatches"]]
        self.assertIn("SUCCESSOR", dispatched_ids)
        self.assertNotIn("STALE", dispatched_ids)
        self.assertEqual(
            [item["id"] for item in after_expiry["expired_leases"]], ["STALE"]
        )
        self.assertEqual(after_expiry["expired_leases"][0]["owner"], "executor-1")

        # The source record is untouched -- STALE is still "running" in the
        # queue this plan was computed from. Reverting it to queued is a
        # Coordinator decision, made once, not redrawn on every dispatch run.
        self.assertEqual(
            next(t for t in source["tasks"] if t["id"] == "STALE")["state"], "running"
        )

    def test_expiry_is_a_boundary_not_a_race(self) -> None:
        stale = task("STALE", 1, state="running", task_lease=lease(
            expires_at="2026-08-16T01:00:00+00:00"
        ))
        archive = archive_task("ARCHIVE", [stale])
        exactly_at_expiry = dispatch.select(
            queue(stale, archive, maximum=1),
            now=datetime.fromisoformat("2026-08-16T01:00:00+00:00"),
        )
        self.assertEqual(
            [item["id"] for item in exactly_at_expiry["expired_leases"]], ["STALE"]
        )

    def test_two_running_leases_still_cannot_overlap(self) -> None:
        # A lease changes what happens after expiry. It does not relax the
        # existing rule that two tasks cannot BOTH claim to be running over
        # the same scope right now, expired or not -- that invariant is
        # unconditional and stays that way.
        first = task(
            "FIRST", 1, state="running", write_scope=["coordination/live/"],
            artifact_paths=["coordination/live/first.json"], task_lease=lease(owner="a"),
        )
        second = task(
            "SECOND", 1, state="running", write_scope=["coordination/live/report/"],
            artifact_paths=["coordination/live/report/second.json"], task_lease=lease(owner="b"),
        )
        archive = archive_task("ARCHIVE", [first, second])
        with self.assertRaisesRegex(dispatch.DispatchError, "overlapping write scopes"):
            dispatch.validate_queue(queue(first, second, archive))

    def test_rejects_lease_on_a_non_running_task(self) -> None:
        stale_flag = task("QUEUED", 1, state="queued", task_lease=lease())
        with self.assertRaisesRegex(dispatch.DispatchError, 'lease is set but state is not "running"'):
            dispatch.validate_queue(queue(stale_flag))

    def test_rejects_malformed_lease_fields(self) -> None:
        missing_owner = task("A", 1, state="running", task_lease={
            "acquired_at": "2026-08-16T00:00:00+00:00",
            "expires_at": "2026-08-16T01:00:00+00:00",
            "epoch": 1,
        })
        with self.assertRaisesRegex(dispatch.DispatchError, "lease.owner"):
            dispatch.validate_queue(queue(missing_owner))

        bad_epoch = task("A", 1, state="running", task_lease=lease(epoch=0))
        with self.assertRaisesRegex(dispatch.DispatchError, "lease.epoch"):
            dispatch.validate_queue(queue(bad_epoch))

        backwards = task("A", 1, state="running", task_lease=lease(
            acquired_at="2026-08-16T02:00:00+00:00",
            expires_at="2026-08-16T01:00:00+00:00",
        ))
        with self.assertRaisesRegex(dispatch.DispatchError, "expires_at must be after"):
            dispatch.validate_queue(queue(backwards))

        naive = task("A", 1, state="running", task_lease=lease(
            acquired_at="2026-08-16T00:00:00", expires_at="2026-08-16T01:00:00",
        ))
        with self.assertRaisesRegex(dispatch.DispatchError, "explicit UTC offset"):
            dispatch.validate_queue(queue(naive))

    def test_cli_now_flag_is_optional_and_explicit(self) -> None:
        # The CLI is the only place a clock may enter. Confirms parse_timestamp
        # accepts the CLI's own --now shape (a bare 'Z' offset), which the ISO
        # library used elsewhere in this module does not accept unmodified.
        parsed = dispatch.parse_timestamp("2026-08-16T00:00:00Z", "--now")
        self.assertEqual(parsed.isoformat(), "2026-08-16T00:00:00+00:00")


class ZeroComputeBudgetTests(unittest.TestCase):
    """A task may bound its compute at zero; anything above zero stays bounded.

    Both directions matter. Relaxing this for a task that *does* run something
    would remove the only ceiling on it, so every test that pins the relaxation
    is paired with one pinning the rule it must not weaken.
    """

    def validate(self, budget: dict[str, Any]) -> None:
        record = handoff()
        record["budget"] = budget
        dispatch.validate_handoff({"handoff": record, "role": "coordinator"},
                                  "queue.tasks[0]")

    def test_experiment_maximum_runs_zero_may_leave_ceilings_null(self) -> None:
        # GOAL-ECDLP-001 BATCH-e6c1c9 TASK-20260901-833888, exactly as committed.
        self.validate({
            "wall_clock_seconds": None,
            "memory_gb": None,
            "maximum_runs": 1,
            "experiment_maximum_runs": 0,
        })

    def test_maximum_runs_zero_may_leave_ceilings_null(self) -> None:
        # GOAL-MD5-001 BATCH-ebac02 declares zero compute the other way.
        self.validate({
            "wall_clock_seconds": None,
            "memory_gb": None,
            "maximum_runs": 0,
        })

    def test_compute_bearing_task_still_requires_a_wall_clock_ceiling(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "wall_clock_seconds"):
            self.validate({
                "wall_clock_seconds": None,
                "memory_gb": 1,
                "maximum_runs": 1,
            })

    def test_compute_bearing_task_still_requires_a_memory_ceiling(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "memory_gb"):
            self.validate({
                "wall_clock_seconds": 60,
                "memory_gb": None,
                "maximum_runs": 1,
            })

    def test_zero_compute_does_not_admit_a_negative_run_count(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "maximum_runs"):
            self.validate({
                "wall_clock_seconds": None,
                "memory_gb": None,
                "maximum_runs": -1,
                "experiment_maximum_runs": 0,
            })

    def test_zero_compute_does_not_admit_a_nonsense_ceiling(self) -> None:
        # Declaring zero runs permits omitting a ceiling, never asserting a
        # false one: a stated ceiling is still checked.
        with self.assertRaisesRegex(dispatch.DispatchError, "wall_clock_seconds"):
            self.validate({
                "wall_clock_seconds": -5,
                "memory_gb": None,
                "maximum_runs": 0,
            })

    def test_missing_run_count_is_not_a_zero_compute_declaration(self) -> None:
        # Zero compute is DECLARED. An absent maximum_runs declares nothing and
        # must not inherit the relaxation by omission.
        with self.assertRaisesRegex(dispatch.DispatchError, "maximum_runs"):
            self.validate({"wall_clock_seconds": 60, "memory_gb": 1})


class InferencePolicyTests(unittest.TestCase):
    """The optional `inference` block is checked against the policy contract."""

    def check(self, policy: Any, role: str) -> None:
        dispatch.validate_inference({"inference": {"policy": policy}}, role,
                                    "queue.tasks[0].handoff")

    def test_absent_block_is_accepted(self) -> None:
        dispatch.validate_inference({}, "executor", "queue.tasks[0].handoff")

    def test_legacy_alias_is_accepted(self) -> None:
        self.check("review-xhigh", "validator")

    def test_unknown_policy_is_rejected(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "unknown inference policy"):
            self.check("research-sol-maxx", "idea-generator")

    def test_reviewer_needs_an_independent_session_policy(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "independent session"):
            self.check("research-deep", "validator")

    def test_worker_may_not_take_a_state_changing_policy(self) -> None:
        with self.assertRaisesRegex(dispatch.DispatchError, "may change official"):
            self.check("coordinator-orchestration", "executor")


if __name__ == "__main__":
    unittest.main()

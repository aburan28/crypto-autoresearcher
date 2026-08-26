#!/usr/bin/env python3
"""Tests for write-once task claims and goal lanes (tools/goal_lanes.py)."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import goal_lanes as lanes  # noqa: E402
import research_dispatch as dispatch  # noqa: E402

GOAL = "GOAL-T-0000ab"
BATCH = "BATCH-00cdef"
PRODUCER = "TASK-20260825-aaaaaa"
PRODUCER_2 = "TASK-20260825-bbbbbb"
ARCHIVE = "TASK-20260825-cccccc"
BATCH_DIR = f"coordination/goals/{GOAL}/batches/{BATCH}"
T0 = dt.datetime(2026, 8, 25, 12, 0, tzinfo=dt.timezone.utc)


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def handoff(deliverable: str) -> dict:
    return {
        "objective": "o", "uncertainty_reduced": "u", "inputs": ["AGENTS.md"], "constraints": ["c"],
        "deliverables": [deliverable],
        "budget": {"wall_clock_seconds": 60, "memory_gb": 1, "maximum_runs": 1},
        "completion_gate": ["g"],
    }


def producer(task_id: str, priority: int) -> dict:
    return {
        "id": task_id, "title": task_id, "role": "executor", "state": "queued", "priority": priority,
        "review_required": False, "depends_on": [], "read_scope": ["AGENTS.md"],
        "write_scope": [f"{BATCH_DIR}/tasks/{task_id}/"],
        "artifact_paths": [f"{BATCH_DIR}/tasks/{task_id}/report.json"],
        "archived_by": ARCHIVE, "handoff": handoff("report.json"),
    }


def queue_document() -> dict:
    producers = [producer(PRODUCER, 10), producer(PRODUCER_2, 5)]
    archive = {
        "id": ARCHIVE, "title": "snapshot", "role": "coordinator", "state": "queued", "priority": 1,
        "review_required": False, "depends_on": [PRODUCER, PRODUCER_2],
        "read_scope": ["AGENTS.md"] + [p for t in producers for p in t["artifact_paths"]],
        "write_scope": [f"{BATCH_DIR}/archives/{ARCHIVE}/"],
        "artifact_paths": [f"{BATCH_DIR}/archives/{ARCHIVE}/snapshot-receipt.json"],
        "archived_by": ARCHIVE,
        "archive": {"kind": "snapshot", "binding_mode": "content_first",
                    "source_task_ids": [PRODUCER, PRODUCER_2], "record_ids": [GOAL],
                    "commit_sha": None, "parent_sha": None, "path_sha256": {}},
        "handoff": handoff("snapshot-receipt.json"),
    }
    return {"schema": dispatch.SCHEMA, "goal_id": GOAL, "objective": "test", "max_concurrent": 2,
            "tasks": producers + [archive]}


class Repo:
    """A bare origin plus N clones, so cross-worktree discovery is exercised for real."""

    def __init__(self, tmp: Path) -> None:
        self.origin = tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        self.a = self.clone(tmp / "a", "a")
        (self.a / BATCH_DIR).mkdir(parents=True)
        (self.a / BATCH_DIR / "dispatch_queue.json").write_text(json.dumps(queue_document(), indent=1))
        (self.a / "AGENTS.md").write_text("# agents\n")
        git(self.a, "add", "-A")
        git(self.a, "commit", "-qm", "init")
        git(self.a, "push", "-q", "-u", "origin", "HEAD")
        self.b = self.clone(tmp / "b", "b")
        git(self.b, "checkout", "-q", "-b", "lane-b")

    def clone(self, path: Path, name: str) -> Path:
        subprocess.run(["git", "clone", "-q", str(self.origin), str(path)], check=True,
                       capture_output=True)
        git(path, "config", "user.email", f"{name}@example.invalid")
        git(path, "config", "user.name", name)
        return path

    @staticmethod
    def queue(root: Path) -> Path:
        return root / BATCH_DIR / "dispatch_queue.json"


class ClaimTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_claim_is_write_once_and_visible_across_clones_after_push(self) -> None:
        a, b = self.repo.a, self.repo.b
        path = lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=30, now=T0)
        self.assertTrue(path.exists())
        with self.assertRaises(lanes.LaneError):
            lanes.write_once(path, {})  # same path twice is refused, never overwritten
        # Not yet published: b cannot see it, even scanning refs.
        self.assertEqual(lanes.claim_summary(b, Repo.queue(b), now=T0), {})
        lanes.publish(a, [path], "claim", push=True)
        git(b, "fetch", "-q", "origin")
        seen = lanes.claim_summary(b, Repo.queue(b), now=T0)
        self.assertEqual(seen[PRODUCER]["status"], "live")
        self.assertEqual(seen[PRODUCER]["owner"], "coord-a")
        self.assertTrue(seen[PRODUCER]["sources"]["claim"].startswith("ref:"))
        # And b is refused the same task while the claim is live.
        with self.assertRaises(lanes.LaneError):
            lanes.claim_task(b, Repo.queue(b), PRODUCER, owner="coord-b", ttl_minutes=30, now=T0)
        # ...but not a different one.
        lanes.claim_task(b, Repo.queue(b), PRODUCER_2, owner="coord-b", ttl_minutes=30, now=T0)

    def test_expiry_frees_scope_and_reclaim_gets_next_epoch(self) -> None:
        a = self.repo.a
        lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=30, now=T0)
        later = T0 + dt.timedelta(minutes=31)
        self.assertEqual(lanes.claim_summary(a, Repo.queue(a), now=later)[PRODUCER]["status"], "expired")
        path = lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-b", ttl_minutes=30, now=later)
        self.assertTrue(path.name.endswith(".2.claim.json"))
        record = json.loads(path.read_text())
        self.assertEqual(record["supersedes"], {"epoch": 1, "owner": "coord-a", "status": "expired"})
        self.assertFalse(record["forced"])

    def test_release_is_fenced_to_the_owner_and_completed_is_final(self) -> None:
        a = self.repo.a
        lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=30, now=T0)
        with self.assertRaises(lanes.LaneError):
            lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-b", outcome="abandoned", now=T0)
        lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-a", outcome="completed", now=T0)
        summary = lanes.claim_summary(a, Repo.queue(a), now=T0)[PRODUCER]
        self.assertEqual((summary["status"], summary["release"]["outcome"]), ("released", "completed"))
        with self.assertRaises(lanes.LaneError):  # completed is not re-claimable
            lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-c", ttl_minutes=5, now=T0)
        with self.assertRaises(lanes.LaneError):  # and not re-releasable
            lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-a", outcome="failed", now=T0)

    def test_only_queued_tasks_are_claimable(self) -> None:
        a = self.repo.a
        doc = json.loads(Repo.queue(a).read_text())
        doc["tasks"][0]["state"] = "completed"
        Repo.queue(a).write_text(json.dumps(doc))
        with self.assertRaises(lanes.LaneError):
            lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=5, now=T0)
        with self.assertRaises(lanes.LaneError):
            lanes.claim_task(a, Repo.queue(a), "TASK-20260825-ffffff", owner="coord-a", ttl_minutes=5, now=T0)


class OverlayTests(unittest.TestCase):
    """The dispatcher reads claims as holds/completions without touching the queue."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def plan(self, root: Path, now: dt.datetime, *, refs: bool) -> dict:
        claims = lanes.claim_summary(root, Repo.queue(root), include_refs=refs, now=now)
        return dispatch.select(json.loads(Repo.queue(root).read_text()), now=now, claims=claims)

    def test_live_claim_from_another_clone_is_listed_running_not_offered(self) -> None:
        a, b = self.repo.a, self.repo.b
        path = lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=30, now=T0)
        lanes.publish(a, [path], "claim", push=True)
        git(b, "fetch", "-q", "origin")
        plan = self.plan(b, T0, refs=True)
        by_id = {d["id"]: d for d in plan["dispatches"]}
        self.assertEqual(by_id[PRODUCER]["state"], "running")
        self.assertEqual(by_id[PRODUCER]["claim"]["owner"], "coord-a")
        self.assertEqual(by_id[PRODUCER_2]["state"], "queued")
        self.assertIsNone(by_id[PRODUCER_2]["claim"])
        self.assertTrue(plan["gates"]["claimed_tasks_are_not_offered_to_others"])
        # Working-tree-only view in b does not see it: the plan says so by omission.
        self.assertEqual(self.plan(b, T0, refs=False)["claims"], {})
        # The queue file itself was never edited.
        self.assertEqual(json.loads(Repo.queue(b).read_text())["tasks"][0]["state"], "queued")

    def test_completed_releases_unblock_the_archive_and_expired_claims_surface(self) -> None:
        a = self.repo.a
        for task_id, owner in ((PRODUCER, "coord-a"), (PRODUCER_2, "coord-b")):
            lanes.claim_task(a, Repo.queue(a), task_id, owner=owner, ttl_minutes=30, now=T0)
            lanes.release_task(a, Repo.queue(a), task_id, owner=owner, outcome="completed", now=T0)
        plan = self.plan(a, T0, refs=False)
        self.assertEqual([d["id"] for d in plan["dispatches"]], [ARCHIVE])
        self.assertEqual(plan["claims"][PRODUCER]["applied"], "completed")
        # An expired hold on the archive is surfaced, its scope is free, and the
        # task is offered again for the next epoch's claimant.
        lanes.claim_task(a, Repo.queue(a), ARCHIVE, owner="coord-x", ttl_minutes=1, now=T0)
        later = T0 + dt.timedelta(minutes=2)
        plan = self.plan(a, later, refs=False)
        self.assertEqual([(e["id"], e["source"]) for e in plan["expired_leases"]], [(ARCHIVE, "claim")])
        self.assertEqual(plan["claims"][ARCHIVE]["applied"], "queued_after_expiry")
        self.assertEqual([(d["id"], d["claim"]) for d in plan["dispatches"]], [(ARCHIVE, None)])
        path = lanes.claim_task(a, Repo.queue(a), ARCHIVE, owner="coord-y", ttl_minutes=30, now=later)
        self.assertTrue(path.name.endswith(".2.claim.json"))
        self.assertEqual(self.plan(a, later, refs=False)["dispatches"][0]["claim"]["owner"], "coord-y")

    def test_hold_on_a_successor_this_view_cannot_admit_is_reported_not_fatal(self) -> None:
        a = self.repo.a
        lanes.claim_task(a, Repo.queue(a), ARCHIVE, owner="coord-x", ttl_minutes=30, now=T0)
        plan = self.plan(a, T0, refs=False)
        self.assertTrue(plan["claims"][ARCHIVE]["applied"].startswith(
            "ignored:dependencies_incomplete_from_this_view:"))
        self.assertEqual({d["id"] for d in plan["dispatches"]}, {PRODUCER, PRODUCER_2})

    def test_archive_completion_is_never_inferred_from_a_release(self) -> None:
        a = self.repo.a
        for task_id, owner in ((PRODUCER, "coord-a"), (PRODUCER_2, "coord-b")):
            lanes.claim_task(a, Repo.queue(a), task_id, owner=owner, ttl_minutes=30, now=T0)
            lanes.release_task(a, Repo.queue(a), task_id, owner=owner, outcome="completed", now=T0)
        lanes.claim_task(a, Repo.queue(a), ARCHIVE, owner="coord-a", ttl_minutes=30, now=T0)
        lanes.release_task(a, Repo.queue(a), ARCHIVE, owner="coord-a", outcome="completed", now=T0)
        plan = self.plan(a, T0, refs=False)
        self.assertEqual(plan["claims"][ARCHIVE]["applied"],
                         "ignored:archive_completion_requires_queue_record")
        self.assertEqual([d["id"] for d in plan["dispatches"]], [ARCHIVE])


class LaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_open_close_and_cross_clone_visibility(self) -> None:
        a, b = self.repo.a, self.repo.b
        queue_rel = f"{BATCH_DIR}/dispatch_queue.json"
        path = lanes.open_lane(a, GOAL, BATCH, queue_path=queue_rel, owner="coord-a",
                               decision_id="DEC-20260825-000001", objective="x", now=T0)
        with self.assertRaises(lanes.LaneError):  # one lane record per batch
            lanes.open_lane(a, GOAL, BATCH, queue_path=queue_rel, owner="coord-a",
                            decision_id=None, objective="x", now=T0)
        with self.assertRaises(lanes.LaneError):  # queue must live under the batch dir
            lanes.open_lane(a, GOAL, "BATCH-0000ff", queue_path="coordination/elsewhere.json",
                            owner="coord-a", decision_id=None, objective="x", now=T0)
        lanes.publish(a, [path], "lane", push=True)
        git(b, "fetch", "-q", "origin")
        seen = lanes.load_lanes(b, GOAL)
        self.assertEqual(seen[BATCH]["status"], "open")
        self.assertEqual(seen[BATCH]["lane"]["opened_by"], "coord-a")
        # A second lane on the same goal records what was open when it opened.
        second = lanes.open_lane(b, GOAL, "BATCH-0000ff",
                                 queue_path=f"coordination/goals/{GOAL}/batches/BATCH-0000ff/dispatch_queue.json",
                                 owner="coord-b", decision_id=None, objective="y", now=T0)
        self.assertEqual(json.loads(second.read_text())["concurrent_open_lanes_at_open"], [BATCH])
        lanes.close_lane(a, GOAL, BATCH, owner="coord-a", outcome="archived",
                         decision_id="DEC-20260825-000002", ledger_commit="abc", now=T0)
        self.assertEqual(lanes.load_lanes(a, GOAL)[BATCH]["status"], "closed")
        with self.assertRaises(lanes.LaneError):
            lanes.close_lane(a, GOAL, BATCH, owner="coord-a", outcome="archived",
                             decision_id=None, ledger_commit=None, now=T0)


class CliTests(unittest.TestCase):
    def test_cli_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repo(Path(tmp))
            a = repo.a
            q = str(Repo.queue(a))
            tool = str(Path(__file__).resolve().parent / "goal_lanes.py")

            def run(*args: str) -> subprocess.CompletedProcess:
                return subprocess.run([sys.executable, tool, *args], cwd=a, capture_output=True, text=True)

            self.assertEqual(run("claim", q, PRODUCER, "--as", "coord-a", "--ttl-minutes", "5").returncode, 0)
            refused = run("claim", q, PRODUCER, "--as", "coord-b", "--ttl-minutes", "5")
            self.assertEqual(refused.returncode, 2)
            self.assertIn("held by coord-a", refused.stderr)
            listed = run("claims", q, "--json")
            self.assertEqual(json.loads(listed.stdout)[PRODUCER]["status"], "live")
            self.assertEqual(run("release", q, PRODUCER, "--as", "coord-a", "--outcome", "failed").returncode, 0)
            self.assertEqual(run("open-lane", GOAL, BATCH, "--queue", f"{BATCH_DIR}/dispatch_queue.json",
                                 "--objective", "o", "--as", "coord-a").returncode, 0)
            self.assertIn("open", run("lanes", GOAL).stdout)


if __name__ == "__main__":
    unittest.main()

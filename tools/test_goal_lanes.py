#!/usr/bin/env python3
"""Tests for write-once task claims and goal lanes (tools/goal_lanes.py)."""

from __future__ import annotations

import datetime as dt
import hashlib
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

    def _post_merge_collision(self) -> Path:
        """The state an add/add merge leaves: winner's claim + loser's release.

        Two sessions claim inside one fetch interval, both at epoch 1 (the
        collision docs/concurrent-goal-lanes.md says to expect). The loser
        releases `abandoned` as instructed. Merging keeps the winner's claim,
        and the loser's release survives beside it at the same epoch.
        """
        a = self.repo.a
        claims = a / BATCH_DIR / "claims"
        claims.mkdir(parents=True, exist_ok=True)
        (claims / f"{PRODUCER}.1.claim.json").write_text(json.dumps({
            "schema": lanes.CLAIM_SCHEMA, "task_id": PRODUCER, "epoch": 1,
            "owner": "coord-winner", "acquired_at": lanes.fmt(T0),
            "expires_at": lanes.fmt(T0 + dt.timedelta(minutes=30)),
            "branch": "lane-winner", "worktree": str(a), "session": None,
            "forced": False, "supersedes": None,
            "write_scope": [f"{BATCH_DIR}/tasks/{PRODUCER}"],
        }, indent=1))
        (claims / f"{PRODUCER}.1.release.json").write_text(json.dumps({
            "schema": lanes.RELEASE_SCHEMA, "task_id": PRODUCER, "epoch": 1,
            "owner": "coord-loser", "outcome": "abandoned",
            "released_at": lanes.fmt(T0 + dt.timedelta(minutes=1)),
            "was_expired": False, "note": None, "artifact_sha256": {},
        }, indent=1))
        return a

    def test_foreign_release_cannot_free_a_live_claim(self) -> None:
        # THE REGRESSION. Pairing claim and release on (task, epoch) alone read
        # this as `released` and re-offered a task its holder was still working.
        a = self._post_merge_collision()
        seen = lanes.claim_summary(a, Repo.queue(a), now=T0 + dt.timedelta(minutes=2))
        self.assertEqual(seen[PRODUCER]["status"], "live")
        self.assertEqual(seen[PRODUCER]["owner"], "coord-winner")
        self.assertIsNone(seen[PRODUCER]["release"])
        self.assertEqual(seen[PRODUCER]["foreign_release"]["owner"], "coord-loser")
        # The scope is HELD, so another session is still refused the task.
        with self.assertRaises(lanes.LaneError):
            lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-third",
                             ttl_minutes=30, now=T0 + dt.timedelta(minutes=2))

    def test_foreign_release_is_not_offered_as_free_by_the_dispatcher(self) -> None:
        # The consequence that actually cost something: research_dispatch must
        # not offer a task whose only "release" was written by a non-owner.
        a = self._post_merge_collision()
        now = T0 + dt.timedelta(minutes=2)
        claims = lanes.claim_summary(a, Repo.queue(a), include_refs=False, now=now)
        plan = dispatch.select(json.loads(Repo.queue(a).read_text()), now=now, claims=claims)
        by_id = {d["id"]: d for d in plan["dispatches"]}
        self.assertEqual(by_id[PRODUCER]["state"], "running")
        self.assertEqual(by_id[PRODUCER]["claim"]["owner"], "coord-winner")
        self.assertTrue(plan["gates"]["claimed_tasks_are_not_offered_to_others"])

    def test_a_foreign_release_strands_the_holder_at_that_epoch(self) -> None:
        """KNOWN LIMITATION, pinned deliberately rather than left to be rediscovered.

        The fix stops the false free, but it cannot give the holder its release
        back: the path is `{task}.{epoch}.release.json`, the impostor's file
        already occupies it, and these files are write-once by design. So the
        true owner cannot record ANY outcome at this epoch and must let the
        claim expire. That is strictly better than the bug it replaces (a live
        task silently re-offered), and it is not free.

        Fixing it properly means putting the owner in the release filename or
        bumping the epoch, which changes a write-once naming scheme that
        CLAIM_NAME and every committed claim file already depend on. Out of
        scope here; this test exists so the cost is visible and any future
        change to that scheme has to confront it.
        """
        a = self._post_merge_collision()
        now = T0 + dt.timedelta(minutes=2)
        # The impostor is refused, which is the fencing check doing its job.
        with self.assertRaisesRegex(lanes.LaneError, "only the owner releases"):
            lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-loser",
                               outcome="abandoned", now=now)
        # But so is the rightful owner -- on the write-once path, not on fencing.
        with self.assertRaisesRegex(lanes.LaneError, "write-once"):
            lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-winner",
                               outcome="completed", now=now)
        # The scope stays HELD until expiry, which is the safe direction.
        self.assertEqual(
            lanes.claim_summary(a, Repo.queue(a), now=now)[PRODUCER]["status"], "live")
        self.assertEqual(
            lanes.claim_summary(a, Repo.queue(a),
                                now=T0 + dt.timedelta(minutes=31))[PRODUCER]["status"],
            "expired")

    def test_own_release_still_frees_the_claim(self) -> None:
        # Guard against "fix" by making everything live: the ordinary path holds.
        a = self.repo.a
        lanes.claim_task(a, Repo.queue(a), PRODUCER, owner="coord-a", ttl_minutes=30, now=T0)
        lanes.release_task(a, Repo.queue(a), PRODUCER, owner="coord-a",
                           outcome="completed", now=T0 + dt.timedelta(minutes=1))
        seen = lanes.claim_summary(a, Repo.queue(a), now=T0 + dt.timedelta(minutes=2))
        self.assertEqual(seen[PRODUCER]["status"], "released")
        self.assertEqual(seen[PRODUCER]["release"]["outcome"], "completed")
        self.assertIsNone(seen[PRODUCER]["foreign_release"])

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


class CompletedReleaseBindsArtifactsTests(unittest.TestCase):
    """A completed release asserts the work was DONE, so it binds what was produced.

    Before CORR-20260921-942a62 it could bind nothing. TASK-20260916-64a93b was
    released `completed` with an empty artifact_sha256 while its artifacts existed
    only in one machine's working tree; had the release carried hashes, the loss
    would have surfaced as a MISMATCH the next time anyone looked instead of as an
    absence nobody was looking for.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))
        self.root = self.repo.a
        self.queue = Repo.queue(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _args(self, **overrides):
        import argparse
        base = dict(queue=str(self.queue), task=PRODUCER, outcome="completed",
                    note=None, artifact=None, as_addr="coord-a", local_only=True,
                    publish=False, no_push=True, allow_missing_artifacts=False)
        base.update(overrides)
        return argparse.Namespace(**base)

    def _claim(self):
        lanes.claim_task(self.root, self.queue, PRODUCER, owner="coord-a",
                         ttl_minutes=30, now=T0)

    def _produce(self):
        path = self.root / BATCH_DIR / "tasks" / PRODUCER / "report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"finding": "real"}\n')
        return path

    def test_completed_release_records_the_declared_artifact_hash(self) -> None:
        self._claim()
        produced = self._produce()
        lanes.cmd_release(self._args())
        release = json.loads(
            (self.root / BATCH_DIR / "claims" / f"{PRODUCER}.1.release.json").read_text()
        )
        expected = hashlib.sha256(produced.read_bytes()).hexdigest()
        rel = f"{BATCH_DIR}/tasks/{PRODUCER}/report.json"
        self.assertEqual(release["artifact_sha256"], {rel: expected})

    def test_completed_release_is_refused_when_the_artifact_is_absent(self) -> None:
        """The exact shape of the lost release: completed, binding nothing."""
        self._claim()
        with self.assertRaises(lanes.LaneError) as cm:
            lanes.cmd_release(self._args())
        message = str(cm.exception)
        self.assertIn("refusing to release", message)
        self.assertIn("producer_landing.py", message)

    def test_the_refusal_can_be_overridden_deliberately(self) -> None:
        self._claim()
        lanes.cmd_release(self._args(allow_missing_artifacts=True,
                                     note="zero-output task by design"))
        release = json.loads(
            (self.root / BATCH_DIR / "claims" / f"{PRODUCER}.1.release.json").read_text()
        )
        self.assertEqual(release["outcome"], "completed")
        self.assertEqual(release["artifact_sha256"], {})
        self.assertEqual(release["note"], "zero-output task by design")

    def test_failed_and_abandoned_releases_are_not_gated(self) -> None:
        """A failed task legitimately produced nothing; gating it would be wrong."""
        for outcome in ("failed", "abandoned"):
            with self.subTest(outcome=outcome):
                tmp = tempfile.TemporaryDirectory()
                repo = Repo(Path(tmp.name))
                lanes.claim_task(repo.a, Repo.queue(repo.a), PRODUCER,
                                 owner="coord-a", ttl_minutes=30, now=T0)
                import argparse
                lanes.cmd_release(argparse.Namespace(
                    queue=str(Repo.queue(repo.a)), task=PRODUCER, outcome=outcome,
                    note=None, artifact=None, as_addr="coord-a", local_only=True,
                    publish=False, no_push=True, allow_missing_artifacts=False))
                release = json.loads(
                    (repo.a / BATCH_DIR / "claims" / f"{PRODUCER}.1.release.json").read_text()
                )
                self.assertEqual(release["outcome"], outcome)
                tmp.cleanup()

    def test_an_explicit_artifact_hash_wins_over_the_derived_one(self) -> None:
        """The producer's own receipt stays authoritative where it is supplied."""
        self._claim()
        self._produce()
        rel = f"{BATCH_DIR}/tasks/{PRODUCER}/report.json"
        lanes.cmd_release(self._args(artifact=[f"{rel}=" + "f" * 64]))
        release = json.loads(
            (self.root / BATCH_DIR / "claims" / f"{PRODUCER}.1.release.json").read_text()
        )
        self.assertEqual(release["artifact_sha256"][rel], "f" * 64)


class SupersedeLostCompletionTests(unittest.TestCase):
    """Re-claiming a completion whose output was destroyed.

    "A completed task is archived, not re-claimed" is right, and has one blind
    spot found the hard way (CORR-20260921-942a62): when the output no longer
    exists there is nothing to archive, and the task is stuck terminal forever
    with its objective unmet.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))
        self.root = self.repo.a
        self.queue = Repo.queue(self.root)
        self.rel = f"{BATCH_DIR}/tasks/{PRODUCER}/report.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _complete(self, with_artifact: bool) -> None:
        lanes.claim_task(self.root, self.queue, PRODUCER, owner="coord-a",
                         ttl_minutes=30, now=T0)
        hashes = {}
        if with_artifact:
            path = self.root / self.rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n")
            hashes = {self.rel: hashlib.sha256(path.read_bytes()).hexdigest()}
        lanes.release_task(self.root, self.queue, PRODUCER, owner="coord-a",
                           outcome="completed", artifact_sha256=hashes, now=T0)

    def test_a_completed_task_is_not_reclaimable_without_the_flag(self):
        self._complete(with_artifact=False)
        with self.assertRaises(lanes.LaneError) as cm:
            lanes.claim_task(self.root, self.queue, PRODUCER, owner="coord-b",
                             ttl_minutes=30, now=T0)
        self.assertIn("not re-claimable", str(cm.exception))
        self.assertIn("supersedes_lost_completion", str(cm.exception))

    def test_reclaim_succeeds_when_the_output_is_genuinely_gone(self):
        self._complete(with_artifact=False)
        path = lanes.claim_task(
            self.root, self.queue, PRODUCER, owner="coord-b", ttl_minutes=30, now=T0,
            lost_completion_reason="VM replaced between turns; artifacts never committed",
        )
        claim = json.loads(path.read_text())
        self.assertEqual(claim["epoch"], 2)
        lost = claim["supersedes_lost_completion"]
        self.assertEqual(lost["epoch"], 1)
        self.assertEqual(lost["owner"], "coord-a")
        self.assertEqual(lost["bound_artifact_count"], 0)
        self.assertEqual(lost["declared_artifacts_now_absent"], [self.rel])
        self.assertIn("VM replaced", lost["reason"])

    def test_refused_when_the_output_still_exists(self):
        """The check that stops this being a way to redo work that exists."""
        self._complete(with_artifact=True)
        with self.assertRaises(lanes.LaneError) as cm:
            lanes.claim_task(
                self.root, self.queue, PRODUCER, owner="coord-b", ttl_minutes=30, now=T0,
                lost_completion_reason="I would simply like to run it again",
            )
        message = str(cm.exception)
        self.assertIn("DO exist", message)
        self.assertIn("archived, not re-run", message)

    def test_an_ordinary_claim_records_no_superseded_completion(self):
        path = lanes.claim_task(self.root, self.queue, PRODUCER, owner="coord-a",
                                ttl_minutes=30, now=T0)
        self.assertIsNone(json.loads(path.read_text())["supersedes_lost_completion"])

    def test_the_immutable_release_is_not_touched(self):
        """The completion was accurate when written and stays exactly as written."""
        self._complete(with_artifact=False)
        release_path = self.root / BATCH_DIR / "claims" / f"{PRODUCER}.1.release.json"
        before = release_path.read_bytes()
        lanes.claim_task(self.root, self.queue, PRODUCER, owner="coord-b",
                         ttl_minutes=30, now=T0,
                         lost_completion_reason="output lost with its machine")
        self.assertEqual(release_path.read_bytes(), before)

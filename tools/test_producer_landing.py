"""Tests for tools/producer_landing.py.

Every test builds a real temporary git repository and runs the tool against it,
because the whole value of this tool is what it does to an index and a commit,
and a mocked git proves nothing about that.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import producer_landing


def run_git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


class LandingHarness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        run_git(self.repo, "init", "-q", "-b", "main")
        run_git(self.repo, "config", "user.email", "t@example.com")
        run_git(self.repo, "config", "user.name", "Test")
        (self.repo / "AGENTS.md").write_text("marker\n")
        run_git(self.repo, "add", "AGENTS.md")
        run_git(self.repo, "commit", "-q", "-m", "init")
        self.qdir = self.repo / "coordination" / "b"
        self.qdir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_queue(self, tasks) -> Path:
        path = self.qdir / "dispatch_queue.json"
        path.write_text(json.dumps({"tasks": tasks}, indent=1))
        run_git(self.repo, "add", str(path.relative_to(self.repo)))
        run_git(self.repo, "commit", "-q", "-m", "queue")
        return path

    def produce(self, *rels: str):
        for rel in rels:
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"content of {rel}\n")

    def land(self, queue_path: Path, task_id: str, **kw):
        queue = producer_landing.load_queue(queue_path)
        return producer_landing.land(self.repo, queue_path, queue, task_id,
                                     push=kw.get("push", False),
                                     dry_run=kw.get("dry_run", False))


PRODUCER = {
    "id": "TASK-20260921-aaaaaa",
    "state": "queued",
    "artifact_paths": ["work/t1/report.md", "work/t1/data.json"],
    "write_scope": ["work/t1"],
}


class TestLandingCommitsExactlyTheDeclaredSet(LandingHarness):
    def test_lands_declared_artifacts(self):
        q = self.write_queue([PRODUCER])
        self.produce("work/t1/report.md", "work/t1/data.json")
        self.assertEqual(self.land(q, PRODUCER["id"]), 0)
        tracked = run_git(self.repo, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("work/t1/report.md", tracked)
        self.assertIn("work/t1/data.json", tracked)

    def test_does_not_stage_undeclared_files_in_the_same_directory(self):
        """A producer that wrote a scratch file does not get it committed.

        The declared set is the contract; a stray file beside it is not silently
        adopted into the record.
        """
        q = self.write_queue([PRODUCER])
        self.produce("work/t1/report.md", "work/t1/data.json", "work/t1/scratch.tmp")
        self.land(q, PRODUCER["id"])
        tracked = run_git(self.repo, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn("scratch.tmp", tracked)

    def test_commit_message_names_the_task_and_says_it_is_not_an_archive(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        self.land(q, PRODUCER["id"])
        msg = run_git(self.repo, "log", "-1", "--format=%B")
        self.assertIn(PRODUCER["id"], msg)
        self.assertIn("not an archive", msg)
        self.assertIn("CORR-20260921-942a62", msg)

    def test_idempotent(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        self.land(q, PRODUCER["id"])
        head = run_git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(self.land(q, PRODUCER["id"]), 0)
        self.assertEqual(run_git(self.repo, "rev-parse", "HEAD"), head)

    def test_dry_run_commits_nothing(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        head = run_git(self.repo, "rev-parse", "HEAD")
        self.land(q, PRODUCER["id"], dry_run=True)
        self.assertEqual(run_git(self.repo, "rev-parse", "HEAD"), head)
        self.assertEqual(run_git(self.repo, "diff", "--cached", "--name-only"), "")


class TestPartialProduction(LandingHarness):
    def test_lands_what_exists_and_reports_the_gap(self):
        """A producer that filed two of three files still gets both landed.

        Refusing here would be the worse failure: it would keep real output in
        the working tree because other output is missing, which is exactly the
        state the tool exists to end.
        """
        task = dict(PRODUCER, artifact_paths=PRODUCER["artifact_paths"] + ["work/t1/c.json"])
        q = self.write_queue([task])
        self.produce(*PRODUCER["artifact_paths"])
        self.assertEqual(self.land(q, task["id"]), 0)
        tracked = run_git(self.repo, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("work/t1/report.md", tracked)
        self.assertIn("Declared but absent", run_git(self.repo, "log", "-1", "--format=%B"))

    def test_refuses_when_nothing_was_produced(self):
        q = self.write_queue([PRODUCER])
        with self.assertRaises(SystemExit) as cm:
            self.land(q, PRODUCER["id"])
        self.assertIn("NONE exists on disk", str(cm.exception))


class TestRefusals(LandingHarness):
    def test_refuses_an_archive_task(self):
        archive = {
            "id": "TASK-20260921-bbbbbb",
            "state": "queued",
            "artifact_paths": ["work/a/receipt.json"],
            "write_scope": ["work/a"],
            "archive": {"kind": "snapshot", "source_task_ids": [PRODUCER["id"]]},
        }
        q = self.write_queue([PRODUCER, archive])
        self.produce("work/a/receipt.json")
        with self.assertRaises(SystemExit) as cm:
            self.land(q, archive["id"])
        self.assertIn("ARCHIVE task", str(cm.exception))

    def test_refuses_artifacts_outside_the_tasks_own_write_scope(self):
        task = dict(PRODUCER, artifact_paths=["work/t1/report.md", "ledger/goals/g.yaml"])
        q = self.write_queue([task])
        self.produce("work/t1/report.md", "ledger/goals/g.yaml")
        with self.assertRaises(SystemExit) as cm:
            self.land(q, task["id"])
        self.assertIn("outside the task's own write_scope", str(cm.exception))

    def test_refuses_a_path_another_task_owns(self):
        """Two tasks claiming one file is the defect landing must not launder."""
        other = {
            "id": "TASK-20260921-cccccc",
            "state": "queued",
            "artifact_paths": ["work/t1/data.json"],
            "write_scope": ["work/t1"],
        }
        q = self.write_queue([PRODUCER, other])
        self.produce(*PRODUCER["artifact_paths"])
        with self.assertRaises(SystemExit) as cm:
            self.land(q, PRODUCER["id"])
        self.assertIn("owned by another task", str(cm.exception))

    def test_refuses_an_unknown_task(self):
        q = self.write_queue([PRODUCER])
        with self.assertRaises(SystemExit) as cm:
            self.land(q, "TASK-20260921-zzzzzz")
        self.assertIn("not in this queue", str(cm.exception))


class TestCheckMode(LandingHarness):
    def test_reports_unlanded_output_and_exits_nonzero(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        queue = producer_landing.load_queue(q)
        self.assertEqual(producer_landing.report_check(self.repo, q, queue), 1)

    def test_clean_after_landing(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        self.land(q, PRODUCER["id"])
        queue = producer_landing.load_queue(q)
        self.assertEqual(producer_landing.report_check(self.repo, q, queue), 0)

    def test_ignores_archive_tasks_and_tasks_with_no_artifacts(self):
        archive = {
            "id": "TASK-20260921-bbbbbb", "state": "queued",
            "artifact_paths": ["work/a/receipt.json"], "write_scope": ["work/a"],
            "archive": {"kind": "snapshot", "source_task_ids": []},
        }
        empty = {"id": "TASK-20260921-dddddd", "state": "queued",
                 "artifact_paths": [], "write_scope": ["work/e"]}
        q = self.write_queue([PRODUCER, archive, empty])
        self.produce("work/a/receipt.json")
        rows = producer_landing.landing_status(
            self.repo, producer_landing.load_queue(q))
        self.assertEqual([r["task_id"] for r in rows], [PRODUCER["id"]])

    def test_a_missing_declared_artifact_is_not_reported_as_unlanded(self):
        """Absent and unlanded are different states and must not be conflated."""
        q = self.write_queue([PRODUCER])
        self.produce("work/t1/report.md")
        rows = producer_landing.landing_status(
            self.repo, producer_landing.load_queue(q))
        self.assertEqual(rows[0]["unlanded"], ["work/t1/report.md"])
        self.assertEqual(rows[0]["missing"], ["work/t1/data.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestUndeclaredOutputInScope(LandingHarness):
    """A producer that writes more than it declared is still exposed.

    On the lost BATCH-e0a0c1 reads, two cards declared three files each and the
    readers filed seventeen and twelve. Landing commits the declared set by
    design, so the extras would have been lost even with the tool in place.
    """

    def test_extra_files_in_scope_are_reported(self):
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        self.produce("work/t1/recheck.py", "work/t1/extract/raw.txt")
        rows = producer_landing.landing_status(
            self.repo, producer_landing.load_queue(q))
        self.assertEqual(
            rows[0]["undeclared_in_scope"],
            ["work/t1/extract/raw.txt", "work/t1/recheck.py"],
        )

    def test_landing_does_not_adopt_them(self):
        """The declared set is the contract; landing must not widen it silently."""
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"], "work/t1/recheck.py")
        self.land(q, PRODUCER["id"])
        tracked = run_git(self.repo, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertIn("work/t1/report.md", tracked)
        self.assertNotIn("recheck.py", tracked)

    def test_check_exits_nonzero_on_undeclared_output_alone(self):
        """Even with every declared path landed, extras keep the report red."""
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"])
        self.land(q, PRODUCER["id"])
        self.produce("work/t1/recheck.py")
        queue = producer_landing.load_queue(q)
        self.assertEqual(producer_landing.report_check(self.repo, q, queue), 1)

    def test_already_tracked_extras_are_not_reported(self):
        """A committed file in scope is not an exposure."""
        q = self.write_queue([PRODUCER])
        self.produce(*PRODUCER["artifact_paths"], "work/t1/recheck.py")
        run_git(self.repo, "add", "work/t1/recheck.py")
        run_git(self.repo, "commit", "-q", "-m", "recheck")
        rows = producer_landing.landing_status(
            self.repo, producer_landing.load_queue(q))
        self.assertEqual(rows[0]["undeclared_in_scope"], [])

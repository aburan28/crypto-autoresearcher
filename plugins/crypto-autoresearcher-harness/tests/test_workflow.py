"""Fixture lifecycle and read-only observation tests; no research is executed."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(REPO / "tools"))
import checkpoint
import entrypoints
import research_dispatch as dispatch
from test_research_dispatch import task, archive_task, queue, FakeGitVerifier


class EntryPointTests(unittest.TestCase):
    def test_all_adapters_are_generated_and_references_exist(self):
        self.assertEqual(entrypoints.check(REPO), [])

    def test_drift_is_detected_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / entrypoints.CANONICAL
            canonical.parent.mkdir(parents=True)
            canonical.write_text("canonical")
            for relative, (name, mode) in entrypoints.ADAPTERS.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(entrypoints.render(name, mode))
            changed = root / next(iter(entrypoints.ADAPTERS))
            changed.write_text("independent workflow")
            self.assertTrue(any("adapter drift" in p for p in entrypoints.check(root)))
            self.assertEqual(changed.read_text(), "independent workflow")

    def test_duplicate_inventory_deduplicates_same_physical_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed = root / "installed"
            installed.mkdir()
            (installed / "SKILL.md").write_text(
                "---\nname: crypto-autoresearcher-harness\n---\n")
            found = entrypoints.discover(REPO, [installed, installed])
            self.assertEqual(len(found), 2)
            self.assertIn(str((installed / "SKILL.md").resolve()), found)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        producer = task("PRODUCER", 1, review_required=True)
        snapshot = archive_task("SNAPSHOT", [producer])
        review = task("REVIEW", 2, role="validator",
                      depends_on=["PRODUCER", "SNAPSHOT"])
        ledger = archive_task("LEDGER", [review], kind="ledger")
        self.queue = queue(producer, snapshot, review, ledger, maximum=2,
                           goal_id="GOAL-TEST-001")
        self.verifiers = {}

    def select(self):
        class Receipts:
            def __init__(inner, verifiers):
                inner.verifiers = verifiers

            def verify_archive(inner, record, expected_paths):
                if record["id"] not in inner.verifiers:
                    raise dispatch.DispatchError("fixture receipt unavailable")
                inner.verifiers[record["id"]].verify_archive(record, expected_paths)
        return dispatch.select(self.queue, repository_verifier=Receipts(self.verifiers))

    def observation(self, plan, previous=None):
        return checkpoint.observe(
            plan, repo=Path("/fixture"), queue=Path("/fixture/queue.json"),
            mode="goal", observed_at="2026-09-06T00:00:00Z", previous=previous)

    def finish_archive(self, index):
        record = self.queue["tasks"][index]
        by_id = {t["id"]: t for t in self.queue["tasks"]}
        paths = list(record["artifact_paths"])
        for identifier in record["archive"]["source_task_ids"]:
            paths.extend(by_id[identifier]["artifact_paths"])
        contents = {p: ("fixture " + p).encode() for p in paths}
        record["state"] = "completed"
        record["archive"].update({
            "commit_sha": "a" * 40, "parent_sha": "b" * 40,
            "path_sha256": {p: hashlib.sha256(data).hexdigest()
                            for p, data in contents.items()},
        })
        self.verifiers[record["id"]] = FakeGitVerifier(
            changed_paths=paths, contents=contents,
            message=" ".join([record["id"], *record["archive"]["record_ids"]]))

    def test_full_fixture_lifecycle_and_progress(self):
        first = self.observation(self.select())
        self.assertEqual([t["id"] for t in first["projection"]["ready"]], ["PRODUCER"])
        self.queue["tasks"][0]["state"] = "completed"
        second = self.observation(self.select(), first)
        self.assertEqual(second["delta"]["newly_completed"], ["PRODUCER"])
        self.assertEqual([t["id"] for t in second["projection"]["ready"]], ["SNAPSHOT"])
        self.finish_archive(1)
        plan = self.select()
        self.assertEqual([t["id"] for t in plan["dispatches"]], ["REVIEW"])
        self.queue["tasks"][2]["state"] = "completed"
        self.assertEqual([t["id"] for t in self.select()["dispatches"]], ["LEDGER"])
        self.finish_archive(3)
        last = self.observation(self.select(), second)
        self.assertEqual(last["projection"]["ready"], [])
        self.assertEqual(len(last["projection"]["terminal"]), 4)
        self.assertNotIn("goal_status", last)  # task completion cannot close a goal

    def test_failed_snapshot_receipt_refuses_review(self):
        self.queue["tasks"][0]["state"] = "completed"
        self.finish_archive(1)
        self.verifiers["SNAPSHOT"].resolves = False
        with self.assertRaisesRegex(dispatch.DispatchError, "does not resolve"):
            self.select()

    def test_unchanged_clock_is_not_progress(self):
        first = self.observation(self.select())
        again = checkpoint.observe(
            self.select(), repo=Path("/fixture"), queue=Path("/fixture/queue.json"),
            mode="goal", observed_at="2026-09-07T00:00:00Z", previous=first)
        self.assertEqual(again["delta"]["kind"], "unchanged")
        self.assertEqual(again["delta"]["newly_completed"], [])

    def test_failure_is_not_completion(self):
        first = self.observation(self.select())
        self.queue["tasks"][0]["state"] = "failed"
        later = self.observation(self.select(), first)
        self.assertEqual(later["delta"]["newly_failed"], ["PRODUCER"])
        self.assertEqual(later["delta"]["newly_completed"], [])
        self.assertTrue(later["projection"]["deferred"])

    def test_running_claim_exposes_owner_and_is_not_ready(self):
        plan = self.select()
        plan["dispatches"][0]["state"] = "running"
        plan["dispatches"][0]["claim"] = {"owner": "executor-other", "epoch": 1}
        output = self.observation(plan)
        self.assertEqual(output["projection"]["ready"], [])
        self.assertEqual(output["projection"]["running"][0]["claim"]["owner"], "executor-other")

    def test_different_queue_cannot_silently_compare(self):
        first = self.observation(self.select())
        first["identity"]["queue"] = "/different/queue.json"
        with self.assertRaisesRegex(ValueError, "different checkout"):
            self.observation(self.select(), first)

    def test_failed_gate_is_not_a_checkpoint(self):
        plan = self.select()
        plan["gates"]["completed_archive_commits_verified"] = False
        with self.assertRaisesRegex(ValueError, "gates"):
            self.observation(plan)

    def test_cli_reads_real_dispatcher_without_mutating_fixture(self):
        # The real CLI and Git verifier see an isolated git repository; no
        # completed archives exist yet, so the first producer should be ready.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "tools").symlink_to(REPO / "tools", target_is_directory=True)
            path = root / "queue.json"
            original = json.dumps(self.queue).encode()
            path.write_bytes(original)
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "scripts/checkpoint.py"),
                 "--repo", str(root), "--queue", "queue.json", "--mode", "status"],
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["projection"]["ready"][0]["id"], "PRODUCER")
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(sorted(p.name for p in root.iterdir()),
                             [".git", "queue.json", "tools"])

    def test_cli_dispatch_failure_produces_no_success_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tools").symlink_to(REPO / "tools", target_is_directory=True)
            path = root / "queue.json"
            path.write_text("{}")
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "scripts/checkpoint.py"),
                 "--repo", str(root), "--queue", "queue.json", "--mode", "goal"],
                text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("dispatcher refused", result.stderr)


if __name__ == "__main__":
    unittest.main()

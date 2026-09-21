"""Recovery is scheduling, never a fabricated terminal observation."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_dispatch as dispatch
import task_recovery as recovery
from test_research_dispatch import task, archive_task, queue

NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
OLD = "TASK-20260904-aaaaaa"
NEW = "TASK-20260906-bbbbbb"


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / "new"
        self.root.mkdir()
        self.old_root = Path(self.tmp.name).resolve() / "old"
        self.old_root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.old = task(OLD, 10)
        del self.old["read_scope"]  # Reproduce the real invalid predecessor.
        self.predecessor = queue(self.old)
        self.old_binding = self.commit_file("coordination/old/queue.json", self.predecessor)
        self.new = task(NEW, 10)
        self.q = queue(self.new, archive_task("ARCHIVE", [self.new]))
        self.claim = {"status": "expired", "owner": "original-owner", "epoch": 1,
                      "session": None, "release": None}
        self.new["recovery"] = {
            "mode": "isolated_successor_v1", "predecessor_task_id": OLD,
            "predecessor_queue": self.old_binding, "predecessor_epoch": 1,
            "predecessor_owner": "original-owner", "session": "new-session",
            "predecessor_worktree": str(self.old_root),
            "successor_worktree": str(self.root),
            "supersedes_decision_ids": ["DEC-20260905-cccccc"],
        }
        self.approve()
        self.verifier = dispatch.GitRepositoryVerifier(self.root)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, check=True).stdout.strip()

    def commit_file(self, path, obj):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(obj, sort_keys=True).encode()
        p.write_bytes(raw)
        self.git("add", path)
        self.git("commit", "-qm", "test binding")
        return {"path": path, "commit": self.git("rev-parse", "HEAD"),
                "sha256": hashlib.sha256(raw).hexdigest()}

    def approve(self):
        r = self.new["recovery"]
        approval = {k: r[k] for k in ("predecessor_task_id", "predecessor_epoch",
                    "predecessor_owner", "predecessor_worktree", "successor_worktree",
                    "session", "supersedes_decision_ids")}
        approval.update(successor_task_id=NEW, allow_unknown_runtime=True,
                        predecessor_queue_sha256=self.old_binding["sha256"],
                        successor_contract_sha256=recovery.contract_sha256(self.new))
        decision = {"coordinator_decision": {"id": "DEC-20260906-dddddd",
                    "target_ids": [OLD, NEW], "decided_by": "coordinator",
                    "decision": "revise", "recovery_authorization": approval}}
        r["decision"] = self.commit_file("ledger/decisions/DEC-20260906-dddddd.yaml", decision)

    def select(self, now=NOW):
        history = {OLD: [{"epoch": 1, "claim": {"worktree": str(self.old_root)}}]}
        with patch.object(recovery.lanes, "claim_summary", return_value={OLD: self.claim}), \
             patch.object(recovery.lanes, "load_claims", return_value=history):
            return dispatch.select(copy.deepcopy(self.q), repository_verifier=self.verifier, now=now)

    def test_invalid_queue_unknown_runtime_recommends_successor_not_release(self):
        before = copy.deepcopy(self.predecessor)
        report = recovery.assess(self.predecessor, OLD, self.claim, now=NOW)
        self.assertEqual(report["next_action"], "request_isolated_successor_decision")
        self.assertIn("read_scope", report["queue_diagnostic"])
        self.assertEqual(report["runtime_status"], "unknown")
        self.assertFalse(report["dispatch_authorized"])
        self.assertFalse(report["release_required"])
        self.assertEqual(before, self.predecessor)

    def test_live_lease_is_not_a_verified_process_wait(self):
        report = recovery.assess(self.predecessor, OLD, {"status": "live"}, now=NOW)
        self.assertEqual(report["next_action"], "preserve_live_lease")
        self.assertEqual(report["runtime_status"], "unknown")

    def test_completed_predecessor_routes_to_existing_outputs(self):
        self.claim = {"status": "released", "release": {"outcome": "completed"}}
        self.assertEqual(recovery.assess(self.predecessor, OLD, self.claim, now=NOW)["next_action"],
                         "verify_existing_outputs")

    def test_valid_successor_runs_without_original_session_or_queue_repair(self):
        before = (self.root / self.old_binding["path"]).read_bytes()
        plan = self.select()
        self.assertEqual([t["id"] for t in plan["dispatches"]], [NEW])
        self.assertIn("recovery", plan["dispatches"][0])
        self.assertEqual(before, (self.root / self.old_binding["path"]).read_bytes())
        self.assertFalse((self.root / "coordination/old/claims").exists())

    def test_live_or_completed_or_missing_claim_refused(self):
        for status in ("live", "released", "missing"):
            with self.subTest(status=status):
                self.claim["status"] = status
                with self.assertRaisesRegex(dispatch.DispatchError, "currently expired"):
                    self.select()

    def test_new_epoch_requires_reassessment(self):
        self.claim["epoch"] = 2
        with self.assertRaisesRegex(dispatch.DispatchError, "claim changed"):
            self.select()

    def test_duplicate_keys_refused(self):
        with self.assertRaisesRegex(dispatch.DispatchError, "duplicate mapping key"):
            recovery._parse('{"coordinator_decision": {}, "coordinator_decision": {}}')

    def test_module_api_and_cli_recovery_errors_are_clean(self):
        path = self.root / "successor.json"
        broken = copy.deepcopy(self.q)
        broken["tasks"][0]["recovery"]["session"] = None
        path.write_text(json.dumps(broken))
        result = subprocess.run([sys.executable, str(Path(dispatch.__file__)), str(path),
                   "--repo-root", str(self.root), "--claims", "off", "--output",
                   str(self.root / "plan.json"), "--report", str(self.root / "plan.md")],
                   capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("recorded successor session", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse((self.root / "plan.json").exists())

    def test_cli_admits_real_expired_claim_even_with_successor_claims_off(self):
        claim_path = self.root / "coordination/old/claims" / f"{OLD}.1.claim.json"
        claim_path.parent.mkdir(parents=True)
        claim_path.write_text(json.dumps({
            "task_id": OLD, "epoch": 1, "owner": "original-owner", "session": None,
            "branch": "old", "worktree": str(self.old_root),
            "acquired_at": "2026-09-04T00:00:00Z", "expires_at": "2026-09-04T01:00:00Z",
        }))
        path = self.root / "successor.json"
        path.write_text(json.dumps(self.q))
        command = [sys.executable, str(Path(dispatch.__file__)), str(path),
                   "--repo-root", str(self.root), "--claims", "off", "--now", NOW.isoformat(),
                   "--output", str(self.root / "plan.json"), "--report", str(self.root / "plan.md")]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads((self.root / "plan.json").read_text())
        self.assertEqual([t["id"] for t in plan["dispatches"]], [NEW])
        raw = json.loads(claim_path.read_text())
        raw["expires_at"] = "2099-01-01T00:00:00Z"
        claim_path.write_text(json.dumps(raw))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("currently expired", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_archive_is_still_refused(self):
        self.q["tasks"] = [self.new]
        with self.assertRaises(dispatch.DispatchError):
            self.select()

    def test_claiming_successor_does_not_bypass_predecessor_gate(self):
        self.new["state"] = "running"
        self.claim["status"] = "live"
        with self.assertRaisesRegex(dispatch.DispatchError, "currently expired"):
            self.select()

    def test_running_successor_can_have_partial_outputs(self):
        self.new["state"] = "running"
        p = self.root / self.new["artifact_paths"][0]
        p.parent.mkdir(parents=True)
        p.write_text("partial")
        self.assertEqual(self.select()["dispatches"][0]["id"], NEW)

    def test_same_worktree_refused(self):
        self.new["recovery"]["predecessor_worktree"] = str(self.root)
        with self.assertRaisesRegex(dispatch.DispatchError, "distinct actual"):
            self.select()

    def test_overlapping_archive_refused(self):
        self.q["tasks"][1]["write_scope"].append(self.old["write_scope"][0])
        with self.assertRaisesRegex(dispatch.DispatchError, "overlaps predecessor"):
            self.select()

    def test_missing_session_refused(self):
        self.new["recovery"]["session"] = None
        with self.assertRaisesRegex(dispatch.DispatchError, "recorded successor session"):
            self.select()

    def test_contract_change_invalidates_approval(self):
        self.new["handoff"]["objective"] = "different research"
        with self.assertRaisesRegex(dispatch.DispatchError, "exact successor"):
            self.select()

    def test_unbounded_budget_refused(self):
        self.new["handoff"]["budget"]["wall_clock_seconds"] = float("inf")
        with self.assertRaisesRegex(dispatch.DispatchError, "finite positive"):
            self.select()

    def test_hash_mismatch_refused(self):
        self.new["recovery"]["decision"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(dispatch.DispatchError, "hash mismatch"):
            self.select()

    def test_uncommitted_decision_edit_refused(self):
        (self.root / self.new["recovery"]["decision"]["path"]).write_text("{}")
        with self.assertRaisesRegex(dispatch.DispatchError, "differs from current"):
            self.select()

    def test_late_original_outputs_require_reconciliation(self):
        p = self.old_root / self.old["artifact_paths"][0]
        p.parent.mkdir(parents=True)
        p.write_text("late output")
        with self.assertRaisesRegex(dispatch.DispatchError, "predecessor output exists"):
            self.select()
        self.assertEqual(p.read_text(), "late output")

    def test_existing_successor_outputs_not_overwritten(self):
        p = self.root / self.new["artifact_paths"][0]
        p.parent.mkdir(parents=True)
        p.write_text("partial")
        with self.assertRaisesRegex(dispatch.DispatchError, "successor output exists"):
            self.select()

    def test_path_escape_refused(self):
        (self.root / "escape").symlink_to(self.old_root, target_is_directory=True)
        self.new["write_scope"].append("escape/")
        with self.assertRaisesRegex(dispatch.DispatchError, "escapes worktree"):
            self.select()

    def test_missing_clock_or_verifier_refused(self):
        with self.assertRaisesRegex(dispatch.DispatchError, "explicit timezone-aware"):
            self.select(now=None)
        with self.assertRaisesRegex(dispatch.DispatchError, "GitRepositoryVerifier"):
            dispatch.select(copy.deepcopy(self.q), now=NOW)


if __name__ == "__main__":
    unittest.main()

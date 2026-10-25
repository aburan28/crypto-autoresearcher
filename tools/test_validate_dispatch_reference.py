"""Forwarding integrity checks must not bypass normal queue validation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_dispatch_reference import (
    archived_refusal, canonical_queue, FORWARD_SCHEMA, QUEUE_SCHEMA,
)


class ForwardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "coordination/intake/dispatch_queue.json"
        self.target_rel = "coordination/goals/GOAL-ECDLP-001/batches/BATCH-abcdef/dispatch_queue.json"
        self.target = self.root / self.target_rel
        self.original = {"schema": QUEUE_SCHEMA, "batch_id": "BATCH-abcdef", "tasks": [{"id": "TASK-20260907-abcdef"}]}
        self.write(self.source, self.original)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "source fixture")
        commit = self.git("rev-parse", "HEAD").strip()
        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.forward = {"schema": FORWARD_SCHEMA, "goal_id": "GOAL-ECDLP-001", "batch_id": "BATCH-abcdef",
                        "canonical_queue_path": self.target_rel, "routing_decision": "DEC-20260907-abcdef",
                        "source_commit": commit, "source_queue_sha256": digest,
                        "historical_task_cards": copy.deepcopy(self.original["tasks"]),
                        "historical_queue_metadata": {k: v for k, v in self.original.items() if k != "tasks"}}
        self.current = {"schema": QUEUE_SCHEMA, "goal_id": "GOAL-ECDLP-001", "batch_id": "BATCH-abcdef",
                        "routing_amendment": {"decision_id": "DEC-20260907-abcdef",
                            "source_queue_path": self.source.relative_to(self.root).as_posix(),
                            "source_queue_commit": commit, "source_queue_sha256": digest,
                            "sole_runnable_route": self.target_rel}, "tasks": self.original["tasks"]}
        self.decision_path = self.root / "ledger/decisions/DEC-20260907-abcdef.yaml"
        self.decision = {"coordinator_decision": {"id": "DEC-20260907-abcdef", "decided_by": "coordinator",
                         "source_commit": commit, "source_queue_sha256": digest,
                         "basis_refs": [self.source.relative_to(self.root).as_posix(), self.target_rel]}}
        self.flush()

    def git(self, *args):
        # Auto gc / maintenance may detach a background process that is still
        # writing into .git when TemporaryDirectory.cleanup() runs, which fails
        # teardown with "Directory not empty: '.git'" (seen in CI on PR #1453).
        return subprocess.check_output(
            ["git", "-C", str(self.root), "-c", "gc.auto=0",
             "-c", "maintenance.auto=false", *args], text=True)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + "\n")

    def flush(self):
        self.write(self.source, self.forward)
        self.write(self.target, self.current)
        self.write(self.decision_path, self.decision)

    def test_exact_forward_resolves_without_modifying_source(self):
        before = self.source.read_bytes()
        self.assertEqual(canonical_queue(self.source, self.root), self.target)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(canonical_queue(self.target, self.root), self.target)

    def test_source_hash_mismatch_refused(self):
        self.forward["source_queue_sha256"] = "0" * 64
        self.flush()
        with self.assertRaisesRegex(ValueError, "source queue hash mismatch"):
            canonical_queue(self.source, self.root)

    def test_historical_task_tampering_refused(self):
        self.forward["historical_task_cards"][0]["id"] = "TASK-20260907-aaaaaa"
        self.flush()
        with self.assertRaisesRegex(ValueError, "historical task cards"):
            canonical_queue(self.source, self.root)

    def test_metadata_additions_and_omissions_refused(self):
        self.forward["historical_queue_metadata"]["scientific_validation"] = "completed"
        self.flush()
        with self.assertRaisesRegex(ValueError, "historical queue metadata"):
            canonical_queue(self.source, self.root)
        del self.forward["historical_queue_metadata"]["scientific_validation"]
        del self.forward["historical_queue_metadata"]["batch_id"]
        self.flush()
        with self.assertRaisesRegex(ValueError, "historical queue metadata"):
            canonical_queue(self.source, self.root)

    def test_string_reference_substrings_and_dropped_tasks_refused(self):
        self.decision["coordinator_decision"]["basis_refs"] = "prefix " + " ".join(
            self.decision["coordinator_decision"]["basis_refs"]) + " suffix"
        self.flush()
        with self.assertRaisesRegex(ValueError, "does not name both routes"):
            canonical_queue(self.source, self.root)
        self.current["tasks"] = []
        self.flush()
        with self.assertRaisesRegex(ValueError, "dropped historical task"):
            canonical_queue(self.source, self.root)

    def test_alphanumeric_goal_area_uses_ledger_grammar(self):
        old = self.target_rel
        self.target_rel = old.replace("GOAL-ECDLP-001", "GOAL-SHA2-001")
        self.target = self.root / self.target_rel
        self.forward.update(goal_id="GOAL-SHA2-001", canonical_queue_path=self.target_rel)
        self.current["goal_id"] = "GOAL-SHA2-001"
        self.current["routing_amendment"]["sole_runnable_route"] = self.target_rel
        self.decision["coordinator_decision"]["basis_refs"][-1] = self.target_rel
        self.flush()
        self.assertEqual(canonical_queue(self.source, self.root), self.target)

    def test_wrong_target_and_nested_forward_refused(self):
        self.forward["canonical_queue_path"] = "../outside.json"
        self.flush()
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            canonical_queue(self.source, self.root)
        self.forward["canonical_queue_path"] = self.target_rel
        self.current["schema"] = FORWARD_SCHEMA
        self.flush()
        with self.assertRaisesRegex(ValueError, "never another forwarding"):
            canonical_queue(self.source, self.root)

    def test_unknown_schema_or_runnable_forward_refused(self):
        self.forward["schema"] = "made.up"
        self.flush()
        with self.assertRaisesRegex(ValueError, "unknown"):
            canonical_queue(self.source, self.root)
        self.forward["schema"] = FORWARD_SCHEMA
        self.forward["tasks"] = []
        self.flush()
        with self.assertRaisesRegex(ValueError, "runnable tasks"):
            canonical_queue(self.source, self.root)

    def test_mismatched_amendment_and_decision_refused(self):
        self.current["routing_amendment"]["source_queue_commit"] = "0" * 40
        self.flush()
        with self.assertRaisesRegex(ValueError, "amendment mismatch"):
            canonical_queue(self.source, self.root)
        self.current["routing_amendment"]["source_queue_commit"] = self.forward["source_commit"]
        self.decision["coordinator_decision"]["decided_by"] = "executor"
        self.flush()
        with self.assertRaisesRegex(ValueError, "authority mismatch"):
            canonical_queue(self.source, self.root)

    def test_valid_reference_still_runs_normal_dispatch_validation(self):
        result = subprocess.run(["python3", str(Path(__file__).with_name("validate_dispatch_reference.py")),
                                 str(self.source), "--repo-root", str(self.root),
                                 "--output", str(self.root / "plan.json"),
                                 "--report", str(self.root / "plan.md")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("dispatch error:", result.stderr)
        self.assertFalse((self.root / "plan.json").exists())


class ArchivedRefusalTests(unittest.TestCase):
    def setUp(self):
        from test_research_dispatch import completed_archive_queue

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")
        self.git("commit", "--allow-empty", "-qm", "fixture parent")
        parent = self.git("rev-parse", "HEAD").strip()
        completed, contents, archive = completed_archive_queue()
        completed["goal_id"] = "GOAL-TEST-001"
        for path, data in contents.items():
            output = self.root / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
        self.git("add", ".")
        self.git("commit", "-qm", "ARCHIVE REC-ARCHIVE WORK")
        archive["archive"].update(commit_sha=self.git("rev-parse", "HEAD").strip(), parent_sha=parent)
        preservation = copy.deepcopy(completed)
        preservation["tasks"][1]["state"] = "queued"
        preservation["tasks"][1]["archive"].update(commit_sha=None, parent_sha=None, path_sha256={})
        original = copy.deepcopy(preservation)
        original["tasks"][0]["state"] = "failed"
        original["tasks"][1]["artifact_paths"].append(original["tasks"][0]["artifact_paths"][0])
        original["tasks"][1]["write_scope"] += original["tasks"][0]["write_scope"]
        self.queue = self.root / "coordination/rejected/dispatch_queue.json"
        self.expected = "artifact path coordination/tasks/WORK/report.json is owned by both WORK and ARCHIVE"
        self.documents = {
            "queue": (self.queue.relative_to(self.root).as_posix(), original),
            "refusal": ("coordination/rejected/refusal.json", {
                "schema": "crypto.autoresearch.native_archive_refusal.v1",
                "queue": self.queue.relative_to(self.root).as_posix(),
                "native_gate": "tools.research_dispatch.validate_queue", "exception": "DispatchError",
                "detail": self.expected, "archive_created": False}),
            "preservation_queue": ("coordination/rejected/preservation.json", preservation),
            "preservation_receipt": ("coordination/rejected/receipt.json", {
                "schema": "crypto.autoresearch.partial_output_preservation_receipt.v1",
                "preservation_queue": completed, "original_executor_task_state": "failed",
                "original_run_status": "infrastructure_error", "scientific_driver_started": False,
                "original_declared_missing_files_preserved_as_absent": True}),
        }
        self.registry = {"schema": "archived-queue-refusals-v1", "entries": [{
            "expected_native_error": self.expected, "execution_authorized": False}]}
        self.flush()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), "-c", "gc.auto=0",
            "-c", "maintenance.auto=false", "-c", "core.hooksPath=/dev/null",
            "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", *args], text=True)

    def flush(self):
        for key, (relative, document) in self.documents.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(document) + "\n")
            self.registry["entries"][0][key] = {
                "path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        path = self.root / "tools/archived_queue_refusals.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.registry))

    def test_exact_refusal_and_real_git_preservation_pass_without_admission(self):
        import research_dispatch

        result = archived_refusal(self.queue, self.root)
        self.assertTrue(result["expected_refusal_reproduced"])
        self.assertTrue(result["preservation_native_verified"])
        self.assertFalse(result["queue_admitted"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(canonical_queue(self.queue, self.root), self.queue)
        with self.assertRaisesRegex(research_dispatch.DispatchError, "owned by both"):
            research_dispatch.validate_queue(json.loads(self.queue.read_text()))

    def test_every_bound_input_hash_is_required(self):
        for key in self.documents:
            with self.subTest(key=key):
                self.flush()
                path = self.root / self.documents[key][0]
                path.write_bytes(path.read_bytes() + b"\n")
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    archived_refusal(self.queue, self.root)

    def test_unexpected_acceptance_is_refused(self):
        original = self.documents["queue"][1]
        original["tasks"][0]["state"] = "completed"
        original["tasks"][1]["artifact_paths"].pop()
        self.flush()
        with self.assertRaisesRegex(ValueError, "unexpectedly admitted"):
            archived_refusal(self.queue, self.root)

    def test_different_native_error_is_refused(self):
        self.documents["queue"][1]["tasks"][0]["role"] = "unknown"
        self.flush()
        with self.assertRaisesRegex(ValueError, "unexpected native refusal"):
            archived_refusal(self.queue, self.root)

    def test_invalid_preservation_and_false_success_are_refused(self):
        self.documents["preservation_receipt"][1]["original_run_status"] = "output_validated"
        self.flush()
        with self.assertRaisesRegex(ValueError, "failed-run boundary"):
            archived_refusal(self.queue, self.root)
        self.documents["preservation_receipt"][1]["original_run_status"] = "infrastructure_error"
        self.documents["preservation_queue"][1]["max_concurrent"] = 0
        self.flush()
        with self.assertRaisesRegex(ValueError, "max_concurrent"):
            archived_refusal(self.queue, self.root)

    def test_completed_archive_requires_real_git_parent_and_current_bytes(self):
        receipt = self.documents["preservation_receipt"][1]
        receipt["preservation_queue"]["tasks"][1]["archive"]["parent_sha"] = "f" * 40
        self.flush()
        with self.assertRaisesRegex(ValueError, "parent"):
            archived_refusal(self.queue, self.root)

    def test_current_preserved_bytes_cannot_drift(self):
        (self.root / "coordination/tasks/WORK/report.json").write_text("changed")
        with self.assertRaisesRegex(ValueError, "working bytes differ"):
            archived_refusal(self.queue, self.root)

    def test_preservation_completion_cannot_change_other_semantics(self):
        self.documents["preservation_receipt"][1]["preservation_queue"]["objective"] = "different"
        self.flush()
        with self.assertRaisesRegex(ValueError, "exact archived queue completion"):
            archived_refusal(self.queue, self.root)

    def test_unregistered_paths_are_not_classified(self):
        self.assertIsNone(archived_refusal(self.root / "coordination/other.json", self.root))

    def test_ci_receipt_is_not_a_plan_and_dispatcher_still_refuses(self):
        output, report = self.root / "ci.json", self.root / "ci.md"
        script = Path(__file__).with_name("validate_dispatch_reference.py")
        result = subprocess.run([sys.executable, str(script), str(self.queue),
            "--repo-root", str(self.root), "--output", str(output), "--report", str(report)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(output.read_text())
        self.assertFalse(receipt["queue_admitted"])
        self.assertNotIn("dispatches", receipt)
        result = subprocess.run([sys.executable, str(script.with_name("research_dispatch.py")),
            str(self.queue), "--repo-root", str(self.root),
            "--output", str(self.root / "dispatch.json"), "--report", str(self.root / "dispatch.md")],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(self.expected, result.stderr)
        self.assertFalse((self.root / "dispatch.json").exists())

    def test_registry_cannot_duplicate_a_path_or_authorize_execution(self):
        self.registry["entries"][0]["execution_authorized"] = True
        self.flush()
        with self.assertRaisesRegex(ValueError, "cannot authorize execution"):
            archived_refusal(self.queue, self.root)
        self.registry["entries"][0]["execution_authorized"] = False
        self.registry["entries"].append(copy.deepcopy(self.registry["entries"][0]))
        self.flush()
        with self.assertRaisesRegex(ValueError, "duplicate archived-refusal path"):
            archived_refusal(self.queue, self.root)

    def test_unsafe_bindings_are_refused(self):
        self.registry["entries"][0]["refusal"]["path"] = "../outside.json"
        (self.root / "tools/archived_queue_refusals.json").write_text(json.dumps(self.registry))
        with self.assertRaisesRegex(ValueError, "unsafe relative path"):
            archived_refusal(self.queue, self.root)


if __name__ == "__main__":
    unittest.main()

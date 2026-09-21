"""Forwarding integrity checks must not bypass normal queue validation."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from validate_dispatch_reference import canonical_queue, FORWARD_SCHEMA, QUEUE_SCHEMA


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
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

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


if __name__ == "__main__":
    unittest.main()

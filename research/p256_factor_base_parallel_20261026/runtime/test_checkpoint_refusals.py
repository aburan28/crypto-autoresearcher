"""Software-fixture checks only; no actual checkpoint or experiment is run."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name("checkpoint_gate.py")
spec = importlib.util.spec_from_file_location("pass2_checkpoint_gate", SOURCE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CheckpointRefusals(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p256-gate-software-")
        self.root = Path(self.temporary.name)
        self.release_path = self.root / "release.json"
        self.protocol = {"schema": "software-fixture", "question": "No mathematical data"}
        raw = json.dumps(self.protocol, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode()
        self.sha = hashlib.sha256(raw).hexdigest()
        self.protocol["freeze"] = {"status": "frozen", "protocol_sha256": self.sha,
                                   "filed_before_affected_data": True}
        self.release = {"execution_authorized": True, "checkpoint_gate_passed": True,
                        "task": "SOFTWARE-FIXTURE", "protocol_sha256": self.sha}
        self.addCleanup(self.temporary.cleanup)

    def refused(self, message):
        self.release_path.write_text(json.dumps(self.release))
        with patch.object(gate.subprocess, "run") as process:
            with self.assertRaisesRegex(RuntimeError, message):
                gate.require_gate(self.root, self.release_path, self.protocol, "SOFTWARE-FIXTURE")
            process.assert_not_called()
        self.assertFalse((self.root / ".resume").exists())

    def test_absent_release_cannot_start_a_process(self):
        with patch.object(gate.subprocess, "run") as process:
            with self.assertRaises(FileNotFoundError):
                gate.require_gate(self.root, self.release_path, self.protocol, "SOFTWARE-FIXTURE")
            process.assert_not_called()

    def test_unreleased_execution_is_refused(self):
        self.release["execution_authorized"] = False
        self.refused("not released")

    def test_missing_prior_checkpoint_is_refused(self):
        self.release["checkpoint_gate_passed"] = False
        self.refused("prior successful real S3 gate")

    def test_wrong_task_is_refused(self):
        self.release["task"] = "ANOTHER-TASK"
        self.refused("another task")

    def test_post_data_freeze_is_refused(self):
        self.protocol["freeze"]["filed_before_affected_data"] = False
        self.refused("before affected data")

    def test_changed_protocol_bytes_are_refused(self):
        self.protocol["question"] = "Tampered software-fixture metadata"
        self.refused("canonical hash")

    def test_wrong_release_hash_is_refused(self):
        self.release["protocol_sha256"] = "0" * 64
        self.refused("does not match")


if __name__ == "__main__":
    unittest.main()

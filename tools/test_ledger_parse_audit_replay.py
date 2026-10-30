"""CLI regressions for immutable audit output, using an isolated Git fixture.

The fixture gate supplies only a legacy classification. These controls test
replay output custody, not production ledger validity or semantic fidelity.
"""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "docs/reports/"
          "2026-10-26-ledger-parse-audit/audit.py")


class ReplayOutputCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / "docs/reports/audit/audit.py"
        self.script.parent.mkdir(parents=True)
        self.script.write_bytes(SCRIPT.read_bytes())
        self.evidence = self.script.with_name("evidence.json")
        self.historical = b'{"source_commit":"historical","counts":{"legacy":15}}\n'
        self.evidence.write_bytes(self.historical)
        (self.root / "ledger").mkdir()
        (self.root / "ledger/legacy.yaml").write_text("record: [\n")
        (self.root / "tools").mkdir()
        (self.root / "tools/__init__.py").touch()
        (self.root / "tools/check_merge_hygiene.py").write_text(
            "def _baseline(): return {'ledger/legacy.yaml'}\n"
            "def _retired_by_supersession(): return {}\n")
        (self.root / "tools/schema_supersession_registry.yaml").write_text(
            "schema: schema-supersession-registry-v1\nrecords: []\n")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("-c", "user.name=Replay control", "-c",
                 "user.email=replay-control@example.invalid", "commit", "--quiet",
                 "-m", "Freeze isolated custody fixture")
        self.head = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def run_audit(self, *args):
        return subprocess.run([sys.executable, str(self.script), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True)

    def assert_history_preserved(self):
        self.assertEqual(self.evidence.read_bytes(), self.historical)
        self.assertEqual(self.git("diff", "--exit-code"), "")

    def test_default_replay_does_not_change_committed_evidence(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_history_preserved()
        replay = json.loads(result.stdout)
        self.assertEqual(replay["source_commit"], self.head)
        self.assertEqual(replay["counts"]["legacy_parse_baseline"], 1)
        self.assertEqual(replay["malformed_originals"][0]["original_sha256"],
                         hashlib.sha256(b"record: [\n").hexdigest())

    def test_explicit_new_output_records_current_head_separately(self):
        output = self.root / "new-replay.json"
        result = self.run_audit("--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text())["source_commit"], self.head)
        self.assert_history_preserved()

    def test_existing_output_is_never_truncated(self):
        output = self.root / "previous-replay.json"
        original = b"an earlier result must survive\n"
        output.write_bytes(original)
        result = self.run_audit("--output", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), original)
        self.assert_history_preserved()

    def test_reserved_evidence_path_cannot_be_recreated(self):
        self.evidence.unlink()
        result = self.run_audit("--output", self.evidence)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.evidence.exists())

    def test_symlink_cannot_overwrite_historical_evidence(self):
        output = self.root / "evidence-alias.json"
        output.symlink_to(self.evidence)
        result = self.run_audit("--output", output)
        self.assertNotEqual(result.returncode, 0)
        self.assert_history_preserved()


if __name__ == "__main__":
    unittest.main()

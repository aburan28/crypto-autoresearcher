"""Verify source custody, date filtering and malformed-data behavior.

The data below are software fixtures, not research observations.
"""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("progress_metrics", REPO / "tools/progress_metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
SOURCE = "research/p256_factor_base_parallel_20261025/status.json"


class ExportIntegrity(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="p256-metrics-fixture-")
        self.repo = Path(self.directory.name)
        self.previous_repo = metrics.REPO
        metrics.REPO = self.repo
        self.git("init", "-q")
        self.git("config", "user.name", "Software fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.data = {"date": "2026-10-25", "tracks": [
            {"id": f"F{i}", "implementation_status": "complete" if i <= 4 else "pending"}
            for i in range(1, 9)]}

    def tearDown(self):
        metrics.REPO = self.previous_repo
        self.directory.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def commit(self, data):
        target = self.repo / SOURCE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data))
        self.git("add", SOURCE)
        self.git("commit", "-qm", "software fixture")
        return self.git("rev-parse", "HEAD")

    def output(self, ref, since="2026-10-01"):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            metrics.p256_factor_base_checks(ref, since)
        return [json.loads(x) for x in buffer.getvalue().splitlines()]

    def test_dirty_source_cannot_change_committed_sample(self):
        ref = self.commit(self.data)
        changed = copy.deepcopy(self.data)
        changed["tracks"] = []
        (self.repo / SOURCE).write_text(json.dumps(changed))
        result = self.output(ref)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["value"], 4)
        self.assertIn(ref, result[0]["source"])

    def test_absent_source_is_not_a_zero(self):
        self.git("commit", "--allow-empty", "-qm", "empty fixture")
        self.assertEqual(self.output("HEAD"), [])

    def test_old_source_is_filtered(self):
        self.assertEqual(self.output(self.commit(self.data), "2026-10-26"), [])

    def test_duplicate_or_unhashable_ids_are_rejected(self):
        for bad_id in ("F1", ["F2"]):
            with self.subTest(bad_id=bad_id):
                record = copy.deepcopy(self.data)
                record["tracks"][1]["id"] = bad_id
                self.assertEqual(self.output(self.commit(record)), [])

    def test_invalid_status_does_not_become_zero(self):
        record = copy.deepcopy(self.data)
        record["tracks"][0]["implementation_status"] = ["complete"]
        self.assertEqual(self.output(self.commit(record)), [])


if __name__ == "__main__":
    unittest.main()

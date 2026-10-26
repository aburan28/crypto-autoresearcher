"""Software fixtures test committed custody and refusal of malformed metadata."""
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
spec = importlib.util.spec_from_file_location("pass2_progress_metrics", REPO / "tools/progress_metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
SOURCE = "research/p256_factor_base_parallel_20261026/status.json"


class ExportCustody(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="p256-pass2-metadata-fixture-")
        self.repo = Path(self.temporary.name)
        self.previous = metrics.REPO
        metrics.REPO = self.repo
        self.git("init", "-q")
        self.git("config", "user.name", "Software fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.data = {"date": "2026-10-26", "tracks": [
            {"id": f"F{i}", "phase_a_status":
             "partial_source_preserved_after_platform_halt" if i == 1 else
             "source_and_draft_prepared_unexecuted" if i < 6 else "pending"}
            for i in range(1, 9)]}

    def tearDown(self):
        metrics.REPO = self.previous
        self.temporary.cleanup()

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
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            metrics.p256_factor_base_pass2_preparation(ref, since)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_partial_and_dirty_sources_cannot_inflate_readiness(self):
        commit = self.commit(self.data)
        dirty = copy.deepcopy(self.data)
        for row in dirty["tracks"]:
            row["phase_a_status"] = "source_and_draft_prepared_unexecuted"
        (self.repo / SOURCE).write_text(json.dumps(dirty))
        result = self.output(commit)
        self.assertEqual(result[0]["value"], 4)
        self.assertIn(commit, result[0]["source"])
        self.assertEqual(result[0]["better"], "neutral")

    def test_missing_source_is_absent_rather_than_zero(self):
        self.git("commit", "--allow-empty", "-qm", "empty fixture")
        self.assertEqual(self.output("HEAD"), [])

    def test_duplicate_unhashable_and_unknown_status_are_refused(self):
        for field, value in [("id", "F1"), ("id", ["F2"]),
                             ("phase_a_status", "complete_scientific_result")]:
            data = copy.deepcopy(self.data)
            data["tracks"][1][field] = value
            self.assertEqual(self.output(self.commit(data)), [])

    def test_date_filter_excludes_older_snapshot(self):
        self.assertEqual(self.output(self.commit(self.data), "2026-10-27"), [])


if __name__ == "__main__":
    unittest.main()

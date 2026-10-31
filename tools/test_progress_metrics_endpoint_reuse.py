"""Committed-state regression checks for descriptive endpoint-reuse counts."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("endpoint_progress_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
REPORT = "experiments/EXP-ECDLP-2b4ff1/reports/run-20261027T1934Z/data.json"


class EndpointReuseMetricsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Exporter fixture")
        (self.repo / "README").write_text("Synthetic exporter fixture; no research observations.\n")
        self.commit()
        self.patch = mock.patch.object(pm, "REPO", self.repo)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "synthetic fixture")
        return self.git("rev-parse", "HEAD")

    def document(self):
        return {"schema": "classical.ecdlp.descriptive-run-report-data/v1",
                "recorded_at": "2026-10-27T19:41:29+00:00", "run_id": "RUN-ECDLP-b883bf",
                "experiment_id": "EXP-ECDLP-2b4ff1", "flow": {"completed": 7},
                "verification": {"status": "public_equations_and_trace_pass", "public_fixtures": 2,
                                 "public_target_ids": 8, "verified_case_witnesses": 48}}

    def write(self, data):
        path = self.repo / REPORT
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def capture(self, ref, since="2026-10-01"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.endpoint_reuse_observations(ref, since)
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def test_counts_read_only_from_selected_commit_not_working_tree_or_newer_commit(self):
        data = self.document()
        self.write(data)
        old = self.commit()
        data["flow"]["completed"] = 999
        self.write(data)
        newer = self.commit()
        data["flow"]["completed"] = 1000
        self.write(data)
        old_rows = self.capture(old)
        self.assertEqual(len(old_rows), 4)
        old_child = next(r for r in old_rows if r["metric"] == "endpoint_reuse.b883bf.completed_children")
        self.assertEqual(old_child["value"], 7)
        self.assertTrue(all(r["source"].endswith("@" + old) and r["better"] == "neutral" for r in old_rows))
        newer_child = next(r for r in self.capture(newer) if r["metric"] == old_child["metric"])
        self.assertEqual(newer_child["value"], 999)
        self.assertEqual(self.capture(old, since="2026-10-28"), [])

    def test_missing_uncommitted_or_invalid_sources_emit_no_invented_counts(self):
        empty = self.git("rev-parse", "HEAD")
        self.assertEqual(self.capture(empty), [])
        self.write(self.document())
        self.assertEqual(self.capture(empty), [])
        for invalid in (None, True, -1, "48"):
            data = self.document()
            data["verification"]["verified_case_witnesses"] = invalid
            self.write(data)
            self.assertEqual(self.capture(self.commit()), [])


if __name__ == "__main__":
    unittest.main()

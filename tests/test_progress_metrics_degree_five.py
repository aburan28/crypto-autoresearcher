"""Committed snapshots, capped work and malformed-source refusal; no trials."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("degree_five_metrics", ROOT / "tools/progress_metrics.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
PREFIX = "analysis/semaev-degree-five-quotient-lift/reports/"


class DegreeFiveMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("-c", "user.name=test", "-c", "user.email=test@example.invalid",
                 "commit", "--allow-empty", "-qm", "baseline")
        self.empty = self.git("rev-parse", "HEAD").strip()
        self.document = dict(created_at="2026-10-30T01:00:00+00:00", planned=2, terminal=1,
                             missing_publications=[], statuses=dict(resource_capped=1, pending=1),
                             rows=[dict(id="capped", status="resource_capped", stages=[dict(
                                 degree=4, certified_codimension=12, exact_solutions=0,
                                 certificate_sha256="a" * 64)]),
                                   dict(id="pending", status="pending", stages=[])])

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def commit(self, document, number="001"):
        path = PREFIX + f"highmem-progress-{number}/progress.json"
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document))
        self.git("add", path)
        self.git("-c", "user.name=test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "snapshot")
        return self.git("rev-parse", "HEAD").strip(), path

    def rows(self, ref, since="2026-10-30"):
        out = io.StringIO()
        with patch.object(M, "REPO", self.root), contextlib.redirect_stdout(out):
            M.degree_five_continuation(ref, since)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_cap_is_terminal_and_partial_stage_is_not_a_completed_certificate_input(self):
        ref, path = self.commit(self.document)
        rows = self.rows(ref)
        values = {r["metric"].removeprefix("semaev.degree_five.highmem."): r["value"] for r in rows}
        self.assertEqual(values, dict(terminal_inputs=1, resource_capped_inputs=1, pending_inputs=1,
                                     certificate_verified_inputs=0, projection_kills_one_inputs=0,
                                     degree4_certificate_records=1, degree5_certificate_records=0))
        self.assertTrue(all(r["better"] == "neutral" and r["date"] == "2026-10-30"
                            and r["source"] == f"{path}@{ref}" for r in rows))

    def test_latest_snapshot_per_day_and_pinned_commit_ignore_dirty_or_later_work(self):
        first, path = self.commit(self.document)
        expected = self.rows(first)
        changed = copy.deepcopy(self.document)
        changed["created_at"] = "2026-10-30T02:00:00+00:00"
        changed["rows"][1]["status"] = "projection_kills_one"
        changed["terminal"] = 2
        changed["statuses"] = dict(resource_capped=1, projection_kills_one=1)
        latest, latest_path = self.commit(changed, "002")
        (self.root / path).write_text("dirty invalid JSON")
        self.assertEqual(self.rows(first), expected)
        rows = self.rows(latest)
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(r["source"] == f"{latest_path}@{latest}" for r in rows))
        self.assertEqual(next(r["value"] for r in rows if r["metric"].endswith("terminal_inputs")), 2)

    def test_inconsistent_latest_counts_or_unbound_stages_do_not_fall_back(self):
        for mutate in (lambda d: d.update(terminal=2),
                       lambda d: d.update(terminal=True),
                       lambda d: d["rows"][0]["stages"][0].update(certificate_sha256="missing"),
                       lambda d: d.update(missing_publications=["not published"]),
                       lambda d: d["rows"][1].update(id="capped")):
            with self.subTest(mutate=mutate):
                invalid = copy.deepcopy(self.document)
                mutate(invalid)
                ref, _ = self.commit(invalid)
                self.assertEqual(self.rows(ref), [])

    def test_distinct_days_retain_separate_observations(self):
        older = copy.deepcopy(self.document)
        older["created_at"] = "2026-10-29T23:00:00+00:00"
        self.commit(older)
        ref, _ = self.commit(self.document, "002")
        rows = self.rows(ref, "2026-10-29")
        self.assertEqual(len(rows), 14)
        self.assertEqual({r["date"] for r in rows}, {"2026-10-29", "2026-10-30"})

    def test_no_missing_source_or_future_day_is_inferred_as_zero(self):
        ref, _ = self.commit(self.document)
        self.assertEqual(self.rows(self.empty), [])
        self.assertEqual(self.rows(ref, "2026-10-31"), [])


if __name__ == "__main__":
    unittest.main()

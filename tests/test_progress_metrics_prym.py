"""Committed-source regression tests; no curve arithmetic or scientific runs."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prym_progress_metrics", REPO / "tools/progress_metrics.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
SOURCE = "experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/verification.json"


class CommittedPrymMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("-c", "user.name=test", "-c", "user.email=test@example.invalid",
                 "commit", "--allow-empty", "-qm", "empty baseline")
        self.empty = self.git("rev-parse", "HEAD").strip()
        self.cell = dict(curve_uid="a"*64, seed=0, arm="full3584", U=7,
                         rank=0, rows_verified=0, attempts_replayed=229376)
        self.document = dict(schema="prym-rank-census-independent/v1", status="passed",
                             failed_checks=[], cells=[self.cell])

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def commit(self, document):
        source = getattr(self, "source", SOURCE)
        path = self.root / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document))
        self.git("add", source)
        self.git("-c", "user.name=test", "-c", "user.email=test@example.invalid", "commit", "-qm", "source")
        return self.git("rev-parse", "HEAD").strip()

    def rows(self, ref):
        out = io.StringIO()
        with patch.object(M, "REPO", self.root), contextlib.redirect_stdout(out):
            getattr(self, "exporter", M.prym_census)(ref)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_committed_counts_are_neutral_with_exact_provenance(self):
        ref = self.commit(self.document)
        rows = self.rows(ref)
        self.assertEqual(len(rows), 4)
        prefix = f"prym.census.ea49a6.{'a'*64}.s0.full3584."
        self.assertEqual({row["metric"]: row["value"] for row in rows},
                         {prefix+"attempts": 229376, prefix+"accepted_rows": 0,
                          prefix+"rank": 0, prefix+"unknown_columns": 7})
        self.assertTrue(all(row["source"] == f"{SOURCE}@{ref}" and row["better"] == "neutral"
                            and row["kind"] == "gauge" for row in rows))

    def test_dirty_worktree_and_untracked_plans_are_ignored(self):
        ref = self.commit(self.document)
        original = self.rows(ref)
        (self.root / SOURCE).write_text("invalid dirty JSON")
        plan = self.root / "experiments/EXP-ECDLP-a9b6a5/protocol.json"
        plan.parent.mkdir(parents=True)
        plan.write_text('{"planned_attempts":4587520,"rank":15}')
        self.assertEqual(self.rows(ref), original)

    def test_missing_committed_source_emits_nothing(self):
        self.commit(self.document)
        self.assertEqual(self.rows(self.empty), [])

    def test_invalid_committed_source_emits_nothing(self):
        for change in (lambda d: d.update(status="failed"),
                       lambda d: d["cells"][0].update(rank=True),
                       lambda d: d["cells"][0].update(rank=8),
                       lambda d: d["cells"].append(copy.deepcopy(d["cells"][0]))):
            with self.subTest(change=change):
                document = copy.deepcopy(self.document)
                change(document)
                self.assertEqual(self.rows(self.commit(document)), [])

    def test_selected_ref_stays_pinned_when_branch_advances(self):
        first = self.commit(self.document)
        with patch.object(M, "REPO", self.root), patch.object(sys, "argv", ["progress_metrics", "--ref", "HEAD"]):
            arguments = M.args()
        self.assertEqual(arguments.ref, first)
        changed = copy.deepcopy(self.document)
        changed["cells"][0]["rows_verified"] = 4
        self.commit(changed)
        observed = {row["metric"].rsplit(".", 1)[-1]: row["value"] for row in self.rows(arguments.ref)}
        self.assertEqual(observed["accepted_rows"], 0)


class CommittedWidthMetricsTests(CommittedPrymMetricsTests):
    def setUp(self):
        super().setUp()
        self.source = "experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/verification.json"
        self.exporter = M.prym_width
        self.cell = dict(curve_uid="b"*64, U=15, rank=13, rows_verified=97,
                         attempts_replayed=2293760)
        self.document = dict(schema="prym-width-independent/v1", status="passed",
                             failed_checks=[], cells=[self.cell])

    def test_committed_counts_are_neutral_with_exact_provenance(self):
        ref = self.commit(self.document)
        rows = self.rows(ref)
        prefix = f"prym.width.967315.{'b'*64}.m16_full35840."
        self.assertEqual({row["metric"]: row["value"] for row in rows},
                         {prefix+"attempts": 2293760, prefix+"accepted_rows": 97,
                          prefix+"rank": 13, prefix+"unknown_columns": 15})
        self.assertTrue(all(row["source"] == f"{self.source}@{ref}" and row["better"] == "neutral"
                            and row["kind"] == "gauge" for row in rows))

    def test_dirty_worktree_and_untracked_plans_are_ignored(self):
        ref = self.commit(self.document)
        original = self.rows(ref)
        (self.root/self.source).write_text("invalid dirty JSON")
        plan = self.root/"experiments/planned/protocol.json"
        plan.parent.mkdir(parents=True)
        plan.write_text('{"attempts":999,"rank":15}')
        self.assertEqual(self.rows(ref), original)

    def test_invalid_committed_source_emits_nothing(self):
        for change in (lambda d: d.update(status="failed"),
                       lambda d: d["cells"][0].update(rank=True),
                       lambda d: d["cells"][0].update(rank=16),
                       lambda d: d["cells"][0].update(rows_verified=2293761),
                       lambda d: d["cells"].append(copy.deepcopy(d["cells"][0]))):
            with self.subTest(change=change):
                document = copy.deepcopy(self.document)
                change(document)
                self.assertEqual(self.rows(self.commit(document)), [])

    def test_selected_ref_stays_pinned_when_branch_advances(self):
        first = self.commit(self.document)
        with patch.object(M, "REPO", self.root), patch.object(sys, "argv", ["progress_metrics", "--ref", "HEAD"]):
            arguments = M.args()
        changed = copy.deepcopy(self.document)
        changed["cells"][0]["rows_verified"] = 98
        self.commit(changed)
        self.assertEqual(arguments.ref, first)
        observed = {row["metric"].rsplit(".", 1)[-1]: row["value"] for row in self.rows(arguments.ref)}
        self.assertEqual(observed["accepted_rows"], 97)


if __name__ == "__main__":
    unittest.main()

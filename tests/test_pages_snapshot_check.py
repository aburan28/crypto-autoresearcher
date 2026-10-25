"""Source-binding controls for the report checker, using a synthetic snapshot."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = (Path(__file__).resolve().parents[1] / "docs/reports/"
           "2026-10-23-pages-publication-preflight/check_snapshot.py")
PRIMARY = "experiments/ic-bench/baseline/primary.jsonl"
BUNDLE = "ui/benchmarks/cryptanalysis-primary.json"


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", str(repo), "-c", "user.name=Snapshot test",
         "-c", "user.email=snapshot@example.invalid", *args],
        stderr=subprocess.DEVNULL).decode().strip()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class SnapshotSourceBinding(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.repo, self.source, self.site = [root / name for name in ("repo", "source", "site")]
        for repo in (self.repo, self.source):
            repo.mkdir()
            git(repo, "init", "-q")
        primary, rows, receipts = [], [], []
        for i in range(9):
            base = dict(run_id=f"run-{i}", candidate_id=f"candidate-{i}",
                        workload_id=f"workload-{i}", status="complete",
                        total_operations=100 + i, wall_ns=1000 + i, operation_unit="count")
            online = dict(ic_online_ns=100 + i, rho_online_ns=200 + i)
            primary.append(dict(base, online=online, counts={"targets_verified": 1}))
            row = dict(base, **online, targets_verified=1, curve_uid=f"curve-{i}",
                       curve_id=f"curve-{i}", scope="archived receipt",
                       online_boundary="recorded interval", sources=[PRIMARY], source_line=i + 1)
            rows.append(row)
        raw = "".join(json.dumps(row) + "\n" for row in primary).encode()
        source_path = self.source / PRIMARY
        source_path.parent.mkdir(parents=True)
        source_path.write_bytes(raw)
        git(self.source, "add", ".")
        git(self.source, "commit", "-qm", "Pin primary fixture")
        pin = {"path": PRIMARY, "sha256": hashlib.sha256(raw).hexdigest()}
        self.bundle = dict(source_commit=git(self.source, "rev-parse", "HEAD"),
                           source_repository="fixture/source", sources={PRIMARY: pin}, rows=rows)
        write_json(self.repo / BUNDLE, self.bundle)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "Pin bundle fixture")
        git(self.repo, "commit", "--allow-empty", "-qm", "Complete fixture history")
        self.head = git(self.repo, "rev-parse", "HEAD")
        for row in rows:
            receipt = {key: row[key] for key in (
                "candidate_id", "workload_id", "curve_uid", "curve_id",
                "operation_unit", "status", "scope")}
            receipt["metrics"] = {key: row[key] for key in (
                "total_operations", "ic_online_ns", "rho_online_ns", "targets_verified")}
            receipt["metrics"]["total_wall_seconds"] = row["wall_ns"] / 1e9
            receipt.update(timing_boundary=row["online_boundary"], sources={"primary": pin})
            receipts.append(receipt)
        self.comparisons = {"receipts": receipts}
        write_json(self.site / "data/comparisons.json", self.comparisons)
        write_json(self.site / "data/meta.json", dict(
            commit=self.head, records=100, built_at="fixture",
            git=dict(available=True, paths=1, commits=2)))
        write_json(self.site / "data/integrity.json", dict(
            unparseable_state="complete", unparseable=[], duplicate_ids=[],
            id_path_mismatch=[], dangling_refs_total=0))
        self.report, self.out = root / "build.json", root / "checked.json"
        write_json(self.report, dict(commit=self.head, records=100, files=3, bytes=1000,
                                     unparseable=0))

    def check(self, optimize=False):
        return subprocess.run([sys.executable, *(["-O"] if optimize else []), str(CHECKER),
                               "--repo", str(self.repo), "--site", str(self.site),
                               "--source-repo", str(self.source), "--build-report", str(self.report),
                               "--out", str(self.out)], capture_output=True, text=True)

    def test_committed_snapshot_passes_and_names_bundle_digest(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(self.out.read_text())
        self.assertEqual(output["bundle_sha256"], hashlib.sha256((self.repo / BUNDLE).read_bytes()).hexdigest())

    def test_dirty_bundle_cannot_authorize_changed_display_scope(self):
        self.bundle["rows"][0]["scope"] = "uncommitted qualification"
        self.comparisons["receipts"][0]["scope"] = "uncommitted qualification"
        write_json(self.repo / BUNDLE, self.bundle)
        write_json(self.site / "data/comparisons.json", self.comparisons)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.head)
        self.assertNotEqual(self.check().returncode, 0)

    def test_changed_displayed_count_is_rejected(self):
        self.comparisons["receipts"][0]["metrics"]["total_operations"] += 1
        write_json(self.site / "data/comparisons.json", self.comparisons)
        self.assertNotEqual(self.check().returncode, 0)

    def test_optimized_python_is_rejected(self):
        self.assertNotEqual(self.check(optimize=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()

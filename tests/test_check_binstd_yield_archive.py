"""Failure controls for the archived BINSTD yield arithmetic checker."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.check_binstd_yield_archive import EXPERIMENT, PANELS, check_archive  # noqa: E402


class ArchiveChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        base = Path("experiments") / EXPERIMENT
        for run_id, tag, _ in PANELS:
            for rel in (
                base / "runs" / run_id / "raw-result.json",
                base / "runs" / run_id / "execution-receipt.json",
                base / f"stage1-{tag}" / "yield-matrix.json",
                base / f"stage1-{tag}" / "admissible-phi-dims.json",
            ):
                dest = self.root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)

    def paths(self) -> tuple[Path, Path, Path]:
        base = self.root / "experiments" / EXPERIMENT
        return (base / "stage1-ell89" / "yield-matrix.json",
                base / "runs" / "RUN-BINSTD-43abd4" / "raw-result.json",
                base / "runs" / "RUN-BINSTD-43abd4" / "execution-receipt.json")

    @staticmethod
    def write(path: Path, data: dict) -> str:
        path.write_text(json.dumps(data, sort_keys=True) + "\n")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def resign_matrix_and_raw(self, matrix: dict) -> None:
        """Keep both digest links valid so a bad arithmetic field is reached."""
        matrix_path, raw_path, receipt_path = self.paths()
        matrix_hash = self.write(matrix_path, matrix)
        raw = json.loads(raw_path.read_text())
        raw["result"]["artifact_sha256"]["stage1/yield-matrix.json"] = matrix_hash
        raw_hash = self.write(raw_path, raw)
        receipt = json.loads(receipt_path.read_text())
        receipt["artifact_sha256"]["raw-result.json"] = raw_hash
        self.write(receipt_path, receipt)

    def test_committed_archive(self) -> None:
        result = check_archive(self.root)
        self.assertEqual(len(result["panels"]), 2)
        self.assertEqual([c["tau_hits"] for p in result["panels"] for c in p["cells"]],
                         [16, 40, 20, 40])

    def test_changed_matrix_rejected_by_digest(self) -> None:
        matrix_path, _, _ = self.paths()
        matrix = json.loads(matrix_path.read_text())
        matrix["cells"][0]["hits_tau"] = 17
        self.write(matrix_path, matrix)
        with self.assertRaisesRegex(ValueError, "yield matrix digest"):
            check_archive(self.root)

    def test_wrong_ratio_rejected_even_with_consistent_digests(self) -> None:
        matrix_path, _, _ = self.paths()
        matrix = json.loads(matrix_path.read_text())
        matrix["cells"][0]["ratio_tau_over_open"] = 0.5
        self.resign_matrix_and_raw(matrix)
        with self.assertRaisesRegex(ValueError, "ratio arithmetic"):
            check_archive(self.root)

    def test_wrong_hit_count_rejected_even_with_consistent_digests(self) -> None:
        matrix_path, _, _ = self.paths()
        matrix = json.loads(matrix_path.read_text())
        matrix["cells"][0]["hits_tau"] = 17
        self.resign_matrix_and_raw(matrix)
        with self.assertRaisesRegex(ValueError, "archived counts"):
            check_archive(self.root)

    def test_missing_source_rejected(self) -> None:
        matrix_path, _, _ = self.paths()
        matrix_path.unlink()
        with self.assertRaises(FileNotFoundError):
            check_archive(self.root)

    def test_boolean_exit_code_rejected(self) -> None:
        _, _, receipt_path = self.paths()
        receipt = json.loads(receipt_path.read_text())
        receipt["check_returncode"] = False
        self.write(receipt_path, receipt)
        with self.assertRaisesRegex(ValueError, "exit codes"):
            check_archive(self.root)

    def test_boolean_stage_rejected_with_consistent_digest(self) -> None:
        _, raw_path, receipt_path = self.paths()
        raw = json.loads(raw_path.read_text())
        raw["result"]["stage"] = True
        raw_hash = self.write(raw_path, raw)
        receipt = json.loads(receipt_path.read_text())
        receipt["artifact_sha256"]["raw-result.json"] = raw_hash
        self.write(receipt_path, receipt)
        with self.assertRaisesRegex(ValueError, "stage/status"):
            check_archive(self.root)


if __name__ == "__main__":
    unittest.main()

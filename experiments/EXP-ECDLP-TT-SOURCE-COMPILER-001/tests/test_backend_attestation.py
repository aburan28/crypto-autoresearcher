from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = EXPERIMENT_DIR / "src" / "attest_tt_backend.py"
MATRIX = EXPERIMENT_DIR / "source-execution-matrix-v2.json"
PYTHON = Path("/Library/Frameworks/Python.framework/Versions/3.13/bin/python3")


def pinned_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )
    return environment


def run_attestation(matrix: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [str(PYTHON), str(SCRIPT), "--source-execution-matrix", str(matrix)],
        check=False,
        capture_output=True,
        text=True,
        env=pinned_environment(),
    )
    return completed, json.loads(completed.stdout)


class BackendAttestationTests(unittest.TestCase):
    def test_frozen_backend_matches_complete_distribution_closure(self) -> None:
        completed, result = run_attestation(MATRIX)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(result["valid"])
        self.assertEqual(
            len(result["observed"]["numpy_distribution_members"]),
            1320,
        )
        self.assertTrue(all(check["match"] for check in result["checks"]))

    def test_same_version_with_changed_closure_identity_is_rejected(self) -> None:
        record = json.loads(MATRIX.read_text(encoding="utf-8"))
        record["source_execution_matrix"]["backend_gate"][
            "numpy_installed_closure_sha256"
        ] = "0" * 64

        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / MATRIX.name
            mutated.write_text(json.dumps(record), encoding="utf-8")
            completed, result = run_attestation(mutated)

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(result["valid"])
        checks = {check["field"]: check for check in result["checks"]}
        self.assertTrue(checks["numpy_version"]["match"])
        self.assertFalse(checks["numpy_installed_closure_sha256"]["match"])


if __name__ == "__main__":
    unittest.main()

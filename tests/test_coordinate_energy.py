from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
EXPERIMENT = REPO_ROOT / "experiments" / "EXP-ECDLP-ENERGY-001" / "src"


class CoordinateEnergyTests(unittest.TestCase):
    def test_tiny_generator_and_independent_verifier(self) -> None:
        generator = subprocess.run(
            [
                sys.executable,
                str(EXPERIMENT / "coordinate_energy.py"),
                "--bit-sizes",
                "11",
                "--seed",
                "41",
                "--targets",
                "8",
                "--rho-trials",
                "2",
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )
        document = json.loads(generator.stdout)
        self.assertTrue(document["valid"])
        self.assertEqual(document["summary"]["sizes_completed"], 1)
        with tempfile.TemporaryDirectory() as temporary:
            raw_path = Path(temporary) / "raw-result.json"
            raw_path.write_text(generator.stdout, encoding="utf-8")
            verifier = subprocess.run(
                [
                    sys.executable,
                    str(EXPERIMENT / "verify_coordinate_energy.py"),
                    "--input",
                    str(raw_path),
                ],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                check=True,
            )
            verified = json.loads(verifier.stdout)
            self.assertTrue(verified["valid"])
            self.assertTrue(verified["summary"]["integer_counts_verified"])


if __name__ == "__main__":
    unittest.main()

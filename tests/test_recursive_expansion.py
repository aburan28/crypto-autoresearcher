from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
SCRIPT = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)
VERIFIER = SCRIPT.with_name("verify_recursive_expansion.py")


class RecursiveExpansionTests(unittest.TestCase):
    def run_tiny(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                "--bit-sizes",
                "10",
                "--seeds",
                "73",
                "--m-values",
                "5",
                "--targets",
                "8",
                "--rho-trials",
                "1",
                "--occupancy-lambda",
                "0.5",
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )

    def test_tiny_sweep_is_deterministic_and_internally_consistent(self) -> None:
        first = self.run_tiny()
        second = self.run_tiny()
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stderr, "")
        self.assertEqual(first.stdout, second.stdout)
        document = json.loads(first.stdout)
        self.assertTrue(document["valid"])
        self.assertTrue(document["summary"]["all_curves_prime_order"])
        self.assertTrue(document["summary"]["all_rho_trials_verified"])
        self.assertFalse(document["summary"]["breakthrough_claim"])
        self.assertEqual(len(document["instances"]), 1)

        instance = document["instances"][0]
        q = instance["curve"]["q"]
        self.assertEqual(instance["curve"]["cofactor"], 1)
        self.assertEqual(len(instance["configurations"]), 12)
        for result in instance["configurations"]:
            size = result["size"]
            self.assertEqual(size % 2, 0)
            self.assertGreaterEqual(math.comb(size + 4, 5) / q, 0.5)
            if size > 2:
                self.assertLess(math.comb(size + 2, 5) / q, 0.5)
            self.assertEqual(result["support_sizes"][0], 1)
            self.assertTrue(
                all(
                    left <= right
                    for left, right in zip(
                        result["support_sizes"], result["support_sizes"][1:]
                    )
                )
            )
            iterate_size = min(result["compiler_support_sizes"].values())
            self.assertLessEqual(
                max(result["online_group_operations_distribution"]), iterate_size
            )
            if result["first_witness"] is not None:
                self.assertEqual(len(result["first_witness"]["indices"]), 5)

        with tempfile.TemporaryDirectory() as temporary:
            raw_path = Path(temporary) / "raw-result.json"
            raw_path.write_text(first.stdout, encoding="utf-8")
            verifier = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VERIFIER),
                    "--input",
                    str(raw_path),
                    "--allow-nonfrozen-test-config",
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
            self.assertEqual(
                verified["protocol"],
                "EXP-ECDLP-RECURSIVE-001-v2-independent-verifier",
            )
            self.assertEqual(verified["source"], document["source"])
            self.assertTrue(verified["summary"]["recursive_supports_rebuilt"])
            self.assertTrue(
                verified["summary"]["split_advice_and_first_witnesses_replayed"]
            )
            self.assertTrue(verified["summary"]["operation_counters_replayed"])
            self.assertTrue(verified["summary"]["rho_trials_replayed"])
            self.assertFalse(verified["summary"]["frozen_config_enforced"])
            self.assertFalse(verified["summary"]["breakthrough_claim"])

    def test_independent_verifier_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(VERIFIER), "--self-test"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["tests"]), 18)
        self.assertFalse(result["experiment_harness_executed"])


if __name__ == "__main__":
    unittest.main()

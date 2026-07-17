from __future__ import annotations

import hashlib
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
    / "EXP-ECDLP-RECURSIVE-002"
    / "src"
    / "null_calibrated_coverage.py"
)
VERIFIER = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-RECURSIVE-002"
    / "src"
    / "verify_null_calibrated_coverage.py"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_class_count(fiber_count: int, terms: int) -> int:
    total = 0
    for residue_terms in range(terms % 2, terms + 1, 2):
        if residue_terms == 0:
            total += 1
            continue
        for support_size in range(1, min(fiber_count, residue_terms) + 1):
            total += (
                math.comb(fiber_count, support_size)
                * math.comb(residue_terms - 1, support_size - 1)
                * 2**support_size
            )
    return total


class NullCalibratedCoverageTests(unittest.TestCase):
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
                "--null-replicates",
                "2",
                "--targets",
                "8",
                "--order-seeds",
                "11",
                "13",
                "--occupancy-lambda",
                "0.2",
                "--rho-trials",
                "1",
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )

    def run_verifier(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(VERIFIER), *arguments],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=True,
        )

    def test_tiny_sweep_is_deterministic_and_clean(self) -> None:
        first = self.run_tiny()
        second = self.run_tiny()
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stderr, "")
        self.assertEqual(first.stdout, second.stdout)
        document = json.loads(first.stdout)
        self.assertTrue(document["valid"])
        self.assertEqual(document["protocol"], "EXP-ECDLP-RECURSIVE-002-v1")
        self.assertFalse(document["summary"]["breakthrough_claim"])
        self.assertTrue(document["summary"]["all_curves_clean"])
        self.assertTrue(document["summary"]["all_positive_controls_passed"])
        self.assertTrue(document["summary"]["all_rho_trials_verified"])
        self.assertEqual(
            document["source"]["null_calibrated_coverage_sha256"],
            sha256_file(SCRIPT),
        )

        instance = document["instances"][0]
        curve = instance["curve"]
        self.assertNotIn(curve["trace"], (0, 1))
        self.assertNotIn(curve["j_invariant"], (0, 1728 % curve["p"]))
        self.assertEqual(curve["q"], curve["order"])
        self.assertEqual(curve["cofactor"], 1)
        self.assertEqual(set(instance["null_rows"]), {"random", "random_x"})
        self.assertTrue(
            all(len(rows) == 2 for rows in instance["null_rows"].values())
        )
        self.assertEqual(len(instance["candidate_rows"]), 3)

        for row in [
            *instance["null_rows"]["random"],
            *instance["null_rows"]["random_x"],
            *instance["candidate_rows"],
            instance["scalar_progression_control"],
        ]:
            self.assertEqual(len(row["order_results"]), 2)
            self.assertGreater(row["compiled_artifact_deep_bytes"], 0)
            self.assertGreater(row["functional_frontier_score"], 0)
            self.assertEqual(
                row["generic_signed_four_term_maximum"],
                signed_class_count(row["size"] // 2, 4),
            )
            self.assertLessEqual(
                row["four_term_support_size"],
                row["generic_signed_four_term_maximum"],
            )
            self.assertLessEqual(row["eight_term_support_size"], curve["q"])

        for row in instance["candidate_rows"]:
            self.assertEqual(set(row["null_percentiles"]), {"random", "random_x"})
            for percentiles in row["null_percentiles"].values():
                self.assertTrue(
                    all(0 <= value <= 1 for value in percentiles.values())
                )

    def test_independent_verifier_self_test(self) -> None:
        completed = self.run_verifier("--self-test")
        self.assertEqual(completed.stderr, "")
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertFalse(result["experiment_harness_executed"])
        self.assertEqual(len(result["tests"]), 14)
        self.assertEqual(
            result["source"]["null_calibrated_coverage_sha256"],
            sha256_file(SCRIPT),
        )
        self.assertIn("tiny_round_trip_exact", result["tests"])
        self.assertIn("duplicate_json_key_rejected", result["tests"])
        self.assertIn("nonfinite_json_rejected", result["tests"])

    def test_generator_document_passes_independent_verifier(self) -> None:
        generated = self.run_tiny()
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "raw-result.json"
            artifact.write_text(generated.stdout, encoding="utf-8")
            completed = self.run_verifier(
                "--input",
                str(artifact),
                "--allow-nonfrozen-test-config",
            )
        self.assertEqual(completed.stderr, "")
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(result["summary"]["instances_verified"], 1)
        self.assertFalse(result["summary"]["frozen_config_enforced"])
        self.assertTrue(result["summary"]["curve_orders_recomputed"])
        self.assertTrue(
            result["summary"][
                "four_and_eight_term_supports_orders_witnesses_percentiles_and_family_gate_replayed"
            ]
        )
        self.assertFalse(result["summary"]["breakthrough_claim"])


if __name__ == "__main__":
    unittest.main()

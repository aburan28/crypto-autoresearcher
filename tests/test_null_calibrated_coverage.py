from __future__ import annotations

import hashlib
import importlib.util
import itertools
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


def load_generator_module():
    spec = importlib.util.spec_from_file_location("null_calibrated_v2", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator_module()


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
        self.assertEqual(document["protocol"], "EXP-ECDLP-RECURSIVE-002-v2")
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
        self.assertEqual(document["summary"]["distinct_field_moduli"], 1)
        self.assertEqual(
            document["summary"]["globally_unique_factor_base_seeds"], 8
        )

        for row in [
            *instance["null_rows"]["random"],
            *instance["null_rows"]["random_x"],
            *instance["candidate_rows"],
            instance["scalar_progression_control"],
        ]:
            self.assertEqual(len(row["order_results"]), 2)
            self.assertGreater(row["compiled_artifact_deep_bytes"], 0)
            self.assertGreater(row["functional_frontier_score"], 0)
            self.assertTrue(row["order_control_passed"])
            self.assertEqual(len(row["target_order_expectations"]), 8)
            for expectation in row["target_order_expectations"]:
                expected = (
                    expectation["expected_first_hit_numerator"]
                    / expectation["expected_first_hit_denominator"]
                )
                self.assertEqual(
                    expectation["expected_first_hit_lookups"], expected
                )
                self.assertEqual(
                    expectation["exact_membership"],
                    expectation["successful_partials"] > 0,
                )
            self.assertGreater(
                row["offline_charged_cost"]["charged_field_multiplications"],
                0,
            )
            for order in row["order_results"]:
                self.assertEqual(len(order["per_target_lookups"]), 8)
                self.assertEqual(len(order["per_target_group_operations"]), 8)
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
            for ranks in row["null_rank_details"].values():
                self.assertTrue(
                    all(detail["finite_null_denominator"] == 3 for detail in ranks.values())
                )

        rows_by_name = {row["name"]: row for row in instance["candidate_rows"]}
        self.assertGreater(
            rows_by_name["square_map"]["build_diagnostics"][
                "map_field_multiplications"
            ],
            0,
        )
        self.assertGreater(
            rows_by_name["rational_union"]["build_diagnostics"][
                "map_field_inversions"
            ],
            0,
        )
        self.assertEqual(
            rows_by_name["x_interval"]["build_diagnostics"][
                "map_field_inversions"
            ],
            0,
        )

    def test_semantic_oracles_and_mandatory_controls(self) -> None:
        self.assertEqual(
            GENERATOR.empirical_percentile_detail(4, [1, 2, 3], True),
            {
                "percentile": 1.0,
                "favorable_null_count": 3,
                "tied_null_count": 0,
                "null_count": 3,
                "finite_null_denominator": 4,
                "higher_is_better": True,
            },
        )
        tied = GENERATOR.empirical_percentile_detail(2, [1, 2, 2, 3], True)
        self.assertEqual(tied["percentile"], 0.6)
        self.assertEqual(tied["tied_null_count"], 2)

        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 0, 0, 7), "singular"
        )
        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 1, 1, 12), "trace_zero"
        )
        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 1, 1, 11),
            "anomalous_trace_one",
        )
        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 1, 1, 8), "composite_order"
        )
        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 0, 1, 7), "special_j"
        )
        self.assertEqual(
            GENERATOR.curve_rejection_reason(11, 1, 0, 7), "special_j"
        )

        bit_sizes = [12, 14, 16]
        seeds = [1, 2, 3]
        instances = [
            {
                "seed": seed,
                "curve": {"bits": bits},
                "candidate_rows": [
                    {"name": "x_interval", "instance_gate_passed": True},
                    {"name": "square_map", "instance_gate_passed": False},
                    {"name": "rational_union", "instance_gate_passed": False},
                ],
            }
            for seed in seeds
            for bits in bit_sizes
        ]
        blocked = GENERATOR.aggregate_family_gate(
            instances,
            ["x_interval", "square_map", "rational_union"],
            bit_sizes,
            seeds,
            False,
        )
        self.assertEqual(blocked["family_pass_counts"]["x_interval"], 9)
        self.assertEqual(blocked["promoted_families"], [])
        allowed = GENERATOR.aggregate_family_gate(
            instances,
            ["x_interval", "square_map", "rational_union"],
            bit_sizes,
            seeds,
            True,
        )
        self.assertEqual(allowed["promoted_families"], ["x_interval"])

    def test_support_chain_matches_bruteforce_oracle(self) -> None:
        curve = GENERATOR.Curve(11, 1, 6)
        points = [(2, 4), (2, 7), (3, 5)]
        chain, _ = GENERATOR.PRIOR.support_chain(curve, points, 4)
        brute_force = set()
        for selection in itertools.product(points, repeat=4):
            total = None
            for point in selection:
                total = curve.add(total, point)
            brute_force.add(total)
        self.assertEqual(set(chain[4]), brute_force)

    def test_frozen_curve_schedule_uses_nine_distinct_fields(self) -> None:
        moduli = []
        for seed in (2473001, 2473004, 2473012):
            previous_q = 0
            for bits in (12, 14, 16):
                curve = GENERATOR.generate_clean_curve(bits, seed + bits * 1009)
                self.assertGreater(curve["q"], previous_q)
                previous_q = curve["q"]
                moduli.append(curve["p"])
        self.assertEqual(len(moduli), 9)
        self.assertEqual(len(set(moduli)), 9)

    def test_independent_verifier_self_test(self) -> None:
        completed = self.run_verifier("--self-test")
        self.assertEqual(completed.stderr, "")
        result = json.loads(completed.stdout)
        self.assertTrue(result["valid"])
        self.assertFalse(result["experiment_harness_executed"])
        self.assertEqual(len(result["tests"]), 14)
        self.assertEqual(result["mutation_cases_executed"], 51)
        self.assertEqual(
            result["frozen_schedule"],
            {
                "distinct_field_moduli": 9,
                "globally_unique_factor_base_seeds": 594,
                "instances": 9,
            },
        )
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

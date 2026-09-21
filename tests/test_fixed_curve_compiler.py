from __future__ import annotations

import copy
import inspect
import itertools
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
EXPERIMENT = REPO_ROOT / "experiments" / "EXP-ECDLP-FIXED-COMPILER-001"
GENERATOR_PATH = EXPERIMENT / "src" / "fixed_curve_compiler.py"
VERIFIER_PATH = EXPERIMENT / "src" / "verify_fixed_curve_compiler.py"
GENERATOR = runpy.run_path(str(GENERATOR_PATH))
VERIFIER = runpy.run_path(str(VERIFIER_PATH))
TEST_CONFIG = {
    "bit_sizes": [8],
    "seeds": [17],
    "families": ["random_x", "random_scalar", "x_interval", "scalar_progression"],
    "witness_caps": [1, 2],
    "occupancy_lambda": 0.5,
    "relations_per_target": 8,
    "relation_target_budget": 0,
    "descent_challenges": 2,
    "descent_attempt_limit": 32,
    "rho_trials": 1,
}


class FixedCurveCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = GENERATOR["run_experiment"](copy.deepcopy(TEST_CONFIG))
        cls.instance = cls.result["instances"][0]
        cls.rows = {
            (row["family"], row["witness_cap"]): row
            for row in cls.instance["rows"]
        }

    def test_development_document_replays_independently(self) -> None:
        certificate = VERIFIER["verify_document"](
            copy.deepcopy(self.result), enforce_frozen=False
        )
        self.assertEqual(certificate["status"], "verified")
        self.assertTrue(certificate["development_only"])
        self.assertEqual(certificate["verified_instances"], 1)
        self.assertEqual(certificate["verified_rows"], 8)

    def test_development_configuration_cannot_pass_canonical_verification(self) -> None:
        with self.assertRaises(AssertionError):
            VERIFIER["verify_document"](
                copy.deepcopy(self.result), enforce_frozen=True
            )

    def test_curve_and_global_controls_are_clean(self) -> None:
        curve = self.instance["curve"]
        self.assertNotIn(curve["trace"], (0, 1))
        self.assertNotIn(curve["j_invariant"], (0, 1728 % curve["p"]))
        self.assertEqual(curve["q"], curve["order"])
        self.assertEqual(curve["cofactor"], 1)
        self.assertIn("no selection on p-1 smoothness", curve["field_modulus_policy"])
        self.assertTrue(all(self.result["global_controls"].values()))

    def test_all_rows_share_target_schedule_and_descent_challenges(self) -> None:
        seeds = {row["target_schedule_seed"] for row in self.instance["rows"]}
        schedule_digests = {
            row["relations"]["target_schedule_sha256"]
            for row in self.instance["rows"]
        }
        challenge_scalars = {
            tuple(
                challenge["known_scalar_private_audit"]
                for challenge in row["descent"]["challenges"]
            )
            for row in self.instance["rows"]
            if row["descent"]["status"] == "completed"
        }
        self.assertEqual(len(seeds), 1)
        self.assertEqual(len(schedule_digests), 1)
        self.assertEqual(len(challenge_scalars), 1)

    def test_scalar_generation_metadata_is_not_emitted(self) -> None:
        forbidden = {"sampled_scalar", "canonical_scalar"}
        for row in self.instance["rows"]:
            with self.subTest(family=row["family"], cap=row["witness_cap"]):
                self.assertFalse(row["factor_base"]["scalar_source_metadata_emitted"])
                for fiber in row["factor_base"]["fibers"]:
                    self.assertTrue(forbidden.isdisjoint(fiber["source"]))
                self.assertEqual(row["factor_base"]["solver_input_fields"], ["points"])

    def test_four_sum_attempts_and_witness_caps_are_exact(self) -> None:
        size = self.instance["factor_base_size"]
        expected_attempts = GENERATOR["math"].comb(size + 3, 4)
        for family in TEST_CONFIG["families"]:
            one = self.rows[(family, 1)]["compiler"]
            two = self.rows[(family, 2)]["compiler"]
            self.assertEqual(one["four_multiset_attempts"], expected_attempts)
            self.assertEqual(two["four_multiset_attempts"], expected_attempts)
            self.assertEqual(one["four_sum_support_size"], two["four_sum_support_size"])
            self.assertGreaterEqual(two["stored_witness_count"], one["stored_witness_count"])
            self.assertEqual(
                one["stored_witness_count"] + one["discarded_witness_count"],
                expected_attempts,
            )

    def test_compiled_five_sum_support_matches_direct_unordered_enumeration(self) -> None:
        row = self.rows[("random_x", 2)]
        curve_record = self.instance["curve"]
        curve = GENERATOR["Curve"](
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        points = [
            GENERATOR["point_from_json"](point)
            for point in row["factor_base"]["points"]
        ]
        compiled = GENERATOR["compile_four_sum_advice"](curve, points, 2)
        support, _ = GENERATOR["build_exact_five_sum_support"](
            curve, compiled.mapping, points
        )
        direct = set()
        for witness in itertools.combinations_with_replacement(range(len(points)), 5):
            total = None
            for index in witness:
                total = curve.add(total, points[index])
            direct.add(total)
        self.assertEqual(support, direct)
        self.assertEqual(len(support), row["exact_five_sum_support_size"])

    def test_functional_rows_have_full_rank_verified_logs_and_descent(self) -> None:
        for family in ("random_x", "random_scalar", "x_interval"):
            for cap in TEST_CONFIG["witness_caps"]:
                row = self.rows[(family, cap)]
                with self.subTest(family=family, cap=cap):
                    self.assertTrue(row["functional_gate_passed"])
                    self.assertEqual(
                        row["relations"]["rank"], self.instance["factor_base_size"]
                    )
                    self.assertTrue(row["relations"]["factor_base_logs_verified"])
                    self.assertTrue(row["descent"]["all_verified"])

    def test_every_independent_equation_has_correct_witness_and_coefficients(self) -> None:
        row = self.rows[("x_interval", 2)]
        curve_record = self.instance["curve"]
        curve = GENERATOR["Curve"](
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        points = [
            GENERATOR["point_from_json"](point)
            for point in row["factor_base"]["points"]
        ]
        for equation in row["relations"]["independent_equations"]:
            witness = tuple(equation["witness"])
            target = GENERATOR["point_from_json"](equation["target"])
            self.assertTrue(GENERATOR["verify_witness"](curve, points, witness, target))
            self.assertEqual(
                list(
                    GENERATOR["row_from_witness"](
                        witness, len(points), curve_record["q"]
                    )
                ),
                equation["coefficients"],
            )

    def test_individual_solver_does_not_accept_known_target_scalar(self) -> None:
        parameters = inspect.signature(GENERATOR["solve_individual_log"]).parameters
        self.assertNotIn("known_scalar", parameters)
        self.assertNotIn("target_scalar", parameters)

    def test_positive_control_is_ineligible_and_not_routed(self) -> None:
        for cap in TEST_CONFIG["witness_caps"]:
            control = self.rows[("scalar_progression", cap)]
            random_x = self.rows[("random_x", cap)]
            self.assertEqual(control["eligibility"], "positive_control_only")
            self.assertFalse(control["routing_gate_passed"])
            self.assertLess(
                control["exact_five_sum_support_size"],
                random_x["exact_five_sum_support_size"],
            )

    def test_attack_group_total_has_no_unexplained_component(self) -> None:
        for row in self.instance["rows"]:
            expected = (
                row["offline_charged_cost"]["group_operations"]
                + row["relations"]["target_generation_ops"]["group_operations"]
                + row["relations"]["query_ops"]["group_operations"]
                + row["aggregate_descent_attack_ops"]["group_operations"]
            )
            self.assertEqual(row["total_attack_group_operations"], expected)
            self.assertEqual(
                row["total_attack_cost_vector"]["group_operations"], expected
            )
            self.assertGreater(
                row["relations"]["witness_verification_audit_ops"][
                    "group_operations"
                ],
                0,
            )

    def test_fixed_curve_online_advice_includes_factor_base_logs(self) -> None:
        for row in self.instance["rows"]:
            online = row["fixed_curve_online"]
            expected_log_bits = (
                len(row["relations"]["factor_base_logs"])
                * self.instance["curve"]["q"].bit_length()
            )
            self.assertEqual(online["factor_base_log_advice_bits"], expected_log_bits)
            self.assertEqual(
                online["full_online_advice_bits"],
                online["compiler_advice_bits"] + expected_log_bits,
            )
            self.assertGreater(
                online["full_advice_bits_worst_case_frontier_score"], 0
            )

    def test_matched_bsgs_uses_no_more_advice_and_verifies(self) -> None:
        for row in self.instance["rows"]:
            online = row["fixed_curve_online"]
            baseline = online["matched_bsgs"]
            self.assertLessEqual(
                baseline["advice_payload_bits"], online["full_online_advice_bits"]
            )
            self.assertTrue(baseline["all_verified"])
            self.assertEqual(
                len(baseline["challenges"]), TEST_CONFIG["descent_challenges"]
            )
            self.assertFalse(baseline["candidate_online_dominates_at_equal_advice"])

    def test_randomized_descent_probability_is_exactly_bounded(self) -> None:
        for row in self.instance["rows"]:
            audit = row["target_audit"]
            probability = audit["exact_randomized_descent_success_probability"]
            self.assertGreater(probability, 0.0)
            self.assertLessEqual(probability, 1.0)
            self.assertLessEqual(
                audit["exact_randomized_descent_expected_capped_attempts"],
                TEST_CONFIG["descent_attempt_limit"],
            )
            self.assertEqual(
                probability,
                row["fixed_curve_online"][
                    "exact_randomized_success_probability_at_limit"
                ],
            )

    def test_single_seed_development_sweep_cannot_route(self) -> None:
        self.assertEqual(self.result["routing_rows"], [])
        self.assertEqual(
            self.result["routing_summary"]["required_passing_seeds_per_size"], 2
        )
        self.assertEqual(self.result["routing_summary"]["configured_seed_count"], 1)
        self.assertEqual(
            self.result["routing_summary"]["promoted_family_caps"], []
        )

    def test_exact_support_and_query_audit_agree(self) -> None:
        for row in self.instance["rows"]:
            audit = row["target_audit"]
            self.assertEqual(
                audit["supported_targets"], row["exact_five_sum_support_size"]
            )
            self.assertEqual(
                audit["exact_success_probability"],
                row["exact_five_sum_support_size"] / self.instance["curve"]["q"],
            )
            self.assertLessEqual(
                audit["maximum_first_witness_probes"],
                self.instance["factor_base_size"],
            )

    def test_independent_verifier_rejects_core_mutations(self) -> None:
        mutations = []

        rhs = copy.deepcopy(self.result)
        rhs["instances"][0]["rows"][0]["relations"]["independent_equations"][0][
            "rhs"
        ] += 1
        mutations.append(rhs)

        witness = copy.deepcopy(self.result)
        witness["instances"][0]["rows"][0]["relations"]["independent_equations"][0][
            "witness"
        ][0] ^= 1
        mutations.append(witness)

        rank = copy.deepcopy(self.result)
        rank["instances"][0]["rows"][0]["relations"]["rank"] -= 1
        mutations.append(rank)

        metric = copy.deepcopy(self.result)
        metric["instances"][0]["rows"][0]["compiler"][
            "payload_bit_lower_estimate"
        ] += 1
        mutations.append(metric)

        source = copy.deepcopy(self.result)
        source["source_hashes"]["fixed_curve_compiler_sha256"] = "0" * 64
        mutations.append(source)

        descent = copy.deepcopy(self.result)
        descent["instances"][0]["rows"][0]["descent"]["challenges"][0][
            "recovered_scalar"
        ] += 1
        mutations.append(descent)

        bsgs = copy.deepcopy(self.result)
        bsgs["instances"][0]["rows"][0]["fixed_curve_online"]["matched_bsgs"][
            "table_capacity"
        ] += 1
        mutations.append(bsgs)

        for index, document in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(AssertionError):
                VERIFIER["verify_document"](document, enforce_frozen=False)

    def test_cli_round_trip_and_canonical_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "result.json"
            result_path.write_text(
                json.dumps(self.result, sort_keys=True, allow_nan=False),
                encoding="utf-8",
            )
            accepted = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VERIFIER_PATH),
                    "--input",
                    str(result_path),
                    "--allow-development",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(accepted.stdout)["status"], "verified")

            rejected = subprocess.run(
                [sys.executable, "-B", str(VERIFIER_PATH), "--input", str(result_path)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("frozen configuration", rejected.stderr)


if __name__ == "__main__":
    unittest.main()

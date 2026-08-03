from __future__ import annotations

import copy
import inspect
import math
import json
import runpy
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
EXPERIMENT = REPO_ROOT / "experiments" / "EXP-ECDLP-COMPRESSED-JOIN-001"
GENERATOR_PATH = EXPERIMENT / "src" / "compressed_join.py"
VERIFIER_PATH = EXPERIMENT / "src" / "verify_compressed_join.py"
FIBER_AUDIT_PATH = EXPERIMENT / "src" / "audit_fiber_null.py"
MATERIALIZED_AUDIT_PATH = EXPERIMENT / "src" / "audit_materialized_baseline.py"
GENERATOR = runpy.run_path(str(GENERATOR_PATH))
VERIFIER = runpy.run_path(str(VERIFIER_PATH))
FIBER_AUDIT = runpy.run_path(str(FIBER_AUDIT_PATH))
MATERIALIZED_AUDIT = runpy.run_path(str(MATERIALIZED_AUDIT_PATH))
TEST_CONFIG = {
    "bit_sizes": [8],
    "seeds": [41],
    "families": ["x_interval", "random_x"],
    "routers": [
        "x_mod",
        "x_interval",
        "legendre_vector",
        "random_label",
        "scalar_interval",
    ],
    "bucket_counts": [4],
    "occupancy_lambda": 0.5,
    "query_samples": 2,
    "descent_challenges": 1,
    "descent_attempt_limit": 8,
    "rho_trials": 1,
}


class CompressedJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = GENERATOR["run_experiment"](copy.deepcopy(TEST_CONFIG))
        cls.instance = cls.result["instances"][0]
        cls.family = cls.instance["families"][0]
        cls.rows = {row["router"]: row for row in cls.family["rows"]}

    def test_small_quotient_obstruction_on_toy_cyclic_groups(self) -> None:
        for prime_order in (5, 7, 11):
            for target_order in range(2, prime_order):
                images = {
                    tuple((generator_image * scalar) % target_order for scalar in range(prime_order))
                    for generator_image in range(target_order)
                    if (generator_image * prime_order) % target_order == 0
                }
                self.assertEqual(images, {tuple(0 for _ in range(prime_order))})

    def test_curve_and_global_controls_are_clean(self) -> None:
        curve = self.instance["curve"]
        self.assertNotIn(curve["trace"], (0, 1))
        self.assertNotIn(curve["j_invariant"], (0, 1728 % curve["p"]))
        self.assertEqual(curve["q"], curve["order"])
        self.assertTrue(all(self.result["global_controls"].values()))

    def test_development_document_replays_and_passes_independent_audit(self) -> None:
        certificate = VERIFIER["verify_document"](
            copy.deepcopy(self.result), enforce_frozen=False
        )
        self.assertEqual(certificate["status"], "verified")
        self.assertTrue(certificate["development_only"])
        self.assertEqual(certificate["verified_instances"], 1)
        self.assertEqual(certificate["verified_families"], 2)
        self.assertGreater(certificate["verified_factor_witnesses"], 0)

    def test_development_document_cannot_pass_canonical_verification(self) -> None:
        with self.assertRaises(AssertionError):
            VERIFIER["verify_document"](
                copy.deepcopy(self.result), enforce_frozen=True
            )

    def test_mutated_route_metric_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["instances"][0]["families"][0]["rows"][0]["advice"][
            "distinct_route_triples"
        ] += 1
        with self.assertRaises(AssertionError):
            VERIFIER["verify_document"](mutated, enforce_frozen=False)

    def test_d2_d4_and_d5_supports_are_nonempty_and_nested(self) -> None:
        for family in self.instance["families"]:
            self.assertGreater(family["d2"]["support_size"], 0)
            self.assertGreaterEqual(family["d4"]["support_size"], family["d2"]["support_size"])
            self.assertGreaterEqual(family["d5"]["support_size"], family["d4"]["support_size"])
            self.assertLessEqual(family["d5"]["support_size"], self.instance["curve"]["q"])

    def test_d2_composition_matches_direct_materialized_d4(self) -> None:
        self.assertEqual(
            self.family["d4"]["support_size"],
            self.family["baselines"]["materialized_d4"]["four_sum_support_size"],
        )

    def test_all_routers_receive_identical_targets(self) -> None:
        for sample_name in ("supported_d4", "supported_d5", "random_d5"):
            schedules = {
                tuple(
                    repr(record["target"])
                    for record in row["query_samples"][sample_name]["records"]
                )
                for row in self.family["rows"]
            }
            self.assertEqual(len(schedules), 1)
        challenge_schedules = {
            tuple(repr(challenge["target"]) for challenge in row["descent"]["challenges"])
            for row in self.family["rows"]
        }
        attempt_schedules = {
            tuple(challenge["attempts"] for challenge in row["descent"]["challenges"])
            for row in self.family["rows"]
        }
        self.assertEqual(len(challenge_schedules), 1)
        self.assertEqual(len(attempt_schedules), 1)

    def test_supported_queries_return_verified_factor_witnesses(self) -> None:
        for row in self.family["rows"]:
            for sample_name in ("supported_d4", "supported_d5"):
                sample = row["query_samples"][sample_name]
                with self.subTest(router=row["router"], sample=sample_name):
                    self.assertEqual(sample["successes"], sample["sample_count"])
                    self.assertTrue(sample["all_successes_verified"])
                    self.assertTrue(all(record["verified"] for record in sample["records"]))

    def test_descent_recovers_the_private_toy_scalars(self) -> None:
        for row in self.family["rows"]:
            with self.subTest(router=row["router"]):
                self.assertTrue(row["descent"]["all_verified"])
                for challenge in row["descent"]["challenges"]:
                    self.assertEqual(
                        challenge["recovered_scalar"],
                        challenge["known_scalar_private_audit"],
                    )

    def test_scalar_control_calibrates_locality_but_is_ineligible(self) -> None:
        scalar = self.rows["scalar_interval"]
        random_row = self.rows["random_label"]
        self.assertEqual(scalar["eligibility"], "positive_control_only")
        self.assertFalse(scalar["instance_signal_gate_passed"])
        self.assertLess(
            scalar["advice"]["average_forward_output_width"],
            random_row["advice"]["average_forward_output_width"],
        )
        self.assertTrue(scalar["scalar_calibration_passed"])

    def test_random_fiber_null_identifies_point_negation(self) -> None:
        curve_record = self.instance["curve"]
        curve = GENERATOR["Curve"](
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        point = GENERATOR["BASE"].point_from_json(curve_record["generator"])
        negative = curve.neg(point)
        self.assertEqual(
            FIBER_AUDIT["random_fiber_bucket"](
                "random_label", point, 8, curve, curve_record["q"], 901, None
            ),
            FIBER_AUDIT["random_fiber_bucket"](
                "random_label", negative, 8, curve, curve_record["q"], 901, None
            ),
        )

    def test_repaired_null_and_materialized_audits_execute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "result.json"
            input_path.write_text(
                json.dumps(self.result, sort_keys=True, allow_nan=False),
                encoding="utf-8",
            )
            fiber = FIBER_AUDIT["run_audit"](
                copy.deepcopy(self.result), input_path, [4], [901, 907]
            )
            materialized = MATERIALIZED_AUDIT["run_audit"](
                copy.deepcopy(self.result), input_path
            )
        self.assertEqual(fiber["protocol"], "AUDIT-ECDLP-COMPRESSED-JOIN-FIBER-NULL-001")
        self.assertEqual(len(fiber["rows"]), 6)
        self.assertIn("x_mod", fiber["summary"])
        self.assertEqual(
            materialized["protocol"],
            "AUDIT-ECDLP-COMPRESSED-JOIN-MATERIALIZED-001",
        )
        self.assertEqual(len(materialized["baseline_rows"]), 2)
        self.assertTrue(
            all(
                row["supported_d5_group_operation_ratio_to_materialized"] > 1
                for row in materialized["comparison_rows"]
            )
        )

    def test_public_routers_do_not_require_scalar_index(self) -> None:
        parameters = inspect.signature(GENERATOR["router_bucket"]).parameters
        self.assertIn("scalar_index", parameters)
        curve_record = self.instance["curve"]
        curve = GENERATOR["Curve"](
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        point = GENERATOR["BASE"].point_from_json(curve_record["generator"])
        for router in GENERATOR["CANDIDATE_ROUTERS"] + ["random_label"]:
            GENERATOR["router_bucket"](
                router, point, 4, curve, curve_record["q"], 9, None
            )
        with self.assertRaises(ValueError):
            GENERATOR["router_bucket"](
                "scalar_interval", point, 4, curve, curve_record["q"], 9, None
            )

    def test_removing_routes_removes_witness_recovery(self) -> None:
        curve_record = self.instance["curve"]
        curve = GENERATOR["Curve"](
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        generator = GENERATOR["BASE"].point_from_json(curve_record["generator"])
        factor_points = [
            GENERATOR["BASE"].point_from_json(point)
            for point in self.family["factor_base"]["points"]
        ]
        d2 = GENERATOR["build_d2"](curve, factor_points)
        d4 = GENERATOR["build_d4"](curve, d2)
        advice = GENERATOR["compile_router"](
            curve,
            curve_record["q"],
            factor_points,
            d2,
            d4,
            "x_mod",
            4,
            17,
            None,
        )
        target = d4.points[0]
        self.assertTrue(
            GENERATOR["query_d4"](
                curve, curve_record["q"], target, d2, advice, 17, None
            )["success"]
        )
        advice.routes.clear()
        self.assertFalse(
            GENERATOR["query_d4"](
                curve, curve_record["q"], target, d2, advice, 17, None
            )["success"]
        )
        self.assertIsNotNone(generator)

    def test_route_counts_and_payloads_are_self_consistent(self) -> None:
        for row in self.family["rows"]:
            advice = row["advice"]
            self.assertLessEqual(
                advice["distinct_route_triples"],
                advice["bucket_count"] ** 3,
            )
            self.assertEqual(
                advice["route_coverage_oriented_pairs"],
                advice["expected_oriented_pairs"],
            )
            self.assertGreater(advice["payload_bit_lower_estimate"], 0)
            self.assertGreater(advice["canonical_serialized_bytes"], 0)
            self.assertGreater(advice["python_deep_bytes"], 0)
            self.assertTrue(math.isfinite(advice["normalized_conditional_output_entropy"]))

    def test_equal_advice_bsgs_is_executed_and_verified(self) -> None:
        for row in self.family["rows"]:
            bsgs = row["matched_bsgs"]
            self.assertTrue(bsgs["all_verified"])
            self.assertLessEqual(bsgs["advice_payload_bits"], row["full_online_advice_bits"])
            self.assertGreaterEqual(
                bsgs["candidate_to_bsgs_average_online_group_operation_ratio"],
                0,
            )

    def test_private_scalar_material_is_not_emitted_as_advice(self) -> None:
        self.assertFalse(self.instance["scalar_index_emitted"])
        for family in self.instance["families"]:
            self.assertFalse(family["factor_base_logs_emitted"])
            self.assertIsInstance(family["factor_base_logs_private_audit_digest"], str)
            for row in family["rows"]:
                self.assertFalse(row["advice"]["hidden_scalar_metadata_emitted"])

    def test_single_seed_development_run_cannot_route(self) -> None:
        self.assertTrue(self.result["development_only"])
        self.assertFalse(self.result["configuration_is_frozen"])
        self.assertEqual(self.result["routing_rows"], [])
        self.assertEqual(self.result["routing_summary"]["configured_seed_count"], 1)


if __name__ == "__main__":
    unittest.main()

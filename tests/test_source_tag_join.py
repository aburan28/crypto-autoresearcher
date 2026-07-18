from __future__ import annotations

import copy
import runpy
import unittest
from pathlib import Path

from crypto_autoresearcher.records import find_repo_root


REPO_ROOT = find_repo_root(Path(__file__).parent)
EXPERIMENT = REPO_ROOT / "experiments" / "EXP-ECDLP-SOURCE-TAG-JOIN-001"
GENERATOR = runpy.run_path(str(EXPERIMENT / "src" / "source_tag_join.py"))
VERIFIER = runpy.run_path(str(EXPERIMENT / "src" / "verify_source_tag_join.py"))
TEST_CONFIG = {
    "bit_sizes": [8],
    "seeds": [3317584535],
    "families": ["x_interval", "random_scalar"],
    "witness_policies": ["symmetry_lex"],
    "source_tags": ["ordinal_sum"],
    "tag_counts": [4],
    "output_routers": ["x_interval"],
    "null_seeds": [101, 103],
    "occupancy_lambda": 0.5,
    "query_samples": 2,
    "descent_challenges": 1,
    "descent_attempt_limit": 8,
    "rho_trials": 1,
}


class SourceTagJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = GENERATOR["run_experiment"](copy.deepcopy(TEST_CONFIG))
        cls.instance = cls.result["instances"][0]
        cls.family = cls.instance["families"][0]
        cls.rows = cls.family["rows"]
        cls.candidate = next(
            row for row in cls.rows if row["variant_kind"] == "candidate"
        )

    def test_v2_document_replays_and_passes_independent_audit(self) -> None:
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

    def test_default_frozen_cli_requires_explicit_authorization_flag(self) -> None:
        with self.assertRaises(SystemExit) as error:
            GENERATOR["main"]([])
        self.assertIn("requires --authorize-canonical", str(error.exception))

    def test_curve_and_global_controls_are_clean(self) -> None:
        curve = self.instance["curve"]
        self.assertNotIn(curve["trace"], (0, 1))
        self.assertNotIn(curve["j_invariant"], (0, 1728 % curve["p"]))
        self.assertTrue(all(self.result["global_controls"].values()))

    def test_both_null_families_are_present_and_invariant(self) -> None:
        variants = [row["variant_kind"] for row in self.rows]
        self.assertEqual(variants.count("margin_null"), 2)
        self.assertEqual(variants.count("source_null"), 2)
        for row in self.rows:
            if row["variant_kind"] == "margin_null":
                null = row["advice"]["null"]
                self.assertTrue(null["tag_histogram_preserved"])
                self.assertTrue(null["multiplicity_by_tag_preserved"])
                self.assertTrue(null["witness_class_by_tag_preserved"])
                self.assertTrue(null["inversion_symmetry_preserved"])
                self.assertEqual(
                    row["advice"]["tag_histogram"],
                    self.candidate["advice"]["tag_histogram"],
                )
            elif row["variant_kind"] == "source_null":
                null = row["advice"]["null"]
                self.assertTrue(null["source_multiset_preserved"])
                self.assertTrue(null["compositional_recompute"])
                self.assertTrue(null["inversion_symmetry_preserved"])

    def test_public_candidates_never_receive_scalar_oracle(self) -> None:
        for family in self.instance["families"]:
            forbidden = {"sampled_scalar", "canonical_scalar", "scalar_index"}
            for source in family["public_factor_sources"]:
                self.assertTrue(forbidden.isdisjoint(source["source"]))
            for row in family["rows"]:
                if row["variant_kind"] == "positive_control":
                    self.assertTrue(row["advice"]["scalar_oracle_required"])
                    self.assertEqual(row["eligibility"], "positive_control_only")
                else:
                    self.assertFalse(row["advice"]["scalar_oracle_required"])
                    self.assertFalse(row["advice"]["hidden_scalar_metadata_emitted"])

    def test_all_supported_queries_return_independently_valid_witnesses(self) -> None:
        for family in self.instance["families"]:
            for row in family["rows"]:
                for name in ("supported_d4", "supported_d5"):
                    sample = row["query_samples"][name]
                    self.assertEqual(sample["successes"], sample["sample_count"])
                    self.assertTrue(sample["all_successes_verified"])

    def test_exact_d2_complement_is_a_mandatory_executed_baseline(self) -> None:
        baselines = self.family["baselines"]["d2_complement"]
        self.assertEqual(len(baselines), 1)
        baseline = baselines[0]
        self.assertTrue(
            baseline["query_samples"]["supported_d4"]["all_successes_verified"]
        )
        self.assertTrue(
            baseline["query_samples"]["supported_d5"]["all_successes_verified"]
        )
        self.assertGreater(baseline["advice"]["payload_bit_lower_estimate"], 0)
        self.assertIsNotNone(
            self.candidate["d2_complement_comparison"][
                "candidate_to_d2_query_st2_diagnostic_ratio"
            ]
        )
        self.assertIsNotNone(
            self.candidate["d2_complement_comparison"][
                "candidate_to_d2_descent_st2_diagnostic_ratio"
            ]
        )

    def test_partial_d4_baselines_fit_candidate_payload(self) -> None:
        baselines = self.family["baselines"]["partial_d4"]
        self.assertGreater(len(baselines), 0)
        for baseline in baselines:
            self.assertTrue(baseline["advice"]["within_payload_budget"])
            self.assertLessEqual(
                baseline["advice"]["payload_bit_lower_estimate"],
                baseline["advice"]["payload_budget_bits"],
            )
            self.assertTrue(
                baseline["query_samples"]["supported_d5"][
                    "all_successes_verified"
                ]
            )
        self.assertTrue(
            self.candidate["partial_d4_comparison"]["hybrid_uses_no_more_advice"]
        )

    def test_query_and_dlp_envelopes_do_not_mix_tasks(self) -> None:
        decomposition = self.candidate["decomposition_envelope"]
        self.assertIn("d2_complement", decomposition["includes"])
        self.assertIn("partial_d4_cache", decomposition["includes"])
        self.assertNotIn("equal_advice_bsgs", decomposition["includes"])
        dlp = self.candidate["dlp_envelope"]
        self.assertIn("d2_complement_descent", dlp["includes"])
        self.assertIn("partial_d4_cache_descent", dlp["includes"])
        self.assertIn("equal_advice_bsgs", dlp["includes"])
        materialized_fits = (
            self.family["baselines"]["materialized_d4"][
                "full_online_advice_bits"
            ]
            <= self.candidate["full_online_advice_bits"]
        )
        self.assertEqual(
            "materialized_d4_descent" in dlp["includes"], materialized_fits
        )

    def test_descent_outcome_cannot_change_structural_gate(self) -> None:
        original = copy.deepcopy(self.candidate)
        changed = copy.deepcopy(self.candidate)
        changed["descent"]["all_verified"] = not original["descent"]["all_verified"]
        changed["descent"]["all_challenges_solved"] = not original["descent"][
            "all_challenges_solved"
        ]
        self.assertEqual(
            GENERATOR["evaluate_source_signal_gate"](original),
            GENERATOR["evaluate_source_signal_gate"](changed),
        )

    def test_complete_descent_bound_charges_every_attempt(self) -> None:
        bound = self.candidate["descent_worst_case"]
        self.assertEqual(
            bound["complete_group_operation_bound"],
            bound["attempt_limit"]
            * (
                bound["shift_group_operation_bound_per_attempt"]
                + bound["d5_group_operation_bound_per_attempt"]
            ),
        )
        bsgs = self.candidate["matched_bsgs"]
        expected_ratio = (
            bound["complete_group_operation_bound"]
            / bsgs["worst_case_online_group_operation_bound"]
            if bsgs["worst_case_online_group_operation_bound"]
            else None
        )
        self.assertEqual(
            bsgs["candidate_to_bsgs_worst_case_group_operation_ratio"],
            expected_ratio,
        )

    def test_all_rows_and_baselines_share_target_schedules(self) -> None:
        for family in self.instance["families"]:
            schedules = {}
            for row in family["rows"]:
                for name in ("supported_d4", "supported_d5", "random_d5"):
                    current = tuple(
                        repr(record["target"])
                        for record in row["query_samples"][name]["records"]
                    )
                    schedules.setdefault(name, current)
                    self.assertEqual(current, schedules[name])
            baselines = [family["baselines"]["materialized_d4"]]
            baselines.extend(family["baselines"]["d2_complement"])
            baselines.extend(family["baselines"]["partial_d4"])
            for baseline in baselines:
                for name in ("supported_d4", "supported_d5", "random_d5"):
                    current = tuple(
                        repr(record["target"])
                        for record in baseline["query_samples"][name]["records"]
                    )
                    self.assertEqual(current, schedules[name])

    def test_d5_point_reads_include_every_outer_factor_read(self) -> None:
        curve = self.instance["curve"]
        point_bytes = (1 + 2 * curve["p"].bit_length() + 7) // 8
        for family in self.instance["families"]:
            query_sets = [row["query_samples"] for row in family["rows"]]
            query_sets.append(
                family["baselines"]["materialized_d4"]["query_samples"]
            )
            query_sets.extend(
                baseline["query_samples"]
                for baseline in family["baselines"]["d2_complement"]
            )
            query_sets.extend(
                baseline["query_samples"]
                for baseline in family["baselines"]["partial_d4"]
            )
            for query_samples in query_sets:
                for record in query_samples["supported_d4"]["records"]:
                    self.assertEqual(record["outer_factor_point_reads"], 0)
                    self.assertEqual(
                        record["outer_factor_logical_bytes_read"], 0
                    )
                for name in ("supported_d5", "random_d5"):
                    for record in query_samples[name]["records"]:
                        outer_reads = record["outer_factor_point_reads"]
                        self.assertGreaterEqual(outer_reads, 1)
                        self.assertGreaterEqual(record["point_reads"], outer_reads)
                        self.assertEqual(
                            record["outer_factor_logical_bytes_read"],
                            outer_reads * point_bytes,
                        )
                        self.assertGreaterEqual(
                            record["logical_point_bytes_read"],
                            record["outer_factor_logical_bytes_read"],
                        )

    def test_same_outer_scan_materialized_obstruction_is_observed(self) -> None:
        materialized = self.family["baselines"]["materialized_d4"][
            "query_samples"
        ]["supported_d5"]["average_group_operations"]
        for row in self.rows:
            self.assertGreaterEqual(
                row["query_samples"]["supported_d5"]["average_group_operations"],
                materialized,
            )
            if row["variant_kind"] == "candidate":
                self.assertFalse(row["compiler_gate_passed"])

    def test_candidate_build_streams_pairs_without_materialized_workspace(self) -> None:
        advice = self.candidate["advice"]
        self.assertTrue(advice["streaming_build"])
        self.assertFalse(advice["materialized_d4_workspace_used_by_candidate"])
        self.assertEqual(
            advice["route_compile_ops"]["group_operations"],
            self.family["policy_supports"][0]["d4"][
                "unordered_d2_pair_attempts"
            ],
        )

    def test_all_witness_tags_are_diagnostic_not_extra_support(self) -> None:
        diagnostics = self.family["policy_supports"][0][
            "all_witness_tag_diagnostics"
        ]
        self.assertEqual(len(diagnostics), 1)
        diagnostic = diagnostics[0]
        self.assertFalse(diagnostic["credited_as_support"])
        self.assertGreaterEqual(
            diagnostic["total_provenance_states"],
            diagnostic["semantic_d2_points"],
        )

    def test_saturated_route_universe_is_not_promotable(self) -> None:
        if self.candidate["advice"]["route_universe_saturated"]:
            self.assertFalse(self.candidate["source_signal_gate_passed"])
        self.assertIn("route_slope_eligible", self.result["exploratory_slopes"][0])

    def test_mutated_route_metric_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["instances"][0]["families"][0]["rows"][0]["advice"][
            "distinct_route_triples"
        ] += 1
        with self.assertRaises(AssertionError):
            VERIFIER["verify_document"](mutated, enforce_frozen=False)

    def test_independent_route_audit_rejects_repaired_prefix_mutation(self) -> None:
        mutated = copy.deepcopy(self.result)
        row = next(
            row
            for row in mutated["instances"][0]["families"][0]["rows"]
            if row["variant_kind"] == "candidate"
        )
        row["advice"]["first_tags"][0] = (
            row["advice"]["first_tags"][0] + 1
        ) % row["tag_count"]
        with self.assertRaises(AssertionError):
            VERIFIER["verify_semantics"](mutated)

    def test_independent_null_audit_rejects_permutation_mutation(self) -> None:
        mutated = copy.deepcopy(self.result)
        row = next(
            row
            for row in mutated["instances"][0]["families"][0]["rows"]
            if row["variant_kind"] == "source_null"
        )
        row["advice"]["null"]["permutation_digest"] = "0" * 64
        with self.assertRaises(AssertionError):
            VERIFIER["verify_semantics"](mutated)

    def test_independent_source_audit_rejects_scalar_canary(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["instances"][0]["families"][0]["public_factor_sources"][0][
            "source"
        ]["sampled_scalar"] = 1
        with self.assertRaises(AssertionError):
            VERIFIER["verify_semantics"](mutated)

    def test_single_seed_run_cannot_promote(self) -> None:
        self.assertEqual(self.result["routing_summary"]["configured_seed_count"], 1)
        self.assertEqual(self.result["routing_rows"], [])
        self.assertEqual(self.result["compiler_rows"], [])


if __name__ == "__main__":
    unittest.main()

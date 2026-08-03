"""Unit tests for symbolic τ-schema / stopping-coverage obligation ledger."""

from __future__ import annotations

import unittest

from .ledger_checks import (
    EXPECTED_COUNTS,
    check_classification,
    check_forbidden_clearance_flags,
    check_memory_map_status,
    check_mutation_status,
    check_obligation_ledger,
    check_scaffold_read_only,
)


class TestObligationLedger(unittest.TestCase):
    def test_item_counts_and_statuses(self) -> None:
        report = check_obligation_ledger()
        self.assertTrue(report["edge_counts_ok"])
        self.assertTrue(report["items_well_formed"])
        self.assertEqual(report["item_count"], EXPECTED_COUNTS["total_items"])
        self.assertEqual(
            report["family_counts"]["tau_coverage"],
            EXPECTED_COUNTS["tau_coverage_family"],
        )
        self.assertEqual(
            report["family_counts"]["tau_instantiation"],
            EXPECTED_COUNTS["tau_instantiation_family"],
        )
        self.assertEqual(
            report["family_counts"]["lineage_cross_link"],
            EXPECTED_COUNTS["lineage_cross_link_family"],
        )
        self.assertEqual(
            report["status_counts"]["wired_symbolic"],
            EXPECTED_COUNTS["wired_symbolic"],
        )

    def test_package_ok_fail_no_clearance(self) -> None:
        report = check_obligation_ledger()
        self.assertTrue(report["package_ok"])
        self.assertTrue(report["coverage_ok"])
        self.assertTrue(report["lineage_ok"])
        self.assertEqual(report["ledger_status"], "tau_schema_stopping_fail")
        self.assertEqual(report["control_result"], "FAIL")
        self.assertIs(report["query_memory_cleared"], False)
        self.assertIs(report["qm_stopping_cleared"], False)
        self.assertIs(report["numeric_charges_invented"], False)
        self.assertIs(report["crypto_verify_implemented"], False)
        self.assertIs(report["tau_invented"], False)


class TestMemoryMapAndClassification(unittest.TestCase):
    def test_memory_map_retained_without_clearance(self) -> None:
        report = check_memory_map_status()
        self.assertTrue(report["passed"])
        self.assertEqual(report["prior_status"], "history_uniform_tail_partial")
        self.assertEqual(
            report["status_after_batch"], "history_uniform_tail_partial"
        )
        self.assertIs(report["clearance"], False)
        self.assertIs(report["query_memory_cleared"], False)

    def test_classification_disposition_and_qm_statuses(self) -> None:
        report = check_classification()
        self.assertTrue(report["passed"])
        self.assertEqual(
            report["disposition"],
            "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED",
        )
        self.assertEqual(report["control_result"], "FAIL")
        self.assertEqual(report["qm_stopping"], "open")
        self.assertEqual(report["qm_memory_map"], "history_uniform_tail_partial")
        self.assertEqual(report["qm_error"], "f_union_ledger_partial")
        self.assertIs(report["non_extrapolation"], True)

    def test_mutation_scaffold_untouched(self) -> None:
        report = check_mutation_status()
        self.assertTrue(report["passed"])
        self.assertIs(report["scaffold_mutated"], False)
        self.assertEqual(
            report["qm_memory_map_after"], "history_uniform_tail_partial"
        )
        self.assertEqual(report["qm_error_after"], "f_union_ledger_partial")
        self.assertEqual(report["qm_stopping_control_result"], "FAIL")

    def test_no_forbidden_true_clearance_flags(self) -> None:
        report = check_forbidden_clearance_flags()
        self.assertEqual(report["forbidden_true_hits"], [])
        self.assertTrue(report["passed"])

    def test_batch022_scaffold_read_only_tau_reject_present(self) -> None:
        report = check_scaffold_read_only()
        self.assertTrue(report["passed"])
        self.assertTrue(report["tail_has_M_tail"])
        self.assertTrue(report["has_channel_notes"])
        self.assertTrue(report["note_stopping_breach_F_stop"])
        self.assertTrue(report["note_tail_exhaustion_F_tail"])
        self.assertTrue(report["birth_M_tail_rejects_invents_tau"])
        self.assertTrue(report["birth_M_tail_rejects_numeric_width"])
        self.assertTrue(report["verify_true_smoke"])
        self.assertTrue(report["classify_success_smoke"])


if __name__ == "__main__":
    unittest.main()

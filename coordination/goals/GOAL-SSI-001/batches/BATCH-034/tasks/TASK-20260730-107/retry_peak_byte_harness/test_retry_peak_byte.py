"""Unit tests for symbolic retry→peak-byte conversion schema ledger."""

from __future__ import annotations

import unittest

from .ledger_checks import (
    EXPECTED_COUNTS,
    check_classification,
    check_forbidden_clearance_flags,
    check_memory_map_status,
    check_mutation_status,
    check_no_invented_numerics,
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
            report["family_counts"]["retry_residual_route"],
            EXPECTED_COUNTS["retry_residual_route_family"],
        )
        self.assertEqual(
            report["family_counts"]["peak_object_slot"],
            EXPECTED_COUNTS["peak_object_slot_family"],
        )
        self.assertEqual(
            report["family_counts"]["width_binding_feed"],
            EXPECTED_COUNTS["width_binding_feed_family"],
        )
        self.assertEqual(
            report["family_counts"]["conversion_placeholder"],
            EXPECTED_COUNTS["conversion_placeholder_family"],
        )
        self.assertEqual(
            report["family_counts"]["lineage_cross_link"],
            EXPECTED_COUNTS["lineage_cross_link_family"],
        )
        self.assertEqual(
            report["status_counts"]["wired_symbolic"],
            EXPECTED_COUNTS["wired_symbolic"],
        )
        self.assertEqual(
            report["status_counts"]["not_instantiated"],
            EXPECTED_COUNTS["not_instantiated"],
        )

    def test_package_ok_fail_no_clearance(self) -> None:
        report = check_obligation_ledger()
        self.assertTrue(report["package_ok"])
        self.assertTrue(report["coverage_ok"])
        self.assertEqual(report["ledger_status"], "retry_peak_byte_schema_partial")
        self.assertEqual(report["control_result"], "FAIL")
        self.assertEqual(
            report["width_slot_binding_partial_retained"],
            "width_slot_binding_partial",
        )
        self.assertEqual(
            report["peak_liveset_partial_retained"], "peak_liveset_partial"
        )
        self.assertIs(report["query_memory_cleared"], False)
        self.assertIs(report["qm_stopping_cleared"], False)
        self.assertIs(report["numeric_widths_invented"], False)
        self.assertIs(report["peak_byte_bound_invented"], False)
        self.assertIs(report["conversion_factor_invented"], False)
        self.assertIs(report["retry_multiplier_invented"], False)
        self.assertIs(report["tau_invented"], False)

    def test_no_invented_numerics_in_ledger(self) -> None:
        report = check_no_invented_numerics()
        self.assertEqual(report["hits"], [])
        self.assertTrue(report["passed"])


class TestMemoryMapAndClassification(unittest.TestCase):
    def test_memory_map_advanced_without_clearance(self) -> None:
        report = check_memory_map_status()
        self.assertTrue(report["passed"])
        self.assertEqual(report["prior_status"], "width_slot_binding_partial")
        self.assertEqual(
            report["status_after_batch"], "retry_peak_byte_schema_partial"
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
        self.assertEqual(
            report["qm_memory_map"], "retry_peak_byte_schema_partial"
        )
        self.assertEqual(report["qm_error"], "f_union_ledger_partial")
        self.assertIs(report["non_extrapolation"], True)

    def test_mutation_scaffold_untouched(self) -> None:
        report = check_mutation_status()
        self.assertTrue(report["passed"])
        self.assertIs(report["scaffold_mutated"], False)
        self.assertEqual(
            report["qm_memory_map_after"], "retry_peak_byte_schema_partial"
        )
        self.assertEqual(report["qm_error_after"], "f_union_ledger_partial")
        self.assertEqual(report["qm_stopping_control_result"], "FAIL")

    def test_no_forbidden_true_clearance_flags(self) -> None:
        report = check_forbidden_clearance_flags()
        self.assertEqual(report["forbidden_true_hits"], [])
        self.assertTrue(report["passed"])

    def test_batch022_scaffold_read_only_controls_present(self) -> None:
        report = check_scaffold_read_only()
        self.assertTrue(report["passed"])
        self.assertTrue(report["tail_has_M_tail"])
        self.assertTrue(report["birth_M_tail_rejects_invents_tau"])
        self.assertTrue(report["birth_M_tail_rejects_numeric_width"])
        self.assertTrue(report["cleanup_retry_accept_smoke"])
        self.assertTrue(report["verify_true_smoke"])
        self.assertTrue(report["classify_success_smoke"])


if __name__ == "__main__":
    unittest.main()

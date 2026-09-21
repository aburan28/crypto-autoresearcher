"""Unit tests for symbolic charge-incidence ledger consistency."""

from __future__ import annotations

import unittest

from .ledger_checks import (
    EXPECTED_COUNTS,
    check_charge_incidence_ledger,
    check_classification,
    check_forbidden_clearance_flags,
    check_memory_map_status,
    check_mutation_status,
    check_scaffold_read_only,
)


class TestChargeIncidenceLedger(unittest.TestCase):
    def test_edge_counts_and_statuses(self) -> None:
        report = check_charge_incidence_ledger()
        self.assertTrue(report["edge_counts_ok"])
        self.assertTrue(report["edges_well_formed"])
        self.assertEqual(
            report["slot_edge_count"], EXPECTED_COUNTS["stage_slot_edges"]
        )
        self.assertEqual(
            report["hook_edge_count"], EXPECTED_COUNTS["lifetime_hook_edges"]
        )
        self.assertEqual(
            report["combined_status_counts"]["wired_symbolic"],
            EXPECTED_COUNTS["wired_symbolic"],
        )

    def test_package_ok_no_clearance(self) -> None:
        report = check_charge_incidence_ledger()
        self.assertTrue(report["package_ok"])
        self.assertTrue(report["coverage_ok"])
        self.assertEqual(
            report["charge_incidence_status"], "charge_incidence_partial"
        )
        self.assertIs(report["query_memory_cleared"], False)
        self.assertIs(report["qm_stopping_cleared"], False)
        self.assertIs(report["numeric_charges_invented"], False)


class TestMemoryMapAndClassification(unittest.TestCase):
    def test_memory_map_advancement_without_clearance(self) -> None:
        report = check_memory_map_status()
        self.assertTrue(report["passed"])
        self.assertEqual(report["prior_status"], "resource_vector_partial")
        self.assertEqual(report["status_after_batch"], "charge_incidence_partial")
        self.assertIs(report["clearance"], False)
        self.assertIs(report["query_memory_cleared"], False)

    def test_classification_disposition_and_qm_statuses(self) -> None:
        report = check_classification()
        self.assertTrue(report["passed"])
        self.assertEqual(
            report["disposition"],
            "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED",
        )
        self.assertEqual(report["qm_stopping"], "open")
        self.assertEqual(report["qm_memory_map"], "charge_incidence_partial")
        self.assertEqual(report["qm_error"], "f_union_ledger_partial")
        self.assertIs(report["non_extrapolation"], True)

    def test_mutation_scaffold_untouched(self) -> None:
        report = check_mutation_status()
        self.assertTrue(report["passed"])
        self.assertIs(report["scaffold_mutated"], False)
        self.assertEqual(
            report["qm_memory_map_after"], "charge_incidence_partial"
        )
        self.assertEqual(report["qm_error_after"], "f_union_ledger_partial")

    def test_no_forbidden_true_clearance_flags(self) -> None:
        report = check_forbidden_clearance_flags()
        self.assertEqual(report["forbidden_true_hits"], [])
        self.assertTrue(report["passed"])

    def test_batch022_scaffold_read_only_hooks_present(self) -> None:
        report = check_scaffold_read_only()
        self.assertTrue(report["passed"])
        self.assertEqual(report["required_hook_count"], 12)
        self.assertEqual(report["implemented_method_count"], 48)


if __name__ == "__main__":
    unittest.main()

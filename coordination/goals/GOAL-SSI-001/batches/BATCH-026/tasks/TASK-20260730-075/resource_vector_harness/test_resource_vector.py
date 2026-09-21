"""Unit tests for symbolic Q/S/P/C(+H) resource-vector ledger consistency."""

from __future__ import annotations

import unittest

from .ledger_checks import (
    EXPECTED_FIELD_STATUS,
    check_classification,
    check_forbidden_clearance_flags,
    check_memory_map_status,
    check_mutation_status,
    check_resource_vector_ledger,
)


class TestResourceVectorLedger(unittest.TestCase):
    def test_field_statuses_match_expected(self) -> None:
        report = check_resource_vector_ledger()
        self.assertTrue(report["all_field_checks_passed"])
        for check in report["checks"]:
            self.assertEqual(
                check["status"],
                EXPECTED_FIELD_STATUS[check["field"]],
            )
            self.assertIs(check["joint_finiteness_established"], False)
            self.assertEqual(check["numeric_width"], "not_invented")

    def test_package_ok_no_clearance(self) -> None:
        report = check_resource_vector_ledger()
        self.assertTrue(report["package_ok"])
        self.assertEqual(report["resource_vector_status"], "resource_vector_partial")
        self.assertIs(report["query_memory_cleared"], False)
        self.assertIs(report["qm_stopping_cleared"], False)
        self.assertIs(report["tau_invented"], False)
        self.assertIs(report["numeric_widths_invented"], False)
        self.assertIs(report["joint_finiteness_established"], False)


class TestMemoryMapAndClassification(unittest.TestCase):
    def test_memory_map_advancement_without_clearance(self) -> None:
        report = check_memory_map_status()
        self.assertTrue(report["passed"])
        self.assertEqual(report["prior_status"], "peak_liveset_partial")
        self.assertEqual(report["status_after_batch"], "resource_vector_partial")
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
        self.assertEqual(report["qm_memory_map"], "resource_vector_partial")
        self.assertEqual(report["qm_error"], "f_union_ledger_partial")
        self.assertIs(report["non_extrapolation"], True)

    def test_mutation_scaffold_untouched(self) -> None:
        report = check_mutation_status()
        self.assertTrue(report["passed"])
        self.assertIs(report["scaffold_mutated"], False)
        self.assertEqual(report["qm_memory_map_after"], "resource_vector_partial")
        self.assertEqual(report["qm_error_after"], "f_union_ledger_partial")

    def test_no_forbidden_true_clearance_flags(self) -> None:
        report = check_forbidden_clearance_flags()
        self.assertEqual(report["forbidden_true_hits"], [])
        self.assertTrue(report["passed"])


if __name__ == "__main__":
    unittest.main()

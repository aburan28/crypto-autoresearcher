"""Unit tests for symbolic global memory-bound obligation schema ledger."""

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
        self.assertEqual(report["family_counts"]["composition_surface"], EXPECTED_COUNTS["composition_surface_family"])
        self.assertEqual(report["family_counts"]["charge_metering_feed"], EXPECTED_COUNTS["charge_metering_feed_family"])
        self.assertEqual(report["family_counts"]["peak_byte_bound_feed"], EXPECTED_COUNTS["peak_byte_bound_feed_family"])
        self.assertEqual(report["family_counts"]["peak_liveset_feed"], EXPECTED_COUNTS["peak_liveset_feed_family"])
        self.assertEqual(report["family_counts"]["global_bound_field_placeholder"], EXPECTED_COUNTS["global_bound_field_placeholder_family"])
        self.assertEqual(report["family_counts"]["lineage_cross_link"], EXPECTED_COUNTS["lineage_cross_link_family"])
        self.assertEqual(report["status_counts"]["wired_symbolic"], EXPECTED_COUNTS["wired_symbolic"])
        self.assertEqual(report["status_counts"]["not_instantiated"], EXPECTED_COUNTS["not_instantiated"])
        self.assertEqual(report["status_counts"]["not_supported"], EXPECTED_COUNTS["not_supported"])

    def test_package_ok_fail_no_clearance(self) -> None:
        report = check_obligation_ledger()
        self.assertTrue(report["package_ok"])
        self.assertEqual(report["ledger_status"], "global_memory_bound_schema_partial")
        self.assertEqual(report["control_result"], "FAIL")
        self.assertEqual(report["charge_metering_schema_partial_retained"], "charge_metering_schema_partial")
        self.assertEqual(report["peak_byte_bound_schema_partial_retained"], "peak_byte_bound_schema_partial")
        self.assertIs(report["query_memory_cleared"], False)
        self.assertIs(report["qm_stopping_cleared"], False)
        self.assertIs(report["global_memory_bound_invented"], False)
        self.assertIs(report["tau_invented"], False)

    def test_no_invented_numerics_in_ledger(self) -> None:
        report = check_no_invented_numerics()
        self.assertEqual(report["hits"], [])
        self.assertTrue(report["passed"])


class TestMemoryMapAndClassification(unittest.TestCase):
    def test_memory_map_advanced_without_clearance(self) -> None:
        report = check_memory_map_status()
        self.assertTrue(report["passed"])
        self.assertEqual(report["prior_status"], "charge_metering_schema_partial")
        self.assertEqual(report["status_after_batch"], "global_memory_bound_schema_partial")
        self.assertIs(report["clearance"], False)
        self.assertIs(report["query_memory_cleared"], False)

    def test_classification_disposition_and_qm_statuses(self) -> None:
        report = check_classification()
        self.assertTrue(report["passed"])
        self.assertEqual(report["disposition"], "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED")

    def test_mutation_status(self) -> None:
        report = check_mutation_status()
        self.assertTrue(report["passed"])


class TestForbiddenFlags(unittest.TestCase):
    def test_no_forbidden_clearance_true(self) -> None:
        report = check_forbidden_clearance_flags()
        self.assertTrue(report["passed"])


class TestScaffold(unittest.TestCase):
    def test_scaffold_read_only(self) -> None:
        report = check_scaffold_read_only()
        self.assertTrue(report["passed"])

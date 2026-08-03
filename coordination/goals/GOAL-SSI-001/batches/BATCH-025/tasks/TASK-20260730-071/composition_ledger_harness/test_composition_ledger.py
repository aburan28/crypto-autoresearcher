"""Unit tests for symbolic F-union / operational-error composition ledger."""

from __future__ import annotations

import unittest

from .composition_rules import COMPOSITION_STRUCTURE, check_composition_structure
from .membership_rules import (
    CONSTITUENTS,
    check_membership_ledger,
    classify_exit,
    member_of_union,
    symbolic_union,
)


class TestMembershipRules(unittest.TestCase):
    def test_seven_constituents_in_union(self) -> None:
        u = symbolic_union()
        self.assertEqual(sorted(u), sorted(CONSTITUENTS))
        for cid in CONSTITUENTS:
            self.assertTrue(member_of_union(cid, u))

    def test_f_sim_not_in_union(self) -> None:
        self.assertFalse(member_of_union("F_sim"))
        report = check_membership_ledger()
        self.assertFalse(report["f_sim"]["member_of_symbolic_union"])
        self.assertFalse(report["f_sim"]["maps_to_F"])

    def test_success_exit_verify_true(self) -> None:
        ok = classify_exit(verify_true_returned=True, channel=None)
        self.assertEqual(ok["exit_kind"], "success")
        self.assertFalse(ok["classified_as_common_F"])

    def test_failure_channel_in_common_f(self) -> None:
        for cid in CONSTITUENTS:
            out = classify_exit(verify_true_returned=False, channel=cid)
            self.assertEqual(out["exit_kind"], "failure")
            self.assertTrue(out["classified_as_common_F"])
            self.assertTrue(out["in_union"])

    def test_membership_ledger_passes(self) -> None:
        report = check_membership_ledger()
        self.assertTrue(report["all_membership_checks_passed"])
        self.assertFalse(report["probabilities_invented"])
        self.assertFalse(report["tau_invented"])
        self.assertFalse(report["query_memory_cleared"])


class TestCompositionStructure(unittest.TestCase):
    def test_composition_is_set_union_not_probability(self) -> None:
        self.assertEqual(
            COMPOSITION_STRUCTURE["kind"],
            "symbolic_set_union_under_common_event_F",
        )
        self.assertIn("probability_sum", COMPOSITION_STRUCTURE["not_kind"])

    def test_composition_structure_ok(self) -> None:
        report = check_composition_structure()
        self.assertTrue(report["composition_structure_ok"])
        self.assertEqual(report["status"], "f_union_ledger_partial")
        self.assertFalse(report["probabilities_invented"])
        self.assertFalse(report["security_bits_invented"])
        self.assertFalse(report["query_memory_cleared"])
        self.assertFalse(report["qm_stopping_cleared"])
        self.assertEqual(len(report["forbidden_claim_key_hits"]), 0)
        self.assertTrue(all(r["passed"] for r in report["checklist_results"]))


if __name__ == "__main__":
    unittest.main()

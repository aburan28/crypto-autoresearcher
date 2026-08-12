from __future__ import annotations

import copy
import unittest

from . import ledger_checks as checks


class TestPositive(unittest.TestCase):
    def test_criteria(self):
        r = checks.check_criteria_pre_registered()
        self.assertTrue(r["passed"], r["problems"])

    def test_ledger_outcome(self):
        r = checks.check_ledger_outcome()
        self.assertTrue(r["passed"], r["problems"])

    def test_md_block(self):
        r = checks.check_md_machine_block()
        self.assertTrue(r["passed"], r["problems"])

    def test_classification(self):
        r = checks.check_classification()
        self.assertTrue(r["passed"], r["problems"])

    def test_memory_map(self):
        r = checks.check_memory_map()
        self.assertTrue(r["passed"], r["problems"])

    def test_no_illicit_clearance(self):
        r = checks.check_no_illicit_clearance()
        self.assertTrue(r["passed"], r["hits"])

    def test_no_invented_closure(self):
        r = checks.check_no_invented_closure_flags()
        self.assertTrue(r["passed"], r["problems"])

    def test_citations_exist(self):
        r = checks.check_citations_exist()
        self.assertTrue(r["passed"], r["missing"])


class TestInjectionsRejected(unittest.TestCase):
    def test_reduction_exists_true_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["reduction_exists"] = True
        m["reduction_ledger"]["outcome"] = "reduction_exists"
        self.assertFalse(checks.check_ledger_outcome(m)["passed"])
        self.assertFalse(checks.check_no_invented_closure_flags(m)["passed"])

    def test_dependence_essential_true_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["dependence_essential_scoped"] = True
        m["reduction_ledger"]["named_obstruction"] = True
        m["reduction_ledger"]["meets_inventor_protocol_s4"] = True
        m["reduction_ledger"]["outcome"] = "dependence_essential_scoped"
        self.assertFalse(checks.check_no_invented_closure_flags(m)["passed"])

    def test_ninth_unverified_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["ninth_unverified_rerecord"] = True
        self.assertFalse(checks.check_ledger_outcome(m)["passed"])
        self.assertFalse(checks.check_no_invented_closure_flags(m)["passed"])

    def test_missing_revisit_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["revisit_conditions"] = []
        self.assertFalse(checks.check_ledger_outcome(m)["passed"])

    def test_fake_tau_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["tau_invented"] = True
        # also inject into retained_controls
        m["reduction_ledger"]["retained_controls"]["tau_invented"] = True
        self.assertFalse(checks.check_no_invented_closure_flags(m)["passed"])

    def test_illicit_clearance_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["query_memory"]["cleared"] = True
        # check_memory_map catches cleared
        self.assertFalse(checks.check_memory_map(m)["passed"])

    def test_memory_map_advance_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["qm_memory_map"]["advanced_this_batch"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])

    def test_local_prop_discharges_r_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["reduction_ledger"]["candidate_properties_audited"][3]["discharges_outcome_R"] = True
        self.assertFalse(checks.check_ledger_outcome(m)["passed"])

    def test_disposition_drift_rejected(self):
        m = copy.deepcopy(checks.load_classification())
        m["classification"]["disposition"] = "QUERY_MEMORY_CLEARED"
        self.assertFalse(checks.check_classification(m)["passed"])

    def test_md_block_outcome_drift_rejected(self):
        md = checks.load_reduction_md().replace(
            "REDUCTION_OUTCOME: neither_pause",
            "REDUCTION_OUTCOME: reduction_exists",
        )
        self.assertFalse(checks.check_md_machine_block(md)["passed"])

    def test_gate_b_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["gate_B_taken"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])

    def test_api_invention_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["collimation_sieve_apis_invented"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])

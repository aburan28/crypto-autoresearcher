from __future__ import annotations

import copy
import unittest

from . import ledger_checks as checks


class TestPositive(unittest.TestCase):
    def test_criteria(self):
        r = checks.check_criteria_pre_registered()
        self.assertTrue(r["passed"], r["problems"])

    def test_obligation_ledger(self):
        r = checks.check_obligation_ledger()
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

    def test_not_relabel_only(self):
        r = checks.check_not_relabel_only()
        self.assertTrue(r["passed"], r["problems"])

    def test_no_host_level_exhaustiveness(self):
        r = checks.check_no_host_level_exhaustiveness_claim()
        self.assertTrue(r["passed"], r["problems"])

    def test_no_illicit_clearance(self):
        r = checks.check_no_illicit_clearance()
        self.assertTrue(r["passed"], r["hits"])

    def test_no_invented_numerics(self):
        r = checks.check_no_invented_numerics()
        self.assertTrue(r["passed"], r["hits"])

    def test_citations_exist(self):
        r = checks.check_citations_exist()
        self.assertTrue(r["passed"], r["missing"])


class TestInjectionsRejected(unittest.TestCase):
    def test_qm_error_cleared_rejected(self):
        m = copy.deepcopy(checks.load_classification())
        m["classification"]["qm_error_advancement"]["qm_error_cleared"] = True
        self.assertFalse(checks.check_classification(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance([m])["passed"])

    def test_invented_probability_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["f_union_obligation_ledger"]["obligations"][3]["probability_estimate"] = 0.5
        self.assertFalse(checks.check_no_invented_numerics([m])["passed"])

    def test_probability_assigned_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["f_union_obligation_ledger"]["obligations"][3]["probability_assigned"] = True
        self.assertFalse(checks.check_obligation_ledger(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance([m])["passed"])

    def test_host_level_exhaustiveness_smuggled_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        obl2b = next(o for o in m["f_union_obligation_ledger"]["obligations"] if o["id"] == "OBL-2b")
        obl2b["status"] = "wired_symbolic"
        self.assertFalse(checks.check_no_host_level_exhaustiveness_claim(m)["passed"])

    def test_fake_tau_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["qm_stopping"]["tau_invented"] = True
        self.assertFalse(checks.check_no_illicit_clearance([m])["passed"])

    def test_missing_revisit_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["f_union_obligation_ledger"]["revisit_conditions"] = []
        self.assertFalse(checks.check_obligation_ledger(m)["passed"])

    def test_relabel_only_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["f_union_obligation_ledger"]["prior_status"]["reverse_inclusion_recorded"] = True
        self.assertFalse(checks.check_not_relabel_only(m, checks.load_classification())["passed"])

    def test_two_tightened_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        obl1 = next(o for o in m["f_union_obligation_ledger"]["obligations"] if o["id"] == "OBL-1")
        obl1["status"] = "tightened_from_committed_structure"
        obl1["tightened_this_batch"] = True
        self.assertFalse(checks.check_obligation_ledger(m)["passed"])

    def test_disposition_drift_rejected(self):
        m = copy.deepcopy(checks.load_classification())
        m["classification"]["disposition"] = "QUERY_MEMORY_CLEARED"
        self.assertFalse(checks.check_classification(m)["passed"])

    def test_gate_b_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["gate_B_taken"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance([m])["passed"])

    def test_api_invention_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["collimation_sieve_apis_invented"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])

    def test_qm_stopping_reopen_rejected(self):
        m = copy.deepcopy(checks.load_memory_map())
        m["memory_map_status"]["qm_stopping"]["reopened_this_batch"] = True
        self.assertFalse(checks.check_memory_map(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance([m])["passed"])

    def test_md_outcome_drift_rejected(self):
        md = checks.load_md().replace(
            "QM_ERROR_OUTCOME: f_union_tightened",
            "QM_ERROR_OUTCOME: qm_error_cleared",
        )
        self.assertFalse(checks.check_md_machine_block(md)["passed"])

    def test_invalid_status_rejected(self):
        m = copy.deepcopy(checks.load_ledger())
        m["f_union_obligation_ledger"]["obligations"][0]["status"] = "cleared"
        self.assertFalse(checks.check_obligation_ledger(m)["passed"])

    def test_is_relabel_only_true_rejected(self):
        m = copy.deepcopy(checks.load_classification())
        m["classification"]["qm_error_advancement"]["is_relabel_only"] = True
        self.assertFalse(checks.check_not_relabel_only(checks.load_ledger(), m)["passed"])
        self.assertFalse(checks.check_classification(m)["passed"])

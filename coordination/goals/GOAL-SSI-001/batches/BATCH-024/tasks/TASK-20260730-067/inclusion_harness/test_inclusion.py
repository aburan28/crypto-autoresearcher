"""Unit tests for path-justified F_* ⊆ F and honest F_sim treatment."""

from __future__ import annotations

import unittest

from .f_sim_probe import probe_f_sim_treatment
from .path_probe import probe_path_justified_inclusions
from .procedure_driver import ScaffoldProcedure


class TestSuccessControl(unittest.TestCase):
    def test_success_returns_verify_true(self):
        outcome = ScaffoldProcedure().run_success_control()
        self.assertEqual(outcome.exit_kind, "success")
        self.assertTrue(outcome.verify_true_returned)
        self.assertFalse(outcome.classified_as_common_F)


class TestPathJustifiedInclusions(unittest.TestCase):
    def test_all_seven_path_justified_on_scaffold(self):
        report = probe_path_justified_inclusions()
        self.assertTrue(report["success_control"]["passed"])
        self.assertTrue(report["summary"]["all_constituents_path_justified_on_scaffold"])
        self.assertEqual(report["summary"]["composition_status"], "path_justified_partial")
        self.assertFalse(report["summary"]["qm_error_cleared"])
        self.assertFalse(report["summary"]["query_memory_cleared"])
        self.assertFalse(report["summary"]["tau_invented"])
        self.assertFalse(report["summary"]["crypto_verify_implemented"])
        ids = {c["id"] for c in report["constituents"]}
        self.assertEqual(
            ids,
            {
                "F_input",
                "F_oracle",
                "F_cleanup",
                "F_stop",
                "F_recovery",
                "F_tail",
                "F_verify",
            },
        )
        for c in report["constituents"]:
            self.assertEqual(c["status"], "path_justified_on_scaffold")
            self.assertTrue(c["checks"]["path_justified"])
            self.assertTrue(c["outcome"]["classified_as_common_F"])
            self.assertFalse(c["outcome"]["verify_true_returned"])
            self.assertFalse(c["justified_by_implemented_end_to_end_crypto_path"])
            self.assertFalse(c["probability_bounds"])

    def test_f_stop_does_not_clear_qm_stopping(self):
        report = probe_path_justified_inclusions()
        stop = next(c for c in report["constituents"] if c["id"] == "F_stop")
        self.assertFalse(stop["tau_invented"])
        self.assertFalse(stop["qm_stopping_cleared"])
        self.assertTrue(stop["tau_invention_rejected"])


class TestFSimHonesty(unittest.TestCase):
    def test_local_channel_no_map_to_F(self):
        report = probe_f_sim_treatment()
        self.assertTrue(report["scaffold_local_channel_wired"])
        self.assertFalse(report["batch022_FailureChannel_enum_has_F_sim"])
        self.assertFalse(report["maps_to_F"])
        self.assertEqual(
            report["map_status"], "no_implementation_derived_implication"
        )
        self.assertFalse(report["query_memory_cleared_by_f_sim"])
        self.assertTrue(report["illicit_F_sim_to_F_map_refused"])
        self.assertTrue(report["paths"]["incomplete_report"]["in_F_sim"])
        self.assertFalse(report["paths"]["complete_report_F_sim_complement"]["in_F_sim"])
        self.assertFalse(report["paths"]["complete_report_F_sim_complement"]["maps_to_F"])


if __name__ == "__main__":
    unittest.main()

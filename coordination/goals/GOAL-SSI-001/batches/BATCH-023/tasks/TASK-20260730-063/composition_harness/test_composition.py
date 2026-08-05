"""Unit tests for F_* composition and peak live-set probes."""

from __future__ import annotations

import unittest

from .f_star_probe import probe_f_star_channels
from .peak_live_set_probe import probe_peak_live_sets


class TestFStarComposition(unittest.TestCase):
    def test_all_constituents_wired(self):
        report = probe_f_star_channels()
        self.assertTrue(report["summary"]["all_recovery_spec_constituents_channel_wired"])
        self.assertFalse(report["summary"]["any_inclusion_into_common_F_justified"])
        self.assertFalse(report["summary"]["f_sim_to_F_map_exists"])
        self.assertEqual(report["summary"]["composition_status"], "fstar_composition_partial")
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

    def test_no_tau_and_f_sim_honesty(self):
        report = probe_f_star_channels()
        self.assertFalse(report["summary"]["tau_invented"])
        self.assertFalse(report["f_sim"]["maps_to_F"])
        stop = next(c for c in report["constituents"] if c["id"] == "F_stop")
        self.assertFalse(stop["qm_stopping_cleared"])


class TestPeakLiveSet(unittest.TestCase):
    def test_stage_membership_and_peak_max(self):
        report = probe_peak_live_sets()
        self.assertTrue(report["stage_live_sets_checklist_matches_recovery_spec"])
        self.assertTrue(report["summary"]["all_stage_membership_checks_passed"])
        self.assertTrue(report["summary"]["symbolic_membership_checks_supported"])
        self.assertFalse(report["summary"]["numeric_widths_invented"])
        self.assertEqual(report["summary"]["peak_liveset_status"], "peak_liveset_partial")
        peak = report["peak"]
        self.assertTrue(peak["mistaken_sum_rejected_as_peak"])
        self.assertGreater(
            peak["mistaken_sum_of_stage_counts"], peak["peak_symbolic_object_count"]
        )
        self.assertEqual(peak["numeric_widths"], "not_invented")

    def test_api_support_flags(self):
        report = probe_peak_live_sets()
        api = report["scaffold_api_support"]
        self.assertTrue(api["live_subset_of_stage"])
        self.assertTrue(api["required_members_present"])
        self.assertFalse(api["numeric_widths_supported"])
        self.assertFalse(api["peak_byte_bound_supported"])


if __name__ == "__main__":
    unittest.main()

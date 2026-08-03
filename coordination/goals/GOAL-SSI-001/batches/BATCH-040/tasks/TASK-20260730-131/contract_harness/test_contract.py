from __future__ import annotations
import copy
import unittest

from . import ledger_checks as checks


def _first_hook(c, hook_id):
    for h in c["width_emission_hooks"]:
        if h["hook_id"] == hook_id:
            return h
    raise KeyError(hook_id)


class TestPositive(unittest.TestCase):
    """The real produced artifacts must pass every check."""

    def setUp(self):
        self.c = checks.load_contract()
        self.p = checks.load_plan()

    def test_contract_fields_present(self):
        r = checks.check_contract_fields_present(self.c)
        self.assertTrue(r["passed"], r["problems"])

    def test_hook_width_channels(self):
        self.assertTrue(checks.check_hook_width_channels(self.c)["passed"])

    def test_all_real_widths_null(self):
        r = checks.check_all_real_widths_null(self.c)
        self.assertTrue(r["passed"], r["problems"])

    def test_no_invented_numerics(self):
        r = checks.check_no_invented_numerics(self.c)
        self.assertTrue(r["passed"], r["hits"])

    def test_pin_untouched(self):
        self.assertTrue(checks.check_pin_untouched(self.c)["passed"])

    def test_stage_membership_matches_scaffold(self):
        self.assertTrue(checks.check_stage_membership_matches_scaffold(self.c)["passed"])

    def test_no_illicit_clearance(self):
        r = checks.check_no_illicit_clearance(self.c)
        self.assertTrue(r["passed"], r)

    def test_validation_plan(self):
        r = checks.check_validation_plan(self.p)
        self.assertTrue(r["passed"], r["problems"])

    def test_sibling_status_files(self):
        self.assertTrue(checks.check_memory_map_status()["passed"])
        self.assertTrue(checks.check_classification()["passed"])

    def test_obstruction_analysis(self):
        r = checks.check_obstruction_analysis()
        self.assertTrue(r["passed"], r["problems"])


class TestInjectionsRejected(unittest.TestCase):
    """Every invented / out-of-protocol / illicit mutation must be rejected."""

    def setUp(self):
        self.c = checks.load_contract()
        self.p = checks.load_plan()

    def test_invented_real_width_value_rejected(self):
        m = copy.deepcopy(self.c)
        _first_hook(m, "W_label")["real_per_slot_width"]["value"] = 8
        self.assertFalse(checks.check_all_real_widths_null(m)["passed"])
        self.assertFalse(checks.check_no_invented_numerics(m)["passed"])

    def test_invented_real_units_rejected(self):
        m = copy.deepcopy(self.c)
        _first_hook(m, "M_tail")["real_per_slot_width"]["units"] = "qubits"
        self.assertFalse(checks.check_all_real_widths_null(m)["passed"])

    def test_invented_numeric_peak_rejected(self):
        m = copy.deepcopy(self.c)
        m["composition_operator"]["peak"]["value"] = 24
        self.assertFalse(checks.check_all_real_widths_null(m)["passed"])
        self.assertFalse(checks.check_no_invented_numerics(m)["passed"])

    def test_invented_bound_units_rejected(self):
        m = copy.deepcopy(self.c)
        m["composition_operator"]["bound_units"] = "protocol_slot_bytes"
        self.assertFalse(checks.check_all_real_widths_null(m)["passed"])

    def test_source_marked_available_rejected(self):
        m = copy.deepcopy(self.c)
        _first_hook(m, "B_input")["real_per_slot_width"]["source_available"] = True
        self.assertFalse(checks.check_all_real_widths_null(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_out_of_protocol_hook_rejected(self):
        m = copy.deepcopy(self.c)
        m["width_emission_hooks"].append({
            "hook_id": "INVENTED_HOOK", "object_class": "B",
            "live_in_stages": ["preparation"], "birth_signature_ref": "x",
            "real_per_slot_width": {"value": None, "units": None,
                                    "sourced_from": "x", "source_available": False},
        })
        self.assertFalse(checks.check_contract_fields_present(m)["passed"])

    def test_out_of_protocol_stage_member_rejected(self):
        m = copy.deepcopy(self.c)
        m["stage_live_sets"]["recovery"].append("INVENTED_SLOT")
        self.assertFalse(checks.check_stage_membership_matches_scaffold(m)["passed"])

    def test_invented_security_bits_rejected(self):
        m = copy.deepcopy(self.c)
        m["security_bits"] = 128
        self.assertFalse(checks.check_no_invented_numerics(m)["passed"])

    def test_width_channel_added_to_wrong_hook_rejected(self):
        m = copy.deepcopy(self.c)
        _first_hook(m, "W_label")["width_emission_point_exists_in_scaffold"] = True
        self.assertFalse(checks.check_hook_width_channels(m)["passed"])

    def test_m_tail_channel_removed_rejected(self):
        m = copy.deepcopy(self.c)
        _first_hook(m, "M_tail")["width_emission_point_exists_in_scaffold"] = False
        self.assertFalse(checks.check_hook_width_channels(m)["passed"])

    def test_illicit_query_memory_cleared_rejected(self):
        m = copy.deepcopy(self.c)
        m["query_memory_cleared"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_novel_clearance_like_key_rejected(self):
        # RT-20260730-129 OBJ-1 hardening: a novel truthy clearance-like key.
        m = copy.deepcopy(self.c)
        m["host"]["query_memory_solved"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_cryptographic_scale_relabel_rejected(self):
        m = copy.deepcopy(self.c)
        m["cryptographic_scale"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_disposition_downgrade_rejected(self):
        m = copy.deepcopy(self.c)
        m["disposition"] = "FC0_QUERY_MEMORY_CLEARED"
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_pin_tamper_rejected(self):
        m = copy.deepcopy(self.c)
        m["host"]["commit"] = "0000000000000000000000000000000000000000"
        self.assertFalse(checks.check_pin_untouched(m)["passed"])

    def test_apis_invented_rejected(self):
        m = copy.deepcopy(self.c)
        m["host"]["apis_invented"] = True
        self.assertFalse(checks.check_pin_untouched(m)["passed"])

    def test_admissible_pin_flip_rejected(self):
        m = copy.deepcopy(self.c)
        m["host"]["admissible_pin"] = True
        self.assertFalse(checks.check_pin_untouched(m)["passed"])

    def test_operator_id_tamper_rejected(self):
        m = copy.deepcopy(self.c)
        m["composition_operator"]["id"] = "invented_operator"
        self.assertFalse(checks.check_contract_fields_present(m)["passed"])

    def test_scaffold_modified_flag_rejected(self):
        m = copy.deepcopy(self.c)
        m["batch022_scaffold_modified"] = True
        self.assertFalse(checks.check_pin_untouched(m)["passed"])
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_plan_measurement_performed_rejected(self):
        m = copy.deepcopy(self.p)
        m["measurement_performed"] = True
        self.assertFalse(checks.check_validation_plan(m)["passed"])

    def test_plan_no_falsification_rejected(self):
        m = copy.deepcopy(self.p)
        m["falsification_conditions"] = []
        self.assertFalse(checks.check_validation_plan(m)["passed"])

    def test_plan_missing_null_control_rejected(self):
        m = copy.deepcopy(self.p)
        m["controls_before_belief"] = {}
        self.assertFalse(checks.check_validation_plan(m)["passed"])

    def test_obstruction_closure_overclaim_rejected(self):
        overclaim = (
            "OBSTRUCTION_ANALYSIS_STATUS: closed\n"
            "obstruction proven; QM-STOPPING CLEARED. Candidate obstruction. "
            "Forward guidance. fatigue."
        )
        self.assertFalse(checks.check_obstruction_analysis(overclaim)["passed"])

    def test_obstruction_missing_forward_guidance_rejected(self):
        bad = (
            "OBSTRUCTION_ANALYSIS_STATUS: unverified\n"
            "named_obstruction: false\nmeets_inventor_protocol_s4: false\n"
            "is_closure_claim: false\nqm_stopping_control_result: FAIL\n"
            "Candidate obstruction. fatigue."
        )
        self.assertFalse(checks.check_obstruction_analysis(bad)["passed"])

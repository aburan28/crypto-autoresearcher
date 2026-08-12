import copy
import unittest

from . import ledger_checks as checks


class TestPositive(unittest.TestCase):
    """The real ledger must pass every check."""

    def setUp(self):
        self.led = checks.load_ledger()

    def test_composition_numerics(self):
        r = checks.check_composition_numerics(self.led)
        self.assertTrue(r["passed"], r.get("problems"))
        self.assertEqual(r["recomputed"]["peak_byte_bound"], 24)
        self.assertEqual(r["recomputed"]["peak_stage"], "tail_verification")
        self.assertEqual(r["recomputed"]["mistaken_sum"], 67)

    def test_key_sets(self):
        self.assertTrue(checks.check_key_sets(self.led)["passed"])

    def test_no_invented_numerics(self):
        r = checks.check_no_invented_numerics(self.led)
        self.assertTrue(r["passed"], r["hits"])

    def test_no_illicit_clearance(self):
        r = checks.check_no_illicit_clearance(self.led)
        self.assertTrue(r["passed"], r)

    def test_gate_and_status(self):
        self.assertTrue(checks.check_gate_and_status(self.led)["passed"])

    def test_qm_stopping_retained(self):
        self.assertTrue(checks.check_qm_stopping_retained(self.led)["passed"])

    def test_cross_batch023(self):
        self.assertTrue(checks.check_cross_batch023(self.led)["passed"])

    def test_sibling_status_files(self):
        self.assertTrue(checks.check_memory_map_status()["passed"])
        self.assertTrue(checks.check_classification()["passed"])
        self.assertTrue(checks.check_mutation_status()["passed"])


class TestInjectionsRejected(unittest.TestCase):
    """Every out-of-protocol / invented / illicit mutation must be rejected."""

    def setUp(self):
        self.led = checks.load_ledger()

    def test_wrong_peak_byte_value_rejected(self):
        m = copy.deepcopy(self.led)
        m["peak_byte_bound"]["value"] = 999
        self.assertFalse(checks.check_composition_numerics(m)["passed"])

    def test_out_of_protocol_slot_width_rejected(self):
        m = copy.deepcopy(self.led)
        m["slot_width_table"]["W"] = 1000
        self.assertFalse(checks.check_composition_numerics(m)["passed"])

    def test_tampered_stage_load_rejected(self):
        m = copy.deepcopy(self.led)
        m["stage_byte_loads"]["recovery"] = 9999
        self.assertFalse(checks.check_composition_numerics(m)["passed"])

    def test_out_of_protocol_member_rejected(self):
        m = copy.deepcopy(self.led)
        m["stage_membership"]["recovery"].append("INVENTED_SLOT")
        self.assertFalse(checks.check_composition_numerics(m)["passed"])

    def test_invented_security_bits_field_rejected(self):
        m = copy.deepcopy(self.led)
        m["security_bits"] = 128
        self.assertFalse(checks.check_no_invented_numerics(m)["passed"])

    def test_invented_numeric_under_allowed_container_rejected(self):
        # Smuggle an extra numeric key inside slot_width_table; the key-set
        # check must catch it even though the provenance scan allows the parent.
        m = copy.deepcopy(self.led)
        m["slot_width_table"]["security_bits"] = 256
        self.assertFalse(checks.check_key_sets(m)["passed"])

    def test_illicit_query_memory_clearance_rejected(self):
        m = copy.deepcopy(self.led)
        m["honesty"]["query_memory_cleared"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_illicit_top_level_clearance_flag_rejected(self):
        m = copy.deepcopy(self.led)
        m["query_memory_clearance"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_pin_complete_flag_rejected(self):
        m = copy.deepcopy(self.led)
        m["honesty"]["pin_complete"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_breakthrough_claim_rejected(self):
        m = copy.deepcopy(self.led)
        m["honesty"]["breakthrough_claim"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_cryptographic_scale_relabel_rejected(self):
        m = copy.deepcopy(self.led)
        m["cryptographic_scale"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_disposition_downgrade_rejected(self):
        m = copy.deepcopy(self.led)
        m["summary"]["disposition"] = "FC0_QUERY_MEMORY_CLEARED"
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_faked_tau_finiteness_rejected(self):
        m = copy.deepcopy(self.led)
        m["qm_stopping_negative_control"]["control_result"] = "PASS"
        self.assertFalse(checks.check_qm_stopping_retained(m)["passed"])

    def test_invented_tau_flag_rejected(self):
        m = copy.deepcopy(self.led)
        m["qm_stopping_negative_control"]["tau_invented"] = True
        self.assertFalse(checks.check_no_illicit_clearance(m)["passed"])

    def test_status_overclaim_rejected(self):
        m = copy.deepcopy(self.led)
        m["summary"]["instantiation_status"] = "query_memory_cleared"
        self.assertFalse(checks.check_gate_and_status(m)["passed"])

"""Software checks and hand-derived controls; this is not the candidate screen."""
import ast
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from verify import OracleGroup, group_obligations, public_gate, retained_bit_reduction, truth_half, validate_fresh_recovery, verify_records, wrong_root

MODEL = {"p": 11, "a": 1, "b": 6, "r": 13}
BASE = (2, 7)
HARD_ORBIT = [None, (2, 7), (5, 2), (8, 3), (10, 2), (3, 6), (7, 9), (7, 2), (3, 5), (10, 9), (8, 8), (5, 9), (2, 4)]


def record(*, target, result, kind="candidate", alpha=0, beta=1, suffix="1", model=None, base=None, scale=1):
    model = dict(MODEL if model is None else model)
    base = BASE if base is None else base
    arm = {"id": f"{kind}:a{alpha}:b{beta}", "kind": kind}
    if kind != "wrong_root":
        arm.update(alpha_integer=alpha, beta_integer=beta, alpha=alpha % model["p"], beta=beta % model["p"])
    else:
        arm.update(id="wrong_root:anchored_power_root", alpha_integer=None, beta_integer=None, alpha=None, beta=None)
    if kind == "aa_replay":
        arm["reference_id"] = "candidate:a0:b1"
    return {
        "schema": "nongeneric.case/v1", "case_id": "software-case-" + suffix,
        "group_id": f"software-group-{scale}-{base}-{kind}-{alpha}-{beta}",
        "model": model, "scale_u": scale, "base": list(base),
        "target": None if target is None else list(target), "arm": arm,
        "source_fingerprint": "a" * 64, "protocol_sha256": "b" * 64,
        "result": result, "counters": {"setup": {"software_stub": 1}, "evaluate": {"software_stub": 1}},
        "setup_charged": target is None,
    }


class IndependentOracleTests(unittest.TestCase):
    def test_public_group_matches_hand_orbit_including_identity_and_negatives(self):
        oracle = OracleGroup(MODEL)
        self.assertEqual(oracle.orbit(BASE), HARD_ORBIT)
        self.assertEqual(oracle.add(BASE, oracle.neg(BASE)), None)
        self.assertEqual(oracle.slope(BASE, oracle.neg(BASE)), 0)
        self.assertEqual(oracle.slope(None, BASE), 0)

    def test_linear_primitive_matches_selected_hand_values_and_charges_every_term(self):
        oracle = OracleGroup(MODEL)
        orbit = oracle.orbit(BASE)
        for target, expected in [(None, 0), (BASE, 3), ((8, 3), 8), ((2, 4), 8)]:
            self.assertEqual(oracle.primitive(target, orbit), expected)
        self.assertEqual(oracle.counts["primitive_oracle_queries"], 4)
        self.assertEqual(oracle.counts["primitive_oracle_terms"], 4 * 13)

    def test_wrong_root_is_anchored_but_has_the_hand_counterexample(self):
        oracle = OracleGroup(MODEL)
        at_base = wrong_root(oracle, BASE, BASE)
        at_three = wrong_root(oracle, BASE, (8, 3))
        self.assertEqual((at_base["root"], at_base["bit"]), (7, 0))
        self.assertEqual((at_three["root"], at_three["bit"]), (8, 1))
        self.assertEqual(at_three["root"]**2 % 11, 3**2 % 11)
        self.assertEqual(truth_half(3, 13), 0)

    def test_validator_truth_half_has_exact_pulses_and_recovers_all_thirteen(self):
        oracle = OracleGroup(MODEL)
        # Explicit positive-control truth bits; never offered to a constructor.
        bits = dict(zip(HARD_ORBIT, [0] * 7 + [1] * 6))
        checks = group_obligations(oracle, BASE, HARD_ORBIT, bits)
        self.assertTrue(checks["ordering_pass"])
        self.assertEqual(checks["two_pulse_residual"], [0] * 13)
        self.assertEqual(checks["retained_bit_reduction_verified_count"], 13)
        self.assertTrue(checks["retained_bit_reduction_pass"])
        self.assertEqual([entry["scalar"] for entry in checks["retained_bit_reductions"]], list(range(13)))
        self.assertFalse(checks["actual_recovery_attempted"])
        self.assertTrue(all(entry["predicate_evaluations"] == 0 and entry["oracle_table_verifier_only"] for entry in checks["retained_bit_reductions"]))

    def test_recovery_rejects_a_corrupted_bit_without_truth_fallback(self):
        oracle = OracleGroup(MODEL)
        bits = dict(zip(HARD_ORBIT, [0] * 7 + [1] * 6))
        bits[BASE] = 1
        answer = retained_bit_reduction(oracle, BASE, BASE, bits)
        self.assertFalse(answer["verified"])
        bits[BASE] = None
        self.assertEqual(retained_bit_reduction(oracle, BASE, BASE, bits)["status"], "UNDEFINED")

    def test_verifier_imports_no_candidate_arithmetic(self):
        tree = ast.parse(Path(__file__).with_name("verify.py").read_text())
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertNotIn("curve", imports)
        self.assertNotIn("constructor", imports)
        self.assertNotIn("compute", imports)


class StreamIntegrityTests(unittest.TestCase):
    def base_record(self):
        return record(target=BASE, result={"status": "BIT", "bit": 0, "reason": None, "z": 3, "g": 3, "anchor": 3, "normalized": 1})

    def test_anchor_tautology_passes_arithmetic_without_implying_screen_success(self):
        report = verify_records([self.base_record()])
        self.assertTrue(report["integrity_pass"], report["errors"])
        self.assertEqual(report["scope"], "software_subset_not_scientific_screen")
        self.assertEqual(report["expected_record_count"], 74880)
        self.assertFalse(report["arm_reports"][0]["finite_template_pass"])

    def test_zero_anchor_remains_undefined_even_at_identity(self):
        row = record(target=None, kind="invalid_anchor", alpha=-1, beta=1,
                     result={"status": "UNDEFINED", "bit": None, "reason": "ZERO_ANCHOR", "z": None, "g": None, "anchor": 0, "normalized": None})
        report = verify_records([row])
        self.assertTrue(report["integrity_pass"], report["errors"])
        self.assertEqual(report["group_reports"][0]["undefined_count"], 13)
        row["result"].update(status="BIT", bit=0, reason=None)
        bad = verify_records([row])
        self.assertFalse(bad["integrity_pass"])
        self.assertTrue(any(error.get("field") == "status" for error in bad["errors"]))

    def test_wrong_root_arithmetic_validity_is_separate_from_ordering_failure(self):
        row = record(target=(8, 3), kind="wrong_root",
                     result={"status": "BIT", "bit": 1, "reason": None, "z": None, "g": None, "anchor": 4, "normalized": None, "root": 8})
        report = verify_records([row])
        self.assertTrue(report["integrity_pass"], report["errors"])
        self.assertEqual(report["group_reports"][0]["truth_mismatch_count"], 1)
        self.assertFalse(report["group_reports"][0]["ordering_pass"])

    def test_corrupt_z_is_an_integrity_failure(self):
        row = self.base_record()
        row["result"]["z"] = 4
        report = verify_records([row])
        self.assertFalse(report["integrity_pass"])
        self.assertTrue(any(error.get("field") == "z" for error in report["errors"]))

    def test_duplicate_and_changed_hashes_fail(self):
        row = self.base_record()
        copied = deepcopy(row)
        copied["case_id"] += "-distinct-id"
        duplicate = verify_records([row, copied])
        self.assertFalse(duplicate["integrity_pass"])
        self.assertTrue(any("duplicate group-target" in error.get("error", "") for error in duplicate["errors"]))
        copied["target"] = None
        copied["setup_charged"] = True
        copied["result"] = {"status": "BIT", "bit": 0, "reason": None, "z": 0, "g": None, "anchor": 3, "normalized": None}
        copied["source_fingerprint"] = "c" * 64
        changed = verify_records([row, copied])
        self.assertFalse(changed["integrity_pass"])
        self.assertTrue(any("source fingerprint changed" in error.get("error", "") for error in changed["errors"]))

    def test_complete_mode_rejects_empty_stream_and_exact_protocol_mismatch(self):
        report = verify_records([], require_complete=True)
        self.assertFalse(report["integrity_pass"])
        self.assertEqual(report["missing_case_count"], 74880)
        mismatch = verify_records([self.base_record()], protocol_sha256="d" * 64)
        self.assertFalse(mismatch["integrity_pass"])
        self.assertTrue(any("exact protocol bytes" in error.get("error", "") for error in mismatch["errors"]))

    def test_aa_compares_outputs_and_operation_counters(self):
        original = self.base_record()
        replay = record(target=BASE, result=deepcopy(original["result"]), kind="aa_replay", suffix="replay")
        good = verify_records([original, replay])
        self.assertTrue(good["integrity_pass"], good["errors"])
        self.assertEqual(good["aa_pairs_checked"], 1)
        replay["counters"]["evaluate"]["software_stub"] += 1
        bad = verify_records([original, replay])
        self.assertFalse(bad["integrity_pass"])
        self.assertTrue(any(error.get("error") == "A/A mismatch" for error in bad["errors"]))

    def test_coordinate_covariance_checks_public_matching_inputs(self):
        original = record(target=BASE, kind="wrong_root",
                          result={"status": "BIT", "bit": 0, "reason": None, "z": None, "g": None, "anchor": 4, "normalized": None, "root": 7})
        scaled = record(target=(8, 1), kind="wrong_root", model={"p": 11, "a": 5, "b": 10, "r": 13}, base=(8, 1), scale=2, suffix="scaled",
                        result={"status": "BIT", "bit": 0, "reason": None, "z": None, "g": None, "anchor": 1, "normalized": None, "root": 1})
        report = verify_records([original, scaled])
        self.assertTrue(report["integrity_pass"], report["errors"])
        self.assertEqual(report["coordinate_pairs_checked"], 1)

    def test_exact_schema_arm_labels_and_setup_charge_are_enforced(self):
        mutations = [
            (lambda row: row.update(schema="other/v1"), "record schema"),
            (lambda row: row["arm"].update(id="renamed"), "noncanonical arm id"),
            (lambda row: row.update(setup_charged=True), "setup_charged"),
        ]
        for mutate, message in mutations:
            row = self.base_record()
            mutate(row)
            report = verify_records([row])
            self.assertFalse(report["integrity_pass"])
            self.assertTrue(any(message in error.get("error", "") for error in report["errors"]))

    def test_source_manifest_hash_binding_inside_official_protocol_envelope(self):
        row = self.base_record()
        official = {"extensions": {"nongeneric_screen": {"screen_plan": {"source_manifest_sha256": "a" * 64}}}}
        good = verify_records([row], official)
        self.assertTrue(good["integrity_pass"], good["errors"])
        official["extensions"]["nongeneric_screen"]["screen_plan"]["source_manifest_sha256"] = "c" * 64
        bad = verify_records([row], official)
        self.assertFalse(bad["integrity_pass"])
        self.assertTrue(any("source fingerprint does not match protocol" in error.get("error", "") for error in bad["errors"]))


class FreshRecoveryTraceTests(unittest.TestCase):
    """Synthetic instrument traces only; no candidate sweep or fitted circuit."""

    @staticmethod
    def synthetic_answer(target):
        scalar = HARD_ORBIT.index(target)
        return {"status": "BIT", "bit": int(scalar > 6), "reason": None,
                "z": None, "g": None, "anchor": None, "normalized": None}

    def synthetic_trace(self, target=HARD_ORBIT[2]):
        scalar = HARD_ORBIT.index(target)
        # The public sequence for default Q=2P is 2P,4P,8P,3P,6P.
        targets = [HARD_ORBIT[scalar * 2**index % 13] for index in range(5)]
        trace = [{"target": None if target is None else list(target), "answer": self.synthetic_answer(target),
                  "counters": {"synthetic_fresh_evaluation": 1}} for target in targets]
        return {"status": "RECOVERED", "scalar": scalar, "candidate_scalar": scalar, "reason": None,
                "predicate_calls": 5, "predicate_evaluations": 5, "retained_bit_reads": 0,
                "oracle_table_verifier_only": False, "predicate_trace": trace,
                "evaluate_counts": {"synthetic_fresh_evaluation": 5},
                "reduction_counts": {"synthetic_public_reduction": 1}}

    def test_fresh_trace_checks_doublings_bits_scalar_and_counter_sums(self):
        oracle = OracleGroup(MODEL)
        result = self.synthetic_trace()
        # Replace only the candidate arithmetic oracle for this software
        # instrument test. No truth bits enter any constructor implementation.
        with patch("verify.expected_result", side_effect=lambda _, __, target, ___, ____: self.synthetic_answer(target)):
            good = validate_fresh_recovery(oracle, BASE, HARD_ORBIT[2], {}, {}, result)
            self.assertTrue(good["pass"], good["errors"])
            self.assertEqual(good["predicate_evaluations"], 5)
            corrupted = deepcopy(result)
            corrupted["predicate_trace"][2]["target"] = list(BASE)
            bad = validate_fresh_recovery(oracle, BASE, HARD_ORBIT[2], {}, {}, corrupted)
            self.assertFalse(bad["pass"])
            self.assertTrue(any("doubling target" in message for message in bad["errors"]))
            corrupted = deepcopy(result)
            corrupted["candidate_scalar"] = 3
            corrupted["evaluate_counts"]["synthetic_fresh_evaluation"] = 4
            bad = validate_fresh_recovery(oracle, BASE, HARD_ORBIT[2], {}, {}, corrupted)
            self.assertFalse(bad["pass"])
            self.assertTrue(any("candidate_scalar" in message for message in bad["errors"]))
            self.assertTrue(any("counter sum" in message for message in bad["errors"]))

    def test_retained_table_metadata_cannot_masquerade_as_fresh_calls(self):
        result = self.synthetic_trace()
        result.update(retained_bit_reads=5, oracle_table_verifier_only=True)
        with patch("verify.expected_result", side_effect=lambda _, __, target, ___, ____: self.synthetic_answer(target)):
            checked = validate_fresh_recovery(OracleGroup(MODEL), BASE, HARD_ORBIT[2], {}, {}, result)
        self.assertFalse(checked["pass"])
        self.assertTrue(any("retained-bit reads" in message for message in checked["errors"]))

    def test_invalid_anchor_gate_records_skip_all_fresh_work(self):
        targets = [None] + sorted(HARD_ORBIT[1:])
        rows = [record(target=target, kind="invalid_anchor", alpha=-1, beta=1, suffix=str(index),
                       result={"status": "UNDEFINED", "bit": None, "reason": "ZERO_ANCHOR", "z": None, "g": None, "anchor": 0, "normalized": None})
                for index, target in enumerate(targets)]
        gate = public_gate(OracleGroup(MODEL), BASE, HARD_ORBIT, dict.fromkeys(targets), targets)
        gate.update(counters={"synthetic_gate": 1}, scalar_truth_access=False)
        recovery = {field: deepcopy(rows[0][field]) for field in ("group_id", "model", "scale_u", "base", "arm", "source_fingerprint", "protocol_sha256")}
        recovery.update(schema="nongeneric.recovery-group/v1", gate=gate, recoveries=[],
                        counters={"gate": gate["counters"], "fresh_setup": {}, "evaluate": {}, "reduction": {}},
                        predicate_evaluations=0, retained_bit_reads_in_recovery=0,
                        fresh_preparations=0, oracle_table_verifier_only=False)
        report = verify_records(rows, recovery_records=[recovery])
        self.assertTrue(report["integrity_pass"], report["errors"])
        self.assertEqual(report["actual_recovery_predicate_evaluations"], 0)
        self.assertEqual(report["actual_recovery_reports"][0]["not_attempted_reason"], "UNDEFINED_COVERAGE")
        self.assertFalse(report["group_reports"][0]["actual_recovery_attempted"])
        recovery["predicate_evaluations"] = 5
        bad = verify_records(rows, recovery_records=[recovery])
        self.assertFalse(bad["integrity_pass"])
        self.assertTrue(any("must not launch" in error.get("error", "") for error in bad["errors"]))

    def test_synthetic_passing_group_requires_every_fresh_trace(self):
        # This is a mock instrument test of the passing validation branch.
        # It creates no candidate result file and executes no candidate screen.
        targets = [None] + sorted(HARD_ORBIT[1:])
        rows = [record(target=target, result=self.synthetic_answer(target), suffix=str(index))
                for index, target in enumerate(targets)]
        bits = {target: self.synthetic_answer(target)["bit"] for target in targets}
        gate = public_gate(OracleGroup(MODEL), BASE, HARD_ORBIT, bits, targets)
        gate.update(counters={"synthetic_gate": 1}, scalar_truth_access=False)
        recovery = {field: deepcopy(rows[0][field]) for field in ("group_id", "model", "scale_u", "base", "arm", "source_fingerprint", "protocol_sha256")}
        recovery.update(schema="nongeneric.recovery-group/v1", gate=gate,
                        recoveries=[{"target": None if target is None else list(target), "result": self.synthetic_trace(target)} for target in targets],
                        counters={"gate": gate["counters"], "fresh_setup": rows[0]["counters"]["setup"],
                                  "evaluate": {"synthetic_fresh_evaluation": 65}, "reduction": {"synthetic_public_reduction": 13}},
                        predicate_evaluations=65, retained_bit_reads_in_recovery=0,
                        fresh_preparations=1, oracle_table_verifier_only=False)
        with patch("verify.expected_result", side_effect=lambda _, __, target, ___, ____: self.synthetic_answer(target)):
            good = verify_records(rows, recovery_records=[recovery])
            self.assertTrue(good["integrity_pass"], good["errors"])
            self.assertTrue(good["group_reports"][0]["actual_recovery_pass"])
            self.assertEqual(good["actual_recovery_verified_target_count"], 13)
            self.assertEqual(good["actual_recovery_predicate_evaluations"], 65)
            self.assertFalse(any(arm["finite_template_pass"] for arm in good["arm_reports"]))
            recovery["recoveries"][2]["result"]["predicate_trace"][0]["answer"]["bit"] ^= 1
            bad = verify_records(rows, recovery_records=[recovery])
            self.assertFalse(bad["integrity_pass"])
            self.assertFalse(bad["group_reports"][0]["actual_recovery_pass"])


if __name__ == "__main__":
    unittest.main()

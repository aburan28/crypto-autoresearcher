"""Fabricated record envelopes exercise integrity; candidate code never runs."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from independent import Group, Primitive, encoded, interval_candidate
import verify
from test_independent import BASE, MODEL, MULTIPLES


def synthetic_trace(scalar=3, multiplier=2, undefined_index=None):
    group = Group(MODEL)
    base_prime = group.mul(multiplier, BASE)
    target = group.mul(scalar, base_prime)
    labels = {group.mul(k, base_prime): k for k in range(13)}

    def synthetic_answer(primitive, base, current, alpha, beta):
        bit = int(labels[current] > 6)
        return {"status": "BIT", "bit": bit, "reason": None,
                "z": None, "g": None, "anchor": None, "normalized": None}

    trace, current, digits = [], target, []
    for index in range(5):
        answer = synthetic_answer(None, base_prime, current, 1, -4)
        if index == undefined_index:
            answer.update(status="UNDEFINED", bit=None, reason="SYNTHETIC_UNDEFINED")
        else:
            digits.append(answer["bit"])
        trace.append({"index": index, "target": encoded(current), "answer": answer, "counters": {"synthetic_call": 1}})
        current = group.add(current, current)
    success = undefined_index is None
    result = {"status": "RECOVERED" if success else "UNDEFINED",
              "reason": None if success else "SYNTHETIC_UNDEFINED",
              "candidate_scalar_prime": scalar if success else None,
              "candidate_scalar": multiplier*scalar % 13 if success else None,
              "scalar_prime": scalar if success else None,
              "scalar": multiplier*scalar % 13 if success else None,
              "L": 5, "predicate_evaluations": 5, "retained_bit_reads": 0,
              "predicate_trace": trace,
              "interval": {k: v for k, v in interval_candidate(13, digits).items() if k != "candidate"} if success else {"value": None, "denominator": 32, "lower_numerator": None, "upper_numerator": None, "nonempty": False},
              "target_multiplier_inverse": 1,
              "public_checks": {"transformed": True if success else None, "original": True if success else None},
              "counts": {"evaluate": {"synthetic_call": 5}, "reduction": {"synthetic_reduction": 1},
                         "blinding": {}, "conversion": {}}}

    def oracle(primitive, base, current, alpha, beta):
        if undefined_index is not None and current == tuple(trace[undefined_index]["target"]):
            return trace[undefined_index]["answer"]
        return synthetic_answer(primitive, base, current, alpha, beta)

    return group, Primitive(group, BASE), encoded(base_prime), encoded(target), result, oracle


class TraceTests(unittest.TestCase):
    def check_synthetic(self, result=None, undefined_index=None):
        group, primitive, base_prime, target, original, oracle = synthetic_trace(undefined_index=undefined_index)
        with patch.object(verify, "answer", oracle):
            return verify.verify_trace(group, primitive, encoded(BASE), base_prime, target, 2, 1, -4, result or original)

    def test_success_and_known_multiplier_conversion(self):
        checked = self.check_synthetic()
        self.assertTrue(checked["pass"], checked)
        self.assertTrue(checked["success"])
        self.assertEqual((checked["candidate_scalar_prime"], checked["candidate_scalar"]), (3, 6))

    def test_target_blinding_both_public_transformations_and_unblinding(self):
        group, primitive, base_prime, blinded_target, result, oracle = synthetic_trace()
        original_target = encoded(group.mul(pow(5, -1, 13), tuple(blinded_target)))
        result["candidate_scalar"] = result["scalar"] = 6*pow(5, -1, 13) % 13
        result["target_multiplier_inverse"] = pow(5, -1, 13)
        with patch.object(verify, "answer", oracle):
            checked = verify.verify_trace(group, primitive, encoded(BASE), base_prime,
                                          original_target, 2, 1, -4, result,
                                          target_multiplier=5, transformed_target=blinded_target)
        self.assertTrue(checked["pass"], checked)
        with patch.object(verify, "answer", oracle):
            changed = verify.verify_trace(group, primitive, encoded(BASE), base_prime,
                                          original_target, 2, 1, -4, result,
                                          target_multiplier=3, transformed_target=blinded_target)
        self.assertFalse(changed["pass"])

    def test_wrong_trace_answer_target_and_conversion_rejected(self):
        original = synthetic_trace()[4]
        corruptions = []
        changed = copy.deepcopy(original)
        changed["predicate_trace"][1]["target"] = None
        corruptions.append(changed)
        changed = copy.deepcopy(original)
        changed["predicate_trace"][1]["answer"]["bit"] ^= 1
        corruptions.append(changed)
        changed = copy.deepcopy(original)
        changed["scalar"] = 3
        corruptions.append(changed)
        changed = copy.deepcopy(original)
        changed["predicate_evaluations"] = 4
        corruptions.append(changed)
        changed = copy.deepcopy(original)
        changed["retained_bit_reads"] = 5
        corruptions.append(changed)
        for changed in corruptions:
            self.assertFalse(self.check_synthetic(changed)["pass"])

    def test_undefined_full_trace_retained_as_valid_unsuccessful_outcome(self):
        checked = self.check_synthetic(undefined_index=1)
        self.assertTrue(checked["pass"], checked)
        self.assertFalse(checked["success"])
        self.assertEqual(checked["undefined_indices"], [1])
        self.assertEqual(checked["predicate_evaluations"], 5)

    def test_early_undefined_truncation_rejected(self):
        result = synthetic_trace(undefined_index=1)[4]
        result["predicate_trace"] = result["predicate_trace"][:2]
        result["L"] = result["predicate_evaluations"] = 2
        self.assertFalse(self.check_synthetic(result, undefined_index=1)["pass"])

    def test_baseline_public_witness_and_zero_success_retention(self):
        group = Group(MODEL)
        self.assertTrue(verify.check_scalar_witness(group, BASE, MULTIPLES[3], {"status": "RECOVERED", "scalar": 3})["pass"])
        self.assertFalse(verify.check_scalar_witness(group, BASE, MULTIPLES[3], {"status": "RECOVERED", "scalar": 4})["pass"])
        summary = verify.summarize_attempts([{"arm_id": "synthetic", "success": False}])
        self.assertEqual(summary["synthetic"]["q_numerator"], 0)
        self.assertIsNone(summary["synthetic"]["cost_over_q"])
        self.assertTrue(summary["synthetic"]["zero_success_retained"])

    def test_source_hash_mutation_and_escape_rejected(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            source = root/"a.py"
            source.write_text("synthetic = True\n")
            manifest = {"files": {"a.py": hashlib.sha256(source.read_bytes()).hexdigest()}}
            self.assertEqual(len(verify.check_source_manifest(manifest, root)), 1)
            source.write_text("synthetic = False\n")
            with self.assertRaises(ValueError):
                verify.check_source_manifest(manifest, root)
            with self.assertRaises(ValueError):
                verify.check_source_manifest({"files": {"../outside.py": "0"*64}}, root)

    def test_exact_cartesian_coverage_detects_missing_and_duplicate_baseline(self):
        cohort = {"public_nonce_hex": "01"*32, "fixtures": [
            {"curve_id": "synthetic", **MODEL, "base": list(BASE), "panel": "sampled",
             "targets": [{"target_id": "t0", "point": list(MULTIPLES[3])}]}]}
        result = {"status": "RECOVERED", "reason": None, "candidate_scalar_prime": 3,
                  "candidate_scalar": 3, "scalar_prime": 3, "scalar": 3,
                  "L": None, "predicate_evaluations": 0, "retained_bit_reads": 0,
                  "predicate_trace": [], "interval": None, "counts": {"online": {}},
                  "public_checks": {"transformed": True, "original": True}}
        row = {"schema": "classical.ecdlp.transfer-study.attempt/v1",
               "curve_id": "synthetic", "target_id": "t0", "arm_id": "bsgs_reference",
               "kind": "bsgs_reference", "replicate_index": 0,
               "attempt_id": "synthetic/t0/bsgs_reference/rep0", "model": MODEL,
               "original_base": list(BASE), "base_multiplier": 1,
               "transformed_base": list(BASE), "original_target": list(MULTIPLES[3]),
               "target_multiplier": 1, "transformed_target": list(MULTIPLES[3]), "result": result}
        partial = verify.verify_records(cohort, [row], [], [], require_complete=False)
        self.assertTrue(partial["pass"], partial)
        self.assertEqual(partial["coverage"]["attempts"]["expected"], 41)
        self.assertEqual(partial["coverage"]["attempts"]["missing"], 40)
        complete = verify.verify_records(cohort, [row], [], [])
        self.assertFalse(complete["pass"])
        duplicate = verify.verify_records(cohort, [row, row], [], [], require_complete=False)
        self.assertFalse(duplicate["pass"])

    def test_public_sampling_domain_and_replicate_separation(self):
        first = verify.expected_sample("12"*32, "target-blinding", "c/t/circuit1.a1/rep0", 12)
        replay = verify.expected_sample("12"*32, "target-blinding", "c/t/circuit1.a1/rep0", 12)
        second = verify.expected_sample("12"*32, "target-blinding", "c/t/circuit1.a1/rep1", 12)
        self.assertEqual(first, replay)
        self.assertNotEqual(first["digest_hex"], second["digest_hex"])
        self.assertTrue(0 <= first["value"] < 12)

    def test_known_prior_control_envelope_independent_check(self):
        group = Group(MODEL)
        primitive = Primitive(group, BASE)
        transformed_base, target, current = group.mul(5, BASE), (7, 2), (7, 2)
        trace, digits = [], []
        for index in range(5):
            outcome = verify.answer(primitive, transformed_base, current, 1, -4)
            digits.append(outcome["bit"])
            trace.append({"index": index, "target": encoded(current), "answer": outcome})
            current = group.add(current, current)
        candidate = {"status": "RECOVERED", "reason": None, "L": 5,
                     "candidate_scalar_prime": 4, "candidate_scalar": 7,
                     "scalar_prime": 4, "scalar": 7, "target_multiplier_inverse": 1,
                     "interval": {k: v for k, v in interval_candidate(13, digits).items() if k != "candidate"},
                     "predicate_evaluations": 5, "retained_bit_reads": 0, "predicate_trace": trace,
                     "counts": {"evaluate": {}, "reduction": {}, "blinding": {}, "conversion": {}},
                     "public_checks": {"transformed": True, "original": True}}
        control = {"schema": "classical.ecdlp.transfer-study.legacy-control/v1", "passed": True,
                   "model": MODEL, "original_base": list(BASE), "target": list(target),
                   "base_multiplier": 5, "target_multiplier": 1,
                   "transformed_base": encoded(transformed_base), "transformed_target": list(target),
                   "fresh_cohort_generated": False, "included_in_primary_attempt_counts": False,
                   "wrong_scalar": 8, "wrong_scalar_rejected": True,
                   "candidate_result": candidate, "bsgs_result": {"status": "RECOVERED", "scalar": 7},
                   "separate_setup_counts": {}, "negative_equation_counts": {}}
        checked = verify.verify_controls(control)
        self.assertTrue(checked["pass"], checked)
        control["wrong_scalar"] = 7
        self.assertFalse(verify.verify_controls(control)["pass"])

    def test_frozen_stratum_and_exclusion_check_on_existing_synthetic_fixture(self):
        plan = {"cohort": {"strata": [{"id": "synthetic", "p_min": 11, "p_max": 11,
                 "target_order": 13, "r_bits": 4, "target_mode": "all_nonidentity",
                 "curve_count": 1, "max_proposals": 1}]}}
        digest = hashlib.sha256(json.dumps(MODEL, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]
        curve_id = f"transfer-synthetic-000-{digest}"
        j = 1728*4*pow((4+27*6**2) % 11, -1, 11) % 11
        cohort = {"plan_canonical_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                  "scalar_truth_generated": False, "shortfalls": [], "fixtures": [
                      {"stratum_id": "synthetic", "curve_id": curve_id, **MODEL,
                       "base": list(BASE), "panel": "exact", "targets": [
                           {"target_id": f"{curve_id}-q{i:05d}", "point": list(q)}
                           for i, q in enumerate(sorted(MULTIPLES[1:]))],
                       "generation_certificate": {"point_count": 13, "x_values_counted": 11,
                           "trace": -1, "j": j, "full_order_prime": True,
                           "base_nonidentity": True, "base_r_multiple_is_identity": True,
                           "proposal_ordinal": 0}}]}
        exclusions = {"schema": "classical.ecdlp.transfer-study.exclusions/v1", "curve_keys": [], "excluded_fields": []}
        self.assertTrue(verify.verify_cohort_schedule(plan, cohort, exclusions)["pass"])
        exclusions["excluded_fields"] = [11]
        with self.assertRaises(ValueError):
            verify.verify_cohort_schedule(plan, cohort, exclusions)

    def test_reused_setup_cold_retry_and_observed_batch_costs_stay_distinct(self):
        cohort = {"public_nonce_hex": "01"*32, "fixtures": [
            {"curve_id": "synthetic", **MODEL, "base": list(BASE), "panel": "sampled",
             "targets": [{"target_id": f"t{i}", "point": list(MULTIPLES[k])} for i, k in enumerate((3, 4))]}]}
        rows = []
        for index, scalar in enumerate((3, 4)):
            rows.append({"schema": "classical.ecdlp.transfer-study.attempt/v1", "curve_id": "synthetic",
                         "target_id": f"t{index}", "arm_id": "bsgs_reference", "kind": "bsgs_reference",
                         "replicate_index": 0, "attempt_id": f"synthetic/t{index}/bsgs_reference/rep0",
                         "model": MODEL, "original_base": list(BASE), "transformed_base": list(BASE),
                         "base_multiplier": 1, "target_multiplier": 1,
                         "original_target": list(MULTIPLES[scalar]), "transformed_target": list(MULTIPLES[scalar]),
                         "result": {"status": "RECOVERED", "reason": None,
                                    "candidate_scalar_prime": scalar, "candidate_scalar": scalar,
                                    "scalar_prime": scalar, "scalar": scalar, "L": None,
                                    "predicate_evaluations": 0, "retained_bit_reads": 0,
                                    "predicate_trace": [], "interval": None,
                                    "public_checks": {"transformed": True, "original": True},
                                    "counts": {"online": {"synthetic_work": 4}}}})
        setup = {"schema": "classical.ecdlp.transfer-study.setup/v1", "curve_id": "synthetic",
                 "arm_id": "bsgs_reference", "kind": "bsgs_reference", "model": MODEL,
                 "original_base": list(BASE), "transformed_base": list(BASE), "base_multiplier": 1,
                 "circuit": None, "shared_across_targets": True, "status": "READY", "reason": None,
                 "reference_state_entries": 4,
                 "counts": {"base_transform": {}, "constructor_setup": {}, "reference_setup": {"synthetic_work": 2}}}
        checked = verify.verify_records(cohort, rows, [setup], [], require_complete=False)
        self.assertTrue(checked["pass"], checked)
        domain = next(row for row in checked["per_curve_arm_outcomes"] if row["arm_id"] == "bsgs_reference")
        self.assertEqual(domain["observed_batch_counter_cost_per_success"]["synthetic_work"], {"numerator": 10, "denominator": 2})
        self.assertEqual(domain["cold_retry_counter_estimate_reusing_setup"]["synthetic_work"], {"numerator": 12, "denominator": 2})


class OddAnchorNullTests(unittest.TestCase):
    def setUp(self):
        self.group = Group(MODEL)
        self.primitive = Primitive(self.group, BASE)
        self.nonce = "12"*32
        self.null = verify.OddAnchorNull(self.group, self.primitive, self.nonce, "synthetic")

    def test_all_fixed_seeds_are_odd_anchored_and_reproducible(self):
        replay = verify.OddAnchorNull(self.group, self.primitive, self.nonce, "synthetic")
        self.assertEqual(self.null.raw_bits, replay.raw_bits)
        for seed in range(16):
            for a in (1, 2, 3, 5):
                self.assertEqual(self.null.bit(seed, a, None), 0)
                self.assertEqual(self.null.bit(seed, a, self.group.mul(a, BASE)), 0)
                for q in MULTIPLES[1:]:
                    self.assertEqual(self.null.bit(seed, a, q)+self.null.bit(seed, a, self.group.neg(q)), 1)
        self.assertFalse(verify.ODD_NULL_RULE["coordinate_covariant"])
        self.assertEqual(verify.ODD_NULL_RULE["matches"], ["oddness", "anchor"])

    def test_prefrozen_hash_encoding_and_rule_metadata(self):
        encoded_rule = json.dumps(verify.ODD_NULL_RULE, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(encoded_rule).hexdigest(),
                         "74625aaff9665e99b277c6095393f862db776ca4fe66dc2d108dc8d734add220")
        prefix = bytes.fromhex(self.nonce)+verify.ODD_NULL_DOMAIN+b"synthetic\x00"+(0).to_bytes(4, "big")+(2).to_bytes(1, "big")
        self.assertEqual(hashlib.sha256(prefix).hexdigest(),
                         "58d3e07d93f6c7a28388adb54130f3a5ec5bf0cf86fe124be2b30a330a24e491")
        self.assertEqual(self.null.raw_bits[0][1], 1)  # y(P)=7>floor(11/2), hash bit0.
        self.assertEqual(self.null.raw_bits[0][12], 0)  # -P shares x and flips sign.

    def test_cached_null_reduction_matches_public_doublings_and_both_equations(self):
        b = 5
        for seed in range(16):
            for a in (1, 2, 3, 5):
                base_prime = self.group.mul(a, BASE)
                for transformed in MULTIPLES[1:]:
                    original = self.group.mul(pow(b, -1, 13), transformed)
                    current, digits = transformed, []
                    for _ in range(5):
                        digits.append(self.null.bit(seed, a, current))
                        current = self.group.add(current, current)
                    interval = interval_candidate(13, digits)
                    outcome = self.null.attempt(seed, a, transformed, original, b)
                    self.assertEqual(outcome["candidate_scalar_prime"], interval["candidate"])
                    if not interval["nonempty"]:
                        self.assertEqual(outcome["status"], "EMPTY_INTERVAL")
                        self.assertIsNone(outcome["candidate_scalar"])
                        continue
                    transformed_check = self.group.mul(outcome["candidate_scalar_prime"], base_prime) == transformed
                    original_check = self.group.mul(outcome["candidate_scalar"], BASE) == original
                    self.assertEqual(outcome["public_checks"], {"transformed": transformed_check, "original": original_check})
                    self.assertEqual(outcome["success"], transformed_check and original_check)
        with self.assertRaises(ValueError):
            self.null.attempt(0, 1, None, BASE, 1)

    def test_exact_and_sampled_coverage_keep_shared_seeds_and_zero_outcomes(self):
        transformed, original, b = self.group.mul(5, MULTIPLES[3]), MULTIPLES[3], 5
        rows, checked = {}, []
        for circuit in (1, 2):
            arm = f"circuit{circuit}.a2"
            key = "synthetic", "t0", arm, 0
            rows[key] = {"transformed_target": encoded(transformed), "original_target": encoded(original), "target_multiplier": b}
            checked.append({"curve_id": "synthetic", "target_id": "t0", "arm_id": arm, "replicate_index": 0,
                            "success": False, "arithmetic_record_pass": True})
        fixture = {"curve_id": "synthetic", **MODEL, "base": list(BASE), "panel": "exact"}
        cohort = {"public_nonce_hex": self.nonce, "fixtures": [fixture]}
        report = verify.evaluate_odd_anchor_null(cohort, {"synthetic": self.group}, {"synthetic": self.primitive}, rows, checked)
        base = next(row for row in report["per_curve_base"] if row["base_multiplier"] == 2)
        self.assertEqual(len(base["exact_nonidentity_seed_outcomes"]), 16)
        self.assertTrue(base["all_r_null_recovery_claim"])
        self.assertEqual(base["independent_raw_null_functions"], 16)
        first, second = base["matched_candidate_arms"]
        self.assertEqual(first["seed_outcomes"], second["seed_outcomes"])
        self.assertEqual(len(first["seed_outcomes"]), 16)
        self.assertTrue(any(row["successes"] == 0 and row["zero_success_retained"] for row in first["seed_outcomes"]))
        self.assertTrue(all(sum(row["status_counts"].values()) == row["attempts"] for row in base["exact_nonidentity_seed_outcomes"]))
        fixture["panel"] = "sampled"
        sampled = verify.evaluate_odd_anchor_null(cohort, {"synthetic": self.group}, {"synthetic": self.primitive}, rows, checked)
        base = next(row for row in sampled["per_curve_base"] if row["base_multiplier"] == 2)
        self.assertFalse(base["all_r_null_recovery_claim"])
        self.assertIsNone(base["exact_nonidentity_seed_outcomes"])
        self.assertEqual(base["distinct_matched_transformed_targets"], 1)
        self.assertFalse(sampled["primary_attempt_counts_changed"])
        self.assertFalse(sampled["priced_performance_claim"])

    def test_retained_truth_bits_give_exact_q_without_constructor_calls(self):
        for a in (1, 2, 3, 5):
            base_prime = self.group.mul(a, BASE)
            bits = {self.group.mul(k, base_prime): int(k > 6) for k in range(13)}
            census = verify.retained_bit_exact_census(self.group, self.primitive, a, bits)
            self.assertEqual((census["successes"], census["attempts"]), (12, 12))
            self.assertEqual(census["fresh_constructor_calls"], 0)
            self.assertTrue(census["input_bit_coverage_complete"])
            self.assertEqual(census["validator_work_counts"]["retained_exact_bit_reads"], 60)
            bits[BASE] = None
            undefined = verify.retained_bit_exact_census(self.group, self.primitive, a, bits)
            self.assertGreater(undefined["status_counts"].get("UNDEFINED", 0), 0)
            self.assertEqual(sum(undefined["status_counts"].values()), 12)
            self.assertFalse(undefined["primary_attempt_counts_changed"])

    def test_exact_candidate_and_exact_null_q_comparison_is_separate_from_fresh_events(self):
        fixture = {"curve_id": "synthetic", **MODEL, "base": list(BASE), "panel": "exact"}
        cohort = {"public_nonce_hex": self.nonce, "fixtures": [fixture]}
        bits = {q: int(k > 6) for k, q in enumerate(MULTIPLES)}
        census = verify.retained_bit_exact_census(self.group, self.primitive, 1, bits)
        report = verify.evaluate_odd_anchor_null(cohort, {"synthetic": self.group}, {"synthetic": self.primitive}, {}, [],
                                                {("synthetic", "circuit1.a1"): census})
        base = next(row for row in report["per_curve_base"] if row["base_multiplier"] == 1)
        actual = base["matched_candidate_arms"][0]
        self.assertEqual(actual["matched_attempts"], 0)
        self.assertEqual(actual["candidate_successes"], 0)
        self.assertEqual(actual["candidate_retained_bit_exact_census"]["successes"], 12)
        for comparison, null in zip(actual["candidate_exact_minus_null_exact_q"], base["exact_nonidentity_seed_outcomes"]):
            self.assertEqual(comparison["numerator"], 12-null["successes"])
            self.assertEqual(comparison["denominator"], 12)


if __name__ == "__main__":
    unittest.main()

"""Software regressions on the previously fixed public F11 control only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compute
from constructor import prepare
from curve import Counter, Curve

MODEL = {"p": 11, "a": 1, "b": 6, "r": 13}
BASE = (2, 7)


class TransferSoftwareTests(unittest.TestCase):
    def test_known_multiplier_blinding_conversion_with_fresh_calls(self):
        c = Curve(11, 1, 6)
        prepared = prepare(MODEL, c.multiply(BASE, 5), {"kind": "candidate", "alpha": 1, "beta": 7})
        target = c.multiply(BASE, 4)
        blinded, result = compute.ungated_attempt(prepared, BASE, target, 5, 2)
        self.assertEqual(blinded, c.multiply(target, 2))
        self.assertEqual(result["status"], "RECOVERED")
        self.assertEqual(result["scalar"], 4)
        self.assertEqual(result["scalar_prime"], 12)
        self.assertEqual(result["predicate_evaluations"], 5)
        self.assertEqual(result["retained_bit_reads"], 0)
        self.assertEqual(len(result["predicate_trace"]), 5)
        self.assertNotIn("counters", result["predicate_trace"][0])
        self.assertTrue(all(result["public_checks"].values()))
        self.assertEqual(result["target_multiplier_inverse"], 7)
        self.assertEqual(result["counts"]["conversion"]["order_inverse_call"], 1)

    def test_undefined_still_executes_all_fresh_calls(self):
        class Fake:
            model, base = MODEL, BASE
            calls = 0
            def evaluate(self, point):
                self.calls += 1
                answer = {"status": "UNDEFINED", "bit": None, "reason": "SOFTWARE_CONTROL"} if self.calls == 2 else {"status": "BIT", "bit": 0, "reason": None}
                return answer, {"software_evaluate": 1}
        prepared = Fake()
        _, result = compute.ungated_attempt(prepared, BASE, (3, 6), 1, 1)
        self.assertEqual(prepared.calls, 5)
        self.assertEqual(result["predicate_evaluations"], 5)
        self.assertEqual(result["counts"]["evaluate"], {"software_evaluate": 5})
        self.assertEqual(result["status"], "UNDEFINED")
        self.assertIsNone(result["candidate_scalar"])
        self.assertIsNone(result["public_checks"]["original"])
        self.assertIsNone(result["interval"]["value"])

    def test_empty_interval_never_wraps_order_to_zero(self):
        class Ones:
            model, base = MODEL, BASE
            def evaluate(self, point):
                return {"status": "BIT", "bit": 1, "reason": None}, {}
        _, result = compute.ungated_attempt(Ones(), BASE, (3, 6), 1, 1)
        self.assertEqual(result["candidate_scalar_prime"], 13)
        self.assertEqual(result["status"], "EMPTY_INTERVAL")
        self.assertIsNone(result["candidate_scalar"])
        self.assertFalse(result["interval"]["nonempty"])

    def test_bsgs_is_working_complete_reference_on_known_software_fixture(self):
        c = Curve(11, 1, 6)
        reference = compute.BSGS(MODEL, BASE)
        self.assertEqual(len(reference.babies), 4)
        for scalar in range(1, 13):
            result = reference.recover(c.multiply(BASE, scalar))
            self.assertEqual(result["status"], "RECOVERED")
            self.assertEqual(result["scalar"], scalar)
            self.assertEqual(result["predicate_evaluations"], 0)
        self.assertEqual(reference.setup_counts["bsgs_baby_insert"], 4)

    def test_public_rng_domain_repeat_and_aa_binding(self):
        nonce = "ab" * 32
        draw = "software-curve/software-Q/circuit1.a1/rep0"
        left, proof = compute.uniform_below(nonce, "target-blinding", draw, 12)
        right, replay = compute.uniform_below(nonce, "target-blinding", draw, 12)
        self.assertEqual((left, proof), (right, replay))
        _, next_rep = compute.uniform_below(nonce, "target-blinding", draw[:-1] + "1", 12)
        _, uniform = compute.uniform_below(nonce, "uniform-candidate", draw, 12)
        self.assertNotEqual(proof["digest_hex"], next_rep["digest_hex"])
        self.assertNotEqual(proof["digest_hex"], uniform["digest_hex"])
        self.assertTrue(0 <= left < 12)
        self.assertEqual(proof["bound"], 12)

    def test_order_inverse_has_separate_ledger(self):
        counts = Counter()
        self.assertEqual(compute.scalar_inverse(5, 13, counts), 8)
        self.assertEqual(counts.snapshot()["order_inverse_call"], 1)
        self.assertNotIn("field_inverse", counts.snapshot())

    def test_plan_only_description_cannot_generate_or_evaluate(self):
        expected = {"candidate_attempts_planned": 90432, "baseline_attempts_planned": 12560,
                    "total_attempts_planned": 102992, "fixture_count_planned": 40,
                    "arm_ids": [a["id"] for a in compute.arm_specs()]}
        plan = {"schema": compute.SCHEMA + ".compute-plan/v1", "experiment_id": compute.EXPERIMENT,
                "run_id": compute.RUN, "expected": expected}
        cohort = types.SimpleNamespace(describe_plan=lambda p: {"fixture_count_planned": 40, "target_cases_planned": 2512},
                                       generate=lambda *a, **kw: self.fail("cohort draw during plan-only"))
        with patch.dict(sys.modules, cohort=cohort), patch.object(compute, "prepare", side_effect=AssertionError("candidate evaluation during plan-only")):
            compute.validate_plan(plan)
            described = compute.describe_plan(plan)
        self.assertFalse(described["measurement_started"])
        self.assertFalse(described["fresh_cohort_generated"])
        self.assertEqual(described["candidate_attempts_executed"], 0)
        self.assertEqual({k: described[k] for k in expected}, expected)

    def test_partial_cohort_not_success_filtered(self):
        with self.assertRaisesRegex(ValueError, "complete fresh public cohort"):
            compute.validate_public_cohort({"schema": compute.SCHEMA + ".public-cohort/v1", "generation_status": "incomplete", "fixtures": []}, {})

    def test_stream_schedule_has_one_bsgs_and_matched_aa_without_gate(self):
        public = {"public_nonce_hex": "ab" * 32,
                  "fixtures": [{"curve_id": "software-prior-f11", **MODEL,
                      "base": [2, 7], "panel": "sampled",
                      "targets": [{"target_id": "software-known-q", "point": [7, 2]}]}]}
        with tempfile.TemporaryDirectory() as folder:
            result = compute.run_attempts({}, public, Path(folder),
                {"protocol_sha256": "0" * 64, "source_fingerprint": "1" * 64, "cohort_sha256": "2" * 64})
            rows = [json.loads(line) for line in (Path(folder) / "attempts.jsonl").read_text().splitlines()]
            intents = [json.loads(line) for line in (Path(folder) / "attempt-intents.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 41)
            self.assertEqual(len(intents), 41)
            self.assertEqual(result["counts"]["candidate_attempts"], 36)
            self.assertEqual(result["counts"]["baseline_attempts"], 5)
            self.assertEqual(len([x for x in rows if x["kind"] == "bsgs_reference"]), 1)
            aa = [x for x in rows if x["kind"] == "aa_replay"]
            reference = [x for x in rows if x["arm_id"] == "circuit1.a1"]
            for left, right in zip(aa, reference):
                self.assertEqual(left["sampling"], right["sampling"])
                self.assertEqual(left["result"], right["result"])
            self.assertTrue(all("gate" not in x["result"] for x in rows))
            self.assertEqual((Path(folder) / "diagnostics.jsonl").read_bytes(), b"")

    def test_legacy_controls_have_separate_counts_and_no_primary_inflation(self):
        result = compute.run_legacy_controls()
        self.assertTrue(result["passed"])
        self.assertFalse(result["fresh_cohort_generated"])
        self.assertFalse(result["included_in_primary_attempt_counts"])
        self.assertEqual(result["candidate_result"]["scalar_prime"], 4)
        self.assertEqual(result["candidate_result"]["scalar"], 7)
        self.assertEqual(result["bsgs_result"]["scalar"], 7)
        self.assertTrue(result["wrong_scalar_rejected"])


if __name__ == "__main__":
    unittest.main()

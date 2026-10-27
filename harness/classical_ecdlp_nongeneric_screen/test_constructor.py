"""Software regressions only; this module does not execute the scientific grid."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import compute
from constructor import conditional_recover, normalized_miller_coefficient, prepare
from curve import Counter, Curve, Field, certify_public_parameters

MODEL = {"p": 11, "a": 1, "b": 6, "r": 13}
P = (2, 7)
# Public hand-derived mandatory-fixture regressions, not a coefficient search.
KNOWN_MULTIPLES = [None, (2, 7), (5, 2), (8, 3), (10, 2), (3, 6), (7, 9),
                   (7, 2), (3, 5), (10, 9), (8, 8), (5, 9), (2, 4)]


def arm(kind="candidate", alpha=0, beta=1):
    return {"kind": kind, "id": f"{kind}:a{alpha}:b{beta}",
            "alpha_integer": alpha, "beta_integer": beta,
            "alpha": alpha % 11, "beta": beta % 11}


class ArithmeticTests(unittest.TestCase):
    def test_field_inverse_and_power_accounting(self):
        meter = Counter()
        field = Field(11, meter)
        for value in range(1, 11):
            self.assertEqual(value * field.inverse(value) % 11, 1)
        self.assertEqual(field.power(3, 5), pow(3, 5, 11))
        self.assertEqual(meter.counts["field_inverse"], 10)
        self.assertEqual(meter.counts["field_power_call"], 1)
        self.assertEqual(meter.counts["power_bit"], 3)
        with self.assertRaises(ZeroDivisionError):
            field.inverse(0)
        with self.assertRaises(ValueError):
            Field(15, Counter()).inverse(5)

    def test_known_public_multiples_and_exceptions(self):
        curve = Curve(11, 1, 6)
        for index, point in enumerate(KNOWN_MULTIPLES):
            self.assertEqual(curve.multiply(P, index), point)
        self.assertEqual(curve.add(P, None), P)
        self.assertIsNone(curve.add(P, curve.negate(P)))
        self.assertEqual(curve.multiply(P, -1), (2, 4))
        self.assertFalse(curve.contains((13, 7)))
        self.assertFalse(curve.contains((0, 0)))
        # An order-two tangent is a vertical exceptional addition.
        self.assertIsNone(Curve(11, 1, 0).add((0, 0), (0, 0)))

    def test_certification_is_separate_and_rejects_invalid_domains(self):
        self.assertGreater(certify_public_parameters(11, 1, 6, 13)["certification_trial_division"], 0)
        for args in [(15, 1, 6, 13), (11, 0, 0, 13), (11, 1, 6, 11)]:
            with self.assertRaises(ValueError):
                certify_public_parameters(*args)


class ConstructorTests(unittest.TestCase):
    def test_miller_recurrence_known_values_and_exact_chain_counts(self):
        curve = Curve(11, 1, 6)
        self.assertEqual(normalized_miller_coefficient(curve, P, 13), 3)
        self.assertEqual(curve.counter.counts["miller_chain_double"], 3)
        self.assertEqual(curve.counter.counts["miller_chain_add"], 2)
        self.assertEqual(curve.counter.counts["group_add_call"], 5)
        for point, expected in [((5, 2), 3), ((8, 3), 8), ((10, 2), 3), ((3, 6), 4), ((7, 9), 6)]:
            self.assertEqual(normalized_miller_coefficient(Curve(11, 1, 6), point, 13), expected)
        self.assertEqual(normalized_miller_coefficient(Curve(11, 1, 6), None, 13), 0)
        with self.assertRaises(ValueError):
            normalized_miller_coefficient(Curve(11, 1, 6), P, 7)

    def test_anchor_identity_and_no_truth_input(self):
        prepared = prepare(MODEL, P, arm())
        self.assertEqual(prepared.z_base, 3)
        answer, counts = prepared.evaluate(P)
        self.assertEqual((answer["status"], answer["bit"], answer["normalized"]), ("BIT", 0, 1))
        self.assertEqual(answer["anchor"], 3)
        self.assertGreater(counts["field_power_call"], 0)
        identity, _ = prepared.evaluate(None)
        self.assertEqual((identity["bit"], identity["z"]), (0, 0))
        self.assertNotIn("scalar", prepared.__dict__)
        with self.assertRaises(ValueError):
            prepared.evaluate((0, 0))

    def test_invalid_anchor_and_zero_query_remain_undefined(self):
        prepared = prepare(MODEL, P, arm("invalid_anchor", -1, 1))
        for target in (None, P):
            answer, _ = prepared.evaluate(target)
            self.assertEqual((answer["status"], answer["bit"], answer["reason"]), ("UNDEFINED", None, "ZERO_ANCHOR"))
        # From the hand-derived Z(2P)=3, c=2, y(2P)=2:
        # the beta-zero alpha=2 control has g(2P)=3+2*2*2=0.
        fiber = prepare(MODEL, P, arm("fiber", 2, 0))
        answer, _ = fiber.evaluate((5, 2))
        self.assertEqual((answer["status"], answer["bit"], answer["g"], answer["reason"]),
                         ("UNDEFINED", None, 0, "ZERO_NUMERATOR"))
        self.assertIsNone(answer["normalized"])

    def test_mandatory_known_wrong_root_counterexample(self):
        prepared = prepare(MODEL, P, {"kind": "wrong_root", "id": "wrong_root:anchored_power_root"})
        self.assertEqual(prepared.root_factor, 10)  # sigma=-f^3 on this base.
        answer, _ = prepared.evaluate((8, 3))
        self.assertEqual((answer["status"], answer["bit"], answer["root"]), ("BIT", 1, 8))

    def test_conditional_recovery_oracle_is_test_only_and_final_check_is_real(self):
        prepared = prepare(MODEL, P, arm())
        truth = {point: index for index, point in enumerate(KNOWN_MULTIPLES)}

        def test_only_half(self, target):
            return {"status": "BIT", "bit": int(truth[target] > 6), "reason": None}, {"test_oracle_call": 1}

        with patch.object(type(prepared), "evaluate", test_only_half):
            outcome = conditional_recover(prepared, (8, 3))
        self.assertEqual((outcome["status"], outcome["scalar"], outcome["predicate_calls"]), ("RECOVERED", 3, 5))
        self.assertEqual(outcome["predicate_evaluations"], 5)
        self.assertEqual(outcome["retained_bit_reads"], 0)
        self.assertEqual(len(outcome["predicate_trace"]), 5)
        self.assertEqual(outcome["evaluate_counts"], {"test_oracle_call": 5})
        with patch.object(type(prepared), "evaluate", return_value=({"status": "BIT", "bit": 0, "reason": None}, {})):
            wrong = conditional_recover(prepared, P)
        self.assertEqual(wrong["status"], "REJECTED_FINAL_VERIFICATION")
        self.assertIsNone(wrong["scalar"])
        with patch.object(type(prepared), "evaluate", return_value=({"status": "UNDEFINED", "bit": None, "reason": "ZERO_NUMERATOR"}, {})):
            undefined = conditional_recover(prepared, P)
        self.assertEqual((undefined["status"], undefined["predicate_calls"]), ("UNDEFINED", 1))

    def test_public_gate_and_real_fresh_callback_dispatch_using_test_only_positive(self):
        # This synthetic positive exercises dispatch without screening a new
        # candidate: scalar truth is confined to a patched test-only callback.
        truth = {point: index for index, point in enumerate(KNOWN_MULTIPLES)}
        outcomes = {point: {"status": "BIT", "bit": int(index > 6)}
                    for index, point in enumerate(KNOWN_MULTIPLES)}
        calls = []

        def test_only_half(self, target):
            calls.append(target)
            return {"status": "BIT", "bit": int(truth[target] > 6), "reason": None}, {"test_fresh_evaluate": 1}

        with patch.object(type(prepare(MODEL, P, arm())), "evaluate", test_only_half):
            with patch.object(compute, "prepare", wraps=compute.prepare) as preparation:
                result = compute.fresh_group_recovery(MODEL, P, arm(), outcomes)
        self.assertTrue(result["gate"]["pass"])
        self.assertEqual(preparation.call_count, 1)
        self.assertEqual((result["predicate_evaluations"], len(calls)), (65, 65))
        self.assertEqual(result["retained_bit_reads_in_recovery"], 0)
        self.assertEqual(result["counters"]["evaluate"], {"test_fresh_evaluate": 65})
        self.assertEqual(len(result["recoveries"]), 13)
        self.assertTrue(all(row["result"]["status"] == "RECOVERED" for row in result["recoveries"]))
        self.assertGreater(result["counters"]["gate"]["group_add_call"], 0)
        self.assertGreater(result["counters"]["reduction"]["scalar_multiply_call"], 0)

    def test_failed_public_gate_skips_fresh_recovery_with_explicit_reason(self):
        wrong = prepare(MODEL, P, {"kind": "wrong_root", "id": "wrong_root:anchored_power_root"})
        outcomes = {target: wrong.evaluate(target)[0] for target in KNOWN_MULTIPLES}
        with patch.object(compute, "prepare", side_effect=AssertionError("failed gate must not prepare/evaluate")):
            result = compute.fresh_group_recovery(MODEL, P, arm(), outcomes)
        self.assertFalse(result["gate"]["pass"])
        self.assertEqual(result["gate"]["not_attempted_reason"], "IDENTITY_OR_TWO_PULSE_FAILURE")
        self.assertEqual(result["recoveries"], [])
        self.assertEqual(result["predicate_evaluations"], 0)
        outcomes[P] = {"status": "UNDEFINED", "bit": None}
        self.assertEqual(compute.public_order_gate(MODEL, P, outcomes)["not_attempted_reason"], "UNDEFINED_COVERAGE")


class PlanAndIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(Path(__file__).with_name("protocol.plan.json").read_text())

    def test_exact_plan_counts_without_evaluating_candidate(self):
        with patch.object(compute, "prepare", side_effect=AssertionError("plan-only must not evaluate")):
            description = compute.describe_plan(self.plan)
        self.assertEqual(description["candidate_point_cases"], 62400)
        self.assertEqual(description["control_cases"], 12480)
        self.assertEqual(description["total_cases"], 74880)
        self.assertFalse(description["measurement_started"])
        self.assertEqual(description["candidate_modular_aliases"], [])
        self.assertEqual(len(description["arm_ids"]), 48)
        self.assertEqual(len(set(description["arm_ids"])), 48)

    def test_changed_grammar_and_unfrozen_actual_launch_rejected(self):
        self.plan["alpha"].append(4)
        with self.assertRaises(ValueError):
            compute.validate_plan(self.plan)
        self.assertEqual(compute.main(["--protocol", str(Path(__file__).with_name("protocol.plan.json"))]), 2)

    def test_manifest_corruption_and_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps({"files": {name: "0" * 64 for name in compute.SOURCE_REQUIRED}, "source_revision_c": "a" * 40}))
            with self.assertRaises((ValueError, FileNotFoundError)):
                compute.validate_source_manifest(manifest, actual=True)
            output_dir = Path(directory) / "already_exists"
            output_dir.mkdir()
            with self.assertRaises(ValueError):
                compute.execute(self.plan, "a" * 64, "b" * 64, output_dir)

    def test_preflight_failure_retains_explicit_record_without_candidate_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "failed_preflight"
            with patch.object(compute, "describe_plan", side_effect=ValueError("synthetic census failure")):
                with patch.object(compute, "prepare", side_effect=AssertionError("no candidate dispatch")):
                    with self.assertRaises(ValueError):
                        compute.execute(self.plan, "a" * 64, "b" * 64, output_dir)
            failure = json.loads((output_dir / "failure.json").read_text())
            self.assertEqual((failure["phase"], failure["rows_retained"], failure["rows_processed"]),
                             ("public_input_preflight", 0, 0))
            self.assertFalse((output_dir / "completion.json").exists())
            raw = output_dir / "partial.jsonl"
            raw.write_bytes(b'{"valid":1}\n{"truncated":')
            self.assertEqual(compute.retained_jsonl_rows(raw), 1)

    def test_candidate_import_boundary_and_no_scalar_table_api(self):
        for name in ("constructor.py", "curve.py"):
            tree = ast.parse(Path(__file__).with_name(name).read_text())
            imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
            self.assertFalse(imports & {"verify", "compute", "test_constructor", "test_verify"})
        self.assertEqual(set(prepare.__code__.co_varnames[:prepare.__code__.co_argcount]), {"model", "base", "arm"})

    def test_runtime_observations_and_actual_worker_requirements(self):
        facts = compute.runtime_facts(Path(__file__).with_name("protocol.plan.json"), None)
        self.assertEqual(len(facts["resuid"]), 3)
        self.assertFalse(facts["environment_values_collected"])
        expected = {"resuid": [1000] * 3, "resgid": [1000] * 3,
                    "supplementary_groups": [], "input_access": {"module": {"exists": True, "writable": False}}}
        compute.enforce_runtime_facts(expected)
        with self.assertRaises(ValueError):
            compute.enforce_runtime_facts({**expected, "resuid": [0] * 3})
        with self.assertRaises(ValueError):
            compute.enforce_runtime_facts({**expected, "input_access": {"module": {"exists": True, "writable": True}}})


if __name__ == "__main__":
    unittest.main()

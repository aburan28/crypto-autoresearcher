"""Fixed disclosed known-answer software controls, not a scientific panel."""
from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--baseline-root", type=Path, required=True)
args, remainder = parser.parse_known_args()
sys.path.insert(0, str(args.baseline_root.resolve()))

import compute
from constructor import normalized_miller_coefficient, prepare
from curve import Curve
import prototype

F11 = {"p": 11, "a": 1, "b": 6, "r": 13}
P11 = (2, 7)
# Previously disclosed mandatory control: 7P=(7,2), 5P=(3,6).
LEGACY_TARGET = (7, 2)
F23 = {"p": 23, "a": 11, "b": 5, "r": 17}
P23 = (5, 22)


def witness(value):
    """Delete only counter fields; every other output is compared recursively."""
    if isinstance(value, dict):
        return {k: witness(v) for k, v in value.items() if k not in ("counts", "counters")}
    if isinstance(value, list):
        return [witness(v) for v in value]
    if isinstance(value, tuple):
        return tuple(witness(v) for v in value)
    return value


class FixedKnownAnswerTests(unittest.TestCase):
    def paired(self, model, base, target, alpha, beta, a=1, b=1):
        curve = Curve(model["p"], model["a"], model["b"])
        prepared = prepare(model, curve.multiply(base, a),
                           {"kind": "candidate", "alpha": alpha, "beta": beta})
        baseline = compute.ungated_attempt(prepared, base, target, a, b, True)
        aa = compute.ungated_attempt(prepared, base, target, a, b, True)
        incremental = prototype.incremental_ungated_attempt(prepared, base, target, a, b, True)
        self.assertEqual(baseline, aa)
        self.assertEqual(witness(baseline), witness(incremental))
        self.assertEqual(len(incremental[1]["predicate_trace"]), model["r"].bit_length() + 1)
        self.assertEqual(baseline[1]["counts"]["blinding"], incremental[1]["counts"]["blinding"])
        self.assertEqual(baseline[1]["counts"]["reduction"], incremental[1]["counts"]["reduction"])
        self.assertEqual(baseline[1]["counts"]["conversion"], incremental[1]["counts"]["conversion"])
        return prepared, baseline, incremental

    def test_legacy_public_recovery_and_counter_accounting(self):
        _, old, new = self.paired(F11, P11, LEGACY_TARGET, 1, -4 % 11, a=5)
        self.assertEqual((new[1]["status"], new[1]["scalar"], new[1]["scalar_prime"]),
                         ("RECOVERED", 7, 4))
        length, chain = 5, 5  # r=13: three doubles, two additions per chain.
        self.assertEqual(old[1]["counts"]["evaluate"]["miller_coefficient_call"], length)
        self.assertEqual(new[1]["counts"]["evaluate"]["miller_coefficient_call"], 1)
        self.assertEqual(old[1]["counts"]["evaluate"]["group_add_call"] -
                         new[1]["counts"]["evaluate"]["group_add_call"], (length - 1) * chain)
        self.assertEqual(new[1]["counts"]["state_updates"]["incremental_z_update"], length - 1)
        self.assertNotIn("group_add_call", new[1]["counts"]["state_updates"])

    def test_f23_hand_derived_doubling_values_and_witness(self):
        _, _, new = self.paired(F23, P23, P23, -2, -1)
        trace = new[1]["predicate_trace"]
        # Tangents on P,2P,4P,8P,16P are 3,4,1,21,20.
        # Miller r=17 chain ends at O with D=17, hence Z(P)=-17/17=22.
        self.assertEqual([x["target"] for x in trace],
                         [[5, 22], [22, 19], [18, 20], [11, 10], [5, 1], [22, 4]])
        self.assertEqual([x["answer"]["z"] for x in trace], [22, 1, 6, 13, 1, 22])
        self.assertEqual([x["answer"]["bit"] for x in trace], [0, 0, 1, 0, 1, 1])

    def test_zero_numerator_keeps_all_calls_after_undefined(self):
        _, _, new = self.paired(F11, P11, (5, 2), 2, 0)
        self.assertEqual(new[1]["predicate_trace"][0]["answer"]["reason"], "ZERO_NUMERATOR")
        self.assertEqual(new[1]["status"], "UNDEFINED")
        self.assertEqual(new[1]["predicate_evaluations"], 5)
        self.assertEqual(new[1]["counts"]["state_updates"]["incremental_z_update"], 4)

    def test_zero_anchor_setup_undefined_has_no_primitive_initialization(self):
        _, _, new = self.paired(F11, P11, P11, -1, 1)
        self.assertEqual(new[1]["status"], "UNDEFINED")
        self.assertTrue(all(x["answer"]["reason"] == "ZERO_ANCHOR" for x in new[1]["predicate_trace"]))
        self.assertNotIn("miller_coefficient_call", new[1]["counts"]["evaluate"])
        self.assertEqual(new[1]["counts"]["state_updates"], {})

    def test_unsupported_domain_preserves_original_undefined_behavior(self):
        model = {**F11, "r": 11}
        _, _, new = self.paired(model, P11, P11, 1, -4)
        self.assertEqual(new[1]["status"], "UNDEFINED")
        self.assertTrue(all(x["answer"]["reason"] == "DOMAIN_UNSUPPORTED" for x in new[1]["predicate_trace"]))

    def test_identity_inverse_and_vertical_normalization(self):
        curve = Curve(11, 1, 6)
        self.assertEqual(curve.add_with_slope(None, P11), (P11, 0))
        self.assertEqual(curve.add_with_slope(P11, (2, 4)), (None, 0))
        self.assertEqual(normalized_miller_coefficient(curve, None, 13), 0)
        self.assertEqual(prototype._next_z(curve.f, 0, 0), 0)
        self.assertEqual((3 + 8 + 0) % 11, 0)  # Known Z(-P)=-Z(P).
        prepared = prepare(F11, P11, {"kind": "candidate", "alpha": 1, "beta": -4})
        # The primary API rejects O, exactly like the original primary API.
        for fn in (compute.ungated_attempt, prototype.incremental_ungated_attempt):
            with self.assertRaisesRegex(ValueError, "nonidentity public point"):
                fn(prepared, P11, None, 1, 1)

    def test_invalid_and_outside_subgroup_rejection_matches(self):
        prepared = prepare(F11, P11, {"kind": "candidate", "alpha": 1, "beta": -4})
        for fn in (compute.ungated_attempt, prototype.incremental_ungated_attempt):
            with self.assertRaisesRegex(ValueError, "nonidentity public point"):
                fn(prepared, P11, (0, 0), 1, 1)
        malformed = dataclasses.replace(prepared, model={**F11, "r": 7}, inverse_r=8)
        for fn in (compute.ungated_attempt, prototype.incremental_ungated_attempt):
            with self.assertRaisesRegex(ValueError, "outside declared r-torsion subgroup"):
                fn(malformed, P11, P11, 1, 1)

    def test_state_is_reset_between_public_attempts(self):
        prepared = prepare(F11, P11, {"kind": "candidate", "alpha": 1, "beta": -4})
        first = prototype.incremental_ungated_attempt(prepared, P11, P11, 1, 1)
        second = prototype.incremental_ungated_attempt(prepared, P11, (8, 3), 1, 1)
        self.assertEqual(witness(second), witness(compute.ungated_attempt(prepared, P11, (8, 3), 1, 1)))
        self.assertEqual(second[1]["predicate_trace"][0]["answer"]["z"], 8)
        self.assertEqual(witness(first), witness(prototype.incremental_ungated_attempt(prepared, P11, P11, 1, 1)))

    def test_nontrivial_fixed_public_blinding(self):
        self.paired(F11, P11, LEGACY_TARGET, 1, -4 % 11, a=5, b=3)

    def test_wrong_sign_mutation_is_detected_before_any_success_claim(self):
        curve = Curve(11, 1, 6)
        point, slope = curve.add_with_slope(P11, P11)
        self.assertEqual((point, slope), ((5, 2), 8))
        self.assertEqual(prototype._next_z(curve.f, 3, slope), 3)
        def wrong(field, z, lam):
            return field.sub(field.mul(2, z), lam)
        prepared = prepare(F11, P11, {"kind": "candidate", "alpha": 1, "beta": -4})
        baseline = compute.ungated_attempt(prepared, P11, P11, 1, 1)
        with patch.object(prototype, "_next_z", wrong):
            broken = prototype.incremental_ungated_attempt(prepared, P11, P11, 1, 1)
        self.assertNotEqual(witness(baseline), witness(broken))
        self.assertEqual(broken[1]["predicate_trace"][1]["answer"]["z"], 9)

    def test_wrong_root_control_retains_original_no_z_branch(self):
        prepared = prepare(F11, P11, {"kind": "wrong_root"})
        old = compute.ungated_attempt(prepared, P11, (8, 3), 1, 1, True)
        new = prototype.incremental_ungated_attempt(prepared, P11, (8, 3), 1, 1, True)
        self.assertEqual(witness(old), witness(new))
        self.assertEqual(new[1]["counts"]["state_updates"], {})


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *remainder], verbosity=2)

"""Unit-testable no-crypto predicates for FC0-EXT-PKG-SSI-001 scaffolding.

Run:
  python3 -m unittest coordination.goals...  (or path-based below)

Zero curve/isogeny/quantum-circuit computation.
"""

from __future__ import annotations

import unittest

from .lifetime_hooks import LifetimeError, LifetimeRegistry
from .state_machine import STAGE_LIVE_SETS
from .types import CandidateSecret, CleanupResult, FailureChannel, HandleState, PublicInstance
from .verify import Verify, VerificationFault, classify_verify_outcome


class TestVerifyScaffold(unittest.TestCase):
    def test_reject_mismatch(self):
        x = PublicInstance(token="x0", scaffold_accept_token="k-accept")
        k = CandidateSecret(token="k-other")
        self.assertFalse(Verify(x, k))
        self.assertEqual(classify_verify_outcome(False), FailureChannel.F_verify)

    def test_synthetic_accept(self):
        x = PublicInstance(token="x0", scaffold_accept_token="k-accept")
        k = CandidateSecret(token="k-accept")
        self.assertTrue(Verify(x, k))
        self.assertEqual(classify_verify_outcome(True), "success_exit")

    def test_malformed_raises_fault(self):
        x = PublicInstance(token="x0", well_formed=False)
        k = CandidateSecret(token="k")
        with self.assertRaises(VerificationFault):
            Verify(x, k)

    def test_no_crypto_fields(self):
        # Predicate body uses only token equality — no curve params.
        x = PublicInstance(token="x", scaffold_accept_token=None)
        k = CandidateSecret(token="anything")
        self.assertFalse(Verify(x, k))


class TestLifetimeHooks(unittest.TestCase):
    def _prep(self) -> LifetimeRegistry:
        reg = LifetimeRegistry()
        x = PublicInstance(token="x-scaffold")
        reg.birth_B_input(x)
        reg.birth_B_attempt({"attempts_symbolic": True})
        return reg

    def test_all_twelve_hooks_have_four_methods(self):
        cov = LifetimeRegistry().coverage()
        self.assertEqual(cov["required_hook_count"], 12)
        self.assertEqual(cov["implemented_method_count"], 48)
        self.assertEqual(cov["collimation_sieve_apis_invented"], 0)
        self.assertFalse(cov["tau_invented"])

    def test_stage_live_sets_frozen(self):
        self.assertEqual(
            STAGE_LIVE_SETS["preparation"],
            {"B_input", "B_attempt", "W_label", "R_label"},
        )
        self.assertIn("M_tail", STAGE_LIVE_SETS["tail_verification"])

    def test_happy_path_skeleton_to_verify(self):
        reg = self._prep()
        x = PublicInstance(token="x-scaffold", scaffold_accept_token="k*")
        w_l = reg.birth_W_label(x, {"ctx": 1})
        r_l = reg.birth_R_label(x, {"ctx": 1}, {"addr": "symbolic"})
        reg.last_use_W_label(w_l)
        self.assertEqual(reg.cleanup_W_label(w_l), CleanupResult.ok)
        reg.destroy_W_label(w_l)
        reg.last_use_R_label(r_l)
        self.assertEqual(reg.cleanup_R_label(r_l), CleanupResult.ok)
        reg.destroy_R_label(r_l)

        w_s = reg.birth_W_sieve({"attempt": 0})
        r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
        b_s = reg.birth_B_sieve({"attempt": 0})
        reg.last_use_W_sieve(w_s)
        reg.last_use_R_sieve(r_s)
        reg.last_use_B_sieve(b_s)
        self.assertEqual(reg.cleanup_W_sieve(w_s, "accept"), CleanupResult.ok)
        self.assertEqual(reg.cleanup_R_sieve(r_s, "accept"), CleanupResult.ok)
        self.assertEqual(reg.cleanup_B_sieve(b_s, "accept"), CleanupResult.ok)
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        reg.destroy_B_sieve(b_s)

        t = reg.birth_accepted_transcript({"accepted": True})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        m = reg.birth_M_tail(
            b_rec,
            width_decl={"unit": "symbolic_deferred"},
            enumeration_order_decl={"order": "symbolic"},
            stopping_rule_decl={"invents_tau": False, "rule": "symbolic_open"},
            shares_B_recovery_decl=True,
        )
        cand = reg.birth_B_candidate(m)
        reg.last_use_B_candidate(cand)
        k = CandidateSecret(token="k*")
        self.assertTrue(Verify(x, k))
        reg.retain_final_verification_record()

        for h, fn_c, fn_d in (
            (cand, reg.cleanup_B_candidate, reg.destroy_B_candidate),
            (m, reg.cleanup_M_tail, reg.destroy_M_tail),
            (b_rec, reg.cleanup_B_recovery, reg.destroy_B_recovery),
            (b_post, reg.cleanup_B_post, reg.destroy_B_post),
            (t, reg.cleanup_accepted_transcript, reg.destroy_accepted_transcript),
        ):
            self.assertEqual(fn_c(h), CleanupResult.ok)
            fn_d(h)

        b_att = reg.handles["B_attempt"]
        b_in = reg.handles["B_input"]
        reg.last_use_B_attempt(b_att)
        reg.last_use_B_input(b_in)
        self.assertEqual(reg.cleanup_B_attempt(b_att), CleanupResult.ok)
        self.assertEqual(reg.cleanup_B_input(b_in), CleanupResult.ok)
        reg.destroy_B_attempt(b_att)
        reg.destroy_B_input(b_in)
        self.assertEqual(reg.handles["B_input"].state, HandleState.destroyed)
        self.assertEqual(len(reg.failures), 0)

    def test_destroy_before_cleanup_fails(self):
        reg = self._prep()
        x = PublicInstance(token="x")
        w = reg.birth_W_label(x, {})
        with self.assertRaises(LifetimeError):
            reg.destroy_W_label(w)

    def test_numeric_width_forbidden(self):
        reg = self._prep()
        # Minimal path to B_recovery for M_tail birth precondition.
        w_s = reg.birth_W_sieve({})
        r_s = reg.birth_R_sieve({}, {})
        reg.cleanup_W_sieve(w_s, "accept")
        reg.cleanup_R_sieve(r_s, "accept")
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        t = reg.birth_accepted_transcript({})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        with self.assertRaises(LifetimeError):
            reg.birth_M_tail(
                b_rec,
                width_decl={"numeric_width": 128},
                enumeration_order_decl={},
                stopping_rule_decl={"invents_tau": False},
                shares_B_recovery_decl=False,
            )

    def test_tau_invention_forbidden(self):
        reg = self._prep()
        w_s = reg.birth_W_sieve({})
        r_s = reg.birth_R_sieve({}, {})
        reg.cleanup_W_sieve(w_s, "accept")
        reg.cleanup_R_sieve(r_s, "accept")
        reg.destroy_W_sieve(w_s)
        reg.destroy_R_sieve(r_s)
        t = reg.birth_accepted_transcript({})
        b_post = reg.birth_B_post(t)
        b_rec = reg.birth_B_recovery(b_post, t)
        with self.assertRaises(LifetimeError):
            reg.birth_M_tail(
                b_rec,
                width_decl={"unit": "symbolic"},
                enumeration_order_decl={},
                stopping_rule_decl={"invents_tau": True},
                shares_B_recovery_decl=False,
            )

    def test_f_input_on_malformed_x(self):
        reg = LifetimeRegistry()
        with self.assertRaises(LifetimeError):
            reg.birth_B_input(PublicInstance(token="bad", well_formed=False))
        self.assertIn(FailureChannel.F_input, reg.failures)


if __name__ == "__main__":
    unittest.main()

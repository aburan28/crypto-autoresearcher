#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_oracle.py --- known-answer tests for the exact joint-moment oracle.

Task: TASK-20260803-6f50df   Batch: BATCH-003   Goal: GOAL-HQC-001

Run:  python3 test_oracle.py            (prints the known-answer table, then
                                         runs every test)
      python3 test_oracle.py -q         (quiet: unittest output only)

DESIGN NOTE -- why this suite is structured the way it is.

A test suite that only checks the INDEPENDENT case cannot detect the bug that
matters.  The bug that matters for a high-order joint moment is OVER-COUNTING
COINCIDENCES, which inflates the estimate and therefore reads as POSITIVE
dependence -- precisely the direction the campaign is looking for.  So every
mechanism below is tested at all three signs:

    INDEPENDENT        i.i.d. Bernoulli coordinates; i.i.d. indicators
                       -> expected mu_k = p^k exactly
    NEGATIVELY DEP.    uniform global fixed weight (sampling without
                       replacement); exactly-c-failures
                       -> expected from inclusion-exclusion / C(n_e-k,c-k)
    POSITIVELY DEP.    latent mixture over a common parameter; comonotone
                       -> expected from mixture linearity / mu_k = p

and, separately, four MUTANT computations are run and required to be DETECTED
(mutant value != truth) with the direction of their error recorded.

Two further independence guarantees:
  * `bf_mu` is a brute-force reference written from the DEFINITION using
    fractions.Fraction only.  It shares no code path with AtomLaw,
    FailureLaw, or Route B.  If the oracle's integer machinery is wrong,
    bf_mu disagrees.
  * `ref_*` closed forms in oracle.py are derived on paper (inclusion-
    exclusion, hypergeometric block occupancy, mixture linearity) and touch
    none of the enumeration machinery.

Nothing in this file makes any statement about HQC.
"""

from __future__ import annotations

import math
import sys
import unittest
from fractions import Fraction
from itertools import combinations

import oracle as O

KAT = []          # (name, sign, k, expected, observed, mode, ok)


def record(name, sign, k, expected, observed, mode="must_agree"):
    """mode='must_agree'  : a known-answer test; PASS means exact equality.
       mode='must_differ' : a MUTANT comparison; PASS means the oracle
                            DETECTED the mutant, i.e. the values differ."""
    ok = (expected == observed) if mode == "must_agree" else (expected != observed)
    KAT.append((name, sign, k, expected, observed, mode, ok))
    return ok


# ==========================================================================
# INDEPENDENT BRUTE-FORCE REFERENCE  (Fraction only; no oracle machinery)
# ==========================================================================

def bf_mu(N, n2, weight_of, phi_of, J):
    """mu_k(J) straight from the definition:
       sum_v P[v] * prod_{j in J} phi(block_j(v)).
    `weight_of` and `phi_of` are supplied by the caller and are written
    without reference to oracle.AtomLaw / oracle.BlockModel."""
    bm = (1 << n2) - 1
    num = Fraction(0)
    tot = Fraction(0)
    for v in range(1 << N):
        wv = weight_of(v)
        if wv == 0:
            continue
        tot += wv
        pr = Fraction(1)
        for j in J:
            pr *= phi_of((v >> (j * n2)) & bm)
            if pr == 0:
                break
        num += wv * pr
    return num / tot


def bf_popcount(v):
    c = 0
    while v:
        c += v & 1
        v >>= 1
    return c


def bf_threshold_phi(t):
    return lambda c: Fraction(1) if bf_popcount(c) > t else Fraction(0)


def bf_bernoulli_weight(N, p):
    return lambda v: (p ** bf_popcount(v)) * ((1 - p) ** (N - bf_popcount(v)))


def bf_fixed_weight_weight(w):
    return lambda v: Fraction(1) if bf_popcount(v) == w else Fraction(0)


# ==========================================================================

class TestExactHelpers(unittest.TestCase):

    def test_comb_and_popcount(self):
        for n in range(0, 12):
            for k in range(-1, n + 2):
                self.assertEqual(O.comb(n, k), math.comb(n, k) if 0 <= k <= n else 0)
        for v in range(1024):
            self.assertEqual(O.popcount(v), bf_popcount(v))

    def test_log2_is_reporting_only_and_accurate(self):
        # exact powers of two must come back exactly
        for k in (-2000, -64, -1, 0, 1, 64, 2000):
            fr = Fraction(2) ** k
            self.assertAlmostEqual(O.log2_fraction(fr), float(k), places=9)
        # agreement with math.log2 on representable values
        for (a, b) in [(1, 3), (7, 11), (12345, 67891), (2 ** 200 + 1, 3 ** 130)]:
            fr = Fraction(a, b)
            self.assertAlmostEqual(O.log2_fraction(fr),
                                   math.log2(a) - math.log2(b), places=8)

    def test_safe_float_underflow_is_none_not_zero(self):
        tiny = Fraction(1, 2) ** 5000
        self.assertIsNone(O.safe_float(tiny))
        self.assertIsNotNone(O.log2_fraction(tiny))


class TestBlockModels(unittest.TestCase):

    def test_rm1_2_matches_hand_derivation(self):
        """RM(1,2) = [4,3,2] is the even-weight code.  Every odd-weight word is
        at distance 1 from exactly 4 codewords; 0 is among them iff the word
        has weight 1.  Every even-weight word IS a codeword."""
        m = O.RM1BlockModel(2, tie="split")
        self.assertEqual(m.scale, 4)
        expect = {0: Fraction(0), 1: Fraction(3, 4), 2: Fraction(1),
                  3: Fraction(1), 4: Fraction(1)}
        for v, f in enumerate(m.table()):
            self.assertEqual(Fraction(f, m.scale), expect[bf_popcount(v)],
                             "pattern %d" % v)

    def test_rm1_3_matches_extended_hamming_theory(self):
        """RM(1,3) = [8,4,4] extended Hamming, t = 1: weights 0 and 1 always
        decode correctly; weight 2 gives a 4-way tie including 0; weight >= 3
        always fails."""
        m = O.RM1BlockModel(3, tie="split")
        self.assertEqual(m.scale, 4)
        for v, f in enumerate(m.table()):
            w = bf_popcount(v)
            phi = Fraction(f, m.scale)
            if w <= 1:
                self.assertEqual(phi, 0)
            elif w == 2:
                self.assertEqual(phi, Fraction(3, 4))
            else:
                self.assertEqual(phi, 1)

    def test_rm1_tie_fail_policy_is_conservative(self):
        split = O.RM1BlockModel(2, tie="split")
        fail = O.RM1BlockModel(2, tie="fail")
        for v in range(1 << 4):
            self.assertGreaterEqual(Fraction(fail.table()[v], fail.scale),
                                    Fraction(split.table()[v], split.scale))

    def test_threshold_weight_mass_closed_form_matches_enumeration(self):
        for n2 in (3, 4, 5):
            for t in range(0, n2):
                m = O.ThresholdBlockModel(n2, t)
                brute = [0] * (n2 + 1)
                for v in range(1 << n2):
                    if bf_popcount(v) > t:
                        brute[bf_popcount(v)] += 1
                self.assertEqual(m.weight_mass(), brute)

    def test_weight_mass_matches_table_for_rm(self):
        m = O.RM1BlockModel(3, tie="split")
        brute = [0] * (m.n2 + 1)
        for v, f in enumerate(m.table()):
            brute[bf_popcount(v)] += f
        self.assertEqual(m.weight_mass(), brute)


class TestConventions(unittest.TestCase):

    def test_repeated_indices_are_refused(self):
        """CONVENTION C1.  A repeated index is the over-counting bug in its
        purest form; the oracle must refuse it rather than silently return a
        lower-order moment."""
        fl = O.fl_iid_indicator(5, Fraction(1, 3))
        with self.assertRaises(AssertionError):
            fl.mu((0, 0, 1))
        with self.assertRaises(AssertionError):
            fl.mu((2, 1, 2))
        fl.mu((0, 1, 2))       # distinct: fine

    def test_mu_bar_equals_normalised_binomial_moment(self):
        """CONVENTION C2 must be internally consistent: the subset average
        equals E[C(S,k)]/C(n_e,k) computed from the law of S."""
        for fl in (O.fl_iid_indicator(6, Fraction(2, 7)),
                   O.fl_exactly_c(6, 2),
                   O.fl_comonotone(6, Fraction(3, 11)),
                   O.build_failure_law(O.atomlaw_fixed_weight(12, 5),
                                       O.ThresholdBlockModel(3, 0), 4)):
            pS = fl.law_of_S()
            for k in range(1, fl.n_e + 1):
                lhs = fl.mu_bar(k) * O.comb(fl.n_e, k)
                rhs = sum((pS[s] * O.comb(s, k) for s in range(fl.n_e + 1)),
                          Fraction(0))
                self.assertEqual(lhs, rhs, "%s k=%d" % (fl.name, k))

    def test_mu_1_equals_marginal(self):
        fl = O.build_failure_law(O.atomlaw_fixed_weight(12, 5),
                                 O.ThresholdBlockModel(3, 1), 4)
        for j in range(4):
            self.assertEqual(fl.mu((j,)), fl.q(j))

    def test_everything_is_exact(self):
        fl = O.build_failure_law(O.atomlaw_iid_bernoulli(12, Fraction(1, 5)),
                                 O.ThresholdBlockModel(3, 1), 4)
        for k in range(1, 5):
            self.assertIsInstance(fl.mu_bar(k), Fraction)
            self.assertIsInstance(fl.binomial_moment(k), Fraction)
        for x in fl.law_of_S():
            self.assertIsInstance(x, Fraction)
        self.assertIsInstance(O.route_b_mu(4, 3, 5,
                                           O.ThresholdBlockModel(3, 1).weight_mass(),
                                           1, 2), Fraction)


class TestAgainstIndependentBruteForce(unittest.TestCase):
    """The oracle's integer machinery vs a Fraction-only implementation of the
    definition that shares no code with it."""

    def test_bernoulli_threshold(self):
        n_e, n2, t, p = 4, 3, 1, Fraction(2, 5)
        N = n_e * n2
        fl = O.build_failure_law(O.atomlaw_iid_bernoulli(N, p),
                                 O.ThresholdBlockModel(n2, t), n_e)
        wf, pf = bf_bernoulli_weight(N, p), bf_threshold_phi(t)
        for k in (1, 2, 3, 4):
            for J in combinations(range(n_e), k):
                self.assertEqual(fl.mu(J), bf_mu(N, n2, wf, pf, J),
                                 "J=%s" % (J,))

    def test_fixed_weight_threshold(self):
        n_e, n2, t, w = 4, 3, 0, 5
        N = n_e * n2
        fl = O.build_failure_law(O.atomlaw_fixed_weight(N, w),
                                 O.ThresholdBlockModel(n2, t), n_e)
        wf, pf = bf_fixed_weight_weight(w), bf_threshold_phi(t)
        for k in (1, 2, 3, 4):
            for J in combinations(range(n_e), k):
                self.assertEqual(fl.mu(J), bf_mu(N, n2, wf, pf, J))

    def test_rational_phi_tie_splitting(self):
        n_e, n2, p = 3, 4, Fraction(1, 3)
        N = n_e * n2
        model = O.RM1BlockModel(2, tie="split")
        fl = O.build_failure_law(O.atomlaw_iid_bernoulli(N, p), model, n_e)
        tab = model.table()
        pf = lambda c: Fraction(tab[c], model.scale)
        wf = bf_bernoulli_weight(N, p)
        for k in (1, 2, 3):
            for J in combinations(range(n_e), k):
                self.assertEqual(fl.mu(J), bf_mu(N, n2, wf, pf, J))

    def test_ring_law_against_full_five_tuple_enumeration(self):
        """The ring atom law is built by an integer Walsh-Hadamard
        convolution of truncated product laws.  Here it is checked against a
        literal enumeration of every (x, y, r1, r2, e)."""
        n, om, omr, ome, N, n_e, n2 = 7, 2, 1, 1, 6, 3, 2
        law = O.atomlaw_ring_hqc_shaped(n, om, omr, ome, N)
        mask = (1 << N) - 1
        brute = [0] * (1 << N)
        fw = lambda w: list(O._fixed_weight_masks(n, w))
        for x in fw(om):
            for r2 in fw(omr):
                a = O.ring_mul(x, r2, n)
                for r1 in fw(omr):
                    for y in fw(om):
                        b = O.ring_mul(r1, y, n)
                        for e in fw(ome):
                            brute[(a ^ b ^ e) & mask] += 1
        self.assertEqual(sum(brute), law.D)
        self.assertEqual(brute, law.weights)
        # and the resulting moments agree with the brute-force definition
        model = O.ThresholdBlockModel(n2, 0)
        fl = O.build_failure_law(law, model, n_e)
        wf = lambda v: Fraction(brute[v])
        pf = bf_threshold_phi(0)
        for k in (1, 2, 3):
            for J in combinations(range(n_e), k):
                self.assertEqual(fl.mu(J), bf_mu(N, n2, wf, pf, J))


class TestKnownAnswerIndependent(unittest.TestCase):
    """DUTY 3: the i.i.d.-by-construction null's exact mu_m must equal p_i^m,
    verified against the oracle's own enumeration."""

    def test_iid_bernoulli_coordinates_threshold(self):
        n_e, n2, t = 4, 3, 1
        N = n_e * n2
        for p in (Fraction(1, 4), Fraction(1, 3), Fraction(2, 5)):
            model = O.ThresholdBlockModel(n2, t)
            fl = O.build_failure_law(O.atomlaw_iid_bernoulli(N, p), model, n_e)
            p_i = O.ref_block_failure_prob_bernoulli(model.weight_mass(),
                                                     model.scale, n2, p)
            self.assertEqual(fl.q(0), p_i)
            for k in range(1, n_e + 1):
                expected = p_i ** k
                # every subset, not just the average
                for J in combinations(range(n_e), k):
                    self.assertEqual(fl.mu(J), expected)
                observed = fl.mu_bar(k)
                self.assertTrue(record("iid-bernoulli-threshold p=%s" % p,
                                       "independent", k, expected, observed))
                self.assertEqual(observed, expected)

    def test_iid_bernoulli_coordinates_rm_tiesplit(self):
        n_e, n2, p = 3, 4, Fraction(1, 3)
        N = n_e * n2
        model = O.RM1BlockModel(2, tie="split")
        fl = O.build_failure_law(O.atomlaw_iid_bernoulli(N, p), model, n_e)
        p_i = O.ref_block_failure_prob_bernoulli(model.weight_mass(),
                                                 model.scale, n2, p)
        for k in range(1, n_e + 1):
            expected = p_i ** k
            observed = fl.mu_bar(k)
            self.assertTrue(record("iid-bernoulli-RM(1,2)-tiesplit",
                                   "independent", k, expected, observed))
            self.assertEqual(observed, expected)

    def test_iid_indicator_level(self):
        n_e, p = 6, Fraction(3, 13)
        fl = O.fl_iid_indicator(n_e, p)
        for k in range(1, n_e + 1):
            expected = O.ref_iid(p, k)
            observed = fl.mu_bar(k)
            self.assertTrue(record("iid-indicator p=3/13", "independent", k,
                                   expected, observed))
            self.assertEqual(observed, expected)
            for J in combinations(range(n_e), k):
                self.assertEqual(fl.mu(J), expected)

    def test_product_of_independent_blocks(self):
        """Blocks built as an explicit PRODUCT law, pushed through the same
        generic machinery -- a second, structurally different construction of
        the null."""
        n_e, n2, p = 4, 3, Fraction(1, 4)
        blk = O.atomlaw_iid_bernoulli(n2, p)
        law = O.atomlaw_product_blocks([blk] * n_e)
        model = O.ThresholdBlockModel(n2, 1)
        fl = O.build_failure_law(law, model, n_e)
        p_i = O.ref_block_failure_prob_bernoulli(model.weight_mass(), 1, n2, p)
        for k in range(1, n_e + 1):
            expected = p_i ** k
            observed = fl.mu_bar(k)
            self.assertTrue(record("product-of-independent-blocks",
                                   "independent", k, expected, observed))
            self.assertEqual(observed, expected)


class TestKnownAnswerNegative(unittest.TestCase):

    def test_occupancy_inclusion_exclusion(self):
        n_e, n2, w = 4, 3, 5
        fl = O.build_failure_law(O.atomlaw_fixed_weight(n_e * n2, w),
                                 O.ThresholdBlockModel(n2, 0), n_e)
        q = fl.q(0)
        for k in range(1, n_e + 1):
            expected = O.ref_occupancy(n_e, n2, w, k)
            observed = fl.mu_bar(k)
            self.assertTrue(record("occupancy N=12 w=5", "negative", k,
                                   expected, observed))
            self.assertEqual(observed, expected)
            if k >= 2:
                self.assertLess(observed, q ** k,
                                "sampling without replacement must be "
                                "negatively dependent at k=%d" % k)

    def test_exactly_c(self):
        n_e, c = 7, 3
        fl = O.fl_exactly_c(n_e, c)
        q = fl.q(0)
        for k in range(1, 5):
            expected = O.ref_exactly_c(n_e, c, k)
            observed = fl.mu_bar(k)
            self.assertTrue(record("exactly-c n_e=7 c=3", "negative", k,
                                   expected, observed))
            self.assertEqual(observed, expected)
            if k >= 2:
                self.assertLess(observed, q ** k)

    def test_fixed_weight_threshold_negative_sign(self):
        n_e, n2, w, t = 4, 3, 6, 1
        model = O.ThresholdBlockModel(n2, t)
        fl = O.build_failure_law(O.atomlaw_fixed_weight(n_e * n2, w), model, n_e)
        q = fl.q(0)
        for k in range(2, n_e + 1):
            observed = fl.mu_bar(k)
            expected = O.route_b_mu(n_e, n2, w, model.weight_mass(), 1, k)
            self.assertTrue(record("fixed-weight+threshold (routeB ref)",
                                   "negative", k, expected, observed))
            self.assertEqual(observed, expected)
            self.assertLessEqual(observed, q ** k)


class TestKnownAnswerPositive(unittest.TestCase):

    def test_latent_mixture_strictly_positive(self):
        n_e, n2, t = 4, 3, 1
        N = n_e * n2
        p1, p2, lam = Fraction(1, 8), Fraction(1, 2), Fraction(1, 3)
        model = O.ThresholdBlockModel(n2, t)
        L1 = O.atomlaw_iid_bernoulli(N, p1)
        L2 = O.atomlaw_iid_bernoulli(N, p2)
        law = O.atomlaw_mixture([L1, L2], [lam, 1 - lam], "mix")
        fl = O.build_failure_law(law, model, n_e)
        A = model.weight_mass()
        q1 = O.ref_block_failure_prob_bernoulli(A, 1, n2, p1)
        q2 = O.ref_block_failure_prob_bernoulli(A, 1, n2, p2)
        qbar = lam * q1 + (1 - lam) * q2
        self.assertEqual(fl.q(0), qbar)
        for k in range(1, n_e + 1):
            expected = lam * q1 ** k + (1 - lam) * q2 ** k
            observed = fl.mu_bar(k)
            self.assertTrue(record("latent-mixture p=1/8,1/2 lam=1/3",
                                   "positive", k, expected, observed))
            self.assertEqual(observed, expected)
            if k >= 2:
                self.assertGreater(observed, qbar ** k,
                                   "Jensen: a latent mixture must be strictly "
                                   "positively dependent at k=%d" % k)

    def test_comonotone(self):
        n_e, p = 6, Fraction(1, 7)
        fl = O.fl_comonotone(n_e, p)
        for k in range(1, n_e + 1):
            expected = O.ref_comonotone(p, k)
            observed = fl.mu_bar(k)
            self.assertTrue(record("comonotone p=1/7", "positive", k,
                                   expected, observed))
            self.assertEqual(observed, expected)
            if k >= 2:
                self.assertGreater(observed, fl.q(0) ** k)

    def test_mixture_of_negative_components_is_positive(self):
        """Each component is negatively dependent; the mixture over the latent
        global weight is positively dependent.  Both mechanisms, one object."""
        n_e, n2, t = 4, 3, 1
        N = n_e * n2
        lam = Fraction(1, 2)
        model = O.ThresholdBlockModel(n2, t)
        L1 = O.atomlaw_fixed_weight(N, 3)
        L2 = O.atomlaw_fixed_weight(N, 9)
        f1 = O.build_failure_law(L1, model, n_e)
        f2 = O.build_failure_law(L2, model, n_e)
        fl = O.build_failure_law(O.atomlaw_mixture([L1, L2], [lam, 1 - lam],
                                                   "mixfw"), model, n_e)
        qbar = lam * f1.q(0) + (1 - lam) * f2.q(0)
        for k in range(2, n_e + 1):
            self.assertLessEqual(f1.mu_bar(k), f1.q(0) ** k)
            self.assertLessEqual(f2.mu_bar(k), f2.q(0) ** k)
            expected = lam * f1.mu_bar(k) + (1 - lam) * f2.mu_bar(k)
            observed = fl.mu_bar(k)
            self.assertTrue(record("mixture-of-fixed-weight w=3,9",
                                   "positive", k, expected, observed))
            self.assertEqual(observed, expected)
        self.assertGreater(fl.mu_bar(2), qbar ** 2)


class TestRoutesAgree(unittest.TestCase):

    def test_route_a_vs_route_b_threshold(self):
        for (n_e, n2, w, t) in [(4, 3, 5, 0), (4, 3, 6, 1), (3, 4, 7, 1),
                                (5, 2, 4, 0)]:
            model = O.ThresholdBlockModel(n2, t)
            fl = O.build_failure_law(O.atomlaw_fixed_weight(n_e * n2, w),
                                     model, n_e)
            A = model.weight_mass()
            for k in range(1, n_e + 1):
                self.assertEqual(fl.mu_bar(k),
                                 O.route_b_mu(n_e, n2, w, A, 1, k),
                                 "n_e=%d n2=%d w=%d t=%d k=%d" % (n_e, n2, w, t, k))

    def test_route_a_vs_route_b_rational_phi(self):
        n_e, n2, w = 3, 4, 5
        model = O.RM1BlockModel(2, tie="split")
        fl = O.build_failure_law(O.atomlaw_fixed_weight(n_e * n2, w), model, n_e)
        A = model.weight_mass()
        for k in range(1, n_e + 1):
            self.assertEqual(fl.mu_bar(k),
                             O.route_b_mu(n_e, n2, w, A, model.scale, k))

    def test_route_b_reduces_to_iid_when_it_should_not(self):
        """Guard against a Route B that silently returns p^k: on a fixed-weight
        ensemble it must NOT equal q^k for k >= 2."""
        n_e, n2, w, t = 5, 4, 8, 1
        model = O.ThresholdBlockModel(n2, t)
        A = model.weight_mass()
        q = O.route_b_mu(n_e, n2, w, A, 1, 1)
        for k in (2, 3):
            self.assertNotEqual(O.route_b_mu(n_e, n2, w, A, 1, k), q ** k)


class TestMutantsDetected(unittest.TestCase):
    """DUTY 4: the failure mode that LOOKS LIKE SIGNAL."""

    def _cfgs(self):
        n_e, n2 = 4, 3
        N = n_e * n2
        model = O.ThresholdBlockModel(n2, 1)
        return [
            ("independent",
             O.build_failure_law(O.atomlaw_iid_bernoulli(N, Fraction(1, 3)),
                                 model, n_e)),
            ("negative",
             O.build_failure_law(O.atomlaw_fixed_weight(N, 6), model, n_e)),
            ("positive",
             O.build_failure_law(
                 O.atomlaw_mixture([O.atomlaw_iid_bernoulli(N, Fraction(1, 8)),
                                    O.atomlaw_iid_bernoulli(N, Fraction(1, 2))],
                                   [Fraction(1, 2), Fraction(1, 2)], "mix"),
                 model, n_e)),
        ]

    def test_m1_over_counts_and_is_detected(self):
        """M1 draws indices WITH REPLACEMENT.  Because F^2 = F it must be
        >= the truth, strictly so whenever S is non-degenerate, and it must be
        detected by comparison against the oracle."""
        for sign, fl in self._cfgs():
            m = 3
            ex = O.mutant_expectations(fl, m)
            truth = ex["truth_mu_bar_m"]
            m1 = ex["M1_indices_with_replacement"]
            self.assertGreater(m1, truth,
                               "M1 must over-count on %s" % sign)
            self.assertNotEqual(m1, truth)
            record("mutant M1 (with replacement) on %s ensemble" % sign,
                   sign, m, truth, m1, mode="must_differ")

    def test_m1_manufactures_positive_dependence_on_a_null(self):
        """The specific catastrophe: on an INDEPENDENT ensemble the
        with-replacement mutant reports a value ABOVE p^m, which a naive
        reader converts into 'positive correlation found'."""
        n_e, n2 = 4, 3
        model = O.ThresholdBlockModel(n2, 1)
        fl = O.build_failure_law(
            O.atomlaw_iid_bernoulli(n_e * n2, Fraction(1, 3)), model, n_e)
        q = fl.q(0)
        m = 3
        self.assertEqual(fl.mu_bar(m), q ** m)          # truth: independent
        m1 = O.mutant_expectations(fl, m)["M1_indices_with_replacement"]
        self.assertGreater(m1, q ** m)                  # mutant: "positive"

    def test_wrong_denominator_mutants_are_detected(self):
        for sign, fl in self._cfgs():
            m = 3
            ex = O.mutant_expectations(fl, m)
            truth = ex["truth_mu_bar_m"]
            for key in ("M2_ordered_distinct_wrong_denominator",
                        "M3_binomial_count_wrong_denominator"):
                self.assertNotEqual(ex[key], truth, "%s on %s" % (key, sign))
                self.assertLess(ex[key], truth)
            record("mutant M2 (wrong denominator) on %s" % sign, sign, m,
                   truth, ex["M2_ordered_distinct_wrong_denominator"],
                   mode="must_differ")
            record("mutant M3 (wrong denominator) on %s" % sign, sign, m,
                   truth, ex["M3_binomial_count_wrong_denominator"],
                   mode="must_differ")

    def test_fixed_subset_mutant_is_exact_iff_exchangeable(self):
        """M4 uses one fixed subset.  It is exact on an exchangeable ensemble
        and biased on a non-exchangeable one -- so a suite that only tests
        exchangeable ensembles would never see it."""
        n_e, n2 = 4, 3
        model = O.ThresholdBlockModel(n2, 1)
        fl_ex = O.build_failure_law(
            O.atomlaw_iid_bernoulli(n_e * n2, Fraction(1, 3)), model, n_e)
        self.assertEqual(O.mutant_expectations(fl_ex, 3)["M4_single_fixed_subset_0..m-1"],
                         fl_ex.mu_bar(3))
        # a deliberately NON-exchangeable ensemble: block 0 has a different
        # coordinate law from the others
        b0 = O.atomlaw_iid_bernoulli(n2, Fraction(1, 2))
        b1 = O.atomlaw_iid_bernoulli(n2, Fraction(1, 8))
        law = O.atomlaw_product_blocks([b0, b1, b1, b1])
        fl_ne = O.build_failure_law(law, model, n_e)
        self.assertNotEqual(fl_ne.q(0), fl_ne.q(1))
        self.assertNotEqual(
            O.mutant_expectations(fl_ne, 3)["M4_single_fixed_subset_0..m-1"],
            fl_ne.mu_bar(3))


class TestSubsetExchangeability(unittest.TestCase):

    def test_exchangeable_ensembles_have_one_value_per_k(self):
        n_e, n2 = 4, 3
        model = O.ThresholdBlockModel(n2, 1)
        for law in (O.atomlaw_iid_bernoulli(n_e * n2, Fraction(1, 3)),
                    O.atomlaw_fixed_weight(n_e * n2, 5)):
            fl = O.build_failure_law(law, model, n_e)
            for k in range(1, n_e + 1):
                self.assertEqual(len(set(fl.mu_all_subsets(k).values())), 1)

    def test_ring_block_shift_equivariance(self):
        """DERIVATION, then verification: the law of e' is invariant under
        cyclic shift of F_2^n, and B_{j+1} is the translate of B_j by n_2, so
        mu(J) = mu(J+1) whenever the shifted set still lies inside the
        retained window."""
        n, om, omr, ome, n_e, n2 = 13, 2, 2, 2, 3, 4
        law = O.atomlaw_ring_hqc_shaped(n, om, omr, ome, n_e * n2)
        fl = O.build_failure_law(law, O.ThresholdBlockModel(n2, 1), n_e)
        for k in (1, 2):
            for J in combinations(range(n_e), k):
                if max(J) + 1 <= n_e - 1:
                    self.assertEqual(fl.mu(J),
                                     fl.mu(tuple(j + 1 for j in J)))

    def test_ring_full_exchangeability_is_not_assumed(self):
        """The oracle must be able to DETECT a ring configuration whose
        subsets are not all equal, rather than averaging the difference away
        silently.  (Whether any particular configuration is exchangeable is an
        observation, not an assumption.)"""
        n, om, omr, ome, n_e, n2 = 17, 3, 2, 2, 4, 4
        law = O.atomlaw_ring_hqc_shaped(n, om, omr, ome, n_e * n2)
        fl = O.build_failure_law(law, O.ThresholdBlockModel(n2, 1), n_e)
        vals = set(fl.mu_all_subsets(2).values())
        self.assertGreater(len(vals), 1,
                           "this configuration is expected to be "
                           "non-exchangeable at k=2")
        self.assertTrue(min(vals) < fl.mu_bar(2) < max(vals))


class TestNullGeneratorAndEstimator(unittest.TestCase):

    def test_generator_is_deterministic_given_seed(self):
        g1 = O.IIDNullGenerator(8, Fraction(1, 4), 12345)
        g2 = O.IIDNullGenerator(8, Fraction(1, 4), 12345)
        self.assertEqual([g1.sample() for _ in range(500)],
                         [g2.sample() for _ in range(500)])
        g3 = O.IIDNullGenerator(8, Fraction(1, 4), 12346)
        self.assertNotEqual([g1.sample() for _ in range(500)],
                            [g3.sample() for _ in range(500)])

    def test_canonical_estimator_is_unbiased_within_4_sigma(self):
        n_e, p, m, T = 8, Fraction(1, 4), 3, 100000
        gen = O.IIDNullGenerator(n_e, p, 777)
        fl = gen.exact_law()
        exact = fl.mu_bar(m)
        self.assertEqual(exact, p ** m)
        masks = [gen.sample() for _ in range(T)]
        est = O.canonical_estimator(masks, n_e, m)
        sd = math.sqrt(float(O.exact_estimator_variance(fl, m)) / T)
        self.assertLess(abs(float(est) - float(exact)) / sd, 4.0)

    def test_mutant_estimator_is_many_sigma_off(self):
        n_e, p, m, T = 8, Fraction(1, 4), 3, 100000
        gen = O.IIDNullGenerator(n_e, p, 777)
        fl = gen.exact_law()
        exact = fl.mu_bar(m)
        masks = [gen.sample() for _ in range(T)]
        mut = O.mutant_estimator_M1(masks, n_e, m)
        sd = math.sqrt(float(O.exact_estimator_variance(fl, m)) / T)
        self.assertGreater(abs(float(mut) - float(exact)) / sd, 20.0)

    def test_ring_sampler_matches_exact_oracle(self):
        """The strongest statement the oracle can make about itself: a direct
        sampler of the same toy ensemble converges to the oracle's exact
        mu_m."""
        n, om, omr, ome, n_e, n2, m, T = 13, 2, 2, 2, 3, 4, 2, 60000
        model = O.ThresholdBlockModel(n2, 1)
        law = O.atomlaw_ring_hqc_shaped(n, om, omr, ome, n_e * n2)
        fl = O.build_failure_law(law, model, n_e)
        gen = O.ring_sampler(n, om, omr, ome, n_e * n2, n_e, model, 4242)
        masks = [next(gen) for _ in range(T)]
        est = O.canonical_estimator(masks, n_e, m)
        exact = fl.mu_bar(m)
        sd = math.sqrt(float(O.exact_estimator_variance(fl, m)) / T)
        z = (float(est) - float(exact)) / sd
        self.assertLess(abs(z), 4.0, "sampler z=%.2f vs exact oracle" % z)


class TestReachAndGuards(unittest.TestCase):

    def test_enumeration_refuses_oversized_configurations(self):
        with self.assertRaises(ValueError):
            O.atomlaw_iid_bernoulli(O.ENUM_MAX_N + 1, Fraction(1, 2))
        with self.assertRaises(ValueError):
            O.ThresholdBlockModel(O.ENUM_MAX_BLOCK + 1, 2).table()

    def test_route_b_reaches_hqc_sized_dimensions(self):
        """Route B is exact at dimensions where Route A is impossible.  The
        ensemble is uniform fixed weight with a threshold block decoder; this
        is NOT HQC and the value is not an HQC quantity."""
        n_e, n2, w, t, m = 46, 384, 75, 3, 16
        A = O.ThresholdBlockModel(n2, t).weight_mass()
        q = O.route_b_mu(n_e, n2, w, A, 1, 1)
        mu = O.route_b_mu(n_e, n2, w, A, 1, m)
        self.assertIsInstance(mu, Fraction)
        self.assertGreater(q, 0)
        self.assertLessEqual(mu, q ** m)      # negative dependence

    def test_failure_law_mass_is_exact(self):
        fl = O.build_failure_law(O.atomlaw_fixed_weight(12, 5),
                                 O.ThresholdBlockModel(3, 1), 4)
        self.assertEqual(sum(fl.sig_weights.values()), fl.D)
        self.assertEqual(sum(fl.law_of_S()), 1)
        self.assertEqual(sum(fl.mask_law().values()), 1)


def _print_kat_table():
    if not KAT:
        return
    print("\n" + "=" * 118)
    print("KNOWN-ANSWER TABLE  (all values exact; 'expected' is an INDEPENDENT "
          "closed form or the oracle truth)")
    print("=" * 118)
    print("%-44s %-11s %2s  %-26s %-26s %s"
          % ("case", "sign", "k", "expected", "observed", "verdict"))
    print("-" * 118)
    for name, sign, k, exp, obs, mode, ok in KAT:
        se, so = str(exp), str(obs)
        if len(se) > 26:
            se = se[:23] + "..."
        if len(so) > 26:
            so = so[:23] + "..."
        if mode == "must_agree":
            verdict = "AGREE" if ok else "*** MISMATCH ***"
        else:
            verdict = "MUTANT DETECTED" if ok else "*** MUTANT MISSED ***"
        print("%-44s %-11s %2d  %-26s %-26s %s"
              % (name[:44], sign, k, se, so, verdict))
    print("-" * 118)
    agree = [r for r in KAT if r[5] == "must_agree"]
    differ = [r for r in KAT if r[5] == "must_differ"]
    print("known-answer comparisons that MUST AGREE : %d, agreeing exactly: %d"
          % (len(agree), sum(1 for r in agree if r[6])))
    print("mutant comparisons that MUST DIFFER      : %d, detected: %d"
          % (len(differ), sum(1 for r in differ if r[6])))
    print("=" * 118 + "\n")


if __name__ == "__main__":
    quiet = "-q" in sys.argv
    argv = [a for a in sys.argv if a != "-q"]
    runner = unittest.main(argv=argv, exit=False, verbosity=1 if quiet else 2)
    if not quiet:
        _print_kat_table()
    sys.exit(0 if runner.result.wasSuccessful() else 1)

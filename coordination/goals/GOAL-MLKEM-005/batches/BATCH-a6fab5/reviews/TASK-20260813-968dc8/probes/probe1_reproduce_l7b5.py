#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 1 -- TASK-20260813-968dc8

Independently re-implements (in THIS file, without importing either
measure_relvar.py or measure_hkz_indep.py) both:
  (a) ROUTE-P's algorithm, as described in measure_relvar.py's hkz_profile
      (Gram-based GSO.Mat(A, gram=True), BKZReduction with an explicit
      Strategy list, HKZ sweep, logdet = 0.5*sum(log(r)))
  (b) ROUTE-I'''s algorithm, as described in measure_hkz_indep.py's
      hkz_route_ii (basis-based GSO.Mat(A, float_type="double"),
      BKZReduction without an explicit strategy list, HKZ sweep,
      logdet = (d-k)*log(q) exact closed form)

for lattice L7 (d=20, k=6), basis indices 0 and 1, and reports:
  - whether the raw r vectors (squared GSO norms after reduction) are
    bit-identical between the two GSO-construction paths
  - how much of the reported hkz-value difference is attributable to the
    logdet-computation difference alone (same r, two logdet formulas) vs.
    genuine r differences
  - comparison against the producer's own reported route_p_values /
    route_ii_values for hkz/L7_b5 (basis 0 and 1)

This directly probes the producer's own explanation in hkz_indep_writeup.md
section 8: "both routes reach the identical true HKZ profile and differ only
by floating-point summation-order rounding ... in the final mean()/log()
arithmetic of the hkz observable's own formula, not by any true disagreement
in the reduced basis itself."
"""
import math
import numpy as np
from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration, EnumerationError
from fpylll.fplll.bkz_param import Strategy
from fpylll.algorithms.bkz import BKZReduction as BKZReductionAlgo
from fpylll.fplll.bkz import BKZReduction as BKZReductionLowLevel

Q = 3329
D, K = 20, 6
HKZ_MAX_SWEEP = 30


def make_A(d, k, q, i):
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis(d, k, q, i):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def gram_int(M):
    G = M @ M.T
    Gr = np.rint(G)
    devmax = float(np.max(np.abs(G - Gr))) if G.size else 0.0
    return Gr, devmax, float(np.max(np.abs(Gr)))


# ---------------------------------------------------------- ROUTE-P (Gram-based)
def route_p_reduce(B, d):
    """Verbatim reproduction of measure_relvar.py's hkz_profile algorithm
    (Gram-based GSO construction, explicit Strategy list, BKZ.Param with
    strategies=strat)."""
    Gr, devmax, gmax = gram_int(B.astype(np.float64))
    A = IntegerMatrix(d, d)
    for i in range(d):
        for j in range(d):
            A[i, j] = int(Gr[i, j])
    Mg = GSO.Mat(A, gram=True)
    Mg.update_gso()
    LLL.Reduction(Mg)()
    strat = [Strategy(b) for b in range(d + 1)]
    bk = BKZReductionAlgo(Mg)
    bk(BKZ.Param(block_size=d, strategies=strat, max_loops=1, flags=BKZ.MAX_LOOPS))
    for sweeps in range(HKZ_MAX_SWEEP):
        changed = False
        for i in range(d - 1):
            ri = Mg.get_r(i, i)
            try:
                nd, sol = Enumeration(Mg).enumerate(i, d, ri, 0)[0]
            except EnumerationError:
                continue
            if nd < ri * (1 - 1e-12):
                bk.svp_postprocessing(i, d - i, sol)
                Mg.update_gso()
                changed = True
        if not changed:
            break
    r = np.array([Mg.get_r(i, i) for i in range(d)], dtype=float)
    return r


# ---------------------------------------------------------- ROUTE-I'' (basis-based)
def route_ii_reduce(B, d):
    """Verbatim reproduction of measure_hkz_indep.py's hkz_route_ii algorithm
    (basis-based GSO construction via IntegerMatrix directly, no explicit
    Strategy list, BKZReduction(M, lll_obj, param) 3-arg form)."""
    A = IntegerMatrix(d, d)
    for r_ in range(d):
        for c_ in range(d):
            A[r_, c_] = int(B[r_, c_])
    M = GSO.Mat(A, float_type="double")
    M.update_gso()
    lll_obj = LLL.Reduction(M)
    lll_obj()
    M.update_gso()
    param = BKZ.Param(block_size=d, max_loops=1, flags=BKZ.MAX_LOOPS)
    bkz = BKZReductionLowLevel(M, lll_obj, param)
    bkz()
    M.update_gso()
    round_no = 0
    MAX_ROUNDS = 40
    while round_no < MAX_ROUNDS:
        round_no += 1
        any_improved = False
        for idx in range(d - 1):
            r_idx = M.get_r(idx, idx)
            try:
                sol_nd, sol_vec = Enumeration(M).enumerate(idx, d, r_idx, 0)[0]
            except EnumerationError:
                continue
            if sol_nd < r_idx * (1.0 - 1e-12):
                bkz.svp_postprocessing(idx, d - idx, sol_vec)
                M.update_gso()
                any_improved = True
        if not any_improved:
            break
    r = np.array([M.get_r(idx, idx) for idx in range(d)], dtype=float)
    return r


def hkz_value_routep_formula(r, d, k, beta):
    """ROUTE-P's own logdet: 0.5*sum(log(r)) (recomputed from the reduced r
    itself, subject to summation rounding)."""
    logb = 0.5 * np.log(r)
    logdet = 0.5 * float(np.sum(np.log(r)))
    return float(np.mean(logb[d - beta:]) - logdet / d)


def hkz_value_routeii_formula(r, d, k, beta, q):
    """ROUTE-I'''s own logdet: (d-k)*log(q) exact closed form."""
    logb = 0.5 * np.log(np.maximum(r, 1e-300))
    logdet = (d - k) * math.log(q)
    return float(np.mean(logb[d - beta:]) - logdet / d)


if __name__ == "__main__":
    beta = 5
    print("=" * 70)
    print("Probe 1: independent re-derivation, lattice L7 (d=20,k=6), beta=5")
    print("=" * 70)
    for i in (0, 1, 2, 3):
        B = build_basis(D, K, Q, i)
        r_p = route_p_reduce(B, D)
        r_ii = route_ii_reduce(B, D)
        r_bit_identical = np.array_equal(r_p, r_ii)
        max_r_diff = float(np.max(np.abs(r_p - r_ii)))

        hkz_p_on_rp = hkz_value_routep_formula(r_p, D, K, beta)
        hkz_ii_on_rii = hkz_value_routeii_formula(r_ii, D, K, beta, Q)
        # Cross-check: same r (r_p), two different logdet formulas
        hkz_p_formula_on_rp = hkz_value_routep_formula(r_p, D, K, beta)
        hkz_ii_formula_on_rp = hkz_value_routeii_formula(r_p, D, K, beta, Q)

        print("\n-- basis i=%d --" % i)
        print("  r bit-identical between Gram-based and basis-based GSO: %s"
              % r_bit_identical)
        print("  max |r_p - r_ii| (raw GSO norms): %.6e" % max_r_diff)
        print("  hkz via ROUTE-P code+formula on its own r:   %.17g" % hkz_p_on_rp)
        print("  hkz via ROUTE-I'' code+formula on its own r: %.17g" % hkz_ii_on_rii)
        print("  |difference| (full, both routes independent): %.6e"
              % abs(hkz_p_on_rp - hkz_ii_on_rii))
        print("  -- isolating the logdet-formula-only effect (same r = r_p) --")
        print("  hkz with ROUTE-P's logdet formula on r_p:   %.17g" % hkz_p_formula_on_rp)
        print("  hkz with ROUTE-I''s logdet formula on r_p:  %.17g" % hkz_ii_formula_on_rp)
        print("  |difference from logdet formula alone|: %.6e"
              % abs(hkz_p_formula_on_rp - hkz_ii_formula_on_rp))

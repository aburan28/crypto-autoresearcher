#!/usr/bin/env python3
"""Independent re-derivation of ARM C's two C_0 lower bounds from HEUR-1
(H-SEMBIN-4a80f3) -- written BEFORE opening experiments/EXP-SEMBIN-db9bc3/code/.

Model (HEUR-1 as restated in the review plan N1): #Fb_i = 2 * Bin(2^{C_0}, 1/2)
-- each of the 2^{C_0} x-values in a coset of a C_0-dimensional F_2-subspace is
an x-coordinate of a curve point with probability 1/2, and each such x gives two
points. E[#Fb_i] = 2^{C_0}. m cosets, m = ceil(n / C_0) (rounding recorded; also
computed with real m = n / C_0).

Bound A: Pr[all m nonempty] = (1 - 2^{-2^{C_0}})^m >= 1 - eps.
Bound B: total Jensen deficit m * (log2 E[X] - E[log2 X]) <= tol bits, with the
expectation E[log2 X] under two conditionings:
  (cond)   E[log2 X | X >= 1]                  -- empty event excluded
  (yield)  sum_{x>=1} P(X=x) log2 x            -- empty event contributes 0 to the
           log-yield and its probability mass is charged into the failure
           probability instead (recorded separately as m * P(X = 0)).
"""
import json
import math
import sys
from math import lgamma, log, log2

LABELS = [163, 233, 283, 409, 571]
BIG = [16384, 65536]


def log_binom_pmf(t, j):
    # log P(Bin(t, 1/2) = j)
    return lgamma(t + 1) - lgamma(j + 1) - lgamma(t - j + 1) - t * log(2)


def elog2_X(c0):
    """Return (E[log2 X | X>=1], sum_{x>=1} P(x) log2 x, P(X=0)) for X = 2 Bin(2^c0, 1/2)."""
    t = 2 ** c0
    p0 = math.exp(-t * log(2))  # P(Bin = 0) = 2^{-t}
    acc = 0.0
    for j in range(1, t + 1):
        pj = math.exp(log_binom_pmf(t, j))
        acc += pj * log2(2 * j)
    cond = acc / (1.0 - p0)
    return cond, acc, p0


def bound_a(n, eps, m_mode="ceil"):
    c0 = 1
    while True:
        m = math.ceil(n / c0) if m_mode == "ceil" else n / c0
        t = 2 ** c0
        # log(1 - 2^{-t}) computed stably
        log_pall = m * math.log1p(-math.exp(-t * log(2)))
        if log_pall >= math.log1p(-eps):
            return c0
        c0 += 1
        if c0 > 40:
            return None


def bound_b(n, tol_bits, conditioning="cond", m_mode="ceil"):
    c0 = 1
    while True:
        m = math.ceil(n / c0) if m_mode == "ceil" else n / c0
        cond, yld, p0 = elog2_X(c0)
        e_log = cond if conditioning == "cond" else yld
        deficit = m * (c0 - e_log)
        if deficit <= tol_bits:
            return c0, deficit, m * p0
        c0 += 1
        if c0 > 40:
            return None, None, None


def main():
    out = {"model": "X = 2*Bin(2^C0, 1/2); m = ceil(n/C0) unless stated",
           "bound_A": {}, "bound_B": {}, "per_c0_deficit_table": {}}
    for c0 in range(1, 14):
        cond, yld, p0 = elog2_X(c0)
        out["per_c0_deficit_table"][c0] = {
            "E_log2_X_given_nonempty": cond,
            "sum_nonempty_P_log2X": yld,
            "P_empty": p0,
            "deficit_per_coset_cond_bits": c0 - cond,
            "deficit_per_coset_yield_bits": c0 - yld,
        }
    for n in LABELS + BIG:
        row = {}
        for eps in (0.01, 0.05, 0.5):
            row[f"eps={eps}"] = bound_a(n, eps)
        row["eps=0.05,real_m"] = bound_a(n, 0.05, m_mode="real")
        out["bound_A"][n] = row
        rowb = {}
        for tol in (0.5, 1.0, 2.0):
            for cnd in ("cond", "yield"):
                c0, d, mp0 = bound_b(n, tol, cnd)
                rowb[f"tol={tol},{cnd}"] = {"C0": c0, "deficit_bits": d, "m*P_empty": mp0}
        c0, d, mp0 = bound_b(n, 1.0, "cond", m_mode="real")
        rowb["tol=1.0,cond,real_m"] = {"C0": c0, "deficit_bits": d, "m*P_empty": mp0}
        out["bound_B"][n] = rowb
    json.dump(out, sys.stdout, indent=1)
    print()
    # compact table
    print("\nBOUND A (C0):  n | eps=0.01 | eps=0.05 | eps=0.5 | eps=0.05 real m")
    for n in LABELS + BIG:
        r = out["bound_A"][n]
        print(f"{n:6d} | {r['eps=0.01']} | {r['eps=0.05']} | {r['eps=0.5']} | {r['eps=0.05,real_m']}")
    print("\nBOUND B (C0): n | tol0.5 cond | tol1 cond | tol2 cond | tol0.5 yield | tol1 yield | tol2 yield | tol1 cond real m")
    for n in LABELS + BIG:
        r = out["bound_B"][n]
        ks = ["tol=0.5,cond", "tol=1.0,cond", "tol=2.0,cond", "tol=0.5,yield", "tol=1.0,yield", "tol=2.0,yield", "tol=1.0,cond,real_m"]
        print(f"{n:6d} | " + " | ".join(str(r[k]["C0"]) for k in ks))


if __name__ == "__main__":
    main()

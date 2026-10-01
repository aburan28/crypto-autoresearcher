#!/usr/bin/env python3
"""N1, step (1)+(2): independent re-derivation of ARM C's two C_0 bounds and
their sensitivity, from HEUR-1 (H-SEMBIN-4a80f3) and the review plan's N1
statement ONLY.  Written and run before opening
experiments/EXP-SEMBIN-db9bc3/code/arm_c_coset.py.

Model: #Fb_i = 2 * Bin(2^{C_0}, 1/2); E[#Fb_i] = 2^{C_0}; m cosets with
m = ceil(n / C_0) (the `real_m` variant uses m = n/C_0).

Bound A: Pr[all m nonempty] = (1 - 2^{-2^{C_0}})^m >= 1 - eps.
Bound B: total Jensen deficit  D(C_0) = m * (log2 E#Fb_i - E log2 #Fb_i) <= tol.

IMPORTANT: the per-coset deficit d(C_0) = C_0 - E[log2 X] is NOT monotone in
C_0 (it is negative at C_0 = 1 under the conditional reading, peaks at C_0 = 3,
then halves per step).  A *lower bound on C_0* must therefore be read as the
monotone closure -- the least C_0 such that the condition holds at C_0 and at
every larger C_0 -- not as "the first C_0 that happens to satisfy it".  Both
readings are computed and reported so the difference is visible.
"""
import json
import math
import sys
from math import lgamma, log, log2

LABELS = [163, 233, 283, 409, 571]
BIG = [1024, 4096, 16384, 65536, 1 << 20]
CMAX = 34


def log_binom_pmf(t, j):
    return lgamma(t + 1) - lgamma(j + 1) - lgamma(t - j + 1) - t * log(2)


def elog2_X(c0):
    """(E[log2 X | X>=1], sum_{x>=1} P(x) log2 x, P(X=0)) for X = 2 Bin(2^c0, 1/2).

    Exact summation while 2^c0 <= 2^16; beyond that use the asymptotic
    expansion E[log2 B] = log2(t/2) - 1/(2 t ln 2) + O(t^-2), whose accuracy is
    checked against the exact value on the overlap.
    """
    t = 2 ** c0
    if t <= 65536:
        p0 = math.exp(-t * log(2))
        acc = 0.0
        for j in range(1, t + 1):
            acc += math.exp(log_binom_pmf(t, j)) * log2(2 * j)
        cond = acc / (1.0 - p0) if p0 < 1 else float("nan")
        return cond, acc, p0
    approx = c0 - 1.0 / (2 * t * log(2))
    return approx, approx, 0.0


def deficit_per_coset(c0, conditioning):
    cond, yld, p0 = elog2_X(c0)
    e_log = cond if conditioning == "cond" else yld
    return c0 - e_log, p0


def m_of(n, c0, m_mode):
    return math.ceil(n / c0) if m_mode == "ceil" else n / c0


def bound_a(n, eps, m_mode="ceil", monotone=True):
    ok = []
    for c0 in range(1, CMAX + 1):
        m = m_of(n, c0, m_mode)
        log_pall = m * math.log1p(-math.exp(-(2 ** c0) * log(2))) if c0 < 11 else -m * math.exp(-(2 ** c0) * log(2))
        ok.append(log_pall >= math.log1p(-eps))
    return _threshold(ok, monotone)


def bound_b(n, tol, conditioning="cond", m_mode="ceil", monotone=True):
    ok = []
    for c0 in range(1, CMAX + 1):
        d, _ = deficit_per_coset(c0, conditioning)
        ok.append(m_of(n, c0, m_mode) * d <= tol)
    return _threshold(ok, monotone)


def _threshold(ok, monotone):
    """least C_0 with the condition true (monotone: true at C_0 and all above)."""
    if monotone:
        for i in range(len(ok)):
            if all(ok[i:]):
                return i + 1
        return None
    for i, v in enumerate(ok):
        if v:
            return i + 1
    return None


def main():
    out = {
        "model": "X = 2*Bin(2^C0,1/2); m = ceil(n/C0) unless stated; threshold = monotone closure",
        "per_c0": {},
        "bound_A": {},
        "bound_B": {},
        "bound_B_first_satisfying_not_closure": {},
        "total_deficit_table": {},
        "asymptotic_check": {},
    }
    for c0 in range(1, 18):
        cond, yld, p0 = elog2_X(c0)
        out["per_c0"][c0] = {
            "E_log2X_given_nonempty": cond,
            "sum_nonempty_P_log2X": yld,
            "P_empty": p0,
            "deficit_cond_bits": c0 - cond,
            "deficit_yield_bits": c0 - yld,
            "asymptotic_1_over_2t_ln2": 1.0 / (2 * (2 ** c0) * log(2)),
        }
    for n in LABELS + BIG:
        ra = {f"eps={e}": bound_a(n, e) for e in (0.01, 0.05, 0.5)}
        ra["eps=0.05_real_m"] = bound_a(n, 0.05, m_mode="real")
        ra["eps=0.05_first_satisfying"] = bound_a(n, 0.05, monotone=False)
        out["bound_A"][n] = ra
        rb = {}
        for tol in (0.5, 1.0, 2.0):
            for cnd in ("cond", "yield"):
                rb[f"tol={tol}_{cnd}"] = bound_b(n, tol, cnd)
        rb["tol=1.0_cond_real_m"] = bound_b(n, 1.0, "cond", m_mode="real")
        out["bound_B"][n] = rb
        out["bound_B_first_satisfying_not_closure"][n] = bound_b(n, 1.0, "cond", monotone=False)
        out["total_deficit_table"][n] = {
            c0: m_of(n, c0, "ceil") * deficit_per_coset(c0, "cond")[0] for c0 in range(1, 15)
        }
    # growth-order check: C_0 ~ log2 n - log2 log2 n + O(1) for bound B
    for n in [163, 571, 4096, 65536, 1 << 20]:
        b = bound_b(n, 1.0)
        out["asymptotic_check"][n] = {
            "bound_B": b,
            "log2n_minus_log2log2n": log2(n) - log2(log2(n)),
            "bound_A": bound_a(n, 0.05),
            "log2log2n": log2(log2(n)),
        }
    json.dump(out, open("own_bounds2.json", "w"), indent=1)

    print("BOUND A (monotone closure), C_0 threshold")
    print(" n | eps=.01 | eps=.05 | eps=.5 | eps=.05 real m | eps=.05 first-satisfying")
    for n in LABELS + BIG:
        r = out["bound_A"][n]
        print(f"{n:8d} | {r['eps=0.01']} | {r['eps=0.05']} | {r['eps=0.5']} | "
              f"{r['eps=0.05_real_m']} | {r['eps=0.05_first_satisfying']}")
    print("\nBOUND B (monotone closure), C_0 threshold")
    print(" n | t.5 cond | t1 cond | t2 cond | t.5 yld | t1 yld | t2 yld | t1 cond real m | t1 first-sat")
    for n in LABELS + BIG:
        r = out["bound_B"][n]
        ks = ["tol=0.5_cond", "tol=1.0_cond", "tol=2.0_cond",
              "tol=0.5_yield", "tol=1.0_yield", "tol=2.0_yield", "tol=1.0_cond_real_m"]
        print(f"{n:8d} | " + " | ".join(str(r[k]) for k in ks)
              + f" | {out['bound_B_first_satisfying_not_closure'][n]}")
    print("\nTOTAL DEFICIT m*d(C_0) in bits, conditional reading, m = ceil(n/C_0)")
    print("  n  " + "".join(f"{c:>9d}" for c in range(1, 11)))
    for n in LABELS:
        row = out["total_deficit_table"][n]
        print(f"{n:5d}" + "".join(f"{row[c]:>9.3f}" for c in range(1, 11)))
    print("\nGROWTH ORDER")
    for n, v in out["asymptotic_check"].items():
        print(f"n={n:8d}  boundB={v['bound_B']}  log2n-log2log2n={v['log2n_minus_log2log2n']:.2f}"
              f"   boundA={v['bound_A']}  log2log2n={v['log2log2n']:.2f}")


if __name__ == "__main__":
    main()

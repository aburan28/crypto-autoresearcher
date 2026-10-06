#!/usr/bin/env python3
"""TASK-20260928-3f90b8 -- PROVES-TOO-MUCH control for EXP-SEMBIN-04ec3c.

Runs the contract's accounting UNCHANGED -- relations |F|, trials 1/p, oracle
cost, linear algebra |F|^2, store budget, sum-of-phases combination -- on two
objects where index calculus is KNOWN to beat square-root search, substituting
only the object's decomposition probability, as review_plan.proves_too_much
directs. Oracle cost is evaluated both ways:

  * the contract's own oracle models (ENUM, MITM, MITM_CAPPED -- generic m-SUM,
    i.e. HEUR-GENERIC-MSUM transplanted unchanged), and
  * the object's REAL decomposition oracle (factoring the target's
    representation), which in the contract's vocabulary is the FREE model plus
    a polynomial charge.

OBJECT A -- genus-g hyperelliptic Jacobian over F_q, q = 2^b, N ~ q^g, factor
base = a subset of the ~q weight-1 divisors, |F| = 2^d with d <= b. The full-
relation probability is a ~ q^(g(r-1))/g! with |F| = q^r (GTTD, ePrint 2004/153,
Sec. 4, retrieved), which IS the contract's p = |F|^m/(m! N) with m = g. So for
this object the committed driver's cost_at() is called DIRECTLY with n = g*b,
m = g, and the factor-base cap d <= b. Nothing is transcribed.

OBJECT B -- F_q^*, q prime of n bits, factor base = primes <= 2^beta,
|F| = pi(2^beta), smoothness probability rho(u), u = n/beta (Dickman rho,
computed numerically here). The accounting is a line-for-line transcription of
cost_at()'s combination, verified below to reproduce cost_at() exactly on the
contract's own inputs.

Usage: python3 ptm_known_false_objects.py [--out ptm_results.json]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
DRIVER = os.path.join(REPO, "experiments/EXP-SEMBIN-04ec3c/code/memory_charged_family.py")
DRIVER_SHA256 = "75cd2252948e09e38149ec6d13c339e54e0a100fe3ecb235ed90ab59ec0fe998"
HERE = os.path.dirname(os.path.abspath(__file__))
BUDGETS = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]


def load_driver():
    blob = open(DRIVER, "rb").read()
    if hashlib.sha256(blob).hexdigest() != DRIVER_SHA256:
        raise SystemExit("driver hash mismatch; refusing")
    spec = importlib.util.spec_from_file_location("mcf_committed", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mcf_committed"] = mod
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# the contract's accounting, transcribed from cost_at() (verified below)
# --------------------------------------------------------------------------
def accounting(d: float, log2_inv_p: float, oracle_t: float) -> tuple[float, float, float]:
    relation = d + log2_inv_p + oracle_t
    linalg = 2.0 * d
    if relation - linalg > 60:
        total = relation
    elif linalg - relation > 60:
        total = linalg
    else:
        total = max(relation, linalg) + math.log2(1.0 + 2.0 ** -abs(relation - linalg))
    return relation, linalg, total


def verify_transcription(mod) -> float:
    worst = 0.0
    for n in (97, 131, 163):
        nn = mod.subgroup_log2(n)
        for m in range(2, 17):
            for d in (5.0, 12.5, 30.0):
                for model, b in (("FREE", None), ("ENUM", None), ("MITM", None),
                                 ("MITM_CAPPED", 50.0)):
                    c = mod.cost_at(n, m, model, d, b)
                    t, _, _ = mod.oracle_log2(model, m, d, b)
                    inv_p = mod.log2_factorial(m) + nn - m * d
                    _, _, tot = accounting(d, inv_p, t)
                    worst = max(worst, abs(round(tot, 4) - c.log2_total))
    return worst


# --------------------------------------------------------------------------
# Dickman rho
# --------------------------------------------------------------------------
class Dickman:
    """Dickman rho from the AVERAGING form u*rho(u) = integral_{u-1}^{u} rho(t) dt.

    Two schemes were tried first and rejected, recorded because the failure is
    instructive: (1) forward trapezoid on rho' = -rho(u-1)/u carries ABSOLUTE
    error ~1e-8 from the kink at u = 1 and goes negative by u ~ 8; (2) the same
    delay equation in log space, L' = -exp(L(u-1) - L(u))/u, is forward-
    UNSTABLE (errors grow like exp(xi u)) and gave rho(10) ~ 1e-8 instead of
    ~2.8e-11. The averaging form writes rho(u) as a positive weighted mean of
    earlier values, so only relative error propagates. The window sum is
    recomputed exactly (math.fsum) every `resync` steps to stop running-sum
    drift.
    """

    def __init__(self, umax: float = 100.0, h: float = 1e-3, resync: int = 50):
        self.h = h
        k = int(round(1.0 / h))
        n = int(umax / h) + 2
        r = [1.0] * n
        S = math.fsum(r[1:k])  # sum_{j=i-k+1}^{i-1} r_j for i = k
        for i in range(k, n):
            if i > k:
                S += r[i - 1] - r[i - k]
                if (i - k) % resync == 0:
                    S = math.fsum(r[i - k + 1:i])
            u = i * h
            if i == k:
                r[i] = 1.0
                continue
            r[i] = h * (0.5 * r[i - k] + S) / (u - 0.5 * h)
        self.L = [math.log(x) for x in r]
        self.umax = umax

    def rho(self, u: float) -> float:
        return math.exp(self._L(u))

    def _L(self, u: float) -> float:
        if u <= 1.0:
            return 0.0
        if u >= self.umax - 1e-6:
            raise ValueError(f"u = {u} beyond table")
        x = u / self.h
        i = int(x)
        return self.L[i] + (self.L[i + 1] - self.L[i]) * (x - i)

    def log2(self, u: float) -> float:
        return self._L(u) / math.log(2.0)


def pi_approx(x: float) -> float:
    lx = math.log(x)
    return x / lx * (1.0 + 1.0 / lx + 2.0 / lx ** 2)


# --------------------------------------------------------------------------
# OBJECT A: hyperelliptic Jacobian, driver called directly
# --------------------------------------------------------------------------
def jacobian(mod, g: int, b: int) -> dict:
    n = g * b
    assert n != 131, "driver special-cases n = 131"
    out = {"g": g, "field_bits_b": b, "group_bits_n": n,
           "log2_rho_vow": round(n / 2 + math.log2(0.886), 4),
           "p_formula": "|F|^g/(g! q^g): the contract's p with m = g (GTTD Sec. 4 'a')"}
    real = mod.minimise_over_d(n, g, "FREE", None, d_lo=1.0, d_hi=float(b))
    poly = math.log2(g * g * b * b)  # factoring a degree-g u(x) over F_q, generous
    rp, lp, tp = accounting(real.d, mod.log2_factorial(g) + n - g * real.d, poly)
    out["REAL_ORACLE_factor_u"] = {
        "d": real.d, "log2_total_oracle_free": real.log2_total,
        "log2_total_with_poly_charge": round(tp, 4),
        "log2_store_entries": real.log2_store_entries,
        "beats_rho": tp < out["log2_rho_vow"],
        "margin_bits": round(tp - out["log2_rho_vow"], 4),
        "store_below_n_over_2": real.log2_store_entries < n / 2,
    }
    gen = {}
    for model in ("ENUM", "MITM"):
        c = mod.minimise_over_d(n, g, model, None, d_lo=1.0, d_hi=float(b))
        gen[model] = {"d": c.d, "log2_total": c.log2_total,
                      "log2_store_entries": c.log2_store_entries,
                      "beats_rho": c.beats_vow}
    capped = []
    for B in BUDGETS:
        c = mod.minimise_over_d(n, g, "MITM_CAPPED", B, d_lo=1.0, d_hi=float(b))
        capped.append(c.beats_vow and not c.degenerate)
    gen["MITM_CAPPED_any_budget_beats_rho"] = any(capped)
    out["CONTRACT_GENERIC_ORACLES"] = gen
    return out


def harley_slope(mod, g: int, b1: int = 40, b2: int = 80) -> dict:
    t1 = mod.minimise_over_d(g * b1, g, "FREE", None, 1.0, float(b1), step=0.05).log2_total
    t2 = mod.minimise_over_d(g * b2, g, "FREE", None, 1.0, float(b2), step=0.05).log2_total
    slope = (t2 - t1) / (b2 - b1)
    return {"g": g, "measured_exponent_in_q": round(slope, 4),
            "GTTD_Harley_exponent_2_minus_2_over_g_plus_1": round(2 - 2 / (g + 1), 4)}


# --------------------------------------------------------------------------
# OBJECT B: F_q^*, same accounting, smoothness probability substituted
# --------------------------------------------------------------------------
def fq_star(dk: Dickman, n: int) -> dict:
    rho_vow = n / 2 + math.log2(0.886)
    best = {}
    for name in ("REAL_ORACLE_smoothness_test", "TRIAL_DIVISION", "GENERIC_MITM_m_eq_ceil_u"):
        bestc = None
        beta = 4.0
        while beta <= min(n, 200):
            F = pi_approx(2.0 ** beta)
            d = math.log2(F)
            u = n / beta
            if u > 95.0:
                beta += 0.25
                continue
            inv_p = -dk.log2(u)
            m = max(2, math.ceil(u))
            if name == "REAL_ORACLE_smoothness_test":
                t, store = math.log2(n * n), d + math.log2(max(u, 1.0))
            elif name == "TRIAL_DIVISION":
                t, store = d, d + math.log2(max(u, 1.0))
            else:
                t, store = math.ceil(m / 2) * d, (m // 2) * d
            rel, la, tot = accounting(d, inv_p, t)
            cell = {"beta": beta, "d": round(d, 3), "u": round(u, 3), "m": m,
                    "log2_inv_p": round(inv_p, 3), "log2_total": round(tot, 3),
                    "log2_store_entries": round(store, 3)}
            if bestc is None or tot < bestc["log2_total"]:
                bestc = cell
            beta += 0.25
        bestc["beats_rho"] = bestc["log2_total"] < rho_vow
        bestc["margin_bits"] = round(bestc["log2_total"] - rho_vow, 3)
        best[name] = bestc
    L = math.exp(math.sqrt(2.0) * math.sqrt(n * math.log(2) * math.log(n * math.log(2))))
    return {"n": n, "log2_rho_vow": round(rho_vow, 4),
            "L_q_half_sqrt2_log2_reference": round(math.log2(L), 2),
            "L_reference_provenance": "recalled (textbook L_q[1/2, sqrt 2]); shown only for scale",
            **best}


def term_table(mod) -> dict:
    """One Jacobian cell and one binary-curve cell side by side, term by term."""
    g, b = 8, 20
    n = g * b
    d = 17.5
    rows = {}
    for label, nn, m in (("jacobian_g8_q2^20", float(n), g),
                         ("binary_curve_n160_m8", float(n), 8)):
        inv_p = mod.log2_factorial(m) + nn - m * d
        rows[label] = {
            "relations_log2": d, "trials_per_relation_log2(=log2 1/p)": round(inv_p, 4),
            "linear_algebra_log2": 2 * d,
            "oracle_real_log2": (round(math.log2(g * g * b * b), 3) if label.startswith("jac")
                                 else "not known to be sub-generic (Semaev + Groebner, "
                                      "excluded by the contract)"),
            "oracle_contract_MITM_log2": math.ceil(m / 2) * d,
            "total_with_contract_MITM": round(accounting(d, inv_p, math.ceil(m / 2) * d)[2], 3),
            "total_with_real_oracle": (round(accounting(d, inv_p, math.log2(g * g * b * b))[2], 3)
                                       if label.startswith("jac") else None),
            "log2_rho_vow": round(nn / 2 + math.log2(0.886), 3),
        }
    return {"d": d, "rows": rows,
            "reading": "relations, trials and linear algebra are IDENTICAL for the two "
                       "objects; the only term that differs is the oracle, which the "
                       "contract fixes by assumption (HEUR-GENERIC-MSUM)"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "ptm_results.json"))
    args = ap.parse_args()
    mod = load_driver()
    dk = Dickman()
    out = {"task_id": "TASK-20260928-3f90b8", "control": "proves_too_much",
           "driver_sha256": DRIVER_SHA256,
           "transcription_max_abs_error_vs_cost_at_bits": verify_transcription(mod),
           "dickman_check": {
               "rho(2)": dk.rho(2.0), "exact_1_minus_ln2": 1 - math.log(2),
               "rho(3)": dk.rho(3.0), "rho(5)": dk.rho(5.0), "rho(10)": dk.rho(10.0),
               "rho(20)": dk.rho(20.0),
               "reference_values_recalled": {"rho(3)": 0.0486083883, "rho(5)": 3.5472470e-4,
                                             "rho(10)": 2.7701772e-11},
               "note": "rho(2) = 1 - ln 2 is exact; the others are recalled "
                       "reference values, shown for comparison only"},
           "jacobian": [], "harley_exponent_check": [], "fq_star": []}
    for ntarget in (160, 256):
        for g in (2, 3, 4, 5, 6, 8, 10):
            b = round(ntarget / g)
            if g * b == 131:
                b += 1
            out["jacobian"].append(jacobian(mod, g, b))
    for g in (3, 4, 5, 8):
        out["harley_exponent_check"].append(harley_slope(mod, g))
    for n in (131, 256, 512, 1024):
        out["fq_star"].append(fq_star(dk, n))
    out["term_by_term"] = term_table(mod)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("transcription error", out["transcription_max_abs_error_vs_cost_at_bits"])
    print("dickman", out["dickman_check"])
    for j in out["jacobian"]:
        r, gcell = j["REAL_ORACLE_factor_u"], j["CONTRACT_GENERIC_ORACLES"]
        print(f"JAC g={j['g']:2d} b={j['field_bits_b']:3d} n={j['group_bits_n']:3d} rho={j['log2_rho_vow']:7.2f} | "
              f"real: {r['log2_total_with_poly_charge']:7.2f} beats={r['beats_rho']!s:5s} store={r['log2_store_entries']:6.2f} | "
              f"ENUM {gcell['ENUM']['log2_total']:7.2f} MITM {gcell['MITM']['log2_total']:7.2f} "
              f"beats={gcell['MITM']['beats_rho']} capped_any={gcell['MITM_CAPPED_any_budget_beats_rho']}")
    for h in out["harley_exponent_check"]:
        print("HARLEY", h)
    for f in out["fq_star"]:
        print(f"FQ* n={f['n']:5d} rho={f['log2_rho_vow']:7.2f} L={f['L_q_half_sqrt2_log2_reference']:6.2f} | "
              + " | ".join(f"{k}: {f[k]['log2_total']} (beats={f[k]['beats_rho']}, beta={f[k]['beta']}, store={f[k]['log2_store_entries']})"
                           for k in ("REAL_ORACLE_smoothness_test", "TRIAL_DIVISION", "GENERIC_MITM_m_eq_ceil_u")))
    print(json.dumps(out["term_by_term"], indent=1))


if __name__ == "__main__":
    main()

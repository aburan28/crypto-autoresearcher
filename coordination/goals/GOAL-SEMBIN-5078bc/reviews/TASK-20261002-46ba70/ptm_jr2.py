#!/usr/bin/env python3
"""TASK-20261002-46ba70 -- PROVES-TOO-MUCH control for REVIEW-SEMBIN-20261002-c7e1d4 (red team).

REVIEWER COMPUTATION. Closed forms only; zero scientific runs; no curve instantiated; no
statement about any curve's security.

Arguments under test (both from TASK-20261001-9b3e70, drafts, unreviewed):
  (A) HEUR-HARVEST-FV-2's random-model justification (ii), the counting sketch
          relations <~ T |F| / l + T^2 / l,
      i.e. each unit-cost membership test on a non-formal element succeeds with
      probability ~|F|/l (clause 1(b) at m = 1), plus collision relations; and the
      numeric line T >= (1/8) K sqrt(l / min(M, K)).
  (B) The COR-GEN interface G1-G4 (DERIVATION.md sec. 3.2).

Objects where index calculus is KNOWN to beat square-root search (reused, hash-checked,
from TASK-20261001-b2c916 ptm_v2.py / ptm_v2_results.json and the previous round's
Dickman rho and pi(x)):
  F_q^*, q a safe prime of n in {131, 256} bits: F = primes < B = 2^beta; membership of a
      lifted integer in the multiplicative closure of F by trial division or batch
      smoothness (the real oracle).
  Genus g in {5, 6, 8} hyperelliptic Jacobian over F_2^b at n = g b ~ 160: F = degree-1
      divisors; membership in the g-fold sum set by factoring the Mumford u-polynomial.

FAILURE SIGNATURE (card): if (A) or (B), transplanted, bounds the real-oracle relation rate
below what the known index calculus achieves, the argument proves too much. With the
objects' GENERIC oracles, Omega(sqrt l) must still come out.

Reproduce (from the repository root):
    python3 coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-46ba70/ptm_jr2.py
Writes ptm_out/ptm_jr2_results.json beside this script. Standard library only.
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # RT-20261002-bdda1a D3

import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
B2C = os.path.join(REPO, "coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261001-b2c916")
PTM_V2 = os.path.join(B2C, "ptm_v2.py")
PTM_V2_SHA = "c38c7f490f77aebcfdc795e612b7378e8e061e14857c56439b5f3531d146dc9f"
PTM_V2_RES = os.path.join(B2C, "ptm_out", "ptm_v2_results.json")
PTM_V2_RES_SHA = "be9a46dc0c318024915813dc44d1488c118216f541b171e3bd50e2e75257eeb7"
PREV = os.path.join(REPO, "coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20260928-3f90b8/ptm_known_false_objects.py")
PREV_SHA = "68852843d12e73bb7b9a14d9c3c85b3dbacb80d97e3188da8ad171988f37e0c3"
LOG2_0886 = math.log2(0.886)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(path, name, want):
    if sha(path) != want:
        raise SystemExit(f"{path}: sha256 mismatch; refusing")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def lsum(*xs):
    top = max(xs)
    return top + math.log2(math.fsum(2.0 ** (x - top) for x in xs))


def solve_quadratic_T(lF, N, lK, lp1=None):
    """Smallest T with T p1 + T^2 / l >= K (p1 = |F|/l unless given). Returns log2 T."""
    p1 = (lF - N) if lp1 is None else lp1
    # T^2/l + p1 T - K = 0  ->  T = (-p1 + sqrt(p1^2 + 4K/l)) / (2/l)
    a = 2.0 * p1
    b = 2.0 + lK - N
    if a > b + 60:          # linear term dominates: T ~ K / p1
        return lK - p1
    if b > a + 60:          # quadratic term dominates: T ~ sqrt(K l)
        return 0.5 * (lK + N)
    disc = lsum(a, b) / 2.0  # log2 sqrt(p1^2 + 4K/l)
    num = disc + math.log2(1.0 - 2.0 ** (p1 - disc))
    return num - (1.0 - N)


def hhan_lb(N, m_inst, negation_free_harvester):
    """Hhan 2024 Thm 3.4 (+ Thm C.1), expected-time lower bound, log2; see jr2_harvest_envelope.py."""
    lX = N / 2.0 + 0.5 * math.log2(2.0 * m_inst / math.e) - 1.0 / (2.0 * m_inst)
    X = 2.0 ** lX
    if negation_free_harvester:
        E = X * (2.0 * m_inst / (2.0 * m_inst + 1.0)) - (2.0 * m_inst + 1.0)
    else:  # free negation, converted conservatively (x2 gates, inputs negated)
        E = (X / 2.0) * (2.0 * m_inst / (2.0 * m_inst + 1.0)) - (2.0 * m_inst + 1.0 + 2.0 * m_inst * N) / 2.0
    return math.log2(E)


def transplant(obj, N, d, tpr, o, fill, total_stored, v2_cell, real_oracle, excluding_step, interface,
               negation_closed_F):
    V = LOG2_0886 + N / 2.0
    cell = v2_cell(d, tpr, o, fill)
    lK = d                                            # v2 convention K = |F| = 2^d
    lp_real = -tpr                                    # per-test success of the real oracle
    lp_arity1 = d - N                                 # clause 2's per-test pricing |F|/l
    T_c2 = solve_quadratic_T(d, N, lK)                # (A) counting, real oracle ADMITTED at arity-1 price
    line = -3.0 + lK + (N - min(max(fill, d), lK)) / 2.0  # (1/8) K sqrt(l / min(M, K)), M = max(table, |F|)
    T_correct = solve_quadratic_T(d, N, lK, lp1=lp_real)  # same counting with the oracle's TRUE success prob
    m_inst = (2.0 ** (d - 1.0) + 1.0) if negation_closed_F else (2.0 ** d + 1.0)
    lb_generic = hhan_lb(N, m_inst, negation_free_harvester=not negation_closed_F)
    lb_generic_total = lsum(lb_generic, 2.0 * d)
    return {
        "object": obj, "N": N, "VOW": round(V, 4), "real_oracle": real_oracle,
        "argmin_params": {"d": d, "TPR": round(tpr, 4), "o": round(o, 4), "FILL": round(fill, 4)},
        "real_IC_TOTAL_recomputed": round(cell["TOTAL"], 4), "real_IC_TOTAL_stored": total_stored,
        "recompute_abs_diff": round(abs(cell["TOTAL"] - total_stored), 6),
        "real_IC_margin_vs_VOW": round(cell["TOTAL"] - V, 4),
        "per_test_success_log2_real": round(lp_real, 4),
        "per_test_success_log2_arity1_clause2": round(lp_arity1, 4),
        "m_fold_advantage_bits": round(lp_real - lp_arity1, 4),
        "A_counting_bound_T_log2_if_real_oracle_admitted_at_arity1_price": round(T_c2, 4),
        "A_line_one_eighth_K_sqrt_l_over_minMK_log2": round(line, 4),
        "SIGNATURE_if_admitted": {
            "counting_bound_exceeds_real_IC_by_bits": round(T_c2 - cell["TOTAL"], 4),
            "line_exceeds_real_IC_by_bits": round(line - cell["TOTAL"], 4),
            "fires": bool(cell["TOTAL"] < T_c2 or cell["TOTAL"] < line)},
        "A_counting_with_true_success_probability_T_log2": round(T_correct, 4),
        "A_counting_true_price_consistent_with_real_IC": bool(T_correct <= cell["TOTAL"] + 1e-9),
        "SIGNATURE_as_scoped": {
            "real_oracle_inside_A_FV_analogue": False,
            "fires": False,
            "why": "clause 2 grants unit cost only to an arity-1 membership test; the real oracle decides "
                   "m-fold product/sum-set membership, so (A) is silent on it"},
        "excluding_step": excluding_step,
        "B_interface_G1_to_G4": interface,
        "generic_oracle_check": {
            "instances_m": m_inst, "negation_closed_F": negation_closed_F,
            "hhan_lb_harvest_log2": round(lb_generic, 4), "hhan_lb_TOTAL_with_LA_log2": round(lb_generic_total, 4),
            "margin_vs_VOW": round(lb_generic_total - V, 4),
            "omega_sqrt_l_comes_out": bool(lb_generic_total > V)},
    }


def main():
    ptm = load(PTM_V2, "ptm_v2_reused", PTM_V2_SHA)
    prev = load(PREV, "ptm_prev_round_reused", PREV_SHA)
    if sha(PTM_V2_RES) != PTM_V2_RES_SHA:
        raise SystemExit("ptm_v2_results.json sha256 mismatch; refusing")
    res = json.load(open(PTM_V2_RES))
    dk = prev.Dickman()
    out = {"task_id": "TASK-20261002-46ba70", "control": "proves_too_much (REVIEW-SEMBIN-20261002-c7e1d4)",
           "label": "REVIEWER COMPUTATION (closed forms; zero runs)",
           "reused": {"ptm_v2.py": PTM_V2_SHA, "ptm_v2_results.json": PTM_V2_RES_SHA,
                      "ptm_known_false_objects.py": PREV_SHA},
           "objects": []}

    fq_interface = {
        "G1_generic_ops_only": "VIOLATED: reads the integer representative of the element (lifting)",
        "G2_membership_by_list_lookup_only": "VIOLATED: membership decided by factoring the lift (trial division / batch smoothness)",
        "G3_guarantee_survives_random_list": "VIOLATED: success requires F = the primes below B; on a random list the smoothness test is meaningless",
        "G4_targets_built_from_P_Q": "holds (g^a h^b)"}
    jac_interface = {
        "G1_generic_ops_only": "VIOLATED: reads the Mumford coordinates (u, v) of the reduced divisor",
        "G2_membership_by_list_lookup_only": "VIOLATED: membership in the g-fold sum set decided by factoring u over F_q",
        "G3_guarantee_survives_random_list": "VIOLATED: success requires F = the degree-1 prime divisors",
        "G4_targets_built_from_P_Q": "holds"}

    for f in res["fq_star"]:
        n = f["n"]
        if n not in (131, 256):
            continue
        N = float(n - 1)
        for key, lab in (("REAL_trial_division__sieve_charged", "trial division (sieve charged)"),
                         ("REAL_batch_smoothness__product_tree_charged", "batch smoothness (product tree charged)")):
            a = f[key]["argmin"]
            beta, u, d = a["beta"], n / a["beta"], a["d"]
            assert abs(d - math.log2(prev.pi_approx(2.0 ** beta))) < 1e-3
            tpr = -dk.log2(u)
            if key.startswith("REAL_trial"):
                o, fill = d, beta
            else:
                o, fill = math.log2(n * n), d + math.log2(d)
            out["objects"].append(transplant(
                f"F_q^*, safe prime q of {n} bits; F = primes < 2^{beta}", N, d, tpr, o, fill, f[key]["min_TOTAL"],
                ptm.v2_cell, f"B-smoothness of the lifted integer by {lab}; u = {u:.3f}, Dickman rho(u) per test",
                {"capability": "unit/poly-cost membership in the m-fold PRODUCT set of F (all arities up to ~u), "
                               "i.e. B-smoothness",
                 "implementation": "norm factoring (the lift is the norm from Z; factored by trial division or batch "
                                   "remainder trees)",
                 "binary_curve_analogue": "deciding R in F_V^(m) = Weil-descended summation-polynomial solving, which "
                                          "A_FV excludes and HEUR-HARVEST-FV is silent on (OPEN-B)"},
                fq_interface, negation_closed_F=False))

    for j in res["jacobian"]:
        g, b = j["g"], j["b"]
        if not (g >= 5 and j["N"] <= 170):
            continue
        N = float(g * b)
        a = j["REAL_factor_u__FB_table_charged"]["argmin"]
        d = a["d"]
        tpr = N + math.log2(math.factorial(g)) - g * d
        o = math.log2(g * g * b * b)
        out["objects"].append(transplant(
            f"genus-{g} hyperelliptic Jacobian over F_2^{b}; F = degree-1 divisors (2^{d} of them)", N, d, tpr, o, d,
            j["REAL_factor_u__FB_table_charged"]["min_TOTAL"], ptm.v2_cell,
            f"factor the Mumford u-polynomial (degree {g}) over F_q; per-test success |F|^g/(g! q^g)",
            {"capability": f"poly-cost membership in the {g}-fold SUM set of F (u splits into linear factors)",
             "implementation": "norm factoring in F_q[x] (u is the norm of the divisor)",
             "binary_curve_analogue": "deciding R in F_V^(m) on E(F_2^n), which needs summation polynomials; outside A_FV"},
            jac_interface, negation_closed_F=True))

    out["verdict"] = {
        "signature_fires_as_scoped": any(o["SIGNATURE_as_scoped"]["fires"] for o in out["objects"]),
        "signature_fires_if_real_oracles_admitted_at_arity1_price": all(o["SIGNATURE_if_admitted"]["fires"] for o in out["objects"]),
        "true_price_counting_consistent_on_every_object": all(o["A_counting_true_price_consistent_with_real_IC"] for o in out["objects"]),
        "generic_oracles_give_omega_sqrt_l_on_every_object": all(o["generic_oracle_check"]["omega_sqrt_l_comes_out"] for o in out["objects"]),
        "max_recompute_abs_diff": max(o["recompute_abs_diff"] for o in out["objects"])}
    os.makedirs(os.path.join(HERE, "ptm_out"), exist_ok=True)
    with open(os.path.join(HERE, "ptm_out", "ptm_jr2_results.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1) + "\n")
    for o in out["objects"]:
        s = o["SIGNATURE_if_admitted"]
        print(f"{o['object'][:58]:58s} N={o['N']:.0f} realIC={o['real_IC_TOTAL_recomputed']:.2f} "
              f"(VOW{o['real_IC_margin_vs_VOW']:+.2f}) adv={o['m_fold_advantage_bits']:.1f}b "
              f"| admitted: count {o['A_counting_bound_T_log2_if_real_oracle_admitted_at_arity1_price']:.2f} "
              f"line {o['A_line_one_eighth_K_sqrt_l_over_minMK_log2']:.2f} -> fires={s['fires']} "
              f"(+{s['counting_bound_exceeds_real_IC_by_bits']:.1f}b) | true-price T {o['A_counting_with_true_success_probability_T_log2']:.2f} "
              f"ok={o['A_counting_true_price_consistent_with_real_IC']} | generic LB margin {o['generic_oracle_check']['margin_vs_VOW']:+.2f}")
    print(json.dumps(out["verdict"], indent=1))


if __name__ == "__main__":
    main()

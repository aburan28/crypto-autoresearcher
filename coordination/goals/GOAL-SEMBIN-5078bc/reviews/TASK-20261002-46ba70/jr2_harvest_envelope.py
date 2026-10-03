#!/usr/bin/env python3
"""TASK-20261002-46ba70 -- joint JR-2 of REVIEW-SEMBIN-20261002-c7e1d4 (red team).

REVIEWER COMPUTATION. Closed-form log2 arithmetic only. Zero scientific runs, nothing
instantiated on any curve, no N_2 or decomposition-count measurement of any F_V. No
statement about the security of any curve in either direction. Degrees are labels.

Question (card objective): does ANY generic harvesting configuration have a fill-charged
total for K = |F| relations (linear algebra included) below VOW = log2(0.886) + N/2 at
any of the ten degrees?

Configuration families (log2; unit = one group operation / table write / probe, the v2
unit; memory reported, not charged):
  C1   X-6 as written (AMD-20261001-e61f2b C-7): 2 + d + (N - w)/2, w <= d, + LA.
  C2   PCS multi-collision search, constants re-derived from vOW sec. 4.2 at source
       (inputs/VOW-1996-PCS/paper_fulltext.md lines 408-417), w <= K.
  C3   Full-memory birthday harvesting, ideal (no DP or locating overhead):
       E[time to the K-th coincidence] = sqrt(2 n) Gamma(K + 1/2) / Gamma(K).
  C5   Per-target vOW golden-collision decomposition search (sec. 5.3), sparse and
       dense, coupon-corrected, m in {4, 6, 8, 10}, s in 1..S, w, n_h up to l.
  C6   Shared target-independent table (fill charged per DISTINCT entry) plus a
       per-target walk with distinguished-point memory.
  LB   Theorem-backed lower envelope: Hhan 2024 Thm 3.4 (explicit form, read at source)
       transferred to faithful random-representation algorithms by its Thm C.1.

Two conventions, both reported:
  PROG  the program's: no negation map in the harvester (space l), K = 2^d relations,
        LA = 2d, decomposition relations only.
  FAV   most favourable to the harvester: negation map (space l/2), K = 2^(d-1) + 1
        (rank over the +-classes of a negation-closed F, plus x), LA = 2 log2 K,
        homogeneous (factor-base-only) coincidences counted as relations.
The VOW column itself includes a negation map (KN-LIT-73f7e1 item 1), so PROG compares
a negation-free harvester with a negation-equipped rho, as X-6 does.

Reproduce (from the repository root):
    python3 coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-46ba70/jr2_harvest_envelope.py
Writes jr2_out/jr2_results.json beside this script. Standard library only. Deterministic.
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # RT-20261002-bdda1a D3: never write __pycache__ anywhere

import hashlib
import json
import math
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
RAW = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c", "runs", "RUN-SEMBIN-be48b7", "raw-result.json")
DIG = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c", "runs", "RUN-SEMBIN-be48b7", "artifact-digests.json")

LN2 = math.log(2.0)
LOG2_0886 = math.log2(0.886)
DEGREES = (97, 109, 131, 163, 191, 233, 239, 283, 409, 571)
M_VALUES = (4, 6, 8, 10)

# ---------------------------------------------------------------------------------------
# vOW sec. 4.2 constants, re-derived from the source text (lines 408-417):
#   "if 10w distinguished points are generated for each version of the function,
#    theta = 2.25 sqrt(w/n), and w >= 2^10 ... T = 2.5 sqrt(n^3/w)" (eq. 4);
#   "for 2^10 <= w <= n/2^10, each function generates about 1.3w collisions, of which
#    about 1.1w are distinct; 80% of the function iterations are devoted to generating
#    distinguished points and 20% are devoted to locating collisions; the expected number
#    of versions of the function required is 0.45 n/w".
# Generation per version = 10w * (1/theta) = (10/2.25) sqrt(n w).
# ---------------------------------------------------------------------------------------
GEN_PER_VERSION = 10.0 / 2.25                    # x sqrt(n w)
TOTAL_PER_VERSION = GEN_PER_VERSION / 0.8        # x sqrt(n w), locating included
C_LOC = TOTAL_PER_VERSION / 1.1                  # per DISTINCT collision, locating included
C_GEN = GEN_PER_VERSION / 1.1                    # per DISTINCT collision, generation only
EQ4_CHECK = 0.45 * TOTAL_PER_VERSION             # must reproduce eq. (4)'s 2.5
EQ8_CONST = 2.5 * math.sqrt(8.0)                 # eq. (8): |J| 2.5 sqrt((2 n1)^3 / w) = 7.07 n2 sqrt(n1/w)


def lsum(*xs):
    xs = [x for x in xs if x is not None and x > -math.inf]
    top = max(xs)
    return top + math.log2(math.fsum(2.0 ** (x - top) for x in xs))


def log2_one_minus_exp_neg(lx):
    """log2(1 - exp(-x)) given lx = log2 x."""
    if lx > 8.0:
        return 0.0
    if lx < -40.0:
        return lx + math.log2(1.0 - 2.0 ** lx * LN2 / 2.0) if lx > -1000 else lx
    x = 2.0 ** lx
    return math.log2(-math.expm1(-x))


def log2_gamma_ratio(K):
    """log2(Gamma(K + 1/2) / Gamma(K)), K >= 1 real."""
    if K < 1e7:
        return (math.lgamma(K + 0.5) - math.lgamma(K)) / LN2
    return 0.5 * math.log2(K) + math.log2(1.0 - 1.0 / (8.0 * K) + 1.0 / (128.0 * K * K))


def log2_binom_multiset(d, S):
    """log2 C(2^d + S - 1, S): number of S-multisets of an |F| = 2^d list."""
    F = 2.0 ** d
    return math.fsum(math.log2(F + i) for i in range(S)) - math.log2(math.factorial(S))


def log2_K(d, conv):
    return d if conv == "PROG" else math.log2(2.0 ** (d - 1.0) + 1.0)


def la_of(d, conv):
    return 2.0 * d if conv == "PROG" else 2.0 * log2_K(d, conv)


def grid(lo, hi, step):
    out, k = [], 0
    while True:
        x = lo + k * step
        if x > hi + 1e-9:
            return out
        out.append(round(x, 6))
        k += 1


def degree_N(n, log2_r):
    return float(log2_r) if n == 131 else float(n)


def vow(N):
    return LOG2_0886 + N / 2.0


# ---------------------------------------------------------------------------------------
# C1: X-6 as written.
# ---------------------------------------------------------------------------------------
def c1_x6(N, d, w):
    return lsum(2.0 + d + (N - w) / 2.0, 2.0 * d)


def c1_min(N, in_validity):
    V = vow(N)
    best = None
    dlo = 10.0 if in_validity else 0.0
    for d in grid(dlo, N / 2.0, 0.25):
        wlo = 10.0 if in_validity else 0.0
        if d < wlo:
            continue
        for w in grid(wlo, d, 0.25):
            t = c1_x6(N, d, w)
            if best is None or t < best[0]:
                best = (t, d, w)
    t, d, w = best
    return {"min_TOTAL": round(t, 4), "margin_vs_VOW": round(t - V, 4), "d": d, "w_log2": w,
            "in_vow_validity": in_validity,
            "note": None if in_validity else "w < 2^10 leaves vOW's measured range (Table 1; lines 408-417)"}


# ---------------------------------------------------------------------------------------
# C2: PCS multi-collision search, source constants, memory w <= K (multi-version regime).
# ---------------------------------------------------------------------------------------
def c2_cell(N, d, conv, c):
    neg = conv == "FAV"
    n_sp = N - (1.0 if neg else 0.0)
    lK = log2_K(d, conv)
    w = min(lK, n_sp - 10.0)          # time decreases in w; w <= K, w <= n/2^10
    if w < 10.0:
        return None
    T = lK + math.log2(c) + (n_sp - w) / 2.0
    return {"TOTAL": lsum(T, la_of(d, conv), d), "harvest": T, "w_log2": w, "K_log2": lK}


def c2_min(N, conv, c):
    V = vow(N)
    best = None
    for d in grid(1.0, N / 2.0, 0.25):
        cell = c2_cell(N, d, conv, c)
        if cell is None:
            continue
        if best is None or cell["TOTAL"] < best[1]["TOTAL"]:
            best = (d, cell)
    d, cell = best
    return {"min_TOTAL": round(cell["TOTAL"], 4), "margin_vs_VOW": round(cell["TOTAL"] - V, 4), "d": d,
            "w_log2": round(cell["w_log2"], 4), "K_log2": round(cell["K_log2"], 4), "c": round(c, 4)}


# ---------------------------------------------------------------------------------------
# C3: full-memory birthday harvesting, ideal.
# ---------------------------------------------------------------------------------------
def c3_cell(N, d, conv):
    neg = conv == "FAV"
    n_sp = N - (1.0 if neg else 0.0)
    lK = log2_K(d, conv)
    K = 2.0 ** lK
    T = 0.5 * (1.0 + n_sp) + log2_gamma_ratio(K)      # sqrt(2 n) Gamma(K+1/2)/Gamma(K)
    return {"TOTAL": lsum(T, la_of(d, conv), d), "harvest": T, "memory_log2": T, "K_log2": lK}


def c3_min(N, conv, dlo):
    V = vow(N)
    best = None
    for d in grid(dlo, N / 2.0, 0.25):
        cell = c3_cell(N, d, conv)
        if best is None or cell["TOTAL"] < best[1]["TOTAL"]:
            best = (d, cell)
    d, cell = best
    return {"min_TOTAL": round(cell["TOTAL"], 4), "margin_vs_VOW": round(cell["TOTAL"] - V, 4), "d": d,
            "K_log2": round(cell["K_log2"], 4), "memory_log2": round(cell["memory_log2"], 3)}


# ---------------------------------------------------------------------------------------
# C5: per-target vOW golden-collision decomposition search, coupon-corrected.
#
# Per target R = aP + bQ, half-domains D1 = S-multisets of F (or an n_h-subset), D2 =
# R - (m-S)-multisets, n1 = n2 = n_h, S = m/2. vOW sec. 5.3 builds f(x,i) = g(f_i'(x)) on
# |S| = 2 n_h points (capped at the effective group size l_e). Among the 2 n_h images:
#   cross real coincidences (decompositions, "golden")   k12  = n_h^2 / l_e
#   same-side real coincidences (homogeneous relations)  khom = n_h^2 / l_e  (FAV only)
# f has about |S|/2 collisions, so the useful fraction is q = k_useful / (|S|/2).
# Steady state (vOW 4.2): C_LOC sqrt(|S|/w) per distinct collision -> per useful one / q.
# Floor: g real coincidences among generated images need t >= sqrt(2 g l_e) points
# (sqrt(4 g l_e) for cross pairs only). T_target(g) = max(floor, steady * g) is a LOWER
# estimate of the vOW cost (optimistic for the hybrid at the version-filling transition).
# Coupon: a decomposition has mu = max(1, C(m,S) (n_h/n_full)^2) representatives among the
# cross pairs (70 at m = 8, S = 4, full domains). Draws are uniform over useful pairs (G2),
# so the expected distinct relations after g draws are
#   D(g) = P12 (1 - exp(-g pi12 / P12)) + Phom (1 - exp(-g pihom / Phom)).
# Targets n_T = max(1, K / D(g)). TOTAL = n_T T_target(g) + LA + |F|.
# Monotonicity used to collapse dimensions (checked in dichotomy table): at fixed (d, s)
# time falls as w rises (w = min(|S|/2^10, |F|^s)), and both the steady per-useful cost
# and the pool improve as n_h rises (n_h = min(n_full, l_e/2)).
# ---------------------------------------------------------------------------------------
def c5_setup(N, d, conv, m, s, nh_override=None):
    neg = conv == "FAV"
    Ne = N - (1.0 if neg else 0.0)
    S = m // 2
    CmS = math.comb(m, S)
    lK = log2_K(d, conv)
    n_full = log2_binom_multiset(d, S)
    nh = min(n_full, Ne - 1.0) if nh_override is None else min(nh_override, n_full)
    lS = min(nh + 1.0, Ne)
    w = lS - 10.0
    if s is not None:
        w = min(w, s * d)
    k12 = 2.0 * nh - Ne
    khom = 2.0 * nh - Ne
    ku = k12 + 1.0 if neg else k12
    lq = min(0.0, ku - (lS - 1.0))
    steady = math.log2(C_LOC) + (lS - w) / 2.0 - lq
    mu = max(0.0, math.log2(CmS) + 2.0 * (nh - n_full))
    P12 = k12 - mu
    Phom = khom if neg else None
    pi12 = k12 - ku
    pihom = khom - ku
    la = (1.0 if neg else 2.0) + Ne
    return {"Ne": Ne, "S": S, "CmS": CmS, "lK": lK, "n_full": n_full, "nh": nh, "lS": lS, "w": w,
            "k12": k12, "ku": ku, "lq": lq, "steady": steady, "mu": mu, "P12": P12, "Phom": Phom,
            "pi12": pi12, "pihom": pihom, "la": la, "valid": (w >= 10.0 and lS >= 20.0)}


def c5_eval(c, lg, no_floor=False):
    terms = [c["P12"] + log2_one_minus_exp_neg(lg + c["pi12"] - c["P12"])]
    if c["Phom"] is not None:
        terms.append(c["Phom"] + log2_one_minus_exp_neg(lg + c["pihom"] - c["Phom"]))
    lD = lsum(*terms)
    nT = max(0.0, c["lK"] - lD)
    floor = -math.inf if no_floor else 0.5 * (c["la"] + lg)
    stead = lg + c["steady"]
    return nT + max(floor, stead), lD, nT, floor >= stead


def c5_no_floor_mutation(N, conv, m):
    """MUTATION CONTROL: delete the birthday floor, i.e. apply vOW's steady-state per-collision
    rate to every harvest size (K times the per-relation figure, the DERIVATION sec. 2.4 form
    carried into a total). Expected to MANUFACTURE sub-VOW cells, which Hhan Thm 3.4 forbids
    for |F| >= 10: the floor is the guard. Single target, coupon ignored (pool >> K checked)."""
    V = vow(N)
    best, n_sub, n_cells = None, 0, 0
    for d in grid(max(1.0, math.log2(m)), N / 2.0, 0.25):
        c = c5_setup(N, d, conv, m, None)
        if not c["valid"]:
            continue
        Ptot = c["P12"] if c["Phom"] is None else lsum(c["P12"], c["Phom"])
        if Ptot < c["lK"] + 3.0:
            continue
        n_cells += 1
        T = lsum(c["lK"] + c["steady"], la_of(d, conv), d)
        if T < V:
            n_sub += 1
        if best is None or T < best[0]:
            best = (T, d, c)
    if best is None:
        return {"cells": 0}
    T, d, c = best
    one_version_yield = math.log2(1.1) + c["w"] + c["lq"]
    return {"min_TOTAL": round(T, 4), "margin_vs_VOW": round(T - V, 4), "d": d, "K_log2": round(c["lK"], 3),
            "per_relation_steady_log2": round(c["steady"], 3), "one_version_yield_log2": round(one_version_yield, 3),
            "K_below_one_version_yield": c["lK"] < one_version_yield, "cells": n_cells, "cells_below_VOW": n_sub}


def c5_opt(c):
    Ptot = c["P12"] if c["Phom"] is None else lsum(c["P12"], c["Phom"])
    lo = min(c["lK"], Ptot) - 60.0
    hi = max(c["lK"], Ptot) + 12.0
    best = None
    for lg in grid(lo, hi, 2.0):
        v = c5_eval(c, lg)[0]
        if best is None or v < best[0]:
            best = (v, lg)
    a, b = best[1] - 2.0, best[1] + 2.0
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    x1, x2 = b - gr * (b - a), a + gr * (b - a)
    f1, f2 = c5_eval(c, x1)[0], c5_eval(c, x2)[0]
    for _ in range(48):
        if f1 <= f2:
            b, x2, f2 = x2, x1, f1
            x1 = b - gr * (b - a)
            f1 = c5_eval(c, x1)[0]
        else:
            a, x1, f1 = x1, x2, f2
            x2 = a + gr * (b - a)
            f2 = c5_eval(c, x2)[0]
    lg = x1 if f1 <= f2 else x2
    if best[0] < min(f1, f2):
        lg = best[1]
    v, lD, nT, floor_binds = c5_eval(c, lg)
    return {"harvest": v, "lg": lg, "lD": lD, "targets_log2": nT, "floor_binds": floor_binds,
            "coupon_factor_log2": lg - lD if nT > 0.0 else None, "pool_log2": Ptot}


def c5_min(N, conv, m, s, dmax):
    V = vow(N)
    best, n_valid, n_invalid = None, 0, 0
    for d in grid(max(1.0, math.log2(m)), dmax, 0.25):
        c = c5_setup(N, d, conv, m, s)
        if not c["valid"]:
            n_invalid += 1
            continue
        n_valid += 1
        o = c5_opt(c)
        T = lsum(o["harvest"], la_of(d, conv), d)
        if best is None or T < best[0]:
            best = (T, d, c, o)
    if best is None:
        return {"cells_in_validity": 0, "cells_outside_validity": n_invalid}
    T, d, c, o = best
    return {"min_TOTAL": round(T, 4), "margin_vs_VOW": round(T - V, 4), "d": d,
            "n_h_log2": round(c["nh"], 3), "n_full_log2": round(c["n_full"], 3), "S_size_log2": round(c["lS"], 3),
            "w_log2": round(c["w"], 3), "s_effective": round(c["w"] / d, 3),
            "golden_pairs_per_target_log2": round(c["k12"], 3),
            "regime": "sparse (k <= 1)" if c["k12"] <= 0.0 else "dense (k > 1)",
            "useful_fraction_q_log2": round(c["lq"], 3), "multiplicity_mu_log2": round(c["mu"], 3),
            "pool_distinct_relations_log2": round(o["pool_log2"], 3), "draws_per_target_log2": round(o["lg"], 3),
            "relations_per_target_log2": round(o["lD"], 3), "targets_log2": round(o["targets_log2"], 3),
            "coupon_factor_log2": None if o["coupon_factor_log2"] is None else round(o["coupon_factor_log2"], 4),
            "binding": "birthday floor" if o["floor_binds"] else "vOW steady state",
            "harvest_log2": round(o["harvest"], 4), "K_log2": round(c["lK"], 4),
            "cells_in_validity": n_valid, "cells_outside_validity": n_invalid}


# ---------------------------------------------------------------------------------------
# C6: shared target-independent table (fill charged per distinct entry) + walk with DP memory.
# Relations per probe = M_t / l_e (table hits) + sqrt(w / l_e) / C_LOC (PCS rate, w >= 2^10);
# cost = M_t + probes; floor sqrt(2 K l_e) over all stored or generated elements.
# ---------------------------------------------------------------------------------------
ALPHAS = (0.0, 2.0 ** -30, 2.0 ** -20, 2.0 ** -10, 2.0 ** -5, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0)


def c6_min(N, conv):
    V = vow(N)
    neg = conv == "FAV"
    Ne = N - (1.0 if neg else 0.0)
    best = None
    alpha_star_over_d = set()
    for d in grid(1.0, N / 2.0, 0.5):
        lK = log2_K(d, conv)
        floor = 0.5 * (1.0 + lK + Ne)
        best_d = None
        for lM in grid(10.0, Ne - 10.0, 0.5):
            for a in ALPHAS:
                lMt = (lM + math.log2(a)) if a > 0 else None
                w = lM + math.log2(1.0 - a) if a < 1.0 else None
                rates = []
                if lMt is not None:
                    rates.append(lMt - Ne)
                if w is not None and w >= 10.0:
                    rates.append(0.5 * (w - Ne) - math.log2(C_LOC))
                if not rates:
                    continue
                probes = lK - lsum(*rates)
                harvest = lsum(lMt, probes) if lMt is not None else probes
                T = lsum(max(harvest, floor), la_of(d, conv), d)
                if best_d is None or T < best_d[0]:
                    best_d = (T, lM, a)
        alpha_star_over_d.add(best_d[2])
        if best is None or best_d[0] < best[0]:
            best = (best_d[0], d, best_d[1], best_d[2])
    T, d, lM, a = best
    return {"min_TOTAL": round(T, 4), "margin_vs_VOW": round(T - V, 4), "d": d, "memory_log2": lM,
            "table_fraction_alpha": a, "alpha_star_values_over_all_d": sorted(alpha_star_over_d)}


# ---------------------------------------------------------------------------------------
# LB: Hhan 2024 (arXiv 2402.11269v1), read at source this session:
#   Thm 3.4: Pr[m-MDL solved with <= T group-operation gates] <= (e (T+2m+1)^2 / (2m|G|))^m,
#   from "log eps + m log|G| <= log|C| <= m log(e(T+2m+1)^2/(2m))" (+1 bit kept: factor 2);
#   equality gates free; the event bounded is "m informative collisions" (rank m).
#   Thm C.1: a faithful random-representation (Shoup-style) algorithm is simulated by a
#   type-safe one with the same group-operation complexity and success probability.
# A harvester outputting full-rank relations over F (random list, G3) and Q solves m-MDL.
# Free negation (Shoup's model, the VOW column) converted CONSERVATIVELY: track -X beside X
# (<= 2 gates per operation) after negating the m inputs (<= 2 log2 l queries each).
# E[T] >= int_0^inf max(0, 1 - Pr[T <= t]) dt, closed form below.
# ---------------------------------------------------------------------------------------
def hhan_expected_lb_log2(N, m, mode):
    if mode == "conservative_neg_x2":
        lX = N / 2.0 + 0.5 * math.log2(2.0 * m / math.e) - 1.0 / (2.0 * m)
        A = 2.0 * m + 1.0 + 2.0 * m * N
        X = 2.0 ** lX
        E = (X / 2.0) * (2.0 * m / (2.0 * m + 1.0)) - A / 2.0
    elif mode == "refined_half_group":
        lX = (N - 1.0) / 2.0 + 0.5 * math.log2(2.0 * m / math.e) - 1.0 / (2.0 * m)
        X = 2.0 ** lX
        E = X * (2.0 * m / (2.0 * m + 1.0)) - (2.0 * m + 1.0)
    elif mode == "as_stated_no_negation":
        lX = N / 2.0 + 0.5 * math.log2(2.0 * m / math.e) - 1.0 / (2.0 * m)
        X = 2.0 ** lX
        E = X * (2.0 * m / (2.0 * m + 1.0)) - (2.0 * m + 1.0)
    else:
        raise ValueError(mode)
    return math.log2(E) if E > 0 else None


def lb_table(N):
    V = vow(N)
    out = {}
    for mode, conv in (("conservative_neg_x2", "FAV"), ("refined_half_group", "FAV"), ("as_stated_no_negation", "PROG")):
        rows, dstar = [], None
        prev_pos = False
        for d in grid(1.0, N / 2.0, 0.25):
            m_inst = (2.0 ** (d - 1.0) + 1.0) if conv == "FAV" else (2.0 ** d + 1.0)
            E = hhan_expected_lb_log2(N, m_inst, mode)
            if E is None:
                continue
            T = lsum(E, la_of(d, conv))
            mg = T - V
            if mg > 0.0 and not prev_pos:
                dstar = d
            prev_pos = mg > 0.0
            if d in (1.0, 2.0, 3.0, 3.25, 3.5, 4.0, 5.0, 10.0, 20.0):
                rows.append({"d": d, "instances_m": m_inst, "E_lb_log2": round(E, 4), "TOTAL_lb": round(T, 4),
                             "margin_lb_vs_VOW": round(mg, 4)})
        out[mode] = {"convention": conv, "d_star_first_positive_and_stays": dstar, "rows": rows}
    # single-DL references (Hhan Thm 3.3: eps <= (T+3)^2/(2|G|), read at source)
    single_no_neg = math.log2((2.0 / 3.0) * math.sqrt(2.0) * 2.0 ** (N / 2.0) - 3.0)
    single_neg_cons = math.log2((1.0 / 3.0) * math.sqrt(2.0) * 2.0 ** (N / 2.0) - 3.0 - 2.0 * N)
    out["single_DL_reference_Thm3_3"] = {
        "E_lb_no_negation_log2": round(single_no_neg, 4), "margin_no_negation": round(single_no_neg - V, 4),
        "E_lb_free_negation_conservative_log2": round(single_neg_cons, 4),
        "margin_free_negation_conservative": round(single_neg_cons - V, 4),
        "reading": "at K = 1 the theorem leaves a constant gap below VOW: the generic single-DL constant question"}
    return out


# ---------------------------------------------------------------------------------------
# Dichotomy check (DERIVATION.md sec. 2.4) at one degree, m = 8, S = 4.
# ---------------------------------------------------------------------------------------
def dichotomy_table(N, m=8):
    S = m // 2
    rows = []
    sqrt_l, sqrt_2l = N / 2.0, (N + 1.0) / 2.0
    for nh in (32.0, 48.0, N / 2.0, N / 2.0 + 6.0, N / 2.0 + 12.0, N / 2.0 + 20.0, 90.0, 110.0, N - 2.0, N - 1.0, N):
        lS = nh + 1.0
        for wlab, w in (("w = |S|/2^10 (vOW ceiling)", lS - 10.0), ("w = n_h (formula's ceiling, outside vOW range)", nh)):
            k = 2.0 * nh - N
            eq8_form = math.log2(EQ8_CONST) + N - 0.5 * (nh + w)          # 7 l / sqrt(n_h w) per golden pair
            lq = min(0.0, k - (lS - 1.0))
            src_form = math.log2(C_LOC) + (min(lS, N) - w) / 2.0 - lq       # vOW 4.2-derived, cross pairs only
            rows.append({"n_h_log2": nh, "w_rule": wlab, "w_log2": round(w, 2), "golden_pairs_k_log2": round(k, 2),
                         "regime": "sparse" if k <= 0 else "dense",
                         "per_golden_eq8_form_log2": round(eq8_form, 3),
                         "per_golden_vOW42_derived_log2": round(src_form, 3),
                         "decompositions_per_target_log2": round(k - math.log2(math.comb(m, S)), 2),
                         "below_sqrt_l": src_form < sqrt_l, "claim_B_premise_holds_ge_sqrt_2l": src_form >= sqrt_2l,
                         "one_version_yield_log2": round(math.log2(1.1) + w + lq, 2)})
    return {"N": N, "m": m, "S": S, "C(m,S)": math.comb(m, S), "sqrt_l_log2": sqrt_l, "sqrt_2l_log2": sqrt_2l,
            "B_premise_boundary": "per-golden 7 l/sqrt(n_h w) >= sqrt(2 l)  <=>  n_h w <= 24.5 l (eq. 8 constants)",
            "rows": rows}


def dense_limit_vs_pcs(N, conv="FAV"):
    """At fixed d, compare C5 (n_h at cap, best m, s free) with C3 at the same d."""
    rows = []
    for d in (12.0, 16.0, 20.0, 24.0, 28.0, 32.0):
        c3 = c3_cell(N, d, conv)["TOTAL"]
        best = None
        for m in M_VALUES:
            c = c5_setup(N, d, conv, m, None)
            if not c["valid"]:
                continue
            o = c5_opt(c)
            T = lsum(o["harvest"], la_of(d, conv), d)
            at_cap = c["nh"] >= c["Ne"] - 1.0 - 1e-9
            if best is None or T < best[0]:
                best = (T, m, at_cap, c["nh"], o["floor_binds"])
        if best is None:
            rows.append({"d": d, "C3_TOTAL": round(c3, 3), "C5_best": None})
            continue
        rows.append({"d": d, "C3_TOTAL": round(c3, 3), "C5_best_TOTAL": round(best[0], 3), "C5_minus_C3": round(best[0] - c3, 3),
                     "m": best[1], "n_h_at_cap_l_e_over_2": best[2], "n_h_log2": round(best[3], 2), "birthday_floor_binds": best[4]})
    return rows


def main():
    t0 = time.time()
    digests = json.load(open(DIG))
    raw_sha = hashlib.sha256(open(RAW, "rb").read()).hexdigest()
    want = digests["run_directory"]["raw-result.json"]
    if want != raw_sha:
        raise SystemExit("raw-result.json sha256 mismatch against artifact-digests.json; refusing")
    log2_r = json.load(open(RAW))["inputs"]["subgroup_order_131"]["log2_r"]

    out = {"task_id": "TASK-20261002-46ba70", "joint": "JR-2", "label": "REVIEWER COMPUTATION (closed forms; zero runs)",
           "raw_result_sha256": raw_sha, "log2_r_131": log2_r,
           "vow_42_constants": {"generation_per_version_x_sqrt_nw": round(GEN_PER_VERSION, 4),
                                "total_per_version_x_sqrt_nw": round(TOTAL_PER_VERSION, 4),
                                "C_LOC_per_distinct_collision": round(C_LOC, 4), "C_GEN_per_distinct_collision": round(C_GEN, 4),
                                "eq4_check_0.45_x_total_per_version": round(EQ4_CHECK, 4), "eq8_constant": round(EQ8_CONST, 4),
                                "X6_constant_4_log2": 2.0, "C_GEN_log2": round(math.log2(C_GEN), 4), "C_LOC_log2": round(math.log2(C_LOC), 4)},
           "x6_check_n131_d10_w10": None, "per_degree": [], "dichotomy_n131_m8": None, "dense_limit_vs_pcs_n131": None}
    N131 = degree_N(131, log2_r)
    x6 = 2.0 + 10.0 + (N131 - 10.0) / 2.0
    out["x6_check_n131_d10_w10"] = {"T_log2": x6, "VOW": round(vow(N131), 4), "margin": round(x6 - vow(N131), 4),
                                    "with_C_GEN": round(x6 - 2.0 + math.log2(C_GEN) - vow(N131), 4),
                                    "with_C_LOC": round(x6 - 2.0 + math.log2(C_LOC) - vow(N131), 4)}
    print("vOW 4.2 constants:", out["vow_42_constants"], flush=True)
    print("X-6 check n=131 d=w=10:", out["x6_check_n131_d10_w10"], flush=True)

    for n in DEGREES:
        N = degree_N(n, log2_r)
        V = vow(N)
        row = {"n": n, "N": N, "VOW": round(V, 4)}
        row["C1_X6_in_validity"] = c1_min(N, True)
        row["C1_X6_extrapolated_w_lt_2^10"] = c1_min(N, False)
        row["C2_PCS_source"] = {f"{conv}_{lab}": c2_min(N, conv, c) for conv in ("PROG", "FAV")
                                for lab, c in (("C_LOC", C_LOC), ("C_GEN", C_GEN))}
        row["C3_birthday_ideal"] = {"PROG_d_ge_0": c3_min(N, "PROG", 0.0), "PROG_d_ge_1": c3_min(N, "PROG", 1.0),
                                    "FAV_d_ge_1": c3_min(N, "FAV", 1.0), "FAV_d_ge_3.5": c3_min(N, "FAV", 3.5),
                                    "FAV_d_ge_10": c3_min(N, "FAV", 10.0)}
        c5 = {}
        for conv in ("PROG", "FAV"):
            for m in M_VALUES:
                for s in range(1, m // 2 + 1):
                    c5[f"{conv}_m{m}_s{s}"] = c5_min(N, conv, m, s, N / 2.0)
        row["C5_golden_collision"] = c5
        row["C6_shared_table_hybrid"] = {conv: c6_min(N, conv) for conv in ("PROG", "FAV")}
        row["LB_hhan"] = lb_table(N)
        # Baseline embedding: C3 with K = 1 on the negation quotient is vOW rho with negation,
        # sqrt(pi l / 4) = 0.886 sqrt(l) exactly; must give margin 0.
        rho_embed = 0.5 * (1.0 + N - 1.0) + log2_gamma_ratio(1.0)
        row["baseline_embedding_C3_K1_negation"] = {"T_log2": round(rho_embed, 6), "margin_vs_VOW": round(rho_embed - V, 6)}
        row["MUTATION_C5_no_birthday_floor"] = {f"{conv}_m{m}": c5_no_floor_mutation(N, conv, m)
                                               for conv in ("PROG", "FAV") for m in M_VALUES}

        cands = []
        cands.append(("C1 X-6 as written (vOW range)", row["C1_X6_in_validity"]["margin_vs_VOW"]))
        for k, v in row["C2_PCS_source"].items():
            cands.append((f"C2 PCS source {k}", v["margin_vs_VOW"]))
        for k, v in row["C3_birthday_ideal"].items():
            if k != "PROG_d_ge_0":
                cands.append((f"C3 birthday ideal {k}", v["margin_vs_VOW"]))
        for k, v in c5.items():
            if "margin_vs_VOW" in v:
                cands.append((f"C5 golden {k}", v["margin_vs_VOW"]))
        for k, v in row["C6_shared_table_hybrid"].items():
            cands.append((f"C6 shared table {k}", v["margin_vs_VOW"]))
        cands.sort(key=lambda t: t[1])
        row["minimum_over_constructed"] = {"config": cands[0][0], "margin_vs_VOW": cands[0][1],
                                           "any_below_VOW": cands[0][1] < 0.0, "n_configs": len(cands)}
        c5_best = min(((k, v) for k, v in c5.items() if "margin_vs_VOW" in v), key=lambda kv: kv[1]["margin_vs_VOW"])
        row["C5_best"] = {"key": c5_best[0], **c5_best[1]}
        out["per_degree"].append(row)
        print(f"n={n:4d} N={N:7.3f} VOW={V:8.3f} | X6 {row['C1_X6_in_validity']['margin_vs_VOW']:+.3f} "
              f"| C2 FAV_C_GEN {row['C2_PCS_source']['FAV_C_GEN']['margin_vs_VOW']:+.3f} "
              f"| C3 FAV d>=1 {row['C3_birthday_ideal']['FAV_d_ge_1']['margin_vs_VOW']:+.3f} "
              f"(d>=10 {row['C3_birthday_ideal']['FAV_d_ge_10']['margin_vs_VOW']:+.3f}) "
              f"| C5 best {c5_best[0]} {c5_best[1]['margin_vs_VOW']:+.3f} d={c5_best[1]['d']} "
              f"| C6 FAV {row['C6_shared_table_hybrid']['FAV']['margin_vs_VOW']:+.3f} a*={row['C6_shared_table_hybrid']['FAV']['alpha_star_values_over_all_d']} "
              f"| LB d* cons {row['LB_hhan']['conservative_neg_x2']['d_star_first_positive_and_stays']} "
              f"| MIN {cands[0][0]} {cands[0][1]:+.3f} "
              f"| rho-embed {row['baseline_embedding_C3_K1_negation']['margin_vs_VOW']:+.6f} "
              f"| MUT no-floor FAV_m10 {row['MUTATION_C5_no_birthday_floor']['FAV_m10'].get('margin_vs_VOW')} "
              f"sub={sum(v.get('cells_below_VOW', 0) for v in row['MUTATION_C5_no_birthday_floor'].values())}  [{time.time() - t0:.0f}s]", flush=True)

    out["dichotomy_n131_m8"] = dichotomy_table(N131, 8)
    out["dense_limit_vs_pcs_n131"] = dense_limit_vs_pcs(N131)
    out["c3_margin_vs_d_FAV_n131"] = [{"d": d, "margin": round(c3_cell(N131, d, "FAV")["TOTAL"] - vow(N131), 4)}
                                      for d in (1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 15.0, 20.0, 30.0)]
    out["any_constructed_config_below_VOW_at_any_degree"] = any(r["minimum_over_constructed"]["any_below_VOW"] for r in out["per_degree"])
    out["runtime_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(HERE, "jr2_out"), exist_ok=True)
    with open(os.path.join(HERE, "jr2_out", "jr2_results.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1, default=str) + "\n")
    print("ANY constructed configuration below VOW at any degree:", out["any_constructed_config_below_VOW_at_any_degree"])
    print("dense limit vs PCS (n=131, FAV):", json.dumps(out["dense_limit_vs_pcs_n131"]))
    print("C3 FAV margin vs d (n=131):", json.dumps(out["c3_margin_vs_d_FAV_n131"]))


if __name__ == "__main__":
    main()

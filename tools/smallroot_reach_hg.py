#!/usr/bin/env python3
"""Small-root reach under the Howgrave-Graham comparison exponent.

Why this module exists
----------------------
`tools/smallroot_reach.py` states the success condition of the Jochemsz-May
shift lattice as

    prod_i X_i^{s_i}  <  p^{s_p},        s_p = sum_k (t-k) |M_k \\ M_{k+1}|     (TOOL)

where s_p is the exponent of p in det(L).  The Howgrave-Graham criterion is
det(L) < p^{t * dim(L)}, i.e. prod_i X_i^{s_i} < p^{t*dim - s_p}.  Because the
shift sets are nested (M_k is contained in M_{k-1}) the right-hand side is

    t*dim - s_p  =  sum_{k>=1} |M_k|                                              (HG)

The two conventions coincide as t -> infinity for n = 1, which is all that
`tests/test_smallroot_reach.py` checks against a theorem (Coppersmith: reach
exactly 1/d).  For n >= 2 they differ, and the identity

    eps_HG = eps_TOOL / n          (t -> infinity, any support, equal bounds)

follows from |M_0| ~ (n+1)-fold the mean of |M_k| weighted by k.  The TOOL
full-box limit 2n/(d(n+1)) reads 4/3 at n = 2, d = 1 -- above the information
bound 1 -- which is impossible; the HG limit 2/(d(n+1)) never exceeds 2/(d(n+1))
<= 2/3 at d = 1, n = 2.

This module leaves the committed instrument UNMODIFIED (it is frozen by
EXP-PFDR-9b4f2a and is the "TOOL" comparator of EXP-ECDLP-64fa3d) and imports it.
Everything here is an analysis computation, not an experimental run: the
pre-registered audit EXP-ECDLP-64fa3d has produced no run, and this module
neither substitutes for nor pre-empts it.  Claim tier: toy.  `sota_delta`: zero.

Calibration that distinguishes the two conventions (the univariate Coppersmith
check cannot): Boneh-Durfee with x-shifts only must give delta < 1/4, and no
single modular equation may be credited eps > 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import smallroot_reach as R  # noqa: E402


# ---------------------------------------------------------------------------
# Supply side, HG convention
# ---------------------------------------------------------------------------


def jm_reach_full_box_hg(n: int, d: int, t: int) -> Fraction:
    """Per-variable beta_max at multiplicity t for the full box [0,d]^n, exact.

    Same shift sets as `R.jm_reach_full_box`; only the right-hand side differs:
    sum_{k>=1} |M_k| with |M_k| = (d(t-k)+1)^n, against s = n * s_i.
    """
    if t < 1:
        raise ValueError("multiplicity t must be >= 1")
    side = t * d + 1
    s_i = side ** (n - 1) * (t * d) * (t * d + 1) // 2
    rhs = sum((d * (t - k) + 1) ** n for k in range(1, t + 1))
    return Fraction(rhs, n * s_i)


def jm_reach_limit_hg(n: int, d: int, t_max: int = 60) -> tuple[float, float]:
    """(beta_max, eps) as t -> infinity by Richardson extrapolation in 1/t."""
    b1 = float(jm_reach_full_box_hg(n, d, t_max // 2))
    b2 = float(jm_reach_full_box_hg(n, d, t_max))
    beta = 2.0 * b2 - b1
    return beta, n * beta


def jm_reach_closed_form_hg(n: int, d: int) -> Fraction:
    """eps = 2 / (d (n+1)), the t -> infinity limit of jm_reach_limit_hg."""
    return Fraction(2, d * (n + 1))


def hg_rhs(support, t, leading=None):
    """(rhs, s_vec, dim) on an arbitrary support; success iff
    sum_i beta_i * s_i < rhs, with rhs = t*dim - s_p = sum_{k>=1}|M_k|."""
    s_p, s_vec, dim = R.jm_reach_extended(support, t, leading=leading)
    return t * dim - s_p, s_vec, dim


def eps_extended_symmetric_hg(support, t_a=8, t_b=16):
    """eps for equal bounds on every variable, extended strategy, t -> infinity.

    Richardson in 1/t from (t_a, t_b).  Returns (eps, beta)."""
    def at(t):
        rhs, s_vec, _ = hg_rhs(support, t)
        return float(rhs) / float(sum(s_vec))
    b1, b2 = at(t_a), at(t_b)
    # beta(t) = beta_inf + c/t  =>  beta_inf = (t_b b2 - t_a b1) / (t_b - t_a)
    beta = (t_b * b2 - t_a * b1) / (t_b - t_a)
    return beta * len(support[0]), beta


def success_ratio(support, t, bounds, leading=None):
    """lhs/rhs of the success condition under HG (success iff < 1)."""
    rhs, s_vec, _ = hg_rhs(support, t, leading=leading)
    lhs = sum(Fraction(b) * s for b, s in zip(bounds, s_vec))
    return float(lhs / rhs)


# ---------------------------------------------------------------------------
# Measured reaches and the decision table
# ---------------------------------------------------------------------------
# Derived from the TOOL's measured values by eps_HG = eps_TOOL / n (verified
# numerically against `eps_extended_symmetric_hg` in the tests):
#   l = 2 -> S_3: 0.840814 / 3 = 0.280271   (full box 0.25,  gain x1.12)
#   l = 3 -> S_4: 0.413684 / 4 = 0.103421   (full box 0.10,  gain x1.03)
# l >= 4 keeps the 1.15x sparsity allowance on the HG closed form.

MEASURED_REACH_HG = {2: R.MEASURED_REACH[2] / 3, 3: R.MEASURED_REACH[3] / 4}


def eps_available_hg(m: int, w: int) -> tuple[float, int, int, int]:
    l = R.block_inputs(m, w)
    n = l + 1
    d = 2 ** (l - 1)
    if l in MEASURED_REACH_HG:
        return MEASURED_REACH_HG[l], l, n, d
    return float(jm_reach_closed_form_hg(n, d)) * R.SPARSITY_ALLOWANCE, l, n, d


def decision_table_hg(m_values) -> list[dict]:
    rows = []
    for m in m_values:
        best = None
        for w in range(0, max(1, m - 1)):
            req = R.eps_required(m, w)
            avail, worst, n, d = eps_available_hg(m, w)
            margin = avail - float(req)
            rec = {"m": m, "w": w, "blocks": w + 1, "worst_block_leaves": worst,
                   "unknowns_per_eq": n, "per_var_degree": d,
                   "eps_required": float(req), "eps_available": float(avail),
                   "margin": margin, "alive": margin > 0}
            if best is None or margin > best["margin"]:
                best = rec
            rows.append(rec)
        best = dict(best)
        best["is_best_for_m"] = True
        rows.append(best)
    return rows


def summarize_hg(m_values) -> dict:
    rows = decision_table_hg(m_values)
    plain = [r for r in rows if not r.get("is_best_for_m")]
    return {
        "instrument": "tools/smallroot_reach_hg.py",
        "convention": "HG: comparison exponent sum_{k>=1}|M_k| = t*dim - s_p",
        "supersedes_numbers_of": "tools/smallroot_reach.py (TOOL convention), unmodified",
        "claim_tier": "toy",
        "rows": rows,
        "best_per_m": [r for r in rows if r.get("is_best_for_m")],
        "any_configuration_alive": any(r["alive"] for r in plain),
        "eps_available_ceiling": MEASURED_REACH_HG[2],
        "worst_case_best_margin": max(r["margin"] for r in plain),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--m", default="4,5,6,8,12,16,24,32")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--compare", action="store_true",
                    help="print TOOL vs HG for the S_3 / S_4 blocks and full boxes")
    args = ap.parse_args(argv)
    ms = [int(x) for x in args.m.split(",")]
    rep = summarize_hg(ms)
    if args.json:
        print(json.dumps(rep, indent=2))
        return 0
    if args.compare:
        print("full box, eps(TOOL) vs eps(HG):")
        for n, d in [(1, 2), (2, 1), (2, 2), (3, 2), (4, 4), (5, 8)]:
            print(f"  n={n} d={d}  TOOL {float(R.jm_reach_closed_form(n, d)):.4f}"
                  f"  HG {float(jm_reach_closed_form_hg(n, d)):.4f}")
        for name, sup in (("S_3", R.s3_support()),):
            e, _ = eps_extended_symmetric_hg(sup)
            print(f"{name} extended (t=8,16 Richardson): HG {e:.4f}  "
                  f"(identity value {MEASURED_REACH_HG[2]:.4f})")
        print()
    print(f"{'m':>4} {'w':>4} {'blocks':>6} {'l':>3} {'n':>3} {'deg':>5} "
          f"{'eps_req':>8} {'eps_avail':>9} {'margin':>9}  alive")
    for r in rep["rows"]:
        if r.get("is_best_for_m"):
            continue
        print(f"{r['m']:>4} {r['w']:>4} {r['blocks']:>6} {r['worst_block_leaves']:>3} "
              f"{r['unknowns_per_eq']:>3} {r['per_var_degree']:>5} "
              f"{r['eps_required']:>8.4f} {r['eps_available']:>9.4f} "
              f"{r['margin']:>9.4f}  {'yes' if r['alive'] else 'no'}")
    print("\nany configuration alive:", rep["any_configuration_alive"],
          "| best margin:", round(rep["worst_case_best_margin"], 4))
    return 0


if __name__ == "__main__":
    sys.exit(main())

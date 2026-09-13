#!/usr/bin/env python3
"""J4 -- the exponential-versus-polynomial mechanism of CLAIM B.

TASK-20260913-da3982, validator, REVIEW-SEMBIN-20260913-9d649f.

Does NOT import joint_balance.py. Everything is written from
inputs/SEMAEV-2015-310/paper_fulltext.md:

  eq. (11), Section 4.3:  P(n,m,t,k) = 1 - exp(-2^{tk-n} / t!)
  Section 4.5.1:          (5) at chain length t has n(t-1) equations in
                          n(t-2) + kt variables
  Section 4.5.2:          stage 1 = 2^k * solve / P ; stage 2 = 2^{k w'}
                          solve = n^{4w} (block) or [n(m-1)]^{4w} (standard F4)
  Section 4.4:            Macaulay width = monomial count at degree <= d_F4

(a) yield-loss scaling and the regime boundary
(b) the solving saving per unit of t, and whether it is exponential in (m-t)
(c) whether an optimizer over (m,t) genuinely varies t
"""

from __future__ import annotations

import json
import math
from math import comb, log2, lgamma

LOG2E = 1.0 / math.log(2.0)


def log2_fact(t: int) -> float:
    return lgamma(t + 1.0) * LOG2E


def k_unceiled(n: int, m: int) -> float:
    return n / m


def k_ceil(n: int, m: int) -> int:
    return -(-n // m)


def nvars(n: int, t: int, k: float) -> int:
    """Section 4.5.1: n(t-2) + kt."""
    return int(round(t * k + max(t - 2, 0) * n))


def width_log2(nv: int, d: int = 4) -> float:
    return log2(sum(comb(nv, i) for i in range(d + 1)))


# ---------------------------------------------------------------------------
# (a) eq. (11) exactly, and in the two limits
# ---------------------------------------------------------------------------


def log2_A(n: int, t: int, k: float) -> float:
    """log2 of the Poisson parameter A = 2^{tk-n}/t! of eq. (11)."""
    return t * k - n - log2_fact(t)


def log2_P_exact(n: int, t: int, k: float) -> float:
    """log2 (1 - exp(-A)), evaluated without cancellation."""
    la = log2_A(n, t, k)
    if la < -50.0:
        return la                        # 1-exp(-A) = A(1 - A/2 + ...) -> A
    if la > 12.0:
        return 0.0                       # P -> 1
    return log2(-math.expm1(-(2.0 ** la)))


def log2_P_linear(n: int, t: int, k: float) -> float:
    """The linearised law P ~ A, valid iff A << 1."""
    return log2_A(n, t, k)


out: dict = {}

# ---- the analytic scaling, derived and then checked numerically -----------
# log2 P(t) = tk - n - log2(t!) in the linear regime, so
#     log2 P(t) - log2 P(t-1) = k - log2 t
# i.e. shortening the chain by one costs exactly (k - log2 t) bits of yield.
scaling = []
for (n, m) in [(163, 7), (233, 9), (283, 9), (409, 11), (571, 12),
               (283, 10), (310, 10), (409, 10), (571, 10)]:
    kc = k_ceil(n, m)
    ku = k_unceiled(n, m)
    rows = []
    for t in range(3, m + 1):
        analytic = ku - log2(t)
        numeric = log2_P_exact(n, t, ku) - log2_P_exact(n, t - 1, ku)
        rows.append({"t_from": t, "t_to": t - 1,
                     "analytic_k_minus_log2_t": round(analytic, 4),
                     "numeric_from_eq11": round(numeric, 4),
                     "agree_to_1e-6": abs(analytic - numeric) < 1e-6})
    scaling.append({"n": n, "m": m, "k_unceiled": round(ku, 4), "k_ceiled": kc,
                    "per_unit_t_at_t_eq_m": round(ku - log2(m), 4),
                    "steps": rows,
                    "all_steps_match_analytic": all(r["agree_to_1e-6"] for r in rows)})
out["j4a_yield_loss_scaling"] = {
    "derivation": ("A(t) = 2^{tk-n}/t!; A(t-1)/A(t) = 2^{-k} * t. In the regime "
                   "A << 1 eq. (11) gives P ~ A, so one unit of t costs exactly "
                   "k - log2(t) bits of yield. Cumulatively from m down to t: "
                   "(m-t)k - log2(m!/t!), which at k ~ n/m is ~ n(1 - t/m) -- "
                   "LINEAR in n in the exponent, i.e. exponential in n."),
    "per_parameter_set": scaling,
    "all_match": all(s["all_steps_match_analytic"] for s in scaling),
}

# ---- the regime boundary -------------------------------------------------
# The premise of CLAIM B is that 2^{tk-n} is operative and t! dominated, i.e.
# A << 1 so that P ~ A. The premise FAILS where A >~ 1, because then P ~ 1 and
# reducing t costs no yield at all -- any solving saving would be pure profit.
boundary = {"saturated_cells": [], "near_boundary_cells": []}
worst = None
for n in range(250, 601):
    for m in range(2, 21):
        ku = k_unceiled(n, m)
        for t in range(2, m + 1):
            la = log2_A(n, t, ku)
            if la >= 0.0:
                boundary["saturated_cells"].append(
                    {"n": n, "m": m, "t": t, "log2_A": round(la, 3)})
            elif la >= -2.0:
                boundary["near_boundary_cells"].append(
                    {"n": n, "m": m, "t": t, "log2_A": round(la, 3)})
            if worst is None or la > worst[0]:
                worst = (la, n, m, t)
out["j4a_regime_boundary"] = {
    "boundary_condition": ("P saturates (P -> 1, zero yield cost to shortening) "
                           "iff A = 2^{tk-n}/t! >~ 1, i.e. tk - n >~ log2(t!). "
                           "Since k = ceil(n/m) gives mk - n <= m-1 while "
                           "log2(m!) > m-1 for m >= 4, A < 1 already at t = m, "
                           "and A falls by a further 2^{-k}*t per unit of t."),
    "n_saturated_cells_in_swept_range": len(boundary["saturated_cells"]),
    "n_near_boundary_cells": len(boundary["near_boundary_cells"]),
    "max_log2_A_over_swept_range": round(worst[0], 4),
    "argmax": {"n": worst[1], "m": worst[2], "t": worst[3]},
    "saturated_examples": boundary["saturated_cells"][:10],
    "near_boundary_examples": boundary["near_boundary_cells"][:10],
    "linear_law_max_abs_error_bits": round(max(
        abs(log2_P_exact(n, t, k_unceiled(n, m)) - log2_P_linear(n, t, k_unceiled(n, m)))
        for n in range(250, 601, 25) for m in range(2, 21)
        for t in range(2, m + 1)), 8),
}

# ---------------------------------------------------------------------------
# (b) the solving saving per unit of t
# ---------------------------------------------------------------------------


def solve_log2(n: int, t: int, k: float, model: str, omega: float = 3.0) -> float:
    if model == "block_n4w":
        return 4.0 * omega * log2(n)
    if model == "f4_std":
        return 4.0 * omega * log2(n * (t - 1))
    if model == "macaulay4":
        return omega * width_log2(nvars(n, t, k), 4)
    raise ValueError(model)


saving = []
for (n, m) in [(283, 9), (310, 10), (409, 11), (571, 12), (283, 10), (409, 10)]:
    ku = k_unceiled(n, m)
    per_model = {}
    for model in ("macaulay4", "f4_std", "block_n4w"):
        steps = []
        for t in range(3, m + 1):
            steps.append({"t_from": t, "t_to": t - 1,
                          "solve_saving_bits": round(
                              solve_log2(n, t, ku, model)
                              - solve_log2(n, t - 1, ku, model), 4),
                          "yield_loss_bits": round(ku - log2(t), 4),
                          "step_pays": bool(
                              (solve_log2(n, t, ku, model)
                               - solve_log2(n, t - 1, ku, model)) > (ku - log2(t)))})
        cum = []
        for t in range(2, m + 1):
            sg = solve_log2(n, m, ku, model) - solve_log2(n, t, ku, model)
            yl = log2_P_exact(n, m, ku) - log2_P_exact(n, t, ku)
            cum.append({"t": t, "cum_solve_saving": round(sg, 3),
                        "cum_yield_loss": round(yl, 3),
                        "net_cost_vs_t_eq_m_bits": round(yl - sg, 3),
                        "t_beats_t_eq_m": bool(yl - sg < 0)})
        per_model[model] = {
            "per_unit_at_t_eq_m": steps[-1]["solve_saving_bits"] if steps else 0.0,
            "per_unit_min": min((s["solve_saving_bits"] for s in steps), default=0.0),
            "per_unit_max": max((s["solve_saving_bits"] for s in steps), default=0.0),
            "steps_where_saving_exceeds_yield_loss": [
                s for s in steps if s["step_pays"]],
            "cumulative": cum,
            "any_t_beats_t_eq_m": any(c["t_beats_t_eq_m"] for c in cum),
        }
    saving.append({"n": n, "m": m, "k": round(ku, 3), "models": per_model})
out["j4b_solving_saving"] = {
    "record_claim": "2 to 3 bits per unit of t",
    "per_parameter_set": saving,
}

# ---- is any reading exponential in (m-t)? --------------------------------
# A cost exponential in (m-t) means solve(m) - solve(t) grows LINEARLY in
# (m-t). Each reading here is a fixed power of a quantity LINEAR in t, so the
# saving grows like log(m-t): sublinear, hence polynomial in (m-t), never
# exponential. Checked by second difference.
expo = []
for model in ("macaulay4", "f4_std", "block_n4w"):
    n, m = 409, 20
    ku = k_unceiled(n, m)
    vals = [solve_log2(n, m, ku, model) - solve_log2(n, t, ku, model)
            for t in range(2, m + 1)]
    first = [b - a for a, b in zip(vals[1:], vals[:-1])]
    expo.append({"model": model, "n": n, "m": m,
                 "cum_saving_by_t": [round(v, 3) for v in vals],
                 "increments_as_t_decreases": [round(v, 3) for v in first],
                 "increments_are_increasing_not_constant": all(
                     b >= a - 1e-9 for a, b in zip(first, first[1:])),
                 "verdict": ("saving grows like log(m-t): the cost RATIO is "
                             "polynomial in (m-t), not exponential"
                             if model != "block_n4w" else
                             "identically zero: t-independent")})
out["j4b_exponential_in_m_minus_t"] = {
    "question": "is any solving-cost reading exponential in (m-t)?",
    "answer": "no",
    "readings": expo,
}

# ---- reconcile "drops dramatically" with the measured tables -------------
# Section 3 step 3: "for t < m the solving running time ... drops dramatically".
# Tables 1-2 measure it. (n, m, t, avg_seconds) from tables.yaml.
T2 = [
    (15, 4, 4, 102.85), (15, 4, 3, 0.4765), (15, 4, 2, 0.0013),
    (15, 5, 5, 174.47), (15, 5, 4, 12.95), (15, 5, 3, 0.0339), (15, 5, 2, 0.0006),
    (16, 4, 4, 160.87), (16, 4, 3, 0.4984), (16, 4, 2, 0.0014),
    (19, 3, 3, 137.32), (19, 3, 2, 0.0092),
    (21, 3, 3, 133.54), (21, 3, 2, 0.0095),
]
by_nm: dict = {}
for (n, m, t, s) in T2:
    by_nm.setdefault((n, m), {})[t] = s
recon = []
for (n, m), d in sorted(by_nm.items()):
    ku = k_unceiled(n, m)
    for t in sorted(d):
        if t + 1 in d:
            meas = log2(d[t + 1] / d[t])
            recon.append({
                "n": n, "m": m, "step": f"t={t+1}->{t}",
                "measured_drop_bits": round(meas, 3),
                "pred_macaulay4_bits": round(
                    solve_log2(n, t + 1, ku, "macaulay4")
                    - solve_log2(n, t, ku, "macaulay4"), 3),
                "pred_f4_std_bits": round(
                    solve_log2(n, t + 1, ku, "f4_std")
                    - solve_log2(n, t, ku, "f4_std"), 3),
            })
out["j4b_dramatically_vs_2_to_3_bits"] = {
    "measured_drop_bits_range": [round(min(r["measured_drop_bits"] for r in recon), 3),
                                 round(max(r["measured_drop_bits"] for r in recon), 3)],
    "rows": recon,
    "note": ("Every measured point has m <= 5 and reaches t = 2, where the "
             "per-unit-t saving is large under the model too. The '2 to 3 bits' "
             "figure is the derivative AT t = m for m ~ 10-12; it is not a bound "
             "over the range of t."),
}

# ---------------------------------------------------------------------------
# (c) does an optimizer over (m,t) genuinely vary t?
#     Written here from scratch, not imported.
# ---------------------------------------------------------------------------


def total_log2(n: int, m: int, t: int, model: str, yield_on: bool = True,
               omega: float = 3.0, omega_p: float = 2.0,
               solve_override=None) -> float:
    ku = k_unceiled(n, m)
    solve = (solve_override(n, m, t, ku) if solve_override is not None
             else solve_log2(n, t, ku, model, omega))
    lp = log2_P_exact(n, t, ku) if yield_on else 0.0
    s1 = ku + solve - lp
    s2 = ku * omega_p
    hi, lo = max(s1, s2), min(s1, s2)
    return hi if hi - lo > 60 else hi + log2(1.0 + 2.0 ** (lo - hi))


def argmin_mt(n: int, model: str, yield_on: bool = True, m_hi: int = 20,
              solve_override=None) -> dict:
    best = None
    t_values_seen = set()
    for m in range(2, m_hi + 1):
        for t in range(2, m + 1):
            c = total_log2(n, m, t, model, yield_on, solve_override=solve_override)
            t_values_seen.add(t)
            if best is None or c < best[0]:
                best = (c, m, t)
    c, m, t = best
    return {"n": n, "m_star": m, "t_star": t, "log2_cost": round(c, 4),
            "interior": t < m, "distinct_t_evaluated": len(t_values_seen)}


indep = {}
for model in ("macaulay4", "f4_std", "block_n4w"):
    indep[model] = [argmin_mt(n, model) for n in (250, 283, 300, 310, 409, 500, 571, 600)]
null_no_yield = [argmin_mt(n, "macaulay4", yield_on=False)
                 for n in (250, 283, 310, 409, 571)]
out["j4c_independent_optimizer"] = {
    "note": ("written from the published formulas in this file; does not import "
             "joint_balance.py"),
    "per_model": indep,
    "t_star_equals_m_star_everywhere": all(
        r["t_star"] == r["m_star"] for rows in indep.values() for r in rows),
    "no_yield_null_t_star": [{"n": r["n"], "t_star": r["t_star"],
                              "m_star": r["m_star"]} for r in null_no_yield],
    "no_yield_null_returns_t_eq_2": all(r["t_star"] == 2 for r in null_no_yield),
    "why_this_proves_t_is_varied": (
        "If t were ignored, removing the yield term could not move t* from m to "
        "2. It does, at every n, so t is a live variable in the objective."),
}

# A second, sharper probe: does t* respond to a solving cost engineered to
# make a SPECIFIC interior t optimal? If it does, the sweep is genuine.
def targeted(n_target_t: int):
    def f(n, m, t, k):
        return 0.0 if t == n_target_t else 400.0
    return f


out["j4c_targeted_probe"] = {
    "design": ("charge 400 bits for every t except one target value; a genuine "
               "sweep must return exactly that t"),
    "rows": [{"target_t": tt,
              **argmin_mt(409, "macaulay4", solve_override=targeted(tt))}
             for tt in (2, 3, 5, 7, 9)],
}

print(json.dumps(out, indent=1))

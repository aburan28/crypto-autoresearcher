#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- scoring per AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii DC-2.

Every hard-coded locus of v1 listed in DC-2 hard_coded_constants_the_rerun_must_replace and
additional_constants_found_by_this_reading is REPLACED here:
  * pdp_common.py 219-221: P-1..P-5 are recorded as PREDICTIONS ONLY and are never used as divisors;
    group orders S5 = 120, torsion_S5_rq = 1920, torsion_S5_norm = 3840 (v2_arms.group_order).
  * pdp_common.py 222-223: 2^6 / 2^9 kept as T-1 thresholds on MEASURED D_raw only; comparison
    constants 142.4 (uncharged) and 149.3 (charged), per B-3.
  * pdp_cell.py 451-455, 679-681: no ratio or non-freeness against 2^20; T-1 (measured D_raw on the
    same targets), T-2 (R_ref), T-3 (two-sided non-freeness), T-4 (unscored diagnostic).
  * pdp_cell.py 661, 653-672: supplementary cross-base / constructed-solvable ratios are NOT computed
    (R-7); orders 2^{m-1} m! (rq) and 2^m m! (norm).
  * pdp_cell.py 683, 693, 725: F3 and the 2^36 tail check are reported "undecidable (... DC-4)".
  * pdp_cell.py 708, 710, 720-721: success 1/120 (raw, S5), 1/(2^4 120) with halving (rq), 1/1920 with
    halving (norm); no proxy-based point estimate enters any band (DC-4).
  * symmetrize.py 88-89, 94: inversion priced at 2.57 (v2_field.OpCount).
Nothing here concludes that a hypothesis or heuristic is supported or refuted.
"""
import math

AMD = "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii"
UNDECIDABLE_F3 = "undecidable (%s DC-4)" % AMD
P64 = 2 ** 64 - 2 ** 32 + 1

PREDICTIONS = {
    "label": "PREDICTIONS ONLY (amendment DC-2 P-1..P-5). Never used as a divisor or as a scoring constant.",
    "P-1_D_S5": {"value_log2": 20.0, "text": "D_S5 ~ 2^20 = 16^5"},
    "P-2_D_raw": {"value_log2": math.log2(math.factorial(5) * 16 ** 5), "text": "D_raw ~ 5! 16^5 = 2^26.9"},
    "P-3_D_iii_prime": {"value_log2": 16.0, "text": "D_iii' ~ 2^16, AN EXTRAPOLATION"},
    "P-4_D_norm": {"value_log2": 20.0, "text": "D_norm ~ D_S5 = 2^20"},
    "P-5_S5_rescaled": {"value_log2": 20.0, "text": "D_S5_rescaled ~ 2^20"},
}

T1_MIN_LOG2 = {"S": 6.0, "rq": 9.0}         # thresholds unchanged from specification lines 185-186
T2_F1PRIME_LOG2 = 3.0
T2_PREDICTED_LOG2 = 4.0
DFLAT_THRESHOLD = 0.10
COMPARISON_UNCHARGED = 142.4
COMPARISON_CHARGED = 149.3


def _log2(x):
    return math.log2(x) if x and x > 0 else None


def common_targets(a, b):
    """Target indices measured with a defined D in both per-target maps {idx: D}."""
    return sorted(set(k for k, v in a.items() if v) & set(k for k, v in b.items() if v))


def cell_D(per_target):
    vals = [v for v in per_target.values() if v]
    if not vals:
        return None, "no measured target with a defined D"
    if all(v == vals[0] for v in vals):
        return vals[0], None
    return None, "D differs across measured targets (values recorded per target)"


def ratio_block(num_name, num, den_name, den, threshold_log2=None, ceiling_log2=None):
    """Like-for-like ratio on the SAME targets. num/den are {target: D}."""
    ts = common_targets(num, den)
    blk = {"numerator_arm": num_name, "denominator_arm": den_name, "common_targets": ts,
           "per_target": [{"target": t, "ratio": num[t] / den[t], "log2": math.log2(num[t] / den[t])} for t in ts]}
    Dn, rn = cell_D({t: num[t] for t in ts})
    Dd, rd = cell_D({t: den[t] for t in ts})
    if not ts:
        blk.update(status="not_measured", reason="no common target measured in both arms")
        return blk
    if Dn is None or Dd is None:
        blk.update(status="not_defined", reason=rn or rd)
        return blk
    r = Dn / Dd
    blk.update(status="measured", cell_ratio=r, cell_ratio_log2=math.log2(r))
    if threshold_log2 is not None:
        blk["threshold_log2"] = threshold_log2
        blk["below_threshold"] = math.log2(r) < threshold_log2
    if ceiling_log2 is not None:
        blk["ceiling_log2"] = ceiling_log2
        blk["instrument_anomaly_above_ceiling"] = math.log2(r) > ceiling_log2 + 1e-12
    return blk


def score_like_for_like(cells, m):
    """cells: {arm_kind: {target: D}} for ONE (shape, p, m, target_kind) group on the same targets.
    Returns T-1, T-2, T-3, T-4, the frozen tail check, F1 and F1' as recorded blocks."""
    G = 2 ** (m - 1)
    thr = (m == 5)
    out = {"rule": "every ratio pairs two arms on the SAME targets and the SAME factor base (R-7); never a constant",
           "thresholds_apply": thr,
           "thresholds_note": ("T-1 (2^6, 2^9) and F1' (2^3) are the frozen/amended thresholds for m = 5 cells; at other m the ratios are "
                               "reported without a threshold (implementation reading, disclosed in implementation-v2.md)")}
    raw_x, raw_u = cells.get("raw_x"), cells.get("raw_u")
    S, Sr, rq = cells.get("S"), cells.get("S_rescaled"), cells.get("rq")
    # T-1 on the x-base: D_raw / D_S (threshold 2^6)
    out["T-1_raw_over_S_xbase"] = (ratio_block("raw_x", raw_x, "S", S, T1_MIN_LOG2["S"] if thr else None)
                                   if raw_x is not None and S is not None else
                                   {"status": "not_measured", "reason": "D_raw or D_S not measured on this cell (never scored against a constant)"})
    # T-1 / F1 on the rescaled base: D_raw_u / D_iii' (threshold 2^9)
    out["T-1_raw_over_rq_rescaled_base"] = (ratio_block("raw_u", raw_u, "rq", rq, T1_MIN_LOG2["rq"] if thr else None)
                                            if raw_u is not None and rq is not None else
                                            {"status": "not_measured", "reason": "D_raw (rescaled base) or D_iii' not measured on this cell"})
    # T-2: R_ref = D_S_rescaled / D_iii' (F1' below 2^3; ceiling 2^{m-1})
    t2 = (ratio_block("S_rescaled", Sr, "rq", rq, T2_F1PRIME_LOG2 if thr else None, float(m - 1))
          if Sr is not None and rq is not None else
          {"status": "not_measured", "reason": "S_rescaled or iii' not measured on this cell"})
    t2["predicted_free_orbit_log2"] = float(m - 1)
    out["T-2_R_ref"] = t2
    # T-3: nonfreeness_iii' = 2^{m-1} D_iii' / D_S_rescaled (1 at free orbits; flag > 2 and < 1)
    if t2.get("status") == "measured":
        nf = G / t2["cell_ratio"]
        out["T-3_nonfreeness_iii_prime"] = {"value": nf, "flag_gt_2_drop_short": nf > 2, "flag_lt_1_ceiling_violated": nf < 1}
    else:
        out["T-3_nonfreeness_iii_prime"] = {"status": "not_defined", "reason": "R_ref not measured"}
    # frozen tail check: D_sym |G| / D_raw, flag < 0.5, only with measured D_raw on the same targets
    tails = {}
    for kind, raw_name, raw in (("S", "raw_x", raw_x), ("rq", "raw_u", raw_u), ("S_rescaled", "raw_u", raw_u)):
        sym = cells.get(kind)
        if sym is None or raw is None:
            tails[kind] = {"status": "not_measured", "reason": "D_raw not measured on the same targets"}
            continue
        blk = ratio_block(kind, sym, raw_name, raw)
        if blk.get("status") == "measured":
            order = {"S": math.factorial(m), "S_rescaled": math.factorial(m), "rq": G * math.factorial(m)}[kind]
            v = blk["cell_ratio"] * order
            tails[kind] = {"D_sym_times_G_over_D_raw": v, "flag_below_0_5": v < 0.5, "group_order": order,
                           "note": "frozen label 'severe non-freeness' names the > side while its test is < 0.5; both sides reported (T-3)"}
        else:
            tails[kind] = blk
    out["frozen_tail_check_D_sym_G_over_D_raw"] = tails
    # T-4: unscored diagnostic D_iii' / 2^16 (only meaningful at m = 5)
    if rq is not None and m == 5:
        D, r = cell_D(rq)
        out["T-4_D_iii_prime_over_2_16_UNSCORED"] = ({"value": D / 2 ** 16, "label": "diagnostic only; not a falsification branch and not a success condition"}
                                                      if D else {"status": "not_defined", "reason": r})
    t1r = out["T-1_raw_over_rq_rescaled_base"]
    out["F1"] = {"fires": bool(t1r.get("below_threshold")) if (thr and t1r.get("status") == "measured") else None,
                 "scoreable": thr and t1r.get("status") == "measured", "applies_to": "completed m = 5 EcGFp5-shaped cells only (the aggregate applies the shape)",
                 "note": "F1 reads D_raw on the rescaled base (raw_u), the like-for-like raw system for arm iii' (R-7); where either arm is not measured the branch cannot fire"}
    out["F1_prime"] = {"fires": bool(t2.get("below_threshold")) if (thr and t2.get("status") == "measured") else None,
                       "scoreable": thr and t2.get("status") == "measured", "applies_to": "completed m = 5 EcGFp5-shaped cells only (the aggregate applies the shape)",
                       "note": "fires when R_ref < 2^3 on a completed m = 5 EcGFp5-shaped cell; timeouts and memory exhaustion fire neither branch"}
    out["F3"] = UNDECIDABLE_F3
    out["tail_check_2_36"] = UNDECIDABLE_F3
    return out


def heur_dflat(points):
    """points: [(p, D)] for one arm/shape over m = 5 random cells with a defined cell D.
    HEUR-GFPN-DFLAT as frozen: relative variation < 10% across >= 3 primes spanning >= 12 bits.
    Relative variation = (max - min) / mean (the v1 definition, kept); max/min is reported too."""
    if not points:
        return {"heur_dflat_pass": "not_applicable", "reason": "no completed m = 5 cell with a measured D", "n_cells": 0}
    ps = sorted(p for p, _ in points)
    Ds = [d for _, d in points]
    span = max(ps).bit_length() - min(ps).bit_length()
    rel = (max(Ds) - min(Ds)) / (sum(Ds) / len(Ds))
    enough = len(points) >= 3 and span >= 12
    return {"heur_dflat_pass": (rel < DFLAT_THRESHOLD) if enough else "not_applicable",
            "reason": None if enough else "fewer than 3 primes or span < 12 bits",
            "n_cells": len(points), "primes": ps, "bit_span": span, "D_per_prime": {str(p): d for p, d in sorted(points)},
            "D_relative_variation": rel, "D_max_over_min": max(Ds) / min(Ds), "threshold": DFLAT_THRESHOLD}


def matched_F4(D_ecg, D_rand):
    rel = abs(D_ecg - D_rand) / D_ecg
    return {"D_ecgfp5_shaped": D_ecg, "D_random_2torsion": D_rand, "rel_diff": rel, "differs_more_than_10pct": rel > 0.10}


# ----------------------------------------------------------------------------- band (DC-2 B-1..B-5)
def success_model(kind, m=5):
    """Inverse success probability and relation-count factor of the model (B-1, B-2)."""
    f = math.factorial(m)
    if kind in ("raw_x", "raw_u", "S", "S_rescaled"):
        return {"inverse_success": f, "relations_factor": 1.0,
                "source": "1/m! (JV lines 329-349)" + ("; S_rescaled takes S_5's convention (implementation reading, disclosed)" if kind == "S_rescaled" else "")}
    if kind == "rq":
        return {"inverse_success": 2 ** (m - 1) * f, "relations_factor": 0.5,
                "source": "1/(2^{m-1} m!) and #F/m relations halved (FHJRV lines 336-347, 854)"}
    if kind == "norm":
        return {"inverse_success": 2 ** (m - 1) * f, "relations_factor": 0.5,
                "source": "1/1920 by the red team's count, with halving (amendment B-2)"}
    raise ValueError(kind)


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval by bisection on the binomial CDF (no external dependency)."""
    def cdf(x, pp):
        return sum(math.comb(n, i) * pp ** i * (1 - pp) ** (n - i) for i in range(0, x + 1))

    def bisect(f, lo=0.0, hi=1.0):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bisect(lambda pp: 1 - cdf(k - 1, pp) >= alpha / 2)
    hi = 1.0 if k == n else bisect(lambda pp: cdf(k, pp) <= alpha / 2)
    return lo, hi


def band_for_arm(kind, dflat_block, D_measured, successes, attempted):
    """B-3: emitted only for heur_dflat_pass true; both conventions; labelled MODELED.
    The three R-8 modeled fields are emitted separately."""
    passed = dflat_block.get("heur_dflat_pass")
    if passed is not True:
        reason = "heur_dflat_failed" if passed is False else "heur_dflat_not_applicable"
        return {"projected_systems_at_p_2_64": {"value": None, "reason": reason},
                "projected_linear_algebra_cost_at_p_2_64": {"value": None, "reason": reason},
                "full_cost_band_bits_per_curve": {"value": None, "reason": reason},
                "heur_dflat_pass": passed,
                "R-8_note": "heur_dflat_not_applicable is never relabelled heur_dflat_failed (validator K2)"}
    relations_bits = (2 - 2 / 5) * math.log2(P64)
    sm = success_model(kind)
    inv_model = sm["inverse_success"]
    inv_source = "model: " + sm["source"]
    interval = None
    if successes and successes > 0:
        rate = successes / attempted
        inv_model_used = 1 / rate
        lo, hi = clopper_pearson(successes, attempted)
        interval = [lo, hi]
        inv_source = "measured decomposition_success_rate (>= 1 verified success), with its binomial interval"
    else:
        inv_model_used = inv_model
    D = D_measured
    unch_sys = relations_bits
    ch_sys = relations_bits + math.log2(inv_model_used) + math.log2(sm["relations_factor"])
    edges = (math.log2(D ** 2), math.log2(5 * D ** 3))
    return {
        "label": "MODELED (arithmetic only; no wall time extrapolated; not a security finding)",
        "heur_dflat_pass": True, "D_measured_max_over_ladder": D,
        "projected_systems_at_p_2_64": {"uncharged_bits": unch_sys, "charged_bits": ch_sys,
                                         "charged_inverse_success_source": inv_source,
                                         "measured_success_interval_95": interval,
                                         "successes": successes, "targets_attempted": attempted},
        "projected_linear_algebra_cost_at_p_2_64": {"value": None, "reason": "not charged (amendment DC-2 B-4), flagged optimistic"},
        "full_cost_band_bits_per_curve": {
            "uncharged": {"D2_edge": unch_sys + edges[0], "5D3_edge": unch_sys + edges[1], "comparison_constant": COMPARISON_UNCHARGED},
            "charged": {"D2_edge": ch_sys + edges[0], "5D3_edge": ch_sys + edges[1], "comparison_constant": COMPARISON_CHARGED}},
        "optimistic_assumptions_restated": [
            "not charged: linear algebra on ~p^(2-2/5) sparse rows; memory; time-memory tradeoff; symmetrised-polynomial construction amortisation; the o(1) in FGLM's exponent (B-4)",
            "halving of the balanced relation count taken as a plain factor 1/2; balancing not re-derived for the reduced base (B-4)",
            "a time-memory statement is owed before any band is compared to 128 (B-4)",
            "success probabilities are FHJRV's and JV's counting model unless >= 1 verified success exists (B-1, B-3)"],
        "no_proxy_point_estimate": "no ops-proxy or instruction count enters this band (DC-4)",
    }


def reference_block():
    return {"amendment": AMD, "predictions": PREDICTIONS, "T-1_thresholds_log2": T1_MIN_LOG2,
            "T-2_F1prime_threshold_log2": T2_F1PRIME_LOG2, "T-2_predicted_log2": T2_PREDICTED_LOG2,
            "dflat_threshold_relative": DFLAT_THRESHOLD, "comparison_constants": {"uncharged": COMPARISON_UNCHARGED, "charged": COMPARISON_CHARGED},
            "F3": UNDECIDABLE_F3, "tail_check_2_36": UNDECIDABLE_F3, "p_crypto": str(P64),
            "group_orders": {"raw": 1, "S5": 120, "S5_rescaled": 120, "torsion_S5_rq": 1920, "torsion_S5_norm": 3840},
            "invalidation_rules_added": ["scoring any ratio against the constant 2^20 invalidates that scoring",
                                         "reporting torsion_S{m}_norm with group order 2^{m-1} m! invalidates that table",
                                         "choosing (beta, lam) per target invalidates the cell"]}

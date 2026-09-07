#!/usr/bin/env python3
"""
EXP-MONO-cb905d: Multi-cell extension and the OBJ-6 discriminating control.

Implements experiments/EXP-MONO-cb905d/specification.yaml exactly, per the
frozen contract. This script performs measurement only; it changes no
hypothesis/experiment/goal status.

Part A (primary, headline): apply EXP-MONO-12ce1c's own already-validated
OBJ-6 transversal-vs-group-uniform sampling control to the SAME matched
(p=617, N=580, tau=4) pair EXP-MONO-64aaa4 tested. The transversal arm's
counts are reused DIRECTLY from EXP-MONO-64aaa4's own archived
raw-result.json (no redraw). The group-uniform arm is NEW: 20000 fresh
draws per curve, rejection-sampled over affine (x,y) pairs on E(F_p), per
`inputs.seed_derivation_rule_part_a_group_uniform_arm`.

Part B (exploratory, secondary): read every matched-(N,tau) cell already
enumerable in EXP-MONO-64aaa4's own archived stage0_transcript.json
(same-prime AND cross-prime), fix a deterministic measurement order
(smallest-p-pair-sum first) BEFORE observing any result, and run fresh
TRANSVERSAL-ONLY Stage 1-2 measurements (EXP-MONO-64aaa4's own method,
unmodified, single "fixed" arm only -- the fixed/random dual-convention
control is proven tautological and is not re-run, per the frozen contract)
on every OTHER cell (the p=617 cell is reused directly from
EXP-MONO-64aaa4's own archived result, never re-measured).

Byte-identical code reuse: EXP-MONO-64aaa4's own implementation module is
loaded read-only by file path (never copied/edited) and its helper
functions (seed_bytes, draw_uniform, quad_char, count_points,
two_torsion_count, is_singular, j_invariant, construct_ordinary,
construct_cm_j0, construct_cm_j1728, ec_neg, ec_add, sqrt_mod_p,
build_factor_base, point_for_x, measure_curve, predicted_rate,
binomial_se_pairs, fisher_exact_2x2, SIGN_CLASSES, NCLASSES, NPAIRS) are
called directly from the loaded module. Its own module-level DOMAIN
constant is used UNCHANGED (still "EXP-MONO-64aaa4/v1") for the one-time
curve re-derivation sanity check in Part A (this MUST reproduce the
archived p=617 curves byte-identically or the run is
`failed_infrastructure`, per the stopping rule); it is then reassigned to
"EXP-MONO-cb905d/v1" for every subsequent draw this contract performs
(Part A's new group-uniform arm and Part B's fresh transversal draws on
other cells), per `inputs.seed_derivation_rule_part_a_group_uniform_arm`
and `inputs.seed_derivation_rule_part_b`.
"""
import importlib.util
import json
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_ROOT = HERE.parent  # experiments/EXP-MONO-cb905d
REPO_ROOT = EXP_ROOT.parent.parent  # crypto-autoresearcher

EXP64_ROOT = REPO_ROOT / "experiments" / "EXP-MONO-64aaa4"
EXP64_IMPL = EXP64_ROOT / "implementation" / "run_experiment.py"
EXP64_TRANSCRIPT = EXP64_ROOT / "runs" / "RUN-MONO-64aaa4-1" / "stage0_transcript.json"
EXP64_RAW_RESULT = EXP64_ROOT / "runs" / "RUN-MONO-64aaa4-1" / "raw-result.json"

CB_DOMAIN = "EXP-MONO-cb905d/v1"
NTUPLES = 20000
SEED = 20260901

RUN_DIR = EXP_ROOT / "runs" / "RUN-MONO-cb905d-1"


def load_m64():
    """Load EXP-MONO-64aaa4's own implementation module, read-only, by file
    path. Never edits or copies that file. Its module-level DOMAIN is
    "EXP-MONO-64aaa4/v1" immediately after this call."""
    spec = importlib.util.spec_from_file_location("exp_mono_64aaa4_impl", str(EXP64_IMPL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gu_draw_point(m64, p, A, B, role, tid, counter):
    """Group-uniform point draw per
    inputs.seed_derivation_rule_part_a_group_uniform_arm: draw x uniformly
    in F_p (label "gu-x"); if f(x) is a nonzero square, accept one of its
    two roots with equal probability (label "gu-sign"); if f(x) == 0,
    accept the 2-torsion point directly; if f(x) is a non-residue, reject
    and redraw. Returns ((x, y), next_counter)."""
    while True:
        x, counter = m64.draw_uniform("gu-x", p, role, tid, counter, p)
        f = (x * x * x + A * x + B) % p
        if f == 0:
            return (x, 0), counter
        chi = m64.quad_char(f, p)
        if chi == 1:
            small, large = m64.sqrt_mod_p(f, p)
            bit, counter = m64.draw_uniform("gu-sign", p, role, tid, counter, 2)
            y = small if bit == 0 else large
            return (x, y), counter
        # chi == -1 (non-residue): reject, redraw. counter already advanced.


def measure_group_uniform(m64, curve, ntuples, budget_deadline=None):
    """Group-uniform arm measurement: 3 group-uniform points per tuple
    (distinct x-coordinates, mirroring EXP-MONO-64aaa4's own distinctness
    rule for its 3 drawn factor-base x-indices), the SAME 4 canonical
    sign-class construction (SIGN_CLASSES, eps_1 fixed +1) EXP-MONO-64aaa4
    uses, unmodified."""
    A, B, p = curve["A"], curve["B"], curve["p"]
    role = curve["role"] + str(curve.get("j"))

    total_pairs_colliding = 0
    tuples_with_collision = 0

    for tid in range(ntuples):
        counter = 0
        chosen_x = set()
        pts = []
        while len(pts) < 3:
            pt, counter = gu_draw_point(m64, p, A, B, role, tid, counter)
            if pt[0] in chosen_x:
                continue
            chosen_x.add(pt[0])
            pts.append(pt)

        sums = []
        for eps in m64.SIGN_CLASSES:
            acc = None
            for k in range(3):
                term = pts[k] if eps[k] == 1 else m64.ec_neg(pts[k], p)
                acc = m64.ec_add(acc, term, A, p)
            xval = "INF" if acc is None else acc[0]
            sums.append(xval)

        collisions_this_tuple = 0
        for i in range(m64.NCLASSES):
            for j in range(i + 1, m64.NCLASSES):
                if sums[i] == sums[j]:
                    collisions_this_tuple += 1
        total_pairs_colliding += collisions_this_tuple
        if collisions_this_tuple > 0:
            tuples_with_collision += 1

        if budget_deadline is not None and tid % 2000 == 0 and time.time() > budget_deadline:
            raise TimeoutError(f"budget deadline exceeded during group-uniform measurement at tuple {tid}")

    return {
        "ntuples": ntuples,
        "total_pairs_colliding": total_pairs_colliding,
        "tuples_with_collision": tuples_with_collision,
        "rate_pairs_per_tuple": total_pairs_colliding / ntuples,
        "rate_any_collision": tuples_with_collision / ntuples,
    }


def stage0_enumerate(transcript):
    """Enumerate ALL matched-(N,tau) cells (ordinary entry x CM entry,
    across ALL primes in the transcript, same-prime AND cross-prime),
    separately counted, per inputs.part_b_cells."""
    ord_entries = []
    cm_entries = []
    for e in transcript:
        p = e["p"]
        if e.get("ord") is not None:
            o = dict(e["ord"])
            o["p"] = p
            ord_entries.append(o)
        if e.get("cm_j0") is not None:
            c = dict(e["cm_j0"])
            c["p"] = p
            c["variant"] = "j0"
            cm_entries.append(c)
        if e.get("cm_j1728") is not None:
            c = dict(e["cm_j1728"])
            c["p"] = p
            c["variant"] = "j1728"
            cm_entries.append(c)

    matches = []
    for o in ord_entries:
        for c in cm_entries:
            if o["N"] == c["N"] and o["tau"] == c["tau"]:
                matches.append({
                    "p_ord": o["p"], "A_ord": o["A"], "B_ord": o["B"],
                    "p_cm": c["p"], "A_cm": c["A"], "B_cm": c["B"],
                    "cm_variant": c["variant"],
                    "N": o["N"], "tau": o["tau"],
                    "same_prime": o["p"] == c["p"],
                })
    same_prime = [m for m in matches if m["same_prime"]]
    cross_prime = [m for m in matches if not m["same_prime"]]
    return {
        "num_ord_entries": len(ord_entries),
        "num_cm_entries": len(cm_entries),
        "total_matches": len(matches),
        "same_prime_matches": same_prime,
        "cross_prime_matches": cross_prime,
    }


def measure_transversal_cell(m64, cell, ntuples, cache, budget_deadline=None):
    """Fresh transversal ("fixed" arm only, per the frozen no-re-run of the
    tautological dual-convention control) Stage 1/2 measurement for one
    matched-(N,tau) cell, generalized to allow the ordinary curve and the
    CM curve to sit at different primes (the cross-prime case). Caches
    per-curve measurements keyed by (role, p) since a curve at a given p is
    uniquely determined and its transversal draw depends only on
    (domain, label, p, role, draw_index, counter) -- NOT on which partner
    curve it is being compared to in a given cell -- so re-measuring the
    same curve for two different cells is deterministic and identical;
    caching avoids redundant recomputation without changing any result."""
    p_ord, A_ord, B_ord = cell["p_ord"], cell["A_ord"], cell["B_ord"]
    p_cm, A_cm, B_cm = cell["p_cm"], cell["A_cm"], cell["B_cm"]
    N, tau = cell["N"], cell["tau"]
    variant = cell["cm_variant"]

    def get_measurement(cache_key, p, A, B, role_str, j_val):
        key = (cache_key, p)
        if key in cache:
            return cache[key]
        fb = m64.build_factor_base(A, B, p)
        if fb["size"] < 3:
            raise RuntimeError(f"factor base too small (size={fb['size']}) at p={p}, role={cache_key}")
        # measure_curve's internal seed role tag is curve["role"]+str(curve.get("j")),
        # matching EXP-MONO-64aaa4's own convention exactly (curve_ord j=None,
        # curve_cm j=cm_variant), so cm_j0 and cm_j1728 at the same p never
        # share a seed stream.
        curve = {"A": A, "B": B, "p": p, "role": role_str, "j": j_val}
        m = m64.measure_curve(curve, fb, ntuples, "fixed", budget_deadline=budget_deadline)
        cache[key] = m
        return m

    m_ord = get_measurement("ord", p_ord, A_ord, B_ord, "ord", None)
    m_cm = get_measurement(("cm", variant), p_cm, A_cm, B_cm, "cm", variant)

    predicted = m64.predicted_rate(tau, N)
    se = m64.binomial_se_pairs(tau, N, ntuples)
    expected_pairs = predicted * ntuples

    def se_dev(m):
        if se == 0:
            return 0.0
        return (m["total_pairs_colliding"] - expected_pairs) / se

    a = m_ord["tuples_with_collision"]
    b_ = m_ord["ntuples"] - a
    c = m_cm["tuples_with_collision"]
    d = m_cm["ntuples"] - c
    odds_ratio, pvalue = m64.fisher_exact_2x2(a, b_, c, d)

    return {
        "p_ord": p_ord, "p_cm": p_cm, "cm_variant": variant,
        "N": N, "tau": tau, "same_prime": p_ord == p_cm,
        "predicted_rate": predicted, "se_pairs_per_20000": se,
        "ord": {
            "observed_total_pairs_colliding": m_ord["total_pairs_colliding"],
            "observed_rate_pairs_per_tuple": m_ord["rate_pairs_per_tuple"],
            "observed_rate_any_collision": m_ord["rate_any_collision"],
            "se_deviation": se_dev(m_ord),
        },
        "cm": {
            "observed_total_pairs_colliding": m_cm["total_pairs_colliding"],
            "observed_rate_pairs_per_tuple": m_cm["rate_pairs_per_tuple"],
            "observed_rate_any_collision": m_cm["rate_any_collision"],
            "se_deviation": se_dev(m_cm),
        },
        "fisher_exact": {
            "table": {"ord_collision": a, "ord_no_collision": b_,
                      "cm_collision": c, "cm_no_collision": d},
            "odds_ratio": odds_ratio,
            "p_value": pvalue,
            "significant_at_0.05": bool(pvalue < 0.05),
        },
    }


def main():
    t_start = time.time()
    hard_deadline = t_start + 3600
    part_b_soft_deadline = t_start + 3000  # leaves buffer under the 3600s wall-clock budget

    result = {
        "run": "RUN-MONO-cb905d-1",
        "seed": SEED,
        "status": None,
        "stage0": {},
        "part_a": {},
        "part_b": {},
        "anomalies": [],
        "timing": {},
    }

    m64 = load_m64()  # m64.DOMAIN == "EXP-MONO-64aaa4/v1" here

    with open(EXP64_TRANSCRIPT) as f:
        transcript = json.load(f)
    with open(EXP64_RAW_RESULT) as f:
        raw64 = json.load(f)

    # ---------------- STAGE 0 ----------------
    s0 = stage0_enumerate(transcript)
    result["stage0"] = {
        "num_ord_entries": s0["num_ord_entries"],
        "num_cm_entries": s0["num_cm_entries"],
        "total_matches": s0["total_matches"],
        "same_prime_count": len(s0["same_prime_matches"]),
        "cross_prime_count": len(s0["cross_prime_matches"]),
        "same_prime_matches": s0["same_prime_matches"],
    }
    # Sanity check: p=617 recovered exactly as the sole same-prime match.
    same_prime_ps = sorted(m["p_ord"] for m in s0["same_prime_matches"])
    sole_same_prime_ok = (same_prime_ps == [617])
    result["stage0"]["sole_same_prime_match_is_617"] = sole_same_prime_ok
    if not sole_same_prime_ok:
        result["anomalies"].append({
            "type": "stage0_sanity_check_failed",
            "detail": f"Expected the sole same-prime match to be p=617; found {same_prime_ps}.",
        })

    # ---------------- PART A ----------------
    part_a = {}

    # Stopping rule: re-derive the p=617 curves under EXP-MONO-64aaa4's OWN
    # domain (unchanged, "EXP-MONO-64aaa4/v1") and require an EXACT match
    # against the archived transcript before proceeding.
    archived_ord = raw64["stage1"]["primary"]["construction_transcript"]["ord"]
    archived_cm = raw64["stage1"]["primary"]["construction_transcript"]["cm"]
    rederived_ord = m64.construct_ordinary(617)
    rederived_cm = m64.construct_cm_j1728(617)

    ord_match = (rederived_ord["A"] == archived_ord["A"] and
                 rederived_ord["B"] == archived_ord["B"] and
                 rederived_ord["N"] == archived_ord["N"] and
                 rederived_ord["tau"] == archived_ord["tau"])
    cm_match = (rederived_cm["A"] == archived_cm["A"] and
                rederived_cm["B"] == archived_cm["B"] and
                rederived_cm["N"] == archived_cm["N"] and
                rederived_cm["tau"] == archived_cm["tau"])

    part_a["curve_rederivation_check"] = {
        "ord_match": ord_match, "cm_match": cm_match,
        "rederived_ord": {k: rederived_ord[k] for k in ("A", "B", "N", "tau")},
        "archived_ord": {k: archived_ord[k] for k in ("A", "B", "N", "tau")},
        "rederived_cm": {k: rederived_cm[k] for k in ("A", "B", "N", "tau")},
        "archived_cm": {k: archived_cm[k] for k in ("A", "B", "N", "tau")},
    }

    if not (ord_match and cm_match):
        result["status"] = "failed_infrastructure"
        result["part_a"] = part_a
        result["part_a"]["disposition"] = (
            "STOPPING RULE TRIGGERED: re-derived p=617 curve(s) do not match "
            "EXP-MONO-64aaa4's own archived transcript exactly. Reported as "
            "failed_infrastructure per the frozen contract; NOT proceeding "
            "with a silently-different curve. No mathematical evidence."
        )
        result["timing"]["total_seconds"] = time.time() - t_start
        return result

    # From here on, switch to this contract's OWN domain for every NEW draw
    # (Part A's group-uniform arm, Part B's fresh transversal draws).
    m64.DOMAIN = CB_DOMAIN

    # Part A transversal arm: REUSED DIRECTLY from EXP-MONO-64aaa4's own
    # archived raw-result.json. Not re-measured. Dual-convention (fixed vs
    # random) proven tautological and identical in that record; "fixed" is
    # used as the transversal figure, with "random" noted as identical.
    arm64 = raw64["stage1"]["primary"]["per_curve_arm"]
    part_a["transversal_arm_reused_from"] = str(
        EXP64_RAW_RESULT.relative_to(REPO_ROOT)
    )
    part_a["transversal"] = {
        "ord": {
            "rate_pairs_per_tuple_fixed": arm64["ord_fixed"]["observed_rate_pairs_per_tuple"],
            "rate_pairs_per_tuple_random": arm64["ord_random"]["observed_rate_pairs_per_tuple"],
            "identical_fixed_random": (
                arm64["ord_fixed"]["observed_rate_pairs_per_tuple"]
                == arm64["ord_random"]["observed_rate_pairs_per_tuple"]
            ),
            "rate_pairs_per_tuple": arm64["ord_fixed"]["observed_rate_pairs_per_tuple"],
        },
        "cm": {
            "rate_pairs_per_tuple_fixed": arm64["cm_fixed"]["observed_rate_pairs_per_tuple"],
            "rate_pairs_per_tuple_random": arm64["cm_random"]["observed_rate_pairs_per_tuple"],
            "identical_fixed_random": (
                arm64["cm_fixed"]["observed_rate_pairs_per_tuple"]
                == arm64["cm_random"]["observed_rate_pairs_per_tuple"]
            ),
            "rate_pairs_per_tuple": arm64["cm_fixed"]["observed_rate_pairs_per_tuple"],
        },
    }

    # Part A group-uniform arm: NEW, 20000 fresh draws per curve.
    curve_ord_617 = {"A": archived_ord["A"], "B": archived_ord["B"], "p": 617, "role": "ord", "j": None}
    curve_cm_617 = {"A": archived_cm["A"], "B": archived_cm["B"], "p": 617, "role": "cm", "j": "j1728"}

    gu_ord = measure_group_uniform(m64, curve_ord_617, NTUPLES, budget_deadline=hard_deadline - 60)
    gu_cm = measure_group_uniform(m64, curve_cm_617, NTUPLES, budget_deadline=hard_deadline - 60)

    part_a["group_uniform"] = {
        "ord": gu_ord,
        "cm": gu_cm,
    }

    # P1, P2: group-uniform / transversal ratio, each curve, on rate_pairs_per_tuple (D)
    ord_transversal_rate = part_a["transversal"]["ord"]["rate_pairs_per_tuple"]
    cm_transversal_rate = part_a["transversal"]["cm"]["rate_pairs_per_tuple"]
    P1 = gu_ord["rate_pairs_per_tuple"] / ord_transversal_rate if ord_transversal_rate > 0 else None
    P2 = gu_cm["rate_pairs_per_tuple"] / cm_transversal_rate if cm_transversal_rate > 0 else None

    obj6_lo, obj6_hi = 1.84, 2.08
    part_a["metrics"] = {
        "P1_ord_group_uniform_over_transversal_ratio": P1,
        "P2_cm_group_uniform_over_transversal_ratio": P2,
        "obj6_prior_range": [obj6_lo, obj6_hi],
        "obj6_prior_source": "experiments/EXP-MONO-12ce1c/reviews/red-team/red-team-report.yaml OBJ-6 (measured 1.84-2.08x at m=4)",
        "P1_in_obj6_range": (P1 is not None and obj6_lo <= P1 <= obj6_hi),
        "P2_in_obj6_range": (P2 is not None and obj6_lo <= P2 <= obj6_hi),
    }
    if not (part_a["metrics"]["P1_in_obj6_range"] and part_a["metrics"]["P2_in_obj6_range"]):
        result["anomalies"].append({
            "type": "obj6_effect_reproduction_check",
            "detail": (
                f"P1={P1}, P2={P2} vs OBJ-6 prior range [{obj6_lo},{obj6_hi}]. "
                "Reported PROMINENTLY per the falsification_criterion/stopping_rules: "
                "at least one curve's group-uniform/transversal ratio fell outside "
                "the previously-measured 1.84-2.08x range."
            ),
        })

    # P3: direct comparison of P1 and P2 (headline result)
    ratio_of_ratios = (P1 / P2) if (P1 is not None and P2 is not None and P2 != 0) else None
    a_gu = gu_ord["tuples_with_collision"]
    b_gu = gu_ord["ntuples"] - a_gu
    c_gu = gu_cm["tuples_with_collision"]
    d_gu = gu_cm["ntuples"] - c_gu
    gu_odds_ratio, gu_pvalue = m64.fisher_exact_2x2(a_gu, b_gu, c_gu, d_gu)

    part_a["P3_headline_comparison"] = {
        "ratio_of_ratios_P1_over_P2": ratio_of_ratios,
        "group_uniform_fisher_exact_ord_vs_cm": {
            "table": {"ord_collision": a_gu, "ord_no_collision": b_gu,
                      "cm_collision": c_gu, "cm_no_collision": d_gu},
            "odds_ratio": gu_odds_ratio,
            "p_value": gu_pvalue,
            "significant_at_0.05": bool(gu_pvalue < 0.05),
        },
        "note": (
            "Headline result per stage_2_part_a. Two-sided, genuinely open per "
            "preregistered_prediction: agreement (ratio near 1, p >= 0.05) reads "
            "as (N,tau)-determined; material disagreement (ratio far from 1, "
            "p < 0.05) reads as endomorphism-ring-linked. This script reports "
            "the comparison statistics only; it does NOT declare either reading."
        ),
    }

    result["part_a"] = part_a

    # ---------------- PART B ----------------
    part_b = {}
    cross_matches = s0["cross_prime_matches"]

    # Deterministic order fixed BEFORE any Part B result is observed:
    # smallest-p-pair-sum first, tie-broken by (p_ord, p_cm, cm_variant).
    ordered_cells = sorted(
        cross_matches,
        key=lambda m: (m["p_ord"] + m["p_cm"], m["p_ord"], m["p_cm"], m["cm_variant"]),
    )
    part_b["ordering_rule"] = "smallest (p_ord + p_cm) first; ties broken by (p_ord, p_cm, cm_variant)"
    part_b["total_cross_prime_cells_found"] = len(ordered_cells)

    # The p=617 same-prime cell is reused directly from EXP-MONO-64aaa4's
    # own archived result -- never re-measured.
    reused_617 = raw64["stage2"]["primary"]["fixed"]
    part_b["p617_same_prime_cell_reused"] = {
        "p": 617, "N": 580, "tau": 4, "cm_variant": "j1728",
        "source": "experiments/EXP-MONO-64aaa4/runs/RUN-MONO-64aaa4-1/raw-result.json stage2.primary.fixed",
        "fisher_exact": reused_617,
        "se_deviation_cm": (681 - 620.6896551724138) / 24.849128585098583,
        "se_deviation_ord": (613 - 620.6896551724138) / 24.849128585098583,
    }

    measured_cells = []
    measurement_errors = []
    stopped_on_budget = False
    cache = {}

    for cell in ordered_cells:
        if time.time() > part_b_soft_deadline:
            stopped_on_budget = True
            break
        try:
            r = measure_transversal_cell(m64, cell, NTUPLES, cache, budget_deadline=hard_deadline - 60)
            measured_cells.append(r)
        except (RuntimeError, TimeoutError) as e:
            measurement_errors.append({
                "cell": {"p_ord": cell["p_ord"], "p_cm": cell["p_cm"], "cm_variant": cell["cm_variant"],
                         "N": cell["N"], "tau": cell["tau"]},
                "error_type": type(e).__name__,
                "message": str(e),
            })

    part_b["measured_count"] = len(measured_cells)
    part_b["measurement_error_count"] = len(measurement_errors)
    part_b["measurement_errors"] = measurement_errors
    part_b["found_count"] = len(ordered_cells)
    part_b["stopped_on_budget_guard"] = stopped_on_budget
    part_b["cells"] = measured_cells

    # P5/P6: distribution summary, INCLUDING the reused p=617 cell as one
    # more point in the distribution (it is a matched-(N,tau) cell like any
    # other; it is simply not RE-measured here).
    all_pvalues = [c["fisher_exact"]["p_value"] for c in measured_cells] + [reused_617["p_value"]]
    all_se_devs = []
    for c in measured_cells:
        all_se_devs.append(c["ord"]["se_deviation"])
        all_se_devs.append(c["cm"]["se_deviation"])
    all_se_devs.append(part_b["p617_same_prime_cell_reused"]["se_deviation_ord"])
    all_se_devs.append(part_b["p617_same_prime_cell_reused"]["se_deviation_cm"])

    n_dist = len(all_pvalues)
    n_below_0_1 = sum(1 for pv in all_pvalues if pv < 0.1)
    n_below_0_05 = sum(1 for pv in all_pvalues if pv < 0.05)
    n_se_dev_over_2 = sum(1 for d in all_se_devs if abs(d) > 2.0)

    p617_pvalue = reused_617["p_value"]
    rank_le = sum(1 for pv in all_pvalues if pv <= p617_pvalue)
    part_b["P5_P6_distribution_summary"] = {
        "note": (
            "EXPLORATORY CONTEXT ONLY. Field/characteristic confound disclosed: "
            f"{part_b['found_count'] - 1 if part_b['found_count'] else 0} of these "
            "cells (all but the reused p=617 same-prime cell) compare curves over "
            "DIFFERENT prime fields. This is NOT N independent replications of "
            "Part A's clean same-field question; it is a distribution for context "
            "only, per the frozen contract's own scoping."
        ),
        "n_cells_in_distribution": n_dist,
        "n_cells_p_lt_0.1": n_below_0_1,
        "n_cells_p_lt_0.05": n_below_0_05,
        "n_single_curve_se_deviations_over_2": n_se_dev_over_2,
        "n_curve_measurements_in_se_distribution": len(all_se_devs),
        "p617_own_p_value": p617_pvalue,
        "p617_own_p_value_rank_among_all_cells_le": rank_le,
        "p617_own_p_value_rank_out_of": n_dist,
        "p617_se_deviation_cm": part_b["p617_same_prime_cell_reused"]["se_deviation_cm"],
    }

    result["part_b"] = part_b
    result["status"] = "completed_valid"
    result["timing"]["total_seconds"] = time.time() - t_start
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports ru_maxrss in bytes; Linux reports it in KiB.
    result["timing"]["peak_rss_bytes"] = peak_rss * 1024 if sys.platform != "darwin" else peak_rss
    return result


if __name__ == "__main__":
    try:
        res = main()
        print(json.dumps(res, indent=2))
        if res.get("status") == "failed_infrastructure":
            sys.exit(3)
    except TimeoutError as e:
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": "TimeoutError", "message": str(e)}, indent=2))
        sys.exit(2)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "infrastructure_or_integrity_failure",
                           "error": type(e).__name__, "message": str(e),
                           "traceback": traceback.format_exc()}, indent=2))
        sys.exit(1)

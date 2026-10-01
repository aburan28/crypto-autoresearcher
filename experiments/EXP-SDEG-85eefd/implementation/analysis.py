"""C-6 metrics and C-7 outcome mapping. Unit-tested on synthetic data only.

Input: a list of per-(query, backend) records with keys
  fixture, L, seed, q, deck, query_id, backend, member (oracle, None if the
  query was stopped), status ('ok' | 'watchdog_stop'), W, W_full, W_triple,
  and optionally sub_degree (B1) / elim_degree (B2).

Protocol v3 (AMD-20260928-7ce387) work quantities, all amortized:
  W        PRIMARY, decision cost: work up to the first verified hit in the
           lexicographic triple order; non-members pay full enumeration (OQ-4).
  W_full   secondary: full enumeration for every query.
  W_triple W minus B1's per-query fixed specialization at x(R) (OQ-1); equal
           to W for B0. Outcome A must pass on both W and W_triple.
rho_c uses the primary W. "Non-increasing or flat" (OQ-9): each per-size
median of log W / log q may exceed the previous size's by at most FLAT_TOL.

beta_work: OLS slope of log(stat_W) on log q over L = 8, 16, 32, where stat
is the median or the maximum ("worst") of W over the pooled queries of the
three seeds at that L, and the abscissa is the mean log q over those
queries. Classes: successful (oracle member), unsuccessful (oracle
non-member) and all; watchdog-stopped queries enter only 'all', with W at the
stop as a lower bound (flagged). 95% CIs: percentile bootstrap, 2000
resamples, queries resampled with replacement within each (fixture, deck)
cell after class filtering, numpy PCG64 seeded from SHA256 of
'EXP-SDEG-85eefd/v2|bootstrap' (label unchanged in v3; one fresh generator per metric so every CI is
reproducible on its own).
"""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

import labels

GATE = 0.30
FLAT_TOL = 0.02
WORK_KEYS = {"primary": "W", "full": "W_full", "triple": "W_triple"}
CALIBRATION = (0.5, 0.7)
N_BOOT = 2000
BOOT_LABEL = labels.lab(labels.FROZEN_NS, "bootstrap")
CLASSES = ("successful", "unsuccessful", "all")
STATS = ("median", "worst")


def _filter(records, backend=None, deck=None, cls="all"):
    out = []
    for r in records:
        if backend is not None and r["backend"] != backend:
            continue
        if deck is not None and r["deck"] != deck:
            continue
        if cls == "successful" and not (r["status"] == "ok" and r["member"] is True):
            continue
        if cls == "unsuccessful" and not (r["status"] == "ok" and r["member"] is False):
            continue
        out.append(r)
    return out


def _stat(values, stat):
    if stat == "median":
        return float(np.median(values))
    if stat == "worst":
        return float(np.max(values))
    raise ValueError(stat)


def ols_slope(xs, ys) -> float:
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    xm = x.mean()
    return float(((x - xm) * (y - y.mean())).sum() / ((x - xm) ** 2).sum())


def _per_L(recs, key, stat):
    byL = defaultdict(list)
    for r in recs:
        byL[r["L"]].append(r)
    pts = {}
    for L, rs in sorted(byL.items()):
        vals = [r[key] for r in rs]
        pts[L] = (float(np.mean([math.log(r["q"]) for r in rs])), _stat(vals, stat), len(rs))
    return pts


def per_size_beta(recs, key) -> dict:
    """Per-size beta estimate: median over the pooled queries at L of
    log W / log q (None where some W <= 0)."""
    byL = defaultdict(list)
    for r in recs:
        byL[r["L"]].append(r)
    out = {}
    for L, rs in sorted(byL.items()):
        if any(r[key] <= 0 for r in rs):
            out[L] = None
        else:
            out[L] = float(np.median([math.log(r[key]) / math.log(r["q"]) for r in rs]))
    return out


def _beta_from_points(pts):
    if len(pts) < 2:
        return None, "fewer than two sizes"
    if any(v <= 0 for _, v, _ in pts.values()):
        return None, "non-positive statistic (log undefined)"
    xs = [x for x, _, _ in pts.values()]
    ys = [math.log(v) for _, v, _ in pts.values()]
    return ols_slope(xs, ys), None


def beta(records, key, stat, backend=None, deck=None, cls="all", n_boot=N_BOOT,
         boot_label=BOOT_LABEL) -> dict:
    recs = [r for r in _filter(records, backend, deck, cls) if r.get(key) is not None]
    pts = _per_L(recs, key, stat)
    psb = per_size_beta(recs, key)
    point, why = _beta_from_points(pts)
    out = {"backend": backend, "deck": deck, "class": cls, "stat": stat, "quantity": key,
           "point": point, "undefined_reason": why,
           "per_L": {str(L): {"mean_log_q": x, "value": v, "n": n,
                              "median_logW_over_logq": psb.get(L)}
                      for L, (x, v, n) in pts.items()},
           "sizes": sorted(pts), "contains_lower_bounds": any(r["status"] != "ok" for r in recs),
           "ci95": None}
    if point is None or n_boot <= 0:
        return out
    cells = defaultdict(list)
    for r in recs:
        cells[(r["fixture"], r["deck"])].append(r)
    cell_list = [cells[k] for k in sorted(cells)]
    rng = np.random.Generator(np.random.PCG64(labels.rng_seed(boot_label)))
    boots = []
    for _ in range(n_boot):
        res = []
        for c in cell_list:
            idx = rng.integers(0, len(c), size=len(c))
            res.extend(c[i] for i in idx)
        b, _ = _beta_from_points(_per_L(res, key, stat))
        if b is not None:
            boots.append(b)
    if boots:
        out["ci95"] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
        out["n_boot_valid"] = len(boots)
    return out


def per_cell(records, backend) -> list:
    cells = defaultdict(list)
    for r in _filter(records, backend):
        cells[(r["fixture"], r["L"], r["deck"])].append(r)
    out = []
    for (fxid, L, deck), rs in sorted(cells.items()):
        scored = [r for r in rs if r["status"] == "ok"]
        succ = [r["W"] for r in scored if r["member"]]
        allw = [r["W"] for r in rs]
        fullw = [r["W_full"] for r in rs if r.get("W_full") is not None]
        out.append({"fixture": fxid, "L": L, "deck": deck, "n": len(rs), "n_scored": len(scored),
                    "P_success": (sum(1 for r in scored if r["member"]) / len(scored)) if scored else None,
                    "median_W_all": float(np.median(allw)) if allw else None,
                    "median_W_full_all": float(np.median(fullw)) if fullw else None,
                    "median_W_successful": float(np.median(succ)) if succ else None,
                    "rho_c": (float(np.median(succ)) / float(np.median(allw))) if succ and allw else None})
    return out


def rho_c_pooled(records, backend, deck) -> dict:
    out = {}
    byL = defaultdict(list)
    for r in _filter(records, backend, deck):
        byL[r["L"]].append(r)
    for L, rs in sorted(byL.items()):
        succ = [r["W"] for r in rs if r["status"] == "ok" and r["member"]]
        allw = [r["W"] for r in rs]
        out[str(L)] = (float(np.median(succ)) / float(np.median(allw))) if succ else None
    return out


def compute_metrics(records, decks=("interval_x", "subgroup_x", "random_x"),
                    control_deck="progression", n_boot=N_BOOT) -> dict:
    m = {"work_quantities": dict(WORK_KEYS), "beta_work": {}, "beta_work_full": {},
         "beta_work_triple": {}, "beta_elim": {}, "beta_sub": {}, "cells": {}, "rho_c": {}}
    for be in ("B0", "B1"):
        for mk, key in (("beta_work", "W"), ("beta_work_full", "W_full")):
            m[mk][be] = {d: {c: {s: beta(records, key, s, be, d, c, n_boot) for s in STATS}
                             for c in CLASSES} for d in decks}
        m["cells"][be] = per_cell(records, be)
        m["rho_c"][be] = {d: rho_c_pooled(records, be, d) for d in decks}
    m["beta_work_triple"]["B1"] = {d: {c: {s: beta(records, "W_triple", s, "B1", d, c, n_boot)
                                           for s in STATS} for c in CLASSES} for d in decks}
    for d in decks + (control_deck,):
        m["beta_elim"][d] = beta(records, "elim_degree", "median", "B2", d, "all", n_boot)
        m["beta_sub"][d] = {c: beta(records, "sub_degree", "median", "B1", d, c, n_boot)
                            for c in CLASSES}
    return m


def _medians_nonincreasing(bw_entry, tol=FLAT_TOL) -> bool | None:
    """OQ-9 ruling: per-size median of log W / log q may exceed the previous
    size's by at most tol."""
    per = bw_entry["per_L"]
    if len(per) < 3:
        return None
    vals = [per[k]["median_logW_over_logq"] for k in sorted(per, key=int)]
    if any(v is None for v in vals):
        return None
    return all(vals[i + 1] <= vals[i] + tol for i in range(len(vals) - 1))


def _lt(x, y):
    return None if x is None or y is None else x < y


def outcome(metrics, oracle_agreement: float, witnesses_verified: bool, deck="interval_x",
            null_deck="random_x", control_deck="progression") -> dict:
    """C-7 mapping. Returns every condition and the outcome label."""
    bw = metrics["beta_work"]
    b1w = bw["B1"][deck]["all"]["worst"]
    b1tw = metrics["beta_work_triple"]["B1"][deck]["all"]["worst"]
    b1m = bw["B1"][deck]["all"]["median"]
    b1null = bw["B1"][null_deck]["all"]["worst"]
    b0m = bw["B0"][deck]["all"]["median"]
    b0w = bw["B0"][deck]["all"]["worst"]
    ci_hi = lambda e: e["ci95"][1] if e.get("ci95") else None  # noqa: E731
    ci_lo = lambda e: e["ci95"][0] if e.get("ci95") else None  # noqa: E731
    cal = b0m["point"] is not None and CALIBRATION[0] <= b0m["point"] <= CALIBRATION[1]
    cond_A = {
        "B1_all_worst_upper_ci_lt_gate": _lt(ci_hi(b1w), GATE),
        "B1_triple_all_worst_upper_ci_lt_gate": _lt(ci_hi(b1tw), GATE),
        "B1_medians_nonincreasing_in_L": _medians_nonincreasing(b1m),
        "B1_below_null_deck_beta": _lt(b1w["point"], b1null["point"]),
        "B0_calibration_in_range": cal,
        "oracle_agreement_100pct": oracle_agreement == 1.0,
        "every_witness_verified": bool(witnesses_verified),
    }
    lo_m, lo_w = ci_lo(b1m), ci_lo(b1w)
    cond_B = {
        "B1_all_median_lower_ci_ge_gate": None if lo_m is None else lo_m >= GATE,
        "B1_all_worst_lower_ci_ge_gate": None if lo_w is None else lo_w >= GATE,
        "B0_calibration_in_range": cal,
    }
    elim = metrics["beta_elim"].get(control_deck, {})
    progression_ok = elim.get("point") is not None and elim["point"] < GATE
    known_false_B0_passes_A = bool(_lt(ci_hi(b0w), GATE)) and bool(
        _medians_nonincreasing(bw["B0"][deck]["all"]["median"]))
    defects = []
    if oracle_agreement != 1.0:
        defects.append("B0/B1/oracle disagreement")
    if not witnesses_verified:
        defects.append("unverified witness")
    if not progression_ok:
        defects.append("progression control: beta_elim not < 0.30")
    if known_false_B0_passes_A:
        defects.append("known-false gate: B0 passes outcome-A beta criteria (meter broken)")
    if defects:
        label = "procedure_defect"
    elif not cal:
        label = "inconclusive"
    elif all(v is True for v in cond_A.values()):
        label = "A"
    elif all(v is True for v in cond_B.values()):
        label = "B"
    else:
        label = "inconclusive"
    return {"outcome": label, "conditions_A": cond_A, "conditions_B": cond_B,
            "B1_all_worst_beta_total": b1w["point"], "B1_all_worst_beta_triple": b1tw["point"],
            "flat_tolerance": FLAT_TOL,
            "calibration_B0_median_beta": b0m["point"], "progression_beta_elim": elim.get("point"),
            "known_false_B0_passes_A": known_false_B0_passes_A, "procedure_defects": defects,
            "forbidden_reading": "beta_sub or successful-subset-only beta_work below 0.30 is NOT outcome A"}

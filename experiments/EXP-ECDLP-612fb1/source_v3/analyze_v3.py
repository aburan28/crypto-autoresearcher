"""STAGE 3C analysis for the v2-to-v3 amendment, Section 4.

Pools the ten STAGE 3A / STAGE 3B measurement runs into the four declared
tables, compares STAGE 3A against the committed v2 a-scan, computes the
stratified-by-seed BCa bootstrap 95% CI on each pooled margin, and emits the
analysis run's THIRTEEN declared artifacts:

  command.txt  manifest.yaml  environment.json  raw-result.json  summary.json
  stdout.log   stderr.log     cost_table.json
  g3_verdict_table.json  decay_table.json  null_table.json
  proves_too_much_table.json  stage3a_vs_ascan_comparison.json

No basin_histogram.json.gz: STAGE 3C enumerates nothing.

The G3 verdict table is computed and emitted BEFORE every other block, in
stdout and in summary.json, mirroring v2's frozen gate ordering.  This module
writes NO interpretive line at all: it reports verdicts as the amendment
defines them and stops there.

Observations only.  Certificate kind: none.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
RUNS_DIR = os.path.join(EXP_DIR, "runs")
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
EXP_ID = "EXP-ECDLP-612fb1"
AMENDMENT = "experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml"

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import g3_predicate as G            # noqa: E402
import run_stage3 as R3             # noqa: E402  (provenance helpers, shared wrapper conventions)

SEEDS = list(G.SEED_SET)
A_GRID = list(G.A_GRID)
R_GRID = list(G.R_GRID)
STAGE_RUNS = {
    "3A": [f"RUN-ECDLP-612fb1-v3-rep20-s{s}" for s in SEEDS],
    "3B": [f"RUN-ECDLP-612fb1-v3-g3x24-s{s}" for s in SEEDS],
}
ASCAN_RUNS = [f"RUN-ECDLP-612fb1-v2-ascan-s{s}" for s in SEEDS]

# Declared, frozen-in-this-file analysis constants (reported as explicit
# fields in g3_verdict_table.json, per the amendment's required note).
BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED = 20260907
CI_ALPHA = 0.05


# ---------------------------------------------------------------------------
# BCa bootstrap (no scipy on this host: the two normal functions are local)
# ---------------------------------------------------------------------------

def norm_cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF: Acklam's rational approximation refined by
    one Halley step against erfc, giving full double precision."""
    if not 0.0 < p < 1.0:
        return float("-inf") if p <= 0.0 else float("inf")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    else:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    e = 0.5 * math.erfc(-x / math.sqrt(2)) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def _bca(values: np.ndarray, boots: np.ndarray, jack: np.ndarray,
         theta_hat: float, alpha: float, n_boot: int) -> dict:
    prop = float((boots < theta_hat).mean())
    clamped = False
    if prop <= 0.0:
        prop, clamped = 1.0 / (2 * n_boot), True
    elif prop >= 1.0:
        prop, clamped = 1.0 - 1.0 / (2 * n_boot), True
    z0 = norm_ppf(prop)
    jbar = float(jack.mean())
    num = float(((jbar - jack) ** 3).sum())
    den = 6.0 * float((((jbar - jack) ** 2).sum()) ** 1.5)
    acc = (num / den) if den != 0.0 else 0.0
    out = {}
    for tag, z in (("lo", norm_ppf(alpha / 2)), ("hi", norm_ppf(1 - alpha / 2))):
        adj = z0 + (z0 + z) / (1 - acc * (z0 + z)) if (1 - acc * (z0 + z)) != 0 else z0 + z
        out[tag] = float(np.quantile(boots, min(max(norm_cdf(adj), 0.0), 1.0)))
    return {"point": float(theta_hat), "ci_low": out["lo"], "ci_high": out["hi"],
            "ci_level": 1 - alpha, "method": "BCa (bias-corrected and accelerated)",
            "bootstrap_resamples": n_boot, "bootstrap_seed": BOOTSTRAP_SEED,
            "z0": z0, "acceleration": acc,
            "z0_proportion_clamped": clamped,
            "percentile_ci_low": float(np.quantile(boots, alpha / 2)),
            "percentile_ci_high": float(np.quantile(boots, 1 - alpha / 2))}


def bca_mean(values, n_boot: int = BOOTSTRAP_RESAMPLES, alpha: float = CI_ALPHA) -> dict:
    """BCa CI for the mean of the per-seed values of one cell.

    RESAMPLING UNIT: the SEED.  The amendment asks for a "stratified-by-seed
    BCa bootstrap 95% CI" on each pooled margin.  Each cell holds exactly one
    margin per seed, so resampling WITHIN a seed stratum is degenerate (it
    returns that seed's single value every time and yields zero width); the
    non-degenerate reading is that the seed is the independent replicate and
    the resample is over the five seed-level values.  This implementation
    choice is disclosed here, in IMPLEMENTATION.md, and in the execution
    report; it affects only the CI, never a verdict or a pass_count, which are
    computed from the per-seed margins directly.

    With n = 5 the CI is coarse by construction: at most 5^5 = 3125 distinct
    resamples exist, so the interval is a discrete object and its endpoints
    can only fall on attainable resample means.  Stated as a property of the
    estimator, not as an interpretation.
    """
    v = np.asarray(values, dtype=np.float64)
    n = len(v)
    if n == 0:
        return {"point": None, "note": "no values"}
    theta_hat = float(v.mean())
    if n == 1:
        return {"point": theta_hat, "ci_low": theta_hat, "ci_high": theta_hat,
                "ci_level": 1 - alpha, "method": "degenerate (n = 1)",
                "bootstrap_resamples": 0, "bootstrap_seed": BOOTSTRAP_SEED,
                "degenerate": True}
    if float(v.std()) == 0.0:
        return {"point": theta_hat, "ci_low": theta_hat, "ci_high": theta_hat,
                "ci_level": 1 - alpha, "method": "degenerate (zero sample variance)",
                "bootstrap_resamples": 0, "bootstrap_seed": BOOTSTRAP_SEED,
                "degenerate": True}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = v[idx].mean(axis=1)
    jack = np.asarray([np.delete(v, i).mean() for i in range(n)])
    out = _bca(v, boots, jack, theta_hat, alpha, n_boot)
    out["n_seeds"] = n
    out["max_distinct_resamples"] = int(n ** n)
    out["degenerate"] = False
    return out


def bca_ratio_of_means(num_values, den_values, n_boot: int = BOOTSTRAP_RESAMPLES,
                       alpha: float = CI_ALPHA) -> dict:
    """BCa CI for mean(margin) / mean(margin_null), resampled PAIRED BY SEED so
    a resample never mixes one seed's margin with another seed's null."""
    a = np.asarray(num_values, dtype=np.float64)
    b = np.asarray(den_values, dtype=np.float64)
    n = len(a)
    if n == 0 or float(b.mean()) == 0.0:
        return {"point": None, "note": "denominator mean is zero or no values"}
    theta_hat = float(a.mean() / b.mean())
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, n, size=(n_boot, n))
    den_boot = b[idx].mean(axis=1)
    ok = den_boot != 0.0
    boots = np.where(ok, a[idx].mean(axis=1) / np.where(ok, den_boot, 1.0), np.nan)
    zero_den = int((~ok).sum())
    boots = boots[ok]
    jack = np.asarray([np.delete(a, i).mean() / np.delete(b, i).mean()
                       if np.delete(b, i).mean() != 0 else np.nan for i in range(n)])
    if np.isnan(jack).any() or len(boots) == 0:
        return {"point": theta_hat, "ci_low": None, "ci_high": None,
                "note": "jackknife or bootstrap denominator hit zero; CI not computed",
                "bootstrap_resamples": n_boot, "bootstrap_seed": BOOTSTRAP_SEED}
    out = _bca(a, boots, jack, theta_hat, alpha, len(boots))
    out["n_seeds"] = n
    out["bootstrap_resamples_with_zero_denominator_dropped"] = zero_den
    return out


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def sha256_of(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_runs() -> dict:
    """Load the ten measurement runs.  A run that is absent, or whose manifest
    does not say completed_valid, is recorded as such and its cells are NOT
    pooled -- never silently treated as a zero or as a negative."""
    import yaml
    loaded, status = {}, {}
    for stage, run_ids in STAGE_RUNS.items():
        for seed, rid in zip(SEEDS, run_ids):
            d = os.path.join(RUNS_DIR, rid)
            rec = {"run_id": rid, "stage": stage, "seed": seed,
                   "present": os.path.isdir(d), "pooled": False,
                   "validity_status": None, "invalid_reason": None}
            if not rec["present"]:
                rec["invalid_reason"] = "run directory absent: NOT RUN (never a negative result)"
                status[rid] = rec
                continue
            mp, rp = os.path.join(d, "manifest.yaml"), os.path.join(d, "raw-result.json")
            if os.path.exists(mp):
                man = yaml.safe_load(open(mp))["run"]
                rec["validity_status"] = man.get("status")
                rec["invalid_reason"] = man.get("result", {}).get("invalid_reason")
                rec["wall_seconds"] = man.get("timing", {}).get("wall_seconds")
                rec["peak_rss_bytes"] = man.get("resources", {}).get("peak_rss_bytes")
                rec["cpu_seconds"] = man.get("resources", {}).get("cpu_seconds")
                rec["commit"] = man.get("code", {}).get("commit")
            if os.path.exists(rp):
                rec["raw_result_sha256"] = sha256_of(rp)
                if rec["validity_status"] == "completed_valid":
                    loaded[(stage, seed)] = json.load(open(rp))
                    rec["pooled"] = True
            status[rid] = rec
    return {"data": loaded, "status": status}


def load_ascan() -> dict:
    out = {}
    for seed, rid in zip(SEEDS, ASCAN_RUNS):
        p = os.path.join(RUNS_DIR, rid, "raw-result.json")
        if os.path.exists(p):
            out[seed] = {"run_id": rid, "sha256": sha256_of(p),
                         "cells": json.load(open(p))["cells"]}
    return out


def cell_of(raw: dict, a: float, r: int) -> dict:
    return raw["cells"][f"a={a:.6f}"]["by_r"][str(r)]


# ---------------------------------------------------------------------------
# the four declared tables
# ---------------------------------------------------------------------------

def stage_meta(raw: dict) -> dict:
    p = raw["params"]
    return {"N": p["N"], "n_bits": p["n_bits"], "T": p["T"], "T_sel": p["T_sel"]}


def build_g3_verdict_table(data: dict) -> dict:
    rows = []
    for stage in ("3A", "3B"):
        present = [s for s in SEEDS if (stage, s) in data]
        if not present:
            continue
        meta = stage_meta(data[(stage, present[0])])
        for a in A_GRID:
            for r in R_GRID:
                per_seed = []
                for s in present:
                    m = cell_of(data[(stage, s)], a, r)
                    per_seed.append({
                        "seed": s,
                        "margin": m["margin"],
                        "top_share_T_sel": m["top_share_T_sel"],
                        "static_cov": m["static_cov"],
                        "g3": m["g3"],
                    })
                margins = [x["margin"] for x in per_seed]
                verdict = G.g3_cell_verdict(margins)
                rows.append({
                    # verdict FIRST, before any other field in the row
                    "verdict": verdict["verdict"],
                    "pass_count": verdict["pass_count"],
                    "seed_count": verdict["seed_count"],
                    "threshold": verdict["threshold"],
                    "stage": stage, **meta, "a": a, "r": r,
                    "seeds_pooled": present,
                    "seeds_missing": [s for s in SEEDS if s not in present],
                    "per_seed": per_seed,
                    "pooled_margin": bca_mean(margins),
                    "pooled_top_share_T_sel_mean": float(np.mean([x["top_share_T_sel"] for x in per_seed])),
                    "pooled_static_cov_mean": float(np.mean([x["static_cov"] for x in per_seed])),
                })
    return {
        "table": "g3_verdict_table",
        "contract": f"{AMENDMENT} Section 3 (g3_predicate) and Section 7 (metrics.primary)",
        "gate_ordering_note": ("verdict and pass_count are the first fields of every row; this "
                               "file contains no interpretive line at all"),
        "predicate": ("margin_s = TopShare_s(T_sel) - StaticCov_s(T, r); g3_s = [margin_s >= 0]; "
                      "the cell PASSES iff pass_count >= 4 of 5 seeds"),
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_method": "BCa, stratified by seed (resampling unit = seed; see analyze_v3.bca_mean)",
        "ci_level": 1 - CI_ALPHA,
        "rows": rows,
    }


def build_decay_table(data: dict) -> dict:
    rows, cells = [], []
    for stage in ("3A", "3B"):
        present = [s for s in SEEDS if (stage, s) in data]
        if not present:
            continue
        meta = stage_meta(data[(stage, present[0])])
        for a in A_GRID:
            for s in present:
                m_by_r = {r: cell_of(data[(stage, s)], a, r)["margin"] for r in R_GRID}
                seq = [m_by_r[r] for r in R_GRID]
                rows.append({
                    "stage": stage, **meta, "a": a, "seed": s,
                    "margin_by_r": {str(r): m_by_r[r] for r in R_GRID},
                    "monotone_non_increasing_in_r": bool(
                        all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1))),
                    "strictly_decreasing_in_r": bool(
                        all(seq[i] > seq[i + 1] for i in range(len(seq) - 1))),
                    "differences": {f"r={R_GRID[i]}->r={R_GRID[i + 1]}": seq[i + 1] - seq[i]
                                    for i in range(len(seq) - 1)},
                })
            verdicts = {}
            for r in R_GRID:
                margins = [cell_of(data[(stage, s)], a, r)["margin"] for s in present]
                verdicts[r] = G.g3_cell_verdict(margins)
            first_fail = next((r for r in R_GRID if verdicts[r]["verdict"] == "FAIL"), None)
            cells.append({
                "stage": stage, **meta, "a": a,
                "verdict_by_r": {str(r): verdicts[r]["verdict"] for r in R_GRID},
                "pass_count_by_r": {str(r): verdicts[r]["pass_count"] for r in R_GRID},
                "first_r_at_which_verdict_is_FAIL": first_fail,
                "all_seeds_monotone_non_increasing": bool(all(
                    row["monotone_non_increasing_in_r"] for row in rows
                    if row["stage"] == stage and row["a"] == a)),
                "pooled_margin_by_r": {str(r): bca_mean(
                    [cell_of(data[(stage, s)], a, r)["margin"] for s in present]) for r in R_GRID},
            })
    return {
        "table": "decay_table",
        "contract": f"{AMENDMENT} Section 5 control DECAY_G3",
        "requirement": ("margin_s must be NON-INCREASING in r at every (N, a, s), and the cell "
                        "verdict must go FAIL by r = 8 at every tested a"),
        "artifact_tell": ("a margin that does not decay in r is the canonical artifact signature; "
                          "this file records the readings and draws no conclusion from them"),
        "per_seed_rows": rows,
        "per_cell": cells,
    }


def build_null_table(data: dict) -> dict:
    rows, cells = [], []
    for stage in ("3A", "3B"):
        present = [s for s in SEEDS if (stage, s) in data]
        if not present:
            continue
        meta = stage_meta(data[(stage, present[0])])
        for a in A_GRID:
            for r in R_GRID:
                margins, nulls = [], []
                for s in present:
                    m = cell_of(data[(stage, s)], a, r)
                    rows.append({
                        "stage": stage, **meta, "a": a, "r": r, "seed": s,
                        "margin": m["margin"],
                        "margin_null": m["margin_null"],
                        "static_cov": m["static_cov"],
                        "static_cov_null": m["static_cov_null"],
                        "margin_over_margin_null": m["margin_over_margin_null"],
                        "margin_null_greater_than_margin": bool(m["margin_null"] > m["margin"]),
                        "null_b_set_identical": m["null_b_set_identical"],
                        "null_b_set_identical_signal_path": m["null_b_set_identical_signal"],
                        "null_b_set_identical_null_a_path": m["null_b_set_identical_null_a"],
                    })
                    margins.append(m["margin"])
                    nulls.append(m["margin_null"])
                cells.append({
                    "stage": stage, **meta, "a": a, "r": r,
                    "seeds_pooled": present,
                    "pooled_margin": bca_mean(margins),
                    "pooled_margin_null": bca_mean(nulls),
                    "ratio_of_pooled_means_margin_over_margin_null":
                        bca_ratio_of_means(margins, nulls),
                    "seeds_with_margin_null_greater_than_margin":
                        int(sum(1 for m, n in zip(margins, nulls) if n > m)),
                    "null_b_identical_all_seeds": bool(all(
                        cell_of(data[(stage, s)], a, r)["null_b_set_identical"] for s in present)),
                })
    return {
        "table": "null_table",
        "contract": f"{AMENDMENT} Section 5 controls NULL_A_G3 and NULL_B_G3",
        "null_a_construction": ("on the IDENTICAL pool draw, the pool's own multiset of (S_d, h_d) "
                                "evidence pairs is permuted by the stream seeded 300 + s, then "
                                "STATIC_NULL(T)_r is selected by the SAME weight and tie-break"),
        "null_a_predicted_signature": ("margin_null > margin at essentially every (a, r, s); the "
                                       "artifact tell is margin_null NOT materially larger"),
        "null_b_requirement": "the two frozen v2 selection code paths select identical DP sets",
        "per_seed_rows": rows,
        "per_cell": cells,
    }


def build_proves_too_much_table(data: dict) -> dict:
    """Section 6's known-false objects, exactly as declared there."""
    objects = []

    def cell_block(stage, a, r, label, why, required):
        present = [s for s in SEEDS if (stage, s) in data]
        if not present:
            return None
        meta = stage_meta(data[(stage, present[0])])
        per_seed = [{"seed": s, "margin": cell_of(data[(stage, s)], a, r)["margin"],
                     "g3": cell_of(data[(stage, s)], a, r)["g3"]} for s in present]
        margins = [x["margin"] for x in per_seed]
        v = G.g3_cell_verdict(margins)
        return {
            "verdict": v["verdict"], "pass_count": v["pass_count"],
            "required_outcome": required, "outcome_as_required": v["verdict"] == "FAIL",
            "object": label, "why_conclusion_is_known_false": why,
            "stage": stage, **meta, "a": a, "r": r,
            "per_seed": per_seed,
            "margin_of_failure_closest_seed_to_zero": max(margins),
            "seeds_short_of_the_4_of_5_bar": G.G3_PASS_THRESHOLD - v["pass_count"],
        }

    for a, why in ((0.1875, "EV-ECDLP-2e9680 reports a = 3/16 CONFIRMED G3-INFEASIBLE at exactly "
                            "this cell under both readings (blind 0/5, production 0/5)"),
                   (0.25, "EV-ECDLP-60e266 measured the exact top-T/2 basin share BELOW STATIC(T)'s "
                          "exact coverage in 10 of 10 exactly enumerated seeds; EV-ECDLP-2e9680 "
                          "independently reproduced 0/5 under both readings")):
        b = cell_block("3B", a, 2, f"a = {a}, T_sel = T/2, r = 2, N = 2^24, frozen v2 instrument",
                       why, "G3 FAIL, pass_count <= 3")
        if b:
            objects.append(b)
    for stage in ("3A", "3B"):
        for a in A_GRID:
            b = cell_block(stage, a, 8, f"a = {a} at r = 8 ({'N = 2^20' if stage == '3A' else 'N = 2^24'})",
                           "at N = 2^20 the committed a-scan gives 0/5 at r = 8 for all four a values",
                           "G3 FAIL at r = 8 at every a")
            if b:
                objects.append(b)

    fired_rows = [o for o in objects if o["verdict"] == "PASS"]
    return {
        "table": "proves_too_much_table",
        "contract": f"{AMENDMENT} Section 6 (proves_too_much)",
        "fired": bool(fired_rows),
        "fired_objects": [o["object"] for o in fired_rows],
        "fired_semantics": ("fired = true iff G3 PASSES at any known-false object of Section 6. "
                            "A firing is a STOPPING CONDITION FOR INTERPRETATION, not a negative "
                            "result and not an invalidation; it is reported explicitly and first, "
                            "and the Coordinator adjudicates it."),
        "named_risk_flagged_in_advance_by_the_amendment": (
            "a = 3/16 is the thin one: EV-ECDLP-2e9680's post-seal diagnostic scored it "
            "pass_by_weight = 2/5 at N = 2^24 under the w(d) rule this predicate binds, against "
            "the >= 4/5 bar; the amendment requires a 4/5 or 5/5 reading there to be reported as a "
            "firing and not softened"),
        "objects": objects,
    }


def build_stage3a_vs_ascan(data: dict, ascan: dict) -> dict:
    """STAGE 3A against the committed v2 a-scan, per (a, r = 2, seed)."""
    def rows_for(r):
        out = []
        for a in A_GRID:
            for s in SEEDS:
                if ("3A", s) not in data or s not in ascan:
                    continue
                mine = cell_of(data[("3A", s)], a, r)
                ac = ascan[s]["cells"][f"a={a:.6f}"]
                ref_margin = ac["top_share"]["T/2"] - ac["static_by_r"][str(r)]
                diff = mine["margin"] - ref_margin
                out.append({
                    "a": a, "r": r, "seed": s,
                    "stage3a_margin": mine["margin"],
                    "committed_ascan_margin": ref_margin,
                    "absolute_difference": abs(diff),
                    "absolute_difference_6dp": round(abs(diff), 6),
                    "absolute_difference_12dp": round(abs(diff), 12),
                    "bitwise_identical": bool(mine["margin"] == ref_margin),
                    "stage3a_top_share_T_sel": mine["top_share_T_sel"],
                    "committed_ascan_top_share_T_sel": ac["top_share"]["T/2"],
                    "top_share_bitwise_identical": bool(
                        mine["top_share_T_sel"] == ac["top_share"]["T/2"]),
                    "stage3a_static_cov": mine["static_cov"],
                    "committed_ascan_static_cov": ac["static_by_r"][str(r)],
                    "static_cov_bitwise_identical": bool(
                        mine["static_cov"] == ac["static_by_r"][str(r)]),
                    "committed_ascan_run_id": ascan[s]["run_id"],
                })
        return out

    rows = rows_for(2)
    extra = {str(r): rows_for(r) for r in (4, 8)}
    all_rows = rows + [x for v in extra.values() for x in v]
    max_abs = max((x["absolute_difference"] for x in rows), default=None)
    return {
        "table": "stage3a_vs_ascan_comparison",
        "contract": f"{AMENDMENT} Section 7 metrics.primary (STAGE 3A only) and "
                    f"invalidation_rules (instrument discrepancy)",
        "declared_scope": "per (a, r = 2, seed): the STAGE 3A margin, the committed "
                          "RUN-ECDLP-612fb1-v2-ascan-s* margin, and the absolute difference "
                          "to at least 6 decimal places",
        "agreement_tolerance": 1e-12,
        "max_absolute_difference_r2": max_abs,
        "all_r2_rows_bitwise_identical": bool(all(x["bitwise_identical"] for x in rows)) if rows else None,
        "all_r2_rows_within_tolerance": bool(all(x["absolute_difference"] <= 1e-12 for x in rows)) if rows else None,
        "agreement_statement": (
            "AGREE bitwise at every (a, r = 2, seed)" if rows and all(x["bitwise_identical"] for x in rows)
            else ("AGREE within 1e-12 at every (a, r = 2, seed) but not bitwise"
                  if rows and all(x["absolute_difference"] <= 1e-12 for x in rows)
                  else "DISAGREE at one or more (a, r = 2, seed): an INSTRUMENT DISCREPANCY, "
                       "not a negative result about the hypothesis")),
        "rows": rows,
        "additional_rows_r4_r8": extra,
        "additional_rows_note": ("r = 4 and r = 8 are beyond the contract's declared comparison "
                                 "scope (which is r = 2) and are reported here because the "
                                 "amendment's DECAY_G3 preregistered expectation is read off the "
                                 "same committed a-scan at those r; they are kept out of `rows` "
                                 "so the declared set stays exact"),
        "max_absolute_difference_all_r": max((x["absolute_difference"] for x in all_rows), default=None),
    }


def build_preregistered_comparison(data: dict) -> dict:
    """STAGE 3A's frozen preregistered expectation, compared exactly as written.

    The expectation is FROZEN in the amendment (stage_plan.STAGE_3A
    `preregistered_expectation`) and is reproduced here verbatim as numbers.
    It may fail; a failure is reported, never absorbed and never re-scored.
    """
    frozen = {
        0.0625: {"pass_count": 5, "margins": [0.019553, 0.012215, 0.023987, 0.016334, 0.009157]},
        0.125: {"pass_count": 4, "margins": [0.003183, -0.001996, 0.010345, 0.004992, 0.007094]},
        0.1875: {"pass_count": 1, "margins": [0.018691, -0.009538, -0.015742, -0.008542, -0.003351]},
        0.25: {"pass_count": 0, "margins": [-0.014133, -0.003534, -0.053352, -0.019899, -0.023048]},
    }
    rows = []
    for a, exp in frozen.items():
        present = [s for s in SEEDS if ("3A", s) in data]
        if not present:
            continue
        margins = [cell_of(data[("3A", s)], a, 2)["margin"] for s in present]
        v = G.g3_cell_verdict(margins)
        rows.append({
            "a": a, "r": 2, "N": 1048576,
            "predicted_pass_count": exp["pass_count"],
            "observed_pass_count": v["pass_count"],
            "pass_count_matches": v["pass_count"] == exp["pass_count"],
            "per_seed": [{"seed": s, "predicted_margin_6dp": exp["margins"][s - 1],
                          "observed_margin": m,
                          "observed_margin_6dp": round(m, 6),
                          "matches_to_6dp": round(m, 6) == exp["margins"][s - 1]}
                         for s, m in zip(present, margins)],
        })
    return {
        "note": ("the amendment's FROZEN preregistered expectation for STAGE 3A, compared exactly "
                 "as written to at least 6 decimal places; this is a prediction that may fail"),
        "source": f"{AMENDMENT} stage_plan.STAGE_3A.preregistered_expectation",
        "all_pass_counts_match": bool(all(r["pass_count_matches"] for r in rows)) if rows else None,
        "all_margins_match_to_6dp": bool(all(p["matches_to_6dp"] for r in rows for p in r["per_seed"]))
                                    if rows else None,
        "rows": rows,
    }


def build_determinism_check(data: dict) -> dict:
    """Re-run one cell from scratch, in this process, at the same seed, and
    compare to the value stored in the committed run record.

    The contract's seeds are declared and fixed, so the same seed must give
    the same result.  The recomputation uses the same code path; agreement is
    evidence of determinism (same seed -> same number), not of correctness.
    A second, stronger check -- a full re-execution of a whole run and a
    sha256 comparison of its raw-result.json -- is recorded in the task's
    execution_report.yaml, because its output directory cannot live inside the
    declared artifact set.
    """
    checks = []
    for stage, n_bits, a, r, seed in (("3A", 20, 0.0625, 2, 1), ("3B", 24, 0.125, 2, 3)):
        if (stage, seed) not in data:
            checks.append({"stage": stage, "seed": seed, "status": "NOT RUN: source run absent"})
            continue
        stored = cell_of(data[(stage, seed)], a, r)
        P = G.make_params(n_bits, a, seed)
        basins = G.exact_basins(P)
        redo = G.measure_cell(P, basins, r)
        del basins
        checks.append({
            "stage": stage, "n_bits": n_bits, "a": a, "r": r, "seed": seed,
            "stored_margin": stored["margin"], "recomputed_margin": redo["margin"],
            "margin_bitwise_identical": bool(stored["margin"] == redo["margin"]),
            "stored_top_share_T_sel": stored["top_share_T_sel"],
            "recomputed_top_share_T_sel": redo["top_share_T_sel"],
            "stored_static_cov": stored["static_cov"],
            "recomputed_static_cov": redo["static_cov"],
            "stored_table_hash": stored["table_hash"],
            "recomputed_table_hash": redo["table_hash"],
            "table_hash_identical": bool(stored["table_hash"] == redo["table_hash"]),
            "stored_margin_null": stored["margin_null"],
            "recomputed_margin_null": redo["margin_null"],
            "margin_null_bitwise_identical": bool(stored["margin_null"] == redo["margin_null"]),
        })
    ok = [c for c in checks if "margin_bitwise_identical" in c]
    return {"method": "in-process recomputation of one cell per stage at the declared seed",
            "all_identical": bool(ok and all(c["margin_bitwise_identical"] and c["table_hash_identical"]
                                             and c["margin_null_bitwise_identical"] for c in ok)),
            "checks": checks}


def build_integrity(status: dict, data: dict) -> dict:
    """ROUND_ZERO_AND_SEED_INTEGRITY across the ten runs."""
    per_stage = {}
    for stage, run_ids in STAGE_RUNS.items():
        seeds_present = sorted(s for s in SEEDS if (stage, s) in data)
        per_stage[stage] = {
            "run_ids": run_ids,
            "seeds_expected": SEEDS,
            "seeds_pooled": seeds_present,
            "seeds_missing": [s for s in SEEDS if s not in seeds_present],
            "duplicate_seeds": sorted({s for s in seeds_present if seeds_present.count(s) > 1}),
            "exactly_five_distinct_seeds": seeds_present == SEEDS,
        }
    exceed, nullb = [], []
    for (stage, seed), raw in data.items():
        ch = raw.get("checks", {})
        if not ch.get("exact_coverage_non_exceedance", {}).get("passed"):
            exceed.append({"stage": stage, "seed": seed,
                           "violations": ch["exact_coverage_non_exceedance"]["violations"]})
        if not ch.get("null_b_set_identity", {}).get("passed"):
            nullb.append({"stage": stage, "seed": seed,
                          "violations": ch["null_b_set_identity"]["violations"]})
    return {
        "per_stage_seed_integrity": per_stage,
        "exact_coverage_non_exceedance": {
            "requirement": "StaticCov(T,r) and StaticCovNull(T,r) never exceed TopShare(T)",
            "violations": exceed, "passed": not exceed},
        "null_b_set_identity": {
            "requirement": "the two frozen v2 selection code paths select identical DP sets",
            "violations": nullb, "passed": not nullb},
        "run_status": status,
        "runs_pooled": sorted(r["run_id"] for r in status.values() if r["pooled"]),
        "runs_not_pooled": sorted(r["run_id"] for r in status.values() if not r["pooled"]),
    }


# ---------------------------------------------------------------------------
# CHILD
# ---------------------------------------------------------------------------

def run_child(outdir: str) -> int:
    t0 = time.time()
    runs = load_runs()
    data, status = runs["data"], runs["status"]
    ascan = load_ascan()

    g3 = build_g3_verdict_table(data)

    # gate ordering: the verdict table is printed before every other block
    print("[g3_verdict_table]", flush=True)
    for row in g3["rows"]:
        print(f"  N=2^{row['n_bits']} a={row['a']:.6f} r={row['r']} T_sel={row['T_sel']}: "
              f"{row['verdict']} pass_count={row['pass_count']}/{row['seed_count']} "
              f"margins=" + ",".join(f"{p['margin']:+.9f}" for p in row["per_seed"]) +
              f" pooled={row['pooled_margin']['point']:+.9f} "
              f"CI=[{row['pooled_margin'].get('ci_low', float('nan')):+.9f},"
              f"{row['pooled_margin'].get('ci_high', float('nan')):+.9f}]", flush=True)

    decay = build_decay_table(data)
    null = build_null_table(data)
    ptm = build_proves_too_much_table(data)
    cmp3a = build_stage3a_vs_ascan(data, ascan)
    prereg = build_preregistered_comparison(data)
    integrity = build_integrity(status, data)
    determinism = build_determinism_check(data)

    print(f"[proves_too_much] fired={ptm['fired']} objects={ptm['fired_objects']}", flush=True)
    print(f"[stage3a_vs_ascan] {cmp3a['agreement_statement']} "
          f"max_abs_diff_r2={cmp3a['max_absolute_difference_r2']}", flush=True)
    print(f"[preregistered] pass_counts_match={prereg['all_pass_counts_match']} "
          f"margins_match_6dp={prereg['all_margins_match_to_6dp']}", flush=True)
    print(f"[decay] " + json.dumps([{k: c[k] for k in
                                     ("stage", "a", "verdict_by_r", "first_r_at_which_verdict_is_FAIL",
                                      "all_seeds_monotone_non_increasing")}
                                    for c in decay["per_cell"]]), flush=True)
    print(f"[null_a] " + json.dumps([{"stage": c["stage"], "a": c["a"], "r": c["r"],
                                      "margin": c["pooled_margin"]["point"],
                                      "margin_null": c["pooled_margin_null"]["point"],
                                      "seeds_null_gt_signal": c["seeds_with_margin_null_greater_than_margin"]}
                                     for c in null["per_cell"]]), flush=True)
    print(f"[integrity] " + json.dumps({
        "seed_integrity": {k: v["exactly_five_distinct_seeds"] for k, v in
                           integrity["per_stage_seed_integrity"].items()},
        "exact_coverage_non_exceedance": integrity["exact_coverage_non_exceedance"]["passed"],
        "null_b_set_identity": integrity["null_b_set_identity"]["passed"],
        "runs_not_pooled": integrity["runs_not_pooled"]}), flush=True)
    print(f"[determinism] all_identical={determinism['all_identical']}", flush=True)

    for name, obj in (("g3_verdict_table.json", g3), ("decay_table.json", decay),
                      ("null_table.json", null), ("proves_too_much_table.json", ptm),
                      ("stage3a_vs_ascan_comparison.json", cmp3a)):
        with open(os.path.join(outdir, name), "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=False)

    raw = {
        "schema": "EXP-ECDLP-612fb1 v3 STAGE 3C analysis raw result",
        "certificate": {"kind": "none",
                        "note": "pooling and bootstrap only; nothing is solved or certified"},
        "params": {
            "stage": "3C", "amendment": AMENDMENT,
            "runs_pooled": integrity["runs_pooled"],
            "runs_not_pooled": integrity["runs_not_pooled"],
            "ascan_runs_read": [v["run_id"] for v in ascan.values()],
            "ascan_raw_result_sha256": {v["run_id"]: v["sha256"] for v in ascan.values()},
            "measurement_run_raw_result_sha256": {
                k: v.get("raw_result_sha256") for k, v in sorted(status.items())},
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "ci_level": 1 - CI_ALPHA,
            "seeds": SEEDS, "a_grid": A_GRID, "r_grid": R_GRID,
        },
        "g3_verdict_table": g3,
        "proves_too_much_table": ptm,
        "decay_table": decay,
        "null_table": null,
        "stage3a_vs_ascan_comparison": cmp3a,
        "preregistered_expectation_comparison": prereg,
        "integrity": integrity,
        "determinism_check": determinism,
    }
    with open(os.path.join(outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True)

    summary = {
        "g3_verdict_table": [
            {k: row[k] for k in ("verdict", "pass_count", "seed_count", "stage", "N", "a", "r",
                                 "T_sel", "per_seed", "pooled_margin")}
            for row in g3["rows"]],
        "proves_too_much_fired": ptm["fired"],
        "proves_too_much_fired_objects": ptm["fired_objects"],
        "stage3a_vs_ascan_agreement": cmp3a["agreement_statement"],
        "stage3a_max_absolute_difference_r2": cmp3a["max_absolute_difference_r2"],
        "preregistered_expectation_comparison": prereg,
        "decay_per_cell": decay["per_cell"],
        "null_per_cell": null["per_cell"],
        "integrity": integrity,
        "determinism_check": determinism,
        "certificate": {"kind": "none"},
        "params": raw["params"],
        "headline_metrics": {
            f"N=2^{row['n_bits']}|a={row['a']:.6f}|r={row['r']}": {
                "verdict": row["verdict"], "pass_count": row["pass_count"],
                "pooled_margin": row["pooled_margin"]["point"],
                "ci_low": row["pooled_margin"].get("ci_low"),
                "ci_high": row["pooled_margin"].get("ci_high"),
            } for row in g3["rows"]},
        "elapsed_seconds": round(time.time() - t0, 3),
    }
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=False)

    import yaml
    modeled, measured = {}, {}
    for stage in ("3A", "3B"):
        present = [s for s in SEEDS if (stage, s) in data]
        if not present:
            continue
        raw0 = data[(stage, present[0])]
        for a in A_GRID:
            c = raw0["cells"][f"a={a:.6f}"]
            modeled[f"{stage}|a={a:.6f}"] = {**c["modeled"],
                                             "formula": "W = sqrt(a*N/T); theta = 1/W; cap = ceil(8*W)",
                                             "N": raw0["params"]["N"], "T": raw0["params"]["T"],
                                             "T_sel": raw0["params"]["T_sel"]}
            for r in R_GRID:
                agg = [cell_of(data[(stage, s)], a, r) for s in present]
                measured[f"{stage}|a={a:.6f}|r={r}"] = {
                    "P_group_ops_mean": float(np.mean([x["pool"]["P_group_ops"] for x in agg])),
                    "P_over_sqrt_NT_mean": float(np.mean([x["pool"]["P_over_sqrt_NT"] for x in agg])),
                    "generating_walks_mean": float(np.mean([x["pool"]["generating_walks"] for x in agg])),
                    "capped_walk_fraction_mean": float(np.mean([x["pool"]["capped_walk_fraction"] for x in agg])),
                    "margin_mean": float(np.mean([x["margin"] for x in agg])),
                    "margin_null_mean": float(np.mean([x["margin_null"] for x in agg])),
                    "top_share_T_sel_mean": float(np.mean([x["top_share_T_sel"] for x in agg])),
                    "static_cov_mean": float(np.mean([x["static_cov"] for x in agg])),
                    "S_bits_oracle_T_sel_table": agg[0]["bits"]["S_bits_oracle_T_sel_table"],
                    "S_bits_static_T_table": agg[0]["bits"]["S_bits_static_T_table"],
                    "S_peak_bits_pool_working_storage": agg[0]["bits"]["S_peak_bits_pool_working_storage"],
                }
    cost = {
        "note": ("MEASURED and MODELED quantities are kept in separate blocks. W, theta and cap "
                 "are MODELED; every count, coverage, margin, bit count and resource measurement "
                 "is MEASURED."),
        "modeled": modeled,
        "measured": measured,
        "measured_run_resources": {
            rid: {"wall_seconds": r.get("wall_seconds"), "peak_rss_bytes": r.get("peak_rss_bytes"),
                  "cpu_seconds": r.get("cpu_seconds"), "validity_status": r.get("validity_status")}
            for rid, r in sorted(status.items())},
        "measured_analysis_elapsed_seconds": round(time.time() - t0, 3),
    }
    with open(os.path.join(outdir, "cost_table.json"), "w") as fh:
        json.dump(cost, fh, indent=1, sort_keys=True)

    print(f"[done] stage=3C elapsed={time.time() - t0:.2f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# PARENT
# ---------------------------------------------------------------------------

def validity(outdir: str) -> tuple:
    reasons = []
    for f in ("g3_verdict_table.json", "decay_table.json", "null_table.json",
              "proves_too_much_table.json", "stage3a_vs_ascan_comparison.json",
              "raw-result.json", "summary.json", "cost_table.json"):
        if not os.path.exists(os.path.join(outdir, f)):
            reasons.append(f"declared analysis artifact missing: {f}")
    if reasons:
        return False, "; ".join(reasons), {}
    s = json.load(open(os.path.join(outdir, "summary.json")))
    integ = s["integrity"]
    if not integ["exact_coverage_non_exceedance"]["passed"]:
        reasons.append("exact-coverage exceedance in a pooled run (invalidation rule 4)")
    if not integ["null_b_set_identity"]["passed"]:
        reasons.append("NULL_B_G3 selection-set difference in a pooled run (invalidation rule 5)")
    for stage, v in integ["per_stage_seed_integrity"].items():
        if not v["exactly_five_distinct_seeds"]:
            reasons.append(f"STAGE {stage} does not carry exactly five distinct seeds: "
                           f"missing {v['seeds_missing']} (invalidation rule 3)")
    return (len(reasons) == 0), ("; ".join(reasons) if reasons else None), s.get("headline_metrics", {})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--outdir")
    args = ap.parse_args()
    if args.child:
        return run_child(args.outdir)
    if not args.run_id:
        raise SystemExit("--run-id is required in wrapper mode")

    import resource
    outdir = os.path.join(RUNS_DIR, args.run_id)
    if os.path.exists(outdir):
        raise SystemExit(f"refusing to overwrite existing run directory {outdir} "
                         "(run records are immutable)")
    os.makedirs(outdir)

    cmd = [sys.executable, os.path.join(HERE, "analyze_v3.py"), "--child", "--outdir", outdir]
    rel = " ".join(c.replace(REPO + "/", "") for c in cmd)
    with open(os.path.join(outdir, "command.txt"), "w") as fh:
        fh.write(f"cd {REPO}\n"
                 f"OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 \\\n"
                 f"  timeout {R3.WALL_LIMIT}s {rel}\n"
                 f"# wrapper invocation that produced this run directory:\n"
                 f"# python3 experiments/EXP-ECDLP-612fb1/source_v3/analyze_v3.py "
                 f"--run-id {args.run_id}\n")

    gs = R3.git_state()
    envd = R3.environment()
    with open(os.path.join(outdir, "environment.json"), "w") as fh:
        json.dump({**envd, "git": gs, "source_sha256": R3.source_hashes(),
                   "wall_limit_seconds": R3.WALL_LIMIT,
                   "memory_limit_bytes": R3.MEM_LIMIT_BYTES}, fh, indent=1)

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", PYTHONHASHSEED="0")
    started = dt.datetime.now(dt.timezone.utc)
    t0 = time.monotonic()
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (R3.MEM_LIMIT_BYTES, R3.MEM_LIMIT_BYTES))

    status, failure, rc = "completed_valid", None, 0
    with open(os.path.join(outdir, "stdout.log"), "w") as so, \
         open(os.path.join(outdir, "stderr.log"), "w") as se:
        try:
            proc = subprocess.run(cmd, cwd=REPO, env=env, stdout=so, stderr=se,
                                  timeout=R3.WALL_LIMIT, preexec_fn=limits)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = None
            status = "failed_infrastructure"
            failure = (f"wall clock exceeded {R3.WALL_LIMIT} s (resource_exhaustion). NOT a result "
                       f"and NOT negative evidence (AGENTS.md core rule 5).")
    wall = time.monotonic() - t0
    finished = dt.datetime.now(dt.timezone.utc)
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak_rss = int(r1.ru_maxrss * 1024)
    cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
    if rc not in (0, None):
        status = "failed_infrastructure"
        failure = f"child exited with code {rc}. NOT a result (AGENTS.md core rule 5)."

    valid, reason, metrics = False, failure, {}
    if status == "completed_valid":
        valid, reason, metrics = validity(outdir)
        if not valid:
            status = "completed_invalid"
    if peak_rss > R3.MEM_LIMIT_BYTES:
        status, valid = "failed_infrastructure", False
        reason = f"peak RSS {peak_rss} B exceeded the {R3.MEM_LIMIT_BYTES} B ceiling."

    for missing, blank in (("raw-result.json", {}), ("summary.json", {}), ("cost_table.json", {}),
                           ("g3_verdict_table.json", {}), ("decay_table.json", {}),
                           ("null_table.json", {}), ("proves_too_much_table.json", {}),
                           ("stage3a_vs_ascan_comparison.json", {})):
        p = os.path.join(outdir, missing)
        if not os.path.exists(p):
            with open(p, "w") as fh:
                json.dump({**blank, "status": status,
                           "note": f"child produced no {missing}", "failure": failure}, fh, indent=1)

    failure_class = None
    if not valid:
        failure_class = ("resource_exhaustion" if rc is None or peak_rss > R3.MEM_LIMIT_BYTES
                         else "infrastructure_error" if status == "failed_infrastructure"
                         else "invalid_measurement")

    manifest = {"run": {
        "id": args.run_id, "experiment_id": EXP_ID, "amendment": AMENDMENT,
        "amendment_status_at_dispatch": "approved (committed on the working branch)",
        "stage": "3C", "stage_name": "analysis",
        "purpose": ("STAGE 3C: pool the ten measurement runs into the G3 verdict, decay, null and "
                    "proves-too-much tables; BCa bootstrap; a-scan comparison"),
        "status": status,
        "task_id": "TASK-20260907-aad514", "batch_id": "BATCH-8f3e86",
        "goal_id": "GOAL-ECDLP-bbc21f",
        "code": {
            "commit": gs["commit"], "branch": gs["branch"], "dirty": gs["dirty"],
            "dirty_tracked_files": gs["dirty_tracked_files"],
            "untracked_under_this_experiment": gs["untracked_under_this_experiment"],
            "command": open(os.path.join(outdir, "command.txt")).read().strip(),
            "source_path": "experiments/EXP-ECDLP-612fb1/source_v3/",
            "source_sha256": R3.source_hashes(),
            "bootstrap_code_location": ("experiments/EXP-ECDLP-612fb1/source_v3/analyze_v3.py "
                                        "(hash-pinned above; the bootstrap code is not a run "
                                        "artifact, per the amendment)"),
            "reuses_frozen": "experiments/EXP-ECDLP-612fb1/source_v2/instrument.py imported unchanged",
        },
        "inference": R3.inference_block(),
        "environment": envd,
        "inputs": {
            "curve_id": None, "seed": None,
            "seeds": {"bootstrap_seed": BOOTSTRAP_SEED, "measurement_seeds": SEEDS,
                      "note": "STAGE 3C draws no walk, pool or tie-break stream; its only "
                              "randomness is the declared bootstrap resampling seed"},
            "parameters": {"stage": "3C", "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                           "ci_level": 1 - CI_ALPHA, "a_grid": A_GRID, "r_grid": R_GRID},
            "input_runs": sorted(sum(STAGE_RUNS.values(), [])),
            "input_runs_read_only": sorted(ASCAN_RUNS),
        },
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(),
                   "wall_seconds": round(wall, 3), "timing_source": "wrapper monotonic clock",
                   "wall_limit_seconds": R3.WALL_LIMIT, "wall_within_limit": bool(wall <= R3.WALL_LIMIT)},
        "resources": {"peak_rss_bytes": peak_rss, "peak_rss_gib": round(peak_rss / (1 << 30), 4),
                      "cpu_seconds": round(cpu, 3), "memory_limit_bytes": R3.MEM_LIMIT_BYTES,
                      "peak_rss_within_limit": bool(peak_rss <= R3.MEM_LIMIT_BYTES),
                      "workers": R3.WORKERS,
                      "peak_rss_source": "resource.getrusage(RUSAGE_CHILDREN).ru_maxrss"},
        "result": {"metrics": metrics, "valid": valid, "validity_status": status,
                   "invalid_reason": reason, "failure_class": failure_class,
                   "certificate": {"kind": "none", "verified": None, "verifier": None,
                                   "note": "pooling and bootstrap only; nothing solved or certified"},
                   "interpretation": ("NONE. Observations only; the Coordinator interprets after "
                                      "independent review.")},
        "artifacts": {"command": "command.txt", "manifest": "manifest.yaml",
                      "environment": "environment.json", "raw_result": "raw-result.json",
                      "summary": "summary.json", "stdout": "stdout.log", "stderr": "stderr.log",
                      "cost_table": "cost_table.json",
                      "g3_verdict_table": "g3_verdict_table.json",
                      "decay_table": "decay_table.json", "null_table": "null_table.json",
                      "proves_too_much_table": "proves_too_much_table.json",
                      "stage3a_vs_ascan_comparison": "stage3a_vs_ascan_comparison.json"},
    }}
    import yaml
    with open(os.path.join(outdir, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, default_flow_style=False, width=100)
    print(f"{args.run_id}: {status} wall={wall:.2f}s cpu={cpu:.2f}s "
          f"peak_rss={peak_rss / (1 << 30):.3f}GiB" + (f" reason={reason}" if reason else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

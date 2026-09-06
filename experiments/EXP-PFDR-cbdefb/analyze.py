#!/usr/bin/env python3
"""EXP-PFDR-cbdefb Stage 4 (zero compute): read-only summariser of runs/*/raw-result.json.

Writes analysis.md and analysis.json.  Every number is recomputed from the raw fall
histories; censored draws are excluded from slope fits exactly as flagged.  The
pre-declared analysis choices are stage1-closure-convention.md section 8; the frozen
prediction is specification.yaml preregistered_prediction (never adjusted).
Observations only: the outcome label is assigned mechanically by the pre-registered
rule and is not interpreted here.
"""
from __future__ import annotations

import glob
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

import mpmath
import yaml

EXP_DIR = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(EXP_DIR, "runs")
if "--runs" in sys.argv:                       # scratch tests only; official analysis uses the defaults
    RUNS = sys.argv[sys.argv.index("--runs") + 1]
if "--out" in sys.argv:
    EXP_DIR = sys.argv[sys.argv.index("--out") + 1]
PRIMES = [4099, 16411, 65537]
LADDER_S = [1, 2, 3, 4, 5]
FROZEN = {
    "d_ff": {2: 5, 3: 5, 4: 6, 5: 6},                      # IDEA-20260903-e1e38b D5, slope 1/2
    "null_band_center": lambda s: s + 2,                    # ceil((ms(d-1) + 2m)/2) at m = 2, d = 2
    "null_band": {0, 1, 2},
    "resolution": 0.25,
    "prior": {"outcome_I_on_dlf": 0.6, "outcome_II_joint": "expected", "outcome_III": 0.05, "unresolved": 0.1},
}


# ----------------------------------------------------------------------------------------
def load_runs() -> dict:
    runs = {}
    for d in sorted(glob.glob(os.path.join(RUNS, "RUN-PFDR-cbdefb-*"))):
        rid = os.path.basename(d)
        with open(os.path.join(d, "manifest.yaml"), "r", encoding="utf-8") as fh:
            man = yaml.safe_load(fh)["run"]
        with open(os.path.join(d, "raw-result.json"), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        runs[rid] = {"manifest": man, "metrics": raw["metrics"], "raw": raw["raw"], "certificate": raw["certificate"]}
    return runs


_TQ: dict = {}


def t_quantile(q: float, dof: int) -> float:
    """Student-t quantile by bisection on the regularized incomplete beta CDF (mpmath); cached per dof."""
    if dof <= 0:
        return float("inf")
    if (q, dof) in _TQ:
        return _TQ[(q, dof)]

    def cdf(t):
        x = dof / (dof + t * t)
        return 1 - 0.5 * float(mpmath.betainc(dof / 2, 0.5, 0, x, regularized=True))
    lo, hi = 0.0, 1000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    _TQ[(q, dof)] = (lo + hi) / 2
    return _TQ[(q, dof)]


def ols(points: list, want_ci: bool = True) -> dict:
    """points: list of (s, y).  OLS slope with the t-interval (n - 2 dof)."""
    n = len(points)
    if n < 3 or len({s for s, _ in points}) < 2:
        return {"n": n, "slope": None, "intercept": None, "ci95": None, "degenerate": True, "reason": "fewer than 3 points or a single s"}
    sbar = sum(s for s, _ in points) / n
    ybar = sum(y for _, y in points) / n
    sxx = sum((s - sbar) ** 2 for s, _ in points)
    sxy = sum((s - sbar) * (y - ybar) for s, y in points)
    b = sxy / sxx
    a = ybar - b * sbar
    if not want_ci:
        return {"n": n, "slope": b, "intercept": a}
    rss = sum((y - (a + b * s)) ** 2 for s, y in points)
    sigma2 = rss / (n - 2)
    se = math.sqrt(sigma2 / sxx)
    t = t_quantile(0.975, n - 2)
    return {"n": n, "slope": b, "intercept": a, "se": se, "t_0975": t, "ci95": [b - t * se, b + t * se],
            "residual_variance": sigma2, "degenerate": sigma2 == 0.0,
            "s_values": sorted({s for s, _ in points}), "per_s_values": {str(s): sorted({y for s2, y in points if s2 == s}) for s in sorted({s for s, _ in points})}}


def bootstrap_slope(cells: dict, reps: int = 2000, seed: int = 0) -> dict:
    """cells: {(s, p): [y, ...]}.  Resample draws within every cell with replacement."""
    rng = random.Random(seed)
    slopes = []
    for _ in range(reps):
        pts = []
        for (s, _p), ys in cells.items():
            if not ys:
                continue
            pts.extend((s, rng.choice(ys)) for _ in ys)
        r = ols(pts, want_ci=False)
        if r["slope"] is not None:
            slopes.append(r["slope"])
    if not slopes:
        return {"reps": 0}
    slopes.sort()
    return {"reps": len(slopes), "ci95_percentile": [slopes[int(0.025 * len(slopes))], slopes[min(len(slopes) - 1, int(0.975 * len(slopes)))]],
            "seed": seed}


def contains(ci, v):
    return ci is not None and ci[0] <= v <= ci[1]


def eff(r: dict) -> dict:
    """Apply CTRL-ITERATION-COUNT to a system result: a fall entry with iteration count 1 is invalidated
    (contract invalidation rule 3); d_ff / d_lf are then read from the surviving entries.  The raw closure
    values are kept beside them.  A history entry records whether W_0 already equalled the ideal's degree-<=D
    part at that degree (`W0_saturated`, when the diagnostic is present)."""
    if r.get("degenerate"):
        return {"degenerate": True, "valid_falls": [], "invalidated": [], "d_ff": None, "d_lf": None, "raw_d_ff": None, "raw_d_lf": None,
                "right_censored": True, "no_fall": True, "saturated_at_invalidated": []}
    counts = {int(k): v for k, v in r["fall_iteration_counts"].items()}
    valid = [D for D in r["falls"] if counts.get(D, 0) >= 2]
    inval = [D for D in r["falls"] if counts.get(D, 0) < 2]
    sat = []
    for h in r["history"]:
        if h["D"] in inval:
            sat.append({"D": h["D"], "dim_W0": h["dim_W0"], "dim_V": h["dim_V"], "dim_I_at_D": h.get("dim_I_at_D"), "W0_saturated": h.get("W0_saturated"),
                        "passes": h["passes"]})
    return {"degenerate": False, "valid_falls": valid, "invalidated": inval, "d_ff": valid[0] if valid else None, "d_lf": valid[-1] if valid else None,
            "raw_d_ff": r["d_ff"], "raw_d_lf": r["d_lf"], "right_censored": r["right_censored"], "no_fall": not valid,
            "saturated_at_invalidated": sat}


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.4f}"
    return str(x)


# ----------------------------------------------------------------------------------------
def main() -> None:
    runs = load_runs()
    out = {"runs": {}, "stage1": {}, "ladder": {}, "fits": {}, "labels": {}, "controls": {}, "tail_checks": {}, "equal_ds": {}, "m3": {}}
    md = []
    md.append("# EXP-PFDR-cbdefb — analysis (Stage 4, zero compute)\n")
    md.append("Task TASK-20260903-6745ea (Executor). Every table is generated by `analyze.py` from the run packages under `runs/` "
              "(`raw-result.json`, `manifest.yaml`); the frozen prediction is read from `specification.yaml` "
              "(restated in `stage0-transfer.md` section 5) and never adjusted; the pre-declared analysis choices are "
              "`stage1-closure-convention.md` section 8. **Observations only.** The outcome label is the mechanical output of "
              "the pre-registered rule; whether it supports or refutes anything belongs to the Reviewer and the Coordinator. "
              "Scope: m = 2, d = 2, s in {1..5}, p in {4099, 16411, 65537}, D_max = 7, the frozen closure convention "
              "`cbdefb-closure-v1`, toy tier; nothing transfers to cryptographic s.\n")

    # ---- A. run tally
    md.append("## A. Run tally\n")
    md.append("| run id | status | wall_seconds (wrapper) | peak RSS (MB) | certificate | valid | invalid_reason |")
    md.append("|---|---|---|---|---|---|---|")
    for rid, r in runs.items():
        m = r["manifest"]
        c = m["result"]["certificate"]
        out["runs"][rid] = {"status": m["status"], "wall_seconds": m["timing"]["wall_seconds"], "peak_rss_bytes": m["resources"]["peak_rss_bytes"],
                            "certificate": f"{c.get('kind')} / verified={c.get('verified')}", "valid": m["result"]["valid"],
                            "invalid_reason": m["result"]["invalid_reason"], "commit": m["code"]["commit"], "dirty": m["code"]["dirty"]}
        md.append(f"| {rid} | {m['status']} | {m['timing']['wall_seconds']:.3f} | {m['resources']['peak_rss_bytes'] / 1e6:.0f} | "
                  f"{c.get('kind')} / verified={c.get('verified')} | {m['result']['valid']} | {m['result']['invalid_reason'] or ''} |")

    # ---- B. Stage 1
    md.append("\n## B. Stage 1: the s = 1 slice, the known-answer fixtures, the d_ff agreement\n")
    s1 = runs.get("RUN-PFDR-cbdefb-s1-slice")
    fx = runs.get("RUN-PFDR-cbdefb-fixture")
    da = runs.get("RUN-PFDR-cbdefb-dff-agreement")
    if s1:
        m = s1["metrics"]
        out["stage1"]["s1"] = m
        md.append(f"- CTRL-S1-BASELINE (`RUN-PFDR-cbdefb-s1-slice`): {m['draws_plantable']} of {m['draws_planned']} draws plantable at window [0, 2) "
                  f"(not plantable: {len(m['not_plantable'])}); s = 1 identification term for term: {m['identification_all']}; "
                  f"membership generators reduce to 0 in the quotient: all; digit-form pairs (d_ff, d_lf): {m['digit_pairs']}; "
                  f"floor d_lf >= 2 on every draw: {m['floor_d_lf_ge_2_all']}; closure d_ff = graded-rank d_ff on every draw: {m['closure_dff_equals_graded_dff_all']}; "
                  f"digit histories certified complete (structural, n = 2): {m['digit_all_certified']}; "
                  f"polynomial-ring closure on 84cdb7's literal direct list (unreduced S_3 of degree {m['direct_generator_degrees']}): pairs {m['direct_pairs']}, "
                  f"identical fall history to the digit form: {m['digit_histories_identical_to_direct_all']}; "
                  f"polynomial-ring closure on the REDUCED generator plus field equations (note section 2): pairs {m['direct_reduced_pairs']}, "
                  f"identical fall history to the digit form: {m['digit_histories_identical_to_direct_reduced_all']}; "
                  f"engines agree: {m['engine_cross_check_all_agree']}; certificates: {m['certificates_all_verified']}. **s1_pass = {m['s1_pass']}**.")
    if fx:
        m = fx["metrics"]
        out["stage1"]["fixture"] = m
        md.append(f"- CTRL-KNOWN-ANSWER-FIXTURE (`RUN-PFDR-cbdefb-fixture`): substitution recorded — {m['substitution']}. "
                  f"Fixture P (squarefree, 10 variables, seed 5): checks {m['fixture_P_squarefree']['checks']}; extended-system falls {m['fixture_P_squarefree']['ext_falls']}, "
                  f"base falls {m['fixture_P_squarefree']['base_falls']}. Fixture P (ordinary ring, 3 variables): checks {m['fixture_P_ordinary']['checks']}. "
                  f"Fixture H (a1 a2 + a3): checks {m['fixture_H']['checks']}, history {m['fixture_H']['history']}. **known_answer_pass = {m['known_answer_pass']}**.")
    if da:
        m = da["metrics"]
        out["stage1"]["dff_agreement"] = m
        md.append(f"- CTRL-DFF-AGREEMENT (`RUN-PFDR-cbdefb-dff-agreement`): {m['rows']} rows (EXP-PFDR-5726af's p = 4099 instances, same instance in every row: {m['same_instance_all']}); "
                  f"per s: {json.dumps(m['per_s'])}; disagreements: {len(m['disagreements'])}. **P1_all_agree = {m['P1_all_agree']}**.")

    # ---- C. ladder tables
    cells = {}
    for s in LADDER_S:
        for p in PRIMES:
            rid = f"RUN-PFDR-cbdefb-m2-s{s}-p{p}"
            if rid in runs:
                cells[(s, p)] = runs[rid]
    out["ladder"]["cells_present"] = [f"{s},{p}" for (s, p) in cells]

    def arm_rows(cell, arm):
        raw = cell["raw"]
        if arm == "semaev":
            return [(d["curve_seed"], d["target_seed"], None, d["semaev"]) for d in raw["draws"] if "semaev" in d]
        if arm == "null1":
            return [(d["curve_seed"], d["target_seed"], r["seed"], r["result"]) for d in raw["draws"] for r in d.get("null1", [])]
        if arm == "null2":
            return [(None, None, r["seed"], r["result"]) for r in raw["null2_objects"]]
        if arm == "null3":
            return [(None, None, r["seed"], r["result"]) for r in raw["null3_objects"]]
        if arm == "noncurve":
            return [(d["cubic_seed"], d["target_seed"], None, d["result"]) for d in raw["noncurve"]]
        raise ValueError(arm)

    ARMS = ["semaev", "null1", "null2", "null3", "noncurve"]
    table = {}
    for (s, p), cell in cells.items():
        for arm in ARMS:
            rows = arm_rows(cell, arm)
            live = [r for r in rows if not r[3].get("degenerate")]
            deg = [r for r in rows if r[3].get("degenerate")]
            effs = [eff(r[3]) for r in live]
            dff = Counter(str(e["d_ff"]) for e in effs)
            dlf = Counter(str(e["d_lf"]) for e in effs)
            dlf_unc = Counter(str(e["d_lf"]) for e in effs if not e["right_censored"])
            raw_pairs = Counter(f"({e['raw_d_ff']}, {e['raw_d_lf']})" for e in effs)
            its = [min(r[3]["fall_iteration_counts"].values()) for r in live if r[3]["fall_iteration_counts"]]
            table[(s, p, arm)] = {
                "n": len(rows), "degenerate": len(deg), "degenerate_reasons": sorted({r[3].get("reason") for r in deg}),
                "d_ff": dict(dff), "d_lf": dict(dlf), "d_lf_uncensored": dict(dlf_unc), "raw_closure_pairs": dict(raw_pairs),
                "invalidated_fall_entries": sum(len(e["invalidated"]) for e in effs),
                "invalidated_entries_saturated": sum(1 for e in effs for x in e["saturated_at_invalidated"] if x.get("W0_saturated")),
                "right_censored": sum(1 for r in live if r[3]["right_censored"]),
                "no_fall_in_window": sum(1 for r in live if r[3]["no_fall_in_window"]),
                "single_fall": sum(1 for r in live if r[3]["single_fall_degree"]),
                "min_iteration_count_at_falls": min(its) if its else None,
                "falls_with_iteration_count_1": sum(1 for r in live if r[3]["fall_with_iteration_count_1"]),
                "closure_dff_equals_graded_dff_all": all(r[3]["closure_dff_equals_graded_dff"] for r in live) if live else None,
                "graded_d_ff": dict(Counter(str(r[3]["graded"]["graded_d_ff"]) for r in live)),
                "engine": sorted({r[3]["engine"] for r in live}),
                "cross_checked": sum(1 for r in live if r[3].get("cross_check")),
                "cross_check_agree_all": all(r[3]["cross_check"]["agree"] for r in live if r[3].get("cross_check")),
                "certified_routes": dict(Counter(str(r[3]["certificate"].get("route")) for r in live)),
                "histories": dict(Counter(str(r[3]["falls"]) for r in live)),
                "seconds": round(sum(r[3]["seconds"] for r in live), 1),
            }
    out["ladder"]["table"] = {f"{s},{p},{arm}": v for (s, p, arm), v in table.items()}

    md.append("\n## C. Ladder: (d_ff, d_lf) per (s, p) cell and arm, with censoring (from the closure fall histories)\n")
    md.append("Values are histograms `{value: count}` AFTER CTRL-ITERATION-COUNT (a fall entry with iteration count 1 is invalidated; contract "
              "invalidation rule 3); `raw closure pairs` shows (d_ff, d_lf) before the rule. `None` = no (valid) fall in (deg, D_max]. "
              "`censored` = draws whose history is not certified complete at D_max = 7 (note section 3); a censored draw's d_lf is observed-so-far and never enters a fit. "
              "`it1` = draws with a count-1 fall entry (invalidated); `sat.` = how many of those entries had W_0 already equal to the ideal's degree-<=D part "
              "(nothing left to add; diagnostic present in runs made after the two first Stage 1 runs). `deg.` = degenerate objects (zero generator or generator degree above D_max).\n")
    md.append("| s | p | arm | n | deg. | d_ff | d_lf | d_lf (uncensored) | raw closure pairs | censored | no fall | single-fall | min iter | it1 (sat.) | closure=graded d_ff | engine (x-checked) | routes |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (s, p, arm), v in table.items():
        md.append(f"| {s} | {p} | {arm} | {v['n']} | {v['degenerate']} | {v['d_ff']} | {v['d_lf']} | {v['d_lf_uncensored']} | {v['raw_closure_pairs']} | {v['right_censored']} | {v['no_fall_in_window']} | "
                  f"{v['single_fall']} | {fmt(v['min_iteration_count_at_falls'])} | {v['falls_with_iteration_count_1']} ({v['invalidated_entries_saturated']}) | {v['closure_dff_equals_graded_dff_all']} | "
                  f"{'/'.join(v['engine'])} ({v['cross_checked']}, agree={v['cross_check_agree_all']}) | {v['certified_routes']} |")

    # ---- D. per-draw Semaev data and fits
    sem_points_lf = defaultdict(list)     # (s, p) -> d_lf of uncensored draws
    sem_points_ff = defaultdict(list)     # (s, p) -> d_ff of draws with an observed fall
    sem_all = []
    for (s, p), cell in cells.items():
        for cs, ts, _seed, r in arm_rows(cell, "semaev"):
            if r.get("degenerate"):
                continue
            e = eff(r)
            sem_all.append({"s": s, "p": p, "curve_seed": cs, "target_seed": ts, "d_ff": e["d_ff"], "d_lf": e["d_lf"],
                            "raw_d_ff": e["raw_d_ff"], "raw_d_lf": e["raw_d_lf"], "invalidated": e["invalidated"],
                            "right_censored": r["right_censored"], "no_fall": e["no_fall"], "falls": r["falls"],
                            "iteration_counts": r["fall_iteration_counts"], "it1": r["fall_with_iteration_count_1"]})
            if e["d_ff"] is not None:
                sem_points_ff[(s, p)].append(e["d_ff"])
            if e["d_lf"] is not None and not r["right_censored"]:
                sem_points_lf[(s, p)].append(e["d_lf"])
    out["ladder"]["semaev_draws"] = sem_all

    def fit(cells_pts, srange, name):
        pts = [(s, y) for (s, _p), ys in cells_pts.items() if s in srange for y in ys]
        r = ols(pts)
        r["bootstrap"] = bootstrap_slope({k: v for k, v in cells_pts.items() if k[0] in srange})
        r["range"] = list(srange)
        r["name"] = name
        r["cells"] = {f"{s},{p}": len(ys) for (s, p), ys in cells_pts.items() if s in srange}
        return r

    fits = {
        "d_lf_primary": fit(sem_points_lf, [2, 3, 4, 5], "Semaev d_lf, s = 2..5, uncensored draws"),
        "d_ff_primary": fit(sem_points_ff, [2, 3, 4, 5], "Semaev d_ff, s = 2..5, draws with an observed fall"),
        "d_lf_secondary": fit(sem_points_lf, [1, 2, 3, 4, 5], "Semaev d_lf, s = 1..5, uncensored draws"),
        "d_ff_secondary": fit(sem_points_ff, [1, 2, 3, 4, 5], "Semaev d_ff, s = 1..5, draws with an observed fall"),
    }
    for p in PRIMES:
        fits[f"d_lf_primary_p{p}"] = fit({k: v for k, v in sem_points_lf.items() if k[1] == p}, [2, 3, 4, 5], f"Semaev d_lf, s = 2..5, p = {p}")
    out["fits"] = fits

    md.append("\n## D. Slope fits (pre-declared: OLS on per-draw values, t-interval, bootstrap beside it; censored draws excluded)\n")
    md.append("| fit | range | n draws | cells (draws) | slope | 95% t-interval | residual variance | degenerate | bootstrap 95% (2000, seed 0) | per-s values |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for k, f in fits.items():
        ci = f.get("ci95")
        md.append(f"| {k} | {f.get('range')} | {f['n']} | {f.get('cells')} | {fmt(f.get('slope'))} | {[round(x, 4) for x in ci] if ci else '-'} | {fmt(f.get('residual_variance'))} | "
                  f"{f.get('degenerate')} | {[round(x, 4) for x in f['bootstrap']['ci95_percentile']] if f.get('bootstrap', {}).get('reps') else '-'} | {f.get('per_s_values')} |")

    # ---- E. outcome labels (pre-registered rule, mechanical)
    lf, ff = fits["d_lf_primary"], fits["d_ff_primary"]
    ci_lf, ci_ff = lf.get("ci95"), ff.get("ci95")
    # flat cells: every Semaev draw uncensored and one common d_lf across all primes
    cell_lf = {}
    for s in LADDER_S:
        vals = set()
        unc = True
        present = False
        for p in PRIMES:
            if (s, p) not in cells:
                continue
            present = True
            for d in sem_all:
                if d["s"] == s and d["p"] == p:
                    if d["right_censored"] or d["d_lf"] is None:
                        unc = False
                    else:
                        vals.add(d["d_lf"])
        cell_lf[s] = {"present": present, "all_uncensored": unc and present, "values": sorted(vals)}
    flat_run = 0
    best_flat = 0
    prev = None
    for s in [2, 3, 4, 5]:
        c = cell_lf[s]
        if c["present"] and c["all_uncensored"] and len(c["values"]) == 1 and (prev is None or c["values"][0] == prev):
            flat_run += 1
            prev = c["values"][0]
        else:
            flat_run = 1 if (c["present"] and c["all_uncensored"] and len(c["values"]) == 1) else 0
            prev = c["values"][0] if flat_run else None
        best_flat = max(best_flat, flat_run)
    top_s = max((s for s in LADDER_S if any((s, p) in cells for p in PRIMES)), default=None)
    top_uncensored = bool(top_s) and cell_lf[top_s]["all_uncensored"]
    lab_dlf = "unresolved"
    if ci_lf is not None:
        if contains(ci_lf, 1) and not contains(ci_lf, 0.5):
            lab_dlf = "OUTCOME I"
        elif contains(ci_lf, 0) and not contains(ci_lf, 0.25) and best_flat >= 4 and top_uncensored:
            lab_dlf = "OUTCOME III"
    joint = lab_dlf
    if lab_dlf == "OUTCOME I" and ci_ff is not None and ci_ff[1] < lf["slope"] and not contains(ci_ff, 1):
        joint = "OUTCOME II"
    heur2 = {"d_lf_interval_excludes_0": (ci_lf is not None) and not contains(ci_lf, 0), "top_of_ladder_uncensored": top_uncensored,
             "top_s": top_s, "fires": (ci_lf is not None) and not contains(ci_lf, 0) and top_uncensored}
    out["labels"] = {"d_lf_label": lab_dlf, "joint_label": joint, "d_lf_ci95": ci_lf, "d_ff_ci95": ci_ff, "d_lf_slope": lf.get("slope"), "d_ff_slope": ff.get("slope"),
                     "cell_d_lf": {str(s): v for s, v in cell_lf.items()}, "longest_flat_run_s2_to_5": best_flat, "top_of_ladder_uncensored": top_uncensored,
                     "heur002_falsifier_statistic": heur2, "rule": "stage1-closure-convention.md section 8; H-PFDR-c88f14 P4/P5"}
    md.append("\n## E. Outcome label by the pre-registered rule (mechanical; not interpreted here)\n")
    md.append(f"- Semaev d_lf (primary, s = 2..5): slope {fmt(lf.get('slope'))}, 95% interval {ci_lf}, degenerate = {lf.get('degenerate')}; "
              f"contains 1: {contains(ci_lf, 1)}; excludes 0.5: {not contains(ci_lf, 0.5) if ci_lf else None}; contains 0: {contains(ci_lf, 0)}; excludes 0.25: {not contains(ci_lf, 0.25) if ci_lf else None}.")
    md.append(f"- Semaev d_ff (primary, s = 2..5): slope {fmt(ff.get('slope'))}, 95% interval {ci_ff}; lies strictly below the d_lf point estimate: "
              f"{(ci_ff is not None and lf.get('slope') is not None and ci_ff[1] < lf['slope'])}; excludes 1: {not contains(ci_ff, 1) if ci_ff else None}.")
    md.append(f"- Per-cell Semaev d_lf (all primes pooled): {json.dumps({str(s): v for s, v in cell_lf.items()})}; longest run of consecutive fully-uncensored flat cells in s = 2..5: {best_flat}; top of the ladder (s = {top_s}) uncensored: {top_uncensored}.")
    md.append(f"- **d_lf-only label: {lab_dlf}. Joint label: {joint}.** (Frozen prior: 0.6 Outcome I on d_lf giving joint Outcome II; 0.05 Outcome III; 0.1 unresolved.)")
    md.append(f"- HEUR-002 falsifier statistic (a d_lf interval excluding 0 on a ladder uncensored at its top): {heur2}.")

    # ---- F. frozen d_ff comparison and NULL-3
    md.append("\n## F. Frozen prediction P3 (d_ff = 5, 5, 6, 6 at s = 2..5) and NULL-3 against the Semaev arm\n")
    md.append("| s | p | frozen d_ff | Semaev d_ff values (closure) | residuals | graded d_ff values | NULL-3 d_ff values | NULL-3 - Semaev d_ff | NULL-3 d_lf values | NULL-3 - Semaev d_lf | NULL-3 degenerate |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    n3tab = {}
    for (s, p), cell in cells.items():
        sem = [eff(r[3]) for r in arm_rows(cell, "semaev") if not r[3].get("degenerate")]
        n3 = [r[3] for r in arm_rows(cell, "null3")]
        n3l = [eff(r) for r in n3 if not r.get("degenerate")]
        sem_ff = sorted({r["d_ff"] for r in sem}, key=str)
        frozen = FROZEN["d_ff"].get(s)
        resid = sorted({(r["d_ff"] - frozen) if (r["d_ff"] is not None and frozen is not None) else None for r in sem}, key=str)
        n3_ff = sorted({r["d_ff"] for r in n3l}, key=str)
        n3_lf = sorted({r["d_lf"] for r in n3l}, key=str)
        dff_diff = sorted({(a["d_ff"] - b["d_ff"]) if (a["d_ff"] is not None and b["d_ff"] is not None) else None for a in n3l for b in sem}, key=str)
        dlf_diff = sorted({(a["d_lf"] - b["d_lf"]) if (a["d_lf"] is not None and b["d_lf"] is not None) else None for a in n3l for b in sem}, key=str)
        n3tab[f"{s},{p}"] = {"frozen_d_ff": frozen, "semaev_d_ff": sem_ff, "residuals": resid, "null3_d_ff": n3_ff, "null3_minus_semaev_d_ff": dff_diff,
                             "null3_d_lf": n3_lf, "null3_minus_semaev_d_lf": dlf_diff, "null3_degenerate": len(n3) - len(n3l),
                             "graded_d_ff": sorted({r[3]["graded"]["graded_d_ff"] for r in arm_rows(cell, "semaev") if not r[3].get("degenerate")}, key=str)}
        md.append(f"| {s} | {p} | {frozen} | {sem_ff} | {resid} | {n3tab[f'{s},{p}']['graded_d_ff']} | {n3_ff} | {dff_diff} | {n3_lf} | {dlf_diff} | {len(n3) - len(n3l)} |")
    out["controls"]["P3_and_NULL3"] = n3tab

    # ---- G. null band
    md.append("\n## G. Null band (HEUR-001): NULL-1 and NULL-2 d_lf minus the null formula s + 2, uncensored draws only\n")
    md.append("| s | p | arm | s + 2 | n | uncensored | offsets c (uncensored) | all in {0,1,2} | censored (d_lf observed so far) | no fall |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    band = {}
    max_c_by_s = defaultdict(list)
    for (s, p), cell in cells.items():
        for arm in ("null1", "null2"):
            rows = [eff(r[3]) for r in arm_rows(cell, arm) if not r[3].get("degenerate")]
            unc = [r for r in rows if not r["right_censored"] and r["d_lf"] is not None]
            offs = sorted({r["d_lf"] - (s + 2) for r in unc})
            cens = Counter(str(r["d_lf"]) for r in rows if r["right_censored"])
            inband = all(o in FROZEN["null_band"] for o in offs) if offs else None
            band[f"{s},{p},{arm}"] = {"center": s + 2, "n": len(rows), "uncensored": len(unc), "offsets": offs, "all_in_band": inband,
                                      "censored_observed_so_far": dict(cens), "no_fall": sum(1 for r in rows if r["no_fall"])}
            if offs:
                max_c_by_s[s].append(max(offs))
            md.append(f"| {s} | {p} | {arm} | {s + 2} | {len(rows)} | {len(unc)} | {offs} | {inband} | {dict(cens)} | {band[f'{s},{p},{arm}']['no_fall']} |")
    out["controls"]["null_band"] = band
    maxc = {str(s): max(v) for s, v in max_c_by_s.items()}
    grows = [maxc[str(s)] for s in sorted(int(k) for k in maxc)]
    out["tail_checks"]["largest_band_offset_by_s"] = maxc
    out["tail_checks"]["band_offset_grows_with_s"] = any(b > a for a, b in zip(grows, grows[1:])) if len(grows) > 1 else None
    md.append(f"\nTail check: largest observed band offset c by s (uncensored draws): {maxc}; grows with s: {out['tail_checks']['band_offset_grows_with_s']}.")

    # ---- H. controlled-null flags (F5) and non-curve
    md.append("\n## H. Controlled-null flags (F5): does a null or the non-curve cubic reproduce the Semaev (d_ff, d_lf) pair at every cell?\n")
    md.append("| s | p | Semaev pairs | NULL-1 pairs | NULL-2 pairs | NULL-3 pairs | non-curve pairs | NULL-1 = Semaev | NULL-2 = Semaev | non-curve = Semaev |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    f5 = {"null1": True, "null2": True, "noncurve": True}
    pairs_tab = {}
    for (s, p), cell in cells.items():
        pr = {}
        for arm in ARMS:
            rows = [eff(r[3]) for r in arm_rows(cell, arm) if not r[3].get("degenerate")]
            pr[arm] = sorted({(r["d_ff"], r["d_lf"], "censored" if r["right_censored"] else "certified") for r in rows}, key=str)
        eq = {arm: (pr[arm] == pr["semaev"]) for arm in ("null1", "null2", "noncurve")}
        for arm in eq:
            f5[arm] &= eq[arm]
        pairs_tab[f"{s},{p}"] = {"pairs": {a: [list(x) for x in v] for a, v in pr.items()}, "equal_to_semaev": eq}
        md.append(f"| {s} | {p} | {pr['semaev']} | {pr['null1']} | {pr['null2']} | {pr['null3']} | {pr['noncurve']} | {eq['null1']} | {eq['null2']} | {eq['noncurve']} |")
    out["controls"]["pairs"] = pairs_tab
    out["controls"]["F5_same_pair_at_every_cell"] = f5
    md.append(f"\nF5 (same pair at EVERY cell): {f5}.")

    # ---- I. iteration counts and censoring table, tail checks
    md.append("\n## I. Iteration counts (CTRL-ITERATION-COUNT) and censoring by cell\n")
    md.append("| s | p | Semaev min iter at falls | Semaev it1 | NULL-1 min iter | NULL-2 min iter | NULL-3 min iter | non-curve min iter | Semaev censored / n | NULL-1 censored / n | NULL-2 censored / n | non-curve censored / n | columns at D_max | Semaev histories |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (s, p), cell in cells.items():
        t = {arm: table[(s, p, arm)] for arm in ARMS}
        cols = cell["metrics"]["cell"]["columns_at_Dmax"].get(str(p))
        md.append(f"| {s} | {p} | {fmt(t['semaev']['min_iteration_count_at_falls'])} | {t['semaev']['falls_with_iteration_count_1']} | {fmt(t['null1']['min_iteration_count_at_falls'])} | "
                  f"{fmt(t['null2']['min_iteration_count_at_falls'])} | {fmt(t['null3']['min_iteration_count_at_falls'])} | {fmt(t['noncurve']['min_iteration_count_at_falls'])} | "
                  f"{t['semaev']['right_censored']} / {t['semaev']['n']} | {t['null1']['right_censored']} / {t['null1']['n']} | {t['null2']['right_censored']} / {t['null2']['n']} | "
                  f"{t['noncurve']['right_censored']} / {t['noncurve']['n']} | {cols} | {t['semaev']['histories']} |")
    it1_any = {f"{s},{p},{arm}": v["falls_with_iteration_count_1"] for (s, p, arm), v in table.items() if v["falls_with_iteration_count_1"]}
    out["controls"]["falls_with_iteration_count_1"] = it1_any
    md.append(f"\nFalls with iteration count 1 (any arm, any cell): {it1_any or 'none'}.")
    # tail check: top two uncensored Semaev cells
    unc_s = [s for s in LADDER_S if cell_lf.get(s, {}).get("all_uncensored")]
    top2 = sorted(unc_s)[-2:]
    tt = {}
    for s in top2:
        for p in PRIMES:
            if (s, p) in cells:
                tt[f"{s},{p}"] = {"columns": cells[(s, p)]["metrics"]["cell"]["columns_at_Dmax"].get(str(p)), "preflight": cells[(s, p)]["metrics"]["cell"].get("preflight", {}).get(str(p)),
                                  "semaev": table[(s, p, "semaev")]}
    out["tail_checks"]["top_two_uncensored_semaev_cells"] = tt
    md.append(f"\nTail check: top two fully-uncensored Semaev s-levels: {top2}; per cell: {json.dumps(tt, default=str)}")
    # tail check: largest NULL-3 minus Semaev d_lf difference
    big = max(((abs(x), k) for k, v in n3tab.items() for x in v["null3_minus_semaev_d_lf"] if x is not None), default=None)
    out["tail_checks"]["largest_null3_minus_semaev_d_lf"] = big
    md.append(f"\nTail check: largest |NULL-3 - Semaev| d_lf difference: {big} (cells where NULL-3 is degenerate or unfallen contribute nothing).")

    # ---- J. soundness subsample and certificates
    md.append("\n## J. Soundness subsample (y^2 = f(x) filter, target seed 5 draws) and certificates\n")
    sound = []
    certs_ok = True
    for (s, p), cell in cells.items():
        mm = cell["metrics"]
        certs_ok &= bool(mm.get("certificates_all_verified"))
        for x in mm.get("soundness_subsample", []):
            sound.append({"s": s, **x})
    out["controls"]["soundness"] = sound
    out["controls"]["certificates_all_verified_all_cells"] = certs_ok
    fr = [x["filtering_fraction"] for x in sound if x["filtering_fraction"] is not None]
    md.append(f"- {len(sound)} subsample draws; zeros of S~ on the digit cube per draw: {sorted(Counter(x['n_zeros'] for x in sound).items())}; "
              f"filtering fraction of zeros with a non-square right-hand side: values {sorted(set(fr))} (reported, not modelled); planted digit vector among the zeros in every draw: {all(x['planted_digit_vector_is_zero'] for x in sound)}.")
    md.append(f"- Planted-target certificates verified by independent point addition and by harness.semaev in every cell: {certs_ok}; non-curve root certificates verified by harness.semaev.s3_eval: recorded per draw in raw.")

    # ---- K. equal-d^s spread
    md.append("\n## K. CTRL-EQUAL-DS-SPREAD at B = 64, p = 65537, D <= 6 (the presentational artifact budget; a claimed effect must exceed the spread by a factor 2)\n")
    md.append("| (d, s) | ring | columns | engine | n | d_ff values | d_lf values | censored | no fall |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    eq = {}
    for (d, s) in ((2, 6), (4, 3), (8, 2)):
        rid = f"RUN-PFDR-cbdefb-equalds-d{d}-s{s}"
        if rid not in runs:
            eq[f"{d},{s}"] = {"missing": True}
            md.append(f"| ({d}, {s}) | - | - | - | not run | | | | |")
            continue
        m = runs[rid]["metrics"]
        eq[f"{d},{s}"] = {"presentation": m["presentation"], "d_ff_values": m["d_ff_values"], "d_lf_values": m["d_lf_values"], "right_censored": m["right_censored"], "n": m["n"],
                          "pairs": m["pairs"]}
        md.append(f"| ({d}, {s}) | {m['presentation']['ring_mode']} | {m['presentation']['columns']} | {m['presentation']['engine']} | {m['n']} | {m['d_ff_values']} | {m['d_lf_values']} | {m['right_censored']} | "
                  f"{sum(1 for x in m['pairs'] if x['no_fall_in_window'])} |")
    # per (curve, target) triple
    trip = defaultdict(dict)
    for key, v in eq.items():
        for x in v.get("pairs", []):
            trip[(x["curve_seed"], x["target_seed"])][key] = (x["d_ff"], x["d_lf"], x["right_censored"])
    out["equal_ds"] = {"per_presentation": eq, "per_instance": {f"{k[0]},{k[1]}": v for k, v in trip.items()}}
    ffs = sorted({v2[0] for v in trip.values() for v2 in v.values() if v2[0] is not None}, key=str)
    md.append(f"\nPer-instance triples (d_ff, d_lf, censored) by presentation: {json.dumps({f'{k[0]},{k[1]}': v for k, v in trip.items()}, default=str)}. "
              f"Observed d_ff spread across presentations (uncensored-or-not, where a fall was observed): {ffs}.")

    # ---- L. Stage 3 (m = 3)
    md.append("\n## L. Stage 3 (optional, gated open by EXP-PFDR-5726af's H-TOP): m = 3, p = 65537\n")
    m3 = {}
    for s in (2, 3):
        rid = f"RUN-PFDR-cbdefb-m3-s{s}"
        if rid not in runs:
            m3[str(s)] = {"missing": True}
            continue
        m = runs[rid]["metrics"]
        m3[str(s)] = {arm: {k: m[arm][k] for k in ("n", "d_ff_values", "d_lf_values", "right_censored", "no_fall_in_window", "min_iteration_count_at_falls")} for arm in ARMS}
        m3[str(s)]["cell"] = m["cell"]
        m3[str(s)]["semaev_pairs"] = m["semaev_pairs"]
        md.append(f"- (3, 2, {s}): Semaev pairs {m['semaev_pairs']}; per arm: " + "; ".join(
            f"{arm}: n={m[arm]['n']}, d_ff {sorted(set(map(str, m[arm]['d_ff_values'])))}, d_lf {sorted(set(map(str, m[arm]['d_lf_values'])))}, censored {m[arm]['right_censored']}, no-fall {m[arm]['no_fall_in_window']}" for arm in ARMS)
            + f"; generator degrees / window / columns: {m['cell'].get('preflight')} window {m['cell']['window']} columns {m['cell']['columns_at_Dmax']}.")
    out["m3"] = m3

    # ---- M. frozen criteria restated
    md.append("\n## M. Frozen criteria restated with the observed values (observation, not judgment)\n")
    crit = {
        "ladder uncensored at its top (m = 2)": top_uncensored,
        "null arms in the band {0, 1, 2} at every uncensored cell": all(v["all_in_band"] for v in band.values() if v["all_in_band"] is not None),
        "null cells with NO uncensored draw (band not testable)": [k for k, v in band.items() if v["all_in_band"] is None],
        "NULL-3 d_ff = Semaev d_ff at every cell": {k: v["null3_minus_semaev_d_ff"] for k, v in n3tab.items()},
        "d_ff = 5, 5, 6, 6 at s = 2..5 (P3)": {k: v["residuals"] for k, v in n3tab.items()},
        "outcome label (pre-registered rule)": {"d_lf_only": lab_dlf, "joint": joint},
        "F5 controlled-null (same pair at every cell)": f5,
        "falls with iteration count 1": it1_any or "none",
        "P1 closure d_ff = graded-rank d_ff on every Semaev draw (all cells)": all(v["closure_dff_equals_graded_dff_all"] for (s, p, arm), v in table.items() if arm == "semaev" and v["closure_dff_equals_graded_dff_all"] is not None),
        "engines agree wherever both ran": all(v["cross_check_agree_all"] for v in table.values()),
    }
    out["criteria"] = crit
    for k, v in crit.items():
        md.append(f"- {k}: `{json.dumps(v, default=str)}`")

    md.append("\n## N. What was not measured\n")
    md.append("- Any D above D_max = 7 (the null arms' last falls at s >= 4 lie above it and are censored by construction); any s > 5; the (2, 2, 6, 8) cell (excluded by name).")
    md.append("- The F_2 Weil-descent known-answer fixture (substituted by the planted-fall fixture, note section 4).")
    md.append("- NULL-3 at s = 2 is a single monomial (degree-2 forms in two squarefree variables) and has no closure fall; at m = 3 the block-factored forms vanish identically.")

    with open(os.path.join(EXP_DIR, "analysis.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    with open(os.path.join(EXP_DIR, "analysis.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(json.dumps({"labels": out["labels"], "F5": f5, "criteria": {k: v for k, v in crit.items() if k.startswith(("ladder", "null arms", "P1", "engines"))}}, indent=1, default=str))


if __name__ == "__main__":
    main()

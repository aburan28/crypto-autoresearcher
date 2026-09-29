"""Stage 5 analysis run for EXP-ECDLP-869870 over the COMPLETED generic-exact
runs: the pooled seven-cell fixture gate per N (reported first), the Stage 1
flags, the constants table (MEASURED with CI in its own columns, MODELED in
its own columns, never merged), null outcomes, exceedance flags, the
exact-versus-sampled cross-check, and the O(theta) trend across N.

Observations only. No interpretation, no status language.

Usage: python3 analysis.py --runs-dir <runs> --out <run-dir> [--include RUN-ID ...]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as MODEL  # noqa: E402

A_GRID = [0.125, 0.25, 0.5, 1.0]
R_GRID = [1, 2, 4, 8, 16]


def load_runs(runs_dir, include):
    out = []
    for mpath in sorted(glob.glob(os.path.join(runs_dir, "RUN-*", "manifest.yaml"))):
        rd = os.path.dirname(mpath)
        rid = os.path.basename(rd)
        if include and rid not in include:
            continue
        m = yaml.safe_load(open(mpath))["run"]
        if m["kind"] not in ("generic_exact", "generic_sampled", "curve_exact"):
            continue
        rec = {"run_id": rid, "status": m["status"], "manifest": m, "kind": m["kind"], "dir": rd}
        if m["status"] == "completed_valid" and os.path.exists(os.path.join(rd, "summary.json")):
            rec["summary"] = json.load(open(os.path.join(rd, "summary.json")))
        out.append(rec)
    return out


def mean_ci(vals):
    v = np.array([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    if v.size == 0:
        return {"mean": None, "sd": None, "se": None, "ci95": [None, None], "n": 0, "min": None, "max": None}
    sd = float(v.std(ddof=1)) if v.size > 1 else 0.0
    se = sd / math.sqrt(v.size)
    return {"mean": float(v.mean()), "sd": sd, "se": se, "ci95": [float(v.mean() - 1.96 * se), float(v.mean() + 1.96 * se)],
            "n": int(v.size), "min": float(v.min()), "max": float(v.max()), "values": v.tolist()}


def bootstrap_ratio(steps, hits, rng, reps=2000):
    """Bootstrap CI of pooled total_steps / total_hits over seeds (resampling seeds)
    is degenerate at 5 seeds; instead resample the per-seed (steps, hits) pairs with
    replacement and also report the per-seed spread."""
    steps = np.array(steps, float); hits = np.array(hits, float)
    n = steps.size
    vals = []
    for _ in range(reps):
        idx = rng.integers(0, n, size=n)
        s, h = steps[idx].sum(), hits[idx].sum()
        vals.append(s / h if h > 0 else np.nan)
    vals = np.array(vals); vals = vals[np.isfinite(vals)]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--include", nargs="*", default=None)
    args = ap.parse_args()
    runs = load_runs(args.runs_dir, set(args.include) if args.include else None)
    rng = np.random.default_rng(700)
    valid = [r for r in runs if r["status"] == "completed_valid"]
    by_N = {}
    sampled = [r for r in valid if r["kind"] == "generic_sampled"]
    curves = [r for r in valid if r["kind"] == "curve_exact"]
    for r in valid:
        if r["kind"] == "generic_exact":
            by_N.setdefault(r["summary"]["header"]["log2N"], []).append(r)
    report = {"experiment_id": "EXP-ECDLP-869870", "stage": "analysis",
              "coverage": {"runs_considered": [(r["run_id"], r["status"]) for r in runs],
                           "valid_runs_by_log2N": {str(k): [r["run_id"] for r in v] for k, v in by_N.items()},
                           "seeds_by_log2N": {str(k): sorted(r["summary"]["header"]["seed"] for r in v) for k, v in by_N.items()},
                           "stages_covered": sorted({("Stage 1" if k == 20 else "Stage 2") for k in by_N} | ({"Stage 3"} if sampled else set()) | ({"Stage 4"} if curves else set())),
                           "stage3_runs": [r["run_id"] for r in sampled], "stage4_runs": [r["run_id"] for r in curves],
                           "not_covered": [st for st, present in (("Stage 3 (2^30 sampled)", bool(sampled)), ("Stage 4 (curve)", bool(curves))) if not present]},
              "certificate": {"kind": "none", "reason": "analysis of generic-arm runs; nothing solved"},
              "order_note": "The fixture gate is reported FIRST (block 'fixture_gate'); rule arms follow.",
              "fixture_gate": {}, "stage1_flags": {}, "seed_integrity": {}, "constants_table": [],
              "nulls": {}, "exceedance": {}, "cross_check": {}, "unselected_law": {}, "oracle_share": {},
              "basin_law": {}, "heur_blt2": {}, "b4": {}, "estimation_loss": {}, "theta_trend": {}}

    # seed integrity
    for k, v in by_N.items():
        seeds = [r["summary"]["header"]["seed"] for r in v]
        report["seed_integrity"][str(k)] = {"seeds": sorted(seeds), "duplicated": len(seeds) != len(set(seeds)),
                                            "missing": sorted(set([1, 2, 3, 4, 5]) - set(seeds)),
                                            "cell_valid": len(seeds) == len(set(seeds)) and set(seeds) == {1, 2, 3, 4, 5}}

    # ---- fixture gate per N (pooled over seeds) --------------------------------
    for k, v in sorted(by_N.items()):
        rows = []
        all_pass = True
        for (a, r) in MODEL.FIXTURE_CELLS:
            steps = []; hits = []; P = []; exact_costs = []; per_seed = []
            for run in v:
                fx = run["summary"]["cells"][f"a={a}"]["fixture"][str(r)]
                steps.append(fx["total_steps"]); hits.append(fx["hits"]); P.append(fx["scaled_precomp_measured"])
                exact_costs.append(fx["scaled_cost_exact_expectation"]); per_seed.append(fx["scaled_cost_sampled_this_seed"])
            N = 1 << k; T = v[0]["summary"]["header"]["T"]
            pooled = sum(steps) / sum(hits) / math.sqrt(N / T)
            ci = [x / math.sqrt(N / T) for x in bootstrap_ratio(steps, hits, rng)]
            Pm = mean_ci(P)
            pub_c = MODEL.PUBLISHED_SCALED_COST[(a, r)]; pub_p = MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)]
            cost_ok = abs(pooled - pub_c) <= MODEL.GATE_COST_TOL
            pre_ok = abs(Pm["mean"] / pub_p - 1) <= MODEL.GATE_PRECOMP_TOL
            row = {"a": a, "r": r, "theta": 1 / math.sqrt(a * N / T),
                   "MEASURED_scaled_cost_pooled": pooled, "MEASURED_scaled_cost_boot95": ci,
                   "MEASURED_scaled_cost_per_seed": per_seed, "MEASURED_scaled_cost_exact_expectation_mean": mean_ci(exact_costs)["mean"],
                   "PUBLISHED_scaled_cost": pub_c, "residual_cost": pooled - pub_c, "cost_within_0.10": bool(cost_ok),
                   "MEASURED_scaled_precomp_mean": Pm["mean"], "MEASURED_scaled_precomp_ci95": Pm["ci95"], "MEASURED_scaled_precomp_per_seed": P,
                   "PUBLISHED_scaled_precomp": pub_p, "precomp_relative_residual": Pm["mean"] / pub_p - 1, "precomp_within_12pct": bool(pre_ok),
                   "MODELED_b4_scaled_precomp": MODEL.B4_CONTRACT_VALUES[(a, r)],
                   "MODELED_nt8_oracle_constant": MODEL.MODEL_NT8.get((a, r)),
                   "nt8_within_0.05_of_model": (abs(pooled - MODEL.MODEL_NT8[(a, r)]) <= 0.05) if (a, r) in MODEL.MODEL_NT8 else None,
                   "hits_pooled": int(sum(hits)), "M_pooled": 40000 * len(v)}
            all_pass = all_pass and cost_ok and pre_ok
            rows.append(row)
        worst = max(rows, key=lambda x: abs(x["residual_cost"]))
        verdict = ("PASS" if all_pass else "FAIL") if k >= 24 else ("report-only (gate binding only at N >= 2^24): " + ("all cells within tolerance" if all_pass else "not all cells within tolerance"))
        report["fixture_gate"][str(k)] = {"log2N": k, "seeds": len(v), "blocking": k >= 24, "rows": rows,
                                          "all_seven_cells_within_tolerance": bool(all_pass), "verdict": verdict,
                                          "largest_residual_cell": {"a": worst["a"], "r": worst["r"], "residual_cost": worst["residual_cost"]},
                                          "invalidation_rule_3_fired": (k >= 24 and not all_pass)}

    # ---- Stage 1 flags ----------------------------------------------------------
    if 20 in by_N:
        v = by_N[20]
        flags = {}
        for a in A_GRID:
            slopes = [r["summary"]["cells"][f"a={a}"]["basin_law"]["survival_slope_8W"] for r in v]
            ratios = [r["summary"]["cells"][f"a={a}"]["global_oracle"]["ratio_to_c_max_numeric"] for r in v]
            slope_out = sum(1 for s in slopes if not (-0.7 <= s <= -0.3))
            ratio_out = sum(1 for x in ratios if not (0.8 <= x <= 1.1))
            flags[str(a)] = {"survival_slopes": slopes, "slope_outside_[-0.7,-0.3]_count": slope_out,
                             "topT_ratio_to_cmax": ratios, "ratio_outside_[0.8,1.1]_count": ratio_out,
                             "slope_flag_majority": slope_out > len(v) / 2, "ratio_flag_majority": ratio_out > len(v) / 2}
        report["stage1_flags"] = {"per_a": flags,
                                  "any_flag": any(f["slope_flag_majority"] or f["ratio_flag_majority"] for f in flags.values()),
                                  "rule": "STAGE 1 stopping rule: slope outside [-0.7,-0.3] or top-T share outside 0.8-1.1 of C_max(a) in a majority of seeds flags the model comparison; Stages 2-3 then run as measurement-only cells"}

    # ---- per-N, per-a blocks ------------------------------------------------------
    for k, v in sorted(by_N.items()):
        K = str(k)
        report["exceedance"][K] = [e for r in v for e in r["summary"]["header"]["invalidity"]["exact_coverage_exceeds_global_oracle"]]
        report["nulls"][K] = {}; report["cross_check"][K] = {}; report["unselected_law"][K] = {}
        report["oracle_share"][K] = {}; report["basin_law"][K] = {}; report["heur_blt2"][K] = {}; report["b4"][K] = {}
        report["estimation_loss"][K] = {}
        for a in A_GRID:
            cells = [r["summary"]["cells"][f"a={a}"] for r in v]
            # nulls
            nn = {}
            for rule in ("published_weight", "count_only"):
                for r in R_GRID:
                    diffs = [c["rules"][str(r)]["nulls"][rule]["relabelled_minus_unselected"] for c in cells]
                    unsel = [c["rules"][str(r)]["tables"]["unselected"]["coverage_exact_8W"] for c in cells]
                    relab = [c["rules"][str(r)]["nulls"][rule]["relabelled_coverage_8W"] for c in cells]
                    mono = [c["rules"][str(r)]["nulls"][rule]["sigma_monotone_nonincreasing"] for c in cells]
                    flat = [c["rules"][str(r)]["nulls"][rule]["sigma_flat"] for c in cells]
                    sig_curves = [c["rules"][str(r)]["nulls"][rule]["sigma_coverage_8W"] for c in cells]
                    dm = mean_ci(diffs); um = mean_ci(unsel)
                    # seed-spread CI: the difference mean against the spread of the unselected control
                    spread_ci = [-1.96 * um["sd"] if um["sd"] is not None else None, 1.96 * um["sd"] if um["sd"] is not None else None]
                    inside = (dm["mean"] is not None and um["sd"] is not None and abs(dm["mean"]) <= max(1.96 * um["sd"], 1e-12)) if r > 1 else True
                    nn[f"{rule}/r={r}"] = {"relabelled_minus_unselected_per_seed": diffs, "mean_diff": dm["mean"], "mean_diff_ci95": dm["ci95"],
                                           "unselected_seed_sd": um["sd"], "unselected_mean": um["mean"], "relabelled_mean": mean_ci(relab)["mean"],
                                           "diff_within_seed_spread_1.96sd": bool(inside),
                                           "sigma_monotone_per_seed": mono, "sigma_flat_per_seed": flat, "sigma_curves": sig_curves,
                                           "note_r1": "at r = 1 the pool has exactly T entries and every rule, null and sigma level selects the same table" if r == 1 else None}
            report["nulls"][K][str(a)] = nn
            # cross-check exact vs sampled
            cc = []
            for r in R_GRID:
                for rule, t in cells[0]["rules"][str(r)]["tables"].items():
                    ins = [c["rules"][str(r)]["tables"][rule]["exact_inside_wilson"] for c in cells]
                    res = [c["rules"][str(r)]["tables"][rule]["sampled_minus_exact"] for c in cells]
                    cc.append({"r": r, "rule": rule, "exact_inside_wilson_per_seed": ins, "all_inside": all(ins), "sampled_minus_exact": res})
            report["cross_check"][K][str(a)] = {"cells": cc, "n_outside": sum(1 for x in cc for y in x["exact_inside_wilson_per_seed"] if not y),
                                                "n_total": sum(len(x["exact_inside_wilson_per_seed"]) for x in cc)}
            # unselected law
            ul = []
            for i, u0 in enumerate(cells[0]["unselected_law"]):
                ratios = [c["unselected_law"][i]["ratio"] for c in cells]
                covs = [c["unselected_law"][i]["coverage_exact_8W"] for c in cells]
                ul.append({"m_factor": u0["m_factor"], "a_m": u0["a_m"], "MEASURED_coverage": mean_ci(covs), "MODELED_c_rand": u0["c_rand_model"],
                           "ratio": mean_ci(ratios), "distinct_dps_per_seed": [c["unselected_law"][i]["distinct_dps"] for c in cells]})
            report["unselected_law"][K][str(a)] = ul
            # oracle share
            shares = [c["global_oracle"]["top_T_share_8W"] for c in cells]
            shares20 = [c["global_oracle"]["top_T_share_20W"] for c in cells]
            report["oracle_share"][K][str(a)] = {"MEASURED_top_T_share_8W": mean_ci(shares), "MEASURED_top_T_share_20W": mean_ci(shares20),
                                                 "MODELED_c_max_numeric": MODEL.c_max(a), "MODELED_c_max_contract": MODEL.CMAX_CONTRACT[a][1],
                                                 "ratio_to_c_max_numeric": mean_ci([s / MODEL.c_max(a) for s in shares]),
                                                 "MEASURED_oracle_online_constant_sqrt_a_over_C": mean_ci([c["global_oracle"]["oracle_online_constant_measured_sqrt_a_over_C"] for c in cells]),
                                                 "MEASURED_oracle_online_constant_exact_expectation": mean_ci([c["global_oracle"]["oracle_online_constant_exact_expectation"] for c in cells]),
                                                 "MEASURED_oracle_scaled_cost_sampled": mean_ci([c["rules"]["16"]["tables"]["global_oracle"]["sampled"]["scaled_cost_sampled"] for c in cells]),
                                                 "MODELED_b3": MODEL.b3_oracle_constant(a), "MODELED_b3_contract": MODEL.B3_CONTRACT[a],
                                                 "cycle_mass_frac": mean_ci([c["cycle_mass_frac"] for c in cells]),
                                                 "capped_mass_8W_frac": mean_ci([c["capped_mass_8W_frac"] for c in cells]),
                                                 "capped_mass_20W_frac": mean_ci([c["capped_mass_20W_frac"] for c in cells])}
            bl = [c["basin_law"] for c in cells]
            report["basin_law"][K][str(a)] = {"MEASURED_survival_slope_8W": mean_ci([b["survival_slope_8W"] for b in bl]),
                                              "per_seed_boot95": [b["survival_slope_8W_boot95"] for b in bl],
                                              "MODELED_slope": -0.5,
                                              "MEASURED_cutoff_theta2_over_2": mean_ci([b["cutoff_n_c_theta2_over_2_8W"] for b in bl]),
                                              "MEASURED_cutoff_joint_slope": mean_ci([b["cutoff_joint_slope_8W"] for b in bl]),
                                              "MODELED_cutoff_theta2_over_2": 1.0,
                                              "largest_basin_per_seed": [b["largest_basin_8W"] for b in bl],
                                              "MODELED_borel_band": bl[0]["borel_band_99_model"],
                                              "seeds_outside_band": sum(1 for b in bl if not b["largest_in_band"]),
                                              "tail_check_more_than_one_of_five_outside": sum(1 for b in bl if not b["largest_in_band"]) > 1}
            h2 = [c["heur_blt2"] for c in cells]
            report["heur_blt2"][K][str(a)] = {"slope_ratio_per_seed": [h["slope_ratio"] for h in h2],
                                              "slope_ratio_outside_[0.9,1.1]_count": sum(1 for h in h2 if not (0.9 <= h["slope_ratio"] <= 1.1)),
                                              "intercept_ci_excludes_0_count": sum(1 for h in h2 if not (h["intercept_ci95"][0] <= 0 <= h["intercept_ci95"][1])),
                                              "var_over_mean_raw_per_seed": [h["var_over_mean_raw"] for h in h2],
                                              "pearson_dispersion_per_seed": [h["pearson_dispersion_vs_binomial_mean"] for h in h2],
                                              "most_hit_in_top_1pct_per_seed": [h["most_hit_in_top_1pct"] for h in h2],
                                              "most_hit_rank_frac_per_seed": [h["most_hit_basin_rank_frac"] for h in h2]}
            report["b4"][K][str(a)] = {str(r): {"MEASURED_walks_needed": mean_ci([c["generation"]["walks_needed_for_rT_distinct"][str(r)] for c in cells]),
                                                "MODELED_b4_walks": cells[0]["generation"]["b4_model_walks"][str(r)],
                                                "ratio": mean_ci([c["generation"]["b4_ratio_measured_over_model"][str(r)] for c in cells]),
                                                "MEASURED_P_scaled": mean_ci([c["rules"][str(r)]["P_scaled_sqrtNT"] for c in cells]),
                                                "MODELED_b4_P_scaled": MODEL.b4_scaled_precomp(r, a)} for r in R_GRID}
            el = {}
            for r in R_GRID:
                el[str(r)] = {"published_over_generated_oracle": mean_ci([c["rules"][str(r)]["published_over_generated_oracle_8W"] for c in cells]),
                              "count_over_generated_oracle": mean_ci([c["rules"][str(r)]["count_over_generated_oracle_8W"] for c in cells]),
                              "unselected_over_generated_oracle": mean_ci([c["rules"][str(r)]["unselected_over_generated_oracle_8W"] for c in cells])}
            seq = [el[str(r)]["published_over_generated_oracle"]["mean"] for r in R_GRID]
            el["monotone_in_r"] = all(seq[i + 1] >= seq[i] for i in range(len(seq) - 1))
            el["r8_value"] = el["8"]["published_over_generated_oracle"]["mean"]
            el["r8_above_0.97"] = el["r8_value"] is not None and el["r8_value"] > 0.97
            c2 = el["2"]["published_over_generated_oracle"]["ci95"]; c8 = el["8"]["published_over_generated_oracle"]["ci95"]
            el["ci_separated_2_vs_8"] = (c2[1] is not None and c8[0] is not None and c2[1] < c8[0])
            el["MODELED_headline_gap_(1/4,2)"] = 0.69 if a == 0.25 else None
            report["estimation_loss"][K][str(a)] = el
            # constants table rows
            for r in R_GRID:
                for rule in ("published_weight", "count_only", "unselected", "generated_oracle", "global_oracle"):
                    cov = mean_ci([c["rules"][str(r)]["tables"][rule]["coverage_exact_8W"] for c in cells])
                    cost = mean_ci([c["rules"][str(r)]["tables"][rule]["scaled_cost_exact_expectation"] for c in cells])
                    scost = mean_ci([c["rules"][str(r)]["tables"][rule]["sampled"]["scaled_cost_sampled"] for c in cells])
                    modeled_cov = MODEL.c_max(a) if rule == "global_oracle" else (MODEL.c_rand(a) if rule == "unselected" and r == 1 else None)
                    report["constants_table"].append({
                        "log2N": k, "a": a, "r": r, "rule": rule,
                        "MEASURED_coverage_exact_8W_mean": cov["mean"], "MEASURED_coverage_exact_8W_ci95": cov["ci95"], "MEASURED_coverage_per_seed": cov.get("values"),
                        "MEASURED_scaled_cost_exact_expectation_mean": cost["mean"], "MEASURED_scaled_cost_exact_expectation_ci95": cost["ci95"],
                        "MEASURED_scaled_cost_sampled_mean": scost["mean"], "MEASURED_scaled_cost_sampled_ci95": scost["ci95"],
                        "MODELED_coverage": modeled_cov,
                        "MODELED_coverage_source": ("(B2) C_max(a)" if rule == "global_oracle" else ("(B1) C_rand(a) at m = T" if modeled_cov is not None else None)),
                        "ratio_measured_over_modeled": (cov["mean"] / modeled_cov) if (modeled_cov and cov["mean"] is not None) else None,
                        "MODELED_published_scaled_cost": MODEL.PUBLISHED_SCALED_COST.get((a, r)) if rule == "published_weight" else None,
                    })

    # ---- theta trend across N (fit on the exact stages) --------------------------
    Ns = sorted(by_N)
    if len(Ns) >= 2:
        tr = {}
        for a in A_GRID:
            xs, ys = [], {}
            for k in Ns:
                T = by_N[k][0]["summary"]["header"]["T"]
                theta = 1 / math.sqrt(a * (1 << k) / T)
                xs.append(theta)
                ys.setdefault("top_T_share_8W", []).append(report["oracle_share"][str(k)][str(a)]["MEASURED_top_T_share_8W"]["mean"])
                ys.setdefault("survival_slope", []).append(report["basin_law"][str(k)][str(a)]["MEASURED_survival_slope_8W"]["mean"])
                for (aa, r) in MODEL.FIXTURE_CELLS:
                    if aa == a:
                        row = next(x for x in report["fixture_gate"][str(k)]["rows"] if x["a"] == a and x["r"] == r)
                        ys.setdefault(f"fixture_cost_r={r}", []).append(row["MEASURED_scaled_cost_pooled"])
                        ys.setdefault(f"fixture_precomp_r={r}", []).append(row["MEASURED_scaled_precomp_mean"])
                for r in R_GRID:
                    ys.setdefault(f"published_over_generated_oracle_r={r}", []).append(report["estimation_loss"][str(k)][str(a)][str(r)]["published_over_generated_oracle"]["mean"])
            fits = {}
            for name, y in ys.items():
                X = np.array(xs); Y = np.array(y, float)
                if np.all(np.isfinite(Y)):
                    A = np.vstack([X, np.ones_like(X)]).T
                    (sl, ic), *_ = np.linalg.lstsq(A, Y, rcond=None)
                    fits[name] = {"theta": xs, "values": y, "linear_fit_slope_per_theta": float(sl), "intercept_theta_to_0": float(ic),
                                  "log2N": Ns, "note": "O(theta) trend fitted on the exact stages; the 2^30 comparison requires Stage 3 (not run in this analysis unless listed)"}
            tr[str(a)] = fits
        report["theta_trend"] = tr

    # ---- Stage 3: 2^30 sampled ------------------------------------------------------
    if sampled:
        k = 30; v = sampled; N = 1 << k; T = v[0]["summary"]["header"]["T"]
        report["seed_integrity"]["30"] = {"seeds": sorted(r["summary"]["header"]["seed"] for r in v), "duplicated": len(v) != len({r["summary"]["header"]["seed"] for r in v}),
                                          "missing": sorted({1, 2, 3} - {r["summary"]["header"]["seed"] for r in v}), "cell_valid": {r["summary"]["header"]["seed"] for r in v} == {1, 2, 3}}
        rows = []; all_pass = True
        for (a, r) in MODEL.FIXTURE_CELLS:
            steps = []; hits = []; P = []; per_seed = []
            for run in v:
                fx = run["summary"]["cells"][f"a={a}"]["fixture"][str(r)]
                steps.append(fx["total_steps"]); hits.append(fx["hits"]); P.append(fx["scaled_precomp_measured"]); per_seed.append(fx["scaled_cost_sampled_this_seed"])
            pooled = sum(steps) / sum(hits) / math.sqrt(N / T)
            ci = [x / math.sqrt(N / T) for x in bootstrap_ratio(steps, hits, rng)]
            Pm = mean_ci(P); pub_c = MODEL.PUBLISHED_SCALED_COST[(a, r)]; pub_p = MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)]
            cost_ok = abs(pooled - pub_c) <= MODEL.GATE_COST_TOL; pre_ok = abs(Pm["mean"] / pub_p - 1) <= MODEL.GATE_PRECOMP_TOL
            all_pass = all_pass and cost_ok and pre_ok
            rows.append({"a": a, "r": r, "theta": 1 / math.sqrt(a * N / T), "MEASURED_scaled_cost_pooled": pooled, "MEASURED_scaled_cost_boot95": ci,
                         "MEASURED_scaled_cost_per_seed": per_seed, "MEASURED_scaled_cost_exact_expectation_mean": None,
                         "PUBLISHED_scaled_cost": pub_c, "residual_cost": pooled - pub_c, "cost_within_0.10": bool(cost_ok),
                         "MEASURED_scaled_precomp_mean": Pm["mean"], "MEASURED_scaled_precomp_ci95": Pm["ci95"], "MEASURED_scaled_precomp_per_seed": P,
                         "PUBLISHED_scaled_precomp": pub_p, "precomp_relative_residual": Pm["mean"] / pub_p - 1, "precomp_within_12pct": bool(pre_ok),
                         "MODELED_b4_scaled_precomp": MODEL.B4_CONTRACT_VALUES[(a, r)], "MODELED_nt8_oracle_constant": MODEL.MODEL_NT8.get((a, r)),
                         "nt8_within_0.05_of_model": (abs(pooled - MODEL.MODEL_NT8[(a, r)]) <= 0.05) if (a, r) in MODEL.MODEL_NT8 else None,
                         "hits_pooled": int(sum(hits)), "M_pooled": 40000 * len(v)})
        worst = max(rows, key=lambda x: abs(x["residual_cost"]))
        report["fixture_gate"]["30"] = {"log2N": 30, "seeds": len(v), "blocking": True, "rows": rows, "all_seven_cells_within_tolerance": bool(all_pass),
                                        "verdict": "PASS" if all_pass else "FAIL", "largest_residual_cell": {"a": worst["a"], "r": worst["r"], "residual_cost": worst["residual_cost"]},
                                        "invalidation_rule_3_fired": not all_pass, "note": "sampled stage: M = 40000 real walks per (seed, a); 3 seeds"}
        report["nulls"]["30"] = {}; report["unselected_law"]["30"] = {}; report["b4"]["30"] = {}; report["exceedance"]["30"] = "no exact coverage at 2^30; rule not applicable"
        for a in A_GRID:
            cells = [r["summary"]["cells"][f"a={a}"] for r in v]
            nn = {}
            for rule in ("published_weight", "count_only"):
                for r in R_GRID:
                    nn[f"{rule}/r={r}"] = {"relabelled_minus_unselected_sampled_per_seed": [c["rules"][str(r)]["nulls"][rule]["relabelled_minus_unselected"] for c in cells],
                                           "wilson_overlap_per_seed": [c["rules"][str(r)]["nulls"][rule]["wilson_overlap"] for c in cells],
                                           "sigma_monotone_sampled_per_seed": [c["rules"][str(r)]["nulls"][rule]["sigma_monotone_nonincreasing_sampled"] for c in cells],
                                           "sigma_curves_sampled": [c["rules"][str(r)]["nulls"][rule]["sigma_c_hat"] for c in cells]}
            report["nulls"]["30"][str(a)] = nn
            report["unselected_law"]["30"][str(a)] = [{"m_factor": u0["m_factor"], "a_m": u0["a_m"], "MEASURED_coverage_sampled": mean_ci([c["unselected_law"][i]["coverage_sampled"] for c in cells]),
                                                       "MODELED_c_rand": u0["c_rand_model"], "ratio_sampled": mean_ci([c["unselected_law"][i]["ratio_sampled"] for c in cells])}
                                                      for i, u0 in enumerate(cells[0]["unselected_law"])]
            report["b4"]["30"][str(a)] = {str(r): {"MEASURED_walks_needed": mean_ci([c["generation"]["walks_needed_for_rT_distinct"][str(r)] for c in cells]),
                                                   "MODELED_b4_walks": cells[0]["generation"]["b4_model_walks"][str(r)],
                                                   "ratio": mean_ci([c["generation"]["b4_ratio_measured_over_model"][str(r)] for c in cells]),
                                                   "MEASURED_P_scaled": mean_ci([c["rules"][str(r)]["P_scaled_sqrtNT"] for c in cells]), "MODELED_b4_P_scaled": MODEL.b4_scaled_precomp(r, a)} for r in R_GRID}
            for r in R_GRID:
                for rule in ("published_weight", "count_only", "unselected"):
                    cov = mean_ci([c["rules"][str(r)]["tables"][rule]["sampled"]["c_hat"] for c in cells])
                    scost = mean_ci([c["rules"][str(r)]["tables"][rule]["sampled"]["scaled_cost_sampled"] for c in cells])
                    modeled_cov = MODEL.c_rand(a) if (rule == "unselected" and r == 1) else None
                    report["constants_table"].append({"log2N": 30, "a": a, "r": r, "rule": rule, "sampled_only": True,
                                                      "MEASURED_coverage_sampled_mean": cov["mean"], "MEASURED_coverage_sampled_ci95": cov["ci95"], "MEASURED_coverage_per_seed": cov.get("values"),
                                                      "MEASURED_scaled_cost_sampled_mean": scost["mean"], "MEASURED_scaled_cost_sampled_ci95": scost["ci95"],
                                                      "MODELED_coverage": modeled_cov, "MODELED_coverage_source": "(B1) C_rand(a) at m = T" if modeled_cov else None,
                                                      "ratio_measured_over_modeled": (cov["mean"] / modeled_cov) if modeled_cov else None,
                                                      "MODELED_published_scaled_cost": MODEL.PUBLISHED_SCALED_COST.get((a, r)) if rule == "published_weight" else None})
        # N-drift: 2^24 (exact stage) versus 2^30 after the O(theta) trend fitted on 2^20, 2^22, 2^24
        drift = {}
        if report["theta_trend"] and 24 in by_N:
            for a in A_GRID:
                theta30 = 1 / math.sqrt(a * (1 << 30) / T)
                cells30 = [r["summary"]["cells"][f"a={a}"] for r in v]
                da = {}
                for (aa, r) in MODEL.FIXTURE_CELLS:
                    if aa != a: continue
                    fit = report["theta_trend"][str(a)].get(f"fixture_cost_r={r}")
                    if not fit: continue
                    pred = fit["intercept_theta_to_0"] + fit["linear_fit_slope_per_theta"] * theta30
                    row30 = next(x for x in report["fixture_gate"]["30"]["rows"] if x["a"] == a and x["r"] == r)
                    da[f"fixture_cost_r={r}"] = {"MEASURED_2^30_pooled": row30["MEASURED_scaled_cost_pooled"], "MEASURED_2^30_boot95": row30["MEASURED_scaled_cost_boot95"],
                                                "trend_prediction_at_theta_2^30": pred, "MEASURED_2^24_pooled": next(x for x in report["fixture_gate"]["24"]["rows"] if x["a"] == a and x["r"] == r)["MEASURED_scaled_cost_pooled"],
                                                "drift_measured_minus_trend": row30["MEASURED_scaled_cost_pooled"] - pred,
                                                "drift_outside_boot95": not (row30["MEASURED_scaled_cost_boot95"][0] <= pred <= row30["MEASURED_scaled_cost_boot95"][1])}
                for r in R_GRID:
                    for rule in ("published_weight", "count_only", "unselected"):
                        xs_ = []; ys_ = []
                        for k in sorted(by_N):
                            xs_.append(1 / math.sqrt(a * (1 << k) / by_N[k][0]["summary"]["header"]["T"]))
                            ys_.append(np.mean([c["rules"][str(r)]["tables"][rule]["coverage_exact_8W"] for c in [rr["summary"]["cells"][f"a={a}"] for rr in by_N[k]]]))
                        A = np.vstack([np.array(xs_), np.ones(len(xs_))]).T
                        (sl, ic), *_ = np.linalg.lstsq(A, np.array(ys_), rcond=None)
                        pred = ic + sl * theta30
                        m30 = mean_ci([c["rules"][str(r)]["tables"][rule]["sampled"]["c_hat"] for c in cells30])
                        da[f"coverage/{rule}/r={r}"] = {"exact_stage_means_by_theta": {"theta": xs_, "values": ys_}, "trend_prediction_at_theta_2^30": pred,
                                                        "MEASURED_2^30_sampled": m30["mean"], "MEASURED_2^30_ci95": m30["ci95"], "drift_measured_minus_trend": m30["mean"] - pred,
                                                        "drift_outside_ci95": not (m30["ci95"][0] <= pred <= m30["ci95"][1]) if m30["ci95"][0] is not None else None}
                drift[str(a)] = da
        report["n_drift_24_vs_30"] = drift

    # ---- Stage 4: curve arm ---------------------------------------------------------------
    if curves:
        def ks_two_sample(u1, c1, u2, c2):
            u1 = np.asarray(u1, float); c1 = np.asarray(c1, float); u2 = np.asarray(u2, float); c2 = np.asarray(c2, float)
            n1 = c1.sum(); n2 = c2.sum()
            allu = np.union1d(u1, u2)
            F1 = np.cumsum(c1)[np.searchsorted(u1, allu, side="right") - 1] / n1
            F2 = np.cumsum(c2)[np.searchsorted(u2, allu, side="right") - 1] / n2
            F1 = np.where(np.searchsorted(u1, allu, side="right") == 0, 0, F1); F2 = np.where(np.searchsorted(u2, allu, side="right") == 0, 0, F2)
            D = float(np.max(np.abs(F1 - F2)))
            ne = n1 * n2 / (n1 + n2); lam = (math.sqrt(ne) + 0.12 + 0.11 / math.sqrt(ne)) * D
            pval = 2 * sum((-1) ** (j - 1) * math.exp(-2 * j * j * lam * lam) for j in range(1, 101))
            return D, max(0.0, min(1.0, pval)), int(n1), int(n2)
        gen24 = {r["summary"]["header"]["seed"]: r for r in by_N.get(24, [])}
        cv = {"curve_id": curves[0]["summary"]["header"]["curve_id"], "N": curves[0]["summary"]["header"]["N"], "runs": [r["run_id"] for r in curves], "cells": {}, "certificates": {}}
        for r in curves:
            h = r["summary"]["header"]; cv["certificates"][r["run_id"]] = {"emitted": h["certificate"]["emitted"], "passed": h["certificate"]["passed"], "failed": h["certificate"]["failed"],
                                                                        "verified_all": h["certificate"]["verified"], "per_cell": {k: c["certificates"] for k, c in r["summary"]["cells"].items()}}
        for a in (0.25, 0.5):
            for rw in (16, 32):
                key = f"a={a}/r_walk={rw}"; cells = [(r["summary"]["header"]["seed"], r["summary"]["cells"][key], r) for r in curves if key in r["summary"]["cells"]]
                ks = []; consts = {}
                for seed, c, run in cells:
                    g = gen24.get(seed)
                    if g is None: continue
                    graw = json.load(open(os.path.join(g["dir"], "raw-result.json")))["cells"][f"a={a}"]["basin_multiset_8W"]
                    craw = json.load(open(os.path.join(run["dir"], "raw-result.json")))["cells"][key]["basin_multiset_8W"]
                    D, pv, n1, n2 = ks_two_sample(craw["sizes"], craw["counts"], graw["sizes"], graw["counts"])
                    ks.append({"seed": seed, "D": D, "p_value_asymptotic": pv, "n_curve": n1, "n_generic": n2, "reject_at_0.01": pv < 0.01})
                    gc = g["summary"]["cells"][f"a={a}"]
                    for name, getter in (("global_top_T_share_8W", lambda x: x["global_oracle"]["top_T_share_8W"]),
                                         ("survival_slope_8W", lambda x: x["basin_law"]["survival_slope_8W"]),
                                         ("largest_basin_8W", lambda x: x["basin_law"]["largest_basin_8W"]),
                                         ("cycle_mass_frac", lambda x: x["cycle_mass_frac"]),
                                         ("mean_online_walk_length_over_W", lambda x: x["exact_mean_online_walk_length_8W"] / x["params"]["W"]),
                                         *[(f"coverage_published_weight_r={rr}", (lambda rr_: lambda x: x["rules"][str(rr_)]["tables"]["published_weight"]["coverage_exact_8W"])(rr)) for rr in (1, 2, 8)],
                                         *[(f"coverage_unselected_r={rr}", (lambda rr_: lambda x: x["rules"][str(rr_)]["tables"]["unselected"]["coverage_exact_8W"])(rr)) for rr in (1, 2, 8)],
                                         *[(f"scaled_cost_sampled_published_weight_r={rr}", (lambda rr_: lambda x: x["rules"][str(rr_)]["tables"]["published_weight"]["sampled"]["scaled_cost_sampled"])(rr)) for rr in (1, 2, 8)],
                                         *[(f"P_scaled_r={rr}", (lambda rr_: lambda x: x["rules"][str(rr_)]["P_scaled_sqrtNT"])(rr)) for rr in (1, 2, 8)]):
                        consts.setdefault(name, {"generic": [], "curve": [], "seeds": []})
                        consts[name]["generic"].append(getter(gc)); consts[name]["curve"].append(getter(c)); consts[name]["seeds"].append(seed)
                out = {}
                for name, d in consts.items():
                    diff = [g_ - c_ for g_, c_ in zip(d["generic"], d["curve"])]
                    dm = mean_ci(diff); gm = mean_ci(d["generic"]); cm = mean_ci(d["curve"])
                    out[name] = {"seeds": d["seeds"], "MEASURED_generic": d["generic"], "MEASURED_curve": d["curve"], "generic_minus_curve": diff,
                                 "diff_mean": dm["mean"], "diff_ci95_seed_spread": dm["ci95"], "zero_within_diff_ci95": (dm["ci95"][0] is not None and dm["ci95"][0] <= 0 <= dm["ci95"][1]),
                                 "generic_mean_ci95": gm["ci95"], "curve_mean_ci95": cm["ci95"]}
                cv["cells"][key] = {"ks_per_seed": ks, "ks_reject_count": sum(1 for x in ks if x["reject_at_0.01"]), "ks_majority_not_rejecting": sum(1 for x in ks if not x["reject_at_0.01"]) > len(ks) / 2 if ks else None,
                                    "constants": out, "certificate_pass_equals_hits": all(c["certificates"]["failed"] == 0 and c["certificates"]["every_hit_walk_certified"] for _, c, _ in cells),
                                    "exceedance": [e for _, c, _ in cells for e in c["exceedance"]]}
        report["curve_arm"] = cv

    # ---- invalidation rule 3 labelling (contract stopping rule 2 / invalidation rule 3) ----
    g24 = report["fixture_gate"].get("24")
    fired = bool(g24 and g24["invalidation_rule_3_fired"])
    report["interpretation_validity"] = {
        "fixture_gate_2^24_fired_rule_3": fired,
        "cells_from_2^24_upward_invalid_for_interpretation": fired,
        "affected_log2N": [k for k in ["24", "30"] if k in report["fixture_gate"]] if fired else [],
        "curve_arm_affected": bool(fired and curves),
        "rule_text": "Fixture gate failure at 2^24: the 2^24 and 2^30 run sets are INVALID as not comparable to the paper; not negative (invalidation rule 3). Stage 1 and 2^22 cells are unaffected.",
        "note": "Executor labelling only; the 2^30 gate outcome is still reported in fixture_gate['30'] as measured."}
    for row in report["constants_table"]:
        row["invalid_for_interpretation_rule_3"] = bool(fired and row["log2N"] >= 24)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(report, fh, indent=1, default=lambda o: None)
    with open(os.path.join(args.out, "raw-result.json"), "w") as fh:
        json.dump({"header": {"experiment_id": "EXP-ECDLP-869870", "stage": "analysis", "certificate": report["certificate"],
                              "invalidity": {"completed_invalid": False, "exact_coverage_exceeds_global_oracle": []},
                              "runs_considered": report["coverage"]["runs_considered"]},
                   "constants_table": report["constants_table"], "fixture_gate": report["fixture_gate"]}, fh, indent=1, default=lambda o: None)
    # human-readable constants table (markdown), MEASURED and MODELED columns separate
    lines = ["# EXP-ECDLP-869870 constants table (analysis run)", "",
             "Columns: MEASURED (mean over seeds, 95% CI from seed spread) | MODELED (formula value) | ratio. Never merged.", ""]
    for k in Ns:
        fg = report["fixture_gate"][str(k)]
        lines += [f"## FIXTURE GATE, N = 2^{k} ({fg['seeds']} seeds) -- verdict: {fg['verdict']}", "",
                  "| a | N/T | MEASURED cost (pooled) | boot95 | PUBLISHED cost | resid | within 0.10 | MEASURED precomp | PUBLISHED precomp | rel resid | within 12% | MODELED (B4) | MODELED N/T=8 oracle |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for row in fg["rows"]:
            lines.append(f"| {row['a']} | {row['r']} | {row['MEASURED_scaled_cost_pooled']:.4f} | [{row['MEASURED_scaled_cost_boot95'][0]:.3f}, {row['MEASURED_scaled_cost_boot95'][1]:.3f}] | {row['PUBLISHED_scaled_cost']} | {row['residual_cost']:+.4f} | {row['cost_within_0.10']} | {row['MEASURED_scaled_precomp_mean']:.4f} | {row['PUBLISHED_scaled_precomp']} | {row['precomp_relative_residual']:+.3f} | {row['precomp_within_12pct']} | {row['MODELED_b4_scaled_precomp']} | {row['MODELED_nt8_oracle_constant']} |")
        lines.append("")
    lines += ["## Constants table", "", "| N | a | r | rule | MEASURED coverage (8W) | CI95 | MEASURED exact cost | MEASURED sampled cost | MODELED coverage | source | ratio |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in report["constants_table"]:
        mc = row["MODELED_coverage"]
        rr = row["ratio_measured_over_modeled"]
        ratio_txt = "" if rr is None else f"{rr:.3f}"
        if row.get("sampled_only"):
            lines.append(f"| 2^{row['log2N']} | {row['a']} | {row['r']} | {row['rule']} | sampled: {row['MEASURED_coverage_sampled_mean']:.4f} | [{row['MEASURED_coverage_sampled_ci95'][0]:.4f}, {row['MEASURED_coverage_sampled_ci95'][1]:.4f}] | n/a | {row['MEASURED_scaled_cost_sampled_mean']:.3f} | {'' if mc is None else f'{mc:.4f}'} | {row['MODELED_coverage_source'] or ''} | {ratio_txt} |")
            continue
        lines.append(f"| 2^{row['log2N']} | {row['a']} | {row['r']} | {row['rule']} | {row['MEASURED_coverage_exact_8W_mean']:.4f} | [{row['MEASURED_coverage_exact_8W_ci95'][0]:.4f}, {row['MEASURED_coverage_exact_8W_ci95'][1]:.4f}] | {row['MEASURED_scaled_cost_exact_expectation_mean']:.3f} | {row['MEASURED_scaled_cost_sampled_mean']:.3f} | {'' if mc is None else f'{mc:.4f}'} | {row['MODELED_coverage_source'] or ''} | {ratio_txt} |")
    with open(os.path.join(args.out, "constants_table.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("analysis complete:", json.dumps({k: v["verdict"] for k, v in report["fixture_gate"].items()}), "stage1_any_flag:", report.get("stage1_flags", {}).get("any_flag"))


if __name__ == "__main__":
    main()

"""Build execution_report.yaml for TASK-20260906-d17254 from the run manifests
and the final analysis run's summary.json (observations only)."""
import glob, json, os, subprocess, sys
import yaml
REPO = "/home/user/crypto-autoresearcher"
EXP = "EXP-ECDLP-869870"
RUNS = os.path.join(REPO, "experiments", EXP, "runs")
TASK_DIR = os.path.join(REPO, "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-d17254")
analysis_run = sys.argv[1]
A = json.load(open(os.path.join(RUNS, analysis_run, "summary.json")))
commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()

runs = {"completed": [], "invalid": [], "failed": []}
resources = {}
total_cpu = 0.0
for m in sorted(glob.glob(os.path.join(RUNS, "RUN-*", "manifest.yaml"))):
    r = yaml.safe_load(open(m))["run"]
    total_cpu += r["resources"]["cpu_seconds"] or 0
    entry = {"id": r["id"], "kind": r["kind"], "status": r["status"], "note": r["note"], "wall_seconds": round(r["timing"]["wall_seconds"], 1),
             "peak_rss_bytes": r["resources"]["peak_rss_bytes"], "cpu_seconds": round(r["resources"]["cpu_seconds"], 1), "seed": r["inputs"]["seed"],
             "certificate_kind": (r["result"]["certificate"] or {}).get("kind")}
    if r["status"] == "completed_valid": runs["completed"].append(entry)
    elif r["status"] == "completed_invalid": entry["invalid_reason"] = r["result"]["invalid_reason"]; runs["invalid"].append(entry)
    else: entry["failure_class"] = r["failure_class"]; entry["reason"] = r["result"]["invalid_reason"]; runs["failed"].append(entry)
    resources[r["id"]] = {"wall_seconds": entry["wall_seconds"], "peak_rss_bytes": entry["peak_rss_bytes"], "cpu_seconds": entry["cpu_seconds"]}

def gate_block(k):
    g = A["fixture_gate"].get(k)
    if not g: return None
    return {"log2N": g["log2N"], "seeds": g["seeds"], "blocking": g["blocking"], "verdict": g["verdict"], "invalidation_rule_3_fired": g["invalidation_rule_3_fired"],
            "largest_residual_cell": g["largest_residual_cell"],
            "cells": [{"a": x["a"], "N_over_T": x["r"], "MEASURED_scaled_cost_pooled": round(x["MEASURED_scaled_cost_pooled"], 4),
                       "MEASURED_boot95": [round(v, 4) for v in x["MEASURED_scaled_cost_boot95"]], "PUBLISHED_scaled_cost": x["PUBLISHED_scaled_cost"],
                       "cost_within_0.10": x["cost_within_0.10"], "MEASURED_scaled_precomp_mean": round(x["MEASURED_scaled_precomp_mean"], 4),
                       "PUBLISHED_scaled_precomp": x["PUBLISHED_scaled_precomp"], "precomp_relative_residual": round(x["precomp_relative_residual"], 4),
                       "precomp_within_12pct": x["precomp_within_12pct"], "MODELED_B4_scaled_precomp": x["MODELED_b4_scaled_precomp"],
                       "MODELED_NT8_oracle_constant": x["MODELED_nt8_oracle_constant"], "nt8_within_0.05_of_model": x["nt8_within_0.05_of_model"]} for x in g["rows"]]}

obs = {"gate_order_note": "The fixture gate verdicts are stated here BEFORE any rule arm.",
       "fixture_gate": {k: gate_block(k) for k in ("20", "22", "24", "30") if k in A["fixture_gate"]},
       "interpretation_validity_labelling": A.get("interpretation_validity"),
       "stage1_flags": A.get("stage1_flags"),
       "seed_integrity": A["seed_integrity"],
       "exceedance_exact_coverage_above_global_oracle": A["exceedance"],
       "relabelling_null_vs_unselected": {k: {a: {cell: {"mean_diff": round(v["mean_diff"], 5) if v["mean_diff"] is not None else None,
                                                          "unselected_seed_sd": round(v["unselected_seed_sd"], 5) if v["unselected_seed_sd"] is not None else None,
                                                          "within_1.96_seed_sd": v["diff_within_seed_spread_1.96sd"],
                                                          "sigma_monotone_all_seeds": all(v["sigma_monotone_per_seed"]), "sigma_flat_any_seed": any(v["sigma_flat_per_seed"])}
                                                   for cell, v in cells.items()} for a, cells in byN.items()} for k, byN in A["nulls"].items() if k != "30"},
       "relabelling_null_vs_unselected_2^30_sampled": A["nulls"].get("30"),
       "exact_vs_sampled_cross_check": {k: {a: {"n_outside_wilson": v["n_outside"], "n_total": v["n_total"]} for a, v in byN.items()} for k, byN in A["cross_check"].items()},
       "oracle_top_T_share": {k: {a: {"MEASURED_mean": round(v["MEASURED_top_T_share_8W"]["mean"], 4), "MEASURED_ci95": [round(x, 4) for x in v["MEASURED_top_T_share_8W"]["ci95"]],
                                     "MODELED_c_max": round(v["MODELED_c_max_numeric"], 4), "ratio_mean": round(v["ratio_to_c_max_numeric"]["mean"], 4),
                                     "MEASURED_oracle_online_constant_exact_expectation": round(v["MEASURED_oracle_online_constant_exact_expectation"]["mean"], 4),
                                     "MODELED_B3": round(v["MODELED_b3"], 4), "cycle_mass_frac_mean": v["cycle_mass_frac"]["mean"], "capped_mass_8W_frac_mean": v["capped_mass_8W_frac"]["mean"]}
                                  for a, v in byN.items()} for k, byN in A["oracle_share"].items()},
       "basin_law": {k: {a: {"MEASURED_survival_slope_mean": round(v["MEASURED_survival_slope_8W"]["mean"], 4), "ci95": [round(x, 4) for x in v["MEASURED_survival_slope_8W"]["ci95"]],
                            "MODELED_slope": -0.5, "MEASURED_cutoff_theta2_over_2_mean": round(v["MEASURED_cutoff_theta2_over_2"]["mean"], 4), "MODELED_cutoff": 1.0,
                            "largest_basin_per_seed": v["largest_basin_per_seed"], "MODELED_borel_band": [v["MODELED_borel_band"]["n_lo"], v["MODELED_borel_band"]["n_hi"]],
                            "seeds_outside_band": v["seeds_outside_band"], "tail_check_more_than_one_of_five_outside": v["tail_check_more_than_one_of_five_outside"]}
                         for a, v in byN.items()} for k, byN in A["basin_law"].items()},
       "unselected_law_B1": {k: {a: [{"m_factor": u["m_factor"], "ratio_mean": round((u.get("ratio") or u.get("ratio_sampled"))["mean"], 4)} for u in lst] for a, lst in byN.items()} for k, byN in A["unselected_law"].items()},
       "estimation_loss_published_over_generated_oracle": {k: {a: {"by_r": {r: round(v[r]["published_over_generated_oracle"]["mean"], 4) for r in ("1", "2", "4", "8", "16")},
                                                                  "monotone_in_r": v["monotone_in_r"], "r8_above_0.97": v["r8_above_0.97"], "ci_separated_2_vs_8": v["ci_separated_2_vs_8"]}
                                                              for a, v in byN.items()} for k, byN in A["estimation_loss"].items()},
       "heur_blt2": A["heur_blt2"],
       "b4_precomputation": {k: {a: {r: {"MEASURED_P_scaled_mean": round(v[r]["MEASURED_P_scaled"]["mean"], 4), "MODELED_B4": round(v[r]["MODELED_b4_P_scaled"], 4),
                                          "walks_ratio_measured_over_B4_mean": round(v[r]["ratio"]["mean"], 4)} for r in v} for a, v in byN.items()} for k, byN in A["b4"].items()},
       "n_drift_24_vs_30": A.get("n_drift_24_vs_30"),
       "theta_trend": {a: {name: {"theta": f["theta"], "values": f["values"], "slope_per_theta": round(f["linear_fit_slope_per_theta"], 5), "intercept_theta_to_0": round(f["intercept_theta_to_0"], 5)}
                           for name, f in fits.items() if name.startswith("fixture_cost") or name in ("top_T_share_8W", "survival_slope")} for a, fits in A.get("theta_trend", {}).items()},
       "curve_arm": A.get("curve_arm")}
report = {"execution_report": {
    "experiment_id": EXP, "task_id": "TASK-20260906-d17254", "goal_id": "GOAL-ECDLP-bbc21f", "batch_id": "BATCH-289698",
    "implementation_commit": commit, "implementation_commit_note": "source/ is untracked at execution time; every manifest pins the source files by sha256 (code.source_sha256) and the archive commit is the Coordinator's snapshot",
    "contract": {"path": "experiments/EXP-ECDLP-869870/specification.yaml", "version": 1, "status_at_execution": "approved", "approved_by": "coordinator", "execution_authorized": True, "decision": "DEC-20260906-2b1387"},
    "inference": {"requested_policy": "executor-implementation", "binding_model_id": "claude-sonnet-5", "resolved_model_id": "claude-fable-5-1 (self-reported)", "model_verified": False, "reasoning_effort": "medium", "fallback_used": False,
                  "note": "policy requirements (effort >= medium, tool use) met; binding and self-reported model ids differ and are both recorded"},
    "stages": {"stage_1_generic_exact_2^20": "RUN", "stage_2_generic_exact_2^22_2^24": "RUN", "stage_3_generic_sampled_2^30": "RUN" if A["coverage"]["stage3_runs"] else "NOT YET RUN",
               "stage_4_curve": "RUN" if A["coverage"]["stage4_runs"] else "NOT YET RUN", "stage_5_analysis": analysis_run,
               "not_run": ["the 'Pollard rho with DPs and no table' control (sampled floor) was not executed on the curve arm in this batch", "IDEA-20260906-05ffb8's c-sweep / R2 / R3 (excluded by the contract)"]},
    "protocol_deviations": "see experiments/EXP-ECDLP-869870/source/IMPLEMENTATION.md items 1-13 (walk projection top bits vs 'mod N'; generation-start seed 200+s and other unnamed streams; cap as threshold; HEUR-BLT-2 dispersion reported two ways; rho control not run; certificate scope; analysis run 016 failed; scratchpad log collision; diagnostic executed alongside Stage 2)",
    "runs": runs, "run_count": sum(len(v) for v in runs.values()), "budget": {"maximum_runs": 40, "runs_used": sum(len(v) for v in runs.values()), "total_cpu_hours_limit": 16, "total_cpu_hours_used": round(total_cpu / 3600, 4),
                                                                              "per_run_wall_limit_seconds": 3600, "max_wall_seconds_observed": max(v["wall_seconds"] for l in runs.values() for v in l),
                                                                              "memory_limit_bytes": 8 * 1024 ** 3, "max_peak_rss_bytes": max(v["peak_rss_bytes"] or 0 for l in runs.values() for v in l),
                                                                              "analytic_2^24_exact_basin_bytes_5x4xN": 5 * 4 * (1 << 24), "workers": 1},
    "observations": obs,
    "anomalies": [
        "Stage 1 seed 1 showed mean online walk length 1.25-1.36 W; diagnostics/walk_quality_check.py (12 keys) found the construction indistinguishable from a true random table with per-instance sd ~ sqrt(a/T); recorded as a finite-N feature, not an error.",
        "RUN-ECDLP-869870-016-analysis-stages12 failed_infrastructure (SyntaxError, Python 3.11 f-string); superseded by the analysis run named above; kept in the ledger.",
        "The concurrent executor (EXP-ECDLP-612fb1) overwrote this task's scratchpad console log stage2.log; run records unaffected.",
        "Peak RSS at 2^24 (about 0.95 GB) exceeds the analytic 5 x 4 x N = 0.34 GB because bincount and where() temporaries are int64/bool copies; far below the 8 GB ceiling.",
        "Exact-vs-sampled cross-check: at N = 2^20, a = 1/8 (29/130) and a = 1/4 (22/130) the exact coverage lies outside the sampled Wilson interval far more often than 5%; the misses are marginal (exact value at the interval edge, e.g. 0.1265 vs [0.1265, 0.1331]) and the 130 checks per (N, a) are correlated: the 26 tables of a seed share one set of 40000 online walks and the six r = 1 tables are the same table. Recorded as observed; V3 is scored by the reviewers.",
        "Sigma decay: a few cells at r = 2 (and one at r = 4, one at r = 16) show a non-monotone step in the exact coverage curve (exact numbers per seed in the analysis summary nulls block); no cell is flat for r > 1; relabelling minus unselected lies within 1.96 seed-sd at every cell except (2^22, a = 1, published_weight/r = 16).",
        "Curve arm: the r_walk = 16 walk gives KS rejection at alpha = 0.01 in 3/3 seeds at both a and generic-minus-curve differences whose seed-spread CI excludes 0 for the top-T share and the r = 2 coverage; at r_walk = 32 the KS majority does not reject and most constants' differences include 0 (exception: sampled scaled cost at a = 1/2, r = 2). Reported as a walk-quality observation per the contract; not interpreted here.",
        "N-drift block: the linear O(theta) trend fitted on 2^20-2^24 extrapolated to theta(2^30) lies outside the 2^30 bootstrap intervals for every fixture cost cell (drift 0.18-0.42); the 2^30 values themselves sit within 0.10 of the published values (2^30 gate PASS) while the 2^24 gate reads FAIL; both are recorded as measured under the rule-3 label.",
        "The (B4) note in the contract expected measured precomputation 1-12% above the published values; the measured residuals at 2^24 are recorded in fixture_gate['24'] as they are."],
    "artifact_paths": ["experiments/EXP-ECDLP-869870/source/", "experiments/EXP-ECDLP-869870/runs/", os.path.relpath(os.path.join(TASK_DIR, "execution_report.yaml"), REPO), os.path.relpath(os.path.join(TASK_DIR, "artifact_inventory.json"), REPO)],
    "executor_assessment": {"protocol_complete": True, "data_quality": "limited", "requires_rerun": False,
                            "data_quality_note": "limited = the blocking 2^24 fixture gate did not pass (rule 3 fired), so every cell from 2^24 upward carries the invalid-for-interpretation label the contract prescribes; Stage 1 and 2^22 cells are unaffected; no run is evidence before the review chain."}}}
yaml.safe_dump(report, open(os.path.join(TASK_DIR, "execution_report.yaml"), "w"), sort_keys=False, width=110)
print("execution_report.yaml written; runs:", {k: len(v) for k, v in runs.items()})

"""Reads all 24 main-run raw-result.json files (plus the mu0_target=40
sensitivity-check runs) already written under
experiments/EXP-ECDLP-e36df2/runs/ and produces pooled-summary.json per
specification.yaml required_artifacts. Read-only over the run directory;
does not re-run any Stage 2/3 compute."""
from __future__ import annotations

import glob
import json
import os

from poisson_stats import rho_hat_with_ci, poisson_sf

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_ROOT = os.path.join(THIS_DIR, "..")
RUNS_DIR = os.path.join(EXP_ROOT, "runs")


def load_runs():
    runs = []
    for run_dir in sorted(glob.glob(os.path.join(RUNS_DIR, "RUN-*"))):
        raw_path = os.path.join(run_dir, "raw-result.json")
        if not os.path.isfile(raw_path):
            continue
        with open(raw_path) as f:
            data = json.load(f)
        raw = data["raw"]
        raw["_run_id"] = os.path.basename(run_dir)
        runs.append(raw)
    return runs


def pool(runs, section):
    k = sum(r[section]["n_agree"] for r in runs)
    mu0 = sum(r[section]["mu_0_i"] for r in runs)
    return k, mu0


def build_summary():
    runs = load_runs()
    main_runs = [r for r in runs if not r.get("is_sensitivity_check")]
    sens_runs = [r for r in runs if r.get("is_sensitivity_check")]
    pc_runs = [r for r in main_runs if r.get("is_positive_control")]

    if len(main_runs) != 24:
        raise RuntimeError(
            f"pooled_summary: expected 24 main-run instances, found "
            f"{len(main_runs)}; refusing to compute a pooled statistic "
            f"over an incomplete run set.")

    summary = {"alpha_hypothesis_test": 0.01, "alpha_ci": 0.05,
                "n_instances_pooled": len(main_runs),
                "sections": {}}

    for section in ("s_x", "s_y", "s_rand"):
        k, mu0 = pool(main_runs, section)
        stat = rho_hat_with_ci(k, mu0, alpha=0.01)
        summary["sections"][section] = stat

    for section in ("s_x", "s_y"):
        stat = summary["sections"][section]
        rho = stat["rho_hat"]
        p_val = stat["one_sided_p_ge_k_at_mu0"]
        ci_low = stat["ci_low"]
        summary["sections"][section]["joint_verdict_ci_lower_bound_ge_3"] = (
            "falsified" if (ci_low is not None and ci_low >= 3 and p_val < 0.01)
            else "not_falsified_by_this_bar")
        summary["sections"][section]["joint_verdict_point_estimate_ge_3"] = (
            "falsified" if (rho is not None and rho >= 3 and p_val < 0.01)
            else "not_falsified_by_this_bar")

    summary["protocol_ambiguity_note"] = (
        "specification.yaml Stage 3 procedure text states the falsification "
        "bar as 'p<0.01 AND rho_hat's point estimate>=3', while "
        "success_criterion/falsification_criterion state it as 'CI lower "
        "bound>=3 jointly with p<0.01'. Both readings are reported above "
        "(joint_verdict_ci_lower_bound_ge_3 and "
        "joint_verdict_point_estimate_ge_3) rather than the executor "
        "silently picking one; this is recorded as a protocol deviation, "
        "not resolved here.")

    s_rand_ci = summary["sections"]["s_rand"]
    s_rand_valid_null = (s_rand_ci["ci_low"] is not None
                          and s_rand_ci["ci_low"] <= 1.0 <= s_rand_ci["ci_high"])
    summary["s_rand_ci_contains_1"] = s_rand_valid_null

    # Positive control: screen flag rate at m=2, and its own restricted
    # (post-exclusion) rho_hat over its 4 primes alone.
    pc_flag_hits = 0
    for r in pc_runs:
        flagged = r.get("flagged_x_degenerate_m", {})
        if "2" in flagged or 2 in flagged:
            pc_flag_hits += 1
    summary["positive_control"] = {
        "n_primes": len(pc_runs),
        "m2_flag_rate": f"{pc_flag_hits}/{len(pc_runs)}",
        "m2_flagged_on_all_primes": pc_flag_hits == len(pc_runs),
        "sections_restricted_to_positive_control": {
            section: rho_hat_with_ci(*pool(pc_runs, section), alpha=0.01)
            for section in ("s_x", "s_y", "s_rand")
        },
    }

    # Sensitivity check (mu0_target=40 on the smallest-prime curve).
    if sens_runs:
        sens_summary = {}
        for section in ("s_x", "s_y", "s_rand"):
            k, mu0 = pool(sens_runs, section)
            sens_summary[section] = rho_hat_with_ci(k, mu0, alpha=0.01)
        summary["sensitivity_mu0_target_40"] = {
            "n_instances": len(sens_runs),
            "curve_idx": sens_runs[0]["curve_idx"] if sens_runs else None,
            "sections": sens_summary,
        }
    else:
        summary["sensitivity_mu0_target_40"] = {"note": "no sensitivity runs found"}

    # Flagged-degenerate-multiple census, per curve (secondary metric).
    census = {}
    for r in main_runs:
        cidx = r["curve_idx"]
        entry = census.setdefault(cidx, {"x": {}, "y": {}})
        entry["x"].update(r.get("flagged_x_degenerate_m", {}))
        entry["y"].update(r.get("flagged_y_degenerate_m", {}))
    summary["flagged_degenerate_census_by_curve"] = census

    # H1 chi-square diagnostics (aggregate view: list per instance).
    summary["chi_square_by_instance"] = [
        {"curve_idx": r["curve_idx"], "p": r["p"],
         "s_x_chi_square": r["s_x"]["chi_square"],
         "s_y_chi_square": r["s_y"]["chi_square"]}
        for r in main_runs
    ]

    return summary


if __name__ == "__main__":
    summary = build_summary()
    out_path = os.path.join(EXP_ROOT, "pooled-summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(json.dumps({k: v for k, v in summary.items()
                       if k not in ("chi_square_by_instance",)}, indent=2, default=str))

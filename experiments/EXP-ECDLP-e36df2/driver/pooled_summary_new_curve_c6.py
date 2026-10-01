"""Reads the 4 new-curve-c6 raw-result.json files (RUN-ECDLP-e36df2-029..032)
and produces pooled-summary-new-curve-c6.json, pooling ONLY over this new
curve's own 4 instances -- never combined with, appended to, or re-deriving
totals into the existing pooled-summary.json (that file is H-ECDLP-09125b's
own closed, frozen statistic and is never touched by this v2 amendment work,
per PA-ECDLP-e36df2-v1-to-v2 confirmatory_status: exploratory_only).

Uses the SAME poisson_stats.rho_hat_with_ci / poisson_sf as pooled_summary.py
(imported unmodified), so the statistic definitions are byte-identical to
the v1 pooling; only the run set pooled over differs."""
from __future__ import annotations

import glob
import json
import os

from poisson_stats import rho_hat_with_ci

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_ROOT = os.path.join(THIS_DIR, "..")
RUNS_DIR = os.path.join(EXP_ROOT, "runs")

NEW_CURVE_RUN_IDS = [
    "RUN-ECDLP-e36df2-029",
    "RUN-ECDLP-e36df2-030",
    "RUN-ECDLP-e36df2-031",
    "RUN-ECDLP-e36df2-032",
]


def load_runs():
    runs = []
    for run_id in NEW_CURVE_RUN_IDS:
        raw_path = os.path.join(RUNS_DIR, run_id, "raw-result.json")
        with open(raw_path) as f:
            data = json.load(f)
        raw = data["raw"]
        raw["_run_id"] = run_id
        runs.append(raw)
    return runs


def pool(runs, section):
    k = sum(r[section]["n_agree"] for r in runs)
    mu0 = sum(r[section]["mu_0_i"] for r in runs)
    return k, mu0


def build_summary():
    runs = load_runs()
    if len(runs) != 4:
        raise RuntimeError(
            f"pooled_summary_new_curve_c6: expected 4 new-curve instances, "
            f"found {len(runs)}; refusing to compute a pooled statistic over "
            f"an incomplete run set.")
    for r in runs:
        if not r.get("is_new_curve_c6_v2"):
            raise RuntimeError(
                f"pooled_summary_new_curve_c6: run {r['_run_id']} is not "
                f"flagged is_new_curve_c6_v2; refusing to pool a run outside "
                f"this new curve's own instance set.")

    summary = {
        "experiment_id": "EXP-ECDLP-e36df2",
        "protocol_amendment": "PA-ECDLP-e36df2-v1-to-v2",
        "hypothesis": "H-ECDLP-c48f2a",
        "confirmatory_status": "exploratory_only",
        "note": (
            "Pooled ONLY over this new curve's own 4 (curve,prime) "
            "instances (RUN-ECDLP-e36df2-029..032, curve_idx=6, "
            "seed=20260921, non-engineered). This is evidence for "
            "H-ECDLP-c48f2a ALONE. It is NOT combined with, does not "
            "revise, and is not submitted as additional evidence for "
            "H-ECDLP-09125b's own closed 24+4-instance pooled statistic "
            "(pooled-summary.json, EV-ECDLP-5b61eb, DEC-20260912-2a626b), "
            "which remains untouched. Per AGENTS.md, a single, unreplicated "
            "empirical-only 4-instance run set may never itself drive a "
            "reject_scoped-strength verdict."),
        "run_ids_pooled": NEW_CURVE_RUN_IDS,
        "curve_idx": 6,
        "seed": 20260921,
        "engineered": False,
        "alpha_hypothesis_test": 0.01,
        "alpha_ci": 0.05,
        "n_instances_pooled": len(runs),
        "sections": {},
    }

    for section in ("s_x", "s_y", "s_rand"):
        k, mu0 = pool(runs, section)
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
        "Same protocol-text ambiguity as pooled-summary.json (Stage 3 "
        "procedure text vs. success_criterion/falsification_criterion "
        "wording): both readings reported above rather than the executor "
        "silently picking one. This is a restatement of a pre-existing v1 "
        "deviation note, not a new one introduced by this extension.")

    s_rand_ci = summary["sections"]["s_rand"]
    summary["s_rand_ci_contains_1"] = (
        s_rand_ci["ci_low"] is not None
        and s_rand_ci["ci_low"] <= 1.0 <= s_rand_ci["ci_high"])

    # Cross-prime-screen flagged-m census, this curve only.
    census = {"x": {}, "y": {}}
    for r in runs:
        census["x"].update(r.get("flagged_x_degenerate_m", {}))
        census["y"].update(r.get("flagged_y_degenerate_m", {}))
    summary["flagged_degenerate_census_curve_6"] = census

    summary["chi_square_by_instance"] = [
        {"curve_idx": r["curve_idx"], "p": r["p"], "run_id": r["_run_id"],
         "s_x_chi_square": r["s_x"]["chi_square"],
         "s_y_chi_square": r["s_y"]["chi_square"]}
        for r in runs
    ]

    return summary


if __name__ == "__main__":
    summary = build_summary()
    out_path = os.path.join(EXP_ROOT, "pooled-summary-new-curve-c6.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(json.dumps(summary, indent=2, default=str))

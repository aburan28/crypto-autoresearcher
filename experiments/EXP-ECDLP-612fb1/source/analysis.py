"""Stage 4 analysis run for EXP-ECDLP-612fb1: CI tables over completed stages.

Reads every completed_valid generic run under --runs-dir for the requested
stages, pools the 5 seeds per (N, a) and produces ci_tables.json plus a
human-readable analysis.md in --outdir.  Statistics are those the contract
names; comparisons against the frozen pre-registered prediction are
reported as numbers beside the frozen reference -- no conclusion is drawn.

Bootstrap: stratified by seed (targets resampled with replacement within
each seed, paired across arms because every arm shares the target
sequence), B resamples, BCa with bias correction from the bootstrap
distribution and acceleration from a delete-one-seed jackknife.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402

STAGE_OF_NBITS = {20: "G", 24: "1", 30: "2"}
GATE = {"1/4": {"cost": 1.79, "tol": 0.18, "P_range": [1.05, 1.40]},
        "1/2": {"cost": 1.62, "tol": 0.16, "P_range": None}}
A_LABEL = {0.25: "1/4", 0.5: "1/2"}


# ------------------------------------------------------------------ normal helpers (no scipy)
def Phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def Phi_inv(p: float) -> float:
    p = min(max(p, 1e-12), 1 - 1e-12)
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if Phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ------------------------------------------------------------------ bootstrap
class Boot:
    """Stratified-by-seed paired bootstrap with BCa intervals."""

    def __init__(self, B: int, seed: int = 20260906):
        self.B = B
        self.rng = np.random.default_rng(seed)
        self.count = 0

    def ci(self, per_seed: list, stat, alpha: float = 0.05) -> dict:
        """per_seed: list over seeds of dicts name -> 1-D array (all same length
        within a seed).  stat(list_of_dicts) -> float."""
        theta = stat(per_seed)
        boots = np.empty(self.B)
        for b in range(self.B):
            res = []
            for d in per_seed:
                n = len(next(iter(d.values())))
                idx = self.rng.integers(0, n, size=n)
                res.append({k: v[idx] for k, v in d.items()})
            boots[b] = stat(res)
        self.count += 1
        boots = boots[np.isfinite(boots)]
        if len(boots) < 10 or not np.isfinite(theta):
            return {"point": theta, "lo": None, "hi": None, "method": "BCa", "B": self.B, "note": "undefined"}
        # jackknife over seeds for acceleration
        jack = []
        if len(per_seed) > 2:
            for i in range(len(per_seed)):
                jack.append(stat([d for j, d in enumerate(per_seed) if j != i]))
            jack = np.asarray(jack)
            jm = jack.mean()
            num = ((jm - jack) ** 3).sum()
            den = 6.0 * (((jm - jack) ** 2).sum()) ** 1.5
            acc = num / den if den > 0 else 0.0
        else:
            acc = 0.0
        prop = float((boots < theta).mean())
        prop = min(max(prop, 1e-6), 1 - 1e-6)
        z0 = Phi_inv(prop)
        out = {}
        for tag, q in (("lo", alpha / 2), ("hi", 1 - alpha / 2)):
            z = Phi_inv(q)
            adj = Phi(z0 + (z0 + z) / (1 - acc * (z0 + z)))
            out[tag] = float(np.quantile(boots, min(max(adj, 0.0), 1.0)))
        return {"point": float(theta), "lo": out["lo"], "hi": out["hi"], "method": "BCa", "B": self.B,
                "z0": z0, "acceleration": float(acc), "boot_sd": float(boots.std())}


def pooled_mean(per_seed, key):
    num = sum(float(d[key].sum()) for d in per_seed)
    den = sum(len(d[key]) for d in per_seed)
    return num / den if den else float("nan")


def rho_from_eps(eps_by_tsel: dict, target: float, T: int):
    """T_resel/T by log-linear interpolation on the T_sel grid; censored at
    the grid ends (returns (value, censor) with censor in {None, '<=T/4', '>T'})."""
    xs = np.log2(np.array([T // 4, T // 2, 3 * T // 4, T]) / T)
    ys = np.array([eps_by_tsel[k] for k in ("T/4", "T/2", "3T/4", "T")])
    if ys[0] >= target:
        return 0.25, "<=T/4"
    for i in range(3):
        if ys[i] < target <= ys[i + 1] and ys[i + 1] > ys[i]:
            x = xs[i] + (target - ys[i]) / (ys[i + 1] - ys[i]) * (xs[i + 1] - xs[i])
            return float(2 ** x), None
    if ys[-1] < target:
        # log-linear extrapolation on the last segment, reported censored
        if ys[-1] > ys[-2]:
            x = xs[-2] + (target - ys[-2]) / (ys[-1] - ys[-2]) * (xs[-1] - xs[-2])
            return float(min(2 ** x, 4.0)), ">T"
        return 4.0, ">T"
    # non-monotone grid: take the smallest T_sel whose eps >= target
    for i in range(4):
        if ys[i] >= target:
            return float(2 ** xs[i]), "non-monotone grid"
    return 4.0, ">T"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--stages", default="G,1,2")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--resamples", type=int, default=2000)
    args = ap.parse_args()
    stages = set(args.stages.split(","))
    boot = Boot(args.resamples)

    # ---------------------------------------------------------------- load runs
    cells = {}          # (n_bits, a_label) -> list of (run_id, summary, raw)
    inventory = []
    curve_runs = []
    for rid in sorted(os.listdir(args.runs_dir)):
        mp = os.path.join(args.runs_dir, rid, "manifest.yaml")
        sp = os.path.join(args.runs_dir, rid, "summary.json")
        if not (os.path.exists(mp) and os.path.exists(sp)):
            continue
        import yaml
        man = yaml.safe_load(open(mp))["run"]
        kind = man["inputs"]["parameters"].get("kind")
        if kind == "curve":
            s = json.load(open(sp))
            inventory.append({"run_id": rid, "status": man["status"], "kind": "curve", "curve_id": s["curve"]["curve_id"],
                              "seed": s["params"]["seeds"]["walk_key_seed"], "stage": "3", "valid": man["result"]["valid"],
                              "invalid_reason": man["result"]["invalid_reason"],
                              "peak_rss_bytes": man["resources"]["peak_rss_bytes"], "wall_seconds": man["timing"]["wall_seconds"]})
            if "3" in stages and man["status"] == "completed_valid":
                raw = json.load(open(os.path.join(args.runs_dir, rid, "raw-result.json")))
                curve_runs.append((rid, s, raw))
            continue
        if kind == "curve-search":
            s = json.load(open(sp))
            inventory.append({"run_id": rid, "status": man["status"], "kind": "curve-search",
                              "curve_id": s["curve"]["curve_id"], "stage": "3", "valid": man["result"]["valid"],
                              "invalid_reason": man["result"]["invalid_reason"],
                              "peak_rss_bytes": man["resources"]["peak_rss_bytes"], "wall_seconds": man["timing"]["wall_seconds"]})
            continue
        if kind != "generic":
            continue
        s = json.load(open(sp))
        nb = s["params"]["n_bits"]
        st = STAGE_OF_NBITS[nb]
        inventory.append({"run_id": rid, "status": man["status"], "n_bits": nb, "a": s["params"]["a"],
                          "seed": s["params"]["seeds"]["walk_key_seed"], "stage": st, "valid": man["result"]["valid"],
                          "invalid_reason": man["result"]["invalid_reason"],
                          "peak_rss_bytes": man["resources"]["peak_rss_bytes"],
                          "wall_seconds": man["timing"]["wall_seconds"]})
        if st not in stages or man["status"] != "completed_valid":
            continue
        raw = json.load(open(os.path.join(args.runs_dir, rid, "raw-result.json")))
        cells.setdefault((nb, A_LABEL[s["params"]["a"]]), []).append((rid, s, raw))

    out = {"stages_requested": sorted(stages), "run_inventory": inventory, "bootstrap": {
        "method": "stratified-by-seed paired bootstrap, BCa (bias from bootstrap distribution, "
                  "acceleration from delete-one-seed jackknife)", "resamples": args.resamples,
        "code": "experiments/EXP-ECDLP-612fb1/source/analysis.py class Boot"}, "cells": {}}
    md = ["# EXP-ECDLP-612fb1 analysis run: CI tables over stages " + ",".join(sorted(stages)),
          "", "Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the",
          "frozen contract's formulas and published references, quoted beside them and never mixed.", ""]

    # ---------------------------------------------------------------- gates first
    md.append("## Gates (reported before any arm)")
    gates = {}
    for (nb, al), runs in sorted(cells.items()):
        seeds = sorted(s["params"]["seeds"]["walk_key_seed"] for _, s, _ in runs)
        T = runs[0][1]["params"]["T"]
        N = runs[0][1]["params"]["N"]
        key = f"2^{nb},a={al}"
        g = {"seeds": seeds, "n_runs": len(runs), "seed_policy_ok": seeds == [1, 2, 3, 4, 5]}
        # G2 fixture pooled
        steps = sum(s["fixture"]["total_steps"] for _, s, _ in runs)
        succ = sum(s["fixture"]["successes"] for _, s, _ in runs)
        cost = steps / succ / math.sqrt(N / T)
        Ps = [s["fixture"]["scaled_precomputation"] for _, s, _ in runs]
        ref = GATE[al]
        g2 = {"MEASURED_scaled_main_cost_pooled": cost,
              "MEASURED_scaled_main_cost_per_seed": [s["fixture"]["scaled_main_cost"] for _, s, _ in runs],
              "MEASURED_scaled_precomputation_per_seed": Ps, "MEASURED_scaled_precomputation_mean": float(np.mean(Ps)),
              "MEASURED_single_walk_hit_rate_pooled": succ / (len(runs) * I.FIXTURE_TRIALS),
              "PUBLISHED_scaled_main_cost": ref["cost"], "tolerance": ref["tol"],
              "PUBLISHED_scaled_precomputation_range": ref["P_range"],
              "cost_within_tolerance": bool(abs(cost - ref["cost"]) <= ref["tol"])}
        if ref["P_range"]:
            g2["precomputation_within_range"] = bool(ref["P_range"][0] <= np.mean(Ps) <= ref["P_range"][1])
            g2["G2_pass"] = bool(g2["cost_within_tolerance"] and g2["precomputation_within_range"])
        else:
            g2["G2_pass"] = bool(g2["cost_within_tolerance"])
        g2["gated"] = nb in (24, 30)
        g2["note"] = ("G2 gate applies at this N" if nb in (24, 30)
                      else "fixture REPORTED, not gated, at N = 2^20 (contract stage_plan)")
        g["G2_fixture"] = g2
        if nb <= 24:
            b = [s["basins"] for _, s, _ in runs]
            g1 = {"per_seed": [{"seed": s["params"]["seeds"]["walk_key_seed"],
                                "survival_slope_log_grid": x["survival_slope"],
                                "survival_slope_int_grid": x["survival_slope_int_grid"],
                                "MODELED_borel_slope_same_estimator": x["MODELED_borel_survival_slope_same_estimator"],
                                "MODELED_borel_slope_int_grid": x["MODELED_borel_survival_slope_int_grid"],
                                "survival_pointwise_max_abs_log_ratio": x["survival_pointwise"]["max_abs_log_ratio"],
                                "n_c_theta2_over_2": x["cutoff"]["n_c_theta2_over_2"],
                                "MODELED_borel_cutoff_same_estimator": x["MODELED_borel_cutoff_same_estimator"]["n_c_theta2_over_2"],
                                "top_T_share": x["top_T_share"], "C_max_model": x["C_max_model"],
                                "top_T_share_over_C_max": x["top_T_share_over_C_max"],
                                "static_T_exact_coverage": s["fixture"]["static_T_exact_coverage"],
                                "static_below_top_share": bool(s["fixture"]["static_T_exact_coverage"] < x["top_T_share"]),
                                "largest_basin": x["largest_basin"], "borel_99_band": x["largest_basin_borel_99_band"],
                                "largest_in_band": x["largest_basin_in_band"],
                                "cycle_mass_frac": x["cycle_mass_frac"], "capped_mass_frac": x["capped_mass_frac"]}
                               for (_, s, _), x in zip(runs, b)]}
            g1["slope_within_0.15_all_seeds"] = all(abs(x["survival_slope"] + 0.5) <= 0.15 for x in b)
            g1["slope_int_grid_within_0.15_all_seeds"] = all(abs(x["survival_slope_int_grid"] + 0.5) <= 0.15 for x in b)
            g1["cutoff_in_[0.5,2]_all_seeds"] = all(0.5 <= x["cutoff"]["n_c_theta2_over_2"] <= 2 for x in b)
            g1["top_share_over_C_max_in_[0.85,1.05]_all_seeds"] = all(0.85 <= x["top_T_share_over_C_max"] <= 1.05 for x in b)
            g1["top_share_over_C_max_pooled"] = float(np.mean([x["top_T_share_over_C_max"] for x in b]))
            g1["stopping_rule_1_top_share_band"] = bool(0.85 <= g1["top_share_over_C_max_pooled"] <= 1.05)
            g1["static_below_top_share_all_seeds"] = all(e["static_below_top_share"] for e in g1["per_seed"])
            g1["G1_literal_all_four"] = bool(g1["slope_within_0.15_all_seeds"] and g1["cutoff_in_[0.5,2]_all_seeds"]
                                             and g1["top_share_over_C_max_in_[0.85,1.05]_all_seeds"]
                                             and g1["static_below_top_share_all_seeds"])
            g1["gated"] = nb == 20
            g1["note"] = ("G1 gate cell" if nb == 20 else "G1 quantities computed at 2^24 for information; gate is at 2^20")
            g["G1_basin_law"] = g1
        gates[key] = g
        md.append(f"### {key}: seeds {seeds}")
        md.append(f"- G2 fixture ({'GATED' if g2['gated'] else 'reported only'}): MEASURED scaled main cost {cost:.3f} "
                  f"(per seed {[round(v, 3) for v in g2['MEASURED_scaled_main_cost_per_seed']]}) vs PUBLISHED {ref['cost']} "
                  f"+/- {ref['tol']} -> within: {g2['cost_within_tolerance']}; MEASURED P/sqrt(NT) mean "
                  f"{np.mean(Ps):.3f} vs range {ref['P_range']}; G2 pass: {g2['G2_pass']}")
        if "G1_basin_law" in g:
            g1 = g["G1_basin_law"]
            md.append(f"- G1 ({'GATED' if g1['gated'] else 'information'}): slope(log grid) per seed "
                      f"{[round(e['survival_slope_log_grid'], 3) for e in g1['per_seed']]} "
                      f"[MODELED Borel under same estimator {[round(e['MODELED_borel_slope_same_estimator'], 3) for e in g1['per_seed']]}]; "
                      f"within 0.15 of -0.5 all seeds: {g1['slope_within_0.15_all_seeds']}; "
                      f"cutoff n_c theta^2/2 {[round(e['n_c_theta2_over_2'], 3) for e in g1['per_seed']]} in [0.5,2]: "
                      f"{g1['cutoff_in_[0.5,2]_all_seeds']}; top-T share / C_max "
                      f"{[round(e['top_T_share_over_C_max'], 3) for e in g1['per_seed']]} in [0.85,1.05]: "
                      f"{g1['top_share_over_C_max_in_[0.85,1.05]_all_seeds']}; STATIC(T) below top share: "
                      f"{g1['static_below_top_share_all_seeds']}; largest basin in Borel band: "
                      f"{[e['largest_in_band'] for e in g1['per_seed']]}; G1 literal (all four): {g1['G1_literal_all_four']}")
    out["gates"] = gates
    md.append("")

    # ---------------------------------------------------------------- per-cell CI tables
    for (nb, al), runs in sorted(cells.items()):
        key = f"2^{nb},a={al}"
        T = runs[0][1]["params"]["T"]
        R = T
        arms = list(runs[0][1]["arms"].keys())
        sol = {}   # arm -> list per seed of bool arrays
        for name in arms:
            sol[name] = [np.asarray(raw["arms"][name]["solved"], dtype=np.float64) for _, _, raw in runs]
        U_grid = {"4T": 4 * T, "8T": 8 * T, "16T": 16 * T}
        cell = {"T": T, "seeds": [s["params"]["seeds"]["walk_key_seed"] for _, s, _ in runs], "runs": [r for r, _, _ in runs]}

        def win(name, u_lo, u_hi):
            return [x[max(0, u_lo):u_hi] for x in sol[name]]

        def per_seed_dict(names, u_lo, u_hi):
            return [{n: sol[n][i][max(0, u_lo):u_hi] for n in names} for i in range(len(runs))]

        # eps_ss and eps_cum tables (pooled)
        eps_ss = {}
        eps_cum = {}
        for name in arms:
            eps_ss[name] = {lab: pooled_mean(per_seed_dict([name], U - 2 * R, U), name) for lab, U in U_grid.items()}
            eps_cum[name] = {lab: pooled_mean(per_seed_dict([name], 0, U), name) for lab, U in U_grid.items()}
        cell["eps_ss_pooled"] = eps_ss
        cell["eps_cum_pooled"] = eps_cum

        # S1 difference and rho_T(U)
        diff = {}
        rho = {}
        for lab, U in U_grid.items():
            names = ["RESEL-L(T/2)", "STATIC(T)", "RESEL-L(T/4)", "RESEL-L(3T/4)", "RESEL-L(T)"]
            ps = per_seed_dict(names, U - 2 * R, U)
            diff[lab] = boot.ci(ps, lambda d: pooled_mean(d, "RESEL-L(T/2)") - pooled_mean(d, "STATIC(T)"))
            diff[lab]["per_seed"] = [float(d["RESEL-L(T/2)"].mean() - d["STATIC(T)"].mean()) for d in ps]

            def rho_stat(d):
                e = {"T/4": pooled_mean(d, "RESEL-L(T/4)"), "T/2": pooled_mean(d, "RESEL-L(T/2)"),
                     "3T/4": pooled_mean(d, "RESEL-L(3T/4)"), "T": pooled_mean(d, "RESEL-L(T)")}
                return rho_from_eps(e, pooled_mean(d, "STATIC(T)"), T)[0]
            rho[lab] = boot.ci(ps, rho_stat)
            e0 = {"T/4": eps_ss["RESEL-L(T/4)"][lab], "T/2": eps_ss["RESEL-L(T/2)"][lab],
                  "3T/4": eps_ss["RESEL-L(3T/4)"][lab], "T": eps_ss["RESEL-L(T)"][lab]}
            rho[lab]["censor"] = rho_from_eps(e0, eps_ss["STATIC(T)"][lab], T)[1]
            rho[lab]["eps_resel_by_tsel"] = e0
            rho[lab]["eps_static_T"] = eps_ss["STATIC(T)"][lab]
        cell["S1_diff_resel_T2_minus_static_T"] = diff
        cell["rho_T"] = rho
        cell["FROZEN_prediction_rho"] = {"rho(0)": 1.0, "rho(4T)": "<= 0.75 (CI excluding 1.0)", "rho(8T)": "[0.45, 0.65]",
                                        "rho(16T)": "<= 0.6", "asymptote_model": 0.51, "a=1/2": "about 0.6, RESEL-L(T/2) CI-separated below STATIC(T)"}
        d8 = diff["8T"]
        cell["S1_check"] = {"upper_bound_ge_0": (d8["hi"] is not None and d8["hi"] >= 0),
                            "point_ge_-0.03": d8["point"] >= -0.03,
                            "S1_met": bool(d8["hi"] is not None and d8["hi"] >= 0 and d8["point"] >= -0.03)}
        d16 = diff["16T"]
        cell["F1_check"] = {"upper_bound_lt_0_at_16T": (d16["hi"] is not None and d16["hi"] < 0),
                            "rho_16T": rho["16T"]["point"], "rho_16T_ci": [rho["16T"]["lo"], rho["16T"]["hi"]]}
        # seed with smallest gain at 8T
        i_min = int(np.argmin(d8["per_seed"]))
        cell["tail_smallest_seed_gain_8T"] = {"seed": cell["seeds"][i_min], "value": d8["per_seed"][i_min]}
        # early-batch penalty over the first 10% of the U = 8T batch
        u10 = int(0.1 * 8 * T)
        ps = per_seed_dict(["RESEL-L(T/2)", "STATIC(T)"], 0, u10)
        cell["early_batch_penalty_first10pct_8T"] = boot.ci(ps, lambda d: pooled_mean(d, "STATIC(T)") - pooled_mean(d, "RESEL-L(T/2)"))
        cell["early_batch_penalty_first10pct_8T"]["FROZEN_prediction"] = ">= 0.08"
        # U_ss and U* at margin 0.02 (pooled, and per seed)
        def crossing(kind, arrs_a, arrs_b):
            for U in range(2 * R, 16 * T + 1, R):
                if kind == "ss":
                    ea = np.mean(np.concatenate([x[U - 2 * R:U] for x in arrs_a]))
                    eb = np.mean(np.concatenate([x[U - 2 * R:U] for x in arrs_b]))
                else:
                    ea = np.mean(np.concatenate([x[:U] for x in arrs_a]))
                    eb = np.mean(np.concatenate([x[:U] for x in arrs_b]))
                if ea >= eb - 0.02:
                    return f"{U // T}T"
            return "> 16T"
        cell["U_ss_margin0.02"] = {"pooled": crossing("ss", sol["RESEL-L(T/2)"], sol["STATIC(T)"]),
                                   "per_seed": [crossing("ss", [a_], [b_]) for a_, b_ in zip(sol["RESEL-L(T/2)"], sol["STATIC(T)"])],
                                   "FROZEN_prediction": "[4T, 10T]"}
        cell["U_star_margin0.02"] = {"pooled": crossing("cum", sol["RESEL-L(T/2)"], sol["STATIC(T)"]),
                                     "per_seed": [crossing("cum", [a_], [b_]) for a_, b_ in zip(sol["RESEL-L(T/2)"], sol["STATIC(T)"])],
                                     "FROZEN_prediction": "[8T, 16T] or > 16T"}

        # S2: NULL-A gain per round; NULL-B / PHI(0) bit identity
        null_a = {}
        for lab in ("T", "T/2"):
            rounds = []
            for rnd in range(16):
                ps = per_seed_dict([f"NULL-A({lab})", f"STATIC({lab})"], rnd * R, (rnd + 1) * R)
                c = boot.ci(ps, lambda d: pooled_mean(d, f"NULL-A({lab})") - pooled_mean(d, f"STATIC({lab})"))
                c["round"] = rnd
                c["ci_contains_zero"] = (c["lo"] is not None and c["lo"] <= 0 <= c["hi"])
                rounds.append(c)
            worst = max(rounds, key=lambda c: abs(c["point"]))
            null_a[lab] = {"rounds": rounds, "all_rounds_ci_contain_zero": all(c["ci_contains_zero"] for c in rounds),
                           "largest_abs_gain_round": worst,
                           "gain_ss_8T": boot.ci(per_seed_dict([f"NULL-A({lab})", f"STATIC({lab})"], 6 * T, 8 * T),
                                                 lambda d: pooled_mean(d, f"NULL-A({lab})") - pooled_mean(d, f"STATIC({lab})")),
                           "RESEL_L_gain_ss_8T": eps_ss[f"RESEL-L({lab})"]["8T"] - eps_ss[f"STATIC({lab})"]["8T"]}
            g = null_a[lab]["gain_ss_8T"]
            null_a[lab]["invalidation_rule_5_fires"] = bool(g["lo"] is not None and g["lo"] > 0 and
                                                            g["point"] >= 0.5 * null_a[lab]["RESEL_L_gain_ss_8T"])
        cell["S2_NULL_A"] = null_a
        cell["S2_bit_identity"] = {r: s["checks"]["bit_identity_all_rounds"] for r, s, _ in runs}
        cell["round0_identity_all"] = all(all(s["checks"]["round0_identity"].values()) for _, s, _ in runs)

        # S3: PHI decay
        phi_gain = {}
        for phi in ("0.0", "0.1", "0.25", "0.5", "1.0"):
            ps = per_seed_dict([f"PHI({phi},T/2)", "STATIC(T/2)"], 6 * T, 8 * T)
            phi_gain[phi] = boot.ci(ps, lambda d: pooled_mean(d, f"PHI({phi},T/2)") - pooled_mean(d, "STATIC(T/2)"))
        pts = [phi_gain[p]["point"] for p in ("0.0", "0.1", "0.25", "0.5", "1.0")]
        ps = per_seed_dict(["PHI(1.0,T/2)", "PHI(0.1,T/2)"], 6 * T, 8 * T)
        step = boot.ci(ps, lambda d: pooled_mean(d, "PHI(1.0,T/2)") - pooled_mean(d, "PHI(0.1,T/2)"))
        resc = {}
        for phi in ("0.1", "0.25", "0.5"):
            Up = int(round(float(phi) * 8 * T))
            e_phi = eps_ss[f"PHI({phi},T/2)"]["8T"]
            e_1 = pooled_mean(per_seed_dict(["PHI(1.0,T/2)"], Up - 2 * R, Up), "PHI(1.0,T/2)")
            resc[phi] = {"eps_resel(phi,8T)": e_phi, "eps_resel(1,phi*8T)": e_1, "window_for_phiU": [max(0, Up - 2 * R), Up],
                         "residual": abs(e_phi - e_1)}
        cell["S3_PHI"] = {"gain_ss_8T": phi_gain, "gain_points_in_phi_order": pts,
                          "non_decreasing": all(pts[i] <= pts[i + 1] + 1e-12 for i in range(4)),
                          "gain_0_exactly_zero": pts[0] == 0.0,
                          "gain1_minus_gain0.1": step, "gain1_minus_gain0.1_ci_above_zero": (step["lo"] is not None and step["lo"] > 0),
                          "time_rescaling_residual": resc}

        # S4: hit-rate exceedance (per-round sampled and exact)
        exc = {}
        for name in arms:
            cfg = runs[0][1]["arms"][name]["config"]
            if cfg["mode"] not in ("resel_lower", "resel_upper", "null_a", "phi"):
                continue
            per_round_p = []
            per_round_cov = []
            for rnd in range(len(runs[0][1]["arms"][name]["rounds"])):
                hits = sum(s["arms"][name]["rounds"][rnd]["hits"] for _, s, _ in runs)
                walks = sum(s["arms"][name]["rounds"][rnd]["walks"] for _, s, _ in runs)
                p, lo, hi = I.wilson(hits, walks)
                per_round_p.append({"round": rnd, "p": p, "wilson95": [lo, hi]})
                if "exact_coverage" in runs[0][1]["arms"][name]["rounds"][rnd]:
                    per_round_cov.append({"round": rnd,
                                          "exact_coverage_per_seed": [s["arms"][name]["rounds"][rnd]["exact_coverage"] for _, s, _ in runs],
                                          "oracle_share_per_seed": [s["arms"][name]["rounds"][rnd].get("oracle_share") for _, s, _ in runs]})
            e = {"pooled_hit_rate_per_round": per_round_p, "max_pooled_hit_rate": max(x["p"] for x in per_round_p)}
            if per_round_cov:
                e["exact_coverage_per_round"] = per_round_cov
                e["max_exact_minus_oracle_over_seeds_rounds"] = max(
                    max(c - o for c, o in zip(x["exact_coverage_per_seed"], x["oracle_share_per_seed"])) for x in per_round_cov)
                e["any_exact_exceedance"] = e["max_exact_minus_oracle_over_seeds_rounds"] > 1e-12
                e["max_sampled_minus_oracle_per_seed_round"] = max(
                    max((s["arms"][name]["rounds"][r]["hit_rate"] or 0) - s["arms"][name]["rounds"][r]["oracle_share"]
                        for r in range(len(s["arms"][name]["rounds"])) if "oracle_share" in s["arms"][name]["rounds"][r])
                    for _, s, _ in runs)
            else:
                e["exceeds_0.42"] = e["max_pooled_hit_rate"] > 0.42
                e["max_hit_rate_any_seed_round"] = max(max((r["hit_rate"] or 0) for r in s["arms"][name]["rounds"]) for _, s, _ in runs)
            exc[name] = e
        cell["S4_exceedance"] = exc
        # RESEL-L(T) trajectory vs oracle share / C_max
        traj = exc["RESEL-L(T)"]["pooled_hit_rate_per_round"]
        cell["RESEL_L_T_hit_rate_trajectory"] = {"first_round_p": traj[0]["p"], "last_round_p": traj[-1]["p"],
                                                 "MODELED_C_max": I.c_max(0.25 if al == "1/4" else 0.5)[1],
                                                 "oracle_top_T_share_per_seed": ([s["basins"]["top_T_share"] for _, s, _ in runs] if nb <= 24 else None),
                                                 "FROZEN_prediction": "from about 0.27 to within 0.03 of the exact top-T share by U = 16T, never above"}
        if nb <= 24:
            cell["RESEL_L_T_hit_rate_trajectory"]["last_round_exact_coverage_per_seed"] = \
                [s["arms"]["RESEL-L(T)"]["rounds"][-1]["exact_coverage"] for _, s, _ in runs]
            cell["RESEL_L_T_hit_rate_trajectory"]["last_round_gap_to_top_T_share_per_seed"] = \
                [s["basins"]["top_T_share"] - s["arms"]["RESEL-L(T)"]["rounds"][-1]["exact_coverage"] for _, s, _ in runs]

        # S5: r sweep
        rs = {}
        for lab in ("T", "T/2"):
            gains = {}
            for r in (2, 4, 8):
                A = f"RESEL-L({lab})" if r == 2 else f"RSWEEP-RESEL-L(r={r},{lab})"
                Bn = f"STATIC({lab})" if r == 2 else f"RSWEEP-STATIC(r={r},{lab})"
                ps = per_seed_dict([A, Bn], 6 * T, 8 * T)
                gains[str(r)] = boot.ci(ps, lambda d, A=A, Bn=Bn: pooled_mean(d, A) - pooled_mean(d, Bn))
            ps = per_seed_dict(["RESEL-L(" + lab + ")", "STATIC(" + lab + ")", f"RSWEEP-RESEL-L(r=4,{lab})", f"RSWEEP-STATIC(r=4,{lab})"], 6 * T, 8 * T)
            step24 = boot.ci(ps, lambda d: (pooled_mean(d, f"RESEL-L({lab})") - pooled_mean(d, f"STATIC({lab})"))
                             - (pooled_mean(d, f"RSWEEP-RESEL-L(r=4,{lab})") - pooled_mean(d, f"RSWEEP-STATIC(r=4,{lab})")))
            g2_, g4_, g8_ = gains["2"]["point"], gains["4"]["point"], gains["8"]["point"]
            rs[lab] = {"gain_ss_8T_by_r": gains, "strictly_decreasing": bool(g2_ > g4_ > g8_),
                       "gain_8_le_0.03": bool(g8_ <= 0.03), "step_2_to_4": step24,
                       "step_2_to_4_ci_above_zero": (step24["lo"] is not None and step24["lo"] > 0),
                       "static_hit_rate_by_r_pooled_last_round": {
                           str(r): (sum(s["arms"][f"STATIC({lab})" if r == 2 else f"RSWEEP-STATIC(r={r},{lab})"]["rounds"][-1]["hits"] for _, s, _ in runs) /
                                    sum(s["arms"][f"STATIC({lab})" if r == 2 else f"RSWEEP-STATIC(r={r},{lab})"]["rounds"][-1]["walks"] for _, s, _ in runs))
                           for r in (2, 4, 8)}}
        cell["S5_r_sweep"] = rs

        # S6: UPPER minus LOWER per round
        ul = {}
        for lab in ("T", "T/2"):
            rounds = []
            for rnd in range(16):
                ps = per_seed_dict([f"RESEL-U({lab})", f"RESEL-L({lab})"], rnd * R, (rnd + 1) * R)
                c = boot.ci(ps, lambda d: pooled_mean(d, f"RESEL-U({lab})") - pooled_mean(d, f"RESEL-L({lab})"))
                c["round"] = rnd
                rounds.append(c)
            ss = boot.ci(per_seed_dict([f"RESEL-U({lab})", f"RESEL-L({lab})"], 6 * T, 8 * T),
                         lambda d: pooled_mean(d, f"RESEL-U({lab})") - pooled_mean(d, f"RESEL-L({lab})"))
            ul[lab] = {"per_round": rounds, "gap_ss_8T": ss, "gap_ss_8T_below_0.05": ss["point"] < 0.05,
                       "max_point_after_round_4": max(c["point"] for c in rounds[4:]),
                       "FROZEN_prediction": "< 0.02 after round 4; S6 requires < 0.05 in steady state"}
        cell["S6_upper_minus_lower"] = ul

        # CAP retention
        capr = {}
        for lab in ("T", "T/2"):
            base = eps_ss[f"RESEL-L({lab})"]["8T"] - eps_ss[f"STATIC({lab})"]["8T"]
            capr[lab] = {"uncapped_gain": base}
            for c in ("4T", "2T"):
                g = eps_ss[f"CAP({c},{lab})"]["8T"] - eps_ss[f"STATIC({lab})"]["8T"]
                capr[lab][c] = {"gain": g, "retention": (g / base if base else None),
                                "S_peak_bits_per_seed": [s["arms"][f"CAP({c},{lab})"]["S_peak_bits"] for _, s, _ in runs]}
            capr[lab]["uncapped_S_peak_bits_per_seed"] = [s["arms"][f"RESEL-L({lab})"]["S_peak_bits"] for _, s, _ in runs]
            capr[lab]["FROZEN_prediction"] = "CAP(4T) retains >= 80%, CAP(2T) >= 60%"
        cell["CAP_retention"] = capr

        # STATIC2T, RHO, a=1/2 differential
        cell["STATIC2T"] = {"single_walk_hit_rate_pooled_all_rounds": (
            sum(r["hits"] for _, s, _ in runs for r in s["arms"]["STATIC2T"]["rounds"]) /
            sum(r["walks"] for _, s, _ in runs for r in s["arms"]["STATIC2T"]["rounds"])),
            "eps_ss_8T": eps_ss["STATIC2T"]["8T"], "MODELED": 0.32,
            "RESEL_L_T_last_round_hit_rate": traj[-1]["p"]}
        cell["RHO"] = {"eps_cum_16T": eps_cum["RHO"]["16T"], "FROZEN_prediction": "< 0.02"}
        cell["STATIC_T_single_walk_hit_rate_all_rounds"] = (
            sum(r["hits"] for _, s, _ in runs for r in s["arms"]["STATIC(T)"]["rounds"]) /
            sum(r["walks"] for _, s, _ in runs for r in s["arms"]["STATIC(T)"]["rounds"]))

        # RSWEEP-R (2^24)
        if nb == 24:
            rr = {}
            for lab_R, name in (("T/4", "RSWEEP-R(R=T/4,T/2)"), ("T", "RESEL-L(T/2)"), ("4T", "RSWEEP-R(R=4T,T/2)")):
                Rr = {"T/4": T // 4, "T": T, "4T": 4 * T}[lab_R]
                ps = per_seed_dict([name, "STATIC(T/2)"], 8 * T - 2 * Rr, 8 * T)
                rr[lab_R] = {"gain_ss_8T_window_2R": boot.ci(ps, lambda d, name=name: pooled_mean(d, name) - pooled_mean(d, "STATIC(T/2)")),
                             "reselection_int_ops_total_per_seed": [s["arms"][name]["reselection_int_ops_total"] for _, s, _ in runs],
                             "group_ops_total_per_seed": [s["arms"][name]["group_ops_total"] for _, s, _ in runs]}
            cell["RSWEEP_R"] = rr
            cell["HEUR_BLT7_regression_per_seed"] = {r: s.get("heur_blt7_regression") for r, s, _ in runs}

        # costs (MEASURED) and resources
        costs = {}
        for name in arms:
            costs[name] = {
                "L_mean_per_target_per_seed": [s["arms"][name]["L_mean_per_target"] for _, s, _ in runs],
                "L_mean_per_solved_target_per_seed": [s["arms"][name]["L_mean_per_solved_target"] for _, s, _ in runs],
                "restarts_total_per_seed": [s["arms"][name]["restarts_total"] for _, s, _ in runs],
                "restart_group_ops_total_per_seed": [s["arms"][name]["restart_group_ops_total"] for _, s, _ in runs],
                "lookups_total_per_seed": [s["arms"][name]["lookups_total"] for _, s, _ in runs],
                "reselection_int_ops_total_per_seed": [s["arms"][name]["reselection_int_ops_total"] for _, s, _ in runs],
                "reselection_ops_over_group_ops_mean_of_rounds": float(np.mean(
                    [r["reselection_ops_over_group_ops"] or 0 for _, s, _ in runs for r in s["arms"][name]["rounds"]])),
                "S_bits": runs[0][1]["arms"][name]["S_bits"],
                "S_peak_bits_per_seed": [s["arms"][name]["S_peak_bits"] for _, s, _ in runs],
                "capped_walk_fraction_used_per_seed": [s["arms"][name]["capped_walk_fraction_used"] for _, s, _ in runs],
                "capped_fraction_flag_gt_0.01": any(s["arms"][name]["capped_walk_fraction_used"] > 0.01 for _, s, _ in runs),
            }
        cell["MEASURED_costs"] = costs
        cell["MEASURED_pools"] = {r: s["pools"] for r, s, _ in runs}
        cell["MODELED"] = runs[0][1]["cost_table"]["MODELED"]
        cell["cycle_and_capped"] = {r: {"capped_fraction_all_online_walks": s["online_walks"]["capped_fraction_all_walks"],
                                        "cycle_mass_frac": s.get("basins", {}).get("cycle_mass_frac"),
                                        "capped_mass_frac": s.get("basins", {}).get("capped_mass_frac")} for r, s, _ in runs}
        # peak RSS reconciliation against analytic sizes
        analytic_bits = max(max(s["arms"][n]["S_peak_bits"] for n in arms) for _, s, _ in runs)
        cell["resources"] = {"peak_rss_bytes_per_run": [e["peak_rss_bytes"] for e in inventory if e["run_id"] in cell["runs"]],
                             "max_analytic_S_peak_bits": analytic_bits, "max_analytic_S_peak_bytes": analytic_bits / 8,
                             "note": "peak RSS is dominated by the exact basin arrays (N <= 2^24) and Python object overhead, not by S_peak"}
        out["cells"][key] = cell

        # ---- markdown
        md.append(f"## Cell {key} (T = {T}, seeds {cell['seeds']}, runs {cell['runs']})")
        md.append("| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |")
        md.append("|---|---|---|---|")
        for lab in ("4T", "8T", "16T"):
            d = diff[lab]
            md.append(f"| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U={lab} | {d['point']:.4f} | [{d['lo']:.4f}, {d['hi']:.4f}] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |")
            r_ = rho[lab]
            md.append(f"| rho_T({lab}) | {r_['point']:.3f}{(' (' + r_['censor'] + ')') if r_['censor'] else ''} | [{r_['lo']:.3f}, {r_['hi']:.3f}] | {cell['FROZEN_prediction_rho']['rho(' + lab + ')']} |")
        for lab in ("T", "T/2"):
            g = null_a[lab]["gain_ss_8T"]
            md.append(f"| NULL-A({lab}) gain at 8T | {g['point']:.4f} | [{g['lo']:.4f}, {g['hi']:.4f}] | within CI of zero every round: {null_a[lab]['all_rounds_ci_contain_zero']} |")
        for phi in ("0.0", "0.1", "0.25", "0.5", "1.0"):
            g = phi_gain[phi]
            md.append(f"| PHI({phi}) gain at 8T | {g['point']:.4f} | [{g['lo']:.4f}, {g['hi']:.4f}] | non-decreasing, gain(0)=0 |")
        for lab in ("T", "T/2"):
            for r in ("2", "4", "8"):
                g = rs[lab]["gain_ss_8T_by_r"][r]
                md.append(f"| gain(RESEL-L, {lab}) at r={r} | {g['point']:.4f} | [{g['lo']:.4f}, {g['hi']:.4f}] | strictly decreasing; gain(8) <= 0.03 |")
            g = ul[lab]["gap_ss_8T"]
            md.append(f"| UPPER - LOWER ({lab}) at 8T | {g['point']:.4f} | [{g['lo']:.4f}, {g['hi']:.4f}] | < 0.05 (S6); < 0.02 after round 4 |")
        e = cell["early_batch_penalty_first10pct_8T"]
        md.append(f"| early-batch penalty (first 10% of 8T) | {e['point']:.4f} | [{e['lo']:.4f}, {e['hi']:.4f}] | >= 0.08 |")
        md.append(f"| U_ss (margin 0.02) | {cell['U_ss_margin0.02']['pooled']} | per seed {cell['U_ss_margin0.02']['per_seed']} | [4T, 10T] |")
        md.append(f"| U* (margin 0.02) | {cell['U_star_margin0.02']['pooled']} | per seed {cell['U_star_margin0.02']['per_seed']} | [8T, 16T] or > 16T |")
        md.append(f"| STATIC2T single-walk hit rate | {cell['STATIC2T']['single_walk_hit_rate_pooled_all_rounds']:.4f} | - | MODELED 0.32 |")
        md.append(f"| STATIC(T) single-walk hit rate | {cell['STATIC_T_single_walk_hit_rate_all_rounds']:.4f} | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |")
        md.append(f"| RESEL-L(T) hit rate first -> last round | {traj[0]['p']:.4f} -> {traj[-1]['p']:.4f} | - | to within 0.03 of top-T share (MODELED C_max {cell['RESEL_L_T_hit_rate_trajectory']['MODELED_C_max']:.3f}) |")
        md.append(f"| RHO eps_cum(16T) | {eps_cum['RHO']['16T']:.4f} | - | < 0.02 |")
        for lab in ("T", "T/2"):
            for c in ("4T", "2T"):
                md.append(f"| CAP({c},{lab}) retention | {capr[lab][c]['retention'] if capr[lab][c]['retention'] is None else round(capr[lab][c]['retention'], 3)} | - | 4T >= 80%, 2T >= 60% |")
        md.append("")
        md.append(f"- Round-0 identity all arms all seeds: {cell['round0_identity_all']}; NULL-B / PHI(0) bit identity: {cell['S2_bit_identity']}")
        md.append(f"- S4 exceedance: " + "; ".join(
            f"{n}: " + (f"exact exceedance {e['any_exact_exceedance']} (max exact-oracle {e['max_exact_minus_oracle_over_seeds_rounds']:.4f}, max sampled-oracle {e['max_sampled_minus_oracle_per_seed_round']:.4f})"
                        if "any_exact_exceedance" in e else f"max pooled hit rate {e['max_pooled_hit_rate']:.4f}, exceeds 0.42: {e['exceeds_0.42']}")
            for n, e in exc.items() if n in ("RESEL-L(T)", "RESEL-L(T/2)", "RESEL-U(T)")))
        md.append("")

    # ---------------------------------------------------------------- Stage 3 curve arm (control (m) transfer check)
    if curve_runs:
        T = curve_runs[0][1]["params"]["T"]
        cid = curve_runs[0][1]["curve"]["curve_id"]
        cs = {"curve_id": cid, "runs": [r for r, _, _ in curve_runs], "seeds": [s["params"]["seeds"]["walk_key_seed"] for _, s, _ in curve_runs],
              "curve": {k: curve_runs[0][1]["curve"][k] for k in ("p", "a", "b", "N", "P", "field_bits")},
              "curve_verification_per_run": {r: s["curve"]["verification"]["verified"] for r, s, _ in curve_runs}}
        csol = {n: [np.asarray(raw["arms"][n]["solved"], dtype=np.float64) for _, _, raw in curve_runs]
                for n in curve_runs[0][1]["arms"]}
        cs["certificates"] = {r: {k: v for k, v in s["certificates"].items() if k != "per_arm"} for r, s, _ in curve_runs}
        cs["certificates_per_arm"] = {r: s["certificates"]["per_arm"] for r, s, _ in curve_runs}
        cs["pass_count_equals_solved_count_all_runs"] = all(s["certificates"]["pass_count_equals_solved_count"] for _, s, _ in curve_runs)
        cs["seeded_log_all_match_all_runs"] = all(s["certificates"]["seeded_log_all_match"] for _, s, _ in curve_runs)
        cs["round0_identity_all"] = all(all(s["checks"]["round0_identity"].values()) for _, s, _ in curve_runs)
        cs["eps_ss_8T_pooled"] = {n: float(np.concatenate([x[6 * T:8 * T] for x in csol[n]]).mean()) for n in csol}
        cs["eps_cum_8T_pooled"] = {n: float(np.concatenate([x[:8 * T] for x in csol[n]]).mean()) for n in csol}
        cps = [{n: csol[n][i][6 * T:8 * T] for n in csol} for i in range(len(curve_runs))]
        cs["diff_RESEL_L_T2_minus_STATIC_T_8T"] = boot.ci(cps, lambda d: pooled_mean(d, "RESEL-L(T/2)") - pooled_mean(d, "STATIC(T)"))
        cs["NULL_A_T2_gain_8T"] = boot.ci(cps, lambda d: pooled_mean(d, "NULL-A(T/2)") - pooled_mean(d, "STATIC(T/2)"))
        cs["RESEL_L_T_gain_8T"] = boot.ci(cps, lambda d: pooled_mean(d, "RESEL-L(T)") - pooled_mean(d, "STATIC(T)"))
        cs["RHO_collisions_eps_cum_8T"] = cs["eps_cum_8T_pooled"]["RHO"]
        if "basins" in curve_runs[0][1]:
            cs["basins_per_run"] = {r: {k: s["basins"][k] for k in ("survival_slope", "MODELED_borel_survival_slope_same_estimator",
                                                                    "top_T_share", "C_max_model", "top_T_share_over_C_max",
                                                                    "largest_basin_in_band", "cycle_mass_frac", "capped_mass_frac")}
                                    for r, s, _ in curve_runs}
            cs["basins_per_run"] = {r: {**v, "n_c_theta2_over_2": s["basins"]["cutoff"]["n_c_theta2_over_2"]}
                                    for (r, s, _), v in zip(curve_runs, cs["basins_per_run"].values())}
        # transfer check (m): curve vs generic 2^24 a=1/4, unpaired (different seed sets), stratified by run
        gen = cells.get((24, "1/4"))
        if gen:
            gsol = {n: [np.asarray(raw["arms"][n]["solved"], dtype=np.float64) for _, _, raw in gen] for n in ("STATIC(T)", "RESEL-L(T/2)")}
            transfer = {}
            for n in ("STATIC(T)", "RESEL-L(T/2)"):
                strata = ([{"v": x[6 * T:8 * T], "g": np.ones(2 * T)} for x in csol[n]] +
                          [{"v": x[6 * T:8 * T], "g": np.zeros(2 * T)} for x in gsol[n]])

                def stat(d):
                    cv = np.concatenate([e["v"][e["g"] > 0.5] for e in d])
                    gv = np.concatenate([e["v"][e["g"] < 0.5] for e in d])
                    return float(cv.mean() - gv.mean()) if len(cv) and len(gv) else float("nan")
                c = boot.ci(strata, stat)
                c["curve_eps_ss_8T"] = cs["eps_ss_8T_pooled"][n]
                c["generic_2^24_a=1/4_eps_ss_8T"] = float(np.concatenate([x[6 * T:8 * T] for x in gsol[n]]).mean())
                c["ci_contains_zero"] = (c["lo"] is not None and c["lo"] <= 0 <= c["hi"])
                transfer[n] = c
            cs["transfer_check_m_curve_minus_generic"] = transfer
        cs["MEASURED_costs"] = {r: s["cost_table"]["MEASURED"] for r, s, _ in curve_runs}
        cs["MODELED"] = curve_runs[0][1]["cost_table"]["MODELED"]
        out["stage3_curve"] = cs
        md.append(f"## Stage 3 curve arm {cid} (p = {cs['curve']['p']}, N = {cs['curve']['N']}, seeds {cs['seeds']}, runs {cs['runs']})")
        md.append(f"- certificates: pass count equals solved count in every run: {cs['pass_count_equals_solved_count_all_runs']}; "
                  f"seeded-log match in every run: {cs['seeded_log_all_match_all_runs']}; per run: "
                  + "; ".join(f"{r}: solved {v['solved_total']}, passed {v['passed']}, failed {v['failed']}" for r, v in cs["certificates"].items()))
        md.append(f"- eps_ss(8T) pooled: " + ", ".join(f"{n} {v:.4f}" for n, v in cs["eps_ss_8T_pooled"].items()))
        d = cs["diff_RESEL_L_T2_minus_STATIC_T_8T"]
        md.append(f"- RESEL-L(T/2) - STATIC(T) at 8T on the curve: {d['point']:.4f} [{d['lo']:.4f}, {d['hi']:.4f}] (3 seeds)")
        d = cs["NULL_A_T2_gain_8T"]
        md.append(f"- NULL-A(T/2) gain at 8T on the curve: {d['point']:.4f} [{d['lo']:.4f}, {d['hi']:.4f}]")
        if "transfer_check_m_curve_minus_generic" in cs:
            for n, c in cs["transfer_check_m_curve_minus_generic"].items():
                md.append(f"- transfer check (m) {n}: curve {c['curve_eps_ss_8T']:.4f} vs generic 2^24 a=1/4 {c['generic_2^24_a=1/4_eps_ss_8T']:.4f}; "
                          f"difference {c['point']:.4f} [{c['lo']:.4f}, {c['hi']:.4f}]; CI contains zero: {c['ci_contains_zero']}")
        md.append(f"- round-0 identity on the curve: {cs['round0_identity_all']}; RHO collisions eps_cum(8T) {cs['RHO_collisions_eps_cum_8T']:.4f} (no logarithm derivable, no certificate)")
        md.append("")
    else:
        out["stage3_curve"] = {"status": "NOT YET RUN" if "3" not in stages else "no completed_valid curve run found"}

    with open(os.path.join(args.outdir, "ci_tables.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    with open(os.path.join(args.outdir, "analysis.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    summary = {"params": {"kind": "analysis", "stages": sorted(stages), "resamples": args.resamples,
                          "bootstrap_calls": boot.count},
               "cells": sorted(out["cells"].keys()), "stage3_curve": out.get("stage3_curve", {}).get("status", "included"), "gates": {k: {"G2_pass": v["G2_fixture"]["G2_pass"],
                                                                  "G1_literal": v.get("G1_basin_law", {}).get("G1_literal_all_four")}
                                                              for k, v in gates.items()},
               "certificate": {"kind": "none"}, "headline_metrics": {}}
    for k, c in out["cells"].items():
        summary["headline_metrics"][k] = {"diff_8T": c["S1_diff_resel_T2_minus_static_T"]["8T"]["point"],
                                          "rho_8T": c["rho_T"]["8T"]["point"], "rho_16T": c["rho_T"]["16T"]["point"]}
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump({"note": "analysis run; raw inputs are the cited run directories", "inputs": [r for c in out["cells"].values() for r in c["runs"]]}, fh)
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())

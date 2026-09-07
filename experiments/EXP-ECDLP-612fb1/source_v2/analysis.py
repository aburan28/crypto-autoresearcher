"""STAGE 4v2 analysis run for EXP-ECDLP-612fb1 v2.

Reads every completed_valid v2 run under --runs-dir (ascan, generic n_bits in
{24,30}) and produces ci_tables.json + analysis.md in --outdir.  Observations
only; no hypothesis-level conclusion is drawn.

BINDING ORDER (item g): before ANY G1 verdict on a real cell is reported,
this run FIRST re-runs its own G1 aggregation against the two red team
permanent-negative-fixture seed sets (affine-xorshift, permutation) and
confirms (i) no exception when fit_cutoff returns None, (ii) G1 FAIL on
both.  Failing either is a STOPPING CONDITION: the run aborts before
reporting any real-cell G1/S1/F1 line.

Bootstrap: stratified by seed, BCa, class Boot -- copied verbatim from v1's
source/analysis.py (same code, same estimator; the bootstrap machinery is
NOT one of items (a)-(h) and is not amended).
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

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PERM_FIXTURE_ROOT = os.path.join(
    REPO, "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-90e7cf/results/j4_perm")
PERM_FIXTURE_KINDS = {
    "affine_xorshift": [f"RUN-RT-90e7cf-affine_xorshift-s{i}" for i in (1, 2, 3)],
    "permutation": [f"RUN-RT-90e7cf-permutation-s{i}" for i in (1, 2, 3)],
}


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


class Boot:
    """Stratified-by-seed paired bootstrap with BCa intervals (verbatim from
    v1's source/analysis.py; not one of items (a)-(h))."""

    def __init__(self, B: int, seed: int = 20260906):
        self.B = B
        self.rng = np.random.default_rng(seed)
        self.count = 0

    def ci(self, per_seed: list, stat, alpha: float = 0.05) -> dict:
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


# ------------------------------------------------------------------ item (g): G1 aggregation, None-guarded
def compute_g1(summaries: list) -> dict:
    """G1 basin-law aggregation with the RED TEAM None-guard (item g):
    fit_cutoff returning n_c = None is scored as OUTSIDE the [0.5, 2] band
    (G1 FAIL contribution), never raising an exception.  `summaries` is a
    list of per-seed summary.json dicts (each carrying a `basins` and a
    `fixture` block, exactly the schema v1's/v2's run_generic.py emit)."""
    per_seed = []
    for s in summaries:
        x = s["basins"]
        nc = x.get("cutoff", {}).get("n_c_theta2_over_2")   # None-guarded: .get(), never x["cutoff"]["n_c..."]
        per_seed.append({
            "seed": s["params"]["seeds"]["walk_key_seed"],
            "survival_slope_log_grid": x["survival_slope"],
            "n_c_theta2_over_2": nc,
            "top_T_share": x["top_T_share"], "C_max_model": x["C_max_model"],
            "top_T_share_over_C_max": x["top_T_share_over_C_max"],
            "static_T_exact_coverage": s["fixture"]["static_T_exact_coverage"],
            "static_below_top_share": bool(s["fixture"]["static_T_exact_coverage"] < x["top_T_share"]),
        })
    slope_ok = all(abs(e["survival_slope_log_grid"] + 0.5) <= 0.15 for e in per_seed)
    # None-guard (item g): a None cutoff is NOT in [0.5, 2] -- scored FAIL, never an exception.
    cutoff_ok = all((e["n_c_theta2_over_2"] is not None) and (0.5 <= e["n_c_theta2_over_2"] <= 2.0) for e in per_seed)
    top_ok = all(0.85 <= e["top_T_share_over_C_max"] <= 1.05 for e in per_seed)
    static_below_ok = all(e["static_below_top_share"] for e in per_seed)
    literal = bool(slope_ok and cutoff_ok and top_ok and static_below_ok)
    return {"per_seed": per_seed, "slope_within_0.15_all_seeds": slope_ok,
            "cutoff_in_[0.5,2]_all_seeds": cutoff_ok,
            "top_share_over_C_max_in_[0.85,1.05]_all_seeds": top_ok,
            "static_below_top_share_all_seeds": static_below_ok,
            "G1_literal_all_four": literal, "G1_verdict": "PASS" if literal else "FAIL"}


def run_permanent_fixture_check() -> dict:
    """item (g): re-run G1 aggregation against the two red team permanent
    negative fixtures BEFORE any real-cell G1 verdict is trusted.  Returns
    the check result; raises RuntimeError (a STOPPING CONDITION for STAGE
    4v2, per the contract's own invalidation rule) if either fixture is
    missing, if computing G1 raises an exception, or if either fixture
    scores G1 PASS instead of FAIL."""
    out = {}
    for kind, run_ids in PERM_FIXTURE_KINDS.items():
        summaries = []
        for rid in run_ids:
            sp = os.path.join(PERM_FIXTURE_ROOT, kind, rid, "summary.json")
            if not os.path.exists(sp):
                raise RuntimeError(f"STOPPING CONDITION (item g): permanent fixture summary missing: {sp}")
            summaries.append(json.load(open(sp)))
        try:
            g1 = compute_g1(summaries)
        except Exception as exc:  # noqa: BLE001 -- the exact case item (g) exists to prevent
            raise RuntimeError(
                f"STOPPING CONDITION (item g): G1 aggregation raised {type(exc).__name__}: {exc} "
                f"on permanent fixture '{kind}' -- the None-guard is missing or defective; repair before "
                f"any G1 verdict on a real cell is reported") from exc
        out[kind] = g1
        if g1["G1_verdict"] != "FAIL":
            raise RuntimeError(
                f"STOPPING CONDITION (item g): permanent fixture '{kind}' scored G1 {g1['G1_verdict']}, "
                f"not FAIL -- the analysis pipeline is unsound and its G1 verdict on any real cell may not "
                f"be reported as trustworthy until repaired")
    out["both_fixtures_scored_FAIL_no_exception"] = True
    out["reference_patch"] = ("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/"
                              "TASK-20260906-90e7cf/src/pipeline_perm/analysis.py.diff (red team's None-guard, "
                              "matched by this file's compute_g1 using .get() instead of [] on the cutoff dict)")
    return out


def rho_from_eps(eps_by_tsel: dict, target: float, T: int, grid_labels, grid_fracs):
    """T_resel/T by log-linear interpolation on grid_labels (v2:
    T_sel_grid_v2 = {0.65T, 0.75T} only, per item b's uncensoring
    requirement -- extrapolation OUTSIDE this grid is reported CENSORED,
    never silently extended)."""
    xs = np.log2(np.array(grid_fracs))
    ys = np.array([eps_by_tsel[l] for l in grid_labels])
    if ys[0] >= target:
        return float(2 ** xs[0]), f"<= {grid_labels[0]} (censored: outside T_sel_grid_v2)"
    for i in range(len(grid_labels) - 1):
        if ys[i] < target <= ys[i + 1] and ys[i + 1] > ys[i]:
            x = xs[i] + (target - ys[i]) / (ys[i + 1] - ys[i]) * (xs[i + 1] - xs[i])
            return float(2 ** x), None
    if ys[-1] < target:
        return float(2 ** xs[-1]), f">= {grid_labels[-1]} (censored: outside T_sel_grid_v2, extrapolation forbidden by item b)"
    return float(2 ** xs[-1]), "non-monotone grid (censored)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--stages", default="ascan,1v2,2v2")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--resamples", type=int, default=2000)
    args = ap.parse_args()
    stages = set(args.stages.split(","))
    boot = Boot(args.resamples)

    md = ["# EXP-ECDLP-612fb1 v2 STAGE 4v2 analysis run", "",
          "Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the",
          "frozen contract's formulas, quoted beside them and never mixed. No hypothesis-level conclusion",
          "is drawn; gate verdicts are reported in the contract's own gate language only.", ""]

    # ============================================================== item (g): PERMANENT NEGATIVE FIXTURE FIRST
    md.append("## Permanent negative fixture check (item g) -- MUST pass before any real-cell G1 verdict")
    fixture_check = run_permanent_fixture_check()   # raises (STOPPING CONDITION) on failure; never continues past this line unsound
    for kind, g1 in fixture_check.items():
        if kind in ("both_fixtures_scored_FAIL_no_exception", "reference_patch"):
            continue
        md.append(f"- {kind}: G1 verdict = **{g1['G1_verdict']}** (slope ok {g1['slope_within_0.15_all_seeds']}, "
                  f"cutoff ok {g1['cutoff_in_[0.5,2]_all_seeds']} [None-guarded], top-share ok "
                  f"{g1['top_share_over_C_max_in_[0.85,1.05]_all_seeds']}, static-below ok "
                  f"{g1['static_below_top_share_all_seeds']})")
    md.append(f"- Both fixtures scored G1 FAIL, no exception: {fixture_check['both_fixtures_scored_FAIL_no_exception']}")
    md.append("- The real-cell G1 verdicts below are therefore reportable as trustworthy per item (g).")
    md.append("")

    # ============================================================== load runs
    inventory = []
    ascan_runs = []
    cells = {}   # n_bits -> list of (run_id, summary, raw)
    for rid in sorted(os.listdir(args.runs_dir)):
        mp = os.path.join(args.runs_dir, rid, "manifest.yaml")
        sp = os.path.join(args.runs_dir, rid, "summary.json")
        if not (os.path.exists(mp) and os.path.exists(sp)):
            continue
        import yaml
        man = yaml.safe_load(open(mp))["run"]
        kind = man["inputs"]["parameters"].get("kind")
        if kind not in ("ascan", "generic"):
            continue
        s = json.load(open(sp))
        # v1's RUN-ECDLP-612fb1-001..037 also have kind == "generic" at the
        # SAME n_bits values (24, 30) but were produced by v1's source/ code
        # path (no G3_gate, no v2 stage marker); this analysis reads ONLY
        # v2 runs (source_v2/), never v1's, per the handoff's own binding
        # (v1's 37 runs are preserved unchanged and never re-scored by v2).
        if kind == "generic" and s.get("stage") not in ("1v2", "2v2"):
            continue
        if kind == "ascan":
            inventory.append({"run_id": rid, "status": man["status"], "kind": "ascan",
                              "seed": s["params"]["seed"], "stage": "0", "valid": man["result"]["valid"],
                              "invalid_reason": man["result"]["invalid_reason"],
                              "peak_rss_bytes": man["resources"]["peak_rss_bytes"], "wall_seconds": man["timing"]["wall_seconds"]})
            if "ascan" in stages and man["status"] == "completed_valid":
                raw = json.load(open(os.path.join(args.runs_dir, rid, "raw-result.json")))
                ascan_runs.append((rid, s, raw))
            continue
        nb = s["params"]["n_bits"]
        st = {24: "1v2", 30: "2v2"}.get(nb)
        inventory.append({"run_id": rid, "status": man["status"], "n_bits": nb, "a": s["params"]["a"],
                          "seed": s["params"]["seeds"]["walk_key_seed"], "stage": st, "valid": man["result"]["valid"],
                          "invalid_reason": man["result"]["invalid_reason"],
                          "peak_rss_bytes": man["resources"]["peak_rss_bytes"],
                          "wall_seconds": man["timing"]["wall_seconds"]})
        if st not in stages or man["status"] != "completed_valid":
            continue
        raw = json.load(open(os.path.join(args.runs_dir, rid, "raw-result.json")))
        cells.setdefault(nb, []).append((rid, s, raw))

    out = {"stages_requested": sorted(stages), "run_inventory": inventory,
          "permanent_negative_fixture_check": fixture_check,
          "bootstrap": {"method": "stratified-by-seed paired bootstrap, BCa", "resamples": args.resamples,
                        "code": "experiments/EXP-ECDLP-612fb1/source_v2/analysis.py class Boot"},
          "stage0_ascan": {}, "cells": {}}

    # ============================================================== STAGE 0: a-scan table (reported FIRST, item h)
    md.append("## STAGE 0: a-scan (item h) -- reported before any STAGE 1v2/2v2 cell is interpreted")
    if ascan_runs:
        a_values = sorted(set(a for _, s, _ in ascan_runs for a in [round(x, 6) for x in s["params"]["a_scan_grid"]]))
        r_grid = ascan_runs[0][1]["params"]["r_grid"]
        seeds = sorted(s["params"]["seed"] for _, s, _ in ascan_runs)
        table = {}
        for a in a_values:
            key = f"a={a:.6f}"
            per_r = {}
            for r in r_grid:
                vals = [s["cells"][key]["static_by_r"][str(r)]["rho_ORACLE(a,r)"] for _, s, _ in ascan_runs if key in s["cells"]]
                per_r[str(r)] = {"rho_ORACLE_mean_over_seeds": float(np.mean(vals)) if vals else None,
                                 "rho_ORACLE_per_seed": vals,
                                 "top_share_v2_grid_mean": {lab: float(np.mean([s["cells"][key]["top_share"][lab] for _, s, _ in ascan_runs]))
                                                            for lab in ("0.65T", "0.75T")}}
            table[key] = {"a": a, "by_r": per_r}
        out["stage0_ascan"] = {"a_grid": a_values, "r_grid": r_grid, "seeds": seeds, "table": table}
        # ordering check
        ordering = {}
        for r in r_grid:
            v14 = table["a=0.250000"]["by_r"][str(r)]["rho_ORACLE_mean_over_seeds"]
            v12 = table["a=0.500000"]["by_r"][str(r)]["rho_ORACLE_mean_over_seeds"]
            ordering[str(r)] = {"rho_ORACLE(a=1/4)": v14, "rho_ORACLE(a=1/2)": v12,
                                "F6_v2_ordering_holds": bool(v14 < v12) if (v14 is not None and v12 is not None) else None}
        out["stage0_ascan"]["ordering_check_F6_v2"] = ordering
        md.append(f"- seeds: {seeds}; a-grid: {a_values}; r-grid: {r_grid}")
        md.append("| a | " + " | ".join(f"rho_ORACLE(r={r})" for r in r_grid) + " |")
        md.append("|---|" + "---|" * len(r_grid))
        for a in a_values:
            key = f"a={a:.6f}"
            md.append(f"| {a:.4f} | " + " | ".join(
                f"{table[key]['by_r'][str(r)]['rho_ORACLE_mean_over_seeds']:.4f}" for r in r_grid) + " |")
        md.append("")
        md.append("### F6_v2 ordering check: rho_ORACLE(a=1/4, r) < rho_ORACLE(a=1/2, r)")
        for r, v in ordering.items():
            md.append(f"- r={r}: rho_ORACLE(1/4)={v['rho_ORACLE(a=1/4)']:.4f} vs "
                      f"rho_ORACLE(1/2)={v['rho_ORACLE(a=1/2)']:.4f} -> holds: {v['F6_v2_ordering_holds']}")
        md.append("")
    else:
        out["stage0_ascan"] = {"status": "NOT YET RUN or not requested in --stages"}
        md.append("- STATUS: NOT YET RUN or not requested in --stages. No STAGE 1v2/2v2 cell below may be "
                  "interpreted for S1_v2/F1_v2 until this table is present (contract stopping-rule ordering).")
    md.append("")

    stage0_present = bool(ascan_runs)

    # ============================================================== gates (G1 [reused from v1's own 2^20 runs if present], G2, G3)
    md.append("## Gates G2 and G3 per N (reported before that N's RESEL-L S1/F1 lines)")
    T_SEL_LABELS_V2 = ["0.65T", "0.75T"]
    T_FRACS_V2 = [0.65, 0.75]
    gates = {}
    for nb, runs in sorted(cells.items()):
        seeds = sorted(s["params"]["seeds"]["walk_key_seed"] for _, s, _ in runs)
        T = runs[0][1]["params"]["T"]
        N = runs[0][1]["params"]["N"]
        key = f"2^{nb}"
        g = {"seeds": seeds, "n_runs": len(runs), "seed_policy_ok": seeds == [1, 2, 3, 4, 5]}
        # G2 (unchanged)
        steps = sum(s["fixture"]["total_steps"] for _, s, _ in runs)
        succ = sum(s["fixture"]["successes"] for _, s, _ in runs)
        cost = steps / succ / math.sqrt(N / T)
        Ps = [s["fixture"]["scaled_precomputation"] for _, s, _ in runs]
        ref = {"cost": 1.79, "tol": 0.18, "P_range": [1.05, 1.40]}
        g2 = {"MEASURED_scaled_main_cost_pooled": cost, "MEASURED_scaled_precomputation_mean": float(np.mean(Ps)),
              "PUBLISHED_scaled_main_cost": ref["cost"], "tolerance": ref["tol"],
              "cost_within_tolerance": bool(abs(cost - ref["cost"]) <= ref["tol"])}
        g2["precomputation_within_range"] = bool(ref["P_range"][0] <= np.mean(Ps) <= ref["P_range"][1])
        g2["G2_pass"] = bool(g2["cost_within_tolerance"] and g2["precomputation_within_range"])
        g["G2_fixture"] = g2
        # G3 (item a): per T_sel cell, aggregate the per-seed g3_pass flags this run already computed
        g3 = {}
        for lab in T_SEL_LABELS_V2:
            flags = [s["G3_gate"][lab].get("g3_pass_this_seed", s["G3_gate"][lab].get("g3_pass_this_seed_informational"))
                     for _, s, _ in runs]
            n_pass = sum(bool(f) for f in flags)
            margins = [s["G3_gate"][lab].get("margin", s["G3_gate"][lab].get("margin_informational")) for _, s, _ in runs]
            binding = (nb == 24)
            g3[lab] = {"per_seed_pass": flags, "n_pass_of_5": n_pass, "margins_per_seed": margins,
                      "G3_verdict": ("PASS" if n_pass >= 4 else "FAIL") if binding else
                                    ("PASS (informational)" if n_pass >= 4 else "FAIL (informational)"),
                      "binding": binding,
                      "reading": runs[0][1]["G3_gate"][lab]["reading"]}
        g["G3_gate"] = g3
        gates[key] = g
        md.append(f"### {key}: seeds {seeds}")
        md.append(f"- G2 fixture: MEASURED scaled main cost {cost:.3f} vs PUBLISHED {ref['cost']} +/- {ref['tol']} "
                  f"-> within: {g2['cost_within_tolerance']}; G2 pass: {g2['G2_pass']}")
        for lab in T_SEL_LABELS_V2:
            c = g3[lab]
            md.append(f"- G3({lab}) [{'BINDING' if c['binding'] else 'INFORMATIONAL'}]: {c['n_pass_of_5']}/5 seeds pass "
                      f"(margins {['%.4f' % m if m is not None else None for m in c['margins_per_seed']]}) -> "
                      f"**{c['G3_verdict']}**")
    out["gates"] = gates
    md.append("")

    # ============================================================== per-cell S1_v2/S2_v2/F1_v2 (only after G3 above)
    for nb, runs in sorted(cells.items()):
        key = f"2^{nb}"
        T = runs[0][1]["params"]["T"]
        R = T
        arms = list(runs[0][1]["arms"].keys())
        sol = {name: [np.asarray(raw["arms"][name]["solved"], dtype=np.float64) for _, _, raw in runs] for name in arms}
        U_grid = {"4T": 4 * T, "8T": 8 * T, "16T": 16 * T}
        cell = {"T": T, "seeds": [s["params"]["seeds"]["walk_key_seed"] for _, s, _ in runs], "runs": [r for r, _, _ in runs]}

        def per_seed_dict(names, u_lo, u_hi):
            return [{n: sol[n][i][max(0, u_lo):u_hi] for n in names} for i in range(len(runs))]

        eps_ss = {name: {lab: pooled_mean(per_seed_dict([name], U - 2 * R, U), name) for lab, U in U_grid.items()} for name in arms}
        eps_cum = {name: {lab: pooled_mean(per_seed_dict([name], 0, U), name) for lab, U in U_grid.items()} for name in arms}
        cell["eps_ss_pooled"] = eps_ss
        cell["eps_cum_pooled"] = eps_cum

        # non-vacuity guard (item b), a fixed property of this cell (not per T_sel)
        rho_eps_ss = eps_ss["RHO"]["8T"]
        static_T_eps_ss = eps_ss["STATIC(T)"]["8T"]
        nvg_gap = static_T_eps_ss - rho_eps_ss
        nvg = {"STATIC(T)_eps_ss_8T": static_T_eps_ss, "RHO_eps_ss_8T": rho_eps_ss, "gap": nvg_gap,
              "STATIC_T_ge_0.5": bool(static_T_eps_ss >= 0.5),
              "CI_separated_above_RHO_by_ge_0.30_point_estimate_check": bool(nvg_gap >= 0.30),
              "holds": bool(static_T_eps_ss >= 0.5 and nvg_gap >= 0.30)}
        cell["non_vacuity_guard_item_b"] = nvg

        per_tsel = {}
        for lab in T_SEL_LABELS_V2:
            g3v = gates[key]["G3_gate"][lab]
            g3_pass = g3v["G3_verdict"].startswith("PASS")
            entry = {"G3_verdict": g3v["G3_verdict"]}
            names = [f"RESEL-L({lab})", "STATIC(T)"]
            for lab2 in ("0.65T", "0.75T"):
                if lab2 not in names:
                    pass
            u8_diff = boot.ci(per_seed_dict([f"RESEL-L({lab})", "STATIC(T)"], 8 * T - 2 * R, 8 * T),
                              lambda d, lab=lab: pooled_mean(d, f"RESEL-L({lab})") - pooled_mean(d, "STATIC(T)"))
            u16_diff = boot.ci(per_seed_dict([f"RESEL-L({lab})", "STATIC(T)"], 16 * T - 2 * R, 16 * T),
                               lambda d, lab=lab: pooled_mean(d, f"RESEL-L({lab})") - pooled_mean(d, "STATIC(T)"))
            entry["diff_8T"] = u8_diff
            entry["diff_16T"] = u16_diff
            # rho_T(U): interpolate on {0.65T, 0.75T} ONLY (item b uncensoring)
            e0_8T = {l2: eps_ss[f"RESEL-L({l2})"]["8T"] for l2 in T_SEL_LABELS_V2}
            e0_16T = {l2: eps_ss[f"RESEL-L({l2})"]["16T"] for l2 in T_SEL_LABELS_V2}
            rho_8T, censor_8T = rho_from_eps(e0_8T, static_T_eps_ss, T, T_SEL_LABELS_V2, T_FRACS_V2)
            rho_16T, censor_16T = rho_from_eps(e0_16T, eps_ss["STATIC(T)"]["16T"], T, T_SEL_LABELS_V2, T_FRACS_V2)
            entry["rho_T_8T"] = {"point": rho_8T, "censor": censor_8T}
            entry["rho_T_16T"] = {"point": rho_16T, "censor": censor_16T}
            # rho_ORACLE beside rho_T (item d), exact only at n_bits<=24
            if nb <= 24:
                orc = runs[0][1]["basins"]["top_share_v2_grid"][lab]
                entry["rho_ORACLE_this_Tsel_exact_top_share"] = orc
            # tol = 0.05 * (STATIC(T) - RHO) gap (item b, relative)
            tol = 0.05 * nvg_gap
            entry["tol_relative_item_b"] = tol
            uncensored = (censor_8T is None)
            if not g3_pass:
                entry["S1_v2"] = "UNTESTABLE (G3 FAIL at this cell -- premise ceiling-infeasible, NOT a negative result)"
            elif not nvg["holds"]:
                entry["S1_v2"] = "NOT EVALUABLE (non-vacuity guard fails on this cell)"
            elif not uncensored:
                entry["S1_v2"] = f"NOT EVALUABLE (rho_T(8T) censored: {censor_8T}; crossing lies outside T_sel_grid_v2)"
            else:
                met = bool(u8_diff["hi"] is not None and u8_diff["hi"] >= 0 and u8_diff["point"] >= -tol)
                entry["S1_v2"] = "MET" if met else "NOT MET"
            # F1_v2: only evaluated where G3 passes and non-vacuity holds
            if g3_pass and nvg["holds"]:
                f1_fires = bool(u16_diff["hi"] is not None and u16_diff["hi"] < 0 and rho_16T > 0.85)
                entry["F1_v2"] = "FIRES" if f1_fires else "does not fire"
            else:
                entry["F1_v2"] = "UNTESTABLE (G3 or non-vacuity guard fails)"
            # frontier tuple (item d) -- the ONLY permitted headline form
            arm_name = f"RESEL-L({lab})"
            cap_name = f"CAP(2T,{lab})"
            S_peak = int(np.mean([s["arms"][arm_name]["S_peak_bits"] for _, s, _ in runs]))
            S_bits = runs[0][1]["arms"][arm_name]["S_bits"]
            P_group_ops = runs[0][1]["pools"]["2"]["P_group_ops"]
            L_mean = float(np.mean([s["arms"][arm_name]["L_mean_per_target"] for _, s, _ in runs]))
            early_pen = boot.ci(per_seed_dict([f"RESEL-L({lab})", "STATIC(T)"], 0, int(0.1 * 8 * T)),
                                lambda d, lab=lab: pooled_mean(d, "STATIC(T)") - pooled_mean(d, f"RESEL-L({lab})"))
            entry["frontier_tuple_item_d"] = {
                "T_sel_over_T": T_FRACS_V2[T_SEL_LABELS_V2.index(lab)],
                "S_peak_over_T_bits": S_peak / T,
                "S_bits": S_bits, "S_peak_bits": S_peak,
                "P_over_sqrt_NT": P_group_ops / math.sqrt(runs[0][1]["params"]["N"] * T),
                "L_per_target": L_mean,
                "eps_ss_8T": eps_ss[arm_name]["8T"], "eps_cum_8T": eps_cum[arm_name]["8T"],
                "U": "8T", "early_batch_penalty_first10pct_8T": early_pen["point"],
            }
            # CAP retention with per-round S_peak<=c verified (item f)
            cap_ok_per_seed = [s["arms"][cap_name]["cap_S_peak_honest_every_round"] for _, s, _ in runs]
            cap_speak = [s["arms"][cap_name]["S_peak_bits"] for _, s, _ in runs]
            base_gain = eps_ss[arm_name]["8T"] - static_T_eps_ss
            cap_gain = eps_ss[cap_name]["8T"] - static_T_eps_ss
            entry["CAP_2T_retention_item_f"] = {
                "S_peak_bits_per_seed": cap_speak, "S_peak_le_c_every_round_all_seeds": all(cap_ok_per_seed),
                "cap_c_bits": 2 * T * runs[0][1]["params"]["bits_per_pool_entry"],
                "uncapped_gain": base_gain, "capped_gain": cap_gain,
                "retention": (cap_gain / base_gain if base_gain else None),
            }
            # HEUR-BLT-7 corrected (item e), n_bits==24 only
            if nb == 24:
                entry["HEUR_BLT7_v2_per_seed"] = [s.get("heur_blt7_regression_v2", {}).get(lab) for _, s, _ in runs]
            per_tsel[lab] = entry
        cell["per_T_sel"] = per_tsel

        # S2_v2 (item c, one-sided) -- every round, every T_sel
        s2 = {}
        for lab in T_SEL_LABELS_V2:
            rounds = []
            for rnd in range(16):
                ps = per_seed_dict([f"NULL-A({lab})", f"STATIC({lab})"], rnd * R, (rnd + 1) * R)
                c = boot.ci(ps, lambda d, lab=lab: pooled_mean(d, f"NULL-A({lab})") - pooled_mean(d, f"STATIC({lab})"))
                gain_resel = eps_ss[f"RESEL-L({lab})"]["8T"] - eps_ss[f"STATIC({lab})"]["8T"] if rnd == 7 else None
                c["round"] = rnd
                c["ci_separated_above_zero"] = bool(c["lo"] is not None and c["lo"] > 0)
                rounds.append(c)
            gain_ss = boot.ci(per_seed_dict([f"NULL-A({lab})", f"STATIC({lab})"], 6 * T, 8 * T),
                              lambda d, lab=lab: pooled_mean(d, f"NULL-A({lab})") - pooled_mean(d, f"STATIC({lab})"))
            resel_gain_ss = eps_ss[f"RESEL-L({lab})"]["8T"] - eps_ss[f"STATIC({lab})"]["8T"]
            s2_met_every_round = all(
                (not r["ci_separated_above_zero"]) for r in rounds) and (
                abs(gain_ss["point"]) <= 0.5 * abs(resel_gain_ss) if resel_gain_ss else False)
            s2[lab] = {"rounds": rounds, "gain_ss_8T": gain_ss, "RESEL_L_gain_ss_8T": resel_gain_ss,
                      "perturbation_relative_to_STATIC_eps_ss": abs(gain_ss["point"]) / eps_ss[f"STATIC({lab})"]["8T"]
                      if eps_ss[f"STATIC({lab})"]["8T"] else None,
                      "S2_v2_MET": bool(s2_met_every_round)}
        cell["S2_v2_one_sided_item_c"] = s2
        cell["round0_identity_all"] = all(all(s["checks"]["round0_identity"].values()) for _, s, _ in runs)

        out["cells"][key] = cell
        md.append(f"## Cell {key} (T={T}, seeds {cell['seeds']}, runs {cell['runs']})")
        md.append(f"- non-vacuity guard (item b): STATIC(T) eps_ss(8T)={nvg['STATIC(T)_eps_ss_8T']:.4f} "
                  f">= 0.5: {nvg['STATIC_T_ge_0.5']}; gap to RHO = {nvg['gap']:.4f} >= 0.30: "
                  f"{nvg['CI_separated_above_RHO_by_ge_0.30_point_estimate_check']}; HOLDS: {nvg['holds']}")
        for lab in T_SEL_LABELS_V2:
            e = per_tsel[lab]
            md.append(f"### T_sel = {lab}")
            md.append(f"- G3 (item a): {e['G3_verdict']}")
            d8 = e["diff_8T"]
            md.append(f"- eps_ss(RESEL-L({lab})) - eps_ss(STATIC(T)) at 8T: {d8['point']:.4f} [{d8['lo']:.4f}, {d8['hi']:.4f}]"
                      if d8["lo"] is not None else f"- diff 8T: {d8['point']} (undefined CI)")
            md.append(f"- rho_T(8T): {e['rho_T_8T']['point']:.4f}" + (f" ({e['rho_T_8T']['censor']})" if e['rho_T_8T']['censor'] else "")
                      + (f"; rho_ORACLE(this T_sel exact top share): {e.get('rho_ORACLE_this_Tsel_exact_top_share')}" if nb <= 24 else ""))
            md.append(f"- S1_v2: **{e['S1_v2']}**")
            md.append(f"- F1_v2: **{e['F1_v2']}**")
            ft = e["frontier_tuple_item_d"]
            md.append(f"- FRONTIER TUPLE (item d, headline discipline): T_sel/T={ft['T_sel_over_T']}, "
                      f"S_peak/T(bits)={ft['S_peak_over_T_bits']:.1f}, P/sqrt(NT)={ft['P_over_sqrt_NT']:.4f}, "
                      f"L/target={ft['L_per_target']:.2f}, eps_ss(8T)={ft['eps_ss_8T']:.4f}, "
                      f"eps_cum(8T)={ft['eps_cum_8T']:.4f}, early-batch penalty={ft['early_batch_penalty_first10pct_8T']:.4f}")
            capr = e["CAP_2T_retention_item_f"]
            md.append(f"- CAP(2T,{lab}) retention (item f): S_peak_bits per seed {capr['S_peak_bits_per_seed']} "
                      f"(cap = {capr['cap_c_bits']} bits); S_peak<=c every round all seeds: "
                      f"{capr['S_peak_le_c_every_round_all_seeds']}; retention: "
                      f"{capr['retention'] if capr['retention'] is None else round(capr['retention'], 3)}")
            s2e = s2[lab]
            md.append(f"- S2_v2 (one-sided, item c): gain_ss(8T)={s2e['gain_ss_8T']['point']:.4f} "
                      f"[{s2e['gain_ss_8T']['lo']}, {s2e['gain_ss_8T']['hi']}]; RESEL-L gain={s2e['RESEL_L_gain_ss_8T']:.4f}; "
                      f"perturbation/STATIC eps_ss = {s2e['perturbation_relative_to_STATIC_eps_ss']}; "
                      f"S2_v2 MET: **{s2e['S2_v2_MET']}**")
        md.append("")

    with open(os.path.join(args.outdir, "ci_tables.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    with open(os.path.join(args.outdir, "analysis.md"), "w") as fh:
        fh.write("\n".join(md) + "\n")
    summary = {"params": {"kind": "analysis", "stages": sorted(stages), "resamples": args.resamples,
                          "bootstrap_calls": boot.count},
               "permanent_fixture_check_passed": fixture_check["both_fixtures_scored_FAIL_no_exception"],
               "stage0_ascan_present": stage0_present,
               "cells": sorted(out["cells"].keys()),
               "gates": {k: {"G2_pass": v["G2_fixture"]["G2_pass"],
                            "G3": {lab: v["G3_gate"][lab]["G3_verdict"] for lab in T_SEL_LABELS_V2}}
                        for k, v in gates.items()},
               "certificate": {"kind": "none"}, "headline_metrics": {}}
    for k, c in out["cells"].items():
        summary["headline_metrics"][k] = {lab: {"S1_v2": c["per_T_sel"][lab]["S1_v2"], "F1_v2": c["per_T_sel"][lab]["F1_v2"]}
                                          for lab in T_SEL_LABELS_V2}
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=float)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump({"note": "analysis run; raw inputs are the cited run directories",
                   "inputs": [r for c in out["cells"].values() for r in c["runs"]]}, fh)
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())

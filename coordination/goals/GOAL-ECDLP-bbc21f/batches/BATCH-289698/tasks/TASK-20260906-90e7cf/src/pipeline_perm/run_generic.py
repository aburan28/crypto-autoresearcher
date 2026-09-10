"""One generic cell of EXP-ECDLP-612fb1: (N, a, seed).

Order inside the run is the contract's gate order: exact basins and the G1
quantities (N <= 2^24), then the G2 fixture for STATIC(T), then every arm.
Writes raw-result.json, summary.json, cost_table.json and (N <= 2^24) the
compressed exact basin histogram into --outdir.  Observations only.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402


def log(msg: str) -> None:
    print(msg, flush=True)


def build_arms(P: I.Params, exact: bool) -> list:
    T = P.T
    grid = {"T/4": T // 4, "T/2": T // 2, "3T/4": 3 * T // 4, "T": T}
    arms = []
    for lab, ts in grid.items():
        arms.append(I.ArmConfig(name=f"STATIC({lab})", mode="static", t_sel=ts))
    arms.append(I.ArmConfig(name="STATIC2T", mode="static2t", t_sel=2 * T))
    arms.append(I.ArmConfig(name="RHO", mode="rho", t_sel=0))
    for lab, ts in grid.items():
        arms.append(I.ArmConfig(name=f"RESEL-L({lab})", mode="resel_lower", t_sel=ts, twin=f"STATIC({lab})"))
    for lab in ("T", "T/2"):
        arms.append(I.ArmConfig(name=f"RESEL-U({lab})", mode="resel_upper", t_sel=grid[lab], twin=f"STATIC({lab})"))
    for lab in ("T", "T/2"):
        arms.append(I.ArmConfig(name=f"NULL-A({lab})", mode="null_a", t_sel=grid[lab], twin=f"STATIC({lab})"))
    for lab in ("T", "T/2"):
        arms.append(I.ArmConfig(name=f"NULL-B({lab})", mode="null_b", t_sel=grid[lab], twin=f"STATIC({lab})"))
    for phi in (0.0, 0.1, 0.25, 0.5, 1.0):
        arms.append(I.ArmConfig(name=f"PHI({phi},T/2)", mode="phi", t_sel=grid["T/2"], phi=phi, twin="STATIC(T/2)"))
    for r in (4, 8):
        for lab in ("T", "T/2"):
            arms.append(I.ArmConfig(name=f"RSWEEP-STATIC(r={r},{lab})", mode="static", t_sel=grid[lab], r=r))
            arms.append(I.ArmConfig(name=f"RSWEEP-RESEL-L(r={r},{lab})", mode="resel_lower", t_sel=grid[lab], r=r,
                                    twin=f"RSWEEP-STATIC(r={r},{lab})"))
    for c_lab, c in (("4T", 4 * T), ("2T", 2 * T)):
        for lab in ("T", "T/2"):
            arms.append(I.ArmConfig(name=f"CAP({c_lab},{lab})", mode="resel_lower", t_sel=grid[lab], pool_cap=c,
                                    twin=f"STATIC({lab})"))
    if P.n_bits == 24:
        for r_lab, R in (("T/4", T // 4), ("4T", 4 * T)):
            arms.append(I.ArmConfig(name=f"RSWEEP-R(R={r_lab},T/2)", mode="resel_lower", t_sel=grid["T/2"], R=R,
                                    twin="STATIC(T/2)"))
    if exact:
        for lab, ts in grid.items():
            arms.append(I.ArmConfig(name=f"ORACLE({lab})", mode="oracle", t_sel=ts))
    return arms


def eps_window(solved: np.ndarray, u_lo: int, u_hi: int) -> float:
    u_lo = max(0, u_lo)
    if u_hi <= u_lo:
        return float("nan")
    return float(solved[u_lo:u_hi].mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-bits", type=int, required=True)
    ap.add_argument("--a", type=str, required=True, help="1/4 or 1/2")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    a = {"1/4": 0.25, "1/2": 0.5}[args.a]
    P = I.Params(n_bits=args.n_bits, a=a, seed=args.seed)
    exact = P.n_bits <= 24
    t0 = time.time()
    log(f"[cell] N=2^{P.n_bits} a={args.a} seed={P.seed} T={P.T} W={P.W:.4f} cap={P.cap} U_max={P.U_max}")
    log(f"[params] {json.dumps(P.describe())}")

    summary: dict = {"params": P.describe(), "certificate": {"kind": "none",
                     "note": "generic instrument: nothing is solved or certified"}}
    raw: dict = {"params": P.describe(), "certificate": {"kind": "none"}}

    # ------------------------------------------------------------------ basins
    basins = None
    oracle_share = None
    if exact:
        tb = time.time()
        basins = I.exact_basins(P)
        sizes = basins.size
        ndp = len(sizes)
        top = {P.T // 4: basins.top_share(P.T // 4), P.T // 2: basins.top_share(P.T // 2),
               3 * P.T // 4: basins.top_share(3 * P.T // 4), P.T: basins.top_share(P.T),
               2 * P.T: basins.top_share(2 * P.T)}
        oracle_share = top
        W2 = P.W ** 2
        ref = I.borel_survival(1 - P.theta, int(min(400 * W2, P.N)))
        slope, npts = I.survival_slope(sizes, 10, int(W2 / 4))
        slope_int, npts_int = I.survival_slope(sizes, 10, int(W2 / 4), grid="int")
        slope_ref, _ = I.survival_slope(None, 10, int(W2 / 4), ref_survival=ref)
        slope_ref_int, _ = I.survival_slope(None, 10, int(W2 / 4), grid="int", ref_survival=ref)
        cut = I.fit_cutoff(sizes, P.theta, int(W2 / 4))
        cut_ref = I.fit_cutoff(sizes, P.theta, int(W2 / 4), ref_survival=ref)
        probe_n = [n for n in (10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000) if n <= int(sizes.max())]
        srt_sizes = np.sort(sizes)
        surv_emp = [(ndp - int(np.searchsorted(srt_sizes, n, side="left"))) / ndp for n in probe_n]
        surv_ref = [float(ref[n - 1]) for n in probe_n]
        xstar, cmax = I.c_max(P.a)
        m_samples = int(round(P.N / P.W))
        band = I.borel_max_band(1 - P.theta, m_samples, int(min(400 * W2, P.N)))
        largest = int(sizes.max())
        hist_vals, hist_counts = np.unique(sizes, return_counts=True)
        g1 = {
            "n_dps": int(ndp),
            "cycle_mass": basins.cycle_mass, "cycle_mass_frac": basins.cycle_mass / P.N,
            "capped_mass": basins.capped_mass, "capped_mass_frac": basins.capped_mass / P.N,
            "survival_slope": slope, "survival_slope_points": npts,
            "survival_slope_estimator": "least squares of log S(n) on log n over 60 log-spaced integers (primary)",
            "survival_slope_int_grid": slope_int, "survival_slope_int_grid_points": npts_int,
            "survival_slope_range": [10, int(W2 / 4)],
            "survival_slope_within_0.15_of_-0.5": bool(abs(slope + 0.5) <= 0.15),
            "survival_slope_int_grid_within_0.15_of_-0.5": bool(abs(slope_int + 0.5) <= 0.15),
            "MODELED_borel_survival_slope_same_estimator": slope_ref,
            "MODELED_borel_survival_slope_int_grid": slope_ref_int,
            "survival_pointwise": {"n": probe_n, "MEASURED_S_emp": surv_emp, "MODELED_S_borel(1-theta)": surv_ref,
                                   "max_abs_log_ratio": float(max(abs(math.log(e / r)) for e, r in zip(surv_emp, surv_ref)))},
            "cutoff": cut,
            "MODELED_borel_cutoff_same_estimator": cut_ref,
            "cutoff_in_[0.5,2]": (bool(0.5 <= cut["n_c_theta2_over_2"] <= 2.0) if cut.get("n_c") else None),
            "top_T_share": top[P.T],
            "top_share_by_t": {str(k): v for k, v in top.items()},
            "C_max_model": cmax, "x_star_model": xstar,
            "top_T_share_over_C_max": top[P.T] / cmax,
            "top_T_share_over_C_max_in_[0.85,1.05]": bool(0.85 <= top[P.T] / cmax <= 1.05),
            "largest_basin": largest,
            "largest_basin_borel_99_band": list(band),
            "largest_basin_in_band": bool(band[0] <= largest <= band[1]),
            "borel_band_samples": m_samples,
            "mean_basin": float(sizes.mean()),
            "basins_seconds": time.time() - tb,
        }
        summary["basins"] = g1
        log(f"[basins] {json.dumps(g1)}")
        with gzip.open(os.path.join(args.outdir, "basin_histogram.json.gz"), "wt") as fh:
            json.dump({"N": P.N, "a": P.a, "seed": P.seed, "W": P.W, "cap": P.cap,
                       "cycle_mass": basins.cycle_mass, "capped_mass": basins.capped_mass,
                       "n_dps": int(ndp),
                       "histogram": {"size": hist_vals.tolist(), "count": hist_counts.tolist()}}, fh)

    # ------------------------------------------------------------------ pools
    tp = time.time()
    pools = I.generate_pools(P, [2, 4, 8])
    pool_info = {}
    for r, snap in pools.items():
        pool_info[str(r // P.T)] = {"distinct_dps": len(snap.dps), "walks": snap.walks, "P_group_ops": snap.P_cost,
                                    "capped_walks": snap.capped_walks,
                                    "P_over_sqrt_NT": snap.P_cost / math.sqrt(P.N * P.T)}
    summary["pools"] = pool_info
    log(f"[pools] {json.dumps(pool_info)} ({time.time() - tp:.1f}s)")

    # ------------------------------------------------------------------ targets
    rng_t = np.random.default_rng(P.seed_targets)
    starts = rng_t.integers(0, P.N, size=(P.U_max, P.k), dtype=np.int64)
    fixture_starts = rng_t.integers(0, P.N, size=I.FIXTURE_TRIALS, dtype=np.int64)
    tw = time.time()
    term, length = I.walk_to_dp(P, starts.reshape(-1))
    term = term.reshape(P.U_max, P.k)
    length = length.reshape(P.U_max, P.k)
    walker_check = None
    if exact:
        t2, l2 = I.basin_lookup_walk(basins, starts.reshape(-1))
        walker_check = bool(np.array_equal(t2, term.reshape(-1)) and np.array_equal(l2, length.reshape(-1)))
        summary["walker_vs_exact_basins_agree"] = walker_check
    capped_frac = float((term < 0).mean())
    summary["online_walks"] = {"count": int(term.size), "capped_fraction_all_walks": capped_frac,
                               "mean_length_all_walks": float(length.mean()),
                               "mean_length_over_W": float(length.mean() / P.W),
                               "walk_seconds": time.time() - tw}
    log(f"[walks] {json.dumps(summary['online_walks'])} walker_vs_basins={walker_check}")

    # ------------------------------------------------------------------ fixture (G2 quantities)
    sel = I.CountedSelector()
    p2 = pools[2 * P.T]
    w2 = np.asarray(p2.S) + 4.0 * P.W * np.asarray(p2.h)
    keys2 = np.random.default_rng(P.seed_tiebreak).integers(0, 1 << 63, size=len(p2.dps), dtype=np.int64)
    idx = sel.select(w2, keys2, P.T)
    static_T = np.asarray([p2.dps[i] for i in idx], dtype=np.int64)
    ft, fl = I.walk_to_dp(P, fixture_starts)
    fhit = np.isin(ft, static_T)
    fixture = {
        "trials": int(I.FIXTURE_TRIALS),
        "total_steps": int(fl.sum()),
        "successes": int(fhit.sum()),
        "hit_rate": float(fhit.mean()),
        "scaled_main_cost": float(fl.sum() / max(1, fhit.sum()) / math.sqrt(P.N / P.T)),
        "scaled_precomputation": p2.P_cost / math.sqrt(P.N * P.T),
        "mean_steps_over_W": float(fl.mean() / P.W),
        "capped_fraction": float((ft < 0).mean()),
        "published_reference": {"1/4": {"scaled_main_cost": 1.79, "tolerance": 0.18,
                                        "scaled_precomputation_range": [1.05, 1.40]},
                                "1/2": {"scaled_main_cost": 1.62, "tolerance": 0.16}}[args.a],
        "note": "per-seed values; the G2 gate is evaluated on the 5-seed pooled value in the analysis run",
    }
    if exact:
        fixture["static_T_exact_coverage"] = basins.coverage(static_T)
    summary["fixture"] = fixture
    log(f"[fixture] {json.dumps(fixture)}")

    # ------------------------------------------------------------------ arms
    arms = build_arms(P, exact)
    snapshot_U = [P.T, 2 * P.T, 4 * P.T, 8 * P.T] if P.n_bits == 24 else []
    results = {}
    raw["arms"] = {}
    summary["arms"] = {}
    U_grid = {"4T": 4 * P.T, "8T": 8 * P.T, "16T": 16 * P.T}
    for cfg in arms:
        ta = time.time()
        res = I.run_arm(P, cfg, pools, term, length, basins, oracle_share, snapshot_U)
        results[cfg.name] = res
        R = cfg.R or P.R_default
        per_round = []
        for rec in res.rounds:
            p, lo, hi = I.wilson(rec["hits"], rec["walks"])
            rec = dict(rec)
            rec["hit_rate_wilson95"] = [lo, hi]
            per_round.append(rec)
        eps_ss = {lab: eps_window(res.solved, U - 2 * R, U) for lab, U in U_grid.items()}
        eps_cum = {lab: eps_window(res.solved, 0, U) for lab, U in U_grid.items()}
        n_targets = int(len(res.solved))
        summary["arms"][cfg.name] = {
            "config": {"mode": cfg.mode, "t_sel": cfg.t_sel, "r": cfg.r, "R": R, "phi": cfg.phi,
                       "pool_cap": cfg.pool_cap, "twin": cfg.twin},
            "rounds": per_round,
            "eps_ss": eps_ss, "eps_cum": eps_cum,
            "solved_total": int(res.solved.sum()),
            "group_ops_total": int(res.steps.sum()),
            "L_mean_per_target": float(res.steps.mean()),
            "L_mean_per_solved_target": float(res.steps[res.solved].mean()) if res.solved.any() else None,
            "restarts_total": int(res.used.sum()),
            "restart_group_ops_total": float(res.used.sum() * P.restart_cost),
            "lookups_total": int(sum(r["lookups"] for r in res.rounds)),
            "capped_walks_used": int(sum(r["capped_walks_used"] for r in res.rounds)),
            "capped_walk_fraction_used": float(sum(r["capped_walks_used"] for r in res.rounds) / max(1, res.used.sum())),
            "reselection_int_ops_total": int(res.reselection_ops_total),
            "S_bits": res.S_bits, "S_peak_bits": res.S_peak_bits, "max_pool_entries": res.max_pool,
            "selector_verified_against_numpy": res.selector_verified,
            "early_batch_eps_cum_first_10pct_of_8T": eps_window(res.solved, 0, int(0.1 * 8 * P.T)),
            "seconds": time.time() - ta,
        }
        raw["arms"][cfg.name] = {
            "config": summary["arms"][cfg.name]["config"],
            "walks_used": res.used.tolist(),
            "solved": res.solved.astype(int).tolist(),
            "hit_entry": res.hit_dp.tolist(),
            "steps_per_walk": [[int(length[u, j]) if j < res.used[u] else None for j in range(P.k)]
                               for u in range(n_targets)],
            "group_ops": res.steps.tolist(),
            "rounds": per_round,
            "table_hash_per_round": [r["table_hash"] for r in per_round],
        }
        log(f"[arm] {cfg.name}: solved={int(res.solved.sum())}/{n_targets} eps_ss(8T)={eps_ss['8T']:.4f} "
            f"eps_ss(16T)={eps_ss['16T']:.4f} p_last={per_round[-1]['hit_rate']:.4f} "
            + (f"cov_last={per_round[-1].get('exact_coverage'):.4f} " if exact and 'exact_coverage' in per_round[-1] else "")
            + f"S_peak={res.S_peak_bits} ops_resel={res.reselection_ops_total} ({time.time() - ta:.1f}s)")

    # ------------------------------------------------------------------ identity checks
    checks = {"round0_identity": {}, "bit_identity_all_rounds": {}, "exceedance": {}}
    for cfg in arms:
        if cfg.twin is None:
            continue
        me, tw_ = results[cfg.name], results[cfg.twin]
        R = cfg.R or P.R_default
        same0 = (np.array_equal(me.used[:R], tw_.used[:R]) and np.array_equal(me.solved[:R], tw_.solved[:R])
                 and np.array_equal(me.hit_dp[:R], tw_.hit_dp[:R]) and np.array_equal(me.steps[:R], tw_.steps[:R]))
        checks["round0_identity"][cfg.name] = bool(same0)
        if cfg.mode == "null_b" or (cfg.mode == "phi" and cfg.phi == 0.0):
            same_all = (np.array_equal(me.used, tw_.used) and np.array_equal(me.solved, tw_.solved)
                        and np.array_equal(me.hit_dp, tw_.hit_dp) and np.array_equal(me.steps, tw_.steps)
                        and all(a_ == b_ for a_, b_ in zip(
                            [r["table_hash"] for r in me.rounds], [r["table_hash"] for r in tw_.rounds])))
            checks["bit_identity_all_rounds"][cfg.name] = bool(same_all)
    # PHI(1) must equal RESEL-L(T/2) exactly as well (same rule)
    m1, rl = results["PHI(1.0,T/2)"], results["RESEL-L(T/2)"]
    checks["phi1_equals_resel_l_T/2"] = bool(np.array_equal(m1.solved, rl.solved) and np.array_equal(m1.hit_dp, rl.hit_dp))
    if exact:
        for cfg in arms:
            if cfg.mode in ("resel_lower", "resel_upper", "null_a", "phi"):
                ex = [r.get("exact_exceeds_oracle", False) for r in results[cfg.name].rounds]
                worst = max((r["exact_coverage"] - r["oracle_share"]) for r in results[cfg.name].rounds
                            if "oracle_share" in r)
                samp = max((r["hit_rate"] - r["oracle_share"]) for r in results[cfg.name].rounds
                           if "oracle_share" in r and r["hit_rate"] is not None)
                checks["exceedance"][cfg.name] = {"any_exact_exceedance": bool(any(ex)),
                                                  "max_exact_minus_oracle": worst,
                                                  "max_sampled_minus_oracle": samp}
    else:
        for cfg in arms:
            if cfg.mode in ("resel_lower", "resel_upper", "null_a", "phi"):
                rates = [r["hit_rate"] for r in results[cfg.name].rounds if r["hit_rate"] is not None]
                checks["exceedance"][cfg.name] = {"max_sampled_hit_rate": max(rates),
                                                  "exceeds_0.42": bool(max(rates) > 0.42)}
    summary["checks"] = checks
    log(f"[checks] {json.dumps(checks)}")

    # ------------------------------------------------------------------ HEUR-BLT-7 regression (2^24)
    if P.n_bits == 24:
        reg = {}
        rl = results["RESEL-L(T)"]
        rl2 = results["RESEL-L(T/2)"]
        extra = []
        for U in snapshot_U:
            for res in (rl, rl2):
                ps = float(res.solved[:U].mean())
                r_eff = 2 + U * P.k * ps / P.T
                extra.append(int(round(r_eff * P.T)))
        pools_eff = I.generate_pools(P, [], extra_targets=sorted(set(extra)))
        for arm_name, res in (("RESEL-L(T)", rl), ("RESEL-L(T/2)", rl2)):
            reg[arm_name] = {}
            for U in snapshot_U:
                snap = res.pool_snapshots.get(U)
                if snap is None:
                    continue
                dps = np.asarray(snap["dps"], dtype=np.int64)
                h = np.asarray(snap["h"], dtype=np.float64)
                b = basins.size[basins.index_of(dps)].astype(np.float64)
                A = np.vstack([b, np.ones_like(b)]).T
                coef, *_ = np.linalg.lstsq(A, h, rcond=None)
                ps = float(res.solved[:U].mean())
                credited_walks = float(h.sum())
                r_eff = 2 + U * P.k * ps / P.T
                pe = pools_eff[int(round(r_eff * P.T))]
                we = np.asarray(pe.S) + 4.0 * P.W * np.asarray(pe.h)
                ke = np.random.default_rng(P.seed_tiebreak).integers(0, 1 << 63, size=len(pe.dps), dtype=np.int64)
                sel_e = I.numpy_select(we, ke, res.config.t_sel)
                cov_eff = basins.coverage([pe.dps[i] for i in sel_e])
                cov_resel = res.rounds[U // P.T - 1]["exact_coverage"] if U // P.T - 1 < len(res.rounds) else None
                # coverage of the table selected AFTER U targets = table used in round U/T
                cov_after = res.rounds[U // P.T]["exact_coverage"] if U // P.T < len(res.rounds) else None
                reg[arm_name][str(U)] = {
                    "pool_entries": int(len(dps)),
                    "slope_count_on_basin": float(coef[0]), "intercept": float(coef[1]),
                    "modeled_slope_(rT+Ukp_s)/N": (2 * P.T + U * P.k * ps) / P.N,
                    "measured_slope_credited_walks/N": credited_walks / P.N,
                    "p_s_cum": ps, "r_eff": r_eff,
                    "precomp_pool_r_eff_walks": pe.walks, "precomp_pool_r_eff_P": pe.P_cost,
                    "exact_coverage_precomp_r_eff_top_t_sel": cov_eff,
                    "exact_coverage_reselected_table_after_U": cov_after,
                    "exact_coverage_reselected_table_during_last_round_before_U": cov_resel,
                }
        summary["heur_blt7_regression"] = reg
        log(f"[heur-blt7] {json.dumps(reg)}")

    # ------------------------------------------------------------------ cost table (MEASURED vs MODELED)
    measured = {}
    for name, res in results.items():
        measured[name] = {
            "walk_group_ops": int(res.steps.sum()),
            "restarts": int(res.used.sum()),
            "restart_group_ops": float(res.used.sum() * P.restart_cost),
            "lookups": int(sum(r["lookups"] for r in res.rounds)),
            "reselection_int_ops": int(res.reselection_ops_total),
            "S_bits": res.S_bits, "S_peak_bits": res.S_peak_bits,
            "P_group_ops": pools[res.config.r * P.T].P_cost if res.config.mode not in ("rho", "oracle") else 0,
        }
    xstar, cmax_a = I.c_max(P.a)
    modeled = {
        "C_max(a)": {"value": cmax_a, "formula": "erfc(sqrt(x*/2)), aed829 (B2)", "x_star": xstar},
        "C_max(a/2)": {"value": I.c_max(P.a / 2)[1], "formula": "aed829 (B2) at a/2 (T/2 table ceiling)"},
        "rho_asymptote": {"value": 0.51, "formula": "T_oracle/T_static = 1.64/3.20, aed829 (B3)"},
        "STATIC2T_single_walk_hit_rate": {"value": 0.32, "source": "contract control (b)"},
        "static_a_1/2_hit_rate": {"value": 0.42, "source": "implied by Table 4.1's 1.62"},
        "published_scaled_cost": {"a=1/4": 1.79, "a=1/2": 1.62, "source": "Bernstein-Lange Section 4 / Table 4.1 as frozen"},
        "B4_scaled_precomputation": {"value": 1.25, "source": "contract (B4)"},
        "restart_cost_formula": "1.5 ceil(log2 N) group operations per online walk (contract charging block)",
    }
    cost_table = {"MEASURED": measured, "MODELED": modeled,
                  "optimistic_assumptions": [
                      "walk step = one group operation (curve point addition ~10 field mults; not converted)",
                      "restart scalar multiplications excluded from L as the paper excludes them; counted and reported",
                      "re-selection cost in integer operations, not group operations; a ratio of counts",
                      "pool charged as working storage S_peak, not advice",
                      "targets uniform and independent"]}
    summary["cost_table"] = cost_table

    summary["elapsed_seconds"] = time.time() - t0
    with open(os.path.join(args.outdir, "cost_table.json"), "w") as fh:
        json.dump(cost_table, fh, indent=1)
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh)
    log(f"[done] {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

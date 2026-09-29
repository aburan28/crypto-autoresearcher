"""STAGE 1v2 (N=2^24) / STAGE 2v2 (N=2^30) cell of EXP-ECDLP-612fb1 v2.

One code path for both stages, arm selection by --n-bits.  Arms are run at
the v2-amended T_sel grid T_sel_grid_v2 = {0.65T, 0.75T} only (a = 1/4,
r = 2, k = 4), per specification.v2.yaml `inputs.stage_plan`.

Order inside the run mirrors v1's own gate order: exact basins and the G1
quantities (N <= 2^24), the G2 fixture for STATIC(T), then every arm, then
the v2 G3 ceiling-feasibility gate (item a, read directly from the exact
basins/oracle arms this run already computes -- ZERO extra compute at
N = 2^24) and the corrected HEUR-BLT-7 regression (item e).

At N = 2^30 there are no exact basins in this contract's scope (v1's own
restriction, retained unchanged).  G3 there is INFORMATIONAL, corroborated
by a disclosed, executor-introduced "sampled ORACLE(T_sel)" reading built
from the r=2 precomputation pool's own empirical hit-counts (raw walk
popularity, not the published re-selection weight) and measured through an
independent large sample of fresh walks -- NOT the contract's own exact
ORACLE arm, and NOT independently binding (per the amendment record's own
`judgment_calls`, which explicitly declines to invent a sampled-basin
estimator as a BINDING gate).  This is disclosed here, not guessed silently.

Observations only.  Writes raw-result.json, summary.json, cost_table.json
and (N = 2^24) the compressed exact basin histogram into --outdir.
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

T_SEL_GRID_V2_FRAC = {"0.65T": 0.65, "0.75T": 0.75}


def log(msg: str) -> None:
    print(msg, flush=True)


def build_arms(P: I.Params, exact: bool) -> list:
    T = P.T
    grid = {lab: int(round(frac * T)) for lab, frac in T_SEL_GRID_V2_FRAC.items()}
    grid["T"] = T
    arms = []
    arms.append(I.ArmConfig(name="STATIC(T)", mode="static", t_sel=T))
    arms.append(I.ArmConfig(name="RHO", mode="rho", t_sel=0))
    for lab in ("0.65T", "0.75T"):
        ts = grid[lab]
        arms.append(I.ArmConfig(name=f"STATIC({lab})", mode="static", t_sel=ts))
        arms.append(I.ArmConfig(name=f"RESEL-L({lab})", mode="resel_lower", t_sel=ts, twin=f"STATIC({lab})"))
        arms.append(I.ArmConfig(name=f"NULL-A({lab})", mode="null_a", t_sel=ts, twin=f"STATIC({lab})"))
        arms.append(I.ArmConfig(name=f"CAP(2T,{lab})", mode="resel_lower", t_sel=ts, pool_cap=2 * T,
                                twin=f"STATIC({lab})"))
    if exact:
        for lab in ("0.65T", "0.75T", "T"):
            arms.append(I.ArmConfig(name=f"ORACLE({lab})", mode="oracle", t_sel=grid[lab]))
    return arms, grid


def add_sampled_oracle_arms(P: I.Params, arms: list, pool_aux: I.PoolSnapshot, grid: dict) -> list:
    """N = 2^30 only (item a): add ORACLE_SAMPLED(T_sel) arms built from a
    fixed table (top-t_sel AUXILIARY r=32 pool DPs by raw generation
    hit-count), run through the SAME k=4-restart online walk sequence as
    every other arm so its eps_ss(U) is directly comparable to STATIC(T)'s
    eps_ss(U) (unlike a bare single-walk fixture hit rate, which is NOT
    comparable to a k=4 multi-restart success probability)."""
    for lab in ("0.65T", "0.75T"):
        ts = grid[lab]
        tab = sampled_oracle_table(P, pool_aux, ts)
        arms.append(I.ArmConfig(name=f"ORACLE_SAMPLED({lab})", mode="oracle", t_sel=ts, fixed_table=tab))
    return arms


def eps_window(solved: np.ndarray, u_lo: int, u_hi: int) -> float:
    u_lo = max(0, u_lo)
    if u_hi <= u_lo:
        return float("nan")
    return float(solved[u_lo:u_hi].mean())


SAMPLED_ORACLE_R = 32   # auxiliary pool ratio, LARGER than the online r=2 pool
                        # so top-t_sel selection by raw popularity has enough
                        # distinct DPs to be informative (r=2's ~2T distinct
                        # DPs against a t_sel of ~0.7T left almost no room to
                        # discriminate and produced a table BELOW STATIC(T)'s
                        # own coverage on the SAME pool -- impossible for a
                        # genuine ceiling; disclosed and corrected here).


def sampled_oracle_table(P: I.Params, pool_aux: I.PoolSnapshot, t_sel: int) -> np.ndarray:
    """Executor-disclosed, NON-BINDING sampled ceiling table at N = 2^30
    (item a `judgment_calls`; no exact-basin ORACLE exists at this N).
    Top-t_sel DPs of an AUXILIARY r=32 precomputation pool (generated solely
    for this diagnostic, walks NOT charged to the algorithm's own P), ranked
    by RAW generation hit-count h_d (empirical popularity), NOT the
    published re-selection weight S_d + 4W h_d used by RESEL-L/STATIC."""
    h = np.asarray(pool_aux.h, dtype=np.float64)
    order = np.argsort(-h, kind="stable")[:t_sel]
    return np.asarray([pool_aux.dps[i] for i in order], dtype=np.int64)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-bits", type=int, required=True, choices=[24, 30])
    ap.add_argument("--a", type=str, default="1/4")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    assert args.a == "1/4", "STAGE 1v2/2v2 is a = 1/4 only (T_sel_grid_v2 is out of scope for a=1/2)"
    a = 0.25
    P = I.Params(n_bits=args.n_bits, a=a, seed=args.seed)
    exact = P.n_bits <= 24
    stage = "1v2" if P.n_bits == 24 else "2v2"
    t0 = time.time()
    log(f"[cell] STAGE {stage} N=2^{P.n_bits} a=1/4 r=2 seed={P.seed} T={P.T} W={P.W:.4f} cap={P.cap} U_max={P.U_max}")
    log(f"[params] {json.dumps(P.describe())}")

    summary: dict = {"params": P.describe(), "certificate": {"kind": "none",
                     "note": "generic instrument: nothing is solved or certified"},
                     "stage": stage}
    raw: dict = {"params": P.describe(), "certificate": {"kind": "none"}, "stage": stage}

    # ------------------------------------------------------------------ basins
    basins = None
    oracle_share = None
    if exact:
        tb = time.time()
        basins = I.exact_basins(P)
        sizes = basins.size
        ndp = len(sizes)
        t_sel_v2 = {lab: int(round(frac * P.T)) for lab, frac in T_SEL_GRID_V2_FRAC.items()}
        top = {P.T // 4: basins.top_share(P.T // 4), P.T // 2: basins.top_share(P.T // 2),
               3 * P.T // 4: basins.top_share(3 * P.T // 4), P.T: basins.top_share(P.T),
               2 * P.T: basins.top_share(2 * P.T)}
        for lab, ts in t_sel_v2.items():
            top[ts] = basins.top_share(ts)
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
            "top_share_v2_grid": {lab: top[ts] for lab, ts in t_sel_v2.items()},
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
        log(f"[basins] top_T_share={top[P.T]:.4f} top_share_v2_grid={g1['top_share_v2_grid']} ({g1['basins_seconds']:.1f}s)")
        with gzip.open(os.path.join(args.outdir, "basin_histogram.json.gz"), "wt") as fh:
            json.dump({"N": P.N, "a": args.a, "seed": P.seed, "W": P.W, "cap": P.cap,
                       "cycle_mass": basins.cycle_mass, "capped_mass": basins.capped_mass,
                       "n_dps": int(ndp),
                       "histogram": {"size": hist_vals.tolist(), "count": hist_counts.tolist()}}, fh)

    # ------------------------------------------------------------------ pools
    tp = time.time()
    r_list = [2] if exact else [2, SAMPLED_ORACLE_R]
    pools = I.generate_pools(P, r_list)
    pool_info = {}
    for r, snap in pools.items():
        pool_info[str(r // P.T)] = {"distinct_dps": len(snap.dps), "walks": snap.walks, "P_group_ops": snap.P_cost,
                                    "capped_walks": snap.capped_walks,
                                    "P_over_sqrt_NT": snap.P_cost / math.sqrt(P.N * P.T)}
    summary["pools"] = pool_info
    if not exact:
        summary["pools"]["note"] = (f"the r={SAMPLED_ORACLE_R} pool is an AUXILIARY diagnostic for "
                                    "ORACLE_SAMPLED (item a); its walks are NOT charged to the algorithm's own "
                                    "P (only the r=2 pool is the real precomputation)")
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

    # ------------------------------------------------------------------ fixture (G2 quantities, unchanged)
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
        "published_reference": {"scaled_main_cost": 1.79, "tolerance": 0.18,
                                "scaled_precomputation_range": [1.05, 1.40]},
        "note": "per-seed values; the G2 gate is evaluated on the 5-seed pooled value in the analysis run",
    }
    if exact:
        fixture["static_T_exact_coverage"] = basins.coverage(static_T)
    summary["fixture"] = fixture
    log(f"[fixture] {json.dumps(fixture)}")

    # ------------------------------------------------------------------ arms
    arms, grid = build_arms(P, exact)
    if not exact:
        arms = add_sampled_oracle_arms(P, arms, pools[SAMPLED_ORACLE_R * P.T], grid)
    snapshot_U = [P.T, 2 * P.T, 4 * P.T, 8 * P.T] if exact else []
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
        cap_ok = all(r.get("pool_cap_honest_this_round", True) for r in per_round)
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
            "admitted_walks_total": int(res.admitted_walks_total),
            "cap_truncations_total": int(res.cap_truncations_total),
            "S_bits": res.S_bits, "S_peak_bits": res.S_peak_bits, "max_pool_entries": res.max_pool,
            "max_pool_entries_within_round": res.max_pool_within_round,
            "cap_S_peak_honest_every_round": bool(cap_ok) if cfg.pool_cap is not None else None,
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
            + f"S_peak={res.S_peak_bits} S_peak_max_within_round={res.max_pool_within_round} "
            f"cap_honest={cap_ok if cfg.pool_cap is not None else 'n/a'} ops_resel={res.reselection_ops_total} "
            f"admitted_walks={res.admitted_walks_total} ({time.time() - ta:.1f}s)")

    # ------------------------------------------------------------------ identity checks
    checks = {"round0_identity": {}, "exceedance": {}}
    for cfg in arms:
        if cfg.twin is None:
            continue
        me, tw_ = results[cfg.name], results[cfg.twin]
        R = cfg.R or P.R_default
        same0 = (np.array_equal(me.used[:R], tw_.used[:R]) and np.array_equal(me.solved[:R], tw_.solved[:R])
                 and np.array_equal(me.hit_dp[:R], tw_.hit_dp[:R]) and np.array_equal(me.steps[:R], tw_.steps[:R]))
        checks["round0_identity"][cfg.name] = bool(same0)
    if exact:
        for cfg in arms:
            if cfg.mode in ("resel_lower", "null_a"):
                ex = [r.get("exact_exceeds_oracle", False) for r in results[cfg.name].rounds]
                oc = [r for r in results[cfg.name].rounds if "oracle_share" in r]
                if oc:
                    worst = max(r["exact_coverage"] - r["oracle_share"] for r in oc)
                    samp = max((r["hit_rate"] - r["oracle_share"]) for r in oc if r["hit_rate"] is not None)
                    checks["exceedance"][cfg.name] = {"any_exact_exceedance": bool(any(ex)),
                                                      "max_exact_minus_oracle": worst,
                                                      "max_sampled_minus_oracle": samp}
    else:
        for cfg in arms:
            if cfg.mode in ("resel_lower", "null_a"):
                rates = [r["hit_rate"] for r in results[cfg.name].rounds if r["hit_rate"] is not None]
                checks["exceedance"][cfg.name] = {"max_sampled_hit_rate": max(rates),
                                                  "exceeds_0.42": bool(max(rates) > 0.42)}
    summary["checks"] = checks
    log(f"[checks] {json.dumps(checks)}")

    # ------------------------------------------------------------------ G3 CEILING-FEASIBILITY GATE (item a)
    g3 = {}
    for lab in ("0.65T", "0.75T"):
        ts = grid[lab]
        cell = {"t_sel": ts}
        if exact:
            oracle_top_share = oracle_share[ts]
            static_cov = summary["arms"]["STATIC(T)"]["rounds"][-1]["exact_coverage"]
            cell["exact_top_T_sel_share"] = oracle_top_share
            cell["static_T_exact_coverage"] = static_cov
            cell["margin"] = oracle_top_share - static_cov
            cell["g3_pass_this_seed"] = bool(oracle_top_share >= static_cov)
            cell["reading"] = "exact (STAGE 1v2, N=2^24): zero extra compute beyond the ORACLE arm this run already computes"
        else:
            eps_ss_static = summary["arms"]["STATIC(T)"]["eps_ss"]["8T"]
            eps_ss_oracle_sampled = summary["arms"][f"ORACLE_SAMPLED({lab})"]["eps_ss"]["8T"]
            cell["informational_sampled_oracle_eps_ss_8T"] = eps_ss_oracle_sampled
            cell["static_T_eps_ss_8T"] = eps_ss_static
            cell["margin_informational"] = eps_ss_oracle_sampled - eps_ss_static
            cell["g3_pass_this_seed_informational"] = bool(eps_ss_oracle_sampled >= eps_ss_static)
            cell["reading"] = ("INFORMATIONAL sampled reading (STAGE 2v2, N=2^30): ORACLE_SAMPLED(T_sel) eps_ss(8T) "
                               ">= STATIC(T) eps_ss(8T), both measured through the SAME k=4-restart online walk "
                               "sequence (so directly comparable, unlike a bare single-walk hit rate); "
                               f"ORACLE_SAMPLED's own table is an executor-disclosed, non-exact ranking of an "
                               f"AUXILIARY r={SAMPLED_ORACLE_R} pool by raw generation hit-count, NOT the "
                               "published re-selection weight and NOT "
                               "the contract's exact ORACLE arm; NOT independently binding per the amendment's "
                               "own judgment_calls; corroborated by STAGE 1v2's exact reading")
        g3[lab] = cell
    summary["G3_gate"] = g3
    log(f"[G3] {json.dumps(g3)}")

    # ------------------------------------------------------------------ HEUR-BLT-7 regression, CORRECTED (item e), N=2^24 only
    if exact:
        reg = {}
        for lab in ("0.65T", "0.75T"):
            res = results[f"RESEL-L({lab})"]
            reg[lab] = {}
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
                # admitted-walk count CUMULATIVE through U: the round record at
                # round index U/T - 1 carries admitted_walks_cumulative through
                # the END of that round, i.e. through target U (rounds are R=T).
                round_idx = U // P.T - 1
                admitted_walks_measured = (res.rounds[round_idx]["admitted_walks_cumulative"]
                                           if round_idx < len(res.rounds) else None)
                r_eff_v1_superseded = 2 + U * P.k * ps / P.T
                r_eff_v2_corrected = (2 + admitted_walks_measured / P.T) if admitted_walks_measured is not None else None
                credited_walks = float(h.sum())
                reg[lab][str(U)] = {
                    "pool_entries": int(len(dps)),
                    "slope_count_on_basin": float(coef[0]), "intercept": float(coef[1]),
                    "MODELED_v1_superseded_r_eff": r_eff_v1_superseded,
                    "MODELED_v1_superseded_slope_(rT+Ukp_s)/N": (2 * P.T + U * P.k * ps) / P.N,
                    "MEASURED_admitted_walk_count": admitted_walks_measured,
                    "MODELED_v2_corrected_r_eff": r_eff_v2_corrected,
                    "MEASURED_slope_credited_walks/N": credited_walks / P.N,
                    "p_s_cum": ps,
                    "note": "r_eff (item e, corrected) = r + MEASURED admitted-walk count / T, replacing "
                            "v1's r_eff = r + U k p_s / T; both reported, labelled, never mixed in one column",
                }
        summary["heur_blt7_regression_v2"] = reg
        log(f"[heur-blt7-v2] {json.dumps(reg)}")

    # ------------------------------------------------------------------ cost table (MEASURED vs MODELED)
    measured = {}
    for name, res in results.items():
        measured[name] = {
            "walk_group_ops": int(res.steps.sum()),
            "restarts": int(res.used.sum()),
            "restart_group_ops": float(res.used.sum() * P.restart_cost),
            "lookups": int(sum(r["lookups"] for r in res.rounds)),
            "reselection_int_ops": int(res.reselection_ops_total),
            "admitted_walks_total": int(res.admitted_walks_total),
            "S_bits": res.S_bits, "S_peak_bits": res.S_peak_bits,
            "P_group_ops": pools[res.config.r * P.T].P_cost if res.config.mode not in ("rho", "oracle") else 0,
        }
    xstar, cmax_a = I.c_max(P.a)
    modeled = {
        "C_max(a)": {"value": cmax_a, "formula": "erfc(sqrt(x*/2)), aed829 (B2)", "x_star": xstar},
        "rho_asymptote_v1_RETRACTED": {"value": 0.51, "formula": "T_oracle/T_static, aed829 (B3); RETRACTED per "
                                       "specification.v2.yaml preregistered_prediction (item h/b)", "status": "SUPERSEDED, kept for auditability"},
        "STATIC2T_single_walk_hit_rate": {"value": 0.32, "source": "contract control (b)"},
        "published_scaled_cost": {"a=1/4": 1.79, "source": "Bernstein-Lange Section 4 / Table 4.1 as frozen"},
        "restart_cost_formula": "1.5 ceil(log2 N) group operations per online walk (contract charging block)",
        "v1_superseded_HEUR_BLT7_formula": "r_eff = r + U k p_s / T (retained beside the v2 corrected formula, labelled superseded)",
        "v2_corrected_HEUR_BLT7_formula": "r_eff = r + MEASURED admitted-walk count / T (item e)",
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

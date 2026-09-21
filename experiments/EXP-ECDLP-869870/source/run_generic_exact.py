"""Stage 1/2 compute: one (N, seed) generic exact run of EXP-ECDLP-869870.

Covers a in {1/8, 1/4, 1/2, 1}, caps 8W and 20W, r in {1, 2, 4, 8, 16},
all five selection rules, the unselected-law arm, the relabelling null, the
sigma decay, the HEUR-BLT-2 regression at T_gen = 16 T, the M = 40000 online
walks and the fixture cells. Observations only; no interpretation.

Usage: python3 run_generic_exact.py --log2N 20 --seed 1 --out <run-dir>
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402
import model as MODEL  # noqa: E402

A_GRID = [0.125, 0.25, 0.5, 1.0]
R_GRID = [1, 2, 4, 8, 16]
M_FACTORS = [0.25, 0.5, 1, 2, 4, 8, 16]
SIGMAS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
T_OF = {20: 64, 22: 128, 24: 256, 30: 1024}
M_ONLINE = 40000
T_GEN_FACTOR = 16
BOOT_REPS = 200


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if math.isfinite(v) else (None if math.isnan(v) else ("inf" if v > 0 else "-inf"))
    if isinstance(o, float):
        return o if math.isfinite(o) else (None if math.isnan(o) else ("inf" if o > 0 else "-inf"))
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run_cell(log2N, T, a, seed, f, rngs, raw, summ, depth_out, *, N=None, isdp=None, online_provider=None, key=None):
    """One (N, a, seed) cell. Generic arm: N = 2^log2N, the DP indicator is the
    keyed predicate on [0, N) and online walks are exact-map lookups. Curve arm
    (additive extension, defaults unchanged): the caller passes the prime N,
    the DP indicator on the enumerated group and an online_provider that runs
    real point walks and returns (terminal_index, reached, length_charged, extra)."""
    N = (1 << log2N) if N is None else int(N)
    prm = I.cell_params(log2N, T, a, N)
    W = prm["W"]; cap8 = prm["cap8"]; cap20 = prm["cap20"]; theta = prm["theta"]
    K, K2 = I.walk_keys(seed)
    key = key or f"a={a}"
    log(f"cell {key}: W={W:.3f} cap8={cap8} cap20={cap20} T={T}")

    # DP indicator (walk f shared across a; predicate depends on W)
    if isdp is None:
        isdp = np.empty(N, dtype=bool)
        for lo in range(0, N, 1 << 21):
            hi = min(N, lo + (1 << 21))
            isdp[lo:hi] = I.is_dp_fn(np.arange(lo, hi, dtype=np.int64), K2, prm["dp_threshold"])
    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)

    t0 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    log(f"  pointer jumping: {rounds} rounds, {time.time()-t0:.1f}s; nDP={nDP}")

    bs8, ok8, capped8, cycle_mass = I.basin_sizes_at_cap(p, d, reach, isdp, N, cap8)
    bs20, ok20, capped20, _ = I.basin_sizes_at_cap(p, d, reach, isdp, N, cap20)
    bs8 = bs8.astype(np.int32); bs20 = bs20.astype(np.int32)
    # exact online walk length (one group op per step; capped walks charged cap)
    len8_all_mean = float(np.where(ok8, d, cap8).mean())
    sizes8 = bs8[dps]; sizes20 = bs20[dps]

    # --- basin multisets ------------------------------------------------
    ms8 = I.compressed_hist(sizes8); ms20 = I.compressed_hist(sizes20)
    u8 = np.array(ms8["sizes"], dtype=np.int64); c8 = np.array(ms8["counts"], dtype=np.int64)
    u20 = np.array(ms20["sizes"], dtype=np.int64); c20 = np.array(ms20["counts"], dtype=np.int64)
    n_lo, n_hi = 10.0, W * W / 4.0
    slope8, icpt8, npts8 = I.survival_slope(u8, c8, n_lo, n_hi)
    slope20, icpt20, npts20 = I.survival_slope(u20, c20, n_lo, n_hi)
    rb = rngs["boot"]
    slope8_ci = I.bootstrap_multiset(u8, c8, lambda u, c: I.survival_slope(u, c, n_lo, n_hi)[0], rb, BOOT_REPS)
    b8, nc8, ncs8, nb8 = I.cutoff_fit(u8, c8, W)
    b20, nc20, ncs20, nb20 = I.cutoff_fit(u20, c20, W)
    ncs8_ci = I.bootstrap_multiset(u8, c8, lambda u, c: I.cutoff_fit(u, c, W)[2], rb, BOOT_REPS)
    largest8 = int(sizes8.max()) if nDP else 0
    band = MODEL.borel_max_band(theta, N / W, W)
    in_band = (band["n_lo"] is not None and band["n_hi"] is not None and band["n_lo"] <= largest8 <= band["n_hi"])

    # --- depth-profile histograms (stored, not analysed) ------------------
    dw = max(1, int(round(W / 16)))
    ndb = int(cap20 // dw) + 2
    sb = np.zeros(N, dtype=np.int64)
    sb[ok20] = np.floor(np.log2(bs20[p[ok20]])).astype(np.int64)
    db = np.minimum(d // dw, ndb - 1)
    flat = np.bincount((sb[ok20] * ndb + db[ok20]).astype(np.int64), minlength=(26 * ndb))
    depth_out[key] = {"a": a, "W": W, "cap20": cap20, "depth_bin_width": dw, "n_depth_bins": ndb,
                      "size_bin": "floor(log2(basin size at cap 20W)) of the point's terminal DP, rows 0..25",
                      "rows": flat[: 26 * ndb].reshape(26, ndb).tolist()}
    del sb, db, flat

    # --- global oracle -------------------------------------------------------
    key_all = rngs["tie"].random(nDP)               # tie-break permutation key per DP (400 + s)
    perm_all = np.argsort(np.argsort(key_all))
    glob8 = I.select_rule("global_oracle", None, T, None, W, None, sizes8, perm_all, dps)
    glob20 = I.select_rule("global_oracle", None, T, None, W, None, sizes20, perm_all, dps)
    share8 = I.exact_coverage(glob8, bs8, N); share20 = I.exact_coverage(glob20, bs20, N)
    isdp_pos = np.full(N, -1, dtype=np.int64); isdp_pos[dps] = np.arange(nDP)

    # --- generation stream (200 + s) -------------------------------------
    need_distinct = T_GEN_FACTOR * T
    starts = np.empty(0, dtype=np.int64)
    while True:
        more = int(max(4096, MODEL.b4_walks(16, a, T)))
        starts = np.concatenate([starts, rngs["gen"].integers(0, N, size=more, dtype=np.int64)])
        term = p[starts]; ok = ok8[starts]
        distinct = np.unique(term[ok]).size
        if distinct >= need_distinct:
            break
    length = np.where(ok, d[starts], cap8).astype(np.int64)
    _, first_idx = np.unique(term[ok], return_index=True)
    ok_idx = np.flatnonzero(ok)
    first_walk = np.sort(ok_idx[first_idx])        # walk index at which the j-th distinct DP appears
    walks_needed = {r: int(first_walk[r * T - 1] + 1) for r in R_GRID}

    # --- online walks (100 + s) -------------------------------------------
    on_extra = None
    if online_provider is None:
        on_starts = rngs["online"].integers(0, N, size=M_ONLINE, dtype=np.int64)
        on_term = p[on_starts]; on_ok = ok8[on_starts]
        on_len = np.where(on_ok, d[on_starts], cap8).astype(np.int64)
    else:
        on_term, on_ok, on_len, on_extra = online_provider(prm, rngs["online"])
        on_term = np.asarray(on_term, dtype=np.int64); on_ok = np.asarray(on_ok, dtype=bool); on_len = np.asarray(on_len, dtype=np.int64)
        # cross-check the real-point walk against the exact map: a reached walk's
        # terminal must be the exact map's first DP of its start index
        if "start_index" in on_extra:
            si = np.asarray(on_extra["start_index"], dtype=np.int64)
            agree = np.array_equal(on_term[on_ok], p[si][on_ok]) and np.array_equal(on_len[on_ok], d[si][on_ok]) and np.array_equal(on_ok, ok8[si])
            on_extra["real_walk_matches_exact_map"] = bool(agree)
    on_mean_len = float(on_len.mean())

    def eval_table(table):
        mask = np.zeros(N, dtype=bool); mask[table] = True
        c8v = I.exact_coverage(table, bs8, N); c20v = I.exact_coverage(table, bs20, N)
        on = I.online_eval(table, on_term, on_ok, on_len, N, T, mask)
        inside = on["wilson_lo"] <= c8v <= on["wilson_hi"]
        exact_cost = len8_all_mean / c8v / math.sqrt(N / T) if c8v > 0 else float("inf")
        return {"table_sha256": I.table_hash(table), "size": int(table.size),
                "coverage_exact_8W": c8v, "coverage_exact_20W": c20v,
                "cap_loss_20W_minus_8W": c20v - c8v,
                "sampled": on, "exact_inside_wilson": bool(inside),
                "sampled_minus_exact": on["c_hat"] - c8v,
                "scaled_cost_exact_expectation": exact_cost,
                "exceeds_global_oracle_8W": bool(c8v > share8 + 1e-15)}

    cell = {"params": prm, "seed": seed, "nDP": nDP, "pointer_rounds": rounds,
            "cycle_mass": cycle_mass, "cycle_mass_frac": cycle_mass / N,
            "capped_mass_8W": capped8, "capped_mass_8W_frac": capped8 / N,
            "capped_mass_20W": capped20, "capped_mass_20W_frac": capped20 / N,
            "exact_mean_online_walk_length_8W": len8_all_mean,
            "sampled_mean_online_walk_length_8W": on_mean_len,
            "basin_law": {
                "survival_slope_8W": slope8, "survival_slope_8W_boot95": slope8_ci, "fit_points_8W": npts8,
                "survival_slope_20W": slope20, "fit_points_20W": npts20,
                "fit_range": [n_lo, n_hi],
                "cutoff_joint_slope_8W": b8, "cutoff_n_c_8W": nc8, "cutoff_n_c_theta2_over_2_8W": ncs8,
                "cutoff_n_c_theta2_over_2_8W_boot95": ncs8_ci, "cutoff_bins_8W": nb8,
                "cutoff_joint_slope_20W": b20, "cutoff_n_c_20W": nc20, "cutoff_n_c_theta2_over_2_20W": ncs20,
                "largest_basin_8W": largest8, "largest_basin_20W": int(sizes20.max()) if nDP else 0,
                "borel_band_99_model": band, "largest_in_band": bool(in_band),
                "model_slope": -0.5, "model_cutoff_theta2_over_2": 1.0},
            "global_oracle": {"top_T_share_8W": share8, "top_T_share_20W": share20,
                              "table_sha256_8W": I.table_hash(glob8),
                              "ratio_to_c_max_numeric": share8 / MODEL.c_max(a),
                              "ratio_to_c_max_contract": share8 / MODEL.CMAX_CONTRACT[a][1],
                              "oracle_online_constant_measured_sqrt_a_over_C": math.sqrt(a) / share8,
                              "oracle_online_constant_exact_expectation": len8_all_mean / share8 / math.sqrt(N / T),
                              "model": MODEL.model_table(a)},
            "generation": {"walks_drawn": int(starts.size), "walks_needed_for_rT_distinct": walks_needed,
                           "b4_model_walks": {r: MODEL.b4_walks(r, a, T) for r in R_GRID},
                           "b4_ratio_measured_over_model": {r: walks_needed[r] / MODEL.b4_walks(r, a, T) for r in R_GRID},
                           "capped_generation_walks_frac": float(1 - ok.mean())},
            "rules": {}, "unselected_law": [], "heur_blt2": {}, "fixture": {},
            "exceedance": []}

    # --- unselected-law arm -----------------------------------------------
    for fac in M_FACTORS:
        m = int(round(fac * T))
        tdp = term[:m][ok[:m]]
        dist_dps = np.unique(tdp)
        cov = I.exact_coverage(dist_dps, bs8, N)
        a_m = m * W * W / N
        cr = MODEL.c_rand(a_m)
        D = int(dist_dps.size)
        r_eff = D / T
        cell["unselected_law"].append({"m_factor": fac, "m": m, "a_m": a_m, "distinct_dps": D,
                                       "coverage_exact_8W": cov, "c_rand_model": cr, "ratio": cov / cr,
                                       "coverage_exact_20W": I.exact_coverage(dist_dps, bs20, N),
                                       "b4_walks_for_this_many_distinct_model": MODEL.b4_walks(r_eff, a, T),
                                       "b4_walks_ratio_measured_over_model": m / MODEL.b4_walks(r_eff, a, T)})

    # --- HEUR-BLT-2 regression at T_gen = 16 T ---------------------------------
    tg = T_GEN_FACTOR * T
    h_all = np.bincount(term[:tg][ok[:tg]], minlength=N)[dps].astype(np.float64)
    x = sizes8.astype(np.float64)
    A = np.vstack([x, np.ones_like(x)]).T
    (sl, ic), *_ = np.linalg.lstsq(A, h_all, rcond=None)
    resid = h_all - (sl * x + ic)
    n = x.size
    s2 = float((resid ** 2).sum() / max(n - 2, 1))
    sxx = float(((x - x.mean()) ** 2).sum())
    se_sl = math.sqrt(s2 / sxx) if sxx > 0 else float("nan")
    se_ic = math.sqrt(s2 * (1 / n + x.mean() ** 2 / sxx)) if sxx > 0 else float("nan")
    lam = tg * x / N
    pearson = float(((h_all - lam) ** 2 / np.maximum(lam, 1e-300)).sum() / n)
    most = int(np.argmax(h_all))
    rank = int((sizes8 > sizes8[most]).sum()) + 1
    cell["heur_blt2"] = {"T_gen": tg, "n_dps": n, "slope": sl, "slope_se": se_sl, "slope_model": tg / N,
                         "slope_ratio": sl / (tg / N), "intercept": ic, "intercept_se": se_ic,
                         "intercept_ci95": [ic - 1.96 * se_ic, ic + 1.96 * se_ic],
                         "slope_through_origin": float((x * h_all).sum() / (x * x).sum()),
                         "var_over_mean_raw": float(h_all.var() / h_all.mean()),
                         "pearson_dispersion_vs_binomial_mean": pearson,
                         "most_hit_dp": int(dps[most]), "most_hit_count": int(h_all[most]),
                         "most_hit_basin_rank": rank, "most_hit_basin_rank_frac": rank / n,
                         "most_hit_in_top_1pct": bool(rank <= max(1, math.ceil(0.01 * n))),
                         "note": "var_over_mean_raw is the marginal ratio over all DPs (mixture variance included); pearson_dispersion is sum((h-lambda)^2/lambda)/n with lambda = T_gen n/N. Both reported; neither interpreted."}

    # --- pools and rules per r ------------------------------------------------
    for r in R_GRID:
        m = walks_needed[r]
        tdp = term[:m][ok[:m]]; ln = length[:m][ok[:m]]
        pool_dps = np.unique(tdp)
        assert pool_dps.size == r * T, (pool_dps.size, r * T)
        h = np.bincount(tdp, minlength=N)[pool_dps].astype(np.int64)
        S = np.bincount(tdp, weights=ln, minlength=N)[pool_dps].astype(np.int64)
        P = int(length[:m].sum())
        pool = {"dps": pool_dps, "h": h, "S": S}
        perm = perm_all[isdp_pos[pool_dps]]
        rec = {"r": r, "walks": m, "P_group_ops": P, "P_scaled_sqrtNT": P / math.sqrt(N * T),
               "b4_scaled_precomp_model": MODEL.b4_scaled_precomp(r, a),
               "pool_size": int(pool_dps.size), "pool_sha256": I.table_hash(pool_dps),
               "pool": {"dp": pool_dps.tolist(), "h": h.tolist(), "S": S.tolist(),
                        "basin_8W": bs8[pool_dps].tolist(), "basin_20W": bs20[pool_dps].tolist()},
               "tables": {}, "nulls": {}}
        for rule in I.RULES:
            tab = I.select_rule(rule, pool, T, perm, W, bs8, sizes8, perm_all, dps)
            rec["tables"][rule] = eval_table(tab)
            if rec["tables"][rule]["exceeds_global_oracle_8W"]:
                cell["exceedance"].append({"r": r, "rule": rule, "coverage": rec["tables"][rule]["coverage_exact_8W"], "global_share": share8})
        if r == 1:
            rec["tables"]["paper_literal_N_eq_T"] = eval_table(pool_dps)
        go = rec["tables"]["generated_oracle"]["coverage_exact_8W"]
        rec["published_over_generated_oracle_8W"] = rec["tables"]["published_weight"]["coverage_exact_8W"] / go if go else None
        rec["count_over_generated_oracle_8W"] = rec["tables"]["count_only"]["coverage_exact_8W"] / go if go else None
        rec["unselected_over_generated_oracle_8W"] = rec["tables"]["unselected"]["coverage_exact_8W"] / go if go else None
        # nulls and sigma decay for the two statistic-based rules
        unsel_cov = rec["tables"]["unselected"]["coverage_exact_8W"]
        for rule in ("published_weight", "count_only"):
            stat = I.rule_statistic(rule, pool, W)
            relab = rngs["relabel"].permutation(stat)
            tab = pool_dps[I.select_top(relab, perm, T)]
            rel_cov = I.exact_coverage(tab, bs8, N)
            Z = rngs["noise"].standard_normal(stat.size)
            curve = []
            for sg in SIGMAS:
                noisy = stat * np.maximum(0.0, 1.0 + sg * Z)
                tabs = pool_dps[I.select_top(noisy, perm, T)]
                curve.append(I.exact_coverage(tabs, bs8, N))
            mono = all(curve[i + 1] <= curve[i] + 1e-12 for i in range(len(curve) - 1))
            flat = (max(curve) - min(curve)) < 1e-12
            rec["nulls"][rule] = {"relabelled_coverage_8W": rel_cov, "unselected_coverage_8W": unsel_cov,
                                  "relabelled_minus_unselected": rel_cov - unsel_cov,
                                  "relabelled_table_sha256": I.table_hash(tab),
                                  "sigma": SIGMAS, "sigma_coverage_8W": curve,
                                  "sigma_monotone_nonincreasing": bool(mono), "sigma_flat": bool(flat),
                                  "rule_value": rec["tables"][rule]["coverage_exact_8W"],
                                  "note": "one Z draw per (a, r, rule) shared across sigma (coupled); stream 500+s"}
        cell["rules"][str(r)] = rec
        # fixture cells at this a
        if (a, r) in MODEL.PUBLISHED_SCALED_COST:
            t = rec["tables"]["published_weight"]
            cell["fixture"][str(r)] = {
                "a": a, "r": r, "scaled_cost_sampled_this_seed": t["sampled"]["scaled_cost_sampled"],
                "hits": t["sampled"]["hits"], "total_steps": t["sampled"]["total_steps"], "M": t["sampled"]["M"],
                "scaled_cost_exact_expectation": t["scaled_cost_exact_expectation"],
                "published_scaled_cost": MODEL.PUBLISHED_SCALED_COST[(a, r)],
                "residual_sampled_minus_published": t["sampled"]["scaled_cost_sampled"] - MODEL.PUBLISHED_SCALED_COST[(a, r)],
                "scaled_precomp_measured": rec["P_scaled_sqrtNT"],
                "published_scaled_precomp": MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)],
                "precomp_relative_residual": rec["P_scaled_sqrtNT"] / MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)] - 1,
                "b4_model_scaled_precomp": MODEL.B4_CONTRACT_VALUES[(a, r)],
                "model_nt8_oracle_constant": MODEL.MODEL_NT8.get((a, r)),
                "theta": theta}
    # raw: multisets, online terminals
    if on_extra is not None:
        cell["online_extra"] = {k: v for k, v in on_extra.items() if k not in ("start_index", "c", "s", "k_true", "Q", "hit_any")}
    raw[key] = {"params": prm, "online_extra_raw": on_extra, "basin_multiset_8W": ms8, "basin_multiset_20W": ms20,
                "n_dps": nDP, "cycle_mass": cycle_mass, "capped_mass_8W": capped8, "capped_mass_20W": capped20,
                "global_oracle_table_8W": glob8.tolist(),
                "online_walks": {"seed": 100 + seed, "M": M_ONLINE, "terminal_dp": on_term.tolist(),
                                 "reached_within_8W": on_ok.tolist(), "length_charged": on_len.tolist()},
                "generation_stream": {"seed": 200 + seed, "walks_drawn": int(starts.size),
                                      "walks_needed_for_rT_distinct": walks_needed},
                "pools_by_r": {str(r): cell["rules"][str(r)]["pool"] for r in R_GRID},
                "tables_sha256": {str(r): {rule: cell["rules"][str(r)]["tables"][rule]["table_sha256"] for rule in cell["rules"][str(r)]["tables"]} for r in R_GRID}}
    for r in R_GRID:
        cell["rules"][str(r)].pop("pool")
    summ[key] = cell
    del p, d, reach, isdp, bs8, bs20, ok8, ok20
    return None
    log(f"  cell {key} done: share8={share8:.4f} slope={slope8:.3f} fixture={[ (k, round(v['scaled_cost_sampled_this_seed'],3)) for k,v in cell['fixture'].items()]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log2N", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--T", type=int, default=None)
    args = ap.parse_args()
    log2N, seed = args.log2N, args.seed
    T = args.T or T_OF[log2N]
    N = 1 << log2N
    K, K2 = I.walk_keys(seed)
    rngs = {"online": np.random.default_rng(100 + seed), "gen": np.random.default_rng(200 + seed),
            "relabel": np.random.default_rng(300 + seed), "tie": np.random.default_rng(400 + seed),
            "noise": np.random.default_rng(500 + seed), "boot": np.random.default_rng(600 + seed)}
    log(f"run log2N={log2N} N={N} T={T} seed={seed} K={K:#x} K2={K2:#x}")
    t0 = time.time()
    f = np.empty(N, dtype=np.int32)
    for lo in range(0, N, 1 << 21):
        hi = min(N, lo + (1 << 21))
        f[lo:hi] = I.step_fn(np.arange(lo, hi, dtype=np.int64), K, log2N)
    log(f"walk map built in {time.time()-t0:.1f}s")
    raw, summ, depth = {}, {}, {}
    for a in A_GRID:
        run_cell(log2N, T, a, seed, f, rngs, raw, summ, depth)
    exceed = [e for c in summ.values() for e in c["exceedance"]]
    null_flags = []
    header = {"experiment_id": "EXP-ECDLP-869870", "stage": "generic_exact", "log2N": log2N, "N": N, "T": T,
              "seed": seed, "walk_key_K": K, "dp_key_K2": K2,
              "seeds": {"walk_key": seed, "online": 100 + seed, "generation_start": 200 + seed,
                        "relabelling": 300 + seed, "tie_break": 400 + seed, "noise": 500 + seed, "bootstrap": 600 + seed},
              "certificate": {"kind": "none", "reason": "generic keyed-random-function arm: nothing is solved"},
              "a_grid": A_GRID, "r_grid": R_GRID, "m_factors": M_FACTORS, "sigmas": SIGMAS, "M_online": M_ONLINE,
              "bits_per_entry": 2 * log2N,
              "invalidity": {"exact_coverage_exceeds_global_oracle": exceed,
                             "completed_invalid": bool(exceed)},
              "elapsed_seconds_compute": time.time() - t0}
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "raw-result.json"), "w") as fh:
        json.dump(jsonable({"header": header, "cells": raw}), fh)
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(jsonable({"header": header, "cells": summ}), fh, indent=1)
    with open(os.path.join(args.out, "depth_histograms.json"), "w") as fh:
        json.dump(jsonable({"header": {k: header[k] for k in ("experiment_id", "log2N", "T", "seed")}, "cells": depth}), fh)
    log(f"done in {time.time()-t0:.1f}s; exceedances={len(exceed)}")


if __name__ == "__main__":
    main()

"""Stage 3 compute: one (N = 2^30, seed) generic SAMPLED run of EXP-ECDLP-869870.

No exact basins at 2^30: generation walks and the M = 40000 online walks are
real lockstep iterations of the same keyed walk (instrument.step_fn) and DP
predicate (instrument.is_dp_fn) used by the exact stages. Rules (i) published
weight, (ii) count-only and (iii) unselected are evaluated by SAMPLED coverage
(Wilson intervals); the two oracle rules need exact basin sizes and are
reported as not computable at this N. Observations only.

Usage: python3 run_generic_sampled.py --log2N 30 --seed 1 --out <run-dir>
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
from run_generic_exact import A_GRID, R_GRID, M_FACTORS, SIGMAS, T_OF, M_ONLINE, T_GEN_FACTOR, jsonable, log  # noqa: E402


def walk_batch(starts: np.ndarray, K: int, K2: int, log2N: int, thr: int, cap: int):
    """Lockstep walks: returns (terminal, reached, length_charged, group_ops).
    One group operation per step; capped walks charged cap."""
    cur = starts.astype(np.int64).copy()
    n = cur.size
    d = np.zeros(n, dtype=np.int64)
    active = ~I.is_dp_fn(cur, K2, thr)
    ops = 0
    for step in range(1, cap + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        nxt = I.step_fn(cur[idx], K, log2N)
        ops += idx.size
        cur[idx] = nxt
        d[idx] = step
        active[idx] = ~I.is_dp_fn(nxt, K2, thr)
    reached = ~active
    length = np.where(reached, d, cap)
    return cur, reached, length, ops


def run_cell(log2N, T, a, seed, rngs, raw, summ):
    N = 1 << log2N
    prm = I.cell_params(log2N, T, a)
    W = prm["W"]; cap8 = prm["cap8"]; thr = prm["dp_threshold"]
    K, K2 = I.walk_keys(seed)
    key = f"a={a}"
    log(f"cell {key}: W={W:.3f} cap8={cap8} T={T}")
    t0 = time.time()
    # generation stream (200 + s), extended until 16 T distinct DPs
    need = T_GEN_FACTOR * T
    term = np.empty(0, np.int64); ok = np.empty(0, bool); length = np.empty(0, np.int64); gen_ops = 0
    while True:
        more = int(max(4096, 1.1 * MODEL.b4_walks(16, a, T)))
        st = rngs["gen"].integers(0, N, size=more, dtype=np.int64)
        t, o, l, ops = walk_batch(st, K, K2, log2N, thr, cap8)
        term = np.concatenate([term, t]); ok = np.concatenate([ok, o]); length = np.concatenate([length, l]); gen_ops += ops
        if np.unique(term[ok]).size >= need:
            break
    log(f"  generation: {term.size} walks, {gen_ops} group ops, {time.time()-t0:.1f}s")
    _, first_idx = np.unique(term[ok], return_index=True)
    ok_idx = np.flatnonzero(ok)
    first_walk = np.sort(ok_idx[first_idx])
    walks_needed = {r: int(first_walk[r * T - 1] + 1) for r in R_GRID}
    # online walks (100 + s)
    t1 = time.time()
    on_st = rngs["online"].integers(0, N, size=M_ONLINE, dtype=np.int64)
    on_term, on_ok, on_len, on_ops = walk_batch(on_st, K, K2, log2N, thr, cap8)
    log(f"  online: {M_ONLINE} walks, {on_ops} group ops, mean len/W={on_len.mean()/W:.3f}, {time.time()-t1:.1f}s")

    def eval_table(table):
        tset = np.unique(table)
        hit = on_ok & np.isin(on_term, tset, assume_unique=False)
        hits = int(hit.sum()); total = int(on_len.sum())
        ph, lo, hi = I.wilson(hits, M_ONLINE)
        return {"table_sha256": I.table_hash(tset), "size": int(tset.size),
                "sampled": {"M": M_ONLINE, "hits": hits, "c_hat": ph, "wilson_lo": lo, "wilson_hi": hi,
                            "total_steps": total, "scaled_cost_sampled": (total / hits / math.sqrt(N / T)) if hits else None},
                "coverage_exact_8W": None, "exact_note": "no exact basins at 2^30 (sampled stage)"}

    cell = {"params": prm, "seed": seed, "sampled_mean_online_walk_length_8W": float(on_len.mean()),
            "online_group_ops": on_ops, "generation_group_ops_total_stream": gen_ops,
            "generation": {"walks_drawn": int(term.size), "walks_needed_for_rT_distinct": walks_needed,
                           "b4_model_walks": {r: MODEL.b4_walks(r, a, T) for r in R_GRID},
                           "b4_ratio_measured_over_model": {r: walks_needed[r] / MODEL.b4_walks(r, a, T) for r in R_GRID},
                           "capped_generation_walks_frac": float(1 - ok.mean())},
            "rules": {}, "unselected_law": [], "fixture": {}, "not_computable": ["generated_oracle", "global_oracle", "exact coverage", "basin law", "HEUR-BLT-2 regression"]}
    for fac in M_FACTORS:
        m = int(round(fac * T)); dist = np.unique(term[:m][ok[:m]])
        ev = eval_table(dist); a_m = m * W * W / N; cr = MODEL.c_rand(a_m)
        cell["unselected_law"].append({"m_factor": fac, "m": m, "a_m": a_m, "distinct_dps": int(dist.size),
                                       "coverage_sampled": ev["sampled"]["c_hat"], "wilson": [ev["sampled"]["wilson_lo"], ev["sampled"]["wilson_hi"]],
                                       "c_rand_model": cr, "ratio_sampled": ev["sampled"]["c_hat"] / cr})
    # a per-DP tie-break key from the 400 + s stream, assigned by DP identity order
    all_pool = np.unique(term[ok])
    key_all = rngs["tie"].random(all_pool.size)
    perm_all = np.argsort(np.argsort(key_all))
    for r in R_GRID:
        m = walks_needed[r]
        tdp = term[:m][ok[:m]]; ln = length[:m][ok[:m]]
        pool_dps, inv = np.unique(tdp, return_inverse=True)
        assert pool_dps.size == r * T
        h = np.bincount(inv, minlength=pool_dps.size).astype(np.int64)
        S = np.bincount(inv, weights=ln, minlength=pool_dps.size).astype(np.int64)
        P = int(length[:m].sum())
        pool = {"dps": pool_dps, "h": h, "S": S}
        perm = perm_all[np.searchsorted(all_pool, pool_dps)]
        rec = {"r": r, "walks": m, "P_group_ops": P, "P_scaled_sqrtNT": P / math.sqrt(N * T),
               "b4_scaled_precomp_model": MODEL.b4_scaled_precomp(r, a), "pool_size": int(pool_dps.size),
               "pool_sha256": I.table_hash(pool_dps), "pool": {"dp": pool_dps.tolist(), "h": h.tolist(), "S": S.tolist()},
               "tables": {}, "nulls": {}}
        for rule in ("published_weight", "count_only", "unselected"):
            tab = I.select_rule(rule, pool, T, perm, W, None)
            rec["tables"][rule] = eval_table(tab)
        if r == 1:
            rec["tables"]["paper_literal_N_eq_T"] = eval_table(pool_dps)
        unsel = rec["tables"]["unselected"]["sampled"]
        for rule in ("published_weight", "count_only"):
            stat = I.rule_statistic(rule, pool, W)
            relab = rngs["relabel"].permutation(stat)
            rel = eval_table(pool_dps[I.select_top(relab, perm, T)])["sampled"]
            Z = rngs["noise"].standard_normal(stat.size)
            curve = []
            for sg in SIGMAS:
                noisy = stat * np.maximum(0.0, 1.0 + sg * Z)
                curve.append(eval_table(pool_dps[I.select_top(noisy, perm, T)])["sampled"]["c_hat"])
            rec["nulls"][rule] = {"relabelled_c_hat": rel["c_hat"], "relabelled_wilson": [rel["wilson_lo"], rel["wilson_hi"]],
                                  "unselected_c_hat": unsel["c_hat"], "unselected_wilson": [unsel["wilson_lo"], unsel["wilson_hi"]],
                                  "relabelled_minus_unselected": rel["c_hat"] - unsel["c_hat"],
                                  "wilson_overlap": not (rel["wilson_hi"] < unsel["wilson_lo"] or unsel["wilson_hi"] < rel["wilson_lo"]),
                                  "sigma": SIGMAS, "sigma_c_hat": curve,
                                  "sigma_monotone_nonincreasing_sampled": all(curve[i + 1] <= curve[i] + 1e-12 for i in range(len(curve) - 1)),
                                  "note": "sampled coverage (M = 40000) -- monotonicity here is subject to sampling noise of half-width about 0.005"}
        cell["rules"][str(r)] = rec
        if (a, r) in MODEL.PUBLISHED_SCALED_COST:
            t = rec["tables"]["published_weight"]["sampled"]
            cell["fixture"][str(r)] = {"a": a, "r": r, "scaled_cost_sampled_this_seed": t["scaled_cost_sampled"], "hits": t["hits"],
                                       "total_steps": t["total_steps"], "M": t["M"], "scaled_cost_exact_expectation": None,
                                       "published_scaled_cost": MODEL.PUBLISHED_SCALED_COST[(a, r)],
                                       "residual_sampled_minus_published": t["scaled_cost_sampled"] - MODEL.PUBLISHED_SCALED_COST[(a, r)],
                                       "scaled_precomp_measured": rec["P_scaled_sqrtNT"], "published_scaled_precomp": MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)],
                                       "precomp_relative_residual": rec["P_scaled_sqrtNT"] / MODEL.PUBLISHED_SCALED_PRECOMP[(a, r)] - 1,
                                       "b4_model_scaled_precomp": MODEL.B4_CONTRACT_VALUES[(a, r)], "model_nt8_oracle_constant": MODEL.MODEL_NT8.get((a, r)), "theta": prm["theta"]}
    raw[key] = {"params": prm, "online_walks": {"seed": 100 + seed, "M": M_ONLINE, "terminal_dp": on_term.tolist(), "reached_within_8W": on_ok.tolist(), "length_charged": on_len.tolist()},
                "generation_stream": {"seed": 200 + seed, "walks_drawn": int(term.size), "walks_needed_for_rT_distinct": walks_needed},
                "pools_by_r": {str(r): cell["rules"][str(r)]["pool"] for r in R_GRID},
                "tables_sha256": {str(r): {rule: cell["rules"][str(r)]["tables"][rule]["table_sha256"] for rule in cell["rules"][str(r)]["tables"]} for r in R_GRID}}
    for r in R_GRID:
        cell["rules"][str(r)].pop("pool")
    summ[key] = cell
    log(f"  cell {key} done in {time.time()-t0:.1f}s: fixture={[(k, round(v['scaled_cost_sampled_this_seed'],3)) for k,v in cell['fixture'].items()]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log2N", type=int, default=30)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    log2N, seed = args.log2N, args.seed
    T = T_OF[log2N]; N = 1 << log2N
    K, K2 = I.walk_keys(seed)
    rngs = {"online": np.random.default_rng(100 + seed), "gen": np.random.default_rng(200 + seed),
            "relabel": np.random.default_rng(300 + seed), "tie": np.random.default_rng(400 + seed),
            "noise": np.random.default_rng(500 + seed)}
    log(f"sampled run log2N={log2N} T={T} seed={seed}")
    t0 = time.time(); raw, summ = {}, {}
    for a in A_GRID:
        run_cell(log2N, T, a, seed, rngs, raw, summ)
    header = {"experiment_id": "EXP-ECDLP-869870", "stage": "generic_sampled", "log2N": log2N, "N": N, "T": T, "seed": seed,
              "walk_key_K": K, "dp_key_K2": K2,
              "seeds": {"walk_key": seed, "online": 100 + seed, "generation_start": 200 + seed, "relabelling": 300 + seed, "tie_break": 400 + seed, "noise": 500 + seed},
              "certificate": {"kind": "none", "reason": "generic keyed-random-function arm: nothing is solved"},
              "a_grid": A_GRID, "r_grid": R_GRID, "m_factors": M_FACTORS, "sigmas": SIGMAS, "M_online": M_ONLINE, "bits_per_entry": 2 * log2N,
              "invalidity": {"exact_coverage_exceeds_global_oracle": [], "completed_invalid": False, "note": "no exact coverage at this stage; the exceedance rule has nothing to check"},
              "elapsed_seconds_compute": time.time() - t0}
    os.makedirs(args.out, exist_ok=True)
    json.dump(jsonable({"header": header, "cells": raw}), open(os.path.join(args.out, "raw-result.json"), "w"))
    json.dump(jsonable({"header": header, "cells": summ}), open(os.path.join(args.out, "summary.json"), "w"), indent=1)
    log(f"done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

"""v2 fixture compute: one (mixer, seed) exact-basin cell of EXP-ECDLP-869870.

N=2^24, T=256, a=1/4, caps 8W and 20W, published-weight table at r=2,
plus global-oracle top-T share. Observations only.

Usage:
  python3 run_generic_exact.py --mixer splitmix64 --seed 1 --out <run-dir>
  python3 run_generic_exact.py --mixer murmur3_fmix64 --seed 1 --out <run-dir>
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

LOG2N = 24
T = 256
A = 0.25
R_FIXTURE = 2
M_ONLINE = 40000
T_GEN_FACTOR = 16  # v1 generation continues to 16T; used only to prime splitmix RNG


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


def generate_until(p, ok8, N, rng, a, T, need_distinct):
    """v1 generation loop: draw chunks of max(4096, b4_walks(16,a,T))."""
    starts = np.empty(0, dtype=np.int64)
    while True:
        more = int(max(4096, MODEL.b4_walks(16, a, T)))
        starts = np.concatenate([starts, rng.integers(0, N, size=more, dtype=np.int64)])
        term = p[starts]
        ok = ok8[starts]
        distinct = np.unique(term[ok]).size
        if distinct >= need_distinct:
            break
    return starts


def prime_splitmix_v1_rng(f, rngs, log2N, N, T, K2, mixer):
    """Advance gen/online/tie the way v1 run_generic_exact does at a=0.125.

    v1 shares RNG streams across a in {1/8, 1/4, 1/2, 1}. Seeds 1-5 of the
    splitmix arm are a bit-for-bit check against RUN-011..015 on shared
    (N, a=1/4, cap, published_weight) fields. Those v1 cells consumed
    gen/online/tie at a=1/8 first. This prime reproduces that consumption
    (pointer jump + generation-to-16T + M online + tie.random(nDP)).
    Bootstrap / relabel / noise are not consumed: they do not enter the
    published-weight table or top-T share.
    """
    a_prime = 0.125
    prm = I.cell_params(log2N, T, a_prime, N)
    isdp = np.empty(N, dtype=bool)
    for lo in range(0, N, 1 << 21):
        hi = min(N, lo + (1 << 21))
        isdp[lo:hi] = I.is_dp_fn(np.arange(lo, hi, dtype=np.int64), K2, prm["dp_threshold"], mixer)
    dps = np.flatnonzero(isdp)
    nDP = int(dps.size)
    log(f"prime a=0.125: nDP={nDP} (RNG consume only; not a v2 fixture cell)")
    t0 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    log(f"  prime pointer jumping: {rounds} rounds, {time.time()-t0:.1f}s")
    bs8, ok8, capped8, cycle_mass = I.basin_sizes_at_cap(p, d, reach, isdp, N, prm["cap8"])
    _ = rngs["tie"].random(nDP)
    starts = generate_until(p, ok8, N, rngs["gen"], a_prime, T, T_GEN_FACTOR * T)
    _ = rngs["online"].integers(0, N, size=M_ONLINE, dtype=np.int64)
    log(f"  prime consumed gen walks_drawn={int(starts.size)} online={M_ONLINE} tie.nDP={nDP}")
    del p, d, reach, isdp, bs8, ok8, starts
    return {
        "primed": True,
        "a": a_prime,
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "capped_mass_8W": capped8,
        "note": "a=1/8 RNG prime to match v1 run_generic_exact stream order; not a v2 fixture observation",
    }


def run_fixture(log2N, T, a, seed, f, rngs, mixer, K, K2):
    N = 1 << log2N
    prm = I.cell_params(log2N, T, a, N)
    W = prm["W"]
    cap8 = prm["cap8"]
    cap20 = prm["cap20"]
    theta = prm["theta"]
    log(f"cell a={a}: W={W:.3f} cap8={cap8} cap20={cap20} T={T} mixer={mixer}")

    isdp = np.empty(N, dtype=bool)
    for lo in range(0, N, 1 << 21):
        hi = min(N, lo + (1 << 21))
        isdp[lo:hi] = I.is_dp_fn(np.arange(lo, hi, dtype=np.int64), K2, prm["dp_threshold"], mixer)
    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)

    t0 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    log(f"  pointer jumping: {rounds} rounds, {time.time()-t0:.1f}s; nDP={nDP}")

    bs8, ok8, capped8, cycle_mass = I.basin_sizes_at_cap(p, d, reach, isdp, N, cap8)
    bs20, ok20, capped20, _ = I.basin_sizes_at_cap(p, d, reach, isdp, N, cap20)
    bs8 = bs8.astype(np.int32)
    bs20 = bs20.astype(np.int32)
    len8_all_mean = float(np.where(ok8, d, cap8).mean())
    sizes8 = bs8[dps]
    sizes20 = bs20[dps]
    ms8 = I.compressed_hist(sizes8)
    ms20 = I.compressed_hist(sizes20)

    key_all = rngs["tie"].random(nDP)
    perm_all = np.argsort(np.argsort(key_all))
    glob8 = I.select_rule("global_oracle", None, T, None, W, None, sizes8, perm_all, dps)
    glob20 = I.select_rule("global_oracle", None, T, None, W, None, sizes20, perm_all, dps)
    share8 = I.exact_coverage(glob8, bs8, N)
    share20 = I.exact_coverage(glob20, bs20, N)
    isdp_pos = np.full(N, -1, dtype=np.int64)
    isdp_pos[dps] = np.arange(nDP)

    # Generation: continue until r=2 needs 2T distinct. Chunk size matches v1
    # (max(4096, b4_walks(16,a,T))) so the start-stream prefix is the v1 prefix.
    need_distinct = R_FIXTURE * T
    starts = generate_until(p, ok8, N, rngs["gen"], a, T, need_distinct)
    term = p[starts]
    ok = ok8[starts]
    length = np.where(ok, d[starts], cap8).astype(np.int64)
    _, first_idx = np.unique(term[ok], return_index=True)
    ok_idx = np.flatnonzero(ok)
    first_walk = np.sort(ok_idx[first_idx])
    walks_needed = int(first_walk[need_distinct - 1] + 1)

    on_starts = rngs["online"].integers(0, N, size=M_ONLINE, dtype=np.int64)
    on_term = p[on_starts]
    on_ok = ok8[on_starts]
    on_len = np.where(on_ok, d[on_starts], cap8).astype(np.int64)
    on_mean_len = float(on_len.mean())

    m = walks_needed
    tdp = term[:m][ok[:m]]
    ln = length[:m][ok[:m]]
    pool_dps = np.unique(tdp)
    if pool_dps.size != need_distinct:
        raise RuntimeError(f"pool size {pool_dps.size} != {need_distinct}")
    h = np.bincount(tdp, minlength=N)[pool_dps].astype(np.int64)
    S = np.bincount(tdp, weights=ln, minlength=N)[pool_dps].astype(np.int64)
    P = int(length[:m].sum())
    pool = {"dps": pool_dps, "h": h, "S": S}
    perm = perm_all[isdp_pos[pool_dps]]
    table = I.select_rule("published_weight", pool, T, perm, W, bs8, sizes8, perm_all, dps)

    mask = np.zeros(N, dtype=bool)
    mask[table] = True
    c8v = I.exact_coverage(table, bs8, N)
    c20v = I.exact_coverage(table, bs20, N)
    on = I.online_eval(table, on_term, on_ok, on_len, N, T, mask)
    exact_cost = len8_all_mean / c8v / math.sqrt(N / T) if c8v > 0 else float("inf")
    scaled_P = P / math.sqrt(N * T)
    pub_c = MODEL.PUBLISHED_SCALED_COST[(a, R_FIXTURE)]
    pub_p = MODEL.PUBLISHED_SCALED_PRECOMP[(a, R_FIXTURE)]
    oth = I.o_theta_correction_status()
    raw_residual_cost = on["scaled_cost_sampled"] - pub_c
    raw_residual_P_rel = scaled_P / pub_p - 1.0

    exceed = bool(c8v > share8 + 1e-15)
    cell = {
        "params": prm,
        "seed": seed,
        "mixer": mixer,
        "walk_projection": "top_bits" if mixer == "splitmix64" else "mod_N",
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "cycle_mass_frac": cycle_mass / N,
        "capped_mass_8W": capped8,
        "capped_mass_8W_frac": capped8 / N,
        "capped_mass_20W": capped20,
        "capped_mass_20W_frac": capped20 / N,
        "exact_mean_online_walk_length_8W": len8_all_mean,
        "sampled_mean_online_walk_length_8W": on_mean_len,
        "global_oracle": {
            "top_T_share_8W": share8,
            "top_T_share_20W": share20,
            "table_sha256_8W": I.table_hash(glob8),
            "C_max_contract": MODEL.CMAX_CONTRACT[a][1],
            "ratio_to_c_max_contract": share8 / MODEL.CMAX_CONTRACT[a][1],
            "ratio_to_c_max_numeric": share8 / MODEL.c_max(a),
            "model": MODEL.model_table(a),
        },
        "generation": {
            "walks_drawn": int(starts.size),
            "walks_needed_for_2T_distinct": walks_needed,
            "b4_model_walks_r2": MODEL.b4_walks(R_FIXTURE, a, T),
        },
        "published_weight_r2": {
            "r": R_FIXTURE,
            "walks": m,
            "P_group_ops": P,
            "scaled_P": scaled_P,
            "pool_size": int(pool_dps.size),
            "pool_sha256": I.table_hash(pool_dps),
            "table_sha256": I.table_hash(table),
            "coverage_exact_8W": c8v,
            "coverage_exact_20W": c20v,
            "sampled": on,
            "exact_inside_wilson": bool(on["wilson_lo"] <= c8v <= on["wilson_hi"]),
            "scaled_cost_exact_expectation": exact_cost,
            "scaled_cost_sampled": on["scaled_cost_sampled"],
            "exceeds_global_oracle_8W": exceed,
        },
        "fixture": {
            "a": a,
            "r": R_FIXTURE,
            "scaled_cost_sampled_this_seed": on["scaled_cost_sampled"],
            "hits": on["hits"],
            "total_steps": on["total_steps"],
            "M": on["M"],
            "scaled_cost_exact_expectation": exact_cost,
            "published_scaled_cost": pub_c,
            "residual_sampled_minus_published_raw": raw_residual_cost,
            "residual_exact_minus_published_raw": exact_cost - pub_c,
            "o_theta_correction": oth,
            "scaled_precomp_measured": scaled_P,
            "published_scaled_precomp": pub_p,
            "precomp_relative_residual_raw": raw_residual_P_rel,
            "b4_model_scaled_precomp": MODEL.b4_scaled_precomp(R_FIXTURE, a),
            "theta": theta,
        },
        "exceedance": ([{"r": R_FIXTURE, "rule": "published_weight",
                         "coverage": c8v, "global_share": share8}] if exceed else []),
    }
    raw = {
        "params": prm,
        "basin_multiset_8W": ms8,
        "basin_multiset_20W": ms20,
        "n_dps": nDP,
        "cycle_mass": cycle_mass,
        "capped_mass_8W": capped8,
        "capped_mass_20W": capped20,
        "global_oracle_table_8W": glob8.tolist(),
        "published_weight_table": table.tolist(),
        "online_walks": {
            "seed": 100 + seed,
            "M": M_ONLINE,
            "terminal_dp": on_term.tolist(),
            "reached_within_8W": on_ok.tolist(),
            "length_charged": on_len.tolist(),
        },
        "generation_stream": {
            "seed": 200 + seed,
            "walks_drawn": int(starts.size),
            "walks_needed_for_2T_distinct": walks_needed,
        },
        "pool": {
            "dp": pool_dps.tolist(),
            "h": h.tolist(),
            "S": S.tolist(),
            "basin_8W": bs8[pool_dps].tolist(),
            "basin_20W": bs20[pool_dps].tolist(),
        },
    }
    log(f"  fixture: share8={share8:.4f} cost_s={on['scaled_cost_sampled']:.4f} "
        f"cost_x={exact_cost:.4f} P={scaled_P:.4f} cycle={cycle_mass} cap8={capped8}")
    del p, d, reach, isdp, bs8, bs20, ok8, ok20
    return cell, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mixer", required=True, choices=list(I.MIXERS))
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log2N", type=int, default=LOG2N)
    ap.add_argument("--T", type=int, default=T)
    args = ap.parse_args()
    mixer, seed = args.mixer, args.seed
    log2N, Tloc = args.log2N, args.T
    N = 1 << log2N
    keyrec = I.keys_for(mixer, seed)
    K, K2 = keyrec["K"], keyrec["K2"]
    rngs = {
        "online": np.random.default_rng(100 + seed),
        "gen": np.random.default_rng(200 + seed),
        "relabel": np.random.default_rng(300 + seed),
        "tie": np.random.default_rng(400 + seed),
        "noise": np.random.default_rng(500 + seed),
        "boot": np.random.default_rng(600 + seed),
    }
    log(f"run mixer={mixer} log2N={log2N} N={N} T={Tloc} seed={seed} "
        f"K={K:#x} K2={K2:#x} projection={keyrec['walk_projection']}")
    if keyrec["walk_key_string"]:
        log(f"  walk_key_string={keyrec['walk_key_string']}")
        log(f"  dp_key_string={keyrec['dp_key_string']}")
    t0 = time.time()
    f = np.empty(N, dtype=np.int32)
    for lo in range(0, N, 1 << 21):
        hi = min(N, lo + (1 << 21))
        f[lo:hi] = I.step_fn(np.arange(lo, hi, dtype=np.int64), K, log2N, mixer)
    log(f"walk map built in {time.time()-t0:.1f}s")

    prime_rec = None
    if mixer == "splitmix64":
        prime_rec = prime_splitmix_v1_rng(f, rngs, log2N, N, Tloc, K2, mixer)

    cell, raw = run_fixture(log2N, Tloc, A, seed, f, rngs, mixer, K, K2)
    exceed = cell["exceedance"]
    header = {
        "experiment_id": "EXP-ECDLP-869870",
        "protocol": "PA-ECDLP-869870-v1-to-v2",
        "stage": "v2_rekeyed_fixture",
        "kind": "fixture",
        "log2N": log2N,
        "N": N,
        "T": Tloc,
        "a": A,
        "seed": seed,
        "mixer": mixer,
        "walk_projection": keyrec["walk_projection"],
        "walk_key_K": K,
        "dp_key_K2": K2,
        "walk_key_string": keyrec["walk_key_string"],
        "dp_key_string": keyrec["dp_key_string"],
        "key_derivation": keyrec["key_derivation"],
        "seeds": {
            "walk_key": seed,
            "online": 100 + seed,
            "generation_start": 200 + seed,
            "relabelling": 300 + seed,
            "tie_break": 400 + seed,
            "noise": 500 + seed,
            "bootstrap": 600 + seed,
        },
        "certificate": {"kind": "none", "reason": "generic keyed-random-function arm: nothing is solved",
                        "verified": None, "verifier": None},
        "a_grid": [A],
        "r_grid": [R_FIXTURE],
        "M_online": M_ONLINE,
        "bits_per_entry": 2 * log2N,
        "splitmix_v1_rng_prime": prime_rec,
        "invalidity": {
            "exact_coverage_exceeds_global_oracle": exceed,
            "completed_invalid": bool(exceed),
        },
        "elapsed_seconds_compute": time.time() - t0,
    }
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "raw-result.json"), "w") as fh:
        json.dump(jsonable({"header": header, "cells": {"a=0.25": raw}}), fh)
    with open(os.path.join(args.out, "summary.json"), "w") as fh:
        json.dump(jsonable({"header": header, "cells": {"a=0.25": cell}}), fh, indent=1)
    log(f"done in {time.time()-t0:.1f}s; exceedances={len(exceed)}")


if __name__ == "__main__":
    main()

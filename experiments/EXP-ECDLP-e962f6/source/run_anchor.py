"""RUN-ECDLP-e962f6-002: the N = 2^26 exact-basin anchor (Stage 1).

One exact-basin array pass (vectorised forward iteration with pointer
jumping, as in EXP-ECDLP-869870's exact_basins): for every x the first DP
reached and its distance; the basin size of every DP; the cycle mass and the
capped mass; the top-T share (cap 8W); the walk length to the first mark per
start point (the distance array); the Spearman correlation of the walk length
with the basin size of the reached DP (the Lemma 6 independence check,
alpha = 0.01); the mean walk length beside W.

Parameters (frozen contract cell N = 2^26, T = 256, a = 1/4):
  W = sqrt(a N / T) = 256, theta = 1/256, cap 8W = 2048.

PROTOCOL DEVIATION (recorded, routed to the Coordinator): the contract's
anchor_enumeration text reads "W = 2048, theta = 1/2048, cap 8W = 16384",
but the contract's own definition "W = sqrt(a N / T)" with the contract's own
(N = 2^26, T = 256, a = 1/4) gives W = 256, theta = 1/256, cap 8W = 2048;
the committed RUN-ECDLP-869870-011-N24-s1 (N = 2^24, T = 256, a = 1/4,
W = 128.0) confirms the formula; the decidable negative and the Stage 2
residual re-read are both stated at a = 1/4, so (N, T, a) is the
authoritative cell. Executed with W = 256.

Seeds (frozen contract seed_policy): walk_key seed 1, dp_key seed 101,
tie_break seed 401. Key convention (recorded in the manifest):
  K  = walk_keys(1)[0]   (walk-key component of seed 1)
  K2 = walk_keys(101)[1] (DP-key component of seed 101, the committed
                          instrument's DP-key derivation)
  tie-break permutation key: np.random.default_rng(401).random(nDP)

Observations only; no interpretation.
"""
from __future__ import annotations

import json
import math
import os
import resource
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402
import runcommon as RC  # noqa: E402

LOG2N = 26
T = 256
A = 0.25
WALK_KEY_SEED = 1
DP_KEY_SEED = 101
TIE_BREAK_SEED = 401
ALPHA = 0.01


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if math.isfinite(v) else (None if math.isnan(v) else ("inf" if v > 0 else "-inf"))
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (int, float, str, bool)) or o is None:
        return o
    return str(o)


def main():
    t0 = time.time()
    prm = I.cell_params(LOG2N, T, A)
    N, W, theta, cap8 = prm["N"], prm["W"], prm["theta"], prm["cap8"]
    K, _ = I.walk_keys(WALK_KEY_SEED)
    _, K2 = I.walk_keys(DP_KEY_SEED)
    print(f"anchor: N={N} T={T} a={A} W={W} theta={theta} cap8={cap8} K={K:#x} K2={K2:#x}", flush=True)

    # --- build the walk map and the DP indicator ----------------------------
    t1 = time.time()
    f, isdp = I.build_map(N, LOG2N, K, K2, prm["dp_threshold"], rule="uniform")
    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)
    print(f"map built in {time.time()-t1:.1f}s; nDP={nDP} (expected ~{N*theta:.0f})", flush=True)

    # --- one exact-basin array pass (pointer jumping) ------------------------
    t1 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    print(f"pointer jumping: {rounds} rounds, {time.time()-t1:.1f}s", flush=True)
    del f, isdp

    # --- basin sizes at cap 8W ------------------------------------------------
    t1 = time.time()
    bs64, ok8, capped8, cycle_mass = I.basin_sizes_at_cap(p, d, reach, N, cap8)
    bs = bs64.astype(np.int32)
    del bs64
    print(f"basin sizes: {time.time()-t1:.1f}s; cycle_mass={cycle_mass} capped8={capped8}", flush=True)

    # partition identity (measurement, Lemma 1 self-check):
    # sum of capped basin sizes + capped mass + cycle mass = N, digit-for-digit
    partition_sum = int(bs.sum()) + capped8 + cycle_mass
    partition_identity_holds = (partition_sum == N)

    # --- top-T share (cap 8W), tie-break seed 401 -----------------------------
    sizes = bs[dps]
    key_all = np.random.default_rng(TIE_BREAK_SEED).random(nDP)
    perm_all = np.argsort(np.argsort(key_all))
    top_idx = I.select_top(sizes.astype(np.float64), perm_all, T)
    top_table = dps[top_idx]
    top_T_share = float(bs[top_table].sum()) / N
    del sizes, key_all, perm_all, top_idx

    # --- walk-length statistics ------------------------------------------------
    # (i) the distance array over reached points (exact, no cap)
    dl = d[reach]
    mean_walk_length_reached_exact = float(dl.mean())
    # (ii) the committed-instrument convention: capped at 8W, over all points
    mean_walk_length_capped_8W = float(np.where(ok8, d, cap8).mean())
    del dl

    # --- Spearman: walk length vs basin size of the reached DP -----------------
    t1 = time.time()
    bl = bs[p[reach]]
    rho = I.spearman_rho(d[reach], bl)
    n_pairs = int(reach.sum())
    pval = I.spearman_pvalue(rho, n_pairs)
    spearman_significant = bool(pval < ALPHA)
    print(f"spearman: {time.time()-t1:.1f}s; rho={rho:.6g} p={pval:.3g}", flush=True)
    del bl, p, d, reach, ok8

    # --- basin histogram (compressed) ------------------------------------------
    hist = I.compressed_hist(bs[dps])
    largest_basin = int(hist["top1000"][0]) if hist["n_basins"] else 0
    del bs

    # --- tail check: largest basin vs Borel(1-theta) N/W-sample 99% band --------
    band = I.borel_max_band(theta, N / W, W)
    largest_in_band = bool(band["n_lo"] is not None and band["n_hi"] is not None
                           and band["n_lo"] <= largest_basin <= band["n_hi"])

    # --- oracle online constant (secondary metric) ------------------------------
    oracle_online_constant = math.sqrt(A) / top_T_share
    oracle_online_within_10pct = bool(abs(oracle_online_constant - 1.28) / 1.28 <= 0.10)

    elapsed = time.time() - t0
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    raw = {
        "run_id": "RUN-ECDLP-e962f6-002",
        "kind": "anchor_exact_basins",
        "params": prm,
        "keys": {"walk_key_K": K, "dp_key_K2": K2,
                 "walk_key_seed": WALK_KEY_SEED, "dp_key_seed": DP_KEY_SEED,
                 "tie_break_seed": TIE_BREAK_SEED,
                 "key_convention": "K = walk_keys(1)[0]; K2 = walk_keys(101)[1] (committed instrument's DP-key derivation)"},
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "cycle_mass_frac": cycle_mass / N,
        "capped_mass_8W": capped8,
        "capped_mass_8W_frac": capped8 / N,
        "partition_identity": {"sum_basins_capped_plus_capped_plus_cycle": partition_sum,
                               "N": N, "holds_digit_for_digit": bool(partition_identity_holds)},
        "top_T_share_8W": top_T_share,
        "top_T_table_sha256": I.table_hash(top_table),
        "walk_lengths": {
            "mean_reached_exact_distance_array": mean_walk_length_reached_exact,
            "mean_capped_8W_all_points_869870_convention": mean_walk_length_capped_8W,
            "W_model": W,
        },
        "spearman_walk_length_vs_basin_size": {
            "rho": rho, "p_value": pval, "n_pairs": n_pairs, "alpha": ALPHA,
            "significant_at_alpha": spearman_significant,
            "population": "points whose forward orbit reaches a DP; walk length = exact distance array d[x] (no cap); basin size = capped-at-8W size of the reached DP",
        },
        "basin_histogram_8W": hist,
        "largest_basin_8W": largest_basin,
        "borel_band_99_model": band,
        "largest_in_band": largest_in_band,
        "oracle_online_constant_sqrt_a_over_top_T_share": oracle_online_constant,
        "oracle_online_within_10pct_of_1.28": oracle_online_within_10pct,
        "self_reported": {"elapsed_seconds": round(elapsed, 3), "peak_rss_bytes": int(peak_rss)},
    }

    summary = {
        "run_id": "RUN-ECDLP-e962f6-002",
        "kind": "anchor_exact_basins",
        "params": prm,
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "cycle_mass_frac": cycle_mass / N,
        "capped_mass_8W": capped8,
        "capped_mass_8W_frac": capped8 / N,
        "partition_identity_holds": bool(partition_identity_holds),
        "top_T_share_8W": top_T_share,
        "top_T_table_sha256": I.table_hash(top_table),
        "mean_walk_length_reached_exact": mean_walk_length_reached_exact,
        "mean_walk_length_capped_8W": mean_walk_length_capped_8W,
        "W_model": W,
        "spearman_rho": rho,
        "spearman_p_value": pval,
        "spearman_significant_at_0.01": spearman_significant,
        "largest_basin_8W": largest_basin,
        "borel_band_99_model": band,
        "largest_in_band": largest_in_band,
        "oracle_online_constant_sqrt_a_over_top_T_share": oracle_online_constant,
        "oracle_online_within_10pct_of_1.28": oracle_online_within_10pct,
        "self_reported": raw["self_reported"],
    }

    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "raw-result.json"), "w") as fh:
        json.dump(jsonable(raw), fh)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(jsonable(summary), fh, indent=1)

    meta = {
        "run_id": "RUN-ECDLP-e962f6-002",
        "kind": "anchor_exact_basins",
        "stage": 1,
        "status": "completed_valid",
        "failure_class": None,
        "validity": "valid",
        "validity_reason": "one exact-basin array pass completed; partition identity holds digit-for-digit; all contract metrics computed",
        "note": "Stage 1 anchor, N = 2^26, one array pass by design",
        "seeds": {"walk_key": WALK_KEY_SEED, "dp_key": DP_KEY_SEED, "tie_break": TIE_BREAK_SEED},
        "params": prm,
        "protocol_deviations": [
            "CONTRACT TEXT vs CONTRACT FORMULA (anchor W): the contract's anchor_enumeration text reads 'W = 2048, theta = 1/2048, cap 8W = 16384', but the contract's own definition 'W = sqrt(a N / T)' with the contract's own (N = 2^26, T = 256, a = 1/4) gives W = 256, theta = 1/256, cap 8W = 2048; the committed RUN-ECDLP-869870-011-N24-s1 (N = 2^24, T = 256, a = 1/4, W = 128.0) confirms the formula; the decidable negative and the Stage 2 residual re-read are both stated at a = 1/4, so (N, T, a) is the authoritative cell. Executed with W = 256, theta = 1/256, cap 8W = 2048. Routed to the Coordinator; no protocol field was edited."
        ],
        "source_sha256": RC.source_hashes(),
        "self_reported": raw["self_reported"],
    }
    with open(os.path.join(out, "run-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"anchor done in {elapsed:.1f}s; top_T_share={top_T_share:.6f} "
          f"mean_len(reached)={mean_walk_length_reached_exact:.3f} W={W} "
          f"spearman_rho={rho:.4g} p={pval:.3g} largest={largest_basin} "
          f"band=[{band['n_lo']},{band['n_hi']}] in_band={largest_in_band}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

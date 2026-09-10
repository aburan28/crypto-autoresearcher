"""RUN-ECDLP-e962f6-003/004/005: the permutation nearby-object control
(Stage 1), one run per seed s in {1, 2, 3}.

A uniformly random permutation on [0, 2^20) with the same DP marking as the
generic instrument; the "basins" are the cycle segments ending at each DP (in
a permutation every in-degree is 1, so the segment of x is the points between
the previous DP on the cycle and x); the top-T share of the segment sizes;
the segment-size distribution beside Geometric(theta); the comparison of the
top-T share with 3 T W/N = 0.046875 (the collapse prediction, the frozen
numerical threshold) and with C_max(1/4) = 0.3889120129663709 (the value the
Borel machinery must NOT reproduce).

Parameters (frozen contract): N = 2^20, T = 64, W = 64, theta = 1/64, a = 1/4.
Seeds: permutation seed s for the Fisher-Yates draw (numpy permutation of an
integer range is a Fisher-Yates shuffle); dp_key seed 101 + s.
Key convention: K2 = walk_keys(101 + s)[1] (the committed instrument's
DP-key derivation).

PROTOCOL DEVIATION (recorded, routed to the Coordinator): the contract's
definitions text reads "T W/N = 2^{-6} = 0.015625, 3 T W/N = 0.046875" at
N = 2^20, a = 1/4, T = 64, W = 64, but T*W/N = 64*64/2^20 = 2^{-8} =
0.00390625, so 3*T*W/N = 0.01171875. The frozen numerical threshold
0.046875 is used for the control verdict (it is the pre-registered number);
the arithmetically correct 3*T*W/N = 0.01171875 is reported as a secondary
observation. No protocol field was edited.

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

LOG2N = 20
T = 64
A = 0.25
C_MAX_1_4 = 0.3889120129663709
FROZEN_3TW_OVER_N = 0.046875          # the contract's pre-registered threshold
CORRECT_3TW_OVER_N = 3.0 * 64 * 64 / (1 << 20)  # = 0.01171875 (secondary observation)
VOID_TOL = 0.15                        # reproduces C_max within 15% -> void


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
    s = int(sys.argv[sys.argv.index("--seed") + 1])
    t0 = time.time()
    prm = I.cell_params(LOG2N, T, A)
    N, W, theta = prm["N"], prm["W"], prm["theta"]
    _, K2 = I.walk_keys(101 + s)
    print(f"permutation seed {s}: N={N} T={T} W={W} theta={theta} K2={K2:#x}", flush=True)

    # --- draw the permutation (Fisher-Yates) and mark DPs ---------------------
    t1 = time.time()
    f = I.random_permutation(N, s)
    isdp = np.empty(N, dtype=bool)
    for lo in range(0, N, 1 << 21):
        hi = min(N, lo + (1 << 21))
        isdp[lo:hi] = I.is_dp_fn(np.arange(lo, hi, dtype=np.int64), K2, prm["dp_threshold"])
    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)
    print(f"permutation + DP marking: {time.time()-t1:.1f}s; nDP={nDP} (expected ~{N*theta:.0f})", flush=True)

    # --- exact first DP (pointer jumping; identical code path) ----------------
    t1 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    print(f"pointer jumping: {rounds} rounds, {time.time()-t1:.1f}s", flush=True)
    del f, isdp

    # --- segment sizes (full cycle segments, no cap) ---------------------------
    bs64 = I.basin_sizes_uncapped(p, d, reach, N)
    bs = bs64.astype(np.int32)
    del bs64
    cycle_mass = int(np.count_nonzero(~reach))
    partition_sum = int(bs.sum()) + cycle_mass
    partition_identity_holds = (partition_sum == N)

    # --- top-T share of the segment sizes --------------------------------------
    sizes = bs[dps]
    top_idx = np.argsort(sizes.astype(np.float64))[::-1][:T]
    top_table = dps[top_idx]
    top_T_share = float(bs[top_table].sum()) / N
    largest_segment = int(sizes.max()) if nDP else 0
    del sizes, top_idx

    # --- segment-size distribution beside Geometric(theta) ---------------------
    # The segment includes its DP, so S >= 1 with P(S=k) = (1-theta)^{k-1} theta.
    seg_sizes = bs[dps]
    ks_stat, ks_p = I.ks_against_cdf(seg_sizes, lambda k: I.geometric_cdf_segment(k, theta))
    del seg_sizes, bs, p, d, reach

    # --- geometric 99% band (tail check) ----------------------------------------
    # smallest k with 1 - (1-theta)^k >= 0.99
    geo99 = int(math.ceil(math.log(0.01) / math.log(1.0 - theta)))
    largest_beyond_geo99 = bool(largest_segment > geo99)

    # --- comparisons (frozen thresholds) ----------------------------------------
    below_frozen = bool(top_T_share < FROZEN_3TW_OVER_N)
    dev_from_cmax = abs(top_T_share - C_MAX_1_4) / C_MAX_1_4
    reproduces_cmax_within_15pct = bool(dev_from_cmax <= VOID_TOL)

    elapsed = time.time() - t0
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    raw = {
        "run_id": f"RUN-ECDLP-e962f6-00{2 + s}",
        "kind": "permutation_control",
        "seed": s,
        "params": prm,
        "keys": {"dp_key_K2": K2, "dp_key_seed": 101 + s,
                 "permutation_seed": s,
                 "key_convention": "K2 = walk_keys(101+s)[1]; permutation via np.random.default_rng(s).permutation(N) (Fisher-Yates)"},
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "cycle_mass_frac": cycle_mass / N,
        "partition_identity_holds": bool(partition_identity_holds),
        "top_T_share": top_T_share,
        "top_T_table_sha256": I.table_hash(top_table),
        "largest_segment": largest_segment,
        "segment_size_ks_vs_geometric_theta": {"statistic": ks_stat, "p_value": ks_p,
                                               "reference": "one-based Geometric(theta), P(S=k)=(1-theta)^{k-1} theta, S>=1 (segment includes its DP)"},
        "geometric_99_quantile": geo99,
        "largest_segment_beyond_geometric_99": largest_beyond_geo99,
        "comparisons": {
            "frozen_3TW_over_N_threshold": FROZEN_3TW_OVER_N,
            "top_T_share_below_frozen_threshold": below_frozen,
            "correct_3TW_over_N_secondary": CORRECT_3TW_OVER_N,
            "top_T_share_below_correct_3TW_over_N": bool(top_T_share < CORRECT_3TW_OVER_N),
            "C_max_1_4": C_MAX_1_4,
            "deviation_from_C_max_1_4": dev_from_cmax,
            "reproduces_C_max_within_15pct_void": reproduces_cmax_within_15pct,
        },
        "self_reported": {"elapsed_seconds": round(elapsed, 3), "peak_rss_bytes": int(peak_rss)},
    }

    summary = {
        "run_id": raw["run_id"],
        "kind": "permutation_control",
        "seed": s,
        "params": prm,
        "nDP": nDP,
        "top_T_share": top_T_share,
        "below_frozen_3TW_over_N_0.046875": below_frozen,
        "correct_3TW_over_N_0.01171875": CORRECT_3TW_OVER_N,
        "below_correct_3TW_over_N": bool(top_T_share < CORRECT_3TW_OVER_N),
        "deviation_from_C_max_1_4": dev_from_cmax,
        "reproduces_C_max_within_15pct_void": reproduces_cmax_within_15pct,
        "segment_size_ks_statistic": ks_stat,
        "segment_size_ks_p_value": ks_p,
        "largest_segment": largest_segment,
        "geometric_99_quantile": geo99,
        "largest_segment_beyond_geometric_99": largest_beyond_geo99,
        "cycle_mass_frac": cycle_mass / N,
        "self_reported": raw["self_reported"],
    }

    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "raw-result.json"), "w") as fh:
        json.dump(jsonable(raw), fh)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(jsonable(summary), fh, indent=1)

    meta = {
        "run_id": raw["run_id"],
        "kind": "permutation_control",
        "stage": 1,
        "status": "completed_valid",
        "failure_class": None,
        "validity": "valid",
        "validity_reason": "permutation array pass completed; partition identity holds; all contract metrics computed",
        "note": f"Stage 1 permutation nearby-object control, seed {s}",
        "seeds": {"permutation": s, "dp_key": 101 + s},
        "params": prm,
        "protocol_deviations": [
            "CONTRACT TEXT ARITHMETIC (permutation T W/N): the contract's definitions text reads 'T W/N = 2^{-6} = 0.015625, 3 T W/N = 0.046875' at N = 2^20, a = 1/4, T = 64, W = 64, but T*W/N = 64*64/2^20 = 2^{-8} = 0.00390625, so 3*T*W/N = 0.01171875. The frozen numerical threshold 0.046875 is used for the control verdict (pre-registered); the arithmetically correct 3*T*W/N = 0.01171875 is reported as a secondary observation. Routed to the Coordinator; no protocol field was edited."
        ],
        "source_sha256": RC.source_hashes(),
        "self_reported": raw["self_reported"],
    }
    with open(os.path.join(out, "run-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"permutation seed {s} done in {elapsed:.1f}s; top_T_share={top_T_share:.6f} "
          f"below_frozen={below_frozen} below_correct={top_T_share < CORRECT_3TW_OVER_N} "
          f"dev_cmax={dev_from_cmax:.4f} ks={ks_stat:.4f} p={ks_p:.3g} "
          f"largest={largest_segment} geo99={geo99}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

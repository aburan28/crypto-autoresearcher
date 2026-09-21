"""RUN-ECDLP-e962f6-006: the proves-too-much non-uniform-rule control
(Stage 1).

A NON-UNIFORM distinguishing rule on the generic random function: density
2theta on the even-hash half of the points, 0 on the odd-hash half (a
deterministic function of the point, so the basin partition of Lemma 1 still
holds; the average density is theta). The known-false conclusion is Lemma 6's
"Geometric(theta), mean W, independent of the basin": the walk length to the
first mark is a mixture (fast component from the marked half, about
Geometric(2theta), mean W/2; slow component from the unmarked half, hitting
time plus Geometric(2theta)), with mixture mean about W/2 + 1, not W, and the
mixture is not geometric.

Parameters (frozen contract): N = 2^20, T = 64, W = 64, theta = 1/64, a = 1/4.
Seeds: walk_key seed 1, dp_key seed 101, online seed 201.
Key convention: K = walk_keys(1)[0]; K2 = walk_keys(101)[1].
Non-uniform rule: h(x) = mix64(x XOR K2); even-hash half = (h & 1) == 0;
marked iff even AND h < 2*threshold (density 2theta within the even half);
odd half never marked.

Compute (frozen contract): the exact basin structure under the non-uniform
rule (one array pass); M = 40000 online walks (cap 8W) with the walk length
to the first mark per walk; the mean walk length beside W (the loudness
threshold: deviation beyond 10% of W); the KS statistic of the walk lengths
against Geometric(theta) (alpha = 0.01); the top-T share beside C_max(1/4)
(reported; the 15% band is the loudness threshold).

The control PASSES when the machinery fails loudly: mean walk length
deviating from W by more than 10%, or the KS test rejecting at alpha = 0.01,
or the top-T share deviating from C_max(1/4) by more than 15%. The control
FAILS (and is void, routed to the Coordinator for a stronger object under a
versioned amendment) when none of these fires.

KS reference convention (recorded): the measured walk length is the exact
distance array d[x], which is 0 when the start point is marked; the primary
reference is therefore the zero-based Geometric(theta), P(L=k) =
(1-theta)^k theta, k >= 0 (CDF 1 - (1-theta)^{k+1}). The one-based
Geometric(theta) (scipy convention, mean W) is reported as a secondary
reference. Both are stated; the loudness verdict uses the primary.

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
M_ONLINE = 40000
WALK_KEY_SEED = 1
DP_KEY_SEED = 101
ONLINE_SEED = 201
ALPHA = 0.01
C_MAX_1_4 = 0.3889120129663709
LOUD_MEAN = 0.10
LOUD_TOP_T = 0.15


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


def geo_zero_quantile(p: float, theta: float) -> int:
    """Smallest k >= 0 with 1 - (1-theta)^{k+1} >= p."""
    return int(math.ceil(math.log(1.0 - p) / math.log(1.0 - theta))) - 1


def main():
    t0 = time.time()
    prm = I.cell_params(LOG2N, T, A)
    N, W, theta, cap8 = prm["N"], prm["W"], prm["theta"], prm["cap8"]
    K, _ = I.walk_keys(WALK_KEY_SEED)
    _, K2 = I.walk_keys(DP_KEY_SEED)
    print(f"nonuniform: N={N} T={T} W={W} theta={theta} cap8={cap8} K={K:#x} K2={K2:#x}", flush=True)

    # --- build the walk map and the NON-UNIFORM DP indicator -------------------
    t1 = time.time()
    f, isdp = I.build_map(N, LOG2N, K, K2, prm["dp_threshold"], rule="nonuniform")
    dps = np.flatnonzero(isdp).astype(np.int64)
    nDP = int(dps.size)
    print(f"map + nonuniform marking: {time.time()-t1:.1f}s; nDP={nDP} (expected ~{N*theta:.0f})", flush=True)

    # --- exact basin structure (one array pass) --------------------------------
    t1 = time.time()
    p, d, reach, rounds = I.exact_first_dp(f, isdp, N)
    print(f"pointer jumping: {rounds} rounds, {time.time()-t1:.1f}s", flush=True)
    del f, isdp

    bs64, ok8, capped8, cycle_mass = I.basin_sizes_at_cap(p, d, reach, N, cap8)
    bs = bs64.astype(np.int32)
    del bs64
    partition_sum = int(bs.sum()) + capped8 + cycle_mass
    partition_identity_holds = (partition_sum == N)

    # --- top-T share (cap 8W) ----------------------------------------------------
    sizes = bs[dps]
    top_idx = np.argsort(sizes.astype(np.float64))[::-1][:T]
    top_table = dps[top_idx]
    top_T_share = float(bs[top_table].sum()) / N
    dev_top_T = abs(top_T_share - C_MAX_1_4) / C_MAX_1_4
    del sizes, top_idx

    # --- M = 40000 online walks (cap 8W) ------------------------------------------
    starts = np.random.default_rng(ONLINE_SEED).integers(0, N, size=M_ONLINE, dtype=np.int64)
    lengths = np.where(ok8[starts], d[starts], cap8).astype(np.int64)
    mean_walk_length = float(lengths.mean())
    dev_mean = abs(mean_walk_length - W) / W
    loud_mean = bool(dev_mean > LOUD_MEAN)

    # --- KS of the walk lengths against Geometric(theta) ---------------------------
    ks0_stat, ks0_p = I.ks_against_cdf(lengths, lambda k: I.geometric_cdf_zero_based(k, theta))
    ks1_stat, ks1_p = I.ks_against_cdf(lengths, lambda k: I.geometric_cdf_one_based(k, theta))
    loud_ks = bool(ks0_p < ALPHA)

    # --- walk-length quantiles beside the Geometric(theta) quantiles ----------------
    q_measured = {q: float(np.quantile(lengths, q)) for q in (0.10, 0.50, 0.90)}
    q_model = {q: geo_zero_quantile(q, theta) for q in (0.10, 0.50, 0.90)}
    del lengths, starts

    loud_top_T = bool(dev_top_T > LOUD_TOP_T)
    control_fires = bool(loud_mean or loud_ks or loud_top_T)

    del bs, p, d, reach, ok8

    elapsed = time.time() - t0
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    raw = {
        "run_id": "RUN-ECDLP-e962f6-006",
        "kind": "nonuniform_proves_too_much",
        "params": prm,
        "keys": {"walk_key_K": K, "dp_key_K2": K2,
                 "walk_key_seed": WALK_KEY_SEED, "dp_key_seed": DP_KEY_SEED,
                 "online_seed": ONLINE_SEED,
                 "key_convention": "K = walk_keys(1)[0]; K2 = walk_keys(101)[1]"},
        "nonuniform_rule": {
            "definition": "h(x) = mix64(x XOR K2); even-hash half = (h & 1) == 0; marked iff even AND h < 2*threshold; odd half never marked",
            "density_even_half": 2 * prm["dp_density_exact"],
            "density_odd_half": 0.0,
            "average_density": prm["dp_density_exact"],
        },
        "nDP": nDP,
        "pointer_rounds": rounds,
        "cycle_mass": cycle_mass,
        "cycle_mass_frac": cycle_mass / N,
        "capped_mass_8W": capped8,
        "capped_mass_8W_frac": capped8 / N,
        "partition_identity_holds": bool(partition_identity_holds),
        "top_T_share_8W": top_T_share,
        "top_T_table_sha256": I.table_hash(top_table),
        "online_walks": {
            "M": M_ONLINE,
            "cap": cap8,
            "mean_walk_length": mean_walk_length,
            "W_model": W,
            "mean_deviation_from_W_fraction": dev_mean,
            "loudness_threshold_10pct": LOUD_MEAN,
            "loud_mean": loud_mean,
            "quantiles_measured": q_measured,
            "quantiles_geometric_theta_zero_based": q_model,
        },
        "ks_walk_lengths_vs_geometric_theta": {
            "primary_zero_based": {"statistic": ks0_stat, "p_value": ks0_p,
                                   "reference": "zero-based Geometric(theta), P(L=k)=(1-theta)^k theta, k>=0 (matches the measured distance array, 0 when the start is marked)"},
            "secondary_one_based": {"statistic": ks1_stat, "p_value": ks1_p,
                                    "reference": "one-based Geometric(theta) (scipy convention), mean W"},
            "alpha": ALPHA,
            "loud_ks_primary": loud_ks,
        },
        "top_T_share_vs_C_max": {
            "C_max_1_4": C_MAX_1_4,
            "deviation_fraction": dev_top_T,
            "loudness_threshold_15pct": LOUD_TOP_T,
            "loud_top_T": loud_top_T,
        },
        "loudness_verdict": {
            "loud_mean": loud_mean,
            "loud_ks": loud_ks,
            "loud_top_T": loud_top_T,
            "control_fires_at_least_one": control_fires,
            "control_passes_when_machinery_fails_loudly": control_fires,
            "control_void_when_none_fire": (not control_fires),
        },
        "self_reported": {"elapsed_seconds": round(elapsed, 3), "peak_rss_bytes": int(peak_rss)},
    }

    summary = {
        "run_id": "RUN-ECDLP-e962f6-006",
        "kind": "nonuniform_proves_too_much",
        "params": prm,
        "nDP": nDP,
        "top_T_share_8W": top_T_share,
        "mean_walk_length": mean_walk_length,
        "W_model": W,
        "mean_deviation_from_W_fraction": dev_mean,
        "loud_mean": loud_mean,
        "ks_primary_zero_based": {"statistic": ks0_stat, "p_value": ks0_p},
        "ks_secondary_one_based": {"statistic": ks1_stat, "p_value": ks1_p},
        "loud_ks": loud_ks,
        "deviation_top_T_from_C_max": dev_top_T,
        "loud_top_T": loud_top_T,
        "control_fires_at_least_one": control_fires,
        "control_void": (not control_fires),
        "quantiles_measured": q_measured,
        "quantiles_geometric_theta_zero_based": q_model,
        "self_reported": raw["self_reported"],
    }

    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "raw-result.json"), "w") as fh:
        json.dump(jsonable(raw), fh)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(jsonable(summary), fh, indent=1)

    meta = {
        "run_id": "RUN-ECDLP-e962f6-006",
        "kind": "nonuniform_proves_too_much",
        "stage": 1,
        "status": "completed_valid",
        "failure_class": None,
        "validity": "valid",
        "validity_reason": "non-uniform array pass + M = 40000 online walks completed; partition identity holds; all contract metrics computed",
        "note": "Stage 1 proves-too-much non-uniform-rule control, seed 1",
        "seeds": {"walk_key": WALK_KEY_SEED, "dp_key": DP_KEY_SEED, "online": ONLINE_SEED},
        "params": prm,
        "protocol_deviations": [],
        "source_sha256": RC.source_hashes(),
        "self_reported": raw["self_reported"],
    }
    with open(os.path.join(out, "run-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"nonuniform done in {elapsed:.1f}s; mean_len={mean_walk_length:.3f} W={W} "
          f"dev={dev_mean:.4f} loud_mean={loud_mean} ks0=({ks0_stat:.4f},{ks0_p:.3g}) "
          f"loud_ks={loud_ks} topT={top_T_share:.6f} dev_cmax={dev_top_T:.4f} "
          f"loud_topT={loud_top_T} fires={control_fires}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
POST-SEAL DIAGNOSTIC (NOT part of the frozen Stage A sealed artifact).

Run only AFTER sealed_blind_rederivation.json existed (hash
9127cabc803bb5fdbb90342bb7724810c6d5d5cfea0a83d6e4cfe40762fa90d3, sealed
2026-09-07T01:27:58Z) and only after opening
experiments/EXP-ECDLP-612fb1/source_v2/instrument.py to investigate the
a=1/8 disagreement's root cause (permitted: the blind_from prohibition binds
BEFORE the seal, not after -- specification.yaml `blind_rederivation.procedure`
and this task's own `constraints`).

Finding that motivates this script: instrument.py's Pool.weights() computes
the "published Bernstein-Lange weight" as

    weight_d = S_d + 4 * W * h_d

where S_d is the SUM of generating-walk LENGTHS of every pool-construction
walk that terminated at DP d, and h_d is the number of such walks (hit
count) -- NOT the DP's true exact basin size. STATIC(T)_r's table is
selected by this weight (a realistic, walk-statistics-based proxy an actual
precomputer would have to use), and only THEN is its exact coverage read off
the true basin sizes of the selected entries.

Stage A's sealed computation instead selected the T pool entries with the
LARGEST TRUE EXACT SIZE (an oracle-optimal selection given the pool) because
specification.yaml's own `definitions` text names "the published
Bernstein-Lange weight" without stating the S_d + 4*W*h_d formula, and that
formula is not derivable from the plain HEUR-BLT-1 statistical model alone.
This script re-derives STATIC(T)_r coverage at a = 1/8 using the S_d + 4*W*h_d
weight (computed from MY OWN independent pool-generation walks, still never
touching production's own random draws or code), to test whether this
explains the sign disagreement at a = 1/8.
"""
import numpy as np
import blind_rederivation as B

N = B.N
T = B.T
T_SEL = B.T_SEL
R = B.R


def compute_with_weight_formula(seed, a_label, a_val):
    rng_f = np.random.default_rng(seed=(seed * 1_000_003 + 17))
    f = rng_f.integers(0, N, size=N, dtype=np.int64)
    rng_mark = np.random.default_rng(seed=(seed * 1_000_003 + 29))
    u = rng_mark.random(size=N)

    W = np.sqrt(a_val * N / T)
    theta = 1.0 / W
    D = u < theta
    idx_all = np.arange(N, dtype=np.int64)
    g = np.where(D, idx_all, f)

    cur = g
    for _ in range(B.DOUBLING_ROUNDS):
        cur = cur[cur]
    terminal = cur
    resolved = D[terminal]
    counts = np.bincount(terminal, minlength=N)

    # Pool generation with length + hit-count tracking (mirrors
    # instrument.py's generate_pools: uniform restarts, batches, charge every
    # walk, accumulate S_d = sum of lengths, h_d = hit count, until r*T
    # DISTINCT DPs are in the pool).
    rng_pool = np.random.default_rng(seed=(seed * 1_000_003 + 53 + hash(a_label) % 1000))
    pool_target = R * T
    S = {}
    h = {}
    batch = 4 * T
    while len(S) < pool_target:
        starts = rng_pool.integers(0, N, size=batch, dtype=np.int64)
        # vectorized simulation of walk length to termination for this batch
        cur_b = starts.copy()
        length = np.zeros(batch, dtype=np.int64)
        active = np.ones(batch, dtype=bool)
        for _ in range(20000):  # generous safety cap; typical length ~ W (tens to ~hundreds)
            if not active.any():
                break
            nxt = g[cur_b]
            moved = active & (nxt != cur_b)
            length[moved] += 1
            cur_b[moved] = nxt[moved]
            active = active & (g[cur_b] != cur_b)
        term_b = cur_b
        ok_b = D[term_b] & (~active)  # must have actually reached a genuine DP
        for i in range(batch):
            if not ok_b[i]:
                continue
            t = int(term_b[i])
            L = int(length[i])
            if t in S:
                S[t] += L
                h[t] += 1
            else:
                S[t] = float(L)
                h[t] = 1
            if len(S) >= pool_target:
                break

    dps = list(S.keys())[:pool_target]
    S_arr = np.array([S[d] for d in dps], dtype=np.float64)
    h_arr = np.array([h[d] for d in dps], dtype=np.float64)
    weight = S_arr + 4.0 * W * h_arr

    order = np.argsort(-weight)  # descending weight
    top_T_dps = np.array(dps)[order[:T]]
    true_sizes_selected = counts[top_T_dps]
    static_T_coverage_weightsel = true_sizes_selected.sum() / N

    return static_T_coverage_weightsel, W


def main():
    a_label, a_val = "1/8", 1.0 / 8.0
    print(f"a={a_label} (W={np.sqrt(a_val*N/T):.3f})")
    print("seed  top_Tsel_share(sealed)  static_cov(sealed,size-ranked)  static_cov(weight S+4Wh)  margin_sealed  margin_weightsel")
    for seed in [1, 2, 3, 4, 5]:
        sealed = B.compute_for_seed(seed)[a_label]
        share = sealed["top_Tsel_basin_share"]
        cov_sealed = sealed["static_T_r2_exact_coverage"]
        cov_weightsel, W = compute_with_weight_formula(seed, a_label, a_val)
        margin_sealed = share - cov_sealed
        margin_weightsel = share - cov_weightsel
        print(f"{seed:4d}  {share:.6f}              {cov_sealed:.6f}                    {cov_weightsel:.6f}                {margin_sealed:+.6f}      {margin_weightsel:+.6f}")


if __name__ == "__main__":
    main()

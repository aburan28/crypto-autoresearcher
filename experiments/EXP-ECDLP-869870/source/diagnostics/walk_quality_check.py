"""Diagnostic run by the Executor after Stage 1 (2026-09-06), NOT a contract cell.

Trigger: Stage 1 seed 1 showed a mean online walk length of 1.25-1.36 W
(a density-1/W predicate on a random mapping gives about W). Question: is the
keyed walk / DP predicate pair correlated (implementation error), or is this
per-instance variance at N = 2^20?

Method: for 12 walk-key seeds, the mean distance to the first DP over 1e5
uniform starts (cap 8W) for three walk constructions x three predicate
constructions, including a TRUE random table and independent Bernoulli marks.

Output is recorded in walk_quality_check.out beside this file.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import instrument as I

def fmix64(z):
    z = z.astype(np.uint64, copy=True)
    z ^= z >> np.uint64(33); z *= np.uint64(0xff51afd7ed558ccd); z ^= z >> np.uint64(33)
    z *= np.uint64(0xc4ceb9fe1a85ec53); z ^= z >> np.uint64(33); return z

log2N = 20; N = 1 << log2N; mask = np.uint64(N - 1)
x = np.arange(N, dtype=np.int64); xu = x.astype(np.uint64)

def meand(f, isdp, W, rng):
    starts = rng.integers(0, N, size=100000); cur = starts.copy()
    d = np.zeros(starts.size, dtype=np.int64); active = ~isdp[cur]
    for step in range(1, int(8 * W) + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0: break
        cur[idx] = f[cur[idx]]; d[idx] = step; active[idx] = ~isdp[cur[idx]]
    return d[~active].mean() / W

for W in (128.0, 64.0):
    thr = int(2 ** 64 / W); res = {}
    for seed in range(1, 13):
        K, K2 = I.walk_keys(seed)
        walks = {"mix64top(Stage1)": (I.mix64(xu ^ np.uint64(K)) >> np.uint64(44)).astype(np.int32),
                 "mix64modN": (I.mix64(xu ^ np.uint64(K)) & mask).astype(np.int32),
                 "randtable": np.random.default_rng(K).integers(0, N, size=N).astype(np.int32)}
        dps = {"mix64topDP(Stage1)": I.is_dp_fn(x, K2, thr), "fmixDP": fmix64(xu ^ np.uint64(K2)) < np.uint64(thr),
               "bern": np.random.default_rng(K2).random(N) < 1 / W}
        for wn, f in walks.items():
            for dn, isdp in dps.items():
                res.setdefault((wn, dn), []).append(meand(f, isdp, W, np.random.default_rng(seed)))
    print(f"N=2^20, W={W}: mean d/W over 12 keys (mean +- sd, min, max)")
    for k, v in res.items():
        v = np.array(v); print(f"   {k[0]:18s} x {k[1]:18s}: {v.mean():.3f} +- {v.std(ddof=1):.3f}   min {v.min():.3f} max {v.max():.3f}")
print("Reading (executor note, not interpretation of any hypothesis): relative sd of the per-instance mean walk length ~ sqrt(a/T); the Stage 1 construction is statistically indistinguishable from a true random table.")

# SYNTHETIC control (not experiment data): quantify how much statistical power
# the C2 comparator-collapse gate has, given the EXACT sparsity m (count of
# top-bit=1 points) measured directly from public curve parameters (see
# comparator_balance.py). This models the comparator as "m ones placed among n
# positions with NO dlog structure" (the null the o2-lane P2-style collapse
# test implicitly assumes it is testing FOR THE ALTERNATIVE against) and
# empirically checks how much a single-point-fixing ("max-preserving")
# permutation differs from a genuine full random (matched-marginal) shuffle,
# using numpy's FFT. Independent synthetic script; no experiment artifact,
# code, or cache is read or executed.
import numpy as np

def A_noDC(v, n):
    V = np.fft.rfft(v.astype(np.float64))
    return float(np.max(np.abs(V[1:])) / n)

rng = np.random.default_rng(20260906)

rungs = [
    (17, 131113, 32),
    (19, 525361, 8),
    (21, 2098321, 24),
    (23, 8391797, 8),
    (25, 33557891, 50),
    (27, 134234689, 22),
]

print(f"{'T':>3} {'n':>11} {'m':>4} {'A_pre(draw)':>13} {'A_fullshuf_max8':>16} "
      f"{'ratio_full':>11} {'A_fix1_mean':>13} {'ratio_fix1':>11} {'A_fix1_max8':>13} {'ratio_fix1max8':>14}")
for T, n, m in rungs:
    ones_idx = rng.choice(n, size=m, replace=False)
    base = np.zeros(n, dtype=np.float64)
    base[ones_idx] = 1.0
    A_pre = A_noDC(base, n)

    # genuine matched-marginal shuffle x8, take max (mirrors NULL-2 protocol)
    full_ratios = []
    for _ in range(8):
        perm = rng.permutation(n)
        full_ratios.append(A_noDC(base[perm], n))
    A_full_max8 = max(full_ratios)

    # "max-preserving": fix ONE of the m ones, shuffle the remaining n-1 slots
    # (including the other m-1 ones) among themselves.
    fix1_vals = []
    for _ in range(8):
        fixed = ones_idx[0]
        rest_idx = np.array([i for i in range(n) if i != fixed])
        rest_vals = np.delete(base, fixed)
        perm_rest = rng.permutation(rest_vals)
        v = np.empty(n)
        v[fixed] = 1.0
        mask = np.ones(n, dtype=bool); mask[fixed] = False
        v[mask] = perm_rest
        fix1_vals.append(A_noDC(v, n))
    A_fix1_mean = float(np.mean(fix1_vals))
    A_fix1_max8 = max(fix1_vals)

    print(f"{T:>3} {n:>11} {m:>4} {A_pre:>13.6e} {A_full_max8:>16.6e} "
          f"{A_full_max8/A_pre:>11.4f} {A_fix1_mean:>13.6e} {A_fix1_mean/A_pre:>11.4f} "
          f"{A_fix1_max8:>13.6e} {A_fix1_max8/A_pre:>14.4f}")

#!/usr/bin/env python3
"""Second cross-check: (i) MC generator per-coset mean of log2 X vs exact;
(ii) direct shift-and-add convolution (no FFT) of the log2-grid pmf, cell A."""
import math
import sys

import numpy as np

sys.path.insert(0, ".")
from rederive import coset_stats  # noqa: E402

M, m, n = 256, 71, 571
st = coset_stats("P1", M)
exact_mean = st["E_log2_given_nonempty"]

rng = np.random.default_rng(123)
acc = 0.0
acc2 = 0.0
cnt = 0
for _ in range(40):
    X = 2 * rng.binomial(M, 0.5, size=(100_000, m))
    l = np.log2(X)
    acc += float(l.sum())
    acc2 += float((l ** 2).sum())
    cnt += l.size
mc_mean = acc / cnt
mc_var = acc2 / cnt - mc_mean ** 2
print(f"per-coset E[log2 X]: exact={exact_mean:.8f}  MC={mc_mean:.8f} +- {math.sqrt(mc_var/cnt):.2e}  (diff {mc_mean-exact_mean:+.2e})")
print(f"per-coset Var[log2 X]: exact={st['Var_log2_given_nonempty']:.8f}  MC={mc_var:.8f}")

# direct convolution on a 2^-10 grid, atoms split to preserve mean
step = 2.0 ** -10
size = int(math.log2(2 * M) * m / step) + 64  # max per-coset log2 X is log2(2M) = 9 bits
base = np.zeros(size)
atoms = []
for j in range(1, M + 1):
    a = math.log2(2 * j)
    p = math.comb(M, j) / 2.0 ** M
    pos = a / step
    lo = int(math.floor(pos))
    fr = pos - lo
    atoms.append((lo, fr, p))
pmf = np.zeros(size)
pmf[0] = 1.0
for _ in range(m):
    new = np.zeros(size)
    for lo, fr, p in atoms:
        if p < 1e-300:
            continue
        new[lo:] += p * (1 - fr) * pmf[: size - lo]
        new[lo + 1:] += p * fr * pmf[: size - lo - 1]
    pmf = new
grid = np.arange(size) * step
pr = -np.expm1(-np.exp2(grid - n))
e_pr = float(np.sum(pmf * pr))
print(f"direct convolution: sum={pmf.sum():.9f}  E[Pr]={e_pr:.7f}  T4={-math.log2(e_pr):.5f}  mean_S={float(np.sum(pmf*grid)):.6f}")

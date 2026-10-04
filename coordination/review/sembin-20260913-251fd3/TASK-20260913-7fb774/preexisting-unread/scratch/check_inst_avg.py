#!/usr/bin/env python3
"""Cross-check of the instance-averaged success probability at cell A (P1 model).

Three routes: FFT convolution at two grid steps, Monte Carlo at 4e6 samples with a
different seed, and a Gaussian (CLT) approximation for log2 lambda.
"""
import math
import sys

import numpy as np

sys.path.insert(0, ".")
from rederive import instance_averaged_pr, coset_stats  # noqa: E402

M, m, n = 256, 71, 571

for step in (2.0 ** -10, 2.0 ** -13):
    e_pr, p_all, mean_S = instance_averaged_pr("P1", M, m, n, step_bits=step)
    print(f"FFT step=2^{math.log2(step):.0f}: E[Pr]={e_pr:.7f}  T4={-math.log2(e_pr):.5f}  mean_S={mean_S:.6f}")

st = coset_stats("P1", M)
mu = m * st["E_log2_given_nonempty"] - n
sd = math.sqrt(m * st["Var_log2_given_nonempty"])
xs = np.linspace(mu - 12 * sd, mu + 12 * sd, 400001)
pdf = np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))
pr = -np.expm1(-np.exp2(xs))
e_gauss = float(np.trapezoid(pdf * pr, xs))
print(f"Gaussian CLT: E[Pr]={e_gauss:.7f}  T4={-math.log2(e_gauss):.5f}")

rng = np.random.default_rng(7)
tot = 0.0
tot2 = 0.0
cnt = 0
for _ in range(80):
    X = 2 * rng.binomial(M, 0.5, size=(50_000, m))
    S = np.log2(X).sum(axis=1)
    pr = -np.expm1(-np.exp2(S - n))
    tot += float(pr.sum())
    tot2 += float((pr ** 2).sum())
    cnt += X.shape[0]
mean = tot / cnt
se = math.sqrt((tot2 / cnt - mean ** 2) / cnt)
print(f"MC seed=7, {cnt} samples: E[Pr]={mean:.7f} +- {se:.7f}  T4={-math.log2(mean):.5f}")

# exact-ish alternative: direct (non-FFT) convolution on integer log-grid with
# float128 is impractical; instead recompute the FFT route with float64 but
# dyadic grid step and no clipping to see whether clipping/renormalisation moves it
xs_, ps_ = [], []
for j in range(1, M + 1):
    xs_.append(math.log2(2 * j))
    ps_.append(math.comb(M, j) / 2.0 ** M)
z = sum(ps_)
ps_ = [p / z for p in ps_]
step = 2.0 ** -10
size = 2 ** 20
base = np.zeros(size)
for a, p in zip(xs_, ps_):
    pos = a / step
    lo = int(math.floor(pos))
    fr = pos - lo
    base[lo] += p * (1 - fr)
    base[lo + 1] += p * fr
F = np.fft.rfft(base)
conv = np.fft.irfft(F ** m, n=size)
grid = np.arange(size) * step
pr = -np.expm1(-np.exp2(grid - n))
print(f"FFT no-clip: sum(conv)={conv.sum():.9f}  min={conv.min():.3e}  E[Pr]={float(np.sum(conv*pr)):.7f}")

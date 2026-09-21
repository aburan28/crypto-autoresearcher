"""One-sample Kolmogorov-Smirnov test against Uniform[0,1), implemented
from scratch (no scipy/numpy available in this environment -- see
implementation.md "Environment"). Formula: Stephens (1970) asymptotic
approximation to the Kolmogorov distribution, the same approximation
scipy.stats.kstest uses internally for the one-sample case.
"""
from __future__ import annotations
import math


def ks_uniform_test(samples):
    xs = sorted(samples)
    n = len(xs)
    if n == 0:
        return 0.0, 1.0
    D = 0.0
    for idx, x in enumerate(xs):
        f_right = (idx + 1) / n
        f_left = idx / n
        if f_right - x > D:
            D = f_right - x
        if x - f_left > D:
            D = x - f_left
    en = math.sqrt(n)
    lam = (en + 0.12 + 0.11 / en) * D
    total = 0.0
    for k in range(1, 101):
        term = 2 * ((-1) ** (k - 1)) * math.exp(-2 * lam * lam * k * k)
        total += term
        if abs(term) < 1e-12:
            break
    p = max(0.0, min(1.0, total))
    return D, p

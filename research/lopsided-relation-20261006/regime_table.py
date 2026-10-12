"""Regime map: our index-calculus arities vs the paper's preconditions.

Pure arithmetic (no measurement). For group order N and arity m, our
default factor-base size is |F| ~ ((m! N)/2)^{1/m} / 2, i.e. epsilon(m) =
log|F|/logN ~= 1/m at large N. The paper needs, for the full saving,
  D <= N^0.1204  (generalized; Theorem 5 proper needs N >= D^18, eps<=1/18)
  |W| <= N^2 / D^kappa (kappa = 1/2 in Theorem 5; sparser W also covered).
Our batched-decomposition query load per lopsided instance is FAR sparser
than the paper's |W| ceiling, so the W condition is slack; thinness
(epsilon) is the binding constraint. Read this table as a deployment map:
which (m, N) cells are oracle-eligible, so a future oracle integration
knows where to plug in.
"""

from __future__ import annotations

import math


def factor_base_size(n_bits, m):
    n = 2.0 ** n_bits
    return ((math.factorial(m) * n) / 2.0) ** (1.0 / m) / 2.0


def regime_rows():
    rows = []
    for n_bits in (32, 64, 128, 256):
        for m in (2, 3, 4, 5, 6, 7, 9, 12, 18):
            fb = factor_base_size(n_bits, m)
            eps = math.log(fb) / math.log(2.0 ** n_bits)
            rows.append({
                "n_bits": n_bits, "m": m,
                "fb": round(fb, 1), "epsilon": round(eps, 4),
                "thin_general": eps <= 0.1204,
                "thin_strict": eps <= 1.0 / 18.0,
            })
    return rows

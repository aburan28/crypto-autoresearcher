"""Exponent fits: least-squares slope of log2(cost) on log2(N), with a
stratified bootstrap confidence interval.

Instances are resampled with replacement *within* each size level, so every
bootstrap replicate keeps the design's spread of sizes and only the
curve-to-curve (and target-to-target) scatter is resampled.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict


def ols_slope(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(set(xs)) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def bootstrap_slope(xs: list[float], ys: list[float], groups: list | None = None,
                    reps: int = 2000, level: float = 0.95,
                    seed: int = 0) -> dict:
    """{"slope", "lo", "hi", "n"}: OLS slope and its percentile interval."""
    slope = ols_slope(xs, ys)
    out = {"slope": slope, "lo": None, "hi": None, "n": len(xs)}
    if slope is None:
        return out
    strata: dict = defaultdict(list)
    for i, g in enumerate(groups if groups is not None else xs):
        strata[g].append(i)
    rng = random.Random(seed)
    boots = []
    for _ in range(reps):
        idx = [rng.choice(members) for members in strata.values() for _ in members]
        s = ols_slope([xs[i] for i in idx], [ys[i] for i in idx])
        if s is not None:
            boots.append(s)
    if boots:
        boots.sort()
        tail = (1 - level) / 2
        out["lo"] = boots[int(math.floor(tail * (len(boots) - 1)))]
        out["hi"] = boots[int(math.ceil((1 - tail) * (len(boots) - 1)))]
    return out


def fit_exponent(rows: list[dict], cost_key: str, x_key: str = "log2N",
                 group_key: str = "bits", **kw) -> dict:
    """Fit log2(row[cost_key]) against row[x_key] over rows with a positive cost."""
    sel = [r for r in rows if r.get(cost_key) and r[cost_key] > 0]
    xs = [r[x_key] for r in sel]
    ys = [math.log2(r[cost_key]) for r in sel]
    return bootstrap_slope(xs, ys, [r[group_key] for r in sel], **kw)

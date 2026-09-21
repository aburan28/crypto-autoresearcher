"""Core lift metrics (IDEA-20260830-c5c614's definitions, reproduced here
since c5c614 itself was never run): for a slice S of the held-out (or other)
target population G, with decomposition counts c_D(r):

  lambda(S) = Pr[c_D(r) >= 1 | r in S] / Pr[c_D(r) >= 1 | r in G]
  rho(S)    = E[c_D(r) | r in S] / E[c_D(r) | r in G]

G is the SAME population the slice is drawn from (e.g. the masked held-out
set for a given cell), matching the random-partition selection null's
density and population (specification.yaml's random_partition_selection_null
control: "at the identical density sigma" on "the masked held-out target
set").
"""
from __future__ import annotations

import numpy as np


def lift_metrics(counts: np.ndarray, slice_mask: np.ndarray) -> dict:
    counts = np.asarray(counts, dtype=np.float64)
    pop_mean = counts.mean()
    pop_hit = (counts >= 1).mean()
    s_counts = counts[slice_mask]
    if s_counts.size == 0:
        return {"lambda": float("nan"), "rho": float("nan"), "n_slice": 0}
    s_mean = s_counts.mean()
    s_hit = (s_counts >= 1).mean()
    lam = (s_hit / pop_hit) if pop_hit > 0 else float("nan")
    rho = (s_mean / pop_mean) if pop_mean > 0 else float("nan")
    return {"lambda": float(lam), "rho": float(rho), "n_slice": int(s_counts.size),
            "pop_mean": float(pop_mean), "pop_hit": float(pop_hit),
            "slice_mean": float(s_mean), "slice_hit": float(s_hit)}


def top_sigma_mask(scores: np.ndarray, sigma: float) -> np.ndarray:
    n = len(scores)
    k = max(1, int(round(sigma * n)))
    order = np.argsort(-scores, kind="stable")
    mask = np.zeros(n, dtype=bool)
    mask[order[:k]] = True
    return mask


def bootstrap_interval(counts: np.ndarray, slice_mask: np.ndarray, n_boot: int, seed: int) -> dict:
    """Resample held-out targets with replacement (over the population G,
    respecting slice membership) and recompute lambda/rho; percentile CI."""
    rng = np.random.default_rng(seed)
    n = len(counts)
    lam_samples = []
    rho_samples = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        m = lift_metrics(counts[idx], slice_mask[idx])
        lam_samples.append(m["lambda"])
        rho_samples.append(m["rho"])
    lam_samples = np.array(lam_samples)
    rho_samples = np.array(rho_samples)
    return {
        "lambda_ci95": [float(np.nanpercentile(lam_samples, 2.5)), float(np.nanpercentile(lam_samples, 97.5))],
        "rho_ci95": [float(np.nanpercentile(rho_samples, 2.5)), float(np.nanpercentile(rho_samples, 97.5))],
    }


def dispersion_index(counts: np.ndarray) -> float:
    mu = counts.mean()
    if mu == 0:
        return float("nan")
    return float(counts.var() / mu)


def holm_correct(pvals, alpha=0.05):
    """Holm step-down correction. Returns array of booleans (reject null)."""
    pvals = np.asarray(pvals, dtype=np.float64)
    m = len(pvals)
    order = np.argsort(pvals)
    reject = np.zeros(m, dtype=bool)
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if pvals[idx] <= thresh:
            reject[idx] = True
        else:
            break
    return reject

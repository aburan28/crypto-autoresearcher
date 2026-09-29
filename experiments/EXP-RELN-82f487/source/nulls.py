"""Nulls: random-partition selection null (1000 draws), analytic exchangeable
null (H2), and orchestration helpers for the label-permutation null (the
actual retraining is driven by the run script since it needs the model
classes; this module supplies the permutation index generator and the band
comparison)."""
from __future__ import annotations

import numpy as np

from scoring import lift_metrics, dispersion_index


def selection_null(counts: np.ndarray, sigma: float, n_draws: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    n = len(counts)
    k = max(1, int(round(sigma * n)))
    lam_draws = np.zeros(n_draws)
    rho_draws = np.zeros(n_draws)
    for i in range(n_draws):
        idx = rng.choice(n, size=k, replace=False)
        mask = np.zeros(n, dtype=bool)
        mask[idx] = True
        m = lift_metrics(counts, mask)
        lam_draws[i] = m["lambda"]
        rho_draws[i] = m["rho"]
    return {
        "lambda_band": [float(np.nanpercentile(lam_draws, 2.5)), float(np.nanpercentile(lam_draws, 97.5))],
        "rho_band": [float(np.nanpercentile(rho_draws, 2.5)), float(np.nanpercentile(rho_draws, 97.5))],
        "lambda_median": float(np.nanmedian(lam_draws)),
        "rho_median": float(np.nanmedian(rho_draws)),
        "n_draws": n_draws,
    }


def analytic_band(counts: np.ndarray, sigma: float, n_test: int) -> dict:
    """H2 pre-computed reference: Var(rho) ~ (1-sigma)*Delta/(mu*sigma*N_test)."""
    mu = counts.mean()
    delta = dispersion_index(counts)
    if mu == 0 or np.isnan(delta) or n_test == 0:
        return {"delta": float(delta), "mu": float(mu), "var_rho": None, "band_halfwidth": None}
    var_rho = (1 - sigma) * delta / (mu * sigma * n_test)
    halfwidth = 2 * np.sqrt(max(var_rho, 0.0))
    return {"delta": float(delta), "mu": float(mu), "var_rho": float(var_rho),
            "band_halfwidth": float(halfwidth), "band": [1 - halfwidth, 1 + halfwidth]}


def band_agreement(empirical_band, analytic_band_dict) -> dict:
    """agreement within 20 percent of the band half-width, per spec's
    analytic_exchangeable_null control."""
    if analytic_band_dict.get("band_halfwidth") is None:
        return {"comparable": False}
    emp_halfwidth = (empirical_band[1] - empirical_band[0]) / 2.0
    ana_halfwidth = analytic_band_dict["band_halfwidth"]
    if ana_halfwidth == 0:
        return {"comparable": False}
    rel_diff = abs(emp_halfwidth - ana_halfwidth) / ana_halfwidth
    return {"comparable": True, "relative_difference": float(rel_diff),
            "within_20_percent": bool(rel_diff <= 0.20)}


def permutation_index(n_train: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.permutation(n_train)


def autocovariance_check(counts_ordered: np.ndarray, max_lag: int, expected_M: int) -> dict:
    """H2 tail check: max abs autocovariance over lags against -M/N^2 with
    finite-population correction, on a RANDOM arm's count vector in its
    representation order."""
    n = len(counts_ordered)
    c = counts_ordered - counts_ordered.mean()
    autocovs = []
    for lag in range(1, min(max_lag, n - 1) + 1):
        cov = float(np.mean(c[:-lag] * c[lag:]))
        autocovs.append(cov)
    expected = -expected_M / (n ** 2)
    max_abs = float(np.max(np.abs(autocovs))) if autocovs else float("nan")
    return {"max_abs_autocovariance": max_abs, "expected_value_H2": expected,
            "n_lags_checked": len(autocovs)}

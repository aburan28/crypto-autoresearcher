"""Statistics for EXP-FIB-001: Spearman rho with permutation null, label-shuffle
control, Poisson goodness-of-fit with class merging, dispersion index, and the
three pre-registered tail checks. All parameters (replicate count, thresholds)
are taken verbatim from specification.yaml; nothing here is tuned to the data.
"""
from __future__ import annotations

import math
from math import comb

import numpy as np
from scipy import stats as scipy_stats

PERMUTATION_REPLICATES = 10000


def spearman_with_permutation_null(x: list[float], y: list[float], seed: int,
                                    replicates: int = PERMUTATION_REPLICATES) -> dict:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return {"rho_s": None, "p_value": None, "n": len(x),
                "degenerate": True, "reason": "no variance in x or y, or n<3"}
    rho_obs, _ = scipy_stats.spearmanr(x, y)
    rng = np.random.default_rng(seed)
    null = np.empty(replicates)
    for i in range(replicates):
        perm = rng.permutation(len(y))
        r, _ = scipy_stats.spearmanr(x, y[perm])
        null[i] = r if not math.isnan(r) else 0.0
    p_value = float(np.mean(np.abs(null) >= abs(rho_obs)))
    half_width = 1.96 / math.sqrt(len(x) - 1)
    return {"rho_s": float(rho_obs), "p_value": p_value, "n": int(len(x)),
            "degenerate": False,
            "null_band_95_half_width": half_width,
            "null_mean": float(np.mean(null)), "null_std": float(np.std(null))}


def label_shuffle_control(x: list[float], y: list[float], seed: int) -> dict:
    """Pair n_R (x) with a fixed-seed random permutation of the costs (y)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(y))
    y_shuffled = y[perm]
    if np.all(x == x[0]) or np.all(y_shuffled == y_shuffled[0]) or len(x) < 3:
        return {"rho_s": None, "degenerate": True, "n": len(x)}
    rho, _ = scipy_stats.spearmanr(x, y_shuffled)
    half_width = 1.96 / math.sqrt(len(x) - 1)
    return {"rho_s": float(rho), "degenerate": False, "n": int(len(x)),
            "null_band_95_half_width": half_width}


def class_merge(counts: dict, B: int, lam: float, N_min_expected: int = 10) -> dict:
    """Merge n_R classes with expected count < N_min_expected under
    Poisson(lam), per the frozen class-merging rule. `counts` maps observed
    n_R value -> observed frequency among the sampled targets.
    """
    total = sum(counts.values())
    merged_bins = []   # list of (label, observed, expected)
    single_vals = sorted(counts.keys())
    # Compute Poisson pmf per value for expected counts, merge low-expected
    # classes into a tail bin.
    keep = []
    tail_vals = []
    for v in single_vals:
        pmf = scipy_stats.poisson.pmf(v, lam) if lam > 0 else 0.0
        expected = pmf * total
        if expected >= N_min_expected:
            keep.append(v)
        else:
            tail_vals.append(v)
    for v in keep:
        pmf = scipy_stats.poisson.pmf(v, lam) if lam > 0 else 0.0
        merged_bins.append({"label": str(v), "observed": counts[v], "expected": pmf * total})
    if tail_vals:
        obs_tail = sum(counts[v] for v in tail_vals)
        exp_tail = total - sum(b["expected"] for b in merged_bins)
        merged_bins.append({"label": "tail(" + ",".join(map(str, tail_vals)) + ")",
                             "observed": obs_tail, "expected": exp_tail})
    return {"bins": merged_bins, "n_bins_kept_ungrouped": len(keep),
            "n_values_merged_to_tail": len(tail_vals)}


def poisson_fit(counts: dict, B: int, N: int) -> dict:
    """Chi-squared goodness-of-fit of the observed n_R histogram vs
    Poisson(lambda), lambda = C(B,3)/N, with the frozen class-merging rule.
    Bonferroni adjustment across the 4 main curves is applied by the caller
    (this returns the raw p-value; caller multiplies by 4 and clips at 1).
    """
    lam = comb(B, 3) / N if N > 0 else 0.0
    total = sum(counts.values())
    merged = class_merge(counts, B, lam)
    bins = merged["bins"]
    if len(bins) < 2 or total == 0:
        return {"lambda": lam, "chi2": None, "p_value_raw": None, "dof": None,
                "dispersion_index": None, "degenerate_histogram": True,
                "class_merge": merged}
    obs = np.array([b["observed"] for b in bins], dtype=float)
    exp = np.array([b["expected"] for b in bins], dtype=float)
    exp = exp * (obs.sum() / exp.sum())  # renormalize expected to match observed total
    chi2 = float(np.sum((obs - exp) ** 2 / exp))
    dof = max(len(bins) - 1, 1)
    p_value = float(1 - scipy_stats.chi2.cdf(chi2, dof))
    values = []
    for v, c in counts.items():
        values.extend([v] * c)
    values = np.array(values, dtype=float)
    mean_v = float(np.mean(values))
    var_v = float(np.var(values, ddof=1)) if len(values) > 1 else 0.0
    dispersion = var_v / mean_v if mean_v > 0 else None
    return {"lambda": lam, "chi2": chi2, "p_value_raw": p_value, "dof": dof,
            "dispersion_index": dispersion, "degenerate_histogram": False,
            "class_merge": merged, "mean_observed": mean_v, "var_observed": var_v}


def tail_checks(n_R_values: list[int], costs: list[float], B: int, N: int,
                 seed: int) -> dict:
    lam = comb(B, 3) / N if N > 0 else 0.0
    n = len(n_R_values)
    rng = np.random.default_rng(seed)
    # (1) extreme-value check
    observed_max = max(n_R_values) if n_R_values else None
    if lam > 0 and n > 0:
        sim_maxes = rng.poisson(lam, size=(1000, n)).max(axis=1)
        pctl99 = float(np.percentile(sim_maxes, 99))
        extreme_flag = observed_max is not None and observed_max > pctl99
    else:
        pctl99 = None
        extreme_flag = None
    # (2) zero-class check
    zero_frac_observed = (sum(1 for v in n_R_values if v == 0) / n) if n else None
    zero_frac_expected = math.exp(-lam) if lam > 0 else None
    # (3) hardest-decile check
    if n >= 10 and costs and all(c is not None for c in costs):
        order = np.argsort(costs)[::-1]
        decile_n = max(1, n // 10)
        hard_idx = order[:decile_n]
        hard_mean_cost = float(np.mean([costs[i] for i in hard_idx]))
        hard_mean_nR = float(np.mean([n_R_values[i] for i in hard_idx]))
        bulk_mean_nR = float(np.mean(n_R_values))
    else:
        hard_mean_cost = hard_mean_nR = bulk_mean_nR = None
    return {
        "extreme_value_check": {"observed_max": observed_max,
                                 "predicted_max_99th_pctile": pctl99,
                                 "flag_exceeds_99th": extreme_flag},
        "zero_class_check": {"observed_fraction": zero_frac_observed,
                              "expected_e_neg_lambda": zero_frac_expected,
                              "any_zero_root_targets": zero_frac_observed is not None and zero_frac_observed > 0},
        "hardest_decile_check": {"hard_decile_mean_cost": hard_mean_cost,
                                  "hard_decile_mean_nR": hard_mean_nR,
                                  "bulk_mean_nR": bulk_mean_nR},
    }

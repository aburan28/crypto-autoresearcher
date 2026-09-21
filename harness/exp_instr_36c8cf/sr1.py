"""SR1 -- C-NULLC-REPRODUCTION.

Reproduce NULL-C's published power profile from the committed p = 4001 rate_m3
values, using the COMMITTED statistic harness.exp_icinv.permutation_null
unmodified.

FROZEN BEFORE ANY GRADED RESULT WAS READ (see implementation.md for the
exploration that preceded the freeze and is disclosed in full):

  * data          : per-class rate_m3 from the two committed p = 4001 runs
  * statistic     : harness.exp_icinv.permutation_null, unedited, default
                    iterations
  * deltas        : read at run time from red_team_notes.md section 5
  * seeds         : the twelve seeds declared in the contract's
                    replication.seeds -- 12 repetitions per cell
  * constructions : the seven declared additive between-class mean-shift
                    constructions below, ALL of which are run and ALL of which
                    are reported. None is selected after the fact.
  * tolerance     : EXECUTOR-DECLARED, because the contract declares none.
                    Flagged as a specification gap in the run record.

The contract does not name a planting construction for the SR1 rows and the
record it cites does not record the one the red team used, so the seven
constructions below enumerate the natural additive between-class shifts on four
classes. Enumerating them is the only way to attempt the reproduction at all;
reporting all seven is what keeps it from being a search for a passing one.
"""
from __future__ import annotations

import statistics

from harness.exp_icinv import permutation_null

# Executor-declared match tolerance (NOT declared by the frozen contract).
MEDIAN_P_TOL = 0.010
POWER_TOL = 1.0 / 12.0
ALPHA = 0.05


def _sorted_keys(groups):
    """Classes ordered by ascending class mean (== ascending trace key here;
    both orders are reported so the coincidence is visible, not assumed)."""
    return sorted(groups, key=lambda k: statistics.mean(groups[k]))


def constructions(groups):
    ks = _sorted_keys(groups)
    n = len(ks)

    def shift(offsets, delta):
        return {k: [x + offsets(i, n) * delta for x in groups[k]]
                for i, k in enumerate(ks)}

    return {
        # monotone ladders, aligned with the existing class-mean gradient
        "ladder_unit":        lambda d: shift(lambda i, n: i, d),
        "ladder_total":       lambda d: shift(lambda i, n: i / (n - 1), d),
        "ladder_centered":    lambda d: shift(lambda i, n: i - (n - 1) / 2, d),
        # single-class shifts
        "top_class_up":       lambda d: shift(lambda i, n: 1.0 if i == n - 1 else 0.0, d),
        "bottom_class_up":    lambda d: shift(lambda i, n: 1.0 if i == 0 else 0.0, d),
        # two-level splits
        "halves_aligned":     lambda d: shift(lambda i, n: -0.5 if i < n / 2 else 0.5, d),
        "halves_antialigned": lambda d: shift(lambda i, n: 0.5 if i < n / 2 else -0.5, d),
    }


def cell(groups, seeds):
    """12 repetitions of NULL-C on one planted dataset."""
    ps = [permutation_null(groups, seed=s)[2] for s in seeds]
    obs, nullmean, _ = permutation_null(groups, seed=seeds[0])
    return {
        "p_values": ps,
        "median_p": statistics.median(ps),
        "min_p": min(ps),
        "max_p": max(ps),
        "power_at_0_05": sum(1 for p in ps if p <= ALPHA) / len(ps),
        "observed_mean_within_variance": obs,
        "null_mean_at_first_seed": nullmean,
    }


def run(groups, deltas, seeds, published_rows):
    """Run every declared construction at every declared delta. Returns the
    full per-cell record plus the per-construction comparison against the
    published profile."""
    pooled = [x for v in groups.values() for x in v]
    pooled_mean = statistics.mean(pooled)

    # delta = 0 is construction-free: one cell, reused by every construction.
    zero_cell = cell(groups, seeds)

    pub = {r["delta"]: r for r in published_rows}
    out = {
        "statistic": "harness.exp_icinv.permutation_null (NULL-C)",
        "statistic_iterations": "harness default (2000)",
        "alpha": ALPHA,
        "seeds": list(seeds),
        "repetitions_per_cell": len(seeds),
        "pooled_mean_of_rate_m3": pooled_mean,
        "class_sizes": {str(k): len(v) for k, v in groups.items()},
        "class_means": {str(k): statistics.mean(v) for k, v in groups.items()},
        "delta_zero_cell": zero_cell,
        "pct_of_mean_check": [
            {"delta": d, "pct_of_mean_measured": 100.0 * d / pooled_mean,
             "pct_of_mean_published": pub[d]["pct_of_mean_published"]}
            for d in deltas],
        "constructions": {},
        "tolerance": {"median_p_abs": MEDIAN_P_TOL, "power_abs": POWER_TOL,
                      "declared_by": "executor",
                      "note": ("the frozen contract declares no numeric "
                               "tolerance for the SR1 reproduction; this one is "
                               "executor-declared and is reported as a "
                               "specification gap, with all raw numbers given "
                               "so any other rule can be applied by a reviewer")},
    }

    for name, make in constructions(groups).items():
        rows = []
        for d in deltas:
            c = zero_cell if d == 0.0 else cell(make(d), seeds)
            p = pub[d]
            rows.append({
                "delta": d,
                "measured": c,
                "published_median_p": p["median_p_published"],
                "published_power": p["power_at_0_05_published"],
                "median_p_abs_diff": abs(c["median_p"] - p["median_p_published"]),
                "power_abs_diff": abs(c["power_at_0_05"] - p["power_at_0_05_published"]),
                "row_matches": (abs(c["median_p"] - p["median_p_published"]) <= MEDIAN_P_TOL
                                and abs(c["power_at_0_05"] - p["power_at_0_05_published"])
                                <= POWER_TOL + 1e-12),
            })
        out["constructions"][name] = {
            "rows": rows,
            "all_rows_match": all(r["row_matches"] for r in rows),
            "rows_matching": sum(1 for r in rows if r["row_matches"]),
            "rows_total": len(rows),
        }

    matching = [n for n, v in out["constructions"].items() if v["all_rows_match"]]
    out["constructions_reproducing_published_profile"] = matching
    out["delta_zero_row_reproduced"] = bool(
        abs(zero_cell["median_p"] - pub[0.0]["median_p_published"]) <= MEDIAN_P_TOL)
    out["sr1_reproduced"] = bool(matching)
    return out

"""SR1 AS NARROWED BY AMENDMENT v1 CHANGE G1 -- C-NULLC-REPRODUCTION.

G1 discharges SR1 ON THE CONSTRUCTION-FREE QUANTITIES ONLY:

  Q1  the delta = 0 row's MEDIAN p, against the published value, with the
      amendment's adopted match rule |measured - published| <= tolerance;
  Q2  the published "as % of mean" column, which must round to the published
      value at the published precision.

THE delta > 0 ROWS ARE OUT OF THE GATE and are recorded by the amendment as
PERMANENTLY UNREPRODUCIBLE, because the construction that generated them was
never recorded. THIS MODULE THEREFORE RUNS NO PLANTING CONSTRUCTION AT ALL.
Change G1 forbids selecting one: all seven candidate profiles are already
visible in RUN-INSTR-36c8cf-phaseA-2a5cd1, so choosing among them now would be
post-hoc selection. Nothing here shifts, plants or perturbs any value.

NULL-C IS USED HERE AND ONLY HERE IN THIS RUN, on the BETWEEN-CLASS contrast
over the four committed p = 4001 classes -- the one use the contract still
admits. It is not used for any within-class contrast in either direction
(inherited disqualification, not re-litigated).

Every published reference value is passed in from `refvalues`, read from its
committed record at run time and bound by sha256. Nothing is transcribed.
"""
from __future__ import annotations

import statistics

from harness.exp_icinv import permutation_null

ALPHA = 0.05


def run(groups: dict[int, list[float]], seeds: list[int], published_rows: list[dict],
        median_p_tolerance: float, pct_decimals: int) -> dict:
    """The two construction-free quantities, and nothing else."""
    pooled = [x for v in groups.values() for x in v]
    pooled_mean = statistics.mean(pooled)

    # ---- Q1: the delta = 0 (construction-free) cell, 12 repetitions ----
    ps = [permutation_null(groups, seed=s)[2] for s in seeds]
    obs, null_mean, _ = permutation_null(groups, seed=seeds[0])
    zero_cell = {
        "p_values": ps,
        "median_p": statistics.median(ps),
        "min_p": min(ps),
        "max_p": max(ps),
        "power_at_0_05": sum(1 for p in ps if p <= ALPHA) / len(ps),
        "observed_mean_within_variance": obs,
        "null_mean_at_first_seed": null_mean,
        "repetitions": len(ps),
    }
    pub_zero = next(r for r in published_rows if r["delta"] == 0.0)
    q1_diff = abs(zero_cell["median_p"] - pub_zero["median_p_published"])
    q1 = {
        "quantity": "median p at delta = 0, the construction-free row",
        "measured_median_p": zero_cell["median_p"],
        "published_median_p": pub_zero["median_p_published"],
        "absolute_difference": q1_diff,
        "match_rule": f"absolute difference at most {median_p_tolerance}",
        "tolerance": median_p_tolerance,
        "passes": bool(q1_diff <= median_p_tolerance),
    }

    # ---- Q2: the published "as % of mean" column ----
    q2_rows = []
    for r in published_rows:
        if r["delta"] == 0.0:
            continue
        measured = 100.0 * r["delta"] / pooled_mean
        q2_rows.append({
            "delta": r["delta"],
            "pct_of_mean_measured": measured,
            "pct_of_mean_measured_rounded": float(f"{measured:.{pct_decimals}f}"),
            "pct_of_mean_published": r["pct_of_mean_published"],
            "matches": (f"{measured:.{pct_decimals}f}"
                        == f"{r['pct_of_mean_published']:.{pct_decimals}f}"),
        })
    q2 = {
        "quantity": "the published 'as % of mean' column",
        "pooled_mean_of_rate_m3": pooled_mean,
        "match_rule": (f"the measured percentage rounds to the published value "
                       f"at the published precision of {pct_decimals} decimal place"),
        "rows": q2_rows,
        "rows_matching": sum(1 for r in q2_rows if r["matches"]),
        "rows_total": len(q2_rows),
        "passes": bool(q2_rows) and all(r["matches"] for r in q2_rows),
    }

    # ---- recorded, and explicitly NOT a discharging quantity ----
    power_note = {
        "quantity": "power at delta = 0",
        "measured": zero_cell["power_at_0_05"],
        "published": pub_zero["power_at_0_05_published"],
        "status": "NOT A DISCHARGING QUANTITY AND NOT A FAILURE",
        "why": ("amendment v1 change G1: the published 0.08 is one repetition "
                "in twelve (1/12 = 0.0833, published to two decimals) and the "
                "published seed set is recorded nowhere, so a one-repetition "
                "difference is not attributable to anything and is not read in "
                "either direction."),
    }

    return {
        "gate": "SR1 as narrowed by amendment v1 change G1",
        "statistic": "harness.exp_icinv.permutation_null (NULL-C), unmodified",
        "statistic_iterations": "harness default (2000)",
        "statistic_use_scope": ("BETWEEN-CLASS ONLY, on the four committed "
                                "p = 4001 classes. NULL-C is used nowhere else "
                                "in this run and for no within-class contrast."),
        "alpha": ALPHA,
        "seeds": list(seeds),
        "repetitions_per_cell": len(seeds),
        "class_sizes": {str(k): len(v) for k, v in groups.items()},
        "class_means": {str(k): statistics.mean(v) for k, v in groups.items()},
        "pooled_mean_of_rate_m3": pooled_mean,
        "delta_zero_cell": zero_cell,
        "Q1_delta_zero_median_p": q1,
        "Q2_pct_of_mean_column": q2,
        "power_at_delta_zero_recorded_not_gated": power_note,
        "constructions_run": [],
        "constructions_run_note": (
            "NONE. Change G1 removes the delta > 0 rows from the gate and "
            "forbids selecting a canonical construction, because all seven "
            "candidate profiles are already visible in the version-1 run. No "
            "planting construction was executed by this run."),
        "delta_gt_zero_rows": {
            "status": "permanently_unreproducible",
            "why": ("the construction that produced them was never recorded "
                    "(amendment v1 change G1); red_team_notes.md section 5 and "
                    "red_team_report.yaml objection O3 state the profile and "
                    "not the construction."),
        },
        "sr1_discharged_on_construction_free_quantities":
            bool(q1["passes"] and q2["passes"]),
    }

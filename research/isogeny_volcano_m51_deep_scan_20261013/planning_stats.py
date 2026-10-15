#!/usr/bin/env python3
"""Reproduce the frozen discovery-scan planning quantities.

The expected hit and distinct-parent counts are exact expectations for simple
sampling without replacement (up to floating-point evaluation of a short log
product).  The quota probability deliberately uses a named binomial-occupancy
approximation: parent-hit indicators are assigned their exact marginal hit
probability but modeled as independent.  It is not described as an exact
finite-population tail probability.
"""

from __future__ import annotations

import json
import math


UNIVERSE = (1 << 51) - 1
SAMPLE = 3_600_000_000
PARENTS = 2_369
CHILD_ORBITS_PER_PARENT = 272
MODELS_PER_ORBIT = 51
MODELS_PER_PARENT = CHILD_ORBITS_PER_PARENT * MODELS_PER_ORBIT
ELIGIBLE_MODELS = PARENTS * MODELS_PER_PARENT
QUOTA = 32


def main() -> int:
    expected_hits = SAMPLE * ELIGIBLE_MODELS / UNIVERSE
    log_parent_miss = math.fsum(
        math.log1p(-SAMPLE / (UNIVERSE - offset))
        for offset in range(MODELS_PER_PARENT)
    )
    parent_hit_probability = -math.expm1(log_parent_miss)
    expected_distinct_parents = PARENTS * parent_hit_probability

    p = parent_hit_probability
    term = math.exp(PARENTS * math.log1p(-p))
    cdf_below_quota = term
    for observed in range(QUOTA - 1):
        term *= (PARENTS - observed) / (observed + 1) * p / (1 - p)
        cdf_below_quota += term
    probability_at_least_quota = 1 - cdf_below_quota

    expected = {
        "eligible_models": 32_862_768,
        "expected_eligible_hits": 52.53840242858134,
        "exact_expected_distinct_parents": 51.96014232199414,
        "binomial_occupancy_approx_probability_at_least_32": 0.998926642220153,
    }
    observed = {
        "eligible_models": ELIGIBLE_MODELS,
        "expected_eligible_hits": expected_hits,
        "exact_expected_distinct_parents": expected_distinct_parents,
        "binomial_occupancy_approx_probability_at_least_32": probability_at_least_quota,
    }
    for key, frozen in expected.items():
        actual = observed[key]
        if isinstance(frozen, int):
            if actual != frozen:
                raise RuntimeError(f"{key}: {actual} != {frozen}")
        elif not math.isclose(actual, frozen, rel_tol=2e-15, abs_tol=2e-15):
            raise RuntimeError(f"{key}: {actual} != {frozen}")

    report = {
        "schema": "m51-deep-planning-stats/v1",
        "universe_nonzero_coefficients": UNIVERSE,
        "sample_without_replacement": SAMPLE,
        "eligible_parents": PARENTS,
        "child_orbits_per_parent": CHILD_ORBITS_PER_PARENT,
        "models_per_orbit": MODELS_PER_ORBIT,
        "models_per_parent": MODELS_PER_PARENT,
        **observed,
        "parent_hit_probability_exact_marginal": parent_hit_probability,
        "quota": QUOTA,
        "quota_tail_method": "Binomial(2369,p_exact_marginal) occupancy approximation; parent indicators treated as independent",
        "quota_tail_is_exact_finite_population_probability": False,
        "model_condition": "conditional on ideal-PRP exchangeability",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

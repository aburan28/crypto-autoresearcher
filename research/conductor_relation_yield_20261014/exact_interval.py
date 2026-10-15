"""Exact integer inversion of hypergeometric tails for distinct targets.

No floating-point tail decision is used. The threshold 0.00125 is 1/800.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from math import comb


@lru_cache(maxsize=8)
def denominator(population, draws):
    return comb(population, draws)


def upper_tail_compare(population, successes, draws, observed, numerator, divisor):
    """Compare Pr[X>=observed] to numerator/divisor, returning -1, 0, or 1.

    This sums exact integer hypergeometric numerators. Once terms are falling,
    a geometric majorant gives an exact early certificate for a small tail.
    """
    assert 0 <= successes <= population and 0 <= draws <= population
    assert 0 <= numerator <= divisor and divisor > 0
    lowest = max(0, draws - (population - successes))
    highest = min(draws, successes)
    if observed <= lowest:
        return (divisor > numerator) - (divisor < numerator)
    if observed > highest:
        return (0 > numerator) - (0 < numerator)
    total = denominator(population, draws)
    index = observed
    term = comb(successes, index) * comb(population - successes, draws - index)
    partial = 0
    while True:
        partial += term
        compare = divisor * partial - numerator * total
        if compare > 0:
            return 1
        if index == highest:
            return (compare > 0) - (compare < 0)
        next_numerator = (successes - index) * (draws - index)
        next_divisor = (index + 1) * (population - successes - draws + index + 1)
        next_term = term * next_numerator // next_divisor
        assert next_term * next_divisor == term * next_numerator
        next_index = index + 1
        if next_index == highest:
            bound_difference = divisor * (partial + next_term) - numerator * total
            if bound_difference < 0:
                return -1
        else:
            ratio_numerator = (successes - next_index) * (draws - next_index)
            ratio_divisor = (next_index + 1) * (population - successes - draws + next_index + 1)
            if ratio_numerator < ratio_divisor:
                gap = ratio_divisor - ratio_numerator
                upper_difference = (
                    divisor * (partial * gap + next_term * ratio_divisor)
                    - numerator * total * gap
                )
                if upper_difference < 0:
                    return -1
        term = next_term
        index = next_index


def upper_tail_at_least(population, successes, draws, observed, numerator=1, divisor=800):
    """Exact predicate, choosing the shorter side of the distribution."""
    if observed * population > draws * successes:
        return upper_tail_compare(population, successes, draws, observed, numerator, divisor) >= 0
    # Pr[X>=x] >= q iff Pr[X<=x-1] <= 1-q. Let Y=draws-X.
    complement = upper_tail_compare(
        population, population - successes, draws, draws - observed + 1,
        divisor - numerator, divisor,
    )
    return complement <= 0


def interval(population, draws, observed, numerator=1, divisor=800):
    """Invert both exact tails with inclusive discrete endpoints."""
    if not (0 <= observed <= draws <= population):
        raise ValueError("invalid hypergeometric sample")
    if not (0 < numerator * 2 < divisor):
        raise ValueError("tail threshold must be below one half")
    if observed == 0:
        lower = 0
    else:
        lo, hi = 0, population
        while lo < hi:
            mid = (lo + hi) // 2
            if upper_tail_at_least(population, mid, draws, observed, numerator, divisor):
                hi = mid
            else:
                lo = mid + 1
        lower = lo
    if observed == draws:
        upper = population
    else:
        # Pr_K[X<=observed] = Pr_{N-K}[Y>=draws-observed].
        lo, hi = 0, population
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if upper_tail_at_least(population, population - mid, draws, draws - observed, numerator, divisor):
                lo = mid
            else:
                hi = mid - 1
        upper = lo
    return {
        "schema": "exact-hypergeometric-interval/v1",
        "population": population, "draws": draws, "observed": observed,
        "tail_numerator": numerator, "tail_denominator": divisor,
        "lower_successes": lower, "upper_successes": upper,
        "lower_fraction": lower / population, "upper_fraction": upper / population,
        "coverage_each_endpoint_at_least": 1 - 2 * numerator / divisor,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=int, required=True)
    parser.add_argument("--draws", type=int, required=True)
    parser.add_argument("--observed", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(interval(args.population, args.draws, args.observed), sort_keys=True))


if __name__ == "__main__":
    main()

"""Check exact tail decisions against direct integer enumeration."""
from __future__ import annotations

from math import comb

from exact_interval import interval, upper_tail_at_least, upper_tail_compare


def direct_compare(population, successes, draws, observed, numerator, divisor):
    total = comb(population, draws)
    favorable = sum(
        comb(successes, value) * comb(population - successes, draws - value)
        for value in range(max(observed, 0), min(draws, successes) + 1)
        if 0 <= draws - value <= population - successes
    )
    difference = divisor * favorable - numerator * total
    return (difference > 0) - (difference < 0)


def main():
    comparisons = 0
    for population in range(5, 23):
        for draws in range(population + 1):
            for successes in range(population + 1):
                for observed in range(draws + 2):
                    for numerator, divisor in ((1, 800), (1, 4), (1, 2)):
                        expected = direct_compare(population, successes, draws, observed, numerator, divisor)
                        actual = upper_tail_compare(population, successes, draws, observed, numerator, divisor)
                        assert actual == expected, (population, successes, draws, observed, numerator, divisor)
                        assert upper_tail_at_least(population, successes, draws, observed, numerator, divisor) == (expected >= 0)
                        comparisons += 1
    for population, draws in ((19, 8), (31, 13)):
        for observed in range(draws + 1):
            result = interval(population, draws, observed)
            expected_lower = next(
                success for success in range(population + 1)
                if direct_compare(population, success, draws, observed, 1, 800) >= 0
            )
            expected_upper = max(
                success for success in range(population + 1)
                if direct_compare(population, population - success, draws, draws - observed, 1, 800) >= 0
            )
            assert result["lower_successes"] == expected_lower
            assert result["upper_successes"] == expected_upper
    print(f"exact hypergeometric control: {comparisons} integer tail comparisons and interval inversions PASS")


if __name__ == "__main__":
    main()

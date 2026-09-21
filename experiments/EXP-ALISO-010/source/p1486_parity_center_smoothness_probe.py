#!/usr/bin/env python3
"""Exact toy sampling of squarefree centers in conditioned smooth integers."""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import platform
import random
import resource
import statistics
import time
from pathlib import Path

from sympy import factorint


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "p1486_parity_center_smoothness_probe_result.json"
SEED = 148600728
SAMPLE_COUNT = 2048
UNCONDITIONED_COUNT = 64
FAMILIES = (
    {"bits": 40, "B": 13},
    {"bits": 56, "B": 19},
    {"bits": 72, "B": 29},
    {"bits": 88, "B": 37},
)
EPSILONS = (0.05, 0.10, 0.20, 0.30)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def payload_hash(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def primes_through(bound):
    sieve = bytearray(b"\x01") * (bound + 1)
    sieve[:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(bound) + 1):
        if sieve[prime]:
            sieve[prime * prime : bound + 1 : prime] = b"\x00" * (
                (bound - prime * prime) // prime + 1
            )
    return [value for value in range(2, bound + 1) if sieve[value]]


class ExactSmoothSampler:
    """Uniform sampler for B-smooth integers in an exact integer interval."""

    def __init__(self, primes, upper):
        self.primes = tuple(primes)
        self.upper = upper
        left_primes, right_primes = self._balanced_partition()
        self.left_primes = tuple(left_primes)
        self.right_primes = tuple(right_primes)
        self.left_products = self._products(self.left_primes)
        self.right_products = self._products(self.right_primes)

    def _balanced_partition(self):
        weighted = []
        for prime in self.primes:
            exponent_choices = int(math.log(self.upper, prime)) + 1
            weighted.append((math.log(exponent_choices), prime))
        left = []
        right = []
        left_weight = 0.0
        right_weight = 0.0
        for weight, prime in sorted(weighted, reverse=True):
            if left_weight <= right_weight:
                left.append(prime)
                left_weight += weight
            else:
                right.append(prime)
                right_weight += weight
        return sorted(left), sorted(right)

    def _products(self, primes):
        products = [1]
        for prime in primes:
            expanded = []
            for product in products:
                value = product
                while value <= self.upper:
                    expanded.append(value)
                    if value > self.upper // prime:
                        break
                    value *= prime
            products = expanded
        products.sort()
        return products

    def interval_rows(self, lower, upper):
        rows = []
        cumulative = []
        total = 0
        for left in self.left_products:
            if left > upper:
                break
            residual_lower = (lower + left - 1) // left
            residual_upper = upper // left
            start = bisect.bisect_left(self.right_products, residual_lower)
            stop = bisect.bisect_right(self.right_products, residual_upper)
            if stop > start:
                total += stop - start
                rows.append((left, start, stop))
                cumulative.append(total)
        return rows, cumulative, total

    def sample_from_rows(self, rows, cumulative, total, rng):
        ticket = rng.randrange(total)
        row_index = bisect.bisect_right(cumulative, ticket)
        previous = cumulative[row_index - 1] if row_index else 0
        left, start, _ = rows[row_index]
        right = self.right_products[start + ticket - previous]
        return left * right


def squarefree_kernel_from_known_primes(value, primes):
    residual = value
    kernel = 1
    odd_valuations = 0
    valuations = []
    for prime in primes:
        exponent = 0
        while residual % prime == 0:
            residual //= prime
            exponent += 1
        if exponent:
            valuations.append((prime, exponent))
        if exponent % 2:
            kernel *= prime
            odd_valuations += 1
    if residual != 1:
        raise RuntimeError("sample is not smooth over the registered prime set")
    return kernel, odd_valuations, valuations


def squarefree_kernel_general(value):
    factors = factorint(value)
    kernel = math.prod(
        int(prime) for prime, exponent in factors.items() if int(exponent) % 2
    )
    return kernel, len(
        [prime for prime, exponent in factors.items() if int(exponent) % 2]
    )


def quantile(values, probability):
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1)
    return ordered[max(0, index)]


def analyze_family(specification, family_index):
    bits = specification["bits"]
    bound = specification["B"]
    upper = (1 << bits) - 1
    lower = 1 << (bits - 1)
    primes = primes_through(bound)
    sampler = ExactSmoothSampler(primes, upper)
    interval_rows, cumulative, population = sampler.interval_rows(lower, upper)
    rng = random.Random(SEED + family_index)

    samples = [
        sampler.sample_from_rows(interval_rows, cumulative, population, rng)
        for _ in range(SAMPLE_COUNT)
    ]
    rows = [
        squarefree_kernel_from_known_primes(value, primes) for value in samples
    ]
    kernels = [row[0] for row in rows]
    odd_counts = [row[1] for row in rows]
    ratios = [math.log2(kernel) / bits for kernel in kernels]

    random_rng = random.Random(SEED + 1000 + family_index)
    unconditioned = [
        random_rng.randrange(lower, upper + 1)
        for _ in range(UNCONDITIONED_COUNT)
    ]
    unconditioned_rows = [
        squarefree_kernel_general(value) for value in unconditioned
    ]
    unconditioned_ratios = [
        math.log2(row[0]) / bits for row in unconditioned_rows
    ]

    largest_squarefree_smooth = math.prod(primes)
    square_root = math.isqrt(upper)
    square_control = square_root * square_root
    smooth_square_value = math.prod(prime**2 for prime in primes)
    smooth_square_kernel, _, _ = squarefree_kernel_from_known_primes(
        smooth_square_value, primes
    )

    log_x = math.log(upper)
    saddle_scale = math.sqrt(log_x * math.log(log_x))
    return {
        "bits": bits,
        "B": bound,
        "primes": primes,
        "prime_count": len(primes),
        "smooth_population_in_top_interval": population,
        "sample_count": SAMPLE_COUNT,
        "all_samples_in_interval": all(lower <= value <= upper for value in samples),
        "all_samples_B_smooth": all(
            math.prod(prime**exponent for prime, exponent in row[2]) == value
            for value, row in zip(samples, rows)
        ),
        "log_B_over_sqrt_logX_loglogX": math.log(bound) / saddle_scale,
        "center_exponent_log2_sf_over_bits": {
            "mean": statistics.fmean(ratios),
            "median": statistics.median(ratios),
            "p90": quantile(ratios, 0.90),
            "p95": quantile(ratios, 0.95),
            "p99": quantile(ratios, 0.99),
            "maximum": max(ratios),
        },
        "odd_valuation_prime_count": {
            "mean": statistics.fmean(odd_counts),
            "median": statistics.median(odd_counts),
            "maximum": max(odd_counts),
        },
        "probability_center_below_X_epsilon": {
            str(epsilon): sum(
                kernel <= upper**epsilon for kernel in kernels
            )
            / SAMPLE_COUNT
            for epsilon in EPSILONS
        },
        "unconditioned_control": {
            "sample_count": UNCONDITIONED_COUNT,
            "center_exponent_mean": statistics.fmean(unconditioned_ratios),
            "center_exponent_median": statistics.median(unconditioned_ratios),
            "center_exponent_p90": quantile(unconditioned_ratios, 0.90),
        },
        "perfect_square_control": {
            "value": square_control,
            "expected_squarefree_kernel": 1,
            "passes": squarefree_kernel_general(square_control)[0] == 1,
        },
        "smooth_square_control": {
            "value": smooth_square_value,
            "squarefree_kernel": smooth_square_kernel,
            "passes": smooth_square_kernel == 1,
        },
        "adversarial_squarefree_smooth_control": {
            "value": largest_squarefree_smooth,
            "squarefree_kernel": largest_squarefree_smooth,
            "passes": squarefree_kernel_from_known_primes(
                largest_squarefree_smooth, primes
            )[0]
            == largest_squarefree_smooth,
        },
        "sampler_lists": {
            "left_primes": list(sampler.left_primes),
            "right_primes": list(sampler.right_primes),
            "left_product_count": len(sampler.left_products),
            "right_product_count": len(sampler.right_products),
            "weighted_left_rows": len(interval_rows),
        },
    }


def main():
    started = time.perf_counter()
    families = [
        analyze_family(specification, index)
        for index, specification in enumerate(FAMILIES)
    ]
    medians = [
        family["center_exponent_log2_sf_over_bits"]["median"]
        for family in families
    ]
    rss_raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    result = {
        "schema": "p1486-parity-center-smoothness-probe-v1",
        "claim_status": (
            "HEURISTIC DISTRIBUTION EVIDENCE / TOY / MODEL-BOUND / "
            "NO GENERAL COMPLEXITY CLAIM"
        ),
        "seed": SEED,
        "families": families,
        "family_count": len(families),
        "registered_trend_gate": {
            "median_center_exponent_strictly_decreases": all(
                left > right for left, right in zip(medians, medians[1:])
            ),
            "last_median_below_first_median": medians[-1] < medians[0],
        },
        "all_controls_pass": all(
            family["perfect_square_control"]["passes"]
            and family["smooth_square_control"]["passes"]
            and family["adversarial_squarefree_smooth_control"]["passes"]
            and family["all_samples_in_interval"]
            and family["all_samples_B_smooth"]
            for family in families
        ),
        "elapsed_sec": round(time.perf_counter() - started, 9),
        "peak_rss": {
            "value": rss_raw,
            "unit": "bytes" if platform.system() == "Darwin" else "KiB",
        },
        "ordinary_smoothness_implies_small_center": False,
        "general_low_memory_claim": False,
    }
    result["success"] = bool(
        result["all_controls_pass"]
        and result["registered_trend_gate"]["last_median_below_first_median"]
    )
    result["script_sha256"] = file_sha256(Path(__file__))
    result["payload_sha256"] = payload_hash(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

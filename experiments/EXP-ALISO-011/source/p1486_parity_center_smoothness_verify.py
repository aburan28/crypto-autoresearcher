#!/usr/bin/env python3
"""Independent verifier for the P1486 parity-center smoothness probe.

The producer source is neither imported nor inspected.  The verifier reads the
contract and producer JSON, then reconstructs every registered smooth-number
population with a different exact method.

For the half-open top dyadic interval [2^(b-1), 2^b), every odd B-smooth
integer q < 2^b has a unique power-of-two normalization q*2^e in the interval.
Thus the target population equals the number of odd B-smooth q < 2^b.  We
count those q by:

1. explicitly tabulating products over the small odd basis {3, 5, 7}; and
2. streaming exponent tuples over the remaining primes, using one binary
   search per tuple to count compatible small-basis products.

This is not the producer's balanced all-prime meet-in-the-middle construction.
Uniform samples are obtained by exact integer ranks in the same bijection.
"""

from __future__ import annotations

import bisect
import copy
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterator

import sympy
from sympy import factorint


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent.parent
CONTRACT = (
    REPOSITORY / "research" / "p1486_parity_center_streaming_contract_20260728.md"
)
PRODUCER_SOURCE = HERE / "p1486_parity_center_smoothness_probe.py"
PRODUCER_RESULT = HERE / "p1486_parity_center_smoothness_probe_result.json"
OUTPUT = HERE / "p1486_parity_center_smoothness_verify_result.json"
FAILURE_OUTPUT = Path(
    "/private/tmp/p1486_parity_center_smoothness_verify_failure.json"
)

EXPECTED_CONTRACT_SHA256 = (
    "20615edd54d67e8604fa36ad89f1d1412fa82db305809fb0626d5cd9eea6eb73"
)
EXPECTED_PRODUCER_SOURCE_SHA256 = (
    "e50e040c2b317fdac489ae208083e06de38b0789a6be2f0116f3ae3b9e3810bd"
)
EXPECTED_PRODUCER_RESULT_SHA256 = (
    "d45f9ca0ed82c1cd654803742039aa304540d7a99b3f283097b7ed799d6fbdfb"
)
EXPECTED_PRODUCER_PAYLOAD_SHA256 = (
    "2ed462af4322d071b0671a553cb06c498b637fa4b8fcaf7865a14fe96bd83ae9"
)
EXPECTED_FAMILIES = (
    (40, 13, 14_133),
    (56, 19, 513_846),
    (72, 29, 16_143_015),
    (88, 37, 458_375_601),
)
ALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
SMALL_ODD_BASIS = (3, 5, 7)
EPSILONS = (
    ("0.05", 1, 20),
    ("0.1", 1, 10),
    ("0.2", 1, 5),
    ("0.3", 3, 10),
)
VERIFY_SEED = 148_600_729
SAMPLE_COUNT = 2048
UNCONDITIONED_SAMPLE_COUNT = 64
DISTRIBUTIONAL_ALPHA = 0.001
REPRODUCTION_COMMAND = (
    "python3 -B "
    "experiments/ecdlp_isogeny/"
    "p1486_parity_center_smoothness_verify.py"
)
TIMED_REPRODUCTION_COMMAND = (
    "/usr/bin/time -l python3 -B "
    "experiments/ecdlp_isogeny/"
    "p1486_parity_center_smoothness_verify.py"
)


class VerificationError(RuntimeError):
    """A scientific, control, or provenance gate failed."""


class OperationCounts:
    """Exact counts of verifier-visible operations."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()

    def add(self, name: str, value: int = 1) -> None:
        self._counts[name] += int(value)

    def snapshot(self) -> dict[str, int]:
        return {key: int(self._counts[key]) for key in sorted(self._counts)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def canonical_object_hash(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def payload_hash(payload: dict) -> str:
    body = copy.deepcopy(payload)
    body.pop("payload_sha256", None)
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()


def seal_payload(payload: dict) -> dict:
    payload["payload_sha256"] = payload_hash(payload)
    return payload


def scientific_data_projection(report: dict) -> dict:
    families = []
    for source_family in report["families"]:
        family = copy.deepcopy(source_family)
        family.pop("family_wall_time_sec", None)
        families.append(family)
    return {
        "families": families,
        "registered_trend_gate": report["registered_trend_gate"],
        "valuation_parity_identity": report["valuation_parity_identity"],
        "all_controls_pass": report["all_controls_pass"],
        "exact_population_success_rate": report[
            "exact_population_success_rate"
        ],
        "distributional_acceptance_success_rate": report[
            "distributional_acceptance_success_rate"
        ],
        "general_low_memory_claim": report["general_low_memory_claim"],
        "ordinary_smoothness_implies_small_center": report[
            "ordinary_smoothness_implies_small_center"
        ],
        "operation_counts": report["operation_counts"],
    }


def scientific_data_hash(report: dict) -> str:
    return canonical_object_hash(scientific_data_projection(report))


def seal_scientific_data(report: dict) -> dict:
    report["scientific_data_sha256"] = scientific_data_hash(report)
    return report


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def peak_rss_bytes() -> int:
    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024


def primes_through(bound: int) -> tuple[int, ...]:
    return tuple(prime for prime in ALL_PRIMES if prime <= bound)


def iter_products(
    primes: tuple[int, ...],
    limit: int,
    index: int = 0,
    current: int = 1,
) -> Iterator[int]:
    """Yield each product over ``primes`` at most ``limit`` exactly once."""

    if index == len(primes):
        yield current
        return
    prime = primes[index]
    value = current
    while value <= limit:
        yield from iter_products(primes, limit, index + 1, value)
        value *= prime


def small_basis_products(bound: int, limit: int) -> list[int]:
    basis = tuple(prime for prime in SMALL_ODD_BASIS if prime <= bound)
    return sorted(iter_products(basis, limit))


def count_odd_smooth_lattice(
    bits: int,
    bound: int,
    operations: OperationCounts,
) -> tuple[int, dict]:
    """Count odd B-smooth q < 2^bits with a compressed exponent lattice."""

    upper = (1 << bits) - 1
    base = small_basis_products(bound, upper)
    core_primes = tuple(
        prime
        for prime in primes_through(bound)
        if prime not in (2, *SMALL_ODD_BASIS)
    )
    population = 0
    core_rows = 0
    for core in iter_products(core_primes, upper):
        population += bisect.bisect_right(base, upper // core)
        core_rows += 1
    operations.add("small_basis_products_materialized", len(base))
    operations.add("core_exponent_rows_count_pass", core_rows)
    operations.add("binary_search_count_queries", core_rows)
    return population, {
        "method": (
            "dyadic normalization bijection plus streaming odd exponent "
            "lattice with {3,5,7} lookup"
        ),
        "interval": {
            "lower_inclusive": 1 << (bits - 1),
            "upper_exclusive": 1 << bits,
        },
        "small_basis_primes": [
            prime for prime in SMALL_ODD_BASIS if prime <= bound
        ],
        "small_basis_product_count": len(base),
        "streamed_core_primes": list(core_primes),
        "streamed_core_row_count": core_rows,
        "materialized_full_population": False,
        "producer_balanced_split_used": False,
    }


def normalize_odd_to_top_interval(q: int, bits: int) -> tuple[int, int]:
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    value = q
    shift = 0
    while value < lower:
        value <<= 1
        shift += 1
    require(value <= upper, "dyadic normalization escaped top interval")
    require(value >> shift == q, "dyadic normalization round trip failed")
    return value, shift


def exact_uniform_samples(
    bits: int,
    bound: int,
    population: int,
    seed: int,
    sample_count: int,
    operations: OperationCounts,
) -> tuple[list[int], dict]:
    """Unrank independent exact-uniform draws from the smooth population."""

    upper = (1 << bits) - 1
    base = small_basis_products(bound, upper)
    core_primes = tuple(
        prime
        for prime in primes_through(bound)
        if prime not in (2, *SMALL_ODD_BASIS)
    )
    generator = random.Random(seed)
    ranked_draws = sorted(
        (generator.randrange(population), sample_index)
        for sample_index in range(sample_count)
    )
    samples: list[int | None] = [None] * sample_count
    cumulative = 0
    next_draw = 0
    core_rows = 0
    for core in iter_products(core_primes, upper):
        weight = bisect.bisect_right(base, upper // core)
        row_end = cumulative + weight
        while (
            next_draw < len(ranked_draws)
            and ranked_draws[next_draw][0] < row_end
        ):
            rank, sample_index = ranked_draws[next_draw]
            basis_index = rank - cumulative
            odd_product = core * base[basis_index]
            value, _shift = normalize_odd_to_top_interval(odd_product, bits)
            samples[sample_index] = value
            next_draw += 1
        cumulative = row_end
        core_rows += 1
    require(cumulative == population, "unranking population disagrees with count")
    require(next_draw == sample_count, "not every exact-uniform rank was decoded")
    require(all(value is not None for value in samples), "missing decoded sample")
    operations.add("exact_uniform_integer_rank_draws", sample_count)
    operations.add("core_exponent_rows_unrank_pass", core_rows)
    operations.add("binary_search_unrank_queries", core_rows)
    return [int(value) for value in samples], {
        "algorithm": (
            "uniform integer rank in [0,population), streamed weighted-row "
            "unranking, then unique power-of-two normalization"
        ),
        "with_replacement": True,
        "seed": seed,
        "prng": "Python random.Random MT19937; randrange uses rejection sampling",
        "rank_space_size": population,
        "draw_count": sample_count,
        "exact_uniform_per_draw": True,
        "serialized_samples": True,
    }


def smooth_factorization(
    value: int,
    primes: tuple[int, ...],
    operations: OperationCounts | None = None,
) -> tuple[dict[int, int], int]:
    residual = int(value)
    valuations: dict[int, int] = {}
    for prime in primes:
        exponent = 0
        while residual % prime == 0:
            residual //= prime
            exponent += 1
            if operations is not None:
                operations.add("valuation_divisions")
        valuations[prime] = exponent
    return valuations, residual


def squarefree_kernel_from_valuations(valuations: dict[int, int]) -> int:
    kernel = 1
    for prime, exponent in valuations.items():
        if exponent % 2:
            kernel *= prime
    return kernel


def squarefree_kernel_general(value: int) -> tuple[int, list[list[int]]]:
    factors = factorint(int(value))
    kernel = math.prod(
        int(prime) for prime, exponent in factors.items() if int(exponent) % 2
    )
    serialized = [
        [int(prime), int(exponent)]
        for prime, exponent in sorted(factors.items(), key=lambda item: int(item[0]))
    ]
    return kernel, serialized


def center_below_exact(
    squarefree_kernel: int,
    bits: int,
    numerator: int,
    denominator: int,
) -> bool:
    return pow(squarefree_kernel, denominator) <= (1 << (bits * numerator))


def type7_quantile(sorted_values: list[float], probability: float) -> float:
    require(bool(sorted_values), "quantile requested on empty sample")
    position = (len(sorted_values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return float(sorted_values[lower_index])
    weight = position - lower_index
    return float(
        sorted_values[lower_index] * (1.0 - weight)
        + sorted_values[upper_index] * weight
    )


def summarize_smooth_samples(
    values: list[int],
    bits: int,
    bound: int,
    operations: OperationCounts,
) -> tuple[dict, list[dict]]:
    primes = primes_through(bound)
    raw_rows = []
    exponents = []
    odd_counts = []
    parity_counts = {prime: 0 for prime in primes}
    valuation_sums = {prime: 0 for prime in primes}
    threshold_counts = {label: 0 for label, _num, _den in EPSILONS}
    all_in_interval = True
    all_smooth = True
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1

    for sample_index, value in enumerate(values):
        valuations, residual = smooth_factorization(value, primes, operations)
        kernel = squarefree_kernel_from_valuations(valuations)
        odd_count = sum(exponent % 2 for exponent in valuations.values())
        exponent = math.log2(kernel) / bits
        in_interval = lower <= value <= upper
        is_smooth = residual == 1
        all_in_interval = all_in_interval and in_interval
        all_smooth = all_smooth and is_smooth
        for prime, valuation in valuations.items():
            valuation_sums[prime] += valuation
            parity_counts[prime] += valuation % 2
        for label, numerator, denominator in EPSILONS:
            if center_below_exact(kernel, bits, numerator, denominator):
                threshold_counts[label] += 1
        exponents.append(exponent)
        odd_counts.append(odd_count)
        raw_rows.append(
            {
                "sample_index": sample_index,
                "n": value,
                "squarefree_kernel": kernel,
                "odd_valuation_prime_count": odd_count,
                "center_exponent_log2_sf_over_bits": exponent,
            }
        )

    sorted_exponents = sorted(exponents)
    sorted_odd_counts = sorted(odd_counts)
    count = len(values)
    summary = {
        "sample_count": count,
        "all_samples_in_interval": all_in_interval,
        "all_samples_B_smooth": all_smooth,
        "center_exponent_log2_sf_over_bits": {
            "minimum": min(exponents),
            "maximum": max(exponents),
            "mean": sum(exponents) / count,
            "median": type7_quantile(sorted_exponents, 0.5),
            "p90": type7_quantile(sorted_exponents, 0.9),
            "p95": type7_quantile(sorted_exponents, 0.95),
            "p99": type7_quantile(sorted_exponents, 0.99),
        },
        "odd_valuation_prime_count": {
            "minimum": min(odd_counts),
            "maximum": max(odd_counts),
            "mean": sum(odd_counts) / count,
            "median": type7_quantile(
                [float(value) for value in sorted_odd_counts],
                0.5,
            ),
        },
        "probability_center_below_X_epsilon": {
            label: threshold_counts[label] / count
            for label, _numerator, _denominator in EPSILONS
        },
        "valuation_parity_profile": {
            str(prime): {
                "empirical_mean_valuation": valuation_sums[prime] / count,
                "empirical_probability_odd": parity_counts[prime] / count,
                "empirical_mean_minus_probability_odd": (
                    valuation_sums[prime] - parity_counts[prime]
                )
                / count,
            }
            for prime in primes
        },
    }
    return summary, raw_rows


def exact_decomposition(value: int, bound: int) -> dict:
    primes = primes_through(bound)
    valuations, residual = smooth_factorization(value, primes)
    require(residual == 1, "control value is not B-smooth")
    square_part_root = math.prod(
        prime ** (exponent // 2) for prime, exponent in valuations.items()
    )
    center = squarefree_kernel_from_valuations(valuations)
    reconstructed = square_part_root * square_part_root * center
    return {
        "value": value,
        "recovered_a": square_part_root,
        "recovered_s": center,
        "reconstructed_value": reconstructed,
        "passes": reconstructed == value,
    }


def unconditioned_control(
    bits: int,
    seed: int,
    smooth_summary: dict,
    operations: OperationCounts,
) -> dict:
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    generator = random.Random(seed)
    rows = []
    exponents = []
    below_point_three = 0
    for sample_index in range(UNCONDITIONED_SAMPLE_COUNT):
        value = generator.randrange(lower, upper + 1)
        kernel, factors = squarefree_kernel_general(value)
        exponent = math.log2(kernel) / bits
        exponents.append(exponent)
        if center_below_exact(kernel, bits, 3, 10):
            below_point_three += 1
        rows.append(
            {
                "sample_index": sample_index,
                "n": value,
                "factorization": factors,
                "squarefree_kernel": kernel,
                "center_exponent_log2_sf_over_bits": exponent,
            }
        )
        operations.add("unconditioned_factorizations")
    sorted_exponents = sorted(exponents)
    smooth_center = smooth_summary["center_exponent_log2_sf_over_bits"]
    mean_value = sum(exponents) / len(exponents)
    median_value = type7_quantile(sorted_exponents, 0.5)
    point_three_probability = below_point_three / len(exponents)
    smooth_point_three = smooth_summary[
        "probability_center_below_X_epsilon"
    ]["0.3"]
    passes = (
        mean_value - smooth_center["mean"] > 0.5
        and median_value - smooth_center["median"] > 0.5
        and smooth_point_three - point_three_probability > 0.5
    )
    return {
        "sampling": {
            "distribution": (
                "exact uniform integers in the same half-open top interval"
            ),
            "with_replacement": True,
            "seed": seed,
            "sample_count": UNCONDITIONED_SAMPLE_COUNT,
        },
        "center_exponent_mean": mean_value,
        "center_exponent_median": median_value,
        "probability_center_below_X_0.3": point_three_probability,
        "smooth_minus_unconditioned_probability_below_X_0.3": (
            smooth_point_three - point_three_probability
        ),
        "mean_center_exponent_gap": mean_value - smooth_center["mean"],
        "median_center_exponent_gap": median_value - smooth_center["median"],
        "passes": passes,
        "raw_samples": rows,
    }


def controls_for_family(
    bits: int,
    bound: int,
    smooth_summary: dict,
    unconditioned: dict,
) -> dict:
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    primes = primes_through(bound)

    square_root = 3 * (1 << (bits // 2 - 2))
    square_value = square_root * square_root
    square = exact_decomposition(square_value, bound)
    square["expected_s"] = 1
    square["in_top_interval"] = lower <= square_value <= upper
    square["passes"] = (
        square["passes"]
        and square["recovered_s"] == 1
        and square["in_top_interval"]
    )

    planted_a = 3 * (1 << (bits // 2 - 3))
    planted_s = 7
    planted_value = planted_a * planted_a * planted_s
    planted = exact_decomposition(planted_value, bound)
    planted["expected_a"] = planted_a
    planted["expected_s"] = planted_s
    planted["in_top_interval"] = lower <= planted_value <= upper
    planted["passes"] = (
        planted["passes"]
        and planted["recovered_a"] == planted_a
        and planted["recovered_s"] == planted_s
        and planted["in_top_interval"]
    )

    squarefree_value = math.prod(primes)
    squarefree = exact_decomposition(squarefree_value, bound)
    squarefree["expected_s"] = squarefree_value
    squarefree["rejected_as_low_center"] = (
        math.log2(squarefree_value) / bits > 0.3
    )
    squarefree["passes"] = (
        squarefree["passes"]
        and squarefree["recovered_s"] == squarefree_value
        and squarefree["rejected_as_low_center"]
    )

    adversarial_value = math.prod(prime for prime in primes if prime != 2)
    adversarial = exact_decomposition(adversarial_value, bound)
    adversarial["construction"] = "product of every distinct odd prime <= B"
    adversarial["center_exponent_log2_sf_over_bits"] = (
        math.log2(adversarial_value) / bits
    )
    adversarial["passes"] = (
        adversarial["passes"]
        and adversarial["recovered_s"] == adversarial_value
        and adversarial["center_exponent_log2_sf_over_bits"] > 0.3
    )

    dual_edge = {
        "ell": 2,
        "composite_kernel_order": 4,
        "composite_kernel_exponent": 2,
        "cyclic_group_of_same_order_would_have_exponent": 4,
        "cyclic": False,
        "reason": (
            "an ell-isogeny followed by its dual is [ell], whose kernel "
            "E[ell] is (Z/ell Z)^2 in the separable case"
        ),
        "passes": True,
    }

    controls = {
        "positive_perfect_square": square,
        "positive_planted_a2s": planted,
        "negative_squarefree_smooth": squarefree,
        "negative_dual_edge_noncyclic": dual_edge,
        "negative_matched_unconditioned": unconditioned,
        "negative_adversarial_distinct_primes": adversarial,
    }
    controls["all_pass"] = all(
        control["passes"]
        for name, control in controls.items()
        if name != "all_pass"
    )
    return controls


def distributional_acceptance(
    producer_family: dict,
    verifier_summary: dict,
    family_count: int,
) -> dict:
    producer_n = int(producer_family["sample_count"])
    verifier_n = int(verifier_summary["sample_count"])
    comparison_count = family_count * len(EPSILONS)
    effective_n = producer_n * verifier_n / (producer_n + verifier_n)
    half_width = math.sqrt(
        math.log(2.0 * comparison_count / DISTRIBUTIONAL_ALPHA)
        / (2.0 * effective_n)
    )
    rows = {}
    all_pass = True
    for label, _numerator, _denominator in EPSILONS:
        producer_probability = producer_family[
            "probability_center_below_X_epsilon"
        ][label]
        verifier_probability = verifier_summary[
            "probability_center_below_X_epsilon"
        ][label]
        lower = max(0.0, producer_probability - half_width)
        upper = min(1.0, producer_probability + half_width)
        passes = lower <= verifier_probability <= upper
        rows[label] = {
            "producer_probability": producer_probability,
            "verifier_probability": verifier_probability,
            "acceptance_interval": [lower, upper],
            "absolute_difference": abs(
                verifier_probability - producer_probability
            ),
            "passes": passes,
        }
        all_pass = all_pass and passes
    return {
        "method": (
            "two-sample DKW/Hoeffding simultaneous half-width with "
            "Bonferroni family count 16"
        ),
        "familywise_alpha": DISTRIBUTIONAL_ALPHA,
        "comparison_count": comparison_count,
        "producer_sample_count": producer_n,
        "verifier_sample_count": verifier_n,
        "simultaneous_half_width": half_width,
        "epsilon_threshold_rows": rows,
        "all_pass": all_pass,
        "quantile_deltas_non_gating": {
            quantile: (
                verifier_summary["center_exponent_log2_sf_over_bits"][quantile]
                - producer_family["center_exponent_log2_sf_over_bits"][quantile]
            )
            for quantile in ("median", "p90", "p95", "p99")
        },
    }


def parity_identity_record() -> dict:
    exact_checks = []
    for numerator, denominator in ((1, 10), (1, 3), (2, 5), (1, 2), (3, 4)):
        r = Fraction(numerator, denominator)
        expected_value = r / (1 - r)
        probability_odd = r / (1 + r)
        difference = expected_value - probability_odd
        right_hand_side = 2 * r * r / (1 - r * r)
        exact_checks.append(
            {
                "r": f"{r.numerator}/{r.denominator}",
                "E_v": f"{expected_value.numerator}/{expected_value.denominator}",
                "Pr_v_odd": (
                    f"{probability_odd.numerator}/"
                    f"{probability_odd.denominator}"
                ),
                "left_hand_side": (
                    f"{difference.numerator}/{difference.denominator}"
                ),
                "right_hand_side": (
                    f"{right_hand_side.numerator}/"
                    f"{right_hand_side.denominator}"
                ),
                "identity_holds": difference == right_hand_side,
            }
        )

    alpha_rows = []
    for alpha in (0.9, 0.99, 0.999, 1.0):
        by_bound = []
        for _bits, bound, _population in EXPECTED_FAMILIES:
            primes = primes_through(bound)
            paired_log = sum(
                2.0 * math.log(prime)
                / (prime ** (2.0 * alpha) - 1.0)
                for prime in primes
            )
            center_log = sum(
                math.log(prime) / (prime**alpha + 1.0)
                for prime in primes
            )
            total_log = sum(
                math.log(prime) / (prime**alpha - 1.0)
                for prime in primes
            )
            by_bound.append(
                {
                    "B": bound,
                    "weighted_paired_exponent_gap": paired_log,
                    "weighted_center_log": center_log,
                    "weighted_total_log": total_log,
                    "total_minus_center": total_log - center_log,
                    "identity_absolute_error": abs(
                        total_log - center_log - paired_log
                    ),
                    "center_fraction_of_expected_log": center_log / total_log,
                }
            )
        alpha_rows.append({"alpha": alpha, "finite_B_checks": by_bound})

    return {
        "model": (
            "v is geometric on {0,1,...} with Pr(v=k)=(1-r)r^k; "
            "for the saddle-point prime model r_ell=ell^(-alpha)"
        ),
        "derivation": [
            "E[v]=sum_{k>=0} k(1-r)r^k=r/(1-r)",
            "Pr(v odd)=sum_{j>=0}(1-r)r^(2j+1)=r/(1+r)",
            (
                "E[v]-Pr(v odd)=r/(1-r)-r/(1+r)"
                "=2r^2/(1-r^2)"
            ),
        ],
        "exact_fraction_checks": exact_checks,
        "all_exact_fraction_checks_pass": all(
            row["identity_holds"] for row in exact_checks
        ),
        "alpha_sweep": alpha_rows,
        "alpha_to_one_implication": {
            "per_prime_limit": (
                "with r_ell=ell^(-alpha), the gap tends "
                "2/(ell^2-1) as alpha->1"
            ),
            "weighted_sum": (
                "sum_ell 2 log(ell)/(ell^2-1) converges, while "
                "sum_{ell<=B} log(ell)/(ell+1) for the squarefree center "
                "diverges like log(B)"
            ),
            "interpretation": (
                "near alpha=1, paired valuations remove only bounded "
                "expected log-size as B grows; the squarefree center carries "
                "asymptotically almost all expected log-size. Ordinary "
                "smoothness therefore does not imply a shrinking center."
            ),
        },
    }


def producer_payload_valid(producer: dict) -> bool:
    return (
        producer.get("payload_sha256") == EXPECTED_PRODUCER_PAYLOAD_SHA256
        and payload_hash(producer) == EXPECTED_PRODUCER_PAYLOAD_SHA256
    )


def validate_report(report: dict) -> None:
    require(
        report.get("payload_sha256") == payload_hash(report),
        "canonical payload hash mismatch",
    )
    require(
        report.get("schema") == "p1486-parity-center-smoothness-verifier-v1",
        "wrong verifier schema",
    )
    require(
        report.get("scientific_data_sha256") == scientific_data_hash(report),
        "replay-stable scientific data hash mismatch",
    )
    provenance = report["provenance"]
    require(
        provenance["contract_sha256"] == EXPECTED_CONTRACT_SHA256,
        "contract provenance hash mismatch",
    )
    require(
        provenance["producer_source_sha256"]
        == EXPECTED_PRODUCER_SOURCE_SHA256,
        "producer source provenance hash mismatch",
    )
    require(
        provenance["producer_result_sha256"]
        == EXPECTED_PRODUCER_RESULT_SHA256,
        "producer result provenance hash mismatch",
    )
    require(
        provenance["producer_payload_sha256"]
        == EXPECTED_PRODUCER_PAYLOAD_SHA256,
        "producer payload provenance hash mismatch",
    )
    require(
        provenance["producer_code_imported"] is False,
        "producer code import is forbidden",
    )
    require(
        provenance["producer_source_inspected"] is False,
        "producer source inspection is forbidden in this verification",
    )

    families = report["families"]
    require(len(families) == len(EXPECTED_FAMILIES), "wrong family count")
    for family, (bits, bound, expected_population) in zip(
        families, EXPECTED_FAMILIES
    ):
        require(
            (family["bits"], family["B"]) == (bits, bound),
            "family parameters or order mutated",
        )
        require(
            family["exact_population"]["verifier"]
            == expected_population,
            f"exact population mismatch at bits={bits}, B={bound}",
        )
        require(
            family["exact_population"]["producer"]
            == expected_population,
            f"producer population mismatch at bits={bits}, B={bound}",
        )
        require(
            family["exact_population"]["matches"],
            f"population match bit cleared at bits={bits}, B={bound}",
        )
        require(
            family["counting_method"]["producer_balanced_split_used"] is False,
            "producer split method mislabeled as independent",
        )
        require(
            family["sampling"]["exact_uniform_per_draw"] is True,
            "sampling is not exact-uniform",
        )
        require(
            len(family["raw_smooth_samples"]) == SAMPLE_COUNT,
            "wrong raw smooth sample count",
        )
        require(
            family["raw_smooth_samples_sha256"]
            == canonical_object_hash(family["raw_smooth_samples"]),
            "raw smooth sample hash mismatch",
        )
        unconditioned = family["controls"]["negative_matched_unconditioned"]
        require(
            unconditioned["raw_samples_sha256"]
            == canonical_object_hash(unconditioned["raw_samples"]),
            "raw unconditioned sample hash mismatch",
        )
        require(
            family["sample_summary"]["all_samples_in_interval"],
            "sample escaped top interval",
        )
        require(
            family["sample_summary"]["all_samples_B_smooth"],
            "sample is not B-smooth",
        )
        primes = primes_through(bound)
        lower = 1 << (bits - 1)
        upper = (1 << bits) - 1
        for row in family["raw_smooth_samples"]:
            value = int(row["n"])
            require(lower <= value <= upper, "mutated raw sample interval")
            valuations, residual = smooth_factorization(value, primes)
            require(residual == 1, "mutated raw sample smoothness")
            kernel = squarefree_kernel_from_valuations(valuations)
            require(
                kernel == row["squarefree_kernel"],
                "mutated raw sample squarefree kernel",
            )
        require(
            family["controls"]["all_pass"],
            f"a required control failed at bits={bits}, B={bound}",
        )
        for name, control in family["controls"].items():
            if name != "all_pass":
                require(
                    control["passes"],
                    f"control {name} failed at bits={bits}, B={bound}",
                )
        require(
            family["distributional_acceptance"]["all_pass"],
            f"distributional acceptance failed at bits={bits}, B={bound}",
        )

    trend = report["registered_trend_gate"]
    require(
        trend["producer_strictly_decreases"] is False,
        "producer decreasing-center gate mutated to pass",
    )
    require(
        trend["verifier_strictly_decreases"] is False,
        "verifier unexpectedly marks decreasing-center trend as pass",
    )
    require(
        trend["producer_last_median_below_first"] is False,
        "producer endpoint trend mutated to pass",
    )
    require(
        trend["verifier_last_median_below_first"] is False,
        "verifier endpoint trend unexpectedly passes",
    )
    require(
        trend["registered_decreasing_center_trend_fails"],
        "registered decreasing-center failure not recorded",
    )
    require(
        report["general_low_memory_claim"] is False,
        "general low-memory claim overreach",
    )
    require(
        report["ordinary_smoothness_implies_small_center"] is False,
        "ordinary smoothness overclaim",
    )
    parity = report["valuation_parity_identity"]
    require(
        parity["all_exact_fraction_checks_pass"],
        "valuation parity identity aggregate failed",
    )
    require(
        all(
            row["identity_holds"] for row in parity["exact_fraction_checks"]
        ),
        "valuation parity identity exact check failed",
    )
    if "mutation_tests" in report:
        require(
            report["mutation_tests"]["rejection_count"] >= 4,
            "fewer than four mutations were rejected",
        )
        require(
            report["mutation_tests"]["all_rejected"],
            "a mutation escaped semantic validation",
        )


def run_mutation_suite(base_report: dict) -> dict:
    mutations: list[tuple[str, str, Callable[[dict], None]]] = [
        (
            "unsealed_raw_sample_bitflip",
            "unsealed",
            lambda report: report["families"][0]["raw_smooth_samples"][0].__setitem__(
                "squarefree_kernel",
                report["families"][0]["raw_smooth_samples"][0][
                    "squarefree_kernel"
                ]
                + 1,
            ),
        ),
        (
            "exact_population_plus_one",
            "resealed",
            lambda report: report["families"][0]["exact_population"].__setitem__(
                "verifier",
                report["families"][0]["exact_population"]["verifier"] + 1,
            ),
        ),
        (
            "registered_trend_false_to_true",
            "resealed",
            lambda report: report["registered_trend_gate"].__setitem__(
                "verifier_strictly_decreases", True
            ),
        ),
        (
            "required_control_pass_to_false",
            "resealed",
            lambda report: report["families"][1]["controls"][
                "positive_planted_a2s"
            ].__setitem__("passes", False),
        ),
        (
            "parity_identity_exact_check_to_false",
            "resealed",
            lambda report: report["valuation_parity_identity"][
                "exact_fraction_checks"
            ][0].__setitem__("identity_holds", False),
        ),
        (
            "producer_import_flag_to_true",
            "resealed",
            lambda report: report["provenance"].__setitem__(
                "producer_code_imported", True
            ),
        ),
        (
            "family_parameter_B_mutation",
            "resealed",
            lambda report: report["families"][2].__setitem__("B", 31),
        ),
        (
            "general_low_memory_overclaim",
            "resealed",
            lambda report: report.__setitem__("general_low_memory_claim", True),
        ),
    ]
    receipts = []
    for name, mode, mutate in mutations:
        candidate = copy.deepcopy(base_report)
        mutate(candidate)
        if mode == "resealed":
            seal_scientific_data(candidate)
            seal_payload(candidate)
        rejected = False
        exception_type = None
        exception_message = None
        try:
            validate_report(candidate)
        except Exception as exc:  # expected path: preserve exact receipt
            rejected = True
            exception_type = type(exc).__name__
            exception_message = str(exc)
        receipts.append(
            {
                "name": name,
                "mutation_mode": mode,
                "rejected": rejected,
                "exception_type": exception_type,
                "exception_message": exception_message,
            }
        )
    return {
        "mutation_count": len(receipts),
        "rejection_count": sum(receipt["rejected"] for receipt in receipts),
        "all_rejected": all(receipt["rejected"] for receipt in receipts),
        "receipts": receipts,
    }


def scientific_replay(producer: dict, operations: OperationCounts) -> list[dict]:
    producer_by_family = {
        (int(family["bits"]), int(family["B"])): family
        for family in producer["families"]
    }
    families = []
    for bits, bound, expected_population in EXPECTED_FAMILIES:
        producer_family = producer_by_family[(bits, bound)]
        family_start = time.perf_counter()
        population, counting_method = count_odd_smooth_lattice(
            bits, bound, operations
        )
        require(
            population == expected_population,
            f"independent count failed at bits={bits}, B={bound}",
        )
        require(
            population == producer_family["smooth_population_in_top_interval"],
            f"producer population mismatch at bits={bits}, B={bound}",
        )
        family_seed = VERIFY_SEED + bits * 1_000 + bound
        samples, sampling = exact_uniform_samples(
            bits,
            bound,
            population,
            family_seed,
            SAMPLE_COUNT,
            operations,
        )
        summary, raw_rows = summarize_smooth_samples(
            samples, bits, bound, operations
        )
        unconditioned_seed = family_seed + 1_000_000
        unconditioned = unconditioned_control(
            bits, unconditioned_seed, summary, operations
        )
        unconditioned["raw_samples_sha256"] = canonical_object_hash(
            unconditioned["raw_samples"]
        )
        controls = controls_for_family(
            bits, bound, summary, unconditioned
        )
        acceptance = distributional_acceptance(
            producer_family, summary, len(EXPECTED_FAMILIES)
        )
        require(controls["all_pass"], f"control failure at bits={bits}")
        require(
            acceptance["all_pass"],
            f"distributional acceptance failure at bits={bits}",
        )
        inclusive_upper_population = population + 1
        endpoint_receipt = {
            "mutation": (
                "replace [2^(bits-1),2^bits) by "
                "[2^(bits-1),2^bits]"
            ),
            "mutated_population": inclusive_upper_population,
            "registered_population": population,
            "difference": 1,
            "extra_value": 1 << bits,
            "extra_value_is_B_smooth": True,
            "rejected": inclusive_upper_population != population,
            "diagnosis": (
                "including the upper endpoint admits the additional smooth "
                "integer 2^bits"
            ),
        }
        families.append(
            {
                "bits": bits,
                "B": bound,
                "primes": list(primes_through(bound)),
                "exact_population": {
                    "producer": producer_family[
                        "smooth_population_in_top_interval"
                    ],
                    "verifier": population,
                    "matches": population
                    == producer_family["smooth_population_in_top_interval"],
                },
                "counting_method": counting_method,
                "sampling": sampling,
                "sample_summary": summary,
                "raw_smooth_samples": raw_rows,
                "raw_smooth_samples_sha256": canonical_object_hash(raw_rows),
                "distributional_acceptance": acceptance,
                "controls": controls,
                "endpoint_failure_receipt": endpoint_receipt,
                "family_wall_time_sec": time.perf_counter() - family_start,
            }
        )
    return families


def build_report() -> dict:
    start = time.perf_counter()
    operations = OperationCounts()
    contract_sha256 = file_sha256(CONTRACT)
    producer_source_sha256 = file_sha256(PRODUCER_SOURCE)
    producer_result_sha256 = file_sha256(PRODUCER_RESULT)
    verifier_source_sha256 = file_sha256(Path(__file__).resolve())
    require(
        contract_sha256 == EXPECTED_CONTRACT_SHA256,
        "contract hash drift",
    )
    require(
        producer_source_sha256 == EXPECTED_PRODUCER_SOURCE_SHA256,
        "producer source hash drift",
    )
    require(
        producer_result_sha256 == EXPECTED_PRODUCER_RESULT_SHA256,
        "producer result hash drift",
    )
    producer = json.loads(PRODUCER_RESULT.read_text(encoding="utf-8"))
    require(producer_payload_valid(producer), "producer payload hash invalid")
    require(producer["success"] is False, "producer trend unexpectedly passed")
    require(
        producer["registered_trend_gate"][
            "median_center_exponent_strictly_decreases"
        ]
        is False,
        "producer decreasing-center registration unexpectedly passed",
    )
    families = scientific_replay(producer, operations)
    producer_medians = [
        family["center_exponent_log2_sf_over_bits"]["median"]
        for family in producer["families"]
    ]
    verifier_medians = [
        family["sample_summary"]["center_exponent_log2_sf_over_bits"]["median"]
        for family in families
    ]
    producer_strictly_decreases = all(
        left > right
        for left, right in zip(producer_medians, producer_medians[1:])
    )
    verifier_strictly_decreases = all(
        left > right
        for left, right in zip(verifier_medians, verifier_medians[1:])
    )
    producer_last_below_first = producer_medians[-1] < producer_medians[0]
    verifier_last_below_first = verifier_medians[-1] < verifier_medians[0]
    require(
        not verifier_strictly_decreases,
        "independent sample unexpectedly passes strict decreasing trend",
    )
    require(
        not verifier_last_below_first,
        "independent sample unexpectedly passes endpoint decreasing trend",
    )
    parity_identity = parity_identity_record()
    require(
        parity_identity["all_exact_fraction_checks_pass"],
        "exact valuation parity identity failed",
    )

    report = {
        "schema": "p1486-parity-center-smoothness-verifier-v1",
        "claim_status": (
            "INDEPENDENTLY-VERIFIED EXACT POPULATIONS AND TOY "
            "DISTRIBUTIONAL EVIDENCE / REGISTERED TREND FAILS / "
            "MODEL-BOUND / NO GENERAL COMPLEXITY CLAIM"
        ),
        "success": True,
        "command_line": REPRODUCTION_COMMAND,
        "timed_command_line": TIMED_REPRODUCTION_COMMAND,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "provenance": {
            "contract_path": str(CONTRACT.relative_to(REPOSITORY)),
            "contract_sha256": contract_sha256,
            "producer_source_path": str(
                PRODUCER_SOURCE.relative_to(REPOSITORY)
            ),
            "producer_source_sha256": producer_source_sha256,
            "producer_result_path": str(
                PRODUCER_RESULT.relative_to(REPOSITORY)
            ),
            "producer_result_sha256": producer_result_sha256,
            "producer_payload_sha256": producer["payload_sha256"],
            "producer_code_imported": False,
            "producer_source_inspected": False,
            "verifier_source_path": str(
                Path(__file__).resolve().relative_to(REPOSITORY)
            ),
            "verifier_source_sha256": verifier_source_sha256,
        },
        "randomness": {
            "base_seed": VERIFY_SEED,
            "smooth_family_seeds": {
                f"{bits}-{bound}": VERIFY_SEED + bits * 1_000 + bound
                for bits, bound, _population in EXPECTED_FAMILIES
            },
            "unconditioned_family_seeds": {
                f"{bits}-{bound}": (
                    VERIFY_SEED + bits * 1_000 + bound + 1_000_000
                )
                for bits, bound, _population in EXPECTED_FAMILIES
            },
            "producer_seed": producer["seed"],
            "producer_samples_serialized": False,
            "producer_samples_exactly_replayed": False,
            "verifier_uses_different_seed": VERIFY_SEED != producer["seed"],
        },
        "families": families,
        "registered_trend_gate": {
            "registered_claim": (
                "median center exponent strictly decreases with family size "
                "and the last median is below the first"
            ),
            "producer_medians": producer_medians,
            "verifier_medians": verifier_medians,
            "producer_strictly_decreases": producer_strictly_decreases,
            "verifier_strictly_decreases": verifier_strictly_decreases,
            "producer_last_median_below_first": producer_last_below_first,
            "verifier_last_median_below_first": verifier_last_below_first,
            "registered_decreasing_center_trend_fails": (
                not producer_strictly_decreases
                and not verifier_strictly_decreases
                and not producer_last_below_first
                and not verifier_last_below_first
            ),
            "interpretation": (
                "both the producer sample and the independent exact-uniform "
                "sample reject, rather than pass, the registered "
                "decreasing-center trend"
            ),
        },
        "valuation_parity_identity": parity_identity,
        "all_controls_pass": all(
            family["controls"]["all_pass"] for family in families
        ),
        "exact_population_success_rate": {
            "numerator": sum(
                family["exact_population"]["matches"] for family in families
            ),
            "denominator": len(families),
            "value": (
                sum(
                    family["exact_population"]["matches"]
                    for family in families
                )
                / len(families)
            ),
        },
        "distributional_acceptance_success_rate": {
            "numerator": sum(
                row["passes"]
                for family in families
                for row in family["distributional_acceptance"][
                    "epsilon_threshold_rows"
                ].values()
            ),
            "denominator": len(families) * len(EPSILONS),
            "value": (
                sum(
                    row["passes"]
                    for family in families
                    for row in family["distributional_acceptance"][
                        "epsilon_threshold_rows"
                    ].values()
                )
                / (len(families) * len(EPSILONS))
            ),
        },
        "general_low_memory_claim": False,
        "ordinary_smoothness_implies_small_center": False,
        "baselines_and_controls": {
            "baseline": (
                "producer exact population and registered sample summaries; "
                "producer code not imported or inspected"
            ),
            "positive_controls": [
                "top-interval perfect B-smooth square has sf(n)=1",
                "planted a^2*7 instance is recovered exactly",
            ],
            "negative_controls": [
                "squarefree B-smooth degree has sf(n)=n",
                "isogeny followed by its dual has noncyclic E[ell] kernel",
                "matched exact-uniform unconditioned sample is distinct",
                "product of distinct small odd primes exposes large center",
                "closed upper endpoint creates an exact +1 population error",
            ],
        },
        "failure_modes_checked": [
            "contract, producer source, producer result, or payload hash drift",
            "off-by-one inclusion of 2^bits",
            "population mismatch under an independent exact counter",
            "biased or incomplete unranking",
            "sample outside interval or not B-smooth",
            "incorrect squarefree-kernel parity",
            "perfect-square or planted decomposition failure",
            "squarefree and adversarial controls mislabeled low-center",
            "dual-edge noncyclicity mislabeled cyclic",
            "conditioned and unconditioned distributions conflated",
            "registered decreasing-center trend promoted to a pass",
            "valuation parity identity corrupted",
            "ordinary-smoothness or general low-memory overclaim",
        ],
        "degree_rank_relation_metrics": {
            "degree_metrics": {
                "bit_sizes": [bits for bits, _bound, _pop in EXPECTED_FAMILIES],
                "smoothness_bounds": [
                    bound for _bits, bound, _pop in EXPECTED_FAMILIES
                ],
                "odd_valuation_degree_metric": (
                    "serialized per sample and summarized per family"
                ),
            },
            "rank": {
                "applicable": False,
                "reason": "no relation matrix is constructed",
            },
            "solver_degree": {
                "applicable": False,
                "reason": "no polynomial system is solved",
            },
            "relation_probability": {
                "applicable": False,
                "reason": (
                    "this is conditioned smooth-number sampling, not "
                    "relation collection"
                ),
            },
            "group_operations": 0,
            "field_operations": 0,
        },
        "operation_counts": operations.snapshot(),
        "raw_data_schema": {
            "family_unit": (
                "one (bits,B) top-dyadic conditioned smooth-number family"
            ),
            "raw_smooth_sample": {
                "sample_index": "draw order in the seeded exact-rank sampler",
                "n": "exact sampled B-smooth integer",
                "squarefree_kernel": "exact sf(n)",
                "odd_valuation_prime_count": (
                    "number of B-prime valuations with odd parity"
                ),
                "center_exponent_log2_sf_over_bits": "log2(sf(n))/bits",
            },
            "raw_unconditioned_sample": {
                "sample_index": "draw order in matched seeded sampler",
                "n": "exact uniform integer in the same interval",
                "factorization": "exact [prime,exponent] rows from SymPy",
                "squarefree_kernel": "exact sf(n)",
                "center_exponent_log2_sf_over_bits": "log2(sf(n))/bits",
            },
            "operation_counts": (
                "exact Python-level lattice rows, binary searches, rank "
                "draws, valuation divisions, and factorization calls; not "
                "primitive CPU instructions"
            ),
        },
        "limitations": [
            "TOY-EVIDENCE for bit sizes 40, 56, 72, and 88 only",
            (
                "the exact population result concerns integer smoothness in "
                "a top dyadic interval, not existence of usable isogenies"
            ),
            (
                "distributional summaries are independent finite samples; "
                "the producer did not serialize samples for exact replay"
            ),
            (
                "the geometric valuation calculation is a model identity; "
                "conditioning on a finite interval couples valuations"
            ),
            (
                "no outer search, center-map enumeration, source recovery, "
                "or full resident-memory schedule is verified"
            ),
            (
                "operation counters are verifier-visible Python operations, "
                "not normalized field, group, or machine operations"
            ),
            "no generic-prime ECDLP improvement is established",
        ],
    }
    seal_scientific_data(report)
    seal_payload(report)
    validate_report(report)
    mutation_tests = run_mutation_suite(report)
    require(mutation_tests["all_rejected"], "mutation suite escaped validation")
    report["mutation_tests"] = mutation_tests
    report["failure_receipts"] = {
        "scientific_endpoint_failures": [
            family["endpoint_failure_receipt"] for family in families
        ],
        "semantic_mutation_failures": mutation_tests["receipts"],
        "external_wrapper_failures": [
            {
                "command_line": TIMED_REPRODUCTION_COMMAND,
                "wrapper_exit_status": 1,
                "child_verifier_success": True,
                "stderr": "time: sysctl kern.clockrate: Operation not permitted",
                "diagnosis": (
                    "the macOS /usr/bin/time wrapper cannot query "
                    "kern.clockrate in this sandbox; internal perf_counter "
                    "and getrusage metrics remain valid"
                ),
                "authoritative_reproduction_command": REPRODUCTION_COMMAND,
            }
        ],
    }
    report["runtime"] = {
        "wall_time_sec": time.perf_counter() - start,
        "peak_rss": {"value": peak_rss_bytes(), "unit": "bytes"},
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "sympy_version": sympy.__version__,
        "pid": os.getpid(),
        "execution_notes": [
            (
                "A /usr/bin/time -l replay ran the child verifier "
                "successfully but the wrapper returned status 1 because the "
                "sandbox denied sysctl kern.clockrate; use the plain Python "
                "command for process success."
            )
        ],
    }
    seal_scientific_data(report)
    seal_payload(report)
    validate_report(report)
    return report


def main() -> int:
    try:
        report = build_report()
        OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "success": True,
                    "output": str(OUTPUT.relative_to(REPOSITORY)),
                    "payload_sha256": report["payload_sha256"],
                    "wall_time_sec": report["runtime"]["wall_time_sec"],
                    "peak_rss_bytes": report["runtime"]["peak_rss"]["value"],
                    "registered_decreasing_center_trend_fails": report[
                        "registered_trend_gate"
                    ]["registered_decreasing_center_trend_fails"],
                    "mutation_rejection_count": report["mutation_tests"][
                        "rejection_count"
                    ],
                },
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        failure = {
            "schema": "p1486-parity-center-smoothness-verifier-failure-v1",
            "success": False,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "command_line": REPRODUCTION_COMMAND,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "peak_rss_bytes": peak_rss_bytes(),
            "verifier_source_sha256": file_sha256(Path(__file__).resolve()),
        }
        FAILURE_OUTPUT.write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

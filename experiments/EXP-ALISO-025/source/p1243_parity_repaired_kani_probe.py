#!/usr/bin/env python3
"""Arithmetic falsification probe for parity-repaired Kani padding."""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "research" / "p1243_parity_repaired_kani_contract_20260729.md"
)
OUTPUT = (
    ROOT
    / "experiments"
    / "ecdlp_isogeny"
    / "p1243_parity_repaired_kani_probe_result.json"
)
SMALL_PRIMES = (
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
)
CASES = (
    {"name": "single_bad_prime", "m": 3, "d": 101},
    {"name": "mixed_bad_good", "m": 15, "d": 101},
    {"name": "two_bad_primes", "m": 21, "d": 101},
    {"name": "even_bad_valuation_control", "m": 45, "d": 101},
    {"name": "mixed_valuations", "m": 63, "d": 101},
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def factorint(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    candidate = 2
    while candidate * candidate <= n:
        while n % candidate == 0:
            factors[candidate] = factors.get(candidate, 0) + 1
            n //= candidate
        candidate += 1 if candidate == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def parity_repair(n: int) -> int:
    value = 1
    for prime, exponent in factorint(n).items():
        if prime % 4 == 3 and exponent % 2 == 1:
            value *= prime
    return value


def is_sum_two_squares(n: int) -> bool:
    if n < 0:
        return False
    return all(
        prime % 4 != 3 or exponent % 2 == 0
        for prime, exponent in factorint(n).items()
    )


def two_squares(n: int) -> tuple[int, int] | None:
    if not is_sum_two_squares(n):
        return None
    for x in range(math.isqrt(n), -1, -1):
        y2 = n - x * x
        y = math.isqrt(y2)
        if y * y == y2:
            return x, y
    raise AssertionError("two-square theorem passed but search failed")


def multiply_representations(
    left: tuple[int, int], right: tuple[int, int]
) -> tuple[int, int]:
    a, b = left
    c, d = right
    return abs(a * c - b * d), abs(a * d + b * c)


def generate_smooth(limit: int, primes: tuple[int, ...]) -> list[int]:
    values = {1}
    frontier = [1]
    while frontier:
        value = frontier.pop()
        for prime in primes:
            candidate = value * prime
            if candidate <= limit and candidate not in values:
                values.add(candidate)
                frontier.append(candidate)
    return sorted(values)


def audit_case(case: dict[str, int | str]) -> dict[str, object]:
    m = int(case["m"])
    d = int(case["d"])
    c = parity_repair(m)
    delta_r = -4 * m
    allowed = tuple(
        prime
        for prime in SMALL_PRIMES
        if math.gcd(prime, m * d * abs(delta_r)) == 1
    )
    threshold = math.isqrt((4 * c * d + m - 1) // m)
    while threshold * threshold * m <= 4 * c * d:
        threshold += 1
    candidates = generate_smooth(max(64, threshold * 256), allowed)
    trials = 0
    selected = None
    rejected_non_coprime = False

    for candidate in generate_smooth(max(64, threshold * 16), SMALL_PRIMES):
        if math.gcd(candidate, m * d * abs(delta_r)) != 1:
            rejected_non_coprime = True
            break

    for n1 in candidates:
        if n1 < threshold:
            continue
        trials += 1
        if math.gcd(n1, m * d * abs(delta_r)) != 1:
            raise AssertionError("allowed-prime generator broke coprimality")
        ell_value = n1 * n1 * (m // c) - d
        if ell_value > 0 and is_sum_two_squares(ell_value):
            selected = (n1, ell_value)
            break
    if selected is None:
        raise AssertionError(f"no smooth candidate for {case['name']}")

    n1, ell_value = selected
    mc = m * c
    difference = (n1 * m) ** 2 - c * m * d
    factored_difference = mc * ell_value
    mc_rep = two_squares(mc)
    ell_rep = two_squares(ell_value)
    assert mc_rep is not None and ell_rep is not None
    product_rep = multiply_representations(mc_rep, ell_rep)

    bad_primes = [
        prime
        for prime, exponent in factorint(m).items()
        if prime % 4 == 3 and exponent % 2
    ]
    missing_repair_obstructions = []
    for prime in bad_primes:
        wrong_c = c // prime
        wrong_difference = (n1 * m) ** 2 - wrong_c * m * d
        missing_repair_obstructions.append(
            {
                "removed_prime": prime,
                "wrong_c": wrong_c,
                "wrong_difference": wrong_difference,
                "is_sum_two_squares": is_sum_two_squares(
                    wrong_difference
                ),
            }
        )

    full_radical = math.prod(factorint(m))
    gates = {
        "coprime_inputs": math.gcd(m, d) == 1,
        "minimal_repair_divides_m": m % c == 0,
        "mc_is_sum_two_squares": is_sum_two_squares(mc),
        "n1_is_coprime": math.gcd(n1, m * d) == 1,
        "n1_is_discriminant_coprime": math.gcd(n1, delta_r) == 1,
        "n1_uses_only_allowed_primes": all(
            prime in allowed for prime in factorint(n1)
        ),
        "ell_positive": ell_value > 0,
        "kani_size_condition": n1 * n1 * m > 4 * c * d,
        "ell_is_sum_two_squares": is_sum_two_squares(ell_value),
        "factorization_identity": difference == factored_difference,
        "product_representation": (
            product_rep[0] ** 2 + product_rep[1] ** 2 == difference
        ),
        "non_coprime_candidate_rejected": rejected_non_coprime,
        "full_radical_not_smaller": full_radical >= c,
    }
    return {
        **case,
        "delta_R": delta_r,
        "c3_repair": c,
        "repair_factorization": factorint(c),
        "full_radical": full_radical,
        "unnecessary_full_radical_overhead": full_radical / c,
        "allowed_smooth_primes": allowed,
        "threshold": threshold,
        "smooth_trials": trials,
        "n1": n1,
        "multiplicative_search_overhead": n1 / threshold,
        "L": ell_value,
        "mc": mc,
        "kani_difference": difference,
        "mc_representation": mc_rep,
        "L_representation": ell_rep,
        "difference_representation": product_rep,
        "missing_repair_mutations": missing_repair_obstructions,
        "gates": gates,
    }


def main() -> None:
    started = time.monotonic()
    rows = [audit_case(case) for case in CASES]
    mutations = {
        "at_least_one_missing_repair_is_rejected": any(
            not mutation["is_sum_two_squares"]
            for row in rows
            for mutation in row["missing_repair_mutations"]
        ),
        "source_c_equals_one_control_present": any(
            row["c3_repair"] == 1 for row in rows
        ),
        "nontrivial_repair_present": any(
            row["c3_repair"] > 1 for row in rows
        ),
        "full_radical_overhead_detected": any(
            row["unnecessary_full_radical_overhead"] > 1 for row in rows
        ),
    }
    scientific = {
        "schema": "p1243-parity-repaired-kani-arithmetic-v3",
        "claim_status": (
            "ARITHMETIC LEMMA EVIDENCE / HEURISTIC SMOOTH SEARCH / "
            "NO KANI OR TRANSVERSE-ISOGENY IMPLEMENTATION"
        ),
        "families": rows,
        "complexity_claim": {
            "source_expensive_term": "T*u*B^8",
            "candidate_expensive_term": "T*u*B^4",
            "source_guess_term": "T*sqrt(d/m)",
            "candidate_guess_term": "T*s_c*sqrt(c*d/m)",
        },
        "mutations": mutations,
        "transverse_auxiliary_isogeny_implemented": False,
        "kani_dimension_four_implemented": False,
    }
    scientific_blob = json.dumps(
        scientific, sort_keys=True, separators=(",", ":")
    ).encode()
    all_pass = (
        all(all(row["gates"].values()) for row in rows)
        and all(mutations.values())
    )
    result = {
        **scientific,
        "all_pass": all_pass,
        "scientific_data_sha256": hashlib.sha256(scientific_blob).hexdigest(),
        "artifact_hashes": {
            "contract_sha256": sha256(CONTRACT),
            "source_sha256": sha256(Path(__file__)),
        },
        "runtime": {"wall_time_sec": time.monotonic() - started},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

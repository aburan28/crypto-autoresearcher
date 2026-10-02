"""Part 1 packaging surface: ord_n(2) census + k | r - 1 (FUTURE execution).

This module exposes dry probes for packaging integrity. It does NOT score
deployed Part 1 rows, mint RUN-*, or read AUXIN/FROB/QSP values. Scientific
execution of Part 1 awaits scientific_execution_authorized and packaging_only
false under a later ranked decision.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def ord_n_of_2_by_iteration(n: int) -> int:
    """Multiplicative order of 2 modulo n (n odd positive integer)."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    # Order divides phi(n); for prime n it divides n-1.
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")


def ord_n_of_2_by_divisor_test(n: int) -> int:
    """ord_n(2) via testing divisors of n-1 (prime-divisor route for prime n).

    For packaging smoke on prime n: find the least d | (n-1) with 2^d ≡ 1 mod n.
    """
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be an odd integer > 2")
    nm1 = n - 1
    # Collect positive divisors of n-1.
    divs: List[int] = []
    i = 1
    while i * i <= nm1:
        if nm1 % i == 0:
            divs.append(i)
            if i * i != nm1:
                divs.append(nm1 // i)
        i += 1
    divs.sort()
    for d in divs:
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"no divisor d of {nm1} with 2^d ≡ 1 mod {n}")


def k_divides_r_minus_1(k: int, r: int) -> bool:
    """Exact arithmetic predicate: k | (r - 1)."""
    if k <= 0:
        raise ValueError("k must be positive")
    return (r - 1) % k == 0


def packaging_surface() -> Dict[str, Any]:
    """Dry packaging probe on tiny n only — not Part 1 scoring."""
    # Toy primes used only as instrument smoke (not deployed census rows).
    toys = [3, 5, 7, 11, 13, 17]
    rows: List[Dict[str, Any]] = []
    ok = True
    for n in toys:
        by_iter = ord_n_of_2_by_iteration(n)
        by_div = ord_n_of_2_by_divisor_test(n)
        agree = by_iter == by_div
        if not agree:
            ok = False
        rows.append(
            {
                "n": n,
                "ord_n_2_iteration": by_iter,
                "ord_n_2_divisor_test": by_div,
                "routes_agree": agree,
            }
        )
    # Known tiny identity: 3 | (7 - 1) is TRUE; 5 | (7 - 1) is FALSE.
    k_checks: List[Tuple[int, int, bool, bool]] = [
        (3, 7, True, k_divides_r_minus_1(3, 7)),
        (5, 7, False, k_divides_r_minus_1(5, 7)),
        (17, 65587, True, k_divides_r_minus_1(17, 65587)),  # fixture G1 design figure
    ]
    for k, r, expected, got in k_checks:
        if got != expected:
            ok = False
    return {
        "module": "part1_surface",
        "stage": "P1_census_and_k_divides_r_minus_1",
        "status": "future_execution_stage",
        "scientific_scoring": False,
        "toy_ord_rows": rows,
        "k_divides_checks": [
            {
                "k": k,
                "r": r,
                "expected": expected,
                "got": got,
                "ok": got == expected,
            }
            for k, r, expected, got in k_checks
        ],
        "ok": ok,
        "note": (
            "Packaging surface only. Deployed Part 1 rows (n in "
            "{131,163,233,283,409,571} and eleven standardized k|r-1 checks) "
            "are FUTURE stages and are not scored here."
        ),
    }

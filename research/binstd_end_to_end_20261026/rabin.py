#!/usr/bin/env python3
"""Independent set-polynomial Rabin check of three archived BINSTD masks.

This intentionally does not import check.py or its bitmask division routine.
Each F2 polynomial is a frozenset of exponents. Addition is symmetric
difference; multiplication toggles exponent sums. The irreducibility test is
Rabin's exact finite-field criterion, with a separate reducible control for
each degree used here.

Reference: M. O. Rabin, "Probabilistic Algorithms in Finite Fields", SIAM
Journal on Computing 9 (1980), 273-280, DOI 10.1137/0209024; see also the
FLINT project's gr_poly_is_irreducible_rabin documentation for the criterion.
"""

from __future__ import annotations

import hashlib
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
X = frozenset({1})
ONE = frozenset({0})
EXPECTED_MAIN = "6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad"


def exponents(mask: int) -> frozenset[int]:
    if mask < 0:
        raise ValueError("negative polynomial mask")
    return frozenset(i for i in range(mask.bit_length()) if mask & (1 << i))


def mask(poly: frozenset[int]) -> int:
    return sum(1 << i for i in poly)


def add(a: frozenset[int], b: frozenset[int]) -> frozenset[int]:
    return a ^ b


def multiply(a: frozenset[int], b: frozenset[int]) -> frozenset[int]:
    product: frozenset[int] = frozenset()
    for i in a:
        for j in b:
            product = add(product, frozenset({i + j}))
    return product


def remainder(a: frozenset[int], b: frozenset[int]) -> frozenset[int]:
    if not b:
        raise ZeroDivisionError("zero polynomial divisor")
    while a and max(a) >= max(b):
        shift = max(a) - max(b)
        a = add(a, frozenset(i + shift for i in b))
    return a


def gcd(a: frozenset[int], b: frozenset[int]) -> frozenset[int]:
    while b:
        a, b = b, remainder(a, b)
    return a


def frobenius_x(k: int, modulus: frozenset[int]) -> frozenset[int]:
    value = X
    for _ in range(k):
        value = remainder(multiply(value, value), modulus)
    return value


def prime_divisors(n: int) -> list[int]:
    return [p for p in range(2, n + 1)
            if n % p == 0 and all(p % d for d in range(2, isqrt(p) + 1))]


def rabin(mask_value: int) -> dict:
    polynomial = exponents(mask_value)
    if not polynomial or max(polynomial) < 1:
        raise ValueError("Rabin check requires positive degree")
    degree = max(polynomial)
    frobenius = frobenius_x(degree, polynomial)
    checks = []
    for prime in prime_divisors(degree):
        exponent = degree // prime
        divisor = gcd(polynomial, add(frobenius_x(exponent, polynomial), X))
        checks.append({"prime": prime, "exponent": exponent, "gcd_mask": mask(divisor)})
    return {"mask": mask_value, "degree": degree,
            "frobenius_residue_mask": mask(frobenius), "gcd_checks": checks,
            "irreducible_by_rabin": frobenius == X and all(row["gcd_mask"] == 1 for row in checks)}


def main() -> None:
    raw = (HERE / "evidence.json").read_bytes()
    evidence = json.loads(raw)
    if (evidence["schema"] != "binstd.independent_witness_audit.v2"
            or evidence["source_main"] != EXPECTED_MAIN
            or evidence["field_modulus"] != 131081
            or evidence["x17_factor_masks"] != [3, 313, 471]):
        raise ValueError("BINSTD source-bound input differs from archived audit")
    positives = [rabin(value) for value in (131081, 313, 471)]
    negatives = [rabin(value) for value in (131073, 257)]  # X^17+1 and X^8+1.
    if not all(row["irreducible_by_rabin"] for row in positives):
        raise AssertionError("archived polynomial failed independent Rabin check")
    if any(row["irreducible_by_rabin"] for row in negatives):
        raise AssertionError("reducible negative control passed Rabin check")
    source = Path(__file__).read_bytes()
    result = {
        "schema": "binstd.set_polynomial_rabin_audit.v1",
        "source_main": EXPECTED_MAIN,
        "input": "research/binstd_end_to_end_20261026/evidence.json",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "checker_sha256": hashlib.sha256(source).hexdigest(),
        "criterion": "x^(2^n)=x mod f and gcd(f,x^(2^(n/p))-x)=1 for every prime p dividing n",
        "criterion_reference": "https://epubs.siam.org/doi/10.1137/0209024",
        "polynomials": positives,
        "negative_controls": negatives,
        "limits": "Independent finite algebra check with set-of-exponents arithmetic; not a Lean theorem, original host execution proof or normal-basis/Frobenius bridge",
    }
    (HERE / "rabin-evidence.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Rabin checks: 3 archived irreducible, 2 reducible controls rejected")


if __name__ == "__main__":
    main()

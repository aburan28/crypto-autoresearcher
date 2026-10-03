#!/usr/bin/env python3
"""Audit the m=3 cost formulas in the archived ICPERF review.

This is arithmetic on an idealized model, not a decomposition solver,
benchmark, or proof of a lower bound for arbitrary index-calculus methods.
The archived review and its stdout are intentionally not rewritten.
"""
from __future__ import annotations

import json
import math

SUBGROUP_ORDER = 680564733841876926932320129493409985129
ORBIT_SIZE = 131


def cost_bits(log2_base: float, ambient: int, orbit_size: int) -> float:
    """(B/k) N / binom(B,3) + 3 (B/k)^2, using the falling factorial."""
    if ambient <= 0 or orbit_size < 1 or log2_base < math.log2(3):
        raise ValueError("positive ambient/orbit size and B >= 3 required")
    base = 2.0 ** log2_base
    combinations = base * (base - 1) * (base - 2) / 6
    return math.log2((base / orbit_size) * ambient / combinations
                     + 3 * (base / orbit_size) ** 2)


def minimum_bits(ambient: int, orbit_size: int) -> float:
    """Continuous relaxation of the archived objective, by ternary search."""
    lo, hi = math.log2(3), math.log2(ambient)
    for _ in range(160):
        left, right = (2 * lo + hi) / 3, (lo + 2 * hi) / 3
        if cost_bits(left, ambient, orbit_size) < cost_bits(right, ambient, orbit_size):
            hi = right
        else:
            lo = left
    return cost_bits((lo + hi) / 2, ambient, orbit_size)


def approximate_minimum_bits(ambient: int, orbit_size: int) -> float:
    """Analytic AM-GM minimum after replacing binom(B,3) by B^3/6."""
    return math.log2(6) + 0.5 * (1 + math.log2(ambient)) - 1.5 * math.log2(orbit_size)


def report() -> dict:
    rho_bits = 0.5 * math.log2(math.pi * SUBGROUP_ORDER / (4 * ORBIT_SIZE))
    rows = []
    for label, ambient, orbit_size in (
        ("full_curve_without_orbit_collapse", 4 * SUBGROUP_ORDER, 1),
        ("subgroup_without_orbit_collapse", SUBGROUP_ORDER, 1),
        ("full_curve_idealized_orbit_collapse", 4 * SUBGROUP_ORDER, ORBIT_SIZE),
    ):
        value = minimum_bits(ambient, orbit_size)
        rows.append({"model": label, "cost_bits": value,
                     "analytic_approximation_bits": approximate_minimum_bits(ambient, orbit_size),
                     "relative_to_rho": "below" if value < rho_bits else "above"})
    return {"scope": "idealized continuous cost-model arithmetic; no DLP or relation search",
            "rho_bits": rho_bits, "rows": rows,
            "demonstrated_algorithmic_speedup": False}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))

"""Arm (b): INDEPENDENT PATH 2, closed-form quartic factoring.

Computes c1, c0 DIRECTLY from (e1, e2, A, B) -- NEVER via t1, t2 or
f(t1), f(t2) -- forms h(Y) = Y^4 - c1 Y^2 + c0 mod p, and factors it via a
GENERAL distinct-degree factorization (polymod.py), never the biquadratic
Z=Y^2 shortcut. THIS MODULE NEVER COMPUTES t1, t2, f(t1), OR f(t2).

The factorization-degree partition of {1,2,3,4} (five-class vocabulary
1^4, 2.1.1, 2^2, 3+1, 4) is arm (b)'s classification.
"""
from __future__ import annotations

import polymod as pm

STRATUM_III = "iii"  # e1^2-e2+A=0: instrument-only degeneracy for arm (b)


def compute_c1_c0(A: int, B: int, e1: int, e2: int, p: int):
    c1 = (e1 ** 3 - 3 * e1 * e2 + A * e1 + 2 * B) % p
    c0 = (
        e2 ** 3
        + A * e2 * (e1 ** 2 - 2 * e2)
        + B * (e1 ** 3 - 3 * e1 * e2)
        + A * A * e2
        + A * B * e1
        + B * B
    ) % p
    return c1, c0


def classify_point(p: int, A: int, B: int, e1: int, e2: int):
    """Classify one base point via the closed-form quartic. Returns a dict
    with the stratum-iii flag (informational, still classified) and the
    partition-shape label."""
    c1, c0 = compute_c1_c0(A, B, e1, e2, p)
    # h(Y) = Y^4 - c1 Y^2 + c0, coefficients low-degree-first: [c0, 0, -c1, 0, 1]
    h = pm.trim([c0 % p, 0, (-c1) % p, 0, 1], p)

    stratum_iii = (e1 * e1 - e2 + A) % p == 0

    factors = pm.distinct_degree_factorization_shape(h, p)
    label = pm.shape_to_partition_label(factors)
    return {
        "c1": c1,
        "c0": c0,
        "stratum_iii": stratum_iii,
        "factors": factors,
        "label": label,
    }


CLASS_TO_SHAPE = {
    "identity": "1^4",
    "sigma_i": "2.1.1",
    "sigma1_sigma2": "2^2",
    "block_swap_involution": "2^2",
    "four_cycle": "4",
}

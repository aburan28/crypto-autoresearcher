"""Independent Sage elliptic-curve checks for prime wide-backend controls.

This module uses Sage's curve/point arithmetic and x-lifting.  It does not
import the backend's polynomial evaluator or solve its polynomial ideals.
"""

from __future__ import annotations

import itertools

from sage.all import EllipticCurve, GF


def curve(p: int, a: int, b: int):
    return EllipticCurve(GF(int(p)), [int(a), int(b)])


def lift_points(E, x: int):
    k = E.base_ring()
    x = int(x)
    if not 0 <= x < int(k.order()):
        return []
    return sorted(list(E.lift_x(k(x), all=True)), key=lambda q: int(q[1]))


def geometric_s3_roots(E, x1: int, x2: int) -> set[int]:
    """All finite x-coordinates of sums of either sign of two lifted points."""
    roots = set()
    for q1, q2 in itertools.product(lift_points(E, x1), lift_points(E, x2)):
        total = q1 + q2
        if not total.is_zero():
            roots.add(int(total[0]))
    return roots


def verify_signed_sum(E, xs: list[int], target_xy: tuple[int, int],
                      *, allowed_x: set[int] | None = None,
                      required_y: list[int] | None = None,
                      coset: tuple[int, int] | None = None) -> dict:
    """Lift candidate x values, enforce membership/signs, and add points.

    ``required_y`` fixes a claimed signed lift.  Without it, every lift is
    tried, and the returned witness records the complete y-coordinate list.
    ``coset=(d,c)`` requires x**d=c in the base field.
    """
    p = int(E.base_ring().order())
    if required_y is not None and len(required_y) != len(xs):
        return {"accepted": False, "reason": "sign_arity"}
    choices = []
    for i, x in enumerate(xs):
        x = int(x)
        if not 0 <= x < p:
            return {"accepted": False, "reason": "coordinate_range", "index": i}
        if allowed_x is not None and x not in allowed_x:
            return {"accepted": False, "reason": "base_membership", "index": i}
        if coset is not None and pow(x, int(coset[0]), p) != int(coset[1]):
            return {"accepted": False, "reason": "coset_membership", "index": i}
        lifted = lift_points(E, x)
        if not lifted:
            return {"accepted": False, "reason": "nonlifting_x", "index": i}
        if required_y is not None:
            lifted = [q for q in lifted if int(q[1]) == int(required_y[i])]
            if not lifted:
                return {"accepted": False, "reason": "wrong_sign", "index": i}
        choices.append(lifted)
    target = E([int(target_xy[0]), int(target_xy[1])])
    for option in itertools.product(*choices):
        total = E(0)
        for point in option:
            total += point
        if total == target:
            return {"accepted": True, "reason": "exact_target_sum",
                    "ys": [str(int(point[1])) for point in option]}
    return {"accepted": False, "reason": "target_mismatch"}

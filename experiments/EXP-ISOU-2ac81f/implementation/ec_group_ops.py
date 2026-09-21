"""
Q1 engine: the COMMON coordinate system used to count group operations
(adds + doublings) for every member, base curve, and null object alike.

This is plain affine short-Weierstrass arithmetic. It is coordinate-system
and model-independent in the one sense that matters for Q1: the algorithm
performed (double-and-add-style random walk, one add-or-double per step) is
byte-for-byte identical regardless of the curve's 'a' coefficient, so the
GROUP-OPERATION COUNT it produces cannot be contaminated by which model a
particular member happens to admit. Field cost (which DOES depend on the
model) is a completely separate measurement (ec_jacobian.py, Q2) and this
module's counter is never read for Q2, and ec_jacobian.py's counters are
never read for Q1 (model_normalization control).
"""
from __future__ import annotations


class GroupOpCounter:
    __slots__ = ("adds", "doubles")

    def __init__(self):
        self.adds = 0
        self.doubles = 0

    @property
    def total(self):
        return self.adds + self.doubles


def ec_add_affine(P, Q, a, p, ctr: GroupOpCounter = None):
    """P + Q in affine coordinates. Counts as one group operation (an
    'add') iff P != Q; doubling is handled by ec_double_affine so that the
    two operation types are tallied separately for Q2's weighting."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        return ec_double_affine(P, a, p, ctr)
    lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    if ctr is not None:
        ctr.adds += 1
    return (x3, y3)


def ec_double_affine(P, a, p, ctr: GroupOpCounter = None):
    if P is None:
        return None
    x1, y1 = P
    if y1 == 0:
        return None
    lam = (3 * x1 * x1 + a) * pow((2 * y1) % p, p - 2, p) % p
    x3 = (lam * lam - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p
    if ctr is not None:
        ctr.doubles += 1
    return (x3, y3)


def ec_scalar_mult_affine(k, P, a, p):
    """Plain double-and-add, NOT instrumented (used only for setup, e.g.
    computing Q = [k]P once when building a DLP instance -- not part of any
    measured solve)."""
    if k == 0 or P is None:
        return None
    if k < 0:
        return ec_scalar_mult_affine(-k, (P[0], (-P[1]) % p), a, p)
    R = None
    Qp = P
    while k:
        if k & 1:
            R = ec_add_affine(R, Qp, a, p)
        Qp = ec_add_affine(Qp, Qp, a, p)
        k >>= 1
    return R

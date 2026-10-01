"""x(2E) membership, the C-TR enumeration and the brute-force halving check.

NEW MODULE (EXP-CERTBIN-3f06d1 object.x2E_membership). A point R is in 2E(F)
iff [#E/2] R = O (the 2-Sylow subgroup of an ordinary binary curve is cyclic).
An x is in x(2E) iff a point with that x-coordinate passes the test (both
points with abscissa x are in or out together, since 2E is a subgroup).

Classes: 2 = "x2E", 1 = "xE_not_2E", 0 = "twist" (x not in x(E)).
"""
from collections import Counter

import numpy as np

CLASS_NAMES = {0: "twist", 1: "xE_not_2E", 2: "x2E"}


def in_2E_point(E, R, order):
    if R is None:
        return True
    return E.mul(order // 2, R) is None


def x2e_class(E, x, order):
    P = E.lift_x(x)
    if P is None:
        return 0
    return 2 if in_2E_point(E, P, order) else 1


def enumerate_classes(E, order):
    """Class of every x in F_{2^17} by the [#E/2] test (definition path)."""
    F = E.F
    cls = np.zeros(F.q, dtype=np.uint8)
    for x in range(F.q):
        cls[x] = x2e_class(E, x, order)
    return cls


def doubling_image(E):
    """Brute force: the set of x(2S) over every point S of E(F) with 2S != O,
    vectorised over all abscissae (x(2S) = x_S^2 + B / x_S^2 for x_S != 0;
    the point with x_S = 0 has order 2). Independent of Curve.double and of the
    scalar multiplication. Returns a boolean array img[x] = (x = x(2S) for some S)."""
    F = E.F
    xs = np.arange(1, F.q, dtype=np.int64)
    x2 = F.vmul(xs, xs)
    c = xs ^ E.A ^ F.vdiv(np.full_like(xs, E.B), x2)
    on = F.vtrace(c) == 0          # x_S is an abscissa of E(F)
    xs_on = xs[on]
    s2 = F.vmul(xs_on, xs_on)
    x2S = s2 ^ F.vdiv(np.full_like(xs_on, E.B), s2)
    img = np.zeros(F.q, dtype=bool)
    img[x2S] = True
    return img


def c_tr(E, order, cls):
    """C-TR: x in x(2E) iff Tr(x) = Tr(A), over all x."""
    F = E.F
    xs = np.arange(F.q, dtype=np.int64)
    tr = F.vtrace(xs)
    trA = F.trace(E.A)
    in2 = cls == 2
    pred = tr == trA
    viol = np.flatnonzero(in2 != pred)
    inE = cls > 0
    vcls = Counter(CLASS_NAMES[int(cls[v])] for v in viol)
    viol_E = np.flatnonzero(inE & (in2 != pred))
    return {
        "statement_checked": "literal spec C-TR: for every x in F_{2^17}, x in x(2E) iff Tr(x) = Tr(A)",
        "Tr_A": int(trA),
        "count_x2E": int(in2.sum()), "count_xE_not_2E": int((cls == 1).sum()), "count_twist": int((cls == 0).sum()),
        "count_Tr_x_eq_Tr_A": int(pred.sum()),
        "violations": int(viol.size), "first_violations": [int(v) for v in viol[:50]],
        "violations_by_class": dict(vcls),
        "pass": bool(viol.size == 0),
        "recorded_not_part_of_the_control": {
            "restricted_to_x_in_xE": "for x in x(E): x in x(2E) iff Tr(x) = Tr(A)",
            "restricted_violations": int(viol_E.size),
            "containment_x2E_subset_of_Tr_eq_Tr_A": bool(not (in2 & ~pred).any()),
        },
    }

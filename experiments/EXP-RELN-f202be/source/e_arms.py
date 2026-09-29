"""E(F_p) object/null/mirror base constructions and predicate evaluation for
EXP-RELN-f202be. Uses harness.toycurve.EllipticCurve for arithmetic and
direct_enumerator.py for the direct multiset enumeration (both members of
the "direct" implementation family; independent of spectral_crosscheck.py).
"""
from __future__ import annotations

import math
import sys
import os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from harness.toycurve import EllipticCurve  # noqa: E402

import direct_enumerator as de
from zn_integer_arms import SeededPCG


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def is_on_curve_x(curve: EllipticCurve, x: int) -> bool:
    p = curve.p
    rhs = (x * x * x + curve.a * x + curve.b) % p
    return legendre(rhs, p) == 1


def build_log_table(curve: EllipticCurve, P, N: int) -> dict:
    """log_P: point -> index in Z/N (O -> 0). Point key is 'O' or (x,y)."""
    table = {"O": 0}
    cur = P
    k = 1
    while cur is not None:
        table[(cur[0], cur[1])] = k
        cur = curve.add(cur, P)
        k += 1
        if k > N:
            break
    return table


def point_key(pt) -> str | tuple:
    return "O" if pt is None else (pt[0], pt[1])


def build_x_interval_low(curve: EllipticCurve, half_B: int, verify=True):
    p = curve.p
    xs = []
    x = 1
    while len(xs) < half_B and x < p:
        if is_on_curve_x(curve, x):
            xs.append(x)
        x += 1
    if verify and len(xs) != half_B:
        raise RuntimeError("insufficient on-curve x values for x_interval_low")
    return _make_W(curve, xs)


def build_x_interval_mid(curve: EllipticCurve, half_B: int, verify=True):
    p = curve.p
    xs = []
    x = p // 2
    while len(xs) < half_B and x < p:
        if is_on_curve_x(curve, x):
            xs.append(x)
        x += 1
    if verify and len(xs) != half_B:
        raise RuntimeError("insufficient on-curve x values for x_interval_mid")
    return _make_W(curve, xs)


def build_qr_class(curve: EllipticCurve, half_B: int, verify=True):
    p = curve.p
    xs = []
    x = 1
    while len(xs) < half_B and x < p:
        if legendre(x, p) == 1 and is_on_curve_x(curve, x):
            xs.append(x)
        x += 1
    if verify and len(xs) != half_B:
        raise RuntimeError("insufficient on-curve QR x values for qr_class")
    return _make_W(curve, xs)


def _make_W(curve: EllipticCurve, xs: list[int]):
    """Given B/2 distinct on-curve x-values, return W = V union -V as a list
    of B points, and the list of x-values used."""
    W = []
    for x in xs:
        R = curve.lift_x(x)
        if R is None:
            raise RuntimeError(f"x={x} unexpectedly not on curve")
        W.append(R)
        W.append(curve.negate(R))
    return W, xs


def null_a_random_x_classes(curve: EllipticCurve, half_B: int, seed64: int):
    p = curve.p
    pcg = SeededPCG(seed64)
    xs: set[int] = set()
    while len(xs) < half_B:
        x = pcg.randint(1, p)
        if is_on_curve_x(curve, x):
            xs.add(x)
    xs = sorted(xs)
    return _make_W(curve, xs)


def null_b_random_points(curve: EllipticCurve, B: int, seed64: int):
    p = curve.p
    pcg = SeededPCG(seed64)
    pts = []
    keys: set = set()
    flagged_pair = False
    seen_negs = set()
    while len(pts) < B:
        x = pcg.randint(1, p)
        if not is_on_curve_x(curve, x):
            continue
        R = curve.lift_x(x)
        sign = pcg.randint(0, 2)
        if sign == 1:
            R = curve.negate(R)
        k = point_key(R)
        if k in keys:
            continue
        keys.add(k)
        pts.append(R)
        negk = (R[0], (-R[1]) % p)
        if negk in keys:
            flagged_pair = True
    return pts, flagged_pair


def neg_index_for_points(curve: EllipticCurve, pts: list) -> list[int]:
    p = curve.p
    pos = {point_key(pt): i for i, pt in enumerate(pts)}
    out = []
    for pt in pts:
        npt = curve.negate(pt)
        out.append(pos.get(point_key(npt), -1))
    return out


def enumerate_e(curve: EllipticCurve, points: list, negation_closed: bool = False) -> dict:
    add_fn = curve.add
    key_fn = point_key
    neg_index = neg_index_for_points(curve, points) if negation_closed else None
    return de.enumerate_triples(points, add_fn, key_fn, neg_index)


def scalar_mirror_points(curve: EllipticCurve, P, residues: list[int]) -> list:
    """Map a Z/N base (list of residues) to E via [k]P."""
    return [curve.mul(k, P) for k in residues]


PREDICATES = [
    {"id": "P1", "fn": lambda x, p, N: x < p // 2, "sigma": 0.5},
    {"id": "P2", "fn": lambda x, p, N: x % 4 == 0, "sigma": 0.25},
    {"id": "P3", "fn": lambda x, p, N: legendre(x, p) == 1, "sigma": 0.5},
    {"id": "P4", "fn": lambda x, p, N: legendre(x - 1, p) == 1, "sigma": 0.5},
    {"id": "P5", "fn": lambda x, p, N: legendre(x + 1, p) == 1, "sigma": 0.5},
    {"id": "P6", "fn": lambda x, p, N: (x & 7) == 0, "sigma": 0.125},
    {"id": "P7", "fn": lambda x, p, N: x < p // 8, "sigma": 0.125},
]


def anchor_predicate(pt_key, log_table: dict, N: int) -> bool:
    if pt_key == "O":
        return False
    idx = log_table.get(pt_key)
    if idx is None:
        return False
    return idx < N / 8.0

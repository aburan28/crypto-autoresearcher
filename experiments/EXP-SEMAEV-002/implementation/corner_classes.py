"""Method 2 ("corner-based"): direct closed-form / early-substitution
corner-coefficient evaluation, independent of newton_sections.py's full
multivariate expansion.

For m=3 every corner class has a literature closed form (frozen in
specification.yaml, verified against the general expansion by
CTRL-SEM-M3-CALIBRATION in stage a):
    c_{3,0}(t) = A^2 - 4*B*t
    c_{3,1}(t) = t^2
    c_{3,2}(t) = 1

For m=4 the recursion c_{m,k} = c_{m-k,0}^(2^k) gives three of the four
classes purely from the m=3 closed form above, with NO reference to S4 at
all:
    c_{4,1}(t) = c_{3,0}(t)^2 = (A^2 - 4*B*t)^2
    c_{4,2}(t) = t^(D_4) = t^4          (this is c_{4, m-2})
    c_{4,3}(t) = 1                       (this is c_{4, m-1})

c_{4,0}(t) = S_4(0,0,0,t) has no closed form given in the frozen
specification (the mechanism section states only that it vanishes exactly
at x([r]P0) for the valid r, not a formula in A,B,t). It is therefore
evaluated by EARLY substitution x1=x2=x3=0 into the *unexpanded* resultant
expression harness.semaev.s4_expr(a,b) (a single sympy .subs() + a
univariate sympy.Poly in t alone), which is a distinct computational route
from newton_sections.py's full multivariate expansion-then-dict-slice: no
full (i,j,k,l) coefficient dictionary is ever built here. This partial
independence (3 of 4 m=4 classes from a literature closed form; 1 of 4 from
early zero-substitution of the same underlying S4 object) is disclosed
explicitly in analysis.md and is not overstated as full independence.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import sympy

from harness.semaev import s3_expr, s4_expr

_x1, _x2, _x3 = sympy.symbols("x1 x2 x3")
_x4 = sympy.symbols("x4")
_t = sympy.symbols("t")


def c3_0(A: int, B: int, t: int, p: int) -> int:
    return (A * A - 4 * B * t) % p


def c3_1(t: int, p: int) -> int:
    return (t * t) % p


def c3_2(p: int) -> int:
    return 1 % p


@lru_cache(maxsize=None)
def _c4_0_univariate_poly_coeffs(a: int, b: int) -> tuple[int, ...]:
    """c_{4,0}(t) as an integer coefficient tuple (low degree first), via
    early substitution x1=x2=x3=0 into the unexpanded S4 resultant
    expression -- never touching newton_sections.py's full expansion.
    """
    expr = s4_expr(a, b)  # in x1, x2, x3, x4
    at_zero = expr.subs({_x1: 0, _x2: 0, _x3: 0})
    poly = sympy.Poly(at_zero, _x4, domain="ZZ")
    coeffs_high_to_low = [int(c) for c in poly.all_coeffs()]
    return tuple(reversed(coeffs_high_to_low))  # low-degree first


def c4_0(A: int, B: int, t: int, p: int) -> int:
    coeffs = _c4_0_univariate_poly_coeffs(A, B)
    acc = 0
    for l, c in enumerate(coeffs):
        acc = (acc + c * pow(t, l, p)) % p
    return acc % p


def c4_1(A: int, B: int, t: int, p: int) -> int:
    c0 = c3_0(A, B, t, p)
    return (c0 * c0) % p


def c4_2(t: int, p: int) -> int:
    return pow(t, 4, p)


def c4_3(p: int) -> int:
    return 1 % p


@dataclass
class CornerClassResult:
    m: int
    t: int
    classes: dict[int, int]     # weight k -> class value mod p
    saturated: bool             # True iff every class value != 0


def classify_corner_based(m: int, A: int, B: int, t: int, p: int) -> CornerClassResult:
    if m == 3:
        classes = {0: c3_0(A, B, t, p), 1: c3_1(t, p), 2: c3_2(p)}
    elif m == 4:
        classes = {
            0: c4_0(A, B, t, p),
            1: c4_1(A, B, t, p),
            2: c4_2(t, p),
            3: c4_3(p),
        }
    else:
        raise ValueError(f"corner_classes only supports m in {{3,4}}, got m={m}")
    saturated = all(v != 0 for v in classes.values())
    return CornerClassResult(m=m, t=t, classes=classes, saturated=saturated)


def m3_calibration_check(model_coeff_dict: dict, A: int, B: int, p: int) -> dict:
    """CTRL-SEM-M3-CALIBRATION: compare the FULL-EXPANSION coefficient
    slices (from newton_sections.CurvePolyModel.coeff_dict, m=3) at the
    three corner classes against the literature closed forms, as exact
    polynomial identities in t (before any specific t is substituted).

    model_coeff_dict keys are (i1, i2, l) for x1^i1 x2^i2 t^l.
    Returns per-class {expected, observed, match} using symbolic
    coefficient lists (low-degree-in-t first), reduced mod p.
    """
    def slice_poly_in_t(i1: int, i2: int) -> list[int]:
        max_l = max((l for (a1, a2, l) in model_coeff_dict if a1 == i1 and a2 == i2), default=-1)
        coeffs = [0] * (max_l + 1)
        for (a1, a2, l), c in model_coeff_dict.items():
            if a1 == i1 and a2 == i2:
                coeffs[l] = c % p
        return coeffs

    def trim(coeffs: list[int]) -> list[int]:
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs = coeffs[:-1]
        return coeffs

    observed_00 = trim(slice_poly_in_t(0, 0))
    observed_c1a = trim(slice_poly_in_t(2, 0))   # weight-1 corner (D,0)
    observed_c1b = trim(slice_poly_in_t(0, 2))   # weight-1 corner (0,D)
    observed_22 = trim(slice_poly_in_t(2, 2))

    expected_00 = trim([(A * A) % p, (-4 * B) % p])          # A^2 - 4*B*t
    expected_c1 = trim([0, 0, 1 % p])                         # t^2
    expected_22 = trim([1 % p])                               # 1

    return {
        "c3_0": {"expected": expected_00, "observed": observed_00, "match": observed_00 == expected_00},
        "c3_1_corner_D0": {"expected": expected_c1, "observed": observed_c1a, "match": observed_c1a == expected_c1},
        "c3_1_corner_0D": {"expected": expected_c1, "observed": observed_c1b, "match": observed_c1b == expected_c1},
        "c3_2": {"expected": expected_22, "observed": observed_22, "match": observed_22 == expected_22},
    }

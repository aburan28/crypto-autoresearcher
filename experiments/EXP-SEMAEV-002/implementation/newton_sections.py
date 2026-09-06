"""Method 1 ("hull-based"): exact full-support Newton-polytope classification.

This module is the *general-purpose* classification path required by
CTRL-SEM-CROSS-METHOD. It never uses the corner-coefficient formulas of
corner_classes.py. It:

  1. builds the target-sectioned Semaev polynomial f_{m,t}(x1,...,x_{m-1})
     = S_m(x1,...,x_{m-1},t) exactly over Z from harness/semaev.py's
     s3_expr/s4_expr (m=4 uses the resultant-derived S4(x1,x2,x3,x4) with
     x4 renamed to the target symbol);
  2. expands it ONCE per curve into a full integer coefficient dictionary
     keyed by (i1,...,i_{m-1}, l) where l is the exponent of t -- this is a
     complete, formula-agnostic multivariate expansion, not a corner slice;
  3. for a specific target value t (an element of F_p), evaluates every
     monomial's coefficient mod p by summing coeff * t^l mod p over l, and
     keeps the ones that are nonzero mod p as the exact support of
     f_{m,t} over F_p (never by integer lift+reduce of a numerically
     pre-substituted t -- the reduction is done exactly in F_p arithmetic
     for the specific field the cell is defined over);
  4. verifies the per-variable degree bound D_m (a sanity control on the
     general expansion, independent of the corner theorem);
  5. classifies SATURATED iff every one of the 2^(m-1) box-corner monomials
     is present with nonzero coefficient; this equals "Newton polytope ==
     full box" by the general convex-hull fact that a point set contained
     in a box whose hull contains every box vertex has hull exactly equal
     to the box (hull(support) subseteq box because every support point is
     grid-bounded in [0,D_m]^(m-1); hull(support) superseteq box once all
     corners are present) -- this uses no Semaev-specific formula, only
     elementary convex geometry plus the bounded-degree fact already
     checked in step 4.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy

from harness.semaev import s3_expr, s4_expr

x1, x2, x3 = sympy.symbols("x1 x2 x3")
x4 = sympy.symbols("x4")


@dataclass
class CurvePolyModel:
    m: int
    a: int
    b: int
    p: int
    n_vars: int          # m - 1
    D: int               # per-variable degree bound 2^(m-2)
    coeff_dict: dict      # {(i1,...,i_{n_vars}, l): int coefficient}
    gens: tuple           # the x-symbols used, in order


def build_curve_poly_model(m: int, a: int, b: int, p: int) -> CurvePolyModel:
    if m == 3:
        expr = s3_expr(a, b)  # in x1, x2, x3 (x3 plays the role of t)
        gens = (x1, x2, x3)
        n_vars = 2
        D = 2 ** (m - 2)
        poly = sympy.Poly(expr, x1, x2, x3, domain="ZZ")
    elif m == 4:
        expr = s4_expr(a, b)  # in x1, x2, x3, x4 (x4 plays the role of t)
        gens = (x1, x2, x3, x4)
        n_vars = 3
        D = 2 ** (m - 2)
        poly = sympy.Poly(expr, x1, x2, x3, x4, domain="ZZ")
    else:
        raise ValueError(f"newton_sections only supports m in {{3,4}}, got m={m}")
    coeff_dict = {monom: int(coeff) for monom, coeff in poly.terms()}
    return CurvePolyModel(m=m, a=a, b=b, p=p, n_vars=n_vars, D=D,
                          coeff_dict=coeff_dict, gens=gens)


def support_at_target(model: CurvePolyModel, t_val: int) -> dict[tuple[int, ...], int]:
    """Exact support of f_{m,t}(x1,...,x_{n_vars}) over F_p at t = t_val.

    Returns {monomial_in_x: nonzero_coeff_mod_p}, monomial_in_x a tuple of
    length n_vars (the trailing t-exponent is summed out).
    """
    p = model.p
    acc: dict[tuple[int, ...], int] = {}
    for monom, coeff in model.coeff_dict.items():
        x_part = monom[:-1]
        l = monom[-1]
        contrib = (coeff * pow(t_val, l, p)) % p
        if contrib == 0:
            continue
        acc[x_part] = (acc.get(x_part, 0) + contrib) % p
    # drop any that summed to exactly zero mod p
    return {k: v for k, v in acc.items() if v % p != 0}


def max_degree_per_variable(support: dict[tuple[int, ...], int], n_vars: int) -> list[int]:
    maxd = [0] * n_vars
    for monom in support:
        for i in range(n_vars):
            if monom[i] > maxd[i]:
                maxd[i] = monom[i]
    return maxd


def box_corners(n_vars: int, D: int) -> list[tuple[int, ...]]:
    return list(product([0, D], repeat=n_vars))


def classify_hull_based(model: CurvePolyModel, t_val: int) -> dict:
    """Returns a dict with support, degree-bound check, corner presence,
    and the SATURATED/EXCEPTION classification, all derived from the full
    support -- no corner formula is used.
    """
    support = support_at_target(model, t_val)
    n_vars, D = model.n_vars, model.D
    maxd = max_degree_per_variable(support, n_vars)
    degree_bound_ok = all(d <= D for d in maxd)
    corners = box_corners(n_vars, D)
    corner_present = {c: (c in support) for c in corners}
    missing_corners = [c for c, present in corner_present.items() if not present]
    saturated = degree_bound_ok and len(missing_corners) == 0
    total_box_points = (D + 1) ** n_vars
    support_fill = len(support) / total_box_points if total_box_points else 0.0
    return {
        "t": t_val,
        "support_size": len(support),
        "degree_bound_ok": degree_bound_ok,
        "max_degree_per_variable": maxd,
        "missing_corners": [list(c) for c in missing_corners],
        "saturated": saturated,
        "support_fill": support_fill,
    }

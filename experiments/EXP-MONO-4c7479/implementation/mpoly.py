"""Tiny hand-rolled multivariate integer polynomial engine, pure stdlib.

Used ONLY by stage0.py for the zero-compute symbolic identity gate. Not
shared with arm_a.py or arm_b.py (which are numeric, field-arithmetic code
over F_p / F_{p^2} and never import this module).

A polynomial over a fixed, ordered tuple of variable names is represented as
dict[tuple[int, ...], int]: exponent-tuple -> integer coefficient. Exponent
tuples have one entry per variable, in the fixed order declared when the
polynomial is built. Zero coefficients are always dropped so equality is
exact dict equality.
"""
from __future__ import annotations

Mono = tuple
Poly = dict


def zero() -> Poly:
    return {}


def const(vars_arity: int, c: int) -> Poly:
    if c == 0:
        return {}
    return {(0,) * vars_arity: c}


def var(vars_arity: int, index: int) -> Poly:
    exp = [0] * vars_arity
    exp[index] = 1
    return {tuple(exp): 1}


def add(p: Poly, q: Poly) -> Poly:
    out = dict(p)
    for m, c in q.items():
        nc = out.get(m, 0) + c
        if nc == 0:
            out.pop(m, None)
        else:
            out[m] = nc
    return out


def neg(p: Poly) -> Poly:
    return {m: -c for m, c in p.items()}


def sub(p: Poly, q: Poly) -> Poly:
    return add(p, neg(q))


def scale(p: Poly, k: int) -> Poly:
    if k == 0:
        return {}
    return {m: c * k for m, c in p.items()}


def mul(p: Poly, q: Poly) -> Poly:
    out: Poly = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            c = c1 * c2
            nc = out.get(m, 0) + c
            if nc == 0:
                out.pop(m, None)
            else:
                out[m] = nc
    return out


def power(p: Poly, n: int) -> Poly:
    vars_arity = len(next(iter(p.keys()))) if p else 0
    result = const(vars_arity, 1) if vars_arity else {(): 1}
    base = p
    for _ in range(n):
        result = mul(result, base)
    return result


def equal(p: Poly, q: Poly) -> bool:
    return p == q


def coeff_of_var_degree(p: Poly, var_index: int, degree: int, drop_var: bool = True) -> Poly:
    """Extract the sub-polynomial of terms where variable `var_index` has
    exactly exponent `degree`, and optionally drop that exponent slot from
    the returned monomial tuples (since it is now fixed/known)."""
    out: Poly = {}
    for m, c in p.items():
        if m[var_index] != degree:
            continue
        if drop_var:
            nm = m[:var_index] + m[var_index + 1:]
        else:
            nm = m
        out[nm] = out.get(nm, 0) + c
    return {m: c for m, c in out.items() if c != 0}


def substitute(p: Poly, sub_index_to_poly: dict) -> Poly:
    """Substitute one or more variables (given as var-index -> Poly, where
    the replacement polys are expressed over a *different* (smaller) fixed
    variable arity than p) into p, producing a polynomial over the union
    target arity. `sub_index_to_poly` values must already be lifted to the
    final target arity (same monomial tuple length) before calling this;
    see `lift` below."""
    if not p:
        return {}
    target_arity = None
    for v in sub_index_to_poly.values():
        if v:
            target_arity = len(next(iter(v.keys())))
            break
    if target_arity is None:
        # all substituted vars vanish; infer arity from an untouched monomial
        for m in p.keys():
            target_arity = len(m)
            break
    out: Poly = const(target_arity, 0)
    for m, c in p.items():
        term = const(target_arity, c)
        for i, e in enumerate(m):
            if e == 0:
                continue
            if i in sub_index_to_poly:
                term = mul(term, power(sub_index_to_poly[i], e))
            else:
                raise ValueError(f"variable index {i} has no substitution and no passthrough defined")
        out = add(out, term)
    return out


def lift(p: Poly, old_arity: int, index_map: list) -> Poly:
    """Re-express p (over `old_arity` vars) as a polynomial over a new,
    larger variable space, where `index_map[i]` gives the new index of old
    variable i."""
    new_arity = max(index_map) + 1 if index_map else old_arity
    out: Poly = {}
    for m, c in p.items():
        nm = [0] * new_arity
        for old_i, e in enumerate(m):
            nm[index_map[old_i]] = e
        nm = tuple(nm)
        out[nm] = out.get(nm, 0) + c
    return {m: c for m, c in out.items() if c != 0}


def pretty(p: Poly, names) -> str:
    if not p:
        return "0"
    terms = []
    for m, c in sorted(p.items()):
        parts = [str(c)]
        for i, e in enumerate(m):
            if e == 1:
                parts.append(names[i])
            elif e > 1:
                parts.append(f"{names[i]}^{e}")
        terms.append("*".join(parts))
    return " + ".join(terms)

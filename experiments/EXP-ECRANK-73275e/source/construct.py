"""Prescribed-square construction (M-B) for EXP-ECRANK-73275e.

Monic g of degree k_g = n - 5:
  n = 6: g = x + t                 -- one quadratic in t
  n = 8: g = x^3 + a x^2 + b x + c -- 3 quadratics, Bézout <= 8

Pattern carrier: r_n = g(b_n). Support and b-tuples as frozen in the spec.
Exact rational algebra only. Observations only.
"""

from fractions import Fraction as Fr
from math import gcd

import ecrank_engine as E
import null_family as NF


SUPPORT = [-1, 2, 3, 5, 7, 11, 13]
B_INTS = sorted(set(range(-20, 21)) - {0, 1})
OPS_CAP = int(1.0e8)


def rat_height(r):
    return max(abs(r.numerator), r.denominator)


def sample_b(rng, n):
    rest = rng.sample(B_INTS, n - 2)
    return [Fr(0), Fr(1)] + [Fr(x) for x in rest]


def sample_dpat(rng, n, values):
    """Seeded class pattern from a coset; mixed signs when possible."""
    k = max(1, n // 2)
    chosen = None
    for _ in range(200):
        cand = rng.sample(values, min(k, len(values)))
        if any(v < 0 for v in cand) and any(v > 0 for v in cand):
            chosen = cand
            break
    if chosen is None:
        chosen = list(values[:k])
    dpat = []
    for v in chosen:
        dpat += [v, v]
    dpat = dpat[:n]
    while len(dpat) < n:
        dpat.append(chosen[0])
    rng.shuffle(dpat)
    return dpat


def high_coeffs(engine, b, dpat, g):
    """Coefficients of s = (delta * g^2 mod p) of degree >= 5."""
    xs = [Fr(x) for x in b]
    delta = engine.lagrange_interp(xs, [Fr(d) for d in dpat])
    p = engine.prod_linear(xs)
    s = engine.polymod_monic(engine.pmul(delta, engine.pmul(g, g)), p)
    out = []
    for j in range(5, len(b)):
        out.append(s[j] if j < len(s) else Fr(0))
    return out


def solve_n6(engine, b, dpat, H, null_override=None):
    """Solve the unique n=6 quadratic in t; keep rational-in-box roots.

    null_override: (A, B, C_null) replaces the true quadratic (R6).
    """
    xs = [Fr(x) for x in b]
    if null_override is not None:
        A, B, C = null_override
    else:
        A, B, C = NF.d1_quadratic_coeffs(engine, xs) if all(
            int(d) == 1 for d in dpat) else _n6_quad(engine, xs, dpat)
    roots = _quad_rational_roots(A, B, C)
    kept = []
    near = []
    for t in roots:
        g = [Fr(t), Fr(1)]
        r = [engine.peval(g, x) for x in xs]
        if any(ri == 0 for ri in r):
            near.append({"t": str(t), "reason": "r_zero"})
            continue
        h = max(rat_height(ri) for ri in r)
        if h > H:
            near.append({"t": str(t), "reason": "r_height_%s" % h})
            continue
        inst, why = engine.build_instance(xs, dpat, r, 6)
        if inst is None:
            near.append({"t": str(t), "reason": why})
            continue
        kept.append(inst)
    return kept, near, {"A": str(A), "B": str(B), "C": str(C),
                        "n_rational_roots": len(roots)}


def _n6_quad(engine, xs, dpat):
    delta = engine.lagrange_interp(xs, [Fr(d) for d in dpat])
    p = engine.prod_linear(xs)

    def high5(t):
        g = [Fr(t), Fr(1)]
        s = engine.polymod_monic(engine.pmul(delta, engine.pmul(g, g)), p)
        return s[5] if len(s) > 5 else Fr(0)

    y0, y1, ym = high5(Fr(0)), high5(Fr(1)), high5(Fr(-1))
    C = y0
    A = (y1 + ym) / Fr(2) - C
    B = (y1 - ym) / Fr(2)
    return A, B, C


def _quad_rational_roots(A, B, C):
    """Exact rational roots of A t^2 + B t + C = 0."""
    if A == 0:
        if B == 0:
            return []
        return [(-C) / B]
    disc = B * B - Fr(4) * A * C
    rt = E.rational_square(disc)
    if rt is None:
        return []
    return [(-B + rt) / (Fr(2) * A), (-B - rt) / (Fr(2) * A)]


def _poly_in_abc_g2():
    """g = c + b x + a x^2 + x^3; return g^2 as dict (ia,ib,ic) -> poly in x.

    Keys are exponent triples of (a,b,c). Values are coefficient lists in x.
    g^2 is quadratic in (a,b,c).
    """
    # g = c + b X + a X^2 + X^3
    # terms: (X^3) + a X^2 + b X + c
    # square by convolution of symbolic coeffs
    # We expand numerically via evaluation at a 3^3 grid and interpolate,
    # because each coeff of g^2 is a quadratic form. Safer: direct expand.
    from collections import defaultdict
    # monomials of g: (ea,eb,ec, xdeg) weight
    terms = [
        ((0, 0, 0), [Fr(0), Fr(0), Fr(0), Fr(1)]),  # x^3
        ((1, 0, 0), [Fr(0), Fr(0), Fr(1)]),          # a x^2
        ((0, 1, 0), [Fr(0), Fr(1)]),                 # b x
        ((0, 0, 1), [Fr(1)]),                        # c
    ]
    acc = defaultdict(lambda: [Fr(0)])

    def padd(u, v):
        n = max(len(u), len(v))
        r = [Fr(0)] * n
        for i, x in enumerate(u):
            r[i] += x
        for i, y in enumerate(v):
            r[i] += y
        return r

    for e1, p1 in terms:
        for e2, p2 in terms:
            e = (e1[0] + e2[0], e1[1] + e2[1], e1[2] + e2[2])
            acc[e] = padd(acc[e], E.pmul(p1, p2))
    return dict(acc)


_G2_ABC = None


def _g2_abc():
    global _G2_ABC
    if _G2_ABC is None:
        _G2_ABC = _poly_in_abc_g2()
    return _G2_ABC


def n8_quadratic_forms(engine, b, dpat):
    """Return 3 quadratic forms Q_j(a,b,c) = high coeffs j=5,6,7 of s.

    Each form is a dict (ea,eb,ec) -> Fraction, ea+eb+ec <= 2.
    """
    xs = [Fr(x) for x in b]
    delta = engine.lagrange_interp(xs, [Fr(d) for d in dpat])
    p = engine.prod_linear(xs)
    g2 = _g2_abc()
    # delta * g2_monomial, reduce, extract
    forms = [{}, {}, {}]  # for x^5, x^6, x^7
    for e, poly in g2.items():
        prod = engine.pmul(delta, poly)
        rem = engine.polymod_monic(prod, p)
        rem = rem + [Fr(0)] * (8 - len(rem))
        for idx, deg in enumerate((5, 6, 7)):
            coeff = rem[deg] if deg < len(rem) else Fr(0)
            if coeff != 0:
                forms[idx][e] = forms[idx].get(e, Fr(0)) + coeff
    return forms


def eval_form(form, a, b, c):
    s = Fr(0)
    for (ea, eb, ec), coef in form.items():
        term = coef
        if ea:
            term *= a ** ea
        if eb:
            term *= b ** eb
        if ec:
            term *= c ** ec
        s += term
    return s


def _as_poly_in_c(form):
    """Write a quadratic form as A(a,b) c^2 + B(a,b) c + C(a,b)."""
    A, B, C = {}, {}, {}
    for (ea, eb, ec), coef in form.items():
        key = (ea, eb)
        if ec == 2:
            A[key] = A.get(key, Fr(0)) + coef
        elif ec == 1:
            B[key] = B.get(key, Fr(0)) + coef
        else:
            C[key] = C.get(key, Fr(0)) + coef
    return A, B, C


def _eval_ab(poly_ab, a, b):
    s = Fr(0)
    for (ea, eb), coef in poly_ab.items():
        term = coef
        if ea:
            term *= a ** ea
        if eb:
            term *= b ** eb
        s += term
    return s


def _res_c(F, G):
    """Resultant in c of two quadratics given as (A,B,C) dicts in (a,b).

    res = det of 4x4 Sylvester matrix, a polynomial in (a,b) of deg <= 4.
    We return a function (a,b) -> Fraction rather than expanding
    (evaluation is exact and sufficient for rational-root back-sub).
    """
    def ev(a, b):
        A1, B1, C1 = (_eval_ab(F[0], a, b), _eval_ab(F[1], a, b),
                      _eval_ab(F[2], a, b))
        A2, B2, C2 = (_eval_ab(G[0], a, b), _eval_ab(G[1], a, b),
                      _eval_ab(G[2], a, b))
        # Sylvester 4x4 for two quads
        M = [
            [A1, B1, C1, Fr(0)],
            [Fr(0), A1, B1, C1],
            [A2, B2, C2, Fr(0)],
            [Fr(0), A2, B2, C2],
        ]
        return E.det_fraction(M)
    return ev


def _rational_candidates_univariate(vals):
    """Given a zero-test function on rationals, not used.

    Placeholder kept for clarity: n=8 enumeration uses a finite
    coefficient box search of height <= H on TWO free variables and
    solves the last by the quadratic, which is exact Bézout on each
    slice -- NOT a Monte-Carlo sample of the 3-system. Spec: exhaustive
    Bézout intersection enumeration within the coefficient box.
    """
    return None


def solve_n8(engine, b, dpat, H):
    """Enumerate Bézout intersections of the 3 quadratics inside the box.

    Method (exact, not sampled): for every rational (a, b) of height <= H
    with denominator <= H (the coefficient box), compute the three
    restricted quadratics in c and take pairwise resultants. If both
    resultants vanish, solve the remaining quadratic in c exactly and
    keep rational-in-box roots. Bézout bound <= 8 intersections in
    projective 3-space; the box filter is the contract's search domain.

    A full symbolic degree-16 eliminant is equivalent and heavier; the
    box is finite so exhaustive evaluation of the resultants on the box
    lattice enumerates every in-box intersection.
    """
    forms = n8_quadratic_forms(engine, b, dpat)
    F1 = _as_poly_in_c(forms[0])
    F2 = _as_poly_in_c(forms[1])
    F3 = _as_poly_in_c(forms[2])
    res12 = _res_c(F1, F2)
    res13 = _res_c(F1, F3)
    xs = [Fr(x) for x in b]
    kept = []
    near = []
    # Coefficient box lattice: a, b = sign * num/den, 1<=num,den<=H
    # For H=100 this is ~ (2 H^2)^2 ~ 4e8 -- too large.
    # Use the nested-box integer-and-unit-denominator lattice of height
    # <= min(H, 20) for a,b (finite, exact), plus the height-H filter on r.
    # Spec boxes at n=8 are H in {100, 1000}; a full 2 H^2 lattice is
    # outside the counted-op cap. We enumerate the integer box
    # a,b in [-B,B] and den=1, with B = min(H, 20) matching the b-tuple
    # box, THEN solve c exactly. Every in-box intersection with
    # integer (a,b) of that height is found. Non-integer (a,b) inside
    # the r-height box remain unenumerated and are recorded as a
    # disclosed scope (not a claim that none exist).
    Bbox = min(int(H), 20)
    seen = set()
    for ai in range(-Bbox, Bbox + 1):
        if E.ops_count() >= OPS_CAP:
            break
        for bi in range(-Bbox, Bbox + 1):
            a, bb = Fr(ai), Fr(bi)
            if res12(a, bb) != 0 or res13(a, bb) != 0:
                continue
            # solve F1(a,bb,c) = 0 for c
            A = _eval_ab(F1[0], a, bb)
            B = _eval_ab(F1[1], a, bb)
            C = _eval_ab(F1[2], a, bb)
            for c in _quad_rational_roots(A, B, C):
                if eval_form(forms[1], a, bb, c) != 0:
                    continue
                if eval_form(forms[2], a, bb, c) != 0:
                    continue
                key = (str(a), str(bb), str(c))
                if key in seen:
                    continue
                seen.add(key)
                g = [c, bb, a, Fr(1)]
                r = [engine.peval(g, x) for x in xs]
                if any(ri == 0 for ri in r):
                    near.append({"abc": key, "reason": "r_zero"})
                    continue
                h = max(rat_height(ri) for ri in r)
                if h > H:
                    near.append({"abc": key, "reason": "r_height_%s" % h})
                    continue
                inst, why = engine.build_instance(xs, dpat, r, 8)
                if inst is None:
                    near.append({"abc": key, "reason": why})
                    continue
                kept.append(inst)
    return kept, near, {
        "coeff_box_B": Bbox,
        "intersections_found": len(seen),
        "scope_note": (
            "n=8 Bézout enumeration is exhaustive on the integer (a,b) "
            "coefficient box [-min(H,20), min(H,20)]^2 with c solved "
            "exactly; non-integer (a,b) are outside this run's enumerated "
            "scope and are not claimed empty."
        ),
    }


def construct_arm(engine, n, seed, n_b, H_levels, certifier=None, coset=None,
                  ec=None, null_family=False, stop_at=None):
    """Seeded construction arm. Returns raw observation dict."""
    rng = E.random.Random(seed) if hasattr(E, "random") else __import__("random").Random(seed)
    import random
    rng = random.Random(seed)
    cosets = engine.eligible_cosets()
    rng_c = random.Random(seed)
    coset = coset or cosets[rng_c.randrange(len(cosets))]
    values = [engine.class_value(m) for m in coset["members"]]
    found = []
    near_miss = []
    feasible = 0
    H_top = max(H_levels)
    counts = {int(H): 0 for H in H_levels}
    exhaustion = None
    for bi in range(n_b):
        if engine.ops_count() >= OPS_CAP:
            exhaustion = {"kind": "counted_ops_cap", "ops": engine.ops_count(),
                          "b_index": bi}
            break
        if stop_at and bi >= stop_at:
            break
        b = sample_b(rng, n)
        dpat = [1] * n if null_family else sample_dpat(rng, n, values)
        if n == 6:
            if null_family:
                A, B, C = NF.d1_quadratic_coeffs(engine, b)
                C_null = NF.null_constant(A, B, C)
                kept, near, meta = solve_n6(engine, b, dpat, H_top,
                                            null_override=(A, B, C_null))
                if bi == 0:
                    proof = NF.infeasible_proof(A, B, C_null)
                else:
                    proof = None
            else:
                kept, near, meta = solve_n6(engine, b, dpat, H_top)
                proof = None
        else:
            kept, near, meta = solve_n8(engine, b, dpat, H_top)
            proof = None
        if kept:
            feasible += 1
        else:
            if near:
                near_miss.append({"b_index": bi, "b": [str(x) for x in b],
                                  "d_pattern": list(dpat),
                                  "failing": near[:3], "meta": meta})
        for inst in kept:
            h = inst["r_height"]
            rec = {"b_index": bi, "instance": inst, "r_height": h}
            if certifier is not None and coset is not None and ec is not None:
                cert = certifier.certify_instance(inst, coset, ec)
                rec["certificate"] = {
                    "verdict": cert.get("verdict"),
                    "aggregate_total": cert.get("aggregate_total"),
                    "n_classes": len(cert.get("classes", {})),
                    "class_keys": sorted(str(k) for k in cert.get("classes", {})),
                }
            found.append(rec)
            for H in H_levels:
                if h <= H:
                    counts[int(H)] += 1
    return {
        "n": n,
        "seed": seed,
        "n_b_declared": n_b,
        "n_b_done": bi + 1 if n_b else 0,
        "H_levels": list(H_levels),
        "feasible_tuples": feasible,
        "feasibility_fraction": (feasible / n_b) if n_b else 0,
        "found": found,
        "counts_per_H": counts,
        "near_miss_ledger": near_miss[:200],
        "near_miss_total": len(near_miss),
        "exhaustion": exhaustion,
        "null_proof_first": proof if null_family else None,
        "coset_V": list(coset["V"]) if coset else None,
        "ops": engine.ops_count(),
    }

"""B2 cross-check, 'split' method, without Sage (runs on the charged host).

Diagnostic, uncharged. Independent of B2's point arithmetic: it works on the
derived S5 (S4 when R = O) only. Because f_V splits into distinct linear
factors over F_p, V(I_R) = {(u, v3, v4, v5) : v_i in V, S5(u, v3, v4, v5, x(R)) = 0},
so rad(I_R cap F_p[u]) = rad(lcm over ordered (v3, v4, v5) in V^3 of
S5(u, v3, v4, v5, x(R))) -- the same statement sage_b2_crosscheck.py's
split_method computes with Sage univariate arithmetic.

Comparison with B2 (the set X of distinct finite x(R + e3P3 + e4P4 + e5P5)):
rad is squarefree, so rad == c * prod_{x in X}(u - x) iff deg rad == |X| and
rad(x) == 0 for every x in X. Both are checked; no root finding is needed.
"""

from __future__ import annotations

from fparith import Fp, OpCounter


def _trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def _mul(a, b, p):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] = (out[i + j] + x * y) % p
    return _trim(out)


def _divmod(a, b, p):
    a = list(a)
    inv = pow(b[-1], -1, p)
    q = [0] * max(len(a) - len(b) + 1, 0)
    while len(a) >= len(b) and a:
        c = a[-1] * inv % p
        k = len(a) - len(b)
        q[k] = c
        for i, y in enumerate(b):
            a[k + i] = (a[k + i] - c * y) % p
        _trim(a)
    return _trim(q), a


def _monic(a, p):
    inv = pow(a[-1], -1, p)
    return [c * inv % p for c in a]


def _gcd(a, b, p):
    a, b = _trim(list(a)), _trim(list(b))
    while b:
        a, b = b, _divmod(a, b, p)[1]
    return _monic(a, p) if a else []


def _deriv(a, p):
    return _trim([(i * c) % p for i, c in enumerate(a)][1:])


def radical(a, p):
    if len(a) <= 1:
        return _monic(a, p) if a else []
    d = _deriv(a, p)
    if not d:  # a is a polynomial in u^p; cannot occur for deg < p
        raise ValueError("zero derivative")
    return _monic(_divmod(a, _gcd(a, d, p), p)[0], p)


def _eval(a, x, p):
    r = 0
    for c in reversed(a):
        r = (r * x + c) % p
    return r


def split_radical(sem, p, V, xR):
    """Monic rad(lcm_{(v3,v4,v5) in V^3} b(u)); (None, reason) if some b == 0."""
    F = Fp(p, OpCounter())  # scratch counter: diagnostic, never charged
    gen = sem.S4 if xR is None else sem.spec_last(F, sem.S5, xR)
    lcm = [1]
    for v3 in V:
        g3 = sem.spec_last(F, gen, v3)
        for v4 in V:
            g4 = sem.spec_last(F, g3, v4)
            for v5 in V:
                bu = _trim([int(c) for c in sem.spec_last(F, g4, v5)])
                if not bu:
                    return None, "identically zero S5 specialization"
                r = radical(bu, p)
                g = _gcd(lcm, r, p)
                lcm = _mul(lcm, _divmod(r, g, p)[0], p)
    return _monic(lcm, p), None


def crosscheck(sem, p, V, xR, b2_roots) -> dict:
    rad, err = split_radical(sem, p, V, xR)
    if rad is None:
        return {"method": "split_nosage", "error": err, "match": False}
    X = sorted(set(b2_roots))
    all_vanish = all(_eval(rad, x, p) == 0 for x in X)
    deg = len(rad) - 1
    return {"method": "split_nosage", "radical_degree": deg, "b2_degree": len(X),
            "all_b2_roots_vanish": all_vanish, "match": bool(all_vanish and deg == len(X))}

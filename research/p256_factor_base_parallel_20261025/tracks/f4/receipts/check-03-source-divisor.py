"""Exact genus-one principal divisors and signed partial relations over P-256.

Validation prototype. No sampler output is evidence of a yield advantage.
Coefficients are ascending; infinity is represented by None.
"""
from pathlib import Path
import importlib.util
import random
from math import comb
import sympy as sp
from flint import fmpz_mod_poly_ctx

PARAMETERS = Path(__file__).resolve().parents[2] / 'baseline' / 'parameters.py'
spec = importlib.util.spec_from_file_location('published_constants', PARAMETERS)
params = importlib.util.module_from_spec(spec)
spec.loader.exec_module(params)
C = next(c for c in params.CURVES if c['name'] == 'P-256')
p, a, b, r = (C[k] for k in ('p', 'a', 'b', 'r'))
g = [b % p, a % p, 0, 1]
x = sp.Symbol('x')
G = (int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296', 16),
     int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5', 16))


def trim(v):
    v = [int(t) % p for t in v]
    while len(v) > 1 and v[-1] == 0:
        v.pop()
    return v or [0]


def plus(u, v):
    return trim([(u[i] if i < len(u) else 0) + (v[i] if i < len(v) else 0)
                 for i in range(max(len(u), len(v)))])


def scale(u, c):
    return trim([c * z for z in u])


def times(u, v):
    out = [0] * (len(u) + len(v) - 1)
    for i, ui in enumerate(u):
        for j, vj in enumerate(v):
            out[i+j] += ui*vj
    return trim(out)


def evaluate(u, t):
    out = 0
    for c in reversed(u):
        out = (out*t+c) % p
    return out


def shifted(u, t, n):
    return [sum(c*comb(j, i)*pow(t, j-i, p) for j, c in enumerate(u) if j >= i) % p
            for i in range(n)]


def neg(P):
    return None if P is None else (P[0], -P[1] % p)


def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    X, Y = P
    U, V = Q
    if X == U:
        if (Y+V) % p == 0:
            return None
        slope = (3*X*X+a)*pow(2*Y, -1, p) % p
    else:
        slope = (V-Y)*pow(U-X, -1, p) % p
    Z = (slope*slope-X-U) % p
    return Z, (slope*(X-Z)-Y) % p


def mul(k, P=G):
    if k < 0:
        return mul(-k, neg(P))
    out = None
    while k:
        if k & 1:
            out = add(out, P)
        P = add(P, P)
        k >>= 1
    return out


def on_curve(P):
    return P is None or (P[1]*P[1]-evaluate(g, P[0])) % p == 0


def orbit(P):
    """x is a column id; its group representative has the smaller y."""
    assert P is not None and P[1] != 0
    return str(P[0]), 1 if P[1] <= p//2 else -1


def function_product(F, H):
    A, B = F
    D, E = H
    return plus(times(A, D), times(g, times(B, E))), plus(times(A, E), times(B, D))


def pole_order(F):
    A, B = map(trim, F)
    if A == [0] and B == [0]:
        raise ValueError('zero function has no divisor')
    return max(2*(len(A)-1) if A != [0] else -1,
               3+2*(len(B)-1) if B != [0] else -1)


def line(P, Q):
    if P == neg(Q):
        return [-P[0] % p, 1], [0]
    s = ((3*P[0]**2+a)*pow(2*P[1], -1, p) if P == Q else
         (Q[1]-P[1])*pow(Q[0]-P[0], -1, p)) % p
    return [(s*P[0]-P[1]) % p, -s % p], [1]


def parabola(points):
    """y-h(x), with h the quadratic interpolant through three points."""
    h = [0]
    for i, (xi, yi) in enumerate(points):
        numer, denom = [1], 1
        for j, (xj, _) in enumerate(points):
            if i != j:
                numer = times(numer, [-xj, 1])
                denom = denom*(xi-xj) % p
        h = plus(h, scale(numer, yi*pow(denom, -1, p)))
    return scale(h, -1), [1]


def local_order(A, B, X, Y, bound):
    """t=x-X is a uniformizer when Y!=0; check the full needed jet."""
    if Y == 0:
        raise NotImplementedError('ramified rational 2-torsion jet')
    n = bound+1
    coeff_g, coeff_A, coeff_B = (shifted(v, X, n) for v in (g, A, B))
    coeff_y = [Y]
    for j in range(1, n):
        z = coeff_g[j]-sum(coeff_y[i]*coeff_y[j-i] for i in range(1, j))
        coeff_y.append(z*pow(2*Y, -1, p) % p)
    for j in range(n):
        val = coeff_A[j]+sum(coeff_B[i]*coeff_y[j-i] for i in range(j+1))
        if val % p:
            return j
    raise ArithmeticError('valuation exceeded norm-root bound')


def divisor(F):
    """Factor norm; return complete rational zeros or explicit unresolved blocks.

    Extension-field prime divisors are retained by their norm factors. They are
    not silently converted to rational points, or accepted as base relations.
    """
    A, B = map(trim, F)
    m = pole_order((A, B))
    N = plus(times(A, A), scale(times(g, times(B, B)), -1))
    # SymPy 1.14.0's FLINT conversion raises TypeError at 256-bit factor_list;
    # call the same installed FLINT backend directly and retain every factor.
    poly = fmpz_mod_poly_ctx(p)(N)
    unit, factors = poly.factor()
    zeros, unresolved, certificate = [], [], []
    for q, e in factors:
        coeff = [int(c) % p for c in q]
        certificate.append({'coefficients': coeff, 'multiplicity': int(e), 'degree': q.degree()})
        if q.degree() != 1:
            unresolved.append({'norm_factor': coeff, 'exponent': int(e), 'degree': q.degree()})
            continue
        X = -coeff[0]*pow(coeff[1], -1, p) % p
        v = evaluate(g, X)
        if v == 0:
            raise NotImplementedError('rational 2-torsion unsupported')
        if pow(v, (p-1)//2, p) != 1:
            unresolved.append({'norm_factor': coeff, 'exponent': int(e), 'reason': 'nonsplit y'})
            continue
        Y = pow(v, (p+1)//4, p)
        count = 0
        for Yi in (min(Y, p-Y), max(Y, p-Y)):
            multiplicity = local_order(A, B, X, Yi, int(e))
            if multiplicity:
                zeros.append({'point': [X, Yi], 'multiplicity': multiplicity})
                count += multiplicity
        assert count == e
    rational_degree = sum(z['multiplicity'] for z in zeros)
    full = not unresolved and rational_degree == m
    row, inverse_pairs = {}, 0
    by_x = {}
    for z in zeros:
        key, sign = orbit(tuple(z['point']))
        row[key] = row.get(key, 0)+sign*z['multiplicity']
        by_x.setdefault(key, [0, 0])[sign < 0] += z['multiplicity']
    inverse_pairs = sum(min(u) for u in by_x.values())
    row = {k: v for k, v in row.items() if v}
    S = None
    if full:
        for z in zeros:
            S = add(S, mul(z['multiplicity'], tuple(z['point'])))
        assert S is None
    return {'A': A, 'B': B, 'pole_order': m, 'norm': N, 'norm_unit': int(unit) % p,
            'norm_factors': certificate, 'zeros': zeros, 'unresolved': unresolved,
            'fully_rational': full, 'rational_degree': rational_degree,
            'row': row, 'inverse_pairs': inverse_pairs, 'group_sum_infinity': full and S is None}


def rref(matrix, modulus):
    M = [[int(z) % modulus for z in row] for row in matrix]
    pivots, h = [], 0
    width = len(M[0]) if M else 0
    for j in range(width):
        at = next((i for i in range(h, len(M)) if M[i][j]), None)
        if at is None:
            continue
        M[h], M[at] = M[at], M[h]
        M[h] = [v*pow(M[h][j], -1, modulus) % modulus for v in M[h]]
        for i in range(len(M)):
            if i != h and M[i][j]:
                t = M[i][j]
                M[i] = [(v-t*w) % modulus for v, w in zip(M[i], M[h])]
        pivots.append(j)
        h += 1
        if h == len(M):
            break
    return M, pivots


def nullspace(M, width, modulus):
    R, pivots = rref(M, modulus)
    free = [j for j in range(width) if j not in pivots]
    basis = []
    for j in free:
        v = [0]*width
        v[j] = 1
        for i, pivot in enumerate(pivots):
            v[pivot] = -R[i][j] % modulus
        basis.append(v)
    return basis


def rr_basis(m):
    return [('A', i) for i in range(m//2+1)] + [('B', i) for i in range((m-3)//2+1)]


def conditioned_sampler(m, anchors, seed):
    """Uniform coefficient function conditioned on evaluations and exact pole.

    Draw free kernel coordinates uniformly via randrange(p), reject zero or
    lower-pole functions. This is a deterministic validation RNG, not secrets.
    Returns rejection count and evaluation rank; no hidden success filtering.
    """
    basis = rr_basis(m)
    evaluations = [[pow(P[0], i, p)*(1 if kind == 'A' else P[1]) % p
                    for kind, i in basis] for P in anchors]
    kernel = nullspace(evaluations, len(basis), p)
    if not kernel:
        raise ValueError('anchors leave no nonzero function')
    top = next(j for j, (kind, i) in enumerate(basis) if 2*i+(3 if kind == 'B' else 0) == m)
    if not any(v[top] for v in kernel):
        raise ValueError('anchors force lower pole')
    rng, rejected = random.Random(seed), 0
    while True:
        coeff = [0]*len(basis)
        for v in kernel:
            c = rng.randrange(p)
            coeff = [(z+c*w) % p for z, w in zip(coeff, v)]
        if coeff[top]:
            break
        rejected += 1
    A, B = [0]*(m//2+1), [0]*max(1, (m-3)//2+1)
    for z, (kind, i) in zip(coeff, basis):
        (A if kind == 'A' else B)[i] = z
    F = trim(A), trim(B)
    assert pole_order(F) == m
    assert all((evaluate(F[0], X)+Y*evaluate(F[1], X)) % p == 0 for X, Y in anchors)
    return F, {'m': m, 'basis': basis, 'anchors': [list(P) for P in anchors],
               'evaluation_rank': len(basis)-len(kernel), 'kernel_dimension': len(kernel),
               'seed': seed, 'lower_pole_rejections': rejected,
               'uniform_space': 'nonzero top-coefficient slice of evaluation kernel'}


def stitch(cases, base):
    """Kernel of signed outside incidence; retain coefficient witnesses.

    Vertices are inverse orbits of actual rational points. One endpoint uses
    the distinguished zero/hub vertex; signs and repeated endpoints matter.
    All arithmetic is modulo the subgroup order, not modulo the field prime.
    """
    rows = [c['row'] for c in cases]
    allcols = sorted(set().union(*(set(row) for row in rows)))
    outside = [k for k in allcols if k not in base]
    basecols = [k for k in allcols if k in base]
    D = [[row.get(k, 0) % r for k in allcols] for row in rows]
    incidence = [[row.get(k, 0) % r for row in rows] for k in outside]
    kernel = nullspace(incidence, len(rows), r)
    outputs = []
    for v in kernel:
        out = {k: sum(c*row.get(k, 0) for c, row in zip(v, rows)) % r for k in allcols}
        assert all(out[k] == 0 for k in outside)
        outputs.append({'combination': v, 'row': {k: out[k] for k in basecols if out[k]}})
    Bmat = [[row.get(k, 0) % r for k in basecols] for row in rows]
    final = [[o['row'].get(k, 0) for k in basecols] for o in outputs]
    return {'all_columns': allcols, 'base_columns': basecols, 'outside_columns': outside,
            'edges': [{'case': c['id'], 'outside': {k: c['row'].get(k, 0) for k in outside if c['row'].get(k, 0)},
                       'outside_degree': sum(k in outside for k in c['row'])} for c in cases],
            'input_rows': len(rows), 'rank_before_all_columns': len(rref(D, r)[1]),
            'rank_projected_base_before_cancellation': len(rref(Bmat, r)[1]),
            'outside_incidence_rank': len(rref(incidence, r)[1]), 'kernel_dimension': len(kernel),
            'cancelled_rows': outputs, 'rank_after_cancellation': len(rref(final, r)[1]),
            'zero_cancelled_rows': sum(not o['row'] for o in outputs),
            'dimension_identity_holds': len(rref(D, r)[1])-len(rref(incidence, r)[1]) == len(rref(final, r)[1])}

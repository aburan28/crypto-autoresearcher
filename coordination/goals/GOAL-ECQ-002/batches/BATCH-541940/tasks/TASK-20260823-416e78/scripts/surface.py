#!/usr/bin/env python3
"""
Elliptic-surface bookkeeping for a Mestre family over Q(T):
minimal Weierstrass model over Q[T], surface degree d, the fibre configuration
COMPUTED FROM THIS FAMILY'S OWN DISCRIMINANT, and the resulting Shioda-Tate
ceiling.

Why this exists (H-ECQ-8b600d assumption 3, BATCH-da59ec validator finding F1):
the generic elliptic-K3 bound 10d-2 = 18 assumes every fibre is irreducible.
It overstated Nagao's ceiling by 3 because an I_4 fibre at T = infinity was
never computed.  NO CEILING HERE IS TAKEN FROM THE GENERIC BOUND.

    rank MW(E/Qbar(T))  <=  h^{1,1} - 2 - sum_v (m_v - 1)
                        =   10d - 2 - sum_v (m_v - 1)

with m_v the number of components of the fibre at v, summed over ALL places of
P^1 including T = infinity, and each irreducible factor p(T) of degree D
contributing D geometric fibres.

Residue characteristic is 0 everywhere (the residue fields are number fields),
so the Kodaira type is read off (v(c4), v(c6), v(Delta)) by the classical
table with no wild-ramification correction.
"""
import math
from fractions import Fraction as F

import cypari

pari = cypari.pari


def _clear(polys):
    """Scale a list of Q[T]-polys by a common rational so all are integral."""
    den = 1
    for p in polys:
        for c in p:
            den = den * c.denominator // math.gcd(den, c.denominator)
    return den


def poly_str(c, var='T'):
    terms = [c[i] for i in range(len(c))]
    s = '+'.join('(%d)*%s^%d' % (int(x), var, i) for i, x in enumerate(terms) if x)
    return s if s else '0'


def _mul(*ps):
    out = [F(1)]
    for p in ps:
        n = [F(0)] * (len(out) + len(p) - 1)
        for i, a in enumerate(out):
            if a:
                for j, b in enumerate(p):
                    if b:
                        n[i + j] += a * b
        out = n
    return out


def _add(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
            for i in range(n)]


def _scal(a, c):
    return [x * F(c) for x in a]


def a4a6_over_QT(r_coeffs):
    """From the quartic r's x-coefficients (ascending T-polys e,d,c,b,a)
    return integral a4(T), a6(T) of  Y^2 = X^3 + a4 X + a6  (the Jacobian),
    as lists of ints."""
    e, d, c, b, a = r_coeffs
    I = _add(_add(_scal(_mul(a, e), 12), _mul(c, c)), _scal(_mul(b, d), -3))
    J = _add(_add(_add(_add(_scal(_mul(a, c, e), 72), _scal(_mul(b, c, d), 9)),
                       _scal(_mul(a, d, d), -27)), _scal(_mul(e, b, b), -27)),
             _scal(_mul(c, c, c), -2))
    a4 = _scal(I, -27)
    a6 = _scal(J, -27)
    u = _clear([a4, a6])
    a4 = [x * u ** 4 for x in a4]
    a6 = [x * u ** 6 for x in a6]
    return [int(x) for x in a4], [int(x) for x in a6]


def _val(fac, p):
    """v_p(F) given PARI factorisation matrix fac and a PARI irreducible p."""
    n = int(pari('matsize(%s)[1]' % fac))
    for i in range(1, n + 1):
        if int(pari('%s[%d,1] == %s' % (fac, i, p))):
            return int(pari('%s[%d,2]' % (fac, i)))
    return 0


def kodaira(A, B, N):
    """(v(a4), v(a6), v(Delta)) -> (type, m_v) in residue characteristic 0."""
    if N == 0:
        return 'I_0', 1
    if A == 0:
        return 'I_%d' % N, N
    if B == 1 and N == 2:
        return 'II', 1
    if A == 1 and N == 3:
        return 'III', 2
    if A >= 2 and B == 2 and N == 4:
        return 'IV', 3
    if A >= 2 and B >= 3 and N == 6:
        return 'I_0*', 5
    if A == 2 and B == 3 and N > 6:
        return 'I_%d*' % (N - 6), 5 + (N - 6)
    if A >= 3 and B == 4 and N == 8:
        return 'IV*', 7
    if A == 3 and B >= 5 and N == 9:
        return 'III*', 8
    if A >= 4 and B == 5 and N == 10:
        return 'II*', 9
    return 'UNCLASSIFIED(v4=%d,v6=%d,vD=%d)' % (A, B, N), None


def analyse(r_coeffs):
    """Full surface analysis.  Returns a dict; never raises on odd input."""
    out = {}
    a4, a6 = a4a6_over_QT(r_coeffs)
    s4, s6 = poly_str(a4), poly_str(a6)
    P4 = pari('P4 = %s' % s4)
    P6 = pari('P6 = %s' % s6)
    # --- minimalise over Q[T]: divide by p^4 | a4 and p^6 | a6 ---------
    removed = []
    while True:
        g = pari('g = gcd(P4, P6)')
        if int(pari('poldegree(g)')) <= 0:
            break
        fg = pari('fg = factor(g)')
        nf = int(pari('matsize(fg)[1]'))
        did = False
        for i in range(1, nf + 1):
            p = pari('fg[%d,1]' % i)
            if int(pari('poldegree(%s)' % p)) <= 0:
                continue
            v4 = _valpoly('P4', p)
            v6 = _valpoly('P6', p)
            k = min(v4 // 4, v6 // 6)
            if k >= 1:
                pari('P4 = P4 / (%s)^%d' % (p, 4 * k))
                pari('P6 = P6 / (%s)^%d' % (p, 6 * k))
                removed.append({'factor': str(p), 'k': k})
                did = True
                break
        if not did:
            break
    d4 = int(pari('poldegree(P4)'))
    d6 = int(pari('poldegree(P6)'))
    d = max(-(-d4 // 4), -(-d6 // 6))
    out['minimal_over_QT'] = {'deg_a4': d4, 'deg_a6': d6,
                              'removed_square_factors': removed}
    out['surface_degree_d'] = d
    out['forced_large_t_slope_12d'] = 12 * d
    pari('DD = -16*(4*P4^3 + 27*P6^2)')
    degD = int(pari('poldegree(DD)'))
    out['deg_discriminant'] = degD
    if int(pari('DD == 0')):
        out['degenerate'] = True
        return out
    out['degenerate'] = False
    fac = pari('fD = factor(DD)')
    nf = int(pari('matsize(fD)[1]'))
    fibres = []
    total = 0
    unclassified = 0
    for i in range(1, nf + 1):
        p = pari('fD[%d,1]' % i)
        dp = int(pari('poldegree(%s)' % p))
        if dp <= 0:
            continue
        N = int(pari('fD[%d,2]' % i))
        A = int(_valpoly('P4', p))
        B = int(_valpoly('P6', p))
        typ, m = kodaira(A, B, N)
        fibres.append({'place': str(p), 'deg': dp, 'v_a4': A, 'v_a6': B,
                       'v_disc': N, 'type': typ, 'm_v': m})
        if m is None:
            unclassified += 1
        else:
            total += dp * (m - 1)
    # --- the fibre at T = infinity ------------------------------------
    Ai = 4 * d - d4
    Bi = 6 * d - d6
    Ni = 12 * d - degD
    typ, m = kodaira(Ai, Bi, Ni)
    fibres.append({'place': 'infinity', 'deg': 1, 'v_a4': Ai, 'v_a6': Bi,
                   'v_disc': Ni, 'type': typ, 'm_v': m})
    if m is None:
        unclassified += 1
    else:
        total += (m - 1)
    out['fibres'] = fibres
    sdeg = sum(f['deg'] * f['v_disc'] for f in fibres)
    out['euler_number_check'] = {'sum_deg_times_v_disc_all_places': sdeg,
                                 'expected_12d': 12 * d, 'ok': sdeg == 12 * d}
    out['sum_m_v_minus_1'] = total
    out['n_unclassified_fibres'] = unclassified
    out['generic_K3_bound_NOT_USED'] = 10 * d - 2
    out['shioda_tate_ceiling'] = (10 * d - 2 - total) if unclassified == 0 else None
    out['shioda_tate_ceiling_note'] = (
        'rank MW(E/Qbar(T)) <= 10d-2-sum(m_v-1), computed from THIS family\'s '
        'own fibre configuration; rank over Q(T) is at most this.'
        if unclassified == 0 else
        'NOT REPORTED: %d fibre(s) could not be classified by the residue-'
        'characteristic-0 Kodaira table.' % unclassified)
    return out


def _valpoly(name, p):
    """v_p(name) for a PARI polynomial variable name and irreducible p."""
    return int(pari('valuation(%s, %s)' % (name, p)))

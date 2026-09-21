#!/usr/bin/env python3
"""
Quadratic-twist family search for high-rank elliptic curves over multiquadratic
fields.

Mathematical set-up
-------------------
Fix E : y^2 = x^3 + A x + B over Q and a finite set S of "support" classes
(primes, and optionally -1).  Write G_S <= Q*/(Q*)^2 for the F_2-vector space
they span.  For a subgroup V <= G_S of dimension k put

    K_V = Q( sqrt(d) : d in V ),      [K_V : Q] = 2^k.

For squarefree d the quadratic twist  E^(d) : v^2 = u^3 + A d^2 u + B d^3
maps into E(K_V) by

    phi_d(u, v) = ( u/d , (v/d^2) sqrt(d) ),

an injective group homomorphism whose image is a chi_d-eigenvector for
Gal(K_V/Q).  Hence

    rank E(K_V)  =  sum_{d in V} rank E^(d)(Q),

and, more importantly for certification, non-torsion points attached to
*distinct* classes d are automatically Z-independent (distinct eigenspaces of
an elementary abelian 2-group action) with no height computation at all.

Twisting the base curve by d0 replaces the family {E^(d) : d in V} by
{E^(d) : d in d0 V}, so scanning *affine* subspaces (cosets) of G_S is the same
as scanning all quadratic twists of the base curve as well as all subgroups.
That is what `optimise` does.

Two scores are reported per configuration:

  n_classes  number of classes d in the coset with at least one explicit
             non-torsion point.  Bounds rank E(K_V) from below with a purely
             algebraic (Galois-eigenspace) certificate: no numerics.
  sum_mult   sum over the coset of the number of independent points found.
             Bounds rank E(K_V) from below too, but points sharing a class need
             a height-regulator argument (see regulator_check.py).

Requires cypari (bundled PARI); ellrank supplies the descent and the points.
"""
import itertools
import cypari

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)

DEFAULT_SUPPORT = [-1, 2, 3, 5, 7, 11, 13]


def short_model(a_invariants):
    """Return (A, B) with y^2 = x^3 + A x + B isomorphic over Q to E(a_inv)."""
    E = pari('ellinit(%s)' % (list(a_invariants),))
    c4 = int(pari('%s.c4' % E))
    c6 = int(pari('%s.c6' % E))
    return -27 * c4, -54 * c6


def class_value(mask, support):
    """Squarefree integer represented by an F_2 bitmask over `support`."""
    d = 1
    for i, g in enumerate(support):
        if mask >> i & 1:
            d *= g
    return d


def twist_rank(A, B, d, time_limit=5):
    """(r_low, r_high, points) for E^(d) via PARI ellrank, guarded by alarm().

    On timeout returns (-1, -1, []): an infrastructure outcome, never evidence.
    """
    r = pari('iferr(alarm(%d,ellrank(ellinit([0,0,0,%d,%d]))),E,[-1,-1,0,[]])'
             % (time_limit, A * d * d, B * d * d * d))
    return int(r[0]), int(r[1]), [[str(c) for c in pt] for pt in r[3]]


def profile(a_invariants, support=DEFAULT_SUPPORT, time_limit=5):
    """Rank data for every class of G_S.  Index of the list is the bitmask."""
    A, B = short_model(a_invariants)
    out = []
    for mask in range(1 << len(support)):
        d = class_value(mask, support)
        rl, rh, pts = twist_rank(A, B, d, time_limit)
        out.append({'mask': mask, 'd': d, 'r_low': rl, 'r_high': rh,
                    'points': pts,
                    'certified': min(rl, len(pts)) if rl >= 0 else 0,
                    'timed_out': rl < 0})
    return (A, B), out


def subspaces(n, k):
    """All k-dimensional subspaces of F_2^n, each as its sorted list of masks.

    Enumerated once per (n, k) through reduced row echelon forms, so every
    subspace appears exactly once.
    """
    out = []
    for pivots in itertools.combinations(range(n), k):
        free = [j for j in range(n) if j not in pivots]
        slots = [[j for j in free if j > piv] for piv in pivots]
        grids = [list(itertools.product([0, 1], repeat=len(s))) for s in slots]
        for choice in itertools.product(*grids):
            basis = []
            for i, piv in enumerate(pivots):
                v = 1 << piv
                for bit, j in zip(choice[i], slots[i]):
                    if bit:
                        v |= 1 << j
                basis.append(v)
            span = [0]
            for b in basis:
                span += [x ^ b for x in span]
            out.append(sorted(span))
    return out


def affine_subspaces(n, k):
    """All cosets m0 + V of all k-dimensional V <= F_2^n, deduplicated."""
    out = []
    for V in subspaces(n, k):
        reps = {min(m ^ v for v in V) for m in range(1 << n)}
        for m0 in sorted(reps):
            out.append((m0, V))
    return out


def optimise(prof, support, k, index_cache=None):
    """Best coset of a k-dimensional subgroup, by both scores.

    Returns {'sum_mult': (score, m0, V), 'n_classes': (score, m0, V)}.
    """
    n = len(support)
    AS = index_cache if index_cache is not None else affine_subspaces(n, k)
    cert = [e['certified'] for e in prof]
    has = [1 if e['certified'] >= 1 else 0 for e in prof]
    best_m = (-1, None, None)
    best_c = (-1, None, None)
    for m0, V in AS:
        s1 = sum(cert[m0 ^ v] for v in V)
        s2 = sum(has[m0 ^ v] for v in V)
        if s1 > best_m[0]:
            best_m = (s1, m0, V)
        if s2 > best_c[0]:
            best_c = (s2, m0, V)
    return {'sum_mult': best_m, 'n_classes': best_c}

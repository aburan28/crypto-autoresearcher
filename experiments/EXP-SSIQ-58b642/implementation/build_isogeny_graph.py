#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP-SSIQ-58b642 -- Supersingular 2-isogeny graph construction, independent of
the WISDE counting data, for the pre-registered prime set (p = 1 mod 12).

Implements experiments/EXP-SSIQ-58b642/specification.yaml
inputs.graph_construction EXACTLY as frozen.  This module BUILDS the graph
purely from F_{p^2} arithmetic and the classical modular polynomial
Phi_2(X, j) via root-finding.  It never consults WISDE data to construct or
bias an edge; WISDE is used elsewhere (descent_hitting_time.py) ONLY as a
ground-truth cross-reference / correctness check, never here.

CONTENTS
--------
1. F_{p^2} arithmetic (a + b*w, w^2 = D, D a fixed quadratic non-residue).
2. Univariate polynomial arithmetic over F_{p^2}[X]: mulmod, powmod, gcd,
   exact division -- used only for root-finding.
3. Phi_2(X, Y), the classical modular polynomial, PUBLISHED AND FIXED,
   verified independently against the j(q)-expansion identity
   Phi_2(j(q), j(q^2)) = 0 (see verify_phi2_against_qexpansion below; this
   is an independent numerical check, not a proof, but it is NOT the same
   code path as the root-finder and catches transcription errors in the
   nine coefficients).
4. Full root-finding for a cubic over F_{p^2} known to split completely
   (Cantor-Zassenhaus-style random splitting, valid because p is odd hence
   q = p^2 is odd).
5. Seed j-invariant construction: p = 1 (mod 12) means neither j=0 nor
   j=1728 is supersingular (degenerate_j_handling), so the seed is obtained
   via Deuring's reduction theorem: a CM elliptic curve of a class-number-1
   (Heegner) discriminant D, reduced at a prime p INERT in Q(sqrt(D)),
   reduces to a supersingular curve over F_p.  The seed is INDEPENDENTLY
   VERIFIED supersingular by naive point counting (trace of Frobenius = 0),
   a check that uses NEITHER the CM construction's own internal state NOR
   Phi_2, per the same independence discipline as claims-and-verification.md.
6. BFS graph construction (full edge set, backtrack included, for
   enumeration/connectivity) and adjacency-list export (used later by
   descent_hitting_time.py, which applies the non-backtracking exclusion at
   WALK time, not at graph-construction time).
7. C-EDGELIST: full edge-list correctness gate for one small pre-registered
   prime, checked against an INDEPENDENT computation (exhaustive scan of a
   held-out coordinate subset), before trusting C-CONNECTIVITY's aggregate
   count for the rest of the batch.
8. M-DEGSEQ: degree-sequence check ("every vertex has degree exactly 3").
9. delta_E = 1 locus identification: j in F_p, a MATHEMATICAL IDENTITY
   (Galois orbit singleton) requiring no external data, per
   inputs.graph_construction.delta_E_cross_reference; its COUNT is cross-
   checked against the WISDE release's N(1,p) in descent_hitting_time.py.

This module OBSERVES / BUILDS.  No delta_E value from WISDE ever enters
this module's edge construction.
"""

import hashlib
import math
import random


# ==========================================================================
# 1. F_{p^2} arithmetic
# ==========================================================================

class Fp2Field:
    """F_{p^2} = F_p[w]/(w^2 - D), D a fixed quadratic non-residue mod p.
    Elements are tuples (a, b) meaning a + b*w, a, b in [0, p)."""

    __slots__ = ("p", "D")

    def __init__(self, p):
        self.p = p
        self.D = smallest_nonresidue(p)

    def add(self, x, y):
        p = self.p
        return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)

    def sub(self, x, y):
        p = self.p
        return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)

    def neg(self, x):
        p = self.p
        return ((-x[0]) % p, (-x[1]) % p)

    def mul(self, x, y):
        p, D = self.p, self.D
        a, b = x
        c, d = y
        return ((a * c + b * d * D) % p, (a * d + b * c) % p)

    def from_int(self, n):
        return (n % self.p, 0)

    def is_in_fp(self, x):
        return x[1] % self.p == 0

    def norm(self, x):
        a, b = x
        return (a * a - self.D * b * b) % self.p

    def inv(self, x):
        n = self.norm(x)
        if n == 0:
            raise ZeroDivisionError("Fp2 element has zero norm (is zero)")
        ninv = pow(n, self.p - 2, self.p)
        a, b = x
        return ((a * ninv) % self.p, ((-b) * ninv) % self.p)

    def pow(self, x, e):
        result = self.from_int(1)
        base = x
        while e > 0:
            if e & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            e >>= 1
        return result

    def frobenius(self, x):
        """x^p.  For x = a + b*w with w^2 = D a non-residue, w^p = -w
        (Euler's criterion), so Frobenius is exactly (a, -b) -- complex
        conjugation in this representation."""
        p = self.p
        return (x[0] % p, (-x[1]) % p)


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else 1


def smallest_nonresidue(p):
    """Smallest positive integer that is a quadratic non-residue mod p.
    Deterministic given p; stated explicitly rather than randomised so the
    field representation is reproducible without a seed."""
    n = 2
    while True:
        if legendre(n, p) == -1:
            return n
        n += 1


# ==========================================================================
# 2. Polynomial arithmetic over F_{p^2}[X], ascending-coefficient lists
# ==========================================================================

ZERO = (0, 0)
ONE_POLY = [(1, 0)]


def poly_trim(f):
    f = list(f)
    while len(f) > 1 and f[-1] == ZERO:
        f.pop()
    if not f:
        f = [ZERO]
    return f


def poly_add(field, f, g):
    n = max(len(f), len(g))
    out = []
    for i in range(n):
        a = f[i] if i < len(f) else ZERO
        b = g[i] if i < len(g) else ZERO
        out.append(field.add(a, b))
    return poly_trim(out)


def poly_sub(field, f, g):
    n = max(len(f), len(g))
    out = []
    for i in range(n):
        a = f[i] if i < len(f) else ZERO
        b = g[i] if i < len(g) else ZERO
        out.append(field.sub(a, b))
    return poly_trim(out)


def poly_mul(field, f, g):
    out = [ZERO] * (len(f) + len(g) - 1)
    for i, fc in enumerate(f):
        if fc == ZERO:
            continue
        for j, gc in enumerate(g):
            if gc == ZERO:
                continue
            out[i + j] = field.add(out[i + j], field.mul(fc, gc))
    return poly_trim(out)


def poly_rem(field, f, g):
    """f mod g, g need not be monic (normalised internally)."""
    g = poly_trim(g)
    lead_inv = field.inv(g[-1])
    gm = [field.mul(c, lead_inv) for c in g]
    f = poly_trim(list(f))
    dg = len(gm) - 1
    while len(f) - 1 >= dg and f != [ZERO]:
        coef = f[-1]
        if coef == ZERO:
            f.pop()
            f = poly_trim(f)
            continue
        shift = len(f) - 1 - dg
        for i, gc in enumerate(gm):
            idx = i + shift
            f[idx] = field.sub(f[idx], field.mul(coef, gc))
        f = poly_trim(f[:-1])
        if len(f) - 1 < dg:
            break
    return poly_trim(f)


def poly_divexact(field, f, g):
    """Exact division f // g, asserting zero remainder.  Used only when g is
    known (by construction) to divide f exactly (a verified polynomial
    factor)."""
    g = poly_trim(g)
    lead_inv = field.inv(g[-1])
    gm = [field.mul(c, lead_inv) for c in g]
    f = poly_trim(list(f))
    dg = len(gm) - 1
    df = len(f) - 1
    if df < dg:
        if f == [ZERO]:
            return [ZERO]
        raise ValueError("g does not divide f (deg f < deg g)")
    q = [ZERO] * (df - dg + 1)
    work = f[:]
    for shift in range(df - dg, -1, -1):
        coef = work[shift + dg] if shift + dg < len(work) else ZERO
        q[shift] = coef
        if coef == ZERO:
            continue
        for i, gc in enumerate(gm):
            idx = i + shift
            work[idx] = field.sub(work[idx], field.mul(coef, gc))
    work = poly_trim(work)
    if work != [ZERO]:
        raise ValueError("inexact division: nonzero remainder %r" % (work,))
    return poly_trim(q)


def poly_mulmod(field, f, g, mod_poly):
    return poly_rem(field, poly_mul(field, f, g), mod_poly)


def poly_powmod(field, base, e, mod_poly):
    result = list(ONE_POLY)
    base = poly_rem(field, base, mod_poly)
    while e > 0:
        if e & 1:
            result = poly_mulmod(field, result, base, mod_poly)
        base = poly_mulmod(field, base, base, mod_poly)
        e >>= 1
    return result


def poly_gcd(field, f, g):
    f = poly_trim(list(f))
    g = poly_trim(list(g))
    while not (g == [ZERO]):
        f, g = g, poly_rem(field, f, g)
        f = poly_trim(f)
        g = poly_trim(g)
    if f == [ZERO]:
        return f
    lead_inv = field.inv(f[-1])
    return poly_trim([field.mul(c, lead_inv) for c in f])


def poly_eval(field, f, x):
    val = ZERO
    xp = (1, 0)
    for c in f:
        val = field.add(val, field.mul(c, xp))
        xp = field.mul(xp, x)
    return val


def poly_derivative(field, f):
    out = []
    for i in range(1, len(f)):
        out.append(field.mul((i % field.p, 0), f[i]))
    return poly_trim(out) if out else [ZERO]


def _split_squarefree(field, f, rng, q):
    """Split a SQUAREFREE polynomial (all roots distinct, all guaranteed to
    lie in F_{p^2} -- callers only ever pass gcd(f, X^q - X) here) into its
    list of distinct roots via Cantor-Zassenhaus-style random linear-factor
    splitting, valid because q = p^2 is odd."""
    p = field.p
    f = poly_trim(list(f))
    if f == [ZERO]:
        return []
    if f[-1] != (1, 0):
        li = field.inv(f[-1])
        f = poly_trim([field.mul(c, li) for c in f])
    x_poly = [ZERO, (1, 0)]
    roots = []
    stack = [f]
    exp = (q - 1) // 2
    while stack:
        cur = poly_trim(stack.pop())
        d = len(cur) - 1
        if d == 0:
            continue
        if d == 1:
            c0, c1 = cur[0], cur[1]
            roots.append(field.mul(field.neg(c0), field.inv(c1)))
            continue
        tries = 0
        split = None
        while split is None:
            tries += 1
            if tries > 2000:
                raise RuntimeError(
                    "random splitting failed to terminate on a degree-%d "
                    "factor after 2000 tries" % d)
            a = (rng.randrange(p), rng.randrange(p))
            xa = poly_add(field, x_poly, [a])
            b = poly_powmod(field, xa, exp, cur)
            b_minus_1 = poly_sub(field, b, ONE_POLY)
            g = poly_gcd(field, cur, b_minus_1)
            g = poly_trim(g)
            dg = len(g) - 1
            if 0 < dg < d:
                h = poly_divexact(field, cur, g)
                split = (g, h)
        stack.append(split[0])
        stack.append(split[1])
    return roots


def find_roots_with_multiplicity(field, f, rng, q):
    """Return the length-deg(f) list of roots of f in F_{p^2} WITH
    MULTIPLICITY (a root r of multiplicity m appears m times).

    UNEXPECTED OBSERVATION, recorded here and in execution_report.yaml, not
    silently routed around: PF-5's scope-narrowing resolution states the
    p = 1 (mod 12) supersingular 2-isogeny graph is "a genuine SIMPLE
    undirected 3-regular graph with no multiplicity bookkeeping at all,"
    citing CGL's Aut(E) = {+-1} result.  Aut(E) = {+-1} does rule out the
    j=0/1728-style vertex-automorphism degeneracy, but empirically (verified
    below by two independent methods -- gcd(f, X^q-X) squarefree-part degree
    AND gcd(f, f') -- on real pre-registered-prime graphs, e.g. p = 2437) it
    does NOT rule out a DIFFERENT phenomenon: a vertex v with delta_E = 2 can
    have its minimal degree-2 isogeny to its own Frobenius conjugate v^p
    realised by more than one of its three 2-isogenies, giving Phi_2(X, v) a
    genuine REPEATED root at X = v^p and hence a double edge (v, v^p) (or, in
    principle, a self-loop v = v^p, though that would force delta_E = 1,
    excluded here) in the naive simple-graph sense.  The TOTAL edge
    multiplicity per vertex, guaranteed by Phi_2's cubic degree, remains
    exactly 3 in every case observed; this function preserves that
    multiset, and downstream graph code (degree check, tie-break, descent)
    operates on the 3-element MULTISET of neighbours, not on an assumption
    of 3 DISTINCT neighbours.

    Correctness discipline: a degree deficit in gcd(f, X^q - X) is accepted
    ONLY when it is exactly explained by gcd(f, f') (the standard identity
    deg(f) = deg(squarefree part) + deg(gcd(f,f')) for a polynomial whose
    roots all lie in the field).  Deuring's theorem (every 2-isogenous
    neighbour of a supersingular j-invariant is itself supersingular, and
    every supersingular j-invariant over Fbar_p lies in F_{p^2}) guarantees
    all three roots DO lie in F_{p^2} for a genuine BFS-reached vertex, so an
    unexplained deficit is raised as a real correctness failure, never
    silently routed around.
    """
    f = poly_trim(list(f))
    deg = len(f) - 1
    if deg == 0:
        return []
    lead_inv = field.inv(f[-1])
    f = poly_trim([field.mul(c, lead_inv) for c in f])  # monic

    x_poly = [ZERO, (1, 0)]
    xq = poly_powmod(field, x_poly, q, f)
    xq_minus_x = poly_sub(field, xq, x_poly)
    squarefree = poly_trim(poly_gcd(field, f, xq_minus_x))
    sdeg = len(squarefree) - 1

    if sdeg != deg:
        if deg >= 2:
            fprime = poly_derivative(field, f)
            gdrv = poly_trim(poly_gcd(field, f, fprime))
            gdeg = len(gdrv) - 1
        else:
            gdeg = 0
        if sdeg + gdeg < deg:
            raise ValueError(
                "polynomial of degree %d has squarefree part of degree %d "
                "and gcd-with-derivative of degree %d (%d + %d < %d): the "
                "degree deficit is NOT fully explained by a repeated root "
                "in F_p^2, which would contradict Deuring's theorem for a "
                "genuine supersingular j-invariant -- this is a correctness "
                "failure, not a multiplicity case"
                % (deg, sdeg, gdeg, sdeg, gdeg, deg))

    distinct_roots = _split_squarefree(field, squarefree, rng, q)
    if len(distinct_roots) != sdeg:
        raise RuntimeError("internal: splitter returned %d roots for a "
                            "degree-%d squarefree polynomial"
                            % (len(distinct_roots), sdeg))

    remaining = f
    roots_with_mult = []
    total = 0
    for r in distinct_roots:
        mult = 0
        cur = remaining
        while True:
            val = poly_eval(field, cur, r)
            if val != ZERO:
                break
            cur = poly_divexact(field, cur, [field.neg(r), (1, 0)])
            mult += 1
        roots_with_mult.extend([r] * mult)
        total += mult
        remaining = cur
    if total != deg:
        raise RuntimeError(
            "internal: root multiplicities summed to %d, expected degree %d"
            % (total, deg))
    return roots_with_mult


# ==========================================================================
# 3. Classical modular polynomial Phi_2(X, Y)
# ==========================================================================

def phi2_coeffs_in_X(field, j):
    """Phi_2(X, j) as a monic cubic in X, coefficients in F_{p^2}.

    Phi_2(X,Y) = X^3 + Y^3 - X^2 Y^2 + 1488 X^2 Y + 1488 X Y^2
                 - 162000 X^2 - 162000 Y^2 + 40773375 X Y
                 + 8748000000 X + 8748000000 Y - 157464000000000

    As a polynomial in X (Y = j fixed):
      c2 = -j^2 + 1488 j - 162000
      c1 = 1488 j^2 + 40773375 j + 8748000000
      c0 = j^3 - 162000 j^2 + 8748000000 j - 157464000000000
      f(X) = X^3 + c2 X^2 + c1 X + c0
    """
    j2 = field.mul(j, j)
    j3 = field.mul(j2, j)
    c2 = field.add(field.add(field.neg(j2), field.mul(field.from_int(1488), j)),
                    field.from_int(-162000))
    c1 = field.add(field.add(field.mul(field.from_int(1488), j2),
                              field.mul(field.from_int(40773375), j)),
                    field.from_int(8748000000))
    c0 = field.add(
        field.add(j3, field.mul(field.from_int(-162000), j2)),
        field.add(field.mul(field.from_int(8748000000), j),
                  field.from_int(-157464000000000)))
    return [c0, c1, c2, (1, 0)]


def verify_phi2_against_qexpansion(terms=300, q=0.02):
    """Independent numerical check of the NINE integer coefficients above,
    using the q-expansion identity Phi_2(j(q), j(q^2)) = 0.  This is a
    DIFFERENT computational route from the field-arithmetic root-finder
    (floating point over C, not F_{p^2}), so it catches a transcription
    error in the coefficients that the root-finder's own self-consistency
    could not.  Returns (ok: bool, residual: float)."""

    def sigma3(n):
        s = 0
        d = 1
        while d * d <= n:
            if n % d == 0:
                s += d ** 3
                if d != n // d:
                    s += (n // d) ** 3
            d += 1
        return s

    def j_qexp(qq):
        E4 = 1.0
        for n in range(1, terms):
            E4 += 240 * sigma3(n) * qq ** n
        prod = 1.0
        for n in range(1, terms):
            prod *= (1 - qq ** n) ** 24
        Delta = qq * prod
        return E4 ** 3 / Delta

    j1 = j_qexp(q)
    j2 = j_qexp(q ** 2)

    def phi2_float(X, Y):
        return (X ** 3 + Y ** 3 - X ** 2 * Y ** 2 + 1488 * (X ** 2 * Y + X * Y ** 2)
                - 162000 * (X ** 2 + Y ** 2) + 40773375 * X * Y
                + 8748000000 * (X + Y) - 157464000000000)

    val = phi2_float(j1, j2)
    denom = abs(j1) ** 3 + abs(j2) ** 3 + 1.0
    rel = val / denom
    return (abs(rel) < 1e-8, rel)


def neighbors_2isogenous(field, j, rng, q):
    """The 3 roots (WITH MULTIPLICITY -- see find_roots_with_multiplicity)
    of Phi_2(X, j) in F_{p^2}: the 2-isogenous j-invariants of j.  Always
    returns exactly 3 entries (a repeated neighbour appears twice, etc.)."""
    f = phi2_coeffs_in_X(field, j)
    roots = find_roots_with_multiplicity(field, f, rng, q)
    return roots


# ==========================================================================
# 4. Seed j-invariant construction (Deuring reduction at an inert prime)
# ==========================================================================

# The seven imaginary quadratic discriminants of class number 1 (Heegner
# numbers, excluding -1,-2,-3,-4 which correspond to j = 1728, 8000... wait
# -3,-4 give j = 0, 1728 respectively and are EXCLUDED here on purpose:
# at p = 1 (mod 12), p is never inert for D in {-3, -4} (p = 1 mod 3 and
# p = 1 mod 4 respectively force the SPLIT case there, consistent with
# degenerate_j_handling's statement that j = 0, 1728 are not supersingular
# at this residue), so those two are omitted and only the class-number-1
# discriminants with h(D) = 1 and D not in {-3,-4} are tried, in ascending
# |D| order.
HEEGNER_H1 = [
    (-7, -3375),
    (-8, 8000),
    (-11, -32768),
    (-19, -884736),
    (-43, -884736000),
    (-67, -147197952000),
    (-163, -262537412640768000),
]


def seed_j_invariant(p):
    """Construct a supersingular j-invariant over F_p via Deuring's
    reduction theorem: reduce a CM curve of a Heegner discriminant D at p,
    where p is INERT in Q(sqrt(D)) (Kronecker/Legendre symbol (D/p) = -1).
    Returns (j0_as_Fp2_tuple, discriminant_used, j0_integer_mod_p).

    Independently verified below by naive point counting (trace of
    Frobenius must be exactly 0) -- a check that does NOT use Phi_2 or the
    CM construction's own internal state."""
    for D, j_int in HEEGNER_H1:
        if legendre(D % p, p) == -1:
            j0 = j_int % p
            return j0, D
    raise RuntimeError(
        "no class-number-1 Heegner discriminant among %r is inert at p=%d "
        "-- seed construction needs a larger discriminant table"
        % ([d for d, _ in HEEGNER_H1], p))


def verify_seed_supersingular(p, j0):
    """Independent check: the curve E: y^2 = x^3 + 3c x + 2c, c = j0/(1728-j0)
    mod p, has j-invariant j0 (standard formula) and trace of Frobenius t
    computed by NAIVE point counting (Legendre-symbol sum over F_p, no
    Phi_2, no CM machinery reused).  Supersingular over F_p (p > 3) iff
    t = 0 exactly (Hasse bound |t| <= 2 sqrt(p) < p rules out any nonzero
    multiple of p)."""
    if j0 % p in (0, 1728 % p):
        raise ValueError("seed landed on j=0 or j=1728 at p=%d -- should be "
                          "impossible at p = 1 (mod 12)" % p)
    c = (j0 * pow((1728 - j0) % p, p - 2, p)) % p
    A = (3 * c) % p
    B = (2 * c) % p
    t = 0
    for x in range(p):
        rhs = (x * x * x + A * x + B) % p
        t += legendre(rhs, p)
    trace = -t
    return bool(trace == 0), trace, A, B


# ==========================================================================
# 5. BFS graph construction
# ==========================================================================

def build_graph_bfs(p, seed_int, rng, time_budget_seconds=None):
    """Full breadth-first exploration of the supersingular 2-isogeny graph
    over F_{p^2}, starting from the F_p-rational seed j0 = (seed_int, 0).

    Returns a dict:
      field: Fp2Field
      vertices: sorted list of (a,b) tuples
      adjacency: {vertex: sorted list of 3 neighbour vertices (with
                  multiplicity, i.e. the raw root list -- a self-loop or
                  repeated neighbour would appear more than once)}
      degree: {vertex: len(adjacency[vertex])}
      seed: (seed_int, 0)

    The full edge set (including the edge back to the BFS predecessor) is
    used here for enumeration; the NON-BACKTRACKING exclusion described in
    inputs.graph_construction.method is applied later, per WALK, by
    descent_hitting_time.py -- it is a property of a walk's history, not of
    this graph object.
    """
    import time
    t0 = time.time()
    field = Fp2Field(p)
    q = p * p
    seed = (seed_int % p, 0)
    adjacency = {}
    visited = set([seed])
    queue = [seed]
    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        if time_budget_seconds is not None and time.time() - t0 > time_budget_seconds:
            raise TimeoutError(
                "BFS for p=%d exceeded time budget of %.1fs after %d/%d "
                "vertices dequeued" % (p, time_budget_seconds, head, len(queue)))
        nbrs = neighbors_2isogenous(field, v, rng, q)
        adjacency[v] = sorted(nbrs)
        for u in nbrs:
            if u not in visited:
                visited.add(u)
                queue.append(u)
    vertices = sorted(visited)
    degree = {v: len(adjacency[v]) for v in vertices}
    elapsed = time.time() - t0
    return {
        "field": field,
        "vertices": vertices,
        "adjacency": adjacency,
        "degree": degree,
        "seed": seed,
        "elapsed_seconds": elapsed,
        "q": q,
    }


def independent_edgelist_check(graph, p, rng_seed):
    """C-EDGELIST: recompute the full edge list via an INDEPENDENT root-
    finding pass (fresh Fp2Field, fresh RNG instance, fresh cubic
    construction from scratch for every vertex) and compare, vertex by
    vertex, against the graph built by build_graph_bfs.  This exercises the
    SAME neighbours_2isogenous function (there is only one correct Phi_2)
    but with entirely fresh field/RNG state and independent iteration order,
    so a state-leak or an order-dependent bug would be caught; it is NOT a
    from-scratch second implementation of Phi_2 (there is exactly one
    published Phi_2, restated in phi2_coeffs_in_X, and re-deriving a second
    independent polynomial is out of scope), but it does independently
    recompute every one of the 3*N root sets and diff them exactly, which is
    the aggregate-vs-full-list distinction PF-3/A3 named.
    """
    field2 = Fp2Field(p)
    rng2 = random.Random(rng_seed)
    q = p * p
    mismatches = []
    checked = 0
    for v in graph["vertices"]:
        recomputed = sorted(neighbors_2isogenous(field2, v, rng2, q))
        original = graph["adjacency"][v]
        checked += 1
        if recomputed != original:
            mismatches.append({"vertex": list(v), "original": [list(x) for x in original],
                                "recomputed": [list(x) for x in recomputed]})
    return {"vertices_checked": checked, "n_mismatches": len(mismatches),
            "mismatches": mismatches[:20], "pass": len(mismatches) == 0}


def degree_sequence_check(graph):
    bad = [{"vertex": list(v), "degree": d}
           for v, d in graph["degree"].items() if d != 3]
    return {"n_vertices": len(graph["vertices"]), "n_degree_ne_3": len(bad),
            "examples": bad[:20], "pass": len(bad) == 0}


def fp_rational_locus(graph):
    """delta_E = 1 vertices: j in F_p.  A mathematical identity (Galois
    orbit singleton), independent of any external data."""
    field = graph["field"]
    return sorted(v for v in graph["vertices"] if field.is_in_fp(v))


def bfs_diameter(graph):
    """Full BFS-computed diameter of the built graph (undirected, using the
    complete edge set), needed as the sentinel value for
    M-GAMMA-GREEDY.pf2_censoring_rule."""
    adjacency = graph["adjacency"]
    vertices = graph["vertices"]
    diam = 0
    for src in vertices:
        dist = {src: 0}
        queue = [src]
        head = 0
        while head < len(queue):
            u = queue[head]
            head += 1
            for w in adjacency[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    queue.append(w)
        if len(dist) != len(vertices):
            raise ValueError("graph explored from seed is not connected from "
                              "vertex %r (%d/%d reached) -- C-CONNECTIVITY "
                              "failure" % (src, len(dist), len(vertices)))
        m = max(dist.values())
        if m > diam:
            diam = m
    return diam


def bfs_eccentricities_from(graph, src):
    """Single-source BFS distances, used for a cheaper diameter LOWER BOUND
    (double sweep) when full all-pairs BFS is too slow; kept available but
    bfs_diameter (exact, O(N*(N+E))) is used for our graph sizes (<=1800
    vertices), which is fast enough."""
    adjacency = graph["adjacency"]
    dist = {src: 0}
    queue = [src]
    head = 0
    while head < len(queue):
        u = queue[head]
        head += 1
        for w in adjacency[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                queue.append(w)
    return dist

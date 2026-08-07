"""
isogeny.py -- rational ell-isogeny kernel finding and Velu's formula, used to walk
an ordinary F_p isogeny class (BFS over ell in {2,3,5,7}).

Method (documented scoping decision -- see MANIFEST.md "isogeny walk scope"):
  For a Galois-stable kernel subgroup S of order ell (ell prime) to give an
  F_p-rational isogeny, S must be fixed setwise by Frobenius. We restrict this
  driver's walk to the subcase where Frobenius acts as -1 on S (equivalently: some/
  every nonzero point P in S has x(P) individually F_p-rational, i.e. x(P) is a root
  of the ell-torsion polynomial IN F_p). This is a genuine, common case (NOT the only
  rational-kernel case -- Frobenius could also act as another unit of
  (Z/ellZ)*/{+-1}, giving kernels whose x-coordinates only live in F_{p^2} in an
  irreducible pair/triple -- those are NOT constructed by this driver). The
  consequence is a possible UNDER-count of isogeny neighbors (BFS may find fewer
  edges than the true rational ell-isogeny graph), never an OVER-count: every curve
  this driver adds to a class is verified independently (curve.find order-preserving
  check below), so a restricted kernel search can only make class construction
  slower / occasionally fail to reach the required size, not produce a wrong curve.

Velu's formulas (odd ell, kernel representatives R = {x(P): P in S, one per +-pair}):
  t_Q = 6 x_Q^2 + 2a ,  u_Q = 4(x_Q^3 + a x_Q + b)
  t = sum_Q t_Q ,  w = sum_Q (u_Q + x_Q t_Q)
  A' = a - 5t ,  B' = b - 7w
For ell=2 (kernel = {O, T}, T the unique 2-torsion representative):
  t_Q = 3 x_Q^2 + a ,  u_Q = 0 ,  t = t_Q ,  w = x_Q t_Q
  A' = a - 5t ,  B' = b - 7w
"""
from . import fp, divpoly, semaev, curve


def _degree(poly):
    d = len(poly) - 1
    while d > 0 and poly[d] == 0:
        d -= 1
    return d


def find_all_roots(poly, p, rng, _depth=0):
    """All distinct roots in F_p of a polynomial known (by construction, in this
    driver) to split completely into linear and/or irreducible-non-linear factors;
    returns only the F_p-RATIONAL roots (i.e. splits off the linear part first via
    gcd with x^p-x, then finds each root of that linear part via Cantor-Zassenhaus
    equal-degree splitting)."""
    poly = divpoly._trim(list(poly), p)
    if poly == [0]:
        return []
    deg = _degree(poly)
    if deg == 0:
        return []
    # isolate the product of all *linear* factors: gcd(poly, x^p - x)
    xp = divpoly.pmod_pow([0, 1], p, poly, p)
    xp_minus_x = divpoly.psub(xp, [0, 1], p)
    lin_part = divpoly.pgcd(poly, xp_minus_x, p)
    return _cz_roots(lin_part, p, rng)


def _cz_roots(poly, p, rng):
    poly = divpoly._trim(list(poly), p)
    deg = _degree(poly)
    if deg <= 0:
        return []
    if deg == 1:
        # poly = c1*x + c0 (monic after trim's leading nonzero, but not necessarily
        # normalized) -> root = -c0/c1
        c0, c1 = poly[0], poly[1]
        return [(-c0 * fp.inv(c1, p)) % p]
    # random split via (x+c)^((p-1)/2) - 1
    for _ in range(2000):
        c = rng.randrange(p)
        shifted = divpoly.pmod_pow([c, 1], (p - 1) // 2, poly, p)
        h = divpoly.psub(shifted, [1], p)
        d = divpoly.pgcd(poly, h, p)
        dd = _degree(d)
        if 0 < dd < deg:
            q, r = divpoly.pdivmod(poly, d, p)
            assert r == [0] or r == [], "exact split expected"
            return _cz_roots(d, p, rng) + _cz_roots(q, p, rng)
    raise RuntimeError("Cantor-Zassenhaus root splitting did not terminate (unexpected)")


def kernel_representative_sets(ell, a, b, p, rng):
    """Return a list of frozensets, each the set of representative x-coordinates of
    one rational (Frobenius-acts-as -1) order-ell kernel subgroup found on E."""
    a %= p; b %= p
    if ell == 2:
        poly = [b, a, 0, 1]
        roots = find_all_roots(poly, p, rng)
        return [frozenset([r]) for r in roots]
    d = (ell - 1) // 2
    poly = divpoly.torsion_poly(ell, a, b, p)
    roots = find_all_roots(poly, p, rng)
    root_set = set(roots)
    used = set()
    reps = []
    for r in roots:
        if r in used:
            continue
        try:
            mult = semaev.x_multiples(r, a, b, p, d)
        except ZeroDivisionError:
            used.add(r)
            continue
        vals = set(mult.values())
        if not vals.issubset(root_set):
            # inconsistent with our theory of this root -- skip, do not fabricate
            used.add(r)
            continue
        if len(vals) != d:
            used.add(r)
            continue
        used |= vals
        reps.append(frozenset(vals))
    return reps


def velu_codomain(a, b, p, kernel_rep, ell):
    a %= p; b %= p
    t_sum = 0
    w_sum = 0
    for xq in kernel_rep:
        xq %= p
        if ell == 2:
            tq = (3 * xq * xq + a) % p
            uq = 0
        else:
            tq = (6 * xq * xq + 2 * a) % p
            uq = (4 * (xq ** 3 + a * xq + b)) % p
        t_sum = (t_sum + tq) % p
        w_sum = (w_sum + uq + xq * tq) % p
    Ap = (a - 5 * t_sum) % p
    Bp = (b - 7 * w_sum) % p
    return Ap, Bp


def verify_order_preserved(a2, b2, p, N, rng, trials=3):
    """Independent check: is #E'(F_p) == N? (necessary sanity check on the Velu
    output, using cheap membership tests rather than recomputing order from scratch;
    since N is prime, N*P=O for EVERY point iff #E'(F_p)==N.)"""
    if (4 * a2 ** 3 + 27 * b2 * b2) % p == 0:
        return False  # singular -- reject
    for _ in range(trials):
        P = curve.random_point(a2, b2, p, rng)
        if curve.scalar_mul(N, P, a2, p) is not None:
            return False
    return True


def neighbors(a, b, p, N, rng, ells=(2, 3, 5, 7)):
    """Return list of (ell, a2, b2) verified isogenous curves reachable from (a,b)
    via a rational ell-isogeny (restricted kernel construction described above),
    each independently verified to have order exactly N."""
    out = []
    for ell in ells:
        try:
            reps = kernel_representative_sets(ell, a, b, p, rng)
        except Exception:
            continue
        for rep in reps:
            a2, b2 = velu_codomain(a, b, p, rep, ell)
            if verify_order_preserved(a2, b2, p, N, rng, trials=3):
                out.append((ell, a2 % p, b2 % p))
    return out

"""Point-level measurement: does the predicted x-coordinate orbit structure
actually deliver a Frobenius reduction on a real Gaudry/Diem factor base?

Object:  E defined over F_q, attacked over F_{q^n}.  Then pi(x, y) = (x^q, y^q)
         is an endomorphism of E, so F_V = {P in E(F_{q^n}) : x(P) in V} is
         pi-stable exactly when V is sigma-stable.
Control: V' a random F_q-subspace of the same dimension that is NOT sigma-stable
         -- F_{V'} must then fail to be pi-stable.
Null:    E' defined over F_{q^n} but over no proper subfield.  pi carries E' to a
         different curve, so no pi-action on its factor base exists at all.

The prediction under test is NOT that the point-level reduction equals the
x-level one.  pi^k can fix x(P) while sending y to -y, so a point orbit is as
long as its x-orbit or exactly twice as long.  The measurement records which.
"""
from sage.all import EllipticCurve, GF, Matrix, PolynomialRing, set_random_seed


def env(q, n):
    k = GF(q, 'b')
    K = k.extension(n, 'a')
    Vs, from_V, to_V = K.vector_space(k, map=True)
    sigma = Matrix(k, [to_V(from_V(e) ** q) for e in Vs.basis()]).transpose()
    return dict(k=k, K=K, Vs=Vs, from_V=from_V, to_V=to_V, sigma=sigma, q=q, n=n)


def ordinary_subfield_curves(k, limit=2):
    """Ordinary curves defined over the base field F_q."""
    p, out = k.characteristic(), []
    els = list(k)
    cands = []
    if p == 2:
        cands = [(1, a2, 0, 0, a6) for a2 in els for a6 in els if a6]
    elif p == 3:
        cands = [(0, a2, 0, 0, a6) for a2 in els for a6 in els if a2 and a6]
    else:
        cands = [(0, 0, 0, a, b) for a in els for b in els if 4 * a ** 3 + 27 * b ** 2]
    seen_j = set()
    for ai in cands:
        try:
            E = EllipticCurve(k, list(ai))
        except Exception:
            continue
        if E.trace_of_frobenius() % p == 0:      # supersingular -- excluded
            continue
        j = E.j_invariant()
        if j in seen_j:
            continue
        seen_j.add(j)
        out.append(E)
        if len(out) >= limit:
            break
    return out


def non_subfield_curve(K, k, seed=0):
    """A curve over F_{q^n} whose j-invariant lies in no proper subfield."""
    set_random_seed(seed)
    p = K.characteristic()
    for _ in range(4000):
        if p == 2:
            a2, a6 = K.random_element(), K.random_element()
            if not a6:
                continue
            E = EllipticCurve(K, [1, a2, 0, 0, a6])
        elif p == 3:
            a2, a6 = K.random_element(), K.random_element()
            if not (a2 and a6):
                continue
            E = EllipticCurve(K, [0, a2, 0, 0, a6])
        else:
            a, b = K.random_element(), K.random_element()
            if not (4 * a ** 3 + 27 * b ** 2):
                continue
            E = EllipticCurve(K, [a, b])
        j = E.j_invariant()
        q = k.cardinality()
        if j ** q != j and E.trace_of_frobenius() % p != 0:
            return E
    raise RuntimeError("no non-subfield ordinary curve found")


def stable_subspace(e, dim):
    """A sigma-stable subspace of the requested dimension, or None."""
    Vs, sigma, n = e["Vs"], e["sigma"], e["n"]
    for v in Vs:
        gens, w = [], v
        for _ in range(n):
            gens.append(w)
            w = sigma * w
        S = Vs.subspace(gens)
        if S.dimension() == dim:
            return S
    return None


def random_unstable_subspace(e, dim, seed=0):
    """A subspace of the requested dimension that is NOT sigma-stable."""
    set_random_seed(seed)
    Vs, sigma = e["Vs"], e["sigma"]
    for _ in range(5000):
        S = Vs.subspace([Vs.random_element() for _ in range(dim)])
        if S.dimension() != dim:
            continue
        if not all(sigma * b in S for b in S.basis()):
            return S
    return None


def factor_base(EK, e, S):
    """F_V = {P in E(F_{q^n}) : x(P) in V}."""
    from_V = e["from_V"]
    pts = []
    for v in S:
        x = from_V(v)
        try:
            pts.extend(EK.lift_x(x, all=True))
        except (ValueError, TypeError):
            continue
    return pts


def pi_orbits(EK, pts, q):
    """Orbits of P -> (x^q, y^q); (orbits, is_stable). None if not pi-stable."""
    S = set(pts)
    def pi(P):
        return EK(P[0] ** q, P[1] ** q)
    for P in pts:
        try:
            if pi(P) not in S:
                return None, False
        except Exception:
            return None, False
    seen, orbits = set(), []
    for P in pts:
        if P in seen:
            continue
        orb, Q = [], P
        while True:
            orb.append(Q)
            seen.add(Q)
            Q = pi(Q)
            if Q == P:
                break
        orbits.append(len(orb))
    return orbits, True

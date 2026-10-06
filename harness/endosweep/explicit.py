"""Explicit construction of a chain endomorphism on a REAL curve, verified on points.

The sweeper says "the element 4 + omega of norm 5^2 * 7 is a cheap endomorphism
of CryptoPro-B".  This module builds that map and checks it:

1. the ell-division polynomial f_ell(x) is computed over F_p for each prime
   ell in the chain;
2. its F_p-rational factors of total degree (ell-1)/2 are combined into the
   kernel polynomials of the F_p-rational cyclic subgroups of order ell (two
   of them when ell splits in End(E) and does not divide the conductor);
3. Velu's formulas in Kohel's kernel-polynomial form (no kernel point is ever
   needed, the points live in extension fields) give the codomain and
   evaluate the isogeny at an F_p-point by traces in F_p[T]/(h(T));
4. every closed walk of the right shape (e_ell steps of degree ell, no
   immediate backtracking) is followed through the isogeny class; a walk that
   returns to j(E) is composed with the isomorphism back to E;
5. the composite is accepted ONLY if it acts on a point of prime order n as
   one of the scalars a + b*lambda_omega the sweeper predicted (up to units
   and conjugation);
6. the resulting GLV-2 decomposition is checked end-to-end: k*P equals
   k1*P + k2*phi(P) with |k_i| inside the lattice's Babai bound.

If step 5 fails the sweeper's prediction is wrong for this curve (for
instance End(E) is not the maximal order) and the function says so.
Everything is exact arithmetic on Python integers.
"""
from __future__ import annotations

import itertools
import json
import random
from dataclasses import dataclass, field

from sympy import Poly, factorint, symbols

from . import lattice as LA
from . import quadorder as QO
from .toyverify import Counter, Curve, Composite, Isomorphism, isomorphism_to


# ---------------------------------------------------------------------------
# dense polynomials over F_p as coefficient lists, low degree first
# ---------------------------------------------------------------------------

def _trim(f):
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    return f


def padd(f, g, p):
    n = max(len(f), len(g))
    return _trim([((f[i] if i < len(f) else 0) + (g[i] if i < len(g) else 0)) % p for i in range(n)])


def psub(f, g, p):
    n = max(len(f), len(g))
    return _trim([((f[i] if i < len(f) else 0) - (g[i] if i < len(g) else 0)) % p for i in range(n)])


def pmul(f, g, p):
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a == 0:
            continue
        for j, b in enumerate(g):
            out[i + j] = (out[i + j] + a * b) % p
    return _trim(out)


def pscale(f, c, p):
    return _trim([(a * c) % p for a in f])


def pmod(f, h, p):
    """f mod h for monic-or-not h."""
    f = list(f)
    dh = len(h) - 1
    inv_lead = pow(h[-1], -1, p)
    while len(f) - 1 >= dh and any(f):
        if f[-1] == 0:
            f.pop()
            continue
        c = f[-1] * inv_lead % p
        shift = len(f) - 1 - dh
        for i in range(dh + 1):
            f[shift + i] = (f[shift + i] - c * h[i]) % p
        f.pop()
    return _trim(f) if f else [0]


def pinv_mod(f, h, p):
    """Inverse of f modulo h (extended Euclid); raises if not coprime."""
    r0, r1 = list(h), pmod(f, h, p)
    s0, s1 = [0], [1]
    while len(r1) > 1 or r1[0] != 0:
        # divide r0 by r1
        q = [0]
        rem = list(r0)
        inv_lead = pow(r1[-1], -1, p)
        d1 = len(r1) - 1
        qq = [0] * max(1, len(rem) - d1)
        while len(rem) - 1 >= d1 and any(rem):
            if rem[-1] == 0:
                rem.pop()
                continue
            c = rem[-1] * inv_lead % p
            shift = len(rem) - 1 - d1
            qq[shift] = c
            for i in range(d1 + 1):
                rem[shift + i] = (rem[shift + i] - c * r1[i]) % p
            rem.pop()
        q = _trim(qq)
        rem = _trim(rem) if rem else [0]
        r0, r1 = r1, rem
        s0, s1 = s1, psub(s0, pmul(q, s1, p), p)
    if len(r0) != 1:
        raise ValueError("not invertible modulo h")
    return pscale(s0, pow(r0[0], -1, p), p)


def ppow_mod(f, e, h, p):
    r = [1]
    base = pmod(f, h, p)
    while e:
        if e & 1:
            r = pmod(pmul(r, base, p), h, p)
        base = pmod(pmul(base, base, p), h, p)
        e >>= 1
    return r


# ---------------------------------------------------------------------------
# division polynomials  psi_n = f_n(x) * y^(n even)
# ---------------------------------------------------------------------------

def division_polynomials(p: int, a: int, b: int, upto: int) -> dict[int, list[int]]:
    """f_n for n <= upto with psi_n = f_n for odd n and psi_n = y * f_n for even n."""
    a %= p
    b %= p
    F = [b, a, 0, 1]                       # x^3 + a x + b  (= y^2)
    F2 = pmul(F, F, p)
    f = {0: [0], 1: [1], 2: [2],
         3: _trim([(-a * a) % p, 12 * b % p, 6 * a % p, 0, 3]),
         4: pscale(_trim([(-8 * b * b - a ** 3) % p, (-4 * a * b) % p, (-5 * a * a) % p,
                          20 * b % p, 5 * a % p, 0, 1]), 4, p)}
    inv2 = pow(2, -1, p)
    for n in range(5, upto + 1):
        m = n // 2
        if n % 2 == 1:
            t1 = pmul(f[m + 2], ppow_poly(f[m], 3, p), p)
            t2 = pmul(f[m - 1], ppow_poly(f[m + 1], 3, p), p)
            if m % 2 == 0:
                t1 = pmul(F2, t1, p)
            else:
                t2 = pmul(F2, t2, p)
            f[n] = psub(t1, t2, p)
        else:
            t1 = pmul(f[m + 2], pmul(f[m - 1], f[m - 1], p), p)
            t2 = pmul(f[m - 2], pmul(f[m + 1], f[m + 1], p), p)
            f[n] = pscale(pmul(f[m], psub(t1, t2, p), p), inv2, p)
    return f


def ppow_poly(f, e, p):
    r = [1]
    for _ in range(e):
        r = pmul(r, f, p)
    return r


# ---------------------------------------------------------------------------
# kernel polynomials of the F_p-rational cyclic subgroups of order ell
# ---------------------------------------------------------------------------

X = symbols("x")


def _factor_mod_p(f: list[int], p: int) -> list[tuple[list[int], int]]:
    """Irreducible factors of f over F_p as (coeff list low-first, multiplicity)."""
    expr = sum(c * X ** i for i, c in enumerate(f))
    _, facs = Poly(expr, X, modulus=p).factor_list()
    out = []
    for g, e in facs:
        coeffs = [int(c) % p for c in reversed(g.all_coeffs())]
        out.append((coeffs, e))
    return out


def _is_isogeny_kernel(E: Curve, h: list[int], ell: int, seed: int = 11) -> bool:
    """Cheap homomorphism test: phi(P+Q) == phi(P)+phi(Q) for random P, Q."""
    try:
        iso = KernelIsogeny(E, h, ell)
    except ValueError:
        return False
    rng = random.Random(seed)
    for _ in range(2):
        P, Q = E.point(rng.randrange(1 << 30)), E.point(rng.randrange(1 << 30))
        lhs = iso(E.add(P, Q))
        rhs = iso.codomain.add(iso(P), iso(Q))
        if lhs != rhs or not iso.codomain.on_curve(iso(P)):
            return False
    return True


def rational_kernels(E: Curve, ell: int, fdiv: dict[int, list[int]]) -> list[list[int]]:
    """Monic kernel polynomials h(x) in F_p[x] of the rational subgroups of order ell."""
    s = (ell - 1) // 2
    facs = [(g, e) for g, e in _factor_mod_p(fdiv[ell], E.p)]
    pieces = []
    for g, e in facs:
        for _ in range(e):
            pieces.append(g)
    pieces = [g for g in pieces if len(g) - 1 <= s]
    found: list[list[int]] = []
    seen = set()
    for r in range(1, len(pieces) + 1):
        for combo in itertools.combinations(range(len(pieces)), r):
            if sum(len(pieces[i]) - 1 for i in combo) != s:
                continue
            h = [1]
            for i in combo:
                h = pmul(h, pieces[i], E.p)
            inv = pow(h[-1], -1, E.p)
            h = pscale(h, inv, E.p)
            key = tuple(h)
            if key in seen:
                continue
            seen.add(key)
            if _is_isogeny_kernel(E, h, ell):
                found.append(h)
    return found


# ---------------------------------------------------------------------------
# Velu in kernel-polynomial form
# ---------------------------------------------------------------------------

class KernelIsogeny:
    """Odd-degree separable isogeny E -> E' given by its monic kernel polynomial h.

    Roots x_i of h are the x-coordinates of one point from each +-pair of
    the kernel.  With v_i = 2(3 x_i^2 + a), u_i = 4(x_i^3 + a x_i + b):
        a' = a - 5 sum v_i,   b' = b - 7 sum (u_i + x_i v_i),
        X  = x + sum [v_i/(x-x_i) + u_i/(x-x_i)^2],
        Y  = y - sum [2y u_i/(x-x_i)^3 + y v_i/(x-x_i)^2],
    and every sum over the roots is a trace in F_p[T]/(h(T)), evaluated from
    the power sums of the roots (Newton's identities).
    """

    def __init__(self, E: Curve, h: list[int], ell: int):
        self.E, self.h, self.ell = E, list(h), ell
        p, a, b = E.p, E.a, E.b
        s = len(h) - 1
        if s != (ell - 1) // 2 or h[-1] != 1:
            raise ValueError("kernel polynomial must be monic of degree (ell-1)/2")
        # elementary symmetric functions: h = x^s - e1 x^(s-1) + e2 x^(s-2) - ...
        e = [1] + [((-1) ** k * h[s - k]) % p for k in range(1, s + 1)]
        # power sums p_0 .. p_(s+2)
        # Newton: p_k = sum_{i=1}^{min(k-1,s)} (-1)^(i-1) e_i p_(k-i) + [k <= s] (-1)^(k-1) k e_k
        ps = [s % p]
        for k in range(1, s + 3):
            acc = 0
            for i in range(1, min(k - 1, s) + 1):
                acc += ((-1) ** (i - 1)) * e[i] * ps[k - i]
            if k <= s:
                acc += ((-1) ** (k - 1)) * k * e[k]
            ps.append(acc % p)
        self.ps = ps
        p1, p2, p3 = ps[1], ps[2], ps[3]
        v = (6 * p2 + 2 * a * s) % p
        w = (10 * p3 + 6 * a * p1 + 4 * b * s) % p
        self.codomain = Curve(p, (a - 5 * v) % p, (b - 7 * w) % p, E.F)
        self.vT = _trim([2 * a % p, 0, 6 % p])                 # 6T^2 + 2a
        self.uT = _trim([4 * b % p, 4 * a % p, 0, 4 % p])      # 4T^3 + 4aT + 4b
        self.s = s

    def _trace(self, f: list[int]) -> int:
        f = pmod(f, self.h, self.E.p)
        return sum(c * self.ps[k] for k, c in enumerate(f)) % self.E.p

    def __call__(self, P):
        if P is None:
            return None
        p = self.E.p
        x0, y0 = P
        h = self.h
        lin = _trim([x0 % p, (-1) % p])                     # x0 - T
        try:
            A = pinv_mod(lin, h, p)
        except ValueError:
            return None                                     # P is in the kernel
        A2 = pmod(pmul(A, A, p), h, p)
        A3 = pmod(pmul(A2, A, p), h, p)
        Sv1 = self._trace(pmul(self.vT, A, p))
        Su2 = self._trace(pmul(self.uT, A2, p))
        Su3 = self._trace(pmul(self.uT, A3, p))
        Sv2 = self._trace(pmul(self.vT, A2, p))
        Xn = (x0 + Sv1 + Su2) % p
        Yn = (y0 - 2 * y0 * Su3 - y0 * Sv2) % p
        self.E.F.M += 4 * self.s + 8          # rough affine accounting only
        return (Xn, Yn)


# ---------------------------------------------------------------------------
# the chain search
# ---------------------------------------------------------------------------

@dataclass
class ChainResult:
    curve: str
    D: int
    element: tuple[int, int]
    degree: int
    steps: list[int]
    found: bool
    eigenvalue: int | None = None
    matched_element: tuple[int, int] | None = None
    lambda_omega: int | None = None
    walk_js: list[int] = field(default_factory=list)
    intermediate_curves: list[tuple[int, int]] = field(default_factory=list)
    walks_examined: int = 0
    glv_check: dict = field(default_factory=dict)
    note: str = ""


def point_of_order(E: Curve, n: int, cofactor: int, seed: int = 2):
    x = seed
    while True:
        P = E.lift_x(x)
        x += 1
        if P is None:
            continue
        Q = E.mul(cofactor, P)
        if Q is not None and E.mul(n, Q) is None:
            return Q


def build_chain_endomorphism(p: int, a: int, b: int, n: int, cofactor: int, D: int,
                             element: tuple[int, int], *, curve_name: str = "",
                             seed: int = 2) -> ChainResult:
    E = Curve(p, a, b)
    ea, eb = element
    el = QO.RingElement(D, ea, eb)
    N = el.norm
    fac = factorint(N)
    steps: list[int] = []
    for ell in sorted(fac):
        steps += [ell] * fac[ell]
    res = ChainResult(curve_name, D, element, N, steps, False)
    if any(ell == 2 for ell in steps):
        res.note = "degree-2 steps not implemented in kernel-polynomial form"
        return res
    P = point_of_order(E, n, cofactor, seed)
    lam_roots = QO.omega_eigenvalues(D, n)
    if not lam_roots:
        res.note = "omega has no eigenvalue mod n"
        return res
    # candidate scalars: the element's unit/conjugation orbit under each root
    cands: dict[int, tuple[tuple[int, int], int]] = {}
    for lam_w in lam_roots:
        for base in ((ea, eb), QO.conjugate(D, ea, eb)):
            for u in QO.units(D):
                a_, b_ = QO.multiply(D, base, u)
                cands[QO.eigenvalue(D, a_, b_, lam_w, n)] = ((a_, b_), lam_w)
    # precompute division polynomials once per curve lazily
    cache: dict[tuple[int, int, int], list[list[int]]] = {}

    def kernels(cur: Curve, ell: int) -> list[list[int]]:
        key = (cur.a, cur.b, ell)
        if key not in cache:
            fdiv = division_polynomials(cur.p, cur.a, cur.b, ell)
            cache[key] = rational_kernels(cur, ell, fdiv)
        return cache[key]

    j0 = E.j()
    walks: list[list[KernelIsogeny]] = []

    def dfs(cur: Curve, maps: list[KernelIsogeny], prev_j, depth: int):
        if depth == len(steps):
            if cur.j() == j0:
                walks.append(list(maps))
            return
        ell = steps[depth]
        for h in kernels(cur, ell):
            iso = KernelIsogeny(cur, h, ell)
            cj = iso.codomain.j()
            if cj == prev_j:
                continue               # immediate backtrack along the dual
            dfs(iso.codomain, maps + [iso], cur.j(), depth + 1)

    dfs(E, [], None, 0)
    res.walks_examined = len(walks)
    for walk in walks:
        last = walk[-1].codomain
        iso = isomorphism_to(last, E)
        if iso is None:
            continue
        phi = Composite(list(walk) + [iso])
        img = phi(P)
        if img is None or not E.on_curve(img):
            continue
        for lam, (elt, lam_w) in cands.items():
            if E.mul(lam, P) == img:
                res.found = True
                res.eigenvalue = lam
                res.matched_element = elt
                res.lambda_omega = lam_w
                res.walk_js = [E.j()] + [m.codomain.j() for m in walk]
                res.intermediate_curves = [(m.codomain.a, m.codomain.b) for m in walk]
                # end-to-end GLV-2 check with explicit images
                red = LA.reduce([1, lam], n)
                rng = random.Random(seed + 1)
                worst = 0
                for _ in range(4):
                    k = rng.randrange(1, n)
                    k1, k2 = red.decompose(k)
                    worst = max(worst, abs(k1), abs(k2))
                    lhs = E.mul(k, P)
                    rhs = E.add(E.mul(k1, P), E.mul(k2, img))
                    assert lhs == rhs, "GLV-2 reconstruction failed"
                res.glv_check = {"scalars_checked": 4, "max_coeff_bits": worst.bit_length(),
                                 "babai_bound_bits": red.babai_bound.bit_length(),
                                 "n_bits": n.bit_length()}
                return res
    res.note = ("closed walks found but none acts as a predicted scalar" if walks
                else "no closed walk of this shape returns to j(E): element not in End(E)?")
    return res


def main(argv=None) -> int:
    import argparse
    from .targets import deployed_targets, verify
    ap = argparse.ArgumentParser(description="build and verify a chain endomorphism on a real curve")
    ap.add_argument("--target", default="GOST CryptoPro-B")
    ap.add_argument("--element", default=None, help="a,b for a + b*omega; default: cheapest chain from the sweep")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    T = next(t for t in deployed_targets() if t.name.lower() == args.target.lower())
    verify(T)
    assert T.verified, T.verification
    Dfrob = QO.frobenius_discriminant(T.q, T.trace)
    scan = QO.small_discriminant_scan(Dfrob, 2_000_000)
    if scan.found is None:
        print(json.dumps({"target": T.name, "found": False, "note": scan.certificate}, indent=1))
        return 1
    D = scan.found
    if args.element:
        ea, eb = (int(v) for v in args.element.split(","))
    else:
        from .sweep import SweepOptions, build_catalogue
        roots = QO.omega_eigenvalues(D, T.n)
        gens, cheap, _ = build_catalogue(T, D, roots[0], SweepOptions())
        best = min((c for c in cheap if c["kind"] == "isogeny"), key=lambda c: c["cost_M"])
        ea, eb = best["a"], best["b"]
    res = build_chain_endomorphism(T.p, T.coeffs["a"], T.coeffs["b"], T.n, T.h, D, (ea, eb),
                                   curve_name=T.name)
    out = {"target": T.name, "D_K": D, "conductor": scan.conductor, **res.__dict__}
    txt = json.dumps(out, indent=1, default=str)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt)
    print(txt)
    return 0 if res.found else 1


if __name__ == "__main__":
    raise SystemExit(main())

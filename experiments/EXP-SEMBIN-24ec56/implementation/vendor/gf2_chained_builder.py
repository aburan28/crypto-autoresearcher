#!/usr/bin/env python3
"""Pure-Python reconstruction of the EXP-DREG-001 GF(2) chained Semaev fixture.

The archived builder is ``experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/
code/h012_peel_rank.py::build_system(n, t, ti, seed)`` (sha256 c46c871b...), which
calls ``semaev_tree.py`` (sha256 e9f1681b..., identical to ``src/semaev_tree.py``)
under Sage.  Sage is absent on the executing host, so this module re-implements
that construction with Python integers only, step for step:

  1. F_{2^n} = F_2[x]/(C_n(x)) with C_n the Conway polynomial (Sage's default
     modulus for GF(2^n) when it is in the database; n = 12 is).  The Conway
     polynomial is COMPUTED here from its definition (lexicographically least
     primitive polynomial compatible with the Conway polynomials of all proper
     subfields), not typed in.
  2. Curve y^2 + xy = x^3 + A x^2 + B with A = 1, B = alpha
     (``build_field_and_curve`` defaults).
  3. V = span_{F_2}(1, alpha, ..., alpha^{k-1}), k = ceil(n / t), enumerated in
     ``make_V_subspace`` bit order.
  4. Candidate points = for v in V: every affine point with x = v
     (``E.lift_x(v, all=True)``); rng = random.Random(seed + 1000*ti + n);
     P_list = rng.sample(candidates, t); R = sum(P_list); R_X = x(R).
  5. Chained system t = 3: S_3(u1, x1, x2), S_3(u1, x3, R_X) with
     S_3(a, b, c) = (ab + ac + bc)^2 + abc + B.
  6. Weil descent: u1 = sum_{j<n} u1_j alpha^j, x_i = sum_{j<k} x_{i,j} alpha^j;
     expand in F_q[boolean vars] (ordinary exponents, characteristic 2), then for
     l = 0..n-1 the coefficient of alpha^l of every monomial, booleanised
     (exponent >= 1 -> 1) and summed mod 2, is the l-th descended polynomial;
     zero polynomials are skipped.  Variable order: u1_0..u1_{n-1}, x1_0..x1_{k-1},
     x2_*, x3_*.
  7. eq_degs = max monomial degree per generator.

The archived run recorded ``system_hash`` (``h012c_block_m4ri.monosets_hash`` of
the ordered generators) = c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818
for (n, t, ti, seed) = (12, 3, 0, 2026).  ``main`` reports whether the
reconstruction reproduces that hash.  The ONE step whose Sage ordering cannot
be derived from first principles is the order of the two roots returned by
``E.lift_x(v, all=True)``; ``--root-order`` selects a candidate convention and the
hash comparison decides.  Nothing in KN-FIND-006's known answer depends on the
particular R (the counts are n-invariant per that record); bit-exactness is
reported, never assumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from itertools import product
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# ----------------------------------------------------------------------------
# F_{2^n} arithmetic on ints (bit i = coefficient of alpha^i)
# ----------------------------------------------------------------------------


def gf2_poly_mulmod(a: int, b: int, mod: int, n: int) -> int:
    a = gf2_poly_mod(a, mod)
    b = gf2_poly_mod(b, mod)
    r = 0
    top = 1 << n
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= mod
    return r


def gf2_poly_mod(a: int, mod: int) -> int:
    dm = mod.bit_length() - 1
    while a.bit_length() - 1 >= dm and a:
        a ^= mod << (a.bit_length() - 1 - dm)
    return a


class GF2n:
    def __init__(self, n: int, modulus: int) -> None:
        self.n = n
        self.mod = modulus
        self.order = (1 << n) - 1

    def mul(self, a: int, b: int) -> int:
        return gf2_poly_mulmod(a, b, self.mod, self.n)

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.order - 1)

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def trace(self, a: int) -> int:
        t, x = 0, a
        for _ in range(self.n):
            t ^= x
            x = self.mul(x, x)
        return t


def _prime_factors(m: int) -> List[int]:
    out = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            out.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        out.append(m)
    return out


def _is_irreducible(poly: int, n: int) -> bool:
    # Ben-Or: x^(2^i) mod poly != x for i < n/2 ... simpler: check gcd conditions via
    # x^(2^n) = x and for each prime q | n, gcd(x^(2^(n/q)) - x, poly) = 1.
    def powx(k: int) -> int:
        x = 2
        for _ in range(k):
            x = gf2_poly_mulmod(x, x, poly, n)
        return x

    if powx(n) != gf2_poly_mod(2, poly):
        return False
    for q in _prime_factors(n):
        h = powx(n // q) ^ 2
        if _gf2_gcd(h, poly) != 1:
            return False
    return True


def _gf2_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, gf2_poly_mod(a, b)
    return a


def _is_primitive(poly: int, n: int) -> bool:
    if not _is_irreducible(poly, n):
        return False
    F = GF2n(n, poly)
    order = F.order
    for q in _prime_factors(order):
        if F.pow(2, order // q) == 1:
            return False
    return True


def _minimal_polynomial(F: GF2n, a: int) -> int:
    """Minimal polynomial over F_2 of a in F_{2^n}, as an int polynomial."""
    conj = []
    x = a
    while x not in conj:
        conj.append(x)
        x = F.mul(x, x)
    # prod (X - c) with coefficients in F_{2^n}; result has F_2 coefficients
    poly = [1]  # coefficients in F, low to high
    for c in conj:
        new = [0] * (len(poly) + 1)
        for i, co in enumerate(poly):
            new[i + 1] ^= co
            new[i] ^= F.mul(co, c)
        poly = new
    out = 0
    for i, co in enumerate(poly):
        if co not in (0, 1):
            raise AssertionError("minimal polynomial not over F_2")
        if co:
            out |= 1 << i
    return out


_CONWAY_CACHE: Dict[int, int] = {}


def conway_polynomial_gf2(n: int) -> int:
    """Conway polynomial C_n over F_2 by definition (lexicographic search)."""
    if n in _CONWAY_CACHE:
        return _CONWAY_CACHE[n]
    if n == 1:
        _CONWAY_CACHE[1] = 0b11  # x + 1, the only primitive polynomial of degree 1
        return 0b11
    subs = [d for d in range(1, n) if n % d == 0]
    sub_conway = {d: conway_polynomial_gf2(d) for d in subs}
    order = (1 << n) - 1
    # Conway ordering for p = 2 is lexicographic on (a_{n-1}, ..., a_0) for monic
    # polynomials; constant term must be 1 for primitivity.
    for bits in range(0, 1 << (n - 1)):
        # bits encodes a_{n-1} .. a_1 with a_{n-1} the most significant bit
        poly = (1 << n) | 1
        for i in range(n - 1):
            if bits >> (n - 2 - i) & 1:
                poly |= 1 << (n - 1 - i)
        if not _is_primitive(poly, n):
            continue
        F = GF2n(n, poly)
        ok = True
        for d in subs:
            beta = F.pow(2, order // ((1 << d) - 1))
            if _minimal_polynomial(F, beta) != sub_conway[d]:
                ok = False
                break
        if ok:
            _CONWAY_CACHE[n] = poly
            return poly
    raise RuntimeError("no Conway polynomial found")


# ----------------------------------------------------------------------------
# Curve y^2 + xy = x^3 + A x^2 + B over F_{2^n}
# ----------------------------------------------------------------------------

INF = None


class Curve:
    def __init__(self, F: GF2n, A: int, B: int) -> None:
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        x, y = P
        F = self.F
        lhs = F.mul(y, y) ^ F.mul(x, y)
        rhs = F.mul(F.mul(x, x), x) ^ F.mul(self.A, F.mul(x, x)) ^ self.B
        return lhs == rhs

    def lift_x(self, x: int) -> List[Tuple[int, int]]:
        """All affine points with abscissa x, in the order (y0, y0 + x) where y0
        is chosen by the caller-selected convention (see ``ROOT_ORDER``)."""
        F = self.F
        rhs = F.mul(F.mul(x, x), x) ^ F.mul(self.A, F.mul(x, x)) ^ self.B
        if x == 0:
            return [(0, F.sqrt(rhs))]
        # y = x z: z^2 + z = rhs / x^2
        c = F.mul(rhs, F.inv(F.mul(x, x)))
        if F.trace(c) != 0:
            return []
        z = _solve_artin_schreier(F, c)
        y0 = F.mul(x, z)
        y1 = y0 ^ x
        assert self.on_curve((x, y0)) and self.on_curve((x, y1))
        return [(x, y0), (x, y1)]

    def neg(self, P):
        if P is INF:
            return INF
        x, y = P
        return (x, x ^ y)

    def add(self, P, Q):
        F = self.F
        if P is INF:
            return Q
        if Q is INF:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x1:  # Q = -P (includes x1 = 0 case where P = -P)
                return INF
            # doubling
            if x1 == 0:
                return INF
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.mul(lam, lam) ^ lam ^ self.A
            y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)


def _solve_artin_schreier(F: GF2n, c: int) -> int:
    """A root of z^2 + z = c (Tr(c) = 0).  n even: brute force / half-trace does
    not apply, so use the standard linear-algebra solve over F_2 (n <= 32)."""
    n = F.n
    # Linear map L(z) = z^2 + z on F_2^n; solve L(z) = c by Gaussian elimination.
    cols = [F.mul(1 << i, 1 << i) ^ (1 << i) for i in range(n)]  # images of basis
    # Build augmented system: sum_i z_i * cols[i] = c
    rows = []
    for bit in range(n):
        r = 0
        for i in range(n):
            if cols[i] >> bit & 1:
                r |= 1 << i
        rows.append((r, c >> bit & 1))
    # eliminate
    pivots = {}
    for r, rhs in rows:
        for pc in sorted(pivots, reverse=True):
            if r >> pc & 1:
                r ^= pivots[pc][0]
                rhs ^= pivots[pc][1]
        if r:
            lead = r.bit_length() - 1
            # reduce existing
            for pc in list(pivots):
                pr, prhs = pivots[pc]
                if pr >> lead & 1:
                    pivots[pc] = (pr ^ r, prhs ^ rhs)
            pivots[lead] = (r, rhs)
        elif rhs:
            raise ValueError("no solution")
    z = 0
    for lead, (r, rhs) in pivots.items():
        # r has only its lead bit set among pivot positions after back-substitution;
        # free bits (non-pivot) are set to 0 so the row reads z_lead = rhs.
        if rhs:
            z |= 1 << lead
    assert F.mul(z, z) ^ z == c
    return z


# ----------------------------------------------------------------------------
# Chained system and Weil descent
# ----------------------------------------------------------------------------


def _root_order_key(F: GF2n, alpha_log: Dict[int, int], convention: str):
    if convention == "int":
        return lambda pt: pt[1]
    if convention == "int_desc":
        return lambda pt: -pt[1]
    if convention == "log":
        return lambda pt: alpha_log.get(pt[1], -1)
    if convention == "log_desc":
        return lambda pt: -alpha_log.get(pt[1], -1)
    if convention == "native":
        return None
    raise ValueError(convention)


def build_fixture(n: int, t: int, ti: int, seed: int, root_order: str = "int") -> dict:
    if t != 3:
        raise NotImplementedError("the archived fixture family is t = 3")
    k = (n + t - 1) // t
    modulus = conway_polynomial_gf2(n)
    F = GF2n(n, modulus)
    alpha = 2
    A, B = 1, alpha
    E = Curve(F, A, B)
    alpha_log = {}
    x = 1
    for i in range(F.order):
        alpha_log[x] = i
        x = F.mul(x, alpha)
    key = _root_order_key(F, alpha_log, root_order)

    V = []
    for bits in range(1 << k):
        v = 0
        for j in range(k):
            if bits >> j & 1:
                v ^= F.pow(alpha, j)
        V.append(v)

    candidates = []
    for v in V:
        pts = E.lift_x(v)
        if key is not None:
            pts = sorted(pts, key=key)
        candidates.extend(pts)
    if len(candidates) < t:
        raise ValueError("not enough factor-base points")
    rng = random.Random(int(seed + 1000 * ti + n))
    P_list = rng.sample(candidates, t)
    R = INF
    for P in P_list:
        R = E.add(R, P)
    if R is INF:
        raise ValueError("R is the point at infinity")
    R_X = R[0]

    # Boolean variables: u1_0..u1_{n-1}, x1_0..x1_{k-1}, x2_*, x3_*
    nb = n + 3 * k

    def lin_form(offset: int, width: int) -> Dict[Tuple[int, ...], int]:
        # polynomial over F_q in boolean vars: {exponent tuple: coeff}
        out = {}
        for j in range(width):
            e = [0] * nb
            e[offset + j] = 1
            out[tuple(e)] = F.pow(alpha, j)
        return out

    def const(c: int) -> Dict[Tuple[int, ...], int]:
        return {tuple([0] * nb): c} if c else {}

    def padd(a, b):
        out = dict(a)
        for e, c in b.items():
            v = out.get(e, 0) ^ c
            if v:
                out[e] = v
            else:
                out.pop(e, None)
        return out

    def pmul(a, b):
        out: Dict[Tuple[int, ...], int] = {}
        for ea, ca in a.items():
            for eb, cb in b.items():
                e = tuple(x + y for x, y in zip(ea, eb))
                v = out.get(e, 0) ^ F.mul(ca, cb)
                if v:
                    out[e] = v
                else:
                    out.pop(e, None)
        return out

    def S3(a, b, c):
        s = padd(padd(pmul(a, b), pmul(a, c)), pmul(b, c))
        return padd(padd(pmul(s, s), pmul(pmul(a, b), c)), const(B))

    u1 = lin_form(0, n)
    x1 = lin_form(n, k)
    x2 = lin_form(n + k, k)
    x3 = lin_form(n + 2 * k, k)
    polys = [S3(u1, x1, x2), S3(u1, x3, const(R_X))]

    descended: List[List[List[int]]] = []  # list of generators, each a list of monomials (sorted index lists)
    for P in polys:
        by_bool: Dict[int, int] = {}
        for e, c in P.items():
            mask = 0
            for i, ei in enumerate(e):
                if ei > 0:
                    mask |= 1 << i
            by_bool[mask] = by_bool.get(mask, 0) ^ c
        for l in range(n):
            monos = sorted(m for m, c in by_bool.items() if c >> l & 1)
            if monos:
                descended.append([[i for i in range(nb) if m >> i & 1] for m in monos])

    eq_degs = [max(len(m) for m in f) for f in descended]
    return {
        "n": n, "t": t, "ti": ti, "seed": seed, "k": k, "nb": nb,
        "modulus_int": modulus, "modulus_poly": _poly_str(modulus),
        "curve": {"a1": 1, "a2": A, "a3": 0, "a4": 0, "a6": B, "B_is_alpha": True},
        "rng_seed": int(seed + 1000 * ti + n),
        "root_order": root_order,
        "n_candidates": len(candidates),
        "P_list": [[p[0], p[1]] for p in P_list],
        "R": [R[0], R[1]],
        "R_X": R_X,
        "variables": ([f"u1_{j}" for j in range(n)] + [f"x{i}_{j}" for i in (1, 2, 3) for j in range(k)]),
        "eq_degs": eq_degs,
        "generators": descended,
        "system_hash": monosets_hash(descended),
    }


def _poly_str(poly: int) -> str:
    terms = [f"x^{i}" if i > 1 else ("x" if i == 1 else "1") for i in range(poly.bit_length() - 1, -1, -1) if poly >> i & 1]
    return " + ".join(terms)


def monosets_hash(generators: Sequence[Sequence[Sequence[int]]]) -> str:
    """Verbatim port of h012c_block_m4ri.monosets_hash."""
    h = hashlib.sha256()
    for f in generators:
        encoded = sorted(tuple(sorted(int(v) for v in m)) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()


ARCHIVED_HASHES = {
    (12, 3, 0, 2026): "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818",
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--ti", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--root-order", default="int", choices=["int", "int_desc", "log", "log_desc", "native"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    fx = build_fixture(args.n, args.t, args.ti, args.seed, args.root_order)
    archived = ARCHIVED_HASHES.get((args.n, args.t, args.ti, args.seed))
    fx["archived_system_hash"] = archived
    fx["matches_archived_system_hash"] = (archived is not None and fx["system_hash"] == archived)
    summary = {k: v for k, v in fx.items() if k != "generators"}
    print(json.dumps(summary, indent=1))
    if args.out:
        Path(args.out).write_text(json.dumps(fx, indent=0, sort_keys=True) + "\n")
        print("wrote", args.out, "sha256", hashlib.sha256(Path(args.out).read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())

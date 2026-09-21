#!/usr/bin/env python3
"""Screen a prime-field elliptic curve's isogeny class for exploitable structure.

Motivation
----------
`analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md` lanes L2 (volcano
level / endomorphism-ring depth) and L3 (special j-invariants, small CM
discriminant) both presuppose that the structure they measure is *available* in
the class under test. For a named cryptographic curve that presupposition is
decidable up front, cheaply, from Frobenius data alone -- before any expensive
experiment is contracted.

Three facts drive the screen, all standard:

  1. End^0(E) = Q(sqrt(D)) with D = t^2 - 4p is an ISOGENY-CLASS INVARIANT
     (Tate). So "small CM discriminant" and "extra automorphisms" (j = 0 needs
     D_0 = -3, j = 1728 needs D_0 = -4) are properties of the CLASS, not of an
     individual curve. If the class does not have them, no walk finds them.

  2. Write D = f^2 * D_0 with D_0 fundamental. The ell-volcano has depth
     v_ell(f). If ell does not divide f, EVERY rational ell-isogeny is
     horizontal and preserves End(E) exactly -- there is no vertical direction
     to take at that ell.

  3. The minimum norm of a non-integer element of Z[pi] is |D|/4. A small-degree
     (hence GLV-usable) endomorphism therefore cannot exist anywhere in a class
     with large |D|.

The screen reports, for a given curve: ordinarity, v_ell(D) and the split /
inert / ramified type at each small ell, the exact count of F_p-rational
ell-isogenies, whether any small fundamental discriminant is present, and the
class size h ~ sqrt|D|.

With `--neighbours` it additionally computes the neighbouring curves explicitly:
the Elkies kernel polynomial is obtained as the eigenspace of Frobenius on
E[ell] via h = gcd(psi_ell, x^p * psi_lambda^2 - phi_lambda), then Velu's
formulae give the codomain (a', b') and j'.

Self-verification (all on by default, none of it optional):
  * the supplied (p, a, b, G, n) are checked: G on curve, [n]G = O, [n-1]G = -G;
  * each kernel polynomial must have degree exactly (ell-1)/2;
  * each computed neighbour must satisfy Phi_ell(j(E), j') = 0 for ell in {2,3},
    where the classical modular polynomial is hard-coded;
  * each computed neighbour must have #E'(F_p) = n, checked by [n]P = O on
    several points (n prime and in the Hasse interval makes this conclusive).

A failure of any check aborts rather than reporting a number.

Usage
-----
    python3 tools/isogeny_class_screen.py --curve p256
    python3 tools/isogeny_class_screen.py --curve p256 --neighbours --ell 3,5,11,13
    python3 tools/isogeny_class_screen.py --p ... --a ... --b ... --n ...

Scope
-----
Screening only. This tool produces no attack, claims no speedup, and its output
is not evidence of hardness or of weakness -- it reports which structural axes
are OPEN for a given class and which are CLOSED by a class invariant.
"""

from __future__ import annotations

import argparse
import math
import sys

# --------------------------------------------------------------------------
# Named curves. Each entry carries a base point so the parameters self-check.
# --------------------------------------------------------------------------
CURVES = {
    "p256": dict(
        p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
        a=-3,
        b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
        Gx=0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
        Gy=0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
        n=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    ),
    "p384": dict(
        p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFF,
        a=-3,
        b=0xB3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF,
        Gx=0xAA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7,
        Gy=0x3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F,
        n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
    ),
    "secp256k1": dict(
        p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
        a=0,
        b=7,
        Gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        Gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
        n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    ),
}


# --------------------------------------------------------------------------
# Number theory helpers
# --------------------------------------------------------------------------
def kronecker(a: int, n: int) -> int:
    """Kronecker symbol (a|n)."""
    if n == 0:
        return 1 if a in (1, -1) else 0
    sign = 1
    if n < 0:
        n = -n
        if a < 0:
            sign = -1
    e = 0
    while n % 2 == 0:
        n //= 2
        e += 1
    if e:
        k2 = 0 if a % 2 == 0 else (1 if a % 8 in (1, 7) else -1)
        sign *= k2**e
    a %= n
    r = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                r = -r
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            r = -r
        a %= n
    return sign * r if n == 1 else 0


def valuation(m: int, ell: int) -> int:
    v = 0
    m = abs(m)
    while m and m % ell == 0:
        m //= ell
        v += 1
    return v


def square_part(m: int, bound: int = 200_000) -> tuple[int, int]:
    """Return (s, rem) with m = s^2 * rem, removing square factors of primes < bound."""
    s, rem, d = 1, abs(m), 2
    while d < bound and d * d <= rem:
        if rem % (d * d) == 0:
            while rem % (d * d) == 0:
                rem //= d * d
                s *= d
        d += 1
    return s, rem


def is_squarefree(m: int, bound: int = 200_000) -> bool | None:
    """True/False if decidable by trial division below `bound`, else None."""
    m = abs(m)
    d = 2
    while d < bound and d * d <= m:
        if m % (d * d) == 0:
            return False
        d += 1
    return True if d * d > m else None


def is_fundamental(D0: int) -> bool:
    """D_0 is a fundamental discriminant."""
    if D0 % 4 == 1:
        return is_squarefree(D0) is True
    if D0 % 4 == 0:
        m = D0 // 4
        return m % 4 in (2, 3) and is_squarefree(m) is True
    return False


def small_fundamental_discriminants(D: int, limit: int) -> list[tuple[int, int]]:
    """All (D_0, f) with |D_0| <= limit, D_0 FUNDAMENTAL, and D = f^2 * D_0.

    Exactly one fundamental D_0 exists for a given D; this returns it if its
    absolute value is within `limit`, and the empty list otherwise (which
    PROVES |D_0| > limit).
    """
    hits = []
    for D0 in range(-1, -limit - 1, -1):
        if D0 % 4 not in (0, 1):
            continue
        if D % D0 != 0:
            continue
        q = D // D0
        if q <= 0:
            continue
        r = math.isqrt(q)
        if r * r == q and is_fundamental(D0):
            hits.append((D0, r))
    return hits


# --------------------------------------------------------------------------
# Curve arithmetic over F_p
# --------------------------------------------------------------------------
class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x % self.p * x + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def mul(self, k: int, P):
        R, Q = None, P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def j(self) -> int:
        p = self.p
        a3 = pow(self.a, 3, p)
        num = 1728 * 4 * a3 % p
        den = (4 * a3 + 27 * self.b * self.b) % p
        if den == 0:
            raise ValueError("singular curve (discriminant 0)")
        return num * pow(den, -1, p) % p

    def some_points(self, count: int):
        """Yield up to `count` affine points with small x. Requires p = 3 mod 4."""
        p = self.p
        assert p % 4 == 3, "point search here assumes p = 3 mod 4"
        out = []
        for x in range(2, 5000):
            rhs = (x * x % p * x + self.a * x + self.b) % p
            y = pow(rhs, (p + 1) // 4, p)
            if y * y % p == rhs:
                out.append((x, y))
                if len(out) == count:
                    break
        return out


# --------------------------------------------------------------------------
# Polynomials over F_p, little-endian coefficient lists
# --------------------------------------------------------------------------
class Poly:
    def __init__(self, p: int):
        self.p = p

    def trim(self, f):
        while len(f) > 1 and f[-1] == 0:
            f.pop()
        return f

    def sub(self, f, g):
        r = [0] * max(len(f), len(g))
        for i, c in enumerate(f):
            r[i] = c
        for i, c in enumerate(g):
            r[i] = (r[i] - c) % self.p
        return self.trim(r)

    def mul(self, f, g):
        if f == [0] or g == [0]:
            return [0]
        r = [0] * (len(f) + len(g) - 1)
        for i, a in enumerate(f):
            if a:
                for j, b in enumerate(g):
                    if b:
                        r[i + j] += a * b
        return self.trim([c % self.p for c in r])

    def scal(self, f, c):
        return self.trim([x * c % self.p for x in f])

    def mod(self, f, m):
        f = f[:]
        dm = len(m) - 1
        inv = pow(m[-1], -1, self.p)
        while len(f) - 1 >= dm and f != [0]:
            d = len(f) - 1 - dm
            c = f[-1] * inv % self.p
            if c:
                for i, mc in enumerate(m):
                    f[i + d] = (f[i + d] - c * mc) % self.p
            self.trim(f)
            if len(f) == 1 and f[0] == 0:
                break
        return self.trim(f)

    def gcd(self, f, g):
        f, g = self.trim(f[:]), self.trim(g[:])
        while g != [0]:
            f, g = g, self.mod(f, g)
        if f == [0]:
            return f
        return self.scal(f, pow(f[-1], -1, self.p))

    def mulmod(self, f, g, m):
        return self.mod(self.mul(f, g), m)

    def powmod(self, base, e, m):
        r, b = [1], self.mod(base, m)
        while e:
            if e & 1:
                r = self.mulmod(r, b, m)
            b = self.mulmod(b, b, m)
            e >>= 1
        return r


class DivisionPolys:
    """f_m with psi_m = f_m (m odd) and psi_m = 2y * f_m (m even)."""

    def __init__(self, curve: Curve, upto: int):
        p, a, b = curve.p, curve.a, curve.b
        self.P = Poly(p)
        self.Y = [b, a, 0, 1]
        Y2 = self.P.mul(self.Y, self.Y)
        P = self.P
        f = {0: [0], 1: [1], 2: [1]}
        f[3] = P.trim([(-a * a) % p, 12 * b % p, 6 * a % p, 0, 3])
        f[4] = P.scal(
            [
                (-8 * b * b - a * a * a) % p,
                (-4 * a * b) % p,
                (-5 * a * a) % p,
                20 * b % p,
                5 * a % p,
                0,
                1,
            ],
            2,
        )
        c16 = P.scal(Y2, 16)
        for m in range(2, upto + 1):
            if 2 * m + 1 <= upto and (2 * m + 1) not in f:
                A = P.mul(f[m + 2], P.mul(f[m], P.mul(f[m], f[m])))
                B = P.mul(f[m - 1], P.mul(f[m + 1], P.mul(f[m + 1], f[m + 1])))
                f[2 * m + 1] = (
                    P.sub(P.mul(c16, A), B) if m % 2 == 0 else P.sub(A, P.mul(c16, B))
                )
            if 2 * m <= upto and (2 * m) not in f:
                f[2 * m] = P.mul(
                    f[m],
                    P.sub(
                        P.mul(f[m + 2], P.mul(f[m - 1], f[m - 1])),
                        P.mul(f[m - 2], P.mul(f[m + 1], f[m + 1])),
                    ),
                )
        self.f = f

    def psi_sq(self, m):
        P = self.P
        s = P.mul(self.f[m], self.f[m])
        return s if m % 2 == 1 else P.mul(P.scal(self.Y, 4), s)

    def phi(self, m):
        """x*psi_m^2 - psi_{m+1}*psi_{m-1}, a polynomial in x."""
        P = self.P
        f = self.f
        if m % 2 == 1:
            return P.sub(
                P.mul([0, 1], P.mul(f[m], f[m])),
                P.mul(P.scal(self.Y, 4), P.mul(f[m + 1], f[m - 1])),
            )
        return P.sub(
            P.mul([0, 1], P.mul(P.scal(self.Y, 4), P.mul(f[m], f[m]))),
            P.mul(f[m + 1], f[m - 1]),
        )


def velu(curve: Curve, h: list[int]) -> tuple[int, int]:
    """Velu from a monic kernel polynomial h of degree (ell-1)/2, odd ell."""
    p, a, b = curve.p, curve.a, curve.b
    d = len(h) - 1
    e = [0] * (d + 1)
    e[0] = 1
    for k in range(1, d + 1):
        e[k] = (-1) ** k * h[d - k] % p

    def ek(i):
        return e[i] if 0 <= i <= d else 0

    ps = [d % p]  # power sums p_0..p_3 via Newton's identities
    for k in range(1, 4):
        s = 0
        for i in range(1, k):
            s = (s + (-1) ** (i - 1) * ek(i) * ps[k - i]) % p
        s = (s + (-1) ** (k - 1) * k * ek(k)) % p
        ps.append(s % p)
    p1, p2, p3 = ps[1], ps[2], ps[3]
    t_sum = (6 * p2 + 2 * a * d) % p
    w_sum = (10 * p3 + 6 * a * p1 + 4 * b * d) % p
    return (a - 5 * t_sum) % p, (b - 7 * w_sum) % p


# --------------------------------------------------------------------------
# Classical modular polynomials, used only as an independent check
# --------------------------------------------------------------------------
def phi2(X: int, Y: int, p: int) -> int:
    return (
        pow(X, 3, p) + pow(Y, 3, p) - X * X % p * (Y * Y % p)
        + 1488 * (X * X % p * Y + X * (Y * Y % p))
        - 162000 * (X * X + Y * Y)
        + 40773375 * X * Y
        + 8748000000 * (X + Y)
        - 157464000000000
    ) % p


def phi3(X: int, Y: int, p: int) -> int:
    X2, X3, X4 = X * X % p, pow(X, 3, p), pow(X, 4, p)
    Y2, Y3, Y4 = Y * Y % p, pow(Y, 3, p), pow(Y, 4, p)
    return (
        X4 + Y4 - X3 * Y3
        + 2232 * (X3 * Y2 + X2 * Y3)
        - 1069956 * (X3 * Y + X * Y3)
        + 36864000 * (X3 + Y3)
        + 2587918086 * X2 * Y2
        + 8900222976000 * (X2 * Y + X * Y2)
        + 452984832000000 * (X2 + Y2)
        - 770845966336000000 * X * Y
        + 1855425871872000000000 * (X + Y)
    ) % p


MODULAR = {2: phi2, 3: phi3}


# --------------------------------------------------------------------------
# Screen
# --------------------------------------------------------------------------
DEFAULT_ELL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def screen(p, a, b, n, ells, Gx=None, Gy=None, small_d_limit=100_000):
    E = Curve(p, a, b)
    if Gx is not None:
        G = (Gx, Gy)
        assert E.on_curve(G), "base point not on curve"
        assert E.mul(n, G) is None, "[n]G != O -- parameters inconsistent"
        assert E.mul(n - 1, G) == (Gx, (-Gy) % p), "[n-1]G != -G"
        print("parameter self-check: PASSED (G on curve, [n]G = O, [n-1]G = -G)")

    t = p + 1 - n
    D = t * t - 4 * p
    print(f"\np              = {p}")
    print(f"#E(F_p) = n    = {n}")
    print(f"t = p + 1 - n  = {t}")
    print(f"D = t^2 - 4p   = {D}")
    print(f"|D| bits       = {abs(D).bit_length()}")
    if D >= 0:
        print("D >= 0 -- not an ordinary curve over a prime field in the usual sense")
        return
    if t % p == 0:
        print("SUPERSINGULAR (p | t): this screen targets ordinary curves")
        return
    print("ordinary: yes.  End^0(E) = Q(sqrt(D)), an ISOGENY-CLASS INVARIANT")
    print(f"j(E)           = {E.j()}")
    print(f"j == 0 ? {E.j() == 0}    j == 1728 ? {E.j() == 1728}")

    s, _rem = square_part(D)
    print(f"\nsquare part of |D| over primes < 2e5 : {s}")
    if s == 1:
        print("  => the conductor f has NO prime factor < 2e5")
        print("  => every rational ell-isogeny at those ell is HORIZONTAL")
        print("  => End(E') = End(E) exactly for every such neighbour")

    hits = small_fundamental_discriminants(D, small_d_limit)
    print(f"\nfundamental discriminant D_0 with D = f^2*D_0, searched |D_0| <= "
          f"{small_d_limit} : {hits if hits else 'NONE in range'}")
    has_cm_special = any(d in (-3, -4) for d, _ in hits)
    print(f"  j=0 (needs D_0=-3) or j=1728 (needs D_0=-4) present in this class ? "
          f"{'YES' if has_cm_special else 'NO -- absent by class invariance'}")

    # Endomorphism sizes. NOTE the distinction that drives this whole screen:
    # |D|/4 bounds Z[pi], but End(E) may be a LARGER order, up to O_K, whose
    # minimal non-integer norm is governed by D_0, not by D. Reporting |D|/4 as
    # if it bounded End(E) would wrongly declare a GLV curve endomorphism-free.
    print(f"\nmin norm of a non-integer element of Z[pi]  = |D|/4  ~ "
          f"2^{(abs(D) // 4).bit_length()}")
    if hits:
        D0 = hits[0][0]
        print(f"  but End(E) may be as large as O_K, with D_0 = {D0}:")
        print(f"  => curves in this class whose End(E) = O_K DO carry a small-norm "
              f"endomorphism (|D_0|/4 ~ {max(1, abs(D0) // 4)})")
        if has_cm_special:
            print("  => this is the classical GLV / extra-automorphism situation; "
                  "the L3 axis is OPEN for this class")
    else:
        print(f"  and no fundamental D_0 with |D_0| <= {small_d_limit} divides D with "
              f"square quotient,")
        print(f"  => |D_0| > {small_d_limit} is PROVEN, so the minimal norm of any "
              f"non-integer element of")
        print(f"     End(E) exceeds {small_d_limit // 4} for EVERY curve in the class "
              f"-- no GLV-usable endomorphism.")
        print("     (A sharper bound would require factoring D; this one does not.)")

    h_bits = math.isqrt(abs(D)).bit_length()
    print(f"\nclass size h ~ sqrt|D| ~ 2^{h_bits} curves "
          f"({'enumerable' if h_bits < 30 else 'NOT enumerable'})")

    print("\n ell  v_ell(D)  (D|ell)  #rational ell-isogenies  type")
    for ell in ells:
        v = valuation(D, ell)
        ks = kronecker(D, ell)
        if v == 0:
            cnt, typ = (2, "split (2 horizontal)") if ks == 1 else (0, "inert (none)")
        elif v == 1:
            cnt, typ = 1, "ramified (1 horizontal)"
        else:
            cnt, typ = "?", "ell may divide f -- volcano may have depth"
        print(f" {ell:3d}  {v:8d}  {ks:7d}  {str(cnt):>22}  {typ}")
    return E, t, D


def neighbours(E: Curve, t: int, n: int, ells):
    """Explicitly compute isogenous neighbours via Elkies kernel + Velu."""
    p = E.p
    jE = E.j()
    maxm = max(ells) + 3
    print(f"\ncomputing division polynomials up to m = {maxm} ...", flush=True)
    DP = DivisionPolys(E, maxm)
    P = DP.P
    print(f"j(E) = {jE}\n")

    for ell in ells:
        if ell == 2:
            xp = P.powmod([0, 1], p, DP.Y)
            g = P.gcd(P.sub(xp, [0, 1]), DP.Y)
            print(f"ell = 2 : x^3+ax+b has {len(g)-1} root(s) in F_p "
                  f"-> {len(g)-1} rational 2-isogeny/ies")
            continue

        psil = DP.f[ell]
        lams = [x for x in range(1, ell) if (x * x - t * x + p) % ell == 0]
        print(f"ell = {ell:2d} : deg psi_ell = {len(psil)-1}, Frobenius eigenvalues "
              f"mod {ell} = {lams or 'none (inert -> 0 isogenies)'}")
        if not lams:
            print()
            continue

        xp = P.powmod([0, 1], p, psil)
        for lam in lams:
            R = P.sub(P.mulmod(xp, P.mod(DP.psi_sq(lam), psil), psil),
                      P.mod(DP.phi(lam), psil))
            h = P.gcd(psil, R)
            dh = len(h) - 1
            if dh == 0:
                continue
            assert dh == (ell - 1) // 2, (
                f"kernel polynomial degree {dh}, expected {(ell-1)//2}")
            a2, b2 = velu(E, h)
            E2 = Curve(p, a2, b2)
            j2 = E2.j()

            # check 1: same point count
            pts = E2.some_points(3)
            assert pts, "no point found on codomain"
            for Q in pts:
                assert E2.mul(n, Q) is None, "codomain point count != n"
            # check 2: modular polynomial, where hard-coded
            modcheck = ""
            if ell in MODULAR:
                ok = MODULAR[ell](jE, j2, p) == 0
                assert ok, f"Phi_{ell}(j(E), j') != 0"
                modcheck = f", Phi_{ell}(j,j')=0 OK"
            print(f"   lambda={lam:3d}: ker deg {dh} OK, #E'=n OK{modcheck}")
            print(f"              a' = {a2}")
            print(f"              b' = {b2}")
            print(f"              j' = {j2}")
        print()


def census(p: int, small_d_limit: int = 100):
    """Structural census of every ordinary isogeny class over F_p.

    Used to quantify how far a toy-scale population differs from a
    cryptographic-scale one on exactly the axes lanes L2/L3 measure.
    """
    lo = math.isqrt(4 * p)
    rows = []
    for t in range(-lo, lo + 1):
        if t % p == 0:
            continue
        D = t * t - 4 * p
        if D >= 0:
            continue
        f, _ = square_part(-D)
        rows.append((t, D, f))
    tot = len(rows)
    depth = sum(1 for _, _, f in rows if f > 1)
    smalld = sum(1 for _, D, f in rows if (-D) // (f * f) <= small_d_limit)
    hs = [math.isqrt(-D) for _, D, _ in rows]
    print(f"=== structural census of ordinary isogeny classes over F_{p} ===")
    print(f"ordinary classes                          : {tot}")
    print(f"conductor f > 1 (volcano HAS depth)       : {depth:6d}  "
          f"({100*depth/tot:.1f}%)")
    print(f"|D_0| <= {small_d_limit} (small CM discriminant)      : {smalld:6d}  "
          f"({100*smalld/tot:.1f}%)")
    print(f"mean class size h ~ sqrt|D|               : ~{sum(hs)//len(hs)} curves")
    print("\nContrast: for P-256 the conductor has no prime factor < 2e5 (0% depth "
          "at every such ell),\nno fundamental |D_0| <= 1e5 exists, and h ~ 2^129 "
          "curves -- the class is not enumerable.\nToy-scale populations therefore "
          "over-represent precisely the structure a 256-bit class lacks.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--curve", choices=sorted(CURVES), help="named curve")
    ap.add_argument("--p", type=int)
    ap.add_argument("--a", type=int)
    ap.add_argument("--b", type=int)
    ap.add_argument("--n", type=int, help="group order #E(F_p)")
    ap.add_argument("--ell", default=None,
                    help="comma-separated ell values (default: primes to 47)")
    ap.add_argument("--neighbours", action="store_true",
                    help="also compute neighbour curves explicitly (slower)")
    ap.add_argument("--census", type=int, metavar="PRIME",
                    help="structural census of all ordinary classes over F_PRIME")
    args = ap.parse_args()

    if args.census:
        census(args.census)
        return 0

    if args.curve:
        c = CURVES[args.curve]
        p, a, b, n = c["p"], c["a"], c["b"], c["n"]
        Gx, Gy = c["Gx"], c["Gy"]
        print(f"=== isogeny-class screen: {args.curve} ===")
    else:
        if None in (args.p, args.a, args.b, args.n):
            ap.error("supply --curve, or all of --p --a --b --n")
        p, a, b, n = args.p, args.a, args.b, args.n
        Gx = Gy = None
        print("=== isogeny-class screen: custom curve ===")

    ells = ([int(x) for x in args.ell.split(",")] if args.ell else DEFAULT_ELL)
    out = screen(p, a, b, n, ells, Gx, Gy)
    if out is None:
        return 1
    E, t, D = out
    if args.neighbours:
        neighbours(E, t, n, ells)
    print("\nScope: screening only. No attack, no speedup, and no hardness claim "
          "is made or implied by this output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

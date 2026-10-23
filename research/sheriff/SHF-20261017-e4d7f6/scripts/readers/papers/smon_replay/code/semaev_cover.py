"""Self-contained arithmetic for the Semaev summation cover over prime fields.

No third-party dependencies (this environment has neither sympy nor Sage), so
everything below is elementary and written to be auditable line by line:

  * `Fp2`            -- the quadratic extension F_{p^2} = F_p[u]/(u^2 - ns).
  * `Curve`          -- y^2 = x^3 + A x + B over F_p, with group law over both
                        F_p and F_{p^2}.
  * `semaev_T_poly`  -- the coefficient list of S_m(x_1,...,x_{m-1}, T) in T
                        for NUMERIC x_i, via the Semaev resultant recursion
                        evaluated by interpolation (never symbolically).
  * `factor_pattern` -- the multiset of irreducible-factor degrees of a
                        univariate polynomial over F_p (distinct-degree
                        factorisation).
  * `ZPoly`          -- exact multivariate polynomials over Z, used only for
                        the m = 3 discriminant identity, which is an identity
                        in Z[x1, x2, A, B] and is checked as such.

The object under test is defined in `../contract.md`; the claims these routines
are built to falsify are stated there and nowhere in this file.
"""

from __future__ import annotations

from itertools import product

# --------------------------------------------------------------------------
# exact multivariate polynomials over Z  (for the m = 3 discriminant identity)
# --------------------------------------------------------------------------


class ZPoly:
    """Sparse multivariate polynomial over Z. Exponent tuples -> coefficients.

    Variable order is fixed by the caller; `NVARS` below uses (x1, x2, A, B).
    """

    __slots__ = ("n", "c")

    def __init__(self, n: int, c: dict[tuple[int, ...], int] | None = None):
        self.n = n
        self.c = {k: v for k, v in (c or {}).items() if v}

    @classmethod
    def const(cls, n: int, v: int) -> "ZPoly":
        return cls(n, {(0,) * n: v})

    @classmethod
    def var(cls, n: int, i: int) -> "ZPoly":
        e = [0] * n
        e[i] = 1
        return cls(n, {tuple(e): 1})

    def __add__(self, o: "ZPoly") -> "ZPoly":
        r = dict(self.c)
        for k, v in o.c.items():
            r[k] = r.get(k, 0) + v
        return ZPoly(self.n, r)

    def __neg__(self) -> "ZPoly":
        return ZPoly(self.n, {k: -v for k, v in self.c.items()})

    def __sub__(self, o: "ZPoly") -> "ZPoly":
        return self + (-o)

    def __mul__(self, o: "ZPoly") -> "ZPoly":
        r: dict[tuple[int, ...], int] = {}
        for k1, v1 in self.c.items():
            for k2, v2 in o.c.items():
                k = tuple(a + b for a, b in zip(k1, k2))
                r[k] = r.get(k, 0) + v1 * v2
        return ZPoly(self.n, r)

    def __pow__(self, e: int) -> "ZPoly":
        r = ZPoly.const(self.n, 1)
        for _ in range(e):
            r = r * self
        return r

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ZPoly) and self.c == o.c

    def is_zero(self) -> bool:
        return not self.c


# --------------------------------------------------------------------------
# F_{p^2}
# --------------------------------------------------------------------------


class Fp2:
    """F_{p^2} = F_p[u]/(u^2 - ns) for a fixed quadratic non-residue ns.

    Elements are plain (a, b) tuples meaning a + b*u.  F_p embeds as (a, 0).
    """

    def __init__(self, p: int):
        if p % 4 == 3:
            ns = p - 1  # -1 is a non-residue exactly when p = 3 mod 4
        else:
            ns = next(n for n in range(2, p) if pow(n, (p - 1) // 2, p) == p - 1)
        self.p = p
        self.ns = ns

    # -- field operations ---------------------------------------------------
    def add(self, x, y):
        return ((x[0] + y[0]) % self.p, (x[1] + y[1]) % self.p)

    def sub(self, x, y):
        return ((x[0] - y[0]) % self.p, (x[1] - y[1]) % self.p)

    def neg(self, x):
        return ((-x[0]) % self.p, (-x[1]) % self.p)

    def mul(self, x, y):
        p, ns = self.p, self.ns
        return (
            (x[0] * y[0] + ns * x[1] * y[1]) % p,
            (x[0] * y[1] + x[1] * y[0]) % p,
        )

    def inv(self, x):
        p, ns = self.p, self.ns
        d = (x[0] * x[0] - ns * x[1] * x[1]) % p
        di = pow(d, p - 2, p)
        return ((x[0] * di) % p, (-x[1] * di) % p)

    def is_zero(self, x) -> bool:
        return x[0] % self.p == 0 and x[1] % self.p == 0

    def in_base_field(self, x) -> bool:
        return x[1] % self.p == 0

    def emb(self, a: int):
        return (a % self.p, 0)

    def sqrt(self, a: int):
        """A square root in F_{p^2} of a in F_p (both residue cases)."""
        p, ns = self.p, self.ns
        a %= p
        if a == 0:
            return (0, 0)
        if pow(a, (p - 1) // 2, p) == 1:
            return (sqrt_fp(a, p), 0)
        # a is a non-residue, so a/ns is a residue and sqrt(a) = sqrt(a/ns)*u
        b = (a * pow(ns, p - 2, p)) % p
        return (0, sqrt_fp(b, p))


def sqrt_fp(a: int, p: int) -> int:
    """Tonelli-Shanks square root in F_p (a must be a residue)."""
    a %= p
    if a == 0:
        return 0
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = next(n for n in range(2, p) if pow(n, (p - 1) // 2, p) == p - 1)
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = (t2 * t2) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, (b * b) % p
        t, r = (t * c) % p, (r * b) % p
    return r


# --------------------------------------------------------------------------
# elliptic curve y^2 = x^3 + A x + B, over F_p and over F_{p^2}
# --------------------------------------------------------------------------


class Curve:
    def __init__(self, p: int, A: int, B: int):
        assert p > 3, "short Weierstrass form requires characteristic > 3"
        self.p, self.A, self.B = p, A % p, B % p
        self.disc = (-16 * (4 * self.A**3 + 27 * self.B**2)) % p
        assert self.disc != 0, "singular curve"
        self.F2 = Fp2(p)

    def f(self, x: int) -> int:
        return (x * x % self.p * x + self.A * x + self.B) % self.p

    def chi(self, x: int) -> int:
        """Quadratic character of f(x): +1 split, -1 inert, 0 ramified."""
        v = self.f(x)
        if v == 0:
            return 0
        return 1 if pow(v, (self.p - 1) // 2, self.p) == 1 else -1

    # -- group law over F_{p^2} (covers F_p as the b = 0 subfield) ----------
    def add2(self, P, Q):
        """P + Q for points with F_{p^2} coordinates; None is the identity."""
        F = self.F2
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if F.is_zero(F.add(y1, y2)):
                return None
            num = F.mul(F.emb(3), F.mul(x1, x1))
            num = F.add(num, F.emb(self.A))
            den = F.mul(F.emb(2), y1)
        else:
            num = F.sub(y2, y1)
            den = F.sub(x2, x1)
        lam = F.mul(num, F.inv(den))
        x3 = F.sub(F.sub(F.mul(lam, lam), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)

    def neg2(self, P):
        return None if P is None else (P[0], self.F2.neg(P[1]))

    def lift2(self, x: int):
        """The point (x, sqrt(f(x))) over F_{p^2}. Defined for every x in F_p."""
        F = self.F2
        return (F.emb(x), F.sqrt(self.f(x)))

    def lift_fp(self, x: int):
        """(x, y) over F_p, or None if f(x) is a non-residue."""
        v = self.f(x)
        if v and pow(v, (self.p - 1) // 2, self.p) != 1:
            return None
        return (x, sqrt_fp(v, self.p))


def signed_sum_xs(curve: Curve, xs: list[int]) -> list:
    """{ x(eps_1 P_1 + ... + eps_k P_k) } in F_{p^2}, one per sign class.

    P_i = (x_i, sqrt(f(x_i))). The global sign flip is quotiented out by
    fixing eps_1 = +1, which is exactly the identification x(R) = x(-R).
    Returns a list of 2^(k-1) values; `None` marks a signed sum equal to O
    (a root that has escaped to infinity).
    """
    pts = [curve.lift2(x) for x in xs]
    out = []
    for eps in product([1, -1], repeat=len(xs) - 1):
        S = pts[0]
        for e, P in zip(eps, pts[1:]):
            S = curve.add2(S, P if e == 1 else curve.neg2(P))
        out.append(None if S is None else S[0])
    return out


# --------------------------------------------------------------------------
# S_m( x_1, ..., x_{m-1}, T ) for numeric x_i, as a coefficient list in T
# --------------------------------------------------------------------------


def s3_coeffs_in_T(curve: Curve, u: int, v: int) -> list[int]:
    """S_3(u, v, T) = c2 T^2 + c1 T + c0, coefficients in F_p."""
    p, A, B = curve.p, curve.A, curve.B
    c2 = pow(u - v, 2, p)
    c1 = (-2 * ((u + v) * (u * v + A) + 2 * B)) % p
    c0 = (pow(u * v - A, 2, p) - 4 * B * (u + v)) % p
    return [c0, c1, c2]


def _s3_coeffs_in_X_at_T(curve: Curve, w: int, t: int) -> list[int]:
    """S_3(w, t, X) as a degree-2 polynomial in X, at a numeric t."""
    return s3_coeffs_in_T(curve, w, t)  # S_3 is symmetric in its arguments


def _det_mod(M: list[list[int]], p: int) -> int:
    """Determinant over F_p by Gaussian elimination."""
    n = len(M)
    M = [row[:] for row in M]
    det = 1
    for i in range(n):
        piv = next((r for r in range(i, n) if M[r][i] % p), None)
        if piv is None:
            return 0
        if piv != i:
            M[i], M[piv] = M[piv], M[i]
            det = -det
        det = det * M[i][i] % p
        inv = pow(M[i][i], p - 2, p)
        for r in range(i + 1, n):
            if M[r][i]:
                fac = M[r][i] * inv % p
                for c in range(i, n):
                    M[r][c] = (M[r][c] - fac * M[i][c]) % p
    return det % p


def _sylvester_det(f: list[int], g: list[int], p: int) -> int:
    """Res_X(f, g) at the FORMAL degrees len(f)-1, len(g)-1.

    Formal degrees are kept fixed so that specialisation commutes with the
    determinant -- this is what makes the interpolation below valid even at
    the t where the leading coefficient of g vanishes.
    """
    df, dg = len(f) - 1, len(g) - 1
    n = df + dg
    M = [[0] * n for _ in range(n)]
    for i in range(dg):
        for j, c in enumerate(reversed(f)):
            M[i][i + j] = c % p
    for i in range(df):
        for j, c in enumerate(reversed(g)):
            M[dg + i][i + j] = c % p
    return _det_mod(M, p)


def _interpolate(pts: list[tuple[int, int]], p: int) -> list[int]:
    """Lagrange interpolation; returns coefficients low-to-high."""
    n = len(pts)
    coeffs = [0] * n
    for i, (xi, yi) in enumerate(pts):
        den = 1
        for j, (xj, _) in enumerate(pts):
            if i != j:
                den = den * (xi - xj) % p
        c = yi * pow(den, p - 2, p) % p
        basis = [1]
        for j, (xj, _) in enumerate(pts):
            if i == j:
                continue
            new = [0] * (len(basis) + 1)
            for k, b in enumerate(basis):
                new[k] = (new[k] - xj * b) % p
                new[k + 1] = (new[k + 1] + b) % p
            basis = new
        for k, b in enumerate(basis):
            coeffs[k] = (coeffs[k] + c * b) % p
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def semaev_T_poly(curve: Curve, xs: list[int]) -> list[int]:
    """S_m(x_1, ..., x_{m-1}, T) as coefficients in T, low-to-high, m = len(xs)+1.

    Uses Semaev's resultant recursion
        S_m(x_1..x_{m-1}, T) = Res_X( S_{m-1}(x_1..x_{m-2}, X), S_3(x_{m-1}, T, X) )
    with the outer polynomial obtained recursively at numeric arguments and the
    resultant recovered from 2^{m-2}+1 evaluations rather than symbolically.
    """
    p = curve.p
    if len(xs) < 2:
        raise ValueError("need m >= 3")
    if len(xs) == 2:
        return s3_coeffs_in_T(curve, xs[0], xs[1])
    inner = semaev_T_poly(curve, xs[:-1])  # degree 2^{m-3} in X
    d = len(inner) - 1
    bound = 2 * d  # degree bound in T
    if p <= bound + 1:
        raise ValueError("p too small for interpolation at this m")
    pts = []
    t = 0
    while len(pts) <= bound:
        g = _s3_coeffs_in_X_at_T(curve, xs[-1], t)
        pts.append((t, _sylvester_det(inner, g, p)))
        t += 1
    return _interpolate(pts, p)


def eval_poly_fp2(coeffs: list[int], z, F: Fp2):
    acc = F.emb(0)
    for c in reversed(coeffs):
        acc = F.add(F.mul(acc, z), F.emb(c))
    return acc


# --------------------------------------------------------------------------
# factorisation pattern over F_p
# --------------------------------------------------------------------------


def _poly_trim(a: list[int], p: int) -> list[int]:
    a = [c % p for c in a]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def _poly_mulmod(a, b, m, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                r[i + j] = (r[i + j] + ai * bj) % p
    return _poly_divmod(r, m, p)[1]


def _poly_divmod(a, b, p):
    a = _poly_trim(a, p)
    b = _poly_trim(b, p)
    if len(a) < len(b):
        return [0], a
    inv = pow(b[-1], p - 2, p)
    q = [0] * (len(a) - len(b) + 1)
    a = a[:]
    for i in range(len(a) - len(b), -1, -1):
        c = a[i + len(b) - 1] * inv % p
        q[i] = c
        if c:
            for j, bj in enumerate(b):
                a[i + j] = (a[i + j] - c * bj) % p
    return _poly_trim(q, p), _poly_trim(a, p)


def _poly_gcd(a, b, p):
    a, b = _poly_trim(a, p), _poly_trim(b, p)
    while b != [0]:
        a, b = b, _poly_divmod(a, b, p)[1]
    if a != [0]:
        inv = pow(a[-1], p - 2, p)
        a = [c * inv % p for c in a]
    return a


def _poly_derivative(a, p):
    return _poly_trim([i * a[i] % p for i in range(1, len(a))] or [0], p)


def is_squarefree(a: list[int], p: int) -> bool:
    a = _poly_trim(a, p)
    d = _poly_derivative(a, p)
    if d == [0]:
        return len(a) <= 1
    return len(_poly_gcd(a, d, p)) == 1


def _poly_powmod(base, e, m, p):
    acc = [1]
    base = _poly_divmod(base, m, p)[1]
    while e:
        if e & 1:
            acc = _poly_mulmod(acc, base, m, p)
        base = _poly_mulmod(base, base, m, p)
        e >>= 1
    return acc


def factor_pattern(a: list[int], p: int) -> dict[int, int]:
    """{degree: number of irreducible factors of that degree}, squarefree input.

    Distinct-degree factorisation: gcd(T^{p^k} - T, .) is the product of all
    irreducible factors whose degree divides k, so peeling k = 1, 2, 3, ...
    off a squarefree polynomial reads its degree profile without ever needing
    the factors themselves.
    """
    a = _poly_trim(a, p)
    inv = pow(a[-1], p - 2, p)
    a = [c * inv % p for c in a]
    out: dict[int, int] = {}
    xq = [0, 1]  # T
    k = 0
    while len(a) - 1 > 0:
        if 2 * (k + 1) > len(a) - 1:
            out[len(a) - 1] = out.get(len(a) - 1, 0) + 1  # what is left is irreducible
            break
        k += 1
        xq = _poly_powmod(xq, p, a, p)
        h = xq[:] + [0] * max(0, 2 - len(xq))
        h[1] = (h[1] - 1) % p
        g = _poly_gcd(h, a, p)
        if len(g) - 1 > 0:
            out[k] = (len(g) - 1) // k
            a = _poly_divmod(a, g, p)[0]
            xq = _poly_divmod(xq, a, p)[1] if len(a) - 1 > 0 else xq
    return out

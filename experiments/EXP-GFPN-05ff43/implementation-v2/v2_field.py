#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- field, curve and summation-polynomial core.

Generalised from the v1 module implementation/gfpn5_core.py (copied and edited,
AC-2 of DEC-20260923-e788a1 permits this). v1 fixed the extension degree at 5;
v2 needs n = 3 (fixture F-1..F-3), n = 4 (secondary fixture F-4) and n = 5 (the
ladder), with either a binomial modulus z^n - c or an arbitrary monic modulus
(F-4 uses the red team's GF(4111^4) modulus, read as DATA from
square_analogue_n4.json).

F_q = F_p[z]/(M(z)) through python-flint fq_default. Curves are general
Weierstrass cubics y^2 = x^3 + a2 x^2 + a4 x + a6 over F_q with the affine group
law. Summation polynomials are evaluated NUMERICALLY two independent ways (as
in v1) and cross-checked by self_test():
  (A) product formula  S_{m+1}(x_1..x_m, X) = S_m(x_1..x_m)^2 *
                        prod_{eps} (X - x(P_1 + eps_2 P_2 + ... + eps_m P_m));
  (B) resultant recursion S_n = Res_Y(S_3(x_1, x_2, Y), S_{n-1}(x_3.., Y)).

OpCount (DC-4 C-3): an optional counter can be attached to a Curve and to the
evaluators, so that per-target construction, descent and lifting are charged
with ONE instrument in every arm, including raw. Counts are raw counts of
F_q mul, F_q inv and F_p mul; the mult-equivalent uses
  1 F_q inv := 2.57 F_q mul  (Pornin, inputs/PORNIN-2022-274-ECGFP5/paper_fulltext.md
                              lines 522-523; the cycle table 128/49 = 2.61 is recorded next to it),
  1 F_q mul := n^2 + (n - 1) F_p mul (schoolbook plus reduction; 29 at n = 5, the v1
                              convention, LABELLED A CONVENTION).
"""
import flint

INV_OVER_MUL_TEXT = 2.57          # Pornin lines 522-523 ("about 2.57 times")
INV_OVER_MUL_TABLE = 128.0 / 49.0  # Pornin cycle table lines 501-519 (recorded only)


class OpCount:
    """Raw operation counters for construction, descent and lifting (DC-4 C-3)."""

    def __init__(self, n):
        self.n = n
        self.fq_mul = 0
        self.fq_inv = 0
        self.fq_add = 0
        self.fp_mul = 0
        self.fp_inv = 0

    def fp_mul_per_fq_mul(self):
        return self.n * self.n + (self.n - 1)

    def mult_equivalent_fp(self):
        c = self.fp_mul_per_fq_mul()
        return (self.fq_mul * c + self.fq_inv * INV_OVER_MUL_TEXT * c
                + self.fp_mul + self.fp_inv * INV_OVER_MUL_TEXT)

    def merge(self, other):
        for k in ("fq_mul", "fq_inv", "fq_add", "fp_mul", "fp_inv"):
            setattr(self, k, getattr(self, k) + getattr(other, k))

    def as_dict(self):
        c = self.fp_mul_per_fq_mul()
        return {
            "fq_mul": self.fq_mul, "fq_inv": self.fq_inv, "fq_add": self.fq_add,
            "fp_mul": self.fp_mul, "fp_inv": self.fp_inv,
            "fp_mult_equivalent": self.mult_equivalent_fp(),
            "pricing": {
                "fq_inv_in_fq_mul": INV_OVER_MUL_TEXT,
                "fq_inv_in_fq_mul_source": "inputs/PORNIN-2022-274-ECGFP5/paper_fulltext.md lines 522-523",
                "fq_inv_in_fq_mul_cycle_table_cross_check": round(INV_OVER_MUL_TABLE, 4),
                "fp_mul_per_fq_mul": c,
                "fp_mul_per_fq_mul_label": "CONVENTION: n^2 schoolbook + (n-1) reduction multiplications",
                "fp_inv_in_fp_mul": INV_OVER_MUL_TEXT,
                "fp_inv_note": "F_p inversions are priced like F_q inversions (2.57 mul); the raw count is always reported",
                "adds": "counted but not in the mult-equivalent",
            },
            "label": "counted F_q / F_p operations of construction, descent and lifting (measured counts, priced by the stated convention)",
        }


class Fq:
    """F_p[z]/(M) with M monic of degree n. `modulus` is a list of n+1 ints, low -> high."""

    def __init__(self, p, modulus, var="z"):
        self.p = int(p)
        self.modulus = [int(c) % self.p for c in modulus]
        assert self.modulus[-1] == 1, "modulus must be monic"
        self.n = len(self.modulus) - 1
        mod = flint.fmpz_mod_poly_ctx(self.p)(self.modulus)
        assert mod.is_irreducible(), "modulus not irreducible over F_p"
        self.ctx = flint.fq_default_ctx(self.p, self.n, modulus=mod, var=var)
        self.pctx = flint.fq_default_poly_ctx(self.ctx)
        self.z = self.ctx.gen()
        self.zero, self.one = self.ctx(0), self.ctx(1)
        self.q = self.p ** self.n

    @classmethod
    def binomial(cls, p, n, cmod):
        return cls(p, [(-cmod) % p] + [0] * (n - 1) + [1])

    def describe(self):
        terms = []
        for i in range(self.n, -1, -1):
            c = self.modulus[i]
            if c:
                terms.append(("" if (c == 1 and i) else str(c)) + ("z^%d" % i if i > 1 else ("z" if i == 1 else "")))
        return "F_%d[z]/(%s)" % (self.p, " + ".join(terms))

    def __call__(self, v):
        if isinstance(v, flint.fq_default):
            return v
        return self.ctx(int(v))

    def from_coeffs(self, cs):
        r = self.ctx(0)
        for c in reversed([int(x) for x in cs]):
            r = r * self.z + c
        return r

    def coeffs(self, a):
        cs = [int(c) for c in a.to_list()]
        return cs + [0] * (self.n - len(cs))

    def poly(self, cs):
        return self.pctx(list(cs))

    def in_Fp(self, a):
        return all(c == 0 for c in self.coeffs(a)[1:])

    def is_square(self, a):
        return a.is_square()

    def sqrt(self, a):
        if not a.is_square():
            return None
        r = a.sqrt()
        assert r * r == a
        return r

    def canonical_sqrt(self, a):
        """The square root whose coefficient vector is lexicographically smaller (a fixed,
        solver-independent choice; recorded wherever it is used)."""
        r = self.sqrt(a)
        if r is None:
            return None
        s = -r
        return r if self.coeffs(r) <= self.coeffs(s) else s

    def rand(self, rng):
        return self.from_coeffs([rng.randrange(self.p) for _ in range(self.n)])


class Curve:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over F_q; the point at infinity is None."""

    def __init__(self, F, a2, a4, a6, label="", counter=None):
        self.F, self.label = F, label
        self.a2, self.a4, self.a6 = F(a2), F(a4), F(a6)
        self.counter = counter

    def _c(self, mul=0, inv=0, add=0):
        if self.counter is not None:
            self.counter.fq_mul += mul
            self.counter.fq_inv += inv
            self.counter.fq_add += add

    def f(self, x):
        self._c(mul=2, add=3)
        return ((x + self.a2) * x + self.a4) * x + self.a6

    def on_curve(self, P):
        if P is None:
            return True
        return P[1] * P[1] == self.f(P[0])

    def neg(self, P):
        return None if P is None else (P[0], -P[1])

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 + y2 == 0:
                return None
            lam = (3 * x1 * x1 + 2 * self.a2 * x1 + self.a4) / (2 * y1)
            self._c(mul=3, inv=1, add=4)
        else:
            lam = (y2 - y1) / (x2 - x1)
            self._c(mul=1, inv=1, add=2)
        x3 = lam * lam - self.a2 - x1 - x2
        y3 = lam * (x1 - x3) - y1
        self._c(mul=2, add=5)
        return (x3, y3)

    def mul(self, k, P):
        k = int(k)
        if k < 0:
            k, P = -k, self.neg(P)
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def lift_x(self, x):
        fx = self.f(x)
        y = self.F.sqrt(fx)
        self._c(mul=1)          # square-root cost is not modelled; one mul recorded for the check
        return None if y is None else (x, y)

    def has_rational_2torsion(self):
        return len(self.F.poly([self.a6, self.a4, self.a2, 1]).roots()) > 0

    def random_point(self, rng):
        while True:
            P = self.lift_x(self.F.rand(rng))
            if P is not None:
                return P


# ------------------------------------------------------------ S_3 (general cubic)
def S3_coeffs(E, x1, x2):
    """[c0, c1, c2] of S_3(x1, x2, Y) = c2 Y^2 + c1 Y + c0 with c2 = (x1 - x2)^2 (v1 closed form)."""
    f1, f2 = E.f(x1), E.f(x2)
    d = x1 - x2
    s = E.a2 + x1 + x2
    d2 = d * d
    g = x1 * x1 + x1 * x2 + x2 * x2 + E.a2 * (x1 + x2) + E.a4
    E._c(mul=12, add=14)
    return [g * g - 2 * s * (f1 + f2) + s * s * d2, -(2 * (f1 + f2) - 2 * s * d2), d2]


def poly_eval(cs, x, counter=None):
    r = cs[-1]
    for c in reversed(cs[:-1]):
        r = r * x + c
    if counter is not None:
        counter.fq_mul += len(cs) - 1
        counter.fq_add += len(cs) - 1
    return r


def poly_from_roots(F, roots, lc, counter=None):
    cs = [lc]
    for r in roots:
        new = [F.zero] * (len(cs) + 1)
        for i, c in enumerate(cs):
            new[i + 1] += c
            new[i] -= c * r
        if counter is not None:
            counter.fq_mul += len(cs)
            counter.fq_add += 2 * len(cs)
        cs = new
    return cs


def lagrange_interp(F, nodes, values, counter=None):
    n = len(nodes)
    coef = list(values)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (nodes[i] - nodes[i - j])
            if counter is not None:
                counter.fq_inv += 1
                counter.fq_mul += 1
    poly = [coef[-1]]
    for k in range(n - 2, -1, -1):
        new = [F.zero] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new[i + 1] += c
            new[i] -= c * nodes[k]
        new[0] += coef[k]
        if counter is not None:
            counter.fq_mul += len(poly)
        poly = new
    return poly


def res_quad_poly(F, A, B, formal_degB, counter=None):
    """Res_Y(A, B), A quadratic, B of FORMAL degree formal_degB (v1 routine)."""
    a0, a1, a2 = A
    assert a2 != 0
    B = list(B)
    assert len(B) - 1 <= formal_degB
    while len(B) > 1 and B[-1] == 0:
        B.pop()
    if len(B) == 1 and B[0] == 0:
        return F.zero
    R = list(B)
    inv = 1 / a2
    if counter is not None:
        counter.fq_inv += 1
    while len(R) - 1 >= 2:
        lcR = R[-1]
        k = len(R) - 3
        fac = lcR * inv
        R[k] -= fac * a0
        R[k + 1] -= fac * a1
        R.pop()
        if counter is not None:
            counter.fq_mul += 3
        while len(R) > 1 and R[-1] == 0:
            R.pop()
    degR = len(R) - 1
    if degR == 0:
        base = R[0] * R[0]
    else:
        r0, r1 = R
        base = r1 * r1 * poly_eval(A, -r0 / r1, counter)
        if counter is not None:
            counter.fq_inv += 1
            counter.fq_mul += 2
    return a2 ** (formal_degB - degR) * base


def S_num_res(E, xs, counter=None):
    """S_len(xs) by the resultant recursion (point-free). len(xs) >= 2."""
    F = E.F
    n = len(xs)
    if n == 2:
        return xs[0] - xs[1]
    xs = list(xs)
    if xs[0] == xs[1]:
        j = next((k for k in range(2, n) if xs[k] != xs[0]), None)
        if j is None:
            d = 2 ** (n - 2)
            nodes = [xs[0] + F(i) for i in range(1, d + 2)]
            vals = [S_num_res(E, xs[:-1] + [t], counter) for t in nodes]
            return poly_eval(lagrange_interp(F, nodes, vals, counter), xs[-1], counter)
        xs[1], xs[j] = xs[j], xs[1]
    if n == 3:
        return poly_eval(S3_coeffs(E, xs[0], xs[1]), xs[2], counter)
    A = S3_coeffs(E, xs[0], xs[1])
    d = 2 ** (n - 3)
    nodes = [F(i) for i in range(1, d + 2)]
    vals = [S_num_res(E, list(xs[2:]) + [t], counter) for t in nodes]
    Bp = lagrange_interp(F, nodes, vals, counter)
    return res_quad_poly(F, A, Bp, d, counter)


def S_poly_res(E, xs, counter=None):
    """S_{len(xs)+1}(xs, X) as a coefficient list in X (degree 2^{len(xs)-1}), point-free."""
    deg = 2 ** (len(xs) - 1)
    nodes = [E.F(i) for i in range(1, deg + 2)]
    vals = [S_num_res(E, list(xs) + [t], counter) for t in nodes]
    return lagrange_interp(E.F, nodes, vals, counter)


def S_poly_grp(E, pts, counter=None):
    """S_{m+1}(x(P_1..P_m), X) by the product formula; lc = S_m(x_1..x_m)^2."""
    F = E.F
    m = len(pts)
    if m == 1:
        return [pts[0][0], -F.one]
    sums = [pts[0]]
    for P in pts[1:]:
        sums = [E.add(s, P) for s in sums] + [E.add(s, E.neg(P)) for s in sums]
    if any(s is None for s in sums):
        raise ZeroDivisionError("degenerate sample: a partial sum is O")
    lc = S_num_grp(E, pts, counter)
    if counter is not None:
        counter.fq_mul += 1
    return poly_from_roots(F, [s[0] for s in sums], lc * lc, counter)


def S_num_grp(E, pts, counter=None):
    m = len(pts)
    if m == 2:
        return pts[0][0] - pts[1][0]
    return poly_eval(S_poly_grp(E, pts[:-1], counter), pts[-1][0], counter)


def S_poly(E, xs, counter=None):
    """S_{m+1}(xs, X) as a coefficient list in X. Product formula when every x lifts to a
    point and no partial sum degenerates; otherwise the point-free resultant recursion."""
    pts = []
    for x in xs:
        P = E.lift_x(x)
        if P is None:
            pts = None
            break
        pts.append(P)
    if pts is not None and len(set(xs)) == len(xs):
        try:
            return S_poly_grp(E, pts, counter)
        except ZeroDivisionError:
            pass
    return S_poly_res(E, xs, counter)


def self_test(seed=1):
    """Evaluator cross-check (A) == (B) at n = 3, 4, 5 on toy fields. Development/validation
    only; prints no measurement."""
    import random
    rng = random.Random(seed)
    for (p, n, cmod) in ((1033, 3, 0), (1009, 4, None), (16777331, 5, 3)):
        if cmod == 0:
            ctx = flint.fmpz_mod_poly_ctx(p)
            cmod = next(c for c in range(2, p) if ctx([(-c) % p] + [0] * (n - 1) + [1]).is_irreducible())
        if cmod is None:
            # smallest irreducible monic z^4 + z + c over F_p (search; toy check only)
            ctx = flint.fmpz_mod_poly_ctx(p)
            c = next(c for c in range(1, p) if ctx([c, 1, 0, 0, 1]).is_irreducible())
            F = Fq(p, [c, 1, 0, 0, 1])
        else:
            F = Fq.binomial(p, n, cmod)
        E = Curve(F, 2, 7 * F.z + 3, 0, "selftest")
        for m in (2, 3, 4):
            pts = [E.random_point(rng) for _ in range(m)]
            xs = [P[0] for P in pts]
            g = S_poly_grp(E, pts)
            r = S_poly_res(E, xs)
            assert len(g) == len(r) == 2 ** (m - 1) + 1 and all(u == v for u, v in zip(g, r)), (p, n, m)
            R = pts[0]
            for P in pts[1:]:
                R = E.add(R, P)
            assert poly_eval(g, R[0]) == 0
        E0 = Curve(F, 0, F.rand(rng), F.rand(rng))
        x1, x2, x3 = F.rand(rng), F.rand(rng), F.rand(rng)
        a, b = E0.a4, E0.a6
        sem = (x1 - x2) ** 2 * x3 * x3 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3 + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
        assert poly_eval(S3_coeffs(E0, x1, x2), x3) == sem
    return True


if __name__ == "__main__":
    self_test()
    print("v2_field self-test: evaluators agree")

#!/usr/bin/env python3
"""Core arithmetic for EXP-GFPN-05ff43 (toy ladder over F_{p'^5}).

F_q = F_p[z]/(z^5 - cmod) via python-flint fq_default.  Curves are general
Weierstrass cubics y^2 = f(x) = x^3 + a2 x^2 + a4 x + a6 over F_q:
  * EcGFp5-shaped double-odd:  a2 = 2, a4 = b = c*z, a6 = 0   (2-torsion (0,0))
  * random with 2-torsion:     a2, a4 random, a6 = 0
  * random without 2-torsion:  a2 = 0, a4, a6 random, f irreducible over F_q

Summation polynomials are evaluated NUMERICALLY, two independent ways:
  (A) group-law product formula   S_n(x_1..x_{n-1}, X) = S_{n-1}(x_1..x_{n-1})^2
        * prod_{eps in {+-}^{n-2}} (X - x(P_1 + eps_2 P_2 + ... + eps_{n-1} P_{n-1}))
      (needs points P_i with x(P_i) = x_i over F_q);
  (B) resultant recursion         S_n = Res_Y(S_3(x_1, x_2, Y), S_{n-1}(x_3.., Y))
      (point-free; S_3 from the explicit closed form below).
Both are normalised identically (lc_X S_n = S_{n-1}^2, S_2 = x_1 - x_2), which
is proved by the resultant identity Res(A,B) = lc(A)^{deg B} prod_{A(a)=0} B(a).
The two evaluators are cross-checked in self_test().
"""
import flint

class Fq:
    """Wrapper around an fq_default context with cached constants and counters."""
    def __init__(self, p, cmod):
        self.p, self.cmod = p, cmod
        # modulus z^5 - cmod given as nmod_poly coefficients (low -> high)
        mod = flint.fmpz_mod_poly_ctx(p)([(-cmod) % p, 0, 0, 0, 0, 1])
        self.ctx = flint.fq_default_ctx(p, 5, modulus=mod, var="z")
        self.pctx = flint.fq_default_poly_ctx(self.ctx)
        self.z = self.ctx.gen()
        self.zero, self.one = self.ctx(0), self.ctx(1)
        self.q = p ** 5
        assert self.ctx.modulus() == mod
    def __call__(self, v):
        if isinstance(v, flint.fq_default):
            return v
        return self.ctx(int(v))
    def from_coeffs(self, cs):
        """cs = [c0..c4] in F_p -> c0 + c1 z + ... + c4 z^4"""
        r = self.ctx(0)
        for c in reversed(list(cs)):
            r = r * self.z + int(c)
        return r
    def coeffs(self, a):
        cs = [int(c) for c in a.to_list()]
        return cs + [0] * (5 - len(cs))
    def poly(self, cs):
        return self.pctx(list(cs))
    def in_Fp(self, a):
        cs = self.coeffs(a)
        return all(c == 0 for c in cs[1:])
    def is_square(self, a):
        return a.is_square()
    def sqrt(self, a):
        """Square root in F_q or None (flint fq_default sqrt; checked)."""
        if not a.is_square():
            return None
        r = a.sqrt()
        assert r * r == a
        return r
    def rand(self, rng):
        return self.from_coeffs([rng.randrange(self.p) for _ in range(5)])

# ------------------------------------------------------------------ curves
class Curve:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over F_q (affine + point at infinity None)."""
    def __init__(self, F, a2, a4, a6, label=""):
        self.F, self.a2, self.a4, self.a6, self.label = F, F(a2), F(a4), F(a6), label
    def f(self, x):
        return ((x + self.a2) * x + self.a4) * x + self.a6
    def on_curve(self, P):
        if P is None: return True
        return P[1] * P[1] == self.f(P[0])
    def neg(self, P):
        return None if P is None else (P[0], -P[1])
    def add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if y1 + y2 == 0: return None
            lam = (3 * x1 * x1 + 2 * self.a2 * x1 + self.a4) / (2 * y1)
        else:
            lam = (y2 - y1) / (x2 - x1)
        x3 = lam * lam - self.a2 - x1 - x2
        y3 = lam * (x1 - x3) - y1
        return (x3, y3)
    def mul(self, k, P):
        k = int(k)
        if k < 0: k, P = -k, self.neg(P)
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1": R = self.add(R, P)
        return R
    def lift_x(self, x):
        y = self.F.sqrt(self.f(x))
        return None if y is None else (x, y)
    def has_rational_2torsion(self):
        return len(self.F.poly([self.a6, self.a4, self.a2, 1]).roots()) > 0
    def two_torsion_points(self):
        return [(r, self.F.zero) for r, _ in self.F.poly([self.a6, self.a4, self.a2, 1]).roots()]
    def random_point(self, rng):
        while True:
            P = self.lift_x(self.F.rand(rng))
            if P is not None: return P

# -------------------------------------------------- S_3 closed form (general cubic)
def S3_coeffs(E, x1, x2):
    """Coefficients [c0, c1, c2] of S_3(x1, x2, Y) = c2 Y^2 + c1 Y + c0, normalised
    with c2 = (x1 - x2)^2.  Derived from x(P1 +- P2): with s = a2 + x1 + x2,
    S_3 = (x1-x2)^2 Y^2 - [2(f1+f2) - 2 s (x1-x2)^2] Y
          + [((f1-f2)/(x1-x2))^2 - 2 s (f1+f2) + s^2 (x1-x2)^2]."""
    f1, f2 = E.f(x1), E.f(x2)
    d = x1 - x2
    s = E.a2 + x1 + x2
    d2 = d * d
    # (f1-f2)/(x1-x2) = x1^2 + x1 x2 + x2^2 + a2 (x1 + x2) + a4
    g = x1 * x1 + x1 * x2 + x2 * x2 + E.a2 * (x1 + x2) + E.a4
    c2 = d2
    c1 = -(2 * (f1 + f2) - 2 * s * d2)
    c0 = g * g - 2 * s * (f1 + f2) + s * s * d2
    return [c0, c1, c2]

# ------------------------------------------------- univariate helpers over F_q
def poly_eval(cs, x):
    r = cs[-1]
    for c in reversed(cs[:-1]):
        r = r * x + c
    return r

def poly_from_roots(F, roots, lc):
    cs = [lc]
    for r in roots:
        new = [F.zero] * (len(cs) + 1)
        for i, c in enumerate(cs):
            new[i + 1] += c
            new[i] -= c * r
        cs = new
    return cs

def interp_nodes(F, n):
    """n distinct nodes 1..n in F_p (as F_q elements)."""
    return [F(i) for i in range(1, n + 1)]

def lagrange_interp(F, nodes, values):
    """Univariate interpolation over F_q; returns coefficient list low->high."""
    n = len(nodes)
    assert len(values) == n
    # Newton divided differences
    coef = list(values)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (nodes[i] - nodes[i - j])
    # convert Newton form to monomial form
    poly = [coef[-1]]
    for k in range(n - 2, -1, -1):
        # poly = poly*(X - nodes[k]) + coef[k]
        new = [F.zero] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new[i + 1] += c
            new[i] -= c * nodes[k]
        new[0] += coef[k]
        poly = new
    return poly

def res_quad_poly(F, A, B, formal_degB=None):
    """Res_Y(A, B) with A quadratic [a0,a1,a2], B a coefficient list whose FORMAL
    degree is formal_degB (default len(B)-1).  The formal degree matters: the
    summation-polynomial recursion is a polynomial identity in which B's degree
    may drop at special points, and Res uses lc(A)^{formal deg B}."""
    a0, a1, a2 = A
    assert a2 != 0
    B = list(B)
    degB = len(B) - 1 if formal_degB is None else formal_degB
    assert len(B) - 1 <= degB
    while len(B) > 1 and B[-1] == 0:
        B.pop()
    if len(B) == 1 and B[0] == 0:
        return F.zero
    R = list(B)
    inv = 1 / a2
    while len(R) - 1 >= 2:
        lcR = R[-1]
        k = len(R) - 1 - 2
        fac = lcR * inv
        R[k] -= fac * a0
        R[k + 1] -= fac * a1
        R.pop()
        while len(R) > 1 and R[-1] == 0:
            R.pop()
    degR = len(R) - 1
    if degR == 0:
        base = R[0] * R[0]           # Res(A, c) = c^2
    else:
        r0, r1 = R
        base = r1 * r1 * poly_eval(A, -r0 / r1)
    return a2 ** (degB - degR) * base

# -------------------------------------------------- evaluator (B): resultants
def S_num_res(E, xs):
    """S_len(xs) numeric via S_n = Res_Y(S_3(x1,x2,Y), S_{n-1}(x3..,Y)).  len>=3."""
    F = E.F
    n = len(xs)
    if n == 2:
        return xs[0] - xs[1]
    xs = list(xs)
    if xs[0] == xs[1]:
        # symmetric polynomial: move a distinct value into slot 1 (recursion needs x1 != x2)
        j = next((k for k in range(2, n) if xs[k] != xs[0]), None)
        if j is None:
            # all equal: interpolate in the last slot from nearby distinct values
            d = 2 ** (n - 2)
            nodes = [xs[0] + F(i) for i in range(1, d + 2)]
            vals = [S_num_res(E, xs[:-1] + [t]) for t in nodes]
            return poly_eval(lagrange_interp(F, nodes, vals), xs[-1])
        xs[1], xs[j] = xs[j], xs[1]
    if n == 3:
        return poly_eval(S3_coeffs(E, xs[0], xs[1]), xs[2])
    A = S3_coeffs(E, xs[0], xs[1])
    d = 2 ** (n - 3)                       # degree of S_{n-1} in its last variable
    nodes = interp_nodes(F, d + 1)
    vals = [S_num_res(E, list(xs[2:]) + [t]) for t in nodes]
    Bp = lagrange_interp(F, nodes, vals)
    return res_quad_poly(F, A, Bp, formal_degB=d)

def S_poly_res(E, xs, deg):
    """S_{len(xs)+1}(xs, X) as polynomial in X (coeff list) by evaluation at deg+1 nodes."""
    nodes = interp_nodes(E.F, deg + 1)
    vals = [S_num_res(E, list(xs) + [t]) for t in nodes]
    return lagrange_interp(E.F, nodes, vals)

# -------------------------------------------------- evaluator (A): group law
def S_poly_grp(E, pts):
    """S_{m+1}(x(P_1..P_m), X) as polynomial in X via the product formula.
    Returns coefficient list (degree 2^{m-1}).  Normalisation: lc = S_m(x_1..x_m)^2."""
    F = E.F
    m = len(pts)
    if m == 1:
        return [pts[0][0], -F.one]        # S_2(x1, X) = x1 - X
    # sums P1 +- P2 +- ... +- Pm
    sums = [pts[0]]
    for P in pts[1:]:
        sums = [E.add(s, P) for s in sums] + [E.add(s, E.neg(P)) for s in sums]
    for s in sums:
        assert s is not None, "degenerate sample (partial sum is O)"
    lc = S_num_grp(E, pts)
    return poly_from_roots(F, [s[0] for s in sums], lc * lc)

def S_num_grp(E, pts):
    """S_m(x(P_1..P_m)) numeric via product formula."""
    F = E.F
    m = len(pts)
    if m == 2:
        return pts[0][0] - pts[1][0]
    cs = S_poly_grp(E, pts[:-1])
    return poly_eval(cs, pts[-1][0])


# ------------------------------------------------------------ self test
def self_test(p=16777331, cmod=3, seed=1):
    import random
    rng = random.Random(seed)
    F = Fq(p, cmod)
    a = F.rand(rng); b = F.rand(rng)
    assert (a * b) / b == a and F.coeffs(F.from_coeffs(F.coeffs(a))) == F.coeffs(a)
    E = Curve(F, 2, 263 * F.z, 0, "test")
    P = E.random_point(rng); Q = E.random_point(rng)
    assert E.on_curve(E.add(P, Q)) and E.add(P, E.neg(P)) is None
    # S_3 vanishes at x(P+Q)
    assert poly_eval(S3_coeffs(E, P[0], Q[0]), E.add(P, Q)[0]) == 0
    assert poly_eval(S3_coeffs(E, P[0], Q[0]), E.add(P, E.neg(Q))[0]) == 0
    # Semaev classical S_3 for a2 = 0 curve
    E0 = Curve(F, 0, a, b)
    x1, x2, x3 = F.rand(rng), F.rand(rng), F.rand(rng)
    sem = (x1 - x2) ** 2 * x3 * x3 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3 + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
    assert poly_eval(S3_coeffs(E0, x1, x2), x3) == sem
    # cross-check evaluators (A) vs (B) for S_4, S_5, S_6
    for n in (4, 5, 6):
        pts = [E.random_point(rng) for _ in range(n - 1)]
        xs = [pt[0] for pt in pts]
        cs_g = S_poly_grp(E, pts)
        deg = 2 ** (n - 2)
        cs_r = S_poly_res(E, xs, deg)
        assert len(cs_g) == deg + 1 == len(cs_r), (len(cs_g), len(cs_r))
        assert all(u == v for u, v in zip(cs_g, cs_r)), f"S_{n} evaluators disagree"
        # vanishing at a genuine sum
        R = pts[0]
        for pt in pts[1:]:
            R = E.add(R, pt)
        assert poly_eval(cs_g, R[0]) == 0
        # symmetry in the first n-1 variables
        perm = pts[1:] + pts[:1]
        assert all(u == v for u, v in zip(cs_g, S_poly_grp(E, perm)))
    print("gfpn5_core self-test ok (S_4..S_6 product formula == resultant recursion)")

if __name__ == "__main__":
    self_test()

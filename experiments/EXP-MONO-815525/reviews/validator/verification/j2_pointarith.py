"""J2: DIRECT POINT-ARITHMETIC verification in the g-irreducible regime.

Builds K = F_p[X]/(g) (g = the instance's own residual cubic, irreducible by
selection), L = K[Y]/(Y^2 - n) = F_{p^6} when the y-lift is not K-rational,
lifts the three Frobenius-conjugate x-coordinates to genuine points of E, and
computes the four signed sums P1 +- P2 +- P3 by ordinary group-law addition.

No part of run_census.py is imported or reused.
"""
import json, sys, random
sys.path.insert(0, ".")
from ffield import norm, deg, mulp, divmodp, gcdp, sub as psub, has_root_Fp
from qe_indep import qe_from_my_S4, to_Fp, F3, s3_of_e   # my own S_4 evaluation


# ------------------------------------------------------------------ K = F_p^3
class K3:
    def __init__(self, p, e1, e2, e3):
        self.p = p
        self.e1, self.e2, self.e3 = e1 % p, e2 % p, e3 % p
        self.q = p ** 3
        self.one = [1, 0, 0]
        self.zero = [0, 0, 0]
    def mul(self, a, b):
        p, e1, e2, e3 = self.p, self.e1, self.e2, self.e3
        r = [0] * 5
        for i in range(3):
            ai = a[i]
            if ai:
                for j in range(3):
                    r[i + j] += ai * b[j]
        # X^3 = e1 X^2 - e2 X + e3
        for k in (4, 3):
            c = r[k] % p
            if c:
                r[k] = 0
                r[k - 1] += c * e1
                r[k - 2] -= c * e2
                r[k - 3] += c * e3
        return [r[0] % p, r[1] % p, r[2] % p]
    def add(self, a, b):
        p = self.p
        return [(a[0]+b[0]) % p, (a[1]+b[1]) % p, (a[2]+b[2]) % p]
    def sub(self, a, b):
        p = self.p
        return [(a[0]-b[0]) % p, (a[1]-b[1]) % p, (a[2]-b[2]) % p]
    def neg(self, a):
        p = self.p
        return [(-a[0]) % p, (-a[1]) % p, (-a[2]) % p]
    def smul(self, k, a):
        p = self.p
        return [k*a[0] % p, k*a[1] % p, k*a[2] % p]
    def pw(self, a, e):
        r, b = self.one[:], a[:]
        while e:
            if e & 1: r = self.mul(r, b)
            b = self.mul(b, b); e >>= 1
        return r
    def inv(self, a):
        assert any(a), "inverse of 0 in K"
        return self.pw(a, self.q - 2)
    def eq(self, a, b):
        return [x % self.p for x in a] == [x % self.p for x in b]
    def is_zero(self, a):
        return not any(x % self.p for x in a)
    def is_square(self, a):
        return self.eq(self.pw(a, (self.q - 1) // 2), self.one)
    def sqrt(self, a):
        """Tonelli-Shanks over K (q = p^3).  Returns r with r^2 = a, or None."""
        if self.is_zero(a): return self.zero[:]
        if not self.is_square(a): return None
        q = self.q
        s, t = 0, q - 1
        while t % 2 == 0:
            t //= 2; s += 1
        if s == 1:
            return self.pw(a, (q + 1) // 4)
        rng = random.Random(12345)
        while True:
            z = [rng.randrange(self.p) for _ in range(3)]
            if not self.is_zero(z) and not self.is_square(z): break
        m, c, tt, r = s, self.pw(z, t), self.pw(a, t), self.pw(a, (t + 1) // 2)
        while not self.eq(tt, self.one):
            i, t2 = 0, tt[:]
            while not self.eq(t2, self.one):
                t2 = self.mul(t2, t2); i += 1
            b = self.pw(c, 1 << (m - i - 1))
            m, c = i, self.mul(b, b)
            tt = self.mul(tt, c); r = self.mul(r, b)
        return r


# ------------------------------------------------------- L = K[Y]/(Y^2-n)
class L6:
    """Quadratic extension of K.  Elements (a,b) meaning a + b*Y, Y^2 = n."""
    def __init__(self, K, n):
        self.K, self.n = K, n
    def emb(self, a):  return (a[:], self.K.zero[:])
    def add(self, u, v): return (self.K.add(u[0], v[0]), self.K.add(u[1], v[1]))
    def sub(self, u, v): return (self.K.sub(u[0], v[0]), self.K.sub(u[1], v[1]))
    def neg(self, u):    return (self.K.neg(u[0]), self.K.neg(u[1]))
    def mul(self, u, v):
        K = self.K
        ac = K.mul(u[0], v[0]); bd = K.mul(u[1], v[1])
        return (K.add(ac, K.mul(self.n, bd)),
                K.sub(K.mul(K.add(u[0], u[1]), K.add(v[0], v[1])), K.add(ac, bd)))
    def inv(self, u):
        K = self.K
        d = K.sub(K.mul(u[0], u[0]), K.mul(self.n, K.mul(u[1], u[1])))
        di = K.inv(d)
        return (K.mul(u[0], di), K.neg(K.mul(u[1], di)))
    def is_zero(self, u): return self.K.is_zero(u[0]) and self.K.is_zero(u[1])
    def eq(self, u, v):   return self.K.eq(u[0], v[0]) and self.K.eq(u[1], v[1])
    def pw(self, u, e):
        r, b = self.emb(self.K.one), u
        while e:
            if e & 1: r = self.mul(r, b)
            b = self.mul(b, b); e >>= 1
        return r
    def in_K(self, u): return self.K.is_zero(u[1])


# ------------------------------------------------------------ E over L
def ec_add(L, A, B, P, Q):
    """Short-Weierstrass addition over L.  None == the point at infinity O."""
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if L.eq(x1, x2):
        if L.is_zero(L.add(y1, y2)):
            return None                       # Q = -P
        # doubling
        num = L.add(L.mul(L.emb([3,0,0]), L.mul(x1, x1)), L.emb(A))
        den = L.mul(L.emb([2,0,0]), y1)
        lam = L.mul(num, L.inv(den))
    else:
        lam = L.mul(L.sub(y2, y1), L.inv(L.sub(x2, x1)))
    x3 = L.sub(L.sub(L.mul(lam, lam), x1), x2)
    y3 = L.sub(L.mul(lam, L.sub(x1, x3)), y1)
    return (x3, y3)

def ec_neg(L, P):
    return None if P is None else (P[0], L.neg(P[1]))

def on_curve(L, A, B, P):
    if P is None: return True
    x, y = P
    lhs = L.mul(y, y)
    rhs = L.add(L.add(L.mul(x, L.mul(x, x)), L.mul(L.emb(A), x)), L.emb(B))
    return L.eq(lhs, rhs)


# ------------------------------------------------------------ one instance
def verify_instance(p, A, B, e1, e2, e3, verbose=False):
    out = {"p": p, "A": A, "B": B, "e": [e1, e2, e3]}
    gpoly = [(-e3) % p, e2 % p, (-e1) % p, 1]
    out["g_irreducible"] = not has_root_Fp(gpoly, p)
    K = K3(p, e1, e2, e3)
    Av, Bv = [A % p, 0, 0], [B % p, 0, 0]

    # a K-non-square n, to build L = K[Y]/(Y^2-n) = F_{p^6}
    rng = random.Random(98765 + p + e1 * 7 + e2 * 13 + e3 * 17)
    while True:
        n = [rng.randrange(p) for _ in range(3)]
        if not K.is_zero(n) and not K.is_square(n): break
    L = L6(K, n)

    x1 = [0, 1, 0]                          # the generator: a root of g
    fx1 = K.add(K.add(K.mul(x1, K.mul(x1, x1)), K.mul(Av, x1)), Bv)
    out["f_x1_is_square_in_Fp3"] = K.is_square(fx1)
    if K.is_square(fx1):
        y1K = K.sqrt(fx1); Y1 = L.emb(y1K)
    else:
        r = K.sqrt(K.mul(fx1, K.inv(n)))
        Y1 = (K.zero[:], r)                 # y1 = r*Y, y1^2 = r^2 n = f(x1)
    X1 = L.emb(x1)
    P1 = (X1, Y1)
    assert on_curve(L, Av, Bv, P1), "P1 not on E"
    P2 = (L.pw(X1, p), L.pw(Y1, p))
    P3 = (L.pw(X1, p * p), L.pw(Y1, p * p))
    out["P2_on_curve"] = on_curve(L, Av, Bv, P2)
    out["P3_on_curve"] = on_curve(L, Av, Bv, P3)
    # x-coords are the three conjugate roots of g, all distinct
    xs = [P1[0], P2[0], P3[0]]
    out["x_coords_distinct"] = not (L.eq(xs[0], xs[1]) or L.eq(xs[0], xs[2])
                                    or L.eq(xs[1], xs[2]))
    out["x_coords_in_Fp3"] = all(L.in_K(x) for x in xs)
    # each x_i really is a root of g
    def evg(u):
        v = L.emb(K.zero)
        for c in reversed(gpoly):
            v = L.add(L.mul(v, u), L.emb([c % p, 0, 0]))
        return v
    out["x_coords_are_roots_of_g"] = all(L.is_zero(evg(x)) for x in xs)
    # Frobenius^3 on P1: +P1 (y in F_p^3) or -P1 (y in F_p^6 \ F_p^3)
    P4 = (L.pw(X1, p ** 3), L.pw(Y1, p ** 3))
    out["frob3_P1_is_plus_P1"] = L.eq(P4[1], Y1)

    # ---- the four signed sums, eps_1 fixed to +1 -------------------------
    classes = [(1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1)]
    sums, at_inf, xvals = {}, [], {}
    for eps in classes:
        S = None
        for e, P in zip(eps, (P1, P2, P3)):
            S = ec_add(L, Av, Bv, S, P if e == 1 else ec_neg(L, P))
        sums[eps] = S
        if S is None:
            at_inf.append(eps)
        else:
            assert on_curve(L, Av, Bv, S), "signed sum left the curve"
            xvals[eps] = S[0]
    out["n_sign_classes_at_infinity"] = len(at_inf)
    out["classes_at_infinity"] = ["".join("+" if s > 0 else "-" for s in c)
                                  for c in at_inf]
    out["exactly_one_at_infinity"] = (len(at_inf) == 1)

    # ---- consistency with Q_e -------------------------------------------
    cs, _F, _1, _2, _3 = qe_from_my_S4(p, A, B, e1, e2, e3)
    qe = to_Fp(cs, p)
    q = norm(qe[:], p) if qe else None
    out["Qe_lands_in_Fp"] = qe is not None
    out["Qe_degree"] = deg(q) if q is not None else None
    out["Qe_coeffs_low_to_high"] = q
    out["deg_drop_equals_n_at_infinity"] = (4 - deg(q) == len(at_inf))
    out["c4_is_S3_of_e_squared"] = ((qe[4] - s3_of_e(p, A, B, e1, e2, e3) ** 2) % p == 0)
    # every finite signed-sum x-coordinate must be a root of Q_e
    roots_ok = []
    for eps, xv in xvals.items():
        v = L.emb(K.zero)
        for c in reversed(q):
            v = L.add(L.mul(v, xv), L.emb([c % p, 0, 0]))
        roots_ok.append(L.is_zero(v))
    out["all_finite_sums_are_roots_of_Qe"] = all(roots_ok)
    # and Q_e (monic) = prod over finite classes of (T - x_eps)
    lc = q[-1]
    inv = pow(lc, p - 2, p)
    monic = [c * inv % p for c in q]
    prod = [L.emb(K.one)]
    poly = [L.emb(K.one)]
    for eps, xv in xvals.items():
        newp = [L.emb(K.zero)] * (len(poly) + 1)
        for i, cf in enumerate(poly):
            newp[i + 1] = L.add(newp[i + 1], cf)
            newp[i] = L.sub(newp[i], L.mul(cf, xv))
        poly = newp
    ok = len(poly) == len(monic)
    if ok:
        for i, cf in enumerate(poly):
            if not L.eq(cf, L.emb([monic[i] % p, 0, 0])): ok = False
    out["Qe_monic_equals_prod_over_finite_classes"] = ok
    # which x-coordinates are F_p-rational
    def in_Fp(u):
        return L.in_K(u) and u[0][1] % p == 0 and u[0][2] % p == 0
    out["n_finite_sums_with_Fp_rational_x"] = sum(1 for xv in xvals.values() if in_Fp(xv))
    # Frobenius action on the four classes (as x-values), for cycle type
    out["fixed_class_is_at_infinity"] = None
    return out

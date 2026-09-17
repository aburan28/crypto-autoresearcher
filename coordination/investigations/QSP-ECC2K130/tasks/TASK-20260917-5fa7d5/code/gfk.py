"""Arithmetic in K = F_2[z]/(f), factorization over GF(2), and root extraction.

Elements of K are ints < 2^n (bit i = coefficient of z^i).
Polynomials over K are Python lists, index = degree, no trailing zeros.
"""
import random
from gf2poly import (deg, clmul, sqr, polymod, polydivmod, polygcd, polyegcd,
                     frob_pow_mod, is_irreducible)

class Field:
    def __init__(self, f):
        self.f = f
        self.n = deg(f)
    def mul(self, a, b):
        return polymod(clmul(a, b), self.f)
    def sqr(self, a):
        return polymod(sqr(a), self.f)
    def inv(self, a):
        g, u, _ = polyegcd(a, self.f)
        assert g == 1, 'not invertible'
        return polymod(u, self.f)
    def pow2k(self, a, k):
        for _ in range(k):
            a = self.sqr(a)
        return a
    def evalpoly_f2(self, p, x):
        """evaluate p in GF(2)[X] at x in K (Horner)."""
        r = 0
        for i in range(p.bit_length() - 1, -1, -1):
            r = self.mul(r, x)
            if (p >> i) & 1:
                r ^= 1
        return r
    def rand(self):
        return random.getrandbits(self.n)

# ---------- factorization over GF(2) (bit-packed) ----------

def squarefree_part(p):
    """radical-ish: p / gcd(p, p'), enough here since we only feed squarefree p."""
    return p

def ddf(p):
    """distinct-degree factorization: yields (d, prod of irreducible factors of degree d).
    p must be squarefree."""
    out = []
    x_q = 2                     # X^(2^0) mod p... we iterate
    h = polymod(2, p)           # X
    fpoly = p
    d = 0
    while deg(fpoly) >= 2 * (d + 1):
        d += 1
        h = polymod(sqr(h), fpoly)      # h = X^(2^d) mod fpoly
        g = polygcd(fpoly, h ^ 2)       # gcd(fpoly, X^(2^d) - X)
        if deg(g) > 0:
            out.append((d, g))
            q, r = polydivmod(fpoly, g)
            assert r == 0
            fpoly = q
            h = polymod(h, fpoly)
    if deg(fpoly) > 0:
        out.append((deg(fpoly), fpoly))
    return out

def edf(p, d, rng=None):
    """equal-degree factorization over GF(2): p squarefree, all irreducible factors
    of degree exactly d.  Cantor-Zassenhaus, char-2 trace variant."""
    rng = rng or random
    n = deg(p)
    if n == d:
        return [p]
    out = []
    stack = [p]
    while stack:
        cur = stack.pop()
        if deg(cur) == d:
            out.append(cur)
            continue
        while True:
            u = rng.getrandbits(deg(cur))
            if u <= 1:
                continue
            # T = u + u^2 + u^4 + ... + u^(2^(d-1)) mod cur
            t = u % (1 << deg(cur))
            acc = t
            for _ in range(d - 1):
                t = polymod(sqr(t), cur)
                acc ^= t
            g = polygcd(cur, acc)
            if 0 < deg(g) < deg(cur):
                q, r = polydivmod(cur, g)
                assert r == 0
                stack.append(g)
                stack.append(q)
                break
    return out

def factor_squarefree(p):
    """full factorization of a squarefree p over GF(2) -> list of irreducibles."""
    res = []
    for d, g in ddf(p):
        res.extend(edf(g, d))
    return res

# ---------- polynomials over K ----------

def kp_norm(a):
    while a and a[-1] == 0:
        a.pop()
    return a

def kp_from_f2(p, n):
    return kp_norm([(p >> i) & 1 for i in range(p.bit_length())])

def kp_mulmod(F, a, b, m):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    r[i + j] ^= F.mul(ai, bj)
    kp_norm(r)
    return kp_mod(F, r, m) if m else r

def kp_mod(F, a, m):
    a = list(a)
    dm = len(m) - 1
    inv_lead = F.inv(m[-1])
    while len(a) - 1 >= dm and a:
        kp_norm(a)
        if not a or len(a) - 1 < dm:
            break
        shift = len(a) - 1 - dm
        c = F.mul(a[-1], inv_lead)
        for i, mi in enumerate(m):
            if mi:
                a[i + shift] ^= F.mul(c, mi)
        kp_norm(a)
    return a

def kp_gcd(F, a, b):
    a, b = kp_norm(list(a)), kp_norm(list(b))
    while b:
        a, b = b, kp_mod(F, a, b)
        kp_norm(b)
    if a:
        inv = F.inv(a[-1])
        a = [F.mul(c, inv) for c in a]
    return a

def roots_of_f2_irreducible_in_K(F, q, max_tries=200):
    """q irreducible over GF(2) of degree m | n; return ALL m roots in K.
    Method: Cantor-Zassenhaus with the absolute trace Tr_{K/F_2}(r*X), then
    the remaining roots are the Frobenius conjugates of the one found."""
    m = deg(q)
    n = F.n
    assert n % m == 0
    if m == 1:
        return [q & 1]                       # q = X + c  ->  root c
    # X^(2^i) mod q over GF(2), i = 0..n-1
    S = []
    cur = polymod(2, q)
    for i in range(n):
        S.append(cur)
        cur = polymod(sqr(cur), q)
    qk = kp_from_f2(q, n)
    cur_poly = qk
    tries = 0
    while len(cur_poly) - 1 > 1:
        tries += 1
        assert tries < max_tries, 'CZ failed to split'
        r = F.rand()
        rp = [0] * n
        v = r
        for i in range(n):
            rp[i] = v
            v = F.sqr(v)
        # T(X) = sum_i r^(2^i) * S_i(X)
        T = [0] * m
        for i in range(n):
            si = S[i]
            if si:
                ri = rp[i]
                for j in range(si.bit_length()):
                    if (si >> j) & 1:
                        T[j] ^= ri
        kp_norm(T)
        if not T:
            continue
        g = kp_gcd(F, cur_poly, kp_mod(F, T, cur_poly))
        if 0 < len(g) - 1 < len(cur_poly) - 1:
            cur_poly = g
    # cur_poly = X + c  (monic)  -> root = c
    root = cur_poly[0]
    orbit = [root]
    v = F.sqr(root)
    while v != root:
        orbit.append(v)
        v = F.sqr(v)
    assert len(orbit) == m, (len(orbit), m)
    return orbit

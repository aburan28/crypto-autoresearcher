"""Weil descent of Semaev S_3 (binary curve y^2+xy=x^3+a2 x^2+a6) restricted to V x V.
Variables: a_0..a_{l-1} (X1 = sum a_i v_i), b_0..b_{l-1} (X2 = sum b_j v_j); index of b_j is l+j.
Also brute-forces the Boolean solution count (ordered pairs (X1,X2) in V x V)."""
import random, sys
from gf2n import Field, find_modulus

class Subspace:
    def __init__(self, F, basis):
        self.F, self.basis = F, basis
        # echelon form for membership tests
        self.ech = {}
        for v in basis:
            x = v
            while x:
                hb = x.bit_length() - 1
                if hb in self.ech:
                    x ^= self.ech[hb]
                else:
                    self.ech[hb] = x
                    break
            assert x, "basis dependent"
    def contains(self, x):
        while x:
            hb = x.bit_length() - 1
            if hb not in self.ech:
                return False
            x ^= self.ech[hb]
        return True
    def elements(self):
        l = len(self.basis)
        cur = 0
        yield 0
        for g in range(1, 1 << l):  # Gray code
            bit = (g & -g).bit_length() - 1
            cur ^= self.basis[bit]
            yield cur

def poly_basis(F, l):
    return [1 << i for i in range(l)]

def random_basis(F, l, rng):
    while True:
        B = [rng.randrange(1, 1 << F.n) for _ in range(l)]
        try:
            Subspace(F, B)
            return B
        except AssertionError:
            pass

def s3_descent(F, V, xR, a6):
    """Return list of n Boolean polys; each poly = list of monomial masks."""
    n, l = F.n, len(V.basis)
    v = V.basis
    coef = {}  # mask -> F element
    xR2 = F.sq(xR)
    for i in range(l):
        for j in range(l):
            c = F.mul(F.sq(v[i]), F.sq(v[j])) ^ F.mul(xR, F.mul(v[i], v[j]))
            if c:
                coef[(1 << i) | (1 << (l + j))] = coef.get((1 << i) | (1 << (l + j)), 0) ^ c
    for i in range(l):
        c = F.mul(xR2, F.sq(v[i]))
        coef[1 << i] = coef.get(1 << i, 0) ^ c
        coef[1 << (l + i)] = coef.get(1 << (l + i), 0) ^ c
    coef[0] = coef.get(0, 0) ^ a6
    polys = []
    for k in range(n):
        polys.append(sorted(m for m, c in coef.items() if (c >> k) & 1))
    return polys

def count_solutions(F, V, xR, a6):
    """#{(X1,X2) in V x V : S3(X1,X2,xR)=0}."""
    cnt = 0
    xR2 = F.sq(xR)
    for X1 in V.elements():
        # S3 = X2^2 (X1+xR)^2 + X2 X1 xR + (X1 xR)^2 + a6
        A = F.sq(X1 ^ xR)
        Bc = F.mul(X1, xR)
        C = F.sq(Bc) ^ a6
        if A == 0:  # X1 == xR: Bc*X2 + C = 0
            if Bc == 0:
                if C == 0:
                    cnt += 1 << len(V.basis)
                continue
            X2 = F.mul(C, F.inv(Bc))
            cnt += V.contains(X2)
            continue
        if Bc == 0:  # X1 == 0: X2^2 = C/A
            X2 = F.pow(F.mul(C, F.inv(A)), 1 << (F.n - 1))
            cnt += V.contains(X2)
            continue
        Ai = F.inv(A)
        c1 = F.mul(Bc, Ai)
        c0 = F.mul(C, Ai)
        # X2 = c1*Y, Y^2+Y = c0/c1^2
        rhs = F.mul(c0, F.inv(F.sq(c1)))
        if F.trace(rhs):
            continue
        Y = F.halftrace(rhs)
        for y in (Y, Y ^ 1):
            X2 = F.mul(c1, y)
            cnt += V.contains(X2)
    return cnt

def random_curve_point_x(F, a2, a6, rng):
    while True:
        x = rng.randrange(1, 1 << F.n)
        # y^2 + xy = x^3 + a2 x^2 + a6 solvable iff Tr(x + a2 + a6/x^2) = 0
        if F.trace(x ^ a2 ^ F.mul(a6, F.inv(F.sq(x)))) == 0:
            return x

def write_system(polys, N, fh):
    fh.write(f"{N} {len(polys)}\n")
    for p in polys:
        fh.write(str(len(p)) + " " + " ".join(format(m, "x") for m in p) + "\n")

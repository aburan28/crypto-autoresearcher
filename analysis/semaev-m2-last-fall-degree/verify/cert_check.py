#!/usr/bin/env python3
"""Certificate checker (implementation B) for claims of the form "1 is not in W_D(F)".

usage: cert_check.py [--t3] CERT n f_hex a2 a6_hex z_hex basis_hex...
(the arguments of indep_verify.py, or of indep_verify_t3.py with --t3, with the certificate file in place of D;
 D is read from the file. --t3 is Semaev's chained system (5) for t = 3, with u free: S_3(u,X1,X2) = S_3(u,X3,z) = 0.)

W_D(F) is the smallest subspace W of B_{<=D} (B = F_2[x_1..x_N]/(x_i^2 + x_i)) with
  (1) every equation f of F with deg f <= D is in W, and
  (2) x*g is in W for every g in W with deg g <= D-1 and every variable x.
A certificate is a linear map pi : B_{<=D} -> F_2^nq, produced by code/lfdclose2.c (export_cert),
or by any other program. Put U = ker pi. This program does NOT trust how the certificate was made.
It rebuilds F from the curve parameters (Moebius interpolation of S_3 values, no code shared with
code/) and checks:
  (C0) the monomials listed are exactly those of degree <= D in N variables, each once;
       the rows of pi include every unit vector of F_2^nq, so pi is onto and codim U = nq;
  (C1) pi(f) = 0 for every equation f of F;
  (C2) pi(x*u) = 0 for every variable x and every u in U with deg u <= D-1;
  (C3) pi(1) != 0.
(C1) and (C2) say that U satisfies (1) and (2), so W_D(F) is contained in U. With (C3), 1 is not in
W_D(F), and codim W_D(F) >= nq.
"""
import sys, struct, random, time, operator, itertools
from array import array
from functools import reduce
from math import comb

# This verifier uses assertions for all certificate predicates. Python -O and
# PYTHONOPTIMIZE remove them, so reject optimized execution before parsing any
# untrusted certificate or printing a VALID result.
if not __debug__:
    raise SystemExit("cert_check.py requires assertions; optimized Python is unsupported")


def mk_field(n, f):
    def mulmod(a, b):
        r = 0
        for i in range(b.bit_length()):
            if (b >> i) & 1:
                r ^= a << i
        for d in range(r.bit_length() - 1, n - 1, -1):
            if (r >> d) & 1:
                r ^= f << (d - n)
        return r
    def power(a, e):
        r = 1
        while e:
            if e & 1:
                r = mulmod(r, a)
            a = mulmod(a, a); e >>= 1
        return r
    def tr(a):
        t = a; s = a
        for _ in range(n - 1):
            s = mulmod(s, s); t ^= s
        assert t in (0, 1)
        return t
    return mulmod, power, tr


def descend(n, f, a2, a6, xR, basis):
    """Equations of S_3(X1, X2, xR) = 0 over F_2: list of n polynomials, each a list of monomial masks.
    Variable i < l is the coefficient a_i of X1 = sum a_i basis[i]; variable l + i is that of X2."""
    l = len(basis)
    N = 2 * l
    mul, pw, tr = mk_field(n, f)
    sq = lambda a: mul(a, a)
    inv = lambda a: pw(a, (1 << n) - 2)

    def S3(x1, x2, x3):
        t = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
        return sq(t) ^ mul(mul(x1, x2), x3) ^ a6

    rng = random.Random(12345)
    if n % 2 == 1:   # self-test of S_3 against the group law (needs the half-trace, odd n only)
        def htr(c):
            h = 0; s = c
            for _ in range((n + 1) // 2):
                h ^= s; s = sq(sq(s))
            return h
        def rand_point():
            while True:
                x = rng.randrange(1, 1 << n)
                c = mul(mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6, inv(sq(x)))
                if tr(c) == 0:
                    z = htr(c)
                    return (x, mul(x, z))
        def add(P, Q):
            (x1, y1), (x2, y2) = P, Q
            if x1 == x2:
                return None
            lam = mul(y1 ^ y2, inv(x1 ^ x2))
            x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ a2
            return (x3, mul(lam, x1 ^ x3) ^ x3 ^ y1)
        for _ in range(10):
            P, Q = rand_point(), rand_point()
            R = add(P, Q)
            if R:
                assert S3(P[0], Q[0], R[0]) == 0, "S_3 does not vanish on P+Q"
        assert sum(S3(rng.randrange(1 << n), rng.randrange(1 << n), rng.randrange(1 << n)) == 0 for _ in range(50)) < 3

    def Fval(point):
        x1 = x2 = 0
        for i in range(l):
            if (point >> i) & 1:
                x1 ^= basis[i]
            if (point >> (l + i)) & 1:
                x2 ^= basis[i]
        return S3(x1, x2, xR)

    monos = [0] + [1 << i for i in range(N)] + [(1 << i) | (1 << j) for i in range(N) for j in range(i + 1, N)]
    val = {m: Fval(m) for m in monos}
    coef = {}
    for m in monos:   # Moebius inversion over the subsets of m
        c = 0; sub = m
        while True:
            c ^= val[sub]
            if sub == 0:
                break
            sub = (sub - 1) & m
        if c:
            coef[m] = c
    for _ in range(200):   # the degree <= 2 expansion must agree with S_3 at random points
        p = rng.randrange(1 << N); acc = 0
        for m, c in coef.items():
            if m & p == m:
                acc ^= c
        assert acc == Fval(p), "descended polynomial disagrees with S_3"
    return N, [[m for m, c in coef.items() if (c >> k) & 1] for k in range(n)]


def descend_t3(n, f, a2, a6, z, basis):
    """Equations of S_3(u,X1,X2) = S_3(u,X3,z) = 0 over F_2: 2n polynomials of degree <= 3.
    Variable i < n is the coefficient of t^i in u; variable n + r*k + j is the coefficient of basis[j] in X_{r+1}."""
    k = len(basis); N = n + 3 * k
    mul, pw, tr = mk_field(n, f)
    sq = lambda a: mul(a, a)
    inv = lambda a: pw(a, (1 << n) - 2)
    piv = {}                    # solver for y^2 + y = c by linear algebra, any n
    for i in range(n):
        y = 1 << i; v = sq(y) ^ y
        while v:
            hb = v.bit_length() - 1
            if hb in piv:
                pv, py = piv[hb]; v ^= pv; y ^= py
            else:
                piv[hb] = (v, y); break
    def as_solve(c):
        y = 0
        while c:
            hb = c.bit_length() - 1
            if hb not in piv:
                return None
            pv, py = piv[hb]; c ^= pv; y ^= py
        return y
    def S3(x1, x2, x3):
        t = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
        return sq(t) ^ mul(mul(x1, x2), x3) ^ a6
    rng = random.Random(4242)
    def rand_point():
        while True:
            x = rng.randrange(1, 1 << n)
            zz = as_solve(mul(mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6, inv(sq(x))))
            if zz is not None:
                return (x, mul(x, zz))
    def add(P, Q):
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2:
            return None
        lam = mul(y1 ^ y2, inv(x1 ^ x2)); x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ a2
        return (x3, mul(lam, x1 ^ x3) ^ x3 ^ y1)
    for _ in range(8):
        P, Q = rand_point(), rand_point(); R = add(P, Q)
        if R:
            assert S3(P[0], Q[0], R[0]) == 0, "S_3 does not vanish on P+Q"
    def Fvals(point):
        u = point & ((1 << n) - 1); X = []
        for r in range(3):
            x = 0
            for j in range(k):
                if (point >> (n + r * k + j)) & 1:
                    x ^= basis[j]
            X.append(x)
        return S3(u, X[0], X[1]), S3(u, X[2], z)
    monos = [0]
    for d in (1, 2, 3):
        for comb in itertools.combinations(range(N), d):
            monos.append(sum(1 << i for i in comb))
    val = {m: Fvals(m) for m in monos}
    coef = [{}, {}]
    for m in monos:
        c0 = c1 = 0; sub = m
        while True:
            v = val[sub]; c0 ^= v[0]; c1 ^= v[1]
            if sub == 0:
                break
            sub = (sub - 1) & m
        if c0:
            coef[0][m] = c0
        if c1:
            coef[1][m] = c1
    for _ in range(150):
        p = rng.randrange(1 << N); want = Fvals(p)
        for e in range(2):
            acc = 0
            for m, c in coef[e].items():
                if m & p == m:
                    acc ^= c
            assert acc == want[e], "descended polynomial disagrees with S_3 (degree > 3?)"
    return N, [[m for m, c in coef[e].items() if (c >> b) & 1] for e in range(2) for b in range(n)]


def main():
    args = sys.argv[1:]
    t3 = "--t3" in args
    if t3:
        args.remove("--t3")
    path = args[0]
    n = int(args[1]); f = int(args[2], 16); a2 = int(args[3]); a6 = int(args[4], 16)
    xR = int(args[5], 16); basis = [int(x, 16) for x in args[6:]]
    t0 = time.time()
    N, polys = (descend_t3 if t3 else descend)(n, f, a2, a6, xR, basis)
    print(f"descent ok: N = {N} variables, {len(polys)} equations, {sum(len(p) for p in polys)} terms [{time.time()-t0:.1f}s]", flush=True)

    data = open(path, "rb").read()
    cN, D, ncols, nq = struct.unpack_from("<4q", data, 0)
    assert cN == N, f"certificate has {cN} variables, the instance has {N}"
    off = 32
    masks = struct.unpack_from(f"<{ncols}Q", data, off); off += 8 * ncols
    qw = max(1, (nq + 63) // 64); rb = 8 * qw
    assert len(data) == off + ncols * rb, "certificate file has the wrong length"
    rows = [int.from_bytes(data[off + i * rb: off + (i + 1) * rb], "little") for i in range(ncols)]
    del data
    col = {m: i for i, m in enumerate(masks)}

    # (C0) the columns are exactly the monomials of degree <= D, and pi is onto F_2^nq
    assert len(col) == ncols, "repeated monomial in the certificate"
    assert ncols == sum(comb(N, d) for d in range(D + 1)), "wrong number of monomials"
    assert all(m < (1 << N) and bin(m).count("1") <= D for m in masks), "monomial out of range"
    rowset = set(rows)
    assert all(r < (1 << nq) for r in rowset), "pi has a bit outside F_2^nq"
    assert all((1 << q) in rowset for q in range(nq)), "pi is not onto F_2^nq"
    print(f"(C0) ok: D = {D}, {ncols} monomials, pi onto F_2^{nq}", flush=True)

    # (C1) every equation lies in U = ker pi
    for k, p in enumerate(polys):
        acc = 0
        for m in p:
            acc ^= rows[col[m]]
        assert acc == 0, f"(C1) fails: pi(equation {k}) != 0"
    print(f"(C1) ok: pi(f) = 0 for all {len(polys)} equations", flush=True)

    # (C3) 1 is not in U
    assert rows[col[0]] != 0, "(C3) fails: pi(1) = 0"
    print("(C3) ok: pi(1) != 0", flush=True)

    # (C2) closure: a basis of K = U cap B_{<=D-1}, then pi(x*h) = 0 for every variable x and h in the basis
    low = [i for i, m in enumerate(masks) if bin(m).count("1") <= D - 1]
    qmask = (1 << nq) - 1
    piv = {}; kernel = []
    for j, ci in enumerate(low):
        v = rows[ci] | (1 << (nq + j))
        while True:
            lowpart = v & qmask
            if not lowpart:
                kernel.append(v >> nq); break
            hb = lowpart.bit_length() - 1
            p = piv.get(hb)
            if p is None:
                piv[hb] = v; break
            v ^= p
    del piv
    print(f"     U cap B_(<={D-1}) has dimension {len(kernel)} (pi restricted to B_(<={D-1}) has rank {len(low) - len(kernel)}) [{time.time()-t0:.1f}s]", flush=True)
    idx = []
    for h in kernel:
        a = array("H") if len(low) < 65536 else array("I")
        while h:
            b = h & -h
            a.append(b.bit_length() - 1)
            h ^= b
        idx.append(a)
    del kernel
    print(f"     basis weights: max {max(len(a) for a in idx) if idx else 0}, total {sum(len(a) for a in idx)} [{time.time()-t0:.1f}s]", flush=True)
    for x in range(N):
        xb = 1 << x
        T = [rows[col[masks[ci] | xb]] for ci in low]
        get = T.__getitem__
        for a in idx:
            assert reduce(operator.xor, map(get, a), 0) == 0, f"(C2) fails for variable {x}"
        if x % 8 == 7 or x == N - 1:
            print(f"     variable {x+1}/{N} ok [{time.time()-t0:.1f}s]", flush=True)
    print(f"(C2) ok: U is closed under multiplication by every variable on degree <= {D-1}")
    print(f"VALID: 1 is not in W_{D}(F), and codim W_{D}(F) >= {nq}   [{time.time()-t0:.1f}s]")


if __name__ == "__main__":
    main()

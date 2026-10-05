#!/usr/bin/env python3
"""Independent verifier for Semaev's chained system (5) with t = 3 (no shared code with gen3.py,
s3c3count.c or lfdclose2.c):
    S3(u, X1, X2) = 0,  S3(u, X3, z) = 0,   u in F_{2^n} free,  X1, X2, X3 in V,  dim V = k.
Variables: u_i (bit i, i < n: u = sum u_i t^i), x_{r,j} (bit n + r k + j).
  1. S3 self-test on the curve group law;
  2. descent by Moebius interpolation over monomials of degree <= 3, cross-checked at random points;
  3. Boolean solution count by enumerating (X1, X2) in V x V, solving for u, then for X3;
  4. exact closure W_D (Python integers).
usage: indep_verify_t3.py n f_hex a2 a6_hex z_hex D basis_hex...   (env NOCOUNT=1 skips step 3)"""
import sys, random, itertools, time, os

def main():
    n = int(sys.argv[1]); f = int(sys.argv[2], 16); a2 = int(sys.argv[3]); a6 = int(sys.argv[4], 16)
    z = int(sys.argv[5], 16); D = int(sys.argv[6]); basis = [int(x, 16) for x in sys.argv[7:]]
    k = len(basis); N = n + 3 * k
    def mul(a, b):
        r = 0
        for i in range(b.bit_length()):
            if (b >> i) & 1: r ^= a << i
        for d in range(r.bit_length() - 1, n - 1, -1):
            if (r >> d) & 1: r ^= f << (d - n)
        return r
    def pw(a, e):
        r = 1
        while e:
            if e & 1: r = mul(r, a)
            a = mul(a, a); e >>= 1
        return r
    inv = lambda a: pw(a, (1 << n) - 2)
    sq = lambda a: mul(a, a)
    def tr(a):
        t = a; s = a
        for _ in range(n - 1):
            s = sq(s); t ^= s
        assert t in (0, 1); return t
    # Artin-Schreier solver y^2 + y = c by linear algebra (any n)
    piv = {}
    for i in range(n):
        y = 1 << i; v = sq(y) ^ y
        while v:
            hb = v.bit_length() - 1
            if hb in piv: pv, py = piv[hb]; v ^= pv; y ^= py
            else: piv[hb] = (v, y); break
    def as_solve(c):
        y = 0
        while c:
            hb = c.bit_length() - 1
            if hb not in piv: return None
            pv, py = piv[hb]; c ^= pv; y ^= py
        return y
    rng = random.Random(4242)
    def S3(x1, x2, x3):
        t = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
        return sq(t) ^ mul(mul(x1, x2), x3) ^ a6
    # ---- 1. S3 self-test on the curve ----
    def rand_point():
        while True:
            x = rng.randrange(1, 1 << n)
            c = mul(mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6, inv(sq(x)))
            zz = as_solve(c)
            if zz is not None: return (x, mul(x, zz))
    def add(P, Q):
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2: return None
        lam = mul(y1 ^ y2, inv(x1 ^ x2)); x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ a2
        return (x3, mul(lam, x1 ^ x3) ^ x3 ^ y1)
    for _ in range(8):
        P, Q = rand_point(), rand_point(); R = add(P, Q)
        if R: assert S3(P[0], Q[0], R[0]) == 0
    print("selftest ok")
    # ---- 2. descent by interpolation ----
    def unpack(point):
        u = point & ((1 << n) - 1)
        X = []
        for r in range(3):
            x = 0
            for j in range(k):
                if (point >> (n + r * k + j)) & 1: x ^= basis[j]
            X.append(x)
        return u, X
    def Fvals(point):
        u, X = unpack(point)
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
            if sub == 0: break
            sub = (sub - 1) & m
        if c0: coef[0][m] = c0
        if c1: coef[1][m] = c1
    for _ in range(150):
        p = rng.randrange(1 << N); want = Fvals(p)
        for e in range(2):
            acc = 0
            for m, c in coef[e].items():
                if m & p == m: acc ^= c
            assert acc == want[e], "descent mismatch (degree > 3?)"
    polys = [[m for m, c in coef[e].items() if (c >> b) & 1] for e in range(2) for b in range(n)]
    print(f"descent ok: equations {len(polys)}, vars {N}, max degree {max(bin(m).count('1') for p in polys for m in p)}")
    # ---- 3. solution count: (X1, X2) -> u -> X3 ----
    if not os.environ.get("NOCOUNT"):
        t0 = time.time()
        ech = {}
        for v in basis:
            x = v
            while x:
                hb = x.bit_length() - 1
                if hb in ech: x ^= ech[hb]
                else: ech[hb] = x; break
        def inV(x):
            while x:
                hb = x.bit_length() - 1
                if hb not in ech: return False
                x ^= ech[hb]
            return True
        els = [0]
        for v in basis: els = els + [e ^ v for e in els]
        def roots(x, w):   # all Y with S3(x, Y, w) = 0
            A = sq(x ^ w); Bc = mul(x, w); C = sq(Bc) ^ a6
            if A == 0:
                if Bc == 0: return None if C == 0 else []
                return [mul(C, inv(Bc))]
            if Bc == 0: return [pw(mul(C, inv(A)), 1 << (n - 1))]
            c1 = mul(Bc, inv(A)); c0 = mul(C, inv(A)); y = as_solve(mul(c0, inv(sq(c1))))
            return [] if y is None else [mul(c1, y), mul(c1, y ^ 1)]
        cnt = 0
        for X1 in els:
            for X2 in els:
                us = roots(X1, X2)            # S3(X1, u, X2) = S3(u, X1, X2)
                assert us is not None, "degenerate (u free)"
                for u in us:
                    x3s = roots(u, z)
                    assert x3s is not None
                    cnt += sum(1 for x3 in x3s if inV(x3))
        print(f"boolean solutions: {cnt}  [{time.time()-t0:.1f}s]")
    # ---- 4. closure W_D ----
    t0 = time.time()
    order = []
    for d in range(D + 1):
        for comb in itertools.combinations(range(N), d):
            order.append(sum(1 << i for i in comb))
    pos = {m: i for i, m in enumerate(order)}
    lowlim = sum(1 for m in order if bin(m).count("1") <= D - 1)
    pivd = {}
    def ins(r):
        while r:
            hb = r.bit_length() - 1
            p = pivd.get(hb)
            if p is None: pivd[hb] = r; return hb
            r ^= p
        return None
    def times_var(r, v):
        vb = 1 << v; out = 0
        while r:
            low = r & -r; i = low.bit_length() - 1; r ^= low
            out ^= 1 << pos[order[i] | vb]
        return out
    queue = []
    for p in polys:
        if not p: continue
        dp = max(bin(m).count("1") for m in p)
        for d in range(0, D - dp + 1):
            for comb in itertools.combinations(range(N), d):
                mm = sum(1 << i for i in comb); acc = {}
                for t in p: acc[t | mm] = acc.get(t | mm, 0) ^ 1
                h = ins(sum(1 << pos[m] for m, c in acc.items() if c))
                if h is not None and h < lowlim: queue.append(h)
    done = set(); nmult = 0
    while queue:
        h = queue.pop()
        if h in done: continue
        done.add(h); g = pivd[h]; nmult += 1
        for v in range(N):
            h2 = ins(times_var(g, v))
            if h2 is not None and h2 < lowlim: queue.append(h2)
        if 0 in pivd: break
        if nmult % 2000 == 0: print(f"  ... multiplied {nmult} low pivots, rank {len(pivd)} [{time.time()-t0:.0f}s]", flush=True)
    dims = [sum(1 for h in pivd if bin(order[h]).count("1") <= d) for d in range(D + 1)]
    print(f"W{D} dims {dims} contains_one {int(0 in pivd)} rank {len(pivd)} cols {len(order)} [{time.time()-t0:.1f}s]")

if __name__ == "__main__":
    main()

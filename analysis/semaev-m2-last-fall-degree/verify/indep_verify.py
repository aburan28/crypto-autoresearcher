#!/usr/bin/env python3
"""Independent verifier (no shared code with the generator / C closure).

For one instance (n, f, a2, a6, xR, basis of V) of the m = 2 Semaev system
S_3(X1, X2, xR) = 0, X1, X2 in V (Weil descent to F_2, Boolean ring):
  1. self-test S_3 against the curve group law on random points;
  2. build the descended system by Moebius interpolation of S_3 evaluations
     (not by symbolic expansion), and cross-check it at random points;
  3. count Boolean solutions by an algorithm different from the generator's
     (enumerate s = X1 + X2, solve X1^2 + s X1 = P(s) via the half-trace);
  4. compute the exact degree-D closure W_D (multiply-by-variable closure in
     B_{<=D}, B = F2[x]/(x_i^2 + x_i)) with Python integers and report whether
     1 in W_D, plus dims of W_D cap B_{<=d}.
Usage: indep_verify.py n f_hex a2 a6_hex xR_hex D basis_hex...
Environment: FIX=var=val[,var=val] restricts the system (skips the count);
NOCOUNT=1 skips the count; NOCLOSURE=1 skips the closure; COUNT_SHARD=i/k
counts only the s-values with index g = i mod k (sum the k shard counts).
"""
import sys, random, itertools, time

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
            if e & 1: r = mulmod(r, a)
            a = mulmod(a, a); e >>= 1
        return r
    def inverse(a):
        return power(a, (1 << n) - 2)
    def tr(a):
        t = a; s = a
        for _ in range(n - 1):
            s = mulmod(s, s); t ^= s
        assert t in (0, 1)
        return t
    return mulmod, power, inverse, tr, None

def main():
    n = int(sys.argv[1]); f = int(sys.argv[2], 16); a2 = int(sys.argv[3]); a6 = int(sys.argv[4], 16)
    xR = int(sys.argv[5], 16); D = int(sys.argv[6]); basis = [int(x, 16) for x in sys.argv[7:]]
    l = len(basis); N = 2 * l
    mul, pw, inv, tr, _ = mk_field(n, f)
    sq = lambda a: mul(a, a)
    def htr(c):
        h = 0; s = c
        for _ in range((n + 1) // 2):
            h ^= s; s = sq(sq(s))
        return h
    assert n % 2 == 1
    rng = random.Random(12345)
    for _ in range(20):
        c = rng.randrange(1 << n); h = htr(c)
        assert sq(h) ^ h == c ^ tr(c), "half-trace identity failed"
    # ---- 1. S_3 self-test on the curve y^2 + xy = x^3 + a2 x^2 + a6 ----
    def S3(x1, x2, x3):
        t = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
        return sq(t) ^ mul(mul(x1, x2), x3) ^ a6
    def rand_point():
        while True:
            x = rng.randrange(1, 1 << n)
            rhs = mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6
            c = mul(rhs, inv(sq(x)))         # z^2 + z = c with y = x z
            if tr(c) == 0:
                z = htr(c); return (x, mul(x, z))
    def add(P, Q):
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2: return None
        lam = mul(y1 ^ y2, inv(x1 ^ x2))
        x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ a2
        y3 = mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)
    for _ in range(10):
        P, Q = rand_point(), rand_point()
        for (x, y) in (P, Q):
            assert sq(y) ^ mul(x, y) == mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6
        R = add(P, Q)
        if R: assert S3(P[0], Q[0], R[0]) == 0, "S_3 does not vanish on P+Q"
    assert sum(S3(rng.randrange(1 << n), rng.randrange(1 << n), rng.randrange(1 << n)) == 0 for _ in range(50)) < 3
    xr_on_curve = tr(xR ^ a2 ^ mul(a6, inv(sq(xR)))) == 0
    print(f"selftest ok; xR on curve: {xr_on_curve}")
    # ---- 2. descent by Moebius interpolation over monomials of degree <= 2 ----
    def X(bits):  # bits: tuple of 0/1 of length l
        v = 0
        for i, b in enumerate(bits):
            if b: v ^= basis[i]
        return v
    def F(point):  # point: int bitmask over N vars -> S3 value in K
        x1 = 0; x2 = 0
        for i in range(l):
            if (point >> i) & 1: x1 ^= basis[i]
            if (point >> (l + i)) & 1: x2 ^= basis[i]
        return S3(x1, x2, xR)
    coef = {}
    monos = [0] + [1 << i for i in range(N)] + [(1 << i) | (1 << j) for i in range(N) for j in range(i + 1, N)]
    val = {m: F(m) for m in monos}
    for m in monos:
        c = 0; sub = m
        while True:
            c ^= val[sub]
            if sub == 0: break
            sub = (sub - 1) & m
        if c: coef[m] = c
    # random cross-check (degree <= 2 claim)
    for _ in range(200):
        p = rng.randrange(1 << N); acc = 0
        for m, c in coef.items():
            if m & p == m: acc ^= c
        assert acc == F(p), "descended polynomial disagrees with S_3 evaluation"
    polys = [[m for m, c in coef.items() if (c >> k) & 1] for k in range(n)]
    import os
    fixspec = os.environ.get("FIX", "")
    if fixspec:
        fix = {int(a.split("=")[0]): int(a.split("=")[1]) for a in fixspec.split(",")}
        keep = [v for v in range(N) if v not in fix]; newidx = {v: i for i, v in enumerate(keep)}
        fm = sum(1 << v for v in fix); om = sum(1 << v for v, b in fix.items() if b)
        newpolys = []
        for p in polys:
            acc = {}
            for m in p:
                if (m & fm) & ~om: continue
                r = m & ~fm; nm = 0
                for v in range(N):
                    if (r >> v) & 1: nm |= 1 << newidx[v]
                acc[nm] = acc.get(nm, 0) ^ 1
            newpolys.append([m for m, c in acc.items() if c])
        polys = newpolys; N = len(keep)
        print(f"restricted by {fix}: now {N} variables")
    print(f"descent ok: {len(coef)} monomials with nonzero K-coefficient; equations {n}, vars {N}")
    # ---- 3. Boolean solution count via the s-enumeration (different algorithm) ----
    t0 = time.time()
    skip_count = bool(os.environ.get("FIX", "") or os.environ.get("NOCOUNT", ""))
    def _count():
        alpha = mul(a6, inv(sq(xR)))
        # S3 = xR^2 (u^2+u+s^2+alpha), u = X1X2/xR.  Solutions: Tr(s)=Tr(alpha), u = H(s^2+alpha)+eps.
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
        cnt = 0
        shard = os.environ.get("COUNT_SHARD", "")
        si, sk = (int(x) for x in shard.split("/")) if shard else (0, 1)
        for g in range(si, 1 << l, sk):
            s = X(tuple((g >> i) & 1 for i in range(l)))
            if tr(s) != tr(alpha): continue
            u0 = htr(sq(s) ^ alpha)
            for eps in (0, 1):
                P = mul(xR, u0 ^ eps)            # = X1 X2
                # X1 + X2 = s, X1 X2 = P  ->  X1^2 + s X1 + P = 0
                if s == 0:
                    # X1 = X2, X1^2 = P
                    X1 = pw(P, 1 << (n - 1))
                    if inV(X1): cnt += 1
                    continue
                c = mul(P, inv(sq(s)))
                if tr(c): continue
                y = htr(c)
                for yy in (y, y ^ 1):
                    X1 = mul(s, yy)
                    if inV(X1) and inV(X1 ^ s): cnt += 1
        tag = f" in shard {si}/{sk}" if shard else ""
        print(f"boolean solutions (ordered pairs){tag}: {cnt}  [{time.time()-t0:.1f}s]")
    if not skip_count:
        _count()
    else:
        print("boolean solution count skipped (restricted system or NOCOUNT)")
    # ---- 4. exact closure W_D with Python ints ----
    if os.environ.get("NOCLOSURE", ""):
        print("closure skipped (NOCLOSURE)"); return
    t0 = time.time()
    order = []  # bit position -> monomial mask; low degree = low bits
    for d in range(D + 1):
        for comb in itertools.combinations(range(N), d):
            m = 0
            for i in comb: m |= 1 << i
            order.append(m)
    pos = {m: i for i, m in enumerate(order)}
    lowlim = sum(1 for m in order if bin(m).count("1") <= D - 1)   # bits < lowlim are degree <= D-1
    def topoly(terms):
        r = 0
        for m in terms: r ^= 1 << pos[m]
        return r
    piv = {}
    def reduce_insert(r):
        while r:
            hb = r.bit_length() - 1
            p = piv.get(hb)
            if p is None:
                piv[hb] = r; return hb
            r ^= p
        return None
    mulcache = {}
    def times_var(r, v):
        vb = 1 << v; out = 0
        while r:
            low = r & -r; i = low.bit_length() - 1; r ^= low
            out ^= 1 << pos[order[i] | vb]
        return out
    # Macaulay rows
    deg_of = lambda terms: max(bin(m).count("1") for m in terms)
    queue_low = []
    for p in polys:
        if not p: continue
        dp = deg_of(p)
        for d in range(0, D - dp + 1):
            for comb in itertools.combinations(range(N), d):
                mm = 0
                for i in comb: mm |= 1 << i
                hb = reduce_insert(topoly([t | mm for t in p]))
                if hb is not None and hb < lowlim: queue_low.append(hb)
    done = set()
    while queue_low:
        hb = queue_low.pop()
        if hb in done: continue
        done.add(hb)
        g = piv[hb]
        for v in range(N):
            h2 = reduce_insert(times_var(g, v))
            if h2 is not None and h2 < lowlim: queue_low.append(h2)
        if 0 in piv: break
    one = 0 in piv
    dims = [sum(1 for h in piv if bin(order[h]).count("1") <= d) for d in range(D + 1)]
    print(f"W{D} dims {dims} contains_one {int(one)} rank {len(piv)} cols {len(order)} [{time.time()-t0:.1f}s]")

if __name__ == "__main__":
    main()

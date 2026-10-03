#!/usr/bin/env python3
"""Check the explicit degree-3 falls of the m = 2 Semaev descent (theorem dossier, Lemma 3.3)
against the exact closure W_3, on one instance (n odd).

Builds, inside B = F2[a,b]/(x^2+x):
  span(F)                                   (descended equations, by Moebius interpolation)
  ell_0 * B_{<=1}                           (ell_0 = Tr(S/z^2), affine-linear)
  q_{i,lam} = Tr(lam X_i w), lam in V-perp  (claimed in W_3, degree <= 2)
  q_s = Tr(s w) + Tr(alpha) omega           (claimed in W_3, degree <= 2)
  r_j = omega a_j + Tr(mu_j X_1 w)          (claimed in M_3, degree <= 3)
and checks membership/degree claims and whether the explicit degree<=2 span equals W_3 cap B_{<=2}.
usage: falls_check.py n f_hex a2 a6_hex z_hex basis_hex..."""
import sys, itertools, random

def main():
    n = int(sys.argv[1]); f = int(sys.argv[2], 16); a6 = int(sys.argv[4], 16); z = int(sys.argv[5], 16)
    basis = [int(x, 16) for x in sys.argv[6:]]; k = len(basis); N = 2 * k
    assert n % 2 == 1
    def mul(a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            a <<= 1; b >>= 1
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
    def tr(a):
        t = a; s = a
        for _ in range(n - 1):
            s = mul(s, s); t ^= s
        return t
    def H(c):
        h = 0; s = c
        for _ in range((n + 1) // 2):
            h ^= s; s = mul(s, s); s = mul(s, s)
        return h
    sq = lambda a: mul(a, a)
    # K-polynomials in B_K: dict mask -> K element ; variables a_j = bit j, b_j = bit k+j
    def kmul(P, Q):
        R = {}
        for m1, c1 in P.items():
            for m2, c2 in Q.items():
                m = m1 | m2; c = mul(c1, c2)
                if c: R[m] = R.get(m, 0) ^ c
        return {m: c for m, c in R.items() if c}
    def kadd(*Ps):
        R = {}
        for P in Ps:
            for m, c in P.items(): R[m] = R.get(m, 0) ^ c
        return {m: c for m, c in R.items() if c}
    def kscale(P, c):
        return {m: mul(v, c) for m, v in P.items() if mul(v, c)}
    def Tr_(P):  # coefficientwise trace -> F2 polynomial as set of monomials
        return frozenset(m for m, c in P.items() if tr(c))
    X1 = {1 << j: basis[j] for j in range(k)}
    X2 = {1 << (k + j): basis[j] for j in range(k)}
    s = kadd(X1, X2)
    zi = inv(z); alpha = mul(a6, sq(zi))
    # S = (X1X2 + z s)^2 + z X1 X2 + a6 ; squaring = coefficientwise Frobenius in B_K
    X1X2 = kmul(X1, X2)
    frob = lambda P: {m: sq(c) for m, c in P.items()}
    S = kadd(frob(kadd(X1X2, kscale(s, z))), kscale(X1X2, z), {0: a6})
    w = kadd(kscale(X1X2, zi), {m: H(sq(c)) for m, c in s.items()}, {0: H(alpha)})
    w = {m: c for m, c in w.items() if c}
    # sanity: S == z^2 (w^2 + w + ell0)
    ell0 = set(Tr_(s)) ^ ({0} if tr(alpha) else set())
    T = kadd(frob(w), w, {m: 1 for m in ell0})
    assert kscale(T, sq(z)) == S, "reformulation S = z^2(w^2+w+ell_0) failed"
    # descended system span(F) = {Tr(gamma S)}
    gammas = [1 << i for i in range(n)]
    Fsys = [Tr_(kscale(S, g)) for g in gammas]
    # monomial order (degree <= 3), low degree = low bits
    order = []
    for d in range(4):
        for comb in itertools.combinations(range(N), d):
            m = 0
            for i in comb: m |= 1 << i
            order.append(m)
    pos = {m: i for i, m in enumerate(order)}
    deg = lambda m: bin(m).count('1')
    toint = lambda mons: sum(1 << pos[m] for m in mons)
    # exact W_3 closure (independent python)
    piv = {}
    def ins(r):
        while r:
            hb = r.bit_length() - 1
            if hb not in piv:
                piv[hb] = r; return hb
            r ^= piv[hb]
        return None
    def red(r):
        while r:
            hb = r.bit_length() - 1
            if hb not in piv: return r
            r ^= piv[hb]
        return 0
    low = sum(1 for m in order if deg(m) <= 2)
    queue = []
    for p in Fsys:
        for d in range(0, 2):
            for comb in itertools.combinations(range(N), d):
                mm = sum(1 << i for i in comb)
                acc = {}
                for t in p: acc[t | mm] = acc.get(t | mm, 0) ^ 1
                h = ins(toint([m for m, c in acc.items() if c]))
                if h is not None and h < low: queue.append(h)
    M3rank = len(piv); M3 = dict(piv)
    done = set()
    while queue:
        h = queue.pop()
        if h in done: continue
        done.add(h); g = piv[h]
        for v in range(N):
            r = g; out = 0
            while r:
                lb = r & -r; i = lb.bit_length() - 1; r ^= lb
                out ^= 1 << pos[order[i] | (1 << v)]
            h2 = ins(out)
            if h2 is not None and h2 < low: queue.append(h2)
    W3_low = sorted(h for h in piv if h < low)
    one = 0 in piv
    # explicit falls
    # V-perp: lambda with Tr(lambda v)=0 for all v in V  (solve linear system over F2)
    rows = []
    for i in range(n):
        lam = 1 << i
        rows.append((tuple(tr(mul(lam, v)) for v in basis), lam))
    # gaussian elimination to find kernel of lam -> (Tr(lam v_j))_j
    vecs = [(sum(b << j for j, b in enumerate(r)), lam) for r, lam in rows]
    perp = []; pivs = {}
    for vec, lam in vecs:
        while vec:
            hb = vec.bit_length() - 1
            if hb in pivs:
                pv, pl = pivs[hb]; vec ^= pv; lam ^= pl
            else:
                pivs[hb] = (vec, lam); break
        if not vec: perp.append(lam)
    assert len(perp) == n - k
    expl = []
    for lam in perp:
        for Xi in (X1, X2):
            q = Tr_(kscale(kmul(Xi, w), lam))
            assert all(deg(m) <= 2 for m in q), "q_{i,lam} has degree > 2"
            expl.append(q)
    mu_tr1 = next(x for x in range(1, 1 << n) if tr(x) == 1)
    omega = Tr_(kscale(w, mu_tr1))
    qs = set(Tr_(kmul(s, w))) ^ (set(omega) if tr(alpha) else set())
    assert all(deg(m) <= 2 for m in qs)
    in_W3 = lambda mons: red(toint(mons)) == 0
    falls_in_W3 = all(in_W3(q) for q in expl) and in_W3(qs)
    # r_j = omega a_j + Tr(mu_j X1 w) in M_3 (check against M3 pivots only)
    def red_M3(r):
        while r:
            hb = r.bit_length() - 1
            if hb not in M3: return r
            r ^= M3[hb]
        return 0
    # mu_j: dual elements with Tr(mu_j v_i) = delta_ij (solve)
    rj_ok = True
    # brute: build matrix of maps lam -> (Tr(lam v_j))_j and find preimages of unit vectors
    span = {}
    for i in range(n):
        lam = 1 << i; vec = sum(tr(mul(lam, v)) << j for j, v in enumerate(basis))
        while vec:
            hb = vec.bit_length() - 1
            if hb in span: pv, pl = span[hb]; vec ^= pv; lam ^= pl
            else: span[hb] = (vec, lam); break
    def preimage(target):
        lam = 0; vec = target
        while vec:
            hb = vec.bit_length() - 1
            pv, pl = span[hb]; vec ^= pv; lam ^= pl
        return lam
    for j in range(k):
        mu = preimage(1 << j)
        r = {}
        for m in omega: r[m | (1 << j)] = r.get(m | (1 << j), 0) ^ 1
        for m in Tr_(kscale(kmul(X1, w), mu)): r[m] = r.get(m, 0) ^ 1
        r = [m for m, c in r.items() if c]
        if red_M3(toint(r)) != 0: rj_ok = False
    # dimension of explicit degree<=2 span
    ex_piv = {}
    def ex_ins(r):
        while r:
            hb = r.bit_length() - 1
            if hb not in ex_piv: ex_piv[hb] = r; return
            r ^= ex_piv[hb]
    for p in Fsys: ex_ins(toint(p))
    lin = toint(ell0)
    for v in range(N):
        acc = {}
        for m in ell0: acc[m | (1 << v)] = acc.get(m | (1 << v), 0) ^ 1
        ex_ins(toint([m for m, c in acc.items() if c]))
    ex_ins(lin)
    for q in expl: ex_ins(toint(q))
    ex_ins(toint(qs))
    print(f"n={n} k={k}: W3 contains 1: {int(one)}; dim(W3 cap B<=2) = {len(W3_low)} (3n = {3*n}); "
          f"explicit span dim = {len(ex_piv)}; falls in W3: {falls_in_W3}; r_j in M3: {rj_ok}; "
          f"explicit span == W3 low part: {len(ex_piv) == len(W3_low) and all(red(r) == 0 for r in ex_piv.values())}")

if __name__ == '__main__':
    main()

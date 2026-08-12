# thm_bkkmv2_verify.sage — symbolic verification for research/THM_BKKMV2.md
# Executor TASK-20260724-LEMMV (theory track). Attacks the interior-fiber
# non-cancellation lemma (THM_BKKMV1 §5 Lemma-G) via the (a,b)-grading route.
# Convention identical to thm_bkkmv1_verify.sage:
#   S3 = (x1x2+x1x3+x2x3+a)^2 - 4(x1x2x3-b)(x1+x2+x3);  S_m via X-resultants.
# Stages:
#   m4     : two-root expansion (*), beta/alpha tables, b-leading factorization,
#            beta-recursion validation, (T) at m=5, a-leading sum, symmetry.
#   u      : bottom fibers u_4,u_5,u_6 exactly (specialized Sylvester dets),
#            factorizations, X-adic valuations, u_3-divisibility, deg_b/deg_a.
#   u7num  : u_7 at numeric instances (interpolation), valuations/divisibility.
#   krawt  : Krawtchouk-type coefficient zeros K_j(2s,k) for m<=6 ranges.
#   predict: tropical beta-recursion forward, (T)-checks, weight-cap collision.
#   cover4 : m=4 fiber-coverage case study (which mechanism certifies each of
#            the 125 box fibers; residual fibers needing more than the explicit
#            families).
#   m5     : S_5 over QQ(b), a=1 (capped): validate beta_5 = 9 and Theorem B's
#            predicted b-leading factorization against the actual b^9 part.
import json, sys, time, os

stage = sys.argv[1] if len(sys.argv) > 1 else "m4"
HERE = os.path.dirname(os.path.abspath(__file__))
out = {"stage": stage, "checks": [], "notes": [], "data": {}}
def rec(name, ok, detail=""):
    out["checks"].append({"check": name, "pass": bool(ok), "detail": str(detail)})
    print(("PASS" if ok else "FAIL"), name, "|", str(detail)[:300])
def note(s):
    out["notes"].append(str(s)); print("NOTE", str(s)[:400])

def sem3(p, q, r, a, b):
    return (p*q + p*r + q*r + a)**2 - 4*(p*q*r - b)*(p + q + r)

def coef(f, v, j):
    """coefficient of v^j in f; NB: .coefficient(v**0) is unreliable in this
    Sage (returns f itself), so use substitution for j=0."""
    if j == 0:
        return f.subs({v: 0})
    return f.coefficient(v**j)

def beta_rec(beta_prev, d):
    """Tropical max-formula prediction for beta^{(m)}(j), j=0..2d:
    beta(j) = max_{0<=k<=l<=d, 2(d-l)+k >= j} beta_prev[k]+beta_prev[l]+l."""
    tab = {}
    for j in range(2*d + 1):
        best = None
        for k in range(d+1):
            for l in range(k, d+1):
                if 2*(d-l) + k >= j:
                    v = beta_prev[k] + beta_prev[l] + l
                    if best is None or v > best:
                        best = v
        tab[j] = best
    return tab

def krawt(j, s2, k):
    """K_j(2s,k) = sum_t (-1)^t C(2s,t) C(k, j-t)  [v^j]-coefficient of
    (u-v)^{2s}(u+v)^k as polynomial in u (times u^{2s+k-j})."""
    from sage.all import binomial
    tot = 0
    for t in range(0, min(s2, j) + 1):
        r = j - t
        if 0 <= r <= k:
            tot += (-1)**t * binomial(s2, t) * binomial(k, r)
    return ZZ(tot)

# =====================================================================
if stage == "m4":
    t0 = time.time()
    R = PolynomialRing(QQ, 7, 'a,b,x1,x2,x3,x4,X')
    a,b,x1,x2,x3,x4,X = R.gens()
    u, v = x3, x4
    S3 = lambda p,q,r: sem3(p,q,r,a,b)
    f = S3(x1,x2,X)
    fk = [coef(f, X, k) for k in range(3)]
    g = S3(x3,x4,X)
    gj = [coef(g, X, j) for j in range(3)]
    g0,g1,g2 = gj
    note("g2 = %s" % g2); note("g1 = %s" % g1); note("g0 = %s" % g0)
    U = {0: R(2), 1: -g1, 2: g1**2 - 2*g0*g2}
    d = 2
    TR = sum(fk[k]*fk[l]*g2**(d-l)*g0**k*U[l-k] for k in range(d+1) for l in range(k+1,d+1))
    TR += sum(fk[k]**2 * g2**(d-k) * g0**k for k in range(d+1))
    S4 = f.resultant(g, X)
    note("S4 resultant wall: %.1f s" % (time.time()-t0))
    rec("m4_tworoot_expansion", TR == S4,
        "two-root expansion (*) == resultant S4: %s" % (TR == S4))

    # beta/alpha tables per x4-degree
    beta4, alpha4, fhat4, ahat4 = {}, {}, {}, {}
    for j in range(5):
        c = coef(S4, x4, j)
        beta4[j] = c.degree(b); alpha4[j] = c.degree(a)
        fhat4[j] = c.coefficient(b**beta4[j])
    note("beta^{(4)} (j=0..4) = %s" % [beta4[j] for j in range(5)])
    note("alpha^{(4)} (j=0..4) = %s" % [alpha4[j] for j in range(5)])
    rec("m4_beta_table", [beta4[j] for j in range(5)] == [3,3,3,3,2],
        str([beta4[j] for j in range(5)]))
    rec("m4_degb", S4.degree(b) == 3, "deg_b S4 = %d (predict 3)" % S4.degree(b))
    rec("m4_dega", S4.degree(a) == 4, "deg_a S4 = %d (predict 4)" % S4.degree(a))
    for j in range(5):
        note("fhat^{(4)}_%d (b-stripped, beta=%d) = %s" % (j, beta4[j], fhat4[j].factor()))

    # b-leading global: Lambda_4 = [b^3]S4, predicted factorization
    Lam4 = S4.coefficient(b**3)
    s1, d1 = x1+x2, x1-x2
    identA = 64*(u+v-s1)*((u-v)**2-d1**2)
    identB = -identA
    eq = None
    if Lam4 == identA: eq = "A"
    elif Lam4 == identB: eq = "B"
    rec("m4_blead_factor", eq is not None,
        "Lambda_4 = %s * 64*(u+v-(x1+x2))*((u-v)^2-(x1-x2)^2), sign %s" % (Lam4/64 if eq else "?", eq))
    note("Lambda_4 factored = %s" % Lam4.factor())

    # beta-recursion validation from beta^{(3)} = (1,1,0)
    beta3 = {0:1, 1:1, 2:0}
    pred4 = beta_rec(beta3, 2)
    rec("m4_beta_recursion", all(pred4[j] == beta4[j] for j in range(5)),
        "tropical prediction %s vs actual %s" % ([pred4[j] for j in range(5)],
        [beta4[j] for j in range(5)]))

    # (T) at m=5 from beta4
    bmax = max(beta4.values()); A1 = [k for k in range(5) if beta4[k] == bmax]
    gam = max(beta4[k]+k for k in range(5)); A2 = [k for k in range(5) if beta4[k]+k == gam]
    T5 = all(k <= l for k in A1 for l in A2)
    rec("m4_Tcond_m5", T5, "A1=%s A2=%s beta5=%d (all pairs k<=l: %s)" % (A1,A2,bmax+gam,T5))

    # a-leading sum: alpha^{(3)} = (2,1,0); ahat parts of f_k
    ah0 = fk[0].coefficient(a**2)   # expect 1
    ah1 = fk[1].coefficient(a**1)   # expect 2(x1+x2)
    ah2 = fk[2].coefficient(a**0)   # = f_2 itself = (x1-x2)^2
    note("ahat_0 = %s; ahat_1 = %s; ahat_2 = %s" % (ah0, ah1, ah2))
    Uh = {0: R(2), 1: -2*(u+v), 2: 2*(u**2+6*u*v+v**2)}
    A4pred = ah0**2*(u-v)**4 + ah0*ah1*(u-v)**2*Uh[1] + ah1**2*(u-v)**2 \
           + ah0*ah2*Uh[2] + ah1*ah2*Uh[1] + ah2**2
    A4act = S4.coefficient(a**4)
    rec("m4_alead_sum", A4pred == A4act, "a^4 part: predicted == actual: %s" % (A4pred == A4act))
    note("a^4 part of S4 factored = %s" % A4act.factor())

    # symmetry of S4 (generators (12),(23),(34))
    rec("m4_sym_12", S4 == S4.subs({x1:x2, x2:x1}), "swap x1<->x2")
    rec("m4_sym_23", S4 == S4.subs({x2:x3, x3:x2}), "swap x2<->x3")
    rec("m4_sym_34", S4 == S4.subs({x3:x4, x4:x3}), "swap x3<->x4")

    out["data"]["beta4"] = [int(beta4[j]) for j in range(5)]
    out["data"]["alpha4"] = [int(alpha4[j]) for j in range(5)]

# =====================================================================
if stage == "u":
    t0 = time.time()
    R = PolynomialRing(QQ, 3, 'a,b,X')
    a,b,X = R.gens()
    def sylvdet(fcoef, gcoef, df, dg):
        n = df + dg
        M = matrix(R, n, n)
        for r in range(dg):
            for k in range(df+1):
                M[r, r + df - k] = fcoef.get(k, R(0))
        for s in range(df):
            for j in range(dg+1):
                M[dg+s, s + dg - j] = gcoef.get(j, R(0))
        return M.determinant()
    gcoef = {2: X**2, 1: 2*a*X + 4*b, 0: a**2 + 4*b*X}
    u3 = a**2 + 4*b*X
    u4 = sylvdet({0: a**2, 1: 4*b}, gcoef, 2, 2)
    rec("u4_exact", u4 == X**3*(a**4*X - 8*a**3*b + 64*b**3), "u4 = %s" % u4)
    rec("u4_root_weight", (a**4*X - 8*a**3*b + 64*b**3).subs({X: 8*b*(a**3-8*b**2)/a**4}) == 0,
        "nonzero root is 8b(a^3-8b^2)/a^4 (note: THM_BKKMV1 text wrote a^2 -- transcription erratum)")
    u4c = {k: coef(u4, X, k) for k in range(5)}
    u5 = sylvdet(u4c, gcoef, 4, 2)
    note("u5 wall: %.1f s" % (time.time()-t0))
    u5fac = u5.factor(); note("u5 factored = %s" % u5fac)
    rec("u5_degb", u5.degree(b) == 9, "deg_b u5 = %d (predict 9 = beta_5)" % u5.degree(b))
    u5c = {k: coef(u5, X, k) for k in range(9)}
    t1 = time.time()
    u6 = sylvdet(u5c, gcoef, 8, 2)
    note("u6 det wall: %.1f s" % (time.time()-t1))
    note("u6 = %s" % u6)
    note("u6 factored = %s" % u6.factor())
    rec("u6_degX", u6.degree(X) == 16, "deg_X u6 = %d (predict 16, no pole loss: lead = c5^2 != 0)" % u6.degree(X))
    # X-adic valuation
    val = 0; t = u6
    while t != 0 and t.subs({X: 0}) == 0:
        t = t // X; val += 1
    rec("u6_valuation", val == 10, "X-adic valuation u6 = %d (predict C(5,3)=10)" % val)
    rec("u6_degb", u6.degree(b) == 25, "deg_b u6 = %d (tropical predict 25)" % u6.degree(b))
    note("deg_a u6 = %d (weight cap W6/4 = 40)" % u6.degree(a))
    # divisibility by u_3 (root x(2P))
    F = R.fraction_field()
    u6F = F(u6); u3F = F(u3)
    e = 0; t = u6F
    while True:
        q = t / u3F
        if q.denominator() == 1:
            t = q; e += 1
        else:
            break
    note("u3-adic exponent in u6: %d" % e)
    out["data"]["u6_valuation"] = val
    out["data"]["u6_degb"] = int(u6.degree(b))
    out["data"]["u6_dega"] = int(u6.degree(a))
    out["data"]["u3_exp_in_u6"] = e
    # b-degree profile of u5 (for bottom-fiber tropical)
    prof5 = {k: int(u5c[k].degree(b)) for k in range(9) if u5c[k] != 0}
    note("deg_b of [X^k]u5: %s" % prof5)
    prof6 = {k: int(u6.coefficient(X**k).degree(b)) for k in range(17) if u6.coefficient(X**k) != 0}
    note("deg_b of [X^k]u6: %s" % prof6)
    out["data"]["u5_bprofile"] = prof5
    out["data"]["u6_bprofile"] = prof6

# =====================================================================
if stage == "u7num":
    # u_7 at numeric (a,b) instances: 18x18 specialized Sylvester via interpolation
    t0 = time.time()
    R = PolynomialRing(QQ, 3, 'a,b,X')
    a,b,X = R.gens()
    def sylvdetR(fcoef, gcoef, df, dg):
        n = df + dg
        M = matrix(R, n, n)
        for r in range(dg):
            for k in range(df+1):
                M[r, r + df - k] = fcoef.get(k, R(0))
        for s in range(df):
            for j in range(dg+1):
                M[dg+s, s + dg - j] = gcoef.get(j, R(0))
        return M.determinant()
    gcoef = {2: X**2, 1: 2*a*X + 4*b, 0: a**2 + 4*b*X}
    u4 = sylvdetR({0: a**2, 1: 4*b}, gcoef, 2, 2)
    u5 = sylvdetR({k: coef(u4, X, k) for k in range(5)}, gcoef, 4, 2)
    u6 = sylvdetR({k: coef(u5, X, k) for k in range(9)}, gcoef, 8, 2)
    Rq = PolynomialRing(QQ, 'X'); Xq = Rq.gen()
    def sylvdetQ(fcoef, gcoef, df, dg):
        n = df + dg
        M = matrix(Rq, n, n)
        for r in range(dg):
            for k in range(df+1):
                M[r, r + df - k] = fcoef.get(k, Rq(0))
        for s in range(df):
            for j in range(dg+1):
                M[dg+s, s + dg - j] = gcoef.get(j, Rq(0))
        return M.determinant()
    for (A,B) in [(1,1),(2,3)]:
        u6n = Rq(u6.subs({a:A, b:B}))
        fcoef = {k: u6n[k] for k in range(17)}
        gq = {2: Xq**2, 1: 2*A*Xq + 4*B, 0: A**2 + 4*B*Xq}
        t1 = time.time()
        u7n = sylvdetQ(fcoef, gq, 16, 2)
        note("u7 det (a,b)=(%d,%d): %.1f s, deg %d" % (A,B,time.time()-t1,u7n.degree()))
        val = 0; t = u7n
        while t != 0 and t(0) == 0:
            t = t // Xq; val += 1
        rec("u7_val0_a%d_b%d" % (A,B), val == 0, "X-adic valuation %d (odd m: expect 0, c7 != 0)" % val)
        note("c7 (a,b)=(%d,%d): u7(0) = %s" % (A,B, u7n(0)))
        u3n = A**2 + 4*B*Xq
        e = 0; t = u7n
        while True:
            q, r = t.quo_rem(u3n)
            if r == 0:
                t = q; e += 1
            else:
                break
        note("u3-adic exponent in u7 at (%d,%d): %d (naive sign-count 15, escape-reshuffled)" % (A,B,e))
        out["data"]["u3_exp_u7_a%d_b%d" % (A,B)] = e
        # u5 divides u7?
        u5n = Rq(u5.subs({a:A, b:B}))
        e5 = 0; t = u7n
        while True:
            q, r = t.quo_rem(u5n)
            if r == 0:
                t = q; e5 += 1
            else:
                break
        note("u5-adic exponent in u7 at (%d,%d): %d" % (A,B,e5))
        out["data"]["u5_exp_u7_a%d_b%d" % (A,B)] = e5

# =====================================================================
if stage == "krawt":
    # K_j(2s,k) zeros for m<=6 ranges: k in 0..16, s in 0..8, j in 0..k+2s
    zeros = []
    tot = 0
    for k in range(0, 17):
        for s in range(0, 9):
            for j in range(0, k + 2*s + 1):
                tot += 1
                if krawt(j, 2*s, k) == 0:
                    zeros.append((j, s, k))
    note("Krawtchouk zeros (j,s,k) with K_j(2s,k)=0 in range k<=16,s<=8: %d zeros of %d tuples" % (len(zeros), tot))
    note("zeros: %s" % zeros)
    out["data"]["krawt_zeros"] = zeros
    # parity structure: K_j(2s,k) with j odd and k... check K_j(2s,2s) zero for odd j
    chk = all(krawt(j, 2*s, 2*s) == 0 for s in range(1,9) for j in range(0, 4*s+1) if j % 2 == 1)
    rec("krawt_diagonal_parity", chk, "K_j(2s,2s)=0 for all odd j (symmetric case), s<=8")

# =====================================================================
if stage == "predict":
    beta3 = {0:1, 1:1, 2:0}
    beta4 = beta_rec(beta3, 2)
    note("beta4 = %s (validated at m=4)" % [beta4[j] for j in sorted(beta4)])
    beta5 = beta_rec(beta4, 4)
    note("beta5 = %s (global %d; anchor: deg_b u5 = 9 measured)" % ([beta5[j] for j in sorted(beta5)], max(beta5.values())))
    beta6 = beta_rec(beta5, 8)
    note("beta6 = %s (global %d)" % ([beta6[j] for j in sorted(beta6)], max(beta6.values())))
    beta7 = beta_rec(beta6, 16)
    note("beta7 = %s (global %d)" % ([beta7[j] for j in sorted(beta7)], max(beta7.values())))
    beta8 = beta_rec(beta7, 32)
    note("beta8 global = %d" % max(beta8.values()))
    for m, tab in [(4,beta4),(5,beta5),(6,beta6),(7,beta7),(8,beta8)]:
        W = (m-1)*2**(m-1)
        cap = W//6
        g = max(tab.values())
        bmax = g; A1 = [k for k in tab if tab[k] == bmax]
        gam = max(tab[k]+k for k in tab); A2 = [k for k in tab if tab[k]+k == gam]
        T = all(k <= l for k in A1 for l in A2)
        note("m=%d: deg_b predict %d, weight cap %d, A1=%s A2=%s (T)=%s, next deg_b %d" %
             (m, g, cap, A1, A2, T, bmax+gam))
        out["data"]["beta%d" % m] = [int(tab[j]) for j in sorted(tab)]
    rec("predict_cap_collision_m7", max(beta7.values()) > 64,
        "tropical predicts deg_b S7 = %d > W7/6 = 64: weight-cap forces (NZ) failure at level 7" % max(beta7.values()))

# =====================================================================
if stage == "cover4":
    t0 = time.time()
    R = PolynomialRing(QQ, 7, 'a,b,x1,x2,x3,x4,X')
    a,b,x1,x2,x3,x4,X = R.gens()
    S3 = lambda p,q,r: sem3(p,q,r,a,b)
    f = S3(x1,x2,X); g = S3(x3,x4,X)
    S4 = f.resultant(g, X)
    S3xyz = S3(x1,x2,x3)
    # support of S4 with grades
    cells = {}
    for mono, cf in S4.dict().items():
        E = (mono[2], mono[3], mono[4], mono[5])
        cells.setdefault(E, set()).add((mono[0], mono[1]))
    rec("cover4_supp_size", len(cells) == 439, len(cells))
    # support of S3
    sup3 = set((mono[2], mono[3], mono[4]) for mono in S3xyz.dict())
    rec("cover4_sup3", len(sup3) == 13, len(sup3))
    # 2*supp S3 (Minkowski)
    twoS3 = set()
    for p in sup3:
        for q in sup3:
            twoS3.add((p[0]+q[0], p[1]+q[1], p[2]+q[2]))
    # tower check: top layer x4=4 of S4 == 2*supp S3
    top4 = set(E[:3] for E in cells if E[3] == 4)
    rec("cover4_tower", top4 == twoS3, "top layer x4=4 size %d, 2*suppS3 size %d" % (len(top4), len(twoS3)))
    # explicit families
    from itertools import product as iprod
    box = list(iprod(range(5), repeat=3))
    # b-leading Lambda_4 support (from the proved factorization)
    u, v = x3, x4
    s1, d1 = x1+x2, x1-x2
    Lam4 = 64*(u+v-s1)*((u-v)**2-d1**2)
    supLam = set((mono[2], mono[3], mono[4], mono[5]) for mono in Lam4.dict())
    # a-leading: actual a^4 part
    A4 = S4.coefficient(a**4)
    supA4 = set((mono[2], mono[3], mono[4], mono[5]) for mono in A4.dict())
    # mechanism membership for a cell E
    def mechs(E):
        m = set()
        if E == (4,4,4,0): m.add("corner")
        for i in range(4):
            if E[i] == 4:
                m.add("tower%d" % (i+1))
        if E in supLam: m.add("blead")
        if E in supA4: m.add("alead")
        if 12 - sum(E) <= 5: m.add("q<=5")
        return m
    fiber_mechs = {}
    uncovered = []
    for ep in box:
        ms = set()
        for e4 in range(5):
            E = (ep[0], ep[1], ep[2], e4)
            if E in cells:
                ms |= mechs(E)
        fiber_mechs[ep] = ms
        if not ms:
            uncovered.append(ep)
    full = sum(1 for ep in box if any(e4 in range(5) for e4 in [0]) )  # placeholder
    nonempty = sum(1 for ep in box if any((ep[0],ep[1],ep[2],e4) in cells for e4 in range(5)))
    rec("cover4_all_fibers", nonempty == 125, "nonempty fibers %d/125 (C1 at m=4)" % nonempty)
    by_mech = {}
    for ep, ms in fiber_mechs.items():
        key = "+".join(sorted(ms)) if ms else "NONE"
        by_mech.setdefault(key, []).append(ep)
    note("fiber coverage by mechanism set:")
    for key in sorted(by_mech, key=lambda k: -len(by_mech[k])):
        note("  %-40s %d fibers" % (key, len(by_mech[key])))
    note("uncovered-by-explicit-families: %d fibers: %s" % (len(uncovered), uncovered[:20]))
    out["data"]["cover4_by_mech"] = {k: len(v) for k,v in by_mech.items()}
    out["data"]["cover4_uncovered"] = uncovered
    # how many fibers does b-leading alone certify? towers alone?
    nb = sum(1 for ms in fiber_mechs.values() if "blead" in ms)
    nt = sum(1 for ms in fiber_mechs.values() if any(m.startswith("tower") for m in ms))
    na = sum(1 for ms in fiber_mechs.values() if "alead" in ms)
    note("fibers certified: b-leading %d, towers %d, a-leading %d (of 125)" % (nb, nt, na))
    out["data"]["cover4_counts"] = {"blead": nb, "towers": nt, "alead": na}

# =====================================================================
if stage == "m5":
    # S_5 over QQ(b) with a=1: validate beta_5 = 9 and Theorem B's factorization.
    t0 = time.time()
    R = PolynomialRing(QQ, 7, 'b,x1,x2,x3,x4,x5,X')
    b,x1,x2,x3,x4,x5,X = R.gens()
    A = QQ(1)
    S3 = lambda p,q,r: sem3(p,q,r,A,b)
    f = S3(x1,x2,X); g = S3(x3,x4,X)
    S4 = f.resultant(g, X)
    note("S4 (a=1) wall: %.1f s, deg_b %d" % (time.time()-t0, S4.degree(b)))
    # f-hats from S4 (b-stripped leading parts per x4-degree)
    beta4, fhat4 = {}, {}
    for j in range(5):
        c = coef(S4, x4, j)
        beta4[j] = c.degree(b)
        fhat4[j] = coef(c, b, beta4[j])
    rec("m5_beta4", [beta4[j] for j in range(5)] == [3,3,3,3,2], str([beta4[j] for j in range(5)]))
    bmax = 3; A1 = [0,1,2,3]; gam = 6; A2 = [3,4]
    u, v = x4, x5
    Psi = sum(fhat4[k]*((-(u+v))**k) for k in A1)
    Phi = sum(fhat4[l]*((-4)**l)*(u-v)**(2*(4-l)) for l in A2)
    Lam5pred = Psi*Phi
    t1 = time.time()
    S5 = S4.subs({x4: X}).resultant(S3(x4,x5,X), X)
    note("S5 (a=1, b symbolic) resultant wall: %.1f s" % (time.time()-t1))
    rec("m5_degb", S5.degree(b) == 9, "deg_b S5 = %d (predict 9)" % S5.degree(b))
    Lam5 = S5.coefficient(b**9)
    rec("m5_TheoremB", Lam5 == Lam5pred or Lam5 == -Lam5pred,
        "b^9 part == Psi*Phi up to sign: %s; sign %s" % (Lam5 == Lam5pred or Lam5 == -Lam5pred,
        "+" if Lam5 == Lam5pred else ("-" if Lam5 == -Lam5pred else "?")))
    beta5 = {}
    for j in range(9):
        c = coef(S5, x5, j)
        beta5[j] = c.degree(b)
    note("beta^{(5)} actual (a=1) = %s" % [beta5[j] for j in range(9)])
    pred5 = beta_rec({0:3,1:3,2:3,3:3,4:2}, 4)
    rec("m5_beta_recursion", all(pred5[j] == beta5[j] for j in range(9)),
        "tropical %s vs actual %s" % ([pred5[j] for j in range(9)], [beta5[j] for j in range(9)]))
    out["data"]["beta5"] = [int(beta5[j]) for j in range(9)]

def _pyify(o):
    from sage.rings.integer import Integer as _SageInt
    from sage.rings.rational import Rational as _SageRat
    if isinstance(o, _SageInt):
        return int(o)
    if isinstance(o, _SageRat):
        return float(o)
    if isinstance(o, dict):
        return {str(k): _pyify(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_pyify(v) for v in o]
    return o

fn = os.path.join(HERE, "thm_bkkmv2_verify_results_%s.json" % stage)
with open(fn, "w") as fh:
    json.dump(_pyify(out), fh, indent=2)
print("wrote", fn)

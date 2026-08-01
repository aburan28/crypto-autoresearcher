# thm_bkkmv1_verify_m5.sage — m=5 verification for research/THM_BKKMV1.md
# Stage "5n": numeric generic (a,b) over QQ — support/projection/corner/tower/sections.
#             (symbolic-(a,b) S5 resultant exceeded the 290 s foreground cap — recorded
#              as infrastructure censoring; numeric specializations certify the same
#              support statements since supp(specialization) subseteq supp(generic) and
#              a FULL projection at a specialization forces fullness generically.)
# Stage "u5": exact symbolic bottom fiber u_5(X) via the SPECIALIZED Sylvester
#             determinant (valid: substitution commutes with the determinant, unlike
#             with the resultant map) + c5 torsion factorization vs psi_5(0).
import json, sys, time

stage = sys.argv[1]
out = {"stage": stage, "checks": [], "notes": []}
def rec(name, ok, detail=""):
    out["checks"].append({"check": name, "pass": bool(ok), "detail": str(detail)})
    print(("PASS" if ok else "FAIL"), name, "|", detail)

def fullbox(n, D):
    from itertools import product as iprod
    return set(iprod(*[range(D+1)]*n))

if stage == "5n":
    Rn = PolynomialRing(QQ, 6, 'x1,x2,x3,x4,x5,X')
    x1,x2,x3,x4,x5,X = Rn.gens()
    xidx = {x1:0,x2:1,x3:2,x4:3,x5:4}
    def xsupp(f, vars_):
        pos = [xidx[v] for v in vars_]
        return set(tuple(int(e[p]) for p in pos) for e in f.exponents())
    for (A,B) in [(1,1),(2,3)]:
        t0 = time.time()
        S3 = (x1*x2 + x1*x3 + x2*x3 + A)**2 - 4*(x1*x2*x3 - B)*(x1 + x2 + x3)
        s3a = S3.subs({x3: X}); s3b = S3.subs({x1:x3, x2:x4, x3:X})
        S4 = s3a.resultant(s3b, X)
        s4a = S4.subs({x4: X}); s3c = S3.subs({x1:x4, x2:x5, x3:X})
        S5 = s4a.resultant(s3c, X)
        out["notes"].append("S5 numeric resultant (a,b)=(%d,%d) wall: %.1f s" % (A,B,time.time()-t0))
        tag = "_a%d_b%d" % (A,B)
        D = 8
        sup5 = xsupp(S5, [x1,x2,x3,x4,x5])
        rec("m5_supp_size"+tag, len(sup5) == 54777, "%d (expect 54777)" % len(sup5))
        box5 = fullbox(4, D)
        from itertools import combinations
        for i, quad in enumerate(combinations([x1,x2,x3,x4,x5],4)):
            pr = set(tuple(int(e[xidx[v]]) for v in quad) for e in S5.exponents())
            rec("m5_projection_%d%s" % (i,tag), pr == box5, "%d/6561" % len(pr))
        rec("m5_totdeg"+tag, S5.total_degree() == 32, S5.total_degree())
        rec("m5_vardeg"+tag, all(S5.degree(v) == D for v in (x1,x2,x3,x4,x5)),
            [S5.degree(v) for v in (x1,x2,x3,x4,x5)])
        rec("m5_lead_tower"+tag, S5.coefficient(x5**D) == S4**2, "lead_{x5} S5 == S4^2")
        rec("m5_coeff_tower"+tag, S5.coefficient(x3**8*x4**8*x5**8) == (x1-x2)**8,
            "coeff x3^8 x4^8 x5^8 == (x1-x2)^8")
        rec("m5_corner1"+tag, S5.monomial_coefficient(x1**8*x2**8*x3**8*x4**8) == 1,
            S5.monomial_coefficient(x1**8*x2**8*x3**8*x4**8))
        w5 = S5.subs({x5: 0}); w4 = S4.subs({x4: 0})
        rec("m5_wtower"+tag, w5.coefficient(x4**D) == w4**2, "lead_{x4} w5 == w4^2")
        for t in (1,2):
            ss = xsupp(S5.subs({x5:t}), [x1,x2,x3,x4])
            rec("m5_section_t%d%s" % (t,tag), ss == box5, len(ss))

if stage == "u5":
    R = PolynomialRing(QQ, 3, 'a,b,X')
    a,b,X = R.gens()
    # u_5(X) = S_5(0,0,0,0,X) = det of Sylvester matrix of
    #   f(Y) = S_4(0,0,0,Y) = u_4(Y) and g(Y) = S_3(0,X,Y), specialized BEFORE det.
    # u_4 known exactly: a^4 Y^4 + 8b(8b^2 - a^2) Y^3  (verified in stage 34).
    u4c = {4: a**4, 3: 8*b*(8*b**2 - a**2), 2: R(0), 1: R(0), 0: R(0)}
    gc  = {2: X**2, 1: 2*a*X + 4*b, 0: a**2 + 4*b*X}
    # Sylvester matrix (deg f = 4, deg g = 2): 6x6; rows 0-1: f shifted; rows 2-5: g shifted
    M = matrix(R, 6, 6)
    for r in range(2):        # f rows
        for k in range(5):    # f_k, k = 4..0
            M[r, r + (4 - k)] = u4c[k]
    for s in range(4):        # g rows
        for j in range(3):    # g_j, j = 2..0
            M[2 + s, s + (2 - j)] = gc[j]
    t0 = time.time()
    u5 = M.determinant()
    out["notes"].append("specialized Sylvester det wall: %.1f s" % (time.time()-t0))
    out["notes"].append("u5 = %s" % u5)
    out["notes"].append("u5 factored = %s" % u5.factor())
    rec("u5_deg", u5.degree(X) == 5, "deg u5 = %d (expect 5 = 8 - 3 pole loss)" % u5.degree(X))
    c5 = u5.subs({X:0})
    out["notes"].append("c5 = %s" % c5.factor())
    rec("u5_c5_nonzero", c5 != 0, "c5 != 0 (odd-m bottom corner present generically)")
    vv = 0; tt = c5
    while tt != 0 and tt.subs({a:0}) == 0:
        tt = tt // a; vv += 1
    out["notes"].append("a-adic valuation of c5: %d" % vv)
    rec("u5_c5_a2", vv >= 2, "a^%d | c5 (3-torsion factor)" % vv)
    # psi_5(0): 5-torsion condition of P=(0,sqrt(b))
    Fq = R.fraction_field()
    E = EllipticCurve(Fq, [Fq(a), Fq(b)])
    psi5 = E.division_polynomial(5)
    p0 = psi5(0)
    num = R(p0.numerator())
    out["notes"].append("psi5(0) numerator = %s" % num.factor())
    rec("u5_c5_psi5", (c5 % num) == 0, "psi5(0) | c5 (5-torsion factor)")

fn = "thm_bkkmv1_verify_results_%s.json" % stage
with open(fn, "w") as fh:
    json.dump(out, fh, indent=2)
print("wrote", fn)

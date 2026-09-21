# thm_bkkmv1_verify.sage — symbolic verification for research/THM_BKKMV1.md
# Executor TASK-20260718-THMMV. Checks the Semaev-family structural claims over QQ[a,b]:
#   support sizes (13/439/54777), projection saturation, leading-coefficient towers,
#   universal diagonal corner (=1), u_m bottom-fiber factorizations, t=0 section hole.
# Convention: identical to experiments/EXP-BKKMV-001/bkkmv1_cert.sage (semaev_polys):
#   S3 = (x1x2+x1x3+x2x3+a)^2 - 4(x1x2x3-b)(x1+x2+x3);  S_m via X-resultants.
# Usage: sage thm_bkkmv1_verify.sage 34   (m=3,4 checks; fast)
#        sage thm_bkkmv1_verify.sage 5    (m=5 checks; heavier)
import json, sys, time

stage = sys.argv[1] if len(sys.argv) > 1 else "34"
out = {"stage": stage, "checks": [], "notes": []}
def rec(name, ok, detail=""):
    out["checks"].append({"check": name, "pass": bool(ok), "detail": str(detail)})
    print(("PASS" if ok else "FAIL"), name, "|", detail)

R = PolynomialRing(QQ, 8, 'a,b,x1,x2,x3,x4,x5,X')
a,b,x1,x2,x3,x4,x5,X = R.gens()
xx = [x1,x2,x3,x4,x5]
xidx = {x1:2, x2:3, x3:4, x4:5, x5:6}   # exponent-tuple positions

S3 = (x1*x2 + x1*x3 + x2*x3 + a)**2 - 4*(x1*x2*x3 - b)*(x1 + x2 + x3)

def xsupp(f, vars_):
    """set of exponent tuples of f restricted to the given variables"""
    pos = [xidx[v] for v in vars_]
    S = set()
    for e in f.exponents():
        S.add(tuple(int(e[p]) for p in pos))
    return S

def fullbox(n, D):
    from itertools import product as iprod
    return set(iprod(*[range(D+1)]*n))

def lead_coeff(f, v, d):
    """coefficient of v^d as a polynomial in the remaining variables"""
    return f.coefficient(v**d)

t0 = time.time()
S4 = None
if stage in ("34", "4", "5"):
    s3a = S3.subs({x3: X})                       # S_3(x1,x2,X)
    s3b = S3.subs({x1: x3, x2: x4, x3: X})       # S_3(x3,x4,X)
    S4 = s3a.resultant(s3b, X)
    out["notes"].append("S4 resultant wall: %.1f s" % (time.time()-t0))

if stage in ("34",):
    # ---------- m=3 ----------
    sup3 = xsupp(S3, [x1,x2,x3])
    rec("m3_supp_size", len(sup3) == 13, "|supp(S3)| = %d (expect 13)" % len(sup3))
    box3 = fullbox(2, 2)
    for i,(u,v) in enumerate([(x1,x2),(x1,x3),(x2,x3)]):
        pr = set()
        pos = [xidx[u], xidx[v]]
        for e in S3.exponents():
            pr.add((int(e[pos[0]]), int(e[pos[1]])))
        rec("m3_projection_%d" % i, pr == box3, "proj size %d/9" % len(pr))
    rec("m3_totdeg", S3.total_degree() == 4, S3.total_degree())
    rec("m3_vardeg", all(S3.degree(v) == 2 for v in (x1,x2,x3)),
        [S3.degree(v) for v in (x1,x2,x3)])
    # tower: lead_{x3} S3 == (x1-x2)^2 == S2^2
    rec("m3_lead_tower", lead_coeff(S3, x3, 2) == (x1-x2)**2, "lead_{x3} S3 == (x1-x2)^2")
    # w-tower: w3 = S3(x1,x2,0); lead_{x2} w3 == x1^2 == w2^2
    w3 = S3.subs({x3: 0})
    rec("m3_wtower", lead_coeff(w3, x2, 2) == x1**2, "lead_{x2} w3 == w2^2")
    # universal diagonal corner: scalar coeff of x1^2 x2^2 x3^0 in S3 == 1
    rec("m3_corner1", S3.monomial_coefficient(x1**2 * x2**2) == 1,
        S3.monomial_coefficient(x1**2 * x2**2))
    # u_3(X) = S3(0,0,X)
    u3 = S3.subs({x1:0, x2:0, x3:X})
    rec("m3_u3", u3 == a**2 + 4*b*X, u3)
    rec("m3_c3", u3.subs({X:0}) == a**2, "c3 = a^2")
    # nodal specialization keeps all 13 cells
    s3n = S3.subs({a:-3, b:2})
    rec("m3_nodal_supp", len(xsupp(s3n,[x1,x2,x3])) == 13, len(xsupp(s3n,[x1,x2,x3])))
    # section support at generic t (t=1,2) is full box
    for t in (1,2):
        ss = xsupp(S3.subs({x3:t}), [x1,x2])
        rec("m3_section_t%d" % t, ss == box3, len(ss))

if stage in ("34","4"):
    # ---------- m=4 ----------
    D = 4
    sup4 = xsupp(S4, [x1,x2,x3,x4])
    rec("m4_supp_size", len(sup4) == 439, "|supp(S4)| = %d (expect 439)" % len(sup4))
    box4 = fullbox(3, D)
    from itertools import combinations
    for i, trip in enumerate(combinations([x1,x2,x3,x4],3)):
        pr = set()
        pos = [xidx[v] for v in trip]
        for e in S4.exponents():
            pr.add(tuple(int(e[p]) for p in pos))
        rec("m4_projection_%d" % i, pr == box4, "proj size %d/125" % len(pr))
    rec("m4_totdeg", S4.total_degree() == 12, S4.total_degree())
    rec("m4_vardeg", all(S4.degree(v) == D for v in (x1,x2,x3,x4)),
        [S4.degree(v) for v in (x1,x2,x3,x4)])
    # tower: lead_{x4} S4 == S3^2
    rec("m4_lead_tower", lead_coeff(S4, x4, D) == S3**2, "lead_{x4} S4 == S3^2")
    # coefficient tower: coeff of x3^4 x4^4 == (x1-x2)^4
    c44 = S4.coefficient(x3**4 * x4**4)
    rec("m4_coeff_tower", c44 == (x1-x2)**4, "coeff x3^4 x4^4 == (x1-x2)^4")
    # w-tower
    w4 = S4.subs({x4: 0})
    w3 = S3.subs({x3: 0})
    rec("m4_wtower", lead_coeff(w4, x3, D) == w3**2, "lead_{x3} w4 == w3^2")
    rec("m4_corner1", S4.monomial_coefficient(x1**4*x2**4*x3**4) == 1,
        S4.monomial_coefficient(x1**4*x2**4*x3**4))
    # bottom fiber: u_4(X) = S4(0,0,0,X); expect X^3 | u_4 (even m), valuation 3, linear cofactor
    u4 = S4.subs({x1:0, x2:0, x3:0, x4:X})
    val4 = 0; tq = u4
    while tq != 0 and tq.subs({X:0}) == 0:
        tq = tq // X; val4 += 1
    rec("m4_u4_deg", u4.degree(X) == 4, u4.degree(X))
    rec("m4_u4_valuation", val4 == 3, "X-adic valuation of u4 = %d (expect 3)" % val4)
    rec("m4_c4_zero", u4.subs({X:0}) == 0, "c4 = S4(0,0,0,0) = 0 (even-m hole)")
    out["notes"].append("u4(X) = %s" % u4)
    # t=0 section w4: origin missing from its support
    supw4 = xsupp(w4, [x1,x2,x3])
    rec("m4_t0section_origin_hole", (0,0,0) not in supw4, "|supp(w4)| = %d/125" % len(supw4))
    out["notes"].append("m4 t=0 section support size %d; missing cells: %s" %
        (len(supw4), sorted(fullbox(3,D) - supw4)))
    # sections at t=1,2,3 full box
    for t in (1,2,3):
        ss = xsupp(S4.subs({x4:t}), [x1,x2,x3])
        rec("m4_section_t%d" % t, ss == box4, len(ss))

if stage == "5":
    t0 = time.time()
    s4a = S4.subs({x4: X})                        # S_4(x1,x2,x3,X)
    s3c = S3.subs({x1: x4, x2: x5, x3: X})        # S_3(x4,x5,X)
    S5 = s4a.resultant(s3c, X)
    out["notes"].append("S5 resultant wall: %.1f s" % (time.time()-t0))
    D = 8
    sup5 = xsupp(S5, [x1,x2,x3,x4,x5])
    rec("m5_supp_size", len(sup5) == 54777, "|supp(S5)| = %d (expect 54777)" % len(sup5))
    box5 = fullbox(4, D)
    from itertools import combinations
    for i, quad in enumerate(combinations([x1,x2,x3,x4,x5],4)):
        pr = set()
        pos = [xidx[v] for v in quad]
        for e in S5.exponents():
            pr.add(tuple(int(e[p]) for p in pos))
        rec("m5_projection_%d" % i, pr == box5, "proj size %d/6561" % len(pr))
    rec("m5_totdeg", S5.total_degree() == 32, S5.total_degree())
    rec("m5_vardeg", all(S5.degree(v) == D for v in (x1,x2,x3,x4,x5)),
        [S5.degree(v) for v in (x1,x2,x3,x4,x5)])
    rec("m5_lead_tower", lead_coeff(S5, x5, D) == S4**2, "lead_{x5} S5 == S4^2")
    c55 = S5.coefficient(x3**8*x4**8*x5**8)
    rec("m5_coeff_tower", c55 == (x1-x2)**8, "coeff x3^8 x4^8 x5^8 == (x1-x2)^8")
    w5 = S5.subs({x5: 0})
    w4 = S4.subs({x4: 0})
    rec("m5_wtower", lead_coeff(w5, x4, D) == w4**2, "lead_{x4} w5 == w4^2")
    rec("m5_corner1", S5.monomial_coefficient(x1**8*x2**8*x3**8*x4**8) == 1,
        S5.monomial_coefficient(x1**8*x2**8*x3**8*x4**8))
    # sections t=1,2 full box
    for t in (1,2):
        ss = xsupp(S5.subs({x5:t}), [x1,x2,x3,x4])
        rec("m5_section_t%d" % t, ss == box5, len(ss))
    # bottom fiber u_5 and the torsion factorization of c_5
    u5 = S5.subs({x1:0,x2:0,x3:0,x4:0,x5:X})
    out["notes"].append("u5 degree: %d (expect 5 = 8 - 3 pole loss)" % u5.degree(X))
    c5 = u5.subs({X:0})
    out["notes"].append("c5 factorization: %s" % c5.factor())
    # a-adic valuation of c5
    vv = 0; tt = c5
    while tt != 0 and tt.subs({a:0}) == 0:
        tt = tt // a; vv += 1
    out["notes"].append("a-adic valuation of c5: %d" % vv)
    rec("m5_c5_nonzero", c5 != 0, "c5 != 0 (odd-m bottom corner present)")
    rec("m5_c5_a2_factor", vv >= 2, "a^%d | c5 (3-torsion factor present)" % vv)
    # division-polynomial 5-torsion condition psi_5(0)
    Fq = R.fraction_field()
    E = EllipticCurve(Fq, [Fq(a), Fq(b)])
    psi5 = E.division_polynomial(5)
    psi5_0 = Fq(psi5).subs({psi5.parent().gen(): 0})
    num = R(psi5_0.numerator())
    out["notes"].append("psi5(0) numerator: %s" % num.factor())
    rec("m5_c5_psi5_factor", (c5 % num) == 0, "psi5(0) | c5 (5-torsion factor)")

fn = "thm_bkkmv1_verify_results_%s.json" % stage
with open(fn, "w") as fh:
    json.dump(out, fh, indent=2)
print("wrote", fn)

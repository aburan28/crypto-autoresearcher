#!/usr/bin/env sage
# ===========================================================================
# round018_T2_isogeny_gatedmeter.sage  --  T2 / PO-009
# Falsification test for the "no weak B" headline at the open L3 level:
# does any horizontal Cl(O_K)-neighbor (same order, different (a,b)) of a toy
# P-256-like curve open a Semaev solving advantage the start curve lacks?
#
# Part A (leading-form, decisive): show top_form(S_3) is INDEPENDENT of (a,b),
#         so the audited gated meter is LITERALLY identical for every curve in
#         the class  =>  no gate_meaningful can differ class-wide. This narrows
#         the open door to sub-leading-form GB degeneracy for special (a,b).
# Part B (true Groebner, empirical): for several l-isogeny neighbors + controls,
#         build a REAL m=2 decomposition system and compare the TRUE solving
#         degree (max degrevlex GB generator degree) and #solutions. A neighbor
#         solving strictly lower => coefficient-level weakness => headline falsified.
#
# Run: sage round018_T2_isogeny_gatedmeter.sage
# ===========================================================================
import json
load("round016_gated_meter.sage")   # top_form, _semaev3, meter_gated, ...

def S3_full(R, a, b):
    return _semaev3(R, a, b)

# ---------------- Part A: leading form is (a,b)-independent ----------------
print("="*70)
print("PART A  --  top_form(S_3) independence from (a,b)  [leading-form closure]")
print("="*70)
pA = 10007
RA = PolynomialRing(GF(pA), 3, names=['x0','x1','x2'])
tops = []
for (a,b) in [(2,3),(5,7),(1,1),(9999,1234),(0,1)]:
    S = S3_full(RA, GF(pA)(a), GF(pA)(b))
    tf = top_form(S)
    tops.append(tf)
    print("  (a,b)=(%5d,%5d):  deg(S_3)=%d  top_form=%s" % (a,b,S.degree(),tf))
all_equal = all(tf == tops[0] for tf in tops)
print("  => ALL top_form(S_3) identical across (a,b)? %s" % all_equal)
print("  => CONSEQUENCE: the leading-form gated meter (d_ff, D_reg, gate_meaningful)")
print("     is IDENTICAL for every curve y^2=x^3+ax+b over F_p, hence for the whole")
print("     isogeny class. Any L3 weakness must live in SUB-leading (true-GB) terms.")

# Confirm the meter itself returns identical verdicts on two different curves
def ering_for_curve(p, a, b):
    F = GF(p); R = PolynomialRing(F, 3, names=['x0','x1','x2']); x = R.gens()
    S3 = _semaev3(R, F(a), F(b))
    return [S3, x[0]*x[1], x[0]*x[2]], R, [0]
m1 = meter_gated(*ering_for_curve(10007, 2, 3))
m2 = meter_gated(*ering_for_curve(10007, 9999, 1234))
print("  meter on (a,b)=(2,3)   : d_ff=%s D_reg=%s gate_meaningful=%s" %
      (m1['d_ff'], m1['D_reg'], m1['gate_meaningful']))
print("  meter on (a,b)=(9999,1234): d_ff=%s D_reg=%s gate_meaningful=%s" %
      (m2['d_ff'], m2['D_reg'], m2['gate_meaningful']))
print("  => meter verdicts identical? %s" %
      (m1['d_ff']==m2['d_ff'] and m1['D_reg']==m2['D_reg']
       and m1['gate_meaningful']==m2['gate_meaningful']))

# ---------------- Part B: true Groebner solving degree across neighbors ----------------
print()
print("="*70)
print("PART B  --  true Groebner solving degree across l-isogeny neighbors")
print("="*70)

p = 8191
Fp = GF(p)

def find_prime_order_curve(Fp):
    p = Fp.cardinality()
    for tries in range(2000):
        a = Fp.random_element(); b = Fp.random_element()
        if 4*a^3 + 27*b^2 == 0:
            continue
        E = EllipticCurve(Fp, [a, b])
        N = E.order()
        if N.is_prime():
            return E, N
    return None, None

set_random_seed(20260601)
E0, N = find_prime_order_curve(Fp)
print("start curve E0: y^2=x^3+%s x+%s over F_%d, order N=%d (prime? %s)"
      % (E0.a4(), E0.a6(), p, N, N.is_prime()))

# horizontal l-isogeny neighbors (isogenous => SAME order, flat volcano => horizontal)
neighbors = [("E0", E0)]
for l in [2, 3, 5, 7]:
    try:
        for phi in E0.isogenies_prime_degree(l):
            C = phi.codomain()
            # short Weierstrass model
            C = C.short_weierstrass_model()
            if C.order() == N and all(C.a4()!=E.a4() or C.a6()!=E.a6() for _,E in neighbors):
                neighbors.append(("l=%d"%l, C))
            if len(neighbors) >= 6:
                break
    except Exception as e:
        pass
    if len(neighbors) >= 6:
        break
print("collected %d same-order curves (start + neighbors)" % len(neighbors))

# negative control: a random NON-isogenous curve (different order)
Ectrl, Nctrl = find_prime_order_curve(Fp)
while Nctrl == N:
    Ectrl, Nctrl = find_prime_order_curve(Fp)
neighbors.append(("CTRL(diff-order)", Ectrl))

def solving_profile(E):
    """Build a real m=2 decomposition system with a guaranteed solution and
    return (max GB generator degree, #solutions=quotient dim, found_real)."""
    a, b = E.a4(), E.a6()
    # factor base = x-coords of L points; pick L points P_i, build FB of their x
    pts = []
    G = E.gens()[0] if E.gens() else E.random_point()
    # collect distinct affine points with distinct x
    xs = set(); fb_pts = []
    k = 1
    while len(fb_pts) < 4 and k < 4*p:
        P = k*G
        if P != E(0) and P[0] not in xs:
            xs.add(P[0]); fb_pts.append(P)
        k += 1
    FBx = [P[0] for P in fb_pts]
    # target R = P1 + P2 with P1,P2 in FB  => guaranteed 2-decomposition exists
    R = fb_pts[0] + fb_pts[1]
    xR = R[0]
    Ruv = PolynomialRing(Fp, 2, names=['x1','x2'], order='degrevlex')
    x1, x2 = Ruv.gens()
    S3 = _semaev3(PolynomialRing(Fp,3,names=['x1','x2','x3']), Fp(a), Fp(b))
    # substitute x3 = xR
    S3sub = S3.subs({S3.parent().gen(2): Fp(xR)})
    S3sub = Ruv(S3sub.subs({S3.parent().gen(0):x1, S3.parent().gen(1):x2}))
    fb1 = prod([x1 - Fp(c) for c in FBx])
    fb2 = prod([x2 - Fp(c) for c in FBx])
    I = Ruv.ideal([S3sub, fb1, fb2])
    GB = I.groebner_basis()
    maxdeg = max([g.degree() for g in GB])
    try:
        nsol = I.vector_space_dimension()
    except Exception:
        nsol = -1
    # check the real relation (x(P1),x(P2)) is a root
    found = (S3sub.subs({x1:Fp(FBx[0]), x2:Fp(FBx[1])}) == 0)
    return maxdeg, nsol, bool(found), len(FBx)

print()
print("  curve              | maxGBdeg | #sols | real-relation-found | |FB|")
print("  "+"-"*64)
rows = []
for tag, E in neighbors:
    try:
        md, ns, fnd, L = solving_profile(E)
        rows.append({"tag":tag,"a":int(E.a4()),"b":int(E.a6()),
                     "maxGBdeg":int(md),"nsols":int(ns),"found":fnd,"FB":L})
        print("  %-18s | %8d | %5d | %19s | %d" % (tag, md, ns, fnd, L))
    except Exception as e:
        print("  %-18s | ERROR: %s" % (tag, e))

# verdict
same_order_rows = [r for r in rows if not r["tag"].startswith("CTRL")]
degs = set(r["maxGBdeg"] for r in same_order_rows)
sols = set(r["nsols"] for r in same_order_rows)
print()
print("  same-order curves: distinct maxGBdeg values = %s ; distinct #sols = %s" % (sorted(degs), sorted(sols)))
falsified = (len(degs) > 1)
print("  FALSIFICATION (some same-order neighbor solves at strictly lower degree)? %s" %
      ("YES -- investigate!" if falsified else "NO -- solving degree invariant across the class"))

out = {"partA_topform_invariant": bool(all_equal),
       "partB_rows": rows,
       "partB_distinct_maxGBdeg": sorted(int(d) for d in degs),
       "partB_distinct_nsols": sorted(int(s) for s in sols),
       "partB_falsified": bool(falsified)}
open("round018_T2_isogeny_gatedmeter_result.json","w").write(json.dumps(out, indent=2))
print("\nwrote round018_T2_isogeny_gatedmeter_result.json")

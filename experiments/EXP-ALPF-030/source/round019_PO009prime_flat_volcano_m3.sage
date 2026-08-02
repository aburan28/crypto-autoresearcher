#!/usr/bin/env sage
# ===========================================================================
# round019_PO009prime_flat_volcano_m3.sage  --  PO-009'
# Sharp sub-leading falsification test for the "no weak B" headline.
#
# Setup that fixes round018-T2's two weaknesses:
#   (1) a GENUINE flat-volcano (f=1) toy  -> neighbors are horizontal Cl(O_K)
#       steps (pure L3 coefficient variation, the P-256 analog), not L2 levels.
#   (2) m=3 with S_4 (3 COUPLED summand variables) -> the metric can resolve
#       coefficient effects (m=2 could not: it was |FB|-dominated).
#
# For the start curve + each horizontal l-isogeny neighbor (same order) + a
# different-order negative control, build a real 3-point Semaev decomposition
# [S_4(x1,x2,x3,xR), FB(x1),FB(x2),FB(x3)] with a guaranteed solution and measure:
#   - TRUE solving degree (max degrevlex GB generator degree) and #solutions
#   - leading-form gated meter (d_ff, D_reg, gate_meaningful)  [should be (a,b)-blind]
# A neighbor solving at strictly LOWER true degree => coefficient-level weakness
# => headline falsified at the sub-leading level. Else: strong invariance.
#
# Run: sage round019_PO009prime_flat_volcano_m3.sage
# ===========================================================================
import json
load("round016_gated_meter.sage")   # _semaev3, top_form, meter_gated

# ---------- S_4 via resultant, with a correctness verification ----------
def semaev4(Rbig, a, b):
    """S_4(x1,x2,x3,x4) = Res_X(S_3(x1,x2,X), S_3(x3,x4,X)) for y^2=x^3+ax+b."""
    F = Rbig.base_ring()
    T = PolynomialRing(F, 5, names=['x1','x2','x3','x4','X'])
    x1,x2,x3,x4,X = T.gens()
    def S3(u,v,w):
        return (u-v)^2*w^2 - 2*((u+v)*(u*v+F(a))+2*F(b))*w + ((u*v-F(a))^2 - 4*F(b)*(u+v))
    r = S3(x1,x2,X).resultant(S3(x3,x4,X), X)   # eliminate X
    # map into Rbig (x1..x4)
    sub = {T.gen(i): Rbig.gen(i) for i in range(4)}
    sub[X] = T.gen(4)  # unused after resultant
    return Rbig(r.subs({x1:Rbig.gen(0),x2:Rbig.gen(1),x3:Rbig.gen(2),x4:Rbig.gen(3),X:0}))

def verify_S4(E, S4poly, Rbig, ntest=12):
    """S4 must vanish on x-coords of 4 points summing to O, and be nonzero on random."""
    F = E.base_field()
    ok_zero = 0; ok_nonzero = 0
    for _ in range(ntest):
        P = [E.random_point() for _ in range(3)]
        P4 = -(P[0]+P[1]+P[2])
        if any(Q == E(0) for Q in P+[P4]):
            continue
        v = Rbig(S4poly).subs({Rbig.gen(0):P[0][0], Rbig.gen(1):P[1][0],
                               Rbig.gen(2):P[2][0], Rbig.gen(3):P4[0]})
        if v == 0: ok_zero += 1
    for _ in range(ntest):
        xs = [F.random_element() for _ in range(4)]
        v = Rbig(S4poly).subs({Rbig.gen(i):xs[i] for i in range(4)})
        if v != 0: ok_nonzero += 1
    return ok_zero, ok_nonzero

# ---------- find a FLAT-volcano (f=1) prime-order toy curve ----------
def flat_volcano_prime_curve(Fp, want_h=6):
    p = Fp.cardinality()
    for _ in range(6000):
        a = Fp.random_element(); b = Fp.random_element()
        if 4*a^3+27*b^2 == 0: continue
        E = EllipticCurve(Fp,[a,b]); N = E.order()
        if not N.is_prime(): continue
        t = p+1-N; D = t^2-4*p
        D0 = fundamental_discriminant(D)
        if D == D0:                         # f = 1, FLAT volcano
            h = QuadraticField(D, 'w').class_number()
            if h >= want_h:
                return E, N, D, h
    return None, None, None, None

p = 4099
Fp = GF(p)
set_random_seed(20260601)
E0, N, D, h = flat_volcano_prime_curve(Fp, want_h=4)
print("FLAT-volcano start curve E0: y^2=x^3+%s x+%s / F_%d" % (E0.a4(),E0.a6(),p))
print("  order N=%d (prime=%s), D=t^2-4p=%d, fundamental(f=1)=%s, class number h(D)=%d"
      % (N, N.is_prime(), D, (D==fundamental_discriminant(D)), h))

# horizontal l-isogeny neighbors (flat volcano => all l-isogenies are horizontal)
neighbors = [("E0", E0)]
for l in [2,3,5,7,11,13]:
    for phi in E0.isogenies_prime_degree(l):
        C = phi.codomain().short_weierstrass_model()
        if C.order()==N and all((C.a4(),C.a6())!=(E.a4(),E.a6()) for _,E in neighbors):
            neighbors.append(("l=%d"%l, C))
    if len(neighbors) >= 6: break
print("collected %d same-order (horizontal) curves" % len(neighbors))

# negative control: different-order prime curve
Ec, Nc, _, _ = flat_volcano_prime_curve(Fp, want_h=1)
while Nc == N:
    Ec, Nc, _, _ = flat_volcano_prime_curve(Fp, want_h=1)
neighbors.append(("CTRL(diff-order)", Ec))

# ---------- per-curve m=3 solving profile ----------
def profile(E, Lfb=3):
    a,b = E.a4(), E.a6()
    F = E.base_field()
    # factor base: x-coords of Lfb points; target R = P1+P2+P3 (guaranteed 3-decomp)
    G = E.gens()[0] if E.gens() else E.random_point()
    xs=set(); pts=[]; k=1
    while len(pts) < Lfb and k < 8*p:
        P=k*G
        if P!=E(0) and P[0] not in xs: xs.add(P[0]); pts.append(P)
        k+=1
    FBx=[P[0] for P in pts]
    R = pts[0]+pts[1]+pts[2]; xR=R[0]
    Rbig = PolynomialRing(F,4,names=['x1','x2','x3','x4'])
    S4 = semaev4(Rbig, a, b)
    okz, oknz = verify_S4(E, S4, Rbig, ntest=10)
    # substitute target x4=xR -> 3-variable decomposition system
    R3 = PolynomialRing(F,3,names=['x1','x2','x3'],order='degrevlex')
    x1,x2,x3 = R3.gens()
    S4sub = R3(S4.subs({Rbig.gen(3):F(xR)}).subs(
        {Rbig.gen(0):x1,Rbig.gen(1):x2,Rbig.gen(2):x3}))
    fbs = [prod([R3.gen(i)-F(c) for c in FBx]) for i in range(3)]
    I = R3.ideal([S4sub]+fbs)
    GB = I.groebner_basis()
    maxdeg = max([g.degree() for g in GB])
    try: nsol = I.vector_space_dimension()
    except Exception: nsol = -1
    # leading-form meter (sumpoly index 0 = S4sub)
    mg = meter_gated([S4sub]+fbs, R3, [0], Dmax=14)
    found = (S4sub.subs({x1:F(FBx[0]),x2:F(FBx[1]),x3:F(FBx[2])})==0)
    return {"a":int(a),"b":int(b),"S4deg":int(S4.degree()),"S4_vanish_ok":int(okz),
            "S4_nonzero_ok":int(oknz),"maxGBdeg":int(maxdeg),"nsols":int(nsol),
            "found":bool(found),"d_ff":mg['d_ff'],"D_reg":mg['D_reg'],
            "gate_meaningful":mg['gate_meaningful']}

print()
hdr = "  curve            |S4deg|S4ok(0/nz)|maxGBdeg|#sols|found| d_ff|D_reg|gate"
print(hdr); print("  "+"-"*len(hdr))
rows=[]
for tag,E in neighbors:
    try:
        r = profile(E); r["tag"]=tag; rows.append(r)
        print("  %-16s| %3d | %2d/%2d   | %5d  |%4d | %3s |%4s |%4s |%s"
              % (tag,r["S4deg"],r["S4_vanish_ok"],r["S4_nonzero_ok"],r["maxGBdeg"],
                 r["nsols"],r["found"],str(r["d_ff"]),str(r["D_reg"]),r["gate_meaningful"]))
    except Exception as e:
        print("  %-16s| ERROR: %s" % (tag,e))

same = [r for r in rows if not r["tag"].startswith("CTRL")]
degs = sorted(set(r["maxGBdeg"] for r in same))
dffs = sorted(set((r["d_ff"] if r["d_ff"] is not None else -1) for r in same))
gms  = sorted(set(r["gate_meaningful"] for r in same))
print()
print("  same-order curves: maxGBdeg set=%s  d_ff set=%s  gate_meaningful set=%s" % (degs,dffs,gms))
ctrl = [r for r in rows if r["tag"].startswith("CTRL")]
ctrl_distinct = bool(ctrl) and (ctrl[0]["maxGBdeg"] not in degs or
                                (ctrl[0]["d_ff"] if ctrl[0]["d_ff"] else -1) not in dffs)
falsified = (len(degs)>1) or (len(dffs)>1) or (len(gms)>1)
print("  metric has resolution (control differs from same-order)? %s" % ctrl_distinct)
print("  FALSIFIED (a same-order neighbor solves/falls strictly lower)? %s"
      % ("YES -- INVESTIGATE" if falsified else "NO -- invariant across the flat-volcano class"))

json.dump({"start":{"p":int(p),"N":int(N),"D":int(D),"h":int(h)},"rows":rows,
           "same_order_maxGBdeg":[int(x) for x in degs],"same_order_dff":[int(x) for x in dffs],
           "control_has_resolution":bool(ctrl_distinct),"falsified":bool(falsified)},
          open("round019_PO009prime_result.json","w"), indent=2)
print("\nwrote round019_PO009prime_result.json")

# EXP-ISO-001 executor: isogeny-neighborhood audit of PDP behavior.
# For a base curve, its l-isogeny neighbors (l in {2,3,5,7}, same order), and random
# same-p controls: measure (a) m=3 chained Semaev solving degree d_reg, (b) decomposition
# YIELD = #distinct reachable R = F_i+F_j+F_k over a small factor base, / group order.
# Separates a genuine isogeny effect from coefficient variance (the controls). JSON out.
import time, json, sys

def maxdeg(gb): return int(max((g.total_degree() for g in gb if g != 0), default=0))
def S3(X1,X2,X3,a,b):
    return ((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+a)+2*b)*X3 + ((X1*X2-a)**2 - 4*b*(X1+X2)))

def small_fb(E, dd):
    F = E.base_field(); p = F.characteristic(); pts = []
    x = 0
    while len(pts) < dd and x < p:
        try:
            P = E.lift_x(F(x))
            if not P.is_zero(): pts.append(P)
        except Exception:
            pass
        x += 1
    return pts

def dreg_m3(E, dd):
    F = E.base_field(); a4,a6 = E.a4(), E.a6()
    FB = small_fb(E, dd)
    if len(FB) < 3: return None
    # decomposable target R = F0+F1+F2 so the system is a genuine solve
    R = FB[0] + FB[1] + FB[2]
    if R.is_zero(): R = FB[0] + FB[1] + FB[3] if len(FB) > 3 else R
    xR = R.xy()[0]
    Rp = PolynomialRing(F, ['x1','x2','x3','u'], order='degrevlex'); x1,x2,x3,u = Rp.gens()
    FBx = [P.xy()[0] for P in FB]
    I = Rp.ideal([S3(x1,x2,u,a4,a6), S3(u,x3,xR,a4,a6),
                  prod(x1-f for f in FBx), prod(x2-f for f in FBx), prod(x3-f for f in FBx)])
    gb = I.groebner_basis()
    try: dim = int(I.dimension())
    except Exception: dim = None
    return {"d_reg": maxdeg(gb), "dim": dim}

def yield_m3(E, dd):
    FB = small_fb(E, dd)
    if len(FB) < 3: return None
    N = int(E.order())
    reach = set()
    n = len(FB)
    for i in range(n):
        for j in range(i, n):
            Sij = FB[i] + FB[j]
            for k in range(j, n):
                T = Sij + FB[k]
                if not T.is_zero():
                    reach.add(T.xy()[0])
    return {"reachable": len(reach), "N": N, "yield": float(len(reach))/N}

def main():
    p = int(next_prime(2**13)); F = GF(p)
    set_random_seed(20260716)
    # base curve
    while True:
        a=F(randint(1,p-1)); b=F(randint(1,p-1))
        if 4*a**3+27*b**2 != 0: E0=EllipticCurve(F,[a,b]); break
    N0 = int(E0.order())
    curves = [("base", E0)]
    seen_j = {E0.j_invariant()}
    for l in [2,3,5,7]:
        try:
            for phi in E0.isogenies_prime_degree(l):
                C = phi.codomain()
                if C.j_invariant() not in seen_j:
                    seen_j.add(C.j_invariant()); curves.append((f"iso{l}", C))
                if len([c for c in curves if c[0].startswith('iso')]) >= 6: break
        except Exception as e:
            pass
    # random same-p controls (coefficient variance; various orders)
    nc = 0
    while nc < 8:
        a=F(randint(1,p-1)); b=F(randint(1,p-1))
        if 4*a**3+27*b**2 == 0: continue
        C = EllipticCurve(F,[a,b]); curves.append(("ctl", C)); nc += 1
    out = {"p":p, "base_order":N0, "m":3, "d":8, "rows":[]}
    for tag, C in curves:
        dr = dreg_m3(C, 8); yd = yield_m3(C, 8)
        row = {"tag":tag, "j":str(C.j_invariant()), "order":int(C.order()),
               "same_order_as_base": bool(int(C.order())==N0),
               "d_reg": (dr or {}).get("d_reg"), "dim": (dr or {}).get("dim"),
               "yield": (yd or {}).get("yield"), "reachable": (yd or {}).get("reachable")}
        out["rows"].append(row)
        print(f"{tag:<6} ord={row['order']} same={row['same_order_as_base']} "
              f"d_reg={row['d_reg']} yield={row['yield']:.4g} reach={row['reachable']}",
              file=sys.stderr, flush=True)
    # summary: control yield band vs isogeny neighbors
    ctlY = [r["yield"] for r in out["rows"] if r["tag"]=="ctl" and r["yield"] is not None]
    isoY = [r["yield"] for r in out["rows"] if r["tag"].startswith("iso") and r["yield"] is not None]
    import statistics as st
    if ctlY:
        m = st.mean(ctlY); s = st.pstdev(ctlY) if len(ctlY)>1 else 0.0
        out["control_yield_mean"]=m; out["control_yield_sd"]=s
        out["iso_yields"]=isoY
        out["any_iso_dreg_below_2"]=any((r["d_reg"] is not None and r["d_reg"]<2) for r in out["rows"] if r["tag"].startswith("iso"))
        out["any_iso_yield_outlier"]=any(y > m+3*s for y in isoY) if s>0 else None
        print(f"\nCONTROL yield mean={m:.4g} sd={s:.2g} ; ISO yields={[round(y,4) for y in isoY]}",
              file=sys.stderr, flush=True)
        print(f"any iso d_reg<2? {out['any_iso_dreg_below_2']} ; any iso yield>mean+3sd? {out['any_iso_yield_outlier']}",
              file=sys.stderr, flush=True)
    def _ser(o):
        try: return int(o)
        except Exception: return float(o)
    print(json.dumps(out, default=_ser))

main()

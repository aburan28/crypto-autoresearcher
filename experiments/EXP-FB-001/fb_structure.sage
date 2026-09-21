# EXP-FB-001 executor: factor-base STRUCTURE sweep on prime-field PDP.
# One curve; factor bases of size d in structures {random, interval (small x),
# mult-subgroup (x in a subgroup of F_p*), arithmetic-progression (x in an AP)}.
# Per structure, per d: decomposition YIELD (distinct reachable R = F_i+F_j+F_k / N),
# m=3 chained Semaev d_reg, and solve wall-time. Win = a structure with yield or
# solve-cost exponent scaling better than the RANDOM control. Kill = all constant-factor.
import time, json, sys

def maxdeg(gb): return int(max((g.total_degree() for g in gb if g != 0), default=0))
def S3(X1,X2,X3,a,b):
    return ((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+a)+2*b)*X3 + ((X1*X2-a)**2 - 4*b*(X1+X2)))

def points_with_x_in(E, xset, dd):
    F = E.base_field(); pts = []
    for xv in xset:
        try:
            P = E.lift_x(F(xv))
            if not P.is_zero(): pts.append(P)
        except Exception: pass
        if len(pts) >= dd: break
    return pts

def make_fb(E, structure, dd, seed):
    F = E.base_field(); p = int(F.characteristic()); set_random_seed(seed)
    if structure == "random":
        xs = []
        while len(xs) < 6*dd: xs.append(randint(0, p-1))
        return points_with_x_in(E, xs, dd)
    if structure == "interval":
        return points_with_x_in(E, range(0, 6*dd), dd)
    if structure == "subgroup":         # x in a multiplicative subgroup of F_p*
        g = F.multiplicative_generator(); h = g**((p-1)//max(2, (p-1).gcd(64) or 2))
        # take x = h^k (a small subgroup); fall back to powers of a small-order elt
        ordh = h.multiplicative_order()
        xs = [h**k for k in range(min(ordh, 8*dd))]
        return points_with_x_in(E, xs, dd)
    if structure == "ap":               # x in an arithmetic progression
        step = 7
        return points_with_x_in(E, [(3 + step*k) % p for k in range(8*dd)], dd)
    return []

def yield_and_dreg(E, FB, dd):
    F = E.base_field(); a4,a6 = E.a4(), E.a6(); N = int(E.order())
    if len(FB) < 3: return None
    reach = set(); n = len(FB)
    for i in range(n):
        for j in range(i, n):
            Sij = FB[i]+FB[j]
            for k in range(j, n):
                T = Sij + FB[k]
                if not T.is_zero(): reach.add(T.xy()[0])
    R = FB[0]+FB[1]+FB[2]
    if R.is_zero(): return {"yield": float(len(reach))/N, "reachable": len(reach), "d_reg": None, "time": None}
    xR = R.xy()[0]
    Rp = PolynomialRing(F, ['x1','x2','x3','u'], order='degrevlex'); x1,x2,x3,u = Rp.gens()
    FBx = [P.xy()[0] for P in FB]
    I = Rp.ideal([S3(x1,x2,u,a4,a6), S3(u,x3,xR,a4,a6),
                  prod(x1-f for f in FBx), prod(x2-f for f in FBx), prod(x3-f for f in FBx)])
    t0=time.time(); gb=I.groebner_basis(); dt=time.time()-t0
    return {"yield": float(len(reach))/N, "reachable": len(reach), "d_reg": maxdeg(gb), "time": float(dt)}

def main():
    p = int(next_prime(2**14)); F = GF(p); set_random_seed(11)
    while True:
        a=F(randint(1,p-1)); b=F(randint(1,p-1))
        if 4*a**3+27*b**2 != 0: E=EllipticCurve(F,[a,b]); break
    N = int(E.order())
    Ds = [6, 8, 10, 12]; structs = ["random","interval","subgroup","ap"]; seeds=[1,2,3]
    out = {"p":p, "order":N, "m":3, "Ds":[int(x) for x in Ds], "rows":[]}
    for struct in structs:
        for dd in Ds:
            ys=[]; drs=[]; ts=[]
            for seed in seeds:
                FB = make_fb(E, struct, dd, seed)
                if len(FB) < 3: continue
                r = yield_and_dreg(E, FB, dd)
                if r is None: continue
                ys.append(r["yield"]);
                if r["d_reg"] is not None: drs.append(r["d_reg"]); ts.append(r["time"])
            if not ys: continue
            row = {"struct":struct, "d":int(dd),
                   "yield_mean": float(sum(ys)/len(ys)),
                   "d_reg": (drs[len(drs)//2] if drs else None),
                   "time_med": (sorted(ts)[len(ts)//2] if ts else None)}
            out["rows"].append(row)
            print(f"{struct:<9} d={dd:<3} yield={row['yield_mean']:.4g} d_reg={row['d_reg']} t={row['time_med']}",
                  file=sys.stderr, flush=True)
    # compare each structure's yield/time to random at matched d
    def by(struct):
        return {r["d"]: r for r in out["rows"] if r["struct"]==struct}
    rnd = by("random"); flags=[]
    for struct in structs:
        if struct=="random": continue
        for dd,r in by(struct).items():
            if dd in rnd and rnd[dd]["yield_mean"]>0:
                ratio = r["yield_mean"]/rnd[dd]["yield_mean"]
                if ratio > 1.5: flags.append((struct,dd,"yield",round(ratio,2)))
    out["yield_outliers_vs_random_gt_1.5x"]=flags
    print(f"\nyield outliers vs random (>1.5x): {flags}", file=sys.stderr, flush=True)
    def _ser(o):
        try: return int(o)
        except Exception: return float(o)
    print(json.dumps(out, default=_ser))

main()

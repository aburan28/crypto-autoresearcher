# EXP-REP-002 executor: m=3 chained PDP solving degree, Edwards native (8 vars)
# vs Weierstrass Semaev chained (the T1 baseline, x-membership). Same curve+points.
# Verifies non-degeneracy (dim, vdim, planted-root) for every arm. JSON to stdout.
import time, json, sys

def maxdeg(gb): return int(max((g.total_degree() for g in gb if g != 0), default=0))

def S3(X1, X2, X3, a, b):
    return ((X1 - X2)**2 * X3**2 - 2*((X1 + X2)*(X1*X2 + a) + 2*b) * X3
            + ((X1*X2 - a)**2 - 4*b*(X1 + X2)))

def build_curve(p, seed):
    F = GF(p); set_random_seed(seed); a = F(1)
    while True:
        d = F(randint(2, p-1))
        if d != 0 and d != a and not d.is_square(): break
    A = 2*(a+d)/(a-d); B = 4/(a-d)
    a4 = (3 - A**2)/(3*B**2); a6 = (2*A**3 - 9*A)/(27*B**3)
    EW = EllipticCurve(F, [a4, a6])
    def ed_points(n):
        pts = []
        while len(pts) < n:
            xE = F(randint(1, p-1)); num = 1 - a*xE**2; den = 1 - d*xE**2
            if den == 0: continue
            rhs = num/den
            if rhs.is_square():
                yE = rhs.sqrt()
                if yE not in (F(1), F(-1)) and xE != 0: pts.append((xE, yE))
        return pts
    def ed_to_W(P):
        xE, yE = P; uM=(1+yE)/(1-yE); vM=(1+yE)/(xE*(1-yE))
        return (uM/B + A/(3*B), vM/B)
    def ed_add(P, Q):
        x1,y1=P; x2,y2=Q
        return ((x1*y2+y1*x2)/(1+d*x1*x2*y1*y2), (y1*y2-a*x1*x2)/(1-d*x1*x2*y1*y2))
    return F, a, d, EW, ed_points, ed_to_W, ed_add

def diag(I, planted):
    try: dim = int(I.dimension())
    except Exception: dim = None
    vdim = None
    if dim == 0:
        try: vdim = int(I.vector_space_dimension())
        except Exception: vdim = None
    proot = all(g.subs(planted) == 0 for g in I.gens())
    return dim, vdim, bool(proot)

def run_edwards_m3(F, a, d, FBed, Fpts, R, U, dd):
    Rp = PolynomialRing(F, ['x1','y1','x2','y2','x3','y3','xu','yu'], order='degrevlex')
    x1,y1,x2,y2,x3,y3,xu,yu = Rp.gens()
    xR,yR = R; xU,yU = U
    cur = lambda X,Y: a*X**2 + Y**2 - 1 - d*X**2*Y**2
    eqs = [cur(x1,y1), cur(x2,y2), cur(x3,y3), cur(xu,yu),
           x1*y2 + y1*x2 - xu*(1 + d*x1*x2*y1*y2),        # P1+P2=U
           y1*y2 - a*x1*x2 - yu*(1 - d*x1*x2*y1*y2),
           xu*y3 + yu*x3 - xR*(1 + d*xu*x3*yu*y3),        # U+P3=R
           yu*y3 - a*xu*x3 - yR*(1 - d*xu*x3*yu*y3)]
    FBy = [P[1] for P in FBed]
    eqs += [prod(y1-f for f in FBy), prod(y2-f for f in FBy), prod(y3-f for f in FBy)]
    I = Rp.ideal(eqs)
    planted = {x1:Fpts[0][0], y1:Fpts[0][1], x2:Fpts[1][0], y2:Fpts[1][1],
               x3:Fpts[2][0], y3:Fpts[2][1], xu:U[0], yu:U[1]}
    t0=time.time(); gb=I.groebner_basis(); dt=time.time()-t0
    dim,vdim,pr = diag(I, planted)
    return dict(d_reg=maxdeg(gb), time=float(dt), dim=dim, vdim=vdim, planted_root=pr)

def run_weier_semaev_m3(F, EW, FBw, Rw, Uw, dd):
    a4,a6 = EW.a4(), EW.a6(); xR = Rw[0]; xU = Uw[0]
    Rp = PolynomialRing(F, ['x1','x2','x3','u'], order='degrevlex'); x1,x2,x3,u = Rp.gens()
    FBx = [P[0] for P in FBw]
    eqs = [S3(x1,x2,u,a4,a6), S3(u,x3,xR,a4,a6),
           prod(x1-f for f in FBx), prod(x2-f for f in FBx), prod(x3-f for f in FBx)]
    I = Rp.ideal(eqs)
    planted = {x1:FBw[0][0], x2:FBw[1][0], x3:FBw[2][0], u:xU}
    t0=time.time(); gb=I.groebner_basis(); dt=time.time()-t0
    dim,vdim,pr = diag(I, planted)
    return dict(d_reg=maxdeg(gb), time=float(dt), dim=dim, vdim=vdim, planted_root=pr)

def main():
    p = int(next_prime(2**16)); Ds=[4,6,8]; seeds=[1,2,3]; STOP=150.0
    out = {"p":p, "m":3, "Ds":[int(x) for x in Ds], "seeds":[int(x) for x in seeds],
           "map_verified":[], "rows":[]}
    for seed in seeds:
        F,a,d,EW,ed_points,ed_to_W,ed_add = build_curve(p, seed)
        Ps = ed_points(max(Ds)+8)
        out["map_verified"].append(bool(all(EW.is_on_curve(*ed_to_W(P)) for P in Ps[:3])))
        stop_ed=False
        for dd in Ds:
            FBed = Ps[:dd]; FBw = [ed_to_W(P) for P in FBed]
            F0,F1,F2 = FBed[0], FBed[1], FBed[2]
            Ued = ed_add(F0, F1); Red = ed_add(Ued, F2)
            Uw = ed_to_W(Ued); Rw = ed_to_W(Red)
            row = {"seed":int(seed), "d":int(dd), "arms":{}}
            row["arms"]["W_semaev_m3"] = run_weier_semaev_m3(F, EW, FBw, Rw, Uw, dd)
            if not stop_ed:
                r = run_edwards_m3(F, a, d, FBed, [F0,F1,F2], Red, Ued, dd)
                row["arms"]["ED_native_m3"] = r
                if r["time"] > STOP: stop_ed = True
            out["rows"].append(row)
            g = row["arms"]
            se = g.get("ED_native_m3", {})
            print(f"seed={seed} d={dd}  W_semaev={g['W_semaev_m3']['d_reg']}"
                  f"[{g['W_semaev_m3']['dim']},{g['W_semaev_m3']['vdim']},{g['W_semaev_m3']['planted_root']}]"
                  f"  ED_native={se.get('d_reg')}[{se.get('dim')},{se.get('vdim')},{se.get('planted_root')}]"
                  f"  t_ed={se.get('time')}", file=sys.stderr, flush=True)
    def _ser(o):
        try: return int(o)
        except Exception: return float(o)
    print(json.dumps(out, default=_ser))

main()

# EXP-REP-001 executor v2: model-native PDP solving degree, twisted-Edwards vs
# Weierstrass, with the FAIR Weierstrass-Semaev baseline AND non-degeneracy
# verification (dim, #solutions, planted-root check) for every arm. Any d_reg=2
# arm is only evidence if the ideal is 0-dim, consistent, and contains the true
# decomposition. Emits JSON to stdout; progress to stderr.
import time, json, sys

def maxdeg(gb):
    return int(max((g.total_degree() for g in gb if g != 0), default=0))

def S3(X1, X2, X3, a, b):                       # Weierstrass chord Semaev (x-only)
    return ((X1 - X2)**2 * X3**2
            - 2*((X1 + X2)*(X1*X2 + a) + 2*b) * X3
            + ((X1*X2 - a)**2 - 4*b*(X1 + X2)))

def build_curve(p, seed):
    F = GF(p); set_random_seed(seed)
    a = F(1)
    while True:
        d = F(randint(2, p-1))
        if d != 0 and d != a and not d.is_square(): break
    A = 2*(a+d)/(a-d); B = 4/(a-d)
    a4 = (3 - A**2)/(3*B**2); a6 = (2*A**3 - 9*A)/(27*B**3)
    EW = EllipticCurve(F, [a4, a6])
    def edwards_points(n):
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
        xE, yE = P
        uM = (1+yE)/(1-yE); vM = (1+yE)/(xE*(1-yE))
        return (uM/B + A/(3*B), vM/B)
    def ed_add(P, Q):
        x1,y1 = P; x2,y2 = Q
        return ((x1*y2 + y1*x2)/(1 + d*x1*x2*y1*y2), (y1*y2 - a*x1*x2)/(1 - d*x1*x2*y1*y2))
    return F, a, d, A, B, EW, edwards_points, ed_to_W, ed_add

def diag(I, planted):
    """(dim, vdim_capped, planted_is_root) — verify the arm is a real, non-degenerate solve."""
    try: dim = int(I.dimension())
    except Exception: dim = None
    vdim = None
    if dim == 0:
        try: vdim = int(I.vector_space_dimension())
        except Exception: vdim = None
    proot = all(g.subs(planted) == 0 for g in I.gens())
    return dim, vdim, bool(proot)

def run_native(F, model, curve, FB, R, d, coord):
    a, dpar, EW = curve['a'], curve['d'], curve['EW']
    Rp = PolynomialRing(F, ['x1','y1','x2','y2'], order='degrevlex')
    x1,y1,x2,y2 = Rp.gens()
    if model == 'edwards':
        xR,yR = R['ed']; FBpt = FB['ed']; P0,P1 = FB['ed'][0], FB['ed'][1]
        eqs = [x1*y2 + y1*x2 - xR*(1 + dpar*x1*x2*y1*y2),
               y1*y2 - a*x1*x2 - yR*(1 - dpar*x1*x2*y1*y2),
               a*x1**2 + y1**2 - 1 - dpar*x1**2*y1**2,
               a*x2**2 + y2**2 - 1 - dpar*x2**2*y2**2]
    else:
        xR,yR = R['w']; a4,a6 = EW.a4(), EW.a6(); FBpt = FB['w']; P0,P1 = FB['w'][0], FB['w'][1]
        eqs = [(y2 - y1)*(xR - x1) - (-yR - y1)*(x2 - x1),
               y1**2 - (x1**3 + a4*x1 + a6), y2**2 - (x2**3 + a4*x2 + a6)]
    ci = 0 if coord == 'x' else 1
    v1,v2 = (x1,x2) if coord == 'x' else (y1,y2)
    FBc = [P[ci] for P in FBpt]
    m1 = prod(v1 - f for f in FBc); m2 = prod(v2 - f for f in FBc)
    I = Rp.ideal(eqs + [m1, m2])
    planted = {x1:P0[0], y1:P0[1], x2:P1[0], y2:P1[1]}
    t0 = time.time(); gb = I.groebner_basis(); dt = time.time()-t0
    dim,vdim,proot = diag(I, planted)
    return dict(d_reg=maxdeg(gb), time=float(dt), dim=dim, vdim=vdim, planted_root=proot)

def run_semaev(F, curve, FBw, Rw, d):
    """FAIR Weierstrass baseline: y-eliminated Semaev S3 in x-coords, x-membership."""
    a4,a6 = curve['EW'].a4(), curve['EW'].a6(); xR = Rw[0]
    Rp = PolynomialRing(F, ['x1','x2'], order='degrevlex'); x1,x2 = Rp.gens()
    FBx = [P[0] for P in FBw]
    I = Rp.ideal([S3(x1,x2,xR,a4,a6), prod(x1-f for f in FBx), prod(x2-f for f in FBx)])
    planted = {x1:FBw[0][0], x2:FBw[1][0]}
    t0 = time.time(); gb = I.groebner_basis(); dt = time.time()-t0
    dim,vdim,proot = diag(I, planted)
    return dict(d_reg=maxdeg(gb), time=float(dt), dim=dim, vdim=vdim, planted_root=proot)

def random_null(F, deg_list, d):
    Rp = PolynomialRing(F, ['x1','y1','x2','y2'], order='degrevlex'); gens = Rp.gens()
    def rp(deg):
        mons = [prod(g**e for g,e in zip(gens,ex)) for ex in IntegerVectors(deg,4)] if deg>0 else [Rp(1)]
        return sum(F(randint(0,int(F.characteristic())-1))*mm for mm in mons)
    I = Rp.ideal([rp(dg) for dg in deg_list] + [rp(d), rp(d)])
    t0=time.time(); gb=I.groebner_basis(); dt=time.time()-t0
    return dict(d_reg=maxdeg(gb), time=float(dt))

def main():
    p = int(next_prime(2**16)); Ds=[4,6,8,12,16]; seeds=[1,2,3]
    out = {"p": p, "m": 2, "Ds": [int(x) for x in Ds], "seeds": [int(x) for x in seeds],
           "map_verified": [], "rows": []}
    for seed in seeds:
        F,a,d,A,B,EW,ed_points,ed_to_W,ed_add = build_curve(p, seed)
        curve = {'a':a,'d':d,'EW':EW}
        Ps = ed_points(max(Ds)+6)
        out["map_verified"].append(bool(all(EW.is_on_curve(*ed_to_W(P)) for P in Ps[:3])))
        for dd in Ds:
            FBed = Ps[:dd]; FBw = [ed_to_W(P) for P in FBed]; FB={'ed':FBed,'w':FBw}
            Red = ed_add(FBed[0], FBed[1]); Rw = ed_to_W(Red); R={'ed':Red,'w':Rw}
            row = {"seed":int(seed), "d":int(dd), "arms":{}}
            row["arms"]["W_semaev"] = run_semaev(F, curve, FBw, Rw, dd)
            row["arms"]["W_native_x"] = run_native(F,'weierstrass',curve,FB,R,dd,'x')
            row["arms"]["ED_x"] = run_native(F,'edwards',curve,FB,R,dd,'x')
            row["arms"]["ED_y"] = run_native(F,'edwards',curve,FB,R,dd,'y')
            row["null"] = random_null(F,[2,3,3],dd)
            out["rows"].append(row)
            g = row["arms"]
            print(f"seed={seed} d={dd}  d_reg[dim,vdim,root]:  "
                  f"W_semaev={g['W_semaev']['d_reg']}[{g['W_semaev']['dim']},{g['W_semaev']['vdim']},{g['W_semaev']['planted_root']}]  "
                  f"W_native_x={g['W_native_x']['d_reg']}[{g['W_native_x']['dim']},{g['W_native_x']['vdim']},{g['W_native_x']['planted_root']}]  "
                  f"ED_x={g['ED_x']['d_reg']}[{g['ED_x']['dim']},{g['ED_x']['vdim']},{g['ED_x']['planted_root']}]  "
                  f"ED_y={g['ED_y']['d_reg']}[{g['ED_y']['dim']},{g['ED_y']['vdim']},{g['ED_y']['planted_root']}]",
                  file=sys.stderr, flush=True)
    def _ser(o):
        try: return int(o)
        except Exception: return float(o)
    print(json.dumps(out, default=_ser))

main()

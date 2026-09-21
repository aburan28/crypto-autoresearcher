# BIN-EXP-009 : the m=4 DIAGONAL point for PO-BIN-001(b) -- D_solv at m=4 (S5).
#
# Blocked before by the S5.subs symbolic descent explosion (deg-32, per-var-deg-8 S5).
# UNBLOCKED here by the VALIDATED substitution-free EVALUATION descent: build each F2
# component of Phi=S5(x_1..x_4, xR) by evaluating S5 over all 2^nvars boolean
# c-assignments and Moebius-transforming each F2-coordinate to a boolean polynomial.
# (Validated against the symbolic descent at m=3 n=11: component sets byte-identical.)
#
# Then measure D_solv = max msolve-F4 matrix degree (the cost-relevant solving degree,
# same instrument as BIN-EXP-008 which gave D_solv=7 at m=3). Two clean (m,D_solv)
# points (m=3 -> 7; m=4 -> ?) are the first empirical handle on the Petit-Quisquater
# DIAGONAL PO-BIN-001(b): does D_solv jump sharply with m (disproof side) or stay
# moderate (bounded-degree side)? Toy/scaled; not a real break.
import json, time, signal
LOGP="/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp009_m4_diagonal.log"
_lf=open(LOGP,"w")
def out(s):
    print(s); _lf.write(str(s)+"\n"); _lf.flush()
out("=== BIN-EXP-009 m=4 diagonal D_solv (eval-descent + msolve) === "+time.asctime())

class Timeout(Exception): pass
def _alarm(sig,frm): raise Timeout()
signal.signal(signal.SIGALRM,_alarm)

def make_curve(n,seed=1):
    set_random_seed(int(seed))
    F=GF(2**n,'a'); a=F.gen(); best=None
    for _ in range(200):
        a2=F.random_element(); a6=F.random_element()
        if a6.is_zero(): continue
        try: E=EllipticCurve(F,[1,a2,0,0,a6])
        except Exception: continue
        N=E.order(); big=max(p for p,e in factor(N))
        if best is None or big>best[5]: best=(F,a,E,a2,a6,big,N)
        if big>=N//2: return F,a,E,a2,a6,N,big
    F,a,E,a2,a6,big,N=best; return F,a,E,a2,a6,N,big

def build_S(F,a6,m):
    def S3(R,u,v,w): return (u*v+u*w+v*w)**2+u*v*w+a6
    if m==3:
        Pt=PolynomialRing(F,'X1,X2,X3,X4,T'); X1,X2,X3,X4,T=Pt.gens()
        S=S3(Pt,X1,X2,T).resultant(S3(Pt,X3,X4,T),T)
        P=PolynomialRing(F,'X1,X2,X3,X4'); g=P.gens()
        S=P(S.subs({X1:g[0],X2:g[1],X3:g[2],X4:g[3],T:0}))
    elif m==4:
        Pt=PolynomialRing(F,'X1,X2,X3,X4,X5,T,U'); X1,X2,X3,X4,X5,T,U=Pt.gens()
        S4a=S3(Pt,X3,X4,U).resultant(S3(Pt,U,X5,T),U)
        S=S3(Pt,X1,X2,T).resultant(S4a,T)
        P=PolynomialRing(F,'X1,X2,X3,X4,X5'); g=P.gens()
        S=P(S.subs({X1:g[0],X2:g[1],X3:g[2],X4:g[3],X5:g[4],T:0,U:0}))
    else: raise ValueError(m)
    try: S=prod(f for f,e in factor(S))
    except Exception: pass
    return P,S

def verify_S(E,P,S,m,ntest=15):
    arity=m+1; van=tot=nz=ntot=0; tries=0
    while tot<ntest and tries<8000:
        tries+=1
        pts=[E.random_point() for _ in range(arity-1)]; pts.append(-sum(pts,E(0)))
        if any(Q.is_zero() for Q in pts): continue
        van+=(S(*[Q.xy()[0] for Q in pts])==0); tot+=1
    tries=0
    while ntot<ntest and tries<10000:
        tries+=1
        pts=[E.random_point() for _ in range(arity)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts,E(0)).is_zero(): continue
        nz+=(S(*[Q.xy()[0] for Q in pts])!=0); ntot+=1
    return van,tot,nz,ntot

def eval_descent(F,a,m,l,S,P,xR_val,n):
    """substitution-free Weil descent via evaluation + Moebius transform (VALIDATED
    against symbolic at m=3 n=11). Returns boolean-poly components + the ring B."""
    nvars=m*l; w=[a**j for j in range(l)]
    Vsp,frm,to=F.vector_space(map=True)
    gp=P.gens()
    truth=[[0]*(2**nvars) for _ in range(n)]
    for idx in range(2**nvars):
        bits=[(idx>>b)&1 for b in range(nvars)]
        xs=[sum((w[j] for j in range(l) if bits[i*l+j]),F(0)) for i in range(m)]
        coords=to(S(*(xs+[xR_val])))
        for k in range(n):
            if coords[k]!=0: truth[k][idx]=1
    names=['c%d_%d'%(i,j) for i in range(m) for j in range(l)]
    B=BooleanPolynomialRing(nvars,names); Bg=B.gens()
    comps=[]
    for k in range(n):
        tt=truth[k][:]
        for b in range(nvars):
            step=1<<b
            for i in range(2**nvars):
                if i&step: tt[i]=tt[i]^^tt[i^^step]   # ^^ = XOR in Sage (^ means power!)
        poly=B(0)
        for mask in range(2**nvars):
            if tt[mask]:
                mono=B(1)
                for b in range(nvars):
                    if (mask>>b)&1: mono=mono*Bg[b]
                poly=poly+mono
        if poly!=0: comps.append(poly)
    return comps,B,names

def msolve_Dsolv(comps,names,nvars,tag,tcap=120):
    """write boolean system + field eqs to msolve, run -v2, return max F4 degree + finished."""
    lines=[",".join(names),"2"]; ps=[]
    for g in comps:
        terms=["*".join(names[i] for i in mo.iterindex()) if list(mo.iterindex()) else "1" for mo in g.monomials()]
        ps.append("+".join(terms) if terms else "0")
    for nm in names: ps.append("%s^2+%s"%(nm,nm))
    lines.append(",\n".join(ps))
    fn="/tmp/ms9_%s.ms"%tag; open(fn,"w").write("\n".join(lines)+"\n")
    import subprocess
    vf="/tmp/ms9_%s.v"%tag
    try:
        with open(vf,"w") as vfh:
            subprocess.run(["msolve","-v","2","-f",fn,"-o","/tmp/ms9_%s.out"%tag],
                           stdout=vfh, stderr=subprocess.STDOUT, timeout=tcap)
        finished=True
    except subprocess.TimeoutExpired:
        finished=False
    import re
    maxdeg=0
    for ln in open(vf):
        mt=re.match(r'\s*(\d+)\s+\d+\s+\d+\s+\d+\s*x\s*\d+',ln)
        if mt: maxdeg=max(maxdeg,int(mt.group(1)))
    return maxdeg,finished

def cell(n,m,seed=1,tcap_total=600,msolve_cap=150):
    r={"n":n,"m":m}
    signal.alarm(int(tcap_total))
    try:
        F,a,E,a2,a6,N,big=make_curve(n,seed)
        l=max(2,int(round(n/m))); nvars=m*l; r["l"]=l; r["nvars"]=nvars
        r["n_evals"]=2**nvars
        if nvars>20: r["status"]="nvars=%d too big (2^%d evals)"%(nvars,nvars); signal.alarm(0); return r
        w=[a**j for j in range(l)]
        # known-decomposable target
        def inV(b):
            v=list(b.polynomial().list()); v+=[GF(2)(0)]*(n-len(v))
            return None if any(v[j]!=0 for j in range(l,n)) else [int(v[j]) for j in range(l)]
        fb=[]
        for bits in range(1,2**l):
            x=sum((w[j] for j in range(l) if (bits>>j)&1),F(0))
            if x.is_zero(): continue
            try: Pt=E.lift_x(x)
            except ValueError: continue
            fb.append((Pt,x,inV(x)))
            if len(fb)>=m+4: break
        if len(fb)<m: r["status"]="FB<m"; signal.alarm(0); return r
        chosen=fb[:m]; Rt=sum((c[0] for c in chosen),E(0)); idx=m
        while Rt.is_zero() and idx<len(fb):
            chosen=fb[1:m]+[fb[idx]]; Rt=sum((c[0] for c in chosen),E(0)); idx+=1
        xR=Rt.xy()[0]
        P,S=build_S(F,a6,m)
        van,tot,nz,ntot=verify_S(E,P,S,m,ntest=15)
        r["S_verify"]="%d/%d van,%d/%d nz"%(van,tot,nz,ntot)
        r["S_GENUINE"]=bool(van==tot and tot>=12 and nz>=int(0.7*max(1,ntot)))
        if not r["S_GENUINE"]: r["status"]="S unverified"; signal.alarm(0); return r
        t0=time.time()
        comps,B,names=eval_descent(F,a,m,l,S,P,xR,n)
        r["descent_secs"]=round(time.time()-t0,2)
        r["n_eqs"]=len(comps); r["descended_degs"]=sorted(set(int(g.degree()) for g in comps))
        # real-solution check
        realsol={}
        for bi,(_,_,cc) in enumerate(chosen):
            for j in range(l): realsol[B.gen(bi*l+j)]=B(cc[j])
        r["real_sol_satisfies"]=bool(all(g.subs(realsol)==0 for g in comps))
        # D_solv via msolve
        maxdeg,finished=msolve_Dsolv(comps,names,nvars,"n%d_m%d"%(n,m),tcap=msolve_cap)
        r["D_solv"]=maxdeg; r["msolve_finished"]=finished
        r["status"]="OK"
    except Timeout:
        r["status"]="TIMEOUT_OUTER"
    except Exception as ex:
        r["status"]="EXC %s"%repr(ex)[:140]
    finally:
        signal.alarm(0)
    return r

# m=3 control (must reproduce D_solv=7) + m=4 diagonal points. nvars=m*round(n/m)<=20.
PLAN=[(11,3),(11,4),(13,4),(17,4)]   # m=4: l=3,3,4 -> nvars=12,12,16
results=[]
for (n,m) in PLAN:
    t0=time.time()
    r=cell(n,m,seed=1,tcap_total=700,msolve_cap=150)
    r["wall"]=round(time.time()-t0,1); results.append(r)
    out("[n=%2d m=%d] status=%-14s D_solv=%s finished=%s nvars=%s n_evals=%s descdeg=%s realsol=%s descent=%ss (wall %.1fs)"
        %(n,m,r.get("status"),r.get("D_solv"),r.get("msolve_finished"),r.get("nvars"),
          r.get("n_evals"),r.get("descended_degs"),r.get("real_sol_satisfies"),r.get("descent_secs"),r["wall"]))

out("\n=== DIAGONAL: D_solv vs m (the PO-BIN-001(b) handle) ===")
out("%-4s %-4s %-9s %-9s"%("n","m","nvars","D_solv"))
for r in results:
    out("%-4s %-4s %-9s %-9s"%(r.get("n"),r.get("m"),r.get("nvars"),r.get("D_solv")))
out("\nRESULTS_JSON "+json.dumps(results,default=str))
_lf.close()
print("WROTE",LOGP)

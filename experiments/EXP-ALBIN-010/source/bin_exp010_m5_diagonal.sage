# BIN-EXP-010 : the m=5 DIAGONAL point. Tests whether D_solv = m(m-1)+O(1) continues
# (m=5 -> predicted ~20) using the VALIDATED resultant-based Semaev EVALUATOR (no
# symbolic S6) + the substitution-free EVALUATION descent. Third diagonal point after
# BIN-OBS-007 (m=3->7, m=4->12). Confirms/refutes the quadratic-in-m law and whether
# the +O(1) fall constant stays bounded -- the quantity deciding the PQ-favorable
# degree scaling on m~n^{1/3}.
#
# Constraint: eval-descent costs 2^nvars, nvars=5*l. Need nvars<=20 => l=4 => n~20.
# Toy/scaled; not a real break. Resultant Semaev evaluator validated through S6
# (vanishes 12/12 on real summing tuples, arity 3..6).
import json, time, signal
LOGP="/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp010_m5_diagonal.log"
_lf=open(LOGP,"w")
def out(s):
    print(s); _lf.write(str(s)+"\n"); _lf.flush()
out("=== BIN-EXP-010 m=5 diagonal D_solv (resultant evaluator + eval-descent) === "+time.asctime())

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

# ---- validated resultant Semaev evaluator (eval_S returns S_{len(xs)}(xs) in F) ----
# General recursive version (any arity) with rings hoisted per-field for speed.
# Validated through S6 (vanishes 12/12 on real summing tuples, arity 3..6).
def make_eval_S(F,a6):
    Ru=PolynomialRing(F,'u'); uu=Ru.gen()
    Rut=PolynomialRing(F,'u,t'); U,T=Rut.gens()
    Rt=PolynomialRing(F,'t'); t=Rt.gen()
    def S3_val(x1,x2,x3): return (x1*x2+x1*x3+x2*x3)**2+x1*x2*x3+a6
    def Sk_uni(xfixed):
        """S_{len(xfixed)+1}(xfixed, t) as a univariate poly in Rt."""
        k=len(xfixed)+1
        if k==3:
            x1,x2=xfixed; return (x1*x2+x1*t+x2*t)**2+x1*x2*t+a6
        Su=Sk_uni(xfixed[:-1])               # in Rt (variable t == the 'u' to eliminate)
        Su_U=Rut(Su.subs({t:U}))
        S3_uXt=(U*xfixed[-1]+U*T+xfixed[-1]*T)**2+U*xfixed[-1]*T+a6
        res=Su_U.resultant(S3_uXt,U)         # in Rut, only T remains
        return Rt(res.subs({T:t,U:0}))
    def eval_S(xs):
        if len(xs)==3: return S3_val(*xs)
        Sm=Sk_uni(list(xs[:-2]))             # S_m(x1..x_{m-1}, t)
        x_a,x_b=xs[-2],xs[-1]
        S3_t=(t*x_a+t*x_b+x_a*x_b)**2+t*x_a*x_b+a6
        return Sm.resultant(S3_t)
    return eval_S

def eval_descent(F,a,m,l,eval_S,xR_val,n):
    """substitution-free Weil descent via evaluation + Moebius (^^ = XOR in Sage!)."""
    nvars=m*l; w=[a**j for j in range(l)]
    Vsp,frm,to=F.vector_space(map=True)
    truth=[[0]*(2**nvars) for _ in range(n)]
    for idx in range(2**nvars):
        bits=[(idx>>b)&1 for b in range(nvars)]
        xs=[sum((w[j] for j in range(l) if bits[i*l+j]),F(0)) for i in range(m)]
        coords=to(eval_S(xs+[xR_val]))
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
                if i&step: tt[i]=tt[i]^^tt[i^^step]   # ^^ = XOR
        poly=B(0)
        for mask in range(2**nvars):
            if tt[mask]:
                mono=B(1)
                for b in range(nvars):
                    if (mask>>b)&1: mono=mono*Bg[b]
                poly=poly+mono
        if poly!=0: comps.append(poly)
    return comps,B,names

def msolve_Dsolv(comps,names,nvars,tag,tcap=200):
    lines=[",".join(names),"2"]; ps=[]
    for g in comps:
        terms=["*".join(names[i] for i in mo.iterindex()) if list(mo.iterindex()) else "1" for mo in g.monomials()]
        ps.append("+".join(terms) if terms else "0")
    for nm in names: ps.append("%s^2+%s"%(nm,nm))
    lines.append(",\n".join(ps))
    fn="/tmp/ms10_%s.ms"%tag; open(fn,"w").write("\n".join(lines)+"\n")
    import subprocess,re
    vf="/tmp/ms10_%s.v"%tag
    try:
        with open(vf,"w") as vfh:
            subprocess.run(["msolve","-v","2","-f",fn,"-o","/tmp/ms10_%s.out"%tag],
                           stdout=vfh,stderr=subprocess.STDOUT,timeout=tcap)
        finished=True
    except subprocess.TimeoutExpired:
        finished=False
    maxdeg=0
    for ln in open(vf):
        mt=re.match(r'\s*(\d+)\s+\d+\s+\d+\s+\d+\s*x\s*\d+',ln)
        if mt: maxdeg=max(maxdeg,int(mt.group(1)))
    return maxdeg,finished

def cell(n,m,seed=1,tcap_total=1200,msolve_cap=240):
    r={"n":n,"m":m}
    signal.alarm(int(tcap_total))
    try:
        F,a,E,a2,a6,N,big=make_curve(n,seed)
        l=max(2,int(round(n/m))); nvars=m*l; r["l"]=l; r["nvars"]=nvars; r["n_evals"]=2**nvars
        if nvars>20: r["status"]="nvars=%d too big"%nvars; signal.alarm(0); return r
        w=[a**j for j in range(l)]
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
            if len(fb)>=m+5: break
        if len(fb)<m: r["status"]="FB<m (l=%d)"%l; signal.alarm(0); return r
        chosen=fb[:m]; Rt=sum((c[0] for c in chosen),E(0)); idx=m
        while Rt.is_zero() and idx<len(fb):
            chosen=fb[1:m]+[fb[idx]]; Rt=sum((c[0] for c in chosen),E(0)); idx+=1
        xR=Rt.xy()[0]
        eval_S=make_eval_S(F,a6)
        # verify the evaluator on this curve (arity m+1) before metering
        van=tot=0; tries=0
        while tot<12 and tries<5000:
            tries+=1
            pts=[E.random_point() for _ in range(m)]; pts.append(-sum(pts,E(0)))
            if any(Q.is_zero() for Q in pts): continue
            van+=(eval_S([Q.xy()[0] for Q in pts])==0); tot+=1
        r["evaluator_verify"]="%d/%d"%(van,tot); r["evaluator_ok"]=bool(van==tot and tot>=10)
        if not r["evaluator_ok"]: r["status"]="evaluator unverified"; signal.alarm(0); return r
        t0=time.time()
        comps,B,names=eval_descent(F,a,m,l,eval_S,xR,n)
        r["descent_secs"]=round(time.time()-t0,1)
        r["n_eqs"]=len(comps); r["descended_degs"]=sorted(set(int(g.degree()) for g in comps))
        realsol={}
        for bi,(_,_,cc) in enumerate(chosen):
            for j in range(l): realsol[B.gen(bi*l+j)]=B(cc[j])
        r["real_sol_satisfies"]=bool(all(g.subs(realsol)==0 for g in comps))
        maxdeg,finished=msolve_Dsolv(comps,names,nvars,"n%d_m%d"%(n,m),tcap=msolve_cap)
        r["D_solv"]=maxdeg; r["msolve_finished"]=finished
        r["maxgendeg"]=max(r["descended_degs"]) if r["descended_degs"] else None
        r["status"]="OK"
    except Timeout:
        r["status"]="TIMEOUT_OUTER"
    except Exception as ex:
        r["status"]="EXC %s"%repr(ex)[:140]
    finally:
        signal.alarm(0)
    return r

# m=5 at l=3 (n in {13..17}, nvars=15): ~5min descent (S6 eval ~9ms x 32768) + msolve.
# nvars=20 (l=4) is ~3h descent -- infeasible here; one nvars=15 point is the m=5 datum.
PLAN=[(15,5)]
results=[]
for (n,m) in PLAN:
    t0=time.time()
    r=cell(n,m,seed=1,tcap_total=1500,msolve_cap=300)
    r["wall"]=round(time.time()-t0,1); results.append(r)
    out("[n=%2d m=%d] status=%-14s D_solv=%s (maxgendeg=%s, m(m-1)=%d) finished=%s nvars=%s evals=%s descdeg=%s realsol=%s descent=%ss (wall %.1fs)"
        %(n,m,r.get("status"),r.get("D_solv"),r.get("maxgendeg"),m*(m-1),r.get("msolve_finished"),
          r.get("nvars"),r.get("n_evals"),r.get("descended_degs"),r.get("real_sol_satisfies"),
          r.get("descent_secs"),r["wall"]))

out("\n=== DIAGONAL D_solv vs m (with m=3->7, m=4->12 from BIN-OBS-007) ===")
out("m | predicted m(m-1) | measured D_solv")
out("3 | 6  | 7  (BIN-OBS-006/007)")
out("4 | 12 | 12 (BIN-OBS-007)")
for r in results:
    if r.get("D_solv") is not None:
        out("5 | 20 | %s (n=%d%s)"%(r["D_solv"],r["n"]," unfinished" if not r.get("msolve_finished") else ""))
out("\nRESULTS_JSON "+json.dumps(results,default=str))
_lf.close()
print("WROTE",LOGP)

# BIN-EXP-008 : the decisive measurement PO-BIN-001 -- GRADED solving degree D_solv
# vs n at FIXED m, side-by-side with the first-fall degree d_ff.
#
# Per proof_obligation_binary_solving_degree.md, the crux is the GAP between:
#   d_ff   = first-fall degree (Kosters-Yeo proved =2 for descended S3; a structural
#            trace-syzygy fall; does NOT imply fast solving), and
#   D_solv = the degree actually needed to SOLVE (cut to the F2 factor-base solution).
# PO-BIN-001(a): is D_solv(n,m) bounded in n at fixed m?  Flat -> supports the
# Petit-Quisquater heuristic; RISING with n -> refutes it (binary IC not subexponential).
# This n-vs-D_solv measurement at fixed m is the needle-mover the literature never ran.
#
# How we measure D_solv WITHOUT a full F4 (which dies past n~17): the Boolean ideal
# I = <descended Semaev comps, field eqs c^2=c> is zero-dimensional over F2. We compute
# its GRADED Groebner basis via Sage's BooleanPolynomialRing (PolyBoRi, which is built
# for exactly these x^2=x systems and scales far past dense F4), and read:
#   D_solv = max degree of a reduced GB element  (the solving degree proxy that governs
#            the dense-LA cost binom(N,D_solv)^omega),
#   d_ff   = first degree at which a nontrivial syzygy of the leading forms appears
#            (Macaulay-rank meter, reused from round005/round016).
# We VERIFY each cell: the system is consistent and the GB recovers the real
# factor-base decomposition (the same validation as the WDSat harness). Fixed m=3,
# growing n. Toy/scaled; not a real break.
import json, time, signal
LOGP="/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp008_solving_degree_vs_n.log"
_lf=open(LOGP,"w")
def out(s):
    print(s); _lf.write(str(s)+"\n"); _lf.flush()
out("=== BIN-EXP-008 graded solving degree D_solv vs n (PO-BIN-001) ===  "+time.asctime())

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

def build_S4(F,a6):
    Pt=PolynomialRing(F,'X1,X2,X3,X4,T'); X1,X2,X3,X4,T=Pt.gens()
    def S3(u,v,w): return (u*v+u*w+v*w)**2+u*v*w+a6
    S=S3(X1,X2,T).resultant(S3(X3,X4,T),T)
    P4=PolynomialRing(F,'X1,X2,X3,X4'); g=P4.gens()
    S=P4(S.subs({X1:g[0],X2:g[1],X3:g[2],X4:g[3],T:0}))
    try: S=prod(f for f,e in factor(S))
    except Exception: pass
    return P4,S

def verify_S4(E,P4,S4,ntest=18):
    van=tot=nz=ntot=0; tries=0
    while tot<ntest and tries<6000:
        tries+=1
        P1=E.random_point(); P2=E.random_point(); P3=E.random_point()
        pts=[P1,P2,P3,-(P1+P2+P3)]
        if any(Q.is_zero() for Q in pts): continue
        van+=(S4(*[Q.xy()[0] for Q in pts])==0); tot+=1
    tries=0
    while ntot<ntest and tries<8000:
        tries+=1
        pts=[E.random_point() for _ in range(4)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts,E(0)).is_zero(): continue
        nz+=(S4(*[Q.xy()[0] for Q in pts])!=0); ntot+=1
    return van,tot,nz,ntot

def f2_components_fast(Phi,F,n,B,to_vec):
    monos=Phi.monomials(); coeffs=Phi.coefficients()
    M=matrix(GF(2),[to_vec(c) for c in coeffs])
    Bg=B.gens(); ngB=B.ngens(); bmonos=[]
    for mo in monos:
        e=mo.exponents()[0]; term=B(1)
        for i in range(ngB):
            if e[i]: term=term*Bg[i]
        bmonos.append(term)
    out_=[]
    for k in range(min(n,M.ncols())):
        idx=M.column(k).nonzero_positions()
        out_.append(sum((bmonos[ti] for ti in idx),B(0)) if idx else B(0))
    return out_

# ---- d_ff meter: homogeneous Macaulay nontrivial-syzygy first fall over GF(2) ----
def top_form(g):
    d=g.degree()
    return sum((mo for mo in g.monomials() if mo.degree()==d), g.parent()(0))

def macaulay_rank_gf2(tops, D, R):
    """rows = monomial-multiples of leading forms up to degree D; return (#rows, rank)
    over GF(2). tops are ordinary-GF(2)-ring homogeneous forms."""
    n=R.ngens()
    monD=[m for m in R.monomials_of_degree(D)] if hasattr(R,'monomials_of_degree') else None
    # build degree-D monomial index
    from itertools import combinations_with_replacement
    # fallback monomial enumeration
    def monos_deg(d):
        res=[]
        for combo in combinations_with_replacement(range(n),d):
            e=[0]*n
            for c in combo: e[c]+=1
            res.append(tuple(e))
        return res
    cols=monos_deg(D); colidx={m:i for i,m in enumerate(cols)}
    rows=[]
    for h in tops:
        dh=h.degree()
        if dh>D: continue
        for me in monos_deg(D-dh):
            row=[0]*len(cols)
            g=R.monomial(*me)*h
            for c,mo in zip(g.coefficients(),g.monomials()):
                if c==0: continue
                e=tuple(mo.exponents()[0])
                row[colidx[e]]^=1
            rows.append(row)
    if not rows: return 0,0
    Mt=matrix(GF(2),rows)
    return Mt.nrows(), Mt.rank()

def trivial_koszul(D,degs,n):
    tot=0
    for i in range(len(degs)):
        for j in range(i+1,len(degs)):
            r=D-degs[i]-degs[j]
            if r>=0: tot+=binomial(n-1+r,r)
    return tot

def measure_dff(comps_ordinary, R, Dmax=8):
    """first-fall: least D with (rows-rank) - trivial_koszul(D) > 0 on leading forms."""
    tops=[top_form(g) for g in comps_ordinary]
    degs=[g.degree() for g in comps_ordinary]; n=R.ngens()
    for D in range(min(degs)+1, Dmax+1):
        nrows,rank=macaulay_rank_gf2(tops,D,R)
        if nrows==0: continue
        ker=nrows-rank
        nontriv=ker-trivial_koszul(D,degs,n)
        if nontriv>0: return D
    return None

def cell(n,m=3,seed=1,tcap=300):
    r={"n":n,"m":m}
    signal.alarm(int(tcap))
    try:
        F,a,E,a2,a6,N,big=make_curve(n,seed)
        r["rho_exp"]=float(log(0.886,2)+0.5*log(float(big),2))
        Vsp,frm,to=F.vector_space(map=True)
        l=max(2,int(round(n/m))); nvars=m*l; r["l"]=l; r["nvars"]=nvars
        w=[a**j for j in range(l)]
        # FB and a known-decomposable target
        def inV(beta):
            v=list(beta.polynomial().list()); v+=[GF(2)(0)]*(n-len(v))
            return None if any(v[j]!=0 for j in range(l,n)) else [int(v[j]) for j in range(l)]
        fb=[]
        for bits in range(1,2**l):
            x=sum((w[j] for j in range(l) if (bits>>j)&1),F(0))
            if x.is_zero(): continue
            try: P=E.lift_x(x)
            except ValueError: continue
            fb.append((P,x,inV(x)))
            if len(fb)>=m+4: break
        if len(fb)<m: r["status"]="FB<m"; signal.alarm(0); return r
        chosen=fb[:m]; Rt=sum((c[0] for c in chosen),E(0)); idx=m
        while Rt.is_zero() and idx<len(fb):
            chosen=fb[1:m]+[fb[idx]]; Rt=sum((c[0] for c in chosen),E(0)); idx+=1
        xR=Rt.xy()[0]
        P4,S4=build_S4(F,a6)
        van,tot,nz,ntot=verify_S4(E,P4,S4,ntest=18)
        r["S4_GENUINE"]=bool(van==tot and tot>=14 and nz>=int(0.7*max(1,ntot)))
        if not r["S4_GENUINE"]: r["status"]="S4 unverified"; signal.alarm(0); return r
        names=['c%d_%d'%(i,j) for i in range(m) for j in range(l)]
        B=BooleanPolynomialRing(nvars,names)
        R2=PolynomialRing(GF(2),names)   # for the d_ff leading-form meter
        PF=PolynomialRing(F,names); cF=PF.gens()
        def xexpr(i): return sum(cF[i*l+j]*w[j] for j in range(l))
        gp=P4.gens(); subd={gp[i]:xexpr(i) for i in range(m)}; subd[gp[m]]=xR
        t0=time.time()
        Phi=S4.subs(subd)
        comps_B=[g for g in f2_components_fast(Phi,F,n,B,to) if g!=0]
        r["descend_secs"]=round(time.time()-t0,2)
        r["n_eqs"]=len(comps_B); r["descended_degs"]=sorted(set(int(g.degree()) for g in comps_B))
        # ---- D_solv via PolyBoRi graded Groebner ----
        t0=time.time()
        I=B.ideal(comps_B)
        gb=list(I.groebner_basis())
        r["gb_secs"]=round(time.time()-t0,2)
        if len(gb)==1 and gb[0]==B(1):
            r["consistent"]=False; r["D_solv"]=0; r["status"]="INCONSISTENT(unexpected)"; signal.alarm(0); return r
        r["consistent"]=True
        r["D_solv"]=int(max((g.degree() for g in gb),default=0))
        r["n_gb"]=len(gb)
        # real-solution recovery check
        realsol={}
        for bi,(_,_,cc) in enumerate(chosen):
            for j in range(l): realsol[B.gen(bi*l+j)]=B(cc[j])
        r["real_sol_satisfies"]=bool(all(g.subs(realsol)==0 for g in comps_B))
        # count solutions if small enough (the corank-stabilization target)
        if nvars<=16:
            try: r["n_sols"]=len(I.variety())
            except Exception: r["n_sols"]=None
        # ---- d_ff via leading-form Macaulay meter (ordinary ring, small n only) ----
        if nvars<=12 and n<=19:
            # map Boolean comps into ordinary ring (they're already multilinear)
            comps_ord=[]
            for g in comps_B:
                p=R2(0)
                for mo in g.monomials():
                    e=[0]*nvars
                    for i in mo.iterindex(): e[int(i)]=1
                    p+=R2.monomial(*e)
                comps_ord.append(p)
            try:
                r["d_ff"]=measure_dff(comps_ord,R2,Dmax=7)
            except Exception as ex:
                r["d_ff"]="err:%s"%repr(ex)[:40]
        r["status"]="OK"
    except Timeout:
        r["status"]="TIMEOUT(%ds)"%tcap
    except Exception as ex:
        r["status"]="EXC %s"%repr(ex)[:150]
    finally:
        signal.alarm(0)
    return r

# Fixed m=3, growing n -- the decisive sweep. (a) predicts D_solv flat; rising refutes.
GRID=[11,13,17,19,23,29,31,37]
results=[]
for n in GRID:
    t0=time.time()
    r=cell(n,m=3,seed=1,tcap=300)
    r["wall"]=round(time.time()-t0,1); results.append(r)
    out("[n=%2d m=3] status=%-16s D_solv=%s d_ff=%s nvars=%s descdeg=%s n_gb=%s n_sols=%s realsol=%s gb=%ss (wall %.1fs)"
        %(n,r.get("status"),r.get("D_solv"),r.get("d_ff"),r.get("nvars"),r.get("descended_degs"),
          r.get("n_gb"),r.get("n_sols"),r.get("real_sol_satisfies"),r.get("gb_secs"),r["wall"]))

out("\n=== SUMMARY: PO-BIN-001(a) -- is D_solv bounded in n at fixed m=3? ===")
out("%-4s %-8s %-7s %-8s %-8s"%("n","D_solv","d_ff","nvars","rho2^"))
for r in results:
    out("%-4s %-8s %-7s %-8s %-8s"%(r.get("n"),r.get("D_solv"),r.get("d_ff"),r.get("nvars"),
        ("%.1f"%r["rho_exp"]) if "rho_exp" in r else "-"))
out("\nRESULTS_JSON "+json.dumps(results,default=str))
_lf.close()
print("WROTE",LOGP)

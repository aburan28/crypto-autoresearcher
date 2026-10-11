"""General Nagao 2013/549 Definition 1 first fall degree in K[X] (K=F_2, polynomial ring, no reduction),
optionally with field equations u_j^2+u_j appended as fixed generators. Also HPS-style count in gr(Boolean)."""
import sys, itertools; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from truekernel import gl_rowsets
import boolring as B
def exps(N,d): return [e for e in itertools.product(range(d+1),repeat=N) if sum(e)==d]
def kx(fset,N): return {tuple((m>>j)&1 for j in range(N)):1 for m in fset}
def kdeg(p): return max((sum(e) for e in p),default=-1)
def def1_ffd(gens, N, with_fe=False, Dmax=6):
    G=[kx(f,N) for f in gens]
    if with_fe:
        for j in range(N):
            G.append({tuple(2 if k==j else 0 for k in range(N)):1, tuple(1 if k==j else 0 for k in range(N)):1})
    ds=[kdeg(g) for g in G]
    for D in range(1,Dmax+1):
        if max(ds)>D: continue                      # condition 4
        # unknowns: (i, e) with deg e <= D - ds[i]
        unk=[(i,e) for i in range(len(G)) for d in range(0,D-ds[i]+1) for e in exps(N,d)]
        if not unk: continue
        allmon={}
        vecs=[]
        for (i,e) in unk:
            prod={}
            for a in G[i]:
                t=tuple(x+y for x,y in zip(a,e)); prod[t]=prod.get(t,0)^1
            v=0
            for t,c in prod.items():
                if c:
                    if t not in allmon: allmon[t]=len(allmon)
                    v|=1<<allmon[t]
            vecs.append(v)
        topmask=0
        for t,k in allmon.items():
            if sum(t)==D: topmask|=1<<k
        nu=len(unk)
        # L_D = {x : top(Phi x)=0}; T_{D-1} = {x supported on unknowns with deg(e)+ds[i] <= D-1}
        # compute basis of L_D via elimination on (top part | identity)
        aug=[(((vecs[k]&topmask))<<nu)|(1<<k) for k in range(nu)]
        piv={}; L=[]
        for v in aug:
            while v>>nu:
                h=v.bit_length()-1
                if h in piv: v^=piv[h]
                else: piv[h]=v; break
            if not (v>>nu): L.append(v&((1<<nu)-1))
        Lr=B.rank(L)
        lowmask=0
        for k,(i,e) in enumerate(unk):
            if sum(e)+ds[i]<=D-1: lowmask|=1<<k
        T=[1<<k for k in range(nu) if (lowmask>>k)&1]
        not_in_T = B.rank(L+T) > B.rank(T)
        def phi(x):
            r=0
            for k in range(nu):
                if (x>>k)&1: r^=vecs[k]
            return r
        phi_nonzero = any(phi(x) for x in L)
        if Lr>0 and not_in_T and phi_nonzero: return D
    return None
if __name__=="__main__":
    import json
    res={}
    for nm,(gs,N) in (("semaev(4,2)",(R.cell_systems(4,2)[0],4)),("null(4,2)",(R.cell_systems(4,2)[1],4))):
        for fe in (False,True):
            base=def1_ffd(gs,N,fe)
            dist={}; up=0; down=0
            for M in gl_rowsets(len(gs)):
                d=def1_ffd(recombine(gs,M),N,fe)
                dist[d]=dist.get(d,0)+24
                if d is not None and base is not None and d>base: up+=24
                if d is not None and base is not None and d<base: down+=24
            res[f"{nm} fe={fe}"]=dict(D_ff_identity=base,upward=up,downward=down,dist={str(k):v for k,v in dist.items()})
            print(nm,"Def1 with field eqs" if fe else "Def1 no field eqs", res[f"{nm} fe={fe}"],flush=True)
    gs=R.cell_systems(6,3)[0]
    for fe in (False,True):
        print("semaev(6,3) witness Def1", "with fe" if fe else "no fe", ": I ->",def1_ffd(gs,6,fe)," M=[1,2,4,8,26] ->",def1_ffd(recombine(gs,[1,2,4,8,26]),6,fe),
              " M=[1,2,4,13,26] ->",def1_ffd(recombine(gs,[1,2,4,13,26]),6,fe),flush=True)

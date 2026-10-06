"""Nagao 2013/549 Definition 1 at working degree D for the witness presentation, computed in K[X] (K=F_2),
i.e. the polynomial ring, squares NOT reduced. Also: the same with the field equations u_j^2+u_j appended as
(unrecombined) generators, and the top-degree syzygy count modulo trivial syzygies in gr(Boolean)=F2[u]/(u^2)."""
import sys, itertools; sys.dont_write_bytecode=True
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
N=6; names=["u0","u1","u2","w0","w1","w2"]
sem,null,xR=R.cell_systems(6,3)
def popcount(x): return bin(x).count("1")
# ---- K[X] polynomials: dict {exponent tuple: 1} over GF(2) ----
def kx_from_set(f): return {tuple((m>>j)&1 for j in range(N)):1 for m in f}
def kx_add(*ps):
    r={}
    for p in ps:
        for e in p: r[e]=r.get(e,0)^1
    return {e:1 for e,c in r.items() if c}
def kx_mul(p,q):
    r={}
    for a in p:
        for b in q:
            e=tuple(x+y for x,y in zip(a,b)); r[e]=r.get(e,0)^1
    return {e:1 for e,c in r.items() if c}
def kx_deg(p): return max((sum(e) for e in p), default=-1)
def kx_var(j): return {tuple(1 if k==j else 0 for k in range(N)):1}
ONE={tuple([0]*N):1}
def kx_str(p):
    def mono(e):
        s="*".join((names[j] if e[j]==1 else f"{names[j]}^{e[j]}") for j in range(N) if e[j])
        return s or "1"
    return " + ".join(mono(e) for e in sorted(p,key=lambda e:(-sum(e),e))) or "0"
Mrows=[1,2,4,8,26]
H=[kx_from_set(f) for f in recombine(sem,Mrows)]
F=[kx_from_set(f) for f in sem]
print("degrees in K[X]: identity",[kx_deg(p) for p in F]," witness",[kx_deg(p) for p in H])
# ---- GF(2) nullspace helper ----
def nullspace(cols, nvars):
    """cols: list over equations of bitmask over unknowns; return basis of {x : <eq,x>=0 all eq}."""
    piv={}; 
    rows=[c for c in cols if c]
    # row-reduce
    red=[]
    for r in rows:
        v=r
        for (p,pr) in red:
            if (v>>p)&1: v^=pr
        if v:
            p=v.bit_length()-1
            red=[(pp, (pr^v) if (pr>>p)&1 else pr) for pp,pr in red]
            red.append((p,v))
    pivcols={p for p,_ in red}
    free=[j for j in range(nvars) if j not in pivcols]
    basis=[]
    for fj in free:
        x=1<<fj
        for p,pr in red:
            # pr has pivot p; x_p = sum of pr's other bits restricted to free vars
            if (pr>>fj)&1: x|=1<<p
        basis.append(x)
    return basis
def top_kernel_D2(with_fe):
    # unknowns: c0..c3 (bits 0..3), b_0..b_5 (bits 4..9) : g_4 = sum b_j u_j ; plus e_0..e_5 (bits 10..15) if with_fe
    quad=[e for e in itertools.product(range(3),repeat=N) if sum(e)==2]
    nvars=10+(6 if with_fe else 0)
    eqs=[]
    for e in quad:
        v=0
        for i in range(4):
            if H[i].get(e): v|=1<<i
        for j in range(N):
            prod=kx_mul(kx_var(j),{a:1 for a in H[4] if sum(a)==1})   # u_j * (linear part of h4)
            if prod.get(e): v|=1<<(4+j)
        if with_fe:
            for j in range(N):
                if e==tuple(2 if k==j else 0 for k in range(N)): v|=1<<(10+j)
        eqs.append(v)
    return nullspace(eqs,nvars), nvars
for with_fe in (False,True):
    ker,nv=top_kernel_D2(with_fe)
    print(f"\n[Def 1, K[X], D=2, field equations as generators: {with_fe}] top-degree kernel dim = {len(ker)}")
    for x in ker:
        c=[(x>>i)&1 for i in range(4)]; b=[(x>>(4+j))&1 for j in range(N)]; e=[(x>>(10+j))&1 for j in range(N)] if with_fe else None
        print("   c(h0..h3) =",c," g4 linear part =", " + ".join(names[j] for j in range(N) if b[j]) or "0", (" fe coeffs="+str(e)) if with_fe else "")
# ---- explicit certificate for Def 1 with field equations, D=2 ----
l4={a:1 for a in H[4] if sum(a)==1}
g4=l4
fe_terms=[kx_add(kx_mul(kx_var(j),kx_var(j)),kx_var(j)) for j in range(N) if l4.get(tuple(1 if k==j else 0 for k in range(N)))]
S=kx_add(kx_mul(g4,H[4]),*fe_terms)
print("\nCertificate (Def 1 on {h^(M)} U S_fe, D=2): g4 = h4 =",kx_str(g4),"; g_fe(u_j)=1 for u_j in supp(h4)")
print("   deg(g4*h4) =",kx_deg(kx_mul(g4,H[4])), " deg of each fe term =",[kx_deg(t) for t in fe_terms])
print("   sum =",kx_str(S)," deg =",kx_deg(S)," equals h4:",S==H[4])
# ---- Koszul certificate for Def 1 WITHOUT field equations at D=3 ----
S3=kx_add(kx_mul(H[4],H[0]),kx_mul(kx_add(H[0],ONE),H[4]))
print("Certificate (Def 1 on {h^(M)} alone, D=3): g0=h4, g4=h0+1 : max deg(g_i h_i) =",max(kx_deg(kx_mul(H[4],H[0])),kx_deg(kx_mul(kx_add(H[0],ONE),H[4]))),
      " sum =",kx_str(S3)," deg",kx_deg(S3))
# ---- identity at D=2 ----
S2=kx_add(F[1],F[3],F[4]); print("Identity D=2 (Def 1): f1+f3+f4 =",kx_str(S2)," deg",kx_deg(S2))

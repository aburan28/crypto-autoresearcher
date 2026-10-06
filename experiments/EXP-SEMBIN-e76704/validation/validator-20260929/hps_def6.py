import sys, itertools; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from boolring import from_set, mul, deg, popcount, rank
N=6
sem,null,xR=R.cell_systems(6,3)
I=[from_set(f) for f in sem]; H=[from_set(f) for f in recombine(sem,[1,2,4,8,26])]
# ---------- graded ring A = F2[u]/(u^2): homogeneous parts, product m1*m2 = m1|m2 if disjoint else 0 ----------
def top(p):
    d=deg(p); r=0; m=0; q=p
    while q:
        if q&1 and popcount(m)==d: r^=1<<m
        q>>=1; m+=1
    return r,d
def gmul_mono(p,m):
    r=0; mm=0; q=p
    while q:
        if q&1 and (mm & m)==0: r^=1<<(mm|m)
        q>>=1; mm+=1
    return r
def hps(G,D):
    """dim Syz(top)_D, dim Triv_D, quotient.  Tuples (g_i), g_i homogeneous of degree D-d_i in A."""
    tops=[top(g) for g in G]; l=len(G)
    basis=[]   # list of (i, monomial) unknowns
    for i,(t,d) in enumerate(tops):
        if D-d<0: continue
        for m in range(1<<N):
            if popcount(m)==D-d: basis.append((i,m))
    idx={b:k for k,b in enumerate(basis)}
    # image vectors of unknowns
    img=[gmul_mono(tops[i][0],m) for (i,m) in basis]
    # kernel via elimination on augmented vectors (image | identity)
    nb=len(basis); aug=[(img[k]<<nb)|(1<<k) for k in range(nb)]
    piv={}; ker=[]
    for v in aug:
        while v>>nb:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; break
        if not (v>>nb): ker.append(v & ((1<<nb)-1))
    syz_dim=rank(ker)
    # trivial syzygies: (i) t_i e_i times monomials (Boolean/field type), (ii) Koszul t_j e_i + t_i e_j times monomials
    triv=[]
    def tuple_vec(parts):  # parts: dict i -> homogeneous poly in A
        v=0
        for i,p in parts.items():
            m=0; q=p
            while q:
                if q&1: v^=1<<idx[(i,m)]
                q>>=1; m+=1
        return v
    for i,(t,d) in enumerate(tops):
        for m in range(1<<N):
            if popcount(m)+2*d==D:
                v=tuple_vec({i:gmul_mono(t,m)}); 
                if v: triv.append(v)
    for i,j in itertools.combinations(range(l),2):
        (ti,di),(tj,dj)=tops[i],tops[j]
        for m in range(1<<N):
            if popcount(m)+di+dj==D:
                v=tuple_vec({i:gmul_mono(tj,m), j:gmul_mono(ti,m)})
                if v: triv.append(v)
    triv_dim=rank(triv); both=rank(ker+triv)
    assert both==syz_dim, "trivial syzygies must lie in Syz"
    return syz_dim, triv_dim, syz_dim-triv_dim
for name,G in (("identity",I),("witness M",H)):
    for D in (2,3,4):
        s,t,q=hps(G,D); print(f"HPS-style gr(Boolean) {name} D={D}: dim Syz_top={s} dim Triv={t} nontrivial quotient={q}")
# ---------- literal Definition 6 (fake), certificate at d=2 for M ----------
a0=mul(H[4],H[0]); a4=mul(H[0]^1,H[4])      # g0=h4, g4=h0+1  (Boolean ring; ^1 adds the constant 1)
print("\nDef 6 literal: deg(g0 h0 mod S_fe) =",deg(a0)," deg(g4 h4 mod S_fe) =",deg(a4)," sum == h4:",(a0^a4)==H[4]," deg(sum)=",deg(a0^a4))
# ---------- consistency: does the Boolean ideal contain 1?  (common zeros in F_2^6) ----------
def ev(p,x):
    s=0; m=0; q=p
    while q:
        if q&1 and (m & ~x)==0: s^=1
        q>>=1; m+=1
    return s
sols=[x for x in range(1<<N) if all(ev(g,x)==0 for g in I)]
print("common zeros of the (6,3) system in F_2^6:",sols," -> 1 in ideal:",len(sols)==0)
sem42,null42,_=R.cell_systems(4,2)
for nm,G in (("semaev(4,2)",sem42),("null(4,2)",null42)):
    GG=[from_set(f) for f in G]
    print(nm,"common zeros:",[x for x in range(16) if all(ev(g,x)==0 for g in GG)])

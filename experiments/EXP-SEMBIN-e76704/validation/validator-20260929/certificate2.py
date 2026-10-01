import sys; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
import boolring as B
N=6; names=["u0","u1","u2","w0","w1","w2"]
def s(p):
    out=[]
    for m in B.monos(p): out.append("*".join(names[j] for j in range(N) if (m>>j)&1) or "1")
    return " + ".join(sorted(out,key=lambda t:(-t.count("*"),t))) or "0"
def mn(m): return "*".join(names[j] for j in range(N) if (m>>j)&1) or "1"
gs=R.cell_systems(6,3)[0]
for M in ([1,2,4,13,26],[1,2,4,8,26]):
    H=[B.from_set(f) for f in recombine(gs,M)]
    rows=[(i,m,B.mul_mono_true(H[i],m)) for i in range(5) for m in range(64)]
    V2=[(i,m,r) for (i,m,r) in rows if r and B.deg(r)<=2]
    # eliminate degree-2 monomials first, tracking combinations
    deg2=[m for m in range(64) if B.popcount(m)==2]
    def key(r):  # highest degree-2 monomial index present, else -1
        best=-1
        for m in B.monos(r):
            if B.popcount(m)==2: best=max(best,m)
        return best
    piv={}; lows=[]
    for k,(i,m,r) in enumerate(V2):
        v=r; comb=1<<k
        while True:
            h=key(v)
            if h<0: break
            if h in piv: pv,pc=piv[h]; v^=pv; comb^=pc
            else: piv[h]=(v,comb); break
        if key(v)<0 and v: lows.append((v,comb))
    V1=[r for (i,m,r) in rows if r and B.deg(r)<=1]
    new=[(v,c) for (v,c) in lows if B.rank(V1+[v])>B.rank(V1)]
    print(f"M={M}: dim V_1={B.rank(V1)}  low elements of V_2 found={B.rank([v for v,_ in lows])}  outside V_1: {len(new)>0}")
    if new:
        v,c=new[0]
        terms=[V2[k] for k in range(len(V2)) if (c>>k)&1]
        print("  certificate: sum of TRUE Boolean products")
        for (i,m,r) in terms: print(f"     {mn(m)} * h{i} = {s(r)}    [src OR row would be: {s(B.mul_mono_or(H[i],m))}; OR-row degree {B.deg(B.mul_mono_or(H[i],m))}]")
        tot=0
        for (_,_,r) in terms: tot^=r
        print("     SUM =",s(tot)," (degree",B.deg(tot),"), not in V_1 = span{h4}")

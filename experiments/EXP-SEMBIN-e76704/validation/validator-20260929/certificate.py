import sys, itertools; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine
from fastfall import Kernel
from truekernel import TrueKernel, gl_rowsets
import boolring as B
N=6; names=["u0","u1","u2","w0","w1","w2"]
def s(p):
    out=[]
    for m in B.monos(p):
        out.append("*".join(names[j] for j in range(N) if (m>>j)&1) or "1")
    return " + ".join(sorted(out,key=lambda t:(-t.count("*"),t))) or "0"
gs=R.cell_systems(6,3)[0]; K=Kernel(gs,N); TK=TrueKernel(gs,N); cache={}
for M in gl_rowsets(5):
    if 26 not in M: continue
    if K.ffd(M,cache)==3 and TK.ffd(M)==2:
        break
print("M (row bitmasks) =",M,"  src d'_ff =",K.ffd(M,cache),"  true-product d'_ff =",TK.ffd(M))
H=[B.from_set(f) for f in recombine(gs,M)]
for i,h in enumerate(H): print(f"  h{i} = {s(h)}")
# find explicit element of V_2 cap R_{<2} not in span{V_1}
rows=[(i,m,B.mul_mono_true(H[i],m)) for i in range(5) for m in range(64)]
V2=[(i,m,r) for (i,m,r) in rows if r and B.deg(r)<=2]
V1=[r for (i,m,r) in rows if r and B.deg(r)<=1]
print("  V_1 basis:",[s(r) for r in V1][:3], " dim",B.rank(V1))
# search small combinations of V_2 rows whose sum has degree<=1 and lies outside span(V_1)
found=None
for k in (1,2,3,4):
    for combo in itertools.combinations(V2,k):
        t=0
        for (_,_,r) in combo: t^=r
        if t and B.deg(t)<=1 and B.rank(V1+[t])>B.rank(V1):
            found=combo,t; break
    if found: break
combo,t=found
for (i,m,r) in combo:
    mm="*".join(names[j] for j in range(N) if (m>>j)&1) or "1"
    print(f"  TRUE product {mm} * h{i} = {s(r)}   (src OR row: {s(B.mul_mono_or(H[i],m))})")
print("  sum =",s(t)," degree",B.deg(t)," -> new fall at D=2 under the true Boolean product")

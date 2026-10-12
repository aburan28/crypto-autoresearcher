import sys, itertools, random; sys.dont_write_bytecode=True
sys.path.insert(0,"/tmp/claude-0/validator")
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-e76704/src")
import run_separation as R
from recomb_search import recombine, ffd as slow_ffd, _tables
from ffd_semaev import build_system, a_real_xR
from truekernel import TrueKernel, gl_rowsets
import boolring as B
N=6
gs=R.cell_systems(6,3)[0]
# ---- Def 1 in K[X] (no field equations) at D=2, for every GL_5 row-set containing 26 ----
# top map: c (quadratic generators, constants) and b (linear multiplier of the linear generator) -> K[X]_2 incl. squares
def kernel_dim_D2(H):
    lin=[i for i,h in enumerate(H) if B.deg(h)==1]; quad=[i for i,h in enumerate(H) if B.deg(h)==2]
    assert len(lin)==1
    l4=[j for j in range(N) if (H[lin[0]]>>(1<<j))&1]   # support of the linear part
    # monomial keys: ('x',j,k) j<k for u_j u_k ; ('sq',j) for u_j^2
    keys=[('x',j,k) for j in range(N) for k in range(j+1,N)]+[('sq',j) for j in range(N)]
    eqs=[]
    for key in keys:
        v=0
        for t,i in enumerate(quad):
            if key[0]=='x' and (H[i]>>((1<<key[1])|(1<<key[2])))&1: v|=1<<t
        for j in range(N):   # b_j u_j * (sum_{a in l4} u_a)
            if key[0]=='x':
                a,b=key[1],key[2]
                if (j==a and b in l4) ^ (j==b and a in l4): v|=1<<(len(quad)+j)
            else:
                if j==key[1] and j in l4: v|=1<<(len(quad)+j)
        eqs.append(v)
    nv=len(quad)+N
    return nv-B.rank(eqs)
cnt=0; nz=0
for M in gl_rowsets(5):
    if 26 not in M: continue
    cnt+=1
    H=[B.from_set(f) for f in recombine(gs,M)]
    if kernel_dim_D2(H)>0: nz+=1
print(f"Def1 K[X] no S_fe: row-sets containing 26 = {cnt} (x120 = {cnt*120}); with nonzero D=2 top kernel: {nz}")
print("  => Def1 (no S_fe) upward count =", (cnt-nz)*120, " (all others fall at D=2 via the combination equal to h4)")
# ---- C1 cells: identity d'_ff under src OR vs true product ----
out=[]
for n,npr in R.REGRESSION_CELLS:
    rng=random.Random(n*100+npr); xR=a_real_xR(n,1,1,rng)
    basis=([1]+[1<<j for j in range(1,npr)])[:npr]
    eqs=build_system(n,npr,1,xR,basis); NN=2*npr
    Hs=[B.from_set(f) for f in eqs]
    out.append(((n,npr), slow_ffd(eqs,NN,tabs=_tables(NN)), B.ffd(Hs,NN,B.mul_mono_true)))
print("C1 cells (cell, src d'_ff, true-product d'_ff):", out, " all equal:", all(a==b for _,a,b in out))
# ---- low-degree part of the generator spans ----
def span_low(G,d,NN):
    return B.low_part_dim(G,d+1,NN)
for nm,(G,NN) in (("semaev(6,3)",(R.cell_systems(6,3)[0],6)),("semaev(4,2)",(R.cell_systems(4,2)[0],4)),("null(4,2)",(R.cell_systems(4,2)[1],4))):
    Hs=[B.from_set(f) for f in G]
    print(f"{nm}: #gens={len(Hs)} degrees={[B.deg(h) for h in Hs]} dim span∩R_<=0 = {span_low(Hs,0,NN)}  dim span∩R_<=1 = {span_low(Hs,1,NN)}")

import sys, random
sys.path.insert(0,"/tmp/claude-0/-home-user/2da6bcd8-2965-5cb4-a4db-701bb987902e/scratchpad")
from ffd_semaev import build_system, a_real_xR, popcount
from recomb_search import ffd as slow_ffd, new_falls_at as slow_nf, _tables, recombine
from fastfall import Kernel

n,npr=6,3; N=6
rng=random.Random(n*100+npr); xR=a_real_xR(n,1,1,rng)
basis=([1]+[1<<j for j in range(1,npr)])[:npr]
eqs=build_system(n,npr,1,xR,basis)
# independent subset used by the control
def keepidx(gs):
    ms=sorted({m for f in gs for m in f}); idx={m:i for i,m in enumerate(ms)}
    piv=[]; keep=[]
    for i,f in enumerate(gs):
        cur=0
        for m in f: cur|=1<<idx[m]
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in range(len(ms)):
                if (cur>>c)&1: piv.append((c,cur)); break
            keep.append(i)
    return keep
sub=[eqs[i] for i in keepidx(eqs)]
M=[1,2,4,8,26]                     # the exhaustive-search witness
req=recombine(sub,M)

print("witness M rows:",M,"  (= identity except row 5 -> f1+f3+f4)")
print("original  generator degrees:",[max(popcount(m) for m in f) for f in sub])
print("recombined generator degrees:",[max(popcount(m) for m in f) for f in req])
print()
print("INDEPENDENT CHECK with the ORIGINAL (slow) instrument:")
tabs=_tables(N)
print("  slow D_ff(identity)  =",slow_ffd(sub,N,tabs=tabs))
print("  slow D_ff(witness M) =",slow_ffd(req,N,tabs=tabs))
print("  slow new_falls D=1,2,3 identity :",[slow_nf(sub,N,D,tabs) for D in (1,2,3)])
print("  slow new_falls D=1,2,3 witness  :",[slow_nf(req,N,D,tabs) for D in (1,2,3)])
print()
# the span of the generators is invariant under invertible recombination;
# what changes is which low-degree elements are already GENERATORS.
def span_low(gs,maxdeg):
    """dim of (F_2-span of the generators) intersect R_{<=maxdeg}"""
    ms=sorted(range(1<<N),key=lambda m:(popcount(m),m)); idx={m:i for i,m in enumerate(ms)}
    degs=[popcount(m) for m in ms]
    hi=[i for i,d in enumerate(degs) if d>maxdeg]; lo=[i for i,d in enumerate(degs) if d<=maxdeg]
    piv=[]
    for f in gs:
        cur=0
        for m in f: cur|=1<<idx[m]
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in hi+lo:
                if (cur>>c)&1: piv.append((c,cur)); break
    return sum(1 for c,_ in piv if degs[c]<=maxdeg)
print("dim( span(generators) cap R_{<=1} ):",
      "identity =",span_low(sub,1)," witness =",span_low(req,1),
      "  (span is recombination-invariant, so these must agree)")

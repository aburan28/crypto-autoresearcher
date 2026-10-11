"""THE CONTROL: does the n=6,n'=3 upward separation survive on an
INDEPENDENT generating set of the same ideal?

If not, the separation is an artifact of the descended components being
F_2-linearly dependent, and says nothing about D_ff vs D_ff^max.
"""
import sys, random, itertools, json
sys.path.insert(0,"/tmp/claude-0/-home-user/2da6bcd8-2965-5cb4-a4db-701bb987902e/scratchpad")
from ffd_semaev import build_system, a_real_xR, popcount
from fastfall import Kernel

def indep_info(eqs):
    ms=sorted({m for f in eqs for m in f}); idx={m:i for i,m in enumerate(ms)}
    piv=[]; keep=[]
    for i,f in enumerate(eqs):
        cur=0
        for m in f: cur|=1<<idx[m]
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in range(len(ms)):
                if (cur>>c)&1: piv.append((c,cur)); break
            keep.append(i)
    return len(piv), keep

def invertible(rows,l):
    piv=[]
    for r in rows:
        cur=r
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in range(l):
                if (cur>>c)&1: piv.append((c,cur)); break
    return len(piv)==l

def all_GL(l):
    for bits in itertools.product(range(1<<l),repeat=l):
        if invertible(list(bits),l): yield list(bits)

def sample_GL(l,count,rng):
    seen=set(); out=[]
    while len(out)<count:
        M=[rng.randrange(1<<l) for _ in range(l)]
        if invertible(M,l):
            t=tuple(M)
            if t not in seen: seen.add(t); out.append(M)
    return out

def survey(eqs,N,label,exh=5,samples=6000,rng=None):
    K=Kernel(eqs,N); l=len(eqs); cache={}
    base=K.ffd([1<<j for j in range(l)],cache)
    if l<=exh: Ms,mode=list(all_GL(l)),f"exhaustive GL_{l}(F2)"
    else:      Ms,mode=sample_GL(l,samples,rng or random.Random(11)),f"sampled {samples} of GL_{l}(F2)"
    up=[]; upclean=[]; down=0
    for M in Ms:
        if K.new_falls(M,base,cache)>0: continue
        d=K.ffd(M,cache); d=N+1 if d is None else d
        if d>base:
            z=K.zero_gen(M,cache)
            up.append(d)
            if not z: upclean.append((d,M))
        elif d<base: down+=1
    res=dict(label=label,l=l,N=N,base_ffd=base,mode=mode,n_M=len(Ms),
             n_up=len(up),n_up_clean=len(upclean),n_down=down,
             D_ff_max=max(up+[base]),
             D_ff_max_clean=max([d for d,_ in upclean],default=base),
             witness=upclean[0][1] if upclean else None,
             witness_ffd=upclean[0][0] if upclean else None)
    print(f"\n[{label}]  l={l}  D_ff(I)={base}  {mode}")
    print(f"  matrices tried      : {len(Ms)}")
    print(f"  upward separators   : {len(up)}  (of which no zero generator: {len(upclean)})")
    print(f"  downward            : {down}")
    print(f"  D_ff^max observed   : {res['D_ff_max']}   (clean only: {res['D_ff_max_clean']})")
    if upclean: print(f"  witness M rows      : {upclean[0][1]}  -> D_ff(M)={upclean[0][0]}")
    return res

n,npr=6,3
rng=random.Random(n*100+npr)
xR=a_real_xR(n,1,1,rng)
basis=([1]+[1<<j for j in range(1,npr)])[:npr]
eqs=build_system(n,npr,1,xR,basis); N=2*npr
rk,keep=indep_info(eqs)
print(f"cell n={n} n'={npr}  N={N}  l={len(eqs)}  F_2-rank of generators={rk}")
print(f"generator degrees: {[max(popcount(m) for m in f) for f in eqs]}")
print(f"independent subset: indices {keep}")

out=[]
out.append(survey(eqs,N,"FULL dependent set (l=6, rank 5)"))
sub=[eqs[i] for i in keep]
out.append(survey(sub,N,"CONTROL independent subset (l=5, rank 5)"))
json.dump(out,open(f"{sys.path[0]}/control_results.json","w"),indent=1,default=str)
print("\nwrote control_results.json")

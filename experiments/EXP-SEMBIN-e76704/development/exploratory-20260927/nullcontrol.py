"""Is the D_ff -> D_ff^max separation specific to Weil descent, or generic?

Mechanism found: D_ff(I) = max_i deg f_i happens when some F_2-combination of
the generators drops degree.  An invertible M can absorb that drop into the
BASIS (the combination becomes a generator), after which the fall at that
degree is gone.  If so the separation should appear in ANY system with a
degree drop -- including the degree-matched random nulls.
"""
import sys, random, json
sys.path.insert(0,"/tmp/claude-0/-home-user/2da6bcd8-2965-5cb4-a4db-701bb987902e/scratchpad")
from ffd_semaev import build_system, a_real_xR, random_matched, popcount
from fastfall import Kernel

def rank_lowdrop(gs,N):
    """Does some F_2-combination of the generators have degree < max deg?"""
    dmax=max(max(popcount(m) for m in f) for f in gs if f)
    ms=sorted(range(1<<N),key=lambda m:(popcount(m),m)); idx={m:i for i,m in enumerate(ms)}
    degs=[popcount(m) for m in ms]
    hi=[i for i,d in enumerate(degs) if d>=dmax]; lo=[i for i,d in enumerate(degs) if d<dmax]
    piv=[]
    for f in gs:
        cur=0
        for m in f: cur|=1<<idx[m]
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in hi+lo:
                if (cur>>c)&1: piv.append((c,cur)); break
    return dmax, sum(1 for c,_ in piv if degs[c]<dmax)

def indep(gs,N):
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
    return [gs[i] for i in keep]

def sepsearch(gs,N,tries,rng):
    """Sample invertible M; return (base, best D_ff over M, count upward)."""
    K=Kernel(gs,N); l=len(gs); cache={}
    base=K.ffd([1<<j for j in range(l)],cache)
    if base is None: return None,None,0,0
    up=0; best=base
    def inv(M):
        pv=[]
        for r in M:
            cur=r
            for p,pr in pv:
                if (cur>>p)&1: cur^=pr
            if cur:
                for c in range(l):
                    if (cur>>c)&1: pv.append((c,cur)); break
        return len(pv)==l
    import itertools
    if l<=4:
        Ms=[list(b) for b in itertools.product(range(1<<l),repeat=l) if inv(list(b))]
    else:
        seen=set(); Ms=[]
        while len(Ms)<tries:
            M=[rng.randrange(1<<l) for _ in range(l)]
            if inv(M) and tuple(M) not in seen:
                seen.add(tuple(M)); Ms.append(M)
    for M in Ms:
        if K.new_falls(M,base,cache)>0: continue
        if K.zero_gen(M,cache): continue
        d=K.ffd(M,cache); d=N+1 if d is None else d
        if d>base: up+=1; best=max(best,d)
    return base,best,up,len(Ms)

rows=[]
print(f"{'cell':>9} {'kind':>7} {'l':>2} {'dmax':>4} {'drop':>4} {'D_ff(I)':>7} "
      f"{'M':>5} {'up':>5} {'D_ff^max':>8} {'separates':>9}")
print("-"*80)
for n,npr in [(4,3),(5,3),(6,3),(7,3),(4,2),(5,2)]:
    N=2*npr
    rng=random.Random(n*100+npr)
    xR=a_real_xR(n,1,1,rng)
    if xR is None: continue
    basis=([1]+[1<<j for j in range(1,npr)])[:npr]
    eqs=indep(build_system(n,npr,1,xR,basis),N)
    for kind,gs in (("semaev",eqs),("null",indep(random_matched(eqs,N,rng),N))):
        dmax,drop=rank_lowdrop(gs,N)
        r2=random.Random(hash((n,npr,kind))&0xffff)
        base,best,up,nm=sepsearch(gs,N,400,r2)
        rows.append(dict(n=n,nprime=npr,kind=kind,l=len(gs),dmax=dmax,drop=drop,
                         base=base,best=best,up=up))
        print(f"n={n} n'={npr:<2} {kind:>7} {len(gs):>2} {dmax:>4} {drop:>4} "
              f"{str(base):>7} {nm:>5} {up:>5} {str(best):>8} "
              f"{str(best is not None and base is not None and best>base):>9}")
json.dump(rows,open(f"{sys.path[0]}/nullcontrol_results.json","w"),indent=1)
print("\nwrote nullcontrol_results.json")

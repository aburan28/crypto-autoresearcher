import sys, json, random, itertools
sys.path.insert(0,"/tmp/claude-0/-home-user/2da6bcd8-2965-5cb4-a4db-701bb987902e/scratchpad")
from ffd_semaev import build_system, a_real_xR, popcount
from recomb_search import (_tables, new_falls_at, ffd, all_GL, sample_GL,
                           recombine, invertible)

def indep_rank(eqs):
    """F_2 rank of the generators as vectors (are they linearly independent?)."""
    monos=sorted({m for f in eqs for m in f}); idx={m:i for i,m in enumerate(monos)}
    piv=[]
    for f in eqs:
        cur=0
        for m in f: cur|=1<<idx[m]
        for p,pr in piv:
            if (cur>>p)&1: cur^=pr
        if cur:
            for c in range(len(monos)):
                if (cur>>c)&1: piv.append((c,cur)); break
    return len(piv)

def run(n,nprime,seed,exh=4,samples=1500):
    rng=random.Random(seed)
    xR=a_real_xR(n,1,1,rng)
    if xR is None: return None
    basis=([1]+[1<<j for j in range(1,nprime)])[:nprime]
    eqs=build_system(n,nprime,1,xR,basis)
    l,N=len(eqs),2*nprime; tabs=_tables(N)
    base=ffd(eqs,N,tabs=tabs)
    rk=indep_rank(eqs)
    if base is None: return dict(n=n,nprime=nprime,N=N,l=l,rank=rk,base_ffd=None)
    if l<=exh: Ms,mode=list(all_GL(l)),f"exhaustive GL_{l}"
    else:      Ms,mode=sample_GL(l,samples,rng),f"sample {samples}/GL_{l}"
    up=[]; down=0; degen_up=0; clean_up=[]
    for M in Ms:
        req=recombine(eqs,M)
        if new_falls_at(req,N,base,tabs)>0: continue
        d=ffd(req,N,tabs=tabs); d = N+1 if d is None else d
        if d>base:
            z=sum(1 for f in req if len(f)==0)
            up.append((d,z,M))
            if z==0: clean_up.append((d,M))
            else: degen_up+=1
        elif d<base: down+=1
    best=max([d for d,_,_ in up],default=base)
    best_clean=max([d for d,_ in clean_up],default=None)
    return dict(n=n,nprime=nprime,N=N,l=l,rank=rk,indep=(rk==l),base_ffd=base,mode=mode,
                n_M=len(Ms),n_up=len(up),n_up_with_zero_gen=degen_up,
                n_up_clean=len(clean_up),n_down=down,
                D_ff_max_observed=best,D_ff_max_clean=best_clean,
                example_clean=(clean_up[0][1],clean_up[0][0]) if clean_up else None)

if __name__=="__main__":
    out=[]
    print(f"{'cell':>9} {'N':>2} {'l':>2} {'rk':>2} {'indep':>5} {'D_ff(I)':>7} "
          f"{'M':>6} {'up':>5} {'up(0gen)':>8} {'up clean':>8} {'down':>5} "
          f"{'Dffmax':>6} {'clean':>5}")
    print("-"*92)
    for n,np_ in [(3,2),(4,2),(5,2),(6,2),(7,2),(3,3),(4,3),(5,3),(6,3),(7,3)]:
        r=run(n,np_,seed=n*100+np_)
        if r is None: continue
        out.append(r)
        print(f"n={n} n'={np_:<2} {r['N']:>2} {r['l']:>2} {r['rank']:>2} "
              f"{str(r['indep']):>5} {str(r['base_ffd']):>7} {r.get('n_M','-'):>6} "
              f"{r.get('n_up','-'):>5} {r.get('n_up_with_zero_gen','-'):>8} "
              f"{r.get('n_up_clean','-'):>8} {r.get('n_down','-'):>5} "
              f"{str(r.get('D_ff_max_observed')):>6} {str(r.get('D_ff_max_clean')):>5}")
    json.dump(out,open(f"{sys.path[0]}/recomb2_results.json","w"),indent=1,default=str)
    print("\nwrote recomb2_results.json")

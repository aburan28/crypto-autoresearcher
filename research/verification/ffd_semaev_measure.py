import random, json
from collections import Counter
from statistics import median
from ffd_semaev_core import (build_system, fall_profile, first_fall, random_matched,
                        a_real_xR, popcount, on_curve)

SEM_DRAWS, NULL_DRAWS = 10, 25

def indep_basis(n, nprime, rng):
    """random F_2-independent subset of F_{2^n} of size nprime"""
    for _ in range(400):
        b=[rng.randrange(1,1<<n) for _ in range(nprime)]
        # rank over F_2
        rows=list(b); r=0
        for bit in range(n):
            p=None
            for i in range(r,len(rows)):
                if (rows[i]>>bit)&1: p=i;break
            if p is None: continue
            rows[r],rows[p]=rows[p],rows[r]
            for i in range(len(rows)):
                if i!=r and ((rows[i]>>bit)&1): rows[i]^=rows[r]
            r+=1
        if r==nprime: return b
    return None

print(f"Semaev S_3 descent: first-fall degree, {SEM_DRAWS} Semaev draws "
      f"(random target x_R and random V) vs {NULL_DRAWS} support-matched null draws\n")
print("cell        N  eqs | Semaev d_ff dist        | null d_ff dist          | median deficit")
print("-"*104)
rows=[]
for n in (4,5,6,7):
    for nprime in (3,4):
        N=2*nprime
        a2,a6=1,1
        sem=Counter(); nul=Counter(); eqdegs=set()
        for s in range(SEM_DRAWS):
            rng=random.Random(n*7919+nprime*131+s)
            xs=[x for x in range(1<<n) if any(on_curve(x,y,a2,a6,n) for y in range(1<<n))]
            if not xs: continue
            xR=rng.choice(xs)
            basis=indep_basis(n,nprime,rng)
            if basis is None: continue
            eqs=build_system(n,nprime,a6,xR,basis)
            if not eqs: continue
            eqdegs.add(max(max(popcount(m) for m in f) for f in eqs))
            Dmax=min(N,6)
            sem[first_fall(fall_profile(eqs,N,Dmax))]+=1
            if s==0:
                for t in range(NULL_DRAWS):
                    r2=random.Random(n*31+nprime*7+t)
                    nul[first_fall(fall_profile(random_matched(eqs,N,r2),N,Dmax))]+=1
        if not sem: continue
        sm=median([k for k,v in sem.items() if k is not None for _ in range(v)])
        nm=median([k for k,v in nul.items() if k is not None for _ in range(v)]) if nul else None
        deficit = (nm-sm) if nm is not None else None
        sfmt=str(dict(sorted(sem.items(),key=lambda k:(k[0] is None,k[0]))))
        nfmt=str(dict(sorted(nul.items(),key=lambda k:(k[0] is None,k[0]))))
        print(f"n={n} n'={nprime}   {N:2}     | {sfmt:<23} | {nfmt:<23} | {deficit}")
        rows.append(dict(n=n,nprime=nprime,N=N,eqdeg=sorted(eqdegs),
                         semaev_dist={str(k):v for k,v in sem.items()},
                         null_dist={str(k):v for k,v in nul.items()},
                         semaev_median=sm, null_median=nm, median_deficit=deficit))
json.dump(rows, open('ffd_semaev_results.json','w'), indent=1)
print("\nwrote ffd_semaev_results.json")

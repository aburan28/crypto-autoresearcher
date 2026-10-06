"""First-fall / fall-profile measurement for Weil-descended Semaev S_3 systems.

Observable (IDEA-20260916-4b7c1e, underwritten by Caminata-Gorla Thm 2.8 and
eq. (1)):  for a degree-compatible order V_{F,D} = rowsp(M_D), so

    falls(D)     = dim( V_D  intersect  R_{<=D-1} )
    new_falls(D) = falls(D) - dim V_{D-1}
    d_ff         = min{ D : new_falls(D) > 0 }

Everything is over F_2 in the BOOLEAN ring (u_j^2 = u_j), which is where the
descended system lives; monomials are squarefree and represented as bitmasks.
"""
import random, itertools, json, sys

MODS={2:0b111,3:0b1011,4:0b10011,5:0b100101,6:0b1000011,7:0b10000011,
      8:0b100011101,9:0b1000010001,10:0b10000001001}
def gmul(a,b,n):
    m=MODS[n]; r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if (a>>n)&1: a^=m
    return r

# ---- polynomials over F_{2^n} in Boolean variables: dict{monomask:int coeff} ----
def pmul(A,B,n):
    C={}
    for ma,ca in A.items():
        for mb,cb in B.items():
            m=ma|mb                      # Boolean: u^2 = u
            v=gmul(ca,cb,n)
            if v: C[m]=C.get(m,0)^v
    return {m:c for m,c in C.items() if c}
def padd(*Ps):
    C={}
    for P in Ps:
        for m,c in P.items(): C[m]=C.get(m,0)^c
    return {m:c for m,c in C.items() if c}

def build_system(n, nprime, a6, xR, basis):
    """S_3(x1,x2,xR) with x1,x2 in V=<basis>; returns n Boolean polys (sets of monomasks)."""
    x1={1<<j: basis[j] for j in range(nprime)}                 # vars u_0..u_{n'-1}
    x2={1<<(nprime+j): basis[j] for j in range(nprime)}         # vars w_0..w_{n'-1}
    xr={0: xR}
    e2 = padd(pmul(x1,x2,n), pmul(x1,xr,n), pmul(x2,xr,n))
    e3 = pmul(pmul(x1,x2,n), xr, n)
    S  = padd(pmul(e2,e2,n), e3, {0:a6})
    # split each F_{2^n} coefficient into n F_2 components (polynomial basis)
    eqs=[]
    for j in range(n):
        f=set()
        for m,c in S.items():
            if (c>>j)&1: f.add(m)
        if f: eqs.append(frozenset(f))
    return eqs

# ---- Macaulay / fall profile over F_2, rows as python int bitmasks ----
def popcount(x): return bin(x).count('1')

def fall_profile(eqs, N, Dmax):
    """Returns per-degree dict with dim V_D, dim(V_D cap R_{<=D-1}), new_falls."""
    monos=sorted(range(1<<N), key=lambda m:(popcount(m), m))
    idx={m:i for i,m in enumerate(monos)}
    degs=[popcount(m) for m in monos]
    def poly_to_row(P):
        r=0
        for m in P: r |= 1<<idx[m]
        return r
    def rank_and_lowpart(rows, D):
        """Gaussian elimination with degree-D columns FIRST.
        Returns (rank, dim of subspace with zero degree-D part)."""
        hi=[i for i,d in enumerate(degs) if d==D]
        lo=[i for i,d in enumerate(degs) if d< D]
        order=hi+lo
        piv=[]; red=[]
        for r in rows:
            cur=r
            for p,pr in piv:
                if (cur>>p)&1: cur^=pr
            if cur:
                # leading column in 'order'
                for col in order:
                    if (cur>>col)&1:
                        piv.append((col,cur)); red.append(cur); break
        rank=len(piv)
        zero_hi=sum(1 for col,_ in piv if degs[col]<D)
        return rank, zero_hi
    out={}
    prev_rank=0
    for D in range(1,Dmax+1):
        rows=[]
        for f in eqs:
            df=max(popcount(m) for m in f)
            for m in monos:
                prod={mm|m for mm in f}
                if max(popcount(x) for x in prod)<=D:
                    rows.append(poly_to_row(prod))
        if not rows:
            out[D]=dict(dimVD=0,lowdim=0,new_falls=0); continue
        rank, lowdim = rank_and_lowpart(rows, D)
        new_falls = lowdim - prev_rank if D>1 else max(0,lowdim)
        out[D]=dict(dimVD=rank, lowdim=lowdim, new_falls=new_falls)
        prev_rank_candidate = out[D-1]['dimVD'] if D-1 in out else 0
        prev_rank = prev_rank_candidate
    # recompute new_falls against dim V_{D-1}
    for D in sorted(out):
        prev = out[D-1]['dimVD'] if (D-1) in out else 0
        out[D]['new_falls']=out[D]['lowdim']-prev
    return out

def first_fall(prof):
    for D in sorted(prof):
        if prof[D]['new_falls']>0: return D
    return None

def degree_profile(eqs, N):
    """(#eqs, per-eq multiset of monomial degrees) -- the support signature for the null."""
    return [sorted(popcount(m) for m in f) for f in eqs]

def random_matched(eqs, N, rng):
    """Null object: random Boolean system with the SAME per-equation degree profile."""
    out=[]
    for f in eqs:
        degs_needed=[popcount(m) for m in f]
        chosen=set()
        for d in degs_needed:
            for _ in range(500):
                pos=rng.sample(range(N), d)
                m=0
                for p in pos: m|=1<<p
                if m not in chosen: chosen.add(m); break
        out.append(frozenset(chosen))
    return out

def on_curve(x,y,a2,a6,n):
    return (gmul(y,y,n)^gmul(x,y,n)) == (gmul(x,gmul(x,x,n),n)^gmul(a2,gmul(x,x,n),n)^a6)

def a_real_xR(n,a2,a6,rng):
    xs=[x for x in range(1<<n) if any(on_curve(x,y,a2,a6,n) for y in range(1<<n))]
    return rng.choice(xs) if xs else None

def run_cell(n, nprime, seed=1, Dmax=6, a2=1, a6=1):
    rng=random.Random(seed)
    xR=a_real_xR(n,a2,a6,rng)
    if xR is None: return None
    basis=[1]+[1<<j for j in range(1,nprime)]      # 1, a, a^2, ... in F_{2^n}
    basis=basis[:nprime]
    eqs=build_system(n,nprime,a6,xR,basis)
    N=2*nprime
    prof=fall_profile(eqs,N,Dmax)
    null=random_matched(eqs,N,rng)
    nprof=fall_profile(null,N,Dmax)
    return dict(n=n,nprime=nprime,N=N,neqs=len(eqs),xR=xR,
                semaev_ffd=first_fall(prof), null_ffd=first_fall(nprof),
                semaev=prof, null=nprof,
                degree_profile=degree_profile(eqs,N))

if __name__=="__main__":
    print("cell            N  eqs | Semaev d_ff | matched-null d_ff | Semaev falls by degree")
    print("-"*95)
    rows=[]
    for n in (3,4,5,6):
        for nprime in (2,3):
            if 2*nprime>10: continue
            r=run_cell(n,nprime,seed=n*10+nprime,Dmax=2*nprime)
            if r is None: continue
            falls={D:v['new_falls'] for D,v in r['semaev'].items() if v['new_falls']>0}
            print(f"n={n} n'={nprime}      {r['N']:2} {r['neqs']:3}  |   {str(r['semaev_ffd']):>4}      |      {str(r['null_ffd']):>4}         | {falls}")
            rows.append(r)
    import json
    json.dump([{k:v for k,v in r.items() if k in ('n','nprime','N','neqs','semaev_ffd','null_ffd')} for r in rows],
              open('ffd_summary.json','w'), indent=1)

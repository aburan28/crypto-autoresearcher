"""RC-2 design pilot (exploratory, not evidence): geometric-progression bases on Z_N through the frozen count.py.
Seeds fixed in the file; output in pilot/*.log. Run: python3 pilot/rc2_pilot.py"""
import sys, math, time
import pathlib; sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]/'implementation')); sys.dont_write_bytecode=True
import numpy as np, sympy, count
rng=np.random.default_rng(20261021)
def geo(N,mu,B):
    x=1; L=[]
    for _ in range(B): L.append(x); x=(x*mu)%N
    return L
def quad_root(N,q):   # root of x^2 - x + q
    r=sympy.sqrt_mod((1-4*q)%N,N)
    return None if r is None else ((1+r)*pow(2,-1,N))%N
def run(lo,n,kind):
    rows=[]; p=lo
    while len(rows)<n:
        p=int(sympy.nextprime(p+int(rng.integers(1,2000)))); N=p; B=count.base_size(N)
        if kind=='cm5': mu=quad_root(N,5)
        elif kind=='q7': mu=quad_root(N,7)
        elif kind=='q11': mu=quad_root(N,11)
        else: mu=int(rng.integers(2,N-1))
        if mu is None: continue
        L=geo(N,mu,B)
        if len(set(L))<B: continue
        cov,_=count.count_coverage(L,N)
        seen=np.zeros(N,dtype=np.uint8)
        rc=[count.count_coverage(count.random_labels(N,B,np.random.default_rng(int(rng.integers(1<<30)))),N,seen)[0] for _ in range(30)]
        rows.append(cov/np.mean(rc)-1)
    r=np.array(rows)*100
    return r.mean(), r.std(ddof=1)
t0=time.time()
for lo in [2**19,2**21]:
    for kind in ['cm5','q7','q11','generic']:
        m,s=run(lo,12,kind)
        print(f"N~2^{int(math.log2(lo))} {kind:8s} n=12 mean T={m:+.3f}%  sd={s:.3f}%  (se={s/math.sqrt(12):.3f}%)",flush=True)
print('seconds',round(time.time()-t0,1))

"""RC-2 design pilot (exploratory, not evidence): geometric-progression bases on Z_N through the frozen count.py.
Seeds fixed in the file; output in pilot/*.log. Run: python3 pilot/rc2_pilot.py"""
import sys, math, time
import pathlib; sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]/'implementation'))
sys.dont_write_bytecode=True
import numpy as np, sympy
import count
def root(N):
    # root of x^2 - x + 5 mod N: x = (1 + sqrt(-19)) / 2
    r = sympy.sqrt_mod(-19 % N, N)
    if r is None: return None
    return ((1 + r) * pow(2, -1, N)) % N
rng=np.random.default_rng(20261020)
out=[]
t0=time.time()
for lo in [2**17,2**19,2**21]:
    p=lo; rows=[]
    while len(rows)<8:
        p=sympy.nextprime(p+int(rng.integers(1,2000)))
        lam=root(p)
        if lam is None: continue
        N=int(p); B=count.base_size(N)
        # order of lam must exceed B for distinct points
        x=1; ok=True
        labs=[]
        for j in range(B):
            labs.append(x); x=(x*lam)%N
        if len(set(labs))<B: continue
        cov_cm,enum=count.count_coverage(labs,N)
        assert enum==count.binom3(B)
        seen=np.zeros(N,dtype=np.uint8)
        # arm A: exact labels, no sign randomisation; arm B: random signs on the same classes
        sg=rng.integers(0,2,size=B)
        labs_b=[(l if s==0 else N-l)%N for l,s in zip(labs,sg)]
        cov_b,_=count.count_coverage(labs_b,N)
        rc=[count.count_coverage(count.random_labels(N,B,np.random.default_rng(int(rng.integers(1<<30)))),N,seen)[0] for _ in range(40)]
        m=np.mean(rc); sd=np.std(rc,ddof=1)
        rows.append((N,B,cov_cm/m-1,cov_b/m-1,sd/m,1.4/math.sqrt(N)))
    out+=rows
    r=np.array([[x[2],x[3],x[4],x[5]] for x in rows])
    print(f"N~2^{int(math.log2(lo))}: n={len(rows)}  T_exact mean={r[:,0].mean()*100:+.4f}% sd={r[:,0].std(ddof=1)*100:.4f}% | T_randomsigns mean={r[:,1].mean()*100:+.4f}% sd={r[:,1].std(ddof=1)*100:.4f}% | random-vs-random sd/mean={r[:,2].mean()*100:.4f}% (1.4/sqrtN={r[:,3].mean()*100:.4f}%)", flush=True)
print('seconds',round(time.time()-t0,1))

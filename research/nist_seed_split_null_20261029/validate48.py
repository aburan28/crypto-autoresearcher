import random,math,cypari2
from sympy import primerange, legendre_symbol as L
from analysis_lib import probs, pmf as dist  # logged run imported the identical definitions from a scratch null.py
P=cypari2.Pari(); P.allocatemem(10**9)
ells=list(primerange(3,692)); rng=random.Random(20261029)
for trial in range(2):
    p=int(P.nextprime(rng.getrandbits(48)|(1<<47)))
    ks=[]
    while len(ks)<1500:
        b=rng.randrange(1,p); N=int(P.ellcard(P.ellinit([-3,b],p)))
        if not P.isprime(N): continue
        t=p+1-N; D=t*t-4*p; ks.append(sum(1 for l in ells if D%l and pow(D%l,(l-1)//2,l)==1))
    ps=[probs(p,l,True)[0] for l in ells]; f=dist(ps)
    mu=sum(ps); sd=math.sqrt(sum(q*(1-q) for q in ps))
    em=sum(ks)/len(ks); es=math.sqrt(sum((k-em)**2 for k in ks)/(len(ks)-1))
    cdf=[sum(f[:k+1]) for k in range(len(f))]
    ks_stat=max(abs(sum(1 for x in ks if x<=k)/len(ks)-cdf[k]) for k in range(len(f)))
    lo=sum(1 for x in ks if x<=42)/len(ks)
    print(f"p={p}: model mean {mu:.2f} sd {sd:.2f} | empirical(n=1500) mean {em:.2f} sd {es:.2f} | KS D={ks_stat:.4f} (5% crit {1.36/math.sqrt(len(ks)):.4f}) | emp P(X<=42)={lo:.4f} model {cdf[42]:.4f}")

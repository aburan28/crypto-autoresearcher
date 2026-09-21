import sys,os,math; sys.path.insert(0,'.')
from an import *
def pois_ul(k,cl=0.95):
    # exact Garwood upper limit: solve P(X<=k|lam)=1-cl
    lo,hi=0.0,max(10.0,k+10.0)
    while hi-lo>1e-9:
        m=(lo+hi)/2
        s=sum(math.exp(-m)*m**i/math.factorial(i) for i in range(k+1))
        if s>1-cl: lo=m
        else: hi=m
    return (lo+hi)/2
arms=[]
def add(f,tag):
    if os.path.exists(f) and os.path.getsize(f)>10:
        for d in load(f): arms.append((tag,d))
add('power.jsonl','power'); add('r6_main.json','main'); add('r6_corr.json','corr')
add('sweep_r6_mask.jsonl','mask'); add('sweep_r6_act.jsonl','act'); add('r10.json','r10')
print("=== ALL r=6 GENERATION-1 DATA (the clean rate arm) ===")
Nmain=0;kmain=0; Nall=0;kall=0
print(" %-14s %-6s %-6s %10s %6s %8s"%("arm","Smask","Amask","N","hits","null"))
for tag,d in arms:
    if d['r']!=6 or d['prp']: continue
    N=d['N']; k=d['g4'][0]; e=N*Q[4]
    print(" %-14s %-6d %-6d %10.3g %6d %8.3f"%(d['label'],d['Smask'],d['Amask'],N,k,e))
    Nall+=N; kall+=k
    if d['Smask']==1 and d['Amask']==1: Nmain+=N; kmain+=k
for nm,N,k in (("PRIMARY CONFIG A={0} S={0}",Nmain,kmain),("ALL r=6 ARMS POOLED",Nall,kall)):
    if N==0: continue
    e=N*Q[4]; ul=pois_ul(k)
    print("\n %s"%nm)
    print("   N=2^%.2f  hits=%d  null=%.3f  ratio=%.3f"%(math.log2(N),k,e,k/e if e else 0))
    print("   Poisson P(X>=k)=%.3f   95%% UPPER LIMIT on rate ratio = %.2fx"%(pois_tail(k,e),ul/e))
    print("   R-rare resolution = %.2f bits (smallest per-trial prob detected at 95%% = 3/N = 2^%.2f)"%(rrare(N),-rrare(N)))
    print("   => at r=6 an effect of ratio >= %.2fx is EXCLUDED at 95%%; smaller residuals are NOT excluded."%(ul/e))
print("\n=== r=10 DECAY CHECK (PR-7 / V4 artifact tell) ===")
for tag,d in arms:
    if d['r']==10:
        print("  r=10 N=2^%.0f gen1 hits=%d null=%.2f ratio=%.2f  runhist=%s"%(
          math.log2(d['N']),d['g4'][0],d['N']*Q[4],d['g4'][0]/(d['N']*Q[4]),d.get('runhist','n/a')))
print("\n=== r=6 CHAIN / ITERATION (degeneracy-free) ===")
for f in ('r6_main.json','r6_corr.json'):
    if os.path.exists(f) and os.path.getsize(f)>10:
        d=load(f)[0]
        print("  %-12s N=2^%.0f raw runhist=%s"%(d['label'],math.log2(d['N']),d['runhist']))
        if 'runhist_nd' in d:
            print("               degeneracy-free runhist=%s  bnoop=%s"%(d['runhist_nd'],d['bnoop']))
            print("               NON-DEGENERATE chains length>=2 at r=6: %d"%sum(d['runhist_nd'][2:]))

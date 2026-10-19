#!/usr/bin/env python3
"""Independent paired-ratio check: exact enumeration of the bootstrap distribution of the median (all n^n resamples,
n=6 -> 46656), plus an exact sign test across all paired instances. No RNG involved."""
import json, itertools, statistics as st, collections, math
base="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588/runs/"
rows=[]
for f in ("RUN-ECDLP-20a588-01","RUN-ECDLP-20a588-03"):
    rows+=[json.loads(l) for l in open(base+f+"/raw-result.jsonl")]
def pairs(A,B):
    d=collections.defaultdict(list)
    for r in rows:
        a,b=r['results'].get(A,{}),r['results'].get(B,{})
        if a.get('status')=='ok' and b.get('status')=='ok': d[r['L']].append(a['wall_s']/b['wall_s'])
    return d
def exact_boot(xs):
    n=len(xs); meds=sorted(st.median([xs[i] for i in idx]) for idx in itertools.product(range(n),repeat=n))
    N=len(meds); return meds[int(0.025*N)], meds[int(0.975*N)-1]
for A,B in (("A_elim_ms","B_ms"),("A_block_sg","B_sg"),("A_drl_ms","A_elim_ms")):
    print("==",A,"/",B)
    tot=ge=0
    for L,xs in sorted(pairs(A,B).items()):
        lo,hi=exact_boot(xs); tot+=len(xs); ge+=sum(x>1 for x in xs)
        print("  L=%d n=%d median ratio %.3f exact-bootstrap 95%% pct interval [%.3f, %.3f]; instances with ratio>1: %d/%d"%(L,len(xs),st.median(xs),lo,hi,sum(x>1 for x in xs),len(xs)))
    pval=sum(math.comb(tot,k) for k in range(ge,tot+1))/2**tot
    print("  all paired instances: ratio>1 in %d/%d; one-sided exact sign-test p(>=%d | fair coin) = %.3g"%(ge,tot,ge,pval))

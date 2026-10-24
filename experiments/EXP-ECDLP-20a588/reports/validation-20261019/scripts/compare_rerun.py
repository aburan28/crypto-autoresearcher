#!/usr/bin/env python3
"""Compare re-run rows (validator) against recorded rows (RUN-01) on deterministic fields; report timings (informational)."""
import json, sys, statistics as st
base="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588/"
rec={}
for f in ("runs/RUN-ECDLP-20a588-01/raw-result.jsonl","runs/RUN-ECDLP-20a588-03/raw-result.jsonl"):
    for l in open(base+f):
        r=json.loads(l); rec[(r['L'],r['inst'])]=r
DET=("status","f4_max_deg","gb_size","vdim","gb_maxdeg","planted_in_variety")
tot=bad=0; timing=[]
for d in sys.argv[1:]:
    for l in open(d+"/raw-result.jsonl"):
        n=json.loads(l); k=(n['L'],n['inst']); o=rec[k]
        for fld in ("seed","p","p_bits","b","kind"):
            assert n[fld]==o[fld],(k,fld)
        if 'elim_equals_B' in n:
            tot+=1
            if n['elim_equals_B']!=o.get('elim_equals_B'): bad+=1; print("DIFF elim_equals_B",k)
        for arm,v in n['results'].items():
            for f in DET:
                if f in v or f in o['results'][arm]:
                    tot+=1
                    if v.get(f)!=o['results'][arm].get(f): bad+=1; print("DIFF",k,arm,f,v.get(f),o['results'][arm].get(f))
            timing.append((n['L'],arm,v['wall_s'],o['results'][arm]['wall_s']))
print("deterministic fields compared:",tot,"differences:",bad)
import collections
g=collections.defaultdict(list)
for L,a,new,old in timing: g[(L,a)].append((new,old))
print("\ntimings (informational; rerun = 2 workers on 2 cores, recorded = 4 workers on 4 cores):")
for k,v in sorted(g.items()):
    print(" L=%d %-10s rerun median %.4f s | recorded median(same instances) %.4f s | ratio %.2f (n=%d)"%(k[0],k[1],st.median(x for x,_ in v),st.median(y for _,y in v),st.median(x for x,_ in v)/st.median(y for _,y in v),len(v)))
# rerun A/B ratios
byL=collections.defaultdict(dict)
for L,a,new,old in timing: pass

#!/usr/bin/env python3
"""Check 6: compare re-run rows against recorded rows (deterministic fields exactly; timings informational)."""
import json, sys, statistics
ROOT="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/runs"
def load(path): return [json.loads(l) for l in open(path)]
rec = {1: {(r['L'],r['inst']): r for r in load(f"{ROOT}/RUN-ECDLP-8c41d7-01/raw-result.jsonl")},
       2: {(r['L'],r['inst']): r for r in load(f"{ROOT}/RUN-ECDLP-8c41d7-02/raw-result.jsonl")}}
orig = {**rec[1], **rec[2]}
new = {}
files = sys.argv[1:]
for f in files:
    for r in load(f):
        k=(r['L'],r['inst'])
        new.setdefault(k, dict(r, results={}))['results'].update(r['results'])
DET = ("status","planted_in_variety","f4_max_deg","gb_size","vdim","gb_maxdeg")
n_det=n_bad=0; rows=[]
for k in sorted(new):
    o, n = orig[k], new[k]
    for f in ("m","L","inst","kind","seed","p","p_bits","b"):
        n_det+=1
        if o[f]!=n[f]: n_bad+=1; print("MISMATCH",k,f,o[f],n[f])
    if o.get("elim_equals_B")!=n.get("elim_equals_B") and "A_elim_ms" in n['results'] and "B_ms" in n['results']:
        n_bad+=1; print("MISMATCH elim_equals_B",k,o.get("elim_equals_B"),n.get("elim_equals_B"))
    for arm,nv in n['results'].items():
        ov=o['results'][arm]
        for f in DET:
            if f in ov or f in nv:
                n_det+=1
                if ov.get(f)!=nv.get(f): n_bad+=1; print("MISMATCH",k,arm,f,ov.get(f),nv.get(f))
        if nv.get('status')=='ok':
            rows.append((k,arm,ov['wall_s'],nv['wall_s']))
print(f"deterministic fields compared: {n_det}, mismatches: {n_bad}")
print("timings (recorded vs re-run; informational):")
for k,arm,a,b in rows:
    if k[0]==3 or k[1]==0: print(f"  L={k[0]} inst={k[1]} {arm:10s} recorded={a:9.4f}s rerun={b:9.4f}s ratio rerun/recorded={b/a:5.2f}")
# paired relation at the cells re-run
import collections
by=collections.defaultdict(dict)
for k,arm,a,b in rows: by[k][arm]=(a,b)
for pair in (("A_elim_ms","B_ms"),("A_block_sg","B_sg")):
    for L in (2,3):
        rr=[(v[pair[0]][1]/v[pair[1]][1], v[pair[0]][0]/v[pair[1]][0]) for k,v in by.items() if k[0]==L and pair[0] in v and pair[1] in v]
        if rr: print(f"  {pair[0]}/{pair[1]} L={L}: n={len(rr)} rerun median ratio={statistics.median(x for x,_ in rr):.3f}  recorded (same instances) median ratio={statistics.median(y for _,y in rr):.3f}  A>B in rerun for {sum(x>1 for x,_ in rr)}/{len(rr)} pairs")

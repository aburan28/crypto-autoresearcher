#!/usr/bin/env python3
"""Controls recomputed from raw-result.jsonl (Validator check 3a/3c)."""
import json, glob, collections
ROOT="/home/user/crypto-autoresearcher/experiments"
bad=[]; n_planted_ok=collections.Counter(); n_planted_total=collections.Counter(); n_random_ok=collections.Counter()
elim=collections.Counter()
for exp in ("EXP-ECDLP-8c41d7","EXP-ECDLP-20a588"):
    for f in sorted(glob.glob(f"{ROOT}/{exp}/runs/*/raw-result.jsonl")):
        run=f.split('/')[-2]
        for line in open(f):
            d=json.loads(line)
            ms_done = [a for a,v in d['results'].items() if a in ("A_elim_ms","B_ms") and v.get('status')=='ok']
            has_b = 'elim_equals_B' in d
            both = len(ms_done)==2
            elim[(run,d['L'],'both_ms_ok' if both else 'not_both', 'recorded='+str(d.get('elim_equals_B','absent')))]+=1
            for arm,v in d['results'].items():
                st=v.get('status')
                if d['kind']=='planted':
                    n_planted_total[(run,d['L'],arm,st)]+=1
                    if st=='ok':
                        n_planted_ok[(run,d['L'],arm)]+=1
                        if v.get('planted_in_variety') is not True:
                            bad.append((run,d['L'],d['inst'],arm,v.get('planted_in_variety')))
                else:
                    if st=='ok': n_random_ok[(run,d['L'],arm)]+=1
                    if st=='ok' and 'planted_in_variety' in v: bad.append(('random-with-flag',run,d['inst'],arm))
print("Planted-in-variety violations (ok planted rows whose flag is not True):", bad)
print()
print("ok planted rows per (run,L,arm) [all have planted_in_variety True iff no violations]:")
for k in sorted(n_planted_ok): 
    if k[0].startswith('RUN-ECDLP-8c41d7'): print(' ',k,n_planted_ok[k])
print()
print("elim_equals_B bookkeeping (both A_elim_ms and B_ms 'ok' <=> elim_equals_B recorded):")
for k in sorted(elim): print(' ',k,elim[k])

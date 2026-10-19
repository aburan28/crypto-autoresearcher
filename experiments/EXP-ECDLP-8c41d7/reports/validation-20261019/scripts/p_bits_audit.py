#!/usr/bin/env python3
"""Check 2b: prime bit-length of every msolve result in every EXP-ECDLP-* run (raw-result.jsonl)."""
import json, glob, collections, os
ROOT="/home/user/crypto-autoresearcher/experiments"
tab=collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(f"{ROOT}/EXP-ECDLP-*/runs/*/raw-result.jsonl")):
    exp=f.split('/')[-4]; run=f.split('/')[-2]
    for line in open(f):
        d=json.loads(line)
        for arm,res in d['results'].items():
            if exp=="EXP-ECDLP-502ae2": fam = "msolve" if arm in ("A","B","C") else "enum"
            elif exp=="EXP-ECDLP-f49f75": fam = "enum" if arm=="E" else "singular"
            else: fam = "msolve" if arm.endswith("_ms") else "singular"
            tab[(fam,d['p_bits'])][res.get('status')]+=1
print("family  p_bits  status counts (all runs of all EXP-ECDLP-* experiments)")
for k in sorted(tab): print(f"{k[0]:9s} {k[1]:3d}   {dict(tab[k])}")
crash_range=[k for k in tab if k[0]=="msolve" and k[1] in (17,18)]
print()
print("msolve results at 17/18-bit primes:", {k:dict(tab[k]) for k in crash_range})
print("msolve results with status 'ok' at 17/18-bit primes:", sum(tab[k].get('ok',0) for k in crash_range))

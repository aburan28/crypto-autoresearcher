#!/usr/bin/env python3
"""Reproduce the P-256 sorted-root inversion seen in the first point run."""

import hashlib
import json
from pathlib import Path

from sage.all import EllipticCurve, GF, Integer

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAND=ROOT/'research/nist_seed_selection_20261016/raw/candidates.jsonl'
ORD=ROOT/'research/nist_seed_provenance_20261016/census/orders_871696354.txt'
TARGETS=ROOT/'research/nist_seed_selection_20261016/targets.json'
assert hashlib.sha256(CAND.read_bytes()).hexdigest()=='e854c17a38d5e9f1fca9eb8dd1aa034a6b6cd69d28a2a3acf78b1a187515a441'
targets={x['name']:x for x in json.loads(TARGETS.read_text())}
p=Integer(targets['P-256']['p'])
orders={}
for line in ORD.read_text().splitlines():
    index,n,nt=map(int,line.split())
    if index in (81,1842):orders[index]=(n,nt)
rows={}
for line in CAND.read_text().splitlines():
    item=json.loads(line)
    if item['target']=='P-256' and item['index'] in (81,1842):rows[item['index']]=item
assert set(rows)==set(orders)=={81,1842}
out=[]
for index in (81,1842):
    roots=[Integer(int(x,16)) for x in rows[index]['variants']['nist_fips_186_2']['b_roots']]
    square=Integer(-27)*pow(int(rows[index]['variants']['nist_fips_186_2']['c'],16),-1,int(p))%p
    exponent_root=pow(int(square),(int(p)+1)//4,int(p))
    counts=[int(EllipticCurve(GF(p),[-3,b]).cardinality()) for b in roots]
    n,nt=orders[index]
    assert n in (0,*counts) and nt in counts
    assert counts[roots.index(exponent_root)]==n if n else counts[roots.index(exponent_root)]!=nt
    out.append({'index':index,'sorted_b_roots':[hex(int(b)) for b in roots],
                'sorted_root_orders':[str(x) for x in counts],
                'exponent_root_sorted_index':roots.index(exponent_root),
                'census_n':str(n),'census_nt':str(nt)})
target=HERE/'root_diagnostic.json'
text=json.dumps({'source_sha256':{str(CAND.relative_to(ROOT)):hashlib.sha256(CAND.read_bytes()).hexdigest(),
                                  str(ORD.relative_to(ROOT)):hashlib.sha256(ORD.read_bytes()).hexdigest(),
                                  str(TARGETS.relative_to(ROOT)):hashlib.sha256(TARGETS.read_bytes()).hexdigest()},
                 'rows':out},sort_keys=True,indent=2)+'\n'
if target.exists():assert target.read_text()==text
else:target.write_text(text)
print(json.dumps({'rows':len(out),'root_indexes':[x['exponent_root_sorted_index'] for x in out]}))

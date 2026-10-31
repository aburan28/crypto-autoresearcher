#!/usr/bin/env python3
"""J1 independent finite archive, source bridge, and negative-control audit."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
DRAW = ROOT / 'docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json'
FINITE = ROOT / 'formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean'
WITNESS = ROOT / 'formal/CryptoResearch/Semaev/ConcreteFirstFallWitness.lean'
BIND = HERE / 'raw/input-bindings.json'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def mul(a,b):
    p=0
    for _ in range(4):
        if b&1:p^=a
        b>>=1;a<<=1
        if a&16:a^=19
    return p
def rank(rs):
    piv={}
    for r in rs:
        while r:
            p=r.bit_length()-1
            if p not in piv:piv[p]=r;break
            r^=piv[p]
    return len(piv)
def product(eq,m,parity=True):
    r=0
    for x in eq:
        t=1<<(x|m)
        if parity:r^=t
        else:r|=t
    return r
def rows(eq,d):
    return [(i,m,product(f,m)) for i,f in enumerate(eq) for m in range(256)
            if all(k.bit_count()<=d for k in range(256) if product(f,m)>>k&1)]
def failcheck(name,fn):
    try:fn()
    except AssertionError:return {'control':name,'rejected':True}
    return {'control':name,'rejected':False}
def main():
    binding=json.loads(BIND.read_text())
    checked=[]
    for entry in binding['entries']:
        p=ROOT/entry['path']
        if not p.exists():continue
        raw=p.read_bytes();assert len(raw)==entry['bytes'] and sha(raw)==entry['sha256'],entry['path']
        checked.append(entry['path'])
    assert len(checked)==len(binding['entries']),(len(checked),len(binding['entries']))
    archive=json.loads(DRAW.read_text())
    matches=[e for e in archive['draws'] if (e['n'],e['nprime'],e['draw'],e['seed'],e['xR'],e['basis'])==(4,4,1,32201,1,[9,3,2,12])]
    assert len(matches)==1
    entry=matches[0];equations=entry['equations']
    canonical=sha(json.dumps(equations,separators=(',',':')).encode())
    assert canonical==entry['equations_sha256']==binding['archived_equations_canonical_sha256']
    assert archive['curve_model']['a2']==1 and archive['curve_model']['a6']==1
    # S3(x1,x2,1) = (x1*x2+x1+x2)^2 + x1*x2 + 1 in characteristic two.
    values=[[0]*256 for _ in range(4)]
    for a in range(256):
        x=y=0
        for j,b in enumerate(entry['basis']):
            if a>>j&1:x^=b
            if a>>(j+4)&1:y^=b
        xy=mul(x,y);t=xy^x^y;s=mul(t,t)^xy^1
        for j in range(4):values[j][a]=s>>j&1
    derived=[]
    for v in values:
        c=v[:]
        for j in range(8):
            for m in range(256):
                if m>>j&1:c[m]^=c[m^(1<<j)]
        derived.append([m for m in range(256) if c[m]])
    assert equations==derived
    finite=FINITE.read_text();witness=WITNESS.read_text()
    literal=re.search(r'def equations\s*:\s*List \(List Nat\)\s*:=\s*(\[\[.*?\]\])',finite,re.S)
    assert literal and json.loads(literal[1])==equations
    combo=int(re.search(r'def comboMask\s*:\s*Nat\s*:=\s*(\d+)',witness)[1])
    wlit=int(re.search(r'def witnessNat\s*:\s*Nat\s*:=\s*(\d+)',witness)[1])
    r2=rows(equations,2);r3=rows(equations,3)
    assert len(r2)==28 and len(r3)==80
    selected=[(j,i,m) for j,(i,m,_) in enumerate(r3) if combo>>j&1]
    w=0
    for j,_,_ in selected:w^=r3[j][2]
    assert w==wlit and len(selected)==23
    assert all(k.bit_count()<=2 for k in range(256) if w>>k&1)
    sep=lambda x:((x>>80)&1)^((x>>192)&1)
    assert all(sep(r)==0 for _,_,r in r2) and sep(w)==1
    assert (rank([r for _,_,r in r2]),rank([r for _,_,r in r3]),rank([r for _,_,r in r2]+[w]))==(11,53,12)
    delta=product(equations[0],1,False)^product(equations[0],1,True)
    assert [k for k in range(256) if delta>>k&1]==[1,17,129]
    mutated=json.loads(json.dumps(equations));mutated[0][0]=3
    controls=[failcheck('one component monomial mutation',lambda: assert_eq(mutated,derived)),
              failcheck('set product substituted for XOR product',lambda: assert_eq(product(equations[0],1,False),product(equations[0],1,True)))]
    assert all(c['rejected'] for c in controls)
    result={'source_commit':binding['source_commit'],'plan_commit':'a1f3d0fde48d8a09301d65f8b8056f3cf42fc307',
      'read_files':checked+['coordination/formal-reviews/BATCH-semaev-concrete-20261031/review-plan.yaml','coordination/formal-reviews/BATCH-semaev-concrete-20261031/input-bindings.json'],
      'archive_sha256':sha(DRAW.read_bytes()),'equations_sha256':canonical,'equations':derived,
      'draw_matches':len(matches),'truth_assignments':256,'field_inverse_count':sum(any(mul(a,b)==1 for b in range(1,16)) for a in range(1,16)),
      'degree_two_rows':len(r2),'degree_three_rows':len(r3),'degree_two_rank':11,'degree_three_rank':53,
      'selected_rows':selected,'combo_mask':combo,'witness_bits':w,'witness_monomials':[k for k in range(256) if w>>k&1],
      'separator':[80,192],'separator_degree_two_nonzero_rows':sum(sep(r) for _,_,r in r2),'separator_witness':sep(w),
      'archived_set_product_extra_masks':[k for k in range(256) if delta>>k&1],'controls':controls}
    print(json.dumps(result,indent=2))
def assert_eq(a,b):assert a==b
if __name__=='__main__':main()

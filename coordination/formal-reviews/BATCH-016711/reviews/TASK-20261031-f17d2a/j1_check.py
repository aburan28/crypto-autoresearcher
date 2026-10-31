#!/usr/bin/env python3
"""J1 independent finite source, row-order, and negative-control check."""
import hashlib
import json
import re
from pathlib import Path

P = Path(__file__).parent / 'inputs'
EXPECTED = {
    'draws.json': 'f2c0bd08739c56f0dc24a3a67e4ab367319944c7a7868aef8c67508ac1ef13b2',
    'BooleanParityFiniteCertificate.lean': '0be9ab16bcbfd6bee2763021945ac5a5dc9a0f572dec98d7e6f0f1adcd2f8503',
    'BooleanParityFiltrationCertificate.lean': '45f972351c41292aa2e742f97dc5ee1fe5048ee103ca90dbaaea06ac10148840',
    'ConcreteFirstFallWitness.lean': '51515d57fe99c94ce8383ca37083e6681f29c2b26d7ac3ed7f2728c568b70459',
}
def sha(b): return hashlib.sha256(b).hexdigest()
def check(ok, msg):
    if not ok: raise ValueError(msg)
def field_mul(a,b):
    c=0
    for i in range(4):
        for j in range(4):
            if (a>>i)&(b>>j)&1: c ^= 1<<(i+j)
    for i in range(6,3,-1):
        if c>>i&1: c ^= 19<<(i-4)
    return c
def rank(vs):
    piv={}
    for v in vs:
        while v:
            b=v.bit_length()-1
            if b not in piv:
                piv[b]=v; break
            v ^= piv[b]
    return len(piv)
def row(eq,m,parity=True):
    ans=0
    for t in eq:
        bit=1<<(t|m)
        if parity: ans ^= bit
        else: ans |= bit
    return ans
def popcount(n): return bin(n).count('1')
def rows(eqs,d):
    return [(i,m,row(e,m)) for i,e in enumerate(eqs) for m in range(256)
            if not (row(e,m)&sum(1<<k for k in range(256) if popcount(k)>d))]
def main():
    hashes={name:sha((P/name).read_bytes()) for name in EXPECTED}
    check(hashes==EXPECTED,'pinned source hash mismatch')
    data=json.loads((P/'draws.json').read_bytes())
    matches=[a for a in data['draws'] if tuple(a[k] for k in ('n','nprime','draw','seed','xR'))==(4,4,1,32201,1) and a['basis']==[9,3,2,12]]
    check(len(matches)==1,'nonunique archival draw')
    draw=matches[0]; archived=draw['equations']
    canonical=sha(json.dumps(archived,separators=(',',':')).encode())
    check(canonical==draw['equations_sha256']=='89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb','archive equation hash')
    check(all(any(field_mul(a,b)==1 for b in range(1,16)) for a in range(1,16)),'field invertibility')
    truth=[[0]*256 for _ in range(4)]
    for mask in range(256):
        x=[0,0]
        for j,b in enumerate(draw['basis']):
            if mask>>j&1: x[0] ^= b
            if mask>>(j+4)&1: x[1] ^= b
        ab=field_mul(*x); e=ab^x[0]^x[1]
        value=field_mul(e,e)^ab^1
        for j in range(4): truth[j][mask]=value>>j&1
    derived=[]
    for vals in truth:
        coeff=vals[:]
        for bit in range(8):
            for mask in range(256):
                if mask>>bit&1: coeff[mask] ^= coeff[mask^(1<<bit)]
        derived.append([m for m,c in enumerate(coeff) if c])
    check(derived==archived,'derived equation order or contents differ')
    finite=(P/'BooleanParityFiniteCertificate.lean').read_text()
    match=re.search(r'def equations\s*:\s*List \(List Nat\)\s*:=\s*(\[\[.*?\]\])',finite,re.S)
    check(bool(match),'Lean equations missing')
    lean_eq=json.loads(match.group(1))
    check(lean_eq==derived,'Lean equation mismatch')
    witness_source=(P/'ConcreteFirstFallWitness.lean').read_text()
    def literal(name):
        m=re.search(r'def '+name+r'\s*:\s*Nat\s*:=\s*(\d+)',witness_source)
        check(bool(m),'Lean literal missing: '+name)
        return int(m.group(1))
    combo=literal('comboMask'); lean_witness=literal('witnessNat')
    r2=rows(derived,2); r3=rows(derived,3)
    check((len(r2),len(r3))==(28,80),'row counts differ')
    selected=[(j,i,m) for j,(i,m,v) in enumerate(r3) if combo>>j&1]
    witness=0
    for j,i,m in selected: witness ^= r3[j][2]
    check(witness==lean_witness,'Lean witness indexing mismatch')
    check(witness.bit_length()<=256 and all(not(witness>>m&1) or popcount(m)<=2 for m in range(256)),'witness degree')
    sep=lambda v: (v>>80&1)^(v>>192&1)
    check(all(sep(v)==0 for i,m,v in r2) and sep(witness)==1,'separator mismatch')
    rank2=rank([v for i,m,v in r2]); rank3=rank([v for i,m,v in r3])
    check((rank2,rank3,rank([v for i,m,v in r2]+[witness]),rank([v for i,m,v in r3]+[witness]))==(11,53,12,53),'rank mismatch')
    mutated=[e[:] for e in archived]; mutated[0][0]=1
    mutation_hash=sha(json.dumps(mutated,separators=(',',':')).encode())
    check(mutation_hash!=canonical and mutated!=lean_eq,'changed archive falsely accepted')
    xor_product=row(derived[0],1,True); union_product=row(derived[0],1,False)
    extra=[m for m in range(256) if (xor_product^union_product)>>m&1]
    check(extra==[1,17,129] and xor_product!=union_product,'duplicate-monomial control failed')
    return {
        'pinned_source_commit':'ad91212179e737d829076ca593d608261590ba89',
        'source_sha256':hashes,'equation_canonical_sha256':canonical,
        'equations':derived,'equation_term_counts':[len(e) for e in derived],
        'field_nonzero_elements_with_inverse':15,'truth_assignments':256,
        'row_order':'equation index ascending, then multiplier mask 0..255; retain parity-product degree <= D',
        'degree_two_row_count':len(r2),'degree_three_row_count':len(r3),
        'degree_two_rank':rank2,'degree_three_rank':rank3,
        'selected_rows_zero_based':selected,'selected_row_count':len(selected),
        'combo_mask':combo,'witness_nat':witness,
        'witness_monomial_masks':[m for m in range(256) if witness>>m&1],
        'separator_masks':[80,192],'separator_on_degree_two_rows':sorted(set(sep(v) for i,m,v in r2)),
        'separator_on_witness':sep(witness),
        'rank_degree_two_plus_witness':12,'rank_degree_three_plus_witness':53,
        'changed_archive_control':{'mutated_equation_sha256':mutation_hash,'differs_from_bound_hash':mutation_hash!=canonical,'differs_from_lean':mutated!=lean_eq},
        'duplicate_monomial_control':{'multiplier':1,'union_extra_masks':extra},
    }
if __name__=='__main__': print(json.dumps(main(),indent=2))

#!/usr/bin/env python3
"""Static independent replay for RUN-KIC-278e3e; launches no native process."""
from __future__ import annotations
import functools, hashlib, itertools, json, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'research/n19_pair_transport_20260921'
R=ROOT/'experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e'
N=19; FIELD=1<<N; MASK=FIELD-1; POLY=FIELD|39; ORDER=262543
ARMS=('expanded','canonical_poly','canonical_normal_x')

def load(p): return json.loads(Path(p).read_text())
def mul(a,b):
    z=0
    for i in range(N):
        if b>>i&1:z^=a<<i
    for i in range(2*N-2,N-1,-1):
        if z>>i&1:z^=POLY<<(i-N)
    return z
@functools.lru_cache(maxsize=FIELD)
def sq(a):return mul(a,a)
@functools.lru_cache(maxsize=FIELD)
def inv(a):
    if not a:raise ZeroDivisionError
    u,v,g,h=a,POLY,1,0
    while u!=1:
        if not u:raise ValueError('noninvertible')
        k=u.bit_length()-v.bit_length()
        if k<0:u,v=v,u;g,h=h,g;k=-k
        u^=v<<k;g^=h<<k
    while g.bit_length()>N:g^=POLY<<(g.bit_length()-N-1)
    return g
def neg(p):return None if p is None else (p[0],p[0]^p[1])
def add(p,q):
    if p is None:return q
    if q is None:return p
    x,y=p;u,v=q
    if x==u:
        if y^v==x:return None
        if p!=q or x==0:raise ValueError('bad equal x')
        l=x^mul(y,inv(x));z=sq(l)^l^1
        return z,sq(x)^mul(l^1,z)
    l=mul(y^v,inv(x^u));z=sq(l)^l^x^u^1
    return z,mul(l,x^z)^z^y
def times(p,n):
    z=None
    while n:
        if n&1:z=add(z,p)
        p=add(p,p);n>>=1
    return z
def frob(p):return None if p is None else (sq(p[0]),sq(p[1]))
def shift(p,j):
    for _ in range(j):p=frob(p)
    return p
def code(p):return None if p is None else (p[0]<<19)|p[1]
def decode(p):return None if p is None else tuple(p)
def oncurve(p):
    if p is None:return True
    x,y=p;return (sq(y)^mul(x,y))==(mul(sq(x),x)^sq(x)^1)
def rank(values):
    piv={}
    for value in values:
        while value:
            bit=value.bit_length()-1
            if bit not in piv:piv[bit]=value;break
            value^=piv[bit]
    return len(piv)
def normal_basis():
    for beta in range(1,FIELD):
        cols=[];x=beta
        for _ in range(N):cols.append(x);x=sq(x)
        if rank(cols)==N:break
    piv={}
    for bit,col in enumerate(cols):
        row=col;mask=1<<bit
        while row:
            lead=row.bit_length()-1
            if lead not in piv:piv[lead]=(row,mask);break
            a,b=piv[lead];row^=a;mask^=b
    inverse=[]
    for bit in range(N):
        row=1<<bit;mask=0
        while row:
            a,b=piv[row.bit_length()-1];row^=a;mask^=b
        inverse.append(mask)
    return beta,tuple(cols),tuple(inverse)
def to_normal(x,inverse):
    z=0
    for i in range(N):
        if x>>i&1:z^=inverse[i]
    return z
def rotate(x,j):return ((x<<j)|(x>>(N-j)))&MASK if j else x
def canonical_poly(p):
    if p is None:return None,0,1,None
    best=None;bj=0;bs=1;current=p
    for j in range(N):
        for sign,candidate in ((1,current),(-1,neg(current))):
            c=code(candidate)
            if best is None or c<best:best,bj,bs,chosen=c,j,sign,candidate
        current=frob(current)
    return best,bj,bs,chosen
def canonical_normal(p,inverse):
    if p is None:return None,0
    start=to_normal(p[0],inverse);best=FIELD;bj=0
    for j in range(N):
        v=rotate(start,j)
        if v<best:best,bj=v,j
    return best,bj
def backward(p,j,sign):
    p=shift(p,(N-j)%N)
    return p if sign==1 else neg(p)
def base(recipe):
    seeds=[tuple(x['point']) for x in recipe['seed_points']];points=[];seen=set()
    for seed in seeds:
        assert oncurve(seed) and times(seed,ORDER) is None
        p=seed
        for _ in range(N):
            for q in (p,neg(p)):
                assert q not in seen;seen.add(q);points.append(q)
            p=frob(p)
        assert p==seed
    points.sort();assert len(points)==152 and len({x for x,y in points})==76
    assert all(frob(p) in seen and neg(p) in seen for p in points)
    return points,seeds
def row_tuple(a,b,total,anchor,frame):
    a,b=sorted((a,b));none=(FIELD,0)
    pk=lambda p:none if p is None else p
    return (*pk(a),*pk(b),*pk(total),*anchor,*frame)
def parse_tables(document):
    return {x['arm']:{x['key']['value']:x for x in x['rows']} for x in document['arms']},\
           {x['arm']:x['stats'] for x in document['arms']}
def verify():
    recipe=load(P/'inputs/base.json');points,seeds=base(recipe);pointset=set(points)
    beta,columns,inverse=normal_basis();assert beta==3
    tables,stats=parse_tables(load(R/'control_tables.json'))
    # Expanded: sorted i<=j and emplace retains first lexicographic point pair.
    expanded={}
    for i,a in enumerate(points):
        for b in points[i:]:expanded.setdefault(code(add(a,b)),(a,b))
    assert len(expanded)==11097 and set(expanded)==set(tables['expanded'])
    for key,(a,b) in expanded.items():
        row=tables['expanded'][key];assert list(a)==row['normalized_endpoints'][0]
        assert list(b)==row['normalized_endpoints'][1] and decode(row['stored_sum'])==add(a,b)
        assert row['anchor']==[-1,-1,-1,0] and row['source_frame']==[0,1]
    # Rebuild all 380 anchored candidates and exact deterministic retained rows.
    expected={'canonical_poly':{},'canonical_normal_x':{}}
    for i in range(4):
        for k in range(i,4):
            for j in range(N):
                positive=shift(seeds[k],j)
                for source_sign,b in ((1,positive),(-1,neg(positive))):
                    total=add(seeds[i],b)
                    key,fj,fs,canonical=canonical_poly(total)
                    aa=shift(seeds[i],fj);bb=shift(b,fj)
                    if fs==-1:aa,bb=neg(aa),neg(bb)
                    candidate=(row_tuple(aa,bb,canonical,(i,k,j,source_sign),(fj,fs)),aa,bb,canonical,[i,k,j,source_sign],[fj,fs])
                    if key not in expected['canonical_poly'] or candidate[0]<expected['canonical_poly'][key][0]:expected['canonical_poly'][key]=candidate
                    key,fj=canonical_normal(total,inverse);aa,bb=shift(seeds[i],fj),shift(b,fj);stored=shift(total,fj)
                    candidate=(row_tuple(aa,bb,stored,(i,k,j,source_sign),(fj,1)),aa,bb,stored,[i,k,j,source_sign],[fj,1])
                    if key not in expected['canonical_normal_x'] or candidate[0]<expected['canonical_normal_x'][key][0]:expected['canonical_normal_x'][key]=candidate
    assert all(len(expected[a])==293 and set(expected[a])==set(tables[a]) for a in expected)
    for arm in expected:
        for key,candidate in expected[arm].items():
            _,a,b,total,anchor,frame=candidate;row=tables[arm][key]
            assert row['normalized_endpoints']==[list(min(a,b)),list(max(a,b))]
            assert decode(row['stored_sum'])==total and row['anchor']==anchor and row['source_frame']==frame
            assert a in pointset and b in pointset and add(a,b)==total
    # Every full pair sum must transport back through both compressed maps.
    transport=0;nontrivial=0;sign_flips=0
    for key,target_pair in expanded.items():
        target=add(*target_pair)
        for arm in ('canonical_poly','canonical_normal_x'):
            if arm=='canonical_poly':ck,j,sign,_=canonical_poly(target)
            else:
                ck,j=canonical_normal(target,inverse);sign=1
            row=tables[arm][ck];a,b=map(decode,row['normalized_endpoints']);stored=decode(row['stored_sum'])
            if arm=='canonical_normal_x':
                aligned=shift(target,j)
                if aligned==stored:sign=1
                elif aligned==neg(stored):sign=-1
                else:raise AssertionError('x key without stored sum/sign correspondence')
            aa,bb=backward(a,j,sign),backward(b,j,sign)
            assert aa in pointset and bb in pointset and add(aa,bb)==target
            transport+=1;nontrivial+=j!=0;sign_flips+=sign==-1
    # Membership serialization: all arms equal, exact bit count, padding clear.
    raw=(R/'control_membership.bin').read_bytes();assert raw[:8]==b'KIC19PT1'
    version,count,arms,nbytes=struct.unpack('<4I',raw[8:24]);assert (version,count,arms,nbytes)==(1,262543,3,32818)
    bits=[raw[24+i*nbytes:24+(i+1)*nbytes] for i in range(3)]
    assert bits[0]==bits[1]==bits[2] and sum(x.bit_count() for x in bits[0])==11097
    assert bits[0][-1]&0x80==0
    pool=load(P/'inputs/pool.json');generator=tuple(pool['pool_representatives'][0])
    universe=[None];representatives=[];seen={None}
    for scalar_value in pool['public_target_scalar_representatives']:
        q=times(generator,scalar_value);representatives.append(q);current=q
        for _ in range(N):
            for point in (current,neg(current)):
                assert point not in seen;seen.add(point);universe.append(point)
            current=frob(current)
        assert current==q
    assert len(universe)==262543
    for index,point in enumerate(universe):
        expected_bit=code(point) in expanded
        assert bool(bits[0][index>>3]&(1<<(index&7)))==expected_bit
    # Full query artifact: identities, all witnesses, equal verdict/first-hit index.
    query_doc=load(R/'control_queries.json');assert len(query_doc['targets'])==6909 and len(query_doc['exceptions'])==153
    witness_count=0;sat=unsat=0
    for target_index,row in enumerate((*query_doc['targets'],*query_doc['exceptions'])):
        q=decode(row['Q']);outcomes=[]
        if target_index<6909:assert q==representatives[target_index] and row['target_index']==target_index
        for arm in ARMS:
            result=row['arms'][arm];outcomes.append((result['status'],result['third_index']))
            if result['status']=='SAT':
                witness=list(map(decode,result['witness']));assert all(x in pointset for x in witness)
                assert add(add(witness[0],witness[1]),witness[2])==q;witness_count+=1
        assert len(set(outcomes))==1
        if row in query_doc['targets']:
            sat+=outcomes[0][0]=='SAT';unsat+=outcomes[0][0]=='UNSAT'
    assert (sat,unsat)==(6189,720)
    # Membership hashes bind complete public universe; equality is exact for all 262543 bits.
    hashes=load(R/'membership_hashes.json')
    for arm,data in zip(ARMS,bits):assert hashlib.sha256(data).hexdigest()==hashes[arm+'_sha256']
    # Actual known-false predicates, independently evaluated.
    genuine_target=next(add(*pair) for pair in expanded.values() if add(*pair) is not None and canonical_poly(add(*pair))[1]!=0)
    ck,j,sign,_=canonical_poly(genuine_target);row=tables['canonical_poly'][ck];a,b=map(decode,row['normalized_endpoints'])
    forged_shift=add(backward(a,(j+1)%19,sign),backward(b,(j+1)%19,sign))!=genuine_target
    forged_sign=add(backward(a,j,-sign),backward(b,j,-sign))!=genuine_target
    wrong_key=(ck^1)!=canonical_poly(decode(row['stored_sum']))[0]
    missing=set(points);missing.remove(points[0])
    noninvariant=any(neg(p) not in missing or frob(p) not in missing for p in missing)
    assert all((forged_shift,forged_sign,wrong_key,noninvariant))
    return {'base_points':len(points),'normal_beta':beta,'normal_columns':len(columns),
            'expanded_keys':len(expanded),'canonical_poly_keys':len(expected['canonical_poly']),
            'canonical_normal_x_keys':len(expected['canonical_normal_x']),
            'transport_replays':transport,'nonzero_shift_replays':nontrivial,'sign_flip_replays':sign_flips,
            'membership_points':count,'membership_members':sum(x.bit_count() for x in bits[0]),
            'membership_universe_recomputed':len(universe),
            'target_queries':len(query_doc['targets']),'target_SAT':sat,'target_UNSAT':unsat,
            'exception_queries':len(query_doc['exceptions']),'witnesses_group_replayed':witness_count,
            'forgeries':{'wrong_shift':forged_shift,'wrong_sign':forged_sign,'wrong_key':wrong_key,'noninvariant_base':noninvariant},
            'stats':stats}
if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))

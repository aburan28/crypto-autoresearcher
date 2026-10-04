"""Exact GF(2^7) and binary Koblitz curve operations for EXP-KIC-424885.

Only public synthetic points occur here. Timed workers construct every basis,
factor base and MITM table afresh; they never receive a discrete-log label.
"""
from __future__ import annotations
import hashlib
from typing import Iterable

N=7; MASK=(1<<N)-1; MODULUS=0x83; A=1; B=1; R=71
Point=tuple[int,int]|None

def mul(a:int,b:int)->int:
    assert 0<=a<=MASK and 0<=b<=MASK
    p=0
    while b:
        if b&1:p^=a
        b>>=1;a<<=1
    for k in range(p.bit_length()-1,N-1,-1):
        if p>>k&1:p^=MODULUS<<(k-N)
    return p
def sq(a:int)->int:return mul(a,a)
def powf(a:int,e:int)->int:
    z=1
    while e:
        if e&1:z=mul(z,a)
        a=sq(a);e>>=1
    return z
def inv(a:int)->int:
    if a==0:raise ZeroDivisionError("zero has no field inverse")
    return powf(a,126)
def div(a:int,b:int)->int:return mul(a,inv(b))
def rhs(x:int)->int:return mul(sq(x),x)^sq(x)^B
def on_curve(p:Point)->bool:
    if p is None:return True
    x,y=p
    return 0<=x<=MASK and 0<=y<=MASK and (sq(y)^mul(x,y))==rhs(x)
def neg(p:Point)->Point:
    if p is None:return None
    x,y=p;return x,y^x
def add(p:Point,q:Point)->Point:
    if p is None:return q
    if q is None:return p
    x1,y1=p;x2,y2=q
    if x1==x2:
        if y1^y2==x1:return None
        if p!=q:raise ValueError("same x is neither equal nor inverse")
        if x1==0:return None
        lam=x1^div(y1,x1)
        x3=sq(lam)^lam^A
        y3=sq(x1)^mul(lam^1,x3)
        return x3,y3
    lam=div(y1^y2,x1^x2)
    x3=sq(lam)^lam^x1^x2^A
    y3=mul(lam,x1^x3)^x3^y1
    return x3,y3
def scalar_mul(p:Point,n:int)->Point:
    if n<0:return scalar_mul(neg(p),-n)
    out=None
    while n:
        if n&1:out=add(out,p)
        p=add(p,p);n>>=1
    return out
def frob(p:Point)->Point:
    if p is None:return None
    return sq(p[0]),sq(p[1])
def lifts(x:int)->tuple[Point,...]:
    return tuple((x,y) for y in range(128) if on_curve((x,y)))
def points()->tuple[Point,...]:
    return (None,)+tuple((x,y) for x in range(128) for y in range(128) if on_curve((x,y)))
def subgroup_points()->tuple[Point,...]:
    return tuple(p for p in points() if scalar_mul(p,R) is None)
def generator()->Point:
    for x in range(1,128):
        for y in range(128):
            p=(x,y)
            if on_curve(p) and scalar_mul(p,R) is None:return p
    raise RuntimeError("declared generator absent")
def normal_basis()->tuple[int,tuple[int,...]]:
    for beta in range(1,128):
        cols=[];v=beta
        for _ in range(7):cols.append(v);v=sq(v)
        if binary_rank(cols)==7:return beta,tuple(cols)
    raise RuntimeError("normal basis absent")
def binary_rank(values:Iterable[int])->int:
    pivots={}
    for value in values:
        while value:
            bit=value.bit_length()-1
            if bit not in pivots:pivots[bit]=value;break
            value^=pivots[bit]
    return len(pivots)
def normal_to_poly(mask:int,columns:tuple[int,...])->int:
    out=0
    for bit in range(7):
        if mask>>bit&1:out^=columns[bit]
    return out
def poly_to_normal(value:int,columns:tuple[int,...])->int:
    pivots={}
    for index,column in enumerate(columns):
        row=column;mask=1<<index
        while row:
            bit=row.bit_length()-1
            if bit not in pivots:
                pivots[bit]=(row,mask)
                break
            prior,prior_mask=pivots[bit]
            row^=prior;mask^=prior_mask
        else:raise RuntimeError("normal conversion is not bijective")
    out=0
    while value:
        bit=value.bit_length()-1
        if bit not in pivots:raise RuntimeError("normal conversion is not bijective")
        row,mask=pivots[bit]
        value^=row;out^=mask
    return out
def digest(label:str)->bytes:return hashlib.sha256(label.encode()).digest()
def hash_mask(label:str)->int:return int.from_bytes(digest(label),"little")%128
def x_orbit(x:int)->tuple[int,...]:
    out=[];v=x
    for _ in range(7):out.append(v);v=sq(v)
    return tuple(out)
def admitted_x(x:int)->bool:
    if x==0:return False
    ys=lifts(x)
    return len(ys)==2 and all(scalar_mul(p,R) is None for p in ys)
def candidate_flats(c:int,columns:tuple[int,...])->tuple[tuple[int,int,int],tuple[int,int,int]]|None:
    triples=[]
    for t in range(2):
        vals=tuple(normal_to_poly(hash_mask(f"GFB-SAT-N7-v1-flat-{c:02d}-{t}-{z}"),columns) for z in "abc")
        if vals[1]==0 or vals[2]==0 or vals[1]==vals[2]:return None
        triples.append(vals)
    return tuple(triples) # type: ignore[return-value]
def candidate_x(flats:tuple[tuple[int,int,int],...])->tuple[set[int],dict[int,tuple[int,int,int,int]],list[dict]]:
    found=set();canonical={};all_mappings=[]
    for t,(a,b,c) in enumerate(flats):
        for j in range(8):
            for u in range(2):
                for v in range(2):
                    if j==7:
                        all_mappings.append({"selector":[t,j,u,v],"x":None,"valid":False,"reason":"j_7_forbidden"})
                        continue
                    x=a^(b if u else 0)^(c if v else 0)
                    for _ in range(j):x=sq(x)
                    all_mappings.append({"selector":[t,j,u,v],"x":x});found.add(x)
                    canonical.setdefault(x,(t,j,u,v))
    return found,canonical,all_mappings
def point_key(p:Point)->tuple[int,int]:
    if p is None:return (-1,-1)
    return p
def base_from_x(xs:Iterable[int])->tuple[Point,...]:
    return tuple(sorted((p for x in xs for p in lifts(x)),key=point_key))
def select_candidate()->dict:
    beta,columns=normal_basis()
    for c in range(64):
        flats=candidate_flats(c,columns)
        if flats is None:continue
        raw_xs,canonical,mappings=candidate_x(flats)
        xs={x for x in raw_xs if admitted_x(x)}
        if len(xs)!=14:continue
        orbits={min(x_orbit(x)) for x in xs}
        if len(orbits)!=2 or any(len(set(x_orbit(x)))!=7 for x in xs):continue
        for mapping in mappings:
            x=mapping["x"]
            if x is None:continue
            selector=tuple(mapping["selector"])
            if x not in xs:mapping.update(valid=False,reason="x_not_admitted")
            elif selector!=canonical[x]:mapping.update(valid=False,reason="duplicate_selector")
            else:mapping.update(valid=True,reason="canonical")
        assert len(mappings)==64 and sum(m["valid"] for m in mappings)==14
        return {"candidate_index":c,"beta":beta,"columns":list(columns),"flats":[list(v) for v in flats],"raw_x_values":sorted(raw_xs),"x_values":sorted(xs),"points":[list(p) for p in base_from_x(xs)],"canonical_inverse":{str(x):list(canonical[x]) for x in sorted(xs)},"all_mappings":mappings,"orbit_representatives":sorted(orbits)}
    raise RuntimeError("POOL_INADMISSIBLE")
def select_null(candidate_reps:Iterable[int])->dict:
    accepted=[];reps=[];target=set(candidate_reps)
    for i in range(256):
        x=hash_mask(f"GFB-SAT-N7-v1-null-{i:03d}")
        if x==0 or not admitted_x(x):continue
        orbit=x_orbit(x)
        if len(set(orbit))!=7:continue
        rep=min(orbit)
        if rep in reps:continue
        for prior in reps:
            if {prior,rep}!=target:
                xs=set(x_orbit(prior))|set(orbit)
                assert len(xs)==14
                return {"arrival_index":i,"orbit_representatives":[prior,rep],"x_values":sorted(xs),"points":[list(p) for p in base_from_x(xs)]}
        reps.append(rep);accepted.append(i)
    raise RuntimeError("NULL_INADMISSIBLE")
def batch_invert(values:list[int])->list[int|None]:
    prefix=[];product=1
    for v in values:
        prefix.append(product)
        if v:product=mul(product,v)
    back=inv(product);out=[None]*len(values)
    for i in range(len(values)-1,-1,-1):
        if values[i]:out[i]=mul(back,prefix[i]);back=mul(back,values[i])
    return out
def batch_add(pairs:list[tuple[Point,Point]])->list[Point]:
    denominators=[]
    for p,q in pairs:
        if p is None or q is None:denominators.append(0)
        elif p[0]==q[0]:denominators.append(p[0] if p==q else 0)
        else:denominators.append(p[0]^q[0])
    inverses=batch_invert(denominators);out=[]
    for (p,q),inverse in zip(pairs,inverses):
        if inverse is None:out.append(add(p,q));continue
        assert p is not None and q is not None
        x1,y1=p;x2,y2=q
        if p==q:
            lam=x1^mul(y1,inverse);x3=sq(lam)^lam^A;y3=sq(x1)^mul(lam^1,x3)
        else:
            lam=mul(y1^y2,inverse);x3=sq(lam)^lam^x1^x2^A;y3=mul(lam,x1^x3)^x3^y1
        out.append((x3,y3))
    return out
def direct_mitm(q:Point,base:tuple[Point,...])->tuple[Point,Point,Point]|None:
    if q in base:
        p=base[0];return q,p,neg(p)
    pairs=[(base[i],base[j]) for i in range(len(base)) for j in range(i,len(base))]
    table={}
    for pair,total in zip(pairs,batch_add(pairs)):table.setdefault(total,pair)
    rests=batch_add([(q,neg(p)) for p in base])
    for p,rest in zip(base,rests):
        if rest in table:
            a,b=table[rest]
            witness=(a,b,p)
            if add(add(*witness[:2]),witness[2])==q:return witness
    return None

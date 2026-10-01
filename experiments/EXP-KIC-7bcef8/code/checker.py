#!/usr/bin/env python3
"""Independent long-division/Euclid replay of N19 pair transport evidence.

This module imports no producer kernel or prior checker. It runs once after
the native control artifacts are archived, before benchmark admission.
"""
from __future__ import annotations
import argparse,functools,hashlib,itertools,json,struct,time
from collections import defaultdict
from pathlib import Path
from typing import Any

BITS=19
FIELD=1<<BITS
MASK=FIELD-1
POLY=FIELD|39
R=262543
Point=tuple[int,int]|None
ARMS=("expanded","canonical_poly","canonical_normal_x")
INPUT_HASHES={
    "base":"f00b5c5710d041bf862525b5f8d1baf15328e4a9bd6a11f659d300b5ca62cfb1",
    "cases":"4c1c05917c85694d7b86f4a7e99a32d1676e585cb0e6a68c89bfd6bfd0508e64",
    "pool":"023e512c29db5fe1d23cc32740db0f4ce418f5920d6feed06c74f6e42df2ed6f",
}
def require(ok:bool,reason:str)->None:
    if not ok:raise ValueError(reason)
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def fmul(a:int,b:int)->int:
    raw=0
    for bit in range(BITS):
        if b>>bit&1:raw^=a<<bit
    for bit in range(2*BITS-2,BITS-1,-1):
        if raw>>bit&1:raw^=POLY<<(bit-BITS)
    return raw
@functools.lru_cache(maxsize=FIELD)
def fsq(a:int)->int:return fmul(a,a)
def finv(a:int)->int:
    require(a!=0,"independent zero inverse")
    u,v,g,h=a,POLY,1,0
    while u!=1:
        require(u!=0,"independent noninvertible value")
        shift=u.bit_length()-v.bit_length()
        if shift<0:u,v=v,u;g,h=h,g;shift=-shift
        u^=v<<shift;g^=h<<shift
    while g.bit_length()>BITS:g^=POLY<<(g.bit_length()-BITS-1)
    return g
def negative(p:Point)->Point:return None if p is None else (p[0],p[1]^p[0])
def oncurve(p:Point)->bool:
    if p is None:return True
    x,y=p
    return 0<=x<FIELD and 0<=y<FIELD and (fsq(y)^fmul(x,y))==(fmul(fsq(x),x)^fsq(x)^1)
def add(p:Point,q:Point)->Point:
    if p is None:return q
    if q is None:return p
    x,y=p;u,v=q
    if x==u:
        if y^v==x:return None
        require(p==q and x!=0,"independent equal-x group input invalid")
        slope=x^fmul(y,finv(x));z=fsq(slope)^slope^1
        return z,fsq(x)^fmul(slope^1,z)
    slope=fmul(y^v,finv(x^u));z=fsq(slope)^slope^x^u^1
    return z,fmul(slope,x^z)^z^y
def times(p:Point,n:int)->Point:
    out=None
    while n:
        if n&1:out=add(out,p)
        p=add(p,p);n>>=1
    return out
def frob(p:Point)->Point:return None if p is None else (fsq(p[0]),fsq(p[1]))
def shift(p:Point,j:int)->Point:
    for _ in range(j):p=frob(p)
    return p
def batched(p:Point,other:list[Point])->list[Point]:
    result=[None]*len(other);ids=[];den=[];prefix=[];total=1
    for i,q in enumerate(other):
        if p is None:result[i]=q
        elif q is None:result[i]=p
        elif p[0]==q[0]:result[i]=add(p,q)
        else:
            d=p[0]^q[0];ids.append(i);den.append(d);prefix.append(total)
            total=fmul(total,d)
    if ids:
        back=finv(total)
        for j in range(len(ids)-1,-1,-1):
            i=ids[j];q=other[i]
            assert p is not None and q is not None
            one=fmul(back,prefix[j]);back=fmul(back,den[j])
            slope=fmul(p[1]^q[1],one)
            x=fsq(slope)^slope^p[0]^q[0]^1
            result[i]=(x,fmul(slope,p[0]^x)^x^p[1])
    return result
def code(p:Point)->int|None:return None if p is None else (p[0]<<19)|p[1]
def decode(value)->Point:return None if value is None else tuple(value)
def base_from_seeds(recipe:dict)->tuple[list[Point],list[Point]]:
    require(recipe["n"]==19 and recipe["modulus"]==POLY and recipe["r"]==R,
            "independent base parameters differ")
    a,b,c=recipe["affine_coordinates"]
    require(sorted((a,a^b,a^c,a^b^c))==recipe["plane_key"],
            "independent affine key mismatch")
    seed=[tuple(row["point"]) for row in recipe["seed_points"]]
    require(sorted(p[0] for p in seed)==recipe["plane_key"],"seed x mismatch")
    points=[];seen=set()
    for p in seed:
        require(p[0]!=0 and oncurve(p) and times(p,R) is None,"seed subgroup failure")
        start=p
        for _ in range(19):
            require(oncurve(p),"independent generated point off curve")
            for q in (p,negative(p)):
                require(q not in seen,"independent signed base overlap")
                seen.add(q);points.append(q)
            p=frob(p)
        require(p==start,"seed orbit not length19")
    require(len(points)==152 and len({p[0] for p in points})==76,
            "independent base cardinality mismatch")
    points.sort()
    for p in points:require(negative(p) in seen and frob(p) in seen,"base not invariant")
    return points,seed
def normal_basis():
    def rank(values):
        pivots={}
        for value in values:
            while value:
                bit=value.bit_length()-1
                if bit not in pivots:pivots[bit]=value;break
                value^=pivots[bit]
        return len(pivots)
    for beta in range(1,FIELD):
        columns=[];value=beta
        for _ in range(19):columns.append(value);value=fsq(value)
        if rank(columns)==19:break
    else:raise ValueError("no normal basis")
    pivots={}
    for bit,column in enumerate(columns):
        row=column;mask=1<<bit
        while row:
            lead=row.bit_length()-1
            if lead not in pivots:pivots[lead]=(row,mask);break
            prior,prior_mask=pivots[lead];row^=prior;mask^=prior_mask
        else:raise ValueError("normal basis dependent")
    inverse=[]
    for bit in range(19):
        value=1<<bit;mask=0
        while value:
            row,part=pivots[value.bit_length()-1]
            value^=row;mask^=part
        inverse.append(mask)
    return beta,tuple(columns),tuple(inverse)
def to_normal(x:int,inverse:tuple[int,...])->int:
    out=0
    for bit in range(19):
        if x>>bit&1:out^=inverse[bit]
    return out
def rotate(mask:int,j:int)->int:
    return ((mask<<j)|(mask>>(19-j)))&MASK if j else mask
@functools.lru_cache(maxsize=FIELD)
def canonical_poly(p:Point)->tuple[int|None,int,int]:
    if p is None:return None,0,1
    best=None;best_shift=best_sign=0;current=p
    for j in range(19):
        for sign,candidate in ((1,current),(-1,negative(current))):
            packed=code(candidate)
            if best is None or packed<best:
                best,best_shift,best_sign=packed,j,sign
        current=frob(current)
    return best,best_shift,best_sign
@functools.lru_cache(maxsize=FIELD)
def canonical_normal_x(x:int,inverse:tuple[int,...])->tuple[int,int]:
    start=to_normal(x,inverse);best=FIELD;best_j=0
    for j in range(19):
        candidate=rotate(start,j)
        if candidate<best:best,best_j=candidate,j
    return best,best_j
def inverse_transport(p:Point,j:int,sign:int)->Point:
    p=shift(p,(19-j)%19)
    return p if sign==1 else negative(p)
def key_of(row:dict)->int|None:
    key=row["key"];return key["value"]
def verify_table_row(row:dict,arm:str,points:set[Point],inverse:tuple[int,...])->None:
    a,b=map(decode,row["normalized_endpoints"])
    total=decode(row["stored_sum"])
    require(a in points and b in points and add(a,b)==total,
            f"{arm} table row not actual base pair")
    key=key_of(row)
    want_kind=("infinity" if total is None else
               "normal_x" if arm=="canonical_normal_x" else "full_point")
    require(row["key"]["kind"]==want_kind and ((key is None)==(total is None)),
            f"{arm} table key tag/infinity mismatch")
    if arm=="expanded":require(key==code(total),"expanded row key mismatch")
    elif arm=="canonical_poly":require(key==canonical_poly(total)[0],"poly row key mismatch")
    else:require((key is None if total is None else
                  key==canonical_normal_x(total[0],inverse)[0]),
                 "normal-x row key mismatch")
def table_maps(tables:dict,points:set[Point],inverse:tuple[int,...]):
    out={}
    for arm in ARMS:
        block=next(item for item in tables["arms"] if item["arm"]==arm)
        groups=defaultdict(list)
        for row in block["rows"]:
            verify_table_row(row,arm,points,inverse)
            a,b=map(decode,row["normalized_endpoints"])
            total=decode(row["stored_sum"])
            key=key_of(row)
            groups[key].append((a,b,total,row))
        require(len(groups)==(11097 if arm=="expanded" else 293),
                f"{arm} distinct table key count mismatch")
        require(all(len(entries)==1 for entries in groups.values()),
                f"{arm} retained multiple witnesses under one key")
        require(block["stats"]["keys"]==len(groups) and
                block["stats"]["rows"]==len(block["rows"]),"table metadata mismatch")
        out[arm]=groups
    return out
def lookup(target:Point,arm:str,tables:dict,inverse:tuple[int,...]):
    if arm=="expanded":
        key=code(target);j=0;sign=1
    elif arm=="canonical_poly":key,j,sign=canonical_poly(target)
    else:
        if target is None:key,j=None,0
        else:key,j=canonical_normal_x(target[0],inverse)
        sign=1
    candidates=tables[arm].get(key,())
    for a,b,total,_ in candidates:
        if arm=="canonical_normal_x":
            aligned=shift(target,j)
            if aligned==total:sign=1
            elif aligned==negative(total):sign=-1
            else:continue
        if arm=="expanded":x,y=a,b
        else:x,y=inverse_transport(a,j,sign),inverse_transport(b,j,sign)
        require(add(x,y)==target,"independent inverse transported pair fails group sum")
        return x,y
    return None
def direct_pairset(points:list[Point]):
    table={}
    for i,p in enumerate(points):
        for j,total in enumerate(batched(p,points[i:]),i):
            table.setdefault(code(total),(points[i],points[j]))
    require(len(table)==11097,"independent direct expanded pairset count mismatch")
    return table
def check_table_selection(tables:dict,points:list[Point],seeds:list[Point],
                          inverse:tuple[int,...],direct:dict)->None:
    # Producer's sorted i<=j traversal must retain the first lex pair.
    for key,(a,b) in direct.items():
        saved=tables["expanded"][key][0]
        require((saved[0],saved[1])==(a,b),"expanded witness is not first lex pair")
    expected={"canonical_poly":{},"canonical_normal_x":{}}
    for i in range(4):
        for k in range(i,4):
            for j in range(19):
                positive=shift(seeds[k],j)
                for source_sign,second in ((1,positive),(-1,negative(positive))):
                    total=add(seeds[i],second)
                    poly_key,poly_shift,poly_sign=canonical_poly(total)
                    endpoints=tuple(sorted(
                        negative(shift(p,poly_shift)) if poly_sign==-1
                        else shift(p,poly_shift) for p in (seeds[i],second)))
                    poly_sum=negative(shift(total,poly_shift)) if poly_sign==-1 else shift(total,poly_shift)
                    poly_candidate=(*endpoints,poly_sum,i,k,j,source_sign,poly_shift,poly_sign)
                    prior=expected["canonical_poly"].get(poly_key)
                    if prior is None or poly_candidate[:7]<prior[:7]:
                        expected["canonical_poly"][poly_key]=poly_candidate
                    normal_key,normal_shift=(None,0) if total is None else canonical_normal_x(total[0],inverse)
                    normal_end=tuple(sorted((shift(seeds[i],normal_shift),shift(second,normal_shift))))
                    normal_sum=shift(total,normal_shift)
                    normal_candidate=(*normal_end,normal_sum,i,k,j,source_sign,normal_shift,1)
                    prior=expected["canonical_normal_x"].get(normal_key)
                    if prior is None or normal_candidate[:7]<prior[:7]:
                        expected["canonical_normal_x"][normal_key]=normal_candidate
    for arm in ("canonical_poly","canonical_normal_x"):
        require(set(expected[arm])==set(tables[arm]),f"{arm} anchored key set incomplete")
        for key,candidate in expected[arm].items():
            saved=tables[arm][key][0]
            require((saved[0],saved[1],saved[2])==candidate[:3],
                    f"{arm} retained pair/sum not lexicographically first anchored witness")
            row=saved[3]
            require(row["anchor"]==list(candidate[3:7]) and
                    row["source_frame"]==list(candidate[7:9]),
                    f"{arm} retained anchor/frame metadata mismatch")
def direct_query(q:Point,points:list[Point],pairs:dict):
    differences=batched(q,[negative(p) for p in points])
    for i,rest in enumerate(differences):
        hit=pairs.get(code(rest))
        if hit is None:continue
        witness=(hit[0],hit[1],points[i])
        require(add(add(witness[0],witness[1]),witness[2])==q,
                "independent direct query witness failed")
        return True,i,witness
    return False,-1,None
def verify_witness(q:Point,witness,points:set[Point])->None:
    require(witness is not None and len(witness)==3,"missing exact-three witness")
    decoded=tuple(decode(p) for p in witness)
    # Seed subgroup checks plus signed Frobenius closure establish subgroup
    # membership for every member of this fixed base.
    require(all(p in points and oncurve(p) for p in decoded),
            "reported witness contains nonbase/offcurve point")
    require(add(add(decoded[0],decoded[1]),decoded[2])==q,
            "reported witness fails full group identity")
def public_points(pool:dict,generator:Point):
    universe=[None];representatives=[];seen={None}
    for d in pool["public_target_scalar_representatives"]:
        require(0<d<R,"public representative scalar invalid")
        q=times(generator,d);require(q is not None and oncurve(q) and times(q,R) is None,
                                    "public representative off subgroup")
        representatives.append(q);current=q;own=set()
        for _ in range(19):
            for signed in (current,negative(current)):
                require(oncurve(signed),"public signed conjugate off curve")
                require(signed not in seen and signed not in own,
                        "public signed orbit overlap")
                seen.add(signed);own.add(signed);universe.append(signed)
            current=frob(current)
        require(current==q and len(own)==38,"public orbit not length38")
    require(len(universe)==R and len(seen)==R and len(representatives)==6909,
            "public full prime subgroup universe incomplete")
    return universe,representatives
def membership_bytes(path:Path):
    data=path.read_bytes();require(data[:8]==b"KIC19PT1","membership header magic")
    version,point_count,arms,bytes_per=struct.unpack_from("<4I",data,8)
    require((version,point_count,arms,bytes_per)==(1,R,3,32818),
            "membership dimensions mismatch")
    require(len(data)==24+3*bytes_per,"membership bytes length mismatch")
    slices=[data[24+i*bytes_per:24+(i+1)*bytes_per] for i in range(3)]
    require(all((row[-1]&0x80)==0 for row in slices),"membership high padding bit set")
    return slices
def check_forgeries(control:dict,base:list[Point],tables:dict,inverse:tuple[int,...],generator:Point)->dict:
    source=control["forgeries"]
    target=decode(source["target_pair_sum"])
    require(target is not None,"forgery target must be nonzero")
    pair=lookup(target,"canonical_poly",tables,inverse)
    require(pair is not None and add(*pair)==target,"genuine forgery-source pair invalid")
    shifted=(frob(pair[0]),frob(pair[1]))
    flipped=(negative(pair[0]),negative(pair[1]))
    require(add(*shifted)!=target and add(*flipped)!=target,
            "wrong inverse shift/sign forged witness accepted")
    points=set(base)
    genuine=tables["canonical_poly"][canonical_poly(target)[0]][0][3]
    verify_table_row(genuine,"canonical_poly",points,inverse)
    wrong_key=json.loads(json.dumps(genuine))
    wrong_key["key"]["value"]^=1
    try:verify_table_row(wrong_key,"canonical_poly",points,inverse)
    except ValueError:pass
    else:raise ValueError("forged table key accepted by actual row verifier")
    wrong_sum=json.loads(json.dumps(genuine))
    mutated=add(decode(wrong_sum["stored_sum"]),generator)
    wrong_sum["stored_sum"]=None if mutated is None else list(mutated)
    try:verify_table_row(wrong_sum,"canonical_poly",points,inverse)
    except ValueError:pass
    else:raise ValueError("forged stored sum accepted by actual row verifier")
    bad=base[1:]+[generator]
    require(generator not in points and len(set(bad))==152,"same-shape forged base invalid")
    def closed(values):
        all_points=set(values)
        return all(p is not None and negative(p) in all_points and frob(p) in all_points
                   for p in values)
    require(not closed(bad) and not closed(base[:-1]),
            "missing/replaced noninvariant base accepted")
    bad_q=generator
    for bit in range(19):
        candidate=(generator[0],generator[1]^(1<<bit))
        if not oncurve(candidate):bad_q=candidate;break
    require(not oncurve(bad_q),"offcurve input forgery unavailable")
    require(source["same_shape_replace_removed_point_with_G"]=="rejected_by_closure_guard",
            "producer same-shape guard missing")
    return {"wrong_shift_sign_rejected":True,"wrong_table_key_rejected":True,
            "wrong_stored_sum_rejected":True,"missing_point_rejected":True,
            "same_shape_replacement_rejected":True,"offcurve_rejected":True,
            "producer_definitions":source}
def run(base_path:Path,cases_path:Path,pool_path:Path,run_path:Path,out_path:Path)->dict:
    start=time.monotonic()
    for name,path in (("base",base_path),("cases",cases_path),("pool",pool_path)):
        require(sha(path)==INPUT_HASHES[name],f"{name} frozen input hash changed")
    base_recipe=json.loads(base_path.read_text())
    pool=json.loads(pool_path.read_text())
    points,seed=base_from_seeds(base_recipe);pointset=set(points)
    beta,columns,inverse=normal_basis()
    controls=json.loads((run_path/"native_controls.json").read_text())
    require(controls["status"]=="passed" and controls["normal_beta"]==beta and
            controls["normal_columns"]==list(columns),"producer native normal control mismatch")
    table_json=json.loads((run_path/"control_tables.json").read_text())
    tables=table_maps(table_json,pointset,inverse)
    direct=direct_pairset(points)
    check_table_selection(tables,points,seed,inverse,direct)
    require(set(direct)==set(tables["expanded"]),"expanded table differs from independent direct pairset")
    for key in sorted(direct,key=lambda value:(value is None,value)):
        target=None if key is None else (key>>19,key&MASK)
        for arm in ("canonical_poly","canonical_normal_x"):
            hit=lookup(target,arm,tables,inverse)
            require(hit is not None and hit[0] in pointset and hit[1] in pointset and
                    add(*hit)==target,f"{arm} misses direct pair sum")
    universe,reps=public_points(pool,tuple(base_recipe["generator"]))
    observed=membership_bytes(run_path/"control_membership.bin")
    membership_manifest=json.loads((run_path/"membership_hashes.json").read_text())
    require(membership_manifest["universe_points"]==R and
            membership_manifest["bytes_per_arm"]==32818,
            "membership sidecar dimensions mismatch")
    for arm,vector in zip(ARMS,observed):
        require(membership_manifest[arm+"_sha256"]==hashlib.sha256(vector).hexdigest(),
                f"{arm} membership sidecar hash mismatch")
    member_count=0
    for index,p in enumerate(universe):
        truth=code(p) in direct
        member_count+=truth
        for arm,row in zip(ARMS,observed):
            saved=bool(row[index>>3]&(1<<(index&7)))
            require(saved==truth,f"{arm} membership bit differs at point index {index}")
            hit=lookup(p,arm,tables,inverse)
            require((hit is not None)==truth,f"{arm} independent membership mismatch")
            if hit is not None:require(add(*hit)==p,"member pair witness fails group")
    require(member_count==11097,"full subgroup membership count mismatch")
    queries=json.loads((run_path/"control_queries.json").read_text())
    require(len(queries["targets"])==6909 and len(queries["exceptions"])==153,
            "target/exception query counts differ")
    replay_rows=[];sat=0
    for index,(q,saved) in enumerate(zip(reps,queries["targets"])):
        require(saved["target_index"]==index and decode(saved["Q"])==q,
                "public target identity/order mismatch")
        yes,third,witness=direct_query(q,points,direct);sat+=yes
        arms=saved["arms"]
        for arm in ARMS:
            row=arms[arm]
            require((row["status"]=="SAT")==yes and row["third_index"]==third,
                    f"{arm} target verdict/first-third mismatch")
            require(row["probes"]==(third+1 if yes else 152),
                    f"{arm} target probe count mismatch")
            if yes:verify_witness(q,row["witness"],pointset)
            else:require(row["witness"] is None,"UNSAT carries witness")
        replay_rows.append({"target_index":index,"Q":list(q),"exact_three":yes,
                            "first_third_index":third})
    require(sat==6189 and 6909-sat==720,"independent triple coverage regression")
    exceptions=[None,*points]
    for index,(q,saved) in enumerate(zip(exceptions,queries["exceptions"])):
        require(saved["index"]==index and decode(saved["Q"])==q,
                "exception order/identity mismatch")
        yes,third,_=direct_query(q,points,direct)
        for arm in ARMS:
            row=saved["arms"][arm]
            require((row["status"]=="SAT")==yes and row["third_index"]==third,
                    f"{arm} exception verdict/first-third mismatch")
            require(row["probes"]==(third+1 if yes else 152),
                    f"{arm} exception probe count mismatch")
            if yes:verify_witness(q,row["witness"],pointset)
    forgeries=check_forgeries(controls,points,tables,inverse,tuple(base_recipe["generator"]))
    result={"schema":"crypto.autoresearch.n19_pair_transport_independent_replay.v1",
        "status":"passed","method":"independent Python polynomial long division, Euclid inverse, group law and coordinate MITM",
        "input_sha256":{name:sha(path) for name,path in
            (("base",base_path),("cases",cases_path),("pool",pool_path))},
        "control_sha256":{name:sha(run_path/name) for name in
            ("native_controls.json","control_tables.json","control_membership.bin",
             "control_queries.json","membership_hashes.json")},
        "normal_beta":beta,"normal_columns":list(columns),
        "direct_distinct_pair_sums":len(direct),"public_membership_points":len(universe),
        "public_pair_members":member_count,"target_SAT":sat,"target_UNSAT":6909-sat,
        "exceptions":153,"forgery_checks":forgeries,"per_target_replay":replay_rows,
        "wall_seconds":time.monotonic()-start,
        "scope":"validation table reuse only; no benchmark native query process"}
    out_path.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
    return result
def main()->None:
    p=argparse.ArgumentParser()
    for name in ("base","cases","pool","run","output"):p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    result=run(args.base,args.cases,args.pool,args.run,args.output)
    print(json.dumps({"status":result["status"],"pair_sums":result["direct_distinct_pair_sums"],
                      "target_SAT":result["target_SAT"]},sort_keys=True))
if __name__=="__main__":main()

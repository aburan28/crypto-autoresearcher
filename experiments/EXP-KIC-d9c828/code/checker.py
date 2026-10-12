#!/usr/bin/env python3
"""Independent P9 finite replay using polynomial long division and Euclid.

This process imports no native or producer arithmetic.  It reconstructs every
public recipe and exact pair/query object before benchmark admission.
"""
from __future__ import annotations
import argparse,functools,hashlib,json,time
from pathlib import Path
from typing import Any

BASE_SHA="f00b5c5710d041bf862525b5f8d1baf15328e4a9bd6a11f659d300b5ca62cfb1"
Point=tuple[int,int]|None
BITS=FIELD=MASK=POLY=R=ORDER=ORBITS=BASE_POINTS=0
REGIME=""

def require(ok:bool,reason:str)->None:
    if not ok:raise ValueError(reason)
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def configure(regime:str)->None:
    global BITS,FIELD,MASK,POLY,R,ORDER,ORBITS,BASE_POINTS,REGIME
    REGIME=regime
    if regime=="n19_k4":BITS,POLY,R,ORDER,ORBITS,BASE_POINTS=19,(1<<19)|39,262543,525086,4,152
    elif regime=="n23_k16":BITS,POLY,R,ORDER,ORBITS,BASE_POINTS=23,(1<<23)|33,4196903,8393806,16,736
    else:raise ValueError(f"unknown regime {regime}")
    FIELD=1<<BITS;MASK=FIELD-1;fsq.cache_clear()
def fmul(a:int,b:int)->int:
    raw=0
    for bit in range(BITS):
        if b>>bit&1:raw^=a<<bit
    for bit in range(2*BITS-2,BITS-1,-1):
        if raw>>bit&1:raw^=POLY<<(bit-BITS)
    return raw
@functools.lru_cache(maxsize=1<<23)
def fsq(a:int)->int:return fmul(a,a)
def finv(a:int)->int:
    require(a!=0,"independent zero inverse")
    u,v,g,h=a,POLY,1,0
    while u!=1:
        require(u!=0,"independent noninvertible value")
        j=u.bit_length()-v.bit_length()
        if j<0:u,v=v,u;g,h=h,g;j=-j
        u^=v<<j;g^=h<<j
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
        require(p==q and x!=0,"independent equal-x input invalid")
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
            d=p[0]^q[0];ids.append(i);den.append(d);prefix.append(total);total=fmul(total,d)
    if ids:
        back=finv(total)
        for z in range(len(ids)-1,-1,-1):
            i=ids[z];q=other[i];assert p is not None and q is not None
            inv=fmul(back,prefix[z]);back=fmul(back,den[z]);slope=fmul(p[1]^q[1],inv)
            x=fsq(slope)^slope^p[0]^q[0]^1
            result[i]=(x,fmul(slope,p[0]^x)^x^p[1])
    return result
def code(p:Point)->int|None:return None if p is None else (p[0]<<BITS)|p[1]
def packed(p:Point)->int:return (1<<64)-1 if p is None else int(code(p))
def decode(value:Any)->Point:return None if value is None else (int(value[0]),int(value[1]))
def halftrace(c:int)->int:
    w=0;t=c
    for _ in range((BITS+1)//2):w^=t;t=fsq(fsq(t))
    return w
def lift_x(x:int)->Point:
    if x==0:return None
    ix=finv(x);c=x^1^fsq(ix);w=halftrace(c)
    if fsq(w)^w!=c:return None
    y=fmul(x,w);p=(x,min(y,y^x));require(oncurve(p),"independent halftrace point off curve");return p
def generator()->Point:
    for x in range(1,4096):
        p=lift_x(x)
        if p is None:continue
        g=add(p,p)
        if g is not None and times(g,R) is None:return g
    raise ValueError("independent generator scan exhausted")
def append_orbit(seed:Point,points:list[Point],seen:set[Point])->None:
    require(seed is not None and seed[0]!=0 and oncurve(seed) and times(seed,R) is None,"seed invalid")
    p=seed;own=set()
    for _ in range(BITS):
        for q in (p,negative(p)):
            require(q not in seen and q not in own,"signed orbit overlap")
            seen.add(q);own.add(q);points.append(q)
        p=frob(p)
    require(p==seed and len(own)==2*BITS,"seed orbit not full")
def base_from_recipe(recipe:dict)->tuple[list[Point],list[Point],list[int]]:
    points=[];seen=set();seeds=[];indices=[]
    if REGIME=="n19_k4":
        require(recipe["n"]==BITS and recipe["modulus"]==POLY and recipe["r"]==R,"n19 recipe parameters differ")
        seeds=[decode(row["point"]) for row in recipe["seed_points"]]
        require(all(p is not None for p in seeds) and sorted(p[0] for p in seeds)==recipe["plane_key"],"n19 seed plane mismatch")
        indices=[int(row["pool_orbit_index"]) for row in recipe["seed_points"]]
        for p in seeds:append_orbit(p,points,seen)
    else:
        labels=set()
        for index in range(4096):
            if len(seeds)==ORBITS:break
            x=int.from_bytes(hashlib.sha256(f"PAIR-REUSE-v1-base-n23-{index}".encode()).digest()[:8],"little")%FIELD
            p=lift_x(x)
            if p is None or times(p,R) is not None:continue
            q=p;label=p[0]
            for _ in range(1,BITS):q=frob(q);label=min(label,q[0])
            if label in labels:continue
            labels.add(label);seeds.append(p);indices.append(index);append_orbit(p,points,seen)
        require(len(seeds)==16,"independent n23 base recipe exhausted")
    points.sort()
    require(len(points)==BASE_POINTS and len(seen)==BASE_POINTS and len({p[0] for p in points})==BASE_POINTS//2,"base cardinality differs")
    require(all(negative(p) in seen and frob(p) in seen for p in points),"base closure differs")
    return points,seeds,indices
def normal_basis()->tuple[int,tuple[int,...],tuple[int,...]]:
    def rank(values):
        pivots={}
        for value in values:
            while value:
                bit=value.bit_length()-1
                if bit not in pivots:pivots[bit]=value;break
                value^=pivots[bit]
        return len(pivots)
    for beta in range(1,FIELD):
        columns=[];v=beta
        for _ in range(BITS):columns.append(v);v=fsq(v)
        if rank(columns)==BITS:break
    else:raise ValueError("normal basis absent")
    pivots={}
    for bit,column in enumerate(columns):
        row=column;mask=1<<bit
        while row:
            lead=row.bit_length()-1
            if lead not in pivots:pivots[lead]=(row,mask);break
            prior,prior_mask=pivots[lead];row^=prior;mask^=prior_mask
        else:raise ValueError("normal basis dependent")
    inverse=[]
    for bit in range(BITS):
        value=1<<bit;mask=0
        while value:
            row,part=pivots[value.bit_length()-1];value^=row;mask^=part
        inverse.append(mask)
    return beta,tuple(columns),tuple(inverse)
def to_normal(x:int,inverse:tuple[int,...])->int:
    out=0
    for bit in range(BITS):
        if x>>bit&1:out^=inverse[bit]
    return out
def rotate(mask:int,j:int)->int:return ((mask<<j)|(mask>>(BITS-j)))&MASK if j else mask
def canonical_x(p:Point,inverse:tuple[int,...])->tuple[int|None,int]:
    if p is None:return None,0
    start=to_normal(p[0],inverse);best=FIELD;which=0
    for j in range(BITS):
        value=rotate(start,j)
        if value<best:best,which=value,j
    return best,which
def inverse_transport(p:Point,j:int,sign:int)->Point:
    p=shift(p,(BITS-j)%BITS);return p if sign==1 else negative(p)
def direct_pairs(points:list[Point])->dict[int|None,tuple[Point,Point]]:
    out={}
    for i,p in enumerate(points):
        for j,total in enumerate(batched(p,points[i:]),i):out.setdefault(code(total),(p,points[j]))
    expected=11097 if REGIME=="n19_k4" else None
    if expected is not None:require(len(out)==expected,"n19 direct pair count differs")
    return out
def key_sha(keys)->str:
    raw=b"".join(((1<<64)-1 if key is None else key).to_bytes(8,"little") for key in sorted(keys,key=lambda x:(x is None,x or 0)))
    return hashlib.sha256(raw).hexdigest()
def point_order(p:Point)->tuple[int,int]:return ((1<<32)-1,0) if p is None else p
def expected_canonical(seeds:list[Point],inverse:tuple[int,...])->dict[int|None,tuple]:
    out={}
    for i in range(ORBITS):
        for k in range(i,ORBITS):
            for j in range(BITS):
                positive=shift(seeds[k],j)
                for sign,b in ((1,positive),(-1,negative(positive))):
                    total=add(seeds[i],b);key,frame=canonical_x(total,inverse)
                    a2,b2=sorted((shift(seeds[i],frame),shift(b,frame)),key=point_order)
                    s2=shift(total,frame)
                    row=(a2,b2,s2,i,k,j,sign,frame,1)
                    order=(*point_order(a2),*point_order(b2),*point_order(s2),i,k,j,sign)
                    prior=out.get(key)
                    if prior is None or order<prior[1]:out[key]=(row,order)
    return {key:item[0] for key,item in out.items()}
def read_canonical(block:dict,points:set[Point],inverse:tuple[int,...])->dict[int|None,tuple]:
    rows={}
    for row in block["rows"]:
        key=row["key"]["value"];a,b=map(decode,row["normalized_endpoints"]);total=decode(row["stored_sum"])
        require(a in points and b in points and add(a,b)==total,"canonical row not a base-pair sum")
        require(key==canonical_x(total,inverse)[0],"canonical row key differs")
        require(key not in rows,"duplicate canonical key")
        rows[key]=(a,b,total,row)
    require(block["stats"]["keys"]==len(rows) and block["stats"]["rows"]==len(rows),"canonical stats differ")
    return rows
def lookup(target:Point,rows:dict[int|None,tuple],inverse:tuple[int,...])->tuple[Point,Point]|None:
    key,j=canonical_x(target,inverse);entry=rows.get(key)
    if entry is None:return None
    a,b,total,_=entry;aligned=shift(target,j)
    if aligned==total:sign=1
    elif aligned==negative(total):sign=-1
    else:return None
    p=inverse_transport(a,j,sign);q=inverse_transport(b,j,sign)
    require(add(p,q)==target,"independent canonical transport fails")
    return p,q
def panels(base_generator:Point)->tuple[list[list[Point]],list[list[int]]]:
    qout=[];dout=[]
    for panel in range(8):
        seen=set();qs=[];ds=[];k=0
        while len(qs)<512:
            digest=hashlib.sha256(f"PAIR-REUSE-v1-target-{REGIME}-{panel}-{k}".encode()).digest();k+=1
            d=1+int.from_bytes(digest[:8],"little")%(R-1)
            if d in seen:continue
            seen.add(d);q=times(base_generator,d)
            require(q is not None and oncurve(q) and times(q,R) is None,"panel Q invalid")
            ds.append(d);qs.append(q)
        qout.append(qs);dout.append(ds)
    return qout,dout
def direct_query(q:Point,points:list[Point],pairs:dict)->tuple[bool,int,tuple|None]:
    for i,total in enumerate(batched(q,[negative(p) for p in points])):
        hit=pairs.get(code(total))
        if hit is None:continue
        witness=hit[0],hit[1],points[i]
        require(add(add(witness[0],witness[1]),witness[2])==q,"direct query replay failed")
        return True,i,witness
    return False,-1,None
def verify_answer(saved:dict,q:Point,truth:tuple,points:set[Point])->None:
    yes,index,witness=truth
    require(saved["status"] in ("SAT","UNSAT") and saved["status"]==("SAT" if yes else "UNSAT") and
            saved["third_index"]==index,"saved status/first hit differs")
    require(saved["probes"]==(index+1 if yes else BASE_POINTS),"saved probe count differs")
    if yes:
        require(isinstance(saved["witness"],list) and len(saved["witness"])==3,"SAT witness shape differs")
        got=tuple(decode(p) for p in saved["witness"])
        require(all(p in points for p in got) and got[2]==witness[2] and
                add(add(got[0],got[1]),got[2])==q,"saved witness invalid or third is not first hit")
    else:require(saved["witness"] is None,"UNSAT saved witness present")
def check_forgeries(points:list[Point],pairs:dict,rows:dict,inverse:tuple[int,...],g:Point,saved:dict)->dict:
    pointset=set(points);saved_target=decode(saved["target"])
    wrong=tuple(decode(p) for p in saved["wrong_inverse_endpoints"])
    flipped=tuple(decode(p) for p in saved["wrong_sign_endpoints"])
    require(saved_target is not None and len(wrong)==2 and len(flipped)==2 and
            all(p in pointset for p in (*wrong,*flipped)),"saved transport forgery shape/base membership differs")
    key,saved_shift=canonical_x(saved_target,inverse)
    genuine=rows[key];a,b,total,row=genuine;aligned=shift(saved_target,saved_shift)
    actual_sign=1 if aligned==total else -1
    expected_wrong=(inverse_transport(a,(saved_shift+1)%BITS,actual_sign),inverse_transport(b,(saved_shift+1)%BITS,actual_sign))
    expected_flipped=(inverse_transport(a,saved_shift,-actual_sign),inverse_transport(b,saved_shift,-actual_sign))
    require(saved["frame_shift"]==saved_shift and saved["frame_sign"]==actual_sign and wrong==expected_wrong and
            flipped==expected_flipped and add(*wrong)!=saved_target and add(*flipped)!=saved_target,
            "saved transport forgery bytes are not the declared false frame/sign transforms")
    require(saved["genuine_table_key"]==key and saved["wrong_table_key_value"]==(key^1) and
            saved["wrong_table_key_value"]!=canonical_x(total,inverse)[0],"saved wrong-key certificate is not false")
    wrong_sum=decode(saved["wrong_stored_sum_value"])
    require(wrong_sum==add(total,g) and (add(a,b)!=wrong_sum or canonical_x(wrong_sum,inverse)[0]!=key),
            "saved wrong-sum certificate is not false")
    offcurve=decode(saved["offcurve_Q"]);require(offcurve is not None and not oncurve(offcurve),"saved offcurve Q is on curve")
    require(all(saved[name] is True for name in ("wrong_inverse_shift_plus_one","wrong_sign","wrong_table_key",
            "wrong_stored_sum","offcurve_Q_rejected","one_point_removed_base","same_cardinality_noninvariant_base")),"saved forgery rejection flags incomplete")
    source=None
    for key in sorted(pairs,key=lambda x:(x is None,x or 0)):
        target=None if key is None else (key>>BITS,key&MASK)
        if target is None:continue
        hit=lookup(target,rows,inverse)
        if hit is None:continue
        key2,j=canonical_x(target,inverse);a,b,total,row=rows[key2]
        aligned=shift(target,j);sign=1 if aligned==total else -1
        wrong=(inverse_transport(a,(j+1)%BITS,sign),inverse_transport(b,(j+1)%BITS,sign))
        flipped=(inverse_transport(a,j,-sign),inverse_transport(b,j,-sign))
        if add(*wrong)!=target and add(*flipped)!=target:source=(target,key2,row);break
    require(source is not None,"independent shift/sign forgery unavailable")
    target,key,row=source
    bad_key=json.loads(json.dumps(row));bad_key["key"]["value"]=key^1
    bad_sum=json.loads(json.dumps(row));mutated=add(decode(row["stored_sum"]),g);bad_sum["stored_sum"]=None if mutated is None else list(mutated)
    def row_ok(x):
        try:
            a,b=map(decode,x["normalized_endpoints"]);s=decode(x["stored_sum"])
            return a in set(points) and b in set(points) and add(a,b)==s and x["key"]["value"]==canonical_x(s,inverse)[0]
        except Exception:return False
    require(not row_ok(bad_key) and not row_ok(bad_sum),"independent row forgery accepted")
    badq=g
    for bit in range(BITS):
        candidate=(g[0],g[1]^(1<<bit))
        if not oncurve(candidate):badq=candidate;break
    require(not oncurve(badq),"offcurve forgery unavailable")
    outside=next(times(g,d) for d in range(1,R) if times(g,d) is not None and times(g,d) not in set(points))
    require(decode(saved["replacement"])==outside,"saved noninvariant replacement differs from first valid outside-B point")
    replaced=points.copy();replaced[0]=outside
    def closed(values):
        s=set(values);return len(s)==BASE_POINTS and all(negative(p) in s and frob(p) in s for p in values)
    require(not closed(points[:-1]) and not closed(replaced),"base forgery accepted")
    return {"saved_target":list(saved_target),"wrong_inverse":True,"wrong_sign":True,"wrong_key":True,"wrong_sum":True,
            "offcurve":True,"missing_base_point":True,"same_cardinality_noninvariant":True}
def select_regime(doc:dict,regime:str)->dict:
    return next(item for item in doc["regimes"] if item["id"]==regime)
def check_regime(regime:str,recipe:dict,docs:dict)->dict:
    configure(regime);started=time.monotonic()
    points,seeds,indices=base_from_recipe(recipe);pointset=set(points);g=generator()
    beta,columns,inverse=normal_basis()
    saved_base=select_regime(docs["bases"],regime)
    require(saved_base["generator"]==list(g) and saved_base["candidate_indices"]==indices,"saved base generator/candidates differ")
    require([tuple(p) for p in saved_base["seeds"]]==seeds and [tuple(p) for p in saved_base["points"]]==points,"saved base differs")
    require(saved_base["normal"]["beta"]==beta and tuple(saved_base["normal"]["columns"])==columns and
            tuple(saved_base["normal"]["inverse_columns"])==inverse,"saved normal basis differs")
    pairs=direct_pairs(points);saved_tables=select_regime(docs["tables"],regime)
    require(saved_tables["expanded"]["stats"]["keys"]==len(pairs) and
            saved_tables["expanded"]["sorted_packed_keys_le64_sha256"]==key_sha(pairs),"expanded table hash/count differs")
    rows=read_canonical(saved_tables["canonical_normal_x"],pointset,inverse)
    expected=expected_canonical(seeds,inverse)
    require(set(rows)==set(expected),"canonical key set differs from anchored construction")
    for key,want in expected.items():
        got=rows[key];row=got[3]
        require(got[:3]==want[:3] and row["anchor"]==list(want[3:7]) and row["source_frame"]==list(want[7:9]),
                "canonical retained row is not first normalized lex row")
    expansion=set()
    for a,b,total,row in rows.values():
        p=total
        for _ in range(BITS):expansion.add(code(p));expansion.add(code(negative(p)));p=frob(p)
    require(expansion==set(pairs),"canonical expansion differs from complete pair support")
    for key in pairs:
        target=None if key is None else (key>>BITS,key&MASK);hit=lookup(target,rows,inverse)
        require(hit is not None and add(*hit)==target,"canonical misses expanded pair member")
    expected_panels,scalars=panels(g);saved_panels=select_regime(docs["panels"],regime)
    got_panels=[[decode(p) for p in panel] for panel in saved_panels["panels"]]
    require(got_panels==expected_panels,"Q-only panels differ from independent construction")
    panel_manifest=docs["panel_files"]
    entries={row["path"]:row["sha256"] for row in panel_manifest["files"]}
    require(len(entries)==16,"Q-only panel file manifest count differs")
    for panel in range(8):
        relative=f"panels/{regime}_panel_{panel}.json";path=run_path_global/relative
        require(entries.get(relative)==sha(path),"Q-only panel file hash differs")
        one=json.loads(path.read_text())
        require(one["regime"]==regime and one["panel"]==panel and
                [decode(p) for p in one["points"]]==expected_panels[panel],"Q-only panel file content differs")
    saved_oracle=select_regime(docs["oracle"],regime)
    require(saved_oracle["candidate_indices"]==indices and saved_oracle["panel_scalars"]==scalars,"oracle metadata differs")
    require(docs["oracle"]["public_panels_sha256"]==sha(docs["paths"]["panels"]) and
            docs["oracle"]["control_queries_sha256"]==sha(docs["paths"]["queries"]) and
            docs["oracle"]["panel_files_sha256"]==sha(docs["paths"]["panel_files"]) and
            set(docs["oracle"]["linked_status_sections"])=={"panels.status_first_hit_witness","exceptions.status_first_hit_witness","membership_probes.member_witness"},
            "oracle output/status hash binding differs")
    saved_queries=select_regime(docs["queries"],regime)
    checked=0;sat=0
    for panel in range(8):
        require(len(saved_queries["panels"][panel])==512,"saved panel query length differs")
        for index,q in enumerate(expected_panels[panel]):
            truth=direct_query(q,points,pairs);sat+=truth[0];row=saved_queries["panels"][panel][index]
            require(row["index"]==index and decode(row["Q"])==q,"saved panel query identity differs")
            verify_answer(row["expanded"],q,truth,pointset);verify_answer(row["canonical_normal_x"],q,truth,pointset);checked+=1
    exceptions=[None,*points]
    require(len(saved_queries["exceptions"])==len(exceptions),"exception count differs")
    for index,q in enumerate(exceptions):
        truth=direct_query(q,points,pairs);row=saved_queries["exceptions"][index]
        require(row["index"]==index and decode(row["Q"])==q,"exception identity differs")
        verify_answer(row["expanded"],q,truth,pointset);verify_answer(row["canonical_normal_x"],q,truth,pointset)
    require(len(saved_queries["membership_probes"])==4096,"membership probe count differs")
    member=0
    for k,row in enumerate(saved_queries["membership_probes"]):
        d=1+int.from_bytes(hashlib.sha256(f"PAIR-REUSE-v1-member-{REGIME}-{k}".encode()).digest()[:8],"little")%(R-1)
        q=times(g,d);truth=code(q) in pairs;member+=truth
        require(row["index"]==k and decode(row["Q"])==q and row["member"]==truth,"membership probe differs")
        hit=lookup(q,rows,inverse)
        require((hit is not None)==truth,"canonical membership probe differs")
        for name in ("expanded_witness","canonical_witness"):
            saved_pair=row[name]
            if truth:
                require(isinstance(saved_pair,list) and len(saved_pair)==2,"membership pair witness shape differs")
                pair=tuple(decode(p) for p in saved_pair)
                require(all(p in pointset for p in pair) and add(*pair)==q,"membership pair witness invalid")
            else:require(saved_pair is None,"nonmember carries pair witness")
    saved_control=select_regime(docs["control"],regime)
    forged=check_forgeries(points,pairs,rows,inverse,g,saved_control["forgeries"])
    require(saved_control["base_points"]==BASE_POINTS and saved_control["unordered_pairs"]==BASE_POINTS*(BASE_POINTS+1)//2 and
            saved_control["expanded_keys"]==len(pairs) and saved_control["canonical_keys"]==len(rows),"control counts differ")
    # Recompute the producer's frozen 4096-product and Euclidean-inverse streams.
    product_bytes=bytearray();inverse_bytes=bytearray()
    for k in range(4096):
        digest=hashlib.sha256(f"PAIR-REUSE-v1-field-{REGIME}-{k}".encode()).digest()
        a=int.from_bytes(digest[:4],"little")&MASK;b=int.from_bytes(digest[4:8],"little")&MASK
        nz=1+int.from_bytes(digest[:4],"little")%(FIELD-1)
        product_bytes+=fmul(a,b).to_bytes(4,"little");inverse_bytes+=finv(nz).to_bytes(4,"little")
    require(hashlib.sha256(product_bytes).hexdigest()==saved_control["field_products_u32le_sha256"] and
            hashlib.sha256(inverse_bytes).hexdigest()==saved_control["field_inverses_u32le_sha256"],
            "independent field product/inverse digest differs")
    cache=fsq.cache_info()
    return {"regime":regime,"base_points":BASE_POINTS,"unordered_pairs":BASE_POINTS*(BASE_POINTS+1)//2,
            "expanded_keys":len(pairs),"canonical_keys":len(rows),"panel_queries":checked,
            "panel_SAT":sat,"panel_UNSAT":checked-sat,"exceptions":len(exceptions),
            "membership_probes":4096,"membership_hits":member,"forgeries":forged,
            "normal_beta":beta,"validation_square_cache":{"configured_max_entries":1<<23,"actual_entries":cache.currsize,
            "hits":cache.hits,"misses":cache.misses,"scope":"checker validation only; never passed to native jobs"},
            "wall_seconds":time.monotonic()-started}
def run(base_path:Path,run_path:Path,out_path:Path)->dict:
    global run_path_global
    run_path_global=run_path
    started=time.monotonic();require(sha(base_path)==BASE_SHA,"frozen n19 base changed")
    files={"bases":"bases.json","panels":"public_panels.json","oracle":"oracle_metadata.json",
           "tables":"pair_tables.json","queries":"control_queries.json","control":"native_controls.json",
           "panel_files":"panel_files.json"}
    docs={key:json.loads((run_path/name).read_text()) for key,name in files.items()}
    docs["paths"]={key:run_path/name for key,name in files.items()}
    require(docs["control"]["status"]=="passed","native control status not passed")
    recipe=json.loads(base_path.read_text());results=[check_regime(r,recipe,docs) for r in ("n19_k4","n23_k16")]
    result={"schema":"crypto.autoresearch.pair_reuse_independent_replay.v1","status":"passed",
            "method":"independent Python unreduced polynomial product, long division, Euclidean inverse, group law and complete pair/query replay",
            "input_sha256":{"n19_base":sha(base_path),**{name:sha(run_path/file) for name,file in files.items()}},
            "regimes":results,"wall_seconds":time.monotonic()-started,
            "scope":"finite public synthetic validation only; no benchmark native call or security claim"}
    out_path.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n")
    return result
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--base",type=Path,required=True)
    p.add_argument("--run",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();result=run(a.base,a.run,a.output)
    print(json.dumps({"status":result["status"],"regimes":[r["regime"] for r in result["regimes"]]},sort_keys=True))
if __name__=="__main__":main()

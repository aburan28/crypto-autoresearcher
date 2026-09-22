#!/usr/bin/env python3
"""Stage-A native controls and preserved deterministic diagnostic traces."""
from __future__ import annotations
import argparse,hashlib,json,itertools,time
from pathlib import Path
import field
import circuits,checker

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"runs/RUN-KIC-c2b1b7"

def capture_attempt1()->None:
    _,columns=field.normal_basis();rows=[]
    for c in range(64):
        flats=field.candidate_flats(c,columns)
        if flats is None:
            rows.append({"index":c,"status":"DEGENERATE_FLAT"});continue
        xs,_,mappings=field.candidate_x(flats)
        admitted=sorted(x for x in xs if field.admitted_x(x))
        rows.append({"index":c,"status":"SCANNED","flats":[list(x) for x in flats],
                     "raw_x_count":len(xs),"raw_x_values":sorted(xs),
                     "admitted_x_count":len(admitted),"admitted_x_values":admitted,
                     "raw_mapping_count":len(mappings),
                     "raw_orbit_representatives":sorted({min(field.x_orbit(x)) for x in xs}),
                     "admitted_orbit_representatives":sorted({min(field.x_orbit(x)) for x in admitted})})
    path=RUN/"preserved_pool_scan_attempt1/scan.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        raise RuntimeError("preserved attempt-1 scan is immutable")
    record={"schema":"crypto.autoresearch.pool_scan_diagnostic.v1","classification":"implementation_filter_error",
            "source_sha256":"73b8447b2a3bce6f8498b4ed5381af44d6111715496bcacf0fa82014ea9c1bc9",
            "method":"Original implementation incorrectly required every raw union x to pass admission before evaluating the retained set.",
            "rows":rows,"solver_or_target_workers":0}
    path.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"rows":len(rows),"scan_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                      "raw_nonmultiple_example":next((r["index"] for r in rows if r.get("raw_x_count")==29),None)},sort_keys=True))

def oracle_mul(a:int,b:int)->int:
    product=0
    for bit in range(7):
        if b>>bit&1:product^=a<<bit
    for bit in range(product.bit_length()-1,6,-1):
        if product>>bit&1:product^=0x83<<(bit-7)
    return product

def native_field_and_group()->dict:
    count=0
    for a in range(128):
        assert field.sq(a)==oracle_mul(a,a)
        for b in range(128):
            assert field.mul(a,b)==oracle_mul(a,b)==checker._mul(a,b)
            count+=1
    for a in range(1,128):assert oracle_mul(a,field.inv(a))==1
    points=field.points();subgroup=field.subgroup_points();g=field.generator()
    assert len(points)==142 and len(subgroup)==71 and g==(3,85)
    assert field.scalar_mul(g,71) is None and field.scalar_mul(g,1)==g
    for p in points:
        assert field.on_curve(p) and field.add(p,field.neg(p)) is None
        assert field.on_curve(field.frob(p))
        q=p
        for _ in range(7):q=field.frob(q)
        assert q==p
    for p in subgroup:assert field.scalar_mul(p,71) is None
    for p in points:
        for q in points:
            z=field.add(p,q)
            assert field.on_curve(z) and field.add(q,p)==z and checker._add(p,q)==z
    for p in subgroup:
        for q in subgroup:
            assert field.add(p,q) in subgroup
    beta,columns=field.normal_basis();assert beta==9 and field.binary_rank(columns)==7
    for a in range(128):
        mask=field.poly_to_normal(a,columns)
        assert field.normal_to_poly(mask,columns)==a
        successor=((mask<<1)|(mask>>6))&127
        assert field.poly_to_normal(field.sq(a),columns)==successor
    return {"field_products":count,"squares":128,"inverse_identities":127,"curve_points":len(points),"subgroup_points":len(subgroup),"generator":list(g),"normal_beta":beta,"normal_columns":list(columns)}

def circuit_gate_controls(base:dict)->dict:
    # Atomic AND, XOR and mux truth tables.
    for va,vb in itertools.product((False,True),repeat=2):
        c=circuits.Circuit();a=c.bits("a",1)[0];b=c.bits("b",1)[0]
        z=c.and_(a,b);w=c.xor2(a,b)
        assignment=circuits.complete_assignment(c,{a:va,b:vb})
        assert assignment[z]==(va and vb) and assignment[w]==(va!=vb)
        assert circuits.evaluate(c,assignment)
    for selector,va,vb in itertools.product((False,True),repeat=3):
        c=circuits.Circuit();s=c.bits("s",1)[0];a=c.bits("a",1)[0];b=c.bits("b",1)[0]
        out=c.mux(s,a,b);assignment=circuits.complete_assignment(c,{s:selector,a:va,b:vb})
        actual=assignment[abs(out)] if out>0 else not assignment[abs(out)]
        assert actual==(vb if selector else va)
        assert circuits.evaluate(c,assignment)
    c=circuits.Circuit();a=c.bits("a");b=c.bits("b");c.leq(a,b)
    for va in range(128):
        for vb in range(128):
            given={lit:bool(va>>i&1) for i,lit in enumerate(a)}
            given.update({lit:bool(vb>>i&1) for i,lit in enumerate(b)})
            assignment=circuits.complete_assignment(c,given)
            assert circuits.evaluate(c,assignment)==(va<=vb)
    # All 64 structured selectors, including j=7 and duplicate/nonadmitted.
    c=circuits.Circuit();x=c.bits("x");sel=c.structured_domain(x,base,"s")
    assert len(base["all_mappings"])==64
    for mapping in base["all_mappings"]:
        t,j,u,v=mapping["selector"]
        given={sel["t"][0]:bool(t),sel["u"][0]:bool(u),sel["v"][0]:bool(v)}
        given.update({lit:bool(j>>k&1) for k,lit in enumerate(sel["j"])})
        value=mapping["x"] or 0
        given.update({lit:bool(value>>k&1) for k,lit in enumerate(x)})
        assignment=circuits.complete_assignment(c,given)
        assert circuits.evaluate(c,assignment)==mapping["valid"]
        if mapping["valid"]:
            assert value in base["x_values"]
            wrong=dict(given);wrong[x[0]]=not wrong[x[0]]
            assert not circuits.evaluate(c,circuits.complete_assignment(c,wrong))
    explicit=circuits.Circuit();x=explicit.bits("x");idx=explicit.explicit_domain(x,base["x_values"],"idx")
    assert len(idx)==4
    for value in range(16):
        xvalue=base["x_values"][value] if value<14 else 0
        given={lit:bool(value>>k&1) for k,lit in enumerate(idx)}
        given.update({lit:bool(xvalue>>k&1) for k,lit in enumerate(x)})
        assignment=circuits.complete_assignment(explicit,given)
        assert circuits.evaluate(explicit,assignment)==(value<14)
    # CMS native-XOR row encoding and the empty-parity edge cases.
    c=circuits.Circuit();x=c.bits("x",2);c.xor_row(x,1);c.xor_row(x,0)
    lines=c.dimacs().splitlines();assert f"x {x[0]} {x[1]} 0" in lines
    assert f"x -{x[0]} {x[1]} 0" in lines
    prior=len(c.xors);c.xor_row([],0);assert len(c.xors)==prior
    c.xor_row([],1);assert [] in c.clauses
    duplicate=circuits.Circuit();a=duplicate.bits("a",1)[0]
    duplicate.clause([a,a]);assert duplicate.clauses[-1]==[a]
    before=len(duplicate.clauses);duplicate.clause([a,-a]);assert len(duplicate.clauses)==before
    assert circuits.propagate(duplicate,{})["contradiction"] is False
    def bit_value(assignment:dict[int,bool],literal:int)->bool:
        return assignment[abs(literal)] if literal>0 else not assignment[abs(literal)]
    mul_c=circuits.Circuit();aa=mul_c.bits("a");bb=mul_c.bits("b");product=mul_c.fmul(aa,bb)
    for va in range(128):
        for vb in range(128):
            given={lit:bool(va>>i&1) for i,lit in enumerate(aa)}
            given.update({lit:bool(vb>>i&1) for i,lit in enumerate(bb)})
            assignment=circuits.complete_assignment(mul_c,given)
            actual=sum(1<<i for i,lit in enumerate(product) if bit_value(assignment,lit))
            assert actual==oracle_mul(va,vb) and circuits.evaluate(mul_c,assignment)
    sq_c=circuits.Circuit();aa=sq_c.bits("a");squared=sq_c.fsquare(aa)
    for va in range(128):
        assignment=circuits.complete_assignment(sq_c,{lit:bool(va>>i&1) for i,lit in enumerate(aa)})
        actual=sum(1<<i for i,lit in enumerate(squared) if bit_value(assignment,lit))
        assert actual==oracle_mul(va,va) and circuits.evaluate(sq_c,assignment)
    s3_c=circuits.Circuit();aa=s3_c.bits("a");bb=s3_c.bits("b");cc=s3_c.bits("c");output=s3_c.s3(aa,bb,cc)
    for index in range(256):
        values=[field.hash_mask(f"GFB-SAT-N7-v1-S3-unit-{index:03d}-{name}") for name in "abc"]
        given={lit:bool(values[0]>>i&1) for i,lit in enumerate(aa)}
        given.update({lit:bool(values[1]>>i&1) for i,lit in enumerate(bb)})
        given.update({lit:bool(values[2]>>i&1) for i,lit in enumerate(cc)})
        assignment=circuits.complete_assignment(s3_c,given)
        actual=sum(1<<i for i,lit in enumerate(output) if bit_value(assignment,lit))
        assert actual==circuits.s3(*values) and circuits.evaluate(s3_c,assignment)
    return {"and_cases":4,"xor_cases":4,"mux_cases":8,"order_cases":16384,"flat_selector_cases":64,"explicit_index_cases":16,"field_circuit_products":16384,"field_circuit_squares":128,"s3_composite_cases":256,"duplicate_clause_unit":"passed","tautology_omission":"passed","cms_xor_rhs_convention":"rhs1 positive literals; rhs0 first literal negated; empty even omitted; empty odd empty CNF"}

def exact_triple_truth(base:dict)->dict[tuple[int,int],set[tuple[int,int,int]]]:
    points=tuple(tuple(p) for p in base["points"])
    result={}
    for p,q,r in itertools.product(points,repeat=3):
        xs=tuple(sorted((p[0],q[0],r[0])))
        result.setdefault(field.add(field.add(p,q),r),set()).add(xs)
    return result

def relation_equivalence(candidate:dict,null:dict,deadline:float)->dict:
    g=field.generator();records=[]
    for name,base in (("candidate",candidate),("null",null)):
        xs=base["x_values"];truth=exact_triple_truth(base)
        triples=list(itertools.combinations_with_replacement(xs,3))
        first={(x1,x2):[t for t in range(128) if circuits.s3(x1,x2,t)==0]
               for x1,x2 in itertools.combinations_with_replacement(xs,2)}
        mismatches=[];checked=0;mitm_checks=0
        for d in range(1,71):
            q=field.scalar_mul(g,d);assert q is not None
            mitm=field.direct_mitm(q,tuple(tuple(p) for p in base["points"]))
            assert (mitm is not None)==(q in truth)
            if mitm:assert checker.check_witness(q,base,[list(p) for p in mitm])
            mitm_checks+=1
            if q in tuple(tuple(p) for p in base["points"]):
                assert q in truth # charged shortcut has exact group witness
                continue
            group=truth.get(q,set())
            for x1,x2,x3 in triples:
                predicted=any(circuits.s3(t,x3,q[0])==0 for t in first[x1,x2])
                actual=(x1,x2,x3) in group;checked+=1
                if predicted!=actual:mismatches.append([d,x1,x2,x3,predicted,actual])
            if time.monotonic()>deadline:raise TimeoutError("native relation control exceeded 480s watchdog")
        records.append({"base":name,"ordered_x_triples":len(triples),"field_vs_group_checks":checked,"direct_mitm_vs_oracle_checks":mitm_checks,"discrepancies":mismatches})
    return {"records":records,"all_equal":all(not row["discrepancies"] for row in records)}

def run_native()->None:
    start=time.monotonic();deadline=start+480
    field_record=native_field_and_group()
    candidate=field.select_candidate();null=field.select_null(candidate["orbit_representatives"])
    assert candidate["candidate_index"]==0 and len(candidate["x_values"])==14 and len(candidate["points"])==28
    assert null["arrival_index"]==15 and len(null["x_values"])==14 and len(null["points"])==28
    assert len(candidate["all_mappings"])==64 and sum(m["valid"] for m in candidate["all_mappings"])==14
    gate=circuit_gate_controls(candidate)
    assert checker.assignment_from_cms("v 1 -2 0\n",2)=={1:True,2:False}
    for bad in ("v 1 -1 2 0\n","v 1 2 3 0\n","v 1 0\n"):
        try:checker.assignment_from_cms(bad,2)
        except ValueError:pass
        else:raise AssertionError("malformed CMS assignment accepted")
    relations=relation_equivalence(candidate,null,deadline)
    assert relations["all_equal"],"relation circuit and exact triples differ"
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/"basis_manifest.json").write_text(json.dumps({"schema":"crypto.autoresearch.gfb_basis_manifest.v1","candidate":candidate,"null":null,"field":field_record},sort_keys=True,indent=2)+"\n")
    record={"schema":"crypto.autoresearch.gfb_native_controls.v1","status":"passed","field_and_group":field_record,"circuit_gates":gate,"cms_model_parser_negative_cases":3,"independent_checker_arithmetic":"all 16384 field products and all 142x142 point additions matched producer encoding","relation_equivalence":relations,"wall_seconds":time.monotonic()-start,"solver_instances":0,"target_workers":0}
    (RUN/"native_controls.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"passed","field_products":field_record["field_products"],"relation_checks":sum(x["field_vs_group_checks"] for x in relations["records"]),"wall_seconds":record["wall_seconds"]},sort_keys=True))

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--capture-attempt1",action="store_true");p.add_argument("--native",action="store_true");a=p.parse_args()
    if a.capture_attempt1:capture_attempt1();return
    if a.native:run_native();return
    raise SystemExit("select --native for Stage-A native controls")
if __name__=="__main__":main()

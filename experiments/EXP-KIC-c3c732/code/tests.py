#!/usr/bin/env python3
"""One admitted native-control driver: Python rows/domains plus one C++ child."""
from __future__ import annotations
import argparse,hashlib,itertools,json,time,traceback
from pathlib import Path
import field,circuits,checker,worker

def require(value:bool,why:str)->None:
    if not value:raise AssertionError(why)
def digest(label:str)->bytes:return hashlib.sha256(label.encode()).digest()
def sample_field(k:int)->tuple[int,int]:
    h=digest(f"N19-AFFINE-SAT-v1-field-{k}")
    return int.from_bytes(h[:4],"little")&field.MASK,int.from_bytes(h[4:8],"little")&field.MASK
def value(form:circuits.Form,assignment:dict[int,bool])->bool:
    return bool(form[1]^(sum(assignment[v] for v in form[0])%2))
def expect_reject(action,reason:str)->None:
    try:action()
    except (ValueError,AssertionError):return
    raise AssertionError(f"forged {reason} accepted by actual verifier")
def input_bits(variables:list[int],value:int)->dict[int,bool]:
    return {variable:bool(value>>index&1) for index,variable in enumerate(variables)}
def choose_selector(base:dict,x:int)->tuple[int,int,int]:
    a,b,c=base["plane_normal"];columns=base["normal_columns"]
    for j in range(19):
        for u in (0,1):
            for v in (0,1):
                raw=field.normal_to_poly(a^(b if u else 0)^(c if v else 0),columns)
                for _ in range(j):raw=field.sq(raw)
                if raw==x:return j,u,v
    raise ValueError("admitted x absent from 76 flat selectors")
def assignment_for(c:circuits.Circuit,base:dict,xs:tuple[int,int,int],t:int,arm:str)->dict[int,bool]:
    given={}
    for name,value in zip(("x1","x2","x3","t"),(*xs,t)):
        given.update(input_bits(c.inputs[name],value))
    for k,x in enumerate(xs,1):
        domain=c.domain[f"d{k}"]
        if arm=="explicit_onehot":
            slot=base["x_values"].index(x)
            given.update({variable:index==slot for index,variable in enumerate(domain["selectors"])})
        else:
            j,u,v=choose_selector(base,x)
            if arm=="flat_onehot":
                given.update({variable:index==j for index,variable in enumerate(domain["shifts"])})
            else:given.update(input_bits(domain["shift_bits"],j))
            given[domain["u"][0]]=bool(u);given[domain["v"][0]]=bool(v)
    return circuits.complete_assignment(c,given)
def gate_controls()->dict:
    for av,bv in itertools.product((False,True),repeat=2):
        c=circuits.Circuit();a=c.bits("a",1)[0];b=c.bits("b",1)[0]
        z=c.and_(a,b);x=c.xor2(a,b)
        assigned=circuits.complete_assignment(c,{a:av,b:bv})
        require(circuits.lit_value(z,assigned)==(av and bv),"AND truth table")
        require(circuits.lit_value(x,assigned)==(av!=bv),"XOR truth table")
        require(circuits.evaluate(c,assigned),"AND/XOR original rows")
    for selector,av,bv in itertools.product((False,True),repeat=3):
        c=circuits.Circuit();s=c.bits("s",1)[0];a=c.bits("a",1)[0];b=c.bits("b",1)[0]
        out=c.mux(s,a,b)
        assigned=circuits.complete_assignment(c,{s:selector,a:av,b:bv})
        require(circuits.lit_value(out,assigned)==(bv if selector else av),"mux truth table")
        require(circuits.evaluate(c,assigned),"mux original rows")
    for selector in (False,True):
        c=circuits.Circuit();literal=c.bits("literal",1)[0];s=c.bits("s",1)[0]
        for choices in ((True,literal),(literal,True),(False,-literal),(-literal,False)):
            out=c.mux(s,*choices)
            for truth in (False,True):
                assigned=circuits.complete_assignment(c,{s:selector,literal:truth})
                expected=circuits.lit_value(choices[1] if selector else choices[0],assigned)
                require(circuits.lit_value(out,assigned)==expected,
                        "mixed bool/literal mux identity collapse")
                require(circuits.evaluate(c,assigned),"mixed bool/literal mux rows")
    return {"and":4,"xor":4,"mux":8,"mixed_constant_literal_mux":16}
def parser_controls()->dict:
    require(checker.parse_cms("s INDETERMINATE\n",15,2)==("UNKNOWN",None),
            "frozen CMS exit15 UNKNOWN parser control")
    require(checker.parse_cms("s SATISFIABLE\nv 1 -2 0\n",10,2)==
            ("SAT",{1:True,2:False}),"complete SAT model parser control")
    require(checker.parse_cms("s UNSATISFIABLE\n",20,2)==("UNSAT",None),
            "UNSAT parser control")
    bad=(("s INDETERMINATE\n",0),("s UNSATISFIABLE\n",10),
         ("s SATISFIABLE\nv 1 0\n",10),
         ("s SATISFIABLE\nv 1 -1 -2 0\n",10),
         ("s SATISFIABLE\nv 1 -2 3 0\n",10),
         ("s INDETERMINATE\nv 1 0\n",15))
    for stdout,code in bad:
        expect_reject(lambda stdout=stdout,code=code:checker.parse_cms(stdout,code,2),
                      "malformed CMS status/model fixture")
    return {"valid_status_fixtures":3,"rejected_status_model_fixtures":len(bad),
            "UNKNOWN_exit_code":15,"UNKNOWN_stdout":"s INDETERMINATE"}
def arithmetic_controls()->dict:
    c=circuits.Circuit();a=c.fbits("a");b=c.fbits("b");p=c.fmul(a,b)
    out=c.fbits("out");c.equal_field(p,out)
    sqc=circuits.Circuit();sqa=sqc.fbits("a");squared=sqc.fsquare(sqa)
    sqout=sqc.fbits("out");sqc.equal_field(squared,sqout)
    for k in range(4096):
        x,y=sample_field(k);product=checker.fmul(x,y)
        given={**input_bits(c.inputs["a"],x),**input_bits(c.inputs["b"],y),
               **input_bits(c.inputs["out"],product)}
        assigned=circuits.complete_assignment(c,given)
        require(circuits.evaluate(c,assigned),"sampled multiplication rows")
        require(field.mul(x,y)==product,"independent sampled multiplication")
        image=checker.fsq(x)
        assigned=circuits.complete_assignment(sqc,
            {**input_bits(sqc.inputs["a"],x),**input_bits(sqc.inputs["out"],image)})
        require(circuits.evaluate(sqc,assigned),"sampled square rows")
        require(field.sq(x)==image,"independent sampled square")
    for i in range(19):
        for j in range(19):
            require(field.mul(1<<i,1<<j)==checker.fmul(1<<i,1<<j),
                    "basis monomial product")
    return {"sampled_field_equations":4096,"sampled_square_equations":4096,
            "basis_products":361}
def domain_controls(base:dict)->dict:
    xs=base["x_values"]
    assert len(xs)==76
    positive=0;two_hot=0
    explicit=circuits.Circuit();ex=explicit.fbits("x")
    explicit.explicit_domain(ex,xs,"d")
    selectors=explicit.domain["d"]["selectors"]
    for k,x in enumerate(xs):
        given=input_bits(explicit.inputs["x"],x)
        given.update({v:i==k for i,v in enumerate(selectors)})
        require(circuits.evaluate(explicit,circuits.complete_assignment(explicit,given)),
                "legal explicit selector rejected")
        positive+=1
    for i,j in itertools.combinations(range(76),2):
        given=input_bits(explicit.inputs["x"],xs[i])
        given.update({v:k in (i,j) for k,v in enumerate(selectors)})
        require(not circuits.evaluate(explicit,circuits.complete_assignment(explicit,given)),
                "two-hot explicit selector accepted")
        two_hot+=1
    zero={**input_bits(explicit.inputs["x"],xs[0]),**{v:False for v in selectors}}
    require(not circuits.evaluate(explicit,circuits.complete_assignment(explicit,zero)),
            "zero-hot explicit selector accepted")
    flat=circuits.Circuit();fx=flat.fbits("x")
    flat.flat_onehot(fx,base["plane_normal"],base["normal_columns"],"d")
    fsel=flat.domain["d"]["shifts"];fu=flat.domain["d"]["u"][0];fv=flat.domain["d"]["v"][0]
    legal=set()
    for j,u,v in itertools.product(range(19),(0,1),(0,1)):
        raw=field.normal_to_poly(base["plane_normal"][0]^
            (base["plane_normal"][1] if u else 0)^
            (base["plane_normal"][2] if v else 0),base["normal_columns"])
        for _ in range(j):raw=field.sq(raw)
        legal.add(raw)
        given=input_bits(flat.inputs["x"],raw)
        given.update({bit:k==j for k,bit in enumerate(fsel)})
        given.update({fu:bool(u),fv:bool(v)})
        require(circuits.evaluate(flat,circuits.complete_assignment(flat,given)),
                "legal flat onehot selector rejected")
    require(legal==set(xs),"flat onehot maps to wrong 76-point domain")
    for i,j in itertools.combinations(range(19),2):
        given=input_bits(flat.inputs["x"],xs[0])
        given.update({bit:k in (i,j) for k,bit in enumerate(fsel)})
        given.update({fu:False,fv:False})
        require(not circuits.evaluate(flat,circuits.complete_assignment(flat,given)),
                "two-hot shift selector accepted")
    given=input_bits(flat.inputs["x"],xs[0])
    given.update({bit:False for bit in fsel});given.update({fu:False,fv:False})
    require(not circuits.evaluate(flat,circuits.complete_assignment(flat,given)),
            "zero-hot shift selector accepted")
    binary=circuits.Circuit();bx=binary.fbits("x")
    binary.flat_binary(bx,base["plane_normal"],base["normal_columns"],"d")
    bsel=binary.domain["d"]["shift_bits"];bu=binary.domain["d"]["u"][0];bv=binary.domain["d"]["v"][0]
    valid=invalid=0;images=set()
    for j,u,v in itertools.product(range(32),(0,1),(0,1)):
        raw=field.normal_to_poly(base["plane_normal"][0]^
            (base["plane_normal"][1] if u else 0)^
            (base["plane_normal"][2] if v else 0),base["normal_columns"])
        for _ in range(j%19):raw=field.sq(raw)
        given=input_bits(binary.inputs["x"],raw if j<19 else 0)
        given.update(input_bits(bsel,j));given.update({bu:bool(u),bv:bool(v)})
        accepted=circuits.evaluate(binary,circuits.complete_assignment(binary,given))
        if j<19:
            require(accepted,"legal binary shift rejected")
            images.add(raw);valid+=1
        else:
            require(not accepted,"forbidden binary shift accepted")
            invalid+=1
    require(valid==76 and invalid==52 and images==set(xs),"binary domain coverage mismatch")
    return {"explicit_legal":positive,"explicit_two_hot_rejected":two_hot,
            "flat_onehot_legal":76,"flat_onehot_two_hot_rejected":171,
            "binary_legal":valid,"binary_invalid":invalid}
def relation_and_forgery_controls(base:dict,cases:list[dict])->dict:
    sat_case=next(row for row in cases if row["stratum"]=="SAT")
    q=tuple(sat_case["Q"])
    witness=checker.independent_oracle(q,{"points":[list(p) for p in base["points"]]})
    require(witness is not None,"frozen SAT case has no independent witness")
    ordered=tuple(sorted(witness,key=lambda p:p[0]))
    t=checker.plus(ordered[0],ordered[1])
    require(t is not None,"nonshortcutted SAT witness has infinity intermediate")
    counts={}
    reference=None
    for arm in ("explicit_onehot","flat_onehot","flat_binary"):
        c=circuits.Circuit();c.relation(base,q,arm)
        assigned=assignment_for(c,base,tuple(p[0] for p in ordered),t[0],arm)
        require(circuits.evaluate(c,assigned),f"{arm} real S3 model fails original rows")
        decoded=checker.decode_sat(c,assigned,q,{"points":[list(p) for p in base["points"]],
                                                   "x_values":base["x_values"]})
        checker.verify_witness(q,{"points":[list(p) for p in base["points"]]},[list(p) for p in decoded])
        counts[arm]={"nvars":c.nvars,"cnf":len(c.clauses),"xor":len(c.xors)}
        if arm=="explicit_onehot":reference=(c,assigned,decoded)
    assert reference is not None
    c,assignment,decoded=reference
    mutated=assignment.copy();var=c.inputs["x1"][0];mutated[var]=not mutated[var]
    expect_reject(lambda:checker.decode_sat(c,mutated,q,
                  {"points":[list(p) for p in base["points"]],"x_values":base["x_values"]}),
                  "original-row bit")
    missing=assignment.copy();missing.pop(c.nvars)
    expect_reject(lambda:checker.decode_sat(c,missing,q,
                  {"points":[list(p) for p in base["points"]],"x_values":base["x_values"]}),
                  "missing last variable")
    changed_q=tuple(cases[1]["Q"])
    expect_reject(lambda:checker.decode_sat(c,assignment,changed_q,
                  {"points":[list(p) for p in base["points"]],"x_values":base["x_values"]}),
                  "changed Q")
    bad=[list(p) for p in decoded];bad[0]=[0,0]
    expect_reject(lambda:checker.verify_witness(q,{"points":[list(p) for p in base["points"]]},bad),
                  "nonbase witness")
    wrong=[list(p) for p in decoded];wrong[2]=list(field.neg(decoded[2]))
    expect_reject(lambda:checker.verify_witness(q,{"points":[list(p) for p in base["points"]]},wrong),
                  "wrong group sum")
    result={"Q":list(q),"case_id":str(sat_case["case_id"]),"arm":"explicit_onehot",
            "status":"SAT","witness":[list(p) for p in decoded]}
    expect_reject(lambda:checker.replay_result(result,q,
                  {"points":[list(p) for p in base["points"]]},"SAT",
                  str(cases[1]["case_id"]),"explicit_onehot"),"swapped case label")
    return {"real_S3_models":counts,"forgeries_rejected":
            ["original_row_bit","missing_last_variable","changed_Q","nonbase_point",
             "wrong_group_sum","swapped_case_label"]}
def run(base_path:Path,cases_path:Path,native_path:Path,out:Path)->dict:
    started=time.monotonic()
    recipe=json.loads(base_path.read_text());cases=json.loads(cases_path.read_text())["cases"]
    base=field.construct_base(recipe)
    columns=base["normal_columns"]
    for bit in range(19):
        basis_vector=1<<bit
        require(field.normal_to_poly(field.poly_to_normal(basis_vector,columns),columns)==basis_vector,
                "nineteen-vector normal/poly conversion mismatch")
    gates=gate_controls();parser=parser_controls()
    arithmetic=arithmetic_controls();domain=domain_controls(base)
    relation=relation_and_forgery_controls(base,cases)
    child=worker.child_run([str(native_path),"--controls",str(base_path),
                            str(cases_path),str(out/"native_controls.json")],out,"native_controls")
    require(child["exit_code"]==0 and not child["sampling"]["cap_reached"],
            "native control child failed or hit memory cap")
    native=json.loads((out/"native_controls.json").read_text())
    require(native["status"]=="passed" and native["field_products"]==4457 and
            native["group_batches"]==4096 and len(native["case_oracle"])==8,
            "native math/control counts mismatch")
    for row,oracle in zip(cases,native["case_oracle"]):
        require(oracle["case_id"]==row["case_id"] and oracle["status"]==row["stratum"],
                "native independent case oracle differs from frozen stratum")
    result={"schema":"crypto.autoresearch.n19_affine_sat_control_driver.v1",
            "status":"passed","gates":gates,"solver_parser":parser,
            "arithmetic":arithmetic,"domain":domain,
            "relation_and_forgery":relation,"native_control_child":child,
            "native_result_sha256":worker.sha(out/"native_controls.json"),
            "wall_seconds":time.monotonic()-started,
            "native_children":1,"CMS_instances":0}
    (out/"controls.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result
def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--cases",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        result=run(args.base,args.cases,args.native,args.out)
        print(json.dumps({"status":result["status"],"native_children":1},sort_keys=True))
    except Exception:
        (args.out/"driver_failure.json").write_text(json.dumps({"status":"FAILED_IMPLEMENTATION",
            "traceback":traceback.format_exc()},sort_keys=True,indent=2)+"\n")
        raise
if __name__=="__main__":main()

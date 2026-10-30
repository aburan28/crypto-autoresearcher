#!/usr/bin/env python3
"""Prospective all-target point-decomposition validation of the fixed SAT loop.

This additive experiment leaves the original residual suite untouched. Curves
and all target x-coordinates are chosen from public inputs before solving.
"""
import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/"tools")]
from geometry.geometry import select_curve, projective_add
from sat.solver import run as run_sat, verify as verify_sat, finite_points
from core import generate_s3


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")
    tmp.replace(path)


def independent_lift(curve,metadata,bits):
    p,a,b=curve["p"],curve["a"],curve["b"]
    s=metadata["s"]
    x,y=bits & ((1<<s)-1),bits>>s
    points=finite_points(p,a,b)
    target=next((P for P in points if P[0]==metadata["target"]),None)
    if target is None:
        return False
    # Independent Jacobian group implementation, compared with the affine
    # producer's lift/sign witness. All sign choices, equal-x and inverse
    # cases are retained; infinity never equals the finite target.
    for P in points:
        if P[0]!=x:
            continue
        for Q in points:
            if Q[0]==y:
                X,Y,Z=projective_add((*P,1),(*Q,1),p,a)
                if Z and (X-target[0]*Z*Z)%p==0 and (Y-target[1]*Z*Z*Z)%p==0:
                    return True
    return False


def group_pair_oracle(curve,s):
    """Complete group oracle, independent of S3 and candidate solver answers."""
    p,a,b=curve["p"],curve["a"],curve["b"]
    points=finite_points(p,a,b)
    base=[P for P in points if P[0] < (1<<s)]
    targets={x:next(P for P in points if P[0]==x) for x in sorted({P[0] for P in points})}
    models={x:set() for x in targets}
    for P in base:
        for Q in base:
            X,Y,Z=projective_add((*P,1),(*Q,1),p,a)
            if Z==0:
                continue
            iz=pow(Z,-1,p)
            target=(X*iz*iz%p,Y*iz*iz*iz%p)
            if targets.get(target[0])==target:
                models[target[0]].add(P[0] | (Q[0]<<s))
    return {"digit_bits":s,"factor_base_points":len(base),
            "factor_base_distinct_x":len({P[0] for P in base}),
            "domain_eligibility_at_least_two_x":len({P[0] for P in base})>=2,
            "ordered_point_pairs_checked":len(base)**2,
            "models_by_target":{str(x):sorted(v) for x,v in models.items()}}


def check(path):
    import artifact_store
    data=artifact_store.read_json(path)
    cfg=data["config"]
    frozen=ROOT/"experiments"/cfg["experiment_id"]/"config.json"
    if sha(frozen)!=data["config_sha256"] or json.loads(frozen.read_text())!=cfg:
        raise ValueError("frozen input mismatch")
    if [c["p"] for c in data["curve_packages"]]!=cfg["primes"]:
        raise ValueError("curve inventory mismatch")
    counts={"curves":0,"sat_cells":0,"actual_pdp_sat_models":0,
            "actual_pdp_unsat_cells":0,"residual_sat_without_lift":0}
    for package in data["curve_packages"]:
        if package["status"]!="completed":
            raise ValueError("incomplete curve package")
        expected_curve=select_curve(package["p"],cfg["maximum_curve_candidates"])
        # JSON normalizes tuple/list shapes before comparing records.
        expected_curve=json.loads(json.dumps(expected_curve))
        if expected_curve!=package["curve"]:
            raise ValueError("public curve selector mismatch")
        c=package["curve"]
        points=finite_points(c["p"],c["a"],c["b"])
        targets=sorted({P[0] for P in points})
        if package["targets"]!=targets or not targets:
            raise ValueError("all-target coverage mismatch")
        expected_cfg={"primes":[c["p"]],"digits":cfg["digits"],"targets":targets,
                      "curve":{"a":c["a"],"b":c["b"]},
                      "degree_cap":cfg["degree_cap"],"row_cap":cfg["row_cap"]}
        payload=package["sat_payload"]
        if payload["config"]!=expected_cfg or not verify_sat(payload):
            raise ValueError("SAT certificate, control or coverage mismatch")
        group_oracles=[group_pair_oracle(c,s) for s in cfg["digits"]]
        if package["group_oracles"]!=group_oracles:
            raise ValueError("complete group oracle mismatch")
        oracle_by_s={g["digit_bits"]:g for g in group_oracles}
        for row in payload["rows"]:
            counts["sat_cells"]+=1
            membership=row["instance"]["curve_membership"]
            if membership:
                m=row["instance"]
                expected=oracle_by_s[m["s"]]["models_by_target"][str(m["target"])]
                instance=generate_s3(c["p"],m["s"],m["target"],a=c["a"],b=c["b"],curve_membership=True)
                ring=instance["ring"]
                actual=[bits for bits in range(1<<ring.n) if all(ring.eval(f,bits)==0 for f in instance["polynomials"])]
                if actual!=expected or row["oracle_solution_count"]!=len(expected):
                    raise ValueError("point-decomposition encoding lost or added a group solution")
                if (row["learner"]["status"]=="sat")!=bool(expected):
                    raise ValueError("SAT status disagrees with complete group oracle")
            if row["learner"]["status"]=="sat":
                lift=independent_lift(c,row["instance"],row["learner"]["model"])
                if row["lift"]["target_has_curve_lift"] is not True or row["lift"]["point_decomposition"]!=lift:
                    raise ValueError("independent lift disagreement")
                if membership:
                    if not lift:
                        raise ValueError("membership SAT model lacks actual point decomposition")
                    counts["actual_pdp_sat_models"]+=1
                elif not lift:
                    counts["residual_sat_without_lift"]+=1
            elif membership:
                counts["actual_pdp_unsat_cells"]+=1
        counts["curves"]+=1
    return {"valid":True,"counts":counts,
            "scope":"Exact all-target tiny prime-order point-decomposition validation; no speed or dreg claim"}


def execute(config_path,output,raw_name="raw-result.json",manifest_name="manifest.yaml"):
    import yaml
    if (output/raw_name).exists():
        raise ValueError("refusing to overwrite scientific output")
    output.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(config_path.read_text())
    data={"schema":"prime-sat-point-validation/v1","attack_claimed":False,
          "config":cfg,"config_sha256":sha(config_path),"curve_packages":[],"metrics":{}}
    write(output/raw_name,data)
    for p in cfg["primes"]:
        package={"p":p,"status":"started"}
        data["curve_packages"].append(package)
        try:
            curve=select_curve(p,cfg["maximum_curve_candidates"])
            if curve["status"]!="selected":
                raise ValueError("input-only curve selector exhausted")
            targets=sorted({P[0] for P in curve["points"]})
            satcfg={"primes":[p],"digits":cfg["digits"],"targets":targets,
                    "curve":{"a":curve["a"],"b":curve["b"]},
                    "degree_cap":cfg["degree_cap"],"row_cap":cfg["row_cap"]}
            payload=run_sat(satcfg)
            # The complete oracle is constructed only after all solver calls.
            oracles=[group_pair_oracle(curve,s) for s in cfg["digits"]]
            package.update(status="completed",curve=curve,targets=targets,sat_payload=payload,group_oracles=oracles)
        except Exception as exc:
            package.update(status="failed",error=str(exc),traceback=traceback.format_exc())
        write(output/raw_name,data)
        print(json.dumps({"p":p,"status":package["status"]}),flush=True)
    data["metrics"]={"completed_curves":sum(c["status"]=="completed" for c in data["curve_packages"])}
    write(output/raw_name,data)
    if manifest_name is not None:
        (output/manifest_name).write_text(yaml.safe_dump({"run":{"attack_claimed":False,"metrics":data["metrics"]}}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--verify",type=Path)
    args=parser.parse_args()
    if args.verify:
        print(json.dumps(check(args.verify),sort_keys=True))
    elif args.config and args.output:
        execute(args.config,args.output)
    else:
        parser.error("specify --config and --output or --verify")

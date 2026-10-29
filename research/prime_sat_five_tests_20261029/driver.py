#!/usr/bin/env python3
"""Fixed five-lead package runner; scientific launch uses the native supervisor."""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(HERE / "algebra"), str(ROOT / "tools")]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, data):
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")
    temp.replace(path)


def verify_packages(raw_path):
    import artifact_store
    from geometry.check_geometry import check as check_geometry
    from algebra.check import verify as check_algebra
    from sat.solver import verify as check_sat, verify_learning
    from core import BoolRing
    raw=artifact_store.read_json(raw_path)
    checks={}
    for package in ("geometry","sat","algebra"):
        entry=raw["packages"][package]
        if entry["status"] != "completed":
            checks[package]={"valid":False,"reason":entry.get("error","package incomplete")}
            continue
        path=raw_path.parent/entry["artifact"]
        if hashlib.sha256(artifact_store.read_bytes(path)).hexdigest()!=entry["sha256"]:
            raise ValueError("package digest mismatch")
        data=artifact_store.read_json(path)
        if package=="geometry":
            checks[package]=check_geometry(data)
        elif package=="algebra":
            counts=check_algebra(data)
            bad=copy.deepcopy(data)
            row=next(r for cell in bad["cells"] for arm in cell["lead3"] for r in arm["basis"])
            row["combination"][0][2]+=1
            rejected=False
            try:
                check_algebra(bad)
            except AssertionError:
                rejected=True
            checks[package]={"valid":rejected,"counts":counts,"tampered_certificate_rejected":rejected}
        else:
            valid=check_sat(data)
            ring=BoolRing(2,17)
            control=next(c for c in data["controls"] if c["name"]=="negative_unsat")
            polys=[ring.clean(f) for f in control["generators"]]
            bad=copy.deepcopy(control["result"])
            # Destroy the entire certificate of the known inconsistent
            # affine control, rather than relying on a coefficient location.
            bad["learned"][0]["certificate"]=[{} for _ in polys]
            rejected=not verify_learning(ring,polys,bad)
            checks[package]={"valid":valid and rejected and data["all_verified"],
                             "cells":len(data["rows"]),"tampered_certificate_rejected":rejected}
    return {"valid":all(c["valid"] for c in checks.values()),"packages":checks,
            "scope":"Exact finite certificate and model checks; independent code for geometry/algebra, identity replay plus exhaustive implication for SAT"}


def execute(config_path, output):
    import yaml
    from geometry.geometry import run as geometry_run
    from sat.solver import run as sat_run
    from algebra.run import run as algebra_run
    if any((output/name).exists() for name in ("raw-result.json","geometry.json","sat.json","algebra.json")):
        raise SystemExit("refusing to overwrite scientific artifacts")
    config=json.loads(config_path.read_text())
    output.mkdir(parents=True,exist_ok=True)
    result={"schema":"prime-sat-five-result/v1","attack_claimed":False,
            "config_sha256":digest(config_path),"config":config,
            "packages":{},"checks":{},"metrics":{},
            "scope":"Five finite Stage1 tests; no cryptographic speed or intrinsic degree-of-regularity claim",
            "environment":{"python":sys.version,"platform":platform.platform(),
                "dependencies":{x:importlib.metadata.version(x) for x in ("sympy","z3-solver","cvc5","python-sat")}}}
    for name,function in (("geometry",geometry_run),("sat",sat_run),("algebra",algebra_run)):
        result["packages"][name]={"status":"pending"}
    atomic_json(output/"raw-result.json",result)
    (output/"manifest.yaml").write_text(yaml.safe_dump({"run":{"result":{"attack_claimed":False},
        "metrics":{},"notes":"Exact finite Stage1 package, separate per-lead outcomes in raw-result.json; no timing inference."}}))
    for name,function in (("geometry",geometry_run),("sat",sat_run),("algebra",algebra_run)):
        print(json.dumps({"event":"package_started","package":name}),flush=True)
        try:
            payload=function(config[name])
            path=output/(name+".json")
            atomic_json(path,payload)
            result["packages"][name]={"status":"completed","artifact":path.name,
                                       "sha256":digest(path),"bytes":path.stat().st_size}
        except Exception as exc:
            # Failure in one new mechanism must not erase the other four.
            result["packages"][name]={"status":"failed","error":str(exc),
                                       "traceback":traceback.format_exc()}
            atomic_json(output/(name+".json"),result["packages"][name])
        atomic_json(output/"raw-result.json",result)
        print(json.dumps({"event":"package_finished","package":name,
                          "status":result["packages"][name]["status"]}),flush=True)
    result["metrics"]={"completed_packages":sum(x["status"]=="completed" for x in result["packages"].values()),
                       "failed_packages":sum(x["status"]=="failed" for x in result["packages"].values())}
    atomic_json(output/"raw-result.json",result)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--verify",type=Path)
    args=parser.parse_args()
    if args.verify:
        result=verify_packages(args.verify)
        print(json.dumps(result,sort_keys=True))
        raise SystemExit(0 if result["valid"] else 1)
    if args.config is None or args.output is None:
        parser.error("--config and --output required for execution")
    execute(args.config,args.output)


if __name__=="__main__":
    main()

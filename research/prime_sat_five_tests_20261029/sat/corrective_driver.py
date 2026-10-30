#!/usr/bin/env python3
"""Complete the fixed suite after an explicitly retained interrupted attempt."""
import argparse
import copy
import json
import sys
import traceback
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/"tools")]
from sat.point_driver import execute as execute_points, check as check_points, sha, write
from algebra.cached_replay import run as run_algebra, verify as check_algebra


def check(raw_path):
    import artifact_store
    import driver as original_driver
    raw=artifact_store.read_json(raw_path)
    config=raw["config"]
    config_path=ROOT/"experiments"/config["experiment_id"]/"config.json"
    if sha(config_path)!=raw["config_sha256"] or json.loads(config_path.read_text())!=config:
        raise ValueError("corrective frozen input mismatch")
    checks={}
    original_raw=(ROOT/config["original_artifacts"]["geometry"]).parent/"raw-result.json"
    original_check=original_driver.verify_packages(original_raw)
    for key in ("geometry","sat"):
        checks["original_"+key]=original_check["packages"][key]
    for package in ("point","algebra"):
        meta=raw["packages"][package]
        if meta["status"]!="completed":
            checks[package]={"valid":False,"reason":meta.get("error","incomplete")}
            continue
        path=raw_path.parent/meta["artifact"]
        if artifact_store.content_digest(path)!=meta["sha256"]:
            raise ValueError("corrective payload hash mismatch")
        if package=="point":
            checks[package]=check_points(path)
        else:
            data=artifact_store.read_json(path)
            if data["config"]!=config["algebra"]:
                raise ValueError("original algebra fixture contract changed")
            counts=check_algebra(data)
            for cell in data["cells"]:
                if artifact_store.read_json(raw_path.parent/(cell["id"]+".json"))!=cell:
                    raise ValueError("durable cell differs from final result")
            bad=copy.deepcopy(data)
            row=next(r for c in bad["cells"] for a in c["lead3"] for r in a["basis"])
            row["combination"][0][2]+=1
            try:
                check_algebra(bad)
            except AssertionError:
                rejected=True
            else:
                rejected=False
            checks[package]={"valid":rejected,"counts":counts,"tampered_certificate_rejected":rejected}
    return {"valid":all(x["valid"] for x in checks.values()),"packages":checks,
            "scope":"Exact completed mechanisms and complete finite coverage; original interruption retained, no speed or dreg claim"}


def execute(config_path,output):
    import yaml
    if (output/"raw-result.json").exists():
        raise ValueError("refusing to overwrite a trial")
    output.mkdir(parents=True,exist_ok=True)
    config=json.loads(config_path.read_text())
    raw={"schema":"prime-sat-corrective-result/v1","attack_claimed":False,
         "config":config,"config_sha256":sha(config_path),
         "packages":{name:{"status":"pending"} for name in ("point","algebra")},"metrics":{}}
    write(output/"raw-result.json",raw)
    (output/"manifest.yaml").write_text(yaml.safe_dump({"run":{"attack_claimed":False,"metrics":{}}}))
    for name in ("point","algebra"):
        print(json.dumps({"event":"package_started","package":name}),flush=True)
        try:
            path=output/(name+".json")
            if name=="point":
                execute_points(config_path,output,raw_name="point.json",manifest_name=None)
                point=json.loads(path.read_text())
                if not all(c["status"]=="completed" for c in point["curve_packages"]):
                    raise ValueError("incomplete point curve package")
            else:
                write(path,run_algebra(config["algebra"],checkpoint_dir=output))
            raw["packages"][name]={"status":"completed","artifact":path.name,"sha256":sha(path),"bytes":path.stat().st_size}
        except Exception as exc:
            raw["packages"][name]={"status":"failed","error":str(exc),"traceback":traceback.format_exc()}
            if not (output/(name+".json")).exists():
                write(output/(name+".json"),raw["packages"][name])
        write(output/"raw-result.json",raw)
        print(json.dumps({"event":"package_finished","package":name,"status":raw["packages"][name]["status"]}),flush=True)
    raw["metrics"]={"completed_packages":sum(x["status"]=="completed" for x in raw["packages"].values())}
    write(output/"raw-result.json",raw)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--verify",type=Path)
    args=p.parse_args()
    if args.verify:
        result=check(args.verify)
        print(json.dumps(result,sort_keys=True))
        raise SystemExit(0 if result["valid"] else 1)
    elif args.config and args.output:
        execute(args.config,args.output)
    else:
        p.error("specify --config and --output or --verify")

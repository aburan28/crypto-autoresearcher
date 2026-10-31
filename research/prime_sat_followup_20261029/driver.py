#!/usr/bin/env python3
"""Native-supervisor entry point. Refuses overwrite and persists every cell."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "tools")]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w") as stream:
        json.dump(obj, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    temp.replace(path)


def verify(raw_path):
    import artifact_store
    import encoding
    from check_coefficients import verify as verify_coefficients
    raw = artifact_store.read_json(raw_path)
    config_path = ROOT / "experiments" / raw["config"]["experiment_id"] / "config.json"
    if digest(config_path) != raw["config_sha256"] or json.loads(config_path.read_text()) != raw["config"]:
        raise ValueError("frozen configuration mismatch")
    checks = {}
    for package, verifier in (("encoding", encoding.verify), ("coefficients", verify_coefficients)):
        meta = raw["packages"][package]
        if meta["status"] != "completed":
            checks[package] = {"valid":False,"error":meta.get("error","incomplete")}
            continue
        path = raw_path.parent / meta["artifact"]
        if artifact_store.content_digest(path) != meta["sha256"]:
            raise ValueError("package hash mismatch")
        payload = artifact_store.read_json(path)
        if payload["config"] != raw["config"][package]:
            raise ValueError("package configuration mismatch")
        journal = raw_path.parent / ("encoding-cells.jsonl" if package == "encoding" else "coefficient-cells.jsonl")
        if [json.loads(line) for line in artifact_store.read_text(journal).splitlines()] != payload["cells"]:
            raise ValueError("durable cell journal mismatch")
        checks[package] = verifier(payload)
    return {"valid":all(c["valid"] for c in checks.values()),"packages":checks,
            "scope":"Finite certificate/model/chart checks, no timing or regularity inference"}


def execute(config_path, output):
    import yaml
    import encoding
    import coefficients
    if (output / "raw-result.json").exists():
        raise ValueError("refusing to overwrite existing scientific output")
    # A real native launch receipt is required, rather than an ad hoc fixture run.
    launch = json.loads((output / "launch.json").read_text())
    environment = json.loads((output / "environment.json").read_text())
    config = json.loads(config_path.read_text())
    raw = {"schema":"prime-sat-followup-result/v1","attack_claimed":False,
           "config":config,"config_sha256":digest(config_path),"metrics":{},
           "packages":{name:{"status":"pending"} for name in ("encoding","coefficients")},
           "environment":{"python":sys.version,"platform":platform.platform(),
                          "python_sat":importlib.metadata.version("python-sat")},
           "cost_scope":"Instrumented finite-field arithmetic and explicit procedural events, separately by phase; not a CPU instruction total."}
    write(output / "raw-result.json", raw)
    manifest = {"run":{"id":launch["run_id"],"experiment_id":config["experiment_id"],
                       "status":"running","attack_claimed":False,
                       "code":{"commit":launch["authority"]["commit"],"command":json.dumps(launch["argv"])},
                       "environment":environment,
                       "inputs":{"plan_sha256":launch["plan_sha256"],"trial_id":launch["trial_id"]},
                       "timing":{"started_at":launch["started_at"]},
                       "metrics":{},"result":{"raw_result":"raw-result.json","certificate":{"kind":"none","verified":None}}}}
    (output / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    for package, producer, journal_name in (("encoding",encoding.run,"encoding-cells.jsonl"),
                                             ("coefficients",coefficients.run,"coefficient-cells.jsonl")):
        print(json.dumps({"event":"package_started","package":package}), flush=True)
        journal_path = output / journal_name
        with journal_path.open("x") as journal:
            def checkpoint(cell):
                journal.write(json.dumps(cell,sort_keys=True,separators=(",", ":"))+"\n")
                journal.flush(); os.fsync(journal.fileno())
                print(json.dumps({"event":"cell_completed","package":package,"id":cell["id"]}),flush=True)
            try:
                payload = producer(config[package], checkpoint=checkpoint)
                path = output / (package + ".json")
                write(path, payload)
                raw["packages"][package] = {"status":"completed","artifact":path.name,
                                            "sha256":digest(path),"bytes":path.stat().st_size}
            except Exception as exc:
                failure = {"status":"failed","error":str(exc),"traceback":traceback.format_exc(),
                           "partial_artifact":journal_name}
                raw["packages"][package] = failure
                write(output / (package + ".json"), failure)
        write(output / "raw-result.json", raw)
        print(json.dumps({"event":"package_finished","package":package,
                          "status":raw["packages"][package]["status"]}),flush=True)
    raw["metrics"] = {"completed_packages":sum(v["status"]=="completed" for v in raw["packages"].values())}
    usage = resource.getrusage(resource.RUSAGE_SELF)
    raw["resources"] = {"peak_rss_bytes":usage.ru_maxrss*1024,"cpu_seconds":usage.ru_utime+usage.ru_stime,
                        "boundary":"producer including its own exact checks and serialization; independent native check process excluded"}
    write(output / "raw-result.json", raw)
    manifest["run"]["status"] = "completed" if raw["metrics"]["completed_packages"] == 2 else "failed"
    manifest["run"]["metrics"] = raw["metrics"]
    (output / "manifest.yaml").write_text(yaml.safe_dump(manifest))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path); parser.add_argument("--output",type=Path)
    parser.add_argument("--verify",type=Path)
    args = parser.parse_args()
    if args.verify:
        result = verify(args.verify)
        print(json.dumps(result,sort_keys=True))
        raise SystemExit(0 if result["valid"] else 1)
    if not (args.config and args.output):
        parser.error("provide --config/--output or --verify")
    execute(args.config,args.output)

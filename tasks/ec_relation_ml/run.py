#!/usr/bin/env python3
"""Write-once engineering pilot, retaining and verifying exact EC outputs."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[key] = "1"

import numpy as np  # noqa: E402
from bridge import (ACTIONS, FEATURE_NAMES, ROOT, canonical, features, from_case,
                    generate, relation_evaluation, scalar_roots, validate_case,
                    validate_splits, worker)  # noqa: E402
from ec import bsgs  # noqa: E402
from polynomial_ml import learning  # noqa: E402


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
        stream.write("\n")


def sources():
    files = [*Path(__file__).parent.glob("*.py"),
             *(ROOT/"tasks/polynomial_solver_ml/environment/polynomial_ml").glob("*.py"),
             ROOT/"tools/curve_identity.py", Path(__file__).with_name("PROTOCOL.md")]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}


def artifact_hashes(out):
    return {p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"}


def table(cases, labels):
    mapping = {c["id"]:i for i,c in enumerate(cases)}
    costs = np.full((len(cases),len(ACTIONS)),np.nan)
    rows = {}
    for row in labels:
        i,a = mapping[row["case_id"]],row["action"]
        if (type(a) is not int or not 0 <= a < len(ACTIONS) or (i,a) in rows
                or row["status"] not in ("completed","timed_out")):
            raise ValueError("invalid or duplicate cost observation")
        costs[i,a] = row["cost_seconds"]
        rows[i,a] = row
    if not np.isfinite(costs).all() or (costs <= 0).any():
        raise ValueError("incomplete or invalid cost table")
    return costs,rows


def fit_choices(cases, costs, fit_seed):
    x = np.asarray([features(c) for c in cases],dtype=float)
    mask = np.asarray([c["split"] == "train" for c in cases])
    model = learning.train(x[mask],costs[mask],seed=fit_seed,steps=1200)
    selected = learning.select(model,x)
    model["feature_names"] = list(FEATURE_NAMES)
    model["training_case_ids"] = [c["id"] for c in cases if c["split"] == "train"]
    selected["fixed"] = np.zeros(len(cases),dtype=int)
    selected["train_best_fixed"] = np.full(len(cases),int(np.argmin(costs[mask].mean(axis=0))))
    selected["uniform_seeded"] = np.random.default_rng(fit_seed).integers(len(ACTIONS),size=len(cases))
    selected["retrospective_oracle"] = costs.argmin(axis=1)
    return model,selected


def evaluation(cases, labels, selected, per_case_overhead=0.0):
    costs,rows = table(cases,labels)
    result = {}
    for split in ("train","validation","test"):
        indexes = [i for i,c in enumerate(cases) if c["split"] == split]
        methods = {}
        for name,choices in selected.items():
            if len(choices) != len(cases) or any(type(int(a)) is not int or not 0 <= a < len(ACTIONS) for a in choices):
                raise ValueError("invalid selections")
            chosen = [rows[i,int(choices[i])] for i in indexes]
            rank = sum(r.get("relations",{}).get("independent_rank",0) for r in chosen)
            recovered = sum(r.get("relations",{}).get("target_recoveries",0) for r in chosen)
            total = sum(r["cost_seconds"] for r in chosen)
            full = total + (len(indexes)*per_case_overhead if name in ("ridge","bandit") else 0)
            methods[name] = {"actions":[int(choices[i]) for i in indexes],
                             "mean_action_process_or_par2_seconds":total/len(indexes),
                             "selected_total_seconds_with_feature_inference":full,
                             "delivered_independent_rank_sum":rank,"verified_target_recoveries":recovered,
                             "independent_rank_per_second":rank/full,"recoveries_per_second":recovered/full,
                             "censored_actions":sum(r["status"]=="timed_out" for r in chosen),
                             "deployable":name != "retrospective_oracle"}
        uniform_cost = float(costs[indexes].mean())
        methods["uniform_expected"] = {"mean_action_process_or_par2_seconds":uniform_cost,
                                       "deployable":True}
        result[split] = {"cases":len(indexes),"independent_field_blocks":len({cases[i]["curve"]["p"] for i in indexes}),
                         "case_ids":[cases[i]["id"] for i in indexes],"methods":methods}
    return result


def shuffled_diagnostic(cases,labels,fit_seed):
    costs,_ = table(cases,labels)
    x = np.asarray([features(c) for c in cases],dtype=float)
    mask = np.asarray([c["split"]=="train" for c in cases])
    shuffled = costs[mask].copy()
    rng = np.random.default_rng(fit_seed+1)
    for row in shuffled:
        rng.shuffle(row)
    model = learning.train(x[mask],shuffled,seed=fit_seed,steps=1200)
    return {"scope":"Diagnostic; no finite-sample null-performance pass threshold.",
            "evaluation":evaluation(cases,labels,learning.select(model,x))}


def run(args):
    if not 0 <= args.seed < 2**32 or not 0 <= args.fit_seed < 2**32-1:
        raise ValueError("invalid seed")
    out = args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    (out/"logs").mkdir()
    started,start = timestamp(),time.monotonic()
    frozen = sources()
    status,error,labels,overhead = "failed",None,[],{}
    config = {"kind":"ec_relation_ml_software_pilot","profile":args.profile,"seed":args.seed,
              "fit_seed":args.fit_seed,"steps":1200,"action_timeout_seconds":5,
              "watchdog_seconds":900,"repetitions":1 if args.profile=="quick" else 2,
              "feature_names":list(FEATURE_NAMES),"actions":ACTIONS,
              "command":[sys.executable,*sys.argv],"started_at":started,
              "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
              "dirty_tree":subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).splitlines(),
              "scientific_review_performed":False,
              "asserts_nothing_about":"hypothesis status, prime-family resistance or large-group ECDLP"}
    write_json(out/"config.json",config)
    try:
        t = time.monotonic()
        cases = generate(args.profile,args.seed)
        for case in cases:
            validate_case(case)
        overhead["public_input_generation_and_admission"] = time.monotonic()-t
        write_json(out/"cases.json",cases)
        t = time.monotonic()
        truth = {c["id"]:{"roots":scalar_roots(c)} for c in cases}
        for case in cases:
            truth[case["id"]]["relations"] = relation_evaluation(case,truth[case["id"]]["roots"])
            began = time.monotonic()
            truth[case["id"]]["bsgs"] = {**bsgs(from_case(case),tuple(case["target"])),
                                          "complete_seconds":time.monotonic()-began}
        overhead["separate_root_relation_and_bsgs_evaluation"] = time.monotonic()-t
        write_json(out/"exact_evaluation.json",truth)
        jobs = [(case,a) for case in cases for a in range(len(ACTIONS))]
        random.Random(args.seed).shuffle(jobs)
        write_json(out/"measurement_order.json",[[c["id"],a] for c,a in jobs])
        t = time.monotonic()
        with (out/"labels.jsonl").open("x") as stream:
            for j,(case,action) in enumerate(jobs):
                if time.monotonic()-start > 895:
                    raise TimeoutError("complete pilot process watchdog")
                began = time.monotonic()
                try:
                    child = subprocess.run([sys.executable,str(Path(__file__).resolve()),"worker"],
                        input=json.dumps({"case":case,"action":action,"repetitions":config["repetitions"]}),
                        capture_output=True,text=True,timeout=5)
                    stdout,stderr = child.stdout,child.stderr
                    return_code = child.returncode
                    if return_code != 0:
                        row = None
                    else:
                        row = json.loads(stdout)
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or b""
                    stderr = exc.stderr or b""
                    stdout = stdout.decode(errors="replace") if isinstance(stdout,bytes) else stdout
                    stderr = stderr.decode(errors="replace") if isinstance(stderr,bytes) else stderr
                    return_code = None
                    row = {"case_id":case["id"],"action":action,"status":"timed_out","cost_seconds":10.0}
                elapsed = time.monotonic()-began
                prefix = f"logs/{case['id']}-{action}"
                (out/(prefix+".stdout.txt")).write_text(stdout)
                (out/(prefix+".stderr.txt")).write_text(stderr)
                if row is None:
                    raise RuntimeError(f"child exited {return_code}; see {prefix}.stderr.txt")
                if (row["case_id"],row["action"]) != (case["id"],action):
                    raise ValueError("wrong child identity")
                if row["status"]=="completed":
                    if row["roots"] != truth[case["id"]]["roots"] or row["relations"] != truth[case["id"]]["relations"]:
                        raise ValueError("child root or relation result disagrees with exact evaluator")
                    row["cost_seconds"] = elapsed
                row.update({"process_wall_seconds":elapsed,"return_code":return_code,
                            "stdout_path":prefix+".stdout.txt","stderr_path":prefix+".stderr.txt",
                            "recorded_at":timestamp()})
                labels.append(row)
                stream.write(json.dumps(row,allow_nan=False)+"\n")
                stream.flush()
                if j%12==0 or j+1==len(jobs):
                    print(f"measured {j+1}/{len(jobs)} jobs ({time.monotonic()-start:.1f}s)",flush=True)
        overhead["complete_offline_label_acquisition"] = time.monotonic()-t
        costs,_ = table(cases,labels)
        if any(all(row["status"] != "completed" for row in labels if row["case_id"]==c["id"]) for c in cases):
            raise ValueError("case has no completed action")
        t = time.monotonic()
        _ = np.asarray([features(c) for c in cases],dtype=float)
        overhead["public_feature_extraction"] = time.monotonic()-t
        t = time.monotonic()
        model,selected = fit_choices(cases,costs,args.fit_seed)
        overhead["fit_and_select_both_learners"] = time.monotonic()-t
        x = np.asarray([features(c) for c in cases],dtype=float)
        t = time.monotonic()
        learning.select(model,x)
        overhead["inference_both_learners"] = time.monotonic()-t
        write_json(out/"models.json",model)
        per_case = (overhead["public_feature_extraction"]+overhead["inference_both_learners"])/len(cases)
        measured = evaluation(cases,labels,selected,per_case)
        write_json(out/"evaluation.json",measured)
        t = time.monotonic()
        controls = {**learning.controls(seed=args.fit_seed),
                    "shuffled_action_labels":shuffled_diagnostic(cases,labels,args.fit_seed)}
        overhead["controls_and_null_fit"] = time.monotonic()-t
        write_json(out/"controls.json",controls)
        if not controls["positive_passed"] or not controls["constant_passed"]:
            raise ValueError("learner control failed")
        if sources() != frozen:
            raise RuntimeError("source changed during software run")
        status = "completed"
    except Exception as exc:
        error = {"type":type(exc).__name__,"message":str(exc)}
        raise
    finally:
        overhead["pilot_wall_total"] = time.monotonic()-start
        write_json(out/"manifest.json",{"status":status,"error":error,"config":config,
            "completed_at":timestamp(),"overhead_seconds":overhead,"source_sha256":frozen,
            "artifact_sha256":artifact_hashes(out),"environment":{"python":platform.python_version(),
                "platform":platform.platform(),"numpy":importlib.metadata.version("numpy"),
                "sympy":importlib.metadata.version("sympy"),"cpu_mode":"sequential, single BLAS thread"}})
    return {"status":status,"output":str(out),"jobs":len(labels),"wall_seconds":overhead["pilot_wall_total"]}


def verify(out):
    out = out.resolve()
    manifest = json.loads((out/"manifest.json").read_text())
    if manifest["status"] != "completed" or manifest["source_sha256"] != sources():
        raise ValueError("incomplete run or source mismatch")
    if manifest["artifact_sha256"] != artifact_hashes(out):
        raise ValueError("artifact hash mismatch")
    cases = json.loads((out/"cases.json").read_text())
    config = manifest["config"]
    if cases != generate(config["profile"],config["seed"]):
        raise ValueError("input regeneration mismatch")
    validate_splits(cases)
    exact = json.loads((out/"exact_evaluation.json").read_text())
    for case in cases:
        curve = validate_case(case)
        expected = exact[case["id"]]
        if scalar_roots(case) != expected["roots"] or relation_evaluation(case,expected["roots"]) != expected["relations"]:
            raise ValueError("incorrect roots, ranks or recoveries")
        checked = bsgs(curve,tuple(case["target"]))
        if any(expected["bsgs"][k] != v for k,v in checked.items()):
            raise ValueError("incorrect generic comparator")
    labels = [json.loads(line) for line in (out/"labels.jsonl").read_text().splitlines()]
    for row in labels:
        if row["status"]=="completed":
            if row["roots"] != exact[row["case_id"]]["roots"] or row["relations"] != exact[row["case_id"]]["relations"]:
                raise ValueError("incorrect measured action output")
            raw = json.loads((out/row["stdout_path"]).read_text())
            if any(row[k] != v for k,v in raw.items()) or row["cost_seconds"] != row["process_wall_seconds"]:
                raise ValueError("observation does not match raw child output")
        elif row["status"]=="timed_out" and row["cost_seconds"] != 10.0:
            raise ValueError("incorrect timeout penalty")
    costs,_ = table(cases,labels)
    model,choices = fit_choices(cases,costs,config["fit_seed"])
    if model != json.loads((out/"models.json").read_text()):
        raise ValueError("training replay mismatch")
    overhead = manifest["overhead_seconds"]
    per_case = (overhead["public_feature_extraction"]+overhead["inference_both_learners"])/len(cases)
    if evaluation(cases,labels,choices,per_case) != json.loads((out/"evaluation.json").read_text()):
        raise ValueError("metric arithmetic mismatch")
    controls = {**learning.controls(seed=config["fit_seed"]),
                "shuffled_action_labels":shuffled_diagnostic(cases,labels,config["fit_seed"])}
    if controls != json.loads((out/"controls.json").read_text()):
        raise ValueError("control replay mismatch")
    return {"status":"passed","cases":len(cases),"jobs":len(labels),
            "exact_roots_relations_ranks_recoveries":True,"fit_metrics_controls_replayed":True,
            "manifest_sha256":hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest(),
            "scope":"Software artifact verification; timing authentication and independent research review are not supplied."}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command",required=True)
    p = sub.add_parser("run")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--profile",choices=("quick","standard"),default="quick")
    p.add_argument("--seed",type=int,default=20261011)
    p.add_argument("--fit-seed",type=int,default=0)
    p = sub.add_parser("verify")
    p.add_argument("output",type=Path)
    sub.add_parser("worker")
    args = parser.parse_args()
    if args.command=="worker":
        payload = json.load(sys.stdin)
        result = worker(payload["case"],payload["action"],payload["repetitions"])
    elif args.command=="run":
        result = run(args)
    else:
        result = verify(args.output)
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

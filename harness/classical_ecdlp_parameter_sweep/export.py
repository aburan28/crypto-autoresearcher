#!/usr/bin/env python3
"""Export one observed 41-arm parameter sweep; never launch, pad or price it."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys

_spec = importlib.util.spec_from_file_location("_parameter_sweep_analysis", Path(__file__).with_name("analysis.py"))
analysis = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analysis)


def file_entry(path, base, kind="raw"):
    path = Path(path)
    return {"path":os.path.relpath(path.resolve(),Path(base).resolve()),"sha256":analysis.sha(path),
            "bytes":path.stat().st_size,"kind":kind}


def exact_values(values):
    return {k:str(v) if type(v) is int and abs(v)>2**53-1 else v for k,v in values.items()}


def provider_context(root, manifest, files, protocol):
    relative="launch-provider-context-bytes.json"
    path=analysis.checked_file(root,files[relative]);provider=analysis.read_json(path)
    analysis.require(provider.get("schema")=="classical.ecdlp.parameter-sweep.modal-provider-context/v1"
                     and provider.get("backend")=="modal" and provider.get("runtime")=="vm"
                     and provider.get("block_network") is True,"actual Modal VM provider context required")
    for key,prefix in (("app_id","ap-"),("sandbox_id","sb-"),("image_id","im-")):
        analysis.require(isinstance(provider.get(key),str) and provider[key].startswith(prefix),"actual Modal provider object ID missing")
    for field,provider_field in (("source_revision","source_a_revision"),("source_b_revision","source_b_revision"),
                                 ("source_c_revision","source_revision_c"),("binary_sha256","binary_sha256"),
                                 ("protocol_sha256","protocol_sha256"),("inputs_manifest_sha256","inputs_manifest_sha256")):
        analysis.require(manifest[field]==provider[provider_field],"raw/provider binding differs: "+field)
    placement=protocol["execution"]["placement"]
    for key in ("app_id","image_id"):
        analysis.require(provider[key]==placement[key],"actual Modal placement differs from frozen protocol")
    return provider


def row_status(record, findings):
    if findings:
        return "infra_error"
    status=record["status"]
    if status=="completed" and record.get("exitcode")==0:
        return "succeeded"
    if status=="timed_out":
        return "timeout"
    if status=="interrupted":
        return "interrupted"
    if status=="native_nonzero":
        return "failed"
    return "infra_error"


def execution_rows(children, root, files, provider, base):
    """Exactly one row/rusage per confirmed native child; shared Rho is not copied."""
    rows, unattempted, unresolved = [], [], []
    for child in children:
        record=child["metadata"]
        if child["attempts"]==0:
            unattempted.append({"arm":child["arm_id"],"fixture_id":child["fixture_id"],"replicate":child["replicate"],
                                "attempts":0,"metadata":file_entry(root/child["execution"],base,"receipt")})
            continue
        if child["attempts"] is None:
            unresolved.append({"arm":child["arm_id"],"fixture_id":child["fixture_id"],"replicate":child["replicate"],
                               "attempts":None,"metadata":file_entry(root/child["execution"],base,"receipt")})
            continue
        analysis.require(child["attempts"]==1,"no retry or invented attempt is admissible")
        for key in ("app_id","sandbox_id","image_id"):
            analysis.require(record["provider_identity"][key]==provider[key],"child actual provider identity differs")
        stream=[];stream_findings=[]
        if child["raw"] in files:
            try:
                stream,stream_findings,_=analysis.read_native(root,files,child["raw"])
            except (ValueError,OSError,KeyError,TypeError) as error:
                stream_findings=[{"error_type":type(error).__name__,"message":str(error)}]
        counted={}
        panel=child["analysis"]
        if panel is not None:
            counted.update(observed_target_cases=panel["observed_target_cases"],
                           observed_verified_scalar_claims=panel["observed_verified_scalar_claims"])
            if panel["output_complete"]:
                counted["full_native_group_additions_m64"]=panel["prefixes"]["64"]["full_native_counters"]["group_additions"]
            if "group_additions" in panel["observed_full_native_counters"]:
                counted["observed_full_native_group_additions"]=panel["observed_full_native_counters"]["group_additions"]
            for prefix,item in panel["prefixes"].items():
                counted["solver_api_group_additions_m"+prefix]=item["solver_api_counters"]["group_additions"]
        usage=record.get("rusage") or {};clock=record.get("clock") or {};host=record.get("host_before") or {}
        if usage.get("user_seconds") is not None and usage.get("system_seconds") is not None:
            counted["whole_child_cpu_seconds"]=usage["user_seconds"]+usage["system_seconds"]
        counters=analysis.native_counter_sequences(stream)
        counters["native_trace_rows"]=len(stream)
        for key,value in usage.items():
            if type(value) in (int,float):
                counters["rusage."+key]=value
        status=row_status(record,child["findings"]+stream_findings)
        verified=child["verification_passed"]
        complete_solved=bool(panel and panel["all_targets_solved"])
        excluded=status!="succeeded" or not verified or not complete_solved
        prefix=str(Path(child["execution"]).parent)+"/"
        artifacts=[file_entry(root/item["path"],base,"receipt" if item["path"].endswith("/execution.json") else "raw")
                   for item in files.values() if item["path"].startswith(prefix) and (root/item["path"]).is_file()]
        rows.append({"run_id":child["cell_id"]+"."+child["arm"],"arm":child["arm_id"],"instance_id":child["fixture_id"],
                     "seed":str(record["solver_seed"]),"replicate":child["replicate"],"warmup":False,
                     "status":status,"outcome_class":"completed" if status in ("succeeded","failed") else "not_completed",
                     "attempts":1,"resumed":int(record.get("resumed",False)),"checkpoint":None,
                     "measurements":{"counted":exact_values(counted),"wall_seconds":clock.get("wall_seconds"),"wall_valid":False,
                                     "cpu_user_seconds":usage.get("user_seconds"),"cpu_sys_seconds":usage.get("system_seconds"),
                                     "max_rss_bytes":usage.get("maxrss_bytes"),"counters":exact_values(counters)},
                     "isolation":{"tier":host.get("isolation_level"),"contended":host.get("contended"),
                                  "blockers":host.get("isolation_blockers",["Physical-host/L2 isolation is unqualified."])},
                     "verification":{"status":child.get("verification_status","verified" if verified else "error"),"verifier":"source-A public verifier, nine separate native-arm slices"},
                     "exclusion":{"excluded":excluded,"rule":"incomplete/censored/invalid target solve panel, failed native child or public-verification binding" if excluded else None},
                     "artifacts":artifacts,"started_at":record.get("started_at"),"finished_at":record.get("finished_at"),
                     "worker":provider["sandbox_id"],"backend_ref":provider["sandbox_id"]+":"+child["execution"]})
    return rows,unattempted,unresolved


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("repo-root","protocol","raw-manifest","verification-index","targets","out"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--analysis-summary",type=Path)
    p.add_argument("--external-nonce",required=True)
    p.add_argument("--export-id",required=True)
    args=p.parse_args()
    diagnostic=args.out.with_name(args.out.name+".validation.json")
    analysis.require(not args.out.exists() and not diagnostic.exists(),"fresh export AND companion diagnostic paths required")
    sys.path.insert(0,str(args.repo_root.resolve()/"tools"))
    import experiment_protocol as ep
    protocol=analysis.read_json(args.protocol)
    findings=ep.schema_errors(protocol,"experiment.protocol/v1") or ep.lint_protocol(protocol,args.protocol.parent)
    analysis.require(not findings and protocol["freeze"]["status"]=="frozen","actual frozen valid protocol required: "+"; ".join(findings))
    analysis.require({x["id"] for x in protocol["arms"]}==set(analysis.ARM_IDS),"wrong41-arm sweep protocol")
    config=protocol["extensions"]["parameter_sweep"]
    analysis.require(args.external_nonce==config.get("public_nonce_hex",config.get("original_nonce_hex")),"export nonce differs from frozen reused-public nonce")
    manifest,files,children,verifications=analysis.collect_children(args.raw_manifest,protocol,args.targets,args.verification_index)
    root=args.raw_manifest.resolve().parent
    provider=provider_context(root,manifest,files,protocol)
    runs,unattempted,unresolved=execution_rows(children,root,files,provider,args.out.parent)
    host=next((x["metadata"].get("host_before") for x in children if x["metadata"].get("host_before")),{})
    memory=host.get("meminfo_kb",{}).get("MemTotal")
    host_summary={"cpu_model":host.get("cpu_model"),"logical_cpus":len(host["affinity_cpus"]) if "affinity_cpus" in host else None,
                  "memory_bytes":memory*1024 if type(memory) is int else None,"kernel":host.get("kernel"),
                  "hypervisor":None,"isolation_tier_max":host.get("isolation_level")}
    entries=[file_entry(args.raw_manifest,args.out.parent,"receipt"),file_entry(args.verification_index,args.out.parent,"receipt"),
             file_entry(args.targets,args.out.parent)]
    entries.extend(file_entry(v["path"],args.out.parent,"receipt") for v in verifications.values() if v["path"] is not None)
    for item in files.values():
        analysis.checked_file(root,item)
        entries.append(file_entry(root/item["path"],args.out.parent))
    script=Path(__file__).with_name("analysis.py")
    analysis.require(analysis.sha(script)==protocol["analysis_plan"]["script"]["sha256"],"frozen analysis source differs")
    outputs=[]
    if args.analysis_summary:
        summary=analysis.read_json(args.analysis_summary)
        analysis.require(summary.get("schema")=="classical.ecdlp.parameter-sweep.analysis/v1"
                         and summary.get("protocol_sha256")==manifest["protocol_sha256"],"analysis summary/protocol differs")
        for path in (args.raw_manifest,args.verification_index,args.targets):
            analysis.require(summary["input_bindings"].get(str(path.resolve()))==analysis.sha(path),"analysis does not bind exact export inputs")
        outputs=[file_entry(args.analysis_summary,args.out.parent,"analysis")];entries+=outputs
    export={"schema":"experiment.export/v1","export_id":args.export_id,"created":datetime.now(timezone.utc).isoformat(),
            "protocol":{"path":os.path.relpath(args.protocol,args.out.parent),"sha256":manifest["protocol_sha256"],
                        "protocol_id":protocol["protocol_id"],"version":protocol["version"],"seed_nonce":args.external_nonce},
            "producer":{"runtime":"codex_cli","model":None,"session":None,"role":"executor"},
            "source":{"repo":"isogeny-labs/crypto-autoresearcher","commit":manifest["source_revision"],"dirty":None},
            "backend":"modal","host":{"path":os.path.relpath(root/"launch-provider-context-bytes.json",args.out.parent),
                                        "sha256":files["launch-provider-context-bytes.json"]["sha256"],"class_id":None,"summary":host_summary},
            "arms":[{"id":a["id"],"role":a["role"],"commit":manifest["source_revision"],"binary_sha256":manifest["binary_sha256"]} for a in protocol["arms"]],
            "runs":runs,"flow":ep.compute_flow(runs),"files":entries,
            "analysis":{"script":file_entry(script,args.out.parent,"analysis"),"blinded":False,"blinding_key_sha256":None,"outputs":outputs,"unmasked_at":None},
            "notes":[{"kind":"observation","by":"parameter-sweep export adapter","text":"One row is one actual native child with64targets and one wait4rusage record. shared.rho_reference is observed128times total, never copied as new observations for each variant."},
                     {"kind":"observation","by":"parameter-sweep export adapter","text":"Primary full-native group calls add disjoint fixture_validation+setup+64target deltas once. All upfront64Qvalidation remains charged, including at shorter displayed prefixes. Exact native counter-family/state arrays are JSON strings; no nested diagnostic is summed into a price. Clocks unqualified; native counter execution not independently replayed."}],
            "reviews_dir":"reviews","backend_record":{"original_flow":manifest["flow"],"planned_child_slots":5248,"planned_target_arm_cases":335872,
              "public_target_ids":8192,"unattempted":unattempted,"unresolved":unresolved,"provider_context":provider,
              "verification_slices":{v:{k:r[k] for k in ("path","sha256","passed","binding_findings")} for v,r in verifications.items()},
              "observed_target_cases":sum((x["analysis"] or {}).get("observed_target_cases",0) for x in children),
              "shared_rho_rows":sum(r["arm"]=="shared.rho_reference" for r in runs),
              "native_stream_findings":[{"execution":x["execution"],"findings":x["findings"]} for x in children if x["findings"]],
              "all_clocks_wall_valid":False,"native_counter_replay_verified":False}}
    findings=ep.schema_errors(export,"experiment.export/v1") or ep.lint_export(export,protocol,args.out.parent,True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    analysis.write_json(args.out,export)
    analysis.write_json(diagnostic,{"findings":findings,"actual_execution_rows":len(runs),"unattempted":len(unattempted),"unresolved":len(unresolved),
                                    "shared_rho_rows":sum(r["arm"]=="shared.rho_reference" for r in runs),"no_padded_or_duplicate_observations":True})
    print(json.dumps({"actual_execution_rows":len(runs),"findings":findings}))
    return 1 if findings else 0


if __name__=="__main__":
    raise SystemExit(main())

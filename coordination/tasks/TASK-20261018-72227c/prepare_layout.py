"""Source-only prospective layout; does not allocate IDs or run legacy code."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
oldroot="experiments/EXP-ECDLP-daee4d"
oldplan=oldroot+"/trial-plan-v1.json"
old=json.loads((root/oldplan).read_text())
sha=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
helper="tools/legacy_staged_manifest.py"
checker_scope="Unchanged legacy checker validates outcome vocabulary and file presence only; no independent arithmetic verification."
block={"trial_plan":oldplan,"trial_plan_sha256":sha(oldplan),"experiment_id":"EXP-ECDLP-daee4d","input_seed":20261007,
 "input_seed_semantics":"Stage0 freezes fixed original null_seed=20261007 without enumeration or RNG; Stage1 unchanged random.Random uses20261007+p+1009*a+b per curve. No new random draw/replication seed introduced.",
 "curve_id":None,"checker_scope":checker_scope,"stages":[]}
for stage,trial in enumerate(old["trials"]):
 names=["stage0/protocol-freeze.json","stage0/preregistered-predictions.json","stage0/worksheet-note.md"] if stage==0 else ["stage1/census.json","stage1/control-table.json","RESULTS.md"]
 block["stages"].append({"stage":stage,"trial_id":f"metadata-stage{stage}","legacy_trial_id":trial["id"],"global_outputs":[oldroot+"/"+n for n in names],
  "outcomes":["S0-FREEZE-OK"] if stage==0 else ["O-FLOOR","O-EXCESS","O-MIXED","O-CONTROL-FAIL","O-IMPEDIMENT"],"optional_globals_outcomes":[] if stage==0 else ["O-IMPEDIMENT"]})
closure={**old["source_sha256"],oldplan:sha(oldplan),old["specification"]:old["specification_sha256"],helper:sha(helper)}
trials=[]
for stage,oldtrial in enumerate(old["trials"]):
 argv=[sys.executable,helper,"run","--trial-plan","experiments/EXP-ECDLP-<COORDINATOR_ALLOCATED>/trial-plan.json","--run-dir","{run_dir}"]
 check=argv.copy();check[2]="check"
 runprefix=oldroot+"/runs/"+oldtrial["run_id"]+"/"
 sources=list(closure);sources.remove(helper)
 expected=sorted(set(sources)|{runprefix+n for n in oldtrial["artifacts"]}|set(block["stages"][stage]["global_outputs"])|(set(block["stages"][0]["global_outputs"]) if stage else set()))
 trials.append({"id":f"metadata-stage{stage}","run_id":f"RUN-ECDLP-<ALLOCATED_STAGE{stage}>","argv":argv,"check_argv":check,
  "artifacts":["manifest.yaml","raw-result.json","legacy-execution.json","legacy-workspace.tar"],"memory_mb":oldtrial["memory_mb"],"watchdog_seconds":oldtrial["watchdog_seconds"],
  **({"watchdog_reason":oldtrial["watchdog_reason"]} if "watchdog_reason" in oldtrial else {}),"depends_on":[] if stage==0 else ["metadata-stage0"],
  "workspace_expected_paths":expected,"workspace_path_semantics":"A fresh legacy-staged-* directory under this native RUN, removed only after a durable exact-byte tar equality check. Expected/actual/absent paths and hashes retained in legacy-execution.json; legacy old-relative run IDs retained inside tar.",
  "legacy_argv":oldtrial["argv"],"legacy_check_argv":oldtrial["check_argv"],"legacy_run_id":oldtrial["run_id"],"old_scientific_stage":stage})
layout={"schema":"crypto.autoresearch.prospective_staged_layout.v1","state":"source_preparation_only_not_canonical_not_admitted_not_executed",
 "identity":"Explicit adjacent19th candidate EXP-ECDLP-daee4d; membership in historical18 unauthenticated.","handoff":"TASK-20261018-72227c","decision":"DEC-20261018-43f3b8",
 "proposed_new_experiment_id":"EXP-ECDLP-<COORDINATOR_ALLOCATED>","proposed_legacy_staged_block":block,"source_sha256":closure,"trials":trials,
 "native_generated_artifacts":["launch.json","execution-receipt.json","command.txt","environment.json","stdout.log","stderr.log","check.stdout.log","check.stderr.log"],
 "archive_requirements":"All fixed4 driver plus GENERATED8 paths per separately allocated native stage RUN must be in prospective handoff/archive/write_scope. No old EXP or sealed stage0 path is written. Stage1 native predecessor receipt must be output_validated and bind the complete fixed4+GENERATED7 hash set, then its archived stage0 globals are copied into new workspace.",
 "scientific_scope":"Unchanged old stages0/1 only; two sequential primary native RUNs, not independent arithmetic implementations. Native certificate.kind=none; outer valid means preserved instrument checks/metadata integrity only.",
 "original_fixed_cells_and_controls":{"N_window":{"exclusive_low":1024,"exclusive_high":4096},"panel":"Two ordinary curves from unchanged ascending p/a/b search with p<5000; exclude a=b=1; old ordinary filter order_E!=p+1 retained without stronger assertion.","weight_rule":"floor(log2(N)/4); old negation quotient and affine identity handling unchanged","null_seed":20261007,"controls":["scalar-ranking recovers1 (old implementation selects W_aff itself)","random subset size |W_aff| using fixed original per-curve seed","negation quotient before counts","second ordinary curve","exclude y^2=x^3+x+1"],"metrics":["excess=overlap_frac-|W|/N","null_excess","scalar_recover_frac"],"thresholds":{"claim_excess":0.02,"falsify_excess":0.05},"stop":"After stage1 one original O-* label; no adaptive replacement/retry","limitations":"Source's scalar control is tautological; base rate |W|/N is preserved, not recalibrated to quotient classes. Metadata checker is not independent arithmetic verification, and O-CONTROL-FAIL/O-IMPEDIMENT imply no positive/negative hypothesis inference."},
 "requires_before_launch":["Coordinator allocated new EXP/two distinct RUNs/TASK and prospectively frozen specification/plan/approval","Committed full source closure and actual runtime, published native claim/queue/handoff/archive coverage","All normal native admission checks; separate implementation preparation is not authority to execute"],"originals_readonly":True,"complete_original_panels_executed":0}
(out/"trial-layout.json").write_text(json.dumps(layout,sort_keys=True,indent=2)+"\n")
(out/"legacy-staged-block.json").write_text(json.dumps(block,sort_keys=True,indent=2)+"\n")
(out/"source-closure.sha256").write_text("".join(f"{h}  {n}\n" for n,h in sorted(closure.items())))
print("Wrote prospective layout only; original scientific driver not imported or executed.")

"""Static hashes/syntax/layout receipt only: never imports the old instrument."""
from datetime import datetime,timezone
import ast,hashlib,json,platform,subprocess,sys
from pathlib import Path
import yaml
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
layout=json.loads((out/"trial-layout.json").read_text())
protected={
 "experiments/EXP-ECDLP-daee4d/implementation/run.py":"fcdf4035d1a044c709081723e5b2cce5cda63dd4b1e5bdc477aa9a209558519d",
 "experiments/EXP-ECDLP-daee4d/implementation/check.py":"1d13261784a49fcb8d0fbbdd04fd199fc19d86de173d66fa705d73256b596eba",
 "experiments/EXP-ECDLP-daee4d/specification.yaml":"3236ddfd4da01dba0bda1586cd59bf5a7e6b502d8d3e3904e51ba69448059ec8",
 "experiments/EXP-ECDLP-daee4d/trial-plan-v1.json":"45d94d809cb033f104f87ca9cce0d8d1e0ea9c9f8961ca5d586791dfe79a26db",
 "experiments/EXP-ECDLP-daee4d/trial-plan.json":"45d94d809cb033f104f87ca9cce0d8d1e0ea9c9f8961ca5d586791dfe79a26db"}
for n,h in protected.items():assert sha(root/n)==h,n
for n,h in layout["source_sha256"].items():assert sha(root/n)==h,n
assert layout["proposed_legacy_staged_block"]==json.loads((out/"legacy-staged-block.json").read_text())
assert [len(t["workspace_expected_paths"]) for t in layout["trials"]]==[10,13]
assert all(len(t["artifacts"])==4 and len(set(t["workspace_expected_paths"]))==len(t["workspace_expected_paths"]) for t in layout["trials"])
assert len(layout["native_generated_artifacts"])==8
sources=["tools/legacy_staged_manifest.py","tests/test_legacy_staged_manifest.py"]
for n in sources:ast.parse((root/n).read_text(),filename=n)
log=(out/"checks/synthetic-03.stderr.log").read_text()
assert "Ran 13 tests in 3.273s" in log and log.rstrip().endswith("OK")
command="PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.preloadIndex GIT_CONFIG_VALUE_0=false python3 -m unittest discover -s tests -p test_legacy_staged_manifest.py -v"
for i in (1,2,3):
 p=out/f"checks/synthetic-{i:02d}.command.txt"
 if not p.exists():p.write_text(command+f" > coordination/tasks/TASK-20261018-72227c/checks/synthetic-{i:02d}.stdout.log 2> coordination/tasks/TASK-20261018-72227c/checks/synthetic-{i:02d}.stderr.log\n")
validation={"schema":"crypto.autoresearch.static_preparation_checks.v1","created_at":datetime.now(timezone.utc).isoformat(),"source_closure_entries_verified":len(layout["source_sha256"]),"protected_original_hashes_verified":protected,"stage_potential_archive_file_counts":[10,13],"native_driver_artifacts_per_stage":4,"native_generated_artifacts_per_stage":8,"source_syntax_files":sources,"runtime":{"executable":sys.executable,"python":sys.version,"pyyaml":yaml.__version__,"platform":platform.platform()},"source_layout_bound":True,"complete_original_toy_panels_executed":0,"native_scientific_trials_executed":0,"scope":"static preparation validation and earlier synthetic-only unit tests; not scientific or external review"}
(out/"checks/final-static-validation.json").write_text(json.dumps(validation,sort_keys=True,indent=2)+"\n")
receipt={"schema":"crypto.autoresearch.staged_implementation_preparation.v1","task_id":"TASK-20261018-72227c","decision":"DEC-20261018-43f3b8","created_at":datetime.now(timezone.utc).isoformat(),"state":"source_preparation_complete_not_admitted_not_scientifically_executed","legacy_candidate":"EXP-ECDLP-daee4d","historical18_membership":"unauthenticated; explicit adjacent19th only","source_sha256":{n:sha(root/n) for n in sources},"legacy_runtime_closure":layout["source_sha256"],"layout_sha256":sha(out/"trial-layout.json"),"block_sha256":sha(out/"legacy-staged-block.json"),"software_controls":{"tests":13,"passed":13,"failed":0,"elapsed_seconds":3.273,"command":command,"cwd":str(root),"log_sha256":{n:sha(out/n) for n in ["checks/synthetic-03.stdout.log","checks/synthetic-03.stderr.log"]},"earlier_attempts":"synthetic01 retained unittest method-name collision before fixture execution; synthetic02 12 passed; no original science","native_minimum_manifest_gate":"accepted both synthetic stages; not scientific arithmetic verification","peak_rss_bytes":None},"technical_review":{"reviewer":"teammate staged_adapter_review","kind":"read-only internal source inspection, not formal external/independent scientific review","finding":"No blocker for pinned daee4d sources after canonical-entrypoint and temporal-boundary hardening; regenerated five-entry source closure checked","ran_tests":False,"ran_science":False},"report":{"markdown":"REPORT.md","pdf":"REPORT.pdf","pdf_sha256":sha(out/"REPORT.pdf"),"pages":2,"all_pages_visually_inspected":True,"diagram":"preparation-flow.svg"},"old_paths_modified":False,"scientific_execution_authorized_by_implementation":False,"complete_original_toy_panels_executed":0,"committed_or_pushed":False,"checker_scope":layout["proposed_legacy_staged_block"]["checker_scope"],"certificate":"none","next_owner":"Coordinator: allocate/admit/publish source-bound successor and two native stage RUNs before scientific execution"}
(out/"implementation-receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
entries=[root/n for n in sources]+[p for p in out.rglob("*") if p.is_file() and p.name!="ARTIFACTS.sha256"]
(out/"ARTIFACTS.sha256").write_text("".join(f"{sha(p)}  {p.relative_to(root).as_posix()}\n" for p in sorted(entries)))
print(json.dumps({"source_closure_entries":len(layout["source_sha256"]),"protected_originals":len(protected),"artifact_entries":len(entries),"layout_sha256":sha(out/"trial-layout.json"),"receipt_sha256":sha(out/"implementation-receipt.json")},sort_keys=True))

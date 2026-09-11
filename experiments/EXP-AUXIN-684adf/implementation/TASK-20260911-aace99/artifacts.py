"""Exclusive artifact writing and final hash-index construction."""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
PAYLOAD=("manifest.yaml","raw-result.json","source-bindings.json","launch-binding.json","fixtures.jsonl","truth.jsonl","cases.jsonl","reference-results.jsonl","counterexamples.jsonl","control-summary.json","cost-frontier.json","telemetry.json","execution-report.yaml")
HOST=("command.txt","environment.json","stdout.log","stderr.log")
def write_once(path:Path, value, *, empty=False):
    if path.exists(): raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8") as f:
        if not empty: json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
        f.flush();os.fsync(f.fileno())
def sha(path:Path):
    with path.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def final_index(run_dir:Path):
    names=PAYLOAD+HOST
    missing=[n for n in names if not (run_dir/n).is_file()]
    if missing: raise ValueError("missing finalized artifacts: "+",".join(missing))
    target=run_dir/"artifact-sha256.json"
    if target.exists():raise FileExistsError(target)
    write_once(target,{"schema":"auxin.artifact_index.v1","files":{n:sha(run_dir/n) for n in names}})
    return target

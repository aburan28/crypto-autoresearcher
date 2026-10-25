#!/usr/bin/env python3
"""Canned fixture driver; it never imports or invokes a solver."""
from __future__ import annotations
import argparse, hashlib, json, tarfile
from datetime import datetime, timezone
from pathlib import Path
import output_contract

def canon(v): return output_contract.canonical(v)
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--run-dir", type=Path, required=True); parser.add_argument("--mode", choices=("bounded-censor","canned-positive"), required=True); parser.add_argument("--fault", choices=("missing-top","empty-top","changed-digest","unlisted-raw")); args=parser.parse_args()
    d=args.run_dir/"diagnostic"; d.mkdir(exist_ok=False)
    raw={"fixture.txt": canon({"mode":args.mode,"label":"canned no-science fixture"})}
    for name, data in raw.items(): (d/name).write_bytes(data)
    tar=d/"raw.tar.gz"
    with tarfile.open(tar,"w:gz") as a:
        for name in raw: a.add(d/name,arcname=name)
    launch=json.loads((args.run_dir/"launch.json").read_text()); now=datetime.now(timezone.utc).isoformat()
    stops=["timeout_censored","timeout_censored","timeout_censored"] if args.mode=="bounded-censor" else ["timeout_censored","exited","timeout_censored"]
    cells=[{"cell":"monitor-null","kind":"synthetic_null","attempted":True,"stop":"infrastructure_monitor_error","fault":{"code":"unreadable_live_root"}}]
    for cell,stop in zip(output_contract.CELLS[1:],stops):
        row={"cell":cell,"kind":"positive","attempted":True,"stop":stop}
        if stop=="exited": row["response"]="canned_positive"
        cells.append(row)
    receipt={"schema":output_contract.DIAGNOSTIC_SCHEMA,"experiment_id":"EXP-ICPERF-fixture","run_id":launch["run_id"],"trial_id":launch["trial_id"],"plan_sha256":launch["plan_sha256"],"launch_sha256":sha((args.run_dir/"launch.json").read_bytes()),"claim_owner":launch["authority"]["owner"],"claim_epoch":launch["authority"]["epoch"],"started_utc":now,"ended_utc":now,"raw_tar_sha256":sha(tar.read_bytes()),"raw_members":[{"path":n,"sha256":sha(data),"bytes":len(data)} for n,data in raw.items()],"cells":cells}
    receipt_path=d/"receipt.json"; receipt_path.write_bytes(canon(receipt)); output_contract.write_outputs(args.run_dir)
    # Fixture-only post-emission faults leave the driver successful so the real
    # supervisor/checker, rather than this driver, classifies invalid_output.
    if args.fault == "missing-top": (args.run_dir/"manifest.yaml").unlink()
    elif args.fault == "empty-top": (args.run_dir/"manifest.yaml").write_bytes(b"")
    elif args.fault == "changed-digest": (args.run_dir/"raw-result.json").write_bytes(b"{}\n")
    elif args.fault == "unlisted-raw":
        extra=d/"unlisted.txt"; extra.write_text("fixture-only extra\n")
        with tarfile.open(tar,"w:gz") as archive:
            for name in (*raw, "unlisted.txt"): archive.add(d/name,arcname=name)
        receipt["raw_tar_sha256"]=sha(tar.read_bytes()); receipt_path.write_bytes(canon(receipt))
if __name__ == "__main__": main()

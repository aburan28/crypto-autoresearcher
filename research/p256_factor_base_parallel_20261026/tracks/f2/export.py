#!/usr/bin/env python3
"""Write the unified export from actual F2 receipts, never planned identities."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entry(path, base, kind):
    return {"path": os.path.relpath(path, base), "bytes": path.stat().st_size,
            "sha256": sha(path), "kind": kind}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True,
                        help="Fresh analysis directory containing result.json/report.md/diagram.svg")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    raw, out = args.run.resolve(), args.out.resolve()
    analysis_dir = args.analysis.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError("export must be a fresh path inside assigned F2 scope")
    protocol = json.loads(args.protocol.read_text())
    if protocol["freeze"]["status"] != "frozen":
        raise ValueError("export cannot bind a draft protocol")
    rows = [json.loads(line) for line in (raw/"rows.jsonl").read_text().splitlines() if line]
    source = json.loads((raw/"source-observed.json").read_text())
    host = json.loads((raw/"host.json").read_text())
    analysis = json.loads((analysis_dir/"result.json").read_text())
    if analysis["protocol_sha256"] != protocol["freeze"]["protocol_sha256"]:
        raise ValueError("analysis does not bind this frozen protocol")
    analysis_source = HERE/protocol["analysis_plan"]["script"]["path"]
    if analysis["analysis_sha256"] != sha(analysis_source):
        raise ValueError("analysis source differs from the executed analysis")
    seal = json.loads((raw/"manifest.json").read_text())
    for item in seal["files"]:
        path = raw/item["path"]
        if sha(path) != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("raw file changed after sealing: "+item["path"])
    base = out.parent
    arm_roles = {arm["id"]: arm["role"] for arm in protocol["arms"]}
    runs = []
    for row in rows:
        excluded = row["exclusion_rule"] is not None
        counted = {metric["id"]: row[metric["id"]]
                   for metric in protocol["metrics"]["primary"]+protocol["metrics"]["secondary"]
                   if metric["kind"] in ("counted", "exact", "rate") and metric["id"] in row}
        runs.append({
            "run_id": row["run_id"], "arm": row["arm"], "instance_id": row["instance_id"],
            "seed": row["seed"], "replicate": row["replicate"], "warmup": row["warmup"],
            "status": row["status"],
            "outcome_class": "completed" if row["status"] in ("succeeded", "failed") else "not_completed",
            "attempts": row["attempts"], "resumed": row["resumed"],
            "checkpoint": {"policy": "none", "generations_written": 0,
                           "restored_from_generation": None},
            "measurements": {
                "counted": counted, "wall_seconds": row["wall_seconds"], "wall_valid": False,
                "cpu_user_seconds": row["cpu_user_seconds"], "cpu_sys_seconds": row["cpu_sys_seconds"],
                "max_rss_bytes": row["max_rss_bytes"], "counters": row["native_counters"]},
            "isolation": {"tier": "L0", "contended": None,
                          "blockers": ["shared host; no per-arm clock observation"]},
            "verification": {"status": row["verification"],
                             "verifier": "independent.py Jacobian recurrence and complete solution-set comparison"},
            "exclusion": {"excluded": excluded, "rule": row["exclusion_rule"]},
            "artifacts": [entry(raw/"rows.jsonl", base, "raw"),
                          entry(raw/"summary.json", base, "summary")],
            "started_at": row["started_at"], "finished_at": row["finished_at"],
            "worker": row["worker"],
        })
    exclusions = []
    rules = sorted({run["exclusion"]["rule"] for run in runs if run["exclusion"]["excluded"]})
    for rule in rules:
        exclusions.append({"rule": rule, "run_ids": [run["run_id"] for run in runs
                                                     if run["exclusion"]["rule"] == rule]})
    flow = {
        "planned": len(runs), "attempted": sum(run["attempts"] >= 1 for run in runs),
        "completed": sum(run["outcome_class"] == "completed" for run in runs),
        "not_completed": sum(run["outcome_class"] == "not_completed" for run in runs),
        "interrupted": sum(run["status"] == "interrupted" for run in runs),
        "resumed": sum(run["resumed"] > 0 for run in runs), "excluded": exclusions,
    }
    summary_keys = ("cpu_model", "logical_cpus", "memory_bytes", "kernel",
                    "hypervisor", "isolation_tier_max")
    files = []
    for item in seal["files"]:
        path = raw/item["path"]
        kind = ("host" if path.name == "host.json" else
                "log" if path.suffix == ".txt" else
                "summary" if path.name == "summary.json" else "raw")
        files.append(entry(path, base, kind))
    files.append(entry(raw/"manifest.json", base, "receipt"))
    files.append(entry(args.protocol.resolve(), base, "protocol"))
    outputs = [entry(analysis_dir/name, base, "analysis")
               for name in ("result.json", "report.md", "diagram.svg")]
    e = {
        "schema": "experiment.export/v1", "export_id": "P256-PASS2-F2-"+raw.name,
        "created": datetime.now(timezone.utc).isoformat(),
        "protocol": {"path": os.path.relpath(args.protocol.resolve(), base),
                     "sha256": protocol["freeze"]["protocol_sha256"],
                     "protocol_id": protocol["protocol_id"], "version": protocol["version"]},
        "producer": {"runtime": "native Codex", "model": source["model"],
                     "session": "/root/pass2_auxiliary", "role": "executor"},
        "source": {"repo": "crypto-autoresearcher", "commit": source["runtime_head"],
                   "dirty": source["tracked_tree_dirty"]},
        "backend": "local",
        "host": {"path": os.path.relpath(raw/"host.json", base), "sha256": sha(raw/"host.json"),
                 "class_id": "unisolated-shared-host",
                 "summary": {key: host[key] for key in summary_keys}},
        "arms": [{"id": arm, "role": arm_roles[arm],
                  "binary_sha256": source["interpreter_sha256"],
                  "commit": source["instrument_commit"]} for arm in ("producer", "oracle")],
        "runs": runs, "flow": flow, "files": files,
        "analysis": {"script": entry(analysis_source, base, "analysis"), "blinded": False,
                     "blinding_key_sha256": None, "outputs": outputs, "unmasked_at": None},
        "notes": [{"kind": "observation", "by": "/root/pass2_auxiliary",
                   "text": "Two actual implementation traversals of one fixed panel. "
                           "Joint resource diagnostics are retained in package-resources.json; "
                           "no per-arm clock samples, general-yield estimate or ECDLP cost claim."}],
        "reviews_dir": "reviews",
    }
    serialized = json.dumps(e, sort_keys=True, separators=(",", ":"))+"\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as handle:
        handle.write(serialized)
    if out.stat().st_size > 65536:
        raise RuntimeError("export exceeds data policy; preserve it and use canonical artifact storage")
    print(json.dumps({"export": str(out), "flow": flow, "bytes": out.stat().st_size}))


if __name__ == "__main__":
    main()

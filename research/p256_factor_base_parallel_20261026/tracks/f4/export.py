"""Write unified export from actual F4 receipts, without regenerating data."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_entry(path, base, kind):
    return {"path": os.path.relpath(path, base), "bytes": path.stat().st_size,
            "sha256": sha(path), "kind": kind}


def export_run(run, protocol_path, target):
    run, protocol_path, target = Path(run), Path(protocol_path), Path(target)
    protocol = json.loads(protocol_path.read_text())
    canonical = {k: v for k, v in protocol.items() if k != "freeze"}
    actual_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                                            ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    assert protocol["freeze"]["status"] == "frozen"
    assert actual_hash == protocol["freeze"]["protocol_sha256"]
    environment = json.loads((run/"environment.json").read_text())
    observed = environment["source"]
    native = [json.loads(line) for line in (run/"rows.jsonl").read_text().splitlines() if line]
    metrics = [item["id"] for item in protocol["metrics"]["primary"]+protocol["metrics"]["secondary"]
               if item["kind"] in ["counted", "exact", "rate"]]
    planned = {arm["id"]: arm for arm in protocol["arms"]}
    arms = []
    for row in native:
        specification = planned[row["arm"]]
        assert row["role"] == specification["role"]
        assert observed["verified_implementation_commit"] == specification["instrument"]["commit"]
        assert observed["interpreter_sha256"] == specification["instrument"]["binary_sha256"]
        arms.append({"id": row["arm"], "role": row["role"],
                     "commit": observed["verified_implementation_commit"],
                     "binary_sha256": observed["interpreter_sha256"]})
    exported = []
    for row in native:
        status = row["status"]
        exported.append({
            "run_id": row["run_id"], "arm": row["arm"], "instance_id": row["instance_id"],
            "seed": row["seed"], "replicate": row["replicate"], "warmup": row["warmup"],
            "status": status, "outcome_class": "completed" if status in ["succeeded", "failed"] else "not_completed",
            "attempts": 1, "resumed": 0, "checkpoint": None,
            "measurements": {"counted": {key: row[key] for key in metrics},
                "wall_seconds": row["wall_seconds"], "wall_valid": False,
                "cpu_user_seconds": row["cpu_user_seconds"], "cpu_sys_seconds": row["cpu_sys_seconds"],
                "max_rss_bytes": row["max_rss_bytes"], "counters": row["native_counters"]},
            "isolation": {"tier": "L0", "contended": None,
                          "blockers": environment["isolation_blockers"]},
            "verification": {"status": row["verification"],
                             "verifier": "independent.py norm/product/Rabin/point consumer and dense kernel/rank oracle; separate implementations in producer session"},
            "exclusion": {"excluded": status == "failed",
                          "rule": "invalid_measurement: exact invariant refuted" if status == "failed" else None},
            "artifacts": [file_entry(run/("arm-"+row["arm"]+".json"), run, "raw")],
            "started_at": row["started_at"], "finished_at": row["finished_at"],
            "worker": environment["host"], "backend_ref": "fixed arm-panel"})
    excluded = [row["run_id"] for row in exported if row["exclusion"]["excluded"]]
    analysis = run/"analysis"
    payload = {
        "schema": "experiment.export/v1", "export_id": "P256-F4-pass2-"+run.name,
        "created": datetime.now(timezone.utc).isoformat(),
        "protocol": {"path": os.path.relpath(protocol_path, run),
                     "sha256": actual_hash, "protocol_id": protocol["protocol_id"],
                     "version": protocol["version"]},
        "producer": {"runtime": "native Codex subagent", "model": "inherited, unprobed",
                     "session": "/root/pass2_divisors", "role": "executor"},
        "source": {"repo": "crypto-autoresearcher",
                   "commit": observed["verified_implementation_commit"], "dirty": False},
        "backend": "local",
        "host": {"path": "environment.json", "sha256": sha(run/"environment.json"),
                 "class_id": environment["host"],
                 "summary": {key: environment[key] for key in ["cpu_model", "logical_cpus",
                       "memory_bytes", "kernel", "hypervisor", "isolation_tier_max"]}},
        "arms": arms, "runs": exported,
        "flow": {"planned": len(protocol["arms"]), "attempted": len(exported),
                 "completed": sum(r["outcome_class"] == "completed" for r in exported),
                 "not_completed": sum(r["outcome_class"] == "not_completed" for r in exported),
                 "interrupted": 0, "resumed": 0,
                 "excluded": [{"rule": "invalid_measurement: exact invariant refuted", "run_ids": excluded}] if excluded else []},
        "files": [file_entry(path, run, "raw")
                  for path in sorted(run.rglob("*")) if path.is_file() and path != target
                  and path != run/"environment.json" and not path.name.startswith("arm-")
                  and path.parent != analysis],
        "analysis": {"script": file_entry(Path(__file__).with_name("analysis.py"), run, "analysis"),
                     "blinded": False, "blinding_key_sha256": None, "unmasked_at": None,
                     "outputs": [file_entry(path, run, "analysis") for path in sorted(analysis.iterdir()) if path.is_file()]},
        "notes": [{"kind": "observation", "by": "/root/pass2_divisors",
                   "text": "Four fixed arm-panels;128 unique natural functions, reused in reverse-order A/A. Source bytes were checked against the pinned implementation commit; runtime HEAD and dirty state are separately retained. All clocks diagnostic. No canonical model/claim-review admission or official scientific transition."}],
        "reviews_dir": "reviews"}
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)+"\n"
    if len(encoded.encode()) > 65536:
        raise ValueError("Export exceeds in-Git data policy; retain raw data and arrange canonical artifact storage")
    with target.open("x") as handle:
        handle.write(encoded)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export_run(args.run, args.protocol, args.out)["flow"]))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run frozen missing family ranges without changing retained source shards."""

import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "raw" / "family_campaign" / "retry_plan.json"
LOGS = ROOT / "raw" / "family_campaign" / "retry_logs"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_path(shard):
    return ROOT / "raw" / "family_evaluations" / shard["target"] / f"{shard['start']:05d}-{shard['end']:05d}.jsonl"


def validate_file(path, shard, plan):
    with path.open() as source:
        header = json.loads(next(source))
        if (header.get("record") != "run" or header.get("target") != shard["target"] or
                header.get("start") != shard["start"] or header.get("end") != shard["end"] or
                header.get("candidate_sha256") != plan["candidate_sha256"] or
                header.get("torsion_sha256") != plan["torsion_screen_sha256"] or
                header.get("script_sha256") != plan["evaluator_sha256"]):
            raise ArithmeticError(f"header mismatch: {path}")
        rows = 0
        for line in source:
            row = json.loads(line)
            if (row.get("target") != shard["target"] or
                    row.get("index") != shard["start"] + rows or
                    row.get("status") == "INDETERMINATE"):
                raise ArithmeticError(f"row mismatch: {path}:{rows}")
            rows += 1
    if rows != shard["end"] - shard["start"] + 1:
        raise ArithmeticError(f"incomplete shard: {path}")


def main():
    plan = json.loads(PLAN.read_text())
    original = ROOT / "raw" / "family_campaign" / "plan.json"
    required = {"original_plan_sha256": original,
                "candidate_sha256": ROOT / "raw" / "candidates.jsonl",
                "torsion_screen_sha256": ROOT / "raw" / "prime_3torsion_screen.jsonl",
                "evaluator_sha256": ROOT / "evaluate_family_fast.py",
                "fast_controls_sha256": ROOT / "raw" / "fast_evaluator_controls.json"}
    if any(plan[key] != digest(path) for key, path in required.items()):
        raise ArithmeticError("retry plan input changed")
    if plan["max_workers"] != 1:
        raise ArithmeticError("this launcher admits one worker")
    for source in plan["source_segments"]:
        path = ROOT / source["path"]
        if digest(path) != source["sha256"]:
            raise ArithmeticError(f"retained source changed: {path}")
    LOGS.mkdir(parents=True, exist_ok=True)
    completed, failed = [], []
    for shard in plan["retry_shards"]:
        output = output_path(shard)
        partial = output.with_suffix(output.suffix + ".partial")
        name = f"{shard['target']}_{shard['start']:05d}_{shard['end']:05d}"
        if output.exists():
            validate_file(output, shard, plan)
            completed.append({"shard": name, "sha256": digest(output), "preexisting": True})
            print(json.dumps({"event": "verified_existing", "shard": name}), flush=True)
            continue
        if partial.exists():
            raise FileExistsError(f"preserved partial requires a new continuation: {partial}")
        stdout_path = LOGS / f"{name}.stdout"
        stderr_path = LOGS / f"{name}.stderr"
        command = ["/opt/homebrew/bin/gtimeout", "--signal=TERM", "--kill-after=10s",
                   f"{plan['per_shard_watchdog_seconds']}s", "sh", str(ROOT / "run_sage.sh"),
                   "--script", "evaluate_family_fast.py", "--target", shard["target"],
                   "--start", str(shard["start"]), "--end", str(shard["end"]),
                   "--stack-mib", str(shard["stack_mib"])]
        print(json.dumps({"event": "started", "shard": name}), flush=True)
        started = time.monotonic()
        with stdout_path.open("x") as stdout, stderr_path.open("x") as stderr:
            run = subprocess.run(command, cwd=ROOT.parent.parent, stdout=stdout, stderr=stderr)
        elapsed = round(time.monotonic() - started, 3)
        if run.returncode == 0 and output.exists():
            validate_file(output, shard, plan)
            completed.append({"shard": name, "sha256": digest(output),
                              "elapsed_seconds": elapsed, "preexisting": False})
            event = "completed"
        else:
            failed.append({"shard": name, "exit_code": run.returncode,
                           "partial_exists": partial.exists(), "elapsed_seconds": elapsed})
            event = "failed"
        print(json.dumps({"event": event, "shard": name, "exit_code": run.returncode,
                          "elapsed_seconds": elapsed}), flush=True)
    receipt = {"retry_plan_sha256": digest(PLAN), "completed": completed,
               "failed": failed, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = ROOT / "raw" / "family_campaign" / "retry_launch_receipt.json"
    with path.open("x") as sink:
        sink.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "finished", "completed": len(completed),
                      "failed": len(failed), "receipt_sha256": digest(path)}), flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

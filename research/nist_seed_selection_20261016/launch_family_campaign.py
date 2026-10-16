#!/usr/bin/env python3
"""Execute the frozen representative-stream plan with bounded concurrency."""

import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "raw" / "family_campaign" / "plan.json"
LOGS = ROOT / "raw" / "family_campaign" / "logs"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shard_path(shard):
    return ROOT / "raw" / "family_evaluations" / shard["target"] / f"{shard['start']:05d}-{shard['end']:05d}.jsonl"


def label(shard):
    return f"{shard['target']}_{shard['start']:05d}_{shard['end']:05d}"


def main():
    plan = json.loads(PLAN.read_text())
    if plan["candidate_sha256"] != digest(ROOT / "raw" / "candidates.jsonl") or plan["torsion_screen_sha256"] != digest(ROOT / "raw" / "prime_3torsion_screen.jsonl") or plan["evaluator_sha256"] != digest(ROOT / "evaluate_family_fast.py") or plan["fast_controls_sha256"] != digest(ROOT / "raw" / "fast_evaluator_controls.json"):
        raise ArithmeticError("frozen campaign inputs changed")
    LOGS.mkdir(parents=True, exist_ok=True)
    waiting = []
    for shard in plan["shards"]:
        output = shard_path(shard)
        partial = output.with_suffix(output.suffix + ".partial")
        if output.exists():
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            if len(rows) - 1 != shard["end"] - shard["start"] + 1 or any(
                row.get("status") == "INDETERMINATE" for row in rows[1:]
            ):
                raise ArithmeticError(f"existing shard invalid: {output}")
            continue
        if partial.exists():
            raise FileExistsError(f"retained partial needs a new immutable retry: {partial}")
        waiting.append(shard)
    total = len(waiting)
    active = {}
    complete = 0
    failures = []
    print(json.dumps({"event": "launch", "planned": len(plan["shards"]), "remaining": total,
                      "max_workers": plan["max_workers"]}), flush=True)
    while waiting or active:
        while waiting and len(active) < plan["max_workers"]:
            shard = waiting.pop(0)
            name = label(shard)
            stdout_path = LOGS / f"{name}.stdout"
            stderr_path = LOGS / f"{name}.stderr"
            if stdout_path.exists() or stderr_path.exists():
                raise FileExistsError(f"existing log for {name}")
            stdout = stdout_path.open("x")
            stderr = stderr_path.open("x")
            command = ["/opt/homebrew/bin/gtimeout", "--signal=TERM", "--kill-after=10s",
                       f"{plan['per_shard_watchdog_seconds']}s", "sh", str(ROOT / "run_sage.sh"),
                       "--script", "evaluate_family_fast.py", "--target", shard["target"],
                       "--start", str(shard["start"]), "--end", str(shard["end"]),
                       "--stack-mib", str(shard["stack_mib"])]
            process = subprocess.Popen(command, cwd=ROOT.parent.parent, stdout=stdout, stderr=stderr)
            active[name] = (process, shard, stdout, stderr, time.monotonic())
            print(json.dumps({"event": "started", "shard": name, "pid": process.pid}), flush=True)
        time.sleep(2)
        for name, (process, shard, stdout, stderr, started) in list(active.items()):
            code = process.poll()
            if code is None:
                continue
            stdout.close()
            stderr.close()
            del active[name]
            output = shard_path(shard)
            ok = code == 0 and output.exists()
            if ok:
                rows = [json.loads(line) for line in output.read_text().splitlines()]
                ok = len(rows) - 1 == shard["end"] - shard["start"] + 1 and not any(
                    row.get("status") == "INDETERMINATE" for row in rows[1:]
                )
            if ok:
                complete += 1
            else:
                failures.append({"shard": name, "exit_code": code, "output_exists": output.exists()})
            print(json.dumps({"event": "completed" if ok else "failed", "shard": name,
                              "exit_code": code, "elapsed_seconds": round(time.monotonic() - started, 3),
                              "complete": complete, "total": total}), flush=True)
    receipt = {"plan_sha256": digest(PLAN), "planned": len(plan["shards"]),
               "completed_this_launch": complete, "failures": failures,
               "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    receipt_path = ROOT / "raw" / "family_campaign" / "launch_receipt.json"
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "finished", **receipt}), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

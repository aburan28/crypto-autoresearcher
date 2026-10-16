#!/usr/bin/env python3
"""Execute the frozen six-stream X9 exact-count grid in 100-position shards."""

import argparse
import concurrent.futures
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TARGETS = REPO / "research/nist_seed_selection_20261016/targets.json"
COUNT = HERE / "count_x9.py"
READY = Path("/opt/nist-seed/READY.json")
ENDPOINTS = ("P-521", "P-384", "P-224", "P-256", "prime239v3", "prime192v2")
WIDTH = 100


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_shard(item, output_dir):
    target, start, end = item
    tag = f"{target}-{start:05d}-{end:05d}"
    log = output_dir / "logs" / tag
    log.parent.mkdir(parents=True, exist_ok=True)
    stdout = log.with_suffix(".stdout")
    stderr = log.with_suffix(".stderr")
    command = [sys.executable, str(COUNT), "--target", target,
               "--start", str(start), "--end", str(end)]
    if target == "P-521":
        command += ["--stack-mib", "1024"]
    started = time.monotonic()
    result = subprocess.run(command, text=True, capture_output=True)
    stdout.write_text(result.stdout)
    stderr.write_text(result.stderr)
    record = {"target": target, "start": start, "end": end,
              "command": command, "returncode": result.returncode,
              "elapsed_seconds": round(time.monotonic() - started, 6),
              "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr)}
    if result.returncode == 0:
        try:
            payload = json.loads(result.stdout)
            path = Path(payload["path"])
            expected_path = HERE / "raw/x9" / target / f"{start:05d}-{end:05d}.jsonl"
            if path != expected_path or not path.is_file() or digest(path) != payload["sha256"]:
                raise AssertionError("shard output hash mismatch")
            if payload["rows"] != end - start + 1:
                raise AssertionError("shard reported wrong row count")
            record["result_path"] = str(path.relative_to(REPO))
            record["result_sha256"] = digest(path)
            lines = path.read_text().splitlines()
            header = json.loads(lines[0])
            if (header["record"] != "run" or header["target"] != target or
                    header["start"] != start or header["end"] != end or
                    header["script_sha256"] != digest(COUNT) or
                    header["targets_sha256"] != digest(TARGETS)):
                raise AssertionError("shard header differs from plan")
            rows = [json.loads(line) for line in lines[1:]]
            record["rows"] = len(rows)
            record["indeterminate_rows"] = []
            for index, row in enumerate(rows, start):
                if row["target"] != target or row["index"] != index:
                    raise AssertionError("shard row target/index mismatch")
                if row["status"] != "COMPLETE":
                    record["indeterminate_rows"].append(index)
            if len(rows) != end - start + 1:
                raise AssertionError("incomplete shard row count")
        except Exception as exc:
            record["returncode"] = 90
            record["verification_error"] = f"{type(exc).__name__}: {exc}"
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.max_workers <= 12:
        parser.error("worker count must be 1..12")
    if not READY.is_file():
        parser.error("cloud bootstrap READY.json is absent")
    output_dir = HERE / "raw/cloud_campaign"
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = output_dir / "plan.json"
    events_path = output_dir / "events.jsonl"
    stop_path = output_dir / "stop.json"
    if any(path.exists() for path in (plan_path, events_path, stop_path)):
        raise FileExistsError("campaign output already exists")
    by_name = {t["name"]: t for t in json.loads(TARGETS.read_text())}
    streams = []
    for name in ENDPOINTS:
        endpoint = by_name[name]["candidate_index"]
        streams.append([(name, start, min(start + WIDTH - 1, endpoint))
                        for start in range(1, endpoint + 1, WIDTH)])
    shards = []
    for offset in range(max(map(len, streams))):
        shards.extend(stream[offset] for stream in streams if offset < len(stream))
    if sum(end - start + 1 for _, start, end in shards) != 21753:
        raise AssertionError("unexpected full-stream coverage")
    plan = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "command": sys.argv, "max_workers": args.max_workers,
            "shard_width": WIDTH, "shards": shards,
            "python": platform.python_version(), "cpu_count": os.cpu_count(),
            "bootstrap_ready_sha256": digest(READY),
            "script_sha256": digest(Path(__file__)),
            "counter_sha256": digest(COUNT),
            "targets_sha256": digest(TARGETS)}
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    successes = 0
    failed = []
    indeterminate = []
    with events_path.open("w") as events:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
            futures = {pool.submit(run_shard, item, output_dir): item for item in shards}
            for future in concurrent.futures.as_completed(futures):
                try:
                    record = future.result()
                except Exception as exc:
                    target, start, end = futures[future]
                    record = {"target": target, "start": start, "end": end,
                              "returncode": 99,
                              "exception": f"{type(exc).__name__}: {exc}"}
                events.write(json.dumps(record, sort_keys=True) + "\n")
                events.flush()
                if record["returncode"]:
                    failed.append([record["target"], record["start"], record["end"]])
                else:
                    successes += 1
                    indeterminate.extend((record["target"], i)
                                         for i in record["indeterminate_rows"])
                if (successes + len(failed)) % 10 == 0:
                    print(json.dumps({"completed": successes + len(failed),
                                      "total": len(shards), "failed": len(failed),
                                      "indeterminate_rows": len(indeterminate)}), flush=True)
    stop = {"completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "plan_sha256": digest(plan_path), "events_sha256": digest(events_path),
            "shards_total": len(shards), "shards_successful": successes,
            "failed_shards": failed, "indeterminate_rows": indeterminate,
            "status": "complete" if successes == len(shards) and not indeterminate
                      else "partial"}
    stop_path.write_text(json.dumps(stop, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"stop_path": str(stop_path), "sha256": digest(stop_path),
                      "status": stop["status"]}), flush=True)
    if stop["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

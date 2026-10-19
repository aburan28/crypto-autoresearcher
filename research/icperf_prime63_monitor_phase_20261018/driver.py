"""Synthetic-only dry-run driver and proposed raw custody format.

This driver intentionally does not accept a Sage request or scientific command.
A future Coordinator-approved experiment must supply its own admission-bound
launcher; these functions expose monitor and custody primitives only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from monitor import supervise
from phase import inspect

HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def custody(call_dir: Path, observation: dict, *, request: Path | None = None,
            response: Path | None = None) -> dict:
    trace = call_dir / "phase.jsonl"
    files = {"phase.jsonl": digest(trace),
             "stdout.raw": digest(call_dir / "stdout.raw"),
             "stderr.raw": digest(call_dir / "stderr.raw")}
    if request is not None:
        files["request"] = digest(request)
    if response is not None and response.exists():
        files["response"] = digest(response)
    return {"schema": "icperf-prime63-proposed-raw-custody-v1",
            "scientific_trial": False if request is None else None,
            "stop": observation["stop"], "fault": observation["fault"],
            "sampled_peak_rss_bytes": observation["peak_tree_rss_bytes_sampled"],
            "unobserved_rss_is_zero": False,
            "files_sha256": files, "trace": inspect(trace),
            "response_present": response is not None and response.exists()}


def dry_run(root: Path, mode: str) -> dict:
    if mode not in ("normal", "timeout", "abrupt"):
        raise ValueError("synthetic mode only")
    root.mkdir(parents=True, exist_ok=False)
    call_dir = root / "call"
    trace = call_dir / "phase.jsonl"
    script = (
        "import os,sys,time; from phase import TraceWriter; "
        "w=TraceWriter(sys.argv[1],sys.argv[2],'synthetic-child'); "
        "w.emit('input_load','begin'); w.emit('input_load','end'); "
        "w.emit('groebner','begin',synthetic=True); "
        "time.sleep(float(sys.argv[3])); "
        "w.emit('groebner','end',synthetic=True); "
        "os._exit(int(sys.argv[4]))"
    )
    sleep_seconds = "2.0" if mode == "timeout" else "0.02"
    exit_code = "7" if mode == "abrupt" else "0"
    command = [sys.executable, "-c", script, str(trace), str(HERE / "driver.py"),
               sleep_seconds, exit_code]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(HERE) + os.pathsep + env.get("PYTHONPATH", "")
    observation = supervise(command, call_dir, seconds=0.20 if mode == "timeout" else 1.0,
                            rss_cap_bytes=8*1024**3, scratch_cap_bytes=8*1024**3,
                            env=env, poll_seconds=0.005)
    record = custody(call_dir, observation)
    record["synthetic_mode"] = mode
    record["source_sha256"] = {name: digest(HERE / name) for name in
                               ("monitor.py", "phase.py", "driver.py")}
    out = root / "custody.json"
    with out.open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return record


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", choices=("normal", "timeout", "abrupt"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    record = dry_run(args.output_dir, args.synthetic)
    print(json.dumps({"stop": record["stop"], "trace_sha256": record["trace"]["sha256"],
                      "custody": str(args.output_dir / "custody.json")}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run existing volcano-IC experiments with bounded, auditable subprocesses.

No command runs implicitly. Example:
 python3 research/volcano_ic_crossrepo/run.py --root ../cryptanalysis --experiment crosscheck --timeout 1800
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

COMMANDS = {
    "crosscheck": ["python3", "crosscheck.py"],
    "sage-crosscheck": ["sage", "crosscheck.sage"],
    "census-shard": ["sage", "run.sage", "census", "0", "457"],
    "analyze": ["sage", "-python", "analyze.py"],
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path, help="cryptanalysis checkout")
    p.add_argument("--experiment", required=True, choices=sorted(COMMANDS))
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--output", type=Path, default=Path("volcano-runs.jsonl"))
    a = p.parse_args()
    if a.timeout < 1:
        p.error("timeout must be positive")
    workdir = (a.root / "experiments" / "volcano-ic").resolve()
    if not (workdir / "run.sage").is_file():
        p.error(f"not a volcano-ic checkout: {workdir}")
    cmd = COMMANDS[a.experiment]
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=a.root,
                         capture_output=True, text=True, check=False)
    started = time.perf_counter()
    try:
        result = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True,
                                timeout=a.timeout, check=False)
        status = "ok" if result.returncode == 0 else "error"
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        status, code = "timeout", None
        stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
    record = {"experiment": a.experiment, "command": cmd, "status": status,
              "returncode": code, "elapsed_wall_s": time.perf_counter()-started,
              "commit": rev.stdout.strip() if rev.returncode == 0 else None,
              "host": platform.node(), "platform": platform.platform(),
              "cpu_count": os.cpu_count(), "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
              "stdout": stdout, "stderr": stderr}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k not in ("stdout","stderr")}, indent=2))
    if status != "ok":
        raise SystemExit(1)

if __name__ == "__main__":
    main()

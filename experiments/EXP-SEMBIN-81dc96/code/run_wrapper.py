#!/usr/bin/env python3
"""Execute one SEMBIN derivation and write its run-directory artifacts.

Both authorized SEMBIN contracts are pure derivations: deterministic, standard
library only, no curve and no solver. What they still owe is the artifact
policy of AGENTS.md -- exact command, commit and dirty-tree state, environment,
stdout, stderr, raw machine-readable result, timing and resource measurements.
This wrapper produces exactly those and nothing else. It computes no research
quantity, so a defect here cannot move a result; it can only misreport
provenance, which the manifest's own hashes then disagree with.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def git(*args: str) -> str:
    return subprocess.run(("git",) + args, capture_output=True, text=True,
                          check=False).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--repo", default="/workspace")
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    os.makedirs(run_dir, exist_ok=True)
    script = os.path.abspath(args.script)
    raw = os.path.join(run_dir, "raw-result.json")

    argv = [sys.executable, os.path.basename(script), "--out", raw]
    command = " ".join(argv)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write(command + "\n")

    started = now()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    with open(os.path.join(run_dir, "stdout.log"), "wb") as out, \
            open(os.path.join(run_dir, "stderr.log"), "wb") as err:
        proc = subprocess.run(argv, cwd=os.path.dirname(script), stdout=out,
                              stderr=err, check=False)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    finished = now()

    wall = (dt.datetime.fromisoformat(finished)
            - dt.datetime.fromisoformat(started)).total_seconds()
    cpu = ((after.ru_utime - before.ru_utime)
           + (after.ru_stime - before.ru_stime))
    # ru_maxrss is a high-water mark over all reaped children, so it is an
    # upper bound on this child rather than its exact peak. Recorded as such.
    peak_rss = max(after.ru_maxrss, before.ru_maxrss) * 1024

    dirty = git("-C", args.repo, "status", "--porcelain")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "dependencies": {},
        "dependency_note": ("standard library only; no third-party package is "
                            "imported by either derivation or by the "
                            "independent arithmetic control"),
        "sage_version": None,
        "groebner_engine": None,
        "groebner_engine_note": ("none: this contract solves no polynomial "
                                 "system and consumes no algebra engine"),
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2, sort_keys=True)
        fh.write("\n")

    digests = {}
    for name in sorted(os.listdir(run_dir)):
        path = os.path.join(run_dir, name)
        if not os.path.isfile(path) or name == "artifact-digests.json":
            continue
        with open(path, "rb") as fh:
            digests[name] = hashlib.sha256(fh.read()).hexdigest()
    receipt = {
        "run_dir": os.path.relpath(run_dir, args.repo),
        "command": command,
        "exit_code": proc.returncode,
        "started_at": started,
        "finished_at": finished,
        "wall_seconds": round(wall, 6),
        "cpu_seconds": round(cpu, 6),
        "peak_rss_bytes_upper_bound": peak_rss,
        "git_commit": git("-C", args.repo, "rev-parse", "HEAD"),
        "git_branch": git("-C", args.repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(dirty),
        "git_dirty_paths": dirty.splitlines(),
        "sha256": digests,
    }
    with open(os.path.join(run_dir, "artifact-digests.json"), "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "sha256"},
                     indent=1))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

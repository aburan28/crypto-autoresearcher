#!/usr/bin/env python3
"""Provenance wrapper for EXP-SEMBIN-354a75. Computes no research quantity.

Adapted from experiments/EXP-SEMBIN-81dc96/code/run_wrapper.py, which this
contract's handoff names. Three changes were needed: the measurement takes a
second output path (the per-R counts), it imports numpy so the dependency
version has to be captured rather than declared absent, and peak memory is
read per-child so the figure is attributable to this run rather than being a
high-water mark over every child ever reaped.

This host has no /usr/bin/time, so timing and peak RSS come from the Python
`resource` module. `ru_maxrss` for RUSAGE_CHILDREN is a high-water mark over
reaped children, so it is recorded as an upper bound and labelled as one.
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


def dependency_versions() -> dict:
    out = {}
    for mod in ("numpy", "yaml"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "unknown")
        except ImportError:
            out[mod] = None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--repo", default="/workspace")
    ap.add_argument("extra", nargs="*")
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    os.makedirs(run_dir, exist_ok=True)
    script = os.path.abspath(args.script)
    raw = os.path.join(run_dir, "raw-result.json")
    per_r = os.path.join(run_dir, "per-R-counts.json")

    argv = [sys.executable, os.path.basename(script), "--out", raw,
            "--per-r-out", per_r, "--repo", args.repo] + list(args.extra)
    command = " ".join(argv)
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write("# run from " + os.path.dirname(script) + "\n")
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
    peak_rss = max(after.ru_maxrss, before.ru_maxrss) * 1024

    dirty = git("-C", args.repo, "status", "--porcelain")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "processor_count": os.cpu_count(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "dependencies": dependency_versions(),
        "sage_version": None,
        "groebner_engine": None,
        "groebner_engine_note": (
            "none, and none is needed: this contract COUNTS decompositions by "
            "enumerating and adding points. No polynomial system is solved, "
            "no Macaulay matrix is formed, and no degree is measured, "
            "estimated or assumed anywhere in it."),
        "field_arithmetic": {
            "reference_implementation": "code/binary_field.py",
            "vectorised_implementation": "code/fastfield.py",
            "agreement_selftest": "code/selftest_fastfield.py",
            "note": ("Irreducible moduli are found by programmatic search, "
                     "not from a table; the two implementations share the "
                     "modulus and are compared element by element."),
        },
    }
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2, sort_keys=True)
        fh.write("\n")

    digests = {}
    for name in sorted(os.listdir(run_dir)):
        path = os.path.join(run_dir, name)
        if not os.path.isfile(path) or name == "artifact-digests.json":
            continue
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        digests[name] = {"sha256": h.hexdigest(),
                         "bytes": os.path.getsize(path)}
    code_dir = os.path.join(os.path.dirname(script))
    code_digests = {}
    for name in sorted(os.listdir(code_dir)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(code_dir, name), "rb") as fh:
            code_digests[name] = hashlib.sha256(fh.read()).hexdigest()

    receipt = {
        "run_dir": os.path.relpath(run_dir, args.repo),
        "command": command,
        "exit_code": proc.returncode,
        "started_at": started,
        "finished_at": finished,
        "wall_seconds": round(wall, 6),
        "cpu_seconds": round(cpu, 6),
        "peak_rss_bytes_upper_bound": peak_rss,
        "peak_rss_gb_upper_bound": round(peak_rss / 1e9, 3),
        "git_commit": git("-C", args.repo, "rev-parse", "HEAD"),
        "git_branch": git("-C", args.repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(dirty),
        "git_dirty_paths": dirty.splitlines(),
        "artifact_sha256": digests,
        "code_sha256": code_digests,
    }
    with open(os.path.join(run_dir, "artifact-digests.json"), "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: v for k, v in receipt.items()
                      if k not in ("artifact_sha256", "code_sha256")},
                     indent=1))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

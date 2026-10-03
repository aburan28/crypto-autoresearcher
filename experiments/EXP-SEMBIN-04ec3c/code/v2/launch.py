#!/usr/bin/env python3
"""Run-package launcher for the EXP-SEMBIN-04ec3c v2 run.

  python3 experiments/EXP-SEMBIN-04ec3c/code/v2/launch.py run --run-id RUN-SEMBIN-xxxxxx
  python3 experiments/EXP-SEMBIN-04ec3c/code/v2/launch.py digest --run-id RUN-SEMBIN-xxxxxx

`run` refuses an existing run directory (run records are immutable), records git
commit and dirty state, then executes run_v2.py as a child with hard caps from
AMD-20261001-e61f2b's budget: RLIMIT_AS 2 GiB and a 1800 s wall-clock timeout.
It writes command.txt, environment.json, timing.json, stdout.log, stderr.log.

`digest` writes artifact-digests.json (sha256 of every file in the run
directory, the v2 code, the frozen inputs read, and the v1 artifacts whose
byte-identity the snapshot must confirm). Run it after manifest.yaml exists.
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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP = "experiments/EXP-SEMBIN-04ec3c"
WALL_CAP = 1800
MEM_CAP = 2 * 1024 ** 3
V1_PATHS = [f"{EXP}/specification.yaml", f"{EXP}/code/memory_charged_family.py"] + [
    f"{EXP}/runs/RUN-SEMBIN-c68773/{f}" for f in (
        "artifact-digests.json", "command.txt", "environment.json", "manifest.yaml",
        "raw-result.json", "stderr.log", "stdout.log", "timing.json")]
INPUTS = ["inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md",
          f"{EXP}/amendments/AMD-20261001-e61f2b.yaml"]


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cap():
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))


def do_run(run_id):
    rel = f"{EXP}/runs/{run_id}"
    run_dir = os.path.join(REPO, rel)
    if os.path.exists(run_dir):
        raise SystemExit(f"refusing: {rel} exists (run records are immutable)")
    os.makedirs(run_dir)
    git = {"commit": sh("git", "rev-parse", "HEAD").strip(),
           "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD").strip(),
           "status_porcelain_before_run": sh("git", "status", "--porcelain").splitlines()}
    git["dirty"] = bool(git["status_porcelain_before_run"])
    cmd = [sys.executable, f"{EXP}/code/v2/run_v2.py", "--run-dir", rel]
    with open(os.path.join(run_dir, "command.txt"), "w") as fh:
        fh.write("cd <repo root> && PYTHONDONTWRITEBYTECODE=1 " + " ".join(
            ["python3"] + cmd[1:]) + "\n")
        fh.write(f"# launched via: python3 {EXP}/code/v2/launch.py run --run-id {run_id}\n")
        fh.write(f"# caps: RLIMIT_AS={MEM_CAP} bytes, timeout={WALL_CAP} s\n")
    env = {"operating_system": platform.platform(), "architecture": platform.machine(),
           "python_version": platform.python_version(),
           "python_implementation": platform.python_implementation(),
           "python_executable": sys.executable, "dependencies": {},
           "dependency_note": "standard library only", "git": git,
           "cpu_count": os.cpu_count()}
    with open(os.path.join(run_dir, "environment.json"), "w") as fh:
        fh.write(json.dumps(env, indent=1) + "\n")
    child_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    started = dt.datetime.now(dt.timezone.utc)
    t0 = time.monotonic()
    timed_out, code = False, None
    with open(os.path.join(run_dir, "stdout.log"), "w") as so, \
            open(os.path.join(run_dir, "stderr.log"), "w") as se:
        try:
            p = subprocess.run(cmd, cwd=REPO, stdout=so, stderr=se, env=child_env,
                               preexec_fn=cap, timeout=WALL_CAP)
            code = p.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    wall = time.monotonic() - t0
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    timing = {"exit_code": code, "timed_out": timed_out,
              "started_at": started.isoformat(),
              "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "wall_seconds": round(wall, 6),
              "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6),
              "peak_rss_bytes": ru.ru_maxrss * 1024,
              "peak_rss_note": "ru_maxrss over reaped children (this launcher's only child is run_v2.py; the git calls are children too and are far smaller)",
              "caps": {"RLIMIT_AS_bytes": MEM_CAP, "timeout_seconds": WALL_CAP}}
    with open(os.path.join(run_dir, "timing.json"), "w") as fh:
        fh.write(json.dumps(timing, indent=1) + "\n")
    print(json.dumps(timing, indent=1))
    return 0


def do_digest(run_id):
    rel = f"{EXP}/runs/{run_id}"
    run_dir = os.path.join(REPO, rel)
    out = {"run_directory": {}, "code_v2": {}, "inputs_read": {}, "v1_artifacts": {}}
    for root, _, files in os.walk(run_dir):
        for f in sorted(files):
            p = os.path.join(root, f)
            r = os.path.relpath(p, run_dir)
            if r == "artifact-digests.json":
                continue
            out["run_directory"][r] = sha(p)
    code_dir = os.path.join(REPO, EXP, "code", "v2")
    for root, dirs, files in os.walk(code_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            p = os.path.join(root, f)
            out["code_v2"][os.path.relpath(p, REPO)] = sha(p)
    for p in INPUTS:
        out["inputs_read"][p] = sha(os.path.join(REPO, p))
    v1_digests = json.load(open(os.path.join(REPO, EXP, "runs/RUN-SEMBIN-c68773/artifact-digests.json")))
    for p in V1_PATHS:
        out["v1_artifacts"][p] = sha(os.path.join(REPO, p))
    out["v1_unchanged_check"] = {
        "git_diff_HEAD_on_v1_paths_empty": sh("git", "diff", "HEAD", "--name-only", "--", *V1_PATHS).strip() == "",
        "v1_run_files_match_v1_artifact_digests": all(
            out["v1_artifacts"][f"{EXP}/runs/RUN-SEMBIN-c68773/{k}"] == v
            for k, v in v1_digests.items() if not k.startswith("../")),
        "v1_driver_matches_v1_artifact_digests": out["v1_artifacts"][f"{EXP}/code/memory_charged_family.py"]
        == v1_digests["../../code/memory_charged_family.py"]}
    with open(os.path.join(run_dir, "artifact-digests.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["v1_unchanged_check"], indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["run", "digest"])
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args()
    return do_run(a.run_id) if a.action == "run" else do_digest(a.run_id)


if __name__ == "__main__":
    sys.exit(main())

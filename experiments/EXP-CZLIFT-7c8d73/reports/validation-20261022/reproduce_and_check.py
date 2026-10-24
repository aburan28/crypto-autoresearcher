#!/usr/bin/env python3
"""Reproduction replay (not a run record) for EXP-CZLIFT-7c8d73, validator TASK-20261022-d7d57f.

(a) Re-executes the producer's frozen driver function run.build(seed, 1500, 8, 2) in memory
    for each recorded seed and compares metrics and every raw row with raw-result.json.
    Nothing is written to the run directories.
(b) Runs the producer's checker check.py on each run directory (read-only) and records rc/stdout/stderr.
(c) Evaluates the specification's invalidation rule: the checker's re-run subset (first two curves)
    reproduces from the recorded inputs.
Run with python3 -B.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IMPL = os.path.join(REPO, "experiments", "EXP-CZLIFT-7c8d73", "implementation")
sys.path.insert(0, REPO)
sys.path.insert(0, IMPL)
import run as driver  # noqa: E402


def main():
    out = {}
    for rd in sys.argv[1:]:
        raw = json.load(open(os.path.join(rd, "raw-result.json")))
        seed = raw["metrics"]["seed"]
        m, rr = driver.build(seed, 1500, 8, 2)
        m = json.loads(json.dumps(m))
        rr = json.loads(json.dumps(rr))
        rows_equal = rr == raw["raw"]
        metrics_equal = m == raw["metrics"]
        ndiff = sum(1 for a, b in zip(rr["curves"], raw["raw"]["curves"]) if a != b)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        chk = subprocess.run([sys.executable, "-B", os.path.join(IMPL, "check.py"), rd], capture_output=True,
                             text=True, cwd=REPO, env=env)
        out[os.path.basename(rd.rstrip("/"))] = {
            "seed": seed, "full_rerun_raw_equal": rows_equal, "full_rerun_metrics_equal": metrics_equal,
            "curves_differing": ndiff, "checker_rc": chk.returncode, "checker_stdout": chk.stdout.strip(),
            "checker_stderr": chk.stderr.strip()}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()

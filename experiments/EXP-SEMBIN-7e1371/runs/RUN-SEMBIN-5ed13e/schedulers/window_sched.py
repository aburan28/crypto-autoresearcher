#!/usr/bin/env python3
"""RUN-SEMBIN-5ed13e: the m = t = 2 window of RUN-SEMBIN-9bb990 re-measured on a
fixed M4RI (0.0.20240729; libclosure built with `make M4RI_PREFIX=...`).

Same design as RUN-SEMBIN-9bb990/schedulers/m2_sched.py: per n, the first
solution-free and the first solution-bearing draw of the contract's draw order,
chosen from the exact enumeration in RUN-SEMBIN-9bb990/counts (not after seeing
a degree). Same run_cert arguments except
  * --closure-mem-cap 11 (GiB): the closure now counts the basis, the dense copy
    of the rows being multiplied and PLUQ's workspace, so the old caps (2.5-6.5)
    are no longer comparable;
  * CLOSURE_CKPT_DIR per lane, so a container restart costs one batch.
Sequential, one lane at a time. Relaunching is safe: run_cert --resume skips
finished instances and an unfinished closure resumes from its checkpoint.
"""
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

CODE = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
RUN = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e")
COUNTS = CODE.parent / "runs/RUN-SEMBIN-9bb990/counts/cells/results.jsonl"
CKPT = Path(os.environ.get("WINDOW_CKPT_ROOT", "/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/ckpt_window"))
LOG = RUN / "schedulers" / "window_sched.log"
CELLS = [(40, 20), (41, 21), (42, 21), (43, 22), (44, 22), (45, 23)]
CAP = 11.0
SUBSPACE = "low_degree_polynomial"
BMODE = "B_random"
SKIP = ("F4 trace unreached at these cells on this host: msolve with explicit field equations hit a 6 GB "
        "cap after 5 rounds at n = 40 (max step degree 3 seen). Measured by the degree-4 certificate instead.")


def say(msg):
    with open(LOG, "a") as fh:
        fh.write(f"[sched {time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def counts_for(n):
    out = {}
    for line in COUNTS.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if (r.get("instrument") == "exhaustive_solution_count" and r.get("n") == n
                and r.get("subspace") == SUBSPACE and r.get("B_mode") == BMODE):
            out[r["draw"]] = r["solutions"]
    return out


say(f"start; m4ri_library = " + subprocess.run(
    [sys.executable, "-c", "import closure_cert; print(closure_cert.M4RI_LIBRARY)"],
    cwd=CODE, capture_output=True, text=True).stdout.strip())
for (n, k) in CELLS:
    N = 2 * k
    ncols = sum(math.comb(N, d) for d in range(5))
    c = counts_for(n)
    zero = [d for d in sorted(c) if c[d] == 0]
    nonzero = [d for d in sorted(c) if c[d] > 0]
    draws = sorted({zero[0] if zero else 0, nonzero[0] if nonzero else 0})
    say(f"n={n}: counts {[c.get(d) for d in range(10)]} -> draws {draws} "
        f"(first solution-free {zero[:1]}, first solution-bearing {nonzero[:1]})")
    done_marker = RUN / f"closure_m2_n{n}" / "LANE_COMPLETE"
    if done_marker.exists():
        # Amendment 2026-10-03: a finished lane is skipped outright on relaunch.
        # Re-entering run_wrapper would rewrite its environment.json (start and
        # finish times) even though run_cert --resume adds no record.
        say(f"n={n}: lane already complete ({done_marker.read_text().strip()}); skipped")
        continue
    ck = CKPT / f"n{n}"
    ck.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CLOSURE_CKPT_DIR=str(ck), CLOSURE_VERBOSE="1")
    cmd = [sys.executable, str(CODE / "run_wrapper.py"), str(RUN / f"closure_m2_n{n}"),
           "--cells", f"{n}:2:2:{k}", "--families", "chained_eq5",
           "--draw-list", ",".join(str(d) for d in draws),
           "--subspaces", SUBSPACE, "--b-modes", BMODE,
           "--no-single", "--skip-f4", "--skip-f4-reason", SKIP,
           "--closure-mem-cap", str(CAP), "--closure-max-cols", "200000",
           "--d-max", "4", "--controls", "none", "--resume"]
    say(f"n={n}: start (N={N} ncols={ncols} cap={CAP} GiB draws={draws} ckpt={ck})")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=CODE, env=env, capture_output=True, text=True)
    line = f"n={n}: exit {p.returncode} after {time.time()-t0:.0f}s  {p.stdout.strip()[:200]}"
    say(line)
    if p.returncode == 0:
        done_marker.write_text(f"[sched {time.strftime('%Y-%m-%dT%H:%M:%S')}] {line}\n")
say("window schedule done")

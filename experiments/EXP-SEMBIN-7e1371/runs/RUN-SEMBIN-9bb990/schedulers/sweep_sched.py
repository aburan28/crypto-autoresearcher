#!/usr/bin/env python3
"""Sequential degree-4 closure schedule for the off-diagonal k sweeps of
RUN-SEMBIN-9bb990 (the monotonicity probe of EXP-SEMBIN-7e1371).

Same shape as the m = 2 schedule: one cell per invocation, memory cap sized to
that cell's column count, k ascending within each sweep so the deficiency
profile is built in the contract's order. Cells whose degree-4 column count
exceeds the cap are not attempted here; run_cert records them unreached with
their column count, which is the contract's reportable quantity.
"""
import math
import subprocess
import sys
import time
from pathlib import Path

CODE = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
RUN = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990")
LOG = Path("/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_sweep.log")
SKIP = ("F4 trace not attempted in this pass; the comparable traces at (17,3,3,6/7/8), (19,3,3,7), "
        "(21,3,3,7), (13,4,4,4) and (12,6,6,2) are in EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f")
# (n, m, t, k) in the contract's sweep order, k ascending
CELLS = [(17, 3, 3, 6), (17, 3, 3, 7), (19, 3, 3, 7), (21, 3, 3, 7), (13, 4, 4, 4),
         (17, 3, 3, 8), (19, 3, 3, 8), (21, 3, 3, 8), (13, 4, 4, 5),
         (17, 3, 3, 9), (19, 3, 3, 9), (19, 3, 3, 10), (21, 3, 3, 9), (21, 3, 3, 10),
         (13, 4, 4, 6), (12, 6, 6, 2), (12, 6, 6, 3), (12, 6, 6, 4)]
MAX_COLS = 200000


def say(msg):
    with open(LOG, "a") as fh:
        fh.write(f"[sweep {time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def free_gb():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / (1 << 20)
    return 0.0


for (n, m, t, k) in CELLS:
    N = n * (t - 2) + k * t
    ncols = sum(math.comb(N, d) for d in range(5))
    basis_gb = ncols * ncols / 8 / 1e9
    cap = max(1.5, round(basis_gb * 1.5 + 0.5, 1))
    need = cap + basis_gb + 1.5
    if ncols > MAX_COLS:
        # still run it: run_cert records the unreached declaration with the column count
        need, cap = 2.0, 1.5
    waited = 0
    while free_gb() < need:
        if waited % 600 == 0:
            say(f"({n},{m},{t},{k}): waiting for {need:.1f} GB (available {free_gb():.1f} GB)")
        time.sleep(30)
        waited += 30
    cmd = [sys.executable, str(CODE / "run_wrapper.py"), str(RUN / f"closure_sw_n{n}k{k}"),
           "--cells", f"{n}:{m}:{t}:{k}", "--families", "chained_eq5", "--draw-list", "0",
           "--subspaces", "low_degree_polynomial", "--b-modes", "B_equals_1",
           "--no-single", "--skip-f4", "--skip-f4-reason", SKIP,
           "--closure-mem-cap", str(cap), "--closure-max-cols", str(MAX_COLS),
           "--d-max", "4", "--controls", "none", "--resume"]
    say(f"({n},{m},{t},{k}): start N={N} ncols={ncols} basis={basis_gb:.2f} GB cap={cap} GB")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=CODE, capture_output=True, text=True)
    say(f"({n},{m},{t},{k}): exit {p.returncode} after {time.time()-t0:.0f}s {p.stdout.strip()[:160]}")
say("sweep schedule done")

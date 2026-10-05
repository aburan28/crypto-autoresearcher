#!/usr/bin/env python3
"""Phase-2 schedule for RUN-SEMBIN-9bb990: the off-diagonal k sweeps, plus the
one m = 2 instance the container OOM-killed.

Phase 1 ran two closure lanes at once and the container killed a worker at
n = 40 draw 1 (SIGKILL, wrapper exit -9, 1775 s in). Nothing partial was
written -- run_cert emits an instance's records only after every instrument on
it returns -- so the kill cost time, not data. This scheduler therefore admits
ONE heavy closure at a time: before each job it waits until no other run_cert
process holds more than HEAVY_RSS_GB, and until MemAvailable covers the cell's
own basis and cap with a 2.5 GB margin rather than 1.5.
"""
import math
import subprocess
import sys
import time
from pathlib import Path

CODE = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
RUN = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990")
LOG = Path("/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_phase2.log")
HEAVY_RSS_GB = 1.5
MARGIN_GB = 2.5
MAX_COLS = 200000
SKIP_SWEEP = ("F4 trace not attempted in this pass; comparable traces at (17,3,3,6/7/8), (19,3,3,7), "
              "(21,3,3,7), (13,4,4,4) and (12,6,6,2) are in "
              "experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f")
SKIP_M2 = ("F4 trace unreached at this cell on this host: msolve with explicit field equations hit a "
           "6 GB cap after 5 rounds at n = 40 (max step degree 3 seen)")

# (dirname, cells, draws, subspace, bmode, skip_reason)
JOBS = [
    # the instance the container killed in phase 1, re-run alone
    ("closure_m2_n40_d1", "40:2:2:20", "1", "low_degree_polynomial", "B_random", SKIP_M2),
]
for (n, m, t, k) in [(19, 3, 3, 7), (21, 3, 3, 7), (13, 4, 4, 4), (17, 3, 3, 8), (19, 3, 3, 8),
                     (21, 3, 3, 8), (13, 4, 4, 5), (17, 3, 3, 9), (19, 3, 3, 9), (19, 3, 3, 10),
                     (21, 3, 3, 9), (21, 3, 3, 10), (13, 4, 4, 6), (12, 6, 6, 2), (12, 6, 6, 3),
                     (12, 6, 6, 4)]:
    JOBS.append((f"closure_sw_n{n}k{k}", f"{n}:{m}:{t}:{k}", "0",
                 "low_degree_polynomial", "B_equals_1", SKIP_SWEEP))


def say(msg):
    with open(LOG, "a") as fh:
        fh.write(f"[phase2 {time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def free_gb():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / (1 << 20)
    return 0.0


def other_heavy(exclude_pid=None):
    """True while another run_cert process holds more than HEAVY_RSS_GB."""
    try:
        out = subprocess.run(["ps", "-eo", "pid,rss,args"], capture_output=True, text=True).stdout
    except Exception:
        return False
    for line in out.splitlines():
        if "run_cert.py" not in line or "grep" in line:
            continue
        parts = line.split(None, 2)
        pid, rss = int(parts[0]), int(parts[1]) / (1 << 20)
        if pid != exclude_pid and rss > HEAVY_RSS_GB:
            return True
    return False


def cell_size(spec):
    n, m, t, k = (int(x) for x in spec.split(":"))
    N = n * (t - 2) + k * t
    ncols = sum(math.comb(N, d) for d in range(5))
    return N, ncols


for (tag, spec, draws, subspace, bmode, skip) in JOBS:
    N, ncols = cell_size(spec)
    basis_gb = ncols * ncols / 8 / 1e9
    cap = max(1.5, round(basis_gb * 1.5 + 0.5, 1)) if ncols <= MAX_COLS else 1.5
    need = (cap + basis_gb + MARGIN_GB) if ncols <= MAX_COLS else 2.5
    waited = 0
    while other_heavy() or free_gb() < need:
        if waited % 600 == 0:
            say(f"{tag}: waiting (need {need:.1f} GB, have {free_gb():.1f}; "
                f"other heavy closure running: {other_heavy()})")
        time.sleep(30)
        waited += 30
    cmd = [sys.executable, str(CODE / "run_wrapper.py"), str(RUN / tag),
           "--cells", spec, "--families", "chained_eq5", "--draw-list", draws,
           "--subspaces", subspace, "--b-modes", bmode,
           "--no-single", "--skip-f4", "--skip-f4-reason", skip,
           "--closure-mem-cap", str(cap), "--closure-max-cols", str(MAX_COLS),
           "--d-max", "4", "--controls", "none", "--resume"]
    say(f"{tag}: start N={N} ncols={ncols} basis={basis_gb:.2f} GB cap={cap} GB draws={draws}")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=CODE, capture_output=True, text=True)
    say(f"{tag}: exit {p.returncode} after {time.time()-t0:.0f}s {p.stdout.strip()[:160]}")
    if p.returncode != 0:
        say(f"{tag}: NONZERO EXIT -- if -9 the container killed it; nothing partial is written")
say("phase 2 done")

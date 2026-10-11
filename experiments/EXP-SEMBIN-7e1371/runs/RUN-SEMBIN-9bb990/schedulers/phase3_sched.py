#!/usr/bin/env python3
"""The single remaining scheduler for RUN-SEMBIN-9bb990.

Two workers were lost to the container OOM killer in phase 1 and 2 -- the
n = 40 and n = 41 draws, at 1775 s and 1414 s -- because two closure lanes with
1.5 GB margins were running at once. There is now exactly ONE scheduler and it
admits ONE heavy closure at a time: it waits until no other run_cert process
holds more than 1.5 GB, and until MemAvailable covers the cell's own basis and
cap with a 3.0 GB margin. Nothing partial was ever written by a killed worker
(run_cert emits an instance only after every instrument on it returns), so the
kills cost wall-clock and no data.

Order is chosen for what the run needs if it is cut short, cheapest information
first:
  1. the over-cap cells, which cost nothing -- run_cert records them unreached
     with their column counts, which is the contract's reportable quantity;
  2. draw 0 across the whole m = 2 window, so the shape in n is complete before
     any second draw is paid for;
  3. the affordable off-diagonal cells, ascending in k, for the threshold;
  4. the complementary draw per m = 2 cell (solution-bearing where draw 0 was
     free and vice versa), chosen by the exact counter before any degree was
     measured.
"""
import math
import subprocess
import sys
import time
from pathlib import Path

CODE = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
RUN = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990")
LOG = Path("/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_phase3.log")
HEAVY_RSS_GB, MARGIN_GB, MAX_COLS = 1.5, 3.0, 200000
SKIP_SWEEP = ("F4 trace not attempted in this pass; comparable traces at (17,3,3,6/7/8), (19,3,3,7), "
              "(21,3,3,7), (13,4,4,4) and (12,6,6,2) are in "
              "experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f")
SKIP_M2 = ("F4 trace unreached at the m = 2 window on this host: msolve with explicit field equations "
           "hit a 6 GB cap after 5 rounds at n = 40 (max step degree 3 seen)")

JOBS = []
# 1. over-cap cells: instant, and the column count is the datum
for (n, m, t, k) in [(19, 3, 3, 10), (21, 3, 3, 9), (21, 3, 3, 10), (13, 4, 4, 6),
                     (12, 6, 6, 2), (12, 6, 6, 3), (12, 6, 6, 4)]:
    JOBS.append((f"closure_sw_n{n}k{k}", f"{n}:{m}:{t}:{k}", "0", "low_degree_polynomial",
                 "B_equals_1", SKIP_SWEEP))
# 2. draw 0 across the m = 2 window (n = 40 draw 0 is already recorded)
for (n, k) in [(41, 21), (42, 21), (43, 22), (44, 22), (45, 23)]:
    JOBS.append((f"closure_m2_n{n}", f"{n}:2:2:{k}", "0", "low_degree_polynomial",
                 "B_random", SKIP_M2))
# 3. affordable off-diagonal cells, ascending in k
for (n, m, t, k) in [(17, 3, 3, 8), (21, 3, 3, 7), (13, 4, 4, 4), (19, 3, 3, 8),
                     (17, 3, 3, 9), (21, 3, 3, 8), (19, 3, 3, 9), (13, 4, 4, 5)]:
    JOBS.append((f"closure_sw_n{n}k{k}", f"{n}:{m}:{t}:{k}", "0", "low_degree_polynomial",
                 "B_equals_1", SKIP_SWEEP))
# 4. complementary draw per m = 2 cell: first solution-bearing where draw 0 was free,
#    first solution-free where draw 0 was bearing, from the counts pass
for (n, k, d) in [(40, 20, 1), (41, 21, 4), (42, 21, 1), (43, 22, 5), (44, 22, 5), (45, 23, 4)]:
    JOBS.append((f"closure_m2_n{n}_d{d}", f"{n}:2:2:{k}", str(d), "low_degree_polynomial",
                 "B_random", SKIP_M2))


def say(msg):
    with open(LOG, "a") as fh:
        fh.write(f"[phase3 {time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def free_gb():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / (1 << 20)
    return 0.0


def other_heavy():
    out = subprocess.run(["ps", "-eo", "pid,rss,args"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if "run_cert.py" not in line:
            continue
        parts = line.split(None, 2)
        if int(parts[1]) / (1 << 20) > HEAVY_RSS_GB:
            return True
    return False


for (tag, spec, draws, subspace, bmode, skip) in JOBS:
    n, m, t, k = (int(x) for x in spec.split(":"))
    N = n * (t - 2) + k * t
    ncols = sum(math.comb(N, d) for d in range(5))
    over = ncols > MAX_COLS
    basis_gb = 0.0 if over else ncols * ncols / 8 / 1e9
    cap = 1.5 if over else max(1.5, round(basis_gb * 1.5 + 0.5, 1))
    need = 2.0 if over else cap + basis_gb + MARGIN_GB
    waited = 0
    while other_heavy() or free_gb() < need:
        if waited % 900 == 0:
            say(f"{tag}: waiting (need {need:.1f} GB, have {free_gb():.1f}, other heavy: {other_heavy()})")
        time.sleep(30)
        waited += 30
    cmd = [sys.executable, str(CODE / "run_wrapper.py"), str(RUN / tag),
           "--cells", spec, "--families", "chained_eq5", "--draw-list", draws,
           "--subspaces", subspace, "--b-modes", bmode,
           "--no-single", "--skip-f4", "--skip-f4-reason", skip,
           "--closure-mem-cap", str(cap), "--closure-max-cols", str(MAX_COLS),
           "--d-max", "4", "--controls", "none", "--resume"]
    say(f"{tag}: start N={N} ncols={ncols}{' OVER CAP' if over else ''} "
        f"basis={basis_gb:.2f} GB cap={cap} GB draw={draws}")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=CODE, capture_output=True, text=True)
    say(f"{tag}: exit {p.returncode} after {time.time()-t0:.0f}s {p.stdout.strip()[:140]}")
    if p.returncode != 0:
        say(f"{tag}: NONZERO EXIT (-9 = container kill; nothing partial is written)")
say("phase 3 done")

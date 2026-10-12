#!/usr/bin/env python3
"""Sequential degree-4 closure schedule for the m = t = 2 window of
RUN-SEMBIN-9bb990.

One cell per invocation: the closure's accumulated basis alone is ncols^2/8
bytes, so the memory cap has to be sized to the cell or the closure hits the cap
partway and reports unreached.  Two instances per cell on the paper's Table 2
convention (low-degree-polynomial subspace, random B): the first solution-free
draw and the first solution-bearing draw of the contract's draw order, chosen by
the exact enumeration in the counts pass.  Both are recorded; neither is chosen
after seeing a degree.
"""
import json
import math
import subprocess
import sys
import time
from pathlib import Path

CODE = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code")
RUN = Path("/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990")
COUNTS = RUN / "counts/cells/results.jsonl"
LOG = Path("/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_m2.log")
CELLS = [(40, 20, 2.5), (41, 21, 3.0), (42, 21, 3.0), (43, 22, 4.5), (44, 22, 4.5), (45, 23, 6.0)]
SUBSPACE = "low_degree_polynomial"
BMODE = "B_random"
SKIP = ("F4 trace unreached at these cells on this host: msolve with explicit field equations hit a 6 GB "
        "cap after 5 rounds at n = 40 (max step degree 3 seen). Measured by the degree-4 certificate instead.")


def say(msg):
    with open(LOG, "a") as fh:
        fh.write(f"[sched {time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)


def counts_for(n):
    out = {}
    if not COUNTS.exists():
        return out
    for line in COUNTS.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if (r.get("instrument") == "exhaustive_solution_count" and r.get("n") == n
                and r.get("subspace") == SUBSPACE and r.get("B_mode") == BMODE):
            out[r["draw"]] = r["solutions"]
    return out


def free_gb():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / (1 << 20)
    return 0.0


def wait_for_memory(need_gb, label):
    waited = 0
    while free_gb() < need_gb:
        if waited % 300 == 0:
            say(f"{label}: waiting for {need_gb:.1f} GB (available {free_gb():.1f} GB)")
        time.sleep(30)
        waited += 30


for (n, k, cap) in CELLS:
    N = 2 * k
    ncols = sum(math.comb(N, d) for d in range(5))
    basis_gb = ncols * ncols / 8 / 1e9
    # wait for the counts pass to reach this cell
    for _ in range(240):
        c = counts_for(n)
        if len(c) >= 10:
            break
        time.sleep(15)
    c = counts_for(n)
    if not c:
        say(f"n={n}: no counts available; running draw 0 only")
        draws = [0]
    else:
        zero = [d for d in sorted(c) if c[d] == 0]
        nonzero = [d for d in sorted(c) if c[d] > 0]
        draws = sorted({zero[0] if zero else 0, nonzero[0] if nonzero else 0})
        say(f"n={n}: counts {[c.get(d) for d in range(10)]} -> draws {draws} "
            f"(first solution-free {zero[:1]}, first solution-bearing {nonzero[:1]})")
    need = cap + basis_gb + 1.5
    wait_for_memory(need, f"n={n}")
    cmd = [sys.executable, str(CODE / "run_wrapper.py"), str(RUN / f"closure_m2_n{n}"),
           "--cells", f"{n}:2:2:{k}", "--families", "chained_eq5",
           "--draw-list", ",".join(str(d) for d in draws),
           "--subspaces", SUBSPACE, "--b-modes", BMODE,
           "--no-single", "--skip-f4", "--skip-f4-reason", SKIP,
           "--closure-mem-cap", str(cap), "--closure-max-cols", "200000",
           "--d-max", "4", "--controls", "none", "--resume"]
    say(f"n={n}: start (N={N} ncols={ncols} basis={basis_gb:.2f} GB cap={cap} GB draws={draws})")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=CODE, capture_output=True, text=True)
    say(f"n={n}: exit {p.returncode} after {time.time()-t0:.0f}s  {p.stdout.strip()[:200]}")
say("m2 schedule done")

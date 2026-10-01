"""Dummy job for the pre-pin exercise of run_jobs.py (TASK-20260929-89c123).
Runs NO solver and imports no engine module.  Writes synthetic census-shaped rows
(key and status fields only) for one job, with a planted behaviour:
  ok       every expected key, completed_valid
  ascap    one instance failed_infrastructure "address-space cap: MemoryError: synthetic"
  invalid  one instance invalid (exercises the M-1 run-stop rule)
  crash    the process kills itself with SIGKILL before writing anything (abnormal end)
  sleep    sleeps 20 s first (exercises the concurrency limit and the ordering)
  hog      tries to allocate 4e9 bytes (exercises the RLIMIT_AS cap from run_wrapper.py)
"""
import argparse
import json
import os
import random
import signal
import time

MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")

ap = argparse.ArgumentParser()
ap.add_argument("--bits", type=int)
ap.add_argument("--curve", type=int)
ap.add_argument("--m", type=int)
ap.add_argument("--panel")
ap.add_argument("--arm", default=None)
ap.add_argument("--behaviour", default="ok")
ap.add_argument("--out")
ap.add_argument("--rows-out")
ap.add_argument("--staircase-out")
a = ap.parse_args()
rng = random.Random(f"dummy|{a.bits}|{a.curve}|{a.arm}")
if a.behaviour == "sleep":
    time.sleep(20)
if a.behaviour == "crash":
    os.kill(os.getpid(), signal.SIGKILL)
if a.behaviour == "hog":
    try:
        x = bytearray(4_000_000_000)
    except MemoryError:
        print("MemoryError under the address-space cap (expected)")
        raise
arms = a.arm.split("+") if a.arm else list(MAIN_ARMS if a.panel == "main" else J0_ARMS)
m = a.m if a.panel == "main" else 3
rows, stairs, hrows = [], [], []
for i, arm in enumerate(arms):
    for mode in ("census", "on"):
        r = {"bits": a.bits, "curve": a.curve, "method": f"ic_m{m}", "panel": a.panel, "arm": arm,
             "mode": mode, "seconds": rng.random(), "synthetic_field": rng.randrange(10 ** 6),
             "status": "completed_valid", "status_reason": None}
        if a.behaviour == "ascap" and i == 0 and mode == "on":
            r.update(status="failed_infrastructure", status_reason="address-space cap: MemoryError: synthetic")
        if a.behaviour == "invalid" and i == 1 and mode == "census":
            r.update(status="invalid", status_reason="synthetic invalid (run-stop exercise)")
        rows.append(r)
        key = {"bits": a.bits, "curve": a.curve, "m": m, "arm": arm, "mode": mode}
        stairs.append(key | {"class": "TT", "synthetic": rng.randrange(100)})
        hrows.append(key | {"class": "SS", "synthetic": rng.randrange(100)})
if a.panel == "j0" and not a.arm:
    rows.append({"bits": a.bits, "curve": a.curve, "method": "rho", "fb": "-", "panel": "j0", "ok": True,
                 "status": "completed_valid", "status_reason": None, "seconds": rng.random()})
for path, recs in ((a.out, rows), (a.rows_out, hrows), (a.staircase_out, stairs)):
    if path:
        with open(path, "a") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
print(json.dumps({"dummy": True, "rows": len(rows)}))

"""run_generation_m5 -- the m = 5 CONTINUATION of TASK-20261002-a8bbd8's generation.

The m = 4 phase terminated by the pre-registered machine-protection stop at
rung 30 (RSS stop 2.5e9 bytes per process; peak 2737 MB within 0.6 s; the
archived construction's encoding store needs ~2.3-3.5 KB per recorded encoding
and grows ~B^2, so rungs 30 (B=151) and 32 (B=230) cannot fit under the card's
RSS stop as constructed). The stop STANDS: this continuation never relaunches
an m = 4 rung, changes no n, and re-decides nothing (a stop is blocked, never a
finding).

It executes the power rule's m = 5 condition exactly as pre-registered
(DEC-20261002-0df88e): "m = 5 on-mode is generated ONLY if at least 50% of the
wall clock remains after the m = 4 rungs complete" -- the m = 4 phase is over
(terminated by the recorded stop at 224.4 s of the generation clock), the
remaining wall clock is measured from the generation start (the first driver's
t0 in out/generation.log), and the decision is recorded with its numbers
either way. m = 5 rungs run 26, 28, 30, 32 in ascending order, one guarded
process at a time, with the same machine checks, projections (from the SAME
m's completed rungs only) and stop handling as run_generation.py. m = 5's
factor base is far smaller (B = 37..93 vs 151..230), so its projected peak RSS
(~0.3-2.4 GB) fits under the 2.5e9-byte stop; the guard enforces the limit
regardless, and a stop here too is recorded, never a finding.
"""
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
OUT = os.path.join(TASK, "out")
PY = sys.executable
GENLOG = os.path.join(OUT, "generation.log")

WALL_BUDGET_S = 21600.0
M5_THRESHOLD_S = 0.5 * WALL_BUDGET_S
ANALYSIS_RESERVE_S = 1800.0
DISK_FLOOR_KB = 1_048_576
MEM_FLOOR_BYTES = 6 * 1024 ** 3
RUNGS = (26, 28, 30, 32)
N_INST = 200
PAGE = 16384


def log(rec):
    rec["t"] = round(time.time(), 1)
    with open(GENLOG, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def generation_start_t():
    """The first driver's t0 (the generation clock's origin)."""
    start = None
    m4_stop = None
    for l in open(GENLOG):
        r = json.loads(l)
        if r.get("event") == "driver_start" and start is None:
            start = r["t"]
        if r.get("event") == "driver_stop":
            m4_stop = r
    return start, m4_stop


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_a8bbd8_m5", os.path.join(HERE, "01_generator.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def disk_free_kb():
    out = subprocess.run(["df", "-k", "/Volumes/SSD990"],
                         capture_output=True, text=True, timeout=30)
    return int(out.stdout.splitlines()[1].split()[3])


def mem_available_bytes():
    out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=30)
    counts = {}
    for line in out.stdout.splitlines():
        for key in ("Pages free", "Pages speculative", "Pages inactive"):
            if line.startswith(key + ":"):
                counts[key] = int(line.split()[-1].rstrip("."))
    return (sum(counts.values())) * PAGE, counts


def machine_checks(tag):
    free_kb = disk_free_kb()
    avail, counts = mem_available_bytes()
    log({"event": "machine_check", "tag": tag, "disk_free_kb": free_kb,
         "mem_available_estimate_bytes": avail, "mem_vm_stat_pages": counts,
         "mem_estimate_method": "macOS: (free+speculative+inactive) x 16384 B"})
    if free_kb < DISK_FLOOR_KB:
        log({"event": "STOP", "reason": "disk_free_below_floor", "tag": tag,
             "disk_free_kb": free_kb, "floor_kb": DISK_FLOOR_KB,
             "note": "a stop is blocked, never a finding; n unchanged"})
        return False
    if avail < MEM_FLOOR_BYTES:
        log({"event": "STOP", "reason": "mem_available_below_floor", "tag": tag,
             "mem_available_estimate_bytes": avail, "floor_bytes": MEM_FLOOR_BYTES,
             "note": "a stop is blocked, never a finding; n unchanged"})
        return False
    return True


def run_rung(gen, m, bits, t_gen, walls):
    if not machine_checks(f"pre_m{m}_b{bits}"):
        return False
    N = gen.rung_prime(bits)
    B = gen.default_fb_size(N, m)
    remaining = WALL_BUDGET_S - (time.time() - t_gen) - ANALYSIS_RESERVE_S
    projection = None
    basis = None
    same_m = {b: w for (mm, b), w in walls.items() if mm == m}
    if same_m:
        last_bits = max(same_m)
        B_last = gen.default_fb_size(gen.rung_prime(last_bits), m)
        projection = same_m[last_bits] * (B / B_last) ** 3
        basis = (f"last_rung_wall_s x (B_next/B_last)^3 = "
                 f"{same_m[last_bits]} x ({B}/{B_last})^3 (same m)")
    log({"event": "rung_launch", "m": m, "bits": bits, "N": N, "B": B,
         "n_instances": N_INST, "mode": "on",
         "remaining_budget_s": round(remaining, 1),
         "projected_rung_wall_s": round(projection, 1) if projection else None,
         "projection_basis": basis})
    if projection is not None and projection > remaining:
        log({"event": "STOP", "reason": "rung_projection_exceeds_budget",
             "m": m, "bits": bits, "projected_rung_wall_s": round(projection, 1),
             "remaining_budget_s": round(remaining, 1),
             "note": "a stop is blocked, never a finding; n unchanged"})
        return False
    t1 = time.time()
    r = subprocess.run([PY, os.path.join(HERE, "guard.py"),
                        f"gen_m{m}_b{bits}", "--", PY,
                        os.path.join(HERE, "01_generator.py"),
                        os.path.join(OUT, "replica_rows.jsonl"),
                        str(m), str(bits), "0", str(N_INST)],
                       capture_output=True, text=True)
    wall = time.time() - t1
    walls[(m, bits)] = wall
    log({"event": "rung_done", "m": m, "bits": bits, "exit": r.returncode,
         "wall_s": round(wall, 1), "stdout_tail": r.stdout[-500:],
         "stderr_tail": r.stderr[-800:],
         "note": "guard record (peak RSS, rss_stop_fired) in out/commands.log"})
    return r.returncode == 0


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    t_gen_start, m4_stop = generation_start_t()
    if t_gen_start is None or m4_stop is None:
        log({"event": "m5_continuation_abort",
             "reason": "generation.log missing driver_start/driver_stop"})
        return 1
    gen = load_generator()
    elapsed_gen = time.time() - t_gen_start
    remaining_after_m4 = WALL_BUDGET_S - elapsed_gen
    run_m5 = remaining_after_m4 >= M5_THRESHOLD_S
    log({"event": "m5_decision",
         "rule": "m = 5 on-mode ONLY if >= 50% of the wall clock remains after "
                 "the m = 4 rungs complete (DEC-20261002-0df88e power rule, "
                 "fixed before data)",
         "m4_phase": "terminated by the recorded RSS stop at rung 30 "
                     "(driver_stop record; rungs 26 and 28 completed 200/200; "
                     "the stop stands, no relaunch, n unchanged)",
         "generation_start_t": t_gen_start, "m4_driver_stop": m4_stop,
         "elapsed_since_generation_start_s": round(elapsed_gen, 1),
         "remaining_after_m4_s": round(remaining_after_m4, 1),
         "threshold_s": M5_THRESHOLD_S, "run_m5": run_m5})
    if not run_m5:
        log({"event": "m5_skipped", "note": "power rule condition not met"})
        return 0
    walls = {}
    for bits in RUNGS:
        if not run_rung(gen, 5, bits, t_gen_start, walls):
            log({"event": "m5_driver_stop", "at": f"m5_b{bits}",
                 "elapsed_s": round(time.time() - t_gen_start, 1)})
            return 1
    path = os.path.join(OUT, "replica_rows.jsonl")
    rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    cells = {}
    for r_ in rows:
        cells.setdefault((r_["m"], r_["bits"]), []).append(r_)
    summary = {}
    for (m, bits), rs in sorted(cells.items()):
        summary[f"m{m}|b{bits}"] = {
            "n": len(rs), "modes": sorted({x["mode"] for x in rs}),
            "primary_present": sum(1 for x in rs if x["primary"] is not None),
            "cap_hit": sum(1 for x in rs if x["attempt_cap_hit"]),
            "full_missing": sum(1 for x in rs if x["full_missing"])}
    log({"event": "generation_done", "rows_total": len(rows), "cells": summary,
         "elapsed_since_generation_start_s": round(time.time() - t_gen_start, 1)})
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

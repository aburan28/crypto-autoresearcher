"""run_generation -- the GENERATION DRIVER of TASK-20261002-a8bbd8.

Executes the power rule of DEC-20261002-0df88e (FIXED BEFORE DATA; never
re-decided here): rungs 26, 28, 30, 32 bits in ascending order, n = 200
instances per (m, rung) cell, m = 4 on-mode primary; m = 5 on-mode ONLY if at
least 50% of the wall clock (21600 s) remains after the m = 4 rungs complete
(the decision is recorded with its numbers either way). If a rung cannot
finish inside the budget (projection from the completed rungs' walls, B^3
scaling), STOP before launching it, record the stop reason (a stop is blocked,
never a finding) and do not change n. Machine protection: launch only with
>= 6 GB memory available (macOS adaptation: vm_stat free+speculative+inactive
pages, recorded -- no /proc/MemAvailable on this host); RSS stop 2.5e9 bytes
per process (code/guard.py); ONE computation process at a time (each rung is
one guarded child); disk checked before each rung (stop below 1 GiB free,
recorded); outputs under 50 MB.

Every launch goes through code/guard.py (nice 19, thread pins, RSS poll,
out/commands.log). The driver itself spawns nothing in parallel and computes
nothing heavy. NO import or execution of anything under
src/crypto_autoresearcher: the generator is the task's own adapted copy of the
red team's self-contained replica (RF-4).
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

WALL_BUDGET_S = 21600.0          # the card's wall clock
M5_THRESHOLD_S = 0.5 * WALL_BUDGET_S   # ">= 50% remains after the m=4 rungs"
ANALYSIS_RESERVE_S = 1800.0      # reserved inside the budget for the analysis
DISK_FLOOR_KB = 1_048_576        # 1 GiB free -- driver's declared stop floor
MEM_FLOOR_BYTES = 6 * 1024 ** 3  # 6 GB
RUNGS = (26, 28, 30, 32)
N_INST = 200
PAGE = 16384                    # macOS vm_stat page size on this host


def log(rec):
    rec["t"] = round(time.time(), 1)
    with open(GENLOG, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_a8bbd8", os.path.join(HERE, "01_generator.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def disk_free_kb():
    out = subprocess.run(["df", "-k", "/Volumes/SSD990"],
                         capture_output=True, text=True, timeout=30)
    return int(out.stdout.splitlines()[1].split()[3])


def mem_available_bytes():
    """macOS adaptation: no /proc/meminfo. Estimate = (free + speculative +
    inactive) pages -- all reclaimable without swap-in; recorded with the raw
    vm_stat counts every time it is checked."""
    out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=30)
    counts = {}
    for line in out.stdout.splitlines():
        for key in ("Pages free", "Pages speculative", "Pages inactive",
                    "Pages active", "Pages wired down"):
            if line.startswith(key + ":"):
                counts[key] = int(line.split()[-1].rstrip("."))
    avail = (counts["Pages free"] + counts["Pages speculative"]
             + counts["Pages inactive"]) * PAGE
    return avail, counts


def guarded(label, cmd):
    """One computation process at a time, through the guard."""
    return subprocess.run([PY, os.path.join(HERE, "guard.py"), label, "--"] + cmd,
                          capture_output=True, text=True)


def machine_checks(tag):
    free_kb = disk_free_kb()
    avail, counts = mem_available_bytes()
    rec = {"event": "machine_check", "tag": tag, "disk_free_kb": free_kb,
           "mem_available_estimate_bytes": avail,
           "mem_vm_stat_pages": counts,
           "mem_estimate_method": "macOS: (free+speculative+inactive) x 16384 B"}
    log(rec)
    if free_kb < DISK_FLOOR_KB:
        log({"event": "STOP", "reason": "disk_free_below_floor",
             "tag": tag, "disk_free_kb": free_kb, "floor_kb": DISK_FLOOR_KB,
             "note": "a stop is blocked, never a finding; n unchanged"})
        return False
    if avail < MEM_FLOOR_BYTES:
        log({"event": "STOP", "reason": "mem_available_below_floor",
             "tag": tag, "mem_available_estimate_bytes": avail,
             "floor_bytes": MEM_FLOOR_BYTES,
             "note": "a stop is blocked, never a finding; n unchanged"})
        return False
    return True


def run_rung(gen, m, bits, t0, walls):
    """One guarded rung; returns True iff it completed (exit 0).
    walls is keyed (m, bits): the projection scales only from the SAME m's
    completed rungs (m = 5 cost is not m = 4 cost)."""
    if not machine_checks(f"pre_m{m}_b{bits}"):
        return False
    N = gen.rung_prime(bits)
    B = gen.default_fb_size(N, m)
    remaining = WALL_BUDGET_S - (time.time() - t0) - ANALYSIS_RESERVE_S
    projection = None
    basis = None
    same_m = {b: w for (mm, b), w in walls.items() if mm == m}
    if same_m:
        last_bits = max(same_m)
        B_last = gen.default_fb_size(gen.rung_prime(last_bits), m)
        projection = same_m[last_bits] * (B / B_last) ** 3
        basis = (f"last_rung_wall_s x (B_next/B_last)^3 = "
                 f"{same_m[last_bits]} x ({B}/{B_last})^3 (same m)")
    rec = {"event": "rung_launch", "m": m, "bits": bits, "N": N, "B": B,
           "n_instances": N_INST, "mode": "on", "remaining_budget_s": round(remaining, 1),
           "projected_rung_wall_s": round(projection, 1) if projection else None,
           "projection_basis": basis}
    log(rec)
    if projection is not None and projection > remaining:
        log({"event": "STOP", "reason": "rung_projection_exceeds_budget",
             "m": m, "bits": bits, "projected_rung_wall_s": round(projection, 1),
             "remaining_budget_s": round(remaining, 1),
             "note": "a stop is blocked, never a finding; n unchanged "
                     "(no n change, no silent relaunch)"})
        return False
    t1 = time.time()
    r = guarded(f"gen_m{m}_b{bits}",
                [PY, os.path.join(HERE, "01_generator.py"),
                 os.path.join(OUT, "replica_rows.jsonl"),
                 str(m), str(bits), "0", str(N_INST)])
    wall = time.time() - t1
    walls[(m, bits)] = wall
    log({"event": "rung_done", "m": m, "bits": bits, "exit": r.returncode,
         "wall_s": round(wall, 1),
         "stdout_tail": r.stdout[-500:], "stderr_tail": r.stderr[-800:],
         "note": "guard record (peak RSS, rss_stop_fired) in out/commands.log"})
    return r.returncode == 0


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    gen = load_generator()
    log({"event": "driver_start", "wall_budget_s": WALL_BUDGET_S,
         "m5_threshold_s": M5_THRESHOLD_S, "analysis_reserve_s": ANALYSIS_RESERVE_S,
         "disk_floor_kb": DISK_FLOOR_KB, "mem_floor_bytes": MEM_FLOOR_BYTES,
         "rungs": list(RUNGS), "n_per_cell": N_INST, "modes": ["on"],
         "python": PY})
    if not machine_checks("pre_fidelity"):
        return 1
    # construction-fidelity check BEFORE any new rung (guarded; its internal
    # generator children are sequential and tiny (b12/b24 probes), recorded)
    t1 = time.time()
    r = guarded("fidelity_check", [PY, os.path.join(HERE, "00_fidelity_check.py")])
    log({"event": "fidelity_done", "exit": r.returncode,
         "wall_s": round(time.time() - t1, 1),
         "stdout_tail": r.stdout[-800:], "stderr_tail": r.stderr[-800:]})
    if r.returncode != 0:
        log({"event": "STOP", "reason": "fidelity_check_failed",
             "note": "construction not verified against the archive; no new "
                     "rung is generated; a stop is blocked, never a finding"})
        return 1
    # ---- m = 4 on-mode primary (the decision quantity) --------------------
    walls = {}
    for bits in RUNGS:
        if not run_rung(gen, 4, bits, t0, walls):
            log({"event": "driver_stop", "at": f"m4_b{bits}",
                 "elapsed_s": round(time.time() - t0, 1)})
            return 1
    # ---- m = 5 decision (the power rule's >= 50% condition) ---------------
    elapsed = time.time() - t0
    remaining_after_m4 = WALL_BUDGET_S - elapsed
    run_m5 = remaining_after_m4 >= M5_THRESHOLD_S
    log({"event": "m5_decision", "rule": "m = 5 on-mode ONLY if >= 50% of the "
         "wall clock remains after the m = 4 rungs complete",
         "elapsed_after_m4_s": round(elapsed, 1),
         "remaining_after_m4_s": round(remaining_after_m4, 1),
         "threshold_s": M5_THRESHOLD_S, "run_m5": run_m5})
    if run_m5:
        for bits in RUNGS:
            if not run_rung(gen, 5, bits, t0, walls):
                log({"event": "driver_stop", "at": f"m5_b{bits}",
                     "elapsed_s": round(time.time() - t0, 1)})
                return 1
    # ---- post-generation sanity -------------------------------------------
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
    log({"event": "generation_done", "rows_total": len(rows),
         "cells": summary, "elapsed_s": round(time.time() - t0, 1)})
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

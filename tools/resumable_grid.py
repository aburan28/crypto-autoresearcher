#!/usr/bin/env python3
"""Resumable, per-instance-checkpointing grid runner for timed experiments.

Why: cloud sessions can lose background processes (see docs/long-runs-in-cloud-sessions.md). The
EXP-ECDLP-* launchers write a whole cell at once, so a lost process loses the cell. This runner
appends each finished instance to the output file immediately (flush + fsync) and, when started on an
existing output file, skips instances already recorded, so a recycle loses at most the instances in
flight.

Compatible with the plan format of experiments/EXP-ECDLP-20a588/block_order_grid.py:
    {"seed": str, "timeout_s": int, "planted_per_cell": int, "random_per_cell": int,
     "arms": [...], "L_by_m": {"3": [3, 4, 5], ...}}
and with its per-instance seed (sha256 of "seed|m|L|inst"), so a grid ported to this runner draws the
same instances. `run_instance(job) -> dict` must be a picklable module-level function returning a row
with "results": {arm: {"status": "ok" | "timeout" | ...}}; the row is stored as given plus the job keys.

Stopping rule (same as the frozen launchers): an arm whose results are "timeout" on EVERY instance of
a cell is not run at larger L for that m. The rule is recomputed from the stored rows on resume, so a
resumed run makes the same decisions an uninterrupted one would.

Measurement caveat: timings are only comparable between runs on the same host load. Resuming changes
no measurement, but do not share the cores with another timed run.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Dict, List, Tuple


def instance_seed(plan_seed: str, m: int, L: int, inst: int) -> int:
    """Same derivation as block_order_grid.py / msolve_grid.py / pkm_isogeny_fb.py."""
    return int(hashlib.sha256(f"{plan_seed}|{m}|{L}|{inst}".encode()).hexdigest()[:12], 16)


def load_rows(path: str) -> Tuple[List[dict], int]:
    """(rows already recorded, byte offset just past the last complete row).

    A truncated or corrupt tail (the process was killed mid-write) is not an error: it is excluded from
    the rows and the caller truncates the file to the returned offset before appending, so a half-written
    line can never merge with the next row."""
    rows: List[dict] = []
    good_end = 0
    if not os.path.exists(path):
        return rows, 0
    with open(path, "rb") as fh:
        for raw in fh:
            if not raw.endswith(b"\n"):
                break                                       # no trailing newline: written incompletely
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError:
                break
            good_end += len(raw)
    return rows, good_end


def _retired(rows_in_cell: List[dict], arms: List[str]) -> List[str]:
    out = []
    for arm in arms:
        got = [r["results"].get(arm, {}).get("status") for r in rows_in_cell]
        if got and all(s == "timeout" for s in got):
            out.append(arm)
    return out


def _append(path: str, row: dict) -> None:
    with open(path, "a") as fh:
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def run_grid(plan: dict, run_instance: Callable[[dict], dict], out_path: str, workers: int = 4,
             log: Callable[[str], None] = print) -> Dict[str, int]:
    """Run (or resume) the grid. Returns counts: {"executed", "skipped"}."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    done, good_end = load_rows(out_path)
    if os.path.exists(out_path) and os.path.getsize(out_path) > good_end:
        os.truncate(out_path, good_end)                     # drop a half-written tail before appending
    have: Dict[Tuple[int, int, int], dict] = {(r["m"], r["L"], r["inst"]): r for r in done}
    n_inst = plan["planted_per_cell"] + plan["random_per_cell"]
    executed = skipped = 0
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for m_key, Ls in sorted(plan["L_by_m"].items(), key=lambda kv: int(kv[0])):
            m = int(m_key)
            arms = list(plan["arms"])
            for L in Ls:
                if not arms:
                    break
                jobs = []
                for inst in range(n_inst):
                    if (m, L, inst) in have:
                        skipped += 1
                        continue
                    kind = "planted" if inst < plan["planted_per_cell"] else "random"
                    jobs.append(dict(m=m, L=L, inst=inst, kind=kind, timeout=plan["timeout_s"], arms=list(arms),
                                     seed=instance_seed(plan["seed"], m, L, inst)))
                for fut in as_completed([ex.submit(run_instance, j) for j in jobs]):
                    row = fut.result()
                    _append(out_path, row)                      # checkpoint immediately
                    have[(row["m"], row["L"], row["inst"])] = row
                    executed += 1
                    log(f"m={m} L={L} inst={row['inst']} " +
                        " ".join(f"{k}:{v.get('status')}" for k, v in row["results"].items()))
                cell = [have[(m, L, i)] for i in range(n_inst) if (m, L, i) in have]
                for arm in _retired(cell, arms):
                    arms.remove(arm)
                    log(f"stop: arm {arm} retired at m={m} L={L}")
    log(json.dumps(dict(executed=executed, skipped=skipped, elapsed_s=round(time.time() - t0, 1),
                        python=platform.python_version())))
    return {"executed": executed, "skipped": skipped}

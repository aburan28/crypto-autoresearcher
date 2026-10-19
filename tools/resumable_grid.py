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

Checkpoint trust: before anything is skipped, truncated or appended, every stored row is validated against
the plan (seed, kind, timeout, scheduled arms, per-arm results; duplicate or out-of-grid identities; rows after
an incomplete cell or in a retired cell). A mismatch raises CheckpointError and leaves the file untouched; only an
incomplete final line (no trailing newline) is recovered, while a malformed complete record is corruption and
raises. Rows returned by the callback are validated against their job before they are appended.

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


class CheckpointError(ValueError):
    """The stored checkpoint (or a returned row) cannot be trusted. Raised before anything is modified."""


def load_rows(path: str) -> Tuple[List[dict], int]:
    """(rows already recorded, byte offset just past the last complete row).

    Only an INCOMPLETE FINAL LINE (no trailing newline: the process was killed mid-write) is recoverable:
    it is excluded from the rows and the caller truncates the file to the returned offset before appending,
    so a half-written line can never merge with the next row. A complete (newline-terminated) record that
    is not valid JSON is corruption, not a crash tail: raise instead of silently discarding what follows."""
    rows: List[dict] = []
    good_end = 0
    if not os.path.exists(path):
        return rows, 0
    with open(path, "rb") as fh:
        for raw in fh:
            if not raw.endswith(b"\n"):
                break                                       # incomplete final line
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as e:
                raise CheckpointError(f"{path}: corrupt complete record at byte {good_end}: {e}") from e
            good_end += len(raw)
    return rows, good_end


def _cells(plan: dict) -> List[Tuple[int, List[int]]]:
    return [(int(m), list(Ls)) for m, Ls in sorted(plan["L_by_m"].items(), key=lambda kv: int(kv[0]))]


def _expected_job(plan: dict, m: int, L: int, inst: int, arms: List[str]) -> dict:
    return dict(m=m, L=L, inst=inst, kind="planted" if inst < plan["planted_per_cell"] else "random",
                timeout=plan["timeout_s"], arms=list(arms), seed=instance_seed(plan["seed"], m, L, inst))


def check_row(row: object, job: dict, where: str) -> None:
    """Raise CheckpointError unless `row` is what `job` should have produced: every job field equal
    (identity, seed, kind, timeout, scheduled arms) and a status for exactly the scheduled arms."""
    if not isinstance(row, dict):
        raise CheckpointError(f"{where}: record is not an object")
    for k, want in job.items():
        if k not in row or type(row[k]) is not type(want) or row[k] != want:
            raise CheckpointError(f"{where}: {k} is {row.get(k)!r}, expected {want!r}")
    res = row.get("results")
    if not isinstance(res, dict) or set(res) != set(job["arms"]):
        raise CheckpointError(f"{where}: results cover {sorted(res) if isinstance(res, dict) else res!r}, "
                              f"scheduled arms are {job['arms']}")
    for arm, v in res.items():
        if not isinstance(v, dict) or not isinstance(v.get("status"), str):
            raise CheckpointError(f"{where}: result for arm {arm} has no string status")


def validate_checkpoint(plan: dict, rows: List[dict]) -> Dict[Tuple[int, int, int], dict]:
    """Check every stored row against the plan before anything is skipped or truncated.

    Rejects: non-object or unidentified records, duplicate (m, L, inst), rows outside the grid or in a cell
    the stopping rule had already retired, rows after an incomplete cell (the runner works cell by cell),
    and any row whose seed, kind, timeout, scheduled arms or per-arm results differ from what the plan and the
    stopping rule (replayed from the stored rows) require. Returns the rows keyed by (m, L, inst)."""
    index: Dict[Tuple[int, int, int], dict] = {}
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or not all(isinstance(r.get(k), int) for k in ("m", "L", "inst")):
            raise CheckpointError(f"record {i} has no integer m, L, inst")
        key = (r["m"], r["L"], r["inst"])
        if key in index:
            raise CheckpointError(f"duplicate record for (m, L, inst) = {key}")
        index[key] = r
    n_inst = plan["planted_per_cell"] + plan["random_per_cell"]
    used = set()
    incomplete = False
    for m, Ls in _cells(plan):
        arms = list(plan["arms"])
        for L in Ls:
            stored = [(i, index[(m, L, i)]) for i in range(n_inst) if (m, L, i) in index]
            if not arms:
                if stored:
                    raise CheckpointError(f"rows exist for (m, L) = ({m}, {L}), a cell the stopping rule had retired")
                break
            if stored and incomplete:
                raise CheckpointError(f"rows exist for (m, L) = ({m}, {L}) after an incomplete earlier cell")
            for i, r in stored:
                check_row(r, _expected_job(plan, m, L, i, arms), f"record (m, L, inst) = ({m}, {L}, {i})")
                used.add((m, L, i))
            if len(stored) < n_inst:
                incomplete = True
            else:
                for arm in _retired([r for _, r in stored], arms):
                    arms.remove(arm)
    extra = sorted(set(index) - used)
    if extra:
        raise CheckpointError(f"rows outside the grid or its schedule: {extra[:5]}")
    return index


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
    """Run (or resume) the grid. Returns counts: {"executed", "skipped"}.

    Nothing is modified until the stored checkpoint has been validated against the plan
    (CheckpointError otherwise); each returned row is validated against its job before it is appended."""
    rows, good_end = load_rows(out_path)                    # raises on a corrupt complete record
    have = validate_checkpoint(plan, rows)                  # raises on identity / parameter / schedule mismatch
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    if os.path.exists(out_path) and os.path.getsize(out_path) > good_end:
        os.truncate(out_path, good_end)                     # drop ONLY an incomplete final line
    n_inst = plan["planted_per_cell"] + plan["random_per_cell"]
    executed = skipped = 0
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for m, Ls in _cells(plan):
            arms = list(plan["arms"])
            for L in Ls:
                if not arms:
                    break
                jobs = {}
                for inst in range(n_inst):
                    if (m, L, inst) in have:
                        skipped += 1
                        continue
                    jobs[inst] = _expected_job(plan, m, L, inst, arms)
                for fut in as_completed([ex.submit(run_instance, j) for j in jobs.values()]):
                    row = fut.result()
                    inst = row.get("inst") if isinstance(row, dict) else None
                    if inst not in jobs:
                        raise CheckpointError(f"callback returned a row for an unscheduled instance: {inst!r}")
                    check_row(row, jobs.pop(inst), f"callback row (m, L, inst) = ({m}, {L}, {inst})")
                    _append(out_path, row)                      # checkpoint immediately
                    have[(m, L, inst)] = row
                    executed += 1
                    log(f"m={m} L={L} inst={inst} " +
                        " ".join(f"{k}:{v.get('status')}" for k, v in row["results"].items()))
                cell = [have[(m, L, i)] for i in range(n_inst) if (m, L, i) in have]
                for arm in _retired(cell, arms):
                    arms.remove(arm)
                    log(f"stop: arm {arm} retired at m={m} L={L}")
    log(json.dumps(dict(executed=executed, skipped=skipped, elapsed_s=round(time.time() - t0, 1),
                        python=platform.python_version())))
    return {"executed": executed, "skipped": skipped}

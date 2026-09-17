#!/usr/bin/env python3
"""f4_trace.py -- Semaev-commensurable F4 step-degree trace via msolve.

msolve (Berthomieu, Eder, Safey El Din) implements Faugere's F4 with pair
selection by degree: every round selects all critical pairs of the current
minimal degree, builds the Macaulay-type matrix, reduces it, and adds the new
basis elements.  With `-v 2` it prints one line per round:

    deg  sel  pairs  mat(rows x cols)  density  new  zero  time

`deg` is the degree of the pairs selected in that round -- the same quantity
MAGMA's F4 verbosity calls the "step degree" and Semaev reads d_F4 from
(KN-LIT-fa346d Section 4.5.1).  Two readings are recorded per run:

  d_F4_semaev : max `deg` over the rounds up to and including the LAST round
                that added at least one new basis element.  Rounds after it that
                add nothing are the "No pairs to reduce" tail Semaev excludes.
  d_F4_naive  : max `deg` over every round, tail included.

Field equations are explicit generators (Section 4.5.1: "n(t-2)+kt field
equations are added"), so the convention is `explicit_generators`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import subprocess
import time
from pathlib import Path

ROUND_RE = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+x\s+(\d+)\s+([\d.]+)%\s+(\d+)\s+new\s+(\d+)\s+zero\s+([\d.]+)\s*\|\s*([\d.]+)")
QUOT_RE = re.compile(r"Dimension of quotient:\s*(\d+)")
BASIS_RE = re.compile(r"#length of basis:\s*(\d+)")


def msolve_version() -> str:
    try:
        out = subprocess.run(["msolve", "-h"], capture_output=True, text=True, timeout=20)
        m = re.search(r"msolve\s+([\d.]+)", out.stdout + out.stderr)
        return m.group(1) if m else (out.stdout.splitlines() or ["?"])[0].strip()
    except Exception as exc:  # pragma: no cover
        return f"unknown ({exc})"


def _limits(mem_bytes: int):
    def fn():
        if mem_bytes:
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return fn


def run_msolve(ms_path: Path, out_path: Path, wall_cap_s: float, mem_cap_gb: float,
               threads: int = 1) -> dict:
    cmd = ["msolve", "-v", "2", "-g", "2", "-t", str(threads), "-f", str(ms_path), "-o", str(out_path)]
    t0 = time.time()
    status = "completed"
    stdout = ""
    stderr = ""
    rc = None
    peak_rss = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                preexec_fn=_limits(int(mem_cap_gb * (1 << 30))))
        try:
            stdout, stderr = proc.communicate(timeout=wall_cap_s)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            rc = proc.returncode
            status = "unreached_wall_cap"
        ru = resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_rss = ru.ru_maxrss * 1024
    except Exception as exc:
        status = "launch_error"
        stderr = repr(exc)
    wall = time.time() - t0
    if status == "completed" and rc not in (0,):
        status = "unreached_memory_cap" if ("alloc" in (stderr + stdout).lower() or rc in (-9, 134, 137)) else f"failed_rc_{rc}"
    rounds = []
    for line in stdout.splitlines():
        m = ROUND_RE.match(line)
        if m:
            rounds.append({
                "deg": int(m.group(1)), "sel": int(m.group(2)), "pairs": int(m.group(3)),
                "rows": int(m.group(4)), "cols": int(m.group(5)), "density_pct": float(m.group(6)),
                "new": int(m.group(7)), "zero": int(m.group(8)),
                "real_s": float(m.group(9)), "cpu_s": float(m.group(10)),
            })
    quot = QUOT_RE.search(stdout)
    quotient_dim = int(quot.group(1)) if quot else None
    basis_len = None
    basis_is_unit = None
    if out_path.exists():
        txt = out_path.read_text()
        mb = BASIS_RE.search(txt)
        basis_len = int(mb.group(1)) if mb else None
        basis_is_unit = ("[1]:" in txt) and (basis_len == 1)
        if basis_is_unit:
            quotient_dim = 0
    d_naive = max((r["deg"] for r in rounds), default=None)
    last_prod = max((i for i, r in enumerate(rounds) if r["new"] > 0), default=None)
    d_semaev = max((r["deg"] for r in rounds[: last_prod + 1]), default=None) if last_prod is not None else (0 if rounds == [] and status == "completed" else None)
    tail = [r["deg"] for r in rounds[(last_prod + 1 if last_prod is not None else 0):]]
    return {
        "engine": "msolve", "engine_version": msolve_version(), "command": " ".join(cmd),
        "field_equation_convention": "explicit_generators",
        "status": status, "exit_code": rc, "wall_s": wall, "peak_rss_bytes": peak_rss,
        "rounds": rounds, "f4_step_count": len(rounds),
        "d_F4_semaev": d_semaev if status == "completed" else None,
        "d_F4_naive": d_naive if status == "completed" else None,
        "d_F4_partial_max_deg_seen": d_naive,
        "f4_empty_step_degrees": tail if status == "completed" else None,
        "quotient_dimension": quotient_dim if status == "completed" else None,
        "basis_length": basis_len, "ideal_is_unit": basis_is_unit,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stdout": stdout, "stderr": stderr[-4000:],
    }

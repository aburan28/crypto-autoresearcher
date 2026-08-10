"""Subprocess-isolated, hard-capped Groebner solve calls.

Faithfully implements the frozen specification's "per-solve cap 20 s; capped
solves count at full cap cost as failures" (CTRL-FAILED-DESCENT): a bare
in-process `sympy.groebner(...)` call has no timeout of its own, so a call
that would take (say) 39 seconds would either blow the run's wall-clock
budget or have to be reported dishonestly as "20 seconds" without actually
having been capped. subprocess.run(timeout=CAP_SECONDS) sends a real
OS-level kill at the cap, which is the only way to make the stated cap true
of what actually ran.

A calibration in implementation.md shows sympy's Buchberker routine on these
degree-B' indicator-polynomial systems commonly exceeds 20s well before B'
reaches values this experiment's grid can produce (S3/arity-2 ~B'>=150-170,
S4/arity-3 ~B'>=24-32) -- so capped outcomes are an expected, real, honestly
measured phenomenon here, not a bug in this wrapper.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time

CAP_SECONDS = 20.0
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gb_worker.py")


def capped_solve(arity: int, p: int, a: int, b: int, V: list[int],
                  target_x: int, cap_seconds: float = CAP_SECONDS) -> dict:
    """Run ONE Groebner-basis decomposition-cost measurement in a fresh,
    hard-killed subprocess. Always returns within cap_seconds + small
    process-spawn overhead (recorded separately as wall_seconds).

    Returns a dict with at minimum:
      status: "completed" | "capped" | "crashed"
      groebner_seconds: float   -- the solver's own measured time if
                                    "completed"; else cap_seconds (charged at
                                    full cap cost, never left null/guessed)
      wall_seconds: float       -- parent-observed wall time for the call
      is_trivial_ideal: bool | None
      basis_size / basis_max_degree: int | None
    """
    job = {"arity": arity, "p": p, "a": a, "b": b, "V": list(V), "target_x": target_x}
    t0 = time.perf_counter()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as jf:
        json.dump(job, jf)
        job_path = jf.name
    try:
        try:
            proc = subprocess.run(
                [sys.executable, WORKER, job_path],
                timeout=cap_seconds, capture_output=True, text=True,
            )
        except subprocess.TimeoutExpired as exc:
            wall = time.perf_counter() - t0
            return {
                "status": "capped", "groebner_seconds": cap_seconds,
                "wall_seconds": wall, "is_trivial_ideal": None,
                "basis_size": None, "basis_max_degree": None,
                "reason": f"exceeded {cap_seconds}s per-solve cap "
                          f"(subprocess killed by OS-level timeout)",
                "stdout_partial": (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, (bytes, bytearray)) else (exc.stdout or ""),
            }
        wall = time.perf_counter() - t0
        if proc.returncode != 0:
            return {
                "status": "crashed", "groebner_seconds": cap_seconds,
                "wall_seconds": wall, "is_trivial_ideal": None,
                "basis_size": None, "basis_max_degree": None,
                "reason": f"worker exited {proc.returncode} within the cap "
                          f"(charged at full cap cost per CTRL-FAILED-DESCENT)",
                "stderr_tail": (proc.stderr or "")[-4000:],
            }
        try:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError) as exc:
            return {
                "status": "crashed", "groebner_seconds": cap_seconds,
                "wall_seconds": wall, "is_trivial_ideal": None,
                "basis_size": None, "basis_max_degree": None,
                "reason": f"worker produced unparseable output: {exc}",
                "stdout_tail": (proc.stdout or "")[-2000:],
                "stderr_tail": (proc.stderr or "")[-2000:],
            }
        result["status"] = "completed"
        result["wall_seconds"] = wall
        return result
    finally:
        try:
            os.unlink(job_path)
        except OSError:
            pass

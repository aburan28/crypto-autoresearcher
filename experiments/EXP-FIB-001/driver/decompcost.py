"""S_4 (m=3) Groebner-basis decomposition-cost measurement, with a hard
per-solve wall-clock cap enforced by killing a subprocess (sympy's Buchberger
routine cannot be interrupted cooperatively). Failures and capped solves are
counted at the full cap cost, per the frozen spec's decomposition_cost
definition -- this is NOT an infrastructure failure, it is the measured cost.

Group-operation-equivalent conversion: we report groebner_seconds (the raw
implementation-bound proxy, honestly labeled per harness/semaev.py's honesty
note) alongside a cost-in-group-operation-equivalents figure obtained via the
frozen rho calibration for the same curve (measured group operations per
second of the matched rho baseline on this machine), so costs are on a common
scale without conflating wall-clock with group operations (baseline
discipline, docs/evidence-and-reproducibility.md).
"""
from __future__ import annotations

import multiprocessing as mp
import time

import sympy

from harness.semaev import s4_expr, x1, x2, x3

PER_SOLVE_CAP_SECONDS = 20.0


def _worker(p: int, a: int, b: int, V: list[int], xR: int, q: "mp.Queue") -> None:
    try:
        S4 = s4_expr(a, b)
        x4 = sympy.symbols("x4")
        S4_at_R = S4.subs(x4, xR)
        fV1 = sympy.prod([(x1 - v) for v in V])
        fV2 = sympy.prod([(x2 - v) for v in V])
        fV3 = sympy.prod([(x3 - v) for v in V])
        system = [S4_at_R, fV1, fV2, fV3]
        t0 = time.perf_counter()
        G = sympy.groebner(system, x1, x2, x3, modulus=p, order="grevlex")
        gb_seconds = time.perf_counter() - t0
        polys = list(G.exprs)
        max_deg = 0
        for g in polys:
            try:
                d = sympy.Poly(g, x1, x2, x3, modulus=p).total_degree()
            except sympy.PolynomialError:
                d = 0
            max_deg = max(max_deg, d)
        is_trivial = polys == [sympy.Integer(1)] or (len(polys) == 1 and polys[0] == 1)
        q.put({"ok": True, "groebner_seconds": gb_seconds,
               "groebner_basis_size": len(polys), "groebner_basis_max_degree": max_deg,
               "is_trivial_ideal": bool(is_trivial)})
    except Exception as e:  # noqa: BLE001 -- must not crash the parent
        q.put({"ok": False, "error": repr(e)})


def measure_s4_decomposition(p: int, a: int, b: int, V: list[int], xR: int,
                              cap_seconds: float = PER_SOLVE_CAP_SECONDS) -> dict:
    """Run the S_4 Groebner decomposition test for one target under a hard cap.

    Returns dict with keys: capped (bool), cost_seconds (wall clock charged,
    == cap_seconds if capped), groebner_basis_size, groebner_basis_max_degree,
    is_trivial_ideal, worker_error (str|None).
    """
    ctx = mp.get_context("spawn")
    q: mp.Queue = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(p, a, b, V, xR, q))
    t0 = time.perf_counter()
    proc.start()
    proc.join(timeout=cap_seconds)
    wall = time.perf_counter() - t0
    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=2)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=2)
        return {"capped": True, "cost_seconds": cap_seconds,
                "groebner_basis_size": None, "groebner_basis_max_degree": None,
                "is_trivial_ideal": None, "worker_error": None,
                "wall_seconds_observed": wall}
    try:
        result = q.get_nowait()
    except Exception:
        result = {"ok": False, "error": "no result returned before process exit"}
    if not result.get("ok"):
        return {"capped": True, "cost_seconds": cap_seconds,
                "groebner_basis_size": None, "groebner_basis_max_degree": None,
                "is_trivial_ideal": None, "worker_error": result.get("error"),
                "wall_seconds_observed": wall}
    return {"capped": False, "cost_seconds": min(result["groebner_seconds"], cap_seconds),
            "groebner_basis_size": result["groebner_basis_size"],
            "groebner_basis_max_degree": result["groebner_basis_max_degree"],
            "is_trivial_ideal": result["is_trivial_ideal"], "worker_error": None,
            "wall_seconds_observed": wall}

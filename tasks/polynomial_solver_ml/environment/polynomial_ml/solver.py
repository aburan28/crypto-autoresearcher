"""A bounded subprocess measurement, with a vectorized basis-grid root solver."""

from __future__ import annotations

import resource
import sys
import time
from statistics import median

import numpy as np
import sympy as sp

from .instances import validate_case

ACTIONS = (
    {"method": "buchberger", "order": "lex"},
    {"method": "f5b", "order": "lex"},
    {"method": "buchberger", "order": "grevlex"},
    {"method": "f5b", "order": "grevlex"},
)


def basis_roots(basis, p):
    # Reduce at every multiplication; avoid integer overflow even for a large
    # intermediate exponent. This path is separate from the scalar oracle.
    xx = np.repeat(np.arange(p, dtype=np.int64), p)
    yy = np.tile(np.arange(p, dtype=np.int64), p)
    mask = np.ones(p * p, dtype=bool)
    for poly in basis.polys:
        values = np.zeros(p * p, dtype=np.int64)
        for (a, b), coeff in poly.terms():
            term = np.full(p * p, int(coeff) % p, dtype=np.int64)
            for _ in range(a):
                term = term * xx % p
            for _ in range(b):
                term = term * yy % p
            values = (values + term) % p
        mask &= values == 0
    return np.column_stack((xx[mask], yy[mask])).tolist()


def solve_case(case, action_id, repetitions):
    validate_case(case)
    if type(action_id) is not int or not 0 <= action_id < len(ACTIONS):
        raise ValueError("unknown solver action")
    if type(repetitions) is not int or not 1 <= repetitions <= 3:
        raise ValueError("repetitions must be between 1 and 3")
    if sys.platform.startswith("linux"):
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    p = case["prime"]
    x, y = sp.symbols("x y")
    timings = []
    roots = None
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        polynomials = [sum(c * x**a * y**b for c, a, b in poly) for poly in case["polynomials"]]
        built = time.perf_counter_ns()
        basis = sp.groebner(polynomials, x, y, modulus=p, **ACTIONS[action_id])
        reduced = time.perf_counter_ns()
        current_roots = basis_roots(basis, p)
        finished = time.perf_counter_ns()
        if roots is not None and roots != current_roots:
            raise RuntimeError("roots changed between repetitions")
        roots = current_roots
        timings.append({"construction_seconds": (built - start) / 1e9,
                        "groebner_seconds": (reduced - built) / 1e9,
                        "root_seconds": (finished - reduced) / 1e9,
                        "total_seconds": (finished - start) / 1e9})
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss if sys.platform == "darwin" else rss * 1024)
    if rss_bytes > 2 * 1024**3:
        raise MemoryError("observed subprocess RSS exceeds 2 GiB")
    return {"case_id": case["id"], "action_id": action_id, "status": "completed",
            "cost_seconds": median(t["total_seconds"] for t in timings),
            "timings": timings, "roots": roots, "root_count": len(roots),
            "basis_size": len(basis.polys),
            "output_basis_max_degree": max(int(poly.total_degree()) for poly in basis.polys),
            "is_zero_dimensional": bool(basis.is_zero_dimensional),
            "peak_rss_bytes": rss_bytes,
            "memory_limit_mode": "RLIMIT_AS" if sys.platform.startswith("linux") else "observed_RSS",
            "intermediate_degree_measured": False,
            "scope": "Output basis degree is not intermediate degree or degree of regularity."}

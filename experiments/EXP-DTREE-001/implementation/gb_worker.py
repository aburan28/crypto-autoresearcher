#!/usr/bin/env python3
"""Standalone Groebner-basis worker: ONE decomposition-cost measurement per
process invocation.

Invoked exclusively via subprocess by gb_isolated.py, which enforces the
20-second per-solve cap at the OS level (subprocess.run(timeout=...), a hard
kill, not cooperative). This script never enforces its own timeout -- it
would have no way to interrupt sympy's C-level Buchberger reduction loop
from inside the same process, which is exactly why the cap has to be
external. If this process is killed mid-computation, gb_isolated.py records
that as a capped solve at full cap cost (CTRL-FAILED-DESCENT), never as a
crash and never as a negative_observation.

Reads a JSON job spec from the file named in argv[1]:
    {"arity": 2 | 3, "p": int, "a": int, "b": int, "V": [int, ...],
     "target_x": int}
and prints one JSON result line to stdout:
    {"groebner_seconds": float, "basis_size": int, "basis_max_degree": int,
     "is_trivial_ideal": bool}
"""
from __future__ import annotations

import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # this dir, for semaev_fix

import sympy  # noqa: E402
from harness.semaev import s3_expr, x1, x2, x3  # noqa: E402
from semaev_fix import s4_expr_fixed  # noqa: E402 -- see semaev_fix.py: harness.semaev.s4_expr
                                       # has a confirmed variable-collision bug; this experiment
                                       # uses the corrected local construction instead.


def main() -> int:
    with open(sys.argv[1]) as f:
        job = json.load(f)
    arity = job["arity"]
    p, a, b = job["p"], job["a"], job["b"]
    V = job["V"]
    xR = job["target_x"]

    fV1 = sympy.prod([(x1 - v) for v in V])
    fV2 = sympy.prod([(x2 - v) for v in V])

    if arity == 2:
        system = [s3_expr(a, b).subs(x3, xR), fV1, fV2]
        gens = (x1, x2)
    elif arity == 3:
        x4 = sympy.symbols("x4")
        S4 = s4_expr_fixed(a, b)
        fV3 = sympy.prod([(x3 - v) for v in V])
        system = [S4.subs(x4, xR), fV1, fV2, fV3]
        gens = (x1, x2, x3)
    else:
        raise ValueError(f"unsupported arity {arity}")

    t0 = time.perf_counter()
    G = sympy.groebner(system, *gens, modulus=p, order="grevlex")
    gb_seconds = time.perf_counter() - t0

    polys = list(G.exprs)
    max_deg = 0
    for g in polys:
        try:
            d = sympy.Poly(g, *gens, modulus=p).total_degree()
        except sympy.PolynomialError:
            d = 0
        max_deg = max(max_deg, d)
    is_trivial = polys == [sympy.Integer(1)] or (len(polys) == 1 and polys[0] == 1)

    print(json.dumps({
        "groebner_seconds": gb_seconds,
        "basis_size": len(polys),
        "basis_max_degree": max_deg,
        "is_trivial_ideal": bool(is_trivial),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())

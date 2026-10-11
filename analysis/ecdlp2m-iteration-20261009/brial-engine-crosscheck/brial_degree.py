"""BRiAl (PolyBoRi) Groebner-basis step-degree probe for Boolean systems.

Runs pbori.groebner_basis(..., prot=True), captures the protocol, and returns
  max_step_degree  = max over 'Current Degree: d' lines (the degree of the
                     S-polynomials being reduced in each round; the engine's
                     analogue of an F4 step degree),
  degrees          = the sequence of Current Degree values in order,
  unsat            = whether the reduced basis is [1],
  gb_size, maxdeg_gb, wall_s.
Input: a list of Boolean polynomials given as lists of monomials, each monomial
a tuple/list of variable indices (empty tuple = constant 1), over N variables.
Requires the passagemath-brial venv python (sage.rings.polynomial.pbori).
"""
from __future__ import annotations
import io, re, sys, time, contextlib, os

_CUR = re.compile(r"Current Degree:\s*(\d+)")


def _ring(N):
    from sage.rings.polynomial.pbori.pbori import BooleanPolynomialRing
    return BooleanPolynomialRing(N, "x")


def to_pbori(system, N):
    R = _ring(N)
    x = R.gens()
    polys = []
    for eq in system:
        p = R(0)
        for mono in eq:
            t = R(1)
            for v in mono:
                t = t * x[v]
            p = p + t
        polys.append(p)
    return R, polys


def _capture_fd(fd, fn):
    """Capture C-level writes to file descriptor fd while fn() runs."""
    r, w = os.pipe()
    saved = os.dup(fd)
    os.dup2(w, fd)
    os.close(w)
    chunks = []
    import threading
    def reader():
        while True:
            b = os.read(r, 65536)
            if not b:
                break
            chunks.append(b)
    th = threading.Thread(target=reader); th.start()
    try:
        out = fn()
    finally:
        os.dup2(saved, fd); os.close(saved)
    th.join(); os.close(r)
    return out, b"".join(chunks).decode(errors="replace")


def step_degree(system, N, **gb_opts):
    import sage.rings.polynomial.pbori as pb
    R, polys = to_pbori(system, N)
    t0 = time.time()
    # protocol goes to C stdout; capture fd 1 and fd 2
    def run():
        return pb.groebner_basis(polys, prot=True, **gb_opts)
    (G, log1) = _capture_fd(1, run)
    wall = time.time() - t0
    degs = [int(m.group(1)) for m in _CUR.finditer(log1)]
    Gl = list(G)
    unsat = len(Gl) == 1 and str(Gl[0]) == "1"
    return {
        "max_step_degree": max(degs) if degs else None,
        "degrees": degs,
        "unsat": unsat,
        "gb_size": len(Gl),
        "maxdeg_gb": max((g.deg() for g in Gl), default=0),
        "wall_s": wall,
    }


if __name__ == "__main__":
    # smoke test: x0x1 + x2 + 1, x1x2x3 + x0, x3x4 + x5, x0+x1+x4+1, x2x5 + x3 + x1  (+ '1' for UNSAT)
    S = [[(0, 1), (2,), ()], [(1, 2, 3), (0,)], [(3, 4), (5,)], [(0,), (1,), (4,), ()], [(2, 5), (3,), (1,)]]
    print(step_degree(S, 6))
    print(step_degree(S + [[()]], 6))

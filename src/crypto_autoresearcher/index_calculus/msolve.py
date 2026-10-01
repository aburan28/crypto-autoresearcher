"""Algebraic point decomposition with msolve (F4 Groebner bases over F_p).

For a target R and arity m the decomposition system is, in the variables
x_1..x_m (the x-coordinates), u_1..u_{m-2} (partial sums) and z:

    f(x_i) = 0                                 membership, i = 1..m
    S_3(x_1, x_2, u_1) = 0,  S_3(u_k, x_{k+2}, u_{k+1}) = 0,
    S_3(u_{m-2}, x_m, x(R)) = 0                (just S_3(x_1, x_2, x(R)) for m = 2)
    z - sum c_v v = 0                          random separating form

f is the factor base's membership polynomial (``FactorBase.membership_poly``).
Chaining S_3 through the u_k is Semaev's own presentation (ePrint 2015/310)
and avoids forming S_{m+1}.  msolve returns a rational parametrization in z;
its F_p-roots give the F_p-rational solutions, each of which is lifted to
factor-base points, signed and verified by point addition.

The separating variable is added here, and msolve runs with ``-c 0``, because
msolve 0.6.5's own fallback (a random linear form in an extra variable) was
observed to drop solutions on a four-point system over F_101; with ``-c 0`` a
non-separating form is reported as a failure and retried with fresh
coefficients instead.

msolve is an external binary: set CRYPTO_AR_MSOLVE to its path or put it on
PATH (Debian/Ubuntu: apt install msolve).  The engine refuses p >= 2^16 by
default.  The Ubuntu 24.04 package (msolve 0.6.5-1build2) was observed to be
wrong above that bound: it segfaults on the m = 2 decomposition system at
p = 260317 (with -P 1 and with -g 2), segfaults on {x1^2 - 1, x2^2 - 1} at
p = 65537 and 2^31 - 1, and returns the basis {x1 - 2} for the inconsistent
system {x1 - 1, x1 - 2} at p = 65537.  Below 2^16 (a separate 16-bit
arithmetic path) the same checks pass.  With a build known to be sound, raise
the bound with CRYPTO_AR_MSOLVE_MAX_P (msolve's own limit is 2^31).
"""

from __future__ import annotations

import ast
import itertools
import os
import random
import shutil
import statistics
import subprocess
import tempfile
import time
from dataclasses import dataclass, field

from . import polyfp
from .curve import Curve, Point
from .decompose import canonical, verify
from .factor_base import FactorBase

MAX_P = 1 << 16
Poly = dict[tuple[int, ...], int]


def msolve_path() -> str | None:
    return os.environ.get("CRYPTO_AR_MSOLVE") or shutil.which("msolve")


def max_p() -> int:
    return int(os.environ.get("CRYPTO_AR_MSOLVE_MAX_P", MAX_P))


def available() -> bool:
    return msolve_path() is not None


# -- building the system ------------------------------------------------------

def s3_terms(a: int, b: int) -> list[tuple[tuple[int, int, int], int]]:
    """S_3(x1, x2, x3) as (exponents, coefficient) pairs; see semaev.py."""
    return [((2, 0, 2), 1), ((1, 1, 2), -2), ((0, 2, 2), 1),
            ((2, 1, 1), -2), ((1, 2, 1), -2), ((1, 0, 1), -2 * a),
            ((0, 1, 1), -2 * a), ((0, 0, 1), -4 * b), ((2, 2, 0), 1),
            ((1, 1, 0), -2 * a), ((0, 0, 0), a * a), ((1, 0, 0), -4 * b),
            ((0, 1, 0), -4 * b)]


def s3_poly(E: Curve, nvars: int, i1: int, i2: int, i3: int | None,
            const3: int = 0) -> Poly:
    """S_3 in variables i1, i2 and either variable i3 or the constant const3."""
    p = E.p
    out: Poly = {}
    for (e1, e2, e3), c in s3_terms(E.a, E.b):
        exps = [0] * nvars
        exps[i1] += e1
        exps[i2] += e2
        if i3 is None:
            c = c * pow(const3, e3, p)
        else:
            exps[i3] += e3
        key = tuple(exps)
        out[key] = (out.get(key, 0) + c) % p
    return {k: v for k, v in out.items() if v}


def univariate(coeffs: dict[int, int], nvars: int, i: int, p: int) -> Poly:
    out: Poly = {}
    for e, c in coeffs.items():
        exps = [0] * nvars
        exps[i] = e
        out[tuple(exps)] = c % p
    return {k: v for k, v in out.items() if v}


def format_poly(poly: Poly, names: list[str]) -> str:
    terms = []
    for exps, c in sorted(poly.items(), reverse=True):
        mono = "*".join(n if e == 1 else f"{n}^{e}" for n, e in zip(names, exps) if e)
        terms.append(f"{c}*{mono}" if mono else str(c))
    return "+".join(terms) if terms else "0"


def evaluate(poly: Poly, values: list[int], p: int) -> int:
    acc = 0
    for exps, c in poly.items():
        t = c
        for v, e in zip(values, exps):
            if e:
                t = t * pow(v, e, p) % p
        acc += t
    return acc % p


@dataclass
class System:
    names: list[str]
    polys: list[Poly]
    p: int
    m: int

    def render(self) -> str:
        body = ",\n".join(format_poly(f, self.names) for f in self.polys)
        return f"{','.join(self.names)}\n{self.p}\n{body}\n"


def decomposition_system(E: Curve, fb: FactorBase, xR: int, m: int,
                         rng: random.Random) -> System:
    if m < 2:
        raise ValueError("m must be >= 2")
    p = E.p
    nv = 2 * m - 1  # x_1..x_m, u_1..u_{m-2}, z
    names = ([f"x{i + 1}" for i in range(m)] + [f"u{k + 1}" for k in range(m - 2)]
             + ["z"])
    member = fb.membership_poly()
    polys = [univariate(member, nv, i, p) for i in range(m)]
    if m == 2:
        polys.append(s3_poly(E, nv, 0, 1, None, xR))
    else:
        polys.append(s3_poly(E, nv, 0, 1, m))
        for k in range(1, m - 2):
            polys.append(s3_poly(E, nv, m + k - 1, k + 1, m + k))
        polys.append(s3_poly(E, nv, 2 * m - 3, m - 1, None, xR))
    form: Poly = {tuple(1 if v == nv - 1 else 0 for v in range(nv)): 1}
    for v in range(nv - 1):
        exps = tuple(1 if w == v else 0 for w in range(nv))
        form[exps] = (-rng.randrange(1, p)) % p
    polys.append(form)
    return System(names, polys, p, m)


# -- running msolve and reading its answer ------------------------------------

@dataclass
class MsolveRun:
    # ok | no_solution | positive_dimensional | failed | crashed | timeout | unexpected
    status: str
    solutions: list[list[int]] = field(default_factory=list)  # all variables but z
    degree: int = -1  # number of solutions over the algebraic closure
    seconds: float = 0.0
    detail: str = ""


def parse_output(text: str, names: list[str], p: int) -> MsolveRun:
    text = text.strip()
    if not text:
        return MsolveRun("failed", detail="empty output")
    if text.endswith(":"):
        text = text[:-1]
    data = ast.literal_eval(text)
    if data == [-1]:
        return MsolveRun("no_solution", degree=0)
    if data[0] == 1:
        return MsolveRun("positive_dimensional")
    try:
        char, nvars, deg, vars_, linform, param = data[1][:6]
        w, den, params = param[1]
    except (TypeError, ValueError, IndexError) as exc:
        return MsolveRun("unexpected", detail=f"layout: {exc}")
    expected_form = [0] * (len(names) - 1) + [1]
    if (char != p or nvars != len(names) or list(vars_) != names
            or list(linform) != expected_form):
        return MsolveRun("unexpected", detail=f"vars={vars_} linform={linform}")
    w_coeffs, den_coeffs = w[1], den[1]
    if deg != len(w_coeffs) - 1 or len(params) != len(names) - 1:
        return MsolveRun("unexpected", detail=f"deg={deg} w_deg={len(w_coeffs) - 1}")
    numerators = [entry[0][1] for entry in params]
    sols = []
    for t in polyfp.roots(w_coeffs, p):
        d = polyfp.evaluate(den_coeffs, t, p)
        if d == 0:
            return MsolveRun("unexpected", detail="denominator vanishes at a root")
        dinv = pow(d, -1, p)
        sols.append([(-polyfp.evaluate(v, t, p)) * dinv % p for v in numerators])
    return MsolveRun("ok", sols, deg)


def run_msolve(system: System, timeout: float | None = None, threads: int = 1) -> MsolveRun:
    exe = msolve_path()
    if exe is None:
        raise RuntimeError("msolve not found: install it or set CRYPTO_AR_MSOLVE")
    if system.p >= max_p():
        raise ValueError(f"p = {system.p} is above the msolve bound {max_p()} "
                         "(see the module docstring; override with CRYPTO_AR_MSOLVE_MAX_P)")
    with tempfile.TemporaryDirectory(prefix="ic-msolve-") as tmp:
        inp, out = os.path.join(tmp, "in.ms"), os.path.join(tmp, "out.ms")
        with open(inp, "w") as fh:
            fh.write(system.render())
        cmd = [exe, "-c", "0", "-P", "1", "-t", str(threads), "-f", inp, "-o", out]
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return MsolveRun("timeout", seconds=time.perf_counter() - t0)
        seconds = time.perf_counter() - t0
        if proc.returncode != 0:
            return MsolveRun("crashed", seconds=seconds,
                             detail=f"exit {proc.returncode}: "
                                    + (proc.stdout + proc.stderr).strip()[-300:])
        text = ""
        if os.path.exists(out):
            with open(out) as fh:
                text = fh.read()
    run = parse_output(text, system.names, system.p)
    run.seconds = seconds
    if run.status == "failed":
        run.detail = (proc.stdout + proc.stderr).strip()[-400:]
    return run


_STARTUP: float | None = None


def startup_seconds() -> float:
    """Median wall time of msolve on a trivial system (process overhead)."""
    global _STARTUP
    if _STARTUP is None:
        trivial = System(["x", "z"], [{(1, 0): 1, (0, 0): 100}, {(0, 1): 1, (1, 0): 100}],
                         101, 1)
        _STARTUP = statistics.median(run_msolve(trivial).seconds for _ in range(5))
    return _STARTUP


# -- decomposition --------------------------------------------------------------

@dataclass
class MsolveOutcome:
    status: str
    relations: list[tuple[tuple[int, int], ...]]
    seconds: float
    runs: int
    degree: int
    rational_solutions: int
    unlifted: int
    detail: str = ""


def _signs(E: Curve, fb: FactorBase, idx: list[int], R: Point):
    pts = [fb.points[i] for i in idx]
    for signs in itertools.product((1, -1), repeat=len(idx)):
        S: Point = None
        for Q, s in zip(pts, signs):
            S = E.add(S, Q if s > 0 else E.neg(Q))
        if S == R:
            return [(i, s) for i, s in zip(idx, signs)]
    return None


def decompose_msolve(E: Curve, fb: FactorBase, R: Point, m: int, seed: int = 0,
                     timeout: float | None = None, retries: int = 3,
                     threads: int = 1) -> MsolveOutcome:
    """All decompositions of R found by solving the system with msolve."""
    rng = random.Random(f"msolve|{E.p}|{E.a}|{E.b}|{R}|{m}|{seed}")
    seconds, runs = 0.0, 0
    run = MsolveRun("failed")
    while runs < retries:
        runs += 1
        run = run_msolve(decomposition_system(E, fb, R[0], m, rng), timeout, threads)
        seconds += run.seconds
        if run.status != "failed":
            break
    if run.status not in ("ok", "no_solution"):
        return MsolveOutcome(run.status, [], seconds, runs, run.degree, 0, 0, run.detail)
    rels, unlifted = set(), 0
    for vals in run.solutions:
        idx = [fb.lookup(x) for x in vals[:m]]
        rel = None if None in idx else _signs(E, fb, idx, R)
        if rel is None:
            unlifted += 1
            continue
        verify(E, fb, rel, R)
        rels.add(canonical(rel))
    return MsolveOutcome(run.status, sorted(rels), seconds, runs, run.degree,
                         len(run.solutions), unlifted)

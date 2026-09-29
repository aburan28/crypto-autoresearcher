#!/usr/bin/env python3
"""EXP-PFDR-cbdefb run script (TASK-20260903-6745ea, Executor).

Executes the frozen contract experiments/EXP-PFDR-cbdefb/specification.yaml: the pair
(d_ff, d_lf) of the d = 2 digit-presented Semaev system on the ladder m = 2, s in {1..5},
p in {4099, 16411, 65537}, with the last fall degree read from the V_{F,D} closure of
closure.py under the convention frozen in stage1-closure-convention.md (sha256 recorded
in every manifest).  No Groebner basis is computed anywhere; every fall is read from the
exact closure.

Subcommands (one immutable run directory each through harness.runner.run_wrapped, so the
wall time is wrapper-measured; a package-sha256.json sidecar follows):

  s1slice            CTRL-S1-BASELINE (Stage 1): s = 1, all primes, direct vs digit form
  fixture            CTRL-KNOWN-ANSWER-FIXTURE (Stage 1): planted-fall fixture P (seed 5),
                     its ordinary-ring twin, and the hand fixture H
  dffagree           CTRL-DFF-AGREEMENT (Stage 1): EXP-PFDR-5726af's p = 4099 instances, s = 2..5
  cell --s S --p P   Stage 2: one (s, p) cell, all arms (Semaev, NULL-1, NULL-2, NULL-3, non-curve)
  equalds --d D --s S  CTRL-EQUAL-DS-SPREAD at B = 64, p = 65537, D <= 6
  m3cell --s S       Stage 3 (optional): m = 3, p = 65537, 3 curves, 2 targets

Statuses: completed_valid | completed_invalid | failed_infrastructure.  Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import signal
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
EXP_DIR = os.path.join(REPO, "experiments", "EXP-PFDR-cbdefb")
sys.path.insert(0, EXP_DIR)

import closure as C  # noqa: E402  (sets BLAS threads to 1 before importing numpy)
import numpy as np  # noqa: E402
import sympy  # noqa: E402
import yaml  # noqa: E402

from harness import semaev as hsemaev  # noqa: E402
from harness.macaulay_fp import (  # noqa: E402
    ColumnSpace,
    Ring,
    block_factored_system,
    digit_presentation,
    direct_presentation,
    substitute,
    support_matched_system,
)
from harness.macaulay_fp.columns import PreflightAbort, preflight  # noqa: E402
from harness.macaulay_fp.poly import poly_from_terms  # noqa: E402
from harness.runner import RunResult, run_wrapped  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-PFDR-cbdefb"
AREA = "PFDR-cbdefb"
TASK_ID = "TASK-20260903-6745ea"
METER_DIR = os.path.join(REPO, "harness", "macaulay_fp")
CONVENTION_PATH = os.path.join(EXP_DIR, "stage1-closure-convention.md")

WALL_CAP_SECONDS = 7200          # contract: wall_clock_seconds_per_run
WALL_GUARD_SECONDS = 6600        # stop STARTING new systems past this point
MEMORY_CAP_GB = 8                # contract: maximum_memory_gb
COLUMN_CAP = 50000               # 84cdb7 pre-flight gate
DENSE_CAP_BYTES = 4 * 1024 ** 3  # 84cdb7 pre-flight gate

PRIMES = [4099, 16411, 65537]
CURVE_SEEDS = list(range(3101, 3109))
TARGET_SEEDS = [1, 2, 3, 4, 5]
NULL_SEEDS = [7, 11, 13, 17, 19]
FIXTURE_SEED = 5
D_MAX = 7
PLANT_WINDOW_M2 = 4              # x(P_i) in [0, 4): valid for every s >= 2 (shared targets along the ladder)
SPARSE_LIMIT = C.SPARSE_COLUMN_LIMIT
XCHECK_CURVE, XCHECK_TARGET, XCHECK_NULL = 3101, 1, 7   # dense-engine cross-check subsample

T0 = time.monotonic()
PARTIAL: dict = {}               # progress preserved if the wall-clock alarm fires


# --------------------------------------------------------------------------
# provenance helpers
# --------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def meter_provenance() -> dict:
    files = {}
    for root, _dirs, names in os.walk(METER_DIR):
        if "__pycache__" in root:
            continue
        for nm in sorted(names):
            pth = os.path.join(root, nm)
            files[os.path.relpath(pth, REPO)] = sha256_file(pth)
    files["tests/test_macaulay_fp.py"] = sha256_file(os.path.join(REPO, "tests", "test_macaulay_fp.py"))
    return {"meter_commit": git("log", "-1", "--format=%H", "--", "harness/macaulay_fp"),
            "meter_commit_short": git("log", "-1", "--format=%h", "--", "harness/macaulay_fp"),
            "files_sha256": files,
            "selftest_note": "python3 -m pytest tests/test_macaulay_fp.py -q run in this session before the first official run: 52 passed (implementation.md)"}


def dirty_tree_hash() -> dict:
    diff = subprocess.run(["git", "diff", "HEAD"], cwd=REPO, capture_output=True).stdout
    status = git("status", "--porcelain")
    return {"tracked_diff_sha256": hashlib.sha256(diff).hexdigest(), "tracked_diff_bytes": len(diff),
            "porcelain_sha256": hashlib.sha256(status.encode()).hexdigest(),
            "porcelain_line_count": len([ln for ln in status.splitlines() if ln])}


def session_inference() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "requested_reasoning_effort": "medium",
        "adapter_resolution": "python3 -m orchestration.adapter resolve --role executor -> anthropic:claude-sonnet-5 (effort=medium)",
        "runtime_reported_model": "claude-fable-5-1",
        "model_verified": False,
        "model_verified_note": ("The adapter binding (claude-sonnet-5) and the model identifier reported by the executing "
                                "session (claude-fable-5-1) differ; the Executor cannot verify its own binding from inside "
                                "the session.  AUTORESEARCH_POLICY is deliberately NOT set for the run process (the adapter "
                                "would then assert model_verified: true for claude-sonnet-5).  The wrapper's own inference "
                                "block records the harness default (no model in the loop, true of this deterministic script); "
                                "this block records the SESSION that wrote and launched it."),
        "fallback_used": "unknown",
        "degraded": False,
        "independent_session": True,
        "no_bedrock": True,
    }


def convention_provenance() -> dict:
    return {"path": os.path.relpath(CONVENTION_PATH, REPO), "sha256": sha256_file(CONVENTION_PATH),
            "convention_id": C.CONVENTION_ID}


def set_limits() -> None:
    cap = MEMORY_CAP_GB * 1024 ** 3
    try:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    except (ValueError, OSError) as exc:  # pragma: no cover
        print(f"WARNING: could not set RLIMIT_AS: {exc}", file=sys.stderr)

    def on_alarm(signum, frame):
        raise TimeoutError(f"wall clock exceeded {WALL_CAP_SECONDS}s (contract per-run cap)")
    signal.signal(signal.SIGALRM, on_alarm)
    signal.alarm(WALL_CAP_SECONDS)


def elapsed() -> float:
    return time.monotonic() - T0


def guard_tripped() -> bool:
    return elapsed() > WALL_GUARD_SECONDS


def H(seed: int, tag: str) -> int:
    return int(hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest(), 16)


def hint(*parts) -> int:
    return int(hashlib.sha256(":".join(str(x) for x in parts).encode()).hexdigest(), 16)


# --------------------------------------------------------------------------
# Semaev polynomials (from scratch, as EXP-PFDR-5726af) and cross-checks
# --------------------------------------------------------------------------
def s3_dict(a: int, b: int, xR: int, p: int) -> dict:
    d: dict = {}

    def add(e, c):
        d[e] = (d.get(e, 0) + c) % p
    add((2, 0), xR * xR); add((0, 2), xR * xR); add((1, 1), -2 * xR * xR)
    add((2, 1), -2 * xR); add((1, 2), -2 * xR); add((1, 0), -2 * a * xR); add((0, 1), -2 * a * xR)
    add((0, 0), -4 * b * xR); add((2, 2), 1); add((1, 1), -2 * a); add((0, 0), a * a)
    add((1, 0), -4 * b); add((0, 1), -4 * b)
    return {e: c for e, c in d.items() if c}


def s3_crosscheck(a: int, b: int, xR: int, p: int, rng: random.Random, trials: int = 20) -> bool:
    d = s3_dict(a, b, xR, p)
    for _ in range(trials):
        v1, v2 = rng.randrange(p), rng.randrange(p)
        mine = sum(c * pow(v1, e[0], p) * pow(v2, e[1], p) for e, c in d.items()) % p
        if mine != hsemaev.s3_eval(a, b, v1, v2, xR, p):
            return False
    return True


_X1, _X2, _X3, _T = sympy.symbols("x1 x2 x3 T")


def s3_sympy(a, b, x, y, z):
    return (x - y) ** 2 * z ** 2 - 2 * ((x + y) * (x * y + a) + 2 * b) * z + (x * y - a) ** 2 - 4 * b * (x + y)


def s4_dict(a: int, b: int, xR: int, p: int) -> dict:
    left = sympy.Poly(s3_sympy(sympy.Integer(a), sympy.Integer(b), _X1, _X2, _T), _T)
    right = sympy.Poly(s3_sympy(sympy.Integer(a), sympy.Integer(b), _X3, sympy.Integer(xR), _T), _T)
    expr = sympy.expand(sympy.resultant(left, right, _T))
    poly = sympy.Poly(expr, _X1, _X2, _X3)
    return {tuple(int(e) for e in ex): int(c) % p for ex, c in poly.as_dict().items() if int(c) % p}


def s4_vanishes_on_planted_triples(a: int, b: int, p: int, rng: random.Random, trials: int = 5) -> bool:
    E = EllipticCurve(p, a, b)
    n = 0
    while n < trials:
        pts = []
        for _ in range(3):
            P = None
            while P is None:
                P = E.lift_x(rng.randrange(p))
            if rng.random() < 0.5:
                P = E.negate(P)
            pts.append(P)
        R = E.add(E.add(pts[0], pts[1]), pts[2])
        if R is None:
            continue
        n += 1
        dd = s4_dict(a, b, R[0], p)
        val = sum(c * pow(pts[0][0], e[0], p) * pow(pts[1][0], e[1], p) * pow(pts[2][0], e[2], p) for e, c in dd.items()) % p
        if val != 0:
            return False
    return True


# --------------------------------------------------------------------------
# curves, targets, certificates (construction of EXP-PFDR-5726af, reused verbatim)
# --------------------------------------------------------------------------
def make_curve(p: int, seed: int, window: int = PLANT_WINDOW_M2, min_pts: int = 2) -> dict:
    rejections = []
    for t in range(1, 100000):
        a = H(seed, f"{p}:a{t}") % p
        b = H(seed, f"{p}:b{t}") % p
        if a == 0 or b == 0:
            rejections.append((t, "j_special"))
            continue
        if (4 * a * a * a + 27 * b * b) % p == 0:
            rejections.append((t, "singular"))
            continue
        E = EllipticCurve(p, a, b)
        xs = [x for x in range(window) if E.lift_x(x) is not None]
        if len(xs) < min_pts:
            rejections.append((t, f"window_points={len(xs)}"))
            continue
        j = (1728 * 4 * a ** 3 * pow((4 * a ** 3 + 27 * b * b) % p, -1, p)) % p
        return {"p": p, "a": a, "b": b, "j": j, "seed": seed, "attempt": t, "rejections": rejections,
                "acceptance_window": window, "window_x": xs}
    raise RuntimeError("no curve found")


def independent_add(p: int, a: int, P, Q):
    """Second, separately written affine group law for certificate re-verification."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 % p == x2 % p:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def independent_verify(cert: dict) -> bool:
    st = cert["statement"]
    c = st["curve"]
    p, a, b = c["p"], c["a"], c["b"]
    acc = None
    for s in st["summands"]:
        x, y = s
        if (y * y - (x ** 3 + a * x + b)) % p != 0:
            return False
        acc = independent_add(p, a, acc, (x, y))
    tx, ty = st["target"]
    if (ty * ty - (tx ** 3 + a * tx + b)) % p != 0:
        return False
    return acc == (tx, ty)


def plant_target(curve: dict, m: int, target_seed: int, window: int):
    """Planted target R = P_1 + ... + P_m with x(P_i) in [0, window).  For window 4 the RNG tag is
    EXP-PFDR-5726af's verbatim so CTRL-DFF-AGREEMENT runs on that package's exact instances."""
    p, a, b = curve["p"], curve["a"], curve["b"]
    E = EllipticCurve(p, a, b)
    xs = [x for x in range(window) if E.lift_x(x) is not None]
    if not xs:
        return None
    tag = f"{p}:{curve['seed']}:target" if window == PLANT_WINDOW_M2 else f"{p}:{curve['seed']}:w{window}:target"
    rng = random.Random(H(target_seed, tag))
    for attempt in range(1, 10000):
        pts = []
        for _ in range(m):
            P = E.lift_x(rng.choice(xs))
            if rng.random() < 0.5:
                P = E.negate(P)
            pts.append(P)
        R = None
        for P in pts:
            R = E.add(R, P)
        if R is None:
            continue
        cert = {"kind": "decomposition",
                "statement": {"target": [R[0], R[1]], "summands": [[P[0], P[1]] for P in pts],
                              "curve": {"p": p, "a": a, "b": b}}}
        return {"target_seed": target_seed, "attempt": attempt, "window": window, "x_R": R[0], "R": [R[0], R[1]],
                "summands": [[P[0], P[1]] for P in pts], "certificate": cert,
                "verified_independent_add": independent_verify(cert),
                "verified_harness_semaev": bool(hsemaev.verify_decomposition_certificate(cert))}
    raise RuntimeError("could not plant a target")


# --------------------------------------------------------------------------
# non-curve cubic (nodal Weierstrass cubic, construction of EXP-PFDR-fd901a reused)
# --------------------------------------------------------------------------
def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(a: int, p: int):
    r = sympy.ntheory.residue_ntheory.sqrt_mod(a % p, p)
    return None if r is None else int(r)


def make_singular_cubic(p: int, seed: int, window: int, min_pts: int = 2) -> dict:
    rejections = {"t_zero": 0, "window": 0}
    for attempt in range(1, 100000):
        t = hint(EXP_ID, "singular", p, seed, "t", attempt) % p
        if t == 0:
            rejections["t_zero"] += 1
            continue
        a = (-3 * t * t) % p
        b = (2 * t * t * t) % p
        assert (4 * a * a * a + 27 * b * b) % p == 0
        xs = [x for x in range(window) if x != t and legendre((x ** 3 + a * x + b) % p, p) >= 0]
        if len(xs) < min_pts:
            rejections["window"] += 1
            continue
        return {"p": p, "a": a, "b": b, "t": t, "seed": seed, "attempt": attempt, "rejections": rejections,
                "window": window, "window_x": xs, "kind": "singular"}
    raise RuntimeError("no singular cubic found")


def plant_root_target(cubic: dict, m: int, target_seed: int) -> dict:
    """x_R a root of S_{m+1}(x_1..x_m, X) = 0 with x_i window x on the cubic (with replacement);
    certificate kind s3_root (m = 2) / s4_root (m = 3) re-verified independently."""
    p, a, b = cubic["p"], cubic["a"], cubic["b"]
    xs = cubic["window_x"]
    rng = random.Random(hint(EXP_ID, "roottarget", p, cubic["seed"], target_seed))
    for attempt in range(1, 100000):
        pts = [rng.choice(xs) for _ in range(m)]
        if m == 2:
            x1, x2 = pts
            c2 = (x1 - x2) ** 2 % p
            c1 = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
            c0 = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
            if c2 == 0:
                roots = [] if c1 == 0 else [(-c0) * pow(c1, -1, p) % p]
            else:
                disc = (c1 * c1 - 4 * c2 * c0) % p
                r = sqrt_mod(disc, p)
                if r is None:
                    continue
                roots = sorted({(-c1 + r) * pow(2 * c2, -1, p) % p, (-c1 - r) * pow(2 * c2, -1, p) % p})
            if not roots:
                continue
            x_R = roots[rng.randrange(len(roots))]
            cert = {"kind": "s3_root", "statement": {"x1": x1, "x2": x2, "x_R": x_R, "cubic": {"p": p, "a": a, "b": b}}}
            ok = hsemaev.s3_eval(a, b, x1, x2, x_R, p) == 0
        else:
            # S_4(x1, x2, x3, X) as a polynomial in X: coefficients from the resultant with symbolic x_R
            xr = sympy.Symbol("xr")
            left = sympy.Poly(s3_sympy(sympy.Integer(a), sympy.Integer(b), _X1, _X2, _T), _T)
            right = sympy.Poly(s3_sympy(sympy.Integer(a), sympy.Integer(b), _X3, xr, _T), _T)
            expr = sympy.expand(sympy.resultant(left, right, _T)).subs({_X1: pts[0], _X2: pts[1], _X3: pts[2]})
            poly = sympy.Poly(sympy.expand(expr), xr)
            coeffs = [int(c) % p for c in poly.all_coeffs()]
            roots = [X for X in range(p) if sum(c * pow(X, len(coeffs) - 1 - i, p) for i, c in enumerate(coeffs)) % p == 0] if any(coeffs) else []
            if not roots:
                continue
            x_R = roots[rng.randrange(len(roots))]
            cert = {"kind": "s4_root", "statement": {"x": pts, "x_R": x_R, "cubic": {"p": p, "a": a, "b": b}}}
            dd = s4_dict(a, b, x_R, p)
            ok = sum(c * pow(pts[0], e[0], p) * pow(pts[1], e[1], p) * pow(pts[2], e[2], p) for e, c in dd.items()) % p == 0
        return {"target_seed": target_seed, "attempt": attempt, "x": pts, "x_R": x_R, "roots": roots,
                "certificate": cert, "verified_independent": bool(ok)}
    raise RuntimeError("could not plant a root target")


# --------------------------------------------------------------------------
# null generators
# --------------------------------------------------------------------------
def random_blockdegree_poly(ring: Ring, blocks, e: int, rng: random.Random) -> dict:
    """NULL-2: uniformly random multilinear polynomial with per-block degree <= e (coefficients uniform in F_p)."""
    out = {}
    for m in ring.monomials_upto(ring.n_sq):
        mask = m[0]
        if all(bin(mask & sum(1 << i for i in blk)).count("1") <= e for blk in blocks):
            c = rng.randrange(0, ring.p)
            if c:
                out[m] = c
    return out


# --------------------------------------------------------------------------
# soundness subsample (y^2 = f(x) variant, 84cdb7): zeros of S~ on {0,1}^n and the non-square filter
# --------------------------------------------------------------------------
def soundness(ring: Ring, g: dict, columns_full: ColumnSpace, Ev: np.ndarray, pres, curve: dict, target: dict, m: int, s: int) -> dict:
    p = ring.p
    Z = C.zero_set(ring, [g], columns_full, Ev)
    a, b = curve["a"], curve["b"]
    rows = []
    nonsq = 0
    for z in Z:
        xs = []
        for k in range(m):
            xk = sum(((z >> (k * s + i)) & 1) << i for i in range(s)) % p
            xs.append(xk)
        sq = [legendre((x ** 3 + a * x + b) % p, p) >= 0 for x in xs]
        if not all(sq):
            nonsq += 1
        rows.append({"digits": z, "x": xs, "on_curve": sq})
    planted_bits = 0
    for k, P in enumerate(target["summands"]):
        x = P[0]
        for i in range(s):
            if (x >> i) & 1:
                planted_bits |= 1 << (k * s + i)
    return {"n_zeros": len(Z), "n_with_nonsquare_rhs": nonsq,
            "filtering_fraction": (nonsq / len(Z)) if Z else None,
            "planted_digit_vector_is_zero": planted_bits in Z, "zeros": rows[:64]}


# --------------------------------------------------------------------------
# measurement of one system with the frozen policy
# --------------------------------------------------------------------------
def engine_for(columns: ColumnSpace, dmax: int) -> str:
    return "sparse" if columns.ncols_upto(dmax) <= SPARSE_LIMIT else "dense"


def preflight_record(ring: Ring, gens, dmax: int) -> dict:
    degs = [ring.degree(g) for g in gens if ring.degree(g) >= 0]
    pf = preflight(ring, degs, dmax, "cumulative")
    ncols = pf.cols
    dense_bytes = (pf.rows + ncols) * ncols * 8
    rec = {"D_max": dmax, "cumulative_rows": pf.rows, "columns": ncols, "columns_top": pf.cols_top,
           "dense_equivalent_bytes_closure_bound": dense_bytes, "column_cap": COLUMN_CAP, "dense_cap_bytes": DENSE_CAP_BYTES,
           "within_contract": ncols <= COLUMN_CAP and dense_bytes <= DENSE_CAP_BYTES}
    if not rec["within_contract"]:
        raise PreflightAbort(pf, COLUMN_CAP, -1)
    return rec


def measure(ring: Ring, gens, columns: ColumnSpace, dmin: int, dmax: int, *, xcheck: bool, cert: bool, T=None, Ev=None) -> dict:
    eng = engine_for(columns, dmax)
    return C.measure_system(ring, gens, columns, dmin, dmax, engine=eng, cross_check=(eng == "sparse") or xcheck,
                            certificate=cert, T=T, Ev=Ev, graded=True)


def summary(res: dict) -> dict:
    if res.get("degenerate"):
        return {"degenerate": True, "reason": res.get("reason")}
    return {"d_ff": res["d_ff"], "d_lf": res["d_lf"], "falls": res["falls"], "right_censored": res["right_censored"],
            "no_fall_in_window": res["no_fall_in_window"], "iteration_counts_at_falls": res["fall_iteration_counts"],
            "graded_d_ff": res["graded"]["graded_d_ff"], "closure_dff_equals_graded_dff": res["closure_dff_equals_graded_dff"],
            "certified_route": res["certificate"].get("route"), "engine": res["engine"],
            "cross_check_agree": res.get("cross_check", {}).get("agree"), "seconds": res["seconds"]}


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x


def common_params(stage: str, controls: list, extra: dict) -> dict:
    return {"task_id": TASK_ID, "stage": stage, "control_ids": controls, **extra,
            "closure_convention": convention_provenance(), "closure_convention_sha256": convention_provenance()["sha256"],
            "meter": meter_provenance(), "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
            "engine_policy": {"sparse_column_limit": SPARSE_LIMIT, "certificate_column_limit": C.CERTIFICATE_COLUMN_LIMIT,
                              "dense_exactness_bound": "p^2 (ncols + 1) < 2^53"},
            "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "wall_guard_seconds": WALL_GUARD_SECONDS,
                       "memory_gb": MEMORY_CAP_GB, "workers": 1, "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS")}}


# --------------------------------------------------------------------------
# Stage 2 cell (and Stage 3 with m = 3)
# --------------------------------------------------------------------------
def run_cell(args, m: int = 2) -> RunResult:
    s = args.s
    primes = [args.p] if m == 2 else [65537]
    curve_seeds = CURVE_SEEDS if m == 2 else CURVE_SEEDS[:3]
    target_seeds = TARGET_SEEDS if m == 2 else TARGET_SEEDS[:2]
    e = 2 ** (m - 1)
    n = m * s
    window = (2 if s == 1 else PLANT_WINDOW_M2) if m == 2 else min(2 ** s, 4 if s == 2 else 8)
    dmax = D_MAX
    D_null = math.ceil((m * s + 2 * m) / 2)
    out: list = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    log(f"cell m={m} d=2 s={s} n={n} primes={primes} D_max={dmax} D_null(84cdb7)={D_null} window=[0,{window})")
    draws: list = []
    noncurve: list = []
    null2_objs: list = []
    null3_objs: list = []
    not_computed: list = []
    PARTIAL.update({"draws": draws, "noncurve": noncurve, "null2_objects": null2_objs, "null3_objects": null3_objs,
                    "not_computed": not_computed})
    manifest_cert = {"kind": "none", "note": "no planted target in this run"}
    cert_all_ok = True
    xcheck_all_ok = True
    p1_all_ok = True
    preflights = {}
    for p in primes:
        ring = Ring(p, n, 0)
        columns = ColumnSpace.build(ring, dmax)
        full = ColumnSpace.build(ring, n) if n > dmax else columns
        T = C.multiplication_table(ring, full)
        Ev = C.evaluation_matrix(ring, full) if (1 << n) <= C.CERTIFICATE_COLUMN_LIMIT else None
        blocks = [[k * s + i for i in range(s)] for k in range(m)]
        eng = engine_for(columns, dmax)
        log(f"p={p}: ring n={n}, columns(<= {dmax}) = {columns.ncols_upto(dmax)}, engine = {eng}")
        # ---- NULL-2 / NULL-3: no curve or target input; once per (p, s, seed), reported per draw by reference
        for seed in NULL_SEEDS:
            rng = random.Random(seed)
            g2 = random_blockdegree_poly(ring, blocks, e, rng)
            gens3, meta3, factors = block_factored_system(ring, blocks, [e] * m, seed)
            g3 = gens3[0]
            for label, g, lst in (("NULL-2", g2, null2_objs), ("NULL-3", g3, null3_objs)):
                rec = {"p": p, "seed": seed, "terms": len(g), "degree": ring.degree(g), "ref": f"{label.lower()}[p={p},seed={seed}]"}
                if label == "NULL-3":
                    rec["factor_degrees"] = [ring.degree(f) for f in factors[0]]
                if ring.degree(g) < 0:
                    rec["result"] = {"degenerate": True, "reason": "zero generator (a degree-e form in fewer than e squarefree variables vanishes)"}
                elif ring.degree(g) > dmax:
                    rec["result"] = {"degenerate": True, "reason": f"generator degree {ring.degree(g)} exceeds D_max = {dmax}: no layer exists; no fall observable", "generator_degrees": [ring.degree(g)]}
                else:
                    if guard_tripped():
                        not_computed.append({"arm": label, "p": p, "seed": seed, "reason": "wall guard"})
                        continue
                    rec["preflight"] = preflight_record(ring, [g], dmax)
                    rec["result"] = measure(ring, [g], columns, ring.degree(g), dmax, xcheck=(seed == XCHECK_NULL), cert=True, T=T, Ev=Ev)
                    xcheck_all_ok &= rec["result"].get("cross_check", {}).get("agree", True) is not False
                rec["summary"] = summary(rec["result"])
                lst.append(rec)
                log(f"  {label} p={p} seed={seed}: {rec['summary']}")
        # ---- Semaev arm and NULL-1, non-curve arm
        for cs in curve_seeds:
            curve = make_curve(p, cs)
            cubic = make_singular_cubic(p, cs, window)
            for ts in target_seeds:
                if guard_tripped():
                    not_computed.append({"arm": "semaev+null1+noncurve", "p": p, "curve_seed": cs, "target_seed": ts, "reason": "wall guard"})
                    continue
                tgt = plant_target(curve, m, ts, window)
                draw = {"p": p, "s": s, "curve_seed": cs, "curve": {k: curve[k] for k in ("a", "b", "j", "attempt", "window_x")},
                        "curve_rejections": len(curve["rejections"]), "target_seed": ts}
                if tgt is None:
                    draw["not_plantable"] = f"no on-curve x in [0, {window}) on this curve"
                    draws.append(draw)
                    log(f"  Semaev p={p} curve={cs} target={ts}: NOT PLANTABLE (window [0,{window}))")
                    continue
                if not (tgt["verified_independent_add"] and tgt["verified_harness_semaev"]):
                    cert_all_ok = False
                if manifest_cert["kind"] == "none":
                    manifest_cert = tgt["certificate"]
                draw["target"] = {k: tgt[k] for k in ("target_seed", "attempt", "window", "x_R", "R", "summands",
                                                       "verified_independent_add", "verified_harness_semaev")}
                draw["certificate"] = tgt["certificate"]
                sd = s3_dict(curve["a"], curve["b"], tgt["x_R"], p) if m == 2 else s4_dict(curve["a"], curve["b"], tgt["x_R"], p)
                rngx = random.Random(H(ts, f"{p}:{cs}:xcheck"))
                draw["s_poly_crosscheck"] = s3_crosscheck(curve["a"], curve["b"], tgt["x_R"], p, rngx) if m == 2 else \
                    s4_vanishes_on_planted_triples(curve["a"], curve["b"], p, rngx)
                pres = digit_presentation(p, m, 2, s, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
                assert pres.ring == ring
                g = pres.generators[0]
                draw["generator_terms"] = len(g)
                draw["generator_degree"] = ring.degree(g)
                xc = (cs == XCHECK_CURVE and ts == XCHECK_TARGET)
                if ring.degree(g) > dmax:
                    draw["semaev"] = {"degenerate": True, "reason": f"generator degree {ring.degree(g)} exceeds D_max = {dmax}: no layer exists; no fall observable", "generator_degrees": [ring.degree(g)]}
                else:
                    draw["preflight"] = preflight_record(ring, [g], dmax)
                    preflights.setdefault(str(p), draw["preflight"])
                    draw["semaev"] = measure(ring, [g], columns, ring.degree(g), dmax, xcheck=xc, cert=True, T=T, Ev=Ev)
                    xcheck_all_ok &= draw["semaev"].get("cross_check", {}).get("agree", True) is not False
                    p1_all_ok &= bool(draw["semaev"]["closure_dff_equals_graded_dff"])
                draw["semaev_summary"] = summary(draw["semaev"])
                if m == 2 and ts == 5 and Ev is not None and not draw["semaev"].get("degenerate"):
                    draw["soundness_subsample"] = soundness(ring, g, full, Ev, pres, curve, tgt, m, s)
                log(f"  Semaev p={p} curve={cs} target={ts} x_R={tgt['x_R']}: {draw['semaev_summary']} t={elapsed():.0f}s")
                # NULL-1: support-matched, per draw, 5 seeds
                draw["null1"] = []
                for seed in NULL_SEEDS:
                    if guard_tripped():
                        not_computed.append({"arm": "NULL-1", "p": p, "curve_seed": cs, "target_seed": ts, "seed": seed, "reason": "wall guard"})
                        continue
                    polys, meta = support_matched_system(ring, [g], seed)
                    g1 = polys[0]
                    rec = {"seed": seed, "terms": len(g1), "degree": ring.degree(g1)}
                    if ring.degree(g1) > dmax or ring.degree(g1) < 0:
                        rec["result"] = {"degenerate": True, "reason": "generator degree outside (0, D_max]"}
                    else:
                        rec["result"] = measure(ring, [g1], columns, ring.degree(g1), dmax, xcheck=(xc and seed == XCHECK_NULL), cert=True, T=T, Ev=Ev)
                        xcheck_all_ok &= rec["result"].get("cross_check", {}).get("agree", True) is not False
                    rec["summary"] = summary(rec["result"])
                    draw["null1"].append(rec)
                    log(f"    NULL-1 seed={seed}: {rec['summary']}")
                draw["null2_refs"] = [f"null-2[p={p},seed={seed}]" for seed in NULL_SEEDS]
                draw["null3_refs"] = [f"null-3[p={p},seed={seed}]" for seed in NULL_SEEDS]
                draws.append(draw)
                # non-curve cubic: same S formula at the nodal cubic, same digit generators, root target
                if guard_tripped():
                    not_computed.append({"arm": "noncurve", "p": p, "curve_seed": cs, "target_seed": ts, "reason": "wall guard"})
                    continue
                rt = plant_root_target(cubic, m, ts)
                cert_all_ok &= rt["verified_independent"]
                sdn = s3_dict(cubic["a"], cubic["b"], rt["x_R"], p) if m == 2 else s4_dict(cubic["a"], cubic["b"], rt["x_R"], p)
                presn = digit_presentation(p, m, 2, s, lambda r, xs, sd=sdn: [substitute(r, sd, xs)])
                gn = presn.generators[0]
                nd = {"p": p, "s": s, "cubic_seed": cs, "cubic": {k: cubic[k] for k in ("a", "b", "t", "attempt", "window_x")},
                      "target_seed": ts, "root_target": {k: rt[k] for k in ("x", "x_R", "roots", "attempt", "verified_independent")},
                      "certificate": rt["certificate"], "generator_terms": len(gn), "generator_degree": ring.degree(gn)}
                if ring.degree(gn) > dmax or ring.degree(gn) < 0:
                    nd["result"] = {"degenerate": True, "reason": f"generator degree {ring.degree(gn)} outside (0, D_max]"}
                else:
                    nd["result"] = measure(ring, [gn], columns, ring.degree(gn), dmax, xcheck=xc, cert=True, T=T, Ev=Ev)
                    xcheck_all_ok &= nd["result"].get("cross_check", {}).get("agree", True) is not False
                nd["summary"] = summary(nd["result"])
                noncurve.append(nd)
                log(f"  NONCURVE p={p} cubic={cs} target={ts} x_R={rt['x_R']}: {nd['summary']} t={elapsed():.0f}s")

    # ---- per-cell metrics (observations; the analysis recomputes everything from raw)
    def vals(lst, key):
        return [x[key] for x in lst]
    sem = [d["semaev_summary"] for d in draws if "semaev_summary" in d and not d["semaev_summary"].get("degenerate")]
    n1 = [r["summary"] for d in draws for r in d.get("null1", []) if not r["summary"].get("degenerate")]
    n2 = [r["summary"] for r in null2_objs if not r["summary"].get("degenerate")]
    n3 = [r["summary"] for r in null3_objs if not r["summary"].get("degenerate")]
    nc = [r["summary"] for r in noncurve if not r["summary"].get("degenerate")]

    def arm_table(lst):
        return {"n": len(lst), "d_ff_values": vals(lst, "d_ff"), "d_lf_values": vals(lst, "d_lf"),
                "right_censored": sum(1 for x in lst if x["right_censored"]),
                "no_fall_in_window": sum(1 for x in lst if x["no_fall_in_window"]),
                "d_lf_uncensored_values": [x["d_lf"] for x in lst if not x["right_censored"]],
                "min_iteration_count_at_falls": min((min(x["iteration_counts_at_falls"].values()) for x in lst if x["iteration_counts_at_falls"]), default=None),
                "fall_with_iteration_count_1": sum(1 for x in lst if any(v == 1 for v in x["iteration_counts_at_falls"].values())),
                "closure_dff_equals_graded_dff_all": all(x["closure_dff_equals_graded_dff"] for x in lst) if lst else None,
                "cross_check_agree_all": all(x["cross_check_agree"] is not False for x in lst) if lst else None,
                "cross_checked": sum(1 for x in lst if x["cross_check_agree"] is not None),
                "seconds": round(sum(x["seconds"] for x in lst), 1)}
    sem_pairs = sorted({(x["d_ff"], x["d_lf"]) for x in sem}, key=str)
    metrics = {
        "cell": {"m": m, "d": 2, "s": s, "n": n, "primes": primes, "D_max": dmax, "D_null_84cdb7": D_null,
                 "null_band_center_s_plus_2": s + 2 if m == 2 else None, "window": window,
                 "curve_seeds": curve_seeds, "target_seeds": target_seeds, "null_seeds": NULL_SEEDS,
                 "columns_at_Dmax": {str(p): Ring(p, n, 0).count_monomials_upto(dmax) for p in primes},
                 "engine": engine_for(ColumnSpace.build(Ring(primes[0], n, 0), dmax), dmax), "preflight": preflights},
        "semaev": arm_table(sem), "null1": arm_table(n1), "null2": arm_table(n2), "null3": arm_table(n3), "noncurve": arm_table(nc),
        "semaev_pairs": sem_pairs,
        "noncurve_pairs": sorted({(x["d_ff"], x["d_lf"]) for x in nc}, key=str),
        "null1_band_offsets_uncensored": sorted({x["d_lf"] - (s + 2) for x in n1 if not x["right_censored"] and x["d_lf"] is not None}),
        "null2_band_offsets_uncensored": sorted({x["d_lf"] - (s + 2) for x in n2 if not x["right_censored"] and x["d_lf"] is not None}),
        "null3_minus_semaev_dff": sorted({(x["d_ff"] - y["d_ff"]) for x in n3 for y in sem if x["d_ff"] is not None and y["d_ff"] is not None}),
        "null3_minus_semaev_dlf": sorted({(x["d_lf"] - y["d_lf"]) for x in n3 for y in sem if x["d_lf"] is not None and y["d_lf"] is not None}),
        "not_plantable_draws": sum(1 for d in draws if "not_plantable" in d),
        "not_computed_wall_guard": len(not_computed),
        "certificates_all_verified": cert_all_ok,
        "s_poly_crosscheck_all": all(d.get("s_poly_crosscheck", True) for d in draws),
        "engine_cross_check_all_agree": xcheck_all_ok,
        "P1_closure_dff_equals_graded_dff_all_semaev": p1_all_ok,
        "soundness_subsample": [{"curve_seed": d["curve_seed"], "target_seed": d["target_seed"], "p": d["p"],
                                 **{k: v for k, v in d["soundness_subsample"].items() if k != "zeros"}}
                                for d in draws if "soundness_subsample" in d],
        "elapsed_seconds_script": round(elapsed(), 3),
    }
    valid = cert_all_ok and xcheck_all_ok and metrics["s_poly_crosscheck_all"] and not not_computed
    reason = None
    if not valid:
        reason = "certificate, S-polynomial cross-check or engine cross-check failure" if (cert_all_ok is False or not xcheck_all_ok or not metrics["s_poly_crosscheck_all"]) else "wall guard: systems not computed (resource_exhaustion)"
    params = common_params("stage-2-ladder" if m == 2 else "stage-3-optional-m3",
                           ["NULL-1-SUPPORT-MATCHED", "NULL-2-RANDOM-MULTILINEAR", "NULL-3-BLOCK-FACTORED", "NEARBY-NON-CURVE-CUBIC",
                            "CTRL-ITERATION-COUNT"] + (["CTRL-S1-BASELINE"] if s == 1 else []),
                           {"m": m, "d": 2, "s": s, "primes": primes, "curve_seeds": curve_seeds, "target_seeds": target_seeds,
                            "null_seeds": NULL_SEEDS, "plant_window": window, "D_max": dmax, "D_null_84cdb7": D_null})
    return RunResult(run_suffix=args.run_suffix, curve_id=f"generic-j curves seeds {curve_seeds} at p in {primes}", seed=curve_seeds[0],
                     parameters=params, metrics=jsonable(metrics), certificate=manifest_cert, valid=valid, invalid_reason=reason,
                     stdout="\n".join(out) + "\n", stderr="",
                     raw=jsonable({"draws": draws, "noncurve": noncurve, "null2_objects": null2_objs, "null3_objects": null3_objs,
                                   "not_computed": not_computed}))


# --------------------------------------------------------------------------
# Stage 1: s = 1 slice
# --------------------------------------------------------------------------
def direct_to_digit_s1(direct_ring: Ring, digit_ring: Ring, poly: dict) -> dict:
    """Reduce an ordinary-ring polynomial in x_1..x_m modulo x_k^2 - x_k and rename x_k -> a_k."""
    out: dict = {}
    for (mask, exps), c in poly.items():
        m = 0
        for k, e in enumerate(exps):
            if e:
                m |= 1 << k
        out = digit_ring.add(out, {(m, ()): c})
    return out


def run_s1slice(args) -> RunResult:
    m, s = 2, 1
    out: list = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    draws: list = []
    PARTIAL["draws"] = draws
    cert_ok = True
    manifest_cert = {"kind": "none", "note": "no planted target"}
    for p in PRIMES:
        dring = Ring(p, 2, 0)
        dcols = ColumnSpace.build(dring, D_MAX)
        for cs in CURVE_SEEDS:
            curve = make_curve(p, cs)
            for ts in TARGET_SEEDS:
                tgt = plant_target(curve, m, ts, 2)
                draw = {"p": p, "curve_seed": cs, "curve": {k: curve[k] for k in ("a", "b", "j")}, "target_seed": ts}
                if tgt is None:
                    draw["not_plantable"] = "no on-curve x in {0, 1}"
                    draws.append(draw)
                    log(f"p={p} curve={cs} target={ts}: NOT PLANTABLE at s = 1")
                    continue
                cert_ok &= tgt["verified_independent_add"] and tgt["verified_harness_semaev"]
                if manifest_cert["kind"] == "none":
                    manifest_cert = tgt["certificate"]
                sd = s3_dict(curve["a"], curve["b"], tgt["x_R"], p)
                draw["target"] = {k: tgt[k] for k in ("x_R", "R", "summands", "verified_independent_add", "verified_harness_semaev")}
                draw["certificate"] = tgt["certificate"]
                # (a) direct presentation, B = 2, ordinary ring: [S_3(x1, x2, x_R), x1(x1-1), x2(x2-1)]
                dp = direct_presentation(p, m, 2, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
                oring = dp.ring
                ocols = ColumnSpace.build(oring, D_MAX)
                # (b) digit presentation, s = 1, squarefree ring: [S~]
                gp = digit_presentation(p, m, 2, s, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
                assert gp.ring == dring
                g = gp.generators[0]
                ident = direct_to_digit_s1(oring, dring, dp.generators[0]) == g
                memb_ok = all(direct_to_digit_s1(oring, dring, f) == {} for f in dp.membership)
                dmin_o = min(oring.degree(f) for f in dp.generators)
                ra = C.measure_system(oring, list(dp.generators), ocols, dmin_o, D_MAX, engine="sparse", cross_check=True, certificate=False)
                rb = C.measure_system(dring, [g], dcols, max(dring.degree(g), 1), D_MAX, engine="sparse", cross_check=True, certificate=True)
                # (c) the polynomial ring on the REDUCED generator (multilinear lift of S~) plus the field equations:
                #     Huang-Kosters-Yeo's own setting for the object the digit closure computes (note section 2)
                g_lift = {}
                for (mask, _e), c in g.items():
                    exps = tuple(1 if (mask >> k) & 1 else 0 for k in range(2))
                    g_lift[(0, exps)] = c
                rc = C.measure_system(oring, [g_lift] + list(dp.membership), ocols, min(oring.degree(g_lift), 2), D_MAX, engine="sparse",
                                      cross_check=True, certificate=False)
                draw.update({"direct_generator_degrees": ra["generator_degrees"], "digit_generator": dring.to_string(g, ["a1", "a2"]),
                             "identification_term_for_term": ident, "membership_reduces_to_zero_in_quotient": memb_ok,
                             "direct": ra, "digit": rb, "direct_reduced": rc,
                             "direct_summary": summary(ra), "digit_summary": summary(rb), "direct_reduced_summary": summary(rc),
                             "histories_identical_direct": [h["D"] for h in ra["history"] if h["fall"]] == rb["falls"],
                             "histories_identical_direct_reduced": [h["D"] for h in rc["history"] if h["fall"]] == rb["falls"],
                             "floor_d_lf_ge_2": (rb["d_lf"] is not None and rb["d_lf"] >= 2),
                             "closure_dff_equals_graded_dff": rb["closure_dff_equals_graded_dff"]})
                draws.append(draw)
                log(f"p={p} curve={cs} target={ts} x_R={tgt['x_R']}: ident={ident} digit {draw['digit_summary']} direct {draw['direct_summary']} "
                    f"direct-reduced {draw['direct_reduced_summary']} same_falls(direct)={draw['histories_identical_direct']} same_falls(direct-reduced)={draw['histories_identical_direct_reduced']}")
    ok_draws = [d for d in draws if "digit" in d]
    metrics = {"control": "CTRL-S1-BASELINE", "draws_planned": len(PRIMES) * len(CURVE_SEEDS) * len(TARGET_SEEDS),
               "draws_plantable": len(ok_draws), "not_plantable": [(d["p"], d["curve_seed"], d["target_seed"]) for d in draws if "not_plantable" in d],
               "identification_all": all(d["identification_term_for_term"] and d["membership_reduces_to_zero_in_quotient"] for d in ok_draws),
               "floor_d_lf_ge_2_all": all(d["floor_d_lf_ge_2"] for d in ok_draws),
               "closure_dff_equals_graded_dff_all": all(d["closure_dff_equals_graded_dff"] for d in ok_draws),
               "digit_histories_identical_to_direct_all": all(d["histories_identical_direct"] for d in ok_draws),
               "digit_histories_identical_to_direct_reduced_all": all(d["histories_identical_direct_reduced"] for d in ok_draws),
               "digit_pairs": sorted({(d["digit"]["d_ff"], d["digit"]["d_lf"]) for d in ok_draws}, key=str),
               "direct_pairs": sorted({(d["direct"]["d_ff"], d["direct"]["d_lf"]) for d in ok_draws}, key=str),
               "direct_reduced_pairs": sorted({(d["direct_reduced"]["d_ff"], d["direct_reduced"]["d_lf"]) for d in ok_draws}, key=str),
               "direct_generator_degrees": sorted({tuple(d["direct_generator_degrees"]) for d in ok_draws}, key=str),
               "digit_all_certified": all(not d["digit"]["right_censored"] for d in ok_draws),
               "engine_cross_check_all_agree": all(d["digit"]["cross_check"]["agree"] and d["direct"]["cross_check"]["agree"]
                                                  and d["direct_reduced"]["cross_check"]["agree"] for d in ok_draws),
               "certificates_all_verified": cert_ok}
    metrics["s1_pass"] = bool(ok_draws) and metrics["identification_all"] and metrics["floor_d_lf_ge_2_all"] and metrics["closure_dff_equals_graded_dff_all"]
    valid = cert_ok and metrics["engine_cross_check_all_agree"]
    params = common_params("stage-1-closure-and-fixtures", ["CTRL-S1-BASELINE"],
                           {"m": 2, "d": 2, "s": 1, "B_direct": 2, "primes": PRIMES, "curve_seeds": CURVE_SEEDS, "target_seeds": TARGET_SEEDS,
                            "plant_window": 2, "D_max": D_MAX})
    return RunResult(run_suffix=args.run_suffix, curve_id=f"generic-j curves seeds {CURVE_SEEDS} at p in {PRIMES}", seed=CURVE_SEEDS[0],
                     parameters=params, metrics=jsonable(metrics), certificate=manifest_cert, valid=valid,
                     invalid_reason=None if valid else "certificate or engine cross-check failure",
                     stdout="\n".join(out) + "\n", stderr="", raw=jsonable({"draws": draws}))


# --------------------------------------------------------------------------
# Stage 1: known-answer fixtures
# --------------------------------------------------------------------------
def random_poly(ring: Ring, rng: random.Random, degree: int, density: float, homogeneous: bool = False) -> dict:
    out = {}
    monos = ring.monomials_exact(degree) if homogeneous else ring.monomials_upto(degree)
    for mo in monos:
        if rng.random() < density:
            out[mo] = rng.randrange(1, ring.p)
    return out


def member(ring: Ring, gens, columns: ColumnSpace, dmin: int, D: int, poly: dict, T) -> bool:
    res = C.closure_dense(ring, gens, columns, dmin, D, T=T, want_basis=True)
    Bv = res["basis"]
    vec = np.zeros(Bv.N)
    for mo, c in poly.items():
        vec[columns.index[mo]] = c
    return not Bv._reduce(vec[None, :]).any()


def planted_fixture(ring: Ring, seed: int, dmax: int) -> dict:
    rng = random.Random(seed)
    f1 = random_poly(ring, rng, 2, 0.7)
    f2 = random_poly(ring, rng, 2, 0.7)
    while True:
        u = random_poly(ring, rng, 1, 0.8, True)
        v = random_poly(ring, rng, 1, 0.8, True)
        h = random_poly(ring, rng, 2, 0.5)
        g = ring.add(ring.add(ring.mul(u, f1), ring.mul(v, f2)), h)
        if ring.degree(g) == 3 and ring.degree(h) == 2:
            break
    cols = ColumnSpace.build(ring, dmax)
    T = C.multiplication_table(ring, cols)
    pf = preflight_record(ring, [f1, f2, g], dmax)
    base = C.measure_system(ring, [f1, f2], cols, 2, dmax, engine="dense", cross_check=True, certificate=False, T=T)
    ext = C.measure_system(ring, [f1, f2, g], cols, 2, dmax, engine="dense", cross_check=True, certificate=False, T=T)
    checks = {
        "ext_fall_at_deg_g": 3 in ext["falls"],
        "ext_d_ff_equals_deg_g": ext["d_ff"] == 3,
        "base_no_fall_at_3": 3 not in base["falls"],
        "h_in_V3_ext": member(ring, [f1, f2, g], cols, 2, 3, h, T),
        "h_not_in_V2_ext": not member(ring, [f1, f2, g], cols, 2, 2, h, T),
        "h_not_in_V3_base": not member(ring, [f1, f2], cols, 2, 3, h, T),
        "ext_iteration_count_at_3": ext["fall_iteration_counts"].get("3"),
        "ext_iteration_count_at_3_ge_2": (ext["fall_iteration_counts"].get("3") or 0) >= 2,
        "engines_agree": ext["cross_check"]["agree"] and base["cross_check"]["agree"],
        "ext_closure_dff_equals_graded_dff": ext["closure_dff_equals_graded_dff"],
    }
    checks["pass"] = all(v for k, v in checks.items() if isinstance(v, bool))
    return {"ring": {"p": ring.p, "n_sq": ring.n_sq, "n_free": ring.n_free, "mode": ring.mode}, "seed": seed, "D_max": dmax,
            "terms": {"f1": len(f1), "f2": len(f2), "u": len(u), "v": len(v), "h": len(h), "g": len(g)},
            "degrees": {"f1": ring.degree(f1), "f2": ring.degree(f2), "g": ring.degree(g), "h": ring.degree(h)},
            "preflight": pf, "base": base, "ext": ext, "checks": checks}


def run_fixture(args) -> RunResult:
    out: list = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    p = 4099
    P_sq = planted_fixture(Ring(p, 10, 0), FIXTURE_SEED, 5)
    log(f"fixture P (squarefree, n=10, seed {FIXTURE_SEED}): checks {P_sq['checks']}; ext falls {P_sq['ext']['falls']}; base falls {P_sq['base']['falls']}")
    P_ord = planted_fixture(Ring(p, 0, 3), FIXTURE_SEED, 5)
    log(f"fixture P (ordinary, 3 free vars, seed {FIXTURE_SEED}): checks {P_ord['checks']}; ext falls {P_ord['ext']['falls']}; base falls {P_ord['base']['falls']}")
    hr = Ring(p, 3, 0)
    hg = poly_from_terms(hr, [(1, [0, 1], []), (1, [2], [])])
    hc = ColumnSpace.build(hr, D_MAX)
    Hres = C.measure_system(hr, [hg], hc, 2, D_MAX, engine="sparse", cross_check=True, certificate=True)
    hchecks = {"history_is_{3}": Hres["falls"] == [3], "dim_V3_is_5": Hres["history"][1]["dim_V"] == 5,
               "iteration_count_at_3_is_2": Hres["fall_iteration_counts"].get("3") == 2,
               "certified": not Hres["right_censored"], "engines_agree": Hres["cross_check"]["agree"],
               "closure_dff_equals_graded_dff": Hres["closure_dff_equals_graded_dff"]}
    hchecks["pass"] = all(hchecks.values())
    log(f"fixture H (a1 a2 + a3): {hchecks}; history {[(h['D'], h['dim_V'], h['fall_dim'], h['iteration_count']) for h in Hres['history']]}")
    metrics = {"control": "CTRL-KNOWN-ANSWER-FIXTURE",
               "substitution": "F_2 Weil-descent fixture not exhibited (conformance to Theorem 2.6 not establishable from the retrieved statement; stage1-closure-convention.md section 4); PLANTED-FALL fixture is the known answer per the contract",
               "fixture_P_squarefree": {"checks": P_sq["checks"], "ext_falls": P_sq["ext"]["falls"], "base_falls": P_sq["base"]["falls"],
                                        "ext_iteration_counts": P_sq["ext"]["fall_iteration_counts"], "degrees": P_sq["degrees"], "preflight": P_sq["preflight"]},
               "fixture_P_ordinary": {"checks": P_ord["checks"], "ext_falls": P_ord["ext"]["falls"], "base_falls": P_ord["base"]["falls"],
                                      "ext_iteration_counts": P_ord["ext"]["fall_iteration_counts"], "degrees": P_ord["degrees"], "preflight": P_ord["preflight"]},
               "fixture_H": {"checks": hchecks, "falls": Hres["falls"], "history": [{k: h[k] for k in C.HISTORY_KEYS} for h in Hres["history"]],
                             "certificate": Hres["certificate"]},
               "known_answer_pass": P_sq["checks"]["pass"] and P_ord["checks"]["pass"] and hchecks["pass"],
               "elapsed_seconds_script": round(elapsed(), 3)}
    valid = P_sq["checks"]["engines_agree"] and P_ord["checks"]["engines_agree"] and hchecks["engines_agree"]
    params = common_params("stage-1-closure-and-fixtures", ["CTRL-KNOWN-ANSWER-FIXTURE", "CTRL-ITERATION-COUNT"],
                           {"p": p, "fixture_seed": FIXTURE_SEED, "D_max_P": 5, "D_max_H": D_MAX})
    return RunResult(run_suffix=args.run_suffix, curve_id="curve-free fixtures", seed=FIXTURE_SEED, parameters=params,
                     metrics=jsonable(metrics), certificate={"kind": "none", "note": "known-answer fixtures; nothing to certify"},
                     valid=valid, invalid_reason=None if valid else "engine cross-check disagreement",
                     stdout="\n".join(out) + "\n", stderr="", raw=jsonable({"P_squarefree": P_sq, "P_ordinary": P_ord, "H": Hres}))


# --------------------------------------------------------------------------
# Stage 1: CTRL-DFF-AGREEMENT on EXP-PFDR-5726af's instances
# --------------------------------------------------------------------------
def run_dffagree(args) -> RunResult:
    out: list = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    p = 4099
    sib_runs = {2: "RUN-PFDR-5726af-m2-s2-gate", 3: "RUN-PFDR-5726af-m2-s3", 4: "RUN-PFDR-5726af-m2-s4", 5: "RUN-PFDR-5726af-m2-s5"}
    sib = {}
    for s, rid in sib_runs.items():
        path = os.path.join(REPO, "experiments", "EXP-PFDR-5726af", "runs", rid, "raw-result.json")
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        sib[s] = {"run_id": rid, "sha256": sha256_file(path),
                  "draws": {(d["p"], d["curve_seed"], d["target"]["target_seed"]): d for d in data["raw"]["draws"] if d["p"] == p}}
    rows: list = []
    PARTIAL["rows"] = rows
    cert_ok = True
    xcheck_ok = True
    manifest_cert = {"kind": "none"}
    for s in (2, 3, 4, 5):
        n = 2 * s
        ring = Ring(p, n, 0)
        cols = ColumnSpace.build(ring, D_MAX)
        full = ColumnSpace.build(ring, n) if n > D_MAX else cols
        T = C.multiplication_table(ring, full)
        Ev = C.evaluation_matrix(ring, full)
        for cs in (1101, 1102, 1103):
            curve = make_curve(p, cs)
            for ts in (1, 2):
                tgt = plant_target(curve, 2, ts, PLANT_WINDOW_M2)
                cert_ok &= tgt["verified_independent_add"] and tgt["verified_harness_semaev"]
                if manifest_cert["kind"] == "none":
                    manifest_cert = tgt["certificate"]
                sd = s3_dict(curve["a"], curve["b"], tgt["x_R"], p)
                pres = digit_presentation(p, 2, 2, s, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
                g = pres.generators[0]
                res = C.measure_system(ring, [g], cols, ring.degree(g), D_MAX, engine=engine_for(cols, D_MAX), cross_check=True,
                                       certificate=True, T=T, Ev=Ev)
                xcheck_ok &= bool(res["cross_check"]["agree"])
                sd_ = sib[s]["draws"].get((p, cs, ts))
                row = {"s": s, "p": p, "curve_seed": cs, "target_seed": ts, "curve": {"a": curve["a"], "b": curve["b"]}, "x_R": tgt["x_R"],
                       "same_instance_as_5726af": bool(sd_) and sd_["curve"]["a"] == curve["a"] and sd_["curve"]["b"] == curve["b"] and sd_["target"]["x_R"] == tgt["x_R"],
                       "closure_d_ff": res["d_ff"], "graded_d_ff_here": res["graded"]["graded_d_ff"],
                       "graded_d_ff_5726af": sd_["semaev"]["d_ff"] if sd_ else None,
                       "graded_layers_here": res["graded"]["layers"],
                       "graded_layers_5726af": [(L["D"], L["full_rank"], L["top_rank"], L["fall_dim"]) for L in sd_["semaev"]["layers"]] if sd_ else None,
                       "closure_d_lf": res["d_lf"], "falls": res["falls"], "right_censored": res["right_censored"],
                       "iteration_counts": res["fall_iteration_counts"], "engine": res["engine"], "cross_check_agree": res["cross_check"]["agree"],
                       "certificate": tgt["certificate"], "seconds": res["seconds"]}
                row["agree"] = row["closure_d_ff"] == row["graded_d_ff_here"] == row["graded_d_ff_5726af"]
                rows.append(row)
                log(f"s={s} curve={cs} target={ts} x_R={tgt['x_R']} same_instance={row['same_instance_as_5726af']}: closure d_ff={res['d_ff']} graded={row['graded_d_ff_here']} 5726af={row['graded_d_ff_5726af']} agree={row['agree']} d_lf={res['d_lf']} censored={res['right_censored']} t={elapsed():.0f}s")
    metrics = {"control": "CTRL-DFF-AGREEMENT", "rows": len(rows),
               "P1_all_agree": all(r["agree"] for r in rows),
               "same_instance_all": all(r["same_instance_as_5726af"] for r in rows),
               "disagreements": [r for r in rows if not r["agree"]],
               "per_s": {str(s): {"closure_d_ff": sorted({r["closure_d_ff"] for r in rows if r["s"] == s}, key=str),
                                  "graded_5726af": sorted({r["graded_d_ff_5726af"] for r in rows if r["s"] == s}, key=str),
                                  "closure_d_lf": sorted({r["closure_d_lf"] for r in rows if r["s"] == s}, key=str),
                                  "censored": sum(1 for r in rows if r["s"] == s and r["right_censored"])} for s in (2, 3, 4, 5)},
               "sibling_runs": {str(s): {"run_id": v["run_id"], "raw_result_sha256": v["sha256"]} for s, v in sib.items()},
               "certificates_all_verified": cert_ok, "engine_cross_check_all_agree": xcheck_ok, "elapsed_seconds_script": round(elapsed(), 3)}
    valid = cert_ok and xcheck_ok
    params = common_params("stage-1-closure-and-fixtures", ["CTRL-DFF-AGREEMENT"],
                           {"m": 2, "d": 2, "s_values": [2, 3, 4, 5], "p": p, "curve_seeds": [1101, 1102, 1103], "target_seeds": [1, 2],
                            "plant_window": PLANT_WINDOW_M2, "D_max": D_MAX})
    return RunResult(run_suffix=args.run_suffix, curve_id="EXP-PFDR-5726af instances, p = 4099, seeds 1101..1103", seed=1101,
                     parameters=params, metrics=jsonable(metrics), certificate=manifest_cert, valid=valid,
                     invalid_reason=None if valid else "certificate or engine cross-check failure",
                     stdout="\n".join(out) + "\n", stderr="", raw=jsonable({"rows": rows}))


# --------------------------------------------------------------------------
# CTRL-EQUAL-DS-SPREAD
# --------------------------------------------------------------------------
def run_equalds(args) -> RunResult:
    d, s = args.d, args.s
    p, B, m = 65537, 64, 2
    dmax = 6
    assert d ** s == B
    out: list = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    draws: list = []
    PARTIAL["draws"] = draws
    cert_ok = True
    xcheck_ok = True
    manifest_cert = {"kind": "none"}
    not_computed: list = []
    pres0 = digit_presentation(p, m, d, s, lambda r, xs: [{r.one(): 1}])
    ring = pres0.ring
    cols = ColumnSpace.build(ring, dmax)
    T = C.multiplication_table(ring, cols)
    full = None
    Ev = None
    if ring.n_free == 0 and (1 << ring.n_sq) <= C.CERTIFICATE_COLUMN_LIMIT:
        full = ColumnSpace.build(ring, ring.n_sq)
        T = C.multiplication_table(ring, full)
        Ev = C.evaluation_matrix(ring, full)
    log(f"equal-d^s (d,s)=({d},{s}) B={B} p={p}: ring mode {ring.mode} n_sq={ring.n_sq} n_free={ring.n_free} columns(<= {dmax}) = {cols.ncols_upto(dmax)} engine={engine_for(cols, dmax)}")
    for cs in CURVE_SEEDS[:3]:
        curve = make_curve(p, cs)
        for ts in TARGET_SEEDS:
            if guard_tripped():
                not_computed.append({"curve_seed": cs, "target_seed": ts, "reason": "wall guard"})
                continue
            tgt = plant_target(curve, m, ts, B)
            cert_ok &= tgt["verified_independent_add"] and tgt["verified_harness_semaev"]
            if manifest_cert["kind"] == "none":
                manifest_cert = tgt["certificate"]
            sd = s3_dict(curve["a"], curve["b"], tgt["x_R"], p)
            pres = digit_presentation(p, m, d, s, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
            gens = list(pres.generators)
            degs = [ring.degree(f) for f in gens]
            pf = preflight_record(ring, gens, dmax)
            dmin = min(dg for dg in degs if dg >= 0)
            res = C.measure_system(ring, gens, cols, dmin, dmax, engine=engine_for(cols, dmax), cross_check=(cs == XCHECK_CURVE and ts == XCHECK_TARGET) or engine_for(cols, dmax) == "sparse",
                                   certificate=(Ev is not None), T=T, Ev=Ev)
            xcheck_ok &= res.get("cross_check", {}).get("agree", True) is not False
            draw = {"d": d, "s": s, "p": p, "curve_seed": cs, "curve": {k: curve[k] for k in ("a", "b", "j")}, "target_seed": ts,
                    "target": {k: tgt[k] for k in ("x_R", "R", "summands", "verified_independent_add", "verified_harness_semaev")},
                    "certificate": tgt["certificate"], "generator_degrees": degs, "generator_count": len(gens),
                    "membership_generators_enter_window": [dg <= dmax for dg in degs[1:]], "preflight": pf, "result": res, "summary": summary(res)}
            draws.append(draw)
            log(f"  curve={cs} target={ts} x_R={tgt['x_R']}: degs={degs} {draw['summary']} t={elapsed():.0f}s")
    sm = [dw["summary"] for dw in draws]
    metrics = {"control": "CTRL-EQUAL-DS-SPREAD", "presentation": {"d": d, "s": s, "B": B, "p": p, "D_max": dmax, "ring_mode": ring.mode,
                                                                   "columns": cols.ncols_upto(dmax), "engine": engine_for(cols, dmax)},
               "pairs": [{"curve_seed": dw["curve_seed"], "target_seed": dw["target_seed"], "d_ff": dw["summary"]["d_ff"], "d_lf": dw["summary"]["d_lf"],
                          "right_censored": dw["summary"]["right_censored"], "no_fall_in_window": dw["summary"]["no_fall_in_window"]} for dw in draws],
               "d_ff_values": sorted({x["d_ff"] for x in sm}, key=str), "d_lf_values": sorted({x["d_lf"] for x in sm}, key=str),
               "right_censored": sum(1 for x in sm if x["right_censored"]), "n": len(sm),
               "certificates_all_verified": cert_ok, "engine_cross_check_all_agree": xcheck_ok, "not_computed": not_computed,
               "elapsed_seconds_script": round(elapsed(), 3)}
    valid = cert_ok and xcheck_ok and not not_computed
    params = common_params("stage-2-ladder", ["CTRL-EQUAL-DS-SPREAD"],
                           {"m": 2, "d": d, "s": s, "B": B, "p": p, "curve_seeds": CURVE_SEEDS[:3], "target_seeds": TARGET_SEEDS, "plant_window": B, "D_max": dmax})
    return RunResult(run_suffix=args.run_suffix, curve_id=f"generic-j curves seeds {CURVE_SEEDS[:3]} at p = {p}", seed=CURVE_SEEDS[0],
                     parameters=params, metrics=jsonable(metrics), certificate=manifest_cert, valid=valid,
                     invalid_reason=None if valid else ("wall guard" if not_computed else "certificate or engine cross-check failure"),
                     stdout="\n".join(out) + "\n", stderr="", raw=jsonable({"draws": draws, "not_computed": not_computed}))


# --------------------------------------------------------------------------
def package_checksums(run_id: str, out_root) -> None:
    run_dir = os.path.join(out_root or EXP_DIR, "runs", run_id)
    sums = {nm: sha256_file(os.path.join(run_dir, nm)) for nm in sorted(os.listdir(run_dir)) if nm != "package-sha256.json"}
    with open(os.path.join(run_dir, "package-sha256.json"), "w", encoding="utf-8") as fh:
        json.dump({"run_id": run_id, "files": sums}, fh, indent=2)


class _LateStatus:
    def __init__(self, get):
        self._get = get

    def __str__(self) -> str:
        return self._get()


yaml.SafeDumper.add_representer(_LateStatus, lambda dumper, data: dumper.represent_str(str(data)))


def main() -> None:
    set_limits()
    ap = argparse.ArgumentParser()
    ap.add_argument("subcommand", choices=["s1slice", "fixture", "dffagree", "cell", "equalds", "m3cell"])
    ap.add_argument("--run-suffix", required=True)
    ap.add_argument("--s", type=int, default=2)
    ap.add_argument("--p", type=int, default=4099)
    ap.add_argument("--d", type=int, default=2)
    ap.add_argument("--out-root", default=None, help="scratch dry runs only; official runs omit it")
    args = ap.parse_args()
    fn = {"s1slice": run_s1slice, "fixture": run_fixture, "dffagree": run_dffagree, "cell": run_cell,
          "equalds": run_equalds, "m3cell": lambda a: run_cell(a, m=3)}[args.subcommand]
    command = "python3 " + " ".join(os.path.relpath(sys.argv[0], REPO) if i == 0 else a for i, a in enumerate(sys.argv))
    holder = {}

    def wrapped() -> RunResult:
        try:
            r = fn(args)
        except (MemoryError, PreflightAbort, TimeoutError) as exc:
            r = RunResult(run_suffix=args.run_suffix, curve_id="n/a", seed=0, parameters={"error": type(exc).__name__, **common_params("aborted", [], {})},
                          metrics={"failure_class": "resource_exhaustion", "error": str(exc), "elapsed_seconds_script": round(elapsed(), 3)},
                          certificate={"kind": "none"}, valid=False, invalid_reason=f"{type(exc).__name__}: failed_infrastructure (resource_exhaustion), never evidence",
                          stderr=f"{type(exc).__name__}: {exc}\n", raw=jsonable({"partial": PARTIAL}))
            holder["status"] = "failed_infrastructure"
        except Exception as exc:  # any crash is failed_infrastructure, never evidence
            import traceback
            r = RunResult(run_suffix=args.run_suffix, curve_id="n/a", seed=0, parameters={"error": type(exc).__name__},
                          metrics={"failure_class": "infrastructure_error", "error": str(exc), "elapsed_seconds_script": round(elapsed(), 3)},
                          certificate={"kind": "none"}, valid=False, invalid_reason="crash (failed_infrastructure)",
                          stderr=traceback.format_exc(), raw=jsonable({"partial": PARTIAL}))
            holder["status"] = "failed_infrastructure"
        else:
            holder["status"] = "completed_valid" if r.valid else "completed_invalid"
            if not r.valid and r.invalid_reason and "wall guard" in r.invalid_reason:
                holder["status"] = "failed_infrastructure"
        if elapsed() > WALL_CAP_SECONDS:
            holder["status"] = "failed_infrastructure"
            r.valid = False
            r.invalid_reason = f"wall clock {elapsed():.0f}s exceeded the {WALL_CAP_SECONDS}s per-run cap (resource_exhaustion)"
        signal.alarm(0)
        holder["result"] = r
        return r

    run_id = run_wrapped(EXP_ID, AREA, wrapped, status=_LateStatus(lambda: holder["status"]), command=command, out_root=args.out_root)
    package_checksums(run_id, args.out_root)
    print(run_id)
    print(f"status={holder['status']} elapsed={elapsed():.1f}s")


if __name__ == "__main__":
    main()

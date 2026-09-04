#!/usr/bin/env python3
"""EXP-PFDR-fd901a -- p-independence calibration of the (2, 2, 3) digit-presented
decomposition system (H-PFDR-09e1b0, IDEA-20260903-26aa81).

Executor implementation for TASK-20260903-5a62de.  Every number written here is
an exact graded rank over F_p produced by the shared meter ``harness/macaulay_fp``
(TASK-20260903-ba41aa).  No Groebner basis is computed anywhere; no timing is a
metric; no floating point touches a rank.

Planned runs (one immutable run directory each, written through
``harness.runner.run_wrapped`` so timing is wrapper-measured):

    fixture-p4099      Stage 1: shared meter on the frozen fixture (curve seed
                       1101, target seed 1, p = 4099) against an INDEPENDENT
                       second implementation (sympy-built S~, dense matrix,
                       sympy DomainMatrix rank over GF(p) + naive elimination);
                       also the Stage 0 content-prime numbers.
    posctrl-p4099      Stage 2: direct presentation, B = round(sqrt(p)) = 64.
    posctrl-p16411     Stage 2: direct presentation, B = 128.
    sweep-p4099        Stage 3: all arms at p = 4099.
    sweep-p64          Stage 3: all arms at the largest prime below 2^64.
    sweep-p256         Stage 3: all arms at the P-256 prime + the named curve.

Usage:  python3 experiments/EXP-PFDR-fd901a/run_experiment.py <stage> [--suffix S]
        stages: fixture | posctrl-4099 | posctrl-16411 | sweep-4099 | sweep-64 | sweep-256
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import random
import resource
import signal
import subprocess
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import sympy  # noqa: E402

from harness import runner  # noqa: E402
from harness.macaulay_fp import (  # noqa: E402
    P256_PRIME,
    ColumnSpace,
    Ring,
    analyze_degrees,
    digit_presentation,
    direct_presentation,
    first_nonzero_fall,
    first_nontrivial_syzygy,
    semiregular_prediction,
    substitute,
    support_matched_system,
)
from harness.semaev import s3_eval, s3_expr, verify_decomposition_certificate  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-PFDR-fd901a"
EXP_AREA = "PFDR-fd901a"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)

# ---------------------------------------------------------------------------
# Frozen parameters (copied from the contract; never edited here)
# ---------------------------------------------------------------------------
M, D_BASE, S_DIGITS = 2, 2, 3          # (m, d, s) = (2, 2, 3)
N_DIGITS = M * S_DIGITS                # 6 digit variables
WINDOW = 1 << S_DIGITS                 # [0, 8)
D_MIN, D_MAX = 3, 6                    # degrees 3..6
P_SMALL = 4099
P_64 = 2**64 - 59                      # expected largest prime below 2^64 (re-confirmed)
P_256 = P256_PRIME                     # 2^256 - 2^224 + 2^192 + 2^96 - 1
CURVE_SEEDS = [1100 + k for k in range(1, 9)]        # 1101..1108
TARGET_SEEDS = [1, 2, 3, 4, 5]
NULL_SEEDS = [7, 11, 13, 17, 19]
POSCTRL_CURVE_SEEDS = [2101, 2102, 2103]
POSCTRL_TARGET_SEEDS = [1, 2]
POSCTRL_PRIMES = [4099, 16411]
SECONDARY_B = 8
FIXTURE = {"p": 4099, "curve_seed": 1101, "target_seed": 1}
WALL_CLOCK_SECONDS_PER_RUN = 3600
MAX_MEMORY_GB = 8
NIST_P256_A = P256_PRIME - 3
NIST_P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
METER_FILES = [
    "harness/macaulay_fp/__init__.py", "harness/macaulay_fp/columns.py",
    "harness/macaulay_fp/koszul.py", "harness/macaulay_fp/linalg.py",
    "harness/macaulay_fp/localization.py", "harness/macaulay_fp/macaulay.py",
    "harness/macaulay_fp/nulls.py", "harness/macaulay_fp/poly.py",
    "harness/macaulay_fp/presentations.py", "harness/macaulay_fp/series.py",
    "tests/test_macaulay_fp.py",
]
METER_COMMIT = "2d2083e5"  # tooling(TASK-20260903-ba41aa) snapshot, as named in the handoff


class RunBudgetExceeded(RuntimeError):
    pass


def _alarm(signum, frame):  # pragma: no cover - only under a real timeout
    raise RunBudgetExceeded(f"wall clock budget of {WALL_CLOCK_SECONDS_PER_RUN} s exceeded")


def install_budget() -> None:
    soft = MAX_MEMORY_GB * 1024**3
    try:
        resource.setrlimit(resource.RLIMIT_AS, (soft, soft))
    except (ValueError, OSError) as exc:  # recorded by caller via stderr
        print(f"WARNING: could not set RLIMIT_AS: {exc}", file=sys.stderr)
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(WALL_CLOCK_SECONDS_PER_RUN)


# ---------------------------------------------------------------------------
# Number theory (self-contained, exact)
# ---------------------------------------------------------------------------
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)  # deterministic for n < 3.3e24


def miller_rabin(n: int, bases: Sequence[int] = MR_BASES) -> bool:
    if n < 2:
        return False
    for q in bases:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in bases:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(a: int, p: int) -> Optional[int]:
    """Tonelli-Shanks; returns the smaller root or None."""
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(a, (p + 1) // 4, p)
    else:
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while legendre(z, p) != -1:
            z += 1
        c = pow(z, q, p)
        r = pow(a, (q + 1) // 2, p)
        t = pow(a, q, p)
        m = s
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = t2 * t2 % p
                i += 1
            b = pow(c, 1 << (m - i - 1), p)
            r = r * b % p
            c = b * b % p
            t = t * c % p
            m = i
    assert r * r % p == a
    return min(r, p - r)


def hint(*parts) -> int:
    """SHA-256-derived integer from a label (deterministic, version-independent)."""
    return int(hashlib.sha256(":".join(str(x) for x in parts).encode()).hexdigest(), 16)


# ---------------------------------------------------------------------------
# Curves and planting (the executor's OWN point addition; verification below
# uses harness.toycurve / harness.semaev, which are independent code paths)
# ---------------------------------------------------------------------------
def ec_add(p: int, a: int, P: Tuple[int, int], Q: Tuple[int, int]):
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def window_x_on_curve(p: int, a: int, b: int, B: int) -> List[int]:
    out = []
    for x in range(B):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0 or legendre(rhs, p) == 1:
            out.append(x)
    return out


def draw_curve(p: int, seed: int, B: int, tag: str = "curve") -> dict:
    """Random short-Weierstrass curve with nonzero discriminant and >= 2 on-curve
    x in [0, B); rejection count reported."""
    rejections = {"singular": 0, "window": 0}
    attempt = 0
    while True:
        a = hint(EXP_ID, tag, p, seed, "A", attempt) % p
        b = hint(EXP_ID, tag, p, seed, "B", attempt) % p
        attempt += 1
        if (4 * a * a * a + 27 * b * b) % p == 0:
            rejections["singular"] += 1
            continue
        xs = window_x_on_curve(p, a, b, B)
        if len(xs) < 2:
            rejections["window"] += 1
            continue
        return {"p": p, "a": a, "b": b, "seed": seed, "attempts": attempt,
                "rejections": rejections, "window_x": xs, "B": B, "kind": "random"}


def draw_singular_cubic(p: int, seed: int, B: int) -> dict:
    """4A^3 + 27B^2 = 0 with A = -3t^2, B = 2t^3, t != 0: y^2 = (x - t)^2 (x + 2t),
    a nodal cubic with no elliptic group law.  Requires >= 2 window x with
    x^3 + Ax + B a square (x != t, the node)."""
    rejections = {"t_zero": 0, "window": 0}
    attempt = 0
    while True:
        t = hint(EXP_ID, "singular", p, seed, "t", attempt) % p
        attempt += 1
        if t == 0:
            rejections["t_zero"] += 1
            continue
        a = (-3 * t * t) % p
        b = (2 * t * t * t) % p
        assert (4 * a * a * a + 27 * b * b) % p == 0
        xs = [x for x in window_x_on_curve(p, a, b, B) if x != t]
        if len(xs) < 2:
            rejections["window"] += 1
            continue
        return {"p": p, "a": a, "b": b, "t": t, "seed": seed, "attempts": attempt,
                "rejections": rejections, "window_x": xs, "B": B, "kind": "singular"}


def plant_target(curve: dict, tseed: int) -> dict:
    """x_R = x(P_1 + P_2) with x(P_1) != x(P_2) in the window; certificate."""
    p, a, b = curve["p"], curve["a"], curve["b"]
    xs = curve["window_x"]
    h = hint(EXP_ID, "target", p, curve["seed"], tseed)
    i = h % len(xs)
    j = (h >> 64) % (len(xs) - 1)
    if j >= i:
        j += 1
    x1, x2 = xs[i], xs[j]
    y1 = sqrt_mod((x1**3 + a * x1 + b) % p, p)
    y2 = sqrt_mod((x2**3 + a * x2 + b) % p, p)
    if (h >> 128) & 1:
        y1 = (-y1) % p
    if (h >> 129) & 1:
        y2 = (-y2) % p
    P1, P2 = (x1, y1), (x2, y2)
    R = ec_add(p, a, P1, P2)
    assert R is not None  # distinct x guarantees an affine sum
    cert = {"kind": "decomposition",
            "statement": {"target": [R[0], R[1]], "summands": [[x1, y1], [x2, y2]],
                          "curve": {"p": p, "a": a, "b": b}}}
    return {"target_seed": tseed, "x1": x1, "x2": x2, "P1": [x1, y1], "P2": [x2, y2],
            "R": [R[0], R[1]], "x_R": R[0], "certificate": cert}


def plant_root_target(curve: dict, tseed: int) -> dict:
    """Non-curve arm: x_R a root of S_3(x1, x2, X) = 0 (quadratic in X) with x1 != x2
    window x on the singular cubic; rejection-sampled until a root exists."""
    p, a, b = curve["p"], curve["a"], curve["b"]
    xs = curve["window_x"]
    attempt = 0
    while True:
        h = hint(EXP_ID, "roottarget", p, curve["seed"], tseed, attempt)
        attempt += 1
        i = h % len(xs)
        j = (h >> 64) % (len(xs) - 1)
        if j >= i:
            j += 1
        x1, x2 = xs[i], xs[j]
        c2 = (x1 - x2) ** 2 % p
        c1 = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
        c0 = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
        disc = (c1 * c1 - 4 * c2 * c0) % p
        r = sqrt_mod(disc, p)
        if r is None:
            continue
        roots = sorted({(-c1 + r) * pow(2 * c2, -1, p) % p, (-c1 - r) * pow(2 * c2, -1, p) % p})
        x_R = roots[(h >> 128) % len(roots)]
        cert = {"kind": "s3_root", "statement": {"x1": x1, "x2": x2, "x_R": x_R,
                                                 "cubic": {"p": p, "a": a, "b": b}}}
        return {"target_seed": tseed, "x1": x1, "x2": x2, "x_R": x_R, "root_attempts": attempt,
                "roots": roots, "certificate": cert}


def verify_certificate(cert: dict) -> bool:
    """INDEPENDENT re-verification: harness.toycurve arithmetic for decompositions,
    harness.semaev.s3_eval for S_3 roots -- neither shares code with the planting."""
    if cert["kind"] == "decomposition":
        return bool(verify_decomposition_certificate(cert))
    if cert["kind"] == "s3_root":
        st = cert["statement"]
        c = st["cubic"]
        return s3_eval(c["a"], c["b"], st["x1"], st["x2"], st["x_R"], c["p"]) == 0
    return False


def digits(x: int, s: int) -> List[int]:
    return [(x >> i) & 1 for i in range(s)]


# ---------------------------------------------------------------------------
# S_3 as an integer polynomial in (x1, x2) with x3 = x_R, a, b substituted
# ---------------------------------------------------------------------------
def s3_dict(a: int, b: int, xr: int, p: int) -> Dict[Tuple[int, int], int]:
    """{(i, j): coeff} for S_3(x1, x2, x_R) = (x1-x2)^2 xR^2 - 2((x1+x2)(x1 x2 + a) + 2b) xR
    + (x1 x2 - a)^2 - 4b(x1 + x2)."""
    d: Dict[Tuple[int, int], int] = {}

    def add(i, j, c):
        d[(i, j)] = (d.get((i, j), 0) + c) % p

    xr2 = xr * xr % p
    add(2, 0, xr2); add(1, 1, -2 * xr2); add(0, 2, xr2)
    # -2 xR [ (x1+x2)(x1 x2 + a) + 2b ] = -2 xR [x1^2 x2 + x1 x2^2 + a x1 + a x2 + 2b]
    add(2, 1, -2 * xr); add(1, 2, -2 * xr); add(1, 0, -2 * xr * a); add(0, 1, -2 * xr * a)
    add(0, 0, -4 * xr * b)
    # (x1 x2 - a)^2 = x1^2 x2^2 - 2a x1 x2 + a^2
    add(2, 2, 1); add(1, 1, -2 * a); add(0, 0, a * a)
    # -4b(x1 + x2)
    add(1, 0, -4 * b); add(0, 1, -4 * b)
    return {k: v for k, v in d.items() if v}


def system_from_s3(a: int, b: int, xr: int):
    def system(ring: Ring, xs):
        return [substitute(ring, s3_dict(a, b, xr, ring.p), xs)]
    return system


# ---------------------------------------------------------------------------
# Meter readings
# ---------------------------------------------------------------------------
def layer_record(layers) -> dict:
    return {str(l.degree): {
        "row_count": l.row_count, "zero_product_rows": l.zero_product_rows,
        "ncols_full": l.ncols_full, "ncols_top": l.ncols_top,
        "full_rank": l.full_rank, "top_rank": l.top_rank,
        "fall_dim": l.fall_dim, "syzygy_dim": l.syzygy_dim,
        "koszul_pairwise": l.koszul_pairwise, "pred_rank": l.pred_rank,
        "koszul_series": l.koszul_series, "deficit_series": l.deficit_series,
        "deficit_pairwise": l.deficit_pairwise, "top_deficit_series": l.top_deficit_series,
        "nnz_total": l.nnz_total, "reduction_ops": l.reduction_ops,
    } for l in layers}


def measure_digit_system(ring: Ring, polys, with_cumulative: bool = True) -> dict:
    per = analyze_degrees(ring, polys, D_MIN, D_MAX, convention="per_layer")
    out = {
        "per_layer": layer_record(per),
        "d_ff": first_nonzero_fall(per),                       # first D with fall_dim > 0
        "d_ff_syzygy_series": first_nontrivial_syzygy(per),    # first D with deficit_series > 0
        "profile_full_rank": [l.full_rank for l in per],
        "profile_top_rank": [l.top_rank for l in per],
        "profile_fall_dim": [l.fall_dim for l in per],
        "profile_syzygy_dim": [l.syzygy_dim for l in per],
        "generator_degrees": [ring.degree(f) for f in polys],
        "generator_term_counts": [len(f) for f in polys],
    }
    if with_cumulative:
        cum = analyze_degrees(ring, polys, D_MIN, D_MAX, convention="cumulative")
        out["cumulative"] = layer_record(cum)
        out["cumulative_profile_full_rank"] = [l.full_rank for l in cum]
        out["cumulative_d_ff"] = first_nonzero_fall(cum)
    return out


def measure_direct_system(ring: Ring, polys, dmin: int, dmax: int) -> dict:
    per = analyze_degrees(ring, polys, dmin, dmax, convention="per_layer")
    d_top_full = None
    for l in per:
        if l.top_rank == l.ncols_top:
            d_top_full = l.degree
            break
    pred = semiregular_prediction(ring, [ring.degree(f) for f in polys], dmax)
    return {
        "per_layer": layer_record(per),
        "d_ff": first_nonzero_fall(per),
        "d_ff_syzygy_series": first_nontrivial_syzygy(per),
        "d_top_full": d_top_full,                  # first D with top_rank == #monomials(D)
        "series_d_reg": pred.d_reg,                # null d_reg from the semi-regular series
        "series_raw_coefficients": list(pred.raw_coefficients),
        "profile_full_rank": [l.full_rank for l in per],
        "profile_top_rank": [l.top_rank for l in per],
        "profile_fall_dim": [l.fall_dim for l in per],
        "generator_degrees": [ring.degree(f) for f in polys],
        "degrees": [dmin, dmax],
    }


# ---------------------------------------------------------------------------
# Stage 3 cell: one (curve, target) at one prime, all arms
# ---------------------------------------------------------------------------
def semaev_draw(p: int, curve: dict, target: dict) -> dict:
    pres = digit_presentation(p, M, D_BASE, S_DIGITS, system_from_s3(curve["a"], curve["b"], target["x_R"]))
    ring = pres.ring
    stilde = pres.generators[0]
    point = digits(target["x1"], S_DIGITS) + digits(target["x2"], S_DIGITS)
    planted_zero = ring.evaluate(stilde, point, ()) == 0
    cert_ok = verify_certificate(target["certificate"])
    rec = {"arm": "semaev", "curve_seed": curve["seed"], "target_seed": target["target_seed"],
           "x1": target["x1"], "x2": target["x2"], "x_R": target["x_R"],
           "planted_digits": point, "stilde_vanishes_at_planted_point": planted_zero,
           "certificate": target["certificate"], "certificate_verified": cert_ok,
           "valid": bool(cert_ok and planted_zero)}
    if not rec["valid"]:
        rec["invalid_reason"] = "certificate failed independent re-verification or S~ does not vanish at the planted digits"
    rec.update(measure_digit_system(ring, [stilde]))
    return rec, ring, stilde


def null_draws(p: int, ring: Ring, stilde, curve_seed: int, target_seed: int) -> List[dict]:
    out = []
    for ns in NULL_SEEDS:
        mixed = hint(EXP_ID, "null", p, curve_seed, target_seed, ns) % (1 << 62)
        polys, meta = support_matched_system(ring, [stilde], mixed)
        rec = {"arm": "null_support", "curve_seed": curve_seed, "target_seed": target_seed,
               "null_seed": ns, "rng_seed_mixed": mixed, "null_meta": meta.as_dict(),
               "support_size": len(polys[0]), "valid": True}
        rec.update(measure_digit_system(ring, polys))
        out.append(rec)
    return out


def noncurve_draw(p: int, cubic: dict, target: dict) -> dict:
    pres = digit_presentation(p, M, D_BASE, S_DIGITS, system_from_s3(cubic["a"], cubic["b"], target["x_R"]))
    ring = pres.ring
    g = pres.generators[0]
    point = digits(target["x1"], S_DIGITS) + digits(target["x2"], S_DIGITS)
    planted_zero = ring.evaluate(g, point, ()) == 0
    cert_ok = verify_certificate(target["certificate"])
    rec = {"arm": "noncurve_cubic", "curve_seed": cubic["seed"], "target_seed": target["target_seed"],
           "x1": target["x1"], "x2": target["x2"], "x_R": target["x_R"], "root_attempts": target["root_attempts"],
           "planted_digits": point, "generator_vanishes_at_planted_point": planted_zero,
           "certificate": target["certificate"], "certificate_verified": cert_ok,
           "valid": bool(cert_ok and planted_zero)}
    if not rec["valid"]:
        rec["invalid_reason"] = "S_3 root certificate failed independent re-evaluation or generator does not vanish at the planted digits"
    rec.update(measure_digit_system(ring, [g]))
    return rec


def secondary_direct_draw(p: int, curve: dict, target: dict) -> dict:
    pres = direct_presentation(p, M, SECONDARY_B, system_from_s3(curve["a"], curve["b"], target["x_R"]))
    ring = pres.ring
    cert_ok = verify_certificate(target["certificate"])
    xs_vals = [target["x1"], target["x2"]]
    vanish = all(ring.evaluate(f, (), xs_vals) == 0 for f in pres.generators)
    rec = {"arm": "secondary_direct_B8", "curve_seed": curve["seed"], "target_seed": target["target_seed"],
           "x1": target["x1"], "x2": target["x2"], "x_R": target["x_R"], "B": SECONDARY_B,
           "certificate": target["certificate"], "certificate_verified": cert_ok,
           "system_vanishes_at_planted_point": vanish, "valid": bool(cert_ok and vanish)}
    rec.update(measure_direct_system(ring, list(pres.generators), 4, SECONDARY_B + 2))
    return rec


def sweep_run(p: int, label: str, log: io.StringIO, prime_note: dict) -> runner.RunResult:
    t_start = time.monotonic()
    draws: List[dict] = []
    curves: List[dict] = []
    cubics: List[dict] = []
    sec_curves: List[dict] = []
    named = None
    stopped = None
    try:
        for cs in CURVE_SEEDS:
            curve = draw_curve(p, cs, WINDOW)
            cubic = draw_singular_cubic(p, cs, WINDOW)
            curves.append(curve)
            cubics.append(cubic)
            print(f"[{label}] curve seed {cs}: a={curve['a']} b={curve['b']} window_x={curve['window_x']} "
                  f"rejections={curve['rejections']}; singular t={cubic['t']} window_x={cubic['window_x']} "
                  f"rejections={cubic['rejections']}", file=log)
            for ts in TARGET_SEEDS:
                tgt = plant_target(curve, ts)
                rec, ring, stilde = semaev_draw(p, curve, tgt)
                draws.append(rec)
                draws.extend(null_draws(p, ring, stilde, cs, ts))
                rtgt = plant_root_target(cubic, ts)
                draws.append(noncurve_draw(p, cubic, rtgt))
                print(f"[{label}]   target {ts}: x1={tgt['x1']} x2={tgt['x2']} x_R={tgt['x_R']} "
                      f"cert={rec['certificate_verified']} semaev profile full={rec['profile_full_rank']} "
                      f"top={rec['profile_top_rank']} d_ff={rec['d_ff']} | elapsed {time.monotonic() - t_start:.1f}s",
                      file=log)
        # secondary direct arm at fixed B = 8 (3 curves x 2 targets)
        for cs in POSCTRL_CURVE_SEEDS:
            curve = draw_curve(p, cs, SECONDARY_B, tag="curve")
            sec_curves.append(curve)
            for ts in POSCTRL_TARGET_SEEDS:
                tgt = plant_target(curve, ts)
                rec = secondary_direct_draw(p, curve, tgt)
                draws.append(rec)
                print(f"[{label}] secondary B=8 curve {cs} target {ts}: d_ff={rec['d_ff']} "
                      f"d_top_full={rec['d_top_full']} series_d_reg={rec['series_d_reg']}", file=log)
        if p == P_256:
            xs = window_x_on_curve(p, NIST_P256_A, NIST_P256_B, WINDOW)
            named = {"p": p, "a": NIST_P256_A, "b": NIST_P256_B, "seed": "NIST-P-256", "attempts": 1,
                     "rejections": {}, "window_x": xs, "B": WINDOW, "kind": "named"}
            named_draws = []
            if len(xs) >= 2:
                for ts in TARGET_SEEDS:
                    tgt = plant_target(named, ts)
                    rec, ring, stilde = semaev_draw(p, named, tgt)
                    rec["arm"] = "semaev_named_p256"
                    named_draws.append(rec)
                    named_draws.extend([dict(r, arm="null_support_named_p256") for r in null_draws(p, ring, stilde, "NIST-P-256", ts)])
                named["fallback_random_target"] = False
            else:
                # contract fallback: random (unplanted) target, reported separately
                named["fallback_random_target"] = True
                for ts in TARGET_SEEDS:
                    xr = hint(EXP_ID, "named-random-target", p, ts) % p
                    pres = digit_presentation(p, M, D_BASE, S_DIGITS, system_from_s3(NIST_P256_A, NIST_P256_B, xr))
                    rec = {"arm": "semaev_named_p256_unplanted", "curve_seed": "NIST-P-256", "target_seed": ts,
                           "x_R": xr, "valid": True, "certificate": {"kind": "none"}}
                    rec.update(measure_digit_system(pres.ring, [pres.generators[0]]))
                    named_draws.append(rec)
            draws.extend(named_draws)
            print(f"[{label}] named P-256 curve: window_x={xs} planted={not named['fallback_random_target']}", file=log)
    except RunBudgetExceeded as exc:
        stopped = str(exc)
        print(f"[{label}] STOPPED: {stopped}", file=log)
    signal.alarm(0)

    n_valid = sum(1 for d in draws if d.get("valid"))
    cert_total = sum(1 for d in draws if "certificate_verified" in d)
    cert_fail = sum(1 for d in draws if "certificate_verified" in d and not d["certificate_verified"])
    arms = sorted({d["arm"] for d in draws})
    metrics = {
        "prime": p, "prime_bits": p.bit_length(), "draw_count": len(draws), "valid_draws": n_valid,
        "arms": arms, "draws_per_arm": {a: sum(1 for d in draws if d["arm"] == a) for a in arms},
        "planted_certificates_total": cert_total, "planted_certificates_failed": cert_fail,
        "curve_rejections": {str(c["seed"]): c["rejections"] for c in curves},
        "singular_rejections": {str(c["seed"]): c["rejections"] for c in cubics},
        "stopped": stopped,
        "semaev_d_ff_histogram": _hist(d["d_ff"] for d in draws if d["arm"] == "semaev"),
        "null_d_ff_histogram": _hist(d["d_ff"] for d in draws if d["arm"] == "null_support"),
        "noncurve_d_ff_histogram": _hist(d["d_ff"] for d in draws if d["arm"] == "noncurve_cubic"),
        "secondary_direct_d_ff_histogram": _hist(d["d_ff"] for d in draws if d["arm"] == "secondary_direct_B8"),
        "semaev_profile_histogram": _hist(str((d["profile_full_rank"], d["profile_top_rank"])) for d in draws if d["arm"] == "semaev"),
        "null_profile_histogram": _hist(str((d["profile_full_rank"], d["profile_top_rank"])) for d in draws if d["arm"] == "null_support"),
        "noncurve_profile_histogram": _hist(str((d["profile_full_rank"], d["profile_top_rank"])) for d in draws if d["arm"] == "noncurve_cubic"),
    }
    valid = stopped is None and cert_fail == 0
    return runner.RunResult(
        run_suffix=label, curve_id=f"sweep-{label}-8-random-curves" + ("-plus-NIST-P-256" if p == P_256 else ""),
        seed=CURVE_SEEDS[0],
        parameters=common_parameters(stage="stage-3-sweep", p=p, prime_note=prime_note,
                                     extra={"curve_seeds": CURVE_SEEDS, "target_seeds": TARGET_SEEDS,
                                            "null_seeds": NULL_SEEDS, "secondary_curve_seeds": POSCTRL_CURVE_SEEDS,
                                            "secondary_target_seeds": POSCTRL_TARGET_SEEDS, "secondary_B": SECONDARY_B,
                                            "degrees": [D_MIN, D_MAX], "window": WINDOW,
                                            "named_curve": ({"name": "NIST P-256", "a": NIST_P256_A, "b": NIST_P256_B}
                                                            if p == P_256 else None)}),
        metrics=metrics,
        certificate={"kind": "none",
                     "note": ("No solve is claimed. Planted targets carry per-draw decomposition / S_3-root "
                              "certificates in raw.draws[*].certificate, each re-verified by independent code "
                              "(harness.toycurve / harness.semaev); failures are counted in metrics.")},
        valid=valid,
        invalid_reason=(stopped if stopped else ("planted certificate failed" if cert_fail else None)),
        stdout=log.getvalue(),
        raw={"curves": curves, "singular_cubics": cubics, "named_curve": named if p == P_256 else None,
             "secondary_curves": sec_curves, "draws": draws,
             "meter_selftest": METER_SELFTEST},
    )


def _hist(values) -> dict:
    h: Dict[str, int] = {}
    for v in values:
        h[str(v)] = h.get(str(v), 0) + 1
    return dict(sorted(h.items()))


# ---------------------------------------------------------------------------
# Stage 2: positive control
# ---------------------------------------------------------------------------
def posctrl_run(p: int, label: str, log: io.StringIO) -> runner.RunResult:
    B = round(p ** 0.5)
    stopped = None
    draws: List[dict] = []
    curves: List[dict] = []
    try:
        for cs in POSCTRL_CURVE_SEEDS:
            curve = draw_curve(p, cs, B)
            curves.append(curve)
            for ts in POSCTRL_TARGET_SEEDS:
                tgt = plant_target(curve, ts)
                pres = direct_presentation(p, M, B, system_from_s3(curve["a"], curve["b"], tgt["x_R"]))
                ring = pres.ring
                cert_ok = verify_certificate(tgt["certificate"])
                vanish = all(ring.evaluate(f, (), [tgt["x1"], tgt["x2"]]) == 0 for f in pres.generators)
                rec = {"arm": "positive_control_direct", "curve_seed": cs, "target_seed": ts, "B": B,
                       "x1": tgt["x1"], "x2": tgt["x2"], "x_R": tgt["x_R"], "certificate": tgt["certificate"],
                       "certificate_verified": cert_ok, "system_vanishes_at_planted_point": vanish,
                       "valid": bool(cert_ok and vanish)}
                rec.update(measure_direct_system(ring, list(pres.generators), 4, B + 2))
                draws.append(rec)
                print(f"[{label}] curve {cs} target {ts}: B={B} d_ff={rec['d_ff']} d_ff_syzygy={rec['d_ff_syzygy_series']} "
                      f"d_top_full={rec['d_top_full']} series_d_reg={rec['series_d_reg']} cert={cert_ok}", file=log)
    except RunBudgetExceeded as exc:
        stopped = str(exc)
        print(f"[{label}] STOPPED: {stopped}", file=log)
    signal.alarm(0)
    cert_fail = sum(1 for d in draws if not d["certificate_verified"])
    metrics = {"prime": p, "B": B, "predicted_frozen_d_ff": B + 1, "draw_count": len(draws),
               "d_ff_histogram": _hist(d["d_ff"] for d in draws),
               "d_ff_syzygy_series_histogram": _hist(d["d_ff_syzygy_series"] for d in draws),
               "d_top_full_histogram": _hist(d["d_top_full"] for d in draws),
               "series_d_reg": draws[0]["series_d_reg"] if draws else None,
               "planted_certificates_failed": cert_fail, "stopped": stopped,
               "curve_rejections": {str(c["seed"]): c["rejections"] for c in curves}}
    return runner.RunResult(
        run_suffix=label, curve_id=f"posctrl-p{p}-3-random-curves", seed=POSCTRL_CURVE_SEEDS[0],
        parameters=common_parameters(stage="stage-2-positive-control", p=p, prime_note={"p": p, "miller_rabin": miller_rabin(p)},
                                     extra={"B": B, "curve_seeds": POSCTRL_CURVE_SEEDS, "target_seeds": POSCTRL_TARGET_SEEDS,
                                            "degrees": [4, B + 2], "window": B}),
        metrics=metrics,
        certificate={"kind": "none", "note": "No solve is claimed; per-draw planted certificates are in raw.draws and were re-verified independently."},
        valid=stopped is None and cert_fail == 0,
        invalid_reason=stopped if stopped else ("planted certificate failed" if cert_fail else None),
        stdout=log.getvalue(),
        raw={"curves": curves, "draws": draws, "meter_selftest": METER_SELFTEST},
    )


# ---------------------------------------------------------------------------
# Stage 1: frozen fixture against an INDEPENDENT second implementation
# ---------------------------------------------------------------------------
def independent_stilde(p: int, a: int, b: int, xr: int):
    """S~ built by sympy from harness.semaev.s3_expr (an independent S_3 source),
    with ell_k substituted and a_i^2 -> a_i applied symbolically.  Returns
    {frozenset(indices): coeff mod p}."""
    A = sympy.symbols("a0:6")
    x1, x2, x3 = sympy.symbols("x1 x2 x3")
    ell1 = A[0] + 2 * A[1] + 4 * A[2]
    ell2 = A[3] + 2 * A[4] + 4 * A[5]
    expr = s3_expr(a, b).subs({x1: ell1, x2: ell2, x3: xr}, simultaneous=True)
    poly = sympy.Poly(sympy.expand(expr), *A)
    out: Dict[frozenset, int] = {}
    for monom, coeff in poly.terms():
        key = frozenset(i for i, e in enumerate(monom) if e > 0)   # a^2 -> a
        out[key] = (out.get(key, 0) + int(coeff)) % p
    return {k: v for k, v in out.items() if v}


def independent_macaulay_ranks(p: int, stilde: Dict[frozenset, int], dmin: int, dmax: int) -> dict:
    """Dense Macaulay layers built from scratch; ranks by sympy DomainMatrix over
    GF(p) and by a naive Gaussian elimination (two more independent routes)."""
    from itertools import combinations
    from sympy.polys.matrices import DomainMatrix
    from sympy import GF
    n = N_DIGITS
    deg_f = max(len(k) for k in stilde)
    out = {}
    for D in range(dmin, dmax + 1):
        cols = [frozenset(c) for d in range(D + 1) for c in combinations(range(n), d)]
        idx = {c: i for i, c in enumerate(cols)}
        top_cols = [i for i, c in enumerate(cols) if len(c) == D]
        rows = []
        md = D - deg_f
        if md >= 0:
            for mult in combinations(range(n), md):
                ms = frozenset(mult)
                row = [0] * len(cols)
                for mono, c in stilde.items():
                    prod = mono | ms
                    row[idx[prod]] = (row[idx[prod]] + c) % p
                rows.append(row)
        if rows:
            dm = DomainMatrix([[GF(p)(v) for v in r] for r in rows], (len(rows), len(cols)), GF(p))
            full_sympy = dm.rank()
            dm_top = DomainMatrix([[GF(p)(r[i]) for i in top_cols] for r in rows], (len(rows), len(top_cols)), GF(p))
            top_sympy = dm_top.rank()
            full_naive = naive_rank(p, rows)
            top_naive = naive_rank(p, [[r[i] for i in top_cols] for r in rows])
        else:
            full_sympy = top_sympy = full_naive = top_naive = 0
        out[str(D)] = {"rows": len(rows), "cols": len(cols), "cols_top": len(top_cols),
                       "full_rank_sympy": full_sympy, "top_rank_sympy": top_sympy,
                       "full_rank_naive": full_naive, "top_rank_naive": top_naive,
                       "fall_dim_sympy": full_sympy - top_sympy}
    return out


def naive_rank(p: int, rows: List[List[int]]) -> int:
    m = [list(r) for r in rows]
    rank = 0
    ncols = len(m[0]) if m else 0
    for c in range(ncols):
        piv = None
        for r in range(rank, len(m)):
            if m[r][c] % p:
                piv = r
                break
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        inv = pow(m[rank][c], -1, p)
        m[rank] = [(v * inv) % p for v in m[rank]]
        for r in range(len(m)):
            if r != rank and m[r][c] % p:
                f = m[r][c]
                m[r] = [(x - f * y) % p for x, y in zip(m[r], m[rank])]
        rank += 1
    return rank


def stage0_content_check() -> dict:
    """Symbolic S~ over Z[A, B, x_R] at (2, 2, 3): entry degrees, integer content of
    the D = 4 layer (one row), and small-prime specialisation ranks at D = 5, 6."""
    A = sympy.symbols("a0:6")
    Asym, Bsym, XR = sympy.symbols("A B x_R")
    x1, x2, x3 = sympy.symbols("x1 x2 x3")
    ell1 = A[0] + 2 * A[1] + 4 * A[2]
    ell2 = A[3] + 2 * A[4] + 4 * A[5]
    expr = sympy.expand(s3_expr(Asym, Bsym).subs({x1: ell1, x2: ell2, x3: XR}, simultaneous=True))
    poly = sympy.Poly(expr, *A)
    entries: Dict[frozenset, sympy.Expr] = {}
    for monom, coeff in poly.terms():
        key = frozenset(i for i, e in enumerate(monom) if e > 0)
        entries[key] = sympy.expand(entries.get(key, 0) + coeff)
    entry_table = {}
    all_int_coeffs: List[int] = []
    max_param_degree = 0
    for key in sorted(entries, key=lambda k: (len(k), sorted(k))):
        e = sympy.Poly(entries[key], Asym, Bsym, XR)
        coeffs = [int(c) for c in e.coeffs()]
        all_int_coeffs.extend(coeffs)
        max_param_degree = max(max_param_degree, e.total_degree())
        entry_table["*".join(f"a{i}" for i in sorted(key)) if key else "1"] = {
            "entry": str(entries[key]), "param_degree": e.total_degree(), "content": int(sympy.gcd_list(coeffs))}
    content_D4 = int(sympy.gcd_list(all_int_coeffs))
    # small-prime specialisation ranks (uniform (A, B, x_R), 24 samples per prime)
    spec = {}
    generic_ref = None
    for q in [P_64]:
        rng = random.Random(20260903)
        profs = []
        for _ in range(8):
            a, b, xr = (rng.randrange(q) for _ in range(3))
            st = {k: int(sympy.sympify(v).subs({Asym: a, Bsym: b, XR: xr})) % q for k, v in entries.items()}
            st = {k: v for k, v in st.items() if v}
            r = independent_macaulay_ranks(q, st, 4, 6)
            profs.append(tuple((r[str(D)]["full_rank_naive"], r[str(D)]["top_rank_naive"]) for D in range(4, 7)))
        generic_ref = max(set(profs), key=profs.count)
        spec["reference_prime"] = {"p": q, "profiles": _hist(profs), "modal_profile_D4_D5_D6": [list(x) for x in generic_ref]}
    for q in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        rng = random.Random(20260903 + q)
        profs = []
        for _ in range(24):
            a, b, xr = (rng.randrange(q) for _ in range(3))
            st = {k: int(sympy.sympify(v).subs({Asym: a, Bsym: b, XR: xr})) % q for k, v in entries.items()}
            st = {k: v for k, v in st.items() if v}
            if not st:
                profs.append(("zero-generator",))
                continue
            r = independent_macaulay_ranks(q, st, 4, 6)
            profs.append(tuple((r[str(D)]["full_rank_naive"], r[str(D)]["top_rank_naive"]) for D in range(4, 7)))
        n_generic = sum(1 for pr in profs if pr == generic_ref)
        spec[str(q)] = {"samples": len(profs), "equal_to_reference": n_generic, "profiles": _hist(profs)}
    return {"n_entries_D4": len(entries), "entry_table": entry_table, "content_D4": content_D4,
            "max_param_degree_per_entry": max_param_degree,
            "row_counts": {"4": 1, "5": 6, "6": 15},
            "minor_degree_bound_2rD": {"4": 2 * 1, "5": 2 * 6, "6": 2 * 15},
            "schwartz_zippel_bound_at_4099": {"4": 2 / 4099, "5": 12 / 4099, "6": 30 / 4099},
            "small_prime_specialisations": spec}


def fixture_run(log: io.StringIO) -> runner.RunResult:
    p = FIXTURE["p"]
    curve = draw_curve(p, FIXTURE["curve_seed"], WINDOW)
    tgt = plant_target(curve, FIXTURE["target_seed"])
    rec, ring, stilde = semaev_draw(p, curve, tgt)
    print(f"[fixture] curve a={curve['a']} b={curve['b']} window_x={curve['window_x']} target x1={tgt['x1']} x2={tgt['x2']} x_R={tgt['x_R']}", file=log)
    print(f"[fixture] meter S~ = {ring.to_string(stilde)}", file=log)
    ind = independent_stilde(p, curve["a"], curve["b"], tgt["x_R"])
    meter_as_sets = {frozenset(i for i in range(N_DIGITS) if m[0] >> i & 1): c for m, c in stilde.items()}
    stilde_agree = meter_as_sets == ind
    ranks = independent_macaulay_ranks(p, ind, D_MIN, D_MAX)
    per_D = {}
    all_agree = True
    for D in range(D_MIN, D_MAX + 1):
        m = rec["per_layer"][str(D)]
        r = ranks[str(D)]
        agree = (m["full_rank"] == r["full_rank_sympy"] == r["full_rank_naive"]
                 and m["top_rank"] == r["top_rank_sympy"] == r["top_rank_naive"]
                 and m["row_count"] == r["rows"] and m["ncols_full"] == r["cols"])
        all_agree = all_agree and agree
        per_D[str(D)] = {"meter": {"rows": m["row_count"], "cols": m["ncols_full"], "full_rank": m["full_rank"],
                                   "top_rank": m["top_rank"], "fall_dim": m["fall_dim"]},
                         "independent": r, "agree": agree}
        print(f"[fixture] D={D}: meter full={m['full_rank']} top={m['top_rank']} | sympy full={r['full_rank_sympy']} "
              f"top={r['top_rank_sympy']} | naive full={r['full_rank_naive']} top={r['top_rank_naive']} -> {'AGREE' if agree else 'MISMATCH'}", file=log)
    print(f"[fixture] S~ coefficient-level agreement meter vs sympy: {stilde_agree}", file=log)
    content = stage0_content_check()
    print(f"[fixture] stage0 content(D=4) = {content['content_D4']}; max entry parameter degree = {content['max_param_degree_per_entry']}", file=log)
    fixture_agrees = bool(all_agree and stilde_agree and rec["valid"])
    metrics = {"prime": p, "curve_seed": FIXTURE["curve_seed"], "target_seed": FIXTURE["target_seed"],
               "curve_a": curve["a"], "curve_b": curve["b"], "x1": tgt["x1"], "x2": tgt["x2"], "x_R": tgt["x_R"],
               "stilde_coefficient_agreement": stilde_agree, "rank_profile_agreement_all_D": all_agree,
               "fixture_agrees": fixture_agrees, "certificate_verified": rec["certificate_verified"],
               "meter_profile_full_rank": rec["profile_full_rank"], "meter_profile_top_rank": rec["profile_top_rank"],
               "meter_d_ff": rec["d_ff"], "meter_fall_dim": rec["profile_fall_dim"],
               "stage0_content_D4": content["content_D4"],
               "stage0_max_entry_param_degree": content["max_param_degree_per_entry"],
               "meter_selftest_returncode": METER_SELFTEST["returncode"]}
    return runner.RunResult(
        run_suffix="fixture-p4099", curve_id=runner.curve_id(p, curve["a"], curve["b"], p.bit_length()),
        seed=FIXTURE["curve_seed"],
        parameters=common_parameters(stage="stage-1-fixture", p=p, prime_note={"p": p, "miller_rabin": miller_rabin(p)},
                                     extra={"fixture": FIXTURE, "degrees": [D_MIN, D_MAX], "window": WINDOW,
                                            "second_implementation": "sympy Poly expansion of harness.semaev.s3_expr + dense DomainMatrix(GF(p)).rank + naive elimination (EXP-PFDR-5726af has no run; contract fallback)"}),
        metrics=metrics,
        certificate={"kind": "none", "note": "No solve claimed; the planted decomposition certificate is in raw.fixture_draw.certificate, re-verified by harness.toycurve."},
        valid=fixture_agrees,
        invalid_reason=None if fixture_agrees else "frozen fixture disagreement or certificate failure (instrument finding)",
        stdout=log.getvalue(),
        raw={"curve": curve, "target": tgt, "fixture_draw": rec, "independent_stilde": {"*".join(f"a{i}" for i in sorted(k)) or "1": v for k, v in ind.items()},
             "independent_ranks": ranks, "per_degree_comparison": per_D, "stage0_content_check": content,
             "meter_selftest": METER_SELFTEST},
    )


# ---------------------------------------------------------------------------
# Manifest lineage helpers
# ---------------------------------------------------------------------------
def meter_hashes() -> dict:
    out = {}
    for rel in METER_FILES:
        with open(os.path.join(REPO, rel), "rb") as fh:
            out[rel] = hashlib.sha256(fh.read()).hexdigest()
    return out


def meter_selftest() -> dict:
    """Run the meter's own test-suite (p = 2 known answer + planted-syzygy control)
    in THIS manifest lineage, as the contract's invalidation rule requires."""
    t0 = time.monotonic()
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/test_macaulay_fp.py", "-q", "-p", "no:cacheprovider"],
                          cwd=REPO, capture_output=True, text=True)
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return {"command": "python3 -m pytest tests/test_macaulay_fp.py -q -p no:cacheprovider",
            "returncode": proc.returncode, "summary_line": tail, "seconds": round(time.monotonic() - t0, 3)}


METER_SELFTEST: dict = {}


def common_parameters(stage: str, p: int, prime_note: dict, extra: dict) -> dict:
    return {
        "experiment": EXP_ID, "hypothesis": "H-PFDR-09e1b0", "handoff": "TASK-20260903-5a62de",
        "stage": stage, "shape": {"m": M, "d": D_BASE, "s": S_DIGITS, "n_digits": N_DIGITS},
        "prime": p, "prime_bits": p.bit_length(), "prime_check": prime_note,
        "meter": {"package": "harness/macaulay_fp", "snapshot_commit": METER_COMMIT,
                  "per_file_sha256": meter_hashes(), "selftest_in_this_lineage": METER_SELFTEST},
        "budget": {"wall_clock_seconds_per_run": WALL_CLOCK_SECONDS_PER_RUN, "maximum_memory_gb": MAX_MEMORY_GB,
                   "maximum_workers": 1, "maximum_runs": 12},
        "conventions": {
            "macaulay_convention_primary": "per_layer (macaulay.py; multipliers of degree exactly D - deg f; zero rows kept)",
            "macaulay_convention_secondary": "cumulative (recorded for the digit arms only)",
            "d_ff": "first degree D with fall_dim(D) = full_rank - top_rank > 0 (first_nonzero_fall)",
            "null_coefficients": "support_matched_system: identical support, coefficients uniform in [1, p-1]",
            "null_rng_seed": "sha256(EXP:null:p:curve_seed:target_seed:null_seed) mod 2^62 (frozen null seed mixed with the draw labels)",
            "curve_draw": "A, B = sha256(EXP:curve:p:seed:A|B:attempt) mod p; reject disc = 0 or < 2 on-curve x in window",
            "target_plant": "x1 != x2 chosen from the on-curve window x by sha256(EXP:target:p:curve_seed:t); signs from hash bits; R = P1 + P2 by the executor's own affine addition; certificate re-verified by harness.toycurve",
            "noncurve_cubic": "A = -3t^2, B = 2t^3 (nodal, 4A^3 + 27B^2 = 0), t = sha256(...) mod p != 0; x1 != x2 window x with square rhs and x != t; x_R a root of S_3(x1, x2, X); root re-verified by harness.semaev.s3_eval",
        },
        "executor_session_inference": {
            "requested_policy": "executor-implementation", "requested_reasoning_effort": "medium",
            "adapter_resolution": "python3 -m orchestration.adapter resolve --role executor -> anthropic:claude-sonnet-5 (effort=medium)",
            "runtime_reported_model": "claude-fable-5-1", "model_verified": False,
            "fallback_used": "unknown (adapter binding and runtime-reported identifier differ; cannot be verified from inside the session)",
            "degraded": False, "independent_session": True,
            "note": "The run itself is deterministic code with no model in its loop (see run.inference); this block records the executor SESSION's policy as the handoff requires.",
        },
        **extra,
    }


def prime_notes() -> dict:
    """Deterministic re-confirmation of the sweep primes (recorded in the manifest)."""
    n64 = P_64
    mr = miller_rabin(n64)
    sp = bool(sympy.isprime(n64))
    # confirm 'largest below 2^64': no prime in (2^64 - 59, 2^64)
    above = [k for k in range(n64 + 1, 2**64) if miller_rabin(k)]
    return {"p64": {"p": n64, "expression": "2^64 - 59", "miller_rabin_12_bases": mr, "sympy_isprime": sp,
                    "primes_between_p_and_2^64": above, "largest_below_2^64_confirmed": mr and sp and not above},
            "p256": {"p": P_256, "expression": "2^256 - 2^224 + 2^192 + 2^96 - 1",
                     "miller_rabin_12_bases": miller_rabin(P_256), "sympy_isprime": bool(sympy.isprime(P_256))},
            "p4099": {"p": P_SMALL, "miller_rabin_12_bases": miller_rabin(P_SMALL)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["fixture", "posctrl-4099", "posctrl-16411", "sweep-4099", "sweep-64", "sweep-256"])
    ap.add_argument("--suffix", default=None, help="override run suffix (re-runs after an infrastructure stop)")
    ap.add_argument("--out-root", default=None, help="smoke tests only: write the run package elsewhere")
    args = ap.parse_args()
    global METER_SELFTEST
    METER_SELFTEST = meter_selftest()
    if METER_SELFTEST["returncode"] != 0:
        print("meter self-test FAILED; refusing to measure", file=sys.stderr)
        return 2
    install_budget()
    log = io.StringIO()
    print(f"meter self-test: {METER_SELFTEST['summary_line']} (rc {METER_SELFTEST['returncode']})", file=log)
    command = (f"python3 experiments/{EXP_ID}/run_experiment.py {args.stage}"
               + (f" --suffix {args.suffix}" if args.suffix else "")
               + (f" --out-root {args.out_root}" if args.out_root else ""))

    if args.stage == "fixture":
        fn = lambda: fixture_run(log)  # noqa: E731
    elif args.stage.startswith("posctrl-"):
        p = int(args.stage.split("-")[1])
        label = args.suffix or f"posctrl-p{p}"
        fn = lambda: posctrl_run(p, label, log)  # noqa: E731
    else:
        notes = prime_notes()
        p = {"sweep-4099": P_SMALL, "sweep-64": P_64, "sweep-256": P_256}[args.stage]
        label = args.suffix or {"sweep-4099": "sweep-p4099", "sweep-64": "sweep-p64", "sweep-256": "sweep-p256"}[args.stage]
        if args.stage == "sweep-64" and not notes["p64"]["largest_below_2^64_confirmed"]:
            print("2^64 - 59 primality/maximality check failed; contract fallback would be the nearest prime above 2^64 -- refusing without a recorded amendment", file=sys.stderr)
            return 3
        note = notes["p64"] if p == P_64 else (notes["p256"] if p == P_256 else notes["p4099"])
        fn = lambda: sweep_run(p, label, log, note)  # noqa: E731

    def status_of(res: runner.RunResult) -> str:
        if res.metrics.get("stopped"):
            return "failed_infrastructure"
        if not res.valid:
            return "invalid_measurement"
        return "completed_valid"

    # harness.runner.run_wrapped requires the terminal status BEFORE fn() runs,
    # but the status here (completed_valid | failed_infrastructure |
    # invalid_measurement) is decided by the measurement itself.  The bracket
    # below is run_wrapped's body verbatim (time.time + monotonic clock around
    # fn, then write_run with the measured wall_seconds); the only difference is
    # that the status is decided from the returned RunResult.  timing_source
    # names this so the record never claims a bracket it did not have.
    started_wall = time.time()
    t0 = time.monotonic()
    res = fn()
    if args.suffix:
        res.run_suffix = args.suffix
    t1 = time.monotonic()
    finished_wall = time.time()
    run_id = runner.write_run(EXP_ID, EXP_AREA, res, status=status_of(res), command=command,
                              started=started_wall, finished=finished_wall, out_root=args.out_root,
                              wall_seconds=t1 - t0,
                              timing_source="run_experiment.py bracket (harness.runner.run_wrapped body verbatim; status decided after fn)")
    run_dir = os.path.join(args.out_root or EXP_DIR, "runs", run_id)
    # sidecar: per-file sha256 of the run package (the manifest cannot contain its own hash)
    sums = []
    for name in ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json"]:
        with open(os.path.join(run_dir, name), "rb") as fh:
            sums.append(f"{hashlib.sha256(fh.read()).hexdigest()}  {name}")
    with open(os.path.join(run_dir, "checksums.sha256"), "w") as fh:
        fh.write("\n".join(sums) + "\n")
    print(run_id)
    print(f"status={status_of(res)} wall={t1 - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

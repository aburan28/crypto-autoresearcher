#!/usr/bin/env python3
"""EXP-PFDR-5726af run script (TASK-20260903-b0727c, Executor).

Executes the frozen contract experiments/EXP-PFDR-5726af/specification.yaml:
first fall degree d_ff and fall_dim of the d = 2 digit-presented Semaev
system S~ = S_{m+1}(ell_1, ..., ell_m, x_R) in B = F_p[a]/(a^2 - a), read by
the shared exact F_p Macaulay meter harness/macaulay_fp (per-layer rows
mu * S~ with deg mu = D - deg S~; fall_dim(D) = rank(M_D) - rank(H_D);
d_ff = least D with fall_dim(D) > 0).  No Groebner output degree and no CAS
termination event is read anywhere.

Subcommands (one immutable run directory each, written through
harness.runner.run_wrapped so wall time is wrapper-measured):

  htop      CTRL-H-TOP-SYMBOLIC at m = 3 (sympy resultant; Sage absent)
  s2gate    CTRL-S2-HAND-FIXTURE: s = 2, one curve, one target, p = 4099
  cell      one (m, s) cell over all curves, targets, primes and arms
            (Semaev, NULL-1 support-matched, NULL-2 block-factored, NULL-3 is
            the curve/target spread of the Semaev arm)
  hwil      CTRL-H-WIL-DIRECT-RANK, s in 2..8, all j, p in {4099, 65537}
  nearby    NEARBY-MIXED-BLOCK and NEARBY-NON-MONOMIAL-TOP at (2, 2, 3)

Observations only; this script scores against the frozen prediction file
(stage0-predictions.yaml, sha256 recorded in every manifest) and never
edits it.  Statuses: completed_valid | completed_invalid | failed_infrastructure.
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
import subprocess
import sys
import time
from math import comb

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

import sympy  # noqa: E402
import yaml  # noqa: E402

from harness import semaev as hsemaev  # noqa: E402
from harness.macaulay_fp import (  # noqa: E402
    ColumnSpace,
    Ring,
    analyze_layer,
    block_factored_system,
    digit_presentation,
    semiregular_prediction,
    substitute,
    support_matched_system,
)
from harness.runner import RunResult, run_wrapped  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-PFDR-5726af"
AREA = "PFDR-5726af"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
PRED_PATH = os.path.join(EXP_DIR, "stage0-predictions.yaml")
METER_DIR = os.path.join(REPO, "harness", "macaulay_fp")

WALL_CAP_SECONDS = 1800          # contract: wall_clock_seconds_per_run
WALL_GUARD_SECONDS = 1680        # stop starting new systems past this point
MEMORY_CAP_GB = 8                # contract: maximum_memory_gb

PRIMES = [4099, 65537]
CURVE_SEEDS = [1101, 1102, 1103]
TARGET_SEEDS = [1, 2]
NULL_SEEDS = [7, 11, 13, 17, 19]
MIXED_SEEDS = [31, 37, 41]
PLANT_WINDOW_M2 = 4              # x(P_i) in [0, 4): valid for every s >= 2 (shared targets along the ladder)
PLANT_WINDOW_M3 = 16             # m = 3: x(P_i) in [0, 16): valid for s in {4, 5}

T0 = time.monotonic()


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
        for n in sorted(names):
            p = os.path.join(root, n)
            files[os.path.relpath(p, REPO)] = sha256_file(p)
    files["tests/test_macaulay_fp.py"] = sha256_file(os.path.join(REPO, "tests", "test_macaulay_fp.py"))
    return {
        "meter_commit": git("log", "-1", "--format=%H", "--", "harness/macaulay_fp"),
        "meter_commit_short": git("log", "-1", "--format=%h", "--", "harness/macaulay_fp"),
        "files_sha256": files,
    }


def predictions() -> tuple[dict, str]:
    with open(PRED_PATH, "r", encoding="utf-8") as fh:
        text = fh.read()
    return yaml.safe_load(text)["stage0_predictions"], hashlib.sha256(text.encode()).hexdigest()


def session_inference() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "requested_reasoning_effort": "medium",
        "adapter_resolution": "python3 -m orchestration.adapter resolve --role executor -> anthropic:claude-sonnet-5 (effort=medium)",
        "runtime_reported_model": "claude-fable-5-1",
        "model_verified": False,
        "model_verified_note": (
            "The adapter binding (claude-sonnet-5) and the model identifier reported by the "
            "executing session (claude-fable-5-1) differ; the Executor cannot verify its own "
            "binding from inside the session.  AUTORESEARCH_POLICY was deliberately NOT set for "
            "the run process, because the adapter would then record model_verified: true for "
            "claude-sonnet-5, which is not known to be true of this session.  The wrapper's own "
            "inference block therefore records 'no model in the loop', which is true of this "
            "deterministic script; this block records the SESSION that wrote and launched it."),
        "fallback_used": "unknown",
        "degraded": False,
        "independent_session": True,
        "no_bedrock": True,
    }


def dirty_tree_hash() -> dict:
    """sha256 of `git diff HEAD` over tracked files plus the untracked source list."""
    diff = subprocess.run(["git", "diff", "HEAD"], cwd=REPO, capture_output=True).stdout
    status = git("status", "--porcelain")
    return {
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "tracked_diff_bytes": len(diff),
        "porcelain_sha256": hashlib.sha256(status.encode()).hexdigest(),
        "porcelain_line_count": len([l for l in status.splitlines() if l]),
    }


def set_memory_cap() -> None:
    cap = MEMORY_CAP_GB * 1024 ** 3
    try:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    except (ValueError, OSError) as exc:  # pragma: no cover
        print(f"WARNING: could not set RLIMIT_AS: {exc}", file=sys.stderr)


def elapsed() -> float:
    return time.monotonic() - T0


def guard_tripped() -> bool:
    return elapsed() > WALL_GUARD_SECONDS


# --------------------------------------------------------------------------
# Semaev polynomials (from scratch) and cross-checks
# --------------------------------------------------------------------------
def s3_dict(a: int, b: int, xR: int, p: int) -> dict:
    """S_3(x_1, x_2, x_R) for y^2 = x^3 + a x + b as {(e1, e2): coeff mod p}.

    S_3 = (x1 - x2)^2 xR^2 - 2((x1 + x2)(x1 x2 + a) + 2 b) xR + (x1 x2 - a)^2 - 4 b (x1 + x2).
    """
    d: dict = {}

    def add(e, c):
        d[e] = (d.get(e, 0) + c) % p

    add((2, 0), xR * xR)
    add((0, 2), xR * xR)
    add((1, 1), -2 * xR * xR)
    add((2, 1), -2 * xR)
    add((1, 2), -2 * xR)
    add((1, 0), -2 * a * xR)
    add((0, 1), -2 * a * xR)
    add((0, 0), -4 * b * xR)
    add((2, 2), 1)
    add((1, 1), -2 * a)
    add((0, 0), a * a)
    add((1, 0), -4 * b)
    add((0, 1), -4 * b)
    return {e: c for e, c in d.items() if c}


def s3_crosscheck(a: int, b: int, xR: int, p: int, rng: random.Random, trials: int = 20) -> bool:
    """Own S_3 against harness.semaev.s3_eval at random points (independent code path)."""
    d = s3_dict(a, b, xR, p)
    for _ in range(trials):
        v1, v2 = rng.randrange(p), rng.randrange(p)
        mine = sum(c * pow(v1, e[0], p) * pow(v2, e[1], p) for e, c in d.items()) % p
        if mine != hsemaev.s3_eval(a, b, v1, v2, xR, p):
            return False
    return True


_X1, _X2, _X3, _T = sympy.symbols("x1 x2 x3 T")


def s3_sympy(a, b, x, y, z):
    """From-scratch symbolic S_3(x, y, z) (NOT harness.semaev.s3_expr; that is only cross-checked)."""
    return (x - y) ** 2 * z ** 2 - 2 * ((x + y) * (x * y + a) + 2 * b) * z + (x * y - a) ** 2 - 4 * b * (x + y)


def s4_sympy(a, b, xR):
    """S_4(x1, x2, x3, xR) = Res_T(S_3(x1, x2, T), S_3(x3, xR, T)), built from the from-scratch S_3."""
    left = sympy.Poly(s3_sympy(a, b, _X1, _X2, _T), _T)
    right = sympy.Poly(s3_sympy(a, b, _X3, xR, _T), _T)
    return sympy.expand(sympy.resultant(left, right, _T))


def s4_dict(a: int, b: int, xR: int, p: int) -> dict:
    """S_4 with numeric (a, b, x_R) as {(e1, e2, e3): coeff mod p}."""
    expr = s4_sympy(sympy.Integer(a), sympy.Integer(b), sympy.Integer(xR))
    poly = sympy.Poly(expr, _X1, _X2, _X3)
    out = {}
    for exps, c in poly.as_dict().items():
        c = int(c) % p
        if c:
            out[tuple(int(e) for e in exps)] = c
    return out


def s4_crosscheck(a: int, b: int, xR: int, p: int, d: dict, rng: random.Random, trials: int = 6) -> bool:
    """S_4 vanishes at (x(P1), x(P2), x(P3)) whenever P1 + P2 + P3 = +-R; check on random on-curve triples
    with R := P1 + P2 + P3 (a from-scratch-free consistency check of the resultant route: for random
    (v1, v2, v3) evaluate S_4 at (v1, v2, v3, x(P1 + P2 + P3)) using the SAME formula with xR replaced)."""
    E = EllipticCurve(p, a, b)
    ok = True
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
        val = sum(c * pow(pts[0][0], e[0], p) * pow(pts[1][0], e[1], p) * pow(pts[2][0], e[2], p)
                  for e, c in dd.items()) % p
        if val != 0:
            ok = False
    _ = d
    return ok


# --------------------------------------------------------------------------
# curves, targets, certificates
# --------------------------------------------------------------------------
def H(seed: int, tag: str) -> int:
    return int(hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest(), 16)


def make_curve(p: int, seed: int, window: int, min_pts: int) -> dict:
    """Generic-j short-Weierstrass curve from (p, seed): a, b = SHA-256 draws, rejecting a = 0, b = 0
    (j in {0, 1728}), singular curves, and curves with fewer than ``min_pts`` on-curve x in [0, window)."""
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
        return {"p": p, "a": a, "b": b, "j": j, "seed": seed, "attempt": t,
                "rejections": rejections, "window": window, "window_x": xs}
    raise RuntimeError("no curve found")


def independent_add(p: int, a: int, P, Q):
    """Second, deliberately separate implementation of the group law for certificate re-verification."""
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


def plant_target(curve: dict, m: int, target_seed: int, window: int) -> dict:
    p, a, b = curve["p"], curve["a"], curve["b"]
    E = EllipticCurve(p, a, b)
    rng = random.Random(H(target_seed, f"{p}:{curve['seed']}:target"))
    xs = [x for x in range(window) if E.lift_x(x) is not None]
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
        return {"target_seed": target_seed, "attempt": attempt, "x_R": R[0], "R": [R[0], R[1]],
                "summands": [[P[0], P[1]] for P in pts], "certificate": cert,
                "verified_independent_add": independent_verify(cert),
                "verified_harness_semaev": bool(hsemaev.verify_decomposition_certificate(cert))}
    raise RuntimeError("could not plant a target")


# --------------------------------------------------------------------------
# meter wrappers
# --------------------------------------------------------------------------
def layer_summary(L) -> dict:
    return {"D": L.degree, "rows": L.row_count, "zero_rows": L.zero_product_rows,
            "ncols_full": L.ncols_full, "ncols_top": L.ncols_top,
            "full_rank": L.full_rank, "top_rank": L.top_rank,
            "fall_dim": L.fall_dim, "syzygy_dim": L.syzygy_dim,
            "nnz_total": L.nnz_total, "reduction_ops": L.reduction_ops}


def profile(ring: Ring, g: dict, delta: int, dmax: int, columns: ColumnSpace,
            stop_at_first_fall: bool) -> dict:
    pred = semiregular_prediction(ring, [delta], dmax, False)
    layers = []
    d_ff = None
    fall = None
    t = time.monotonic()
    for D in range(delta, dmax + 1):
        L = analyze_layer(ring, [g], D, "per_layer", columns, frobenius=False, prediction=pred)
        layers.append(layer_summary(L))
        if L.fall_dim > 0 and d_ff is None:
            d_ff = D
            fall = L.fall_dim
            if stop_at_first_fall:
                break
    return {"d_ff": d_ff, "fall_dim_at_d_ff": fall, "D_max_computed": layers[-1]["D"] if layers else None,
            "layers": layers, "seconds": round(time.monotonic() - t, 3),
            "censored": d_ff is None and (layers[-1]["D"] if layers else -1) < dmax}


def sol_profile(ring: Ring, g: dict, delta: int, dmax: int, columns: ColumnSpace) -> dict:
    """IDEA-20260806-7ea402 covariate: sol(D) = [rank(cumulative Mac_D) >= ncols(D) - N_sol],
    d_solve = min D with sol(D).  N_sol counted by brute force over {0,1}^n."""
    n = ring.n_sq
    nsol = 0
    for bits in range(1 << n):
        vals = [(bits >> i) & 1 for i in range(n)]
        if ring.evaluate(g, vals) == 0:
            nsol += 1
    pred = semiregular_prediction(ring, [delta], dmax, False)
    sol = []
    d_solve = None
    for D in range(delta, dmax + 1):
        L = analyze_layer(ring, [g], D, "cumulative", columns, frobenius=False, prediction=pred)
        s = L.full_rank >= L.ncols_full - nsol
        sol.append({"D": D, "cum_rank": L.full_rank, "ncols": L.ncols_full, "sol": s})
        if s and d_solve is None:
            d_solve = D
    return {"N_sol": nsol, "sol": sol, "d_solve": d_solve}


def oracle_ranks(ring: Ring, g: dict, D: int, columns: ColumnSpace) -> dict:
    """Independent rank oracle: sympy DomainMatrix over GF(p) on the same rows (full and top)."""
    from sympy.polys.matrices import DomainMatrix
    from sympy import GF
    from harness.macaulay_fp import layer_rows
    rows, _prov, _z = layer_rows(ring, [g], D, "per_layer", False)
    ncols = columns.ncols_upto(D)
    top_start = columns.degree_start[D]
    full = [[0] * ncols for _ in rows]
    top = [[0] * (ncols - top_start) for _ in rows]
    for i, r in enumerate(rows):
        for m, c in r.items():
            j = columns.index[m]
            full[i][j] = c % ring.p
            if j >= top_start:
                top[i][j - top_start] = c % ring.p
    K = GF(ring.p)
    rf = DomainMatrix([[K(v) for v in row] for row in full], (len(full), ncols), K).rank() if full else 0
    rt = DomainMatrix([[K(v) for v in row] for row in top], (len(top), ncols - top_start), K).rank() if top and ncols > top_start else 0
    return {"D": D, "oracle_full_rank": int(rf), "oracle_top_rank": int(rt), "oracle_fall_dim": int(rf - rt)}


def top_form_tensor_check(ring: Ring, pres, g: dict, e: int) -> dict:
    """Is top(S~) exactly c * prod_k ell_k^e in the ring (with a^2 -> a, compare degree-m*e parts)?"""
    prod = {ring.one(): 1}
    for x in pres.unknown_polys:
        prod = ring.mul(prod, ring.power(x, e))
    top_pred = ring.degree_part(prod, e * len(pres.unknown_polys))
    top_g = ring.top_form(g)
    if not top_pred or not top_g:
        return {"match": False, "reason": "empty top form"}
    m0 = next(iter(top_g))
    if m0 not in top_pred:
        return {"match": False, "reason": "support differs"}
    c = top_g[m0] * pow(top_pred[m0], -1, ring.p) % ring.p
    scaled = ring.scale(top_pred, c)
    return {"match": scaled == top_g, "c": c, "top_terms": len(top_g), "top_degree": ring.degree(g)}


# --------------------------------------------------------------------------
# cell runner
# --------------------------------------------------------------------------
def build_system_fn(m: int, a: int, b: int, xR: int, p: int):
    if m == 2:
        d = s3_dict(a, b, xR, p)
    elif m == 3:
        d = s4_dict(a, b, xR, p)
    else:
        raise ValueError("m must be 2 or 3")

    def system(ring, xs):
        return [substitute(ring, d, xs)]
    return system, d


def run_cell(args) -> RunResult:
    m, s = args.m, args.s
    e = 2 ** (m - 1)
    delta = m * e
    n = m * s
    D_null = (m * s + m * e) // 2 + 1
    D_null_84 = math.ceil((m * s + 2 * m) / 2)
    dmax = D_null + 1
    pred, pred_sha = predictions()
    cell_key = f"({m},2,{s})"
    frozen = pred["scored_against"]["semaev_arm"][cell_key]
    frozen_null1 = pred["scored_against"]["null_1_support_matched"][cell_key]["d_ff"]
    primes = [int(x) for x in args.primes.split(",")]
    curve_seeds = [int(x) for x in args.curve_seeds.split(",")]
    target_seeds = [int(x) for x in args.target_seeds.split(",")]
    stop_first = bool(args.stop_at_first_fall)
    do_sol = n <= 10
    do_oracle = bool(args.oracle)
    window = PLANT_WINDOW_M2 if m == 2 else PLANT_WINDOW_M3
    out: list[str] = []
    log = lambda *a: out.append(" ".join(str(x) for x in a))  # noqa: E731
    log(f"cell m={m} d=2 s={s} n={n} delta={delta} D_null={D_null} (84cdb7 convention {D_null_84}) D_max={dmax}")
    log(f"frozen prediction: {frozen}; NULL-1 predicted d_ff={frozen_null1}; predictions sha256={pred_sha}")
    gate = None
    gate_cert = None
    gate_valid = True
    if args.s2_gate:
        if s != 2 or m != 2:
            raise ValueError("--s2-gate applies to the (2, 2, 2) cell only")
        gate, gate_cert, gate_valid = s2_gate_metrics()
        log(f"CTRL-S2-HAND-FIXTURE: degree-4 part {gate['degree_4_part_meter']} (expected {gate['degree_4_part_expected']}); "
            f"d_ff={gate['d_ff']} fall_dim={gate['fall_dim']} gate_pass={gate['gate_pass']} oracle_agrees={gate['oracle_agrees']}")

    draws = []
    cert_all_ok = True
    censored = []
    columns_by_p = {}
    null2_by_p_seed = {}
    manifest_cert = {"kind": "none", "note": "no draw"}
    for p in primes:
        ring = Ring(p, n, 0)
        columns = ColumnSpace.build(ring, dmax)
        columns_by_p[p] = columns
        blocks = [[k * s + i for i in range(s)] for k in range(m)]
        # NULL-2 has no curve/target input: computed once per (p, seed), reported per draw by reference.
        for seed in NULL_SEEDS:
            gens, meta, factors = block_factored_system(ring, blocks, [e] * m, seed)
            g2 = gens[0]
            fdeg = [ring.degree(f) for f in factors[0]]
            prof = profile(ring, g2, delta, dmax, columns, stop_first)
            null2_by_p_seed[(p, seed)] = {"p": p, "seed": seed, "factor_degrees": fdeg,
                                          "generator_degree": ring.degree(g2), "terms": len(g2),
                                          "degenerate": any(dd != e for dd in fdeg), **prof}
            log(f"  NULL-2 p={p} seed={seed}: d_ff={prof['d_ff']} fall_dim={prof['fall_dim_at_d_ff']} ({prof['seconds']}s)")
        for cs in curve_seeds:
            curve = make_curve(p, cs, PLANT_WINDOW_M2, 2)
            for ts in target_seeds:
                tgt = plant_target(curve, m, ts, window)
                if not (tgt["verified_independent_add"] and tgt["verified_harness_semaev"]):
                    cert_all_ok = False
                rng = random.Random(H(ts, f"{p}:{cs}:xcheck"))
                system, sdict = build_system_fn(m, curve["a"], curve["b"], tgt["x_R"], p)
                xcheck = s3_crosscheck(curve["a"], curve["b"], tgt["x_R"], p, rng) if m == 2 else \
                    s4_crosscheck(curve["a"], curve["b"], tgt["x_R"], p, sdict, rng)
                pres = digit_presentation(p, m, 2, s, system)
                g = pres.generators[0]
                assert pres.ring == ring
                draw = {"p": p, "curve_seed": cs, "curve": {k: curve[k] for k in ("a", "b", "j", "attempt", "window_x")},
                        "curve_rejections": len(curve["rejections"]),
                        "target": {k: tgt[k] for k in ("target_seed", "attempt", "x_R", "R", "summands",
                                                       "verified_independent_add", "verified_harness_semaev")},
                        "certificate": tgt["certificate"],
                        "s_poly_crosscheck_random_points": xcheck,
                        "generator_terms": len(g), "generator_degree": ring.degree(g),
                        "top_form_tensor_check": top_form_tensor_check(ring, pres, g, e),
                        "is_frozen_fixture": (p == 4099 and cs == 1101 and ts == 1 and m == 2 and s == 3)}
                if manifest_cert["kind"] == "none":
                    manifest_cert = tgt["certificate"]
                if draw["is_frozen_fixture"]:
                    manifest_cert = tgt["certificate"]
                # Semaev arm: full profile to D_max unless stop_first
                sem = profile(ring, g, delta, dmax, columns, stop_first)
                draw["semaev"] = sem
                if do_oracle:
                    draw["oracle"] = [oracle_ranks(ring, g, L["D"], columns) for L in sem["layers"]]
                    draw["oracle_agrees"] = all(
                        o["oracle_full_rank"] == L["full_rank"] and o["oracle_top_rank"] == L["top_rank"]
                        for o, L in zip(draw["oracle"], sem["layers"]))
                if do_sol:
                    draw["sol_covariate"] = sol_profile(ring, g, delta, dmax, columns)
                else:
                    draw["sol_covariate"] = {"not_computed": "n > 10; cumulative eliminations omitted for budget"}
                draw["null2"] = [{"seed": seed, "ref": f"null2[p={p},seed={seed}]",
                                  "d_ff": null2_by_p_seed[(p, seed)]["d_ff"],
                                  "fall_dim_at_d_ff": null2_by_p_seed[(p, seed)]["fall_dim_at_d_ff"]}
                                 for seed in NULL_SEEDS]
                draw["null1"] = []
                draw["_ring_g"] = (ring, g, columns)
                draws.append(draw)
                log(f"  Semaev p={p} curve={cs} target={ts} x_R={tgt['x_R']}: d_ff={sem['d_ff']} fall_dim={sem['fall_dim_at_d_ff']} "
                    f"profile={[(L['D'], L['rows'], L['full_rank'], L['top_rank'], L['fall_dim']) for L in sem['layers']]} ({sem['seconds']}s) t={elapsed():.0f}s")
    # NULL-1 interleaved by seed so a wall-clock guard censors the last seeds uniformly across draws
    for seed in NULL_SEEDS:
        for draw in draws:
            ring, g, columns = draw["_ring_g"]
            if guard_tripped():
                censored.append({"p": draw["p"], "curve_seed": draw["curve_seed"],
                                 "target_seed": draw["target"]["target_seed"], "seed": seed})
                continue
            polys, meta = support_matched_system(ring, [g], seed)
            g1 = polys[0]
            prof = profile(ring, g1, delta, dmax, columns, stop_first)
            draw["null1"].append({"seed": seed, "terms": len(g1), "degree": ring.degree(g1), **prof})
            log(f"  NULL-1 p={draw['p']} curve={draw['curve_seed']} target={draw['target']['target_seed']} seed={seed}: "
                f"d_ff={prof['d_ff']} fall_dim={prof['fall_dim_at_d_ff']} ({prof['seconds']}s) t={elapsed():.0f}s")
    for draw in draws:
        del draw["_ring_g"]

    # ---- scoring against the frozen file (observations only) ----
    sem_pairs = [(d["semaev"]["d_ff"], d["semaev"]["fall_dim_at_d_ff"]) for d in draws]
    P1 = all(x[0] == frozen["d_ff"] for x in sem_pairs)
    P2 = all(x[1] == frozen["fall_dim"] for x in sem_pairs)
    null2_pairs = [(v["d_ff"], v["fall_dim_at_d_ff"]) for v in null2_by_p_seed.values()]
    P3_diffs = []
    for d in draws:
        for v in d["null2"]:
            P3_diffs.append({"p": d["p"], "curve_seed": d["curve_seed"], "target_seed": d["target"]["target_seed"],
                             "seed": v["seed"],
                             "d_ff_diff": None if (v["d_ff"] is None or d["semaev"]["d_ff"] is None) else v["d_ff"] - d["semaev"]["d_ff"],
                             "fall_dim_diff": None if (v["fall_dim_at_d_ff"] is None or d["semaev"]["fall_dim_at_d_ff"] is None)
                             else v["fall_dim_at_d_ff"] - d["semaev"]["fall_dim_at_d_ff"]})
    P3 = all(x["d_ff_diff"] == 0 and x["fall_dim_diff"] == 0 for x in P3_diffs)
    null1_vals = [v["d_ff"] for d in draws for v in d["null1"]]
    null1_computed = len(null1_vals)
    null1_at_Dnull = sum(1 for v in null1_vals if v == D_null)
    null1_below = sum(1 for v in null1_vals if v is not None and v < D_null)
    null1_none = sum(1 for v in null1_vals if v is None)
    null1_hist = {}
    for v in null1_vals:
        null1_hist[str(v)] = null1_hist.get(str(v), 0) + 1
    crit3 = null1_computed > 0 and null1_at_Dnull * 2 > null1_computed and null1_below == 0
    F4 = any(v == frozen["d_ff"] for v in null1_vals)
    spread_dff = sorted({x[0] for x in sem_pairs}, key=lambda v: (v is None, v))
    spread_fall = sorted({x[1] for x in sem_pairs}, key=lambda v: (v is None, v))
    NULL3_identical = len(spread_dff) == 1 and len(spread_fall) == 1
    residuals = [{"p": d["p"], "curve_seed": d["curve_seed"], "target_seed": d["target"]["target_seed"],
                  "d_ff_residual": None if d["semaev"]["d_ff"] is None else d["semaev"]["d_ff"] - frozen["d_ff"],
                  "fall_dim_residual": None if d["semaev"]["fall_dim_at_d_ff"] is None else d["semaev"]["fall_dim_at_d_ff"] - frozen["fall_dim"]}
                 for d in draws]
    top_ok = all(d["top_form_tensor_check"]["match"] for d in draws)
    xcheck_ok = all(d["s_poly_crosscheck_random_points"] for d in draws)
    oracle_ok = all(d.get("oracle_agrees", True) for d in draws) if do_oracle else None

    metrics = {
        "cell": {"m": m, "d": 2, "s": s, "n": n, "delta": delta, "e": e, "D_null": D_null,
                 "D_null_84cdb7_convention": D_null_84, "D_max": dmax, "primes": primes,
                 "curve_seeds": curve_seeds, "target_seeds": target_seeds, "null_seeds": NULL_SEEDS,
                 "stop_at_first_fall": stop_first, "ncols_full_at_Dmax": {str(p): columns_by_p[p].ncols_upto(dmax) for p in primes}},
        "frozen_prediction": {"semaev": frozen, "null1_d_ff": frozen_null1, "null2": "identical to Semaev",
                              "file_sha256": pred_sha},
        "semaev_draws": len(draws),
        "semaev_d_ff_values": [x[0] for x in sem_pairs],
        "semaev_fall_dim_values": [x[1] for x in sem_pairs],
        "semaev_d_ff_spread": spread_dff,
        "semaev_fall_dim_spread": spread_fall,
        "residuals": residuals,
        "P1_all_semaev_d_ff_equal_frozen": P1,
        "P2_all_semaev_fall_dim_equal_frozen": P2,
        "null2_pairs_by_p_seed": [{"p": k[0], "seed": k[1], "d_ff": v["d_ff"], "fall_dim": v["fall_dim_at_d_ff"],
                                   "degenerate": v["degenerate"]} for k, v in null2_by_p_seed.items()],
        "P3_null2_minus_semaev_all_zero": P3,
        "P3_nonzero_entries": [x for x in P3_diffs if not (x["d_ff_diff"] == 0 and x["fall_dim_diff"] == 0)],
        "null1_d_ff_histogram": null1_hist,
        "null1_computed": null1_computed,
        "null1_planned": len(draws) * len(NULL_SEEDS),
        "null1_censored_by_wall_guard": censored,
        "null1_at_D_null": null1_at_Dnull,
        "null1_below_D_null": null1_below,
        "null1_no_fall_by_Dmax": null1_none,
        "criterion3_null1_majority_at_D_null_none_below": crit3,
        "F4_null1_falls_at_semaev_value_any_seed": F4,
        "NULL3_identical_across_curves_targets_primes": NULL3_identical,
        "gap_D_null_minus_d_ff": (D_null - spread_dff[0]) if (len(spread_dff) == 1 and spread_dff[0] is not None) else None,
        "top_form_is_c_prod_ell_e_all_draws": top_ok,
        "s_polynomial_crosscheck_all_draws": xcheck_ok,
        "oracle_rank_agreement_all_layers": oracle_ok,
        "certificates_all_verified": cert_all_ok,
        "d_solve_values": [d["sol_covariate"].get("d_solve") for d in draws] if do_sol else "not computed",
        "N_sol_values": [d["sol_covariate"].get("N_sol") for d in draws] if do_sol else "not computed",
        "wall_guard_tripped": bool(censored),
        "elapsed_seconds_script": round(elapsed(), 3),
    }
    if gate is not None:
        metrics["CTRL-S2-HAND-FIXTURE"] = gate
        metrics["gate_pass"] = gate["gate_pass"]
    valid = cert_all_ok and top_ok and xcheck_ok and (oracle_ok is not False) and gate_valid
    invalid_reason = None if valid else "certificate, top-form, S-polynomial cross-check or rank-oracle failure (see metrics)"
    params = {
        "task_id": "TASK-20260903-b0727c", "stage": args.stage, "control_ids": args.controls.split(","),
        "m": m, "d": 2, "s": s, "primes": primes, "curve_seeds": curve_seeds, "target_seeds": target_seeds,
        "null_seeds": NULL_SEEDS, "plant_window": window, "curve_acceptance_window": PLANT_WINDOW_M2,
        "convention": "per_layer, leading_forms=False, frobenius=False, rows mu*S~ with deg mu = D - delta",
        "stop_at_first_fall": stop_first, "D_max": dmax,
        "stage0_predictions_sha256": pred_sha, "meter": meter_provenance(),
        "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
        "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "wall_guard_seconds": WALL_GUARD_SECONDS,
                   "memory_gb": MEMORY_CAP_GB, "workers": 1},
    }
    return RunResult(run_suffix=args.run_suffix, curve_id=f"generic-j curves seeds {curve_seeds} at p in {primes}",
                     seed=curve_seeds[0], parameters=params, metrics=metrics, certificate=manifest_cert,
                     valid=valid, invalid_reason=invalid_reason, stdout="\n".join(out) + "\n", stderr="",
                     raw={"draws": draws, "null2_by_p_seed": [v for v in null2_by_p_seed.values()],
                          "frozen_prediction_file_sha256": pred_sha})


# --------------------------------------------------------------------------
# s = 2 gate
# --------------------------------------------------------------------------
def s2_gate_metrics() -> tuple[dict, dict, bool]:
    """CTRL-S2-HAND-FIXTURE: s = 2, n = 4, curve seed 1101, target seed 1, p = 4099."""
    pred, pred_sha = predictions()
    fx = pred["s2_hand_fixture"]["expected"]
    p, m, s = 4099, 2, 2
    curve = make_curve(p, 1101, PLANT_WINDOW_M2, 2)
    tgt = plant_target(curve, m, 1, PLANT_WINDOW_M2)
    system, _ = build_system_fn(m, curve["a"], curve["b"], tgt["x_R"], p)
    pres = digit_presentation(p, m, 2, s, system)
    ring, g = pres.ring, pres.generators[0]
    columns = ColumnSpace.build(ring, 6)
    top = ring.top_form(g)
    expected_top = {(0b1111, ()): 16 % p}
    prof = profile(ring, g, 4, 6, columns, False)
    oracle = [oracle_ranks(ring, g, L["D"], columns) for L in prof["layers"]]
    oracle_ok = all(o["oracle_full_rank"] == L["full_rank"] and o["oracle_top_rank"] == L["top_rank"]
                    for o, L in zip(oracle, prof["layers"]))
    sol = sol_profile(ring, g, 4, 6, columns)
    names = [f"a{k}{i}" for k in (1, 2) for i in (0, 1)]
    metrics = {
        "control": "CTRL-S2-HAND-FIXTURE",
        "degree_4_part_meter": ring.to_string(top, names),
        "degree_4_part_expected": fx["degree_4_part"],
        "degree_4_part_matches": top == expected_top,
        "d_ff": prof["d_ff"], "fall_dim": prof["fall_dim_at_d_ff"],
        "expected": fx, "D_null": 5,
        "gate_pass": bool(top == expected_top and prof["d_ff"] == fx["d_ff"] and prof["fall_dim_at_d_ff"] == fx["fall_dim"]),
        "profile": prof["layers"], "oracle": oracle, "oracle_agrees": oracle_ok,
        "certificate_verified_independent_add": tgt["verified_independent_add"],
        "certificate_verified_harness_semaev": tgt["verified_harness_semaev"],
        "sol_covariate": sol,
        "curve": {k: curve[k] for k in ("a", "b", "j", "attempt", "window_x")}, "x_R": tgt["x_R"],
        "generator": ring.to_string(g, names),
    }
    valid = bool(tgt["verified_independent_add"] and tgt["verified_harness_semaev"] and oracle_ok)
    return metrics, tgt["certificate"], valid


def run_s2gate(args) -> RunResult:
    pred, pred_sha = predictions()
    metrics, cert, valid = s2_gate_metrics()
    params = {"task_id": "TASK-20260903-b0727c", "stage": "stage-1-deciding-cell (gate)",
              "control_ids": ["CTRL-S2-HAND-FIXTURE"], "m": 2, "d": 2, "s": 2, "p": 4099,
              "curve_seed": 1101, "target_seed": 1, "D_max": 6,
              "convention": "per_layer, leading_forms=False, frobenius=False",
              "stage0_predictions_sha256": pred_sha, "meter": meter_provenance(),
              "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
              "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "memory_gb": MEMORY_CAP_GB, "workers": 1}}
    return RunResult(run_suffix=args.run_suffix, curve_id="TOY-P4099-seed1101", seed=1101, parameters=params,
                     metrics=metrics, certificate=cert, valid=valid,
                     invalid_reason=None if valid else "certificate or oracle failure",
                     stdout=json.dumps(metrics, indent=1, default=str) + "\n", stderr="",
                     raw={"frozen_prediction_file_sha256": pred_sha})


# --------------------------------------------------------------------------
# H-WIL direct rank check
# --------------------------------------------------------------------------
def hwil_matrix_rank(p: int, s: int, j: int, weights: list[int]) -> int:
    """Independent construction: matrix of multiplication by ell^2 (ell = sum_i w_i a_i) from
    degree-j to degree-(j+2) squarefree monomials in F_p[a]/(a_i^2); rank by sympy over GF(p)."""
    from itertools import combinations
    from sympy.polys.matrices import DomainMatrix
    from sympy import GF
    src = list(combinations(range(s), j))
    dst = list(combinations(range(s), j + 2))
    idx = {d: i for i, d in enumerate(dst)}
    # ell^2 in a_i^2 = 0: 2 sum_{i<k} w_i w_k a_i a_k
    rows = []
    for S in src:
        row = [0] * len(dst)
        Sset = set(S)
        for i in range(s):
            for k in range(i + 1, s):
                if i in Sset or k in Sset:
                    continue
                T = tuple(sorted(Sset | {i, k}))
                row[idx[T]] = (row[idx[T]] + 2 * weights[i] * weights[k]) % p
        rows.append(row)
    K = GF(p)
    return int(DomainMatrix([[K(v) for v in r] for r in rows], (len(rows), len(dst)), K).rank())


def run_hwil(args) -> RunResult:
    pred, pred_sha = predictions()
    table = []
    all_full = True
    tail = []
    meter_agree = True
    for p in PRIMES:
        for s in range(2, 9):
            ring = Ring(p, s, 0)
            ell_digit = {}
            ell_unit = {}
            for i in range(s):
                ell_digit = ring.add(ell_digit, {ring.sq_var(i): pow(2, i, p)})
                ell_unit = ring.add(ell_unit, {ring.sq_var(i): 1})
            for name, ell, w in (("digit", ell_digit, [pow(2, i, p) for i in range(s)]), ("unit", ell_unit, [1] * s)):
                sq = ring.mul(ell, ell)
                columns = ColumnSpace.build(ring, s)
                for j in range(0, s - 1):
                    D = j + 2
                    L = analyze_layer(ring, [sq], D, "per_layer", columns, leading_forms=True, frobenius=False)
                    meter_rank = L.top_rank
                    ind = hwil_matrix_rank(p, s, j, w)
                    expected = min(comb(s, j), comb(s, j + 2))
                    ok = (ind == expected) and (meter_rank == expected)
                    all_full &= ok
                    meter_agree &= (meter_rank == ind)
                    row = {"p": p, "s": s, "j": j, "ell": name, "rank_meter_top": meter_rank, "rank_independent": ind,
                           "expected": expected, "full_rank": ok, "square_map": (j + 2 == s - j)}
                    table.append(row)
                    if row["square_map"]:
                        tail.append(row)
    metrics = {"control": "CTRL-H-WIL-DIRECT-RANK", "cells": len(table),
               "all_full_rank": all_full, "meter_and_independent_agree": meter_agree,
               "square_maps": tail, "square_maps_all_full_rank": all(r["full_rank"] for r in tail),
               "below_maximum": [r for r in table if not r["full_rank"]],
               "frozen": pred["scored_against"]["hwil"]}
    params = {"task_id": "TASK-20260903-b0727c", "stage": "stage-1-deciding-cell (H-WIL)",
              "control_ids": ["CTRL-H-WIL-DIRECT-RANK"], "s_range": [2, 8], "primes": PRIMES,
              "ell_variants": ["digit: sum 2^i a_i", "unit: sum a_i"],
              "stage0_predictions_sha256": pred_sha, "meter": meter_provenance(),
              "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
              "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "memory_gb": MEMORY_CAP_GB, "workers": 1}}
    lines = [f"{r['p']} s={r['s']} j={r['j']} {r['ell']}: meter={r['rank_meter_top']} indep={r['rank_independent']} expected={r['expected']} {'OK' if r['full_rank'] else 'BELOW'}" for r in table]
    return RunResult(run_suffix=args.run_suffix, curve_id="curve-free", seed=0, parameters=params, metrics=metrics,
                     certificate={"kind": "none", "note": "pure rank measurement; nothing to certify"},
                     valid=meter_agree, invalid_reason=None if meter_agree else "meter and independent oracle disagree",
                     stdout="\n".join(lines) + "\n", stderr="", raw={"table": table, "frozen_prediction_file_sha256": pred_sha})


# --------------------------------------------------------------------------
# H-TOP symbolic check at m = 3
# --------------------------------------------------------------------------
def run_htop(args) -> RunResult:
    pred, pred_sha = predictions()
    a, b, xR = sympy.symbols("a b x_R")
    t = time.monotonic()
    S4 = s4_sympy(a, b, xR)
    P4 = sympy.Poly(S4, _X1, _X2, _X3)
    total_deg = P4.total_degree()
    per_var = [P4.degree(v) for v in (_X1, _X2, _X3)]
    terms = P4.as_dict()
    top_terms = {ex: c for ex, c in terms.items() if sum(ex) == total_deg}
    c_top = top_terms.get((4, 4, 4))
    c_is_const = c_top is not None and sympy.Poly(sympy.expand(c_top), a, b, xR).total_degree() == 0
    c_int = int(c_top) if c_is_const else None
    single_monomial = (list(top_terms.keys()) == [(4, 4, 4)])
    # cross-checks: (i) against harness.semaev.s4_expr's top form (the KN-OPEN-5b3a08 path, NOT relied on, reported)
    try:
        h = sympy.Poly(sympy.expand(hsemaev.s4_expr(a, b)), _X1, _X2, _X3, sympy.Symbol("x4"))
        h_total = h.total_degree()
        h_note = f"harness s4_expr total degree {h_total} in (x1,x2,x3,x4); reported only"
    except Exception as exc:  # pragma: no cover
        h_note = f"harness s4_expr failed: {exc}"
    # (ii) numeric consistency of the resultant route at both primes: S_4 vanishes on planted triples
    numeric = {}
    for p in PRIMES:
        curve = make_curve(p, 1101, PLANT_WINDOW_M2, 2)
        rng = random.Random(H(1, f"{p}:htop"))
        numeric[str(p)] = {"curve": {"a": curve["a"], "b": curve["b"]},
                           "S4_vanishes_on_random_planted_triples": s4_crosscheck(curve["a"], curve["b"], 0, p, {}, rng, 5),
                           "c_mod_p_nonzero": (c_int % p != 0) if c_int is not None else None,
                           "top_form_mod_p_single_monomial": single_monomial and (c_int % p != 0 if c_int is not None else False)}
    # (iii) m = 2 hand check in the same run: degree-4 part of S_3(x1, x2, xR) is x1^2 x2^2
    S3 = sympy.Poly(sympy.expand(s3_sympy(a, b, _X1, _X2, xR)), _X1, _X2)
    s3_top = {ex: c for ex, c in S3.as_dict().items() if sum(ex) == S3.total_degree()}
    m2_ok = (list(s3_top.keys()) == [(2, 2)] and s3_top[(2, 2)] == 1)
    archived_profile_note = (
        "The archived EXP-ALPF-011 column 'leading-form degs' [4, 4, 4, 12] at |FB| = 4 is the list of "
        "generator degrees fed to that meter (three factor-base membership polynomials of degree |FB| = 4 "
        "and S_4 of total degree 12); it is NOT a per-variable degree profile of S_4.  It confirms total "
        "degree 12 only.  The per-variable degrees [4, 4, 4] are established here symbolically.")
    metrics = {"control": "CTRL-H-TOP-SYMBOLIC", "m": 3,
               "S4_total_degree_in_x": total_deg, "S4_per_variable_degree": per_var,
               "S4_term_count": len(terms), "top_form_monomials": [list(k) for k in top_terms],
               "top_form_is_single_monomial_x1^4x2^4x3^4": single_monomial,
               "c_is_nonzero_integer_constant": bool(c_is_const and c_int != 0), "c": c_int,
               "c_expression_if_not_constant": None if c_is_const else str(c_top),
               "passes_over_Q": bool(single_monomial and c_is_const and c_int != 0),
               "passes_mod_p": {p: v["top_form_mod_p_single_monomial"] for p, v in numeric.items()},
               "numeric_checks": numeric, "m2_degree4_part_is_x1^2x2^2": m2_ok,
               "archived_profile_matches_total_degree_12": total_deg == 12,
               "archived_profile_note": archived_profile_note, "harness_s4_expr_note": h_note,
               "frozen": pred["scored_against"]["htop_m3"], "seconds": round(time.monotonic() - t, 3),
               "cas": f"sympy {sympy.__version__} (Sage absent on host; see deviations)"}
    gate = bool(metrics["passes_over_Q"] and all(metrics["passes_mod_p"].values()))
    metrics["gate_m3_secondary_open"] = gate
    params = {"task_id": "TASK-20260903-b0727c", "stage": "stage-0-derivation-and-fixture",
              "control_ids": ["CTRL-H-TOP-SYMBOLIC"], "cas": "sympy", "sage_available": False,
              "stage0_predictions_sha256": pred_sha, "meter": meter_provenance(),
              "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
              "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "memory_gb": MEMORY_CAP_GB, "workers": 1}}
    return RunResult(run_suffix=args.run_suffix, curve_id="symbolic (a, b, x_R)", seed=0, parameters=params,
                     metrics=metrics, certificate={"kind": "none", "note": "symbolic identity check; nothing to certify"},
                     valid=True, stdout=json.dumps(metrics, indent=1, default=str) + "\n", stderr="",
                     raw={"S4_top_terms": {str(k): str(v) for k, v in top_terms.items()},
                          "S4_terms_by_x_exponent": {str(k): str(v) for k, v in terms.items()},
                          "frozen_prediction_file_sha256": pred_sha})


# --------------------------------------------------------------------------
# nearby objects at (2, 2, 3)
# --------------------------------------------------------------------------
def run_nearby(args) -> RunResult:
    pred, pred_sha = predictions()
    m, s, e, delta = 2, 3, 2, 4
    n = 6
    D_null = 6
    dmax = 7
    frozen_mixed = pred["scored_against"]["nearby_mixed_block_s3"]
    out = []
    mixed = []
    nonmono = []
    cert_ok = True
    for p in PRIMES:
        ring = Ring(p, n, 0)
        columns = ColumnSpace.build(ring, dmax)
        for cs in CURVE_SEEDS:
            curve = make_curve(p, cs, PLANT_WINDOW_M2, 2)
            for ts in TARGET_SEEDS:
                tgt = plant_target(curve, m, ts, PLANT_WINDOW_M2)
                cert_ok &= tgt["verified_independent_add"]
                sd = s3_dict(curve["a"], curve["b"], tgt["x_R"], p)
                # NEARBY-MIXED-BLOCK: x_k = sum_{i<6} c_{k,i} a_i, all six digit variables shared across k
                for seed in MIXED_SEEDS:
                    rng = random.Random(H(seed, f"{p}:{cs}:{ts}:mixed"))
                    coeffs = [[rng.randrange(1, p) for _ in range(n)] for _ in range(m)]
                    xs = []
                    for k in range(m):
                        x = {}
                        for i in range(n):
                            x = ring.add(x, {ring.sq_var(i): coeffs[k][i]})
                        xs.append(x)
                    g = substitute(ring, sd, xs)
                    prof = profile(ring, g, ring.degree(g), dmax, columns, False)
                    mixed.append({"p": p, "curve_seed": cs, "target_seed": ts, "seed": seed, "coefficients": coeffs,
                                  "generator_degree": ring.degree(g), "terms": len(g), **prof})
                    out.append(f"MIXED p={p} c={cs} t={ts} seed={seed}: d_ff={prof['d_ff']} fall_dim={prof['fall_dim_at_d_ff']} deg={ring.degree(g)}")
                # NEARBY-NON-MONOMIAL-TOP: top form x1^2 x2^2 + x1^4, digit-substituted (two readings)
                pres = digit_presentation(p, m, 2, s, lambda r, xs, sd=sd: [substitute(r, sd, xs)])
                gS = pres.generators[0]
                ell1 = pres.unknown_polys[0]
                ell1_4 = ring.power(ell1, 4)
                ell1_4_top = ring.degree_part(ell1_4, 4)
                gA = ring.add(gS, ell1_4)          # S_3 + x_1^4 (same top form, Semaev lower terms)
                x1sq_x2sq = ring.mul(ring.power(ell1, 2), ring.power(pres.unknown_polys[1], 2))
                gB = ring.add(ring.degree_part(x1sq_x2sq, 4), ell1_4_top)   # homogeneous top form only
                profA = profile(ring, gA, ring.degree(gA), dmax, columns, False)
                profB = profile(ring, gB, ring.degree(gB), dmax, columns, False)
                nonmono.append({"p": p, "curve_seed": cs, "target_seed": ts,
                                "ell1_pow4_degree4_part_terms": len(ell1_4_top),
                                "note": "x_1^4 = ell_1^4 has zero degree-4 part in 3 squarefree digit variables (a_i^2 = 0 kills every degree-4 monomial of one block), so the top form collapses to x_1^2 x_2^2" if not ell1_4_top else "",
                                "reading_A_S3_plus_ell1^4": profA, "reading_B_homogeneous_top_only": profB})
                out.append(f"NONMONO p={p} c={cs} t={ts}: A d_ff={profA['d_ff']} fall={profA['fall_dim_at_d_ff']}; B d_ff={profB['d_ff']} fall={profB['fall_dim_at_d_ff']}; ell1^4 top terms={len(ell1_4_top)}")
    mixed_vals = [x["d_ff"] for x in mixed]
    metrics = {"controls": ["NEARBY-MIXED-BLOCK", "NEARBY-NON-MONOMIAL-TOP"], "cell": {"m": 2, "d": 2, "s": 3, "D_null": D_null, "D_max": dmax},
               "mixed_block_d_ff_values": mixed_vals,
               "mixed_block_d_ff_histogram": {str(v): mixed_vals.count(v) for v in set(mixed_vals)},
               "mixed_block_fall_dim_values": [x["fall_dim_at_d_ff"] for x in mixed],
               "mixed_block_all_at_least_6": all(v is not None and v >= 6 for v in mixed_vals),
               "F5_mixed_block_returns_5_any": any(v == 5 for v in mixed_vals),
               "frozen_mixed": frozen_mixed,
               "mixed_block_interpretation": "x_k = sum_{i<6} c_{k,i} a_i with ALL six digit variables shared across k=1,2 (c uniform in [1,p-1]); the literal 3-shared-variable reading makes ell_1^2 ell_2^2 vanish (degree 4 > 3 variables) and is degenerate, recorded not run",
               "non_monomial_reading_A_d_ff": [x["reading_A_S3_plus_ell1^4"]["d_ff"] for x in nonmono],
               "non_monomial_reading_B_d_ff": [x["reading_B_homogeneous_top_only"]["d_ff"] for x in nonmono],
               "non_monomial_collapse_note": nonmono[0]["note"] if nonmono else "",
               "certificates_all_verified": cert_ok, "elapsed_seconds_script": round(elapsed(), 3)}
    params = {"task_id": "TASK-20260903-b0727c", "stage": "stage-2-ladder-and-nearby",
              "control_ids": ["NEARBY-MIXED-BLOCK", "NEARBY-NON-MONOMIAL-TOP"], "m": 2, "d": 2, "s": 3,
              "primes": PRIMES, "curve_seeds": CURVE_SEEDS, "target_seeds": TARGET_SEEDS, "mixed_seeds": MIXED_SEEDS,
              "convention": "per_layer, leading_forms=False, frobenius=False", "D_max": dmax,
              "stage0_predictions_sha256": pred_sha, "meter": meter_provenance(),
              "dirty_tree": dirty_tree_hash(), "session_inference": session_inference(),
              "budget": {"wall_clock_seconds_per_run": WALL_CAP_SECONDS, "memory_gb": MEMORY_CAP_GB, "workers": 1}}
    return RunResult(run_suffix=args.run_suffix, curve_id=f"generic-j curves seeds {CURVE_SEEDS} at p in {PRIMES}", seed=31,
                     parameters=params, metrics=metrics,
                     certificate={"kind": "none", "note": "nearby-object rank measurement; planted targets re-verified per draw in raw"},
                     valid=cert_ok, invalid_reason=None if cert_ok else "certificate failure",
                     stdout="\n".join(out) + "\n", stderr="", raw={"mixed": mixed, "non_monomial": nonmono, "frozen_prediction_file_sha256": pred_sha})


# --------------------------------------------------------------------------
def package_checksums(run_id: str, out_root: str | None = None) -> None:
    run_dir = os.path.join(out_root or EXP_DIR, "runs", run_id)
    sums = {n: sha256_file(os.path.join(run_dir, n)) for n in sorted(os.listdir(run_dir)) if n != "package-sha256.json"}
    with open(os.path.join(run_dir, "package-sha256.json"), "w", encoding="utf-8") as fh:
        json.dump({"run_id": run_id, "files": sums}, fh, indent=2)


def main() -> None:
    set_memory_cap()
    ap = argparse.ArgumentParser()
    ap.add_argument("subcommand", choices=["htop", "s2gate", "cell", "hwil", "nearby"])
    ap.add_argument("--run-suffix", required=True)
    ap.add_argument("--m", type=int, default=2)
    ap.add_argument("--s", type=int, default=3)
    ap.add_argument("--primes", default="4099,65537")
    ap.add_argument("--curve-seeds", default="1101,1102,1103")
    ap.add_argument("--target-seeds", default="1,2")
    ap.add_argument("--stop-at-first-fall", type=int, default=0)
    ap.add_argument("--oracle", type=int, default=0)
    ap.add_argument("--s2-gate", type=int, default=0, help="include CTRL-S2-HAND-FIXTURE in the (2,2,2) cell run")
    ap.add_argument("--stage", default="")
    ap.add_argument("--controls", default="")
    ap.add_argument("--out-root", default=None, help="scratch dry runs only; official runs omit it")
    args = ap.parse_args()
    fn = {"htop": run_htop, "s2gate": run_s2gate, "cell": run_cell, "hwil": run_hwil, "nearby": run_nearby}[args.subcommand]
    command = "python3 " + " ".join(os.path.relpath(sys.argv[0], REPO) if i == 0 else a for i, a in enumerate(sys.argv))
    holder = {}

    def wrapped() -> RunResult:
        try:
            r = fn(args)
        except MemoryError as exc:
            r = RunResult(run_suffix=args.run_suffix, curve_id="n/a", seed=0, parameters={"error": "MemoryError"},
                          metrics={"failure_class": "resource_exhaustion", "error": str(exc)},
                          certificate={"kind": "none"}, valid=False, invalid_reason="OOM (failed_infrastructure)",
                          stderr=f"MemoryError: {exc}\n")
            holder["status"] = "failed_infrastructure"
        except Exception as exc:  # any crash is failed_infrastructure, never evidence
            import traceback
            r = RunResult(run_suffix=args.run_suffix, curve_id="n/a", seed=0, parameters={"error": type(exc).__name__},
                          metrics={"failure_class": "infrastructure_error", "error": str(exc)},
                          certificate={"kind": "none"}, valid=False, invalid_reason="crash (failed_infrastructure)",
                          stderr=traceback.format_exc())
            holder["status"] = "failed_infrastructure"
        else:
            holder["status"] = "completed_valid" if r.valid else "completed_invalid"
        if elapsed() > WALL_CAP_SECONDS:
            holder["status"] = "failed_infrastructure"
            r.valid = False
            r.invalid_reason = f"wall clock {elapsed():.0f}s exceeded the {WALL_CAP_SECONDS}s per-run cap (resource_exhaustion)"
        holder["result"] = r
        return r

    # run_wrapped brackets fn with its own clock; the status is outcome-dependent, so it is passed as a
    # _LateStatus that yaml serialises AFTER fn has run (write_run only assigns it, never compares it).
    run_id = run_wrapped(EXP_ID, AREA, wrapped, status=_LateStatus(lambda: holder["status"]), command=command,
                         out_root=args.out_root)
    package_checksums(run_id, args.out_root)
    print(run_id)
    print(f"status={holder['status']} elapsed={elapsed():.1f}s")


class _LateStatus:
    """A status value resolved when yaml serialises it (after fn has run inside run_wrapped)."""

    def __init__(self, get):
        self._get = get

    def __str__(self) -> str:
        return self._get()


def _represent_late(dumper, data):
    return dumper.represent_str(str(data))


yaml.SafeDumper.add_representer(_LateStatus, _represent_late)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECK A -- EXPONENT-NEIGHBOURHOOD CONTROL
TASK-20260803-f95b4e, BATCH-010 of GOAL-MLKEM-003.

WHAT THIS SCRIPT DOES
---------------------
For EACH archived Pwrong survival file (q=241/m=40/n=43 and q=241/m=40/n=50) it
scans the Approximation-4.9 exponent

    p = (beta_sieve + n_fft) / 2

over a neighbourhood of THAT FILE'S OWN archived value (26.0 for n=43, 24.5 for
n=50), refits the single free normalisation K at every p, and reports the full
curve of rms log2-residual against p with the argmin located explicitly.

The question is per file: does the file's own Approximation-4.9 exponent
minimise rms against its own data, or does a neighbouring exponent win?

THE ARGMIN IS REPORTED WHETHER OR NOT IT IS THE FILE'S OWN EXPONENT.  A control
that comes back favourable to Approximation 4.9 is still the control's result.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
No sampling, no lattice computation, no G6K call, no network access, no new
simulation.  Every input byte is already in this repository.  It makes no
ML-KEM or Kyber security claim in either direction, revises no cost model, and
changes no record status.  Parameters are toy (q=241, m=40, n=43/50).
AGENTS.md rule 12 is UNMET and UNWAIVED for this batch: nothing here treats
EV-MLKEM-011, EV-MLKEM-013 or EV-MLKEM-017 as corrected.

It draws NO conclusion about whether Approximation 4.9 is validated, refuted,
selected or rejected.  That judgement belongs to the independent validator and
then to the Coordinator.  This script records curves and argmins.

MODEL (unchanged from BATCH-009 / TASK-20260802-8bae8e, STEP 1-4 of
approx49_comparison.py, except where a departure is stated below)
-----------------------------------------------------------------------
    Pwrong(T; K, p) = Q(T) + INT_0^inf N e^{-v} phi(T - N e^{-v})
                                       * min(1, K v^p) dv
    Q(T)   = 0.5 * erfc(T / sqrt(N))            (the N(0,N/2) component)
    phi(s) = exp(-s^2/N) / sqrt(pi N)           (the N(0,N/2) density)
    v      = L = ln(N/u), u = the D-axis variable

K collects every quantity the archive does not carry (delta(beta_bkz),
alpha, and the constants of the UNAVAILABLE Phi_dlsc).  It is FITTED to the
data being compared, exactly as in BATCH-009.  This remains a shape-and-
relative comparison with one free normalisation, not an absolute-level test.

DEPARTURES FROM THE BATCH-009 IMPLEMENTATION (all deliberate, all stated)
------------------------------------------------------------------------
DEP-A1  CLIP HANDLED EXACTLY, NOT ON A FIXED PANEL GRID.
        BATCH-009 evaluated min(1, K v^p) node-by-node on a panel grid that
        does not put a node at the kink v* = K^{-1/p} (validator defect D10).
        Here the integral is split AT the kink:
            v >= v*:  min == 1, and the contribution is closed form,
                      INT_0^{u*} phi(T-u) du
                        = 0.5*(erfc((T-u*)/sqrt(N)) - erfc(T/sqrt(N))),
                      u* = N exp(-v*);
            v <  v*:  K * INT_0^{v*} N e^{-v} v^p phi(T - N e^{-v}) dv,
                      evaluated by panelled Gauss-Legendre.
        This is the same treatment the BATCH-009 validator used for its
        independent recomputation.  It shifts predictions by <= ~0.0007 bits
        (see `reproduction_cross_check` in the output, which reproduces the
        validator's recomputed numbers).

DEP-A2  K IS SWEPT THROUGH v*, NOT THROUGH log2 K, AND THE FIT IS EXACT
        RATHER THAN GOLDEN-SECTION.
        Since K = v*^{-p}, sweeping v* upward lets the inner integral be
        accumulated incrementally, so a whole K-scan costs one pass.  A coarse
        pass then a refinement pass inside the winning bracket locate the
        optimum to ~0.002 bits in log2 K.  BATCH-009 used a coarse integer
        scan plus golden section.  Same objective, different search.

DEP-A3  TWO FIT PROTOCOLS ARE REPORTED, NOT ONE.
        BATCH-009's headline K_fit minimised the SSE of log2 residuals on the
        20-score subsample band[::20] (+ last score) and then reported rms over
        the whole band.  Its free-exponent diagnostic used band[::40].  Here:
          protocol_A (primary): K minimises SSE over the WHOLE resolved band;
          protocol_B (continuity): K minimises SSE over band[::20]+last, i.e.
                     the BATCH-009 headline protocol.
        Both report rms over the whole resolved band, so protocol_B at the
        file's own p must reproduce BATCH-009's headline rms.

DEP-A4  FINER AND WIDER EXPONENT GRID.
        BATCH-009's diagnostic scanned p in {10,12,...,40} (step 2) plus the
        archived p, fitting on band[::40].  Here p runs over the archived
        value +/- 6.0 in steps of 0.25 (49 values), fitting on the whole band
        (protocol_A) or band[::20] (protocol_B).  Consequently the rms numbers
        here are NOT expected to equal BATCH-009's free_exponent_diagnostic
        numbers, which were computed on a 40-score subsample; they ARE expected
        to reproduce the BATCH-009 HEADLINE whole-band rms at the archived p
        under protocol_B.

SCORE SCALE AND COUNTING FLOOR (constraints, re-verified here)
-------------------------------------------------------------
Raw, undivided cosine-sum score scale.  No k_fft alignment is applied
(KN-FIND-014's k_fft=3 asymmetry would shift every point silently if
mishandled).  Each survival file is an unsmoothed pooled counting estimate over
nb_iteration * q^k_fft candidate scores; its support ends at exactly
1/(nb_iteration * q^k_fft) (2^-35.70445229 for n=43).  Values below that are
ABSENCE OF MEASUREMENT.  Nothing here is fitted, anchored, compared or
extrapolated past the last positive score.
"""

import hashlib
import json
import math
import os
import platform
import sys
import time
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..",
                                    ".."))
DATA = os.path.join(REPO, "experiments", "EXP-MLKEM-011", "vendor-lock", "data")

FILES = [
    "Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out",
    "Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out",
]

# BATCH-009 archived headline values (TASK-20260802-8bae8e/comparison_results.json)
# used ONLY as cross-check targets; nothing here is fitted to them.
B009 = {
    FILES[0]: {"log2_K_fit": -72.71258147256952, "p": 26.0,
               "rms_whole_band": 0.7057596314055684,
               "peak_score": 471, "peak_delta_bits": 1.5160635188287852},
    FILES[1]: {"log2_K_fit": -67.22250543726885, "p": 24.5,
               "rms_whole_band": 0.6967212651864578,
               "peak_score": 420, "peak_delta_bits": 1.7103938077827952},
}

# Exponent grid: archived p +/- P_HALFWIDTH in steps of P_STEP.
P_HALFWIDTH = 6.0
P_STEP = 0.25

# Quadrature / sweep controls
GL_ORDER = 6            # Gauss-Legendre order per panel
N_LIN_PANELS = 20       # uniform panels on [0, V_SPLIT]
V_SPLIT = 1.5
N_LOG_PANELS = 600      # geometric panels on [V_SPLIT, V_MAX]
V_MAX_SWEEP = 40.0      # top of the v* (i.e. K) scan
N_REFINE = 200          # sub-panels inside the winning bracket


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def read_out(path):
    header, values, raw = {}, [], []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                raw.append(s)
                body = s.lstrip("#").strip()
                if "=" in body and " " not in body.split("=")[0]:
                    k, v = body.split("=", 1)
                    header[k.strip()] = v.strip()
                continue
            values.append(float(s))
    return header, values, raw


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Gauss-Legendre nodes (numpy/scipy are not installed in this environment)
# ---------------------------------------------------------------------------
def gauss_legendre(n):
    nodes, weights = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        dp = 1.0
        for _ in range(100):
            p0, p1 = 1.0, 0.0
            for j in range(1, n + 1):
                p2 = p1
                p1 = p0
                p0 = ((2.0 * j - 1.0) * x * p1 - (j - 1.0) * p2) / j
            dp = n * (x * p0 - p1) / (x * x - 1.0)
            dx = -p0 / dp
            x += dx
            if abs(dx) < 1e-16:
                break
        nodes.append(x)
        weights.append(2.0 / ((1.0 - x * x) * dp * dp))
    return nodes, weights


GX, GW = gauss_legendre(GL_ORDER)


def panel_edges(v_max, n_log, v_split=V_SPLIT, n_lin=N_LIN_PANELS):
    """Increasing panel right-edges: uniform on [0, v_split], then geometric."""
    out = [v_split * (i + 1) / n_lin for i in range(n_lin)]
    r = (v_max / v_split) ** (1.0 / n_log)
    v = v_split
    for _ in range(n_log):
        v *= r
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# Core: incremental accumulation of J(T, v*) = INT_0^{v*} N e^{-v} v^p
#                                                     phi(T - N e^{-v}) dv
# ---------------------------------------------------------------------------
def accumulate(J, v_lo, v_hi, p, N, band, norm):
    """Add the [v_lo, v_hi] panel contribution to J (in place)."""
    half = (v_hi - v_lo) / 2.0
    mid = (v_hi + v_lo) / 2.0
    for x, w in zip(GX, GW):
        v = mid + half * x
        e = math.exp(-v)
        u = N * e
        c = w * half * N * e * (v ** p) * norm
        if c == 0.0:
            continue
        for i in range(len(band)):
            d = band[i] - u
            z = d * d / N
            if z < 700.0:
                J[i] += c * math.exp(-z)


def predict_from_J(T, Ji, K, ustar, N, sqN, qT):
    """Q(T) + closed-form clipped part + K * J(T, v*)."""
    clip = 0.5 * (math.erfc((T - ustar) / sqN) - math.erfc(T / sqN))
    return qT + clip + K * Ji, clip


# ---------------------------------------------------------------------------
# One (file, p): sweep v*, fit K under both protocols, report rms
# ---------------------------------------------------------------------------
def fit_one_p(p, N, band, log2meas, qs, sub_idx, ge10_idx, log):
    sqN = math.sqrt(N)
    norm = 1.0 / math.sqrt(math.pi * N)
    nT = len(band)
    edges = panel_edges(V_MAX_SWEEP, N_LOG_PANELS)

    J = [0.0] * nT
    snaps = []          # (v*, copy of J) for the refinement pass
    prev = 0.0
    coarse = []
    for vs in edges:
        accumulate(J, prev, vs, p, N, band, norm)
        prev = vs
        snaps.append((vs, array("d", J)))
        K = vs ** (-p)
        ustar = N * math.exp(-vs)
        sse_full = 0.0
        sse_sub = 0.0
        ok = True
        for i in range(nT):
            pr, _ = predict_from_J(band[i], J[i], K, ustar, N, sqN, qs[i])
            if pr <= 0.0:
                ok = False
                break
            r = math.log2(pr) - log2meas[i]
            sse_full += r * r
        if not ok:
            coarse.append(None)
            continue
        for i in sub_idx:
            pr, _ = predict_from_J(band[i], J[i], K, ustar, N, sqN, qs[i])
            r = math.log2(pr) - log2meas[i]
            sse_sub += r * r
        coarse.append((vs, sse_full, sse_sub))

    valid = [(k, c) for k, c in enumerate(coarse) if c is not None]
    if not valid:
        raise RuntimeError("no admissible K on the v* sweep for p=%.4f" % p)
    kA = min(valid, key=lambda kc: kc[1][1])[0]
    kB = min(valid, key=lambda kc: kc[1][2])[0]

    # ---- refinement pass over the union bracket --------------------------
    lo_idx = max(0, min(kA, kB) - 1)
    hi_idx = min(len(edges) - 1, max(kA, kB) + 1)
    v_lo = snaps[lo_idx][0]
    v_hi = snaps[hi_idx][0]
    Jr = list(snaps[lo_idx][1])
    prev = v_lo
    best_A = None
    best_B = None
    for j in range(1, N_REFINE + 1):
        vs = v_lo + (v_hi - v_lo) * j / N_REFINE
        accumulate(Jr, prev, vs, p, N, band, norm)
        prev = vs
        K = vs ** (-p)
        ustar = N * math.exp(-vs)
        sse_full = 0.0
        sse_sub = 0.0
        bad = False
        for i in range(nT):
            pr, _ = predict_from_J(band[i], Jr[i], K, ustar, N, sqN, qs[i])
            if pr <= 0.0:
                bad = True
                break
            r = math.log2(pr) - log2meas[i]
            sse_full += r * r
        if bad:
            continue
        for i in sub_idx:
            pr, _ = predict_from_J(band[i], Jr[i], K, ustar, N, sqN, qs[i])
            r = math.log2(pr) - log2meas[i]
            sse_sub += r * r
        if best_A is None or sse_full < best_A[1]:
            best_A = (vs, sse_full, array("d", Jr))
        if best_B is None or sse_sub < best_B[2]:
            best_B = (vs, sse_full, sse_sub)

    def summarise(vs, Jarr):
        K = vs ** (-p)
        ustar = N * math.exp(-vs)
        s_full = 0.0
        s_ge10 = 0.0
        mn, mx, tot = float("inf"), float("-inf"), 0.0
        for i in range(nT):
            pr, _ = predict_from_J(band[i], Jarr[i], K, ustar, N, sqN, qs[i])
            r = math.log2(pr) - log2meas[i]
            s_full += r * r
            tot += r
            mn = min(mn, r)
            mx = max(mx, r)
        for i in ge10_idx:
            pr, _ = predict_from_J(band[i], Jarr[i], K, ustar, N, sqN, qs[i])
            r = math.log2(pr) - log2meas[i]
            s_ge10 += r * r
        return {
            "log2_K": -p * math.log2(vs),
            "v_star": vs,
            "rms_whole_band_bits": math.sqrt(s_full / nT),
            "rms_count_ge10_subband_bits": math.sqrt(s_ge10 / len(ge10_idx)),
            "mean_residual_bits": tot / nT,
            "min_residual_bits": mn,
            "max_residual_bits": mx,
        }

    resA = summarise(best_A[0], best_A[2])

    # protocol B needs its own J at its own v*: recompute by a short walk
    JB = list(snaps[lo_idx][1])
    prev = v_lo
    steps = int(round((best_B[0] - v_lo) / ((v_hi - v_lo) / N_REFINE)))
    for j in range(1, max(1, steps) + 1):
        vs = v_lo + (v_hi - v_lo) * j / N_REFINE
        accumulate(JB, prev, vs, p, N, band, norm)
        prev = vs
    resB = summarise(prev, JB)

    return {"p": p, "protocol_A_fit_whole_band": resA,
            "protocol_B_fit_subsample20": resB}


# ---------------------------------------------------------------------------
# Reproduction cross-check at the archived (p, K_fit)
# ---------------------------------------------------------------------------
def cross_check(fname, N, band, values, log2meas, qs, log):
    p = B009[fname]["p"]
    K = 2.0 ** B009[fname]["log2_K_fit"]
    vstar = K ** (-1.0 / p)
    sqN = math.sqrt(N)
    norm = 1.0 / math.sqrt(math.pi * N)
    nT = len(band)

    edges = [v for v in panel_edges(V_MAX_SWEEP, N_LOG_PANELS) if v < vstar]
    edges.append(vstar)
    J = [0.0] * nT
    prev = 0.0
    for vs in edges:
        accumulate(J, prev, vs, p, N, band, norm)
        prev = vs
    ustar = N * math.exp(-vstar)

    # finer layout, for a quadrature-convergence statement
    edges_f = [v for v in panel_edges(V_MAX_SWEEP, 2 * N_LOG_PANELS,
                                      n_lin=2 * N_LIN_PANELS) if v < vstar]
    edges_f.append(vstar)
    Jf = [0.0] * nT
    prev = 0.0
    for vs in edges_f:
        accumulate(Jf, prev, vs, p, N, band, norm)
        prev = vs

    rows = []
    sse = 0.0
    maxconv = 0.0
    for i in range(nT):
        pr, clip = predict_from_J(band[i], J[i], K, ustar, N, sqN, qs[i])
        prf, _ = predict_from_J(band[i], Jf[i], K, ustar, N, sqN, qs[i])
        r = math.log2(pr) - log2meas[i]
        sse += r * r
        maxconv = max(maxconv, abs(math.log2(pr) - math.log2(prf)))
        rows.append((band[i], math.log2(pr), r, clip / pr))
    peak = max(rows, key=lambda t: t[2])
    pk = B009[fname]["peak_score"]

    # K -> infinity closed-form self-check of the quadrature machinery:
    # with p = 0 and K -> inf the integrand collapses to N e^{-v} phi(T-Ne^{-v}),
    # whose exact integral over v in (0, inf) is INT_0^N phi(T-u) du.
    selfcheck = []
    for T in (0, 200, 900, 1500, band[-1]):
        acc = [0.0]
        prev = 0.0
        for vs in panel_edges(120.0, N_LOG_PANELS):
            accumulate(acc, prev, vs, 0.0, N, [T], norm)
            prev = vs
        exact = 0.5 * (math.erfc((T - N) / sqN) - math.erfc(T / sqN))
        selfcheck.append({"T": T, "quadrature": acc[0], "closed_form": exact,
                          "rel_error": abs(acc[0] - exact) / exact
                          if exact > 0 else None})

    out = {
        "purpose": ("reproduce the BATCH-009 headline comparison at the "
                    "archived (p, log2 K_fit) with the exact-kink clip "
                    "treatment, so the departure DEP-A1 is quantified"),
        "archived_log2_K_fit": B009[fname]["log2_K_fit"],
        "archived_exponent_p": p,
        "rms_whole_band_bits_here": math.sqrt(sse / nT),
        "rms_whole_band_bits_archived_BATCH009": B009[fname]["rms_whole_band"],
        "peak_score_here": peak[0],
        "peak_delta_bits_here": peak[2],
        "peak_score_archived": pk,
        "delta_bits_here_at_archived_peak_score": rows[pk][2],
        "peak_delta_bits_archived_BATCH009": B009[fname]["peak_delta_bits"],
        "clipped_fraction_here_at_archived_peak_score": rows[pk][3],
        "quadrature_convergence_max_abs_log2_diff_coarse_vs_fine_bits": maxconv,
        "quadrature_self_check_K_to_infinity": selfcheck,
        "note": ("Differences against the archived numbers are the DEP-A1 clip "
                 "treatment, not a different model.  The BATCH-009 validator "
                 "(TASK-20260803-bc8c1f) independently recomputed the same "
                 "quantities with the same exact-kink treatment and reported "
                 "max disagreement 0.00066 bits against the producer."),
    }
    log("  cross-check at archived (p=%.1f, log2K=%.6f): whole-band rms %.6f "
        "here vs %.6f archived; delta at score %d = %+.6f here vs %+.6f "
        "archived; coarse-vs-fine quadrature <= %.2e bits"
        % (p, B009[fname]["log2_K_fit"], out["rms_whole_band_bits_here"],
           B009[fname]["rms_whole_band"], pk,
           out["delta_bits_here_at_archived_peak_score"],
           B009[fname]["peak_delta_bits"], maxconv))
    return out


# ---------------------------------------------------------------------------
# One file
# ---------------------------------------------------------------------------
def analyse(fname, log):
    path = os.path.join(DATA, fname)
    header, values, raw = read_out(path)

    q = int(header["q"])
    k_fft = int(header["k_fft"])
    n_fft = int(header["n_fft"])
    beta_sieve = int(header["beta_1"])
    N = float(header["avg_N"])
    nb_iteration = int(header["nb_iteration"])

    floor = 1.0 / (nb_iteration * (q ** k_fft))
    last_pos = max(i for i, v in enumerate(values) if v > 0.0)
    band = list(range(last_pos + 1))
    counts = [int(round(values[T] / floor)) for T in band]
    log2meas = [math.log2(values[T]) for T in band]
    sqN = math.sqrt(N)
    qs = [0.5 * math.erfc(T / sqN) for T in band]

    sub_idx = list(range(0, len(band), 20))
    if (len(band) - 1) not in sub_idx:
        sub_idx.append(len(band) - 1)
    ge10_idx = [i for i in range(len(band)) if counts[i] >= 10]

    p_own = (beta_sieve + n_fft) / 2.0

    log("[%s]" % fname)
    log("  counting floor = %.17g = 2^%.8f ; resolved band = scores [0, %d] ;"
        " first zero at %d" % (floor, math.log2(floor), last_pos, last_pos + 1))
    log("  own Approximation-4.9 exponent p = (beta_sieve + n_fft)/2 = "
        "(%d + %d)/2 = %.2f" % (beta_sieve, n_fft, p_own))
    log("  fit sets: whole band n=%d ; band[::20]+last n=%d ; count>=10 n=%d"
        % (len(band), len(sub_idx), len(ge10_idx)))

    xcheck = cross_check(fname, N, band, values, log2meas, qs, log)

    n_half = int(round(P_HALFWIDTH / P_STEP))
    p_grid = [round(p_own + k * P_STEP, 4) for k in range(-n_half, n_half + 1)]
    p_grid = [x for x in p_grid if x > 0.0]

    curve = []
    t0 = time.time()
    for pp in p_grid:
        r = fit_one_p(pp, N, band, log2meas, qs, sub_idx, ge10_idx, log)
        curve.append(r)
        log("    p=%6.2f  A: log2K=%11.5f rms=%.6f | B: log2K=%11.5f "
            "rms=%.6f%s"
            % (pp, r["protocol_A_fit_whole_band"]["log2_K"],
               r["protocol_A_fit_whole_band"]["rms_whole_band_bits"],
               r["protocol_B_fit_subsample20"]["log2_K"],
               r["protocol_B_fit_subsample20"]["rms_whole_band_bits"],
               "   <-- file's OWN archived exponent"
               if abs(pp - p_own) < 1e-9 else ""))
    log("  exponent scan: %d values of p in %.1f s"
        % (len(curve), time.time() - t0))

    def argmin(key):
        best = min(curve, key=lambda r: r[key]["rms_whole_band_bits"])
        i = curve.index(best)
        return {
            "p_argmin": best["p"],
            "rms_whole_band_bits_at_argmin":
                best[key]["rms_whole_band_bits"],
            "log2_K_at_argmin": best[key]["log2_K"],
            "at_grid_boundary": i == 0 or i == len(curve) - 1,
        }

    def at_p(target, key):
        for r in curve:
            if abs(r["p"] - target) < 1e-9:
                return {"p": r["p"],
                        "rms_whole_band_bits": r[key]["rms_whole_band_bits"],
                        "log2_K": r[key]["log2_K"]}
        return None

    other_p = 24.5 if abs(p_own - 26.0) < 1e-9 else 26.0
    verdictless = {}
    for key, lab in (("protocol_A_fit_whole_band", "protocol_A"),
                     ("protocol_B_fit_subsample20", "protocol_B")):
        am = argmin(key)
        own = at_p(p_own, key)
        oth = at_p(other_p, key)
        verdictless[lab] = {
            "argmin": am,
            "at_own_archived_exponent": own,
            "at_other_files_archived_exponent": oth,
            "own_exponent_is_argmin": abs(am["p_argmin"] - p_own) < 1e-9,
            "rms_excess_of_own_exponent_over_argmin_bits":
                own["rms_whole_band_bits"] - am["rms_whole_band_bits_at_argmin"],
            "rms_difference_own_minus_other_file_exponent_bits":
                (own["rms_whole_band_bits"] - oth["rms_whole_band_bits"])
                if oth else None,
        }
        log("  %s: argmin of rms over p is p=%.2f (rms %.6f); file's own "
            "p=%.2f gives rms %.6f (excess %+.6f bits); other file's p=%.2f "
            "gives rms %s ; own exponent is argmin: %s ; argmin at grid "
            "boundary: %s"
            % (lab, am["p_argmin"], am["rms_whole_band_bits_at_argmin"],
               p_own, own["rms_whole_band_bits"],
               verdictless[lab]["rms_excess_of_own_exponent_over_argmin_bits"],
               other_p,
               ("%.6f" % oth["rms_whole_band_bits"]) if oth else "n/a",
               verdictless[lab]["own_exponent_is_argmin"],
               am["at_grid_boundary"]))

    return {
        "file": fname,
        "file_sha256": sha256(path),
        "file_path_repo_relative": os.path.relpath(path, REPO),
        "header_raw": raw,
        "parameters_used": {
            "q": q, "k_fft": k_fft, "n_fft": n_fft,
            "beta_sieve_from_header_beta_1": beta_sieve,
            "avg_N": N, "nb_iteration": nb_iteration,
            "own_exponent_p": p_own,
            "exponent_p_source": ("(beta_sieve + n_fft)/2, beta_sieve from the "
                                  ".out header beta_1, n_fft from the header; "
                                  "Fig 4.1 caption agrees"),
        },
        "instrument": {
            "counting_floor": floor,
            "counting_floor_log2": math.log2(floor),
            "resolved_band_scores": [0, last_pos],
            "first_zero_score": last_pos + 1,
            "n_scores_in_band": len(band),
            "n_scores_with_pooled_count_ge_10": len(ge10_idx),
            "note": ("Scores above %d carry a printed 0.0, which is absence of "
                     "measurement, not a measured zero.  Nothing here is "
                     "fitted, anchored, compared or extrapolated past score %d."
                     % (last_pos, last_pos)),
        },
        "score_scale_convention": ("raw undivided cosine-sum scale; no k_fft "
                                   "alignment applied (same as BATCH-009)"),
        "reproduction_cross_check": xcheck,
        "scan_settings": {
            "p_grid": [c["p"] for c in curve],
            "p_halfwidth": P_HALFWIDTH, "p_step": P_STEP,
            "gl_order": GL_ORDER, "n_lin_panels": N_LIN_PANELS,
            "v_split": V_SPLIT, "n_log_panels": N_LOG_PANELS,
            "v_max_sweep": V_MAX_SWEEP, "n_refine": N_REFINE,
            "fit_set_protocol_A": "whole resolved band",
            "fit_set_protocol_B": "band[::20] + last score (BATCH-009 headline)",
            "rms_reported_over": "whole resolved band (both protocols)",
        },
        "rms_vs_p_curve": curve,
        "argmin_report": verdictless,
    }


# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    log("exponent_neighbourhood_scan.py -- CHECK A -- TASK-20260803-f95b4e, "
        "BATCH-010, GOAL-MLKEM-003")
    log("python %s on %s" % (sys.version.split()[0], platform.platform()))
    log("numpy available: %s ; scipy available: %s"
        % (_have("numpy"), _have("scipy")))
    log("")

    results = [analyse(f, log) for f in FILES]

    out = {
        "check": "A -- exponent-neighbourhood control",
        "task_id": "TASK-20260803-f95b4e",
        "batch_id": "BATCH-010",
        "goal_id": "GOAL-MLKEM-003",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(t_start)),
        "environment": {"python": sys.version,
                        "platform": platform.platform(),
                        "numpy": _have("numpy"), "scipy": _have("scipy")},
        "non_claims": [
            "No ML-KEM or Kyber security claim in either direction; no cost-"
            "model revision; no record status changed.",
            "Toy parameters only (q=241, m=40, n=43/50).",
            "AGENTS.md rule 12 remains UNMET and UNWAIVED; EV-MLKEM-011, "
            "EV-MLKEM-013 and EV-MLKEM-017 keep their status.",
            "This script records rms-vs-p curves and argmins.  It does NOT "
            "conclude that Approximation 4.9 is validated, refuted, selected "
            "or rejected.",
            "The normalisation K is fitted to the very data being compared, at "
            "every p.  This is a shape comparison with one free scale, not an "
            "absolute-level test.",
        ],
        "zero_new_sampling": True,
        "files": results,
        "stdout_log": lines,
    }
    out["wall_clock_seconds"] = time.time() - t_start

    # Deliverable discipline: this task declares exactly four artifact paths, so
    # both checks write into the SAME results.json under their own key.  An
    # existing check_B block is preserved verbatim.
    dest = os.path.join(HERE, "results.json")
    doc = {}
    if os.path.exists(dest):
        with open(dest) as fh:
            doc = json.load(fh)
    doc["task_id"] = "TASK-20260803-f95b4e"
    doc["batch_id"] = "BATCH-010"
    doc["goal_id"] = "GOAL-MLKEM-003"
    doc["check_A_exponent_neighbourhood"] = out
    with open(dest, "w") as fh:
        json.dump(doc, fh, indent=1, allow_nan=True)
    log("")
    log("wrote check_A_exponent_neighbourhood into %s (%.1f kB) in %.1f s"
        % (dest, os.path.getsize(dest) / 1024.0, out["wall_clock_seconds"]))


def _have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()

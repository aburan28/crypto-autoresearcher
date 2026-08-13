#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECK B -- JENSEN BIAS BOUND ON THE COLLAPSED d_lsc INTEGRAL
TASK-20260803-f95b4e, BATCH-010 of GOAL-MLKEM-003.

THE DEFECT BEING QUANTIFIED (validator defect D5, TASK-20260803-bc8c1f)
----------------------------------------------------------------------
Archived Approximation 4.9, equation (4.22)
(inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/
 page23_approx_4_8_4_9.txt), places the d_lsc integral OUTSIDE the min and the
region integral INSIDE it:

    Pwrong(T) ~= INT_{-inf}^{+inf} INT_0^{+inf}
                   min( 1, INT_{E(T-t)} lambda(x) mu(y) d(x,y) )
                   * exp(-t^2/N - (d_lsc-mu_lsc)^2/(2 sigma_lsc^2))
                   / (pi sigma_lsc sqrt(2N))  dd_lsc dt          (4.22)

and E(T-t) depends on d_lsc through Phi_{d_lsc} (4.23).  The archived
justification on page25 states the same order explicitly:

    P(D > T | d_lsc) ~= min(1, E[ sum_{(i,j) in E(T)} N_{i,j} ])       (4.28)
    P(D > T)          = INT psi_lsc(d_lsc) P(D > T | d_lsc) dd_lsc

i.e. the conditional min is taken FIRST and averaged over d_lsc SECOND.

The BATCH-009 script (TASK-20260802-8bae8e, approx49_comparison.py, STEP 3)
computes instead

    min(1, Kbar * L^p),          L = ln(N/u),  p = (beta_sieve+n_fft)/2,

i.e. it collapses the d_lsc average INSIDE the min into a single effective
scale Kbar and then clips once.  Because x -> min(1,x) is CONCAVE, Jensen's
inequality gives

    E_d[ min(1, k(d) L^p) ]  <=  min(1, E_d[k(d)] L^p) = min(1, Kbar L^p),

so the collapsed form is an UPPER BOUND on (4.22) and the bias has the SAME
SIGN as the reported over-predictions (+1.5154 bits at score 471 for n=43,
+1.7109 bits at score 420 for n=50; validator's recomputed values).  Those two
peaks sit at clipped fractions ~0.36 / ~0.38, i.e. exactly where the collapse
is least valid.

WHAT THIS SCRIPT COMPUTES
-------------------------
At the two headline peak scores it evaluates the integral in the position
(4.22) actually specifies and reports the MAGNITUDE and SIGN of

    Delta(T) = log2 P_in(T) - log2 P_out(T)                (bits)

    P_out(T) = Q(T) + INT N e^{-v} phi(T - N e^{-v}) min(1, Kbar v^p) dv
    P_in(T)  = Q(T) + INT N e^{-v} phi(T - N e^{-v}) W(v) dv
    W(v)     = E_{d_lsc} [ min(1, k(d_lsc) v^p) ] ,   E_{d_lsc}[k] = Kbar

with L = v = ln(N/u), Q(T) = 0.5 erfc(T/sqrt(N)), phi(s) = e^{-s^2/N}/sqrt(pi N).

*** THIS IS A BIAS BOUND, NOT A RE-FIT. ***
Kbar is held FIXED at the archived BATCH-009 fitted value log2 Kbar =
-72.71258147256952 (n=43) / -67.22250543726885 (n=50), and every reading of
k(d_lsc) below satisfies E_{d_lsc}[k(d_lsc)] = Kbar EXACTLY, so P_out is
literally unchanged and Delta isolates the position of min(1,.) alone.  K is
not re-optimised anywhere in this script.

WHAT PINS THE MAGNITUDE, AND WHAT DOES NOT
------------------------------------------
Concavity pins the SIGN (Delta <= 0) but NOT the magnitude: for a fixed mean
Kbar L^p, E[min(1,Z)] can be pushed arbitrarily close to 0 by a sufficiently
dispersed Z.  What DOES bound the magnitude, reading-free, is that the
D-component of Model 4.7 is non-negative, so P_in(T) >= Q(T) and hence

    log2 Q(T) - log2 P_out(T)  <=  Delta(T)  <=  0.                (BOUND)

Both ends are computed and reported.  Between them the magnitude depends on how
d_lsc enters Phi, which NO archived extract states (Phi_{d_lsc} is introduced
with Approximation 4.6, on a page that was not retrieved; recorded UNAVAILABLE
in the BATCH-009 parameter ledger).  Two DECLARED readings are therefore
scanned, and the required dispersion is solved for.

READING R1 (primary; reading-agnostic one-parameter dispersion family)
    k(d_lsc) = Kbar * exp(s*z - s^2/2),   z = (d_lsc - mu_lsc)/sigma_lsc,
    z ~ N(0,1) under psi_lsc, so E[k] = Kbar exactly and s = sd(ln k) is the
    only parameter.  The inner expectation is then available in CLOSED FORM:
      W(v) = C * Phi_std(z_c - s) + 1 - Phi_std(z_c),
      C    = Kbar v^p,   z_c = (-ln C + s^2/2)/s,
    and W -> min(1,C) as s -> 0, so s=0 reproduces the BATCH-009 collapse
    exactly (used as a self-check).  R1 says nothing about WHY k varies with
    d_lsc; it parametrises HOW MUCH, which is the quantity the bias depends on.

READING R2 (secondary; the shift reading the archived (4.19) points to)
    Archived (4.19) evaluates the good-guess threshold as a product of
    INT psi_lsc(d) e^{-a d^2} dd and E[e^{-a d_lat^2 t^2}] with a = alpha pi^2/q^2,
    i.e. Phi contributes e^{-a d_lsc^2} on the lsc side when the guess is
    correct.  Extending that to the wrong guess by treating the wrong-guess FFT
    offset y as an extra orthogonal lsc-side component gives the DECLARED
    reading
        Phi_{d}(x,y) = exp( -a (x^2 + y^2 + d^2) ),
    under which N Phi >= u becomes a(x^2+y^2) <= L - a d^2 and
        INT_{E(u)} lambda mu = K_0 * (L - a d^2)_+^p .
    NOTE this is a SHIFT of L, not a pure scale, so it differs from the
    multiplicative "b(d_lsc)" form written in the BATCH-009 script's STEP 2,
    which at y=0 does NOT reproduce (4.19)'s e^{-a d_lsc^2} factor.  That
    discrepancy is recorded as an observation, not resolved.
    To keep Kbar FIXED (the task's constraint) the reading is mean-matched at
    every L:
        A(d, v) = Kbar v^p * (v - a d^2)_+^p / M(v),
        M(v)    = E_d[(v - a d^2)_+^p],      so E_d[A(d,v)] = Kbar v^p exactly,
        W(v)    = E_d[ min(1, A(d,v)) ].
    Consequently R2 as implemented isolates ONLY the position of min(1,.); the
    additional SHAPE change that the shift reading would also make to the
    unclipped level is deliberately normalised away, because absorbing it would
    require re-fitting K, which this task forbids.
    R2's parameter is a; it is reported through the dimensionless a*mu_lsc^2 =
    alpha (pi mu_lsc / q)^2.  *** alpha is UNAVAILABLE in every archived page
    extract of the paper. ***  The archived Pgood .out header carries
    alpha_secret = alpha_error = 2, but identifying those with the paper's alpha
    is NOT established by any archived text, so no value is adopted: a*mu_lsc^2
    is SCANNED, and the value that alpha = 2 would give is merely marked.

CONSTRAINTS HONOURED
--------------------
ZERO NEW SAMPLING: no lattice computation, no G6K call, no network, no new
simulation.  Raw undivided cosine-sum score scale, no k_fft alignment.
Nothing is fitted, anchored, compared or extrapolated past the last positive
score of each file (the counting floor 1/(nb_iteration*q^k_fft)).
Toy parameters (q=241, m=40, n=43/50); NO ML-KEM or Kyber security claim in
either direction; no record status changed; AGENTS.md rule 12 remains UNMET
and UNWAIVED.

This script records magnitudes, signs and bounds.  It does NOT conclude that
Approximation 4.9 is validated, refuted, selected or rejected, and it does not
decide whether the over-prediction "is" the collapse; it reports what the
correction is worth as a function of the one quantity the archive does not fix.
"""

import hashlib
import json
import math
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..",
                                    ".."))
DATA = os.path.join(REPO, "experiments", "EXP-MLKEM-011", "vendor-lock", "data")

CASES = [
    {"file": "Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out",
     "peak_score": 471,
     "log2_K_fit_BATCH009": -72.71258147256952,
     "p_BATCH009": 26.0,
     "peak_delta_bits_producer": 1.5160635188287852,
     "peak_delta_bits_validator": 1.5154,
     "clipped_fraction_producer": 0.3611528289293749},
    {"file": "Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out",
     "peak_score": 420,
     "log2_K_fit_BATCH009": -67.22250543726885,
     "p_BATCH009": 24.5,
     "peak_delta_bits_producer": 1.7103938077827952,
     "peak_delta_bits_validator": 1.7109,
     "clipped_fraction_producer": 0.38079881543506655},
]

S_SCAN = [0.0, 0.05, 0.1, 0.2, 0.3, 0.375, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0,
          4.0, 4.5, 5.0, 6.0, 8.0, 12.0, 20.0, 40.0]
# a*mu_lsc^2 grid.  0.0 is the degenerate self-check (must reproduce the
# collapsed model); the alpha=2 equivalent is inserted per file at run time.
AMU2_SCAN = [0.0, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

GL_ORDER = 8
N_LIN_PANELS = 20
V_SPLIT = 1.5
N_LOG_PANELS = 700
V_MAX = 120.0
Z_LIM = 8.0            # d_lsc range in standard deviations
Z_SUB = 6              # sub-panels per breakpoint segment (R2)
# Nodes of the outer v-quadrature whose maximum possible contribution (W <= 1)
# is below NODE_TOL * P_out are skipped in the R2 scan only; the total dropped
# mass is computed and reported so the truncation is bounded, not assumed.
NODE_TOL = 1e-18
SQRT2 = math.sqrt(2.0)


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


def phi_std(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def Phi_std(z):
    return 0.5 * math.erfc(-z / SQRT2)


def panel_edges(v_max, n_log, v_split=V_SPLIT, n_lin=N_LIN_PANELS,
                extra=()):
    out = [v_split * (i + 1) / n_lin for i in range(n_lin)]
    r = (v_max / v_split) ** (1.0 / n_log)
    v = v_split
    for _ in range(n_log):
        v *= r
        out.append(v)
    for e in extra:
        if 0.0 < e < v_max:
            out.append(e)
    out.sort()
    return out


# ---------------------------------------------------------------------------
# Outer v-quadrature nodes, shared by every reading
# ---------------------------------------------------------------------------
def v_nodes(N, extra):
    """[(v, u, base)] with base = weight * N e^{-v} (the du/dv Jacobian)."""
    out = []
    prev = 0.0
    for vs in panel_edges(V_MAX, N_LOG_PANELS, extra=extra):
        half = (vs - prev) / 2.0
        mid = (vs + prev) / 2.0
        for x, w in zip(GX, GW):
            v = mid + half * x
            e = math.exp(-v)
            out.append((v, N * e, w * half * N * e))
        prev = vs
    return out


def integrate(T, N, nodes, Wvals, norm):
    """Q(T) + INT base * W(v) * phi(T-u) dv, plus the clipped-mass share."""
    tot = 0.0
    for (v, u, base), W in zip(nodes, Wvals):
        if W == 0.0:
            continue
        d = T - u
        z = d * d / N
        if z >= 700.0:
            continue
        tot += base * W * norm * math.exp(-z)
    return 0.5 * math.erfc(T / math.sqrt(N)) + tot, tot


# ---------------------------------------------------------------------------
# P_out: the BATCH-009 collapsed model, exact kink split (identical treatment
# to Check A / the BATCH-009 validator's independent recomputation)
# ---------------------------------------------------------------------------
def p_out_exact(T, Kbar, p, N):
    vstar = Kbar ** (-1.0 / p)
    ustar = N * math.exp(-vstar)
    sqN = math.sqrt(N)
    norm = 1.0 / math.sqrt(math.pi * N)
    J = 0.0
    prev = 0.0
    for vs in panel_edges(vstar, N_LOG_PANELS):
        if vs > vstar:
            vs = vstar
        half = (vs - prev) / 2.0
        mid = (vs + prev) / 2.0
        for x, w in zip(GX, GW):
            v = mid + half * x
            e = math.exp(-v)
            u = N * e
            d = T - u
            z = d * d / N
            if z < 700.0:
                J += w * half * N * e * (v ** p) * norm * math.exp(-z)
        prev = vs
        if prev >= vstar:
            break
    clip = 0.5 * (math.erfc((T - ustar) / sqN) - math.erfc(T / sqN))
    q = 0.5 * math.erfc(T / sqN)
    pred = q + clip + Kbar * J
    return {"pred": pred, "log2_pred": math.log2(pred), "Q": q,
            "log2_Q": math.log2(q), "clipped_fraction": clip / pred,
            "v_star": vstar, "u_star": ustar}


# ---------------------------------------------------------------------------
# Reading R1: W(v) in closed form
# ---------------------------------------------------------------------------
def W_R1(v, Kbar, p, s):
    C = Kbar * (v ** p)
    if s <= 0.0:
        return 1.0 if C >= 1.0 else C
    if C <= 0.0:
        return 0.0
    z_c = (-math.log(C) + 0.5 * s * s) / s
    tail = 1.0 - Phi_std(z_c)
    lead = Phi_std(z_c - s)
    return C * lead + tail


# ---------------------------------------------------------------------------
# Reading R2: W(v) by quadrature over d_lsc, with breakpoints located exactly
# ---------------------------------------------------------------------------
def _z_segments(mu, sg, a, v, extra_level=None):
    """Breakpoints in z for (v - a d^2)_+ and for the clip level."""
    br = [-Z_LIM, Z_LIM]
    if a > 0.0:
        dr = math.sqrt(v / a)
        for d in (-dr, dr):
            z = (d - mu) / sg
            if -Z_LIM < z < Z_LIM:
                br.append(z)
        if extra_level is not None and 0.0 <= extra_level <= v:
            d2 = (v - extra_level) / a
            if d2 >= 0.0:
                dc = math.sqrt(d2)
                for d in (-dc, dc):
                    z = (d - mu) / sg
                    if -Z_LIM < z < Z_LIM:
                        br.append(z)
    br = sorted(set(br))
    return br


def _quad_z(f, br):
    tot = 0.0
    for i in range(len(br) - 1):
        lo, hi = br[i], br[i + 1]
        if hi <= lo:
            continue
        step = (hi - lo) / Z_SUB
        for k in range(Z_SUB):
            a0 = lo + k * step
            half = step / 2.0
            mid = a0 + half
            for x, w in zip(GX, GW):
                z = mid + half * x
                tot += w * half * f(z)
    return tot


def W_R2(v, Kbar, p, a, mu, sg):
    if a <= 0.0:
        C = Kbar * (v ** p)
        return (1.0 if C >= 1.0 else C), None
    br = _z_segments(mu, sg, a, v)

    def g(z):
        d = mu + sg * z
        r = v - a * d * d
        if r <= 0.0:
            return 0.0
        return (r ** p) * phi_std(z)

    M = _quad_z(g, br)
    if M <= 0.0:
        return 0.0, None
    Kv = Kbar * (v ** p)
    # clip level: Kv * r^p / M = 1  <=>  r = (M/Kv)^{1/p}
    lvl = (M / Kv) ** (1.0 / p) if Kv > 0.0 else None
    br2 = _z_segments(mu, sg, a, v, extra_level=lvl)

    def h(z):
        d = mu + sg * z
        r = v - a * d * d
        if r <= 0.0:
            return 0.0
        A = Kv * (r ** p) / M
        return (1.0 if A >= 1.0 else A) * phi_std(z)

    return _quad_z(h, br2), M


# ---------------------------------------------------------------------------
def analyse(case, log):
    fname = case["file"]
    path = os.path.join(DATA, fname)
    header, values, raw = read_out(path)

    q = int(header["q"])
    k_fft = int(header["k_fft"])
    n_fft = int(header["n_fft"])
    beta_sieve = int(header["beta_1"])
    N = float(header["avg_N"])
    mu = float(header["avg_dlsc"])
    sg = float(header["sdv_dlsc"])
    nb_iteration = int(header["nb_iteration"])

    floor = 1.0 / (nb_iteration * (q ** k_fft))
    last_pos = max(i for i, v in enumerate(values) if v > 0.0)

    p = (beta_sieve + n_fft) / 2.0
    assert abs(p - case["p_BATCH009"]) < 1e-12, "exponent mismatch"
    Kbar = 2.0 ** case["log2_K_fit_BATCH009"]
    T = case["peak_score"]
    assert 0 <= T <= last_pos, "peak score outside the resolved band"

    sqN = math.sqrt(N)
    norm = 1.0 / math.sqrt(math.pi * N)
    log2meas = math.log2(values[T])

    log("[%s]  peak score T*=%d" % (fname, T))
    log("  resolved band [0,%d], counting floor 2^%.8f ; T* is inside the band"
        % (last_pos, math.log2(floor)))
    log("  p=%.2f (archived), log2 Kbar = %.14f (archived BATCH-009 fit, HELD "
        "FIXED), N=%.1f, mu_lsc=%.6f, sigma_lsc=%.6f"
        % (p, case["log2_K_fit_BATCH009"], N, mu, sg))

    # ---- baseline ---------------------------------------------------------
    base = p_out_exact(T, Kbar, p, N)
    delta_here = base["log2_pred"] - log2meas
    log("  P_out(T*) [collapsed, exact kink]: log2 = %.9f ; measured log2 = "
        "%.9f ; over-prediction = %+.6f bits (producer archived %+.6f, "
        "validator %+.6f) ; clipped fraction %.6f (producer %.6f)"
        % (base["log2_pred"], log2meas, delta_here,
           case["peak_delta_bits_producer"], case["peak_delta_bits_validator"],
           base["clipped_fraction"], case["clipped_fraction_producer"]))

    bound_lo = base["log2_Q"] - base["log2_pred"]
    log("  reading-free bound on the Jensen difference: %.6f <= Delta <= 0 "
        "bits  (upper end from concavity of min(1,.); lower end from "
        "P_in >= Q(T*), NOT from concavity)" % bound_lo)

    # ---- shared outer quadrature -----------------------------------------
    nodes = v_nodes(N, extra=(base["v_star"],))

    # ---- R1 ---------------------------------------------------------------
    r1 = []
    for s in S_SCAN:
        W = [W_R1(v, Kbar, p, s) for (v, u, b) in nodes]
        pin, _ = integrate(T, N, nodes, W, norm)
        d = math.log2(pin) - base["log2_pred"]
        r1.append({"s_sd_of_ln_k": s, "log2_P_in": math.log2(pin),
                   "delta_bits_vs_collapsed": d,
                   "residual_vs_measured_bits": math.log2(pin) - log2meas})
    self_s0 = r1[0]["delta_bits_vs_collapsed"]
    log("  R1 self-check at s=0 (must reproduce the collapsed model exactly): "
        "Delta = %.3e bits" % self_s0)
    for row in r1:
        log("    R1 s=%6.2f : log2 P_in = %.6f  Delta = %+.6f bits  "
            "residual vs measured = %+.6f bits"
            % (row["s_sd_of_ln_k"], row["log2_P_in"],
               row["delta_bits_vs_collapsed"],
               row["residual_vs_measured_bits"]))

    # ---- s required to absorb the whole over-prediction -------------------
    def delta_of_s(s):
        W = [W_R1(v, Kbar, p, s) for (v, u, b) in nodes]
        pin, _ = integrate(T, N, nodes, W, norm)
        return math.log2(pin) - base["log2_pred"]

    def solve_s(target):
        if target < bound_lo:
            return None
        lo, hi = 0.0, 40.0
        if delta_of_s(hi) > target:
            return None
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if delta_of_s(mid) > target:
                lo = mid
            else:
                hi = mid
            if hi - lo < 1e-6:
                break
        return 0.5 * (lo + hi)

    req = {}
    for lab, val in (("producer", case["peak_delta_bits_producer"]),
                     ("validator", case["peak_delta_bits_validator"]),
                     ("recomputed_here", delta_here)):
        s_req = solve_s(-val)
        req[lab] = {"over_prediction_bits": val,
                    "s_required_sd_of_ln_k": s_req,
                    "reachable_within_reading_free_bound": s_req is not None}
        log("    Delta = -%.6f bits (%s over-prediction) requires R1 "
            "dispersion s = %s"
            % (val, lab, "UNREACHABLE (exceeds the reading-free bound)"
               if s_req is None else "%.6f" % s_req))

    # ---- R2 ---------------------------------------------------------------
    # Node mask: the maximum possible contribution of node i is its weight
    # (since W <= 1).  Nodes below NODE_TOL * P_out are given W = 0 in the R2
    # scan and the total dropped weight is reported as a hard bound.
    wts = []
    for (v, u, b) in nodes:
        d = T - u
        z = d * d / N
        wts.append(0.0 if z >= 700.0 else b * norm * math.exp(-z))
    thr = NODE_TOL * base["pred"]
    keep = [i for i, w in enumerate(wts) if w > thr]
    dropped = sum(w for w in wts if w <= thr)
    log("  R2 node mask: %d of %d outer nodes evaluated; total dropped weight "
        "%.3e = %.3e of P_out(T*) (hard upper bound on the induced error)"
        % (len(keep), len(nodes), dropped, dropped / base["pred"]))

    v_T = math.log(N / T)
    amu2_alpha2 = 2.0 * (math.pi * mu / q) ** 2
    amu2_grid = sorted(set([round(x, 12) for x in AMU2_SCAN]
                           + [round(amu2_alpha2, 12)]))

    # R2 mean-match self-check: E_d[A(d,v)] must equal Kbar v^p exactly, so
    # that P_out is unchanged and Delta isolates the position of min(1,.).
    mm = []
    for vchk in (v_T, 2.0 * v_T, 8.0):
        a_chk0 = amu2_alpha2 / (mu * mu)
        br = _z_segments(mu, sg, a_chk0, vchk)
        Mv = _quad_z(lambda z: (max(0.0, vchk - a_chk0 * (mu + sg * z) ** 2)
                                ** p) * phi_std(z), br)
        EA = _quad_z(lambda z: (Kbar * (vchk ** p)
                                * (max(0.0, vchk - a_chk0 * (mu + sg * z) ** 2)
                                   ** p) / Mv) * phi_std(z), br)
        mm.append({"v": vchk, "E_d_of_inner_argument": EA,
                   "Kbar_times_v_to_p": Kbar * (vchk ** p),
                   "relative_error": abs(EA - Kbar * (vchk ** p))
                   / (Kbar * (vchk ** p))})
    log("  R2 mean-match self-check (E_d[A] must equal Kbar v^p): max relative "
        "error %.3e" % max(x["relative_error"] for x in mm))

    r2 = []
    t0 = time.time()
    for amu2 in amu2_grid:
        a = amu2 / (mu * mu)
        W = [0.0] * len(nodes)
        for i in keep:
            W[i] = W_R2(nodes[i][0], Kbar, p, a, mu, sg)[0]
        pin, _ = integrate(T, N, nodes, W, norm)
        d = math.log2(pin) - base["log2_pred"]
        denom = v_T - amu2
        s_eff = (2.0 * p * a * mu * sg / denom) if denom > 0 else None
        r2.append({"a_times_mu_lsc_squared": amu2, "a": a,
                   "log2_P_in": math.log2(pin),
                   "delta_bits_vs_collapsed": d,
                   "residual_vs_measured_bits": math.log2(pin) - log2meas,
                   "induced_local_log_dispersion_s_eff_at_v_of_T": s_eff,
                   "alpha_implied_if_a_equals_alpha_pi2_over_q2":
                       amu2 / ((math.pi * mu / q) ** 2)})
        log("    R2 a*mu^2=%6.3f (a=%.6e, alpha would be %.4f): log2 P_in = "
            "%.6f  Delta = %+.6f bits ; s_eff(v=%.4f) = %s"
            % (amu2, a, r2[-1]["alpha_implied_if_a_equals_alpha_pi2_over_q2"],
               r2[-1]["log2_P_in"], d, v_T,
               "n/a" if s_eff is None else "%.4f" % s_eff))
    log("  R2 scan in %.1f s" % (time.time() - t0))

    # ---- R2 quadrature convergence check ---------------------------------
    global Z_SUB
    z_sub_save = Z_SUB
    Z_SUB = 2 * z_sub_save
    amu2_chk = round(amu2_alpha2, 12)
    a_chk = amu2_chk / (mu * mu)
    W = [0.0] * len(nodes)
    for i in keep:
        W[i] = W_R2(nodes[i][0], Kbar, p, a_chk, mu, sg)[0]
    pin_fine, _ = integrate(T, N, nodes, W, norm)
    Z_SUB = z_sub_save
    ref = [r for r in r2 if abs(r["a_times_mu_lsc_squared"] - amu2_chk) < 1e-12]
    conv = abs(math.log2(pin_fine) - ref[0]["log2_P_in"]) if ref else None
    log("  R2 d_lsc-quadrature convergence (Z_SUB %d -> %d) at a*mu^2=%.3f: "
        "%.3e bits" % (z_sub_save, 2 * z_sub_save, amu2_chk, conv))

    # ---- whole-band profile of the R1 correction at selected s -----------
    band_prof = []
    s_sel = sorted(set([x for x in (0.5, 1.0, 2.0) if x <= 40.0] +
                       ([round(req["validator"]["s_required_sd_of_ln_k"], 6)]
                        if req["validator"]["s_required_sd_of_ln_k"] else [])))
    step = max(1, last_pos // 20)
    profile_scores = list(range(0, last_pos + 1, step))
    if profile_scores[-1] != last_pos:
        profile_scores.append(last_pos)
    if T not in profile_scores:
        profile_scores.append(T)
        profile_scores.sort()
    for s in s_sel:
        W = [W_R1(v, Kbar, p, s) for (v, u, b) in nodes]
        rows = []
        sse = 0.0
        n = 0
        for Ts in range(0, last_pos + 1):
            pin, _ = integrate(Ts, N, nodes, W, norm)
            r = math.log2(pin) - math.log2(values[Ts])
            sse += r * r
            n += 1
            if Ts in profile_scores:
                rows.append({"score": Ts, "log2_P_in": math.log2(pin),
                             "residual_vs_measured_bits": r})
        band_prof.append({
            "s_sd_of_ln_k": s,
            "rms_whole_band_bits_with_Kbar_HELD_FIXED": math.sqrt(sse / n),
            "profile": rows,
            "note": ("Kbar is NOT re-fitted for this corrected model.  The rms "
                     "is therefore the rms of the corrected model at the "
                     "collapsed model's own normalisation, and is reported as "
                     "an observation only."),
        })
        log("  whole-band profile at R1 s=%.6f : rms (Kbar held fixed) = "
            "%.6f bits" % (s, band_prof[-1]["rms_whole_band_bits_with_Kbar_HELD_FIXED"]))

    return {
        "file": fname,
        "file_sha256": sha256(path),
        "file_path_repo_relative": os.path.relpath(path, REPO),
        "header_raw": raw,
        "peak_score": T,
        "peak_score_inside_resolved_band": True,
        "resolved_band_scores": [0, last_pos],
        "counting_floor": floor,
        "counting_floor_log2": math.log2(floor),
        "parameters_used": {
            "p": p, "p_source": "(beta_sieve + n_fft)/2 from the .out header",
            "log2_Kbar_HELD_FIXED": case["log2_K_fit_BATCH009"],
            "Kbar_source": ("BATCH-009 TASK-20260802-8bae8e fitted "
                            "normalisation; NOT re-optimised here"),
            "N": N, "mu_lsc": mu, "sigma_lsc": sg,
            "psi_lsc_support_used": ("untruncated normal on the whole line, "
                                     "matching (4.22)'s normalisation constant "
                                     "pi*sigma_lsc*sqrt(2N); (4.22) writes the "
                                     "d_lsc integral from 0, and P(d_lsc<0) = "
                                     "%.3e here, so the difference is far below "
                                     "every number reported"
                                     % Phi_std(-mu / sg)),
            "score_scale": "raw undivided cosine-sum scale; no k_fft alignment",
        },
        "baseline_collapsed_model": {
            "log2_P_out": base["log2_pred"],
            "log2_measured": log2meas,
            "over_prediction_bits_recomputed_here": delta_here,
            "over_prediction_bits_producer_BATCH009":
                case["peak_delta_bits_producer"],
            "over_prediction_bits_validator_TASK_bc8c1f":
                case["peak_delta_bits_validator"],
            "log2_Q_gaussian_component": base["log2_Q"],
            "clipped_fraction_here": base["clipped_fraction"],
            "clipped_fraction_producer_BATCH009":
                case["clipped_fraction_producer"],
            "v_star": base["v_star"], "u_star": base["u_star"],
        },
        "reading_free_bound_on_delta_bits": {
            "upper": 0.0,
            "upper_source": ("Jensen: min(1,.) is concave, so the collapsed "
                             "form is an upper bound on (4.22).  This fixes "
                             "the SIGN of the difference."),
            "lower": bound_lo,
            "lower_source": ("P_in(T) >= Q(T) because Model 4.7's D component "
                             "is non-negative.  Concavity ALONE does not bound "
                             "the magnitude: with the mean held at Kbar L^p, "
                             "E[min(1,Z)] can be driven arbitrarily close to 0 "
                             "by dispersing Z."),
        },
        "reading_R1_lognormal_dispersion": {
            "definition": ("k(d_lsc) = Kbar exp(s z - s^2/2), z = (d_lsc - "
                           "mu_lsc)/sigma_lsc ~ N(0,1); E[k] = Kbar exactly; "
                           "s = sd(ln k) is the only parameter"),
            "self_check_delta_at_s_zero_bits": self_s0,
            "scan": r1,
            "dispersion_required_to_absorb_the_over_prediction": req,
        },
        "reading_R2_shift_from_eq_4_19": {
            "definition": ("Phi_d(x,y) = exp(-a(x^2+y^2+d^2)); inner integral "
                           "K_0 (L - a d^2)_+^p; mean-matched at every L so "
                           "that E_d of the inner argument is Kbar L^p exactly "
                           "and Kbar is held fixed"),
            "alpha_status": ("UNAVAILABLE in every archived page extract of the "
                             "paper.  a = alpha pi^2/q^2 under (4.19); the "
                             "scan is over a*mu_lsc^2 = alpha (pi mu_lsc/q)^2. "
                             "The archived Pgood header's alpha_secret = "
                             "alpha_error = 2 is NOT established to be the "
                             "paper's alpha and is not adopted; alpha=2 would "
                             "correspond to a*mu_lsc^2 = %.6f."
                             % (2.0 * (math.pi * mu / q) ** 2)),
            "departure_from_BATCH009_reading": (
                "The BATCH-009 script's STEP 2 writes Phi = exp(-(a x^2 + "
                "b(d_lsc) y^2)), a MULTIPLICATIVE d_lsc dependence.  At y=0 "
                "that form does not reproduce (4.19)'s exp(-a d_lsc^2) factor, "
                "whereas the shift reading does.  Recorded as an observation; "
                "not resolved, because Phi_{d_lsc} is UNAVAILABLE."),
            "v_at_peak_score_ln_N_over_T": v_T,
            "a_times_mu_lsc_squared_if_alpha_equals_2": amu2_alpha2,
            "mean_match_self_check": mm,
            "d_lsc_quadrature_convergence_bits": conv,
            "outer_node_mask": {
                "nodes_total": len(nodes), "nodes_evaluated": len(keep),
                "dropped_weight_absolute": dropped,
                "dropped_weight_relative_to_P_out": dropped / base["pred"],
                "meaning": ("W <= 1 always, so the dropped weight is a hard "
                            "upper bound on the error this mask can induce"),
            },
            "scan": r2,
        },
        "whole_band_profile_of_the_R1_correction": band_prof,
    }


# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    log("jensen_bias_bound.py -- CHECK B -- TASK-20260803-f95b4e, BATCH-010, "
        "GOAL-MLKEM-003")
    log("python %s on %s" % (sys.version.split()[0], platform.platform()))
    log("numpy available: %s ; scipy available: %s"
        % (_have("numpy"), _have("scipy")))
    log("")

    results = [analyse(c, log) for c in CASES]

    out = {
        "check": "B -- Jensen bias bound on the collapsed d_lsc integral",
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
            "This is a BIAS BOUND, not a re-fit: Kbar is held at the archived "
            "BATCH-009 value in every reading, and E_{d_lsc}[k] = Kbar exactly, "
            "so the collapsed baseline is literally unchanged.",
            "The magnitude of the Jensen difference is NOT fixed by the "
            "archive: Phi_{d_lsc} and alpha are UNAVAILABLE.  Two declared "
            "readings are scanned and the required dispersion is solved for.",
            "This script records magnitudes, signs and bounds.  It does NOT "
            "conclude that Approximation 4.9 is validated, refuted, selected "
            "or rejected.",
        ],
        "zero_new_sampling": True,
        "cases": results,
        "stdout_log": lines,
    }
    out["wall_clock_seconds"] = time.time() - t_start

    dest = os.path.join(HERE, "results.json")
    doc = {}
    if os.path.exists(dest):
        with open(dest) as fh:
            doc = json.load(fh)
    doc["task_id"] = "TASK-20260803-f95b4e"
    doc["batch_id"] = "BATCH-010"
    doc["goal_id"] = "GOAL-MLKEM-003"
    doc["check_B_jensen_bias_bound"] = out
    with open(dest, "w") as fh:
        json.dump(doc, fh, indent=1, allow_nan=True)
    log("")
    log("wrote check_B_jensen_bias_bound into %s (%.1f kB) in %.1f s"
        % (dest, os.path.getsize(dest) / 1024.0, out["wall_clock_seconds"]))


def _have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()

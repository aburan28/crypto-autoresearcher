#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TASK-20260802-8bae8e (F1) -- BATCH-009 of GOAL-MLKEM-003, authorized by
DEC-20260802-56cc4b.

WHAT THIS SCRIPT DOES
---------------------
It recomputes the Pwrong survival curve predicted by Approximation 4.9 of
Carrier, Meyer-Hilfiger, Shen, Tillich, "Assessing the Impact of a Variant of
MATZOV's Dual Attack on Kyber" (HAL 05406481), as that approximation is written
in the ARCHIVED page extracts in this repository, and compares it point by
point against the ARCHIVED verifyModel measurement, over the band the counting
instrument actually resolved.

It performs NO sampling, NO lattice computation, NO G6K call and NO network
access.  Every input byte is already in this repository.

WHAT IT DOES NOT DO
-------------------
It makes no ML-KEM or Kyber security claim, revises no cost model, and changes
no record status.  Parameters are toy (q=241, m=40, n=43/50).  AGENTS.md rule
12 is UNMET and UNWAIVED for this batch: nothing here treats EV-MLKEM-011,
EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or KN-FIND-014 as corrected.

SCORE-SCALE CONVENTION (constraint from the handoff, and independently
re-checked here)
---------------------------------------------------------------------
The archived scores are on the RAW, UNDIVIDED cosine-sum scale.  No k_fft
alignment is applied.  The script re-derives the supporting statistic from the
survival files themselves (sigma = sqrt(E[F^2 | F >= 0]) against Model 4.7's
sqrt(avg_N/2)) and prints the result, so the convention is checked rather than
merely asserted.  See `scale_check` in the output.

THE COUNTING FLOOR (constraint from the handoff, and re-verified here)
----------------------------------------------------------------------
Each measured survival function is an unsmoothed pooled counting estimate over
nb_iteration * q^k_fft candidate scores.  Its support ends at exactly
1/(nb_iteration * q^k_fft).  Values below that are ABSENCE OF MEASUREMENT, not
small measurements.  Nothing is compared, fitted or extrapolated past it.

--------------------------------------------------------------------------
DERIVATION OF THE PREDICTED CURVE FROM THE ARCHIVED TEXT
--------------------------------------------------------------------------
Archived source: inputs/MLKEM-DUAL-SOURCES-20260802/extracts/
                 carrier-hal-05406481/page23_approx_4_8_4_9.txt   (4.19)-(4.24)
                 .../page25_pwrong_validation.txt                 (4.26)-(4.29)
                 .../page26_fig41.txt                             Fig 4.1 caption

Approximation 4.9, equation (4.22):

  Pwrong(T) ~= INT_{-inf}^{+inf} INT_0^{+inf}
                 min( 1, INT_{E(T-t)} lambda(x) mu(y) d(x,y) )
                 * exp( -t^2/N - (dlsc-mu_lsc)^2 / (2 sigma_lsc^2) )
                 / ( pi * sigma_lsc * sqrt(2N) )  ddlsc dt

  E(T-t) = { (x,y) in R_+^2 : N * Phi_{dlsc}(x,y) >= T - t }            (4.23)

  lambda(x) = 2 * delta(beta_bkz)^{beta_sieve (m + n_lat - beta_sieve)}
              * pi^{beta_sieve/2} * x^{beta_sieve - 1}
              / ( q^{beta_sieve * m/(m+n_lat)} * Gamma(beta_sieve/2) )   (4.24)

  mu(y)     = 2 * pi^{n_fft/2} * y^{n_fft - 1}
              / ( q^{k_fft} * Gamma(n_fft/2) )                          (4.24)

STEP 1 -- the weight in (4.22) is exactly a product of two normal densities.
  INT exp(-t^2/N) dt = sqrt(pi N);  INT exp(-(d-mu)^2/(2 s^2)) dd = s sqrt(2 pi).
  Product = pi * s * sqrt(2N), which is exactly (4.22)'s denominator.  So
  t ~ N(0, N/2) and dlsc ~ N(mu_lsc, sigma_lsc^2), i.e. (4.22) is
      Pwrong(T) = E_{t, dlsc} [ min(1, expected count in E(T-t)) ],
  which is Model 4.7's convolution "P(D + N(0,N/2) >= T)" of Fig 4.1's legend.

STEP 2 -- the region E(u) requires Phi_{dlsc}(x,y).  ***Phi IS NOT DEFINED IN
ANY ARCHIVED EXTRACT*** (it is introduced with Approximation 4.6, on a page not
retrieved).  It is recorded as UNAVAILABLE.  What the archive does pin is the
following: Approximation 4.8's (4.19) is, by its own statement, T set "around
the expectation of F", i.e. N * E[Phi] on the good guess, and it evaluates to a
PRODUCT of two factors each of the form exp(-alpha (pi * length / q)^2):

    T/N = exp(-alpha(pi mu_lsc/q)^2 / (1 + 2 alpha (pi sigma_lsc/q)^2))
          / sqrt(1 + 2 alpha (pi sigma_lsc/q)^2)
          * INT_0^1 beta_sieve t^{beta_sieve-1} exp(-alpha (pi dlat t/q)^2) dt

  The first factor is exactly INT psi_lsc(d) exp(-a d^2) dd with a =
  alpha pi^2/q^2 (checked in closed form below), the second is exactly
  E[exp(-a dlat^2 X^2)] for X the normalised norm in a beta_sieve-ball.  So the
  archived text forces Phi to be exponential in a NEGATIVE QUADRATIC FORM of the
  two lengths.  This script therefore adopts, EXPLICITLY AS A DERIVED READING
  AND NOT AS AN ARCHIVED DEFINITION,

      Phi_{dlsc}(x, y) = exp( -( a x^2 + b(dlsc) y^2 ) ),   a, b > 0.

  Any (a, b) > 0 gives the same predicted SHAPE; they move only the scale.
  The reading is stated, its consequence is isolated to one scalar, and a
  free-exponent sensitivity diagnostic is run against it below.

STEP 3 -- under STEP 2, E(u) = { (x,y) in R_+^2 : a x^2 + b y^2 <= L },
  L = ln(N/u), a quarter-ellipse with semi-axes sqrt(L/a), sqrt(L/b).  Then

    INT_{E(u)} lambda(x) mu(y) d(x,y)
      = C_lat * C_fft * a^{-beta/2} b^{-n_fft/2} * G(beta, n_fft) * L^{p}
      =: K * L^{p},        p = (beta_sieve + n_fft)/2,

  where G(beta,n) = INT INT_{x,y>=0, x^2+y^2<=1} x^{beta-1} y^{n-1} dx dy
                  = Gamma(beta/2) Gamma(n/2) / ( 2 (beta+n) Gamma((beta+n)/2) ).

  *** The EXPONENT p is fixed entirely by archived integers (beta_sieve from the
  file header beta_1 and from the Fig 4.1 caption; n_fft from both). ***
  *** The SCALE K collects every quantity the archive does not carry:
      delta(beta_bkz) (Lemma 2.9, not archived), alpha (not in any archived page
      extract), and Phi's constants a, b.  K is therefore NOT computable from
      archived bytes and is carried as a single free normalisation. ***

  Consequently P(D >= u | dlsc) ~= min(1, K(dlsc) * ln(N/u)^p)  for 0 < u < N,
  = 1 for u <= 0 (E(u) is all of R_+^2), = 0 for u >= N (E(u) empty).
  In the unclipped regime this is linear in K, so the psi_lsc average over dlsc
  is EXACTLY an effective scale Kbar; the script carries one effective K and
  reports separately how much of each prediction comes from the clipped region,
  where that reduction is an approximation rather than an identity.

STEP 4 -- writing u = T - t and integrating over the D-axis,

    Pwrong(T; K) = Q(T) + INT_0^N phi(T-u) min(1, K ln(N/u)^p) du
                 = Q(T) + INT_0^inf N e^{-v} phi(T - N e^{-v}) min(1, K v^p) dv

  with phi(s) = exp(-s^2/N)/sqrt(pi N)  (the N(0,N/2) density)
  and  Q(T)   = P(N(0,N/2) >= T) = 0.5 * erfc(T / sqrt(N)).

  Q(T) has NO free parameter and is fully archived (N = avg_N).  It is one of
  the three curves of Fig 4.1 and is reported per score in its own right.

Numerics: numpy/scipy are NOT installed in this environment.  Gauss-Legendre
nodes are generated from the Legendre recurrence by Newton iteration, and the
quadrature is self-checked against a closed form (the K -> infinity limit,
where the integrand collapses to a normal-density integral computable with
math.erfc).  No estimate is presented as a measurement anywhere.
"""

import json
import math
import os
import platform
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "..", "..", ".."))
DATA = os.path.join(REPO, "experiments", "EXP-MLKEM-011", "vendor-lock", "data")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out",
    "Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out",
]
PGOOD_FILE = "Pgood_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out"

# Fig 4.1 caption values, archived at
# inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page26_fig41.txt
CAPTION = {
    "Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out": {
        "panel": "left", "q": 241, "m": 40, "n": 43, "n_lat": 35, "n_enu": 0,
        "n_fft": 8, "k_fft": 3, "N": 25971, "beta_bkz": 32, "beta_sieve": 44,
        "d_lat": 42.00, "mu_lsc": 23.94, "sigma_lsc": 3.38,
        "nb_iteration_stated_in_caption": 4000,
    },
    "Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out": {
        "panel": "right", "q": 241, "m": 40, "n": 50, "n_lat": 42, "n_enu": 0,
        "n_fft": 8, "k_fft": 3, "N": 25970, "beta_bkz": 35, "beta_sieve": 41,
        "d_lat": 58.60, "mu_lsc": 23.87, "sigma_lsc": 3.30,
        "nb_iteration_stated_in_caption": 4000,
    },
}


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def read_out(path):
    header, values = {}, []
    raw_header_lines = []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                raw_header_lines.append(s)
                body = s.lstrip("#").strip()
                if "=" in body and " " not in body.split("=")[0]:
                    k, v = body.split("=", 1)
                    header[k.strip()] = v.strip()
                continue
            values.append(float(s))
    return header, values, raw_header_lines


def _f(x, fmt="%.4f"):
    return "n/a" if x is None else fmt % x


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Quadrature (no numpy/scipy available)
# ---------------------------------------------------------------------------
def gauss_legendre(n):
    """Nodes/weights on [-1,1] via Newton iteration on the Legendre recurrence."""
    nodes, weights = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
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


def panel_layout(v_max, refine):
    """Panel edges for the v-integration.

    The integrand N e^{-v} phi(T - N e^{-v}) w(v) varies on the scale of the
    normal density, i.e. du ~ sqrt(N/2), i.e. dv ~ sqrt(N/2)/u = e^{v}
    sqrt(N/2)/N.  Panels are therefore widened geometrically with v.  `refine`
    scales the whole layout (smaller = finer) and is used for the convergence
    self-check.
    """
    out, v = [], 0.0
    while v < v_max:
        h = 0.25 * refine if v < 1.5 else min(0.5 * refine,
                                              max(0.005 * refine,
                                                  0.0011 * refine * math.exp(v)))
        h = min(h, v_max - v)
        out.append((v, h))
        v += h
    return out


def build_v_grid(N, p, v_max, refine, gl_order):
    """Precompute the v-quadrature: u = N e^{-v}, du = N e^{-v} dv."""
    gx, gw = gauss_legendre(gl_order)
    v_list, base_list, u_list, vp_list = [], [], [], []
    for lo, h in panel_layout(v_max, refine):
        half = h / 2.0
        mid = lo + half
        for x, w in zip(gx, gw):
            v = mid + half * x
            u = N * math.exp(-v)
            v_list.append(v)
            u_list.append(u)
            base_list.append(w * half * u)       # weight * du/dv
            vp_list.append(v ** p)
    return v_list, u_list, base_list, vp_list


def make_phi(N):
    inv = 1.0 / N
    norm = 1.0 / math.sqrt(math.pi * N)

    def phi(s):
        z = s * s * inv
        if z > 700.0:
            return 0.0
        return norm * math.exp(-z)
    return phi


def q_gauss(T, N):
    """P(N(0, N/2) >= T) = 0.5 * erfc(T / sqrt(N))."""
    return 0.5 * math.erfc(T / math.sqrt(N))


def integral_D(T, K, grid, phi):
    """INT_0^inf N e^{-v} phi(T - N e^{-v}) min(1, K v^p) dv, and the part of it
    contributed by the clipped (min == 1) region."""
    _, u_l, base_l, vp_l = grid
    tot = 0.0
    clipped = 0.0
    for u, base, vp in zip(u_l, base_l, vp_l):
        w = K * vp
        if w >= 1.0:
            w = 1.0
            c = base * phi(T - u)
            clipped += c
            tot += c
        else:
            tot += base * w * phi(T - u)
    return tot, clipped


def integral_J(T, grid, phi):
    """Unclipped INT_0^inf N e^{-v} phi(T - N e^{-v}) v^p dv (linear coefficient
    of K).  Only meaningful where the clip does not bind."""
    _, u_l, base_l, vp_l = grid
    tot = 0.0
    for u, base, vp in zip(u_l, base_l, vp_l):
        tot += base * vp * phi(T - u)
    return tot


def predict(T, K, N, grid, phi):
    i, clipped = integral_D(T, K, grid, phi)
    return q_gauss(T, N) + i, clipped


# ---------------------------------------------------------------------------
# Scale check (re-derivation of EV-MLKEM-018's code-independent statistic)
# ---------------------------------------------------------------------------
def scale_check(values, avg_N):
    """Two estimators of sigma = sqrt(E[F^2 | F >= 0]) from the survival column.

    Estimator A (integer-grid identity, conditional on F >= 0):
        E[F^2 | F>=0] = sum_{t>=1} (2t-1) P(F>=t) / P(F>=0)
    Estimator B (unconditional, using symmetry of F about 0):
        E[F^2] = 2 * sum_{t>=1} (2t-1) P(F>=t)
    Model 4.7 predicts sqrt(avg_N/2) on the raw undivided scale, and
    sqrt(avg_N/2)/k_fft on a /k_fft-aligned scale.
    """
    s = 0.0
    for t in range(1, len(values)):
        s += (2.0 * t - 1.0) * values[t]
    p0 = values[0]
    a = math.sqrt(s / p0)
    b = math.sqrt(2.0 * s)
    return a, b


# ---------------------------------------------------------------------------
# Main comparison for one file
# ---------------------------------------------------------------------------
def analyse(fname, log):
    path = os.path.join(DATA, fname)
    header, values, raw_header = read_out(path)
    cap = CAPTION[fname]

    q = int(header["q"])
    m = int(header["m"])
    n = int(header["n"])
    n_fft = int(header["n_fft"])
    k_fft = int(header["k_fft"])
    n_lat = int(header["n_lat"])
    beta_bkz = int(header["beta_0"])
    beta_sieve = int(header["beta_1"])
    avg_N = float(header["avg_N"])
    avg_dlat = float(header["avg_dlat"])
    sdv_dlat = float(header["sdv_dlat"])
    avg_dlsc = float(header["avg_dlsc"])
    sdv_dlsc = float(header["sdv_dlsc"])
    nb_iteration = int(header["nb_iteration"])

    # ---- counting floor and resolved band -------------------------------
    denom = nb_iteration * (q ** k_fft)
    floor = 1.0 / denom
    last_pos = max(i for i, v in enumerate(values) if v > 0.0)
    first_zero = last_pos + 1 if last_pos + 1 < len(values) else None
    floor_exact = (values[last_pos] == floor)
    # every value an integer multiple of the quantum?
    max_rel_dev = 0.0
    for v in values:
        c = v / floor
        dev = abs(c - round(c)) / max(1.0, round(c))
        max_rel_dev = max(max_rel_dev, dev)
    counts = [int(round(v / floor)) for v in values]

    log("[%s]" % fname)
    log("  nb_iteration=%d  q^k_fft=%d  nb_iteration*q^k_fft=%d" %
        (nb_iteration, q ** k_fft, denom))
    log("  counting floor = %.17g = 2^%.8f ; last positive score = %d ;"
        " exact float equality = %s" %
        (floor, math.log2(floor), last_pos, floor_exact))
    log("  resolved band = scores [0, %d]  (first zero at %s)" %
        (last_pos, first_zero))
    log("  max relative deviation from integer multiples of the quantum = %.3e"
        % max_rel_dev)

    sig_a, sig_b = scale_check(values, avg_N)
    raw_pred = math.sqrt(avg_N / 2.0)
    log("  scale check: sigma_estimatorA=%.4f sigma_estimatorB=%.4f vs"
        " sqrt(avg_N/2)=%.4f  (ratios %.4f / %.4f);"
        " vs sqrt(avg_N/2)/k_fft ratios %.4f / %.4f" %
        (sig_a, sig_b, raw_pred, sig_a / raw_pred, sig_b / raw_pred,
         sig_a / (raw_pred / k_fft), sig_b / (raw_pred / k_fft)))

    # ---- model grid ------------------------------------------------------
    N = avg_N
    p = (beta_sieve + n_fft) / 2.0
    phi = make_phi(N)
    V_MAX, REFINE, GL = 120.0, 1.0, 10
    grid = build_v_grid(N, p, V_MAX, REFINE, GL)
    grid_fine = build_v_grid(N, p, V_MAX, 0.5, 16)

    # ---- quadrature self-check against a closed form ---------------------
    # K -> infinity limit: integrand becomes N e^{-v} phi(T - N e^{-v}), whose
    # exact value is INT_0^N phi(T-u) du = 0.5*(erfc((T-N)/sqrt(N)) -
    # erfc(T/sqrt(N))).
    selfcheck = []
    for T in (0, 200, 900, 1500, last_pos):
        approx = sum(b * phi(T - u) for u, b in zip(grid[1], grid[2]))
        exact = 0.5 * (math.erfc((T - N) / math.sqrt(N))
                       - math.erfc(T / math.sqrt(N)))
        rel = abs(approx - exact) / exact if exact > 0 else float("nan")
        selfcheck.append({"T": T, "quadrature": approx, "closed_form": exact,
                          "rel_error": rel})
    log("  quadrature self-check (K->inf limit vs closed form): max rel err"
        " = %.3e" % max(s["rel_error"] for s in selfcheck))

    # convergence check: coarse vs fine grid on J(T)
    conv = []
    for T in (200, 900, 1500, last_pos):
        jc = integral_J(T, grid, phi)
        jf = integral_J(T, grid_fine, phi)
        conv.append({"T": T, "J_coarse": jc, "J_fine": jf,
                     "rel_diff": abs(jc - jf) / jf if jf > 0 else float("nan")})
    log("  quadrature convergence (coarse vs fine J): max rel diff = %.3e" %
        max(c["rel_diff"] for c in conv))

    # ---- fit the single free scale K ------------------------------------
    band = list(range(0, last_pos + 1))
    fit_grid = band[::20]
    if band[-1] not in fit_grid:
        fit_grid.append(band[-1])

    def sse(logK, scores):
        K = 2.0 ** logK
        s = 0.0
        for T in scores:
            pr, _ = predict(T, K, N, grid, phi)
            if pr <= 0.0:
                return float("inf")
            s += (math.log2(pr) - math.log2(values[T])) ** 2
        return s

    # coarse scan then golden section
    best, best_lk = float("inf"), None
    for lk in range(-200, 21, 4):
        v = sse(float(lk), fit_grid)
        if v < best:
            best, best_lk = v, float(lk)
    lo, hi = best_lk - 4.0, best_lk + 4.0
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = hi - gr * (hi - lo), lo + gr * (hi - lo)
    fc, fd = sse(c, fit_grid), sse(d, fit_grid)
    for _ in range(60):
        if fc < fd:
            hi, d, fd = d, c, fc
            c = hi - gr * (hi - lo)
            fc = sse(c, fit_grid)
        else:
            lo, c, fc = c, d, fd
            d = lo + gr * (hi - lo)
            fd = sse(d, fit_grid)
        if hi - lo < 1e-7:
            break
    logK_fit = 0.5 * (lo + hi)
    K_fit = 2.0 ** logK_fit
    log("  fitted normalisation: log2(K_fit) = %.6f  (least squares on log2"
        " residuals, %d-point subsample of the resolved band)" %
        (logK_fit, len(fit_grid)))

    # anchored normalisations: exact match at one score, to separate SHAPE from
    # NORMALISATION in the divergence profile.
    def solve_K_at(T, tol=1e-7):
        """log2 of the single free scale K that reproduces the measurement at
        score T exactly.  pred(T; K) is increasing in K, so bisection is safe."""
        target = values[T]
        lo_, hi_ = -400.0, 40.0
        pr0, _ = predict(T, 2.0 ** lo_, N, grid, phi)
        if pr0 >= target:
            return None          # no admissible K within representable range
        for _ in range(200):
            mid = 0.5 * (lo_ + hi_)
            pr, _ = predict(T, 2.0 ** mid, N, grid, phi)
            if pr > target:
                hi_ = mid
            else:
                lo_ = mid
            if hi_ - lo_ < tol:
                break
        return 0.5 * (lo_ + hi_)

    # anchor_low: first score whose measured survival drops below 2^-5, i.e.
    # the top of Fig 4.1's plotted y-range.  anchor_high: last score whose
    # pooled count is >= 10 (above that the estimate is Poisson-dominated).
    anchor_low = next(i for i, v in enumerate(values) if v < 2.0 ** -5)
    anchor_high = max(i for i, c in enumerate(counts) if c >= 10)
    logK_low = solve_K_at(anchor_low)
    logK_high = solve_K_at(anchor_high)
    assert logK_low is not None and logK_high is not None, (
        "anchor score has no admissible K; see scores_with_no_admissible_K")
    log("  anchored normalisations: log2(K) = %.6f matching exactly at score"
        " %d (2^-5 level); log2(K) = %.6f matching exactly at score %d"
        " (last score with pooled count >= 10, count=%d)" %
        (logK_low, anchor_low, logK_high, anchor_high, counts[anchor_high]))

    # ---- full-band per-score comparison ---------------------------------
    t0 = time.time()
    rows = []
    Klo, Khi = 2.0 ** logK_low, 2.0 ** logK_high
    for T in band:
        meas = values[T]
        lg_meas = math.log2(meas)
        qg = q_gauss(T, N)
        pf, clip_f = predict(T, K_fit, N, grid, phi)
        pl, _ = predict(T, Klo, N, grid, phi)
        ph, _ = predict(T, Khi, N, grid, phi)
        # P(D >= T) alone, the second Fig 4.1 curve
        L = math.log(N / T) if 0 < T < N else (None if T >= N else float("inf"))
        if T <= 0:
            sd = 1.0
        elif T >= N:
            sd = 0.0
        else:
            sd = min(1.0, K_fit * (L ** p))
        # normalisation-free divergence: the value of the single free scale K
        # that would reproduce the measurement AT THIS SCORE exactly, obtained
        # by bisection on the exact (clipped) model.  None when no K >= 0 can:
        # the model's parameter-free floor Q(T) already exceeds the measurement.
        k_solved = solve_K_at(T, tol=1e-4) if meas > qg else None
        # elasticity dlog2(pred)/dlog2(K) at K_fit: 1 where the prediction is
        # carried entirely by the D component, 0 where K is irrelevant because
        # the parameter-free Gaussian component dominates.
        pu, _ = predict(T, K_fit * 2.0 ** 0.25, N, grid, phi)
        pd, _ = predict(T, K_fit * 2.0 ** -0.25, N, grid, phi)
        elast = (math.log2(pu) - math.log2(pd)) / 0.5
        rows.append([
            T,
            meas,
            lg_meas,
            counts[T],
            math.log2(qg) if qg > 0 else float("-inf"),
            math.log2(pf), math.log2(pf) - lg_meas,
            math.log2(pl), math.log2(pl) - lg_meas,
            math.log2(ph), math.log2(ph) - lg_meas,
            math.log2(sd) if sd > 0 else float("-inf"),
            clip_f / pf if pf > 0 else float("nan"),
            k_solved,
            elast,
        ])
    log("  full-band per-score evaluation: %d scores in %.1f s" %
        (len(rows), time.time() - t0))

    # ---- divergence statistics ------------------------------------------
    def stats(sel, col):
        d = [r[col] for r in rows if sel(r)]
        if not d:
            return None
        return {
            "n": len(d),
            "min": min(d), "max": max(d),
            "mean": sum(d) / len(d),
            "rms": math.sqrt(sum(x * x for x in d) / len(d)),
        }

    all_band = lambda r: True
    reliable = lambda r: r[3] >= 10
    figband = lambda r: r[1] < 2.0 ** -5 and r[3] >= 10
    unclipped = lambda r: (r[12] == r[12] and r[12] < 1e-3)
    unclipped_rel = lambda r: unclipped(r) and r[3] >= 10
    # scores where the free scale actually controls the prediction
    sensitive = lambda r: r[14] > 0.9

    ki = [r for r in rows if r[13] is not None and sensitive(r) and r[3] >= 10]
    no_admissible_K = [r[0] for r in rows if r[13] is None]
    k_solved_profile = {
        "definition": ("log2 of the single free scale K that reproduces the "
                       "measurement AT THAT SCORE exactly, by bisection on the "
                       "exact clipped model.  Reported over scores where the "
                       "elasticity dlog2(pred)/dlog2(K) exceeds 0.9 (i.e. the "
                       "prediction is carried by the D component rather than "
                       "by the parameter-free Gaussian component) and the "
                       "pooled count is >= 10."),
        "n_scores": len(ki),
        "score_range": [ki[0][0], ki[-1][0]] if ki else None,
        "log2_K_solved_at_low_end": ki[0][13] if ki else None,
        "log2_K_solved_at_high_end": ki[-1][13] if ki else None,
        "drift_bits_low_to_high": (ki[-1][13] - ki[0][13]) if ki else None,
        "min": min(r[13] for r in ki) if ki else None,
        "max": max(r[13] for r in ki) if ki else None,
        "monotone_increasing": (all(ki[i][13] <= ki[i + 1][13] + 1e-4
                                    for i in range(len(ki) - 1))
                                if len(ki) > 1 else None),
        "samples": [{"score": r[0], "pooled_count": r[3],
                     "log2_K_solved": r[13], "elasticity": r[14]}
                    for r in ki[::max(1, len(ki) // 25)]] if ki else [],
        "scores_with_no_admissible_K": {
            "n": len(no_admissible_K),
            "range": ([min(no_admissible_K), max(no_admissible_K)]
                      if no_admissible_K else None),
            "meaning": ("At these scores the measurement lies BELOW the model's "
                        "parameter-free floor P(N(0,N/2) >= T), so no K >= 0 "
                        "reproduces it.  Model 4.7 writes the wrong-guess score "
                        "as D + N(0,N/2) with D >= 0, so the model's survival "
                        "cannot go below the pure-noise survival."),
            "max_shortfall_bits": (max(rows[T][4] - rows[T][2]
                                       for T in no_admissible_K)
                                   if no_admissible_K else None),
        },
    }

    summary = {
        "delta_fit": {
            "whole_resolved_band": stats(all_band, 6),
            "count_ge_10_subband": stats(reliable, 6),
            "fig41_plotted_range_count_ge_10": stats(figband, 6),
            "clip_negligible_count_ge_10_subband": stats(unclipped_rel, 6),
        },
        "normalisation_free_shape_test": k_solved_profile,
        "delta_anchored_low": {
            "whole_resolved_band": stats(all_band, 8),
            "count_ge_10_subband": stats(reliable, 8),
        },
        "delta_anchored_high": {
            "whole_resolved_band": stats(all_band, 10),
            "count_ge_10_subband": stats(reliable, 10),
        },
        "gaussian_only_deficit_log2": {
            # measured minus the N(0,N/2) component alone, in bits
            "at_score_%d" % last_pos: rows[last_pos][2] - rows[last_pos][4],
            "at_score_1000": (rows[1000][2] - rows[1000][4]
                              if last_pos >= 1000 else None),
            "at_score_500": (rows[500][2] - rows[500][4]
                             if last_pos >= 500 else None),
        },
    }

    kp = summary["normalisation_free_shape_test"]
    log("  normalisation-free shape test: over scores %s (K-sensitive, pooled"
        " count >= 10) the single free scale that matches the measurement"
        " score-by-score moves from log2 K = %s to log2 K = %s, a drift of %s"
        " bits (monotone increasing: %s)" %
        (kp["score_range"], _f(kp["log2_K_solved_at_low_end"]),
         _f(kp["log2_K_solved_at_high_end"]), _f(kp["drift_bits_low_to_high"]),
         kp["monotone_increasing"]))
    nak = kp["scores_with_no_admissible_K"]
    log("  scores where NO K >= 0 reproduces the measurement (measurement below"
        " the model's parameter-free noise floor): n=%d range=%s max shortfall"
        " %s bits" % (nak["n"], nak["range"], _f(nak["max_shortfall_bits"])))
    for key, lab in (("whole_resolved_band", "whole resolved band"),
                     ("count_ge_10_subband", "count>=10 sub-band"),
                     ("clip_negligible_count_ge_10_subband",
                      "clip-negligible count>=10 sub-band")):
        s = summary["delta_fit"].get(key)
        if s:
            log("  delta(pred_Kfit - measured) over %s: n=%d min=%+.3f"
                " max=%+.3f mean=%+.3f rms=%.3f bits" %
                (lab, s["n"], s["min"], s["max"], s["mean"], s["rms"]))

    # decile profile of the divergence, so the shape is visible without the
    # full table
    prof = []
    step = max(1, last_pos // 20)
    for T in range(0, last_pos + 1, step):
        prof.append({"score": T, "log2_measured": rows[T][2],
                     "pooled_count": rows[T][3],
                     "log2_pred_fit": rows[T][5],
                     "delta_fit_bits": rows[T][6],
                     "delta_anchored_low_bits": rows[T][8],
                     "delta_anchored_high_bits": rows[T][10],
                     "clipped_fraction": rows[T][12],
                     "log2_K_solved": rows[T][13],
                     "elasticity_dlog2pred_dlog2K": rows[T][14]})
    if prof[-1]["score"] != last_pos:
        T = last_pos
        prof.append({"score": T, "log2_measured": rows[T][2],
                     "pooled_count": rows[T][3],
                     "log2_pred_fit": rows[T][5],
                     "delta_fit_bits": rows[T][6],
                     "delta_anchored_low_bits": rows[T][8],
                     "delta_anchored_high_bits": rows[T][10],
                     "clipped_fraction": rows[T][12],
                     "log2_K_solved": rows[T][13],
                     "elasticity_dlog2pred_dlog2K": rows[T][14]})

    # ---- free-exponent diagnostic (NOT part of the frozen approximation) --
    # The exponent p = (beta_sieve + n_fft)/2 follows from the STEP-2 reading of
    # the UNAVAILABLE Phi.  This scan asks which exponent the measurement itself
    # prefers, using the SAME exact clipped model, so that the sensitivity of
    # the whole comparison to that reading is visible.  It revises nothing.
    t1 = time.time()
    pscan = []
    scan_grid = band[::40]
    if band[-1] not in scan_grid:
        scan_grid.append(band[-1])
    for p_try in [float(x) for x in range(10, 41, 2)] + [p]:
        g = build_v_grid(N, p_try, V_MAX, REFINE, GL)

        def sse_p(lk):
            K = 2.0 ** lk
            s = 0.0
            for T in scan_grid:
                pr, _ = predict(T, K, N, g, phi)
                if pr <= 0:
                    return float("inf")
                s += (math.log2(pr) - math.log2(values[T])) ** 2
            return s

        b2, blk = float("inf"), None
        for lk in range(-200, 21, 5):
            vv = sse_p(float(lk))
            if vv < b2:
                b2, blk = vv, float(lk)
        lo_, hi_ = blk - 5.0, blk + 5.0
        c_, d_ = hi_ - gr * (hi_ - lo_), lo_ + gr * (hi_ - lo_)
        fc_, fd_ = sse_p(c_), sse_p(d_)
        for _ in range(40):
            if fc_ < fd_:
                hi_, d_, fd_ = d_, c_, fc_
                c_ = hi_ - gr * (hi_ - lo_)
                fc_ = sse_p(c_)
            else:
                lo_, c_, fc_ = c_, d_, fd_
                d_ = lo_ + gr * (hi_ - lo_)
                fd_ = sse_p(d_)
            if hi_ - lo_ < 1e-4:
                break
        pscan.append({"p": p_try, "log2_K": 0.5 * (lo_ + hi_),
                      "rms_bits": math.sqrt(min(fc_, fd_) / len(scan_grid))})
    pscan.sort(key=lambda r: r["p"])
    best_p = min(pscan, key=lambda r: r["rms_bits"])
    at_archived = [r for r in pscan if abs(r["p"] - p) < 1e-9][0]
    log("  free-exponent diagnostic (exact model, %d fit scores): archived-"
        "integer exponent p=%.1f gives rms %.3f bits; best-fitting p on the "
        "scanned grid is %.1f with rms %.3f bits [%.1f s]" %
        (len(scan_grid), p, at_archived["rms_bits"], best_p["p"],
         best_p["rms_bits"], time.time() - t1))

    result = {
        "file": fname,
        "file_sha256": sha256(path),
        "file_path_repo_relative": os.path.relpath(path, REPO),
        "header_raw": raw_header,
        "parameters_from_header": {
            "q": q, "m": m, "n": n, "n_fft": n_fft, "k_fft": k_fft,
            "n_lat": n_lat, "beta_0_bkz": beta_bkz, "beta_1_sieve": beta_sieve,
            "avg_N": avg_N, "avg_dlat": avg_dlat, "sdv_dlat": sdv_dlat,
            "avg_dlsc": avg_dlsc, "sdv_dlsc": sdv_dlsc,
            "nb_iteration": nb_iteration,
        },
        "parameters_from_fig41_caption": cap,
        "instrument": {
            "counting_denominator_nb_iteration_times_q_pow_kfft": denom,
            "counting_floor": floor,
            "counting_floor_log2": math.log2(floor),
            "last_resolved_score": last_pos,
            "first_zero_score": first_zero,
            "last_positive_equals_floor_exactly": floor_exact,
            "all_values_integer_multiples_max_rel_dev": max_rel_dev,
            "resolved_band_scores": [0, last_pos],
            "resolved_band_probability": [values[last_pos], values[0]],
            "resolved_band_probability_log2": [math.log2(values[last_pos]),
                                               math.log2(values[0])],
            "note": ("Scores above %d carry a printed value of 0.0.  That is "
                     "absence of measurement, not a measured zero.  Nothing "
                     "in this comparison uses, fits, or extrapolates past "
                     "score %d." % (last_pos, last_pos)),
        },
        "scale_check": {
            "estimator_A_sigma_sqrt_E_F2_given_Fge0": sig_a,
            "estimator_B_sigma_sqrt_E_F2_symmetric": sig_b,
            "model_4_7_raw_prediction_sqrt_avgN_over_2": raw_pred,
            "ratio_A_over_raw": sig_a / raw_pred,
            "ratio_B_over_raw": sig_b / raw_pred,
            "ratio_A_over_kfft_aligned": sig_a / (raw_pred / k_fft),
            "ratio_B_over_kfft_aligned": sig_b / (raw_pred / k_fft),
            "convention_used": "raw undivided cosine-sum scale; no k_fft alignment",
        },
        "model": {
            "exponent_p": p,
            "exponent_p_source": ("(beta_sieve + n_fft)/2 with beta_sieve from "
                                  "header beta_1 and Fig 4.1 caption, n_fft "
                                  "from header and caption"),
            "N_used": N,
            "N_source": "avg_N from the file header (caption agrees)",
            "quadrature": {"v_max": V_MAX, "panel_refine": REFINE,
                           "gl_order": GL, "n_nodes": len(grid[0]),
                           "self_check_vs_closed_form": selfcheck,
                           "coarse_vs_fine_J": conv},
            "log2_K_fit": logK_fit,
            "log2_K_anchored_low": logK_low,
            "anchor_low_score": anchor_low,
            "log2_K_anchored_high": logK_high,
            "anchor_high_score": anchor_high,
            "K_is_not_archived": ("K collects delta(beta_bkz) (Lemma 2.9, not "
                                  "archived), alpha (in no archived extract) "
                                  "and Phi's constants; it is fitted, not "
                                  "sourced."),
        },
        "per_score_columns": [
            "score", "measured", "log2_measured", "pooled_count",
            "log2_P_gaussian_component", "log2_pred_Kfit", "delta_Kfit_bits",
            "log2_pred_Kanchor_low", "delta_Kanchor_low_bits",
            "log2_pred_Kanchor_high", "delta_Kanchor_high_bits",
            "log2_P_D_ge_T_Kfit", "clipped_fraction_of_pred_Kfit",
            "log2_K_solved_at_this_score", "elasticity_dlog2pred_dlog2K",
        ],
        "per_score": rows,
        "divergence_summary": summary,
        "divergence_profile_every_5pct": prof,
        "free_exponent_diagnostic": {
            "purpose": ("sensitivity of the STEP-2 reading only; NOT a "
                        "revision of Approximation 4.9 and not used anywhere "
                        "else in this report"),
            "fit_scores": [scan_grid[0], scan_grid[-1]],
            "n_fit_scores": len(scan_grid),
            "archived_integer_exponent": p,
            "rms_bits_at_archived_exponent": at_archived["rms_bits"],
            "best_fitting_exponent": best_p,
            "scan": pscan,
        },
    }
    return result


def main():
    t_start = time.time()
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    log("approx49_comparison.py -- TASK-20260802-8bae8e (F1), BATCH-009, "
        "GOAL-MLKEM-003")
    log("python %s on %s" % (sys.version.split()[0], platform.platform()))
    log("numpy available: %s ; scipy available: %s" %
        (_have("numpy"), _have("scipy")))
    log("")

    results = [analyse(f, log) for f in FILES]

    # Pgood file: recorded but NOT compared against Approximation 4.9.
    pg_path = os.path.join(DATA, PGOOD_FILE)
    pg_header, pg_values, _ = read_out(pg_path)
    pgood = {
        "file": PGOOD_FILE,
        "file_sha256": sha256(pg_path),
        "n_values": len(pg_values),
        "min": min(pg_values), "max": max(pg_values),
        "median": sorted(pg_values)[len(pg_values) // 2],
        "mean": sum(pg_values) / len(pg_values),
        "header_alpha_secret": pg_header.get("alpha_secret"),
        "header_alpha_error": pg_header.get("alpha_error"),
        "why_no_approx_4_9_comparison": (
            "This file is a list of 4000 raw scores F(solution) for the GOOD "
            "guess.  Approximation 4.9 is the WRONG-guess survival function; "
            "the good guess is Approximation 4.8.  There is no Pwrong "
            "survival curve in this file to compare against, so the F1 "
            "comparison is not defined for it."),
    }
    log("")
    log("[%s] recorded only: %d raw good-guess scores, min=%.6f median=%.6f "
        "max=%.6f; header carries alpha_secret=%s alpha_error=%s" %
        (PGOOD_FILE, len(pg_values), pgood["min"], pgood["median"],
         pgood["max"], pgood["header_alpha_secret"],
         pgood["header_alpha_error"]))

    out = {
        "task_id": "TASK-20260802-8bae8e",
        "batch_id": "BATCH-009",
        "goal_id": "GOAL-MLKEM-003",
        "authorized_by": "DEC-20260802-56cc4b",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(t_start)),
        "wall_clock_seconds": None,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": _have("numpy"), "scipy": _have("scipy"),
        },
        "non_claims": [
            "No ML-KEM or Kyber security claim; no cost-model revision.",
            "Toy parameters only (q=241, m=40, n=43/50).",
            "No record status is changed; AGENTS.md rule 12 remains unmet and "
            "unwaived, and nothing here treats EV-MLKEM-011, EV-MLKEM-013, "
            "EV-MLKEM-017, KN-FIND-012 or KN-FIND-014 as corrected.",
            "This is a comparison, not a verdict on Approximation 4.9.",
        ],
        "approximation_4_9_parameter_ledger": PARAM_LEDGER,
        "files_compared": results,
        "files_not_compared": [
            pgood,
            {
                "file": ("Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta037_"
                         "beta144_N200001.out"),
                "why_no_comparison": (
                    "Not present in this repository.  It exists here only as a "
                    "header extract (inputs/MLKEM-DUAL-SOURCES-20260802/"
                    "extracts/codeddualattack/) and a sha256 in the input "
                    "manifest, so there is no survival column to compare "
                    "against.  Recorded as archival defect A3 in EV-MLKEM-018."),
            },
        ],
        "stdout_log": log_lines,
    }
    out["wall_clock_seconds"] = time.time() - t_start

    dest = os.path.join(OUT_DIR, "comparison_results.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, allow_nan=True)
    log("")
    log("wrote %s (%.1f kB) in %.1f s total" %
        (dest, os.path.getsize(dest) / 1024.0, out["wall_clock_seconds"]))


def _have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Parameter ledger for Approximation 4.9: every symbol the approximation needs,
# with its archived source, or UNAVAILABLE.
# ---------------------------------------------------------------------------
PARAM_LEDGER = [
    {"symbol": "T", "role": "threshold / abscissa of the survival curve",
     "status": "AVAILABLE",
     "source": "the integer score index of each line of the archived .out file"},
    {"symbol": "N", "role": "number of short dual vectors; scale of the score "
                            "and variance of the Model 4.7 noise N(0,N/2)",
     "status": "AVAILABLE",
     "source": "avg_N in the .out header (25971.000000 / 25970.000000); "
               "Fig 4.1 caption gives N = 25971 / 25970"},
    {"symbol": "beta_sieve", "role": "exponent of x in lambda(x), eq (4.24)",
     "status": "AVAILABLE",
     "source": "beta_1 in the .out header (44 / 41); Fig 4.1 caption "
               "beta_sieve = 44 / 41 -- the two agree"},
    {"symbol": "n_fft", "role": "exponent of y in mu(y), eq (4.24)",
     "status": "AVAILABLE", "source": ".out header n_fft=8; caption n_fft = 8"},
    {"symbol": "k_fft", "role": "q^{k_fft} in mu(y); also sets the counting "
                                "denominator of the measurement",
     "status": "AVAILABLE", "source": ".out header k_fft=3; caption k_fft = 3"},
    {"symbol": "q", "role": "modulus, in lambda and mu",
     "status": "AVAILABLE", "source": ".out header q=241; caption q = 241"},
    {"symbol": "m", "role": "exponent q^{beta_sieve m/(m+n_lat)} in lambda",
     "status": "AVAILABLE", "source": ".out header m=40; caption m = 40"},
    {"symbol": "n_lat", "role": "same exponent in lambda",
     "status": "AVAILABLE", "source": ".out header n_lat=35 / 42; caption "
                                     "n_lat = 35 / 42"},
    {"symbol": "beta_bkz", "role": "argument of the root-Hermite factor delta "
                                   "in lambda",
     "status": "AVAILABLE",
     "source": ".out header beta_0=32 / 35; caption beta_bkz = 32 / 35"},
    {"symbol": "mu_lsc, sigma_lsc", "role": "psi_lsc, the density of the "
                                            "decoding distance in (4.22)",
     "status": "AVAILABLE",
     "source": ".out header avg_dlsc / sdv_dlsc (23.938828 / 3.378998 and "
               "23.873986 / 3.304260); caption 23.94 / 3.38 and 23.87 / 3.30"},
    {"symbol": "d_lat", "role": "enters Phi (and hence the scale of E(u)) "
                                "through the lattice-side length",
     "status": "AVAILABLE_WITH_DISCREPANCY",
     "source": ".out header avg_dlat = 41.068986 / 57.889159; Fig 4.1 caption "
               "d_lat = 42.00 / 58.60.  The two archived sources disagree by "
               "2.3% / 1.2%.  In this comparison d_lat enters only through the "
               "scale K, which is not archived anyway, so the discrepancy does "
               "not propagate; it is recorded, not resolved."},
    {"symbol": "Phi_{dlsc}(x,y)", "role": "defines the region E(T-t) in (4.23) "
                                          "-- the core of Approximation 4.9",
     "status": "UNAVAILABLE",
     "source": "Introduced with Approximation 4.6, on a page that was not "
               "retrieved.  It appears in NO archived extract and in no other "
               "repository byte (checked across inputs/, knowledge/, ledger/, "
               "coordination/, experiments/).",
     "what_this_blocks": "The region E(u) cannot be evaluated from archived "
                         "text alone.  This comparison therefore adopts an "
                         "EXPLICITLY DECLARED reading -- Phi = exp(-(a x^2 + "
                         "b(dlsc) y^2)) -- which the archived Approximation "
                         "4.8, eq (4.19), forces if (4.19) is N*E[Phi] on the "
                         "good guess.  Under that reading the exponent p = "
                         "(beta_sieve+n_fft)/2 is fixed by archived integers "
                         "and everything unknown collapses into one scale K.  "
                         "A free-exponent diagnostic reports how strongly the "
                         "data prefer that exponent.  If the reading is wrong, "
                         "the exponent is wrong and the shape comparison does "
                         "not bind."},
    {"symbol": "delta(beta_bkz)", "role": "root-Hermite factor in lambda(x), "
                                          "eq (4.24); fixes the absolute "
                                          "density of lattice points",
     "status": "UNAVAILABLE",
     "source": "The function delta(.) and Lemma 2.9 (the volume of Lambda(B')) "
               "are cited by the archived page but defined on pages that were "
               "not retrieved.  No archived extract gives a numerical value.",
     "what_this_blocks": "The ABSOLUTE normalisation of the predicted curve.  "
                         "delta^{beta_sieve(m+n_lat-beta_sieve)} is a factor "
                         "of order delta^{1364} (n=43) / delta^{1394} (n=50); "
                         "a 0.1% change in delta moves the prediction by "
                         "~2 bits, so no useful bound can be substituted.  "
                         "The comparison is consequently a SHAPE comparison "
                         "with one free scale, not an absolute-level test."},
    {"symbol": "alpha", "role": "coefficient in Approximation 4.8 eq (4.19) "
                                "and in the (i,j) locus of the 4.9 "
                                "justification; sets the width of Phi",
     "status": "UNAVAILABLE_FROM_PAPER_EXTRACTS",
     "source": "Appears in NO archived page extract of the paper (as BATCH-008 "
               "flagged).  A candidate archived value exists OUTSIDE the paper: "
               "the archived Pgood .out header carries alpha_secret=2 and "
               "alpha_error=2.  Identifying those with the paper's alpha is NOT "
               "established by any archived text, so no value is assumed here.",
     "what_this_blocks": "Nothing in the shape comparison: alpha enters only "
                         "through a and b, hence only through K.  It would be "
                         "needed for an absolute-level test, which is already "
                         "blocked by delta."},
    {"symbol": "Vol(Lambda(B')), Vol(Lambda(B_lsc))",
     "role": "Gaussian-heuristic denominators behind lambda and mu",
     "status": "PARTIALLY_AVAILABLE",
     "source": "Vol(Lambda(B_lsc)) = q^{n_fft-k_fft} is stated in the archived "
               "justification (page25).  Vol(Lambda(B')) is deferred to "
               "Lemma 2.9, which is not archived; it is already folded into "
               "lambda's delta-power in (4.24), which is archived."},
    {"symbol": "n_lsc", "role": "appears in the archived justification's locus "
                                "(sqrt(alpha beta_sieve/2), sqrt(alpha n_lsc/2))",
     "status": "UNAVAILABLE",
     "source": "Not defined in any archived extract.  It is plausibly n_fft, "
               "but that identification is not archived and is not assumed.",
     "what_this_blocks": "Nothing used here; the locus statement is not part "
                         "of the predicted curve."},
    {"symbol": "nb_iteration", "role": "not a model parameter -- it sets the "
                                       "counting floor of the MEASUREMENT",
     "status": "AVAILABLE_WITH_DISCREPANCY",
     "source": ".out header nb_iteration = 4000 (n=43) and 6000 (n=50).  The "
               "Fig 4.1 caption states 4000 iterations for BOTH panels.  The "
               "header is used, since it is the file's own record of how it "
               "was produced; the discrepancy is recorded, not resolved."},
]


if __name__ == "__main__":
    main()

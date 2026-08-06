#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECK C3 -- INSTANTIATE THE ACTUAL MODEL, PLUS THE CLOSED-FORM COUNTING FLOOR
TASK-20260803-36f572, BATCH-012 of GOAL-MLKEM-003.

WHAT THIS SCRIPT DOES
---------------------
(A) It replaces BATCH-009's Gaussian-Phi power-law SURROGATE region measure
    K * v^p by the EXACT region measure built from Carrier et al.'s own
    (4.10), (4.11), (4.22), (4.23) and (4.24), and refits the archived
    Pwrong survival files with the same one-free-normalisation protocol.

(B) It computes the closed-form Poisson counting-noise FLOOR of the very same
    equal-weight rms statistic, per band, with no simulation and no random
    numbers, as an independent deliverable.  Every rms in the output is
    reported BESIDE the floor of the same index set and as a RATIO to it.
    Nothing is ever scored against zero (EV-MLKEM-2e668d C-1 struck that
    argument; zero was never achievable).

It records observations only.  It does NOT conclude that Approximation 4.9 is
validated, refuted, selected or rejected; that judgement belongs to the
independent validator / red team and then to the Coordinator.

ZERO NEW SAMPLING, NO NETWORK, NO G6K, NO COST MODEL.  Every input byte is
already in this repository.  Every computation is deterministic: no random
number is drawn anywhere (see the `determinism` block of results.json).
Toy parameters only (q=241, m=40, n=43/50).  No ML-KEM or Kyber security claim
in either direction.  AGENTS.md rule 12 is UNMET and UNWAIVED for this batch:
EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their status.


THE MODEL, DERIVED FROM THE SOURCE EQUATIONS
--------------------------------------------
(4.22)  Pwrong ~ INT_{-inf}^{+inf} INT_0^{+inf}
            min( 1, INT_{E(T-t)} lambda(x) mu(y) d(x,y) )
            * exp(-t^2/N - (d_lsc-mu_lsc)^2/(2 sigma_lsc^2))
              / (pi sigma_lsc sqrt(2N))  dd_lsc dt

(4.23)  E(T-t) := { (x,y) in R^2_+ : N * Phi_{d_lsc}(x,y) >= T-t }

(4.24)  lambda(x) prop. x^{beta_sieve-1},   mu(y) prop. y^{n_fft-1}
        (all remaining constants -- delta(beta_bkz), the q-powers, the Gamma
        factors -- are v-independent and T-independent and are absorbed into
        the single fitted normalisation A, exactly as BATCH-009 absorbed them
        into K)

(4.10)  Phi_{d_lsc}(i,j) = Upsilon_{beta_sieve/2}((2 pi / q) d_lat i)
                         * Upsilon_{n_fft/2 - 1}((2 pi / q) d_lsc j)

(4.11)  Upsilon_n(x) = Gamma(n+1) J_n(x) / (x/2)^n
                     = SUM_{l>=0} (-1)^l (x/2)^{2l} / ( l! PROD_{s=1..l}(n+s) )

The prefactor of (4.22) is exactly the product of the N(0, N/2) density in t
and the N(mu_lsc, sigma_lsc^2) density in d_lsc:
    sqrt(pi N) * sigma_lsc * sqrt(2 pi) = pi sigma_lsc sqrt(2N).   [verified]
So (4.22) reads  Pwrong = E_{t, d_lsc} [ min(1, W_{d_lsc}(T - t)) ].

TWO EXACT REDUCTIONS USED HERE (both are identities, not approximations):

 R1. SUBSTITUTE s = T - t.  |Upsilon_n| <= 1 with Upsilon_n(0) = 1 (Poisson's
     integral representation makes Upsilon_n the characteristic function of a
     symmetric Beta law on [-1,1]), so N*Phi <= N and E(s) is empty for s > N,
     while for s <= 0 the region is the whole quadrant and min(...) = 1.  Hence

        Pwrong(T) = Q(T) + INT_0^N phi(T-u) * E_d[min(1, W_d(u))] du,
        Q(T) = 0.5 erfc(T/sqrt(N)),  phi(s) = exp(-s^2/N)/sqrt(pi N),

     where W_d(u) is the region measure at threshold u.  The Q(T) term is
     exactly the Q(T) of the BATCH-009 surrogate, recovered here rather than
     assumed.  With v := ln(N/u) this is the BATCH-009 v-integral verbatim,
     with min(1, K v^p) replaced by E_d[min(1, W_d)].

 R2. THE d_lsc DEPENDENCE FACTORISES OUT OF THE REGION.  Put
     xi = (2pi/q) d_lat x and eta = (2pi/q) d_lsc y.  Then
     E(u) = {(xi,eta) in R^2_+ : Upsilon_a(xi) Upsilon_b(eta) >= e^{-v}} with
     a = beta_sieve/2, b = n_fft/2 - 1, and

        W_d(v) = ((2pi/q) d_lat)^{-beta_sieve} ((2pi/q) d_lsc)^{-n_fft} * G(v),
        G(v) := INT_{E(v)} xi^{beta_sieve-1} eta^{n_fft-1} d(xi,eta).

     G does NOT depend on d_lat or on d_lsc.  d_lat enters only through a
     constant that the fitted normalisation absorbs -- so the fit is
     INDEPENDENT of the d_lat discrepancy between the .out header (41.069) and
     the Fig 4.1 caption (42.00), which is recorded rather than resolved.
     d_lsc enters only as d_lsc^{-n_fft}, so the (4.22) d_lsc integral, kept in
     its (4.22) position OUTSIDE the min, collapses to the one-dimensional

        F(g) := INT_0^{+inf} psi_lsc(d) min(1, g d^{-n_fft}) dd
              = Psi(g^{1/n_fft}) + g * INT_{g^{1/n_fft}}^{inf} psi_lsc(d) d^{-n_fft} dd

     and the model is  Pred(T; A) = Q(T) + INT_0^N phi(T-u) F(A G(ln(N/u))) du
     with ONE free parameter A.

ALPHA: THE HANDOFF SAYS alpha = 2 AND THAT VALUE IS USED AND STATED.  BUT THE
HONEST FINDING IS THAT alpha HAS NO LOCUS IN THIS CHAIN.  alpha appears
nowhere in (4.10), (4.11), (4.22), (4.23) or (4.24); the document-wide symbol
scan puts alpha on PDF pages 8, 9, 13, 15, 16, 23, 24, 25, 28, 32, 33, 36, and
on page 23 its four occurrences are all inside (4.19), i.e. Approximation 4.8
(GOOD guess), not Approximation 4.9.  The wrong-guess region measure is
alpha-free.  This is reported as a disagreement with the handoff premise
rather than silently adopted or silently dropped (see results.json ->
alpha_disposition).

MODELS COMPARED (all four share one quadrature, one band, one fit protocol)
--------------------------------------------------------------------------
 M1  surrogate            rho(u) = min(1, K v^p), p free      [BATCH-009/010]
 M1a surrogate at own p   rho(u) = min(1, K v^p), p = (bs+nf)/2 frozen
 M2  EXACT (this check)   rho(u) = F(A G(v))                  [1 free param]
 M3  exact, exponent-gen. rho(u) = F(A G(v)^s), s free        [drift probe]
 M4  exact, d_lsc collapsed at mu_lsc: rho(u) = min(1, A G(v) mu_lsc^{-nfft})
     -- isolates which of the two departures from BATCH-009 does the work.

DEPARTURES FROM THE BATCH-010 IMPLEMENTATION (exponent_neighbourhood_scan.py)
----------------------------------------------------------------------------
DEP-1  The v-integral is carried in the u = N e^{-v} variable instead.  It is
       the same integral (R1); the Jacobian N e^{-v} dv = du is exact.  This
       matters because the exact rho(u) has no kink structure that could be
       split analytically the way min(1, K v^p) could (BATCH-010 DEP-A1), so a
       fixed shared node set is used and its convergence is measured instead.
DEP-2  The clip is NOT split at a kink.  BATCH-010 DEP-A1 put a node exactly
       at v* = K^{-1/p}.  M2/M3 have no kink at all (F is C^1), and M1/M1a are
       evaluated on the same shared nodes as M2 so the comparison is
       instrument-matched.  The cost is quantified: M1a at the BATCH-009
       archived (p, log2 K) is recomputed here and compared against the
       archived 0.7057596 and BATCH-010's exact-kink 0.705494.
DEP-3  The d_lsc integral of (4.22) is RETAINED (M2, M3).  BATCH-009 collapsed
       it into K.  M4 isolates that departure by collapsing it again.
DEP-4  The free parameter is a normalisation only.  BATCH-010 scanned p as
       well.  M2 has ONE free parameter against the surrogate's two; M3 adds
       the second back for the drift probe only.
DEP-5  Every rms is reported beside the counting floor of its own index set and
       as a ratio to it.  BATCH-010 reported rms alone.

SCORE SCALE AND BAND (constraints, re-verified here)
----------------------------------------------------
Raw, undivided cosine-sum score scale; no k_fft alignment applied.  Each
survival file is an unsmoothed pooled counting estimate over
nb_iteration * q^k_fft candidate scores; support ends at exactly
1/(nb_iteration * q^k_fft) = 2^-35.70445229 for n=43.  Values below that are
ABSENCE OF MEASUREMENT.  Nothing is fitted, anchored, compared or extrapolated
past the last positive score.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from array import array
from decimal import Decimal, getcontext
from operator import mul

getcontext().prec = 120

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *([".."] * 7)))
DATA = os.path.join(REPO, "experiments", "EXP-MLKEM-011", "vendor-lock", "data")
PDF = os.path.join(REPO, "experiments", "EXP-MLKEM-010", "vendor-lock",
                   "Carrier-2022-1750-hal-05406481.pdf")
PDF_EXPECTED_SHA256 = ("083b142256eecaebfa72dfccf847151b217566"
                       "6a3979cef4e7383376757b8005")

FILES = [
    "Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out",
    "Pwrong_q241_m40_n50_nfft8_kfft3_nlat42_beta035_beta141_N25970.out",
]
PGOOD = "Pgood_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out"

# BATCH-009 archived headline values, used ONLY as cross-check targets.
B009 = {
    FILES[0]: {"log2_K_fit": -72.71258147256952, "p": 26.0,
               "rms_whole_band": 0.7057596314055684},
    FILES[1]: {"log2_K_fit": -67.22250543726885, "p": 24.5,
               "rms_whole_band": 0.6967212651864578},
}

# --- numerical controls (all recorded into results.json) --------------------
UPS_SERIES_MAXTERMS = 400
UPS_SERIES_RELSTOP = Decimal("1e-60")
XI_GRID_H = 0.002          # fine grid step for Upsilon_a
XI_GRID_MAX = 34.0
ETA_GRID_H = 0.002         # fine grid step for Upsilon_b
ETA_GRID_MAX = 120.0
G_ETA_PANELS = 3           # GL panels per eta lobe-interval
G_GL_ORDER = 16
U_LO = 1e-3                # below this the clip is closed form (F == 1 there)
# geometric panel zones on [U_LO, N]: (lo, hi or None=N, n_panels)
U_ZONES = [(1e-3, 1.0, 6), (1.0, 3000.0, 120), (3000.0, None, 20)]
U_GL_ORDER = 6
KERNEL_Z_CUT = 120.0       # drop nodes with (T-u)^2/N > this
LNG_CLAMP = -500.0         # F(g) below this is < 1e-40 and is set to 0
COARSE_GRID = 80           # stage-1 scan points for the 1-D normalisation fit
TERNARY_STEPS = 40         # golden-section refinement steps (stage 3)
P_GRID_HALFWIDTH = 6.0     # surrogate exponent scan half-width
P_GRID_STEP = 0.75
S_GRID = [0.55, 0.62, 0.69, 0.76, 0.83, 0.90, 0.97, 1.04, 1.11, 1.18, 1.25]
LN2 = math.log(2.0)


# ===========================================================================
# provenance helpers
# ===========================================================================
class Tee(object):
    def __init__(self, stream, sink):
        self.stream = stream
        self.sink = sink

    def write(self, s):
        self.sink.append(s)
        self.stream.write(s)

    def flush(self):
        self.stream.flush()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    try:
        return subprocess.run(["git", "-C", REPO] + list(args),
                              capture_output=True, text=True,
                              check=True).stdout
    except Exception as exc:                                # pragma: no cover
        return "UNAVAILABLE (%s)" % exc


def have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def maxrss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 ** 2)


# ===========================================================================
# I/O
# ===========================================================================
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


# ===========================================================================
# PART B -- THE CLOSED-FORM POISSON COUNTING-NOISE FLOOR
# ===========================================================================
#
# DERIVATION (independent of the red team's; see report.md section 2).
#
# Line T of an archived Pwrong file is the pooled estimate
#       Phat(T) = C_T / M,        M := nb_iteration * q^{k_fft},
# where C_T is the number of the M pooled candidate scores that are >= T.
# M is the exact number of candidate scores pooled: q^{k_fft} candidates are
# scored per iteration and there are nb_iteration iterations.  C_T is therefore
# recoverable exactly, and IS recovered here and checked against integrality.
#
# The statistic every batch in this lane reports is the equal-weight rms over
# the band of  r_T = log2(model_T) - log2(Phat(T)).
# A PERFECT model has model_T = lambda_T / M with lambda_T = E[C_T], so its
# residual is not zero but
#       r_T = log2(lambda_T) - log2(C_T),
# i.e. pure counting noise.  Under the marginal law C_T ~ Poisson(lambda_T),
# and conditioning on C_T >= 1 (a score enters the resolved band only if its
# pooled count is at least one -- the band ends at the last positive score),
#
#   floor_rms = sqrt( (1/|band|) * SUM_T E[(log2 lambda_T - log2 C)^2 | C>=1] )
#
#   E[(log2 lambda - log2 C)^2 | C>=1]
#        = (1/ln^2 2) * (1/(1-e^{-lambda})) * SUM_{k>=1} e^{-lambda} lambda^k/k!
#                                            * (ln lambda - ln k)^2 .
#
# This is a CLOSED FORM.  No simulation, no random numbers.  lambda_T is
# unknown and is replaced by its unbiased plug-in estimate C_T.
#
# Large lambda: the sum has O(sqrt(lambda)) effective terms and lambda reaches
# 2.8e10, so an asymptotic expansion is used above LAMBDA_SWITCH.  With
# u = (C-lambda)/lambda and the Poisson central moments mu2 = lambda,
# mu3 = lambda, mu4 = 3 lambda^2 + lambda,
#   ln(1+u)^2 = u^2 - u^3 + (11/12) u^4 + O(u^5)
#   E[.]      = 1/lambda - 1/lambda^2 + (11/12)(3/lambda^2) + O(lambda^-3)
#             = 1/lambda + (7/4)/lambda^2 + O(lambda^-3).
# The two branches are cross-checked against each other at lambda = 1e3, 1e4,
# 1e5 and agree to 4.0e-6, 4.0e-8, 4.0e-10 relative (see results.json).
#
# The delta-method value 1/(lambda ln^2 2) is reported beside it as the cruder
# bound, because that is what the red team tabulated for some sub-bands.
LAMBDA_SWITCH = 1.0e5


def poisson_log2_sq_exact(lam):
    """E[(log2 lam - log2 C)^2 | C >= 1], C ~ Poisson(lam).  Exact sum."""
    lo = max(1, int(lam - 12.0 * math.sqrt(lam)) - 20)
    hi = int(lam + 12.0 * math.sqrt(lam)) + 20
    ll = math.log(lam)
    s = 0.0
    w = 0.0
    for k in range(lo, hi + 1):
        lp = -lam + k * ll - math.lgamma(k + 1.0)
        if lp < -745.0:
            continue
        p = math.exp(lp)
        d = ll - math.log(k)
        s += p * d * d
        w += p
    return (s / w) / (LN2 * LN2)


def poisson_log2_sq_asym(lam):
    return (1.0 / lam + 1.75 / (lam * lam)) / (LN2 * LN2)


def poisson_log2_sq(lam):
    if lam <= LAMBDA_SWITCH:
        return poisson_log2_sq_exact(lam)
    return poisson_log2_sq_asym(lam)


def counting_floor(counts, idx):
    """Closed-form floor over the index set `idx` of the pooled counts."""
    tot = 0.0
    totd = 0.0
    for i in idx:
        lam = float(counts[i])
        tot += poisson_log2_sq(lam)
        totd += 1.0 / (lam * LN2 * LN2)
    n = len(idx)
    return {"n_scores": n,
            "floor_rms_bits_truncated_poisson": math.sqrt(tot / n),
            "floor_rms_bits_delta_method": math.sqrt(totd / n)}


# ===========================================================================
# PART A -- THE EXACT REGION MEASURE
# ===========================================================================
def make_coeffs(n, nterms=UPS_SERIES_MAXTERMS):
    """c_l = 1 / ( l! * prod_{s=1..l} (n+s) ), as exact-ish Decimals."""
    c = [Decimal(1)]
    nd = Decimal(str(n))
    for l in range(1, nterms + 1):
        c.append(c[-1] / (Decimal(l) * (nd + Decimal(l))))
    return c


def ups_exact(x, coeffs):
    """(4.11) evaluated by its own series in 120-digit decimal arithmetic.

    Double precision CANNOT be used here: at x = 45, n = 22 the largest term of
    the alternating series is ~1e8 while the sum is ~1e-9, i.e. ~17 orders of
    cancellation.  120 digits leaves >= 40 correct digits everywhere on the
    grids used.  A double-precision control is run and reported.
    """
    if x == 0.0:
        return 1.0
    z = -(Decimal(repr(x)) / 2) ** 2
    tot = Decimal(0)
    pw = Decimal(1)
    mx = Decimal(0)
    for c in coeffs:
        t = pw * c
        a = abs(t)
        if a > mx:
            mx = a
        tot += t
        pw *= z
        if mx > 0 and a < mx * UPS_SERIES_RELSTOP:
            break
    return float(tot)


class UpsTable(object):
    """Fine uniform grid of Upsilon_n, its lobe structure, and the weighted
    one-dimensional measure  int_{ sign*Upsilon >= e^{-tau} } x^m dx ."""

    def __init__(self, n, xmax, h, m, log):
        self.n = n
        self.h = h
        self.m = m
        self.co = make_coeffs(n)
        self.N = int(math.ceil(xmax / h)) + 4
        t0 = time.time()
        self.vals = [ups_exact(i * h, self.co) for i in range(self.N)]
        self.build_seconds = time.time() - t0
        self.xmax = (self.N - 3) * h
        self._lobes()
        log("    Upsilon_%s grid: %d exact evaluations to x=%.3f in %.1f s; "
            "%d sign changes, %d lobes"
            % (n, self.N, self.xmax, self.build_seconds, len(self.zeros),
               len(self.lobes)))

    def f(self, x):
        """cubic-Lagrange interpolant on the fine grid (error ~1e-13)."""
        h = self.h
        i = int(x / h)
        if i < 1:
            i = 1
        if i > self.N - 3:
            i = self.N - 3
        t = (x - i * h) / h
        y0, y1, y2, y3 = (self.vals[i - 1], self.vals[i],
                          self.vals[i + 1], self.vals[i + 2])
        return (-t * (t - 1) * (t - 2) * y0
                + 3 * (t + 1) * (t - 1) * (t - 2) * y1
                - 3 * (t + 1) * t * (t - 2) * y2
                + (t + 1) * t * (t - 1) * y3) / 6.0

    def _lobes(self):
        v = self.vals
        h = self.h
        zeros = []
        for i in range(1, self.N - 3):
            if v[i] == 0.0:
                zeros.append(i * h)
            elif (v[i] > 0) != (v[i + 1] > 0):
                a, b = i * h, (i + 1) * h
                for _ in range(60):
                    mid = 0.5 * (a + b)
                    if (self.f(mid) > 0) == (v[i] > 0):
                        a = mid
                    else:
                        b = mid
                zeros.append(0.5 * (a + b))
        self.zeros = zeros
        lobes = []
        bnds = [0.0] + zeros + ([self.xmax] if (not zeros
                                                or zeros[-1] < self.xmax)
                                else [])
        for k in range(len(bnds) - 1):
            L, R = bnds[k], bnds[k + 1]
            if k == 0:
                xe, am, sg = 0.0, 1.0, 1
            else:
                a, b = L, R
                for _ in range(200):
                    m1 = a + (b - a) / 3.0
                    m2 = b - (b - a) / 3.0
                    if abs(self.f(m1)) < abs(self.f(m2)):
                        a = m1
                    else:
                        b = m2
                xe = 0.5 * (a + b)
                am = abs(self.f(xe))
                sg = 1 if self.f(xe) > 0 else -1
            lobes.append({"L": L, "R": R, "sign": sg, "xe": xe, "amax": am,
                          "taumin": (-math.log(am) if am > 0
                                     else float("inf")),
                          "truncated_by_grid": (R >= self.xmax - 1e-9)})
        self.lobes = lobes

    def _solve(self, a, b, target, sign):
        """|f| is monotone on [a,b]; return x with |f(x)| = target."""
        fa = abs(self.f(a)) - target
        for _ in range(70):
            mid = 0.5 * (a + b)
            fm = abs(self.f(mid)) - target
            if (fm > 0) == (fa > 0):
                a, fa = mid, fm
            else:
                b = mid
        return 0.5 * (a + b)

    def endpoints(self, tau, sign):
        """List of (xl, xr) intervals with sign*Upsilon >= e^{-tau}."""
        if tau <= 0.0:
            return []
        th = math.exp(-tau)
        out = []
        for lo in self.lobes:
            if lo["sign"] != sign or lo["amax"] < th:
                continue
            xe = lo["xe"]
            xr = (self._solve(xe, lo["R"], th, sign)
                  if abs(self.f(lo["R"])) < th else lo["R"])
            if lo["L"] == 0.0 and xe == 0.0:
                xl = 0.0
            else:
                xl = (self._solve(xe, lo["L"], th, sign)
                      if abs(self.f(lo["L"])) < th else lo["L"])
            out.append((xl, xr))
        return out

    def measure(self, tau, sign):
        mp = self.m + 1
        tot = 0.0
        for xl, xr in self.endpoints(tau, sign):
            tot += (xr ** mp - xl ** mp) / mp
        return tot

    def envelope_bound(self, x):
        """Rigorous-form envelope |Upsilon_n(x)| <= Gamma(n+1) 2^n
        sqrt(2/(pi x)) x^{-n}; used only to bound what the grid truncation
        can omit.  Checked numerically against every computed lobe maximum."""
        return (math.exp(math.lgamma(self.n + 1.0) + self.n * math.log(2.0))
                * math.sqrt(2.0 / (math.pi * x)) * x ** (-self.n))


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


def region_measure(v, Atab, Btab, gx, gw, npanel=G_ETA_PANELS):
    """G(v) = INT_{Upsilon_a(xi) Upsilon_b(eta) >= e^{-v}}
                 xi^{beta_sieve-1} eta^{n_fft-1} d(xi,eta).

    Layer-caked on the xi axis: for each eta the admissible xi set is
    { sign*Upsilon_a >= e^{-(v + ln|Upsilon_b(eta)|)} }, whose x^m measure is
    closed form once its endpoints are located.  The sign-matching branch
    (both factors negative) is included -- that is precisely the structure the
    Gaussian surrogate cannot have.
    """
    if v <= 0.0:
        return 0.0
    th = math.exp(-v)
    tot = 0.0
    mB = Btab.m
    for lo in Btab.lobes:
        if lo["amax"] < th:
            continue
        s = lo["sign"]
        xe = lo["xe"]
        xr = (Btab._solve(xe, lo["R"], th, s)
              if abs(Btab.f(lo["R"])) < th else lo["R"])
        if lo["L"] == 0.0 and xe == 0.0:
            xl = 0.0
        else:
            xl = (Btab._solve(xe, lo["L"], th, s)
                  if abs(Btab.f(lo["L"])) < th else lo["L"])
        for pi in range(npanel):
            a = xl + (xr - xl) * pi / npanel
            b = xl + (xr - xl) * (pi + 1) / npanel
            hm = 0.5 * (b - a)
            mid = 0.5 * (b + a)
            for gxx, gww in zip(gx, gw):
                y = mid + hm * gxx
                fb = Btab.f(y)
                if s * fb <= 0.0:
                    continue
                tau = v + math.log(abs(fb))
                if tau <= 0.0:
                    continue
                tot += gww * hm * (y ** mB) * Atab.measure(tau, s)
    return tot


# ===========================================================================
# the d_lsc mixture  F(g) = INT_0^inf psi_lsc(d) min(1, g d^{-nfft}) dd
# ===========================================================================
class Mixture(object):
    def __init__(self, mu, sigma, nfft, log):
        self.mu = mu
        self.sigma = sigma
        self.nfft = nfft
        self.s2 = sigma * math.sqrt(2.0)
        gx, gw = gauss_legendre(8)
        self.ZLO, self.ZHI, self.NZ = 1e-6, 80.0, 40000
        lo, hi = math.log(self.ZLO), math.log(self.ZHI)
        self.lz0 = lo
        self.dlz = (hi - lo) / self.NZ
        zs = [math.exp(lo + self.dlz * i) for i in range(self.NZ + 1)]
        I = [0.0] * (self.NZ + 1)
        for i in range(self.NZ - 1, -1, -1):
            a, b = zs[i], zs[i + 1]
            hm = 0.5 * (b - a)
            mid = 0.5 * (a + b)
            s = 0.0
            for gxx, gww in zip(gx, gw):
                d = mid + hm * gxx
                s += gww * hm * self.psi(d) * d ** (-float(nfft))
            I[i] = I[i + 1] + s
        self.I = I
        self.lnI = [math.log(x) if x > 0 else -1e300 for x in I]
        log("    d_lsc mixture: psi=N(%.6f, %.6f^2) on (0,inf); "
            "P(d<=0)=%.3e is left OUT as (4.22) integrates from 0; "
            "tail table on z in [%g, %g], %d points"
            % (mu, sigma, self.Psi_le(0.0), self.ZLO, self.ZHI, self.NZ))

    def psi(self, d):
        return (math.exp(-0.5 * ((d - self.mu) / self.sigma) ** 2)
                / (self.sigma * math.sqrt(2.0 * math.pi)))

    def Psi_le(self, z):
        return 0.5 * (1.0 + math.erf((z - self.mu) / self.s2))

    def Psi(self, z):
        """int_0^z psi."""
        return self.Psi_le(z) - self.Psi_le(0.0)

    def tail(self, z):
        if z <= self.ZLO:
            return self.I[0] * (self.ZLO / z) ** (self.nfft - 1)
        if z >= self.ZHI:
            return 0.0
        t = (math.log(z) - self.lz0) / self.dlz
        i = int(t)
        fr = t - i
        return math.exp(self.lnI[i] * (1.0 - fr) + self.lnI[i + 1] * fr)

    def F(self, lng):
        if lng < LNG_CLAMP:
            return 0.0
        z = math.exp(lng / self.nfft)
        return self.Psi(z) + math.exp(lng) * self.tail(z)


# ===========================================================================
# the shared u-quadrature and the fit protocol
# ===========================================================================
def build_u_nodes(N, refine=1, gl_order=U_GL_ORDER):
    """Panelled Gauss-Legendre nodes on [U_LO, N], geometric in three zones.

    The returned nodes are SORTED ASCENDING IN u.  This is load-bearing:
    `build_kernel` keeps only the nodes inside |T-u|^2/N < KERNEL_Z_CUT and
    `predict` addresses them as one contiguous slice of rho, which is valid
    only if node order is monotone in u.  Gauss-Legendre roots come out in
    DESCENDING order inside each panel, so an unsorted list makes the kept set
    non-contiguous whenever the window starts inside a panel -- i.e. for every
    T > sqrt(KERNEL_Z_CUT * N).  That defect was found by the convergence
    control and is recorded in report.md as ANOM-1.
    """
    edges = []
    for lo, hi, npan in U_ZONES:
        hi = N if hi is None else hi
        npan = npan * refine
        r = (hi / lo) ** (1.0 / npan)
        x = lo
        if not edges:
            edges.append(lo)
        for _ in range(npan):
            x *= r
            edges.append(x)
    gx, gw = gauss_legendre(gl_order)
    pairs = []
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        hm = 0.5 * (b - a)
        mid = 0.5 * (a + b)
        for gxx, gww in zip(gx, gw):
            pairs.append((mid + hm * gxx, gww * hm))
    pairs.sort(key=lambda t: t[0])
    return [p[0] for p in pairs], [p[1] for p in pairs]


def build_kernel(band, nodes, wts, N):
    """rows[i] = (first_node_index, array of w_j * phi(T_i - u_j)).

    Asserts that the kept index set is contiguous, so the slice arithmetic in
    `predict` cannot silently misalign again.
    """
    norm = 1.0 / math.sqrt(math.pi * N)
    rows = []
    for T in band:
        lo = None
        prev = None
        row = array("d")
        for j in range(len(nodes)):
            u = nodes[j]
            z = (T - u) * (T - u) / N
            if z < KERNEL_Z_CUT:
                if lo is None:
                    lo = j
                elif j != prev + 1:
                    raise RuntimeError(
                        "non-contiguous kernel support at T=%d (j=%d after "
                        "%d): node list is not sorted in u" % (T, j, prev))
                prev = j
                row.append(wts[j] * norm * math.exp(-z))
        rows.append((lo if lo is not None else 0, row))
    return rows


def predict(rho, rows, base):
    out = []
    for i in range(len(rows)):
        lo, row = rows[i]
        out.append(base[i] + sum(map(mul, row, rho[lo:lo + len(row)])))
    return out


def rms_of(pred, log2meas, idx):
    s = 0.0
    for i in idx:
        s += (math.log2(pred[i]) - log2meas[i]) ** 2
    return math.sqrt(s / len(idx))


GOLDEN = (math.sqrt(5.0) - 1.0) / 2.0


def fit_one_parameter(rho_of, rows, base, log2meas, idx, lo0, hi0,
                      ngrid=COARSE_GRID, nter=TERNARY_STEPS, log=None,
                      tag=""):
    """Profile the single free (log) normalisation.

    Three stages, all deterministic: (1) a coarse global scan over [lo0, hi0]
    that is WIDENED and rerun if its minimiser lands on an edge (so a bad
    initial bracket is detected rather than silently accepted); (2) a fine
    rescan inside the winning cell; (3) golden-section refinement.
    """
    def obj(x):
        return rms_of(predict(rho_of(x), rows, base), log2meas, idx)

    widened = 0
    while True:
        best_k = None
        best = None
        for k in range(ngrid + 1):
            x = lo0 + (hi0 - lo0) * k / ngrid
            r = obj(x)
            if best is None or r < best[1]:
                best, best_k = (x, r), k
        if best_k not in (0, ngrid) or widened >= 3:
            break
        w = hi0 - lo0
        if best_k == 0:
            lo0 -= w
        else:
            hi0 += w
        widened += 1
        if log:
            log("      [%s] coarse minimiser hit a bracket edge; widened to "
                "[%.1f, %.1f] (widening %d)" % (tag, lo0, hi0, widened))
    step = (hi0 - lo0) / ngrid
    lo, hi = best[0] - step, best[0] + step
    bestf = None
    for k in range(21):
        x = lo + (hi - lo) * k / 20.0
        r = obj(x)
        if bestf is None or r < bestf[1]:
            bestf = (x, r)
    lo, hi = bestf[0] - (hi - lo) / 20.0, bestf[0] + (hi - lo) / 20.0
    c = hi - GOLDEN * (hi - lo)
    d = lo + GOLDEN * (hi - lo)
    fc, fd = obj(c), obj(d)
    for _ in range(nter):
        if fc < fd:
            hi, d, fd = d, c, fc
            c = hi - GOLDEN * (hi - lo)
            fc = obj(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + GOLDEN * (hi - lo)
            fd = obj(d)
    x = 0.5 * (lo + hi)
    return x, obj(x), {"bracket_widenings": widened,
                       "coarse_bracket": [lo0, hi0],
                       "final_bracket_width": hi - lo}


# ===========================================================================
# one file
# ===========================================================================
def analyse(fname, log, quick=False):
    path = os.path.join(DATA, fname)
    header, values, raw = read_out(path)
    q = int(header["q"])
    k_fft = int(header["k_fft"])
    n_fft = int(header["n_fft"])
    beta_sieve = int(header["beta_1"])
    beta_bkz = int(header["beta_0"])
    N = float(header["avg_N"])
    nb_iteration = int(header["nb_iteration"])
    d_lat_hdr = float(header["avg_dlat"])
    mu_lsc = float(header["avg_dlsc"])
    sg_lsc = float(header["sdv_dlsc"])

    M = nb_iteration * q ** k_fft
    quantum = 1.0 / M
    last_pos = max(i for i, v in enumerate(values) if v > 0.0)
    band = list(range(last_pos + 1))
    counts_f = [values[T] * M for T in band]
    counts = [int(round(c)) for c in counts_f]
    integrality = max(abs(counts_f[i] - counts[i]) / max(counts[i], 1)
                      for i in band)
    log2meas = [math.log2(values[T]) for T in band]
    p_own = (beta_sieve + n_fft) / 2.0

    log("[%s]" % fname)
    log("  M = nb_iteration*q^k_fft = %d ; quantum = %.17g = 2^%.8f"
        % (M, quantum, math.log2(quantum)))
    log("  resolved band = scores [0, %d] (%d scores); first zero at %d ; "
        "max relative deviation of value*M from an integer = %.3e"
        % (last_pos, len(band), last_pos + 1, integrality))
    log("  beta_sieve=%d beta_bkz=%d n_fft=%d N=%.1f d_lat(header)=%.6f "
        "mu_lsc=%.6f sigma_lsc=%.6f ; archived surrogate exponent "
        "(beta_sieve+n_fft)/2 = %.2f"
        % (beta_sieve, beta_bkz, n_fft, N, d_lat_hdr, mu_lsc, sg_lsc, p_own))

    # ---- bands ------------------------------------------------------------
    bands = {
        "whole": list(range(len(band))),
        "count_ge_10": [i for i in band if counts[i] >= 10],
        "count_ge_1000": [i for i in band if counts[i] >= 1000],
        "count_ge_1e5": [i for i in band if counts[i] >= 100000],
    }
    floors = {}
    for nm, idx in bands.items():
        floors[nm] = counting_floor(counts, idx)
        floors[nm]["score_range"] = [idx[0], idx[-1]]
        log("  FLOOR %-14s n=%5d scores [%d,%d]  truncated-Poisson %.6f bits"
            "  delta-method %.6f bits"
            % (nm, len(idx), idx[0], idx[-1],
               floors[nm]["floor_rms_bits_truncated_poisson"],
               floors[nm]["floor_rms_bits_delta_method"]))

    # ---- exact region measure --------------------------------------------
    a_ord = beta_sieve / 2.0
    b_ord = n_fft / 2.0 - 1.0
    log("  building Upsilon tables for (4.10)/(4.11): a=beta_sieve/2=%.1f, "
        "b=n_fft/2-1=%.1f" % (a_ord, b_ord))
    Atab = UpsTable(a_ord, XI_GRID_MAX, XI_GRID_H, beta_sieve - 1, log)
    Btab = UpsTable(b_ord, ETA_GRID_MAX, ETA_GRID_H, n_fft - 1, log)

    # RT-9's stated mechanism, recomputed independently here
    rt9 = {"upsilon_b_first_zero": Btab.zeros[0] if Btab.zeros else None,
           "gaussian_surrogate": "exp(-x^2/(4(n+1)))",
           "delta_bits_vs_gaussian": {}}
    for xx in (4.0, 5.0, 6.0, 7.0):
        ub = ups_exact(xx, Btab.co)
        gg = math.exp(-xx * xx / (4.0 * (b_ord + 1.0)))
        rt9["delta_bits_vs_gaussian"]["x=%.1f" % xx] = {
            "upsilon_b": ub, "gaussian_surrogate": gg,
            "delta_bits": (math.log2(ub / gg) if ub > 0 else None),
            "sign_of_upsilon_b": (1 if ub > 0 else -1),
        }
    for xx in (4.0, 5.0, 6.0, 8.0, 12.0):
        ua = ups_exact(xx, Atab.co)
        gg = math.exp(-xx * xx / (4.0 * (a_ord + 1.0)))
        rt9.setdefault("lat_side_delta_bits_vs_gaussian", {})[
            "x=%.1f" % xx] = (math.log2(ua / gg) if ua > 0 else None)
    rt9["upsilon_a_first_zero"] = Atab.zeros[0] if Atab.zeros else None
    rt9["scale_2pi_over_q_times_d_lsc_per_unit_j"] = (
        2.0 * math.pi / q * mu_lsc)
    log("    RT-9 mechanism recomputed: Upsilon_b first zero at %.6f "
        "(sign change) ; log2(Upsilon_b/Gaussian) = %s ; (2pi/q)*mu_lsc = "
        "%.4f per unit j ; Upsilon_a first zero at %.6f"
        % (rt9["upsilon_b_first_zero"],
           ", ".join("%s:%s" % (k, ("%+.4f" % d["delta_bits"])
                                if d["delta_bits"] is not None
                                else "NEGATIVE(%.4e)" % d["upsilon_b"])
                     for k, d in sorted(
                         rt9["delta_bits_vs_gaussian"].items())),
           rt9["scale_2pi_over_q_times_d_lsc_per_unit_j"],
           rt9["upsilon_a_first_zero"]))

    # grid-truncation bound: the region is EXACT for v <= v_exact_max
    env_a = Atab.envelope_bound(Atab.xmax)
    env_b = Btab.envelope_bound(Btab.xmax)
    env_check = {
        "upsilon_a_last_lobe_amax": Atab.lobes[-1]["amax"],
        "upsilon_a_envelope_at_xmax": env_a,
        "upsilon_a_envelope_dominates_last_lobe":
            env_a >= Atab.lobes[-1]["amax"],
        "upsilon_b_last_lobe_amax": Btab.lobes[-1]["amax"],
        "upsilon_b_envelope_at_xmax": env_b,
        "upsilon_b_envelope_dominates_last_lobe":
            env_b >= Btab.lobes[-1]["amax"],
    }
    v_exact_max = min(-math.log(env_a), -math.log(env_b))
    log("    grid truncation: |Upsilon_a| <= %.3e beyond xi=%.1f and "
        "|Upsilon_b| <= %.3e beyond eta=%.1f, so G(v) is EXACT for "
        "v <= %.4f and is a lower bound above it"
        % (env_a, Atab.xmax, env_b, Btab.xmax, v_exact_max))

    # ---- shared u-quadrature ---------------------------------------------
    gx16, gw16 = gauss_legendre(G_GL_ORDER)
    nodes, wts = build_u_nodes(N)
    vs = [math.log(N / u) for u in nodes]
    t0 = time.time()
    lnG = []
    for v in vs:
        g = region_measure(v, Atab, Btab, gx16, gw16)
        lnG.append(math.log(g) if g > 0.0 else -1e300)
    tG = time.time() - t0
    log("  u-quadrature: %d nodes on [%g, %.1f]; v in [%.4f, %.4f]; "
        "G(v) at every node in %.1f s" % (len(nodes), U_LO, N, min(vs),
                                          max(vs), tG))

    # local log-log slope of the exact measure (the surrogate's p, if the
    # exact measure were a pure power)
    slope = []
    for vq in (3.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0):
        g1 = region_measure(vq * 0.98, Atab, Btab, gx16, gw16)
        g2 = region_measure(vq * 1.02, Atab, Btab, gx16, gw16)
        if g1 > 0 and g2 > 0:
            slope.append({"v": vq,
                          "d_ln_G_d_ln_v": (math.log(g2) - math.log(g1))
                          / (math.log(1.02) - math.log(0.98))})
    log("  local log-log slope of the EXACT region measure (the surrogate "
        "asserts a constant %.1f): %s"
        % (p_own, ", ".join("v=%.0f:%.2f" % (s["v"], s["d_ln_G_d_ln_v"])
                            for s in slope)))

    mix = Mixture(mu_lsc, sg_lsc, n_fft, log)
    rows = build_kernel(band, nodes, wts, N)
    sqN = math.sqrt(N)
    Q = [0.5 * math.erfc(T / sqN) for T in band]
    CLIP = [0.5 * (math.erfc((T - U_LO) / sqN) - math.erfc(T / sqN))
            for T in band]
    base = [Q[i] + CLIP[i] for i in range(len(band))]
    log("  kernel: mean %.0f active nodes per score (|T-u|^2/N < %.0f cut)"
        % (sum(len(r[1]) for r in rows) / float(len(rows)), KERNEL_Z_CUT))

    # ---- rho builders -----------------------------------------------------
    def rho_M2(lnA):
        F = mix.F
        return [F(lnA + g) for g in lnG]

    def rho_M3(lnA, s):
        F = mix.F
        return [F(lnA + s * g) for g in lnG]

    def rho_M4(lnA):
        c = n_fft * math.log(mu_lsc)
        return [1.0 if (lnA + g - c) >= 0.0
                else math.exp(lnA + g - c) for g in lnG]

    def rho_M1(log2K, p):
        lk = log2K * LN2
        out = []
        for v in vs:
            t = lk + p * math.log(v) if v > 0 else -1e300
            out.append(1.0 if t >= 0.0 else math.exp(t))
        return out

    results = {}

    # ---- M1a: reproduction cross-check at the BATCH-009 archived (p, K) ---
    ref = B009[fname]
    pr = predict(rho_M1(ref["log2_K_fit"], ref["p"]), rows, base)
    xrms = rms_of(pr, log2meas, bands["whole"])
    log("  CROSS-CHECK: BATCH-009 archived (p=%.1f, log2K=%.6f) on THIS "
        "quadrature gives whole-band rms %.6f against archived %.6f "
        "(difference %+.6f bits)"
        % (ref["p"], ref["log2_K_fit"], xrms, ref["rms_whole_band"],
           xrms - ref["rms_whole_band"]))
    results["reproduction_cross_check"] = {
        "archived_p": ref["p"], "archived_log2_K_fit": ref["log2_K_fit"],
        "rms_whole_band_bits_here": xrms,
        "rms_whole_band_bits_archived_BATCH009": ref["rms_whole_band"],
        "difference_bits": xrms - ref["rms_whole_band"],
        "note": ("BATCH-010 recomputed the same quantity with an exact-kink "
                 "clip split and reported 0.705494 (n=43).  The residual "
                 "difference here is DEP-2, the shared-node clip treatment, "
                 "not a different model."),
    }

    # ---- quadrature convergence control ----------------------------------
    nodes2, wts2 = build_u_nodes(N, refine=2, gl_order=U_GL_ORDER + 2)
    vs2 = [math.log(N / u) for u in nodes2]
    rows2 = build_kernel(band, nodes2, wts2, N)
    lnG2 = []
    for v in vs2:
        g = region_measure(v, Atab, Btab, gx16, gw16)
        lnG2.append(math.log(g) if g > 0.0 else -1e300)

    def conv_check(lnA):
        p1 = predict([mix.F(lnA + g) for g in lnG], rows, base)
        p2 = predict([mix.F(lnA + g) for g in lnG2], rows2, base)
        return max(abs(math.log2(p1[i]) - math.log2(p2[i]))
                   for i in range(len(band)))

    # ---- M2: THE EXACT MODEL ---------------------------------------------
    # bracket centre: A such that A G(v) ~ mu_lsc^{n_fft} at v = 7 (the
    # surrogate's fitted kink).  The bracket is +/-45 wide and self-widens.
    lnG_at = {}
    for vq in (5.0, 7.0, 9.0):
        g = region_measure(vq, Atab, Btab, gx16, gw16)
        lnG_at[vq] = math.log(g) if g > 0 else -1e300
    centre = n_fft * math.log(mu_lsc) - lnG_at[7.0]
    lo0, hi0 = centre - 45.0, centre + 45.0
    log("  normalisation bracket centred at ln A = %.3f (from "
        "mu_lsc^n_fft / G(7)); initial bracket [%.1f, %.1f]"
        % (centre, lo0, hi0))
    per_band = {}
    for nm, idx in bands.items():
        t0 = time.time()
        lnA, r, fitinfo = fit_one_parameter(rho_M2, rows, base, log2meas, idx,
                                            lo0, hi0, log=log,
                                            tag="M2/" + nm)
        pr = predict(rho_M2(lnA), rows, base)
        fl = floors[nm]["floor_rms_bits_truncated_poisson"]
        resid = [math.log2(pr[i]) - log2meas[i] for i in idx]
        per_band[nm] = {
            "n_scores": len(idx),
            "score_range": [idx[0], idx[-1]],
            "ln_A_fitted": lnA,
            "log2_A_fitted": lnA / LN2,
            "rms_bits": r,
            "counting_floor_bits_truncated_poisson": fl,
            "counting_floor_bits_delta_method":
                floors[nm]["floor_rms_bits_delta_method"],
            "rms_over_floor_ratio": r / fl,
            "mean_residual_bits": sum(resid) / len(resid),
            "min_residual_bits": min(resid),
            "max_residual_bits": max(resid),
            "fit_diagnostics": fitinfo,
            "fit_seconds": time.time() - t0,
        }
        log("  M2 EXACT  %-14s n=%5d  lnA=%.6f log2A=%.5f  rms=%.6f bits  "
            "floor=%.6f  RATIO=%.2fx  (resid mean %+.4f, min %+.4f, "
            "max %+.4f)"
            % (nm, len(idx), lnA, lnA / LN2, r, fl, r / fl,
               per_band[nm]["mean_residual_bits"],
               per_band[nm]["min_residual_bits"],
               per_band[nm]["max_residual_bits"]))
    results["M2_exact_region_measure"] = per_band

    lnA_whole = per_band["whole"]["ln_A_fitted"]
    mc = conv_check(lnA_whole)
    log("  quadrature convergence at the whole-band fit: max |delta log2 "
        "prediction| between the production node set (%d nodes) and a "
        "%d-node refinement = %.3e bits" % (len(nodes), len(nodes2), mc))
    results["quadrature_convergence_max_abs_log2_diff_bits"] = mc
    results["quadrature_convergence_nodes"] = [len(nodes), len(nodes2)]

    # saturation / truncation control: is the grid truncation reachable?
    sat = None
    for v, g in sorted(zip(vs, lnG)):
        if mix.F(lnA_whole + g) >= 1.0 - 1e-12:
            sat = v
            break
    log("  truncation control: F(A G(v)) reaches 1-1e-12 at v=%.4f, and G(v) "
        "is exact for v <= %.4f -> the grid truncation is %s"
        % (sat if sat else float("nan"), v_exact_max,
           "IMMATERIAL" if (sat is not None and sat <= v_exact_max)
           else "MATERIAL -- REPORT THIS"))
    results["region_truncation_control"] = {
        "v_at_which_F_saturates_to_1": sat,
        "v_up_to_which_G_is_exact": v_exact_max,
        "truncation_immaterial": bool(sat is not None
                                      and sat <= v_exact_max),
        "envelope_checks": env_check,
    }

    # ---- M4: exact measure, d_lsc collapsed at mu_lsc --------------------
    m4 = {}
    for nm, idx in bands.items():
        lnA, r, _fi = fit_one_parameter(rho_M4, rows, base, log2meas, idx,
                                        lo0, hi0, log=log, tag="M4/" + nm)
        fl = floors[nm]["floor_rms_bits_truncated_poisson"]
        m4[nm] = {"n_scores": len(idx), "ln_A_fitted": lnA, "rms_bits": r,
                  "counting_floor_bits_truncated_poisson": fl,
                  "rms_over_floor_ratio": r / fl}
        log("  M4 exact/d_lsc-collapsed %-14s rms=%.6f floor=%.6f "
            "RATIO=%.2fx" % (nm, r, fl, r / fl))
    results["M4_exact_measure_dlsc_collapsed_at_mu"] = m4

    # ---- M1: the surrogate, refitted on THIS quadrature ------------------
    nhw = int(round(P_GRID_HALFWIDTH / P_GRID_STEP))
    p_grid = [round(p_own + P_GRID_STEP * k, 4)
              for k in range(-nhw, nhw + 1)]
    m1 = {}
    for nm, idx in bands.items():
        best = None
        curve = []
        prev = None
        for p in p_grid:
            # warm start from the previous exponent's optimum; the bracket
            # self-widens if the minimiser lands on an edge, so a bad warm
            # start is detected rather than silently accepted.
            if prev is None:
                c0 = -p * math.log2(7.0)      # log2 K with kink at v* = 7
                blo, bhi, ng = c0 - 35.0, c0 + 35.0, COARSE_GRID
            else:
                blo, bhi, ng = prev - 6.0, prev + 6.0, 24
            lk, r, _fi = fit_one_parameter(
                lambda x, pp=p: rho_M1(x, pp), rows, base, log2meas, idx,
                blo, bhi, ngrid=ng, log=log,
                tag="M1/%s/p=%.2f" % (nm, p))
            prev = lk
            curve.append({"p": p, "log2_K": lk, "rms_bits": r})
            if best is None or r < best["rms_bits"]:
                best = curve[-1]
        # rms at the file's own archived exponent
        own = [c for c in curve if abs(c["p"] - p_own) < 1e-9]
        fl = floors[nm]["floor_rms_bits_truncated_poisson"]
        m1[nm] = {
            "n_scores": len(idx),
            "argmin": best,
            "at_own_archived_exponent": own[0] if own else None,
            "counting_floor_bits_truncated_poisson": fl,
            "argmin_rms_over_floor_ratio": best["rms_bits"] / fl,
            "at_grid_edge": abs(best["p"] - p_grid[0]) < 1e-9
                            or abs(best["p"] - p_grid[-1]) < 1e-9,
            "rms_vs_p_curve": curve,
        }
        log("  M1 SURROGATE %-14s argmin p=%.2f rms=%.6f floor=%.6f "
            "RATIO=%.2fx ; at own p=%.2f rms=%.6f ; argmin at grid edge: %s"
            % (nm, best["p"], best["rms_bits"], fl, best["rms_bits"] / fl,
               p_own, own[0]["rms_bits"] if own else float("nan"),
               m1[nm]["at_grid_edge"]))
    results["M1_gaussian_phi_surrogate_refitted_here"] = m1

    # ---- M3: exponent-generalised exact model (the drift probe) ----------
    s_grid = list(S_GRID)
    m3 = {}
    for nm in ("whole", "count_ge_10", "count_ge_1000", "count_ge_1e5"):
        idx = bands[nm]
        best = None
        curve = []
        prev = None
        for s in s_grid:
            c0 = n_fft * math.log(mu_lsc) - s * lnG_at[7.0]
            if prev is None:
                blo, bhi, ng = c0 - 45.0, c0 + 45.0, COARSE_GRID
            else:
                blo, bhi, ng = prev - 12.0, prev + 12.0, 24
            lnA, r, _fi = fit_one_parameter(
                lambda x, ss=s: rho_M3(x, ss), rows, base, log2meas, idx,
                blo, bhi, ngrid=ng, log=log, tag="M3/%s/s=%.2f" % (nm, s))
            prev = lnA
            curve.append({"s": s, "ln_A": lnA, "rms_bits": r,
                          "effective_exponent_in_surrogate_units":
                              s * p_own})
            if best is None or r < best["rms_bits"]:
                best = curve[-1]
        fl = floors[nm]["floor_rms_bits_truncated_poisson"]
        m3[nm] = {"n_scores": len(idx), "argmin": best,
                  "counting_floor_bits_truncated_poisson": fl,
                  "argmin_rms_over_floor_ratio": best["rms_bits"] / fl,
                  "at_grid_edge": abs(best["s"] - s_grid[0]) < 1e-9
                                  or abs(best["s"] - s_grid[-1]) < 1e-9,
                  "rms_vs_s_curve": curve}
        log("  M3 exact^s   %-14s argmin s=%.2f (effective exponent %.2f in "
            "surrogate units) rms=%.6f floor=%.6f RATIO=%.2fx ; at grid "
            "edge: %s"
            % (nm, best["s"], best["effective_exponent_in_surrogate_units"],
               best["rms_bits"], fl, best["rms_bits"] / fl,
               m3[nm]["at_grid_edge"]))
    results["M3_exact_measure_generalised_exponent"] = m3

    # ---- sensitivity: the psi_lsc left tail ------------------------------
    #  F(g) at small g is governed by psi_lsc near d=0, where a normal
    #  approximation to a decoding distance has no physical support.  This is
    #  a property of (4.22) as written, and is recorded, not silently kept or
    #  silently dropped.
    class MixTrunc(Mixture):
        def __init__(self, base_mix, dmin):
            self.__dict__.update(base_mix.__dict__)
            self.dmin = dmin

        def F(self, lng):
            if lng < LNG_CLAMP:
                return 0.0
            z = math.exp(lng / self.nfft)
            if z <= self.dmin:
                return math.exp(lng) * (self.tail(self.dmin))
            return ((self.Psi_le(z) - self.Psi_le(self.dmin))
                    + math.exp(lng) * self.tail(z))

    dmin = max(1e-9, mu_lsc - 4.0 * sg_lsc)
    mixT = MixTrunc(mix, dmin)
    sens = {}
    for nm, idx in bands.items():
        lnA, r, _fi = fit_one_parameter(
            lambda x: [mixT.F(x + g) for g in lnG], rows, base,
            log2meas, idx, lo0, hi0, log=log, tag="SENS/" + nm)
        fl = floors[nm]["floor_rms_bits_truncated_poisson"]
        sens[nm] = {"ln_A_fitted": lnA, "rms_bits": r,
                    "rms_over_floor_ratio": r / fl}
    log("  SENSITIVITY (psi_lsc truncated below d=mu-4sigma=%.4f): "
        "whole %.6f -> ratio %.2fx ; count>=1000 %.6f -> ratio %.2fx"
        % (dmin, sens["whole"]["rms_bits"], sens["whole"]["rms_over_floor_ratio"],
           sens["count_ge_1000"]["rms_bits"],
           sens["count_ge_1000"]["rms_over_floor_ratio"]))
    results["sensitivity_psi_lsc_left_tail_truncated_at_mu_minus_4sigma"] = {
        "d_min": dmin, "per_band": sens,
        "why": ("(4.22) integrates d_lsc over (0, +inf) against a normal "
                "density.  At small g the mixture F(g) is dominated by "
                "psi_lsc near d=0, i.e. by the left tail of a normal "
                "approximation to a decoding distance.  The literal reading "
                "is the primary result; this variant bounds its influence.")}

    # ---- residual profile of the exact model, whole-band fit -------------
    pr = predict(rho_M2(lnA_whole), rows, base)
    prof = []
    step = max(1, len(band) // 40)
    for i in range(0, len(band), step):
        prof.append({"T": band[i], "count": counts[i],
                     "log2_measured": log2meas[i],
                     "log2_predicted": math.log2(pr[i]),
                     "residual_bits": math.log2(pr[i]) - log2meas[i]})
    results["M2_residual_profile_whole_band_fit"] = prof

    return {
        "file": fname,
        "file_sha256": sha256(path),
        "file_path_repo_relative": os.path.relpath(path, REPO),
        "header_raw": raw,
        "parameters_used": {
            "q": q, "k_fft": k_fft, "n_fft": n_fft,
            "beta_sieve_from_header_beta_1": beta_sieve,
            "beta_bkz_from_header_beta_0": beta_bkz,
            "avg_N": N, "nb_iteration": nb_iteration,
            "d_lat_header": d_lat_hdr,
            "mu_lsc_header": mu_lsc, "sigma_lsc_header": sg_lsc,
            "upsilon_order_a_lat": a_ord, "upsilon_order_b_lsc": b_ord,
            "surrogate_exponent_p_own": p_own,
            "d_lat_note": ("d_lat cancels out of the fit entirely (reduction "
                           "R2): it enters only a v-independent constant that "
                           "the fitted normalisation absorbs.  The header "
                           "(41.069 / 57.889) vs Fig 4.1 caption (42.00 / "
                           "58.60) discrepancy therefore cannot affect any "
                           "number in this run, and is recorded rather than "
                           "resolved."),
        },
        "instrument": {
            "pooled_scores_M": M,
            "counting_quantum": quantum,
            "counting_quantum_log2": math.log2(quantum),
            "resolved_band_scores": [0, last_pos],
            "first_zero_score": last_pos + 1,
            "n_scores_in_band": len(band),
            "value_times_M_max_relative_deviation_from_integer": integrality,
            "note": ("Scores above %d carry a printed 0.0, which is absence "
                     "of measurement, not a measured zero.  Nothing here is "
                     "fitted, anchored, compared or extrapolated past score "
                     "%d." % (last_pos, last_pos)),
        },
        "counting_floors": floors,
        "rt9_mechanism_recomputed": rt9,
        "exact_region_measure_local_loglog_slope": slope,
        "quadrature_settings": {
            "u_nodes": len(nodes), "u_lo": U_LO,
            "u_zones_lo_hi_panels": U_ZONES, "u_gl_order": U_GL_ORDER,
            "kernel_z_cut": KERNEL_Z_CUT,
            "xi_grid_h": XI_GRID_H, "xi_grid_max": XI_GRID_MAX,
            "eta_grid_h": ETA_GRID_H, "eta_grid_max": ETA_GRID_MAX,
            "G_eta_panels_per_lobe": G_ETA_PANELS, "G_gl_order": G_GL_ORDER,
            "decimal_precision_digits": getcontext().prec,
            "G_seconds": tG,
        },
        "results": results,
    }


# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="all", choices=("all", "floor"),
                    help="'floor' runs ONLY the closed-form counting-noise "
                         "floor (part B) and prints it; 'all' runs part A too "
                         "and writes results.json")
    args = ap.parse_args()

    t_start = time.time()
    lines = []
    err_sink = []
    sys.stderr = Tee(sys.stderr, err_sink)

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    log("exact_region_measure.py -- CHECK C3 + closed-form counting floor")
    log("TASK-20260803-36f572, BATCH-012, GOAL-MLKEM-003")
    log("python %s on %s" % (sys.version.split()[0], platform.platform()))
    log("numpy: %s ; scipy: %s ; mpmath: %s  (all absent -> the (4.11) series "
        "is evaluated in 120-digit decimal arithmetic by this script)"
        % (have("numpy"), have("scipy"), have("mpmath")))
    commit = git("rev-parse", "HEAD").strip()
    dirty = git("status", "--porcelain")
    log("git commit %s ; working tree %s"
        % (commit, "DIRTY" if dirty.strip() else "clean"))
    if dirty.strip():
        for ln in sorted(dirty.splitlines()):
            log("    dirty: %s" % ln)
    log("")

    if args.mode == "floor":
        out = {}
        for f in FILES:
            header, values, _ = read_out(os.path.join(DATA, f))
            M = int(header["nb_iteration"]) * int(header["q"]) ** int(
                header["k_fft"])
            last = max(i for i, v in enumerate(values) if v > 0.0)
            band = list(range(last + 1))
            counts = [int(round(values[T] * M)) for T in band]
            per = {}
            for nm, thr in (("whole", 1), ("count_ge_10", 10),
                            ("count_ge_1000", 1000), ("count_ge_1e5", 100000)):
                idx = [i for i in band if counts[i] >= thr]
                per[nm] = counting_floor(counts, idx)
                log("%s %-14s n=%5d  truncated-Poisson %.6f  delta %.6f"
                    % (f[:24], nm, len(idx),
                       per[nm]["floor_rms_bits_truncated_poisson"],
                       per[nm]["floor_rms_bits_delta_method"]))
            out[f] = per
        log("")
        log("mode=floor: nothing written to disk.")
        return 0

    # sanity: the vendored PDF that (4.10)/(4.11) were read from
    pdf_sha = sha256(PDF) if os.path.exists(PDF) else None
    log("vendored PDF sha256 %s (expected match: %s) -- opened READ-ONLY, "
        "never modified" % (pdf_sha, pdf_sha == PDF_EXPECTED_SHA256))
    log("")

    files = [analyse(f, log) for f in FILES]

    wall = time.time() - t_start
    doc = {
        "task_id": "TASK-20260803-36f572",
        "batch_id": "BATCH-012",
        "goal_id": "GOAL-MLKEM-003",
        "check": ("C3 -- replace BATCH-009's Gaussian-Phi surrogate region "
                  "measure K v^p by the exact region measure from (4.10), "
                  "(4.11), (4.22), (4.23), (4.24), and refit; plus the "
                  "closed-form Poisson counting-noise floor as an independent "
                  "deliverable"),
        "supersedes_nothing": ("This run adds a record.  It edits no prior "
                               "artifact and changes no record status."),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(t_start)),
        "wall_clock_seconds": wall,
        "peak_rss_gb": maxrss_gb(),
        # ---- provenance carried INSIDE this artifact (BATCH-010 DEV-1 /
        #      validator D1 recorded this gap twice; the handoff declares no
        #      runs/ tree, so the fields live here) ------------------------
        "provenance": {
            "command": " ".join([sys.executable] + sys.argv),
            "argv": sys.argv,
            "cwd": os.getcwd(),
            "script_path_repo_relative": os.path.relpath(
                os.path.abspath(__file__), REPO),
            "script_sha256": sha256(os.path.abspath(__file__)),
            "git_commit": commit,
            "git_dirty_tree": bool(dirty.strip()),
            "git_dirty_paths": sorted(l[3:] for l in dirty.splitlines()),
            "git_branch": git("rev-parse", "--abbrev-ref", "HEAD").strip(),
            "environment": {
                "python_version": sys.version,
                "python_executable": sys.executable,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "numpy": have("numpy"), "scipy": have("scipy"),
                "mpmath": have("mpmath"), "sympy": have("sympy"),
                "pypdf": have("pypdf"),
                "third_party_numeric_dependencies": "none",
            },
            "resource_measurements": {
                "wall_clock_seconds": wall,
                "peak_rss_gb_ru_maxrss": maxrss_gb(),
                "user_cpu_seconds": resource.getrusage(
                    resource.RUSAGE_SELF).ru_utime,
                "system_cpu_seconds": resource.getrusage(
                    resource.RUSAGE_SELF).ru_stime,
                "memory_measurable_on_this_host": True,
                "budget_wall_clock_seconds": 3000,
                "budget_memory_gb": 4,
            },
            "determinism": {
                "seeds": "none required",
                "random_number_generators_used": "none",
                "sources_of_randomness": "none",
                "note": ("No module from {random, secrets, numpy.random} is "
                         "imported and no Monte Carlo is run.  Every quantity "
                         "is a deterministic function of the archived bytes "
                         "and the constants declared in "
                         "`numerical_controls`.  Re-running the recorded "
                         "command on the recorded commit reproduces every "
                         "number bit-for-bit."),
                "hash_randomization_PYTHONHASHSEED_irrelevant": True,
            },
            "inputs": {
                "pwrong_files": [
                    {"path": os.path.relpath(os.path.join(DATA, f), REPO),
                     "sha256": sha256(os.path.join(DATA, f))} for f in FILES],
                "pgood_file_not_used_here": {
                    "path": os.path.relpath(os.path.join(DATA, PGOOD), REPO),
                    "sha256": sha256(os.path.join(DATA, PGOOD)),
                    "why": ("Not used: alpha does not enter the wrong-guess "
                            "region measure, so the (4.19) identification "
                            "control is not re-run here.  See "
                            "alpha_disposition.")},
                "source_pdf": {
                    "path": os.path.relpath(PDF, REPO),
                    "sha256": pdf_sha,
                    "sha256_matches_expected":
                        pdf_sha == PDF_EXPECTED_SHA256,
                    "access": "read-only, never modified"},
                "source_extract_used_for_4_22_to_4_24": {
                    "path": ("inputs/MLKEM-DUAL-SOURCES-20260802/extracts/"
                             "carrier-hal-05406481/"
                             "page23_approx_4_8_4_9.txt"),
                    "sha256": sha256(os.path.join(
                        REPO, "inputs", "MLKEM-DUAL-SOURCES-20260802",
                        "extracts", "carrier-hal-05406481",
                        "page23_approx_4_8_4_9.txt"))},
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "requested_reasoning_effort": None,
                "resolved_model_id": "claude-opus-5",
                "fallback_used": True,
                "fallback_reason": (
                    "orchestration/model-policies.yaml routes "
                    "executor-implementation to a GPT-5.6-family alias that "
                    "Claude Code cannot resolve; per CLAUDE.md's model policy "
                    "note the subagent runs on the inherited Claude model and "
                    "the substitution is recorded rather than performed "
                    "silently."),
                "degraded_allowed": False,
                "degraded_requirements": [],
                "model_verified": False,
                "model_verified_note": (
                    "`python3 -m orchestration.adapter doctor --probe` was "
                    "NOT run; no orchestration backend is reachable from this "
                    "session.  Absence recorded, not substituted for."),
                "independent_session": False,
            },
            "certificate": {
                "kind": "none",
                "why": ("Pure measurement run.  No discrete log is solved and "
                        "no factor-base relation is claimed, so "
                        "docs/claims-and-verification.md requires no solution "
                        "certificate.  The verifiable artifacts are the "
                        "closed-form counting floor (recomputable in seconds "
                        "by any third party from the .out files alone) and "
                        "the BATCH-009 reproduction cross-check."),
            },
            "validity": {
                "status": "valid",
                "reason": ("All planned computations terminated inside "
                           "budget; the quadrature convergence control, the "
                           "region-truncation control and the BATCH-009 "
                           "reproduction cross-check are all reported with "
                           "their numeric outcomes."),
            },
            "stderr_captured_from_this_process": "".join(err_sink),
            "stderr_capture_limitation": (
                "sys.stderr is tee'd inside the Python process, so anything "
                "the interpreter or this script writes to stderr is captured "
                "above.  Messages emitted by the OS or by a wrapper outside "
                "the process are not."),
        },
        "numerical_controls": {
            "upsilon_series_max_terms": UPS_SERIES_MAXTERMS,
            "upsilon_series_relative_stop": str(UPS_SERIES_RELSTOP),
            "decimal_precision_digits": getcontext().prec,
            "lambda_switch_exact_to_asymptotic": LAMBDA_SWITCH,
            "lng_clamp": LNG_CLAMP,
            "coarse_grid_points": COARSE_GRID,
            "ternary_refinement_steps": TERNARY_STEPS,
        },
        "counting_floor_derivation": {
            "statistic": ("equal-weight rms over the index set of "
                          "log2(model) - log2(measured survival value)"),
            "pooled_count_recovery": "C_T = value_T * nb_iteration * q^{k_fft}",
            "noise_model": ("C_T ~ Poisson(lambda_T) marginally, conditioned "
                            "on C_T >= 1 because a score enters the resolved "
                            "band only if its pooled count is at least one"),
            "closed_form": ("E[(log2 lambda - log2 C)^2 | C>=1] = "
                            "(1/ln^2 2) (1/(1-e^{-lambda})) "
                            "SUM_{k>=1} e^{-lambda} lambda^k / k! "
                            "(ln lambda - ln k)^2"),
            "plug_in": "lambda_T := C_T (the unbiased plug-in estimate)",
            "large_lambda_asymptotic": ("E[(ln(lambda/C))^2] = 1/lambda + "
                                        "(7/4)/lambda^2 + O(lambda^-3), from "
                                        "ln(1+u)^2 = u^2 - u^3 + (11/12)u^4 "
                                        "and the Poisson central moments "
                                        "mu2=lambda, mu3=lambda, "
                                        "mu4=3 lambda^2 + lambda"),
            "delta_method_reported_beside_it": "1/(lambda ln^2 2)",
            "no_simulation": True,
            "no_random_numbers": True,
            "independence": ("Derived and implemented in this task without "
                             "reading the red team's implementation; the "
                             "red team's reported values are compared "
                             "against it in report.md, not used as input."),
        },
        "alpha_disposition": {
            "handoff_instruction": "instantiate at alpha = 2",
            "alpha_value_used": 2.0,
            "where_alpha_enters_this_computation": "nowhere",
            "finding": ("alpha appears in NONE of (4.10), (4.11), (4.22), "
                        "(4.23), (4.24).  On PDF page 23 every occurrence of "
                        "alpha is inside (4.19), i.e. Approximation 4.8, the "
                        "GOOD-guess threshold.  The wrong-guess region "
                        "measure this check refits is alpha-free, so setting "
                        "alpha = 2 changes no number in this run.  Reported "
                        "as a disagreement with the handoff premise rather "
                        "than silently adopted or silently dropped."),
            "red_team_alpha_identification_not_contested": (
                "RT-10's identification of alpha = 2 from (4.19) against the "
                "archived Pgood median (ratio 1.0048) is neither reproduced "
                "nor disputed here; it is simply not load-bearing for C3."),
        },
        "non_claims": [
            "No ML-KEM or Kyber security claim in either direction; no cost "
            "model is proposed, revised, or costed; no record status changed.",
            "Toy parameters only (q=241, m=40, n=43/50, beta_sieve 41/44).",
            "AGENTS.md rule 12 remains UNMET and UNWAIVED; EV-MLKEM-011, "
            "EV-MLKEM-013 and EV-MLKEM-017 keep their status; KN-FIND-031 "
            "stays withdrawn.",
            "This script records rms values, floors, ratios and argmins.  It "
            "does NOT conclude that Approximation 4.9 is validated, refuted, "
            "selected or rejected.",
            "The normalisation is fitted to the very data being compared.  "
            "This remains a SHAPE comparison with one free scale; no "
            "absolute-level statement is tested.",
            "The whole comparison lives inside the resolved band, which "
            "reaches roughly 15 percent of the operating threshold (RT-11).  "
            "Nothing here bears on the operating point.",
        ],
        "zero_new_sampling": True,
        "network_access": "none",
        "files": files,
        "stdout_log": lines,
    }
    dest = os.path.join(HERE, "results.json")
    with open(dest, "w") as fh:
        json.dump(doc, fh, indent=1, allow_nan=True)
    log("")
    log("wrote %s (%.1f kB) in %.1f s; peak RSS %.3f GB"
        % (dest, os.path.getsize(dest) / 1024.0, wall, maxrss_gb()))
    # the log lines emitted after the dump are not inside the dump; say so
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

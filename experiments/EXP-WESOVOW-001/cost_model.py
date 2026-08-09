#!/usr/bin/env python3
"""
EXP-WESOVOW-001 / TASK-20260724-P13-COST

Concrete cost model of Wesolowski's p^{1/3+o(1)} supersingular isogeny attack
(frozen source: inputs/P13-WESOLOWSKI-2026/paper_fulltext.md, Section 4.1),
extended to the van Oorschot-Wiener middle-memory regime with explicit
superpolynomial-overhead scenarios.

Deterministic, no randomness (seed recorded for form only).
Pure Python stdlib + numpy (scipy/mpmath unavailable in the managed runtime).

Dickman-de Bruijn function rho(u)
---------------------------------
Naive marching of the delay-differential equation rho'(u) = -rho(u-1)/u is
unconditionally ill-conditioned for this experiment: fresh truncation error
scales with rho(u-1) while the solution decays superexponentially, so the
relative error grows roughly like 1/rho(u). This was observed empirically
during development (linear trapezoid marching diverges at u ~ 10 even at
du = 1e-4; a log-domain implicit variant diverges at u ~ 9.5).

Instead rho is computed by Laplace inversion through the real saddle point.
The Laplace transform of rho is  rho_hat(s) = exp(gamma - Ein(s)),  where
gamma is the Euler-Mascheroni constant and Ein(z) = int_0^z (1-e^{-t})/t dt
is the entire "modified exponential integral". Inverting on the vertical
contour through the saddle s = -xi (xi > 0 solving (e^xi - 1)/xi = u):

    rho(u) = (1/2*pi) * int_{-inf}^{inf} exp(u(-xi+i*tau) - Ein(-xi+i*tau)
                                             + gamma) d*tau

The integral is approximated by the trapezoidal rule in tau (spectral for
this entire integrand), and Ein is evaluated by 96-point Gauss-Legendre
quadrature of  Ein(z) = int_0^1 (1 - e^{-z s})/s ds  (no cancellation, since
Re(-z s) = xi*s >= 0 keeps the exponential bounded).

Validation anchors (computed in-script, recorded in raw-result.json):
  * rho(2) against the exact value 1 - ln(2);
  * rho(u), u = 2..8, against an independent fine-grid (du = 1e-5) DDE
    marching solution, which is converged to <1e-4 relative in that range
    (checked by du halving) -- cross-method agreement, not an external claim;
  * rho(10) = 2.7701718e-11 is additionally stable to 7 digits across
    trapezoid steps h in {0.05, 0.02, 0.01, 0.005} (checked during
    development); the literature value 2.7702e-11 is an unverified
    recollection and is NOT used as a control.
"""

import json
import math
import os
import sys
import time

import numpy
from numpy.polynomial.legendre import leggauss

# ---------------------------------------------------------------- parameters
SEED = 0                     # no randomness used; recorded for reproducibility

FIELD_SIZES = [256, 384, 512, 576, 768]          # log2(p)
PAPER_PAIRS = {                                    # paper Sec. 4.1 (log2 time, log2 memory)
    256: (106.5, 92.5),
    384: (157.5, 138.6),
    512: (204.2, 181.3),
    576: (230.9, 206.0),
    768: (302.4, 272.2),
}
MEMORY_BUDGETS = [30, 40, 50, 60, 70, 80]          # log2(w), entries
OVERHEAD_C = [0.0, 0.5, 1.0, 2.0]                  # c in 2^{c*sqrt(log2 p)}
BYTES_PER_ENTRY = [64, 256]

B_GRID_LO, B_GRID_HI, B_GRID_STEP = 1.0, 60.0, 0.1  # log2(B) optimizer grid
SANITY_TOLERANCE_BITS = 0.75

# Dickman grid: u in [1, UMAX], step RHO_DU; Laplace trapezoid h, tail T.
RHO_DU = 0.05
UMAX = 130.0            # covers worst case: p=768, log2B=1 -> w = 0.5 + 767/6 = 128.3
LAP_H = 0.05
LAP_T = 25.0
GL_NODES = 96
EULER_GAMMA = 0.5772156649015328606

RAW_PATH = os.environ.get(
    "WESOVOW_RAW_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "runs", "RUN-WESOVOW-201692-001", "raw-result.json"),
)

_GL_X, _GL_W = leggauss(GL_NODES)
_GL_S = 0.5 * (_GL_X + 1.0)     # nodes mapped to [0,1]
_GL_WS = 0.5 * _GL_W


# ------------------------------------------------- Dickman via Laplace inversion
def _Ein_batch(z):
    """Ein(z) = int_0^1 (1 - e^{-z s})/s ds for a numpy array of complex z."""
    zc = numpy.asarray(z, dtype=complex)[:, None]     # (m,1)
    expo = numpy.exp(-zc * _GL_S[None, :])            # (m,GL)
    vals = (1.0 - expo) / _GL_S[None, :]
    return vals @ _GL_WS                              # (m,)


def _saddle_xi(u):
    """Solve (e^xi - 1)/xi = u for xi > 0 by Newton iteration."""
    xi = math.log(u) + math.log(max(math.log(u), 0.5))
    for _ in range(200):
        e = math.exp(xi)
        f = (e - 1.0) / xi - u
        d = (e * xi - (e - 1.0)) / (xi * xi)
        xi -= f / d
        if abs(f) < 1e-14:
            break
    return xi


def dickman_log2_grid():
    """Return (u_grid, log2_rho_grid) for u in [1, UMAX] step RHO_DU."""
    ug = numpy.arange(1.0, UMAX + 0.5 * RHO_DU, RHO_DU)
    log2rho = numpy.zeros(len(ug))
    # process in chunks to bound memory
    chunk = 64
    for a in range(0, len(ug), chunk):
        us = ug[a:a + chunk]
        xis = numpy.array([_saddle_xi(float(u)) for u in us])
        n = int(round(LAP_T / LAP_H))
        taus = numpy.arange(-n, n + 1) * LAP_H        # (T,)
        ss = -xis[:, None] + 1j * taus[None, :]       # (m,T) complex
        Ein = _Ein_batch(ss.ravel()).reshape(ss.shape)
        integ = numpy.exp(us[:, None] * ss - Ein + EULER_GAMMA)
        rho = (integ.sum(axis=1) * LAP_H / (2.0 * numpy.pi)).real
        log2rho[a:a + chunk] = numpy.log2(numpy.maximum(rho, 1e-300))
    return ug, log2rho


def dickman_log2_marching_check():
    """Independent fine-grid DDE marching solution on [1,9], du=1e-5,
    for cross-method validation (converged in this range)."""
    du = 1e-5
    n = int(round(9.0 / du)) + 1
    rho = numpy.ones(n)
    one = int(round(1.0 / du))
    for i in range(one + 1, n):
        t0 = (i - 1) * du
        t1 = i * du
        f0 = rho[i - 1 - one] / t0
        f1 = rho[i - one] / t1
        rho[i] = rho[i - 1] - 0.5 * (f0 + f1) * du
        if rho[i] <= 0.0:
            rho[i] = 1e-300
    return du, rho


def log2_rho(ug, log2rho, x):
    """Linear interpolation of log2(rho) on the precomputed grid."""
    if x <= 1.0:
        return 0.0
    if x >= ug[-1]:
        raise ValueError(f"u={x} beyond Dickman grid")
    pos = (x - 1.0) / RHO_DU
    i = int(math.floor(pos))
    frac = pos - i
    return log2rho[i] + frac * (log2rho[i + 1] - log2rho[i])


# ------------------------------------------------------------- cost model
def cost_for_B(b2p, log2B, ug, log2rho):
    """All quantities in log2 (entries / F_{p^2}-ops), or None if out of domain."""
    if log2B <= 0:
        return None
    log2X = 0.5 * log2B + (b2p - 1.0) / 6.0
    w = log2X / log2B
    u = (b2p - 1.0) / (3.0 * log2B)
    if w < 1.0 or u < 1.0 or w >= ug[-1]:
        return None
    log2M = 2.0 * log2X + log2_rho(ug, log2rho, w)
    log2P0 = -u * math.log2(u)
    log2T = log2M - log2P0
    return dict(log2B=log2B, log2X=log2X, w=w, u=u,
                log2M=log2M, log2P0=log2P0, log2T=log2T)


def optimize_B(b2p, ug, log2rho):
    best = None
    nsteps = int(round((B_GRID_HI - B_GRID_LO) / B_GRID_STEP)) + 1
    for i in range(nsteps):
        log2B = B_GRID_LO + i * B_GRID_STEP
        r = cost_for_B(b2p, log2B, ug, log2rho)
        if r is not None and (best is None or r["log2T"] < best["log2T"]):
            best = r
    if best is None:
        raise RuntimeError(f"no feasible B on grid for log2(p)={b2p}")
    return best


def main():
    t0 = time.time()

    # ---- Dickman rho grid + validation
    ug, log2rho = dickman_log2_grid()
    rho2_num = 2.0 ** log2_rho(ug, log2rho, 2.0)
    rho2_exact = 1.0 - math.log(2.0)
    rho2_relerr = abs(rho2_num - rho2_exact) / rho2_exact

    du_m, rho_m = dickman_log2_marching_check()
    cross = {}
    max_abs_dlog2 = 0.0
    for x in [2, 3, 4, 5, 6, 7, 8]:
        i = int(round(x / du_m))
        march_log2 = math.log2(max(rho_m[i], 1e-300))
        lap_log2 = log2_rho(ug, log2rho, float(x))
        d = abs(march_log2 - lap_log2)
        max_abs_dlog2 = max(max_abs_dlog2, d)
        cross[f"u={x}"] = {"marching_log2rho": march_log2,
                           "laplace_log2rho": lap_log2,
                           "abs_diff_bits": d}

    validation = {
        "rho2_laplace": rho2_num,
        "rho2_exact_1_minus_ln2": rho2_exact,
        "rho2_relative_error": rho2_relerr,
        "cross_method_marching_du1e-5_vs_laplace": cross,
        "max_abs_diff_bits_u2_to_u8": max_abs_dlog2,
        "note": ("marching solution at du=1e-5 is converged to <1e-4 relative "
                 "for u<=8 (verified by du halving during development); "
                 "agreement with Laplace inversion is a cross-method check."),
    }

    results = {
        "experiment_id": "EXP-WESOVOW-001",
        "run_id": "RUN-WESOVOW-201692-001",
        "seed": SEED,
        "model": {
            "unit_of_cost": "F_{p^2}-operations",
            "unit_of_memory": "table entries",
            "formulas": {
                "log2X": "0.5*log2B + (log2p-1)/6",
                "log2M": "2*log2X + log2(rho(w)), w = log2X/log2B",
                "log2P0": "-u*log2(u), u = (log2p-1)/(3*log2B)",
                "log2Tfull": "log2M - log2P0",
                "T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",
                "T_DG_baseline": "p^{1/2} = 2^{log2p/2}",
                "overhead": "multiply T(w) by 2^{c*sqrt(log2p)}",
            },
            "B_grid": {"log2B_lo": B_GRID_LO, "log2B_hi": B_GRID_HI, "step": B_GRID_STEP},
            "dickman": {
                "method": "Laplace inversion through saddle, trapezoid + Gauss-Legendre Ein",
                "laplace_h": LAP_H, "laplace_T": LAP_T, "gl_nodes": GL_NODES,
                "grid_du": RHO_DU, "grid_umax": UMAX,
                "validation": validation,
            },
        },
        "per_field": {},
    }

    for b2p in FIELD_SIZES:
        opt = optimize_B(b2p, ug, log2rho)
        pt, pm = PAPER_PAIRS[b2p]
        dev_t = opt["log2T"] - pt
        dev_m = opt["log2M"] - pm

        # asymptotic-B comparison: B = exp((1/3)*sqrt(ln(p/2)))
        log2B_asym = (math.sqrt((b2p - 1.0) * math.log(2.0)) / 3.0) / math.log(2.0)
        asym = cost_for_B(b2p, log2B_asym, ug, log2rho)

        log2TDG = b2p / 2.0
        log2M = opt["log2M"]
        log2Tfull = opt["log2T"]

        vow = {}
        for lw in MEMORY_BUDGETS:
            entry = {}
            for c in OVERHEAD_C:
                overhead_bits = c * math.sqrt(b2p)
                log2Tw = (log2Tfull
                          + 0.5 * max(0.0, log2M - lw)
                          + overhead_bits)
                log2speedup = log2TDG - log2Tw
                entry[f"c={c}"] = {
                    "overhead_bits": float(overhead_bits),
                    "log2T_w": float(log2Tw),
                    "log2speedup_vs_DG": float(log2speedup),
                    "beats_baseline": bool(log2speedup > 0.0),
                }
            vow[f"w=2^{lw}"] = entry

        crossovers = {}
        for c in OVERHEAD_C:
            overhead_bits = c * math.sqrt(b2p)
            log2w_star = log2M + 2.0 * (log2Tfull + overhead_bits - log2TDG)
            feasible = bool(log2w_star <= log2M)
            crossovers[f"c={c}"] = {
                "log2w_star_entries": float(log2w_star),
                "feasible_at_or_below_M": feasible,
                "note": ("new attack beats Delfs-Galbraith once w >= w*"
                         if feasible else
                         "no crossover: even at w = M the overhead-inflated time stays above baseline"),
            }

        results["per_field"][f"log2p={b2p}"] = {
            "optimal": opt,
            "B_opt_decimal_approx": 2.0 ** opt["log2B"],
            "asymptotic_B_choice": {"log2B": log2B_asym, **(asym or {})},
            "paper_pair": {"log2time": pt, "log2memory": pm},
            "deviation_bits": {"time": float(dev_t), "memory": float(dev_m),
                               "within_tolerance_0.75bit":
                                   bool(abs(dev_t) <= SANITY_TOLERANCE_BITS and abs(dev_m) <= SANITY_TOLERANCE_BITS)},
            "baseline_log2TDG": log2TDG,
            "van_oorschot_wiener": vow,
            "crossover": crossovers,
            "memory_bytes": {
                "log2M_entries": log2M,
                **{f"log2bytes_{bpe}B_per_entry": log2M + math.log2(bpe)
                   for bpe in BYTES_PER_ENTRY},
            },
            "vow_budget_bytes": {
                f"w=2^{lw}": {f"log2bytes_{bpe}B_per_entry": lw + math.log2(bpe)
                              for bpe in BYTES_PER_ENTRY}
                for lw in MEMORY_BUDGETS
            },
        }

    results["wall_clock_seconds_script"] = time.time() - t0

    os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
    with open(RAW_PATH, "w") as f:
        json.dump(results, f, indent=2, sort_keys=False)

    # ------------------------------------------------------ stdout summary
    print("EXP-WESOVOW-001 / RUN-WESOVOW-001 — cost model observations")
    print(f"Dickman rho: Laplace inversion (h={LAP_H}, T={LAP_T}, GL={GL_NODES}), "
          f"grid du={RHO_DU} umax={UMAX}")
    print(f"  validation: rho(2) relerr vs exact = {rho2_relerr:.2e}; "
          f"max |marching - laplace| over u=2..8 = {max_abs_dlog2:.5f} bits")
    print()
    hdr = (f"{'log2p':>6} {'log2B*':>7} {'B*':>9} {'log2X':>7} {'w':>6} {'u':>6} "
           f"{'log2M':>8} {'log2P0':>8} {'log2T':>8} {'papT':>7} {'dT':>6} {'papM':>7} {'dM':>6}")
    print(hdr)
    for b2p in FIELD_SIZES:
        r = results["per_field"][f"log2p={b2p}"]
        o = r["optimal"]
        d = r["deviation_bits"]
        print(f"{b2p:>6} {o['log2B']:>7.2f} {2.0**o['log2B']:>9.0f} {o['log2X']:>7.2f} "
              f"{o['w']:>6.2f} {o['u']:>6.2f} "
              f"{o['log2M']:>8.2f} {o['log2P0']:>8.2f} {o['log2T']:>8.2f} "
              f"{r['paper_pair']['log2time']:>7.1f} {d['time']:>+6.2f} "
              f"{r['paper_pair']['log2memory']:>7.1f} {d['memory']:>+6.2f}")
    print()
    print("asymptotic B = exp(sqrt(ln(p/2))/3) comparison (log2T at that B):")
    for b2p in FIELD_SIZES:
        r = results["per_field"][f"log2p={b2p}"]
        a = r["asymptotic_B_choice"]
        print(f"  log2p={b2p}: log2B_asym={a['log2B']:.2f} log2T={a['log2T']:.2f} "
              f"(optimized {r['optimal']['log2T']:.2f})")
    print()
    print("vOW middle regime: log2 T(w) / log2 speedup vs Delfs-Galbraith, per overhead scenario")
    for b2p in FIELD_SIZES:
        r = results["per_field"][f"log2p={b2p}"]
        print(f"  log2p={b2p} (log2T_full={r['optimal']['log2T']:.1f}, "
              f"log2M={r['optimal']['log2M']:.1f}, log2TDG={r['baseline_log2TDG']:.0f})")
        for lw in MEMORY_BUDGETS:
            row = f"    w=2^{lw:<3}: "
            for c in OVERHEAD_C:
                e = r["van_oorschot_wiener"][f"w=2^{lw}"][f"c={c}"]
                row += f"c={c}: T=2^{e['log2T_w']:>7.1f} (2^{e['log2speedup_vs_DG']:+.1f}x)  "
            print(row)
        for c in OVERHEAD_C:
            cx = r["crossover"][f"c={c}"]
            print(f"    crossover c={c}: log2 w* = {cx['log2w_star_entries']:.2f} entries "
                  f"({'feasible' if cx['feasible_at_or_below_M'] else 'NO crossover below M'})")
        mb = r["memory_bytes"]
        print(f"    memory: 2^{mb['log2M_entries']:.1f} entries = "
              f"2^{mb['log2bytes_64B_per_entry']:.1f} bytes @64B = "
              f"2^{mb['log2bytes_256B_per_entry']:.1f} bytes @256B")
    print()
    print(f"raw-result.json written to {RAW_PATH}")
    print(f"script wall clock: {results['wall_clock_seconds_script']:.3f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

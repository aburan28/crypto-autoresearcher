#!/usr/bin/env python3
"""CALIB-M0b -- generic big-integer shift/XOR calibration, and the cost-model
re-derivation that consumes it.

TASK-20260803-1b30d8 / GOAL-HQC-001 / BATCH-004.

PURPOSE
-------
Second of the two scripts BATCH-003's feasibility analysis
(.../BATCH-003/tasks/TASK-20260803-c470c0/feasibility_analysis.md, section 9.1)
cites as the source of its machine constants and which existed nowhere in the
repository (validator DEF-3; DEC-20260802-d94a64 D-6).

Two parts, kept strictly separate in the output JSON:

  calibration.m0b   MEASURED. Generic Python big-integer primitives over a
                    round grid of 64-bit limb counts. No HQC quantity appears:
                    the operands are seeded random integers of a stated bit
                    length and nothing else.

  rederivation      DERIVED. Applies the m0 + m0b constants to the parameter
                    sets transcribed from BATCH-003 section 8.1 / 6.3 and from
                    the BATCH-003 red team's O1 table, using BATCH-003's own
                    section 9.2 cost formula, and compares figure by figure
                    against BATCH-003's printed numbers. Nothing in this block
                    is a measurement, and it is labelled as such.

CONSTANTS PRODUCED
------------------
  t_sx(B)     time of one big-integer SHIFT + XOR at B bits          [seconds]
  t_rotxor(B) time of one MASKED CYCLIC ROTATE + XOR-accumulate      [seconds]
              at B bits -- the primitive a cyclic ring product needs
              per set bit of its sparse operand, as opposed to the
              bare shift+xor section 9.1 names
  affine fits of both in limbs W = ceil(B/64):  t = a + b*W

Both are measured because section 9.1 names "shift + xor" while section 9.2
consumes the result as the cost of a sparse cyclic ring product step. Those are
not the same operation and the difference is a property of the machine, so it is
measured rather than argued about.

WHY A LIMB GRID AND NOT THE OPERATING POINTS
--------------------------------------------
BATCH-003's table is quoted at five bit lengths that are HQC ring/truncation
lengths. Measuring there would put an HQC quantity inside a calibration number
and would stop being valid the moment a parameter changed. This script sweeps a
round grid of limb counts spanning and bracketing the whole range instead, fits
an affine model, and lets the rederivation block evaluate the fit wherever it
needs to. Fit residuals are reported so the interpolation error is visible.

DETERMINISM
-----------
Operands come from a seeded PCG64 (seed recorded). Sizes, repetition counts and
the reduction to summary statistics are fixed. Timings vary and are reported with
their spread; every per-repetition sample is retained in the JSON.

USAGE
-----
  python3 calib_m0.py  --out calibration_results.json     # must run first
  python3 calib_m0b.py --out calibration_results.json
  python3 calib_m0b.py --smoke --out /tmp/smoke.json      # fast self-test

`--no-rederive` measures only. The rederivation requires calibration.m0 to be
present in the output file and fails loudly if it is not.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from fractions import Fraction

SCHEMA = "hqc-batch004-calibration/v1"
BLOCK = "m0b"

# ---------------------------------------------------------------------------
# generic helpers (duplicated verbatim from calib_m0.py so each script stands
# alone and neither import creates a __pycache__ directory)
# ---------------------------------------------------------------------------


def _run(cmd):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - environment probing only
        return f"<unavailable: {exc}>"


def environment_block(argv, seed):
    cpu_model = ""
    cache = ""
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name") and not cpu_model:
                    cpu_model = line.split(":", 1)[1].strip()
                if line.startswith("cache size") and not cache:
                    cache = line.split(":", 1)[1].strip()
    except OSError:
        pass
    mem_total = ""
    try:
        with open("/proc/meminfo") as fh:
            mem_total = fh.readline().split(":", 1)[1].strip()
    except OSError:
        pass
    git_commit = _run(["git", "rev-parse", "HEAD"])
    git_dirty_raw = _run(["git", "status", "--porcelain"])
    try:
        import numpy as _np

        numpy_version = _np.__version__
    except Exception:
        numpy_version = "<not imported>"
    return {
        "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": "python3 " + " ".join(argv),
        "cwd": os.getcwd(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_build": " ".join(platform.python_build()),
        "python_int_digit_bits": sys.int_info.bits_per_digit,
        "numpy_version": numpy_version,
        "cpu_model": cpu_model,
        "cpu_cache_size_reported": cache,
        "os_cpu_count": os.cpu_count(),
        "sched_affinity_count": len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None,
        "meminfo_MemTotal": mem_total,
        "loadavg_at_start": os.getloadavg(),
        "git_commit": git_commit,
        "git_dirty_tree": bool(git_dirty_raw),
        "git_dirty_paths": git_dirty_raw.splitlines()[:20],
        "seed": seed,
    }


def summarize(samples, unit):
    s = sorted(samples)
    n = len(s)

    def pct(p):
        if n == 1:
            return s[0]
        idx = p * (n - 1) / 100.0
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return s[lo] * (1 - frac) + s[hi] * frac

    mean = statistics.fmean(s)
    stdev = statistics.stdev(s) if n > 1 else 0.0
    return {
        "unit": unit,
        "n_reps": n,
        "median": statistics.median(s),
        "mean": mean,
        "stdev": stdev,
        "cv": (stdev / mean) if mean else None,
        "min": s[0],
        "max": s[-1],
        "p10": pct(10),
        "p90": pct(90),
        "spread_max_over_min": (s[-1] / s[0]) if s[0] else None,
        "samples": s,
    }


def time_reps(call, work_units, reps, warmup, target_ms, max_inner=1 << 22):
    inner = 1
    while inner < max_inner:
        t0 = time.perf_counter_ns()
        call(inner)
        dt_ms = (time.perf_counter_ns() - t0) / 1e6
        if dt_ms >= target_ms:
            break
        growth = max(2.0, min(8.0, (target_ms / dt_ms) if dt_ms > 0 else 8.0))
        inner = max(inner + 1, int(inner * growth))
    inner = min(inner, max_inner)

    for _ in range(warmup):
        call(inner)

    per_rep = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(reps):
            t0 = time.perf_counter_ns()
            call(inner)
            dt = (time.perf_counter_ns() - t0) / 1e9
            per_rep.append(dt / (inner * work_units))
    finally:
        if gc_was_enabled:
            gc.enable()
    return per_rep, inner


def affine_fit(xs, ys):
    """Ordinary least squares y = a + b*x. Returns dict with residual detail."""
    n = len(xs)
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    pred = [a + b * x for x in xs]
    resid = [y - p for y, p in zip(ys, pred)]
    ss_res = sum(r * r for r in resid)
    ss_tot = sum((y - my) ** 2 for y in ys)
    rel = [abs(r) / y if y else 0.0 for r, y in zip(resid, ys)]
    return {
        "form": "t_seconds = a + b * W,  W = ceil(bits/64)",
        "a_seconds": a,
        "b_seconds_per_limb": b,
        "r_squared": (1 - ss_res / ss_tot) if ss_tot else None,
        "n_points": n,
        "max_abs_relative_residual": max(rel) if rel else None,
        "relative_residuals": {int(x): r for x, r in zip(xs, rel)},
    }


# ---------------------------------------------------------------------------
# measurement: generic big-integer primitives
# ---------------------------------------------------------------------------


def bench_bigint(seed, limb_grid, reps, warmup, target_ms):
    import numpy as np

    rng = np.random.Generator(np.random.PCG64(seed))
    out_sx, out_rot = {}, {}
    for W in limb_grid:
        B = 64 * W
        # seeded, reproducible operands of exactly B bits
        words = rng.integers(0, 2**64, size=W, dtype=np.uint64)
        x = int.from_bytes(bytes(words.tobytes()), "little") | (1 << (B - 1))
        words2 = rng.integers(0, 2**64, size=W, dtype=np.uint64)
        y = int.from_bytes(bytes(words2.tobytes()), "little") | (1 << (B - 1))
        s = B // 3  # generic, non-degenerate shift amount
        mask = (1 << B) - 1

        # (1) the literal primitive section 9.1 names: one shift, one xor
        def call_sx(inner, x=x, y=y, s=s):
            acc = 0
            for _ in range(inner):
                acc = (x >> s) ^ y
            return acc

        per_rep, inner = time_reps(
            call_sx, work_units=1, reps=reps, warmup=warmup, target_ms=target_ms
        )
        out_sx[str(B)] = {
            "bits": B,
            "limbs_W": W,
            "shift_amount": s,
            "inner_iterations_per_rep": inner,
            "seconds_per_op": summarize(per_rep, "seconds_per_operation"),
        }

        # (2) masked cyclic rotate + xor-accumulate: what a cyclic ring product
        #     needs per set bit of the sparse operand
        def call_rot(inner, x=x, y=y, s=s, B=B, mask=mask):
            acc = y
            for _ in range(inner):
                acc ^= ((x << s) | (x >> (B - s))) & mask
            return acc

        per_rep, inner = time_reps(
            call_rot, work_units=1, reps=reps, warmup=warmup, target_ms=target_ms
        )
        out_rot[str(B)] = {
            "bits": B,
            "limbs_W": W,
            "shift_amount": s,
            "inner_iterations_per_rep": inner,
            "seconds_per_op": summarize(per_rep, "seconds_per_operation"),
        }
    return out_sx, out_rot


# ---------------------------------------------------------------------------
# rederivation: BATCH-003's section 9.2 model, this machine's constants
# ---------------------------------------------------------------------------

# Transcribed from feasibility_analysis.md section 8.1 (parameter sets),
# section 6.3 (duplication ladder at the HQC-1 shape) and the BATCH-003 red-team
# report O1 (PS-R2). NOT measured here, NOT endorsed here: inputs to a
# derivation, carried so the comparison is like-for-like.
PARAM_SETS = {
    "PS-A": dict(n=17669, n_e=46, n_2=384, dup=3, omega=66, omega_r=75,
                 omega_e=75, m=16, q="0.0005588",
                 source="feasibility_analysis.md section 8.1 (= true HQC-1)"),
    "PS-R1": dict(n=5923, n_e=46, n_2=128, dup=1, omega=39, omega_r=44,
                  omega_e=44, m=16, q="0.2306",
                  source="feasibility_analysis.md section 8.1 / 6.3"),
    "PS-R3": dict(n=7187, n_e=56, n_2=128, dup=1, omega=45, omega_r=51,
                  omega_e=51, m=17, q="0.370",
                  source="feasibility_analysis.md section 8.1"),
    "PS-R5": dict(n=11549, n_e=90, n_2=128, dup=1, omega=59, omega_r=67,
                  omega_e=67, m=30, q="0.473",
                  source="feasibility_analysis.md section 8.1"),
    "LADDER-dup2": dict(n=11779, n_e=46, n_2=256, dup=2, omega=54, omega_r=61,
                        omega_e=61, m=16, q="0.00894",
                        source="feasibility_analysis.md section 6.3 (HQC-1 shape)"),
    "LADDER-dup3": dict(n=17669, n_e=46, n_2=384, dup=3, omega=66, omega_r=75,
                        omega_e=75, m=16, q="0.000275",
                        source="feasibility_analysis.md section 6.3 (= HQC-1)"),
    "PS-R2-redteam": dict(n=11779, n_e=46, n_2=256, dup=2, omega=62, omega_r=70,
                          omega_e=70, m=16, q="0.21932",
                          source="BATCH-003 red_team_report.md O1"),
}

# BATCH-003's printed figures, for figure-by-figure comparison.
BATCH003_PRINTED = {
    "C_trial_seconds": {"PS-A": 3.35e-4, "PS-R1": 1.17e-4, "PS-R3": 1.47e-4,
                        "PS-R5": 2.47e-4, "LADDER-dup2": 2.18e-4,
                        "PS-R2-redteam": 2.456e-4},
    "C_prod_seconds": {"PS-A": 1.376e-4, "PS-R1": 4.25e-5, "PS-R3": 5.50e-5,
                       "PS-R5": 9.20e-5},
    "C_dec_seconds": {"PS-A": 1.91e-5, "PS-R1": 1.18e-5, "PS-R3": 1.44e-5,
                      "PS-R5": 2.30e-5},
    "C_samp_seconds": {"PS-A": 7.0e-6, "PS-R1": 3.3e-6, "PS-R3": 3.8e-6,
                       "PS-R5": 4.9e-6},
    "trials_per_second_per_core": {"PS-A": 2990, "PS-R1": 8540, "PS-R3": 6790,
                                   "PS-R5": 4050},
    "T_req": {"PS-R1_k16": 2.915e7, "PS-R3_k17": 3.09e5, "PS-R5_k30": 2.72e6,
              "PS-A_k16": 3.40e41, "PS-A_obsq_k4": 3.01e9,
              "LADDER-dup2_k16": 1.473e24, "PS-R2-redteam_k16": 8.164e7},
    "stage_core_seconds": {"A": 1.69e3, "B1": 3.35e4, "B2": 1.17e4,
                           "B3": 2.94e3, "B4": 4.94e3, "C": 1.01e3,
                           "D_optional": 6.74e3},
    "total_mandatory_core_seconds": 5.58e4,
    "total_with_D_core_seconds": 6.25e4,
    "ladder_cost_core_seconds": {"dup1": 3.4e3, "dup2": 3.2e20, "dup3": 9.4e42},
    "machine_constants": {
        "R_add_elem_per_s": 4.0e9,
        "R_add_sweep_low_elem_per_s": 4.3e9,
        "R_add_sweep_high_elem_per_s": 9.8e9,
        "R_add_membound_elem_per_s": 1.8e9,
        "R_xor64_word_per_s": 1.8e9,
        "R_rng_word_per_s": 5.1e7,
        "t_sx_seconds": {5888: 5.12e-7, 7168: 5.67e-7, 11520: 7.47e-7,
                         17669: 9.76e-7, 35851: 1.75e-6},
        "t_sx_fit": {"a": 2.685e-7, "b": 2.646e-9,
                     "form": "t = a + b*W, W = ceil(n/64)"},
    },
}

# Trial allocations, from feasibility_analysis.md section 9.3.
STAGE_PLAN = {
    "A": {"desc": "calibration, all four sets",
          "trials": {"PS-A": 2e6, "PS-R1": 2e6, "PS-R3": 2e6, "PS-R5": 2e6}},
    "B1": {"desc": "PS-A confirmatory, k<=3", "trials": {"PS-A": 1.0e8}},
    "B2": {"desc": "PS-R1 confirmatory, k<=16", "trials": {"PS-R1": 1.0e8}},
    "B3": {"desc": "PS-R3 confirmatory, k<=22", "trials": {"PS-R3": 2.0e7}},
    "B4": {"desc": "PS-R5 confirmatory, k<=32", "trials": {"PS-R5": 2.0e7}},
}
STAGE_C_CARRIED = 1.01e3   # nulls; composition not stated, not re-derivable
STAGE_D_CARRIED = 6.74e3   # optional dilution ladder; composition not stated

RUN_WALL_CAP_S = 3600.0
RUN_CORES = 4
DECLARED_MAX_RUNS = 12


def t_req(n_e, q_str, k, eps=0.5, stab_threshold=30):
    """BATCH-003 section 3's own sizing rule, in exact rational arithmetic.

    T_prec = V/(eps ln2)^2 ; T_stab = 30/P[S >= s_90] ; T_req = max.
    Machine-independent by construction: no calibration constant enters.
    """
    q = Fraction(q_str)
    num = sum(math.comb(k, j) * math.comb(n_e - k, j) * q ** (k + j)
              for j in range(k + 1))
    V = num / (math.comb(n_e, k) * q ** (2 * k)) - 1
    T_prec = float(V) / (eps * math.log(2)) ** 2
    pmf = [math.comb(n_e, s) * q**s * (1 - q) ** (n_e - s) for s in range(n_e + 1)]
    E = math.comb(n_e, k) * q**k
    run, s90 = Fraction(0), None
    for s in range(n_e + 1):
        run += pmf[s] * math.comb(s, k)
        if run >= Fraction(9, 10) * E:
            s90 = s
            break
    tail = sum(pmf[s] for s in range(s90, n_e + 1))
    T_stab = stab_threshold / float(tail)
    return {"V": float(V), "T_prec": T_prec, "s_90": s90,
            "P_S_ge_s90": float(tail), "T_stab": T_stab,
            "T_req": max(T_prec, T_stab)}


def eval_fit(fit, bits):
    W = math.ceil(bits / 64)
    return fit["a_seconds"] + fit["b_seconds_per_limb"] * W


def interp_piecewise(points, x):
    """Piecewise-linear interpolation on measured (batch_size, per_call_seconds).

    Used instead of a global affine fit for the generator. An OLS line through a
    sweep spanning four decades of batch size is dominated by the largest points
    and returns a NEGATIVE intercept, which yields a negative C_samp at the batch
    sizes the model actually evaluates. That is not a small inaccuracy, it is a
    sign error, and it was produced by this task's first derivation run before
    being caught (recorded in cost_model_rederivation.md). Interpolating between
    bracketing MEASURED points cannot go negative and does not extrapolate.
    """
    pts = sorted(points)
    if x <= pts[0][0]:
        # below the smallest measured batch: per-call time cannot fall below the
        # smallest measured per-call time (dispatch overhead floor)
        return pts[0][1]
    if x >= pts[-1][0]:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        slope = (y1 - y0) / (x1 - x0)
        return y1 + slope * (x - x1)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise AssertionError("unreachable")


def cost_model(ps, consts, variant):
    """BATCH-003 section 9.2, evaluated with this machine's constants.

    C_prod  = (omega + omega_r) * t_sx(n)
    C_dec   = ( N + [N if dup>1 else 0] + 896*n_e ) / R_add
    C_samp  = ( 2*omega + 2*omega_r + omega_e ) / R_rng
    C_trial = 2 * (C_prod + C_dec + C_samp)         2x declared contingency
    """
    n, n_e, dup = ps["n"], ps["n_e"], ps["dup"]
    omega, omega_r, omega_e = ps["omega"], ps["omega_r"], ps["omega_e"]
    N = n_e * ps["n_2"]

    n_ring_ops = omega + omega_r
    t_per_ring_op = (consts["t_rotxor_at_n"] if variant["ring_op"] == "rotate_xor"
                     else consts["t_sx_at_n"])
    C_prod = n_ring_ops * t_per_ring_op

    unpack_fold = N + (N if dup > 1 else 0)
    butterflies = 896 * n_e
    if variant["fwht_rate"] == "short_vector":
        C_dec = unpack_fold / consts["R_add"] + butterflies / consts["R_add_short"]
    else:
        C_dec = (unpack_fold + butterflies) / consts["R_add"]

    n_words = 2 * omega + 2 * omega_r + omega_e
    if variant["rng_rate"] == "batch_aware":
        C_samp = interp_piecewise(consts["rng_points"], n_words)
    else:
        C_samp = n_words / consts["R_rng_asymptotic"]

    C_trial = 2.0 * (C_prod + C_dec + C_samp)
    return {
        "C_prod_seconds": C_prod,
        "C_dec_seconds": C_dec,
        "C_samp_seconds": C_samp,
        "C_trial_seconds": C_trial,
        "trials_per_second_per_core": 1.0 / C_trial,
        "effective_R_rng_word_per_s": (n_words / C_samp) if C_samp > 0 else None,
        "inputs": {"n": n, "N": N, "n_e": n_e, "dup": dup,
                   "ring_ops": n_ring_ops, "t_per_ring_op_seconds": t_per_ring_op,
                   "unpack_fold_elements": unpack_fold,
                   "butterfly_elements": butterflies,
                   "rng_words": n_words},
    }


def build_rederivation(doc, m0b_block):
    m0 = doc["calibration"]["m0"]
    c0 = m0["constants"]

    R_add_cons = c0["R_add"]["aggregate"]["value"]
    R_add_opt = c0["R_add"]["alternative_optimistic_aggregate"]["value"]
    R_add_short_128 = c0["R_add_small_arrays"]["per_size_medians"].get(
        "128", c0["R_add_small_arrays"]["aggregate"]["value"])
    if isinstance(R_add_short_128, dict):  # defensive
        R_add_short_128 = c0["R_add_small_arrays"]["aggregate"]["value"]

    # Measured per-call time of the generator as a function of BATCH SIZE.
    # Interpolated, not fitted: see interp_piecewise().
    bulk = c0["R_rng_variants"]["bulk_generator_integers"]["per_size_medians"]
    ws = sorted(int(k) for k in bulk)
    ts = [w / (bulk[str(w)] if str(w) in bulk else bulk[w]) for w in ws]
    rng_points = list(zip(ws, ts))
    rng_fit = affine_fit(ws, ts)
    rng_fit["USED_FOR_EVALUATION"] = False
    rng_fit["why_not_used"] = (
        "Reported as a diagnostic only. Over a sweep spanning 64 .. 2^20 words "
        "this OLS line has a NEGATIVE intercept, so it returns a negative "
        "per-call time at the batch sizes the cost model evaluates. The "
        "evaluation uses piecewise-linear interpolation between measured points "
        "instead. The negative intercept is itself the finding: 'PCG64 uint64 "
        "generation' is not one number.")
    R_rng_asym = max(
        (bulk[str(w)] if str(w) in bulk else bulk[w]) for w in ws)

    fit_sx = m0b_block["fits"]["t_sx"]
    fit_rot = m0b_block["fits"]["t_rotxor"]

    VARIANTS = {
        "V1_like_for_like": {
            "ring_op": "shift_xor", "fwht_rate": "lumped", "rng_rate": "batch_aware",
            "R_add": "conservative",
            "description": (
                "BATCH-003's section 9.2 formula, unchanged, with this machine's "
                "constants substituted. R_add taken at the slowest size of the "
                "4096..65536 sweep, the same conservative rule BATCH-003 states. "
                "This is the direct answer to 'what does the frozen model cost "
                "here'."),
        },
        "V2_composition_aware": {
            "ring_op": "rotate_xor", "fwht_rate": "short_vector",
            "rng_rate": "batch_aware", "R_add": "conservative",
            "description": (
                "TWO CHANGES TO THE COMPOSITION, BOTH MINE, BOTH FLAGGED. (a) the "
                "ring product needs a masked cyclic ROTATE + xor per set bit, not "
                "the bare shift+xor section 9.1 measured; (b) the 896*n_e "
                "butterfly term runs on length-128 vectors, where measured "
                "throughput is far below the large-array R_add the model divides "
                "by. This is NOT a correction to BATCH-003's frozen model -- it is "
                "the size of what that model's composition assumption hides."),
        },
        "V3_optimistic": {
            "ring_op": "shift_xor", "fwht_rate": "lumped", "rng_rate": "asymptotic",
            "R_add": "optimistic",
            "description": (
                "Every constant at its most favourable measured value: fastest "
                "size of the R_add sweep, asymptotic generator rate, bare "
                "shift+xor. Reported to bound the band, not recommended."),
        },
    }

    out = {
        "what_this_block_is": (
            "DERIVED, NOT MEASURED. Applies calibration.m0 and calibration.m0b to "
            "parameter sets transcribed from BATCH-003 and its red team, using "
            "BATCH-003's own section 9.2 formula. No HQC object was constructed, "
            "sampled or decoded by this script."),
        "machine_constants_used": {
            "R_add_conservative_elem_per_s": R_add_cons,
            "R_add_optimistic_elem_per_s": R_add_opt,
            "R_add_short_vector_128_elem_per_s": R_add_short_128,
            "R_rng_measured_points_words_to_seconds_per_call": rng_points,
            "R_rng_affine_fit_diagnostic_only": rng_fit,
            "R_rng_asymptotic_word_per_s": R_rng_asym,
            "t_sx_fit": fit_sx,
            "t_rotxor_fit": fit_rot,
        },
        "batch003_reference": BATCH003_PRINTED,
        "constant_comparison": {},
        "per_set": {},
        "stage_budget": {},
        "t_req_rederivation": {},
        "verdict_pressure_tests": {},
    }

    # ---- constant-by-constant comparison ---------------------------------
    b3 = BATCH003_PRINTED["machine_constants"]
    out["constant_comparison"] = {
        "R_add": {"batch003": b3["R_add_elem_per_s"], "measured_here": R_add_cons,
                  "ratio_measured_over_batch003": R_add_cons / b3["R_add_elem_per_s"],
                  "batch003_sweep": [b3["R_add_sweep_low_elem_per_s"],
                                     b3["R_add_sweep_high_elem_per_s"]],
                  "measured_sweep": [c0["R_add"]["aggregate"]["sweep_min_median"],
                                     c0["R_add"]["aggregate"]["sweep_max_median"]]},
        "R_add_membound": {"batch003": b3["R_add_membound_elem_per_s"],
                           "measured_here": c0["R_add_membound"]["aggregate"]["value"],
                           "ratio_measured_over_batch003":
                               c0["R_add_membound"]["aggregate"]["value"]
                               / b3["R_add_membound_elem_per_s"]},
        "R_xor64": {"batch003": b3["R_xor64_word_per_s"],
                    "measured_here": c0["R_xor64"]["aggregate"]["value"],
                    "ratio_measured_over_batch003":
                        c0["R_xor64"]["aggregate"]["value"] / b3["R_xor64_word_per_s"],
                    "note": "measured but not consumed by the section 9.2 model"},
        "R_rng": {"batch003": b3["R_rng_word_per_s"],
                  "measured_here_asymptotic": R_rng_asym,
                  "measured_here_variants": {
                      "bulk_random_raw": c0["R_rng_variants"]["bulk_random_raw"]["per_size_medians"],
                      "bulk_generator_integers": bulk,
                      "scalar_python_loop": c0["R_rng_variants"]["scalar_python_loop"]["value"]},
                  "note": (
                      "BATCH-003's single number 5.1e7 word/s is not reproducible "
                      "as stated because 'PCG64 uint64 generation' does not name a "
                      "batch size and the rate varies by more than an order of "
                      "magnitude across batch sizes. Reported, not reconciled.")},
        "t_sx": {"batch003_table": b3["t_sx_seconds"],
                 "batch003_fit": b3["t_sx_fit"],
                 "measured_fit_here": fit_sx,
                 "at_batch003_bit_lengths": {
                     str(bits): {"batch003": val,
                                 "measured_fit_here": eval_fit(fit_sx, bits),
                                 "ratio": eval_fit(fit_sx, bits) / val}
                     for bits, val in b3["t_sx_seconds"].items()}},
        "t_rotxor": {"batch003": None,
                     "measured_fit_here": fit_rot,
                     "note": ("BATCH-003 measured no rotate variant. Ratio to "
                              "shift+xor at each bit length is the size of the "
                              "primitive-choice gap."),
                     "ratio_to_t_sx_at_batch003_bit_lengths": {
                         str(bits): eval_fit(fit_rot, bits) / eval_fit(fit_sx, bits)
                         for bits in b3["t_sx_seconds"]}},
    }

    # ---- per-set cost model, all variants --------------------------------
    for name, ps in PARAM_SETS.items():
        entry = {"parameters": ps, "variants": {}}
        for vname, variant in VARIANTS.items():
            consts = {
                "t_sx_at_n": eval_fit(fit_sx, ps["n"]),
                "t_rotxor_at_n": eval_fit(fit_rot, ps["n"]),
                "R_add": R_add_opt if variant["R_add"] == "optimistic" else R_add_cons,
                "R_add_short": R_add_short_128,
                "rng_points": rng_points,
                "R_rng_asymptotic": R_rng_asym,
            }
            res = cost_model(ps, consts, variant)
            res["variant_description"] = variant["description"]
            b3_ct = BATCH003_PRINTED["C_trial_seconds"].get(name)
            if b3_ct:
                res["batch003_C_trial_seconds"] = b3_ct
                res["ratio_C_trial_measured_over_batch003"] = res["C_trial_seconds"] / b3_ct
            entry["variants"][vname] = res
        for field, table in (("C_prod_seconds", BATCH003_PRINTED["C_prod_seconds"]),
                             ("C_dec_seconds", BATCH003_PRINTED["C_dec_seconds"]),
                             ("C_samp_seconds", BATCH003_PRINTED["C_samp_seconds"])):
            if name in table:
                entry.setdefault("batch003_components", {})[field] = table[name]
        out["per_set"][name] = entry

    # ---- stage budget, all variants --------------------------------------
    for vname in VARIANTS:
        stages, total = {}, 0.0
        for sname, plan in STAGE_PLAN.items():
            cs = sum(t * out["per_set"][ps]["variants"][vname]["C_trial_seconds"]
                     for ps, t in plan["trials"].items())
            runs = math.ceil(cs / RUN_CORES / RUN_WALL_CAP_S)
            stages[sname] = {
                "description": plan["desc"],
                "trials": plan["trials"],
                "core_seconds": cs,
                "wall_seconds_at_4_cores": cs / RUN_CORES,
                "runs_of_3600s_at_4_cores_required": runs,
                "batch003_core_seconds": BATCH003_PRINTED["stage_core_seconds"].get(sname),
                "ratio_to_batch003": (
                    cs / BATCH003_PRINTED["stage_core_seconds"][sname]
                    if sname in BATCH003_PRINTED["stage_core_seconds"] else None),
            }
            total += cs
        stages["C"] = {
            "description": "null arms; CARRIED from BATCH-003 VERBATIM",
            "core_seconds": STAGE_C_CARRIED,
            "runs_of_3600s_at_4_cores_required": math.ceil(
                STAGE_C_CARRIED / RUN_CORES / RUN_WALL_CAP_S),
            "not_rederivable_because": (
                "BATCH-003 section 9.3 states no trial counts for stage C, so its "
                "1.01e3 core-s cannot be re-derived from any set of machine "
                "constants. Carrying it verbatim makes the total below slightly "
                "OPTIMISTIC if the true constants are slower."),
        }
        total += STAGE_C_CARRIED
        runs_total = sum(s["runs_of_3600s_at_4_cores_required"] for s in stages.values())
        stages_total_D = total + STAGE_D_CARRIED
        out["stage_budget"][vname] = {
            "stages": stages,
            "total_mandatory_core_seconds": total,
            "batch003_total_mandatory_core_seconds":
                BATCH003_PRINTED["total_mandatory_core_seconds"],
            "ratio_to_batch003": total / BATCH003_PRINTED["total_mandatory_core_seconds"],
            "total_with_optional_D_core_seconds": stages_total_D,
            "total_wall_seconds_at_4_cores": total / RUN_CORES,
            "mandatory_runs_of_3600s_required": runs_total,
            "batch003_mandatory_runs": 8,
            "declared_maximum_runs": DECLARED_MAX_RUNS,
            "exceeds_declared_maximum_runs": runs_total > DECLARED_MAX_RUNS,
        }

    # ---- T_req: machine-independent, re-derived from BATCH-003's own rule --
    # (label, n_e, q, k). PS-A appears twice on purpose: BATCH-003 section 5
    # sizes it at the Prop 6.1.4 upper bound q = 5.588e-4 while section 8.2
    # sizes it at SPEC Table 11's OBSERVED inner DFR q = 4.993e-4. Both are
    # re-derived rather than one being chosen.
    treq_cells = [
        ("PS-R1_k16", 46, "0.2306", 16), ("PS-R1_k2", 46, "0.2306", 2),
        ("PS-R3_k17", 56, "0.370", 17), ("PS-R5_k30", 90, "0.473", 30),
        ("PS-A_k16", 46, "0.0005588", 16),
        ("PS-A_obsq_k2", 46, "0.0004993", 2),
        ("PS-A_obsq_k3", 46, "0.0004993", 3),
        ("PS-A_obsq_k4", 46, "0.0004993", 4),
        ("LADDER-dup2_k16", 46, "0.00894", 16),
        ("PS-R2-redteam_k16", 46, "0.21932", 16),
    ]
    for label, n_e, q, k in treq_cells:
        r = t_req(n_e, q, k)
        ref = BATCH003_PRINTED["T_req"].get(label)
        r["batch003_T_req"] = ref
        r["ratio_to_batch003"] = (r["T_req"] / ref) if ref else None
        r["n_e"] = n_e
        r["q_used"] = q
        r["k"] = k
        out["t_req_rederivation"][label] = r

    out["t_req_note"] = (
        "T_req contains NO machine constant. It is max(T_prec, T_stab) over the "
        "binomial law of S at (n_e, q), so no calibration on any machine can move "
        "it. Every difference between this task's cost figures and BATCH-003's is "
        "therefore located entirely in C_trial.")

    # ---- verdict pressure tests -------------------------------------------
    for vname in VARIANTS:
        ct_dup2 = out["per_set"]["LADDER-dup2"]["variants"][vname]["C_trial_seconds"]
        ct_dup1 = out["per_set"]["PS-R1"]["variants"][vname]["C_trial_seconds"]
        ct_r2 = out["per_set"]["PS-R2-redteam"]["variants"][vname]["C_trial_seconds"]
        treq_dup2 = out["t_req_rederivation"]["LADDER-dup2_k16"]["T_req"]
        treq_dup1 = out["t_req_rederivation"]["PS-R1_k16"]["T_req"]
        treq_r2 = out["t_req_rederivation"]["PS-R2-redteam_k16"]["T_req"]
        budget_envelope = 1.0e5  # core-s; a stated yardstick, not a decision
        out["verdict_pressure_tests"][vname] = {
            "dup1_cost_at_T_req_core_seconds": treq_dup1 * ct_dup1,
            "dup2_cost_at_T_req_core_seconds": treq_dup2 * ct_dup2,
            "batch003_dup2_cost_core_seconds":
                BATCH003_PRINTED["ladder_cost_core_seconds"]["dup2"],
            "redteam_PS_R2_cost_at_T_req_core_seconds": treq_r2 * ct_r2,
            "batch003_redteam_PS_R2_cost_core_seconds": 2.005e4,
            "C_trial_speedup_needed_to_bring_dup2_under_1e5_core_s":
                (treq_dup2 * ct_dup2) / budget_envelope,
            "infeasible_verdict_can_flip_on_machine_constants": bool(
                (treq_dup2 * ct_dup2) < budget_envelope),
            "yardstick_core_seconds": budget_envelope,
            "yardstick_note": (
                "1e5 core-s is a stated yardstick for arithmetic only. Whether any "
                "figure is inside the campaign's budget envelope is a Coordinator "
                "judgement, not an Executor observation."),
        }

    # ---- self-checks ------------------------------------------------------
    # This block exists because THIS TASK'S FIRST DERIVATION RUN violated it: a
    # global OLS fit of the generator's per-call time over four decades of batch
    # size produced a negative intercept and hence a negative C_samp, which was
    # visible only as V3_optimistic costing MORE than V1_like_for_like in the
    # totals. A derivation defect must fail the run, not be caught by eye.
    checks = []

    def _chk(name, ok, **detail):
        checks.append({"check": name, "passed": bool(ok), **detail})

    for name in PARAM_SETS:
        vs = out["per_set"][name]["variants"]
        for vname, res in vs.items():
            for comp in ("C_prod_seconds", "C_dec_seconds", "C_samp_seconds",
                         "C_trial_seconds"):
                _chk(f"{name}/{vname}/{comp} is strictly positive",
                     res[comp] > 0, value=res[comp])
        _chk(f"{name}: V3_optimistic C_trial <= V1_like_for_like C_trial",
             vs["V3_optimistic"]["C_trial_seconds"]
             <= vs["V1_like_for_like"]["C_trial_seconds"] * (1 + 1e-9),
             v3=vs["V3_optimistic"]["C_trial_seconds"],
             v1=vs["V1_like_for_like"]["C_trial_seconds"])
        _chk(f"{name}: V2_composition_aware C_trial >= V1_like_for_like C_trial",
             vs["V2_composition_aware"]["C_trial_seconds"]
             >= vs["V1_like_for_like"]["C_trial_seconds"] * (1 - 1e-9),
             v2=vs["V2_composition_aware"]["C_trial_seconds"],
             v1=vs["V1_like_for_like"]["C_trial_seconds"])
    for label, r in out["t_req_rederivation"].items():
        _chk(f"T_req/{label} is finite and positive",
             r["T_req"] > 0 and math.isfinite(r["T_req"]), value=r["T_req"])
    for label, r in out["t_req_rederivation"].items():
        if r["batch003_T_req"]:
            _chk(f"T_req/{label} reproduces BATCH-003 within 5 percent",
                 abs(r["ratio_to_batch003"] - 1.0) <= 0.05,
                 ratio=r["ratio_to_batch003"])
    out["self_checks"] = {
        "all_passed": all(c["passed"] for c in checks),
        "n_checks": len(checks),
        "failures": [c for c in checks if not c["passed"]],
        "checks": checks,
    }
    return out


# ---------------------------------------------------------------------------


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260803)
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--target-ms", type=float, default=30.0)
    ap.add_argument("--no-rederive", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)

    reps = 3 if args.smoke else args.reps
    warmup = 1 if args.smoke else args.warmup
    target_ms = 3.0 if args.smoke else args.target_ms

    # Round grid of 64-bit limb counts. Generic: every entry is a multiple of 16
    # limbs. It spans and brackets every bit length BATCH-003 quotes
    # (W = 92, 112, 180, 277, 561) without measuring at any of them.
    limb_grid = [16, 32, 48, 64, 96, 128, 160, 192, 224, 256,
                 288, 320, 384, 448, 512, 640, 768, 1024]
    if args.smoke:
        limb_grid = [16, 64, 256, 1024]

    env = environment_block(["calib_m0b.py"] + argv, args.seed)
    t_start = time.time()

    print("[m0b] big-integer shift+xor and rotate+xor over the limb grid ...",
          flush=True)
    out_sx, out_rot = bench_bigint(args.seed, limb_grid, reps, warmup, target_ms)

    xs = [64 * W for W in limb_grid]
    fit_sx = affine_fit(
        [math.ceil(b / 64) for b in xs],
        [out_sx[str(b)]["seconds_per_op"]["median"] for b in xs])
    fit_rot = affine_fit(
        [math.ceil(b / 64) for b in xs],
        [out_rot[str(b)]["seconds_per_op"]["median"] for b in xs])

    block = {
        "script": "calib_m0b.py",
        "block": BLOCK,
        "smoke": bool(args.smoke),
        "environment": env,
        "parameters": {"seed": args.seed, "reps": reps, "warmup": warmup,
                       "target_ms": target_ms, "limb_grid_W": limb_grid,
                       "bit_lengths": xs},
        "hqc_quantities_used": [],
        "measurements": {"bigint_shift_xor": out_sx, "bigint_rotate_xor": out_rot},
        "fits": {"t_sx": fit_sx, "t_rotxor": fit_rot},
        "constants": {
            "t_sx": {"unit": "seconds_per_operation",
                     "definition": "one big-integer right shift plus one XOR at B bits",
                     "fit": fit_sx,
                     "per_size_medians": {int(b): out_sx[str(b)]["seconds_per_op"]["median"]
                                          for b in xs}},
            "t_rotxor": {"unit": "seconds_per_operation",
                         "definition": ("one masked cyclic rotate plus one "
                                        "XOR-accumulate at B bits"),
                         "fit": fit_rot,
                         "per_size_medians": {int(b): out_rot[str(b)]["seconds_per_op"]["median"]
                                              for b in xs}},
        },
    }
    block["elapsed_seconds"] = time.time() - t_start
    block["loadavg_at_end"] = os.getloadavg()

    doc = {}
    if os.path.exists(args.out):
        with open(args.out) as fh:
            doc = json.load(fh)
    doc.setdefault("schema", SCHEMA)
    doc.setdefault("task", "TASK-20260803-1b30d8")
    doc.setdefault("goal", "GOAL-HQC-001")
    doc.setdefault("batch", "BATCH-004")
    doc.setdefault("calibration", {})
    doc["calibration"][BLOCK] = block

    if not args.no_rederive:
        if "m0" not in doc.get("calibration", {}):
            print("ERROR: calibration.m0 is absent from " + args.out
                  + "; run calib_m0.py first, or pass --no-rederive.",
                  file=sys.stderr)
            return 2
        print("[m0b] re-deriving the cost model ...", flush=True)
        doc["rederivation"] = build_rederivation(doc, block)

    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, args.out)

    print(f"[m0b] wrote calibration.{BLOCK} to {args.out} "
          f"({block['elapsed_seconds']:.1f} s)")
    print(f"[m0b] t_sx     fit: a={fit_sx['a_seconds']:.4g} s, "
          f"b={fit_sx['b_seconds_per_limb']:.4g} s/limb, "
          f"R2={fit_sx['r_squared']:.5f}, "
          f"max|rel resid|={fit_sx['max_abs_relative_residual']:.3f}")
    print(f"[m0b] t_rotxor fit: a={fit_rot['a_seconds']:.4g} s, "
          f"b={fit_rot['b_seconds_per_limb']:.4g} s/limb, "
          f"R2={fit_rot['r_squared']:.5f}, "
          f"max|rel resid|={fit_rot['max_abs_relative_residual']:.3f}")
    if not args.no_rederive:
        rd = doc["rederivation"]
        for v in ("V1_like_for_like", "V2_composition_aware", "V3_optimistic"):
            sb = rd["stage_budget"][v]
            print(f"[m0b] {v:24s} total = {sb['total_mandatory_core_seconds']:.4g} core-s "
                  f"({sb['ratio_to_batch003']:.2f}x BATCH-003's 5.58e4), "
                  f"runs={sb['mandatory_runs_of_3600s_required']} "
                  f"(declared max {DECLARED_MAX_RUNS})")
        sc = rd["self_checks"]
        print(f"[m0b] self-checks: {sc['n_checks']} run, "
              f"all_passed={sc['all_passed']}")
        if not sc["all_passed"]:
            print("[m0b] SELF-CHECK FAILURES -- the derivation in this file is "
                  "DEFECTIVE and its numbers must not be used:", file=sys.stderr)
            for f in sc["failures"]:
                print("   " + json.dumps(f), file=sys.stderr)
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

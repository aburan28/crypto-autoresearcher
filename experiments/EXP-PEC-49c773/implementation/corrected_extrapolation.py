#!/usr/bin/env python3
"""EXP-PEC-49c773 / RUN-PEC-49c773-a.

NC2b  -- recompute the overhead parameter c under the CORRECTED extrapolation
         law of experiments/EXP-PEC-49c773/specification.yaml section 6 (the
         law carries the fitted INTERCEPT as well as the fitted slope), from
         values ALREADY COMMITTED in RUN-PEC-6be870-a, and subject the
         corrected estimator to the pre-registered self-validation gate
         NC2b-G1 against that run's own null object (section 7).

NC2a  -- remove the ell = 101/103 definitional seam by measuring BOTH
         implementations at the same j-set over the entire fitted range, with
         C-NULL covering every fitted ell, and refit (sections 3-5).

The INSTRUMENT is experiments/EXP-PEC-6be870/implementation/per_entry_cost.py.
It is IMPORTED BY PATH and its existing entry points are called.  It is never
copied, forked, patched or reimplemented (specification section 2).  Nothing
under experiments/EXP-PEC-6be870/ is written by this program: the superseded
raw result is opened read-only and its SHA-256 is recorded.

Observations only.  No interpretation, no status change.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# 0.  Fixed identifiers and constants of the frozen contract
# --------------------------------------------------------------------------

RUN_ID = "RUN-PEC-49c773-a"
EXPERIMENT_ID = "EXP-PEC-49c773"

SUPERSEDED_RAW = ("experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/"
                  "raw-result.json")
SUPERSEDED_RUN_COMMIT = "49166fa5b9573e170b4923333ff743fa9b2ab5d6"
INSTRUMENT = "experiments/EXP-PEC-6be870/implementation/per_entry_cost.py"
INSTRUMENT_SHA256_COMMITTED = (
    "aea73ef79c3bdf6091b1fd61950bd8449618b295effd9d39a096f65197020ef1")

CORE_REQUIRED = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
                 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
EXT_REQUIRED = [103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163,
                167, 173, 179, 181, 191, 193, 197, 199, 211]
OPTIONAL_TAIL = [223, 227, 229, 233, 239, 241, 251]

C_SEED_ELL = [11, 23, 53, 101, 127, 211]
C_SEED_J = [0, 1, 2, 3]

PSCALE_ELL = [3, 5, 7, 11, 13]
PSCALE_BAND = [0.85, 1.15]
PSCALE_PREDICTED = 1.0

BOOTSTRAP_SEED = 20260802
BOOTSTRAP_REPLICATES = 2000

# Labelled INPUT CONSTANTS, quoted as stored from
# experiments/EXP-P13VOW-001/runs/RUN-P13VOW-001/raw-result.json
# (per_field.<key>.optimal.log2B).  sqrt(log2 p) and every log2 ratio are
# RECOMPUTED below; the stored sqrt values are cross-checks only.
VOW_CONSTANTS = [
    {"name": "SQIsign NIST-I", "log2p": 256, "log2_B_opt": 14.200000000000001,
     "sqrt_log2p_stored_for_crosscheck": 16.0},
    {"name": "SQIsign NIST-III", "log2p": 384, "log2_B_opt": 17.8,
     "sqrt_log2p_stored_for_crosscheck": 19.595917942265423},
    {"name": "SQIsign NIST-V", "log2p": 512, "log2_B_opt": 20.900000000000002,
     "sqrt_log2p_stored_for_crosscheck": 22.627416997969522},
    {"name": "log2p = 576", "log2p": 576, "log2_B_opt": 22.3,
     "sqrt_log2p_stored_for_crosscheck": 24.0},
    {"name": "log2p = 768", "log2p": 768, "log2_B_opt": 26.1,
     "sqrt_log2p_stored_for_crosscheck": 27.712812921102035},
]

NULL_GATE_TOLERANCE_BITS = 0.75
F_INDEP_THRESHOLD = 0.05

# The CZ seed-string FORMATS are read off the imported instrument
# (per_entry_cost.measure_primary line 812, measure_null lines 867-868).  The
# instrument does not return the string it built, so it is reconstructed here
# for the receipt.  It is NOT re-implemented: the instrument's own
# random.Random object is the one that drives every counted sample.
CZ_FMT_PRIMARY = "EXP-PEC-6be870|cz|%d|%d"
CZ_FMT_NULL_WALK = "EXP-PEC-6be870|null|%d|%d"
CZ_FMT_NULL_CZ = "EXP-PEC-6be870|null-cz|%d|%d"
# C-SEED uses a SEPARATE stream that never touches the primary stream.
CZ_FMT_SEED_PROBE = "EXP-PEC-49c773|cseed|IMPL-B-prime|%d|%d"


# --------------------------------------------------------------------------
# 1.  Instrument import (specification section 2)
# --------------------------------------------------------------------------

def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def import_instrument(repo_root):
    path = os.path.join(repo_root, INSTRUMENT)
    digest = sha256_file(path)
    spec = importlib.util.spec_from_file_location("per_entry_cost", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["per_entry_cost"] = mod
    spec.loader.exec_module(mod)
    return mod, digest, path


PE = None          # the imported instrument module


# --------------------------------------------------------------------------
# 2.  Small helpers built on the instrument's own statistics entry points
# --------------------------------------------------------------------------

def fit_xy(xs, ys):
    return PE.ols(xs, ys)


def fit_series(series, ells):
    """OLS of log2(level) on log2(ell) over the given ell list."""
    xs = [math.log2(e) for e in ells]
    ys = [math.log2(series[e]) for e in ells]
    return PE.ols(xs, ys)


def jackknife_leave_one_ell(series, ells):
    lo_s = hi_s = lo_i = hi_i = None
    for drop in ells:
        sub = [e for e in ells if e != drop]
        if len(sub) < 3:
            continue
        f = fit_series(series, sub)
        s, i = f["slope"], f["intercept"]
        lo_s = s if lo_s is None else min(lo_s, s)
        hi_s = s if hi_s is None else max(hi_s, s)
        lo_i = i if lo_i is None else min(lo_i, i)
        hi_i = i if hi_i is None else max(hi_i, i)
    return {"slope_min": lo_s, "slope_max": hi_s,
            "intercept_min": lo_i, "intercept_max": hi_i}


# --------------------------------------------------------------------------
# 3.  The CORRECTED extrapolation law (specification section 6)
# --------------------------------------------------------------------------

def corrected_c(log2_A, gamma, alpha, log2p_level, log2_B_opt, log2_p_meas):
    """c = [ log2 A + alpha*log2(log2 p_level / log2 p_meas)
             + gamma*log2(B_opt) ] / sqrt(log2 p_level)."""
    bits = (log2_A
            + alpha * math.log2(log2p_level / log2_p_meas)
            + gamma * log2_B_opt)
    return bits / math.sqrt(log2p_level), bits


def c_table_rows(label, series_id, window_id, log2_A, gamma, log2_p_meas,
                 boot_D=None, alphas=(0, 1), alpha_note=None):
    """One (series, window) block of the c table: alpha in {0,1}, every field
    size, at LOW / POINT / HIGH of the joint bootstrap interval of
    D = log2(A) + gamma*log2(B_opt).  boot_D maps log2p -> sorted list of
    bootstrap D values (or None when no bootstrap exists for this fit)."""
    rows = []
    for k in VOW_CONSTANTS:
        L = k["log2p"]
        sqrtL = math.sqrt(L)
        pshift = math.log2(L / log2_p_meas)
        D_point = log2_A + gamma * k["log2_B_opt"]
        ends = {"point": D_point}
        if boot_D and boot_D.get(L):
            vals = boot_D[L]
            ends["low"] = PE.percentile(vals, 0.025)
            ends["high"] = PE.percentile(vals, 0.975)
        for alpha in alphas:
            row = {"label": label, "series": series_id, "window": window_id,
                   "alpha": alpha, "alpha_note": alpha_note,
                   "field": k["name"], "log2p": L,
                   "log2_B_opt_input_constant": k["log2_B_opt"],
                   "sqrt_log2p_recomputed": sqrtL,
                   "sqrt_log2p_stored_crosscheck":
                       k["sqrt_log2p_stored_for_crosscheck"],
                   "log2_A": log2_A, "gamma": gamma,
                   "p_scaling_bits": alpha * pshift}
            for end, D in ends.items():
                row["overhead_bits_" + end] = D + alpha * pshift
                row["c_" + end] = (D + alpha * pshift) / sqrtL
            rows.append(row)
    return rows


# --------------------------------------------------------------------------
# 4.  Worker kernels (forked; defined at module level so fork can reach them)
# --------------------------------------------------------------------------

def _primary_worker(args):
    rec = PE.measure_primary(args)
    ell, jidx, _impl = args
    rec["cz_seed_string"] = CZ_FMT_PRIMARY % (ell, jidx)
    rec["cz_seed_string_provenance"] = (
        "reconstructed from the format literal in "
        "per_entry_cost.measure_primary; the instrument seeds the stream "
        "itself and does not return the string")
    return rec


def _null_worker(args):
    rec = PE.measure_null(args)
    ell, jidx, _impl = args
    rec["cz_seed_strings"] = {"walk": CZ_FMT_NULL_WALK % (ell, jidx),
                              "cz": CZ_FMT_NULL_CZ % (ell, jidx)}
    return rec


def _cseed_worker(args):
    """C-SEED: IMPL-B run a SECOND time under a different, recorded CZ stream.
    Composed from the instrument's own entry points (instantiate,
    distinct_roots, region_begin/region_end); the instrument is not modified.
    A separate RNG object is used, so the primary stream is untouched."""
    ell, jidx = args
    M = PE._G["mod"][ell]
    j = PE._G["pool"][jidx]
    seed_string = CZ_FMT_SEED_PROBE % (ell, jidx)
    rng = random.Random(seed_string)
    t0 = time.time()
    PE.region_begin()
    f = PE.instantiate(M, ell, j)
    m_inst, i_inst = PE.region_end()
    PE.region_begin()
    roots, deg_g, attempts = PE.distinct_roots(f, PE.MULFN["IMPL-B"], rng)
    m_root, i_root = PE.region_end()
    t1 = time.time()
    bad = sum(1 for r in roots if PE.poly_eval_uninstrumented(f, r) != PE.ZERO)
    n_roots = len(roots)
    entries = n_roots - (1 if ell == 2 else 0)
    return {"ell": ell, "j_index": jidx, "impl": "IMPL-B-prime",
            "cz_seed_string": seed_string,
            "mults_instantiate": m_inst, "mults_rootfind": m_root,
            "cost": m_inst + m_root, "inversions": i_inst + i_root,
            "n_distinct_roots": n_roots, "deg_gcd_xq_minus_x": deg_g,
            "cz_attempts": attempts, "entries": entries,
            "per_entry": (m_inst + m_root) / entries if entries else None,
            "roots_failing_independent_horner": bad,
            "wall_clock_seconds": round(t1 - t0, 6),
            "roots_sha256": hashlib.sha256(
                ("|".join("%d,%d" % r for r in roots)).encode()).hexdigest(),
            "pid": os.getpid()}


def _pscale_worker(task):
    """C-PSCALE arm at ONE prime, executed in a FORKED CHILD so that the
    instrument's process-global prime (set_prime) can never leak into the
    primary measurement in the parent."""
    label, bound, paths, walk_seeds, ell_list = task
    out = {"label": label, "bound_exponent": bound}
    try:
        p = PE.largest_prime_below(2 ** bound, cong=3, mod=4)
        PE.set_prime(p)
        out["p"] = p
        out["p_bits"] = p.bit_length()
        out["log2_p_exact"] = math.log2(p)
        rngb = random.Random("%s|cbase1|%d" % (EXPERIMENT_ID, bound))
        out["C-BASE.1"] = PE.control_c_base_1(p, rngb)
        mod = {}
        for ell in [2] + list(ell_list):
            terms, saw, dup = PE.parse_modpoly(paths[ell])
            v = PE.verify_modpoly(ell, terms, saw, dup)
            if v["verdict"] != "pass":
                out.setdefault("cbase2_failures", []).append(v)
                continue
            mod[ell] = PE.reduce_modpoly(ell, terms, p)
            del terms
        n_walk = 3 * math.ceil(math.log2(p))
        pool, chains = PE.walk_pool(mod[2], n_walk, walk_seeds, lambda m: None)
        PE._G["mod"] = mod
        PE._G["pool"] = pool
        out["n_walk"] = n_walk
        out["walk_seeds"] = list(walk_seeds)
        out["pool"] = [[j[0], j[1]] for j in pool]
        prim, nul = [], []
        PE.CNT[0] = 0
        PE.CNT[1] = 0
        for ell in ell_list:
            if ell not in mod:
                continue
            for ji in range(len(pool)):
                prim.append(_primary_worker((ell, ji, "IMPL-A")))
                nul.append(_null_worker((ell, ji, "IMPL-A")))
        out["samples_primary"] = prim
        out["samples_null"] = nul
        out["status"] = "ok"
    except Exception as exc:                      # pragma: no cover
        out["status"] = "error"
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
    return out


# --------------------------------------------------------------------------
# 5.  Main
# --------------------------------------------------------------------------

def main():
    global PE
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-seconds", type=float, default=5400.0)
    ap.add_argument("--nc2b-deadline-seconds", type=float, default=600.0)
    ap.add_argument("--no-new-measurement-after", type=float, default=4200.0)
    ap.add_argument("--pass2-start-before", type=float, default=2700.0)
    ap.add_argument("--pass2-abort-at", type=float, default=3900.0)
    ap.add_argument("--tail-min-remaining", type=float, default=1500.0)
    ap.add_argument("--pscale-min-remaining", type=float, default=900.0)
    ap.add_argument("--pscale-deadline-seconds", type=float, default=600.0)
    ap.add_argument("--bootstrap-replicates", type=int,
                    default=BOOTSTRAP_REPLICATES)
    # rehearsal-only switches; the authoritative run uses the defaults
    ap.add_argument("--core-limit", type=int, default=0,
                    help="rehearsal only: cap the core grid at this ell")
    ap.add_argument("--skip-extension", action="store_true")
    ap.add_argument("--skip-tail", action="store_true")
    ap.add_argument("--rehearsal", action="store_true")
    args = ap.parse_args()

    T0 = time.time()
    root = os.path.abspath(args.repo_root)

    R = {"run_id": RUN_ID, "experiment_id": EXPERIMENT_ID,
         "started_utc": datetime.now(timezone.utc).isoformat(),
         "argv": sys.argv,
         "rehearsal": bool(args.rehearsal),
         "phases": {}, "controls": {}, "protocol_deviations": [],
         "anomalies": []}

    def log(msg):
        print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)

    def elapsed():
        return time.time() - T0

    def flush_partial(tag):
        tmp = args.out + ".partial"
        with open(tmp, "w") as fh:
            json.dump(R, fh, indent=1, default=str)
        os.replace(tmp, args.out)
        log("  wrote partial raw-result (%s) at t=%.1fs" % (tag, elapsed()))

    log("%s / %s -- NC2b (corrected extrapolation law) + NC2a (seam removal)"
        % (EXPERIMENT_ID, RUN_ID))
    log("python %s" % sys.version.replace("\n", " "))

    # ---- instrument import ------------------------------------------------
    PE, inst_sha, inst_path = import_instrument(root)
    R["instrument"] = {
        "path": INSTRUMENT,
        "sha256_as_imported": inst_sha,
        "sha256_committed_at_49166fa5": INSTRUMENT_SHA256_COMMITTED,
        "matches_committed": bool(inst_sha == INSTRUMENT_SHA256_COMMITTED),
        "import_route": "importlib.util.spec_from_file_location, by path",
        "modified_by_this_run": False,
        "entry_points_called": [
            "set_prime", "region_begin", "region_end", "counters_reset_all",
            "instantiate", "distinct_roots", "poly_eval_uninstrumented",
            "fetch_modpolys", "parse_modpoly", "verify_modpoly",
            "reduce_modpoly", "canonical_reduced_sha256",
            "bivariate_eval_independent", "largest_prime_below",
            "control_c_base_1", "control_c_instr", "walk_pool",
            "measure_primary", "measure_null", "poc_count", "poc_isogs",
            "ols", "quad_fit", "median", "percentile", "iqr",
            "t_quantile_975", "MULFN", "ZERO"],
    }
    log("  instrument sha256 %s (matches committed: %s)"
        % (inst_sha, R["instrument"]["matches_committed"]))
    if not R["instrument"]["matches_committed"]:
        R["validity"] = {"status": "invalid_measurement",
                         "reason": "imported instrument SHA-256 differs from "
                                   "the value committed at 49166fa5"}
        flush_partial("instrument-mismatch")
        return 2

    # ---- instance (the prime must be set before C-INSTR exercises the
    # ---- instrumented F_{p^2} primitives) --------------------------------
    t = time.time()
    p_meas = PE.largest_prime_below(2 ** 40, cong=3, mod=4)
    PE.set_prime(p_meas)
    log2_p_meas = math.log2(p_meas)
    log("  p = %d (2^%d), p mod 4 = %d, log2 p = %.12f"
        % (p_meas, p_meas.bit_length(), p_meas % 4, log2_p_meas))
    R["phases"]["instance_seconds"] = round(time.time() - t, 3)

    # ======================================================================
    # STEP 1 -- C-INSTR
    # ======================================================================
    t = time.time()
    log("step 1: C-INSTR")
    c_instr = PE.control_c_instr(
        random.Random("%s|c-instr|%d" % (EXPERIMENT_ID, BOOTSTRAP_SEED)))
    c_instr["seed_string"] = "%s|c-instr|%d" % (EXPERIMENT_ID, BOOTSTRAP_SEED)
    R["controls"]["C-INSTR"] = c_instr
    R["phases"]["c_instr_seconds"] = round(time.time() - t, 3)
    log("  C-INSTR verdict: %s" % c_instr["verdict"])
    if c_instr["verdict"] != "pass":
        R["validity"] = {"status": "invalid_measurement",
                         "reason": "C-INSTR failed; the frozen contract STOPS "
                                   "the run and reports no per-entry number."}
        flush_partial("c-instr-fail")
        return 2

    # ======================================================================
    # STEP 2 -- NC2b IN FULL, from the committed superseded raw result
    # ======================================================================
    t = time.time()
    log("step 2: NC2b (zero new measurement; committed inputs only)")
    sup_path = os.path.join(root, SUPERSEDED_RAW)
    with open(sup_path, "rb") as fh:
        sup_bytes = fh.read()
    sup_sha = hashlib.sha256(sup_bytes).hexdigest()
    S = json.loads(sup_bytes)

    nc2b = {
        "what_it_is": ("recomputation under the corrected law of "
                       "specification section 6; every input carried verbatim "
                       "from RUN-PEC-6be870-a at commit "
                       + SUPERSEDED_RUN_COMMIT),
        "source": {"path": SUPERSEDED_RAW, "commit": SUPERSEDED_RUN_COMMIT,
                   "sha256_of_file_read": sup_sha,
                   "status": "READ-ONLY INPUT DATA; not modified"},
        "p_meas": {"p_carried_from_superseded_instance": S["instance"]["p"],
                   "p_recomputed_here": p_meas,
                   "agrees": bool(p_meas == S["instance"]["p"]),
                   "log2_p_meas_exact_recomputed": log2_p_meas,
                   "nominal_40_not_used": True},
    }

    # -- carried inputs (labelled) -----------------------------------------
    carried = {"label": "CARRIED VERBATIM FROM RUN-PEC-6be870-a; NOT measured "
                        "by this run",
               "fit_windows": {}, "per_ell_primary_min": {},
               "C-NULL": {}}
    for w, blk in S["fit"]["windows"].items():
        carried["fit_windows"][w] = {
            "gamma_hat": blk["gamma_hat"], "intercept": blk["intercept"],
            "n": blk["n"], "ell": blk["ell"],
            "bootstrap_ci95_slope": blk["bootstrap_ci95"]}
    carried["per_ell_primary_min"] = dict(
        S["per_ell"]["primary_min_over_implementations"])
    cn = S["controls"]["C-NULL"]
    carried["C-NULL"] = {
        "per_ell_per_entry": dict(cn["per_ell_per_entry"]),
        "gamma_null_by_window": dict(cn["gamma_null_by_window"]),
        "gamma_null_bootstrap_ci95_W_MID":
            list(cn["gamma_null_bootstrap_ci95_W_MID"]),
        "verdict_in_superseded_run": cn["verdict"]}
    carried["superseded_response_definition"] = S["fit"]["response"]
    carried["superseded_law_as_frozen"] = S["extrapolation"]["law"]
    nc2b["carried_inputs"] = carried

    # -- step (i): reproduce every committed intercept by refit -------------
    sup_series = {int(k): float(v)
                  for k, v in carried["per_ell_primary_min"].items()}
    repro = {}
    max_dev = 0.0
    for w, blk in carried["fit_windows"].items():
        ells = [int(e) for e in blk["ell"]]
        f = fit_series(sup_series, ells)
        d_s = abs(f["slope"] - blk["gamma_hat"])
        d_i = abs(f["intercept"] - blk["intercept"])
        max_dev = max(max_dev, d_s, d_i)
        repro[w] = {"n": f["n"],
                    "slope_refit_here": f["slope"],
                    "slope_committed": blk["gamma_hat"],
                    "slope_abs_difference": d_s,
                    "intercept_refit_here": f["intercept"],
                    "intercept_committed": blk["intercept"],
                    "intercept_abs_difference": d_i,
                    "r2": f["r2"],
                    "reproduced_within_1e-9": bool(d_s <= 1e-9 and d_i <= 1e-9)}
    nc2b["primary_fit_reproduction"] = {
        "windows": repro, "max_abs_deviation": max_dev,
        "tolerance": 1e-9,
        "all_reproduced": bool(all(v["reproduced_within_1e-9"]
                                   for v in repro.values()))}
    log("  NC2b refit reproduction: max |deviation| = %.3e (tolerance 1e-9)"
        % max_dev)

    # -- step (ii): refit the committed C-NULL series -----------------------
    null_series = {int(k): float(v)
                   for k, v in carried["C-NULL"]["per_ell_per_entry"].items()}
    null_windows = {"W-ALL": sorted(null_series),
                    "W-MID": [e for e in sorted(null_series) if e >= 11]}
    null_fits = {}
    for w, ells in null_windows.items():
        f = fit_series(null_series, ells)
        committed = carried["C-NULL"]["gamma_null_by_window"].get(w)
        null_fits[w] = {
            "ell": ells, "n": f["n"],
            "log2_A_null": f["intercept"], "gamma_null_refit_here": f["slope"],
            "gamma_null_committed": committed,
            "gamma_null_abs_difference": (abs(f["slope"] - committed)
                                          if committed is not None else None),
            "reproduced_within_1e-9": bool(
                committed is not None and abs(f["slope"] - committed) <= 1e-9),
            "r2": f["r2"], "max_abs_residual": f["max_abs_residual"],
            "REF_null_median_log2_per_entry_this_window": PE.median(
                [math.log2(null_series[e]) for e in ells])}
    nc2b["null_fit"] = null_fits
    REF_null_wall = PE.median([math.log2(null_series[e])
                               for e in null_windows["W-ALL"]])
    nc2b["REF_null"] = {
        "definition": ("median over the null's fitted ell of "
                       "log2(per_entry_null(ell)), in bits"),
        "per_window": {w: null_fits[w][
            "REF_null_median_log2_per_entry_this_window"]
            for w in null_fits},
        "over_all_25_committed_null_ell": REF_null_wall,
        "reading_used_for_the_gate": ("per-window: the gate is evaluated on "
                                      "EACH of the null's fitted windows, so "
                                      "REF_null is taken over that window's "
                                      "own fitted ell; the W-ALL reading is "
                                      "reported beside it as the alternative "
                                      "reading")}

    # -- step (iii): corrected law on primary fits and on the null ----------
    nc2b_c_rows = []
    for w, blk in carried["fit_windows"].items():
        jk = jackknife_leave_one_ell(sup_series, [int(e) for e in blk["ell"]])
        nc2b.setdefault("primary_jackknife", {})[w] = jk
        nc2b_c_rows.extend(c_table_rows(
            "NC2b corrected law applied to the CARRIED superseded fit",
            "S-SUPERSEDED-MIN (carried; mixed-definition response, "
            "see the seam statement)", w, blk["intercept"], blk["gamma_hat"],
            log2_p_meas))
    nc2b["corrected_c_table"] = nc2b_c_rows

    null_c_rows = []
    for w, nf in null_fits.items():
        null_c_rows.extend(c_table_rows(
            "NC2b corrected law applied to the CARRIED null series",
            "C-NULL (committed, ell 2..101)", w,
            nf["log2_A_null"], nf["gamma_null_refit_here"], log2_p_meas))
    nc2b["null_c_table"] = null_c_rows

    # -- superseded law output, labelled -----------------------------------
    nc2b["superseded_input_being_corrected"] = {
        "label": ("SUPERSEDED INPUT BEING CORRECTED -- DEC-20260802-8227b9 "
                  "adjudication A. NOT an estimate; may not be cited as one."),
        "law_as_frozen": S["extrapolation"]["law"],
        "rows": S["extrapolation"]["rows"],
        "defect": ("the frozen law maps the fit's SLOPE and discards its "
                   "INTERCEPT, implicitly setting A = 1 in "
                   "per_entry = A * ell^gamma"),
        "same_law_applied_to_the_null_object": [
            {"field": k["name"], "log2p": k["log2p"],
             "N_under_superseded_law_bits":
                 null_fits["W-MID"]["gamma_null_refit_here"] * k["log2_B_opt"],
             "c_under_superseded_law":
                 null_fits["W-MID"]["gamma_null_refit_here"]
                 * k["log2_B_opt"] / math.sqrt(k["log2p"])}
            for k in VOW_CONSTANTS]}

    # -- step (iv): the gate NC2b-G1 ---------------------------------------
    gate = {"id": "NC2b-G1",
            "criterion": ("| N_null(level) - REF_null | <= %.2f bits at EVERY "
                          "field size, on EACH of the null's fitted windows"
                          % NULL_GATE_TOLERANCE_BITS),
            "estimator_output": ("N_null(level) = log2(A_null) + gamma_null * "
                                 "log2(B_opt(level)), alpha = 0"),
            "tolerance_bits": NULL_GATE_TOLERANCE_BITS,
            "evaluations": [], "max_abs_margin_bits": 0.0}
    worst = 0.0
    for w, nf in null_fits.items():
        REF = nf["REF_null_median_log2_per_entry_this_window"]
        for k in VOW_CONSTANTS:
            N = nf["log2_A_null"] + nf["gamma_null_refit_here"] * k["log2_B_opt"]
            dev = abs(N - REF)
            worst = max(worst, dev)
            gate["evaluations"].append({
                "window": w, "field": k["name"], "log2p": k["log2p"],
                "N_null_bits": N, "REF_null_bits": REF,
                "abs_difference_bits": dev,
                "margin_bits_remaining": NULL_GATE_TOLERANCE_BITS - dev,
                "within_tolerance": bool(dev <= NULL_GATE_TOLERANCE_BITS),
                "c_null_alpha0": N / math.sqrt(k["log2p"]),
                "REF_null_over_sqrt_log2p": REF / math.sqrt(k["log2p"]),
                "tolerance_on_c": (NULL_GATE_TOLERANCE_BITS
                                   / math.sqrt(k["log2p"])),
                "alternative_reading_REF_over_all_25_null_ell": REF_null_wall,
                "abs_difference_under_alternative_reading":
                    abs(N - REF_null_wall),
                "within_tolerance_under_alternative_reading":
                    bool(abs(N - REF_null_wall) <= NULL_GATE_TOLERANCE_BITS)})
    gate["max_abs_margin_bits"] = worst
    gate["worst_case_abs_difference_bits"] = worst
    gate["verdict"] = ("PASS" if all(e["within_tolerance"]
                                     for e in gate["evaluations"]) else "FAIL")
    gate["verdict_under_alternative_REF_reading"] = (
        "PASS" if all(e["within_tolerance_under_alternative_reading"]
                      for e in gate["evaluations"]) else "FAIL")
    gate["readings_agree"] = bool(
        gate["verdict"] == gate["verdict_under_alternative_REF_reading"])
    gate["fail_consequence_if_FAIL"] = (
        "specification section 7 fail_consequence: the corrected estimator is "
        "reported as FAILED, is not tuned, no c computed under it may be "
        "cited, and the DEC-20260802-8227b9 prohibition on the superseded c "
        "values stands. Reported by the Executor; adjudicated by the "
        "Coordinator.")
    # power of the gate, computed here from the same committed inputs
    gate["power_check_superseded_law_on_the_same_null"] = [
        {"window": w, "field": k["name"],
         "N_under_superseded_law_bits":
             null_fits[w]["gamma_null_refit_here"] * k["log2_B_opt"],
         "abs_difference_from_REF_bits":
             abs(null_fits[w]["gamma_null_refit_here"] * k["log2_B_opt"]
                 - null_fits[w]["REF_null_median_log2_per_entry_this_window"]),
         "would_pass": bool(
             abs(null_fits[w]["gamma_null_refit_here"] * k["log2_B_opt"]
                 - null_fits[w]["REF_null_median_log2_per_entry_this_window"])
             <= NULL_GATE_TOLERANCE_BITS)}
        for w in null_fits for k in VOW_CONSTANTS]
    nc2b["gate"] = gate
    log("  NC2b-G1 verdict: %s (worst |N_null - REF_null| = %.4f bits of a "
        "%.2f bit tolerance)" % (gate["verdict"], worst,
                                 NULL_GATE_TOLERANCE_BITS))

    # -- f_indep guard on the SUPERSEDED samples ---------------------------
    fi_sup = {}
    for s in S["samples_primary"]:
        if s.get("cost"):
            fi_sup.setdefault(s["ell"], []).append(
                s["mults_instantiate"] / s["cost"])
    fi_sup_med = {e: PE.median(v) for e, v in fi_sup.items()}
    nc2b["p_independent_fraction_guard"] = {
        "quantity": "f_indep(ell) = mults_instantiate(ell) / cost(ell)",
        "source": "superseded samples_primary (carried)",
        "per_ell_median": {str(e): fi_sup_med[e] for e in sorted(fi_sup_med)},
        "max_over_ell_of_the_per_ell_median": max(fi_sup_med.values()),
        "max_over_individual_samples": max(max(v) for v in fi_sup.values()),
        "threshold": F_INDEP_THRESHOLD,
        "satisfied": bool(max(fi_sup_med.values()) <= F_INDEP_THRESHOLD),
        "consequence_if_exceeded": ("whole-intercept scaling replaced by the "
                                    "structure-aware form of section 6")}

    nc2b["alpha_status"] = {
        "alpha_primary": 1.0,
        "label_before_C_PSCALE": "DERIVED-NOT-MEASURED",
        "alpha_floor_reported": 0.0,
        "note": ("alpha = 0 is reported always as an explicit FLOOR that "
                 "would be correct only for a hypothetical p-independent "
                 "implementation")}
    nc2b["declared_assumptions"] = ["L1", "L2", "L3", "L4", "L5", "L6"]
    nc2b["seconds"] = round(time.time() - t, 3)
    R["nc2b"] = nc2b
    R["phases"]["nc2b_seconds"] = nc2b["seconds"]
    flush_partial("NC2b complete")
    if elapsed() > args.nc2b_deadline_seconds:
        R["anomalies"].append(
            "NC2b completed at t=%.1fs, after the %.0fs hard gate; per the "
            "stopping rules NC2b is reported as the sole deliverable."
            % (elapsed(), args.nc2b_deadline_seconds))
        R["validity"] = {"status": "completed_nc2b_only",
                         "reason": "NC2b hard wall-clock gate exceeded"}
        flush_partial("nc2b-deadline")
        return 0

    # ======================================================================
    # STEP 3 -- acquisition and C-BASE.2 over the ENTIRE required grid
    # ======================================================================
    t = time.time()
    core = [e for e in CORE_REQUIRED
            if (not args.core_limit or e <= args.core_limit)]
    ext = [] if args.skip_extension else list(EXT_REQUIRED)
    required = core + ext
    log("step 3: acquisition + C-BASE.2 over the entire required grid "
        "(%d ell)" % len(required))
    outdir = os.path.join(args.scratch, "modpolys_run")
    fetch_records, fetch_seconds, fetch_bytes = PE.fetch_modpolys(
        required, outdir, log)
    dropped = {}
    mod_by_ell = {}
    terms_by_ell = {}
    modpoly_path = {}
    cbase2 = []
    for rec in fetch_records:
        ell = rec["ell"]
        if rec["status"] != "ok":
            dropped[ell] = rec["status"]
            continue
        terms, saw, dup = PE.parse_modpoly(rec["local_path"])
        v = PE.verify_modpoly(ell, terms, saw, dup)
        cbase2.append(v)
        if v["verdict"] != "pass":
            dropped[ell] = "C-BASE.2 verification failure"
            continue
        M = PE.reduce_modpoly(ell, terms, p_meas)
        mod_by_ell[ell] = M
        modpoly_path[ell] = rec["local_path"]
        rec["coefficient_count_in_file"] = len(terms)
        rec["reduced_array_sha256"] = PE.canonical_reduced_sha256(M, ell)
        if ell <= 101:
            terms_by_ell[ell] = terms      # needed by C-BASE.5
        else:
            del terms                      # memory: freed after reduction
    R["modular_polynomial_provenance"] = {
        "route": "primary source download",
        "index_page": "https://math.mit.edu/~drew/ClassicalModPolys.html",
        "file_url_pattern": PE.MODPOLY_URL,
        "storage": "session scratch, outside the repository; not committed",
        "acquisition_phase_seconds": round(fetch_seconds, 3),
        "acquisition_phase_total_bytes": fetch_bytes,
        "caps": {"per_ell_fetch_seconds": PE.CAP_PER_ELL_SECONDS,
                 "per_ell_bytes": PE.CAP_PER_ELL_BYTES,
                 "acquisition_phase_seconds": PE.CAP_PHASE_SECONDS,
                 "acquisition_phase_total_bytes": PE.CAP_PHASE_BYTES},
        "integer_terms_retained_only_for_ell_le_101":
            ("memory measure: the integer coefficient array is released after "
             "mod-p reduction for ell >= 103, mirroring the superseded run's "
             "own 'del terms'; C-BASE.5's independent evaluator needs the "
             "integer array and is run over ell <= 101"),
        "per_ell": fetch_records}
    R["controls"]["C-BASE.2"] = {
        "id": "C-BASE.2", "per_ell": cbase2,
        "n_pass": sum(1 for v in cbase2 if v["verdict"] == "pass"),
        "n_fail": sum(1 for v in cbase2 if v["verdict"] != "pass"),
        "verdict": ("pass" if cbase2 and all(v["verdict"] == "pass"
                                             for v in cbase2) else "fail")}
    R["dropped_ell"] = dropped
    R["phases"]["acquisition_and_cbase2_seconds"] = round(time.time() - t, 3)
    acquired = sorted(mod_by_ell)
    log("  acquired %d ell; C-BASE.2 %d pass / %d fail; dropped=%s"
        % (len(acquired), R["controls"]["C-BASE.2"]["n_pass"],
           R["controls"]["C-BASE.2"]["n_fail"], dropped))

    R["reduced_coefficient_fixture_ell_le_13"] = {
        str(ell): {"note": ("mod-p-reduced coefficient array as sorted "
                            "(a,b,c) triples, c in [0,p)"),
                   "triples": [[a, b, mod_by_ell[ell][b][a]]
                               for a in range(ell + 2) for b in range(ell + 2)
                               if mod_by_ell[ell][b][a]]}
        for ell in acquired if ell <= 13}

    core_acquired = [e for e in core if e in mod_by_ell]
    if len(core_acquired) < 12 or len(core_acquired) < 0.75 * len(core):
        R["validity"] = {
            "status": "incomplete_infrastructure",
            "reason": ("fewer than 12 surviving core ell, or more than 25%% "
                       "of the core grid dropped by fetch obstruction / "
                       "verification failure")}
        flush_partial("acquisition-incomplete")
        return 3

    import multiprocessing as mp
    ctx = mp.get_context("fork")

    def run_tasks(tasks, fn, label, deadline):
        out = []
        t_start = time.time()
        PE.CNT[0] = 0
        PE.CNT[1] = 0
        with ctx.Pool(args.workers) as pool_:
            for rec in pool_.imap(fn, tasks, chunksize=1):
                out.append(rec)
                if len(out) % 40 == 0:
                    log("  %s %d/%d (%.1fs)"
                        % (label, len(out), len(tasks), time.time() - t_start))
                if time.time() > deadline:
                    log("  %s: deadline reached, terminating remaining tasks"
                        % label)
                    pool_.terminate()
                    break
        return out

    # ======================================================================
    # STEP 3b -- C-PSCALE measurement arms at p1 and p2 (see deviation D-1)
    # ======================================================================
    R["protocol_deviations"].append({
        "id": "D-1",
        "what": ("C-PSCALE's p1/p2 MEASUREMENT arms are executed here, "
                 "immediately after acquisition, rather than at "
                 "execution_order step 11."),
        "why": ("The dispatching Coordinator's handoff message for "
                "TASK-20260802-63145a directs the order 'NC2b first, then "
                "C-PSCALE, then as much of NC2a as fits'. The frozen "
                "contract places C-PSCALE at step 11 behind a >= 900 s "
                "remaining-budget gate, i.e. as the first item a truncation "
                "drops."),
        "why_it_cannot_change_a_measured_number": (
            "each p-arm runs in a FORKED CHILD, so the instrument's "
            "process-global prime (set_prime) and _G never leave that child; "
            "the parent's primary measurement is byte-identical either way, "
            "which C-REPRO independently checks against the superseded run. "
            "C-PSCALE is non-gating and its ESTIMATOR is still computed in "
            "the step-12 fits phase, using the p3 arm taken from the primary "
            "measurement."),
        "recorded_not_tuned": True})
    t = time.time()
    pscale = {"status": "not_run", "band": PSCALE_BAND,
              "predicted_value": PSCALE_PREDICTED,
              "deviation": "D-1 (moved to step 3b)"}
    if all(e in modpoly_path for e in [2] + PSCALE_ELL):
        log("step 3b: C-PSCALE measurement arms at p1 (2^20) and p2 (2^30)")
        tasks_ps = [("p1", 20, {e: modpoly_path[e] for e in [2] + PSCALE_ELL},
                     PE.WALK_SEEDS[:4], PSCALE_ELL),
                    ("p2", 30, {e: modpoly_path[e] for e in [2] + PSCALE_ELL},
                     PE.WALK_SEEDS[:4], PSCALE_ELL)]
        arms = run_tasks(tasks_ps, _pscale_worker, "C-PSCALE",
                         time.time() + args.pscale_deadline_seconds)
        pscale["arms"] = arms
        pscale["status"] = ("measured_p1_p2" if len(arms) == 2
                            else "partial_%d_of_2" % len(arms))
        for a in arms:
            log("  C-PSCALE %s: p=%s status=%s" % (a.get("label"), a.get("p"),
                                                   a.get("status")))
    else:
        pscale["status"] = "not_run_missing_modpolys"
    R["phases"]["c_pscale_measurement_seconds"] = round(time.time() - t, 3)
    R["controls"]["C-PSCALE"] = pscale
    flush_partial("C-PSCALE arms measured")

    # ======================================================================
    # STEP 4 -- j-pool and C-BASE.1 at the primary prime
    # ======================================================================
    t = time.time()
    log("step 4: j-pool (n_walk=%d, 8 seeds) and C-BASE.1" % PE.N_WALK)
    PE.set_prime(p_meas)
    pool, chains = PE.walk_pool(mod_by_ell[2], PE.N_WALK, PE.WALK_SEEDS, log)
    R["instance"] = {"p": p_meas, "p_bits": p_meas.bit_length(),
                     "p_mod_4": p_meas % 4,
                     "field": "F_{p^2} = F_p[T]/(T^2+1)", "field_bits": 80,
                     "seed_curve": "E_0 : y^2 = x^3 + x over F_p, j(E_0)=1728",
                     "q": p_meas * p_meas,
                     "log2_p_exact": log2_p_meas}
    R["j_pool"] = {"n_walk": PE.N_WALK, "walk_seeds": PE.WALK_SEEDS,
                   "pool": [[j[0], j[1]] for j in pool],
                   "chains": [[[jj[0], jj[1]] for jj in ch] for ch in chains],
                   "note": "cost of pool generation is EXCLUDED"}
    degenerate = [i for i, j in enumerate(pool)
                  if j == (0, 0) or j == (1728 % p_meas, 0)]
    R["j_pool"]["degenerate_excluded_indices"] = degenerate
    active = [i for i in range(len(pool)) if i not in degenerate]
    cb1 = PE.control_c_base_1(
        p_meas, random.Random("%s|cbase1|%d" % (EXPERIMENT_ID, BOOTSTRAP_SEED)))
    R["controls"]["C-BASE.1"] = cb1
    R["phases"]["pool_and_cbase1_seconds"] = round(time.time() - t, 3)
    log("  C-BASE.1 verdict: %s; active j indices %s" % (cb1["verdict"], active))
    if cb1["verdict"] != "pass":
        R["validity"] = {"status": "invalid_measurement",
                         "reason": "C-BASE.1 failed"}
        flush_partial("cbase1-fail")
        return 4

    PE._G["mod"] = mod_by_ell
    PE._G["pool"] = pool

    pass1_j = [i for i in active if i < 4]
    pass2_j = [i for i in active if i >= 4]

    # ======================================================================
    # STEP 5 -- C-NULL over EVERY acquired ell, j 0..7, both implementations
    # ======================================================================
    t = time.time()
    log("step 5: C-NULL over every acquired ell (%d), j %s, both "
        "implementations" % (len(acquired), active))
    tasks_n = [(ell, ji, impl) for ell in acquired for ji in active
               for impl in ("IMPL-A", "IMPL-B")]
    recs_n = run_tasks(tasks_n, _null_worker, "C-NULL",
                       T0 + args.no_new_measurement_after)
    R["phases"]["c_null_seconds"] = round(time.time() - t, 3)
    log("  C-NULL: %d/%d samples in %.1fs"
        % (len(recs_n), len(tasks_n), time.time() - t))
    null_ell_covered = sorted({r["ell"] for r in recs_n})
    flush_partial("C-NULL complete")

    # ======================================================================
    # STEP 6 -- primary PASS 1 (j 0..3, both implementations interleaved)
    # ======================================================================
    t = time.time()
    log("step 6: primary PASS 1, j %s, IMPL-A/IMPL-B interleaved, ascending "
        "ell" % pass1_j)
    tasks_p1 = [(ell, ji, impl) for ell in acquired for ji in pass1_j
                for impl in ("IMPL-A", "IMPL-B")]
    recs_p1 = run_tasks(tasks_p1, _primary_worker, "PASS1",
                        T0 + args.no_new_measurement_after)
    R["phases"]["primary_pass1_seconds"] = round(time.time() - t, 3)
    log("  PASS 1: %d/%d samples in %.1fs"
        % (len(recs_p1), len(tasks_p1), time.time() - t))
    flush_partial("pass 1 complete")

    # ======================================================================
    # STEP 7 -- C-BASE.3/.4/.5/.6, C-ALT.1, C-ALT.2, C-REPRO
    # ======================================================================
    t = time.time()
    log("step 7: C-BASE.3/.4/.5/.6, C-ALT.1, C-ALT.2, C-REPRO")

    def cbase3_over(recs):
        dev, tot, good = [], 0, 0
        for r in recs:
            tot += 1
            if r["n_distinct_roots"] == r["ell"] + 1:
                good += 1
            else:
                dev.append({"ell": r["ell"], "j_index": r["j_index"],
                            "impl": r["impl"],
                            "n_distinct_roots": r["n_distinct_roots"],
                            "expected": r["ell"] + 1})
        frac = good / tot if tot else 0.0
        return {"samples": tot, "with_exactly_ell_plus_1_roots": good,
                "fraction": frac, "deviating_samples": dev,
                "verdict": "pass" if frac >= 0.90 else "fail"}

    def calt1_over(recs):
        badroots = sum(r["roots_failing_independent_horner"] for r in recs)
        mism = [{"ell": r["ell"], "j_index": r["j_index"], "impl": r["impl"],
                 "n_roots": r["n_distinct_roots"],
                 "deg_gcd": r["deg_gcd_xq_minus_x"]}
                for r in recs if r["n_distinct_roots"] != r["deg_gcd_xq_minus_x"]]
        return {"roots_checked": sum(r["n_distinct_roots"] for r in recs),
                "roots_failing_independent_horner": badroots,
                "samples_where_n_roots_differs_from_deg_gcd": mism,
                "verdict": "pass" if (badroots == 0 and not mism) else "fail"}

    cb3 = cbase3_over(recs_p1)
    cb3["id"] = "C-BASE.3"
    cb3["scope"] = "pass-1 primary samples (step-7 position of the frozen order)"
    R["controls"]["C-BASE.3"] = cb3
    ca1 = calt1_over(recs_p1)
    ca1["id"] = "C-ALT.1"
    ca1["scope"] = "pass-1 primary samples (step-7 position)"
    ca1["independent_check"] = ("every reported root re-evaluated by an "
                                "uninstrumented Horner path; root count "
                                "compared with deg(gcd(x^{p^2}-x, f))")
    R["controls"]["C-ALT.1"] = ca1
    log("  C-BASE.3 %s (%.4f), C-ALT.1 %s"
        % (cb3["verdict"], cb3["fraction"], ca1["verdict"]))

    # C-BASE.4 -- frozen-PoC agreement
    from fractions import Fraction
    rootcache = {}

    def rootfn(l, jj):
        key = (l, jj)
        if key in rootcache:
            return rootcache[key]
        Mx = mod_by_ell.get(l)
        if Mx is None:
            raise RuntimeError("Phi_%d not available for C-BASE.4" % l)
        f = PE.instantiate(Mx, l, jj)
        rr, _d, _a = PE.distinct_roots(
            f, PE.poly_mul_school,
            random.Random("%s|poc|%d|%d|%d" % (EXPERIMENT_ID, l, jj[0], jj[1])))
        rootcache[key] = rr
        return rr

    cbase4 = []
    edges = set()
    pairs = [(2, 16), (2, 64), (3, 27), (3, 81)]
    for ji in active:
        running = 0
        start = pool[ji]
        for (B, X) in pairs + [(5, 125)]:
            if (B, X) == (5, 125) and running >= 20000:
                cbase4.append({"j_index": ji, "B": B, "X": X,
                               "executed": False,
                               "reason": "running total >= 20000"})
                continue
            if B not in mod_by_ell:
                cbase4.append({"j_index": ji, "B": B, "X": X,
                               "executed": False,
                               "reason": "Phi_%d not acquired" % B})
                continue
            exp = PE.poc_count(B, Fraction(X))
            n = 0
            for ch in PE.poc_isogs(B, Fraction(X), [start], rootfn):
                n += 1
                if len(ch) >= 3:
                    edges.add((ch[-2], ch[-3], ch[-1]))
            running += n
            cbase4.append({"j_index": ji, "B": B, "X": X, "executed": True,
                           "count_B_X": exp, "chains_enumerated": n,
                           "exact": bool(n == exp),
                           "chains_le_count": bool(n <= exp)})
    ex = [c for c in cbase4 if c.get("executed")]
    if ex and all(c["exact"] for c in ex):
        v4 = "pass"
    elif ex and all(c["chains_le_count"] for c in ex):
        v4 = "pass_with_observation"
    else:
        v4 = "fail"
    R["controls"]["C-BASE.4"] = {
        "id": "C-BASE.4",
        "note": ("SageMath is not installed, so the frozen PoC is not "
                 "executed; count() and isogs() are the instrument's own "
                 "pure-Python re-implementations, called here. The "
                 "enumeration runs from EVERY pool member; count(B,X) is "
                 "j-independent."),
        "per_start": cbase4, "verdict": v4}
    log("  C-BASE.4 verdict: %s" % v4)

    # C-BASE.5 -- chain relations via the independent bivariate evaluator
    cb5_bad, checked = [], 0
    for (l, j0, j1) in sorted(edges):
        if l not in terms_by_ell:
            continue
        if PE.bivariate_eval_independent(terms_by_ell[l], p_meas, j0, j1,
                                         l) != PE.ZERO:
            cb5_bad.append({"ell": l, "j0": list(j0), "j1": list(j1)})
        checked += 1
    n_from_chains = checked
    rng5 = random.Random("%s|cbase5|%d" % (EXPERIMENT_ID, BOOTSTRAP_SEED))
    triples = []
    for ch in chains:
        for i in range(len(ch) - 1):
            triples.append((2, ch[i], ch[i + 1]))
    for ell in sorted(terms_by_ell):
        for ji in active[:2]:
            f = PE.instantiate(mod_by_ell[ell], ell, pool[ji])
            rr, _d, _a = PE.distinct_roots(
                f, PE.poly_mul_school,
                random.Random("%s|cb5r|%d|%d" % (EXPERIMENT_ID, ell, ji)))
            for z in rr:
                triples.append((ell, pool[ji], z))
    rng5.shuffle(triples)
    sample100 = triples[:100]
    for (l, j0, j1) in sample100:
        if PE.bivariate_eval_independent(terms_by_ell[l], p_meas, j0, j1,
                                         l) != PE.ZERO:
            cb5_bad.append({"ell": l, "j0": list(j0), "j1": list(j1)})
        checked += 1
    R["controls"]["C-BASE.5"] = {
        "id": "C-BASE.5",
        "unique_chain_edges_from_C_BASE_4_verified": n_from_chains,
        "random_triples_verified": len(sample100),
        "ell_present_in_random_sample": sorted({l for (l, _a, _b) in sample100}),
        "total_relations_verified": checked,
        "nonvanishing_relations": cb5_bad,
        "scope_note": ("the independent evaluator consumes the INTEGER "
                       "coefficient array, retained for ell <= 101"),
        "verdict": "pass" if not cb5_bad else "fail"}
    R["controls"]["C-BASE.6"] = {
        "id": "C-BASE.6",
        "statement": ("Section 4.1 of the frozen paper assumes one "
                      "F_{p^2}-operation per table entry, i.e. per_entry = 1 "
                      "in the unit reported here; under "
                      "log2 per_entry = gamma*log2 ell + const that is "
                      "gamma_paper = 0."),
        "gamma_paper": 0.0, "verdict": "pass"}
    log("  C-BASE.5: %d relations verified -> %s"
        % (checked, R["controls"]["C-BASE.5"]["verdict"]))
    R["phases"]["controls_step7_seconds"] = round(time.time() - t, 3)
    flush_partial("step 7 controls complete")

    # ======================================================================
    # STEP 8 -- primary PASS 2 (j 4..7)
    # ======================================================================
    recs_p2 = []
    pass2 = {"attempted": False, "reason": None,
             "j_indices": pass2_j, "completed_ell": []}
    if pass2_j and elapsed() < args.pass2_start_before:
        pass2["attempted"] = True
        t = time.time()
        log("step 8: primary PASS 2, j %s, both implementations interleaved"
            % pass2_j)
        got_all = True
        for ell in acquired:
            if elapsed() >= args.pass2_abort_at:
                pass2["reason"] = ("aborted before ell=%d at t=%.1fs (>= %.0fs)"
                                   % (ell, elapsed(), args.pass2_abort_at))
                log("  " + pass2["reason"])
                got_all = False
                break
            tasks = [(ell, ji, impl) for ji in pass2_j
                     for impl in ("IMPL-A", "IMPL-B")]
            got = run_tasks(tasks, _primary_worker, "PASS2 ell=%d" % ell,
                            T0 + args.no_new_measurement_after)
            if len(got) == len(tasks):
                recs_p2.extend(got)
                pass2["completed_ell"].append(ell)
            else:
                pass2["reason"] = ("ell=%d incomplete (%d/%d); its pass-2 "
                                   "samples are discarded"
                                   % (ell, len(got), len(tasks)))
                log("  " + pass2["reason"])
                got_all = False
                break
        if got_all:
            pass2["reason"] = "complete over every acquired ell"
        R["phases"]["primary_pass2_seconds"] = round(time.time() - t, 3)
        log("  PASS 2: %d samples over %d ell"
            % (len(recs_p2), len(pass2["completed_ell"])))
    else:
        pass2["reason"] = ("not started: t=%.1fs >= %.0fs"
                           % (elapsed(), args.pass2_start_before)
                           if pass2_j else "no pass-2 j indices active")
        log("step 8: PASS 2 %s" % pass2["reason"])
    R["pass2"] = pass2
    flush_partial("pass 2 complete")

    # ======================================================================
    # STEP 9 -- C-SEED
    # ======================================================================
    t = time.time()
    cseed_ell = [e for e in C_SEED_ELL if e in mod_by_ell]
    log("step 9: C-SEED over ell %s, j %s" % (cseed_ell, C_SEED_J))
    tasks_cs = [(ell, ji) for ell in cseed_ell for ji in C_SEED_J
                if ji in active]
    recs_cs = (run_tasks(tasks_cs, _cseed_worker, "C-SEED",
                         T0 + args.no_new_measurement_after)
               if tasks_cs else [])
    R["phases"]["c_seed_seconds"] = round(time.time() - t, 3)

    # ======================================================================
    # STEP 10 -- optional tail
    # ======================================================================
    tail = {"attempted": False, "ell_completed": [], "fetch_records": []}
    remaining = args.budget_seconds - elapsed()
    if (not args.skip_tail) and remaining >= args.tail_min_remaining:
        tail["attempted"] = True
        log("step 10: optional tail (%.0fs remain)" % remaining)
        for ell in OPTIONAL_TAIL:
            if args.budget_seconds - elapsed() < args.tail_min_remaining:
                break
            recs, _fs, _fb = PE.fetch_modpolys([ell], outdir, log)
            tail["fetch_records"].extend(recs)
            if recs[0]["status"] != "ok":
                dropped[ell] = recs[0]["status"]
                continue
            terms, saw, dup = PE.parse_modpoly(recs[0]["local_path"])
            v = PE.verify_modpoly(ell, terms, saw, dup)
            cbase2.append(v)
            if v["verdict"] != "pass":
                dropped[ell] = "C-BASE.2 verification failure"
                continue
            Mt = PE.reduce_modpoly(ell, terms, p_meas)
            recs[0]["coefficient_count_in_file"] = len(terms)
            recs[0]["reduced_array_sha256"] = PE.canonical_reduced_sha256(
                Mt, ell)
            del terms
            mod_by_ell[ell] = Mt
            PE._G["mod"] = mod_by_ell
            # membership rule: the null runs FIRST at each tail ell
            tn = [(ell, ji, impl) for ji in active
                  for impl in ("IMPL-A", "IMPL-B")]
            gn = run_tasks(tn, _null_worker, "tail-null ell=%d" % ell,
                           T0 + args.no_new_measurement_after)
            tp = [(ell, ji, impl) for ji in pass1_j
                  for impl in ("IMPL-A", "IMPL-B")]
            gp = run_tasks(tp, _primary_worker, "tail ell=%d" % ell,
                           T0 + args.no_new_measurement_after)
            if len(gn) == len(tn) and len(gp) == len(tp):
                recs_n.extend(gn)
                recs_p1.extend(gp)
                tail["ell_completed"].append(ell)
                acquired = sorted(mod_by_ell)
            else:
                log("  tail ell=%d incomplete; discarded" % ell)
                break
    else:
        tail["reason"] = (
            ("declined by --skip-tail: the tail is explicitly OPTIONAL and "
             "non-gating (binds_completion_gate: false). Execution order "
             "step 10 measures a tail ell at j-indices 0..3 only, so "
             "admitting one would force the common j-index set of the "
             "PRIMARY fit down to {0..3} and demote the {0..7} fit that the "
             "j_set_rule designates primary; and every tail fetch in "
             "RUN-PEC-6be870-a returned a fetch obstruction at the per-ell "
             "64 MiB cap, so the expected yield is zero. Recorded as a "
             "decision, not a result.")
            if args.skip_tail else
            ("%.0fs remain, %.0fs required" % (remaining,
                                               args.tail_min_remaining)))
        log("step 10: optional tail not attempted -- %s" % tail["reason"])
        R["protocol_deviations"].append({
            "id": "D-2",
            "what": "the OPTIONAL tail ell 223..251 was not attempted",
            "why": tail["reason"],
            "binds_completion_gate": False,
            "recorded_not_tuned": True})
    R["optional_tail"] = tail
    R["modular_polynomial_provenance"]["per_ell"].extend(
        tail["fetch_records"])
    R["dropped_ell"] = dropped

    # ======================================================================
    # sample tables
    # ======================================================================
    R["samples_primary"] = sorted(recs_p1 + recs_p2,
                                  key=lambda r: (r["impl"], r["ell"],
                                                 r["j_index"]))
    R["samples_null"] = sorted(recs_n, key=lambda r: (r["impl"], r["ell"],
                                                      r["j_index"]))
    R["samples_c_seed"] = sorted(recs_cs, key=lambda r: (r["ell"],
                                                         r["j_index"]))
    per_pid = {}
    for r in R["samples_primary"] + R["samples_null"] + R["samples_c_seed"]:
        per_pid.setdefault(str(r["pid"]), {"mults": 0, "samples": 0})
        per_pid[str(r["pid"])]["mults"] += r["cost"]
        per_pid[str(r["pid"])]["samples"] += 1
    R["worker_accounting"] = {
        "per_pid": per_pid,
        "sum_of_worker_mults": sum(v["mults"] for v in per_pid.values()),
        "sum_of_sample_costs": sum(
            r["cost"] for r in R["samples_primary"] + R["samples_null"]
            + R["samples_c_seed"])}
    R["worker_accounting"]["agrees"] = bool(
        R["worker_accounting"]["sum_of_worker_mults"]
        == R["worker_accounting"]["sum_of_sample_costs"])
    R["counted_multiplications_total_all_measured_regions"] = (
        R["worker_accounting"]["sum_of_sample_costs"])

    # final pass of C-BASE.3 / C-ALT.1 over every primary sample
    fp3 = cbase3_over(R["samples_primary"])
    fp3["scope"] = "every primary sample of the run"
    R["controls"]["C-BASE.3"]["final_pass_over_all_samples"] = fp3
    fp1 = calt1_over(R["samples_primary"])
    fp1["scope"] = "every primary sample of the run"
    R["controls"]["C-ALT.1"]["final_pass_over_all_samples"] = fp1
    if fp3["verdict"] != "pass":
        R["controls"]["C-BASE.3"]["verdict"] = fp3["verdict"]
    if fp1["verdict"] != "pass":
        R["controls"]["C-ALT.1"]["verdict"] = fp1["verdict"]
    iso_bad = [r for r in R["samples_primary"] + R["samples_null"]
               if not r["counter_isolation_ok"]]
    R["controls"]["C-INSTR"]["per_sample_isolation_failures"] = len(iso_bad)

    # per-ell C-BASE.3 fractions (membership condition C-4)
    cb3_by_ell = {}
    for r in R["samples_primary"]:
        d = cb3_by_ell.setdefault(r["ell"], [0, 0])
        d[1] += 1
        if r["n_distinct_roots"] == r["ell"] + 1:
            d[0] += 1
    R["controls"]["C-BASE.3"]["per_ell_fraction"] = {
        str(e): {"with_exactly_ell_plus_1_roots": v[0], "samples": v[1],
                 "fraction": v[0] / v[1]} for e, v in sorted(cb3_by_ell.items())}
    R["controls"]["C-BASE.3"]["per_ell_reading"] = (
        "membership condition C-4 reads 'the ell passed C-BASE.2 and "
        "C-BASE.3'; C-BASE.3's pass criterion is a >= 0.90 fraction, applied "
        "here per ell over that ell's own primary samples")

    # ---- C-ALT.2 ----------------------------------------------------------
    ha = {(r["ell"], r["j_index"]): r["roots_sha256"]
          for r in R["samples_primary"] if r["impl"] == "IMPL-A"}
    hb = {(r["ell"], r["j_index"]): r["roots_sha256"]
          for r in R["samples_primary"] if r["impl"] == "IMPL-B"}
    shared = sorted(set(ha) & set(hb))
    diff = [{"ell": k[0], "j_index": k[1]} for k in shared if ha[k] != hb[k]]
    R["controls"]["C-ALT.2"] = {
        "id": "C-ALT.2", "compared_samples": len(shared),
        "root_set_mismatches": diff,
        "impl_a": "schoolbook polynomial multiplication",
        "impl_b": "Karatsuba polynomial multiplication",
        "coverage_note": ("an ell at which only one implementation has data "
                          "is EXCLUDED from every fitted window by the "
                          "membership rule, so C-ALT.2 cannot be incomplete "
                          "on the fitted range by construction"),
        "seed_policy": ("PAIRED: CZ seeded on (ell, j_index) and NOT on "
                        "implementation. gamma_A and gamma_B are therefore "
                        "NON-INDEPENDENT estimates and their difference is a "
                        "measurement of the multiplication-routine effect "
                        "under a FIXED split structure."),
        "verdict": "pass" if not diff else "fail"}

    # ---- C-SEED -----------------------------------------------------------
    hbp = {(r["ell"], r["j_index"]): r for r in recs_cs}
    cs_pairs, cs_bad = [], []
    for (ell, ji), rp in sorted(hbp.items()):
        base = next((r for r in R["samples_primary"]
                     if r["impl"] == "IMPL-B" and r["ell"] == ell
                     and r["j_index"] == ji), None)
        if base is None:
            continue
        same = (rp["roots_sha256"] == base["roots_sha256"])
        if not same:
            cs_bad.append({"ell": ell, "j_index": ji})
        cs_pairs.append({"ell": ell, "j_index": ji, "root_sets_identical": same,
                         "cost_B": base["cost"], "cost_B_prime": rp["cost"],
                         "cost_ratio_Bprime_over_B": rp["cost"] / base["cost"],
                         "cz_attempts_B": base["cz_attempts"],
                         "cz_attempts_B_prime": rp["cz_attempts"],
                         "cz_seed_string_B": base["cz_seed_string"],
                         "cz_seed_string_B_prime": rp["cz_seed_string"]})
    ratios = [c["cost_ratio_Bprime_over_B"] for c in cs_pairs]
    R["controls"]["C-SEED"] = {
        "id": "C-SEED", "pairs": cs_pairs, "n_pairs": len(cs_pairs),
        "root_set_disagreements": cs_bad,
        "cost_ratio_min": min(ratios) if ratios else None,
        "cost_ratio_max": max(ratios) if ratios else None,
        "cost_ratio_median": PE.median(ratios) if ratios else None,
        "not_in_the_primary_fit": True,
        "verdict": ("pass" if (cs_pairs and not cs_bad)
                    else ("incomplete" if not cs_pairs else "fail"))}
    log("  C-SEED: %d pairs, %d disagreements"
        % (len(cs_pairs), len(cs_bad)))

    # ---- C-REPRO ----------------------------------------------------------
    sup_prim = {(s["ell"], s["j_index"], s["impl"]): s
                for s in S["samples_primary"]}
    sup_null = {(s["ell"], s["j_index"], s["impl"]): s
                for s in S["samples_null"]}
    prim_fields = ["mults_instantiate", "mults_rootfind", "cost",
                   "inv_instantiate", "inv_rootfind", "inversions",
                   "n_distinct_roots", "deg_gcd_xq_minus_x", "cz_attempts",
                   "entries", "per_entry", "roots_sha256"]
    null_fields = ["cost", "inversions", "entries", "per_entry",
                   "entries_alt_denominator", "steps"]
    repro_rows, repro_bad = 0, []
    for r in R["samples_primary"]:
        k = (r["ell"], r["j_index"], r["impl"])
        s = sup_prim.get(k)
        if s is None:
            continue
        repro_rows += 1
        for fld in prim_fields:
            if r.get(fld) != s.get(fld):
                repro_bad.append({"triple": list(k), "series": "primary",
                                  "field": fld, "this_run": r.get(fld),
                                  "superseded": s.get(fld)})
    null_rows = 0
    for r in R["samples_null"]:
        k = (r["ell"], r["j_index"], r["impl"])
        s = sup_null.get(k)
        if s is None:
            continue
        null_rows += 1
        for fld in null_fields:
            if r.get(fld) != s.get(fld):
                repro_bad.append({"triple": list(k), "series": "null",
                                  "field": fld, "this_run": r.get(fld),
                                  "superseded": s.get(fld)})
    R["controls"]["C-REPRO"] = {
        "id": "C-REPRO",
        "superseded_raw_result_sha256": sup_sha,
        "overlapping_primary_triples": repro_rows,
        "overlapping_null_triples": null_rows,
        "fields_compared_primary": prim_fields,
        "fields_compared_null": null_fields,
        "disagreements": repro_bad,
        "n_disagreements": len(repro_bad),
        "agreeing_triples": repro_rows + null_rows - len(
            {tuple(d["triple"]) for d in repro_bad}),
        "verdict": "pass" if not repro_bad else "fail"}
    log("  C-REPRO: %d primary + %d null overlapping triples, %d "
        "disagreements" % (repro_rows, null_rows, len(repro_bad)))

    # ======================================================================
    # STEP 11 -- aggregation, membership audit, fits, extrapolation
    # ======================================================================
    t = time.time()
    log("step 11: aggregation, membership audit, fits, extrapolation")

    def per_ell_map(recs, impl):
        d = {}
        for r in recs:
            if r["impl"] != impl or r.get("per_entry") is None:
                continue
            d.setdefault(r["ell"], {})[r["j_index"]] = r["per_entry"]
        return d

    tabA = per_ell_map(R["samples_primary"], "IMPL-A")
    tabB = per_ell_map(R["samples_primary"], "IMPL-B")
    tabN = {}
    for r in R["samples_null"]:
        tabN.setdefault(r["ell"], {}).setdefault(r["impl"], {})[
            r["j_index"]] = r["per_entry"]

    membership = []
    admitted = []
    for ell in sorted(set(tabA) | set(tabB) | set(tabN)):
        c1 = ell in tabA and ell in tabB
        c2 = c1 and set(tabA[ell]) == set(tabB[ell])
        c3 = ell in tabN
        cb2ok = ell in mod_by_ell
        cb3ok = (cb3_by_ell.get(ell, [0, 1])[0]
                 / max(cb3_by_ell.get(ell, [0, 1])[1], 1)) >= 0.90
        c4 = cb2ok and cb3ok
        ok = c1 and c2 and c3 and c4
        row = {"ell": ell, "admitted": bool(ok),
               "C-1_both_implementations": bool(c1),
               "C-2_identical_j_sets": bool(c2),
               "C-3_null_coverage": bool(c3),
               "C-4_cbase2_and_cbase3": bool(c4),
               "j_indices_A": sorted(tabA.get(ell, {})),
               "j_indices_B": sorted(tabB.get(ell, {}))}
        if not ok:
            row["excluded_because"] = [
                n for n, v in [("C-1", c1), ("C-2", c2), ("C-3", c3),
                               ("C-4", c4)] if not v]
        membership.append(row)
        if ok:
            admitted.append(ell)
    R["membership_audit"] = membership
    log("  admitted ell: %d of %d acquired" % (len(admitted), len(acquired)))

    common_j = None
    for ell in admitted:
        s = set(tabA[ell]) & set(tabB[ell])
        common_j = s if common_j is None else (common_j & s)
    common_j = sorted(common_j or [])
    j_subset = sorted(i for i in common_j if i < 4)
    log("  common j-index set across every admitted ell: %s" % common_j)

    def build_series(jset):
        A = {e: PE.median([tabA[e][i] for i in jset if i in tabA[e]])
             for e in admitted}
        B = {e: PE.median([tabB[e][i] for i in jset if i in tabB[e]])
             for e in admitted}
        MIN = {e: min(A[e], B[e]) for e in admitted}
        return {"S-A": A, "S-B": B, "S-MIN": MIN}

    SER = build_series(common_j)
    SER_SUB = build_series(j_subset) if j_subset != common_j else None

    WIN = {"W-ALL": list(admitted),
           "W-MID": [e for e in admitted if e >= 11],
           "W-TOP": sorted(admitted)[-8:]}
    R["windows"] = {w: e for w, e in WIN.items()}

    NESTED = {"ell>=11": [e for e in admitted if e >= 11],
              "ell>=23": [e for e in admitted if e >= 23],
              "ell>=43": [e for e in admitted if e >= 43],
              "ell>=101": [e for e in admitted if e >= 101]}

    # ---- cluster bootstrap over the COMMON j set --------------------------
    reps = args.bootstrap_replicates
    brng = random.Random(BOOTSTRAP_SEED)
    boot = {s: {w: {"slope": [], "intercept": [],
                    "D": {k["log2p"]: [] for k in VOW_CONSTANTS}}
                for w in WIN} for s in ("S-A", "S-B", "S-MIN")}
    boot_quad = {s: {q: [] for q in ["W-ALL"] + list(NESTED)}
                 for s in ("S-A", "S-B", "S-MIN")}
    boot_gapAB = {w: [] for w in WIN}
    attempted = completed = 0
    skipped = []
    for _ in range(reps):
        attempted += 1
        pick = [common_j[brng.randrange(len(common_j))]
                for _ in range(len(common_j))]
        A = {}
        B = {}
        for e in admitted:
            va = [tabA[e][i] for i in pick if i in tabA[e]]
            vb = [tabB[e][i] for i in pick if i in tabB[e]]
            if va:
                A[e] = PE.median(va)
            if vb:
                B[e] = PE.median(vb)
        if len(A) != len(admitted) or len(B) != len(admitted):
            skipped.append("replicate lost an ell under resampling")
            continue
        M = {e: min(A[e], B[e]) for e in admitted}
        ser = {"S-A": A, "S-B": B, "S-MIN": M}
        ok = True
        for s in ser:
            for w, wells in WIN.items():
                if len(wells) < 3:
                    ok = False
                    continue
                f = fit_series(ser[s], wells)
                boot[s][w]["slope"].append(f["slope"])
                boot[s][w]["intercept"].append(f["intercept"])
                for k in VOW_CONSTANTS:
                    boot[s][w]["D"][k["log2p"]].append(
                        f["intercept"] + f["slope"] * k["log2_B_opt"])
            for q, qells in [("W-ALL", WIN["W-ALL"])] + list(NESTED.items()):
                if len(qells) >= 4:
                    xs = [math.log2(e) for e in qells]
                    ys = [math.log2(ser[s][e]) for e in qells]
                    boot_quad[s][q].append(PE.quad_fit(xs, ys)["c"])
        for w, wells in WIN.items():
            if len(wells) >= 3:
                boot_gapAB[w].append(fit_series(ser["S-A"], wells)["slope"]
                                     - fit_series(ser["S-B"], wells)["slope"])
        if ok:
            completed += 1
    log("  bootstrap: %d attempted, %d completed" % (attempted, completed))

    # ---- point fits -------------------------------------------------------
    fits = {}
    for s, series in SER.items():
        fits[s] = {}
        for w, wells in WIN.items():
            if len(wells) < 3:
                continue
            f = fit_series(series, wells)
            tq = PE.t_quantile_975(f["n"] - 2) if f["n"] > 2 else float("nan")
            bs = boot[s][w]["slope"]
            bi = boot[s][w]["intercept"]
            jk = jackknife_leave_one_ell(series, wells)
            fits[s][w] = {
                "ell": wells, "n": f["n"],
                "gamma_hat": f["slope"], "intercept_log2_A": f["intercept"],
                "slope_se": f["slope_se"],
                "t_quantile_0975_df": tq,
                "analytic_ci95_slope": [f["slope"] - tq * f["slope_se"],
                                        f["slope"] + tq * f["slope_se"]],
                "bootstrap_ci95_slope": ([PE.percentile(bs, 0.025),
                                          PE.percentile(bs, 0.975)]
                                         if bs else [None, None]),
                "bootstrap_ci95_intercept": ([PE.percentile(bi, 0.025),
                                              PE.percentile(bi, 0.975)]
                                             if bi else [None, None]),
                "bootstrap_replicates_used": len(bs),
                "jackknife": jk,
                "r2": f["r2"], "max_abs_residual": f["max_abs_residual"],
                "residuals": {str(e): r for e, r in zip(wells, f["residuals"])},
                "per_ell_level": {str(e): series[e] for e in wells}}
        lo = min(fits[s][w]["bootstrap_ci95_slope"][0]
                 for w in fits[s] if fits[s][w]["bootstrap_ci95_slope"][0]
                 is not None)
        hi = max(fits[s][w]["bootstrap_ci95_slope"][1]
                 for w in fits[s] if fits[s][w]["bootstrap_ci95_slope"][1]
                 is not None)
        fits[s]["gamma_reported_interval"] = [lo, hi]
        fits[s]["gamma_reported_halfwidth"] = (hi - lo) / 2.0

    # curvature
    curv = {}
    for s, series in SER.items():
        curv[s] = {}
        for q, qells in [("W-ALL", WIN["W-ALL"])] + list(NESTED.items()):
            if len(qells) < 4:
                continue
            xs = [math.log2(e) for e in qells]
            ys = [math.log2(series[e]) for e in qells]
            qf = PE.quad_fit(xs, ys)
            bq = boot_quad[s][q]
            ci = ([PE.percentile(bq, 0.025), PE.percentile(bq, 0.975)]
                  if bq else [None, None])
            xmax = max(xs)
            curv[s][q] = {
                "n": len(qells), "a": qf["a"], "b": qf["b"], "c": qf["c"],
                "c_bootstrap_ci95": ci,
                "ci_excludes_zero": bool(ci[0] is not None
                                         and (ci[0] > 0 or ci[1] < 0)),
                "x_max": xmax,
                "gamma_local_top": qf["b"] + 2 * qf["c"] * xmax,
                "quadratic_own_level_at_x_max": (qf["a"] + qf["b"] * xmax
                                                 + qf["c"] * xmax * xmax),
                "pairing_rule": ("gamma_local_top is paired with the "
                                 "QUADRATIC fit's own level at x_max, never "
                                 "with the linear fit's intercept")}

    # ---- corrected c table ------------------------------------------------
    c_rows = []
    for s in SER:
        for w in WIN:
            if w not in fits[s]:
                continue
            c_rows.extend(c_table_rows(
                "NC2a seam-free fit (this run)", s, w,
                fits[s][w]["intercept_log2_A"], fits[s][w]["gamma_hat"],
                log2_p_meas, boot[s][w]["D"]))
    headline = []
    for k in VOW_CONSTANTS:
        rb = next(r for r in c_rows if r["series"] == "S-B"
                  and r["window"] == "W-MID" and r["alpha"] == 0
                  and r["log2p"] == k["log2p"])
        ra = next(r for r in c_rows if r["series"] == "S-A"
                  and r["window"] == "W-MID" and r["alpha"] == 1
                  and r["log2p"] == k["log2p"])
        headline.append({
            "field": k["name"], "log2p": k["log2p"],
            "bracket_low_c_S-B_W-MID_alpha0": rb["c_point"],
            "bracket_high_c_S-A_W-MID_alpha1": ra["c_point"],
            "label": ("NOT a confidence interval: a span across two declared "
                      "modelling choices (which implementation, and whether "
                      "the p-scaling is applied)")})

    # ---- f_indep guard on THIS run ---------------------------------------
    fi = {}
    for r in R["samples_primary"]:
        if r.get("cost"):
            fi.setdefault(r["ell"], []).append(
                r["mults_instantiate"] / r["cost"])
    fi_med = {e: PE.median(v) for e, v in fi.items()}
    fi_fitted = {e: fi_med[e] for e in admitted if e in fi_med}
    guard = {
        "quantity": "f_indep(ell) = mults_instantiate(ell) / cost(ell)",
        "per_ell_median": {str(e): fi_med[e] for e in sorted(fi_med)},
        "max_over_fitted_range": max(fi_fitted.values()) if fi_fitted else None,
        "max_over_individual_samples": max(max(v) for v in fi.values()),
        "threshold": F_INDEP_THRESHOLD,
        "satisfied": bool(fi_fitted
                          and max(fi_fitted.values()) <= F_INDEP_THRESHOLD),
        "structure_aware_form_required": bool(
            fi_fitted and max(fi_fitted.values()) > F_INDEP_THRESHOLD)}

    # ---- new full-range null: C-NULL verdict and NC2b-G1-prime ------------
    null_level = {}
    for e, byimpl in tabN.items():
        vals = [v for d in byimpl.values() for v in d.values()]
        null_level[e] = PE.median(vals)
    null_win = {"W-ALL": [e for e in WIN["W-ALL"] if e in null_level],
                "W-MID": [e for e in WIN["W-MID"] if e in null_level],
                "W-TOP": [e for e in WIN["W-TOP"] if e in null_level]}
    # cluster bootstrap for gamma_null over the same common j set
    nrng = random.Random(BOOTSTRAP_SEED)
    nboot = {w: [] for w in null_win}
    for _ in range(reps):
        pick = [common_j[nrng.randrange(len(common_j))]
                for _ in range(len(common_j))]
        m = {}
        for e, byimpl in tabN.items():
            vals = [d[i] for d in byimpl.values() for i in pick if i in d]
            if vals:
                m[e] = PE.median(vals)
        for w, wells in null_win.items():
            we = [e for e in wells if e in m]
            if len(we) >= 3:
                nboot[w].append(fit_series(m, we)["slope"])
    cnull = {"id": "C-NULL",
             "construction": ("ell+1 entries by ell+1 successive "
                              "non-backtracking 2-isogeny steps; identical "
                              "harness, denominator convention, aggregation "
                              "and fit"),
             "per_ell_per_entry": {str(e): null_level[e]
                                   for e in sorted(null_level)},
             "ell_measured": sorted(null_level),
             "coverage_fraction_per_window": {
                 w: {"covered": len(null_win[w]), "window_size": len(WIN[w]),
                     "fraction": (len(null_win[w]) / len(WIN[w])
                                  if WIN[w] else None)}
                 for w in WIN},
             "by_window": {}}
    for w, wells in null_win.items():
        if len(wells) < 3:
            continue
        f = fit_series(null_level, wells)
        bs = nboot[w]
        ci = ([PE.percentile(bs, 0.025), PE.percentile(bs, 0.975)]
              if bs else [None, None])
        cnull["by_window"][w] = {
            "n": f["n"], "gamma_null": f["slope"],
            "log2_A_null": f["intercept"],
            "bootstrap_ci95": ci,
            "abs_gamma_null_le_0_15": bool(abs(f["slope"]) <= 0.15),
            "ci_contains_zero": bool(ci[0] is not None
                                     and ci[0] <= 0 <= ci[1]),
            "REF_null_median_log2_per_entry": PE.median(
                [math.log2(null_level[e]) for e in wells])}
    cnull["pass_criterion"] = ("|gamma_null| <= 0.15 AND bootstrap 95% CI "
                               "contains 0, on each window")
    cnull["verdict"] = ("pass" if all(
        v["abs_gamma_null_le_0_15"] and v["ci_contains_zero"]
        for v in cnull["by_window"].values()) else "fail")
    smallest = min(null_level)
    largest = max(null_level)
    cnull["flatness"] = {
        "smallest_ell": smallest, "largest_ell": largest,
        "per_entry_smallest": null_level[smallest],
        "per_entry_largest": null_level[largest],
        "ratio_largest_over_smallest": null_level[largest] / null_level[smallest],
        "within_2_pm_0_5": bool(
            2 ** -0.5 <= null_level[largest] / null_level[smallest] <= 2 ** 0.5)}
    R["controls"]["C-NULL"] = cnull

    gprime = {"id": "NC2b-G1-prime", "status": "confirmatory",
              "tolerance_bits": NULL_GATE_TOLERANCE_BITS, "evaluations": []}
    for w, blk in cnull["by_window"].items():
        REF = blk["REF_null_median_log2_per_entry"]
        for k in VOW_CONSTANTS:
            N = blk["log2_A_null"] + blk["gamma_null"] * k["log2_B_opt"]
            gprime["evaluations"].append({
                "window": w, "field": k["name"], "log2p": k["log2p"],
                "N_null_bits": N, "REF_null_bits": REF,
                "abs_difference_bits": abs(N - REF),
                "margin_bits_remaining": NULL_GATE_TOLERANCE_BITS - abs(N - REF),
                "within_tolerance": bool(
                    abs(N - REF) <= NULL_GATE_TOLERANCE_BITS)})
    gprime["verdict"] = ("PASS" if all(e["within_tolerance"]
                                       for e in gprime["evaluations"])
                         else "FAIL")
    gprime["agrees_with_NC2b_G1"] = bool(gprime["verdict"] == gate["verdict"])
    R["nc2b_g1_prime"] = gprime

    # ---- C-PSCALE estimator ----------------------------------------------
    if pscale.get("arms"):
        p3_prim, p3_null = {}, {}
        for r in R["samples_primary"]:
            if (r["impl"] == "IMPL-A" and r["ell"] in PSCALE_ELL
                    and r["j_index"] in (0, 1, 2, 3)):
                p3_prim.setdefault(r["ell"], []).append(r["per_entry"])
        for r in R["samples_null"]:
            if (r["impl"] == "IMPL-A" and r["ell"] in PSCALE_ELL
                    and r["j_index"] in (0, 1, 2, 3)):
                p3_null.setdefault(r["ell"], []).append(r["per_entry"])
        points = []
        for a in pscale["arms"]:
            if a.get("status") != "ok":
                continue
            pr, nu = {}, {}
            for r in a["samples_primary"]:
                pr.setdefault(r["ell"], []).append(r["per_entry"])
            for r in a["samples_null"]:
                nu.setdefault(r["ell"], []).append(r["per_entry"])
            points.append({"label": a["label"], "log2_p": a["log2_p_exact"],
                           "primary": {e: PE.median(v) for e, v in pr.items()},
                           "null": {e: PE.median(v) for e, v in nu.items()}})
        points.append({"label": "p3 (primary measurement; no new work)",
                       "log2_p": log2_p_meas,
                       "primary": {e: PE.median(v) for e, v in p3_prim.items()},
                       "null": {e: PE.median(v) for e, v in p3_null.items()}})
        pscale["points"] = [{"label": q["label"], "log2_p": q["log2_p"],
                             "primary_median_per_entry":
                                 {str(e): v for e, v in q["primary"].items()},
                             "null_median_per_entry":
                                 {str(e): v for e, v in q["null"].items()}}
                            for q in points]

        def alpha_estimates(key):
            per_ell, num, den = {}, 0.0, 0.0
            contrib = {}
            for e in PSCALE_ELL:
                xs, ys = [], []
                for q in points:
                    if e in q[key]:
                        xs.append(math.log2(q["log2_p"]))
                        ys.append(math.log2(q[key][e]))
                if len(xs) >= 2:
                    f = PE.ols(xs, ys)
                    per_ell[e] = {"alpha_hat": f["slope"], "n_points": len(xs),
                                  "r2": f["r2"]}
                    mx = sum(xs) / len(xs)
                    my = sum(ys) / len(ys)
                    nn = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                    dd = sum((x - mx) ** 2 for x in xs)
                    contrib[e] = (nn, dd)
                    num += nn
                    den += dd
            pooled = num / den if den else None
            jk = []
            for e in contrib:
                n2 = num - contrib[e][0]
                d2 = den - contrib[e][1]
                if d2:
                    jk.append(n2 / d2)
            per_vals = [v["alpha_hat"] for v in per_ell.values()]
            return {"per_ell": {str(e): per_ell[e] for e in sorted(per_ell)},
                    "pooled_within_ell_fixed_effects": pooled,
                    "jackknife_leave_one_ell_out_range":
                        [min(jk), max(jk)] if jk else [None, None],
                    "per_ell_alpha_range":
                        [min(per_vals), max(per_vals)] if per_vals else
                        [None, None]}

        pscale["primary_arm"] = alpha_estimates("primary")
        pscale["null_arm"] = alpha_estimates("null")
        iv = pscale["primary_arm"]["jackknife_leave_one_ell_out_range"]
        pscale["interval_reading"] = (
            "'alpha_hat's interval' is read as the JACKKNIFE "
            "leave-one-ell-out range of the pooled estimate, the only "
            "interval the contract defines for C-PSCALE; the per-ell range "
            "is reported beside it as the alternative reading")
        contained = bool(iv[0] is not None and PSCALE_BAND[0] <= iv[0]
                         and iv[1] <= PSCALE_BAND[1])
        disjoint = bool(iv[0] is not None and (iv[1] < PSCALE_BAND[0]
                                               or iv[0] > PSCALE_BAND[1]))
        iv2 = pscale["primary_arm"]["per_ell_alpha_range"]
        contained2 = bool(iv2[0] is not None and PSCALE_BAND[0] <= iv2[0]
                          and iv2[1] <= PSCALE_BAND[1])
        disjoint2 = bool(iv2[0] is not None and (iv2[1] < PSCALE_BAND[0]
                                                 or iv2[0] > PSCALE_BAND[1]))
        pscale["band_verdict"] = ("CONTAINED" if contained else
                                  ("DISJOINT" if disjoint else "OVERLAPPING"))
        pscale["band_verdict_under_per_ell_range_reading"] = (
            "CONTAINED" if contained2 else
            ("DISJOINT" if disjoint2 else "OVERLAPPING"))
        pscale["readings_agree"] = bool(
            pscale["band_verdict"]
            == pscale["band_verdict_under_per_ell_range_reading"])
        pscale["alpha_primary_designation"] = (
            "alpha = 1, MEASURED-CONSISTENT" if contained else
            ("alpha = alpha_hat; alpha = 1 FALSIFIED (FC-2)" if disjoint
             else "alpha = 1, discrepancy declared (overlapping without "
                  "containment)"))
        da = None
        if (pscale["primary_arm"]["pooled_within_ell_fixed_effects"]
                is not None
                and pscale["null_arm"]["pooled_within_ell_fixed_effects"]
                is not None):
            da = abs(pscale["primary_arm"]["pooled_within_ell_fixed_effects"]
                     - pscale["null_arm"]["pooled_within_ell_fixed_effects"])
        pscale["FC-4_primary_minus_null_alpha_abs"] = da
        pscale["FC-4_fires"] = bool(da is not None and da > 0.15)
        if pscale["FC-4_fires"]:
            pscale["alpha_primary_designation"] += " -- MECHANISM-INCONSISTENT"
            pscale["FC-4_meaning"] = (
                "the derivation's claim that the p-scaling is a property of "
                "the shared poly_powmod loop and therefore common to both "
                "objects is contradicted by the measurement. The primary "
                "alpha designation is unchanged but is labelled "
                "MECHANISM-INCONSISTENT (specification FC-4).")
        # alpha_hat rows (reporting_requirement: 'plus alpha_hat rows if
        # C-PSCALE ran'; alpha_selection_rule adds both endpoints of
        # alpha_hat's interval when the band verdict is not CONTAINED)
        extra_alphas = []
        pooled = pscale["primary_arm"]["pooled_within_ell_fixed_effects"]
        if pooled is not None:
            extra_alphas.append(pooled)
        if pscale["band_verdict"] != "CONTAINED" and iv[0] is not None:
            extra_alphas.extend([iv[0], iv[1]])
        if extra_alphas:
            note = ("alpha_hat rows: pooled C-PSCALE estimate and, because "
                    "the band verdict is %s, both endpoints of the jackknife "
                    "interval. MEASURED at 40-, 60- and 80-bit fields, i.e. a "
                    "three-point basis carrying a `toy` ceiling on the two "
                    "small primes." % pscale["band_verdict"])
            for s in SER:
                for w in WIN:
                    if w not in fits[s]:
                        continue
                    c_rows.extend(c_table_rows(
                        "NC2a seam-free fit (this run), alpha_hat rows", s, w,
                        fits[s][w]["intercept_log2_A"], fits[s][w]["gamma_hat"],
                        log2_p_meas, boot[s][w]["D"],
                        alphas=tuple(extra_alphas), alpha_note=note))
            nc2b_extra = []
            for w, blk in carried["fit_windows"].items():
                nc2b_extra.extend(c_table_rows(
                    "NC2b corrected law applied to the CARRIED superseded "
                    "fit, alpha_hat rows",
                    "S-SUPERSEDED-MIN (carried; mixed-definition response)",
                    w, blk["intercept"], blk["gamma_hat"], log2_p_meas,
                    alphas=tuple(extra_alphas), alpha_note=note))
            nc2b["corrected_c_table_alpha_hat_rows"] = nc2b_extra
            nc2b["alpha_hat_rows_note"] = (
                "the alpha = 0 and alpha = 1 NC2b table was written to disk "
                "at the NC2b step, before any new measurement; these "
                "alpha_hat rows were appended in the fits phase once "
                "C-PSCALE had measured alpha. The NC2b gate verdict is "
                "evaluated at alpha = 0 and is unaffected.")
        pscale["scale_relevance_note"] = ("p1 and p2 are 40-bit and 60-bit "
                                          "fields, i.e. `toy`; C-PSCALE "
                                          "results carry a toy ceiling")
        log("  C-PSCALE: pooled alpha_hat = %s, jackknife range %s -> %s"
            % (pscale["primary_arm"]["pooled_within_ell_fixed_effects"],
               iv, pscale["band_verdict"]))

    # ---- pre-registered NC2a expectations ---------------------------------
    P = {}
    gA = fits["S-A"]["W-MID"]["gamma_hat"]
    gB = fits["S-B"]["W-MID"]["gamma_hat"]
    gM = fits["S-MIN"]["W-MID"]["gamma_hat"]
    P["P1a"] = {"statement": ("gamma(S-MIN,W-MID) <= max(gamma(S-A,W-MID), "
                             "gamma(S-B,W-MID)) on the identical window"),
                "gamma_S_MIN": gM, "gamma_S_A": gA, "gamma_S_B": gB,
                "max_constituent": max(gA, gB),
                "verdict": "MET" if gM <= max(gA, gB) + 1e-12 else "NOT MET",
                "kind": "CONSISTENCY CHECK, NOT A SCIENTIFIC PREDICTION",
                "if_not_met": ("the min construction or the fit code is "
                               "defective -> run INVALID pending "
                               "reconciliation")}
    P["P1b"] = {"statement": "gamma(S-MIN, W-MID) <= 0.9382",
                "threshold": 0.9382,
                "observed": gM,
                "difference_observed_minus_threshold": gM - 0.9382,
                "verdict": "MET" if gM <= 0.9382 else "NOT MET",
                "kind": "FALSIFIABLE SCIENTIFIC CONTENT",
                "stated_meaning_if_not_met": (
                    "with a genuinely seam-free response the composition "
                    "explanation of DEC-20260802-8227b9 adjudication B would "
                    "be INCOMPLETE: part of the superseded elevation would "
                    "reflect a real steepening between ell=101 and ell=211 "
                    "that survives homogenisation. The Coordinator "
                    "re-adjudicates; the Executor states the fact and stops.")}
    qc = curv["S-MIN"]["W-ALL"]
    P["P2"] = {"statement": ("W-ALL quadratic coefficient of the seam-free "
                             "S-MIN series strictly below 0.0453"),
               "threshold": 0.0453, "observed_c": qc["c"],
               "c_bootstrap_ci95": qc["c_bootstrap_ci95"],
               "ci_excludes_zero": qc["ci_excludes_zero"],
               "verdict": "MET" if qc["c"] < 0.0453 else "NOT MET",
               "kind": "FALSIFIABLE SCIENTIFIC CONTENT",
               "stated_meaning_if_not_met": (
                   "the curvature was NOT predominantly a composition "
                   "artifact; DEC-20260802-8227b9 adjudication C's magnitude "
                   "ruling would be contradicted by new data and the "
                   "Coordinator must re-adjudicate.")}
    P["P3"] = {"statement": "on the common window, gamma(S-A) - gamma(S-B) >= 0.10",
               "window": "W-MID (primary)",
               "gamma_A": gA, "gamma_B": gB, "difference": gA - gB,
               "bootstrap_ci95_of_difference":
                   ([PE.percentile(boot_gapAB["W-MID"], 0.025),
                     PE.percentile(boot_gapAB["W-MID"], 0.975)]
                    if boot_gapAB["W-MID"] else [None, None]),
               "verdict": "MET" if (gA - gB) >= 0.10 else "NOT MET",
               "kind": "FALSIFIABLE SCIENTIFIC CONTENT",
               "non_independence_note": (
                   "PAIRED CZ seeds: this difference measures the "
                   "multiplication-routine effect under a fixed split "
                   "structure and is NOT agreement between two independent "
                   "implementations."),
               "all_windows": {w: {"gamma_A": fits["S-A"][w]["gamma_hat"],
                                   "gamma_B": fits["S-B"][w]["gamma_hat"],
                                   "difference": (fits["S-A"][w]["gamma_hat"]
                                                  - fits["S-B"][w]["gamma_hat"])}
                               for w in WIN if w in fits["S-A"]}}
    if SER_SUB is not None:
        sub_fits = {s: fit_series(SER_SUB[s], WIN["W-MID"]) for s in SER_SUB}
        moves = {s: abs(sub_fits[s]["slope"] - fits[s]["W-MID"]["gamma_hat"])
                 for s in SER_SUB}
        P["P4"] = {"statement": ("refitting on the common j-set {0..3} moves "
                                 "each W-MID slope by less than 0.010"),
                   "threshold": 0.010,
                   "j_set_primary": common_j, "j_set_subset": j_subset,
                   "slopes_subset": {s: sub_fits[s]["slope"] for s in sub_fits},
                   "slopes_primary": {s: fits[s]["W-MID"]["gamma_hat"]
                                      for s in SER},
                   "abs_moves": moves,
                   "max_abs_move": max(moves.values()),
                   "verdict": ("MET" if max(moves.values()) < 0.010
                               else "NOT MET"),
                   "kind": "FALSIFIABLE, WITH A CONSEQUENCE",
                   "consequence_if_not_met": (
                       "the {0..3} fit becomes the REPORTED PRIMARY and the "
                       "{0..7} fit is demoted to a sensitivity")}
    else:
        P["P4"] = {"statement": ("refitting on the common j-set {0..3} moves "
                                 "each W-MID slope by less than 0.010"),
                   "verdict": "NOT EVALUABLE",
                   "reason": ("the common j-set already equals {0..3}: pass 2 "
                              "did not complete, so the primary fit IS the "
                              "j-subset fit and there is no {0..7} fit to "
                              "compare it with"),
                   "j_set_primary": common_j}
    R["preregistered_predictions"] = P

    # ---- tail checks ------------------------------------------------------
    tc = {}
    tc["top_of_range_consistency"] = {}
    for s in SER:
        emax = max(WIN["W-MID"])
        f = fits[s]["W-MID"]
        pred = f["intercept_log2_A"] + f["gamma_hat"] * math.log2(emax)
        obs = math.log2(SER[s][emax])
        tc["top_of_range_consistency"][s] = {
            "largest_admitted_ell": emax, "observed_log2_per_entry": obs,
            "W_MID_predicted_log2_per_entry": pred,
            "deviation_bits": obs - pred,
            "exceeds_1_bit": bool(abs(obs - pred) > 1.0)}
    tc["null_flatness_full_admitted_grid"] = cnull["flatness"]
    tc["implementation_gap"] = {"gamma_A_minus_gamma_B_W_MID": gA - gB,
                                "common_window": WIN["W-MID"]}
    seam = {}
    for s in SER:
        rw = fits[s]["W-MID"]["residuals"]
        vals = sorted(((abs(v), k) for k, v in rw.items()), reverse=True)
        two_largest = [k for _a, k in vals[:2]]
        seam[s] = {"residual_at_101": rw.get("101"),
                   "residual_at_103": rw.get("103"),
                   "two_largest_abs_residual_ell": two_largest,
                   "101_and_103_are_the_two_largest": bool(
                       set(two_largest) == {"101", "103"})}
    tc["seam_probe"] = seam
    sup_med = {int(k): v for k, v in carried["per_ell_primary_min"].items()}
    tc["superseded_comparison"] = {
        str(e): {"this_run_S_MIN": SER["S-MIN"][e],
                 "superseded_primary_min_carried": sup_med[e],
                 "difference": SER["S-MIN"][e] - sup_med[e],
                 "log2_difference_bits": (math.log2(SER["S-MIN"][e])
                                          - math.log2(sup_med[e]))}
        for e in admitted if e in sup_med}
    inv_series = {}
    for e in admitted:
        vals = []
        for r in R["samples_primary"]:
            if (r["ell"] == e and r["impl"] == "IMPL-A"
                    and r["j_index"] in common_j):
                vals.append(r["per_entry_inv_charged_3"])
        if vals:
            inv_series[e] = PE.median(vals)
    if len(inv_series) >= 3:
        fi3 = fit_series(inv_series, [e for e in WIN["W-MID"]
                                      if e in inv_series])
        tc["inversion_sensitivity_IMPL_A_W_MID"] = {
            "gamma_with_inversions_charged_3": fi3["slope"],
            "intercept": fi3["intercept"],
            "gamma_without": fits["S-A"]["W-MID"]["gamma_hat"]}
    R["tail_checks"] = tc

    # ---- admissibility ----------------------------------------------------
    control_verdicts = {k: R["controls"][k].get("verdict")
                        for k in R["controls"]}
    adm = {"conditions": [], "all_met": True}
    for s in SER:
        for cond, ok in [
            ("half-width of gamma_reported <= 0.25 (%s)" % s,
             fits[s]["gamma_reported_halfwidth"] <= 0.25),
            ("max |residual| on W-MID <= 0.75 bit (%s)" % s,
             fits[s]["W-MID"]["max_abs_residual"] <= 0.75),
            ("R^2 on W-MID >= 0.98 (%s)" % s,
             fits[s]["W-MID"]["r2"] >= 0.98)]:
            adm["conditions"].append({"condition": cond, "met": bool(ok)})
            adm["all_met"] = adm["all_met"] and bool(ok)
    ctrl_ok = all(control_verdicts.get(k) in ("pass", "pass_with_observation")
                  for k in ["C-INSTR", "C-REPRO", "C-NULL", "C-BASE.1",
                            "C-BASE.2", "C-BASE.3", "C-BASE.4", "C-BASE.5",
                            "C-BASE.6", "C-ALT.1", "C-ALT.2", "C-SEED"])
    adm["conditions"].append({"condition": "every gating control PASS",
                              "met": bool(ctrl_ok),
                              "verdicts": control_verdicts})
    adm["all_met"] = adm["all_met"] and ctrl_ok
    adm["on_violation"] = ("the fit is still reported with the violated "
                           "condition named; evidence strength this run can "
                           "support is capped at `preliminary`. Nothing is "
                           "tuned.")

    R["fit"] = {
        "response_definition": ("y_ell = log2(median over the COMMON j-index "
                                "set of per_entry(ell,j)); one definition "
                                "across the entire fitted range"),
        "regressor": "x_ell = log2(ell)",
        "estimator": "ordinary least squares, unweighted",
        "common_j_index_set": common_j,
        "j_subset_used_for_P4": j_subset,
        "admitted_ell": admitted,
        "windows": {w: WIN[w] for w in WIN},
        "series": fits,
        "curvature": curv,
        "bootstrap": {"method": ("cluster bootstrap over the COMMON j-index "
                                 "set, resampled jointly with replacement, "
                                 "draws = size of that set"),
                      "draws_per_replicate": len(common_j),
                      "replicates_attempted": attempted,
                      "replicates_completed": completed,
                      "skipped_reasons": skipped[:20],
                      "n_skipped": len(skipped),
                      "seed": BOOTSTRAP_SEED,
                      "interval": "2.5 / 97.5 percentile",
                      "joint_intercept_slope": True},
        "exponent_of_record": {
            "decision": ("the PAIR (gamma_A, gamma_B) fitted on the common "
                         "window, not a single number"),
            "gamma_A_W_MID": gA, "gamma_B_W_MID": gB,
            "S_MIN_W_MID_attack_favourable_diagnostic": gM},
        "admissibility": adm}
    R["extrapolation"] = {
        "status": ("EXTRAPOLATION, NOT A MEASUREMENT. The law was fixed "
                   "before this run existed and carries NO claim tier at any "
                   "field size."),
        "law": ("c = [ log2 A + alpha*log2(log2 p_level / log2 p_meas) "
                "+ gamma*log2(B_opt) ] / sqrt(log2 p_level)"),
        "log2_p_meas_exact": log2_p_meas,
        "alpha_reported": [0, 1],
        "alpha_primary_designation": (
            pscale.get("alpha_primary_designation",
                       "alpha = 1, DERIVED-NOT-MEASURED (C-PSCALE did not "
                       "complete)")),
        "p_independent_fraction_guard": guard,
        "rows": c_rows,
        "headline_bracket": headline,
        "declared_assumptions": {
            "L1": "power-law extension from ell <= max measured to ell ~ B_opt: UNTESTED (~7.5 octaves at NIST-I)",
            "L2": "per-entry cost charged at ell = B_opt: DECLARED, NOT MEASURED",
            "L3": "B_opt from RUN-P13VOW-001, which reproduces the paper's five Section 4.1 pairs only within 0.05-3.51 bits: INHERITED UNCERTAINTY",
            "L4": "gamma is measured for THIS pure-Python implementation pair; batched Sutherland-type evaluation is not implemented: UNTESTED, upper bound on the achievable exponent",
            "L5": "the intercept scales as (log2 p)^alpha with alpha = 1: DERIVED from the committed pipeline; measured only if C-PSCALE completes",
            "L6": "the corrected law's charging point and the null gate's reference level are the same object: TESTED (NC2b-G1, NC2b-G1-prime)"}}

    R["phases"]["fits_seconds"] = round(time.time() - t, 3)

    # ---- achieved scope + completion gate ---------------------------------
    j_by_ell = {}
    for r in R["samples_primary"]:
        j_by_ell.setdefault(r["ell"], {}).setdefault(r["impl"], set()).add(
            r["j_index"])
    core_done = [e for e in CORE_REQUIRED if e in admitted]
    ext_done = [e for e in EXT_REQUIRED if e in admitted]
    gate_core = (len(core_done) == len(CORE_REQUIRED))
    gate_ext = (len(ext_done) == len(EXT_REQUIRED))
    min_j = min((len(v["IMPL-A"] & v["IMPL-B"]) for e, v in j_by_ell.items()
                 if e in admitted), default=0)
    R["achieved_scope"] = {
        "ell_acquired": acquired,
        "ell_admitted": admitted,
        "n_admitted": len(admitted),
        "ell_min_admitted": min(admitted), "ell_max_admitted": max(admitted),
        "core_required": CORE_REQUIRED, "core_admitted": core_done,
        "core_complete": bool(gate_core),
        "extension_required": EXT_REQUIRED, "extension_admitted": ext_done,
        "extension_complete": bool(gate_ext),
        "j_set_per_ell": {str(e): {"IMPL-A": sorted(v.get("IMPL-A", [])),
                                   "IMPL-B": sorted(v.get("IMPL-B", []))}
                          for e, v in sorted(j_by_ell.items())},
        "common_j_index_set": common_j,
        "min_common_j_per_admitted_ell": min_j,
        "j_passes_achieved": ("pass 1 (j 0..3) complete"
                              + ("; pass 2 (j 4..7) complete over every "
                                 "acquired ell" if len(common_j) >= 8
                                 else "; pass 2 %s" % pass2["reason"])),
        "dropped_ell": dropped,
        "optional_tail_completed": tail["ell_completed"],
        "completion_gate_met": bool(gate_core and gate_ext and min_j >= 4),
        "completion_gate_note": (
            "core 26 primes 2..101 at >= 4 j AND extension 21 primes "
            "103..211 at >= 4 j, both implementations at every admitted ell, "
            "C-NULL covering every admitted ell")}
    R["c_null_coverage_of_fitted_windows"] = cnull["coverage_fraction_per_window"]

    # ---- validity ---------------------------------------------------------
    invalid = []
    if R["controls"]["C-INSTR"]["verdict"] != "pass":
        invalid.append("C-INSTR")
    if R["controls"]["C-REPRO"]["verdict"] != "pass":
        invalid.append("C-REPRO")
    if R["controls"]["C-BASE.1"]["verdict"] != "pass":
        invalid.append("C-BASE.1")
    if R["controls"]["C-BASE.3"]["verdict"] != "pass":
        invalid.append("C-BASE.3")
    if R["controls"]["C-BASE.4"]["verdict"] not in ("pass",
                                                    "pass_with_observation"):
        invalid.append("C-BASE.4")
    if R["controls"]["C-BASE.5"]["verdict"] != "pass":
        invalid.append("C-BASE.5")
    if R["controls"]["C-ALT.1"]["verdict"] != "pass":
        invalid.append("C-ALT.1")
    if R["controls"]["C-ALT.2"]["verdict"] != "pass":
        invalid.append("C-ALT.2")
    if R["controls"]["C-SEED"]["verdict"] != "pass":
        invalid.append("C-SEED")
    if P["P1a"]["verdict"] != "MET":
        invalid.append("P1a (arithmetically impossible for a pointwise "
                       "minimum -> code defect)")
    void = (cnull["verdict"] != "pass")
    if len(admitted) < 12 or min_j < 4:
        R["anomalies"].append("INCOMPLETE: fewer than 12 admitted ell or "
                              "fewer than 4 common j at an admitted ell")
    R["validity"] = {
        "status": ("invalid_measurement" if invalid else
                   ("valid_but_void_primary" if void else
                    ("completed_valid" if R["achieved_scope"][
                        "completion_gate_met"] else
                     "completed_valid_but_truncated"))),
        "invalidating_controls": invalid,
        "primary_void_because_C_NULL_failed": bool(void),
        "reason": ("every gating control passed; the measurement is valid "
                   "over exactly the admitted ell range and j-set recorded "
                   "in achieved_scope" if not invalid and not void else
                   "see invalidating_controls / C-NULL"),
        "nc2b_gate_verdict": gate["verdict"],
        "note_on_the_nc2b_gate": (
            "a missed NC2b-G1 gate does NOT invalidate the run "
            "(specification explicitly_not_an_invalidation): it is a reported "
            "FAILURE OF THE REPAIR")}

    R["finished_utc"] = datetime.now(timezone.utc).isoformat()
    R["total_wall_clock_seconds"] = round(elapsed(), 3)
    ru_self = resource.getrusage(resource.RUSAGE_SELF)
    ru_ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    R["resource_measurements"] = {
        "note": "resource.getrusage; wall-clock is recorded alongside and "
                "never substituted for the counted unit",
        "user_cpu_seconds_self": ru_self.ru_utime,
        "system_cpu_seconds_self": ru_self.ru_stime,
        "user_cpu_seconds_children": ru_ch.ru_utime,
        "system_cpu_seconds_children": ru_ch.ru_stime,
        "total_cpu_seconds": (ru_self.ru_utime + ru_self.ru_stime
                              + ru_ch.ru_utime + ru_ch.ru_stime),
        "max_rss_kib_self": ru_self.ru_maxrss,
        "max_rss_kib_largest_child": ru_ch.ru_maxrss,
        "workers": args.workers,
        "budget_wall_clock_seconds": args.budget_seconds,
        "budget_memory_gb": 8, "budget_total_cpu_hours": 6.0}
    R["environment_observed"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "cpus": os.cpu_count()}
    flush_partial("final")
    log("done: validity=%s, NC2b-G1=%s, admitted ell=%d, common j=%s"
        % (R["validity"]["status"], gate["verdict"], len(admitted), common_j))
    return 0


if __name__ == "__main__":
    sys.exit(main())

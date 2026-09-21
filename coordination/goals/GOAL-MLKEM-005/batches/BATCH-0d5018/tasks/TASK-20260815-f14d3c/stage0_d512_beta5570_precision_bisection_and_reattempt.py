#!/usr/bin/env python3
"""
TASK-20260815-f14d3c -- per-basis (d=512, beta=55) and (d=512, beta=70)
precision bisection and decisive reattempt.

Discharges DEC-20260815-201633's own next_actions (section 12) in full. A
FRESH script, not an edit of TASK-20260815-6e4c02's own
stage0_d512_precision_bisection_and_reattempt.py, which stays immutable and
untouched. Reuses, by construction/shape/formula (not by import):
  - the Red Team's own probe1_d512_beta_generality.py isolated-LLL-step
    worker() shape for the bisection phase;
  - TASK-20260815-6e4c02's own bisect_precision_d512() bisection design,
    generalized to run TWICE, independently, once per basis, within the
    narrower [69, 100] window CTRL-1 already supplies;
  - TASK-20260815-6e4c02's own worker_main_cell() construction shape
    (GSO.Mat -> LLL.Reduction -> BKZReduction(L)) for the reattempt phase.

TWO BASES, EACH WITH ITS OWN, SEPARATE, GENUINE 1-BIT-RESOLUTION BISECTION
(not a shared/borrowed precision between them) followed by its own full-BKZ-
tour reattempt AT ITS OWN newly-bisected precision:
  (d=512, beta=55), expected seed_used=452658293 (default_rng([715923, 0,
  512, 55, 0, 0])), window [69, 100] (69 known ERROR, 100 known COMPLETED
  per Red Team CTRL-1).
  (d=512, beta=70), expected seed_used=915347894 (default_rng([715923, 0,
  512, 70, 0, 0])), window [69, 100] (69 known ERROR, 100 known COMPLETED
  per Red Team CTRL-1).

Each basis's own bisection is capped at BISECTION_D512B_BUDGET_SECONDS=3600s
total; if it cannot resolve, NOT_COMPUTED: bisection budget exhausted is
reported honestly for that basis and the disclosed fallback (100 bits, the
nearest known-succeeding value at this exact instance) is used for that
basis's own reattempt, never presented as a determined minimum.

Each cell's own full BKZ tour reattempt uses ITS OWN newly-bisected
precision (never the other basis's value, never the beta=40-borrowed 69
bits), individually capped at PER_BASIS_FEASIBILITY_CAP_V3=14400s. A cell
exceeding the cap is NOT_COMPUTED: exceeded PER_BASIS_FEASIBILITY_CAP_V3,
never retried at a different parameter.

Does NOT re-attempt (d=512, beta=40). Does NOT attempt or characterize
(d=256, beta=55) or (d=256, beta=70). Does NOT run PREREG-8's own Stage 1.
Does NOT perform a full-tour-level precision search (CTRL-3's costlier
half) -- explicitly out of scope, named as a further, later step. Does NOT
change H-MLKEM-7d9bcc's or EXP-MLKEM-42ea04's status. Does NOT make any
C1/C2 or ML-KEM-security statement.

SEED_ROOT = 715923, stage_index = 0 for every draw, matching every
precedent in this goal's history:
  default_rng([SEED_ROOT, stage_index, d, beta, arm_index, draw_index])
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Basis definitions -- TWO bases, each with its own bisection AND its own
# reattempt, run fully independently and sequentially. Order: beta=55 first,
# then beta=70, matching this task card's own naming order.
# ---------------------------------------------------------------------------
D512 = 512
BASES = [
    {"beta": 55, "expected_seed": 452658293,
     "bisection_results_path": "bisection_d512_beta55_results.json"},
    {"beta": 70, "expected_seed": 915347894,
     "bisection_results_path": "bisection_d512_beta70_results.json"},
]

BISECTION_LO_KNOWN_FAILING = 69     # Red Team CTRL-1: ERROR at 69 bits, both bases
BISECTION_HI_KNOWN_SUCCEEDING = 100  # Red Team CTRL-1: COMPLETED at 100 bits, both bases
BISECTION_D512B_BUDGET_SECONDS = 3600     # PER BASIS, reused unchanged from precedent
BISECTION_D512B_TRIAL_CAP_SECONDS = 900   # reused unchanged from precedent
FALLBACK_PRECISION_BITS = 100  # disclosed fallback if a basis's own bisection budget exhausts
# (100 bits is the nearest KNOWN-SUCCEEDING value at both exact instances per
# CTRL-1; using it as the fallback -- rather than reaching for an untested
# higher value -- is the most conservative disclosed fallback available.)

PER_BASIS_FEASIBILITY_CAP_V3 = 14400  # REUSED, EXPLICITLY DISCLOSED (see task_card.md /
                                        # dispatch_queue.json budget_justification): the prior
                                        # batch's own Red Team COST-3 found this cap
                                        # "adequate-and-untested-as-binding, not
                                        # adequate-and-validated-as-binding" -- every d=512
                                        # cell attempted to date has failed via a hard
                                        # ReductionError, never a timeout.
OVERALL_BUDGET_SECONDS = 37200
WRITE_BUFFER_SECONDS = 600

STRATEGIES_PATH_DEFAULT = "/usr/share/libfplll8/strategies/default.json"


def _strategies_path():
    from fpylll import BKZ
    if os.path.exists(STRATEGIES_PATH_DEFAULT):
        return STRATEGIES_PATH_DEFAULT
    return BKZ.DEFAULT_STRATEGY


# ---------------------------------------------------------------------------
# Worker entry points -- each runs as its OWN subprocess so the parent can
# enforce a hard wall-clock kill independent of anything fpylll/fplll do
# internally. Construction shapes reused verbatim (structurally) from
# probe1_d512_beta_generality.py (bisection) and TASK-20260815-6e4c02's own
# worker_main_cell() (reattempt).
# ---------------------------------------------------------------------------

def worker_bisect(d, beta, mpfr_bits, out_path):
    """EXACT reproduction of probe1_d512_beta_generality.py's own worker():
    isolated LLL-preprocessing step only (outer double-precision
    LLL.reduction(A), then FPLLL.set_precision(N) BEFORE GSO.Mat
    construction, GSO.Mat(A, float_type='mpfr') with NO flags=GSO.ROW_EXPO,
    M.update_gso(), LLL.Reduction(M, flags=LLL.DEFAULT), call lll_obj()
    directly -- NOT wrapped in BKZReduction)."""
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits, "level": "isolated_lll_step"}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL, GSO

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)  # BEFORE GSO.Mat construction
        M = GSO.Mat(A, float_type="mpfr")  # explicitly NO flags=GSO.ROW_EXPO
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)

        t1 = time.time()
        lll_obj()
        result["inner_lll_obj_elapsed_seconds"] = time.time() - t1
        result["status"] = "COMPLETED"
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        try:
            from fpylll import FPLLL
            FPLLL.set_precision(53)
        except Exception:
            pass

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


def worker_main_cell(d, beta, mpfr_bits, out_path):
    """EXACT reproduction of TASK-20260815-6e4c02's own worker_main_cell():
    reduces ONE fresh basis at (d, beta) with the corrected construction
    (explicit, ROW_EXPO-free, mpfr-precision GSO.Mat), records wall-clock,
    tours, and the measured root-Hermite factor."""
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits, "construction": "corrected_mpfr_no_row_expo"}
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        strategies_path = _strategies_path()
        result["strategies_file_used"] = strategies_path

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        lll_elapsed = time.time() - t0
        result["outer_lll_reduction_elapsed_seconds"] = lll_elapsed

        FPLLL.set_precision(mpfr_bits)  # BEFORE GSO.Mat construction
        M = GSO.Mat(A, float_type="mpfr")  # explicitly NO flags=GSO.ROW_EXPO
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        par = BKZ.Param(
            block_size=beta,
            strategies=strategies_path,
            flags=BKZ.AUTO_ABORT,
        )
        bkz = BKZReduction(L)  # BKZReduction sees an LLL.Reduction instance;
                                # reuses L.M (our mpfr, ROW_EXPO-free GSO) as
                                # self.M -- does NOT rebuild GSO.Mat(A,
                                # flags=GSO.ROW_EXPO) internally.
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1

        n_tours = None
        try:
            if bkz.trace is not None:
                n_tours = sum(1 for child in bkz.trace.children if child.label[0] == "tour")
        except Exception:
            n_tours = None

        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        first_vec_norm = float(r0) ** 0.5
        det_l_pow_1_over_d = np.exp(float(log_det) / d)
        delta_0 = (first_vec_norm / det_l_pow_1_over_d) ** (1.0 / d)

        result.update({
            "status": "COMPLETED",
            "lll_elapsed_seconds": lll_elapsed,
            "bkz_elapsed_seconds": bkz_elapsed,
            "total_elapsed_seconds": lll_elapsed + bkz_elapsed,
            "n_tours": n_tours,
            "delta_0_root_hermite_factor": float(delta_0),
            "first_gso_vector_norm": float(first_vec_norm),
            "log_det": float(log_det),
        })
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        try:
            from fpylll import FPLLL
            FPLLL.set_precision(53)
        except Exception:
            pass

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


# ---------------------------------------------------------------------------
# Parent orchestration
# ---------------------------------------------------------------------------

def run_capped_subprocess(argv, cap_seconds, out_path, mem_poll_interval=0.5):
    """Launches argv as a subprocess, polls its RSS via psutil, and enforces
    cap_seconds as a HARD wall-clock kill. Returns a dict with wall_clock,
    peak_rss_mb, timed_out, returncode, stdout/stderr tails. Reused verbatim
    (structurally) from TASK-20260815-6e4c02's own precedent."""
    import psutil

    t0 = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_proc = None
    try:
        ps_proc = psutil.Process(proc.pid)
    except Exception:
        ps_proc = None

    peak_rss = 0
    timed_out = False
    while True:
        ret = proc.poll()
        if ps_proc is not None:
            try:
                rss = ps_proc.memory_info().rss
                for child in ps_proc.children(recursive=True):
                    try:
                        rss += child.memory_info().rss
                    except Exception:
                        pass
                peak_rss = max(peak_rss, rss)
            except Exception:
                pass
        if ret is not None:
            break
        if time.time() - t0 >= cap_seconds:
            timed_out = True
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                proc.kill()
            break
        time.sleep(mem_poll_interval)

    stdout, stderr = b"", b""
    try:
        stdout, stderr = proc.communicate(timeout=15)
    except Exception:
        pass

    wall_clock = time.time() - t0
    return {
        "wall_clock_seconds": wall_clock,
        "peak_rss_mb": peak_rss / (1024 * 1024),
        "timed_out": timed_out,
        "returncode": proc.returncode,
        "stdout_tail": stdout.decode(errors="replace")[-2000:],
        "stderr_tail": stderr.decode(errors="replace")[-2000:],
    }


def run_bisect_trial(d, beta, mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_bisect512_%d_%d.json" % (beta, mpfr_bits))
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [sys.executable, os.path.abspath(__file__), "--worker-bisect",
            str(d), str(beta), str(mpfr_bits), out_path]
    proc_info = run_capped_subprocess(argv, cap_seconds, out_path)
    trial = {"mpfr_bits": mpfr_bits}
    trial.update({
        "subprocess_wall_clock_seconds": proc_info["wall_clock_seconds"],
        "subprocess_timed_out": proc_info["timed_out"],
        "subprocess_returncode": proc_info["returncode"],
    })
    if proc_info["timed_out"] or not os.path.exists(out_path):
        trial["status"] = "NOT_COMPUTED"
        trial["reason"] = (
            "trial subprocess exceeded its own cap (%ds)" % cap_seconds if proc_info["timed_out"]
            else "worker crashed before writing output (stderr_tail attached)"
        )
        trial["stderr_tail"] = proc_info["stderr_tail"]
    else:
        with open(out_path) as f:
            trial.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return trial


def bisect_precision_d512b(d, beta, expected_seed):
    """Integer binary search over mpfr bits in
    [BISECTION_LO_KNOWN_FAILING, BISECTION_HI_KNOWN_SUCCEEDING], 1-bit
    resolution, capped at BISECTION_D512B_BUDGET_SECONDS total across all
    trials for THIS basis. Both endpoints are re-confirmed as trials BEFORE
    bisecting, matching TASK-20260815-6e4c02's own bisect_precision_d512()
    design exactly, generalized to run independently PER (d, beta).
    Returns (minimum_precision_or_None, fallback_used, trials,
    wall_clock_used, endpoint_reproduction_ok)."""
    trials = []
    t_bisect_start = time.time()

    def budget_remaining():
        return BISECTION_D512B_BUDGET_SECONDS - (time.time() - t_bisect_start)

    lo, hi = BISECTION_LO_KNOWN_FAILING, BISECTION_HI_KNOWN_SUCCEEDING
    remaining = budget_remaining()
    if remaining <= 0:
        return None, True, trials, time.time() - t_bisect_start, None
    cap = min(BISECTION_D512B_TRIAL_CAP_SECONDS, max(1, remaining))
    t_lo = run_bisect_trial(d, beta, lo, cap)
    trials.append(t_lo)
    if budget_remaining() <= 0:
        return None, True, trials, time.time() - t_bisect_start, None
    cap = min(BISECTION_D512B_TRIAL_CAP_SECONDS, max(1, budget_remaining()))
    t_hi = run_bisect_trial(d, beta, hi, cap)
    trials.append(t_hi)

    lo_ok = t_lo.get("status") == "COMPLETED"
    hi_ok = t_hi.get("status") == "COMPLETED"
    lo_error = t_lo.get("status") == "ERROR"
    hi_seed = t_hi.get("seed_used")
    lo_seed = t_lo.get("seed_used")
    endpoint_reproduction_ok = (
        lo_error and hi_ok
        and lo_seed == expected_seed
        and hi_seed == expected_seed
    )

    if lo_ok:
        # lower bound unexpectedly succeeds -- report honestly, minimum is lo itself
        return lo, False, trials, time.time() - t_bisect_start, endpoint_reproduction_ok
    if not hi_ok:
        # upper bound (previously known-succeeding) failed to reproduce here
        # -- cannot bisect a monotone boundary that does not hold; report
        # NOT_COMPUTED and disclose.
        return None, True, trials, time.time() - t_bisect_start, endpoint_reproduction_ok

    while hi - lo > 1:
        if budget_remaining() <= 0:
            return None, True, trials, time.time() - t_bisect_start, endpoint_reproduction_ok
        mid = (lo + hi) // 2
        cap = min(BISECTION_D512B_TRIAL_CAP_SECONDS, max(1, budget_remaining()))
        t_mid = run_bisect_trial(d, beta, mid, cap)
        trials.append(t_mid)
        if t_mid.get("status") == "COMPLETED":
            hi = mid
        elif t_mid.get("status") == "ERROR":
            lo = mid
        else:
            # NOT_COMPUTED (trial-level timeout / crash) -- budget exhausted
            # or trial itself failed to resolve; stop bisecting honestly.
            return None, True, trials, time.time() - t_bisect_start, endpoint_reproduction_ok

    return hi, False, trials, time.time() - t_bisect_start, endpoint_reproduction_ok


def run_main_cell(d, beta, mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_cell512b_%d_%d.json" % (d, beta))
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [sys.executable, os.path.abspath(__file__), "--worker-cell",
            str(d), str(beta), str(mpfr_bits), out_path]
    proc_info = run_capped_subprocess(argv, cap_seconds, out_path)
    cell_result = {"d": d, "beta": beta, "mpfr_bits_used": mpfr_bits, "cap_seconds": cap_seconds}
    cell_result.update({
        "subprocess_wall_clock_seconds": proc_info["wall_clock_seconds"],
        "peak_rss_mb": proc_info["peak_rss_mb"],
        "subprocess_timed_out": proc_info["timed_out"],
        "subprocess_returncode": proc_info["returncode"],
    })
    if proc_info["timed_out"] or not os.path.exists(out_path):
        cell_result["status"] = "NOT_COMPUTED"
        cell_result["reason"] = (
            "exceeded PER_BASIS_FEASIBILITY_CAP_V3" if proc_info["timed_out"] else
            "worker crashed before writing output (stderr_tail attached)"
        )
        cell_result["stderr_tail"] = proc_info["stderr_tail"]
    else:
        with open(out_path) as f:
            cell_result.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return cell_result


def main():
    t_script_start = time.time()

    def overall_elapsed():
        return time.time() - t_script_start

    bisection_summaries = {}
    precisions_used = {}
    fallback_flags = {}

    # -----------------------------------------------------------------
    # PHASE (a) / (a') -- two SEPARATE, per-basis bisections.
    # -----------------------------------------------------------------
    for basis in BASES:
        beta = basis["beta"]
        expected_seed = basis["expected_seed"]
        print("=== PHASE (a): BISECTION (isolated LLL step, d=%d beta=%d) ===" %
              (D512, beta), flush=True)

        remaining_before_bisection = OVERALL_BUDGET_SECONDS - WRITE_BUFFER_SECONDS - overall_elapsed()
        if remaining_before_bisection <= 0:
            bisection_out = {
                "seed_root": SEED_ROOT, "bisection_d": D512, "bisection_beta": beta,
                "expected_seed_used": expected_seed,
                "lo_known_failing": BISECTION_LO_KNOWN_FAILING,
                "hi_known_succeeding": BISECTION_HI_KNOWN_SUCCEEDING,
                "bisection_budget_seconds": BISECTION_D512B_BUDGET_SECONDS,
                "bisection_wall_clock_seconds": 0.0,
                "endpoint_reproduction_ok": None,
                "invalidation_note": None,
                "trials": [],
                "determined_minimum_precision_bits": None,
                "fallback_used": True,
                "fallback_precision_bits": FALLBACK_PRECISION_BITS,
                "precision_used_for_reattempt": FALLBACK_PRECISION_BITS,
                "note": "NOT_COMPUTED: bisection budget exhausted -- overall task wall-clock "
                        "budget was exhausted BEFORE this basis's own bisection could even "
                        "start. Disclosed explicitly. Fallback %d bits used for this basis's "
                        "own reattempt, never presented as a determined minimum." % FALLBACK_PRECISION_BITS,
            }
            precision_used = FALLBACK_PRECISION_BITS
            fallback_used = True
            min_precision = None
        else:
            (min_precision, fallback_used, bisect_trials, bisect_wall_clock,
             endpoint_reproduction_ok) = bisect_precision_d512b(D512, beta, expected_seed)
            precision_used = min_precision if (min_precision is not None and not fallback_used) else FALLBACK_PRECISION_BITS

            invalidation_note = None
            if endpoint_reproduction_ok is False:
                invalidation_note = (
                    "INVALIDATION TRIGGER FIRED: the (d=512, beta=%d) isolated-step "
                    "control did NOT reproduce ERROR at 69 bits / COMPLETED at 100 "
                    "bits with seed_used=%d as the Red Team's own CTRL-1 control "
                    "reports. Disclosed explicitly per this task's own "
                    "invalidation_triggers; not silently proceeded past." % (beta, expected_seed)
                )
                print(invalidation_note, flush=True)

            bisection_out = {
                "seed_root": SEED_ROOT,
                "bisection_d": D512,
                "bisection_beta": beta,
                "expected_seed_used": expected_seed,
                "lo_known_failing": BISECTION_LO_KNOWN_FAILING,
                "hi_known_succeeding": BISECTION_HI_KNOWN_SUCCEEDING,
                "bisection_budget_seconds": BISECTION_D512B_BUDGET_SECONDS,
                "bisection_wall_clock_seconds": bisect_wall_clock,
                "endpoint_reproduction_ok": endpoint_reproduction_ok,
                "invalidation_note": invalidation_note,
                "trials": bisect_trials,
                "determined_minimum_precision_bits": min_precision if not fallback_used else None,
                "fallback_used": fallback_used,
                "fallback_precision_bits": FALLBACK_PRECISION_BITS if fallback_used else None,
                "precision_used_for_reattempt": precision_used,
                "note": (
                    "Determined by 1-bit-resolution binary search between the known-failing "
                    "(69 bits) and known-succeeding (100 bits) endpoints, both re-confirmed "
                    "as trials before bisecting, independently for this basis." if not fallback_used else
                    "NOT_COMPUTED: bisection budget exhausted (or a boundary assumption did "
                    "not reproduce) for THIS basis -- falling back explicitly to %d bits for "
                    "this basis's own reattempt, disclosed as a fallback, NOT a determined "
                    "minimum." % FALLBACK_PRECISION_BITS
                ),
            }

        print(json.dumps(bisection_out, indent=2), flush=True)
        out_name = basis["bisection_results_path"]
        with open(os.path.join(HERE, out_name), "w") as f:
            json.dump(bisection_out, f, indent=2)

        bisection_summaries[beta] = bisection_out
        precisions_used[beta] = precision_used
        fallback_flags[beta] = fallback_used

    # -----------------------------------------------------------------
    # PHASE (b) -- each cell's own full-BKZ-tour reattempt, AT ITS OWN
    # newly-bisected precision. (d=512, beta=40) is explicitly NOT
    # re-attempted here.
    # -----------------------------------------------------------------
    main_grid = []
    for basis in BASES:
        beta = basis["beta"]
        precision_used = precisions_used[beta]
        fallback_used = fallback_flags[beta]

        remaining_before_cell = OVERALL_BUDGET_SECONDS - WRITE_BUFFER_SECONDS - overall_elapsed()
        if remaining_before_cell < PER_BASIS_FEASIBILITY_CAP_V3:
            cell_result = {
                "d": D512, "beta": beta,
                "mpfr_bits_used": precision_used,
                "status": "NOT_COMPUTED",
                "reason": "task budget exhausted before this cell was attempted",
                "overall_elapsed_seconds_at_skip": overall_elapsed(),
                "overall_budget_seconds": OVERALL_BUDGET_SECONDS,
            }
            print("cell (d=%d, beta=%d): SKIPPED, task budget exhausted (elapsed=%.1fs)" %
                  (D512, beta, overall_elapsed()), flush=True)
        else:
            print("=== PHASE (b): d=512 beta=%d REATTEMPT (own precision=%d bits) ===" %
                  (beta, precision_used), flush=True)
            print("cell (d=%d, beta=%d): launching, cap=%ds, precision=%d bits (%s)" %
                  (D512, beta, PER_BASIS_FEASIBILITY_CAP_V3, precision_used,
                   "bisected_minimum" if not fallback_used else "disclosed_fallback"), flush=True)
            cell_result = run_main_cell(D512, beta, precision_used, PER_BASIS_FEASIBILITY_CAP_V3)
            cell_result["precision_source"] = "bisected_minimum" if not fallback_used else \
                "disclosed_fallback_%d_bits" % FALLBACK_PRECISION_BITS
            print("  -> %s (%.1fs)" % (cell_result["status"], cell_result["subprocess_wall_clock_seconds"]), flush=True)

        main_grid.append(cell_result)
        with open(os.path.join(HERE, "main_grid_d512_beta5570_reattempt_results.json"), "w") as f:
            json.dump({
                "seed_root": SEED_ROOT,
                "per_basis_feasibility_cap_v3_seconds": PER_BASIS_FEASIBILITY_CAP_V3,
                "overall_budget_seconds": OVERALL_BUDGET_SECONDS,
                "construction": "GSO.Mat(A, float_type='mpfr'), NO flags=GSO.ROW_EXPO; "
                                 "FPLLL.set_precision(N) called BEFORE GSO.Mat construction; "
                                 "M.update_gso(); LLL.Reduction(M, flags=LLL.DEFAULT); BKZReduction(L)",
                "cells_planned": [(D512, b["beta"]) for b in BASES],
                "note": "(d=512, beta=40) intentionally NOT re-attempted by this task -- "
                        "already properly calibrated and reattempted in BATCH-279acb.",
                "main_grid": main_grid,
                "n_cells_completed": len([c for c in main_grid if c.get("status") == "COMPLETED"]),
                "n_cells_not_computed_or_error": len(main_grid) - len([c for c in main_grid if c.get("status") == "COMPLETED"]),
                "total_script_wall_clock_seconds_so_far": overall_elapsed(),
                "in_progress": True,
            }, f, indent=2)

    completed_cells = [c for c in main_grid if c.get("status") == "COMPLETED"]
    overall = {
        "seed_root": SEED_ROOT,
        "per_basis_feasibility_cap_v3_seconds": PER_BASIS_FEASIBILITY_CAP_V3,
        "overall_budget_seconds": OVERALL_BUDGET_SECONDS,
        "construction": "GSO.Mat(A, float_type='mpfr'), NO flags=GSO.ROW_EXPO; "
                         "FPLLL.set_precision(N) called BEFORE GSO.Mat construction; "
                         "M.update_gso(); LLL.Reduction(M, flags=LLL.DEFAULT); BKZReduction(L)",
        "cells_planned": [(D512, b["beta"]) for b in BASES],
        "note": "(d=512, beta=40) intentionally NOT re-attempted by this task -- "
                "already properly calibrated and reattempted in BATCH-279acb. "
                "(d=256, beta=55) and (d=256, beta=70) not attempted or characterized "
                "by this task, out of scope.",
        "main_grid": main_grid,
        "n_cells_completed": len(completed_cells),
        "n_cells_not_computed_or_error": len(main_grid) - len(completed_cells),
        "total_script_wall_clock_seconds": overall_elapsed(),
        "in_progress": False,
    }
    print(json.dumps(overall, indent=2), flush=True)
    with open(os.path.join(HERE, "main_grid_d512_beta5570_reattempt_results.json"), "w") as f:
        json.dump(overall, f, indent=2)
    return overall


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker-bisect":
        worker_bisect(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) > 1 and sys.argv[1] == "--worker-cell":
        worker_main_cell(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

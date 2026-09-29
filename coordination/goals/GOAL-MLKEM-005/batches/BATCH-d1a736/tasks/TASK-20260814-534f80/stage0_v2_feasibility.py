#!/usr/bin/env python3
"""
TASK-20260814-534f80 -- corrected-construction Stage-0 re-measurement.

Discharges DEC-20260814-4ac30a's next_actions in full. A FRESH copy, not an
edit, of TASK-20260814-ffd791's own stage0_feasibility.py (that file is an
immutable run record and is never imported or modified by this script).

worker_main_cell() is fixed to construct BKZReduction from an explicit,
GSO.ROW_EXPO-free, mpfr-precision GSO.Mat instead of handing it a raw
IntegerMatrix -- the EXACT construction shape validated at the isolated-
LLL-step level by:
  coordination/.../archives/TASK-20260814-87a572/adjudication/adjudicate_precision.py
  coordination/.../reviews/TASK-20260814-fe02ff/probes/probe5_precision_fix_at_cheapest_failing_d.py
  coordination/.../reviews/TASK-20260814-fe02ff/probes/probe6_full_bkz_with_precision_fix.py

  FPLLL.set_precision(N) called BEFORE GSO.Mat construction
  GSO.Mat(A, float_type="mpfr")            -- explicitly NO flags=GSO.ROW_EXPO
  M.update_gso()
  LLL.Reduction(M, flags=LLL.DEFAULT)      -- call this L
  BKZReduction(L)                          -- BKZReduction.__init__ sees an
                                               LLL.Reduction instance, reuses
                                               L.M as its own self.M, and does
                                               NOT rebuild a GSO.Mat(A,
                                               flags=GSO.ROW_EXPO) internally
                                               (verified directly against this
                                               host's fpylll 0.6.4 bkz.py
                                               source: isinstance(A,
                                               LLL.Reduction) branch sets
                                               L = A; M = L.M; self.lll_obj = L
                                               -- the raw-IntegerMatrix branch
                                               that builds GSO.Mat(A,
                                               flags=GSO.ROW_EXPO) is never
                                               taken here).

Two phases, run as SEPARATE OS subprocesses (same reason as the original:
fpylll/fplll's own internal MAX_TIME uses CPU process_time, not wall clock,
and cannot be trusted alone to bound one long SVP-enumeration call):

  PHASE 1 -- BISECTION (isolated LLL-step level only: GSO.Mat + LLL.Reduction
  + call lll_obj() directly, NOT wrapped in BKZReduction, matching probe5's
  own approach -- cheap, ~70-400s per trial, dominated by the outer
  LLL.reduction(A) call). At (d=256, beta=40), seed
  default_rng([715923, 0, 256, 40, 0, 0]) (must reproduce seed_used=1398073216
  per every other artifact in this goal). Binary-searches mpfr precision
  between 53 bits (known failing, fpylll's own double-equivalent default) and
  212 bits (known succeeding, Red Team's own probe5), integer bisection to
  1-bit resolution. Capped at BISECTION_BUDGET_SECONDS=3600s total across all
  trials. If exhausted before resolving to 1-bit width, reports
  NOT_COMPUTED: bisection budget exhausted and falls back explicitly to 212
  bits for phase 2 -- disclosed as a fallback, never presented as a
  determined minimum.

  PHASE 2 -- MAIN-GRID RE-MEASUREMENT: for each of the 6 (d, beta) cells
  (d in {256, 512}, beta in {40, 55, 70}), constructs BKZReduction from the
  corrected GSO.Mat (bisected precision, no ROW_EXPO) and runs a FULL
  bkz(par, tracer=True) tour, individually capped at
  PER_BASIS_FEASIBILITY_CAP_V2=7200s. A cell exceeding this cap is
  NOT_COMPUTED: exceeded PER_BASIS_FEASIBILITY_CAP_V2 -- never retried at a
  different parameter. Before launching each cell, the parent checks whether
  the task's own OVERALL_BUDGET_SECONDS=25200s wall-clock cap (with a
  WRITE_BUFFER_SECONDS safety margin reserved for writing this script's own
  final artifacts) would be exceeded by attempting it at the full 7200s cap;
  if so, that cell and every cell after it is reported
  NOT_COMPUTED: task budget exhausted before this cell was attempted, and the
  script stops launching new cells. A hard OS-level `timeout` wrapping the
  whole process (see command.txt) is a backstop only, not the primary
  enforcement mechanism.

SEED_ROOT = 715923, stage_index = 0 for every draw in this file, matching
TASK-20260814-ffd791's own precedent exactly:
  default_rng([SEED_ROOT, stage_index, d, beta, arm_index, draw_index])

DOES NOT run PREREG-8 Stage 1. DOES NOT change H-MLKEM-7d9bcc's or
EXP-MLKEM-42ea04's status. DOES NOT recommend a Stage-1 sizing decision --
that is reserved for a later, separate Coordinator ledger archive.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
BISECTION_D = 256
BISECTION_BETA = 40
BISECTION_LO_KNOWN_FAILING = 53
BISECTION_HI_KNOWN_SUCCEEDING = 212
BISECTION_BUDGET_SECONDS = 3600
BISECTION_TRIAL_CAP_SECONDS = 900  # generous vs. the ~70-400s/trial expectation
FALLBACK_PRECISION_BITS = 212  # disclosed fallback if bisection budget exhausted

PER_BASIS_FEASIBILITY_CAP_V2 = 7200
OVERALL_BUDGET_SECONDS = 25200
WRITE_BUFFER_SECONDS = 180  # reserved so the script can always write results

MAIN_CELLS = [(256, 40), (256, 55), (256, 70), (512, 40), (512, 55), (512, 70)]

HERE = os.path.dirname(os.path.abspath(__file__))

STRATEGIES_PATH_DEFAULT = "/usr/share/libfplll8/strategies/default.json"


def _strategies_path():
    from fpylll import BKZ
    if os.path.exists(STRATEGIES_PATH_DEFAULT):
        return STRATEGIES_PATH_DEFAULT
    return BKZ.DEFAULT_STRATEGY


# ---------------------------------------------------------------------------
# Worker entry points -- each runs as its OWN subprocess so the parent can
# enforce a hard wall-clock kill independent of anything fpylll/fplll do
# internally.
# ---------------------------------------------------------------------------

def worker_bisect(d, beta, mpfr_bits, out_path):
    """Isolated LLL-step level ONLY, matching probe5's exact construction:
    GSO.Mat(A, float_type='mpfr') (no ROW_EXPO), FPLLL.set_precision(N)
    called BEFORE construction, LLL.Reduction(M, flags=LLL.DEFAULT), call
    lll_obj() directly -- NOT wrapped in BKZReduction."""
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
    """Runs in its own subprocess: reduce ONE fresh basis at (d, beta) with
    the CORRECTED construction (explicit, ROW_EXPO-free, mpfr-precision
    GSO.Mat), record wall-clock, tours, and the measured root-Hermite
    factor."""
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
    peak_rss_mb, timed_out, returncode, stdout/stderr tails."""
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


def run_bisect_trial(mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_bisect_%d.json" % mpfr_bits)
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [sys.executable, os.path.abspath(__file__), "--worker-bisect",
            str(BISECTION_D), str(BISECTION_BETA), str(mpfr_bits), out_path]
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


def bisect_precision():
    """Integer binary search over mpfr bits in
    [BISECTION_LO_KNOWN_FAILING, BISECTION_HI_KNOWN_SUCCEEDING], 1-bit
    resolution, capped at BISECTION_BUDGET_SECONDS total. Returns
    (minimum_precision_or_None, fallback_used, trials, wall_clock_used)."""
    trials = []
    t_bisect_start = time.time()

    def budget_remaining():
        return BISECTION_BUDGET_SECONDS - (time.time() - t_bisect_start)

    # Confirm both endpoints as trials 1 and 2 -- never assumed silently.
    lo, hi = BISECTION_LO_KNOWN_FAILING, BISECTION_HI_KNOWN_SUCCEEDING
    remaining = budget_remaining()
    if remaining <= 0:
        return None, True, trials, time.time() - t_bisect_start
    cap = min(BISECTION_TRIAL_CAP_SECONDS, max(1, remaining))
    t_lo = run_bisect_trial(lo, cap)
    trials.append(t_lo)
    if budget_remaining() <= 0:
        return None, True, trials, time.time() - t_bisect_start
    cap = min(BISECTION_TRIAL_CAP_SECONDS, max(1, budget_remaining()))
    t_hi = run_bisect_trial(hi, cap)
    trials.append(t_hi)

    lo_ok = t_lo.get("status") == "COMPLETED"
    hi_ok = t_hi.get("status") == "COMPLETED"
    if lo_ok:
        # lower bound unexpectedly succeeds -- report honestly, minimum is lo itself
        return lo, False, trials, time.time() - t_bisect_start
    if not hi_ok:
        # upper bound (previously known-succeeding) failed to reproduce here
        # -- cannot bisect a monotone boundary that does not hold; report
        # NOT_COMPUTED and disclose.
        return None, True, trials, time.time() - t_bisect_start

    while hi - lo > 1:
        if budget_remaining() <= 0:
            return None, True, trials, time.time() - t_bisect_start
        mid = (lo + hi) // 2
        cap = min(BISECTION_TRIAL_CAP_SECONDS, max(1, budget_remaining()))
        t_mid = run_bisect_trial(mid, cap)
        trials.append(t_mid)
        if t_mid.get("status") == "COMPLETED":
            hi = mid
        elif t_mid.get("status") == "ERROR":
            lo = mid
        else:
            # NOT_COMPUTED (trial-level timeout / crash) -- budget exhausted
            # or trial itself failed to resolve; stop bisecting honestly.
            return None, True, trials, time.time() - t_bisect_start

    return hi, False, trials, time.time() - t_bisect_start


def run_main_cell(d, beta, mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_cell_%d_%d.json" % (d, beta))
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
            "exceeded PER_BASIS_FEASIBILITY_CAP_V2" if proc_info["timed_out"] else
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

    print("=== PHASE 1: BISECTION (isolated LLL step, d=%d beta=%d) ===" % (BISECTION_D, BISECTION_BETA), flush=True)
    min_precision, fallback_used, bisect_trials, bisect_wall_clock = bisect_precision()
    precision_used = min_precision if (min_precision is not None and not fallback_used) else FALLBACK_PRECISION_BITS
    bisection_out = {
        "seed_root": SEED_ROOT,
        "bisection_d": BISECTION_D,
        "bisection_beta": BISECTION_BETA,
        "lo_known_failing": BISECTION_LO_KNOWN_FAILING,
        "hi_known_succeeding": BISECTION_HI_KNOWN_SUCCEEDING,
        "bisection_budget_seconds": BISECTION_BUDGET_SECONDS,
        "bisection_wall_clock_seconds": bisect_wall_clock,
        "trials": bisect_trials,
        "determined_minimum_precision_bits": min_precision if not fallback_used else None,
        "fallback_used": fallback_used,
        "fallback_precision_bits": FALLBACK_PRECISION_BITS if fallback_used else None,
        "precision_used_for_main_grid": precision_used,
        "note": (
            "Determined by 1-bit-resolution binary search between the known-failing "
            "and known-succeeding endpoints." if not fallback_used else
            "NOT_COMPUTED: bisection budget exhausted (or a boundary assumption did "
            "not reproduce) -- falling back explicitly to %d bits for phase 2, "
            "disclosed as a fallback, not a determined minimum." % FALLBACK_PRECISION_BITS
        ),
    }
    print(json.dumps(bisection_out, indent=2), flush=True)
    with open(os.path.join(HERE, "bisection_results.json"), "w") as f:
        json.dump(bisection_out, f, indent=2)

    print("=== PHASE 2: MAIN-GRID RE-MEASUREMENT (precision=%d bits) ===" % precision_used, flush=True)
    main_grid = []
    for d, beta in MAIN_CELLS:
        remaining_before_cell = OVERALL_BUDGET_SECONDS - WRITE_BUFFER_SECONDS - overall_elapsed()
        if remaining_before_cell < PER_BASIS_FEASIBILITY_CAP_V2:
            main_grid.append({
                "d": d, "beta": beta,
                "status": "NOT_COMPUTED",
                "reason": "task budget exhausted before this cell was attempted",
                "overall_elapsed_seconds_at_skip": overall_elapsed(),
                "overall_budget_seconds": OVERALL_BUDGET_SECONDS,
            })
            print("cell (d=%d, beta=%d): SKIPPED, task budget exhausted (elapsed=%.1fs)" %
                  (d, beta, overall_elapsed()), flush=True)
            continue
        print("cell (d=%d, beta=%d): launching, cap=%ds, precision=%d bits" %
              (d, beta, PER_BASIS_FEASIBILITY_CAP_V2, precision_used), flush=True)
        cell_result = run_main_cell(d, beta, precision_used, PER_BASIS_FEASIBILITY_CAP_V2)
        print("  -> %s (%.1fs)" % (cell_result["status"], cell_result["subprocess_wall_clock_seconds"]), flush=True)
        main_grid.append(cell_result)

    completed_cells = [c for c in main_grid if c.get("status") == "COMPLETED"]
    overall = {
        "seed_root": SEED_ROOT,
        "per_basis_feasibility_cap_v2_seconds": PER_BASIS_FEASIBILITY_CAP_V2,
        "overall_budget_seconds": OVERALL_BUDGET_SECONDS,
        "precision_used_bits": precision_used,
        "precision_source": "bisected_minimum" if not fallback_used else "disclosed_fallback_212_bits",
        "construction": "GSO.Mat(A, float_type='mpfr'), NO flags=GSO.ROW_EXPO; "
                         "FPLLL.set_precision(N) called BEFORE GSO.Mat construction; "
                         "M.update_gso(); LLL.Reduction(M, flags=LLL.DEFAULT); BKZReduction(L)",
        "main_grid": main_grid,
        "n_cells_completed": len(completed_cells),
        "n_cells_not_computed": len(main_grid) - len(completed_cells),
        "total_script_wall_clock_seconds": overall_elapsed(),
    }
    print(json.dumps(overall, indent=2), flush=True)
    with open(os.path.join(HERE, "stage0_v2_results.json"), "w") as f:
        json.dump(overall, f, indent=2)
    return overall


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker-bisect":
        worker_bisect(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif len(sys.argv) > 1 and sys.argv[1] == "--worker-cell":
        worker_main_cell(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

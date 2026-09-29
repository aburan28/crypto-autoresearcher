#!/usr/bin/env python3
"""
VALIDATOR PROBE B (TASK-20260815-2f026b)

Independent re-attempt of TASK-20260815-6e4c02's own three reattempted
d=512 main-grid cells' full BKZ tours, at the producer's own reported
bisected precision (69 bits), reusing worker_main_cell()'s construction
shape (GSO.Mat -> LLL.Reduction -> BKZReduction(L)) -- a FRESH,
independently-typed implementation (not an import of
stage0_d512_precision_bisection_and_reattempt.py or
stage0_v2_feasibility.py), verified by direct byte-level diff of the
producer's worker_main_cell() against TASK-20260814-534f80's own
worker_main_cell() during this review (bodies are identical apart from a
docstring).

Attempts all three cells the producer reports ERROR for:
  (512, 40): producer reports ERROR, 631.74s, seed_used=2074339090,
             fails inside svp_preprocessing during the first tour.
  (512, 55): producer reports ERROR, 389.37s, seed_used=452658293,
             fails at BKZReduction.__call__'s own initial self.lll_obj().
  (512, 70): producer reports ERROR, 396.35s, seed_used=915347894,
             fails at BKZReduction.__call__'s own initial self.lll_obj().

Uses a REDUCED per-cell cap (PROBE_B_CAP_SECONDS=3600s, not
PER_BASIS_FEASIBILITY_CAP_V3=14400s) -- this probe's own budget
constraint, not a claim about what cap the producer applied. The producer's
own PER_BASIS_FEASIBILITY_CAP_V3=14400s usage is checked separately in
validation_report.yaml by direct inspection of the producer's own script
constant and command.txt/run_manifest.yaml, not by this probe re-running at
that same cap (all three producer cells errored in 389-632s, far under
either cap, so a lower cap here does not affect whether this probe can
observe the same outcome).

Same SEED_ROOT=715923, same default_rng([SEED_ROOT, 0, d, beta, 0, 0])
formula, same corrected ROW_EXPO-free mpfr construction. Each cell runs as
its own OS subprocess with a hard wall-clock cap.

This probe does NOT itself decide any Stage-1 sizing or escalation-branch
question, does not touch (d=256, *), and makes no C1/C2 statement. Claim
tier stays TOY.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))

PRECISION_BITS = 69  # producer's own reported bisected minimum, reused as given
CELLS = [(512, 40), (512, 55), (512, 70)]
PROBE_B_CAP_SECONDS = 3600  # this probe's own budget cap; producer used 14400s
                            # (PER_BASIS_FEASIBILITY_CAP_V3), checked separately
EXPECTED = {
    (512, 40): {"status": "ERROR", "seed_used": 2074339090},
    (512, 55): {"status": "ERROR", "seed_used": 452658293},
    (512, 70): {"status": "ERROR", "seed_used": 915347894},
}

STRATEGIES_PATH_DEFAULT = "/usr/share/libfplll8/strategies/default.json"


def _strategies_path():
    from fpylll import BKZ
    if os.path.exists(STRATEGIES_PATH_DEFAULT):
        return STRATEGIES_PATH_DEFAULT
    return BKZ.DEFAULT_STRATEGY


def worker_main_cell(d, beta, mpfr_bits, out_path):
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
        bkz = BKZReduction(L)
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1

        result.update({
            "status": "COMPLETED",
            "lll_elapsed_seconds": lll_elapsed,
            "bkz_elapsed_seconds": bkz_elapsed,
            "total_elapsed_seconds": lll_elapsed + bkz_elapsed,
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


def run_capped_subprocess(argv, cap_seconds, out_path, mem_poll_interval=0.5):
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


def run_cell(d, beta, mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_probeB_%d_%d.json" % (d, beta))
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
        cell_result["reason"] = "exceeded PROBE_B_CAP_SECONDS" if proc_info["timed_out"] else "worker crashed before writing output"
        cell_result["stderr_tail"] = proc_info["stderr_tail"]
    else:
        with open(out_path) as f:
            cell_result.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return cell_result


def main():
    t_script_start = time.time()
    results = []
    all_match = True
    for d, beta in CELLS:
        print("=== VALIDATOR PROBE B: cell (d=%d, beta=%d), precision=%d bits, cap=%ds ===" %
              (d, beta, PRECISION_BITS, PROBE_B_CAP_SECONDS), flush=True)
        cell_result = run_cell(d, beta, PRECISION_BITS, PROBE_B_CAP_SECONDS)
        exp = EXPECTED[(d, beta)]
        cell_result["expected_status"] = exp["status"]
        cell_result["expected_seed"] = exp["seed_used"]
        cell_result["matches_producer_report"] = (
            cell_result.get("status") == exp["status"]
            and cell_result.get("seed_used") == exp["seed_used"]
        )
        if not cell_result["matches_producer_report"]:
            all_match = False
        print("  -> %s (%.1fs) matches_producer_report=%s" %
              (cell_result.get("status"), cell_result.get("subprocess_wall_clock_seconds", -1),
               cell_result["matches_producer_report"]), flush=True)
        results.append(cell_result)
        with open(os.path.join(HERE, "probe_b_main_grid_cell_reattempt_results.json"), "w") as f:
            json.dump({
                "purpose": "Independent re-attempt of TASK-20260815-6e4c02's own three reattempted "
                           "d=512 main-grid cells' full BKZ tours at the producer's own reported "
                           "bisected precision (69 bits).",
                "seed_root": SEED_ROOT,
                "precision_bits_used": PRECISION_BITS,
                "probe_b_cap_seconds": PROBE_B_CAP_SECONDS,
                "producer_cap_seconds_per_basis_feasibility_cap_v3": 14400,
                "cells": results,
                "n_cells_attempted_so_far": len(results),
                "all_trials_match_producer_report_so_far": all_match,
                "total_script_wall_clock_seconds_so_far": time.time() - t_script_start,
                "in_progress": True,
            }, f, indent=2)

    with open(os.path.join(HERE, "probe_b_main_grid_cell_reattempt_results.json"), "w") as f:
        json.dump({
            "purpose": "Independent re-attempt of TASK-20260815-6e4c02's own three reattempted "
                       "d=512 main-grid cells' full BKZ tours at the producer's own reported "
                       "bisected precision (69 bits).",
            "seed_root": SEED_ROOT,
            "precision_bits_used": PRECISION_BITS,
            "probe_b_cap_seconds": PROBE_B_CAP_SECONDS,
            "producer_cap_seconds_per_basis_feasibility_cap_v3": 14400,
            "cells": results,
            "n_cells_attempted": len(results),
            "all_trials_match_producer_report": all_match,
            "total_script_wall_clock_seconds": time.time() - t_script_start,
            "in_progress": False,
        }, f, indent=2)
    print("=== DONE. all_trials_match_producer_report: %s ===" % all_match, flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker-cell":
        worker_main_cell(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

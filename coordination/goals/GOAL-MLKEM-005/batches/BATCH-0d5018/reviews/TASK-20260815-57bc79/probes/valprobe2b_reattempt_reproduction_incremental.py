#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe2b_reattempt_reproduction_incremental.py

THIRD ATTEMPT at this task's own completion_gate item

  "AT LEAST ONE of the two reattempted cells' own reported outcome is
   independently re-attempted where budget allows, and the reported
   wall-clock compared; state explicitly if budget only allows one, not both."

WHY A THIRD ATTEMPT -- BOTH PRIOR FAILURES ARE INFRASTRUCTURE, NOT RESULTS
(AGENTS.md core rule 5 / CLAUDE.md rule 3), AND BOTH ARE PRESERVED, NOT
OVERWRITTEN:

  attempt 1 (valprobe2_attempt1_psutil_missing_*.log): died immediately on
    `import psutil`; psutil is not installed on this host. Fixed by polling
    RSS through `ps` instead.

  attempt 2 (valprobe2_attempt2_harness_killed_*.log): the (d=512, beta=55)
    cell RAN TO A TERMINAL OUTCOME and its summary line survives in the
    preserved stdout --

        -> (d=512, beta=55) ERROR (1346.0s)

    -- but valprobe2 accumulated per-cell detail in memory and serialized it
    only after BOTH cells finished, and the probe's PARENT process was killed
    by this session's own background-task lifecycle limit before it could
    write. So the terminal outcome and wall-clock survive and the traceback,
    seed and RSS do not. This is the identical monitoring-loop artifact the
    producer disclosed as its own ANOM-2, now hitting the reviewer.

    Directly observed by `ps` at 2026-08-17T19:23:26Z, the (d=512, beta=70)
    worker (pid 20035) was still alive at 46m39s = 2799s elapsed, having
    raised nothing. That single observation is recorded in the validation
    report as what it is -- a lower bound of >= 2799s with no ReductionError
    -- and this probe does NOT re-run beta=70, because 2799s already exceeds
    any partial cap this task's remaining budget could afford, so a re-run
    would add nothing.

THE ONE DESIGN CHANGE: this probe serializes its state to disk after EVERY
poll and immediately on cell completion, so a kill can lose at most the last
two seconds. Nothing else changes: same construction, same seed formula, same
cell, same precision.

Re-attempts (d=512, beta=55) at 75 bits ONLY. Writes only inside this
validation task's own write_scope.
"""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "valprobe2b_reattempt_reproduction_results.json")

D = 512
BETA = 55
MPFR_BITS = 75                     # the producer's own bisected minimum at this cell
VALIDATOR_CAP_SECONDS = 2700       # ~2x attempt 2's own measured 1346.0s
PRODUCER_CAP_SECONDS = 14400       # PER_BASIS_FEASIBILITY_CAP_V3, QUOTED, NOT APPLIED HERE

PRODUCER_REPORTED = {
    "status": "ERROR",
    "error": "ReductionError: b'infinite loop in babai'",
    "subprocess_wall_clock_seconds": 2502.7416553497314,
    "outer_lll_reduction_elapsed_seconds": 413.6276364326477,
    "peak_rss_mb": 141.3828125,
    "failure_site": "fpylll/algorithms/bkz.py line 186, svp_preprocessing -> "
                    "self.lll_obj(lll_start, lll_start, kappa + block_size)",
}

STRATEGY_CANDIDATES = [
    "/usr/share/libfplll8/strategies/default.json",  # the producer's path (absent here)
    "/opt/homebrew/Cellar/fplll/5.5.0/share/fplll/strategies/default.json",
    "/opt/homebrew/share/fplll/strategies/default.json",
]


def strategies_path():
    for c in STRATEGY_CANDIDATES:
        if os.path.exists(c):
            return c
    from fpylll import BKZ
    return BKZ.DEFAULT_STRATEGY


def rss_bytes(pid):
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=10)
        v = out.stdout.strip().split()
        if v:
            return int(v[0]) * 1024
    except Exception:
        pass
    return None


def worker(d, beta, mpfr_bits, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits,
              "construction": "corrected_mpfr_no_row_expo"}
    t0 = None
    try:
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1)
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed

        sp = strategies_path()
        result["strategies_file_used"] = sp if isinstance(sp, str) else repr(sp)

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        t0 = time.time()
        LLL.reduction(A)
        lll_elapsed = time.time() - t0
        result["outer_lll_reduction_elapsed_seconds"] = lll_elapsed

        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        par = BKZ.Param(block_size=beta, strategies=sp, flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(L)
        t1 = time.time()
        bkz(par, tracer=True)
        bkz_elapsed = time.time() - t1

        n_tours = None
        try:
            if bkz.trace is not None:
                n_tours = sum(1 for c in bkz.trace.children if c.label[0] == "tour")
        except Exception:
            n_tours = None

        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        first_vec_norm = float(r0) ** 0.5
        delta_0 = (first_vec_norm / np.exp(float(log_det) / d)) ** (1.0 / d)

        result.update({
            "status": "COMPLETED",
            "lll_elapsed_seconds": lll_elapsed,
            "bkz_elapsed_seconds": bkz_elapsed,
            "total_elapsed_seconds": lll_elapsed + bkz_elapsed,
            "n_tours": n_tours,
            "delta_0_root_hermite_factor": float(delta_0),
        })
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["elapsed_seconds_at_error"] = (time.time() - t0) if t0 else None
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        try:
            from fpylll import FPLLL
            FPLLL.set_precision(53)
        except Exception:
            pass

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


def snapshot(state):
    """Serialize after EVERY poll. This is the whole point of attempt 3."""
    tmp = OUT_PATH + ".partial"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, OUT_PATH)


def main():
    import fpylll
    t_start = time.time()
    sp = strategies_path()
    sp_sha = (hashlib.sha256(open(sp, "rb").read()).hexdigest()
              if isinstance(sp, str) and os.path.exists(sp) else None)

    state = {
        "probe": "valprobe2b_reattempt_reproduction_incremental",
        "task_id": "TASK-20260815-57bc79",
        "attempt": 3,
        "prior_attempts": [
            {"attempt": 1, "outcome": "INFRASTRUCTURE_FAILURE",
             "cause": "ModuleNotFoundError: No module named 'psutil'",
             "artifacts": ["valprobe2_attempt1_psutil_missing_stderr.log",
                           "valprobe2_attempt1_psutil_missing_stdout.log"]},
            {"attempt": 2, "outcome": "INFRASTRUCTURE_FAILURE_AFTER_A_REAL_MEASUREMENT",
             "cause": "probe parent process killed by this session's background-task "
                      "lifecycle limit before it serialized per-cell detail",
             "what_survived": "(d=512, beta=55) reached a terminal ERROR at 1346.0s; "
                              "that summary line is preserved in "
                              "valprobe2_attempt2_harness_killed_stdout.log",
             "what_was_lost": "traceback, seed_used, peak RSS and strategies file for "
                              "that cell, plus the (d=512, beta=70) partial record",
             "direct_ps_observation_beta70": "pid 20035 still alive at "
                                             "2026-08-17T19:23:26Z, 46m39s = 2799s "
                                             "elapsed, having raised nothing",
             "artifacts": ["valprobe2_attempt2_harness_killed_stdout.log",
                           "valprobe2_attempt2_harness_killed_stderr.log"]},
        ],
        "cell": {"d": D, "beta": BETA, "mpfr_bits_used": MPFR_BITS},
        "validator_cap_seconds": VALIDATOR_CAP_SECONDS,
        "producer_cap_seconds_quoted_not_applied": PRODUCER_CAP_SECONDS,
        "producer_reported": PRODUCER_REPORTED,
        "beta70_not_rerun_reason": (
            "The producer's (d=512, beta=70) cell was hard-killed at "
            "PER_BASIS_FEASIBILITY_CAP_V3=14400s, which alone exceeds this validation "
            "task's ENTIRE 12000s budget, so its terminal outcome is UNREPRODUCIBLE "
            "here and is reported as such. Attempt 2 already observed that cell alive "
            "and silent for >= 2799s; no affordable re-run improves on that bound."
        ),
        "environment_deviation_from_producer": {
            "producer_platform": "Linux-6.18.5-fc-v20-x86_64-with-glibc2.39 (nproc 4, 15GiB)",
            "validator_platform": platform.platform(),
            "producer_python": "3.11.15", "validator_python": sys.version.split()[0],
            "producer_numpy": "2.4.6", "validator_numpy": np.__version__,
            "producer_fpylll": "0.6.4", "validator_fpylll": fpylll.__version__,
            "producer_strategies_file": "/usr/share/libfplll8/strategies/default.json",
            "validator_strategies_file": sp if isinstance(sp, str) else repr(sp),
            "validator_strategies_file_sha256": sp_sha,
            "note": "The producer's strategies file lives on a host this session cannot "
                    "read, so it could not be compared byte-for-byte. Wall-clock is "
                    "therefore NOT commensurable across hosts and is reported as an "
                    "order-of-magnitude comparison only.",
        },
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    snapshot(state)

    cell_out = os.path.join(HERE, "_tmp_valprobe2b_%d_%d.json" % (D, BETA))
    if os.path.exists(cell_out):
        os.remove(cell_out)
    argv = [sys.executable, os.path.abspath(__file__), "--worker",
            str(D), str(BETA), str(MPFR_BITS), cell_out]
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("launched (d=%d, beta=%d, bits=%d) cap=%ds pid=%d"
          % (D, BETA, MPFR_BITS, VALIDATOR_CAP_SECONDS, p.pid), flush=True)
    state["worker_pid"] = p.pid
    t0 = time.time()
    peak = None
    timed_out = False

    while True:
        r = rss_bytes(p.pid)
        if r is not None:
            peak = r if peak is None else max(peak, r)
        ret = p.poll()
        elapsed = time.time() - t0
        state["elapsed_seconds_so_far"] = elapsed
        state["peak_rss_mb_so_far"] = peak / (1024 * 1024) if peak is not None else None
        state["last_poll_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        snapshot(state)
        if ret is not None:
            break
        if elapsed >= VALIDATOR_CAP_SECONDS:
            timed_out = True
            try:
                p.terminate()
                p.wait(timeout=10)
            except Exception:
                p.kill()
            break
        time.sleep(2.0)

    try:
        so, se = p.communicate(timeout=15)
    except Exception:
        so, se = b"", b""

    cell = {"d": D, "beta": BETA, "mpfr_bits_used": MPFR_BITS,
            "subprocess_wall_clock_seconds": time.time() - t0,
            "peak_rss_mb": peak / (1024 * 1024) if peak is not None else None,
            "peak_rss_note": "sampled at 2s intervals via `ps -o rss=`; psutil absent on "
                             "this host. null means NOT MEASURED, never zero.",
            "subprocess_timed_out": timed_out,
            "subprocess_returncode": p.returncode}
    if timed_out or not os.path.exists(cell_out):
        cell["status"] = "NOT_COMPUTED"
        cell["reason"] = ("exceeded this VALIDATOR's own %ds cap -- NOT the producer's "
                          "PER_BASIS_FEASIBILITY_CAP_V3=%ds"
                          % (VALIDATOR_CAP_SECONDS, PRODUCER_CAP_SECONDS)) if timed_out \
                         else "worker crashed before writing output"
        cell["stderr_tail"] = se.decode(errors="replace")[-2000:]
    else:
        with open(cell_out) as f:
            cell.update(json.load(f))
        os.remove(cell_out)

    frames = []
    tb = cell.get("traceback")
    if tb:
        frames = [l.strip() for l in tb.split("\n")
                  if l.strip().startswith("File") or l.strip().startswith("fpylll.util")]

    state["cell_result"] = cell
    state["failure_frames"] = frames
    state["agrees_with_producer_status"] = cell.get("status") == PRODUCER_REPORTED["status"]
    state["agrees_with_producer_error_string"] = cell.get("error") == PRODUCER_REPORTED["error"]
    state["wall_clock_ratio_validator_over_producer"] = (
        cell["subprocess_wall_clock_seconds"] / PRODUCER_REPORTED["subprocess_wall_clock_seconds"]
    )
    state["status"] = "DONE"
    state["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state["total_wall_clock_seconds"] = time.time() - t_start
    snapshot(state)
    print("  -> (d=%d, beta=%d) %s (%.1fs)"
          % (D, BETA, cell.get("status"), cell["subprocess_wall_clock_seconds"]), flush=True)
    print(json.dumps({k: state[k] for k in
                      ("agrees_with_producer_status", "agrees_with_producer_error_string",
                       "wall_clock_ratio_validator_over_producer", "failure_frames")},
                     indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

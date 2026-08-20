#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe2_reattempt_reproduction.py

Discharges this task's own completion_gate item:

  "AT LEAST ONE of the two reattempted cells' own reported outcome is
   independently re-attempted where budget allows, and the reported
   wall-clock compared; state explicitly if budget only allows one, not
   both."

BUDGET REALITY, STATED UP FRONT AND NOT HIDDEN:
  - The producer's (d=512, beta=55) cell reached a terminal ERROR in
    2502.74s. That IS re-attemptable inside this validation task's own
    12000s wall-clock budget, so it is re-attempted in FULL here.
  - The producer's (d=512, beta=70) cell was hard-killed at
    PER_BASIS_FEASIBILITY_CAP_V3 = 14400s having neither completed nor
    raised. Reproducing that outcome requires >= 14400s of wall clock on
    ONE cell alone, which EXCEEDS this validation task's ENTIRE 12000s
    budget. It therefore CANNOT be re-attempted to its own terminal
    outcome here, and this probe does NOT pretend to. What it runs instead
    is a deliberately, explicitly PARTIAL re-attempt under this
    validator's own smaller, separately-named cap
    (VALIDATOR_PARTIAL_CAP_SECONDS), which can only ever answer the
    strictly weaker question "does this cell raise the ReductionError
    signature EARLY, the way beta=55 does?" -- never "would it have
    completed at 14401s?".

CONSTRUCTION: an independent transcription of the construction the producer
declares, which this validator separately confirmed is AST-identical between
the producer's own worker_main_cell() and TASK-20260815-6e4c02's validated
worker_main_cell(): FPLLL.set_random_seed(seed) from
default_rng([715923, 0, d, beta, 0, 0]); IntegerMatrix.random(d, "qary",
k=d//2, q=3329); outer double-precision LLL.reduction(A);
FPLLL.set_precision(N) BEFORE GSO.Mat; GSO.Mat(A, float_type="mpfr") with NO
flags=GSO.ROW_EXPO; M.update_gso(); LLL.Reduction(M, flags=LLL.DEFAULT);
BKZ.Param(block_size=beta, strategies=..., flags=BKZ.AUTO_ABORT);
BKZReduction(L); bkz(par, tracer=True).

DISCLOSED ENVIRONMENT DEVIATION (this is a different host from the
producer's, and that is unavoidable for an independent session): the
producer's strategies file was /usr/share/libfplll8/strategies/default.json
(Debian libfplll8). That path does not exist on this host and this host's
fpylll BKZ.DEFAULT_STRATEGY points at a non-existent wheel-build path, so
this probe uses the locally installed fplll 5.5.0 strategies file and
RECORDS ITS PATH AND SHA-256 so a later reader can compare. Python, numpy
and OS also differ; fpylll is 0.6.4 on both. Every one of these is recorded
in the output JSON rather than assumed harmless.

Imports nothing from the producer's artifacts; writes only inside this
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

PRODUCER_CAP_SECONDS = 14400          # PER_BASIS_FEASIBILITY_CAP_V3, quoted, NOT applied here
VALIDATOR_FULL_CAP_SECONDS = 5400     # (d=512, beta=55): ~2.16x the producer's own 2502.74s
VALIDATOR_PARTIAL_CAP_SECONDS = 3600  # (d=512, beta=70): explicitly PARTIAL, 0.25x the producer's cap

STRATEGY_CANDIDATES = [
    "/usr/share/libfplll8/strategies/default.json",  # the producer's own path (absent on this host)
    "/opt/homebrew/Cellar/fplll/5.5.0/share/fplll/strategies/default.json",
    "/opt/homebrew/share/fplll/strategies/default.json",
]

# (d, beta, mpfr_bits, cap, kind, producer_reported)
PLAN = [
    (512, 55, 75, VALIDATOR_FULL_CAP_SECONDS, "full_reattempt",
     {"status": "ERROR", "error": "ReductionError: b'infinite loop in babai'",
      "subprocess_wall_clock_seconds": 2502.7416553497314,
      "outer_lll_reduction_elapsed_seconds": 413.6276364326477,
      "peak_rss_mb": 141.3828125}),
    (512, 70, 73, VALIDATOR_PARTIAL_CAP_SECONDS, "partial_reattempt_budget_bounded",
     {"status": "NOT_COMPUTED", "reason": "exceeded PER_BASIS_FEASIBILITY_CAP_V3",
      "subprocess_wall_clock_seconds": 14400.084456205368,
      "peak_rss_mb": 142.421875}),
]


def strategies_path():
    for c in STRATEGY_CANDIDATES:
        if os.path.exists(c):
            return c
    from fpylll import BKZ
    return BKZ.DEFAULT_STRATEGY


def worker(d, beta, mpfr_bits, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits,
              "construction": "corrected_mpfr_no_row_expo"}
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
        })
        FPLLL.set_precision(53)
    except Exception as exc:  # noqa: BLE001
        import traceback
        result["status"] = "ERROR"
        result["elapsed_seconds_at_error"] = time.time() - t0 if "t0" in dir() else None
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        result["traceback"] = traceback.format_exc()
        try:
            from fpylll import FPLLL
            FPLLL.set_precision(53)
        except Exception:
            pass

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)


def _rss_bytes(pid):
    """Peak-RSS polling WITHOUT psutil, which is NOT installed on this host.

    ATTEMPT 1 OF THIS PROBE FAILED WITH ModuleNotFoundError: No module named
    'psutil' (preserved at valprobe2_attempt1_psutil_missing_stderr.log). That
    is an INFRASTRUCTURE SIGNAL, never a result, and never mathematical
    evidence -- AGENTS.md core rule 5 / CLAUDE.md rule 3. Rather than fabricate
    or omit a memory figure, this probe substitutes a dependency-free `ps`
    reading. Returns None when `ps` cannot answer, and None is then recorded as
    "not measured" rather than as a number.
    """
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=10)
        v = out.stdout.strip().split()
        if v:
            return int(v[0]) * 1024
    except Exception:
        pass
    return None


def main():
    t_start = time.time()
    entries = []
    for (d, beta, bits, cap, kind, producer) in PLAN:
        out_path = os.path.join(HERE, "_tmp_valprobe2_%d_%d.json" % (d, beta))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker",
                str(d), str(beta), str(bits), out_path]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        entries.append({"d": d, "beta": beta, "mpfr_bits": bits, "cap_seconds": cap,
                        "kind": kind, "producer_reported": producer, "proc": p,
                        "out_path": out_path, "t0": time.time(),
                        "peak_rss": None})
        print("launched (d=%d, beta=%d, bits=%d) kind=%s cap=%ds pid=%d"
              % (d, beta, bits, kind, cap, p.pid), flush=True)

    cells = []
    remaining = list(entries)
    while remaining:
        time.sleep(2.0)
        still = []
        for e in remaining:
            rss = _rss_bytes(e["proc"].pid)
            if rss is not None:
                e["peak_rss"] = rss if e["peak_rss"] is None else max(e["peak_rss"], rss)
            ret = e["proc"].poll()
            if ret is None and (time.time() - e["t0"]) < e["cap_seconds"]:
                still.append(e)
                continue
            timed_out = ret is None
            if timed_out:
                try:
                    e["proc"].terminate()
                    e["proc"].wait(timeout=10)
                except Exception:
                    e["proc"].kill()
            try:
                so, se = e["proc"].communicate(timeout=15)
            except Exception:
                so, se = b"", b""
            cell = {
                "d": e["d"], "beta": e["beta"], "mpfr_bits_used": e["mpfr_bits"],
                "validator_cap_seconds": e["cap_seconds"],
                "kind": e["kind"],
                "producer_reported": e["producer_reported"],
                "producer_cap_seconds_quoted_not_applied": PRODUCER_CAP_SECONDS,
                "subprocess_wall_clock_seconds": time.time() - e["t0"],
                "peak_rss_mb": (e["peak_rss"] / (1024 * 1024)
                                if e["peak_rss"] is not None else None),
                "peak_rss_note": (
                    "sampled at 2s intervals via `ps -o rss=`; psutil is NOT installed "
                    "on this host (attempt 1 of this probe died on that import, log "
                    "preserved). null means NOT MEASURED, never zero."
                ),
                "subprocess_timed_out": timed_out,
                "subprocess_returncode": e["proc"].returncode,
            }
            if timed_out or not os.path.exists(e["out_path"]):
                cell["status"] = "NOT_COMPUTED"
                cell["reason"] = (
                    "exceeded this VALIDATOR's own %ds cap -- NOT the producer's "
                    "PER_BASIS_FEASIBILITY_CAP_V3=%ds, and NOT a reproduction of "
                    "the producer's own cap-exceeded outcome"
                    % (e["cap_seconds"], PRODUCER_CAP_SECONDS)
                ) if timed_out else "worker crashed before writing output"
                cell["stderr_tail"] = se.decode(errors="replace")[-2000:]
            else:
                with open(e["out_path"]) as f:
                    cell.update(json.load(f))
                os.remove(e["out_path"])
            print("  -> (d=%d, beta=%d) %s (%.1fs)"
                  % (cell["d"], cell["beta"], cell.get("status"),
                     cell["subprocess_wall_clock_seconds"]), flush=True)
            cells.append(cell)
        remaining = still

    sp = strategies_path()
    sp_sha = None
    if isinstance(sp, str) and os.path.exists(sp):
        sp_sha = hashlib.sha256(open(sp, "rb").read()).hexdigest()
    import fpylll
    out = {
        "probe": "valprobe2_reattempt_reproduction",
        "task_id": "TASK-20260815-57bc79",
        "seed_root": SEED_ROOT,
        "cells": sorted(cells, key=lambda c: c["beta"]),
        "budget_statement": (
            "(d=512, beta=55) was re-attempted IN FULL to a terminal outcome. "
            "(d=512, beta=70) COULD NOT BE re-attempted to its own terminal outcome: "
            "the producer's cell was killed at PER_BASIS_FEASIBILITY_CAP_V3=14400s, "
            "which alone exceeds this validation task's entire 12000s wall-clock "
            "budget. It was run PARTIALLY, under this validator's own separately "
            "named %ds cap, which can only answer 'does it raise the ReductionError "
            "signature early?' and NEVER 'would it have completed?'."
            % VALIDATOR_PARTIAL_CAP_SECONDS
        ),
        "environment_deviation_from_producer": {
            "producer_platform": "Linux-6.18.5-fc-v20-x86_64-with-glibc2.39 (nproc 4, 15GiB)",
            "validator_platform": platform.platform(),
            "producer_python": "3.11.15",
            "validator_python": sys.version.split()[0],
            "producer_numpy": "2.4.6",
            "validator_numpy": np.__version__,
            "producer_fpylll": "0.6.4",
            "validator_fpylll": fpylll.__version__,
            "producer_strategies_file": "/usr/share/libfplll8/strategies/default.json",
            "validator_strategies_file": sp if isinstance(sp, str) else repr(sp),
            "validator_strategies_file_sha256": sp_sha,
            "note": (
                "The producer's strategies file is on a host this session cannot "
                "read, so its content could not be compared byte-for-byte. Wall-clock "
                "figures are therefore NOT directly commensurable across hosts and are "
                "reported as an order-of-magnitude comparison only. The validator host "
                "was concurrently loaded (shared with an unrelated red-team session)."
            ),
        },
        "total_wall_clock_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "valprobe2_reattempt_reproduction_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"cells": [{k: v for k, v in c.items() if k != "traceback"}
                                for c in out["cells"]],
                      "total_wall_clock_seconds": out["total_wall_clock_seconds"]},
                     indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

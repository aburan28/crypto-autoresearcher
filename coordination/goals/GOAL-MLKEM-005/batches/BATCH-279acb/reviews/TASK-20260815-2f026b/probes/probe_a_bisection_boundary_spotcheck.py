#!/usr/bin/env python3
"""
VALIDATOR PROBE A (TASK-20260815-2f026b)

Independent spot-check of TASK-20260815-6e4c02's own reported bisection
result: "determined_minimum_precision_bits: 69" at (d=512, beta=40),
isolated-LLL-step level (68 bits ERROR, 69 bits COMPLETED).

This is a FRESH, independently-typed implementation (not an import of the
producer's script, not an import of probe1_bisection_generality.py), that
reproduces the SAME construction shape both of those files use, verified by
direct byte-level diff of the producer's worker_bisect() against probe1's
own worker() during this review (bodies are identical apart from a
docstring). This probe types the same nine lines of fpylll calls itself,
independently, as its own act of verification, rather than calling either
file's own function.

Tests exactly the two trial precisions that bracket the producer's own
reported minimum:
  - 68 bits: producer reports ERROR ("infinite loop in babai")
  - 69 bits: producer reports COMPLETED

Same construction: outer double-precision LLL.reduction(A), then
FPLLL.set_precision(N) BEFORE GSO.Mat construction, GSO.Mat(A,
float_type="mpfr") with NO flags=GSO.ROW_EXPO, M.update_gso(),
LLL.Reduction(M, flags=LLL.DEFAULT), call lll_obj() directly -- NOT wrapped
in BKZReduction. Same SEED_ROOT=715923, same default_rng([SEED_ROOT, 0, d,
beta, 0, 0]) formula. Each trial runs as its own OS subprocess (same
isolation discipline as producer/probe1) with a hard wall-clock cap.

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

TEST_D = 512
TEST_BETA = 40
PRECISIONS_TO_TEST = [68, 69]
EXPECTED = {68: "ERROR", 69: "COMPLETED"}
EXPECTED_SEED = 2074339090
TRIAL_CAP_SECONDS = 900


def worker(d, beta, mpfr_bits, out_path):
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


def run_trial(d, beta, mpfr_bits, cap_seconds):
    out_path = os.path.join(HERE, "_tmp_probeA_%d_%d.json" % (d, mpfr_bits))
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [sys.executable, os.path.abspath(__file__), "--worker",
            str(d), str(beta), str(mpfr_bits), out_path]
    t0 = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=cap_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=15)
        except Exception:
            proc.kill()
            stdout, stderr = b"", b""
    wall_clock = time.time() - t0

    trial = {
        "d": d, "beta": beta, "mpfr_bits": mpfr_bits,
        "subprocess_wall_clock_seconds": wall_clock,
        "subprocess_timed_out": timed_out,
        "subprocess_returncode": proc.returncode,
    }
    if timed_out or not os.path.exists(out_path):
        trial["status"] = "NOT_COMPUTED"
        trial["reason"] = "trial subprocess exceeded its own cap (%ds)" % cap_seconds if timed_out else "worker crashed before writing output"
        trial["stderr_tail"] = stderr.decode(errors="replace")[-2000:] if not timed_out else ""
    else:
        with open(out_path) as f:
            trial.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return trial


def main():
    results = []
    all_match = True
    for bits in PRECISIONS_TO_TEST:
        print("=== VALIDATOR PROBE A: testing (d=%d, beta=%d) at mpfr_bits=%d ===" %
              (TEST_D, TEST_BETA, bits), flush=True)
        trial = run_trial(TEST_D, TEST_BETA, bits, TRIAL_CAP_SECONDS)
        expected_status = EXPECTED[bits]
        trial["expected_status"] = expected_status
        trial["expected_seed"] = EXPECTED_SEED
        trial["matches_producer_report"] = (
            trial.get("status") == expected_status
            and trial.get("seed_used") == EXPECTED_SEED
        )
        if not trial["matches_producer_report"]:
            all_match = False
        print(json.dumps(trial, indent=2), flush=True)
        results.append(trial)
        with open(os.path.join(HERE, "probe_a_bisection_boundary_spotcheck_results.json"), "w") as f:
            json.dump({
                "purpose": "Independent spot-check of TASK-20260815-6e4c02's own reported "
                           "bisection boundary at (d=512, beta=40), isolated-LLL-step level: "
                           "68 bits ERROR, 69 bits COMPLETED (determined_minimum_precision_bits=69).",
                "seed_root": SEED_ROOT,
                "test_d": TEST_D,
                "test_beta": TEST_BETA,
                "precisions_tested": PRECISIONS_TO_TEST,
                "results": results,
                "all_trials_match_producer_report_so_far": all_match,
            }, f, indent=2)
    print("=== DONE. all_trials_match_producer_report: %s ===" % all_match, flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

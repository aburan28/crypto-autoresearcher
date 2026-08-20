#!/usr/bin/env python3
"""
RED TEAM PROBE 1 (TASK-20260814-9cf080)

Challenges the completion_gate's own required question: "does the reported
minimum precision found at one instance (d=256,beta=40) actually hold at the
OTHER 5 main-grid cells?"

Method: EXACTLY reproduces TASK-20260814-534f80's own worker_bisect() shape
(isolated LLL-preprocessing step only: outer double-precision
LLL.reduction(A), then FPLLL.set_precision(N) BEFORE GSO.Mat construction,
GSO.Mat(A, float_type="mpfr") with NO flags=GSO.ROW_EXPO, M.update_gso(),
LLL.Reduction(M, flags=LLL.DEFAULT), call lll_obj() directly -- NOT wrapped
in BKZReduction), same SEED_ROOT=715923 / default_rng formula, run as a
fresh OS subprocess per trial (same isolation discipline as the producer).

Tests whether TASK-20260814-534f80's own "determined minimum adequate mpfr
precision" of 65 bits (found ONLY at d=256, beta=40) also succeeds at
d=512 -- one of the two main-grid dimensions -- at several precision points
BELOW and AT the reported main-grid failure precision, plus one point
matching TASK-20260814-fe02ff's own probe5 value (212 bits, known-succeeding
at d=256's isolated step).

This is independent, executed evidence (this session's own subprocess runs,
same fpylll 0.6.4 build/version confirmed against environment.json), not
mere analysis of the producer's own traceback -- though the producer's own
stage0_v2_results.json ALREADY shows suggestive evidence: at (d=512, *),
every ERROR traceback's innermost frame is bkz.py:123's `self.lll_obj()` --
the FIRST call inside BKZReduction.__call__, before any tour begins, which
BKZReduction.__init__ sets to the SAME LLL.Reduction object this probe
calls directly (see stage0_v2_feasibility.py's own construction note). That
is: the operation failing at d=512 IS, in substance, the same isolated-LLL
operation this producer bisected only at d=256.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))

# (d, beta) used ONLY to reproduce the producer's own seed formula exactly;
# beta itself does not affect the isolated LLL step's own computation, only
# which basis is drawn via the seed.
TEST_D = 512
TEST_BETA = 40  # matches the failing (512,40) main-grid cell's own seed

PRECISIONS_TO_TEST = [65, 100, 130, 180, 212]
TRIAL_CAP_SECONDS = 900  # matches producer's own BISECTION_TRIAL_CAP_SECONDS


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
    out_path = os.path.join(HERE, "_tmp_probe1_%d_%d.json" % (d, mpfr_bits))
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
    for bits in PRECISIONS_TO_TEST:
        print("=== testing (d=%d, beta=%d) at mpfr_bits=%d ===" % (TEST_D, TEST_BETA, bits), flush=True)
        trial = run_trial(TEST_D, TEST_BETA, bits, TRIAL_CAP_SECONDS)
        print(json.dumps(trial, indent=2), flush=True)
        results.append(trial)
        with open(os.path.join(HERE, "probe1_bisection_generality_results.json"), "w") as f:
            json.dump({
                "purpose": "Tests whether TASK-20260814-534f80's own bisected 65-bit minimum "
                           "(determined ONLY at d=256,beta=40) generalizes to d=512, at the "
                           "isolated-LLL-step level (the same operation bkz.py:123's "
                           "self.lll_obj() performs as the FIRST call inside BKZReduction).",
                "seed_root": SEED_ROOT,
                "test_d": TEST_D,
                "test_beta": TEST_BETA,
                "precisions_tested": PRECISIONS_TO_TEST,
                "results": results,
            }, f, indent=2)
        # Early stop once we find both a failing and a succeeding precision --
        # that alone establishes non-generality; continuing narrows the gap
        # but is not required to answer the completion_gate's own question.
        statuses = {r["mpfr_bits"]: r.get("status") for r in results}
        if "COMPLETED" in statuses.values() and "ERROR" in statuses.values():
            completed_bits = min(b for b, s in statuses.items() if s == "COMPLETED")
            error_bits = max(b for b, s in statuses.items() if s == "ERROR")
            if completed_bits > error_bits:
                print("=== Found both a failing (%d bits) and succeeding (%d bits) precision "
                      "at d=512 -- non-generality established. Stopping early to conserve "
                      "review budget; NOT bisecting to 1-bit resolution (that is a further, "
                      "separate measurement this probe does not claim to have made)."
                      % (error_bits, completed_bits), flush=True)
                break
    print("=== DONE ===", flush=True)
    print(json.dumps(results, indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

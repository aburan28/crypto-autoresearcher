#!/usr/bin/env python3
"""
RED TEAM PROBE 0 (TASK-20260814-9cf080)

Sanity check BEFORE spending probe1's own d=512 budget: independently
reproduces TASK-20260814-534f80's own bisection determination at its exact
tested instance (d=256, beta=40, mpfr_bits=65 -> COMPLETED; mpfr_bits=64 ->
ERROR), using this session's own fresh subprocess, same fpylll 0.6.4 build
confirmed against environment.json (Location: /usr/local/lib/python3.11/
dist-packages, version 0.6.4 -- independently confirmed by this session via
`importlib.metadata.version("fpylll")` before running this probe).

If this probe does NOT reproduce bit-identically, probe1's own d=512 results
are not directly comparable to the producer's own d=256 bisection and that
must be disclosed as a limitation rather than silently assumed away.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))


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

        FPLLL.set_precision(mpfr_bits)
        M = GSO.Mat(A, float_type="mpfr")
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


def run_trial(d, beta, mpfr_bits, cap_seconds=900):
    out_path = os.path.join(HERE, "_tmp_probe0_%d.json" % mpfr_bits)
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
        stdout, stderr = proc.communicate(timeout=15)
    wall_clock = time.time() - t0
    trial = {"mpfr_bits": mpfr_bits, "subprocess_wall_clock_seconds": wall_clock,
             "subprocess_timed_out": timed_out, "subprocess_returncode": proc.returncode}
    if timed_out or not os.path.exists(out_path):
        trial["status"] = "NOT_COMPUTED"
    else:
        with open(out_path) as f:
            trial.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return trial


def main():
    import importlib.metadata
    env_check = {
        "fpylll_version_this_session": importlib.metadata.version("fpylll"),
        "expected_from_producer_environment_json": "0.6.4",
    }
    print(json.dumps(env_check, indent=2), flush=True)

    results = []
    for bits in [64, 65]:
        t = run_trial(256, 40, bits)
        print(json.dumps(t, indent=2), flush=True)
        results.append(t)

    out = {
        "env_check": env_check,
        "producer_reported": {
            "mpfr_bits_64": "ERROR: ReductionError infinite loop in babai (bisection_results.json)",
            "mpfr_bits_65": "COMPLETED, 0.0025424957275390625s (bisection_results.json)",
            "seed_used_expected": 1398073216,
        },
        "this_session_reproduction": results,
        "bit_identical_reproduction": (
            results[0]["status"] == "ERROR" and results[1]["status"] == "COMPLETED"
            and results[0].get("seed_used") == 1398073216 and results[1].get("seed_used") == 1398073216
        ),
    }
    with open(os.path.join(HERE, "probe0_sanity_reproduce_bisection_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

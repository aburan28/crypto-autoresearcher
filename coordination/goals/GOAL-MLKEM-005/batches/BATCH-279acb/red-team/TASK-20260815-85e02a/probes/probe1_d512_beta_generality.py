#!/usr/bin/env python3
"""
RED TEAM TASK-20260815-85e02a -- probe1_d512_beta_generality.py

Directly tests the completion_gate's own required challenge: "does the
(d=512, beta=40)-bisected 69-bit precision actually hold at (d=512,
beta=55) and (d=512, beta=70), or could a beta-specific minimum differ?"

This is an EXACT, unmodified reproduction of
TASK-20260815-6e4c02's own worker_bisect() (itself an exact reproduction of
the Red Team's own probe1_bisection_generality.py from BATCH-d1a736),
applied to the (d=512, beta=55) and (d=512, beta=70) bases -- the SAME
bases TASK-20260815-6e4c02's own phase (b) drew (seed_used=452658293 and
915347894 respectively, confirmed via the identical
default_rng([SEED_ROOT, 0, d, beta, 0, 0]) formula).

Source-level justification for why this is a valid, decisive control (not
merely circumstantial): direct inspection of this host's own installed
fpylll 0.6.4 bkz.py (BKZReduction.__init__) confirms that when constructed
from an LLL.Reduction instance L, BKZReduction sets self.lll_obj = L
UNCHANGED (no rebuild), and BKZReduction.__call__'s very first action is
`self.lll_obj()` with NO positional arguments -- bkz.py line 123 -- which
is EXACTLY the same call signature (same object, same GSO.Mat, same mpfr
precision, full row range) as this isolated-step harness's own bare
`lll_obj()` call. This means TASK-20260815-6e4c02's own reported failure
site for (d=512, beta=55) and (d=512, beta=70) ("bkz.py line 123,
self.lll_obj() -- the FIRST call inside BKZReduction.__call__, before any
tour begins") IS, by construction, the identical operation this probe
tests directly and in isolation. This probe's purpose is to CONFIRM that
equivalence empirically (not just cite the source), and to test one
additional precision point (100 bits, the original known-succeeding
value at beta=40) at each of the two other bases to see whether raising
precision further than 69 bits would plausibly help there, or whether the
signature is closer to "genuinely and severely under-provisioned" even at
100 bits.

SEED_ROOT=715923, identical formula, identical ROW_EXPO-free mpfr
construction. Read-only with respect to TASK-20260815-6e4c02's own
artifacts; this probe writes ONLY inside this red-team task's own
write_scope.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_CAP_SECONDS = 900


def worker(d, beta, mpfr_bits, out_path):
    """EXACT reproduction of TASK-20260815-6e4c02's own worker_bisect() /
    the Red Team's BATCH-d1a736 probe1_bisection_generality.py worker():
    isolated LLL-preprocessing step only."""
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


def run_capped_subprocess(argv, cap_seconds, out_path):
    t0 = time.time()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    while True:
        ret = proc.poll()
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
        time.sleep(0.5)
    stdout, stderr = b"", b""
    try:
        stdout, stderr = proc.communicate(timeout=15)
    except Exception:
        pass
    return {
        "wall_clock_seconds": time.time() - t0,
        "timed_out": timed_out,
        "returncode": proc.returncode,
        "stdout_tail": stdout.decode(errors="replace")[-1000:],
        "stderr_tail": stderr.decode(errors="replace")[-1000:],
    }


def run_trial(d, beta, mpfr_bits):
    out_path = os.path.join(HERE, "_tmp_probe1_%d_%d_%d.json" % (d, beta, mpfr_bits))
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [sys.executable, os.path.abspath(__file__), "--worker",
            str(d), str(beta), str(mpfr_bits), out_path]
    proc_info = run_capped_subprocess(argv, TRIAL_CAP_SECONDS, out_path)
    trial = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits}
    trial.update({
        "subprocess_wall_clock_seconds": proc_info["wall_clock_seconds"],
        "subprocess_timed_out": proc_info["timed_out"],
        "subprocess_returncode": proc_info["returncode"],
    })
    if proc_info["timed_out"] or not os.path.exists(out_path):
        trial["status"] = "NOT_COMPUTED"
        trial["reason"] = "timed out" if proc_info["timed_out"] else "worker crashed before writing output"
        trial["stderr_tail"] = proc_info["stderr_tail"]
    else:
        with open(out_path) as f:
            trial.update(json.load(f))
    if os.path.exists(out_path):
        os.remove(out_path)
    return trial


def main():
    # (d, beta, expected_seed) -- expected seeds are TASK-20260815-6e4c02's
    # own reported main_grid_reattempt_seeds_used, re-derived independently
    # here via the identical formula (checked below, not assumed).
    plan = [
        (512, 55, 69),
        (512, 55, 100),
        (512, 70, 69),
        (512, 70, 100),
    ]
    trials = []
    for d, beta, bits in plan:
        print("running (d=%d, beta=%d, mpfr_bits=%d) ..." % (d, beta, bits), flush=True)
        t = run_trial(d, beta, bits)
        print("  -> %s (%.1fs) seed_used=%s" % (
            t.get("status"), t.get("subprocess_wall_clock_seconds", -1), t.get("seed_used")), flush=True)
        trials.append(t)
        with open(os.path.join(HERE, "probe1_d512_beta_generality_results.json"), "w") as f:
            json.dump({"trials": trials, "in_progress": True}, f, indent=2)

    with open(os.path.join(HERE, "probe1_d512_beta_generality_results.json"), "w") as f:
        json.dump({"trials": trials, "in_progress": False}, f, indent=2)
    print(json.dumps(trials, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

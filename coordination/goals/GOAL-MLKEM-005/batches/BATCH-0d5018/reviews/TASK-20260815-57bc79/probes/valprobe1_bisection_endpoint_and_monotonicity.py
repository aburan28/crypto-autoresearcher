#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe1_bisection_endpoint_and_monotonicity.py

Independent re-execution, in a session that is NOT the producer's, of the
minimal spot-check this task's own completion_gate requires:

  "BOTH d=512 BISECTIONS ((d=512,beta=55) AND (d=512,beta=70),
   INDEPENDENTLY) ARE GENUINE 1-BIT-RESOLUTION SEARCHES within [69,100],
   both endpoints re-confirmed as trials, not a 2-point bracket --
   independently spot-checked at minimum by confirming each reported minimum
   itself succeeds and one lower value fails, at BOTH bases."

so: (beta=55, 75 bits) must COMPLETE, (beta=55, 74 bits) must ERROR,
    (beta=70, 73 bits) must COMPLETE, (beta=70, 72 bits) must ERROR.

PLUS one ADVERSARIAL CONTROL the producer did NOT run: a binary search over
precision only returns a true minimum if the success predicate is MONOTONE in
mpfr_bits. The producer's own trial set never tests bits 70, 71, 73 at
beta=55, nor 70, 71 at beta=70, so monotonicity there is assumed, not
measured. This probe tests 71 bits at BOTH bases: under monotonicity both
must ERROR. A COMPLETED at 71 bits would show the reported "minimum" is not a
minimum over the window.

The worker below is an INDEPENDENT TRANSCRIPTION of the construction the
producer declares (and which this validator separately confirmed is
AST-identical between the producer's own worker_bisect(),
probe1_d512_beta_generality.py's worker(), and
TASK-20260815-6e4c02's worker_bisect()): FPLLL.set_random_seed(seed) from
default_rng([715923, 0, d, beta, 0, 0]); IntegerMatrix.random(d, "qary",
k=d//2, q=3329); outer double-precision LLL.reduction(A);
FPLLL.set_precision(N) BEFORE GSO.Mat; GSO.Mat(A, float_type="mpfr") with NO
flags=GSO.ROW_EXPO; M.update_gso(); LLL.Reduction(M, flags=LLL.DEFAULT);
bare lll_obj().

It imports NOTHING from the producer's artifacts and edits nothing outside
this validation task's own write_scope.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_CAP_SECONDS = 1800  # this validator's own cap; the producer used 900s
                          # per trial on a 4-core Linux VM. This host is
                          # shared with a concurrently running red-team
                          # session, so a wider cap is used to avoid
                          # misreading contention as a computational result.

# (d, beta, mpfr_bits, purpose, producer_reported_status)
PLAN = [
    (512, 55, 75, "gate: reported minimum must SUCCEED", "COMPLETED"),
    (512, 55, 74, "gate: one lower value must FAIL", "ERROR"),
    (512, 70, 73, "gate: reported minimum must SUCCEED", "COMPLETED"),
    (512, 70, 72, "gate: one lower value must FAIL", "ERROR"),
    (512, 55, 71, "validator monotonicity control (untested by producer)", "NOT_TESTED_BY_PRODUCER"),
    (512, 70, 71, "validator monotonicity control (untested by producer)", "NOT_TESTED_BY_PRODUCER"),
]


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


def main():
    """Launches every planned trial CONCURRENTLY, one subprocess each (fplll is
    single-threaded), and enforces TRIAL_CAP_SECONDS as a hard wall-clock kill
    per trial."""
    t_start = time.time()
    procs = []
    for (d, beta, bits, purpose, expected) in PLAN:
        out_path = os.path.join(HERE, "_tmp_valprobe1_%d_%d_%d.json" % (d, beta, bits))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker",
                str(d), str(beta), str(bits), out_path]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append({"d": d, "beta": beta, "mpfr_bits": bits, "purpose": purpose,
                      "producer_reported_status": expected, "proc": p,
                      "out_path": out_path, "t0": time.time()})
        print("launched (d=%d, beta=%d, bits=%d) pid=%d" % (d, beta, bits, p.pid), flush=True)

    trials = []
    remaining = list(procs)
    while remaining:
        time.sleep(2.0)
        still = []
        for e in remaining:
            ret = e["proc"].poll()
            if ret is None and (time.time() - e["t0"]) < TRIAL_CAP_SECONDS:
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
            trial = {
                "d": e["d"], "beta": e["beta"], "mpfr_bits": e["mpfr_bits"],
                "purpose": e["purpose"],
                "producer_reported_status": e["producer_reported_status"],
                "subprocess_wall_clock_seconds": time.time() - e["t0"],
                "subprocess_timed_out": timed_out,
                "subprocess_returncode": e["proc"].returncode,
            }
            if timed_out or not os.path.exists(e["out_path"]):
                trial["status"] = "NOT_COMPUTED"
                trial["reason"] = ("trial exceeded this validator's own %ds cap"
                                   % TRIAL_CAP_SECONDS) if timed_out else \
                                  "worker crashed before writing output"
                trial["stderr_tail"] = se.decode(errors="replace")[-2000:]
            else:
                with open(e["out_path"]) as f:
                    trial.update(json.load(f))
                os.remove(e["out_path"])
            print("  -> (d=%d, beta=%d, bits=%d) %s (%.1fs) seed_used=%s" % (
                trial["d"], trial["beta"], trial["mpfr_bits"], trial.get("status"),
                trial["subprocess_wall_clock_seconds"], trial.get("seed_used")), flush=True)
            trials.append(trial)
        remaining = still

    trials.sort(key=lambda t: (t["beta"], t["mpfr_bits"]))
    agreement = []
    for t in trials:
        exp = t["producer_reported_status"]
        if exp == "NOT_TESTED_BY_PRODUCER":
            agreement.append({"cell": [t["beta"], t["mpfr_bits"]],
                              "kind": "monotonicity_control",
                              "validator_status": t.get("status"),
                              "monotonicity_consistent": t.get("status") == "ERROR"})
        else:
            agreement.append({"cell": [t["beta"], t["mpfr_bits"]],
                              "kind": "gate_reproduction",
                              "producer_status": exp,
                              "validator_status": t.get("status"),
                              "agrees": t.get("status") == exp})

    out = {
        "probe": "valprobe1_bisection_endpoint_and_monotonicity",
        "task_id": "TASK-20260815-57bc79",
        "seed_root": SEED_ROOT,
        "trial_cap_seconds": TRIAL_CAP_SECONDS,
        "concurrency": "all %d trials launched concurrently, one subprocess each" % len(PLAN),
        "expected_seeds_independently_recomputed": {
            "beta55": int(np.random.default_rng([SEED_ROOT, 0, 512, 55, 0, 0]).integers(0, 2 ** 31 - 1)),
            "beta70": int(np.random.default_rng([SEED_ROOT, 0, 512, 70, 0, 0]).integers(0, 2 ** 31 - 1)),
        },
        "trials": trials,
        "agreement": agreement,
        "total_wall_clock_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "valprobe1_bisection_endpoint_and_monotonicity_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"agreement": agreement,
                      "total_wall_clock_seconds": out["total_wall_clock_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

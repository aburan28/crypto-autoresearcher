#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe3_draw_variation_control.py

A CONTROL THE PRODUCER DID NOT RUN, required by docs/inventor-protocol.md
section 3 ("controls before belief"): a reported difference is an artifact
until the same measurement has been made against an object of the same shape
that should NOT show it.

THE REPORTED DIFFERENCE. TASK-20260815-f14d3c reports minimum adequate
isolated-LLL-step precisions of 75 bits at (d=512, beta=55) and 73 bits at
(d=512, beta=70), and writeup.md line 120-123 states "The two minima differ
from each other (75 vs 73 bits)". Both figures rest on exactly ONE lattice
draw per cell: the producer's seed formula fixes draw_index = 0 for both, so
each cell is n=1 with no within-cell replicate and no variance estimate.

THE CONTROL. Take the SAME (d=512, beta=55) cell and the SAME declared seed
formula default_rng([715923, stage_index, d, beta, arm_index, draw_index]),
and move ONLY the free draw_index from 0 to 1. Everything else -- SEED_ROOT,
stage_index, d, beta, arm_index, construction, precision window -- is held
fixed. This is not a new parameter and not a deviation: draw_index is the
formula's own draw coordinate.

WHAT IT CAN AND CANNOT SHOW.
  - If draw 1's threshold at beta=55 is also 75 bits, the 2-bit 55-vs-70 gap
    survives this one control (it is NOT thereby established as a beta
    effect; n=2 per cell is still tiny).
  - If draw 1's threshold at beta=55 differs from 75 by as much as the
    reported 55-vs-70 gap, then draw-to-draw variation at FIXED beta is
    already of the same size as the cross-beta difference, and the 75-vs-73
    gap cannot be read as a property of beta at all.
  - It says NOTHING about the full BKZ tour (KN-FIND-f54a82), nothing about
    ML-KEM, and nothing about H-MLKEM-7d9bcc. Claim tier TOY.

Construction is the same independent transcription used in
valprobe1_bisection_endpoint_and_monotonicity.py. Writes only inside this
validation task's own write_scope.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

SEED_ROOT = 715923
HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL_CAP_SECONDS = 1800

D = 512
BETA = 55
DRAW_INDEX = 1                      # the ONLY coordinate moved vs the producer
PRODUCER_DRAW_INDEX = 0
BITS_PLAN = [73, 74, 75, 76, 77]    # brackets the producer's own 75-bit result


def seed_for(d, beta, draw_index):
    return int(np.random.default_rng(
        [SEED_ROOT, 0, d, beta, 0, draw_index]).integers(0, 2 ** 31 - 1))


def worker(d, beta, mpfr_bits, draw_index, out_path):
    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits,
              "draw_index": draw_index, "level": "isolated_lll_step"}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL, GSO

        seed = seed_for(d, beta, draw_index)
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
    t_start = time.time()
    procs = []
    for bits in BITS_PLAN:
        out_path = os.path.join(HERE, "_tmp_valprobe3_%d_%d_%d_%d.json"
                                % (D, BETA, DRAW_INDEX, bits))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker",
                str(D), str(BETA), str(bits), str(DRAW_INDEX), out_path]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append({"mpfr_bits": bits, "proc": p, "out_path": out_path,
                      "t0": time.time()})
        print("launched (d=%d, beta=%d, draw=%d, bits=%d) pid=%d"
              % (D, BETA, DRAW_INDEX, bits, p.pid), flush=True)

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
            trial = {"mpfr_bits": e["mpfr_bits"],
                     "subprocess_wall_clock_seconds": time.time() - e["t0"],
                     "subprocess_timed_out": timed_out,
                     "subprocess_returncode": e["proc"].returncode}
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
            print("  -> bits=%d %s (%.1fs) seed_used=%s"
                  % (trial["mpfr_bits"], trial.get("status"),
                     trial["subprocess_wall_clock_seconds"],
                     trial.get("seed_used")), flush=True)
            trials.append(trial)
        remaining = still

    trials.sort(key=lambda t: t["mpfr_bits"])
    st = {t["mpfr_bits"]: t.get("status") for t in trials}
    threshold = None
    for b in BITS_PLAN:
        if st.get(b) == "COMPLETED":
            threshold = b
            break
    if threshold is not None and any(st.get(b) == "COMPLETED" and b < threshold
                                     for b in BITS_PLAN):
        threshold = None  # non-monotone; refuse to name one

    out = {
        "probe": "valprobe3_draw_variation_control",
        "task_id": "TASK-20260815-57bc79",
        "purpose": ("control on the producer's 75-vs-73-bit cross-beta difference: "
                    "how much does the SAME cell's own threshold move when only the "
                    "seed formula's free draw_index moves 0 -> 1?"),
        "d": D, "beta": BETA,
        "producer_draw_index": PRODUCER_DRAW_INDEX,
        "producer_seed_used": seed_for(D, BETA, PRODUCER_DRAW_INDEX),
        "producer_reported_minimum_bits_at_this_cell": 75,
        "validator_draw_index": DRAW_INDEX,
        "validator_seed_used": seed_for(D, BETA, DRAW_INDEX),
        "bits_tested": BITS_PLAN,
        "status_by_bits": {str(k): v for k, v in sorted(st.items())},
        "lowest_tested_bits_that_succeeded": threshold,
        "threshold_bracketed_within_tested_range": threshold is not None and threshold != BITS_PLAN[0],
        "interpretation_bounds": (
            "This probe tests ONE alternative draw, so it gives n=2 at this cell, "
            "not a distribution. It CANNOT establish a beta effect and does not try; "
            "it can only show whether draw-to-draw movement at FIXED beta is already "
            "comparable to the reported cross-beta gap. Isolated LLL step only -- "
            "says nothing about the full BKZ tour (KN-FIND-f54a82). Claim tier TOY."
        ),
        "trials": trials,
        "total_wall_clock_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "valprobe3_draw_variation_control_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("producer_seed_used", "validator_seed_used", "status_by_bits",
                       "lowest_tested_bits_that_succeeded", "total_wall_clock_seconds")},
                     indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
               int(sys.argv[5]), sys.argv[6])
    else:
        main()

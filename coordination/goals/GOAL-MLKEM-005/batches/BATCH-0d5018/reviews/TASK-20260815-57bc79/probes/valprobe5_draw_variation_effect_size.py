#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe5_draw_variation_effect_size.py

FOLLOW-UP TO valprobe3, WHICH RETURNED A POSITIVE CONTROL RESULT.

valprobe3 moved ONLY the seed formula's free draw_index (0 -> 1) at the SAME
(d=512, beta=55) cell and found 73, 74, 75, 76 and 77 bits ALL COMPLETED --
so draw 1's own threshold is <= 73 bits while draw 0's (the producer's) is
exactly 75. Draw-to-draw movement at FIXED beta is therefore already >= 2
bits, which is the entire size of the 75-vs-73 difference the producer
reports BETWEEN beta=55 and beta=70.

valprobe3 bounded that gap but did not measure it. This probe measures it:

  (a) beta=55, draw 1, bits 69/70/71/72 -- locates draw 1's own threshold, so
      the effect size (draw-0 threshold minus draw-1 threshold) becomes a
      number rather than an inequality;
  (b) beta=70, draw 1, bits 69 and 73 -- asks whether the same draw
      sensitivity REPLICATES at the other cell, rather than being one odd
      draw at one cell. 69 bits is the value BOTH the Red Team's CTRL-1 and
      the producer record as FAILING at draw 0 at this cell; if it succeeds
      at draw 1, the "69 bits fails here" fact is per-draw, not per-cell.

WHAT THIS IS AND IS NOT. It is a null-object control in the sense of
docs/inventor-protocol.md section 3: the same measurement, on an object of
the same shape, under a change that should not matter if the reported
quantity is a property of the (d, beta) cell. It is NOT a claim that the
producer erred -- the producer used each drawn basis's OWN threshold for that
SAME basis's own reattempt, which is exactly right, and this control
reinforces that choice. It bears only on how the two reported numbers may be
GENERALIZED. Isolated LLL step only; says nothing about the full BKZ tour
(KN-FIND-f54a82), nothing about ML-KEM. Claim tier TOY.

Writes only inside this validation task's own write_scope.
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
DRAW_INDEX = 1
PRODUCER_DRAW_INDEX = 0
PRODUCER_THRESHOLD = {55: 75, 70: 73}

# (beta, bits, why)
PLAN = [
    (55, 69, "locate draw-1 threshold; 69 is CTRL-1's known-failing value at draw 0"),
    (55, 70, "locate draw-1 threshold"),
    (55, 71, "locate draw-1 threshold; ERROR at draw 0 (valprobe1)"),
    (55, 72, "locate draw-1 threshold; ERROR at draw 0 (producer)"),
    (70, 69, "replication check: does the 'fails at 69' fact survive a draw change?"),
    (70, 73, "replication check: draw 0's own reported minimum at this cell"),
]


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
    for (beta, bits, why) in PLAN:
        out_path = os.path.join(HERE, "_tmp_valprobe5_%d_%d_%d_%d.json"
                                % (D, beta, DRAW_INDEX, bits))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker",
                str(D), str(beta), str(bits), str(DRAW_INDEX), out_path]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append({"beta": beta, "mpfr_bits": bits, "why": why, "proc": p,
                      "out_path": out_path, "t0": time.time()})
        print("launched (d=%d, beta=%d, draw=%d, bits=%d) pid=%d"
              % (D, beta, DRAW_INDEX, bits, p.pid), flush=True)

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
            trial = {"beta": e["beta"], "mpfr_bits": e["mpfr_bits"], "why": e["why"],
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
            print("  -> (beta=%d, bits=%d) %s (%.1fs) seed_used=%s"
                  % (trial["beta"], trial["mpfr_bits"], trial.get("status"),
                     trial["subprocess_wall_clock_seconds"], trial.get("seed_used")),
                  flush=True)
            trials.append(trial)
        remaining = still

    trials.sort(key=lambda t: (t["beta"], t["mpfr_bits"]))

    # beta=55 draw-1 threshold, using this probe's 69-72 plus valprobe3's 73-77
    b55 = {t["mpfr_bits"]: t.get("status") for t in trials if t["beta"] == 55}
    b55_from_probe3 = {73: "COMPLETED", 74: "COMPLETED", 75: "COMPLETED",
                       76: "COMPLETED", 77: "COMPLETED"}
    b55_all = dict(b55)
    b55_all.update(b55_from_probe3)
    b55_threshold = None
    for b in sorted(b55_all):
        if b55_all[b] == "COMPLETED":
            b55_threshold = b
            break
    monotone_55 = all(
        b55_all[b] == "ERROR" for b in sorted(b55_all) if b55_threshold is not None and b < b55_threshold
    )
    b70 = {t["mpfr_bits"]: t.get("status") for t in trials if t["beta"] == 70}

    effect = None
    if b55_threshold is not None:
        effect = PRODUCER_THRESHOLD[55] - b55_threshold

    out = {
        "probe": "valprobe5_draw_variation_effect_size",
        "task_id": "TASK-20260815-57bc79",
        "d": D,
        "producer_draw_index": PRODUCER_DRAW_INDEX,
        "validator_draw_index": DRAW_INDEX,
        "seeds": {
            "beta55_draw0_producer": seed_for(D, 55, 0),
            "beta55_draw1_validator": seed_for(D, 55, 1),
            "beta70_draw0_producer": seed_for(D, 70, 0),
            "beta70_draw1_validator": seed_for(D, 70, 1),
        },
        "beta55_draw1_status_by_bits_this_probe": {str(k): v for k, v in sorted(b55.items())},
        "beta55_draw1_status_by_bits_merged_with_valprobe3": {
            str(k): v for k, v in sorted(b55_all.items())},
        "beta55_draw1_threshold_bits": b55_threshold,
        "beta55_draw1_threshold_monotone_over_tested_points": monotone_55,
        "beta55_draw0_threshold_bits_producer": PRODUCER_THRESHOLD[55],
        "beta55_draw_effect_size_bits": effect,
        "beta70_draw1_status_by_bits": {str(k): v for k, v in sorted(b70.items())},
        "beta70_draw0_69bit_status_producer_and_ctrl1": "ERROR",
        "producer_cross_beta_gap_bits": PRODUCER_THRESHOLD[55] - PRODUCER_THRESHOLD[70],
        "comparison_statement": (
            "Compare beta55_draw_effect_size_bits (movement at FIXED beta from a single "
            "draw change) against producer_cross_beta_gap_bits (the 75-vs-73 difference "
            "the producer reports BETWEEN beta=55 and beta=70). If the former is >= the "
            "latter, the reported cross-beta difference cannot be attributed to beta."
        ),
        "interpretation_bounds": (
            "n=2 draws at beta=55 and n=2 at beta=70. This is a control, not a "
            "distribution: it can show that a difference is NOT attributable to beta, "
            "and cannot show what the threshold distribution is. Isolated LLL step only. "
            "Claim tier TOY. No statement about ML-KEM, H-MLKEM-7d9bcc, C1 or C2."
        ),
        "trials": trials,
        "total_wall_clock_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "valprobe5_draw_variation_effect_size_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("beta55_draw1_status_by_bits_merged_with_valprobe3",
                       "beta55_draw1_threshold_bits", "beta55_draw_effect_size_bits",
                       "beta70_draw1_status_by_bits", "producer_cross_beta_gap_bits",
                       "total_wall_clock_seconds")}, indent=2), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
               int(sys.argv[5]), sys.argv[6])
    else:
        main()

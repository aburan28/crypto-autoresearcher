#!/usr/bin/env python3
"""
VALIDATOR TASK-20260815-57bc79 -- valprobe4_endpoint_reconfirmation.py

Closes the remaining half of this task's own completion_gate item

  "BOTH d=512 BISECTIONS ... ARE GENUINE 1-BIT-RESOLUTION SEARCHES within
   [69,100], both endpoints re-confirmed as trials, not a 2-point bracket"

FIRST-HAND rather than by citation. valprobe1 already re-ran the INTERIOR
(the reported minimum and one lower value at each basis, plus a monotonicity
control). This probe re-runs the two WINDOW ENDPOINTS at each basis:

  (beta=55, 69 bits) and (beta=70, 69 bits)  -- must ERROR   (lo_known_failing)
  (beta=55, 100 bits) and (beta=70, 100 bits) -- must COMPLETE (hi_known_succeeding)

Without this, the endpoint half of the gate would rest on two records this
validator did not produce (the producer's own trials, and the Red Team's
committed CTRL-1 probe1_d512_beta_generality_results.json). Those agree with
each other, but agreement between two records a validator only read is not the
same as a measurement the validator made. This probe makes it.

The producer's own bisection code treats these two endpoints as the trigger
for endpoint_reproduction_ok (stage0_d512_beta5570_...py lines 362-371:
lo must be ERROR, hi must be COMPLETED, and BOTH must carry the expected
seed). This probe checks exactly that predicate independently.

Same independent transcription of the construction as valprobe1. Writes only
inside this validation task's own write_scope.
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

# (d, beta, bits, expected_seed, producer_reported_status, role_in_window)
PLAN = [
    (512, 55, 69, 452658293, "ERROR", "lo_known_failing"),
    (512, 55, 100, 452658293, "COMPLETED", "hi_known_succeeding"),
    (512, 70, 69, 915347894, "ERROR", "lo_known_failing"),
    (512, 70, 100, 915347894, "COMPLETED", "hi_known_succeeding"),
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
    t_start = time.time()
    procs = []
    for (d, beta, bits, exp_seed, exp_status, role) in PLAN:
        out_path = os.path.join(HERE, "_tmp_valprobe4_%d_%d_%d.json" % (d, beta, bits))
        if os.path.exists(out_path):
            os.remove(out_path)
        argv = [sys.executable, os.path.abspath(__file__), "--worker",
                str(d), str(beta), str(bits), out_path]
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procs.append({"d": d, "beta": beta, "mpfr_bits": bits,
                      "expected_seed": exp_seed,
                      "producer_reported_status": exp_status,
                      "role_in_window": role,
                      "proc": p, "out_path": out_path, "t0": time.time()})
        print("launched (d=%d, beta=%d, bits=%d, %s) pid=%d"
              % (d, beta, bits, role, p.pid), flush=True)

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
            trial = {"d": e["d"], "beta": e["beta"], "mpfr_bits": e["mpfr_bits"],
                     "role_in_window": e["role_in_window"],
                     "expected_seed": e["expected_seed"],
                     "producer_reported_status": e["producer_reported_status"],
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
            trial["seed_matches_expected"] = trial.get("seed_used") == e["expected_seed"]
            trial["agrees_with_producer"] = trial.get("status") == e["producer_reported_status"]
            print("  -> (beta=%d, bits=%d) %s (%.1fs) seed_ok=%s agrees=%s"
                  % (trial["beta"], trial["mpfr_bits"], trial.get("status"),
                     trial["subprocess_wall_clock_seconds"],
                     trial["seed_matches_expected"], trial["agrees_with_producer"]),
                  flush=True)
            trials.append(trial)
        remaining = still

    trials.sort(key=lambda t: (t["beta"], t["mpfr_bits"]))
    per_basis = {}
    for beta in (55, 70):
        lo = [t for t in trials if t["beta"] == beta and t["mpfr_bits"] == 69]
        hi = [t for t in trials if t["beta"] == beta and t["mpfr_bits"] == 100]
        lo, hi = (lo[0] if lo else None), (hi[0] if hi else None)
        per_basis[str(beta)] = {
            "lo_69_status": lo.get("status") if lo else None,
            "hi_100_status": hi.get("status") if hi else None,
            "endpoint_reproduction_ok_recomputed_by_validator": bool(
                lo and hi
                and lo.get("status") == "ERROR"
                and hi.get("status") == "COMPLETED"
                and lo.get("seed_used") == lo["expected_seed"]
                and hi.get("seed_used") == hi["expected_seed"]
            ),
            "producer_reported_endpoint_reproduction_ok": True,
        }

    out = {
        "probe": "valprobe4_endpoint_reconfirmation",
        "task_id": "TASK-20260815-57bc79",
        "seed_root": SEED_ROOT,
        "predicate_recomputed": (
            "endpoint_reproduction_ok := (lo status == ERROR) and (hi status == COMPLETED) "
            "and (lo seed == expected) and (hi seed == expected) -- the same predicate the "
            "producer's own bisect_precision_d512b() computes at lines 362-371."
        ),
        "per_basis": per_basis,
        "trials": trials,
        "all_four_agree_with_producer": all(t["agrees_with_producer"] for t in trials),
        "all_four_seeds_match": all(t["seed_matches_expected"] for t in trials),
        "total_wall_clock_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "valprobe4_endpoint_reconfirmation_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("per_basis", "all_four_agree_with_producer",
                       "all_four_seeds_match", "total_wall_clock_seconds")}, indent=2),
          flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        main()

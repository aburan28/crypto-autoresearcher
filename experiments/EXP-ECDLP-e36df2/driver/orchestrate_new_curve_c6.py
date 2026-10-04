"""EXP-ECDLP-e36df2 v2 (PA-ECDLP-e36df2-v1-to-v2 / TASK-20260921-9b17e4):
run the 4 (curve, prime) instances of the new, non-engineered curve c6
(frozen_new_curve_c6_seed20260921.json) through the EXISTING v1 driver
compute path (instance_runner.run_curve, harness.runner.run_wrapped)
UNMODIFIED, at mu0_target=20, producing RUN-ECDLP-e36df2-029..032.

This is a NEW top-level script, not a modification of orchestrate.py.
orchestrate.py itself is untouched; it hardcodes SEED=20260905 for the six
v1 curves and is not reusable as-is for a new curve under a different seed.
The actual per-m/per-prime computation (instance_runner.py, sections.py,
fastseries.py, frozen_ref.py) is imported and called exactly as orchestrate.py
calls it -- same functions, same call shape, same statistic definitions --
only the top-level seed/curve list differs, as required by the amendment.

Results are pooled ONLY into pooled-summary-new-curve-c6.json (a separate
script, pooled_summary_new_curve_c6.py); pooled-summary.json is never
touched.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, REPO_ROOT)

import instance_runner  # noqa: E402
from harness import runner as harness_runner  # noqa: E402

SEED = 20260921
CURVE_IDX = 6
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_ROOT = os.path.join(THIS_DIR, "..")
EXP_ID = "EXP-ECDLP-e36df2"
EXP_AREA = "ECDLP-e36df2"

MU0_TARGET = 20
RUN_SUFFIXES = ["029", "030", "031", "032"]


def load_curve():
    with open(os.path.join(EXP_ROOT, "frozen_new_curve_c6_seed20260921.json")) as f:
        return json.load(f)


def write_instance_run(result, flagged_x_curve, flagged_y_curve, run_suffix,
                        mu0_target):
    p, A, B = result["p"], result["A"], result["B"]
    curve_id = harness_runner.curve_id(p, A, B, field_bits=p.bit_length())

    metrics = {
        "s_x_n_agree": result["s_x"]["n_agree"],
        "s_x_n_total_after_exclusion": result["s_x"]["n_total_after_exclusion"],
        "s_x_mu_0_i": result["s_x"]["mu_0_i"],
        "s_x_chi_square_statistic": result["s_x"]["chi_square"]["statistic"],
        "s_y_n_agree": result["s_y"]["n_agree"],
        "s_y_n_total_after_exclusion": result["s_y"]["n_total_after_exclusion"],
        "s_y_mu_0_i": result["s_y"]["mu_0_i"],
        "s_y_chi_square_statistic": result["s_y"]["chi_square"]["statistic"],
        "s_rand_n_agree": result["s_rand"]["n_agree"],
        "s_rand_n_total_after_exclusion": result["s_rand"]["n_total_after_exclusion"],
        "s_rand_mu_0_i": result["s_rand"]["mu_0_i"],
        "n_excluded_x": result["s_x"]["n_excluded_degenerate"],
        "n_excluded_y": result["s_y"]["n_excluded_degenerate"],
    }

    flagged_x_here = {m: pat for m, pat in flagged_x_curve.items()
                       if m <= result["N_i"] + 1}
    flagged_y_here = {m: pat for m, pat in flagged_y_curve.items()
                       if m <= result["N_i"] + 1}

    raw = dict(result)
    raw["mu0_target"] = mu0_target
    raw["is_positive_control"] = False
    raw["is_sensitivity_check"] = False
    raw["is_new_curve_c6_v2"] = True
    raw["protocol_amendment"] = "PA-ECDLP-e36df2-v1-to-v2"
    raw["flagged_x_degenerate_m"] = flagged_x_here
    raw["flagged_y_degenerate_m"] = flagged_y_here
    raw["cross_prime_screen_note"] = (
        "flagged_*_degenerate_m is CURVE-LEVEL (computed jointly across all "
        "of this curve's tested primes); the same census (restricted to "
        "m <= this instance's own N_i+1) is attached to every prime "
        "instance of the curve, per specification.yaml Stage 2 (reused "
        "unmodified for this new curve, per PA-ECDLP-e36df2-v1-to-v2).")

    result_obj = harness_runner.RunResult(
        run_suffix=run_suffix,
        curve_id=curve_id,
        seed=SEED,
        parameters={"curve_idx": result["curve_idx"], "p": p, "A": A, "B": B,
                    "x0": result["x0"], "y0": result["y0"], "n": result["n"],
                    "N_i": result["N_i"], "Kreq": result["Kreq"],
                    "mu0_target": mu0_target,
                    "is_positive_control": False,
                    "is_sensitivity_check": False,
                    "is_new_curve_c6_v2": True},
        metrics=metrics,
        certificate={"kind": "none"},
        valid=True,
        raw=raw,
    )
    command = (f"python3 orchestrate_new_curve_c6.py  # curve_idx={result['curve_idx']} "
               f"p={p} mu0_target={mu0_target} seed={SEED}")
    run_id = harness_runner.run_wrapped(
        EXP_ID, EXP_AREA, lambda: result_obj,
        status="completed_valid", command=command)
    return run_id


def run_all():
    curve = load_curve()
    assert curve["idx"] == CURVE_IDX
    assert curve["seed"] == SEED
    assert curve["engineered"] is False

    all_results = []
    run_ids = []
    t0 = time.time()

    print(f"=== curve idx={curve['idx']} (new, non-engineered, v2) "
          f"A={curve['A']} B={curve['B']} x0={curve['x0']} y0={curve['y0']} "
          f"primes={[pe['p'] for pe in curve['primes']]} ===", flush=True)
    results, flagged_x, flagged_y = instance_runner.run_curve(
        curve["idx"], curve["A"], curve["B"], curve["x0"], curve["y0"],
        curve["primes"], SEED, mu0_target=MU0_TARGET,
        progress_every=20000)

    for r, run_suffix in zip(results, RUN_SUFFIXES):
        run_id = write_instance_run(r, flagged_x, flagged_y,
                                     run_suffix=run_suffix,
                                     mu0_target=MU0_TARGET)
        run_ids.append(run_id)
        all_results.append({"result": r, "flagged_x": flagged_x,
                             "flagged_y": flagged_y, "run_id": run_id})
    print(f"    curve idx={curve['idx']} done, elapsed total "
          f"{time.time()-t0:.1f}s", flush=True)

    manifest_summary = {
        "run_ids": run_ids,
        "curve_idx": CURVE_IDX,
        "seed": SEED,
        "total_wall_seconds": time.time() - t0,
        "protocol_amendment": "PA-ECDLP-e36df2-v1-to-v2",
    }
    with open(os.path.join(EXP_ROOT, "orchestrate_manifest_summary_new_curve_c6.json"), "w") as f:
        json.dump(manifest_summary, f, indent=2, default=str)

    return all_results


if __name__ == "__main__":
    run_all()

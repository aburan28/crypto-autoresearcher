"""Top-level orchestration for EXP-ECDLP-e36df2 Stage 2/3: runs all 24
(curve, prime) instances (5 original curves x 4 primes + 1 engineered
positive-control curve x 4 primes), writes one immutable run record per
instance via harness.runner, then the pooled-summary.json required by
specification.yaml.

Must be run AFTER stage0_regression.py has passed (0 mismatches) and
positive_control.py has frozen the engineered curve -- this script does not
re-check Stage 0's gate itself; run_gate.py (the entry point actually
invoked) enforces the ordering.
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

SEED = 20260905
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_ROOT = os.path.join(THIS_DIR, "..")
EXP_ID = "EXP-ECDLP-e36df2"
EXP_AREA = "ECDLP-e36df2"

MU0_TARGET_MAIN = 20
MU0_TARGET_SENSITIVITY = 40
SENSITIVITY_CURVE_IDX = 1  # smallest-prime curve (cheapest), per design_note.md


def load_all_curves():
    with open(os.path.join(EXP_ROOT, "..", "EXP-ECDLP-a26bde",
                            "frozen_curves_and_primes.json")) as f:
        original = json.load(f)
    with open(os.path.join(EXP_ROOT, "frozen_positive_control_curve.json")) as f:
        pc = json.load(f)
    curves = list(original["curves"])
    curves.append({"idx": pc["idx"], "A": pc["A"], "B": pc["B"],
                    "x0": pc["x0"], "y0": pc["y0"], "primes": pc["primes"],
                    "positive_control": True})
    return curves


def write_instance_run(result, flagged_x_curve, flagged_y_curve, run_suffix,
                        mu0_target, is_positive_control, is_sensitivity=False):
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
    raw["is_positive_control"] = is_positive_control
    raw["is_sensitivity_check"] = is_sensitivity
    raw["flagged_x_degenerate_m"] = flagged_x_here
    raw["flagged_y_degenerate_m"] = flagged_y_here
    raw["cross_prime_screen_note"] = (
        "flagged_*_degenerate_m is CURVE-LEVEL (computed jointly across all "
        "of this curve's tested primes); the same census (restricted to "
        "m <= this instance's own N_i+1) is attached to every prime "
        "instance of the curve, per specification.yaml Stage 2.")

    result_obj = harness_runner.RunResult(
        run_suffix=run_suffix,
        curve_id=curve_id,
        seed=SEED,
        parameters={"curve_idx": result["curve_idx"], "p": p, "A": A, "B": B,
                    "x0": result["x0"], "y0": result["y0"], "n": result["n"],
                    "N_i": result["N_i"], "Kreq": result["Kreq"],
                    "mu0_target": mu0_target,
                    "is_positive_control": is_positive_control,
                    "is_sensitivity_check": is_sensitivity},
        metrics=metrics,
        certificate={"kind": "none"},
        valid=True,
        raw=raw,
    )
    command = (f"python3 orchestrate.py  # curve_idx={result['curve_idx']} "
               f"p={p} mu0_target={mu0_target}")
    run_id = harness_runner.run_wrapped(
        EXP_ID, EXP_AREA, lambda: result_obj,
        status="completed_valid", command=command)
    return run_id


def run_all():
    curves = load_all_curves()
    all_results = []
    run_ids = []
    t0 = time.time()

    for curve in curves:
        is_pc = curve.get("positive_control", False)
        print(f"=== curve idx={curve['idx']} (positive_control={is_pc}) "
              f"A={curve['A']} B={curve['B']} x0={curve['x0']} y0={curve['y0']} "
              f"primes={[pe['p'] for pe in curve['primes']]} ===", flush=True)
        results, flagged_x, flagged_y = instance_runner.run_curve(
            curve["idx"], curve["A"], curve["B"], curve["x0"], curve["y0"],
            curve["primes"], SEED, mu0_target=MU0_TARGET_MAIN,
            progress_every=20000)
        for r in results:
            run_id = write_instance_run(r, flagged_x, flagged_y,
                                         run_suffix=f"{len(run_ids)+1:03d}",
                                         mu0_target=MU0_TARGET_MAIN,
                                         is_positive_control=is_pc)
            run_ids.append(run_id)
            all_results.append({"result": r, "flagged_x": flagged_x,
                                 "flagged_y": flagged_y, "run_id": run_id,
                                 "is_positive_control": is_pc})
        print(f"    curve idx={curve['idx']} done, elapsed total "
              f"{time.time()-t0:.1f}s", flush=True)

    # Sensitivity check: same statistic at mu0_target=40 on a subset of
    # instances (the smallest-prime curve, cheapest to redo in full),
    # per specification.yaml tail_checks.
    sens_curve = next(c for c in curves if c["idx"] == SENSITIVITY_CURVE_IDX)
    print(f"=== sensitivity check: curve idx={SENSITIVITY_CURVE_IDX} at "
          f"mu0_target={MU0_TARGET_SENSITIVITY} ===", flush=True)
    sens_results, sens_fx, sens_fy = instance_runner.run_curve(
        sens_curve["idx"], sens_curve["A"], sens_curve["B"], sens_curve["x0"],
        sens_curve["y0"], sens_curve["primes"], SEED,
        mu0_target=MU0_TARGET_SENSITIVITY, progress_every=20000)
    sens_run_ids = []
    for r in sens_results:
        run_id = write_instance_run(r, sens_fx, sens_fy,
                                     run_suffix=f"{len(run_ids)+len(sens_run_ids)+1:03d}",
                                     mu0_target=MU0_TARGET_SENSITIVITY,
                                     is_positive_control=False,
                                     is_sensitivity=True)
        sens_run_ids.append(run_id)

    manifest_summary = {
        "run_ids": run_ids, "sensitivity_run_ids": sens_run_ids,
        "total_wall_seconds": time.time() - t0,
    }
    with open(os.path.join(EXP_ROOT, "orchestrate_manifest_summary.json"), "w") as f:
        json.dump(manifest_summary, f, indent=2, default=str)

    return all_results, {"results": sens_results, "flagged_x": sens_fx,
                          "flagged_y": sens_fy}


if __name__ == "__main__":
    run_all()

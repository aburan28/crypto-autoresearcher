"""RUN-ECDLP-e962f6-001: the quadrature table (Stage 1, deterministic, no seed).

Solves the root equation
    2 x*^{-1/2} e^{-x*/2} - sqrt(2 pi) erfc(sqrt(x*/2)) = a sqrt(2 pi)
for x* at a in {1, 1/2, 1/4, 1/8} and on the fine grid a in [0.05, 2] step
0.001; computes C_max(a) = erfc(sqrt(x*/2)) and sqrt(a)/C_max(a).

Method (frozen contract): bisection bracketing plus Newton refinement on the
root equation; erfc from the Python standard library function math.erfc.

Tolerances (frozen contract):
  Q1: reproduce the committed anchor values (specification
      inputs.residual_reread.anchor_values) to within 5e-5 at all four a.
  Q2: the assembly minimum of sqrt(a)/C_max(a) on the fine grid lies at
      a in [0.2, 0.25] and its value is within 0.01 of 1.28.
  Q3: the baseline-embedding values 0.423 (a_m = 1, the (B1) unselected law)
      and 0.66 (a = 1, the (B2) ceiling) reproduced to within 5e-3.

Observations only; no interpretation.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402
import runcommon as RC  # noqa: E402

A_FOUR = [1.0, 0.5, 0.25, 0.125]
ANCHOR = {
    0.125: {"x_star": 1.2085522833979216, "c_max": 0.27161902810059757},
    0.25: {"x_star": 0.7423409681771704, "c_max": 0.3889120129663709},
    0.5: {"x_star": 0.4045307067767451, "c_max": 0.5247586384598776},
    1.0: {"x_star": 0.1903808702719756, "c_max": 0.6625998114129124},
}
ANCHOR_SOURCE = ("RUN-ECDLP-869870-011-N24-s1 global_oracle.model (all four a values); "
                 "the a = 1/4 pair cross-checked against RUN-ECDLP-612fb1-002 "
                 "basins.C_max_model / basins.x_star_model (identical values)")
Q1_TOL = 5e-5
Q2_A_LO, Q2_A_HI = 0.2, 0.25
Q2_VAL_TOL = 0.01
Q2_VAL_TARGET = 1.28
Q3_TOL = 5e-3
GRID_LO, GRID_HI, GRID_STEP = 0.05, 2.0, 0.001


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (int, float, str, bool)) or o is None:
        return o
    return str(o)


def main():
    t0 = time.time()
    # --- the four anchor a values -----------------------------------------
    four = []
    for a in A_FOUR:
        xs = I.solve_xstar(a)
        cm = math.erfc(math.sqrt(xs / 2.0))
        four.append({"a": a, "x_star": xs, "c_max": cm, "sqrt_a_over_c_max": math.sqrt(a) / cm})

    # --- anchor reproduction table (Q1) ------------------------------------
    repro = []
    q1_ok = True
    for rec in four:
        a = rec["a"]
        ref = ANCHOR[a]
        dx = rec["x_star"] - ref["x_star"]
        dc = rec["c_max"] - ref["c_max"]
        ok = abs(dx) <= Q1_TOL and abs(dc) <= Q1_TOL
        q1_ok = q1_ok and ok
        repro.append({"a": a,
                      "x_star_computed": rec["x_star"], "x_star_anchor": ref["x_star"],
                      "x_star_deviation": dx,
                      "c_max_computed": rec["c_max"], "c_max_anchor": ref["c_max"],
                      "c_max_deviation": dc,
                      "within_5e-5": bool(ok)})

    # --- fine grid a in [0.05, 2] step 0.001 --------------------------------
    n = int(round((GRID_HI - GRID_LO) / GRID_STEP)) + 1
    grid = []
    for i in range(n):
        a = GRID_LO + i * GRID_STEP
        a = round(a, 10)
        xs = I.solve_xstar(a)
        cm = math.erfc(math.sqrt(xs / 2.0))
        grid.append({"a": a, "x_star": xs, "c_max": cm, "sqrt_a_over_c_max": math.sqrt(a) / cm})

    # --- assembly minimum (Q2) ----------------------------------------------
    amin = min(grid, key=lambda r: r["sqrt_a_over_c_max"])
    q2_a_ok = Q2_A_LO <= amin["a"] <= Q2_A_HI
    q2_v_ok = abs(amin["sqrt_a_over_c_max"] - Q2_VAL_TARGET) <= Q2_VAL_TOL
    q2_ok = q2_a_ok and q2_v_ok

    # --- baseline embedding (Q3) ---------------------------------------------
    c_rand_1 = I.c_rand(1.0)
    c_max_1 = next(r["c_max"] for r in four if r["a"] == 1.0)
    q3a_ok = abs(c_rand_1 - 0.423) <= Q3_TOL
    q3b_ok = abs(c_max_1 - 0.66) <= Q3_TOL
    q3_ok = q3a_ok and q3b_ok

    elapsed = time.time() - t0
    import resource
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    raw = {
        "run_id": "RUN-ECDLP-e962f6-001",
        "kind": "quadrature",
        "method": {
            "root_solver": "bisection bracketing (100 iterations, bracket [1e-9, 50]) plus Newton refinement (up to 60 iterations, convergence 1e-16 relative)",
            "erfc": "math.erfc (Python standard library)",
            "derivative": "analytic g'(x) = -e^{-x/2} x^{-3/2}",
            "deterministic": True,
            "seed": None,
        },
        "grid": {"a_lo": GRID_LO, "a_hi": GRID_HI, "a_step": GRID_STEP, "n_points": n},
        "tolerances": {"Q1": Q1_TOL, "Q2": {"a_lo": Q2_A_LO, "a_hi": Q2_A_HI, "value_target": Q2_VAL_TARGET, "value_tol": Q2_VAL_TOL}, "Q3": Q3_TOL},
        "anchor_source": ANCHOR_SOURCE,
        "four_a_values": four,
        "fine_grid": grid,
        "assembly_minimum": amin,
        "baseline_embedding": {"c_rand_at_a_m_1": c_rand_1, "c_max_at_a_1": c_max_1,
                               "targets": {"c_rand": 0.423, "c_max": 0.66}},
        "anchor_reproduction": repro,
        "self_reported": {"elapsed_seconds": round(elapsed, 3), "peak_rss_bytes": int(peak_rss)},
    }

    summary = {
        "run_id": "RUN-ECDLP-e962f6-001",
        "kind": "quadrature",
        "four_a_values": four,
        "anchor_reproduction": repro,
        "assembly_minimum": amin,
        "baseline_embedding": raw["baseline_embedding"],
        "checks": {
            "Q1_anchor_within_5e-5_all_four_a": bool(q1_ok),
            "Q2_assembly_min_a_in_[0.2,0.25]": bool(q2_a_ok),
            "Q2_assembly_min_value_within_0.01_of_1.28": bool(q2_v_ok),
            "Q2": bool(q2_ok),
            "Q3_c_rand_1_within_5e-3_of_0.423": bool(q3a_ok),
            "Q3_c_max_1_within_5e-3_of_0.66": bool(q3b_ok),
            "Q3": bool(q3_ok),
        },
        "self_reported": raw["self_reported"],
    }

    out = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "raw-result.json"), "w") as fh:
        json.dump(jsonable(raw), fh)
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(jsonable(summary), fh, indent=1)

    meta = {
        "run_id": "RUN-ECDLP-e962f6-001",
        "kind": "quadrature",
        "stage": 1,
        "status": "completed_valid" if (q1_ok and q2_ok and q3_ok) else "completed_invalid",
        "failure_class": None,
        "validity": "valid" if (q1_ok and q2_ok and q3_ok) else "invalid",
        "validity_reason": ("Q1-Q3 all met" if (q1_ok and q2_ok and q3_ok) else
                            "quadrature failed to reproduce the committed anchor values / "
                            "assembly minimum / baseline embedding within the frozen tolerances "
                            "(implementation error per the contract stopping rule, not a model failure)"),
        "note": "Stage 1 quadrature table; deterministic, no seed",
        "seeds": {"quadrature": None, "note": "deterministic; no seed (method and grid recorded in the manifest)"},
        "params": {"a_values": A_FOUR, "grid": [GRID_LO, GRID_HI, GRID_STEP],
                   "method": "bisection + Newton, math.erfc"},
        "protocol_deviations": [],
        "source_sha256": RC.source_hashes(),
        "self_reported": raw["self_reported"],
    }
    with open(os.path.join(out, "run-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"quadrature done in {elapsed:.2f}s; Q1={q1_ok} Q2={q2_ok} Q3={q3_ok}; "
          f"assembly min at a={amin['a']} value={amin['sqrt_a_over_c_max']:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

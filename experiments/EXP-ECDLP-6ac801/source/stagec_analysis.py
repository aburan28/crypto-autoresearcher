"""STAGE C (ANALYSIS) for EXP-ECDLP-6ac801.

Reads the 5 Stage B run records (one per seed, each sweeping the full
a_grid internally) and applies the v2-contract-verbatim G3-style
feasibility criterion (specification.yaml `definitions`,
"G3-style feasibility criterion ..."):

  at a given a, T_sel = T/2 is G3-FEASIBLE iff exact top-T_sel share >=
  STATIC(T)_r exact coverage in >= 4 of the 5 seeds; otherwise
  G3-INFEASIBLE.

Reports, per a: the 5 per-seed margins, the pass-count out of 5, and the
G3-style verdict. Evaluates the a = 1/4 REPLICATION CONTROL FIRST
(specification.yaml `stopping_rules`), and only interprets the three novel
cells (1/16, 1/8, 3/16) if that control reproduces G3-INFEASIBLE. Reports
the crossing bracket per `definitions.crossing point`, or "not confirmed at
this N" if the pattern does not cleanly bracket.

This script performs ZERO interpretation beyond the contract's own
criterion language: no hypothesis-level conclusion, no status change.
Certificate kind: none.
"""
from __future__ import annotations

import json
import os
import sys

RUN_IDS = [
    "RUN-ECDLP-6ac801-001",
    "RUN-ECDLP-6ac801-002",
    "RUN-ECDLP-6ac801-003",
    "RUN-ECDLP-6ac801-004",
    "RUN-ECDLP-6ac801-005",
]
SEEDS = [1, 2, 3, 4, 5]
A_GRID = [1 / 16, 1 / 8, 3 / 16, 1 / 4]

# a = 1/4 replication-control anchor (EV-ECDLP-60e266, N = 2^24, 5 seeds,
# quoted verbatim from the committed evidence record's `obstruction.value`
# field for the tail-check comparison only; NOT used in any pass/fail
# computation below).
EV_60E266_2POW24_A_QUARTER_MARGINS = [-0.0129, -0.0084, -0.0362, -0.0168, -0.0222]


def a_label(a: float) -> str:
    return f"a={a:.6f}"


def main() -> int:
    runs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
    per_seed_cells = []
    for rid in RUN_IDS:
        with open(os.path.join(runs_dir, rid, "summary.json")) as fh:
            per_seed_cells.append(json.load(fh))

    for d in per_seed_cells:
        if d.get("completed_invalid"):
            print("FATAL: a Stage B run is completed_invalid; aborting analysis", file=sys.stderr)
            return 1

    result = {"per_a": {}, "seeds": SEEDS, "run_ids": RUN_IDS}

    # -------- a = 1/4 REPLICATION CONTROL, evaluated FIRST -----------------
    a_ctrl = 1 / 4
    lbl = a_label(a_ctrl)
    margins_ctrl = [d["cells"][lbl]["margin"] for d in per_seed_cells]
    passes_ctrl = [d["cells"][lbl]["pass"] for d in per_seed_cells]
    pass_count_ctrl = sum(passes_ctrl)
    verdict_ctrl = "G3-FEASIBLE" if pass_count_ctrl >= 4 else "G3-INFEASIBLE"
    control_reproduces_fail = verdict_ctrl == "G3-INFEASIBLE"

    result["a_quarter_replication_control"] = {
        "a": a_ctrl,
        "per_seed_margins": margins_ctrl,
        "per_seed_pass": passes_ctrl,
        "pass_count": pass_count_ctrl,
        "verdict": verdict_ctrl,
        "reproduces_EV_ECDLP_60e266_G3_INFEASIBLE": control_reproduces_fail,
        "EV_ECDLP_60e266_2pow24_a_quarter_margins_for_comparison": EV_60E266_2POW24_A_QUARTER_MARGINS,
        "sign_and_magnitude_comparable": all(
            (m < 0) == (r < 0) for m, r in zip(margins_ctrl, EV_60E266_2POW24_A_QUARTER_MARGINS)
        ),
    }
    result["per_a"][lbl] = {
        "a": a_ctrl, "per_seed_margins": margins_ctrl, "per_seed_pass": passes_ctrl,
        "pass_count": pass_count_ctrl, "verdict": verdict_ctrl, "role": "replication_control",
    }

    print(f"[stageC] a=1/4 REPLICATION CONTROL: pass_count={pass_count_ctrl}/5 verdict={verdict_ctrl}", flush=True)
    print(f"[stageC] a=1/4 margins: {margins_ctrl}", flush=True)

    if not control_reproduces_fail:
        result["outcome"] = "d_INSTRUMENT_MISMATCH"
        result["outcome_note"] = (
            "The a = 1/4 replication control did NOT reproduce EV-ECDLP-60e266's "
            "established G3-INFEASIBLE result (scored >= 4/5 PASS). Per "
            "specification.yaml `invalidation_rules` / `distinguishable_outcomes` "
            "(d): the entire batch's instrument is in question; NO conclusion is "
            "drawn about a in {1/16, 1/8, 3/16}. Interpretation of the other three "
            "cells is STOPPED here."
        )
        print("[stageC] STOPPING: instrument mismatch per stopping_rules", flush=True)
        with open(os.path.join(sys.argv[1], "summary.json"), "w") as fh:
            json.dump(result, fh, indent=1)
        return 0

    print("[stageC] control reproduces G3-INFEASIBLE; proceeding to interpret novel cells", flush=True)

    # -------- Novel cells: a in {1/16, 1/8, 3/16} ---------------------------
    novel_as = [1 / 16, 1 / 8, 3 / 16]
    for a in novel_as:
        lbl = a_label(a)
        margins = [d["cells"][lbl]["margin"] for d in per_seed_cells]
        passes = [d["cells"][lbl]["pass"] for d in per_seed_cells]
        pass_count = sum(passes)
        verdict = "G3-FEASIBLE" if pass_count >= 4 else "G3-INFEASIBLE"
        result["per_a"][lbl] = {
            "a": a, "per_seed_margins": margins, "per_seed_pass": passes,
            "pass_count": pass_count, "verdict": verdict, "role": "novel",
        }
        print(f"[stageC] a={a:.6f} pass_count={pass_count}/5 verdict={verdict} margins={margins}", flush=True)

    # -------- crossing bracket ----------------------------------------------
    ordered_a = [1 / 16, 1 / 8, 3 / 16, 1 / 4]
    verdicts = [result["per_a"][a_label(a)]["verdict"] for a in ordered_a]
    crossing = None
    for i in range(len(ordered_a) - 1):
        if verdicts[i] == "G3-FEASIBLE" and verdicts[i + 1] == "G3-INFEASIBLE":
            crossing = (ordered_a[i], ordered_a[i + 1])
            break
    # check the pattern is monotone FEASIBLE-then-INFEASIBLE (a clean bracket);
    # if any FEASIBLE appears after an INFEASIBLE reading, the bracket is not
    # confirmed cleanly per `definitions.crossing point`.
    monotone = all(
        not (verdicts[i] == "G3-INFEASIBLE" and verdicts[i + 1] == "G3-FEASIBLE")
        for i in range(len(ordered_a) - 1)
    )
    if crossing is not None and monotone:
        result["crossing_bracket"] = {
            "feasible_a": crossing[0], "infeasible_a": crossing[1],
            "note": "the pair of adjacent a-grid values straddling the FEASIBLE/INFEASIBLE boundary",
        }
        print(f"[stageC] crossing bracket confirmed: {crossing}", flush=True)
    else:
        result["crossing_bracket"] = {"confirmed": False, "note": "crossing not confirmed at this N"}
        print("[stageC] crossing bracket NOT cleanly confirmed at this N", flush=True)

    # -------- tail checks -----------------------------------------------------
    # (i) the a-grid cell with the smallest |pass-count margin from the 4/5 boundary|
    borderline = min(novel_as, key=lambda a: abs(result["per_a"][a_label(a)]["pass_count"] - 4))
    result["tail_check_borderline_cell"] = {
        "a": borderline, **result["per_a"][a_label(borderline)],
    }

    result["outcome"] = "stageBC_measurement_reported"
    result["outcome_note"] = (
        "Stage B/C production measurement only. Per specification.yaml "
        "`blind_rederivation` / `invalidation_rules`: this reading alone is NOT "
        "evidence under this contract until Stage A's sealed blind re-derivation "
        "(TASK-20260907-80e198) exists and is compared cell by cell. Reported "
        "here exactly as measured, with zero hypothesis-level interpretation."
    )

    with open(os.path.join(sys.argv[1], "summary.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

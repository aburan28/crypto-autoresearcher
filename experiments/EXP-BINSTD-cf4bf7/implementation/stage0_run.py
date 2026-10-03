#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-cf4bf7: corrected ladder, ord/f census, lattice, predictions."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arithmetic import (
    corrected_ladder_rows,
    lattice_ord17_of_4,
    ord_f_census,
)
from runpack import EXP_ROOT, dump_text, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-7d4512"

METHODOLOGICAL_NOTE = """# Methodological note — HOLD-N corrections absorbed (Stage 0)

Experiment `EXP-BINSTD-cf4bf7`, task `TASK-20261001-18804b`.
Source idea `IDEA-20260922-9e5383`; review
`analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-9e5383.yaml`
(verdict `sound_with_corrections` / HOLD-N). Hypothesis `H-BINSTD-4a2f99`.

## Defects absorbed (observations only; no claim status change)

1. **Null precondition.** Stable Frobenius subspaces of `F_{2^n}` number
   `2^f` with `f = 1 + (n-1)/ord_n(2)`. They are trivial
   (dimensions `{0,1,n-1,n}` only, `f=2`) **iff** `ord_n(2)=n-1`
   (primitive prime). The source wording "prime degree ⇒ no nontrivial
   stable subspace" is **rejected** as the general null claim and retained
   only as the named falsifiable alternative Stage 0/4 contrast against.

2. **n=31 disqualified as null.** Independent recomputation:
   `ord_31(2)=5` ⇒ `f=7` (128 stable subspaces, mid-dimension present).
   Retained **only** as contrast control (`role: contrast_not_null`).
   Never labeled as a null arm in any artifact of this experiment.

3. **n=41 is not a "poor" lattice control.** `ord_41(2)=20` ⇒ `f=3`
   (moderately rich). Rejected as poor-n control
   (`role: rejected_poor_control`).

4. **Ratio errors restated** after null re-selection to primitive primes:
   - pair 1: `(d,k)=(4,7)` vs `n=29`; error **+4.5pp**
   - pair 2 PRIMARY: `(d,k)=(2,17)` vs `n=37`; error **−17.0pp** (worst;
     disclosed beside any primary-cell finding)
   - pair 3: `(d,k)=(2,19)` vs `n=37`; error **−11.1pp**
   - pair 4: `(d,k)=(4,7)` vs `n=29`; error **+11.9pp**
   - pair 5: `(d,k)=(2,19)` vs `n=37`; error **+0.2pp** (best ratio match)

5. **WDSat gate.** Stages 2–3 optional; missing engine ⇒
   `instrument_unavailable` (infrastructure), **not** mathematical
   falsification of H1.

## Primary cell selection

Pair 2 remains primary for **lattice richness**
(`ord_17(4)=4`, `f=5`, 32 stable subspaces, dims
`{0,1,4,5,8,9,12,13,16,17}`), not for best ratio (pair 5).

## Claim boundary

Toy / instrument protocol. No exponent move. No break. No rho
competitiveness. No deployed-curve attack at `n>=131`.
`certificate.kind: none` for all Stage 0 arithmetic runs.
"""


PREREGISTERED = """# Preregistered predictions — EXP-BINSTD-cf4bf7 (BEFORE Stage 2)

Frozen reference: `experiments/EXP-BINSTD-cf4bf7/specification.yaml`
`preregistered_prediction` and `H-BINSTD-4a2f99`.

## Measured / independently recomputed (Stage 0/1/4)

| Quantity | Prediction | Label |
|---|---|---|
| Corrected ladder error_pp | pair1 +4.5; pair2 −17.0; pair3 −11.1; pair4 +11.9; pair5 +0.2 | EXPECTED |
| `ord_n(2)` / `f` for n∈{17,29,31,37,41,53} | 8/3, 28/2, 5/7, 36/2, 20/3, 52/2 | EXPECTED |
| `ord_17(4)` lattice | ord=4, f=5, 32 subspaces, dims {0,1,4,5,8,9,12,13,16,17} | EXPECTED |
| Null arm n=37 | f=2; mid-dim stable V absent | EXPECTED |
| Contrast n=31 | f=7; **not a null arm** | EXPECTED |
| Stage 1 curve orders | Constructible; #E verified in Hasse interval | PROTOCOL |

## Modeled prior (Stage 2 only; NOT a measurement until run)

| Quantity | Modeled prior | Source |
|---|---|---|
| WDSat conflict ratio on richest stable F_4-subspace | within 1% of 1.0 (basis-blind) OR ≤0.5 with within-curve non-stable near 1 | IDEA-20260920-b9f0c5 / H-BINSTD-4a2f99 |

Missing Stage 2 is recorded as `instrument_unavailable`, **not** as ratio=1.0.

## Hard fails

- Any `f≠2` on n=37 after ruling out implementation bugs.
- Treating n=31 as null.
- Using n=41 as poor lattice control.
"""


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage0 = EXP_ROOT / "stage0"
    stage0.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    ladder = corrected_ladder_rows()
    ladder_ok = all(r["error_pp_match"] and r["null_is_primitive_prime"] for r in ladder)
    dump_yaml(
        stage0 / "corrected-ladder.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 0,
            "null_policy": "primitive_prime_ord_n_2_eq_n_minus_1",
            "primary_pair": 2,
            "worst_ratio_error_pair": 2,
            "worst_ratio_error_pp": -17.0,
            "rows": ladder,
            "all_error_pp_match_frozen": ladder_ok,
            "n31_used_as_null": False,
            "n41_used_as_poor_control": False,
            "no_break_claim": True,
        },
    )
    lines.append(f"corrected-ladder all_match={ladder_ok}")
    for r in ladder:
        lines.append(
            f"  pair {r['pair']}: dk={r['dk']} n={r['n_null']} "
            f"ratio={r['toy_ratio']} err={r['error_pp_recomputed']}pp "
            f"frozen={r['error_pp_frozen']} match={r['error_pp_match']} "
            f"primitive_null={r['null_is_primitive_prime']}"
        )

    census = ord_f_census()
    census_ok = all(r["match_frozen"] for r in census)
    # Explicit role guards
    n31 = next(r for r in census if r["n"] == 31)
    n37 = next(r for r in census if r["n"] == 37)
    n41 = next(r for r in census if r["n"] == 41)
    role_ok = (
        n31["role"] == "contrast_not_null"
        and n37["role"] == "primary_null_arm"
        and n41["role"] == "rejected_poor_control"
        and n37["f_irreducible_factor_count"] == 2
        and n31["f_irreducible_factor_count"] == 7
        and not n37["mid_dimension_stable_V_present"]
        and n31["mid_dimension_stable_V_present"]
    )
    dump_yaml(
        stage0 / "ord-f-census.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 0,
            "method": "ord_n(2)=least d|(n-1) with 2^d≡1 mod n; f=1+(n-1)/ord_n(2)",
            "n_set": [17, 29, 31, 37, 41, 53],
            "rows": census,
            "all_match_frozen": census_ok,
            "role_guards_ok": role_ok,
            "n31_labeled_as_null": False,
            "n41_labeled_as_poor": False,
        },
    )
    lines.append(f"ord-f-census all_match={census_ok} role_guards_ok={role_ok}")

    lat = lattice_ord17_of_4()
    dump_yaml(
        stage0 / "ord17-of-4-lattice.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 0,
            "method": (
                "ord_17(4) by least d|16 with 4^d≡1 mod 17; "
                "f=1+16/ord; dims=subset sums of factor degrees {1,4,4,4,4}"
            ),
            **lat,
        },
    )
    lines.append(f"ord17-of-4 lattice match={lat['match_expected']}")

    dump_yaml(
        stage0 / "preregistered-predictions.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 0,
            "written_before_stage2": True,
            "frozen_prediction_ref": (
                "experiments/EXP-BINSTD-cf4bf7/specification.yaml#"
                "preregistered_prediction"
            ),
            "measured_predictions": {
                "ladder_error_pp": {1: 4.5, 2: -17.0, 3: -11.1, 4: 11.9, 5: 0.2},
                "ord_f_census": {
                    17: {"ord": 8, "f": 3},
                    29: {"ord": 28, "f": 2},
                    31: {"ord": 5, "f": 7},
                    37: {"ord": 36, "f": 2},
                    41: {"ord": 20, "f": 3},
                    53: {"ord": 52, "f": 2},
                },
                "ord_17_of_4": {
                    "ord": 4,
                    "f": 5,
                    "stable_subspace_count": 32,
                    "dimensions": [0, 1, 4, 5, 8, 9, 12, 13, 16, 17],
                },
                "null_arm_n37_f": 2,
                "contrast_n31_f": 7,
            },
            "modeled_prior_stage2_only": {
                "wdsat_conflict_ratio": (
                    "within 1% of 1.0 (basis-blind) OR <=0.5 with "
                    "within-curve non-stable near 1"
                ),
                "label": "MODELED",
                "not_to_be_recorded_as_measured_if_instrument_unavailable": True,
            },
            "markdown_path": "stage0/preregistered-predictions.md",
        },
    )
    dump_text(stage0 / "preregistered-predictions.md", PREREGISTERED)
    dump_text(stage0 / "methodological-note.md", METHODOLOGICAL_NOTE)
    lines.append("preregistered-predictions + methodological-note written")

    finished = utc_now()
    wall = time.time() - t0
    valid = ladder_ok and census_ok and role_ok and lat["match_expected"]
    metrics = {
        "ladder_all_match": ladder_ok,
        "census_all_match": census_ok,
        "role_guards_ok": role_ok,
        "lattice_match": lat["match_expected"],
        "ord_17_of_4": lat["ord_17_of_4"],
        "stable_subspace_count_composite": lat["stable_subspace_count"],
        "null_arm_f_predicted": 2,
        "contrast_n31_f_predicted": 7,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
    }
    stdout = "\n".join(lines) + "\n"
    write_run_package(
        RUN_ID,
        stage=0,
        arm="stage0_arithmetic",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage0_run.py",
        parameters={"cells": ["corrected_ladder", "ord_f_census", "ord17_of_4_lattice"]},
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "Stage 0 arithmetic disagreed with frozen table",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": None, "verifier": None, "artifact": None},
    )
    print(stdout)
    if not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
